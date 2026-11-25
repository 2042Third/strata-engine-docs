# Brief: `automation/mcp`

| Field | Value |
| --- | --- |
| Title | StrataCLI and its MCP server |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `automation/sessions` |
| From | automation ch. 9 (the MCP protocol, commands mapped to tools, results and images, toolsets and the token budget, compact definitions, descriptions written for agents); StrataCLI's structure (`StrataCLILib`, stdout for the protocol and stderr for logs, `ImageOutput`'s strict base64) |
| Unit | `plan/allocation/automation.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `automation/mcp` — StrataCLI and its MCP server

**Covers.** The job: StrataCLI as a program, and its MCP server, which offers the editor's commands to a client built
on a language model as tools. The problem in one paragraph that links `automation/agents` (what a tool costs an agent,
and why toolsets exist). The Model Context Protocol from zero: a dialect of JSON-RPC over the standard streams of a
child process; `initialize` with its protocol versions and the `instructions` for the model,
`notifications/initialized`, `ping`, `tools/list`, `tools/call`, the notice that the list changed, progress tokens, and
batches for clients of the 2025-03-26 revision. The map: StrataCLI's structure, a thin `main` over `StrataCLILib`,
which the tests link and which links only the `Network` layer; inside it `CliApplication`, the `EditorConnection` and
`EditorLauncher` that the CLI and the MCP server share, `McpServer`, `McpToolsets` and `ImageOutput`. The contract,
rule by rule with its reason: standard output carries only results and the protocol, logs go to standard error, and the
streams are binary; the default list stays within 32 tools and 30 KiB, so a command added to `core` takes another's
place; the first sentence of a command's description says what it does; a timeout of the CLI (exit code 4) does not
mean the command failed, and another editor is never started because of it. A toy MCP server of about 60 lines that
lists two commands as tools and calls them. The real code: `main` and the CMake file; `MakeToolName`,
`MakeToolInputSchema` and `MakeToolResult` (errors as `isError` text with code and data, objects as text and
`structuredContent`, the `Image` field as image content, so that the model sees a capture); the toolset tables,
`GetGroupToolset` (exact names before prefixes, an unknown group named after itself) and the compact definitions
(`FirstSentence`, cut at a word and never inside a UTF-8 sequence); `RunMcpServer`, a reader thread and a condition
variable with `wait_until`, so that the server ticks every two seconds when idle. Around them: the CLI's commands
(`call` with parameters inline, from `-` or from `@file`, `list`, `status`, `launch`, `mcp`), its exit codes 0 to 5,
its arguments, `--save-image` and the strict base64 decoder; the generic tools (`strata_status`,
`strata_launch_editor`, `strata_describe`, `strata_toolsets`, `strata_call`, and `strata_list_methods`, which answers
but is not listed); how the list behaves (only the generic tools without an editor, a tool outside the enabled toolsets
still answering by name, a method whose tool name is taken left out with a warning); the budget and the test that holds
it; launching from MCP (an editor reused, or started with `--idle-timeout 600`, and progress notifications that only
rise); the client's name passed on to the handshake. A history aside: until 0.4.0 every command was a tool. The
examples: Claude Code's list of tools after `claude mcp add strata -- StrataCLI mcp`, one `entity_create`, a
`viewport_capture` that the model sees as an image, and `strata_toolsets {enable: ["scene"]}` with the list-changed
notice; then the same calls from a terminal with `StrataCLI` and their exit codes. What the server does not do, in one
paragraph: tools only, the standard streams as its only transport, and no cancellation, so the editor finishes what it
started. Alternatives Strata did not choose; how it is tested (`CLI.Commands`, `CLI.Mcp`, `CLI.McpToolsets` with its
budget, `CLI.McpPresence`); changing it safely (a new command group goes into the toolset table, a new generic tool
keeps the budget). Counts and sizes come from `:value` keys, never from the guide. Afterwards the reader can say what
an agent sees of a command, put a command into a toolset without breaking the budget, and read StrataCLI's code.

**Leaves out.**

- Why tools for a language model are designed this way → `automation/agents`
- Discovery, pinning and launching, which the CLI and the MCP server share → `automation/sessions`
- Connecting Claude Code and making a game with an agent → `make/with-an-agent`
- Running one command with `StrataCLI call` → `editor/commands`
- Every option, exit code, generic tool and toolset in tables → `reference/automation`
- The commands themselves → `reference/commands`

**Fit.** `over`: about 6,600 words against L (5,000). The next size, XL (8,000), by S2: StrataCLI's structure adds a
whole program to the MCP server, with two excerpts and a figure of its own, beside the server's three excerpts, four
rules, four figures and three exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `automation:191-196` | feature | home | StrataCLI's structure, its commands, exit codes and arguments, image results with `--save-image`, logging to standard error |
| `automation:207-217` | feature | home | The protocol, the generic tools, commands as tools, the mapping of results, toolsets, compact definitions, the budget, `strata_describe`, launching from MCP, the client's name, the stream runner; and how the tool list behaves, in two sentences (about 80 words): with no editor connected `tools/list` holds only the generic tools (the test "Only the generic tools are listed without an editor", which the reader can run), a command outside the enabled toolsets still answers when its tool is called by name, and a method whose tool name is already taken (also by a generic tool) is not offered and a warning is logged (`StrataCLI/src/CLI/McpServer.cpp:426-436`, `:476-486`, `:770-797`; `StrataTests/src/CLI/McpServerTests.cpp:117`; `Docs/DeveloperGuide.md:6391-6392`) |
| `automation:236` | feature | home | The suite `CLI.Commands` |
| `automation:238` | feature | home | The suites `CLI.Mcp`, `CLI.McpToolsets` (32 tools, 30 KiB, every command in a known toolset) and `CLI.McpPresence` |
| `automation:514` | code | home | `StrataCLI/src/CLI/McpServer.cpp:180-254`: `MakeToolName`, `MakeToolInputSchema` and `MakeToolResult`, images as image content |
| `automation:516` | code | home | `StrataCLI/src/CLI/McpToolsets.cpp:153-184`: `FirstSentence` and `MakeCompactToolDefinition`, the cut that is safe for UTF-8; with the tables `:17-69` and `GetGroupToolset` `:123-137` |
| `automation:518` | code | home | `StrataCLI/src/CLI/McpServer.cpp:860-916`: `RunMcpServer`, a reader thread, a condition variable and `wait_until` for the ticks |
| `new:2` | code | home | `StrataCLI/CMakeLists.txt:1-19`: all logic in `StrataCLILib` so that tests link it, which links only `Strata::Network`; the executable is a thin `main` |
| `new:3` | code | home | `StrataCLI/src/Main.cpp:11-28`: binary standard streams, logging set up for standard error (`CliApplication.cpp:628-640`), `RunCli` called with the streams it may use |
| `automation:562` | figure | home | The toolsets: core's 27 commands, the other toolsets by group, the exact-name exceptions, the generic tools, and a bar of the default list against 30 KiB and against every command |
| `automation:566` | figure | home | The error map: command error kinds to JSON-RPC codes to the CLI's exit codes to MCP's `isError` |
| `automation:586` | figure | home | Text captures of `StrataCLI status`, `launch --headless --project` with its progress lines, `list`, a `call` that fails with exit code 1, and `--save-image` |
| `automation:588` | figure | home | An MCP client's view: Claude Code's tools after `claude mcp add`, and a `viewport_capture` shown to the model as an image |
| `automation:634-636` | rule | home | At most 32 tools and 30 KiB by default, a command added to `core` takes another's place; the first sentence of a description says what the command does |
| `automation:642` | rule | home | A CLI timeout (exit code 4) does not mean failure; never start another editor because of it |
| `automation:645` | rule | home | StrataCLI's standard output is protocol, logs go to standard error, the streams are binary |
| `automation:681` | hands-on | home | Exercise: register a Query command and see it in `StrataCLI list`, as a tool once its toolset is enabled and in the journal; the `CLI.McpToolsets` test fails until it is in a toolset; before it, `Editor.Journal` fails until the command is listed in `c_QueryCommands` (and in the lists of its flags), as every command is in exactly one kind list, the rule that `editor/commands` teaches and links (`StrataTests/src/Editor/CommandJournalTests.cpp:209-235`) |
| `automation:692` | hands-on | home | Exercise: a new generic tool (a search over descriptions) that keeps the 32-tool budget, with `CLI.Mcp` cases |
| `new:12` | hands-on | home | The "trace it yourself" exercise (D27), the first and easiest of the page's three (before `automation:681` and `:692`; about 200 words): follow one `tools/call` of `entity_create` with a debugger or a search, from the reader thread of `RunMcpServer` through `HandleLine`, `HandleMessage` and `HandleToolsCall` to the lookup in `m_ToolToMethod`, the editor connection's `Call` and `MakeToolResult`; say where a tool outside the enabled toolsets is still found and where an unknown tool's error is made. Evidence: `StrataCLI/src/CLI/McpServer.cpp:306`, `:354`, `:439`, `:476-492`, `:860-916` |
| `automation:766` | term | home | StrataCLI |
| `automation:769-770` | term | home | MCP (Model Context Protocol); MCP client and MCP server |
| `automation:772-775` | term | home | Toolset, core toolset, generic tools, compact definition |
| `automation:777-779` | term | home | `structuredContent`, `tools/list_changed`, progress token and `notifications/progress` |
| `automation:841` | open | home | The part's dating: StrataCLI, MCP, the journal, presence and the skills are in 0.3.0's notes (`Docs/Releases/0.3.0.md:90-99`); toolsets and compact definitions came in 0.4.0 (`Docs/Releases/0.4.0.md:80-82`; before them 121 tools cost about 27,000 tokens, `Docs/Roadmap.md:1262`), which is the history aside; the `settings` toolset in 0.6.0 (`Docs/Releases/0.6.0.md:108`); nothing dates the server, the handshake or pinning before 0.3.0, so no page gives them a date |
| `automation:844` | open | home | The counts: 27 core commands from the source and its test (`EditorMcpToolsetsTests.cpp:113`); the sizes of the tool lists from a run of `CLI.McpToolsets`, which prints them (`:124`); none typed from the guide |
| `new:4` | erratum | home | The inventories count 151, 153 and 154 editor commands (process.md's table, kind `inventory`). At the pin `StrataEditorCore` registers 151 commands (63 Edit, 46 Query, 42 Session) and the editor's window adds `editor.showPanel` and `editor.showDialog`, so a running editor offers more; the page never types the count and writes `:value{key="commands.count"}`. Evidence: `StrataTests/src/Editor/CommandJournalTests.cpp:102-164` (the three kind lists) and `:234` (the check of their total); `StrataEditor/src/EditorLayer.cpp:177`, `:233` |
| `new:6` | erratum | home | The guide gives the tool definitions of every command, about 99 KB, as those of "151 commands" (process.md's table, kind `engine`), and the inventory's budget row repeats it. The test that prints the figure counts the commands of `StrataEditorCore`'s registry; a running editor also registers `editor.showPanel` and `editor.showDialog`, and every command it registers is a tool. The page takes the figure from a run of `CLI.McpToolsets` (`automation:844`) and the count from `:value`, never from the guide. Evidence: `Docs/DeveloperGuide.md:6397-6398`; `StrataTests/src/Editor/EditorMcpToolsetsTests.cpp:31`, `:114-125`; `StrataEditor/src/EditorLayer.cpp:177`, `:233` |
| `new:5` | erratum | home | The toolsets as two texts give them (process.md's table, kind `engine`): the MCP server's `instructions` to the model name eleven toolsets besides `core` and leave out `settings`, and the guide's description of `settings` leaves out the prefix `graphics.`. The page takes the toolsets from the table, never from those texts. Evidence: `StrataCLI/src/CLI/McpServer.cpp:39-40`; `Docs/DeveloperGuide.md:6382-6385`; the table `StrataCLI/src/CLI/McpToolsets.cpp:43-69`, with `graphics.` at `:54` and `settings` at `:69`; `StrataTests/src/Editor/EditorMcpToolsetsTests.cpp:101-105` |
| `new:7` | not-done | home | What the MCP server does not do, in one paragraph that links `appendix/not-in-strata` (about 100 words): it offers tools only (`initialize` declares the `tools` capability alone: no resources, prompts or logging), the standard streams are its only transport, every notification but `notifications/initialized` is dropped, and nothing cancels a command once it is sent: a client that cancels, times out or disconnects loses only the answer, and the editor finishes the command, as it does after the CLI's exit code 4. Evidence: `StrataCLI/src/CLI/McpServer.cpp:367-372`, `:379-397`, `:420`; `StrataCLI/src/CLI/CliApplication.cpp:358-359` (standard input and output); `StrataCLI/src/CLI/CliApplication.h:24` (exit code 4: the command may still be running in the editor); `StrataTests/src/Editor/EditorAutomationTests.cpp:324` ("A client that disconnects while its command is pending loses only the answer"); `git grep -n -i "notifications/cancel" 822a7a46 -- StrataCLI Strata/src/Strata/Network` finds nothing |
| `automation:415` | concept | use | Tool design for language models, from `automation/agents` |
| `automation:197-199` | feature | use | Discovery, pinning and launching, from `automation/sessions`, as the MCP server reuses them |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| What a tool is for a language model, what its definition costs, and why toolsets exist | `automation/agents` | must |
| JSON-RPC 2.0: requests, notifications, ids, batches | `automation/json-rpc` | must |
| Discovery, pinning and launching an editor | `automation/sessions` | must |
| Standard streams, pipes and exit codes | `basics/tools` | must |
| A thread, a mutex, a condition variable and waiting until a time | `basics/threads` | must |
| Base64, and UTF-8 code units | `basics/data-formats` | must |
| Static libraries, executables and linking with CMake | `basics/build` | must |
| A command's description and its JSON Schema | `editor/commands` | must |
| Logging sinks | `core/conventions` | helps |
| Viewport captures and their image result | `editor/camera-viewport` | helps |
| The command catalogue | `reference/commands` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `structuredcontent` | `structuredContent` | - |
| `tools-list-changed` | `tools/list_changed` | - |
| `compact-definition` | Compact definition | - |
| `core-toolset` | Core toolset | - |
| `generic-tools` | Generic tools | - |
| `mcp` | MCP | Model Context Protocol |
| `mcp-client` | MCP client | - |
| `progress-token` | Progress token | notifications/progress |
| `server` | server | - |
| `stratacli` | StrataCLI | - |
| `toolset` | Toolset | - |
