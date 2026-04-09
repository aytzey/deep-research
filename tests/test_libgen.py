from pathlib import Path

from zotero_researcher_mcp.config import Settings
from zotero_researcher_mcp.services.libgen import LibgenService


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        openalex_email=None,
        semantic_scholar_api_key=None,
        zotero_library_id=None,
        zotero_library_type="user",
        zotero_api_key=None,
        data_dir=tmp_path,
        libgen_mirrors=("https://libgen.is",),
        libgen_timeout_sec=10.0,
    )


def test_parse_libgen_search_results(tmp_path: Path) -> None:
    service = LibgenService(_settings(tmp_path))
    html = """
    <html><body>
      <table></table><table></table>
      <table>
        <tr><th>ID</th></tr>
        <tr>
          <td>123</td>
          <td>Jane Doe</td>
          <td>Transformers in Practice</td>
          <td>Test Press</td>
          <td>2024</td>
          <td>320</td>
          <td>English</td>
          <td>12 Mb</td>
          <td>pdf</td>
          <td><a href="/book/index.php?md5=abc" title="libgen">Mirror</a></td>
          <td></td><td></td><td></td><td></td><td></td>
        </tr>
      </table>
    </body></html>
    """
    results = service._parse_search_results(html, "https://libgen.is/search.php?req=x&column=title", 10, ("pdf",))
    assert len(results) == 1
    assert results[0].title == "Transformers in Practice"
    assert results[0].raw["Mirror_1"] == "https://libgen.is/book/index.php?md5=abc"


def test_extract_download_links(tmp_path: Path) -> None:
    service = LibgenService(_settings(tmp_path))
    html = """
    <html><body>
      <a href="/get.php?md5=abc&key=123">GET</a>
      <a href="https://cloudflare-ipfs.com/ipfs/xyz/file.pdf">Cloudflare</a>
    </body></html>
    """
    links = service._extract_download_links(html, "https://libgen.is/book/index.php?md5=abc")
    assert links["GET"] == "https://libgen.is/get.php?md5=abc&key=123"
    assert links["Cloudflare"] == "https://cloudflare-ipfs.com/ipfs/xyz/file.pdf"
