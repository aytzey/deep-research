# Architecture

## Goal

`zotero-researcher-mcp` exposes an MCP surface that lets an agent move from topic discovery to document inspection to Zotero persistence without leaving one server.

## Main Components

### `server.py`

Defines the MCP tools and orchestrates the research pipeline.

### `services/academic.py`

Handles discovery and enrichment across:

- Semantic Scholar
- OpenAlex
- arXiv
- Crossref
- Europe PMC
- Unpaywall

### `services/open_access.py`

Resolves open-access PDF candidates, downloads files, and extracts PDF previews.

### `services/deep_read.py`

Performs:

- full-text extraction with PyMuPDF
- chunk generation for downstream retrieval
- page rendering to PNG for chart and figure review

### `services/zotero.py`

Supports two write paths:

1. Web API mode for remote libraries
2. Local mode for desktop Zotero

Local mode uses:

- local API reads through `pyzotero`
- connector-based item save requests
- a bridge plugin for collection membership, notes, and file imports

For sandboxed desktop installs such as Flatpak, attachment files can be staged under the Zotero home directory before import.

### `services/reporting.py`

Produces Markdown reports for both standard research and deep-read workflows.

## Data Flow

1. `search_literature` gathers candidates from multiple scholarly APIs
2. records are normalized into project models
3. OA enrichment resolves better download targets
4. PDFs are downloaded locally
5. deep-read mode extracts full text and chunk evidence
6. the report is written to `data/reports`
7. Zotero sync optionally persists the collection, items, attachment, and note

## Output Artifacts

Generated files are written under `data/`:

- `downloads/` for PDFs
- `reports/` for Markdown reports
- `deep_reads/` for extracted text and chunk manifests
- `renders/` for PNG page renders
- `cache/` for HTTP response cache data

## Network and Reliability Features

- proxy support via `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY`
- custom CA support via `SSL_CERT_FILE`
- cache fallback for temporary upstream failures
- best-effort handling for unstable LibGen mirrors
