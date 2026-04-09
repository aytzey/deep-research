![Deep Research](docs/hero.svg)

# Deep Research

**Open-source Deep Research that actually reads the papers.**

Everyone's selling "Deep Research" behind paywalls. They scrape some web results, summarize a few abstracts, and call it analysis.

This does what they don't. It downloads the actual PDFs, reads them cover to cover, pulls out evidence with citations, renders the figures so your AI can see them, and saves everything to your Zotero library. It works with Claude, Codex, and any MCP client.

[![CI](https://github.com/aytzey/deep-research/actions/workflows/ci.yml/badge.svg)](https://github.com/aytzey/deep-research/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](pyproject.toml)
[![GitHub stars](https://img.shields.io/github/stars/aytzey/deep-research?style=social)](https://github.com/aytzey/deep-research/stargazers)

---

![Demo](docs/demo.gif)

## One prompt. Full pipeline.

```
Research retrieval-augmented generation, deep-read the top papers, and compare the methods.
```

Your AI will:

1. Search **Semantic Scholar**, **OpenAlex**, **arXiv**, **Crossref**, and **Europe PMC**
2. Find the open-access PDFs, not just abstracts
3. Download and read them cover to cover
4. Extract evidence chunks with source attribution
5. Render specific pages so it can *see* the figures and tables
6. Write a structured Markdown report
7. Save everything into your **Zotero** library

One prompt. Six academic databases. Real PDFs. Real citations.

---

## Why this exists

| | Paid "Deep Research" | This project |
|---|---|---|
| Reads actual PDFs | Nope. Web summaries. | Full text extraction |
| Figures and tables | Text only | Page rendering to PNG |
| Your library | Locked in their UI | Syncs to Zotero |
| Sources | Generic web search | 6 academic databases |
| Cost | $200/month | Free, MIT licensed |
| Your data | Their cloud | Your machine |

---

## Get started

```bash
git clone https://github.com/aytzey/deep-research.git
cd deep-research
uv venv && source .venv/bin/activate
uv sync
cp .env.example .env
uv run deep-research-mcp
```

Point your MCP client at it. Start asking questions.

<details>
<summary><strong>Claude Desktop config</strong></summary>

```json
{
  "mcpServers": {
    "deep-research": {
      "command": "uv",
      "args": ["--directory", "/path/to/deep-research", "run", "deep-research-mcp"],
      "env": {
        "OPENALEX_EMAIL": "you@example.com",
        "UNPAYWALL_EMAIL": "you@example.com",
        "ZOTERO_LOCAL": "true"
      }
    }
  }
}
```

Full config: [examples/claude-desktop.mcp.json](examples/claude-desktop.mcp.json)
</details>

<details>
<summary><strong>Codex config</strong></summary>

```toml
[mcp_servers.deep_research]
command = "uv"
args = ["--directory", "/path/to/deep-research", "run", "deep-research-mcp"]

[mcp_servers.deep_research.env]
OPENALEX_EMAIL = "you@example.com"
UNPAYWALL_EMAIL = "you@example.com"
ZOTERO_LOCAL = "true"
```

Full config: [examples/codex.config.toml](examples/codex.config.toml)
</details>

<details>
<summary><strong>Streamable HTTP mode</strong></summary>

```bash
uv run deep-research-mcp --transport streamable-http --host 127.0.0.1 --port 8000 --path /mcp
```
</details>

---

## Tools

| Tool | What it does |
|---|---|
| `research_topic` | Full pipeline: search, download, report, Zotero sync |
| `deep_read_topic` | Everything above + full-text extraction with evidence chunks |
| `render_pdf_pages` | PDF pages to PNG for figure and table inspection |
| `search_literature` | Fine-grained multi-source academic search |
| `find_similar_papers` | Related work expansion from a seed paper |
| `inspect_open_access_pdf` | OA availability check and PDF preview |
| `extract_local_pdf_text` | Text extraction from any local PDF |
| `search_libgen` | Supplementary shadow library search |
| `list_zotero_collections` | Browse your Zotero library |
| `healthcheck` | Verify all connections are up |

---

## Who uses this

**PhD students** that don't want to spend a week on a literature review. Point it at your thesis topic, get back a structured comparison with real citations and the PDFs already in your Zotero.

**Research labs** that want to scan preprints weekly and auto-file them. Run `research_topic` on a schedule and keep your group library current.

**AI builders** that need their agents to work with real academic papers instead of web scraping snippets. This is the MCP server you've been looking for.

---

## How it works

```
Topic --> Search 6 databases --> Resolve OA PDFs --> Download
  --> Deep Read full text --> Extract evidence --> Render figures
  --> Markdown report --> Zotero sync
```

**Source priority** (OA-first by design):

1. Semantic Scholar open PDFs
2. OpenAlex OA locations
3. arXiv
4. Europe PMC
5. Unpaywall
6. Direct publisher links

No paywalls. No scraping. Real open-access academic papers.

---

## Configuration

```bash
OPENALEX_EMAIL=you@example.com
UNPAYWALL_EMAIL=you@example.com
SEMANTIC_SCHOLAR_API_KEY=           # optional, higher rate limits

# Local Zotero integration
ZOTERO_LOCAL=true
ZOTERO_LIBRARY_TYPE=user
ZOTERO_CONNECTOR_URL=http://127.0.0.1:23119/connector/saveItems
ZOTERO_BRIDGE_URL=http://127.0.0.1:24119

# Web Zotero API (alternative to local)
ZOTERO_LIBRARY_ID=
ZOTERO_API_KEY=

# Institutional networks
HTTP_PROXY=
HTTPS_PROXY=
SSL_CERT_FILE=
```

## Local Zotero setup

Set `ZOTERO_LOCAL=true`, make sure Zotero is running with the local API enabled, install a bridge plugin for full write support, and run `healthcheck` to verify.

Tested with Zotero 8.0.4 on Linux (Flatpak). Works with any standard desktop install.

---

## Project structure

```
src/deep_research_mcp/
  server.py              MCP tools and pipeline orchestration
  config.py              Environment and settings
  services/
    academic.py          Multi-source scholarly search
    open_access.py       OA resolution and PDF downloads
    deep_read.py         Full-text extraction and page rendering
    zotero.py            Local and web Zotero integration
    reporting.py         Markdown report generation
    libgen.py            Supplementary LibGen support
```

Architecture details: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## For AI agents

If you're an agent reading this repo:

- [AGENTS.md](AGENTS.md) -- shared operating guide
- [CLAUDE.md](CLAUDE.md) -- Claude Desktop and Claude Code setup
- [CODEX.md](CODEX.md) -- Codex setup
- [docs/CLIENTS.md](docs/CLIENTS.md) -- side-by-side client comparison

---

## Contributing

PRs welcome. The most impactful areas:

- New scholarly source adapters
- Better OA resolution logic
- PDF parsing improvements
- More MCP client configs

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

MIT. Do whatever you want with it.

If this helps your research, [star the repo](https://github.com/aytzey/deep-research) and tell a colleague about it.
