# CLAUDE.md

This file is the Claude-specific operating guide for `deep-research-mcp`.

## Best Fit

Claude is a good fit when you want:

- long-form literature synthesis
- evidence-backed comparison across multiple papers
- PDF-aware follow-up analysis after initial retrieval

## Setup

Use the config in [examples/claude-desktop.mcp.json](examples/claude-desktop.mcp.json) or adapt this block in Claude Desktop:

```json
{
  "mcpServers": {
    "deep-research": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/deep-research",
        "run",
        "deep-research-mcp"
      ],
      "env": {
        "OPENALEX_EMAIL": "you@example.com",
        "UNPAYWALL_EMAIL": "you@example.com",
        "ZOTERO_LOCAL": "true",
        "ZOTERO_LIBRARY_TYPE": "user",
        "ZOTERO_CONNECTOR_URL": "http://127.0.0.1:23119/connector/saveItems",
        "ZOTERO_BRIDGE_URL": "http://127.0.0.1:24119"
      }
    }
  }
}
```

## First Workflow To Try

1. Run `healthcheck`
2. Run `research_topic` on a concrete topic
3. Run `deep_read_topic` on the same topic
4. Use returned `pdf_path` values for follow-up inspection
5. Run `render_pdf_pages` when charts or methodology diagrams matter

## Claude Prompt Patterns

Use prompts like:

- `Research retrieval-augmented generation, deep-read the strongest OA papers, and summarize the methods, limitations, and open questions.`
- `Find the top papers on multimodal retrieval, render the pages with the main figures, and compare the architectures.`
- `Check Zotero health, then create a new collection and sync the report plus PDFs.`

## Claude-Specific Advice

- Prefer `deep_read_topic` over raw `search_literature` when you want evidence-backed synthesis quickly.
- If a claim depends on a figure or table, call `render_pdf_pages` instead of relying only on text extraction.
- If Zotero is part of the workflow, call `healthcheck` first and only request writes after local mode is healthy.

## Where Claude Should Look Next

- shared instructions: [AGENTS.md](AGENTS.md)
- architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- client matrix: [docs/CLIENTS.md](docs/CLIENTS.md)
