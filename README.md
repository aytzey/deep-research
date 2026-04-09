![Deep Research](docs/hero.svg)

# Academic Research MCP

**Open-source Deep Research that actually reads the papers.**

Everyone's selling "Deep Research" behind paywalls. They scrape some web results, summarize a few abstracts, and call it analysis.

This does what they don't. It downloads the actual PDFs, reads them cover to cover, pulls out evidence with citations, renders the figures so your AI can see them, and saves everything to your Zotero library. It works with Claude, Codex, and any MCP client.

[![CI](https://github.com/aytzey/academic-research-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/aytzey/academic-research-mcp/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](pyproject.toml)
[![GitHub stars](https://img.shields.io/github/stars/aytzey/academic-research-mcp?style=social)](https://github.com/aytzey/academic-research-mcp/stargazers)

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
| Sources | Generic web search | 6 academic databases + Sci-Hub + LibGen |
| Cost | $200/month | Free, MIT licensed |
| Your data | Their cloud | Your machine |

---

## Prerequisites

### 1. Install Zotero

Download and install [Zotero](https://www.zotero.org/download/) for your platform.

**Linux:**

```bash
# Download
curl -sL "https://www.zotero.org/download/client/dl?channel=release&platform=linux-x86_64" -o /tmp/zotero.tar.xz

# Extract to /opt
sudo tar -xJf /tmp/zotero.tar.xz -C /opt/

# Create symlink
sudo ln -sf /opt/Zotero_linux-x86_64/zotero /usr/local/bin/zotero

# Create desktop entry
sudo cp /opt/Zotero_linux-x86_64/zotero.desktop /usr/share/applications/zotero.desktop
sudo sed -i "s|Exec=.*|Exec=/opt/Zotero_linux-x86_64/zotero %u|" /usr/share/applications/zotero.desktop
sudo sed -i "s|Icon=.*|Icon=/opt/Zotero_linux-x86_64/icons/icon128.png|" /usr/share/applications/zotero.desktop
```

**macOS / Windows:** Download from [zotero.org/download](https://www.zotero.org/download/) and run the installer.

### 2. Enable Zotero local API

Open Zotero, go to **Edit > Settings > Advanced** and check **"Allow other applications on this computer to communicate with Zotero"**.

Or add to your Zotero `prefs.js`:

```
user_pref("extensions.zotero.httpServer.localAPI.enabled", true);
```

Verify it works:

```bash
curl http://127.0.0.1:23119/api/users/0/collections
# Should return [] (empty array) or your collections
```

### 3. Install Zotero MCP (library management)

[zotero-mcp](https://github.com/54yyyu/zotero-mcp) provides full Zotero library management: search, annotations, notes, PDF import, collection management, and more.

```bash
uv tool install zotero-mcp-server
```

This gives you the `zotero-mcp` command. No additional setup needed if Zotero is running with the local API enabled.

### 4. Install uv (if you don't have it)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Get started

```bash
git clone https://github.com/aytzey/academic-research-mcp.git
cd academic-research-mcp
uv venv && source .venv/bin/activate
uv sync
cp .env.example .env    # edit with your email
uv run deep-research-mcp
```

---

## MCP client setup

This project provides two MCP servers that work together:

| Server | What it does |
|---|---|
| **academic-research** | Paper discovery, PDF download, deep reading, evidence extraction, Sci-Hub/LibGen |
| **zotero** | Full Zotero library management: search, annotations, notes, imports, collections |

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "academic-research": {
      "command": "uv",
      "args": ["--directory", "/path/to/academic-research-mcp", "run", "deep-research-mcp"],
      "env": {
        "OPENALEX_EMAIL": "you@example.com",
        "UNPAYWALL_EMAIL": "you@example.com",
        "ZOTERO_LOCAL": "true",
        "SCIHUB_ENABLED": "false"
      }
    },
    "zotero": {
      "command": "zotero-mcp",
      "env": {
        "ZOTERO_LOCAL": "true"
      }
    }
  }
}
```

### Claude Code

```bash
# Add academic-research server
claude mcp add --scope user academic-research -- uv --directory /path/to/academic-research-mcp run deep-research-mcp

# Add zotero server
claude mcp add --scope user zotero -- zotero-mcp

# Verify both are connected
claude mcp list
```

Then set environment variables in `~/.claude.json` under each server's `env` block:

```json
{
  "academic-research": {
    "env": {
      "OPENALEX_EMAIL": "you@example.com",
      "UNPAYWALL_EMAIL": "you@example.com",
      "ZOTERO_LOCAL": "true",
      "SCIHUB_ENABLED": "false"
    }
  },
  "zotero": {
    "env": {
      "ZOTERO_LOCAL": "true"
    }
  }
}
```

### Codex

Add to `~/.codex/config.toml`:

```toml
[mcp_servers.academic_research]
command = "uv"
args = ["--directory", "/path/to/academic-research-mcp", "run", "deep-research-mcp"]

[mcp_servers.academic_research.env]
OPENALEX_EMAIL = "you@example.com"
UNPAYWALL_EMAIL = "you@example.com"
ZOTERO_LOCAL = "true"
SCIHUB_ENABLED = "false"

[mcp_servers.zotero]
command = "zotero-mcp"
args = []

[mcp_servers.zotero.env]
ZOTERO_LOCAL = "true"
```

### Streamable HTTP mode

```bash
uv run deep-research-mcp --transport streamable-http --host 127.0.0.1 --port 8000 --path /mcp
```

---

## Tools

### Academic Research MCP

| Tool | What it does |
|---|---|
| `research_topic` | Full pipeline: search, download, report, Zotero sync |
| `deep_read_topic` | Everything above + full-text extraction with evidence chunks |
| `render_pdf_pages` | PDF pages to PNG for figure and table inspection |
| `search_literature` | Fine-grained multi-source academic search |
| `find_similar_papers` | Related work expansion from a seed paper |
| `inspect_open_access_pdf` | OA availability check and PDF preview |
| `extract_local_pdf_text` | Text extraction from any local PDF |
| `search_scihub` | Search Sci-Hub by DOI, title, or keyword (opt-in) |
| `download_scihub_paper` | Download a paper via Sci-Hub by DOI (opt-in) |
| `search_libgen` | Supplementary shadow library search |
| `healthcheck` | Verify all connections are up |

### Zotero MCP ([54yyyu/zotero-mcp](https://github.com/54yyyu/zotero-mcp))

| Tool | What it does |
|---|---|
| `zotero_search_items` | Keyword search across your library |
| `zotero_get_item_fulltext` | Full text of any item |
| `zotero_get_annotations` | Extract PDF annotations with page numbers |
| `zotero_get_notes` | Retrieve notes attached to items |
| `zotero_create_note` | Add notes to items |
| `zotero_add_by_doi` | Import paper by DOI (auto-fetches metadata + OA PDF) |
| `zotero_add_by_url` | Import from arXiv, DOI URLs, or webpages |
| `zotero_create_collection` | Create new collections |
| `zotero_manage_collections` | Add/remove items from collections |
| `zotero_get_recent` | Recently added items |
| `zotero_find_duplicates` | Identify duplicate entries |

Full tool list: [zotero-mcp documentation](https://github.com/54yyyu/zotero-mcp#readme)

---

## Sci-Hub integration (opt-in)

Sci-Hub access is **disabled by default**. When enabled, it acts as a fallback for papers that are not available through open-access channels. To opt in, set:

```bash
SCIHUB_ENABLED=true
```

You can also customize mirrors:

```bash
SCIHUB_MIRRORS=https://sci-hub.se,https://sci-hub.st,https://sci-hub.ru
```

Once enabled, you can use `search_scihub` and `download_scihub_paper` directly, or pass `include_scihub=True` to `research_topic` / `deep_read_topic` for automatic fallback when OA PDFs are unavailable.

> **Disclaimer:** Sci-Hub integration is provided strictly for **educational and research purposes**. The authors of this project do not host, operate, or maintain Sci-Hub. Users are solely responsible for ensuring that their use of Sci-Hub complies with all applicable laws and institutional policies in their jurisdiction. By enabling this feature, you acknowledge that the authors do not endorse, encourage, or condone copyright infringement of any kind. Use this tool responsibly and in accordance with copyright laws.

---

## Who uses this

**PhD students** that don't want to spend a week on a literature review. Point it at your thesis topic, get back a structured comparison with real citations and the PDFs already in your Zotero.

**Research labs** that want to scan preprints weekly and auto-file them. Run `research_topic` on a schedule and keep your group library current.

**AI builders** that need their agents to work with real academic papers instead of web scraping snippets. This is the MCP server you've been looking for.

---

## How it works

```
Topic --> Search 6 databases --> Resolve OA PDFs --> Download
  --> [Sci-Hub fallback if enabled] --> Deep Read full text
  --> Extract evidence --> Render figures
  --> Markdown report --> Zotero sync
```

**Source priority** (OA-first by design):

1. Semantic Scholar open PDFs
2. OpenAlex OA locations
3. arXiv
4. Europe PMC
5. Unpaywall
6. Direct publisher links
7. Sci-Hub (opt-in fallback, disabled by default)
8. LibGen (supplemental, best-effort)

No paywalls by default. No scraping. Real open-access academic papers.

---

## Configuration

```bash
OPENALEX_EMAIL=you@example.com
UNPAYWALL_EMAIL=you@example.com
SEMANTIC_SCHOLAR_API_KEY=           # optional, higher rate limits

# Local Zotero integration
ZOTERO_LOCAL=true
ZOTERO_LIBRARY_TYPE=user

# Web Zotero API (alternative to local)
ZOTERO_LIBRARY_ID=
ZOTERO_API_KEY=

# Sci-Hub (disabled by default)
SCIHUB_ENABLED=false
SCIHUB_MIRRORS=https://sci-hub.se,https://sci-hub.st,https://sci-hub.ru

# Institutional networks
HTTP_PROXY=
HTTPS_PROXY=
SSL_CERT_FILE=
```

---

## Project structure

```
src/deep_research_mcp/
  server.py              MCP tools and pipeline orchestration
  config.py              Environment and settings
  services/
    academic.py          Multi-source scholarly search
    open_access.py       OA resolution and PDF downloads
    scihub.py            Sci-Hub paper resolution (opt-in)
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

## Disclaimer

This tool is designed for **academic research and educational purposes only**. The authors do not endorse or encourage any form of copyright infringement.

- Open-access features use only legal, publicly available sources (Semantic Scholar, OpenAlex, arXiv, Europe PMC, Unpaywall).
- Sci-Hub and LibGen integrations are **disabled by default** and provided as opt-in features. Users who enable these features are solely responsible for compliance with their local laws and institutional policies.
- The authors of this project do not host, operate, or control any third-party services referenced herein.

Please use this tool responsibly and respect intellectual property rights.

---

## License

MIT. Do whatever you want with it.

If this helps your research, [star the repo](https://github.com/aytzey/academic-research-mcp) and tell a colleague about it.
