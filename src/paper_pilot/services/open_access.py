from __future__ import annotations

import asyncio
import re
from pathlib import Path

import httpx

try:
    import pymupdf as fitz
except ModuleNotFoundError:  # pragma: no cover - compatibility fallback
    import fitz

from paper_pilot.config import Settings
from paper_pilot.models import DownloadedDocument, PaperRecord, normalize_doi, slugify, utc_timestamp
from paper_pilot.services.academic import AcademicSearchService
from paper_pilot.services.net import download_capped, is_public_http_url


class OpenAccessService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def download_best_papers(
        self,
        topic: str,
        papers: list[PaperRecord],
        max_papers: int = 3,
    ) -> tuple[list[DownloadedDocument], list[str]]:
        downloaded: list[DownloadedDocument] = []
        warnings: list[str] = []
        candidates = [paper for paper in papers if paper.pdf_url or paper.doi]
        async with httpx.AsyncClient(
            timeout=60.0,
            follow_redirects=True,
            trust_env=True,
            verify=self.settings.ssl_verify,
            headers={"User-Agent": "paper-pilot/0.4", "Accept": "application/pdf,*/*"},
        ) as client:
            for paper in candidates:
                if len(downloaded) >= max_papers:
                    break
                try:
                    try:
                        path = await self._download_pdf(client, topic, paper)
                    except Exception:
                        if not paper.doi or (paper.raw.get("unpaywall") or {}).get("status") == "ok":
                            raise
                        _, lookup_warnings = await AcademicSearchService(self.settings)._enrich_with_unpaywall(
                            client, [paper], force_lookup=True,
                        )
                        warnings.extend(lookup_warnings)
                        path = await self._download_pdf(client, topic, paper)
                    document = await asyncio.to_thread(self.inspect_local_pdf, paper, path)
                    downloaded.append(document)
                except Exception as exc:
                    warnings.append(f"Failed to download {paper.title}: {exc}")
        return downloaded, warnings

    async def inspect_remote_pdf(
        self,
        pdf_url: str | None = None,
        filename_hint: str = "paper",
        doi: str | None = None,
    ) -> DownloadedDocument:
        doi = normalize_doi(doi)
        if doi and not re.fullmatch(r"10\.\d{4,9}/\S+", doi):
            raise ValueError("Invalid DOI.")
        if not pdf_url and not doi:
            raise ValueError("Provide a PDF URL or DOI.")
        paper = PaperRecord(
            source="remote_pdf" if pdf_url else "doi",
            source_id=pdf_url or doi,
            title=filename_hint,
            doi=doi,
            url=pdf_url,
            pdf_url=pdf_url,
            is_open_access=bool(pdf_url),
        )
        documents, warnings = await self.download_best_papers(filename_hint, [paper], 1)
        if not documents:
            raise ValueError("; ".join(warnings) or "No downloadable PDF found.")
        paper.raw = {**paper.raw, "access_warnings": warnings}
        return documents[0]

    async def _download_pdf(self, client: httpx.AsyncClient, topic: str, paper: PaperRecord) -> Path:
        unpaywall = paper.raw.get("unpaywall") or {}
        locations = [unpaywall.get("best_oa_location") or {}, *(unpaywall.get("oa_locations") or [])]
        urls = list(dict.fromkeys(
            url for url in [
                *(location.get("url_for_pdf") for location in locations),
                paper.pdf_url, paper.raw.get("original_pdf_url"),
            ] if url
        ))
        if not urls:
            raise ValueError("No PDF URL available for this record.")
        last_error: Exception | None = None
        content = b""
        for url in urls:
            if not is_public_http_url(url):
                last_error = ValueError(f"Refusing to fetch non-public PDF URL: {url}")
                continue
            for attempt in range(3):
                try:
                    content = await download_capped(client, url, self.settings.max_download_bytes)
                    if not content.startswith(b"%PDF"):
                        raise ValueError("Downloaded content does not appear to be a PDF.")
                    # Try another location if the advertised PDF is corrupt or truncated.
                    with fitz.open(stream=content, filetype="pdf") as pdf:
                        if pdf.page_count == 0:
                            raise ValueError("Downloaded PDF has no pages.")
                    break
                except Exception as exc:
                    last_error = exc
                    content = b""
                    if attempt < 2:
                        await asyncio.sleep(1.5 * (attempt + 1))
            if content:
                break
        if not content:
            raise last_error or ValueError("No downloadable PDF found.")
        filename = f"{slugify(topic)}-{slugify(paper.title, 50)}-{utc_timestamp()}.pdf"
        downloads_dir = self.settings.data_dir / "downloads"
        downloads_dir.mkdir(parents=True, exist_ok=True)
        destination = downloads_dir / filename
        tmp = destination.with_suffix(".pdf.part")
        tmp.write_bytes(content)
        tmp.replace(destination)
        paper.pdf_url = url
        location = next((item for item in locations if item.get("url_for_pdf") == url), None)
        resolver = "unpaywall" if location else paper.source
        if not location and (paper.raw.get("openalex_doi_lookup") or {}).get("pdf_url") == url:
            resolver = "openalex"
        paper.raw = {
            **paper.raw,
            "pdf_download": {"url": url, "resolver": resolver, "location": location},
        }
        return destination

    def inspect_local_pdf(self, paper: PaperRecord, path: Path, max_pages: int = 5, max_chars: int = 12000) -> DownloadedDocument:
        with fitz.open(path) as document:
            extracted_parts: list[str] = []
            for page_index in range(min(max_pages, document.page_count)):
                extracted_parts.append(document.load_page(page_index).get_text("text"))
            preview = "\n".join(extracted_parts).strip()[:max_chars]
            return DownloadedDocument(
                paper=paper,
                path=path,
                page_count=document.page_count,
                extracted_preview=preview,
            )
