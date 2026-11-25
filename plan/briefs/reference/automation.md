# Brief: `reference/automation`

| Field | Value |
| --- | --- |
| Title | Protocol, errors, CLI |
| Kind | R |
| Size | M |
| Tracks | - |
| Needs | `automation/json-rpc` |
| From | automation ch. 10 |
| Unit | `plan/allocation/reference.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `reference/automation` — Protocol, errors, CLI

**Covers.** The paragraph on top says what the page is: the facts an automation client needs, for a reader who writes
a client or reads an error. The tables, in this order. (1) `StrataCLI`'s usage, generated from its usage text
(`call`, `list`, `status`, `launch`, `mcp`, with their connection options) and its exit codes (0 success, 1 the editor
answered with an error, 2 no editor reachable, and the others the usage text lists). (2) The error codes, parsed from
`JsonRpc.h`: the five of JSON-RPC 2.0 and Strata's six (`Unauthorized`, `ConnectionClosed`, `Timeout`, `ServerBusy`,
`OperationFailed`, `Cancelled`), and how the editor's command errors map onto them. (3) The built-in methods the
server serves before and after the handshake. (4) The limits, parsed: the message size and depth limits, the client
limit, the pre-authentication limits, the stalled-client timeout, the reply bound and the idle timeout's default. (5)
The MCP server's generic tools (`strata_describe` among them) and the toolsets, generated from `McpToolsets.cpp`: each
toolset with its commands and the size budget of `core` (its count from `values.json` or the test that pins it). (6) The
environment variables Strata's programs read, one row each with the program and what it changes:
`STRATA_EDITOR_PATH`, `STRATA_EDITOR_PORT`, `STRATA_EDITOR_TOKEN`, `STRATA_SESSION_DIR` (automation),
`STRATA_EXTERNAL_EDITOR`, `STRATA_RECENT_PROJECTS`, `STRATA_SCRIPT_BUILDS_DIR` (the editor),
`STRATA_RUNTIME_DIR` and `STRATA_ERROR_DIALOG_FILE` (every program); a hand-checked table, since no route lists them.
Hand-written besides: one introduction per table, a note that the token never crosses the wire and never appears in
a dump, and `## Where it lives in Strata` (`Strata/src/Strata/Network/`, `StrataCLI/src/CLI/`,
`StrataEditor/src/Editor/EditorAutomation*`). The tools are `tools/reference.py parse` (route "program options" for
the CLI, and the parses of the error codes, the limits and the toolsets that the answer to reference-q3 adds to
`../pipelines.md` §7.1).

**Leaves out.**

- Sockets, framing and JSON-RPC → `automation/json-rpc`
- The server's threads and limits, with their reasons → `automation/rpc-server`
- The handshake and the security model → `automation/security`
- Sessions, discovery and launching → `automation/sessions`
- The MCP server and how commands become tools → `automation/mcp`
- Every command → `reference/commands`
- The editor's own options → `reference/editor`
- Driving the editor from the CLI, for game makers → `make/commands`

**Fit.** `fits`: about 1,500 words against M (3,000). The generated tables give the page its size: the CLI's usage and
exit codes, the error codes, the built-in methods, the limits and the toolsets with their commands, about 1,500 words.
The prose is the paragraph on top, six introductions, the environment table (9 rows), one note and the strip.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `automation:55-56` | feature | link | The message size and depth limits |
| `automation:60` | feature | link | The error codes |
| `automation:67` | feature | link | The built-in methods |
| `automation:74` | feature | link | The pre-authentication limits |
| `automation:76` | feature | link | The client limit |
| `automation:78-79` | feature | link | The stalled-client timeout and bounded replies |
| `automation:123` | feature | link | `STRATA_SESSION_DIR` |
| `automation:132` | feature | link | How command errors map to error codes |
| `automation:136` | feature | link | The idle timeout |
| `automation:192-194` | feature | link | The CLI's commands, exit codes and argument parsing |
| `automation:197` | feature | link | Endpoint discovery and the variables it reads |
| `automation:199-201` | feature | link | Launching, the editor's path and the token on the command line |
| `automation:208` | feature | link | The MCP server's generic tools |
| `automation:211` | feature | link | The toolsets |
| `automation:213-214` | feature | link | The size budget of the toolsets and `strata_describe` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Sockets, framing and JSON-RPC | `automation/json-rpc` | must |
| The MCP server and its toolsets | `automation/mcp` | helps |
| A command line with options; environment variables | `basics/tools` | helps |
| The security model | `automation/security` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-reference-2 | should | shape | `reference/physics`, `reference/animation`, `reference/audio-input`, `reference/ui`, `reference/worlds-runtime`, `reference/editor`, `reference/automation`; some tables of `reference/renderer`, `reference/assets`, `reference/build` | The catalogue pages and `reference/scene`, `reference/core` and `reference/settings` name the teaching page of each group or table. These area pages plan only "one introduction per table", and their Covers never says that an introduction names where the subject is taught, so a reader who looks up a limit, a format or a service cannot go on to the page that explains it. | Each of these Covers says that every table introduction names the page that teaches its subject, one sentence each (about 20 words a table, about 40 tables, about 800 words in all; kind R has no size check). On `reference/renderer` this concerns the bindings, switches, fallbacks and device tables; on `reference/assets` the types, importers, budgets and statistics; on `reference/build` the options, presets, labels and shards. | `allocation/reference.md:480`, `:567`, `:629-630`, `:689`, `:744-745`, `:801`, `:867`, `:930`, `:1050`, `:394-395`; compare `:110-111`, `:190`, `:263`, `:328`, `:989` |
| critic-reference-11 | should | missing-item | `reference/automation`, table (6) | The environment table lists Strata's own nine variables but no system variable that changes what the programs do: `CXX`, which picks the compiler of script builds when the compiler the engine was configured with is not on the machine (a release archive on Linux or macOS), and `XDG_DATA_HOME`, `XDG_RUNTIME_DIR` and `XDG_CACHE_HOME`, which move the user data and runtime folders on Linux. A search for `CXX` and `XDG_` in the plan finds nothing. | Table (6) gets a second part, "system variables Strata reads", one row each with the program and the effect, checked against `ScriptToolchain.cpp` and `PosixPlatform.cpp`, and a row for `STRATA_SLANG_ROOT` that names `reference/build`. About 80 words. | `allocation/reference.md:926-929`; `StrataEditor/src/Editor/ScriptToolchain.cpp:368-381`; `StrataEditor/src/Editor/ScriptBuild.cpp:400`; `Strata/src/Platform/Posix/PosixPlatform.cpp:356-362`, `:418-437`; `Strata/src/Strata/Core/Platform.h:71-77`, `:115-127` |
