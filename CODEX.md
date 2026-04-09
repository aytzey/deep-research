# CODEX.md

This file is the Codex-specific operating guide for `zotero-researcher-mcp`.

## Best Fit

Codex is a good fit when you want:

- iterative tool use with explicit control over the workflow
- follow-up code changes in the MCP server itself
- direct use of local files returned by the research pipeline

## Setup

Add an MCP server block to `~/.codex/config.toml`. A ready-made snippet lives in [examples/codex.config.toml](examples/codex.config.toml).

Minimal config:

```toml
[mcp_servers.zotero_researcher]
command = "uv"
args = ["--directory", "/absolute/path/to/Zotero_Researcher", "run", "zotero-researcher-mcp"]

[mcp_servers.zotero_researcher.env]
OPENALEX_EMAIL = "you@example.com"
UNPAYWALL_EMAIL = "you@example.com"
ZOTERO_LOCAL = "true"
ZOTERO_LIBRARY_TYPE = "user"
ZOTERO_CONNECTOR_URL = "http://127.0.0.1:23119/connector/saveItems"
ZOTERO_BRIDGE_URL = "http://127.0.0.1:24119"
```

## First Workflow To Try

1. Run `healthcheck`
2. Run `research_topic`
3. Run `deep_read_topic`
4. Open the returned `pdf_path` if you need direct file inspection
5. Run `render_pdf_pages` for figure-heavy papers

## Codex Prompt Patterns

- `Research agentic retrieval, then deep-read the strongest papers and show me the best evidence chunks.`
- `Find the OA papers on multimodal RAG, render the pages with the benchmark tables, and explain what changed across papers.`
- `Check whether local Zotero is healthy and sync the resulting report into a collection named RAG Survey.`

## Codex-Specific Advice

- Use `research_topic` when you want an end-to-end pipeline.
- Use `search_literature` and `find_similar_papers` when you want to steer the selection logic manually.
- Treat `pdf_path` and rendered image paths as the source of truth for direct inspection tasks.
- If you are editing this repository, read [AGENTS.md](AGENTS.md) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) before changing code.

## Where Codex Should Look Next

- shared instructions: [AGENTS.md](AGENTS.md)
- architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- client matrix: [docs/CLIENTS.md](docs/CLIENTS.md)
