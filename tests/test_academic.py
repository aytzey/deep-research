import asyncio
from pathlib import Path

import httpx

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

    assert warnings == []
    assert seen["doi"] == "10.7717/peerj-cs.3254"
    assert enriched[0].pdf_url == "https://example.com/paper.pdf"
    assert enriched[0].url == "https://example.com/paper"
    assert enriched[0].is_open_access is True
    assert enriched[0].raw["openalex_doi_lookup"]["id"] == "https://openalex.org/W123"
