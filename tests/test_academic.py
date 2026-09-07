import asyncio
import json
from dataclasses import replace
from pathlib import Path

import httpx
import pytest

from paper_pilot.config import Settings
from paper_pilot.models import PaperRecord
from paper_pilot.services.academic import AcademicSearchService


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        openalex_email="you@example.com",
        semantic_scholar_api_key=None,
        zotero_library_id=None,
        zotero_library_type="user",
        zotero_api_key=None,
        data_dir=tmp_path,
        libgen_mirrors=("https://libgen.is",),
        libgen_timeout_sec=10.0,
        unpaywall_email="you@example.com",
    )


def test_paper_from_europe_pmc_extracts_pdf_url(tmp_path: Path) -> None:
    service = AcademicSearchService(_settings(tmp_path))
    item = {
        "pmcid": "PMC123456",
        "doi": "10.1000/test",
        "title": "Biomedical DL",
        "authorString": "Doe J, Roe R",
        "pubYear": "2024",
        "abstractText": "Abstract",
        "journalInfo": {"journal": {"title": "Test Journal"}},
        "isOpenAccess": "Y",
        "fullTextUrlList": {
            "fullTextUrl": [
                {"availabilityCode": "OA", "documentStyle": "html", "url": "https://europepmc.org/articles/PMC123456"},
                {"availabilityCode": "OA", "documentStyle": "pdf", "url": "https://europepmc.org/articles/PMC123456?pdf=render"},
            ]
        },
    }

    paper = service._paper_from_europe_pmc(item)

    assert paper.source == "europe_pmc"
    assert paper.pdf_url == "https://europepmc.org/articles/PMC123456?pdf=render"
    assert paper.is_open_access is True


def test_arxiv_search_preserves_title_and_year_filters(tmp_path: Path, monkeypatch) -> None:
    service = AcademicSearchService(_settings(tmp_path))
    seen = {}

    async def get_text(client, url, params, namespace):
        seen.update(params)
        return '<feed xmlns="http://www.w3.org/2005/Atom"/>'

    monkeypatch.setattr(service, "_get_text", get_text)
    asyncio.run(service._search_arxiv(None, "Attention Is All You Need", 4, 2017, 2017))
    assert 'ti:"Attention Is All You Need"' in seen["search_query"]
    assert "all:Attention AND all:Is AND all:All AND all:You AND all:Need" in seen["search_query"]
    assert "submittedDate:[201701010000 TO 201712312359]" in seen["search_query"]


def test_enrich_with_unpaywall_falls_back_to_openalex_and_canonicalizes_doi(tmp_path: Path) -> None:
    service = AcademicSearchService(_settings(tmp_path))
    paper = PaperRecord(
        source="crossref",
        source_id="peerj",
        title="PeerJ Figure Record",
        doi="10.7717/peerj-cs.3254/fig-10",
    )
    seen: dict[str, str] = {}

    async def run() -> tuple[list[PaperRecord], list[str]]:
        async with httpx.AsyncClient() as client:
            async def fail_unpaywall(_client: httpx.AsyncClient, doi: str) -> dict[str, object]:
                raise httpx.ConnectTimeout(f"timeout: {doi}")

            async def fallback_openalex(_client: httpx.AsyncClient, doi: str) -> dict[str, object]:
                seen["doi"] = doi
                return {
                    "id": "https://openalex.org/W123",
                    "display_name": "PeerJ Paper",
                    "publication_year": 2024,
                    "authorships": [{"author": {"display_name": "Jane Doe"}}],
                    "primary_location": {
                        "landing_page_url": "https://example.com/paper",
                        "source": {"display_name": "PeerJ"},
                    },
                    "best_oa_location": {
                        "landing_page_url": "https://example.com/paper",
                        "pdf_url": "https://example.com/paper.pdf",
                        "source": {"display_name": "PeerJ"},
                    },
                    "open_access": {"is_oa": True, "oa_status": "gold"},
                    "cited_by_count": 12,
                    "primary_topic": {"display_name": "Machine Learning"},
                }

            service._lookup_unpaywall = fail_unpaywall  # type: ignore[method-assign]
            service._lookup_openalex_by_doi = fallback_openalex  # type: ignore[method-assign]
            return await service._enrich_with_unpaywall(client, [paper])

    enriched, warnings = asyncio.run(run())

    assert len(warnings) == 1 and "Unpaywall lookup failed" in warnings[0]
    assert enriched[0].raw["unpaywall"]["status"] == "error"
    assert seen["doi"] == "10.7717/peerj-cs.3254"
    assert enriched[0].pdf_url == "https://example.com/paper.pdf"
    assert enriched[0].url == "https://example.com/paper"
    assert enriched[0].is_open_access is True
    assert enriched[0].raw["openalex_doi_lookup"]["id"] == "https://openalex.org/W123"


