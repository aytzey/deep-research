# From a paper title to the full document

This example checks whether a whole paper reaches the agent over MCP. It is a recorded
transport check from 7 September 2026, not a simulated conversation or a claim about an AI's understanding.

## Try it with your agent

After [installing Paper Pilot](../README.md#quick-start), ask:

> Use Paper Pilot to find “Attention Is All You Need”. Read the full paper, inspect the
> architecture figure, and explain the method and its limitations with PDF page citations.
> Tell me which version you read and whether any pages were unreadable.

For a repeatable document choice, use [arXiv 1706.03762v7](https://arxiv.org/abs/1706.03762v7).
Search results and PDF versions can change, so compare the actual file hash before comparing counts.

## Recorded result

The [verification JSON](full-text-verification.json) contains the paper identity, PDF hash,
batch cursors, byte-transfer checks, and limitations. Machine-specific local paths were removed
from the original local receipts; the measured values were retained.

| Text response | Characters | PDF pages touched | Next position |
|---|---:|---|---|
| 1 | 12,000 | 1–5 | Page 5, character 551 |
| 2 | 12,000 | 5–8 | Page 8, character 2,564 |
| 3 | 12,000 | 8–12 | Page 12, character 2,069 |
| 4 | 3,498 | 12–15 | End of document |

The same page can span two responses. Concatenating the responses produced exactly the
39,498 characters extracted from all 15 pages, including the references. The original PDF
contained 2,215,244 bytes; both MCP resource retrieval and requested base64 embedding returned
identical bytes. A rendered page also reached the client as an image block.

One provider returned a rate-limit warning during discovery. The other sources completed
the access path; that warning is counted in the receipt.

## Reproduce the transport check

These are calls for an MCP client, not Python functions to paste into a shell:

1. Call `inspect_open_access_pdf(pdf_url="https://arxiv.org/pdf/1706.03762v7")`.
2. Call `read_pdf_text(pdf_path=<returned pdf_path>)` starting at page 1, character 0.
3. Save every response's text segments in order. Pass the same `pdf_path` and each
   `next_cursor.start_page` / `next_cursor.start_char` into the next call until the cursor is null.
4. Check extraction warnings. Compare the joined text with extraction from every page of the
   downloaded file; PDF page labels in formatted reports are not part of the extracted text.
5. Call `read_pdf_document` and retrieve its resource, or request `embed_base64=true` if supported.
   Compare the delivered PDF bytes with the downloaded file. Use `render_pdf_pages` for figures.

The [reading guide](../docs/READING.md) explains response limits and PDF delivery choices.

## A case across disciplines

The same reading path was checked with two papers relevant to the soil-pH design prompt:

| Paper | Copy checked | Pages | Characters | Responses |
|---|---|---:|---:|---:|
| [Distributable screen-printed soil pH sensor demonstrates robust response across variable soil conditions](https://doi.org/10.1038/s41598-026-57457-7) | Accepted manuscript | 24 | 60,332 | 6 |
| [Espial: Electrochemical Soil pH Sensor for In Situ Real-Time Monitoring](https://doi.org/10.3390/mi14122188) | Downloaded article | 13 | 35,831 | 3 |

Both complete extracted texts were delivered: 37 pages, 96,163 characters, nine responses.
This does not select a sensor or validate a circuit. Comparing measurement conditions,
calibration, and contrary results is the next research task for the agent.

## What this proves

Paper Pilot can deliver complete extracted text and original PDF bytes through MCP. The check
does not prove model comprehension, correct figure interpretation, exhaustive literature search,
or the behavior of a specific Codex/Claude UI session. Scans without readable text remain explicit gaps.
