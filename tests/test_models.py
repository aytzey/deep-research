from paper_pilot.models import PaperRecord, combine_papers, normalize_doi


def test_combine_papers_prefers_more_complete_record() -> None:
    sparse = PaperRecord(
        source="crossref",
        source_id="doi:10.1000/test",
        title="A Test Paper",
        doi="10.1000/TEST",
        citation_count=10,
    )
    rich = PaperRecord(
        source="semantic_scholar",
        source_id="abc123",
        title="A Test Paper",
        doi="https://doi.org/10.1000/test",
        authors=["Ada Lovelace", "Alan Turing"],
        abstract="Longer abstract",
        pdf_url="https://example.com/test.pdf",
        is_open_access=True,
        citation_count=25,
    )

    merged = combine_papers([sparse, rich])

    assert len(merged) == 1
    assert merged[0].doi == "10.1000/TEST"
    assert merged[0].citation_count == 25
    assert merged[0].pdf_url == "https://example.com/test.pdf"
    assert merged[0].authors == ["Ada Lovelace", "Alan Turing"]


def test_normalize_doi_accepts_doi_prefix_and_host_without_scheme() -> None:
    assert normalize_doi("doi:10.1000/TEST") == "10.1000/test"
    assert normalize_doi("doi.org/10.1000/TEST") == "10.1000/test"