def test_unpaywall_checks_all_missing_pdf_dois_and_preserves_locations(tmp_path: Path, monkeypatch) -> None:
    service = AcademicSearchService(_settings(tmp_path))
    papers = [PaperRecord(
        source="test", source_id=str(i), title=f"Paper {i}", doi=f"10.1234/{i}",
        is_open_access=True,
    ) for i in range(23)]
    papers.append(PaperRecord(source="arxiv", source_id="1", title="No DOI"))
    papers.append(PaperRecord(source="test", source_id="copy", title="Copy", doi="https://doi.org/10.1234/0"))
    seen = []
    best = {"url_for_pdf": "https://example.org/best.pdf", "host_type": "publisher", "license": "cc-by"}
    alternate = {"url_for_pdf": "https://example.org/repository.pdf", "host_type": "repository", "version": "acceptedVersion"}

    async def lookup(client, doi):
        seen.append(doi)
        return {"doi": doi, "is_oa": True, "oa_status": "gold", "best_oa_location": best, "oa_locations": [best, alternate]}

    monkeypatch.setattr(service, "_lookup_unpaywall", lookup)
    enriched, warnings = asyncio.run(service._enrich_with_unpaywall(None, papers))
    assert len(seen) == len(set(seen)) == 23
    assert warnings == []
    assert all(p.raw["unpaywall"]["status"] == "ok" for p in enriched if p.doi)
    assert enriched[-2].raw["unpaywall"]["status"] == "not_applicable"
    assert enriched[0].pdf_url == best["url_for_pdf"]
    assert enriched[0].raw["original_pdf_url"] is None
    assert enriched[0].raw["unpaywall"]["oa_locations"] == [best, alternate]


def test_missing_email_only_affects_records_needing_unpaywall(tmp_path: Path) -> None:
    service = AcademicSearchService(replace(_settings(tmp_path), unpaywall_email=None))
    paper = PaperRecord(source="test", source_id="1", title="Paper")
    records, _ = asyncio.run(service._enrich_with_unpaywall(None, [paper]))
    assert records[0].raw["unpaywall"]["status"] == "not_applicable"
    paper.doi = "10.1234/1"
    available = PaperRecord(source="test", source_id="2", title="Available", doi="10.1234/2", pdf_url="https://example.org/full.pdf")
    records, warnings = asyncio.run(service._enrich_with_unpaywall(None, [paper, available]))
    assert "UNPAYWALL_EMAIL" in warnings[0]
    assert records[0].raw["unpaywall"]["status"] == "error"
    assert records[1].raw["unpaywall"]["status"] == "deferred"
    records, warnings = asyncio.run(service._enrich_with_unpaywall(None, [available]))
    assert warnings == []


def test_existing_pdf_links_defer_unpaywall_until_download(tmp_path: Path, monkeypatch) -> None:
    service = AcademicSearchService(_settings(tmp_path))
    paper = PaperRecord(source="test", source_id="1", title="Available", doi="10.1234/1", pdf_url="https://example.org/full.pdf")

    async def unexpected(*args, **kwargs):
        pytest.fail("An existing PDF link must be tried before Unpaywall")

    monkeypatch.setattr(service, "_lookup_oa_metadata", unexpected)
    records, warnings = asyncio.run(service._enrich_with_unpaywall(None, [paper]))
    assert warnings == []
    assert records[0].pdf_url == "https://example.org/full.pdf"
    assert records[0].raw["unpaywall"]["status"] == "deferred"


def test_unpaywall_landing_page_is_not_a_pdf(tmp_path: Path, monkeypatch) -> None:
    service = AcademicSearchService(_settings(tmp_path))
    paper = PaperRecord(source="test", source_id="1", title="Paper", doi="10.1234/1")

    async def lookup(client, doi):
        return {"doi": doi, "is_oa": True, "best_oa_location": {"url": "https://example.org/article", "url_for_landing_page": "https://example.org/article"}}

    monkeypatch.setattr(service, "_lookup_unpaywall", lookup)
    asyncio.run(service._enrich_with_unpaywall(None, [paper]))
    assert paper.pdf_url is None
    assert paper.url == "https://example.org/article"
    assert paper.raw["unpaywall"]["status"] == "ok"


def test_unpaywall_outage_does_not_silently_reuse_expired_cache(tmp_path: Path) -> None:
    service = AcademicSearchService(_settings(tmp_path))
    url = "https://api.unpaywall.org/v2/10.1234%2F1"
    params = {"email": service.settings.unpaywall_email}
    service.settings.cache_dir.mkdir()
    service._cache_file("unpaywall_lookup", url, params, "json").write_text(json.dumps({"expires_at": 0, "payload": {"is_oa": True}}))

    def offline(request):
        raise httpx.ConnectError("offline")

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(offline)) as client:
            return await service._enrich_with_unpaywall(client, [PaperRecord(source="test", source_id="1", title="Paper", doi="10.1234/1")])

    records, warnings = asyncio.run(run())
    assert warnings and records[0].raw["unpaywall"]["status"] == "error"
    assert not records[0].is_open_access
