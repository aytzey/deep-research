from pathlib import Path

from deep_research_mcp.config import Settings
from deep_research_mcp.services.academic import AcademicSearchService


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
