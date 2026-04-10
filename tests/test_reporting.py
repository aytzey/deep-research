from pathlib import Path

from paper_pilot.config import Settings
from paper_pilot.models import DownloadedDocument, PaperRecord
from paper_pilot.services.reporting import ReportService


def test_render_markdown_mentions_downloads(tmp_path: Path) -> None:
    settings = Settings(
        openalex_email=None,
        semantic_scholar_api_key=None,
        zotero_library_id=None,
        zotero_library_type="user",
        zotero_api_key=None,
        data_dir=tmp_path,
        libgen_mirrors=("https://libgen.is",),
        libgen_timeout_sec=10.0,
    )
    service = ReportService(settings)
    paper = PaperRecord(
        source="arxiv",
        source_id="1234.5678",
        title="Transformer Methods",
        authors=["Jane Doe"],
        year=2025,
        url="https://arxiv.org/abs/1234.5678",
        pdf_url="https://arxiv.org/pdf/1234.5678.pdf",
        is_open_access=True,
    )
    document = DownloadedDocument(
        paper=paper,
        path=tmp_path / "paper.pdf",
        page_count=12,
        extracted_preview="Sample preview",
    )

    markdown = service.render_markdown(
        topic="transformer methods",
        papers=[paper],
        related=[],
        downloads=[document],
        warnings=[],
    )

    assert "Transformer Methods" in markdown
    assert "Saved PDF" in markdown
    assert "Sample preview" in markdown
