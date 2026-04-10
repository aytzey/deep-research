# Client Guide

This document helps Claude and Codex users get started without reverse-engineering the repository.

## Which File To Read

- Generic agent instructions: [AGENTS.md](../AGENTS.md)
- Claude-specific setup and prompting: [CLAUDE.md](../CLAUDE.md)
- Codex-specific setup and prompting: [CODEX.md](../CODEX.md)

## Configuration Files

- Claude Desktop example: [examples/claude-desktop.mcp.json](../examples/claude-desktop.mcp.json)
- Codex example: [examples/codex.config.toml](../examples/codex.config.toml)

## Client Comparison

| Client | Best For | Config Format | Start Command |
| --- | --- | --- | --- |
| Claude Desktop | long-form research and synthesis | JSON | `uv run paper-pilot` |
| Codex | tool-driven iteration and repo work | TOML | `uv run paper-pilot` |

## Suggested Workflow

Use the same sequence in both clients:

1. `healthcheck`
2. `research_topic`
3. `deep_read_topic`
4. `render_pdf_pages` if visuals matter
5. `write_to_zotero=true` only after Zotero health is confirmed

## Prompt Starters

- `Research <topic>, deep-read the best OA papers, and summarize the evidence.`
- `Find the strongest papers on <topic>, render the important pages, and compare the figures and tables.`
- `Check local Zotero, then create a collection and sync the report and PDFs.`
