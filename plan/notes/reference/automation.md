# Notes: reference/automation

## New terms

None proposed. The page defines the toolset in bold (a term of the glossary's choosing; none homed here).

## Requests

None.

## Not verified

- Whether `strata_list_methods` is listed to clients: the code handles it and counts it as generic, but the guide counts five generic tools; the page lists five.
- The error a client sees for a reply over the message size (the code was not read).
- Behavior of the sign-in when a ping arrives first: taken from the header comment of `RpcServer.h` and the first-request messages at `RpcServer.cpp:1074`.

## Findings not applied

- critic-reference-2: applied (each introduction names its teaching page).
- critic-reference-11: applied for `CXX` and the three `XDG_` variables; the `STRATA_SLANG_ROOT` row is a sentence linking `reference/build`, which is not checked for existence at the pin.

## Hand-written tables

- Error codes: `Strata/src/Strata/Network/JsonRpc.h`.
- Command error mapping: `StrataEditor/src/Editor/EditorAutomation.cpp` (`ToRpcResult`).
- Built-in methods: `Strata/src/Strata/Network/RpcServer.h`, `RpcServer.cpp`.
- Limits: `JsonRpc.h`, `RpcServer.h`, `RpcServer.cpp`, `StrataCLI/src/CLI/McpServer.h` (idle default 600), `EditorApplication.cpp`.
- MCP generic tools: `StrataCLI/src/CLI/McpServer.cpp`.
- Environment variables: `CliApplication.cpp`, `EditorLauncher.cpp`, `EditorSession.cpp`, `ExternalEditor.cpp`, `RecentProjects.h`, `ScriptBuild.cpp`, `PosixPlatform.cpp`, `WindowsPlatform.cpp`, `Application.cpp`, `ScriptToolchain.cpp`.

## Clerk

- Refused: the bold words the page defines locally (toolset, homed on automation/mcp) are not admitted: a reference page restates terms whose homes are their chapters, and the page proposed none.

## Pin move to v0.8.0

- Rechecked at 319075e3 against 822a7a46: `JsonRpc.h`, `RpcServer.h`/`.cpp`, `McpServer.h`/`.cpp` and `EditorAutomation.cpp` did not change, so the error, mapping, method, limit and tool tables stand row by row; the variables read by `CliApplication.cpp`, `EditorLauncher.cpp` and the other files are the same nine plus four.
- The options table gained `--window-size` and `--ui-scale` on `launch`: a paragraph after it says that `StrataCLI` checks both before it starts the editor (exit code 3, `ReportUsageError`) and that a launch whose editor ended names its exit code and log (`EditorLauncher.cpp`).
