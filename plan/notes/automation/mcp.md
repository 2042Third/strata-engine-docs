# Notes: automation/mcp

## New terms

None proposed. The page defines the glossary terms it homes in bold: StrataCLI, toolset, core toolset, generic tools, MCP, MCP client, server, compact definition, progress token. `structuredContent` and `tools/list_changed` are defined as bold code spans, but the lint's term-defined check does not recognise them (see Not verified).

## Requests

- Words: none proposed; every flagged word was replaced.
- Host for Further reading: jsonrpc.org (the JSON-RPC 2.0 specification), cited without a link.
- Text captures of `StrataCLI status`, `launch`, `list`, a failing `call` and `--save-image`, and Claude Code's tool list, were not requested as figures: they need a running editor. The page shows the same calls in an `sh` fence with their exit codes.
- Glossary: the entries for `structuredContent` and `tools/list_changed` are not matched by the term-defined check when written as bold text or bold code; the planner may need to add names or aliases.

## Since

0.3.0: StrataCLI, MCP server (Docs/Releases/0.3.0.md:90-99); toolsets and compact definitions 0.4.0 (Docs/Releases/0.4.0.md:80-82); `settings` toolset 0.6.0.

## Not verified

- A running editor's actual `tools/list` size in bytes: `CLI.McpToolsets` prints it but was not run (no build at the pin); the page gives only the limits (32 tools, 30,720 bytes).
- That `StrataCLI call entity.makeCoffee` (an unknown method) makes the editor answer with an error code other than timeout or closed connection (exit 1): inferred from `ReportCallFailure`.
- That Claude Code lists the tools under its own prefixed names; the page does not say.
- The parameter schema of `viewport.capture` and the exact text of `entity.create`'s later sentences beyond the first.
- MCP revisions allowing batches (2025-03-26): the code answers arrays regardless of version.
- The glossary terms `structuredContent` and `tools/list_changed` and the lint's term-defined check (above).

## Findings not applied

- The brief's text captures (automation:586, :588) are not placed as figures; see Requests.
- The error-map and toolset figures (automation:562, :566): the error map is a Mermaid diagram; the toolset tables are in prose and a quote, with no bar chart of sizes, because the sizes need a run of `CLI.McpToolsets`.
- Exercise automation:681 and :692 are worked in prose answers; no patch under tutorials/ was written.
- Item new:5, new:6, new:4: applied (the page writes `:value` keys, never the guide's counts, and takes the toolsets from the table). The instructions text's list of eleven toolsets is not repeated.

## Clerk

- Nothing to admit.
- Admitted to external-hosts.txt: www.jsonrpc.org (its front page is the JSON-RPC site).
- Left for the planner: the glossary entries `structuredContent` and `tools/list_changed`, whose code names term-defined cannot match.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
