---
id: reference/automation
title: "Protocol, errors, CLI"
description: "The facts a client of the editor's automation interface needs: the command line, error codes, built-in methods, limits, toolsets and environment variables."
kind: reference
size: M
tracks: []
needs: [automation/json-rpc]
status: final
---

The editor serves commands to other programs over a network connection on your own machine. This page is for a person who writes such a client or who has to read an error one returns. Each table answers one question that comes up in that work, and each introduction names the page that teaches its subject. A row is one fact: a command, a code, a method, a limit, a tool or a variable.

## The command line client

`StrataCLI` is the program that talks to the editor for you. How a client connects, finds an editor and launches one is taught in [Sessions and discovery](../automation/sessions.md). The generated tables below come from the usage text of the program, so they cannot drift from what it prints. The usage lists the commands first, then the options that choose the editor, then the variables and the :term[exit codes]{id=exit-code}. A script should test the exit code, never the text.

::include{file="options-cli.md"}

The command `launch` checks the values of `--window-size` and `--ui-scale` itself, before it starts the editor, because nobody reads what that editor prints. A value the editor would refuse ends `StrataCLI` with exit code 3. When the editor ends before a client could reach it, the error names the editor's own exit code and its log file.

The token that proves who a client is never crosses the wire, and it never appears in a dump, a log or a table of this page. The client and the editor each prove they know it by sending a :term[hash]{id=hash} made from it. The option `--token` exists, but it shows the token to every other program on the machine, so the :term[environment variable]{id=environment-variable} is the better way. [The security model](../automation/security.md) explains the sign-in.

## Error codes

Every answer of the editor that fails carries an :term[integer]{id=integer} code and a message. The first five codes come from the :term[JSON-RPC 2.0]{id=json-rpc-2-0} standard. The next six are Strata's own, in the range the standard reserves for each implementation. The message says what went wrong; the code lets a program decide what to do. [Sockets, framing and JSON-RPC](../automation/json-rpc.md) teaches the message format.

The table is written by hand from `Strata/src/Strata/Network/JsonRpc.h`, where the codes are declared.

| Code | Name | Meaning |
| --- | --- | --- |
| -32700 | `ParseError` | The text is not valid :term[JSON]{id=json}, or nests deeper than the depth limit. |
| -32600 | `InvalidRequest` | The JSON is not a request object of version 2.0. |
| -32601 | `MethodNotFound` | The method does not exist. |
| -32602 | `InvalidParams` | The parameters do not fit the method. |
| -32603 | `InternalError` | The server failed while handling the request. |
| -32001 | `Unauthorized` | The connection has not signed in, or used a wrong token. |
| -32002 | `ConnectionClosed` | Client side: not connected, or the connection ended during the call. |
| -32003 | `Timeout` | Client side: no answer arrived in time. |
| -32004 | `ServerBusy` | The server refused a request or connection because of its limits. |
| -32005 | `OperationFailed` | The request was valid, but the method could not do it; the message says why. |
| -32006 | `Cancelled` | The request was abandoned before it finished, for example while the server shut down. |

A command that fails reports one of five kinds of error, and the editor turns the kind into a code. The table is written by hand from `EditorAutomation::ToRpcResult` in `StrataEditor/src/Editor/EditorAutomation.cpp`.

| Kind of command error | Code sent |
| --- | --- |
| Unknown command | `MethodNotFound` |
| Invalid parameters | `InvalidParams`, with the command name and its parameter schema in the data |
| Cancelled | `Cancelled` |
| Internal | `InternalError` |
| Failed (and any other) | `OperationFailed`, with the data the command gives, such as the users of an asset that cannot be deleted |

The schema in the `InvalidParams` data lets a client correct its request without asking again. The exit code of `StrataCLI` is coarser: 1 for any error the editor sent, whatever its code.

## Built-in methods

The server answers four methods itself, on its network thread, without waiting for the :term[main thread's]{id=main-thread} frame. Every name starts with `rpc.`, a prefix that commands may not use. Before the sign-in is complete the server accepts only the first two. A request of any other kind at that point closes the connection. [The editor's server](../automation/rpc-server.md) explains the threads, and [the security model](../automation/security.md) the sign-in.

The table is written by hand from the :term[header]{id=header} comment of `Strata/src/Strata/Network/RpcServer.h`.

| Method | Parameters | Result | Before the sign-in ends |
| --- | --- | --- | --- |
| `rpc.handshake` | a client nonce, and optionally a client name | a server nonce and a server proof | Must be the first request. |
| `rpc.authenticate` | a client proof | an answer that says the client is signed in | Must be the second request. |
| `rpc.ping` | none | an answer that says pong | Refused. |
| `rpc.listMethods` | none | each method's name, description and parameter schema | Refused. |

A nonce is a random value that is used only once, and a proof is the hash that shows its sender knows the token. After the sign-in, every editor command is also a method, under its own name such as `editor.quit`. The list that `rpc.listMethods` returns holds the built-ins first, then the commands in sorted order.

## Limits

A server that listens on a port must bound what a stranger can make it do. These limits are fixed in the source and none of them is a setting. [The editor's server](../automation/rpc-server.md) gives the reason for each. The table is written by hand from `Strata/src/Strata/Network/JsonRpc.h` and `Strata/src/Strata/Network/RpcServer.h`, with the constants in `RpcServer.cpp`.

| Limit | Value | What happens beyond it |
| --- | --- | --- |
| Message size | 64 MiB, in both directions | A longer line puts the reader in a permanent error, because the stream cannot be matched up again. A reply that is too large becomes an error. |
| Nesting depth | 256 levels of arrays and objects | The text is refused as a JSON error. |
| Request id length | 256 characters | The request is refused and the id is not echoed. |
| Method name in a message | 64 characters | The name is cut when an error message quotes it. |
| Signed-in clients | 8 | The next one gets `ServerBusy`. |
| Connections not signed in | 8 | A newcomer takes the place of the oldest one that had time to send. If all of them arrived in one burst, the newcomer is refused. |
| Message size before sign-in | 4 KiB | The connection closes. |
| Output waiting before sign-in | 16 KiB | The connection closes. |
| Time to finish the sign-in | 5 s | The connection closes. |
| Requests in flight for one client | 64 | The server stops reading that client until some finish. |
| Output waiting for one client | 1 MiB | The server stops reading that client until it takes some. |
| Queued requests for all clients | 1024 requests, 256 MiB | The server reads no more requests until the queue has room. |
| Stalled client | 30 s without accepting a :term[byte]{id=byte} of waiting output | The client is dropped. |
| Idle editor | the editor's own default is 0 (never); `StrataCLI mcp` asks for 600 s for the editors it starts | The editor closes itself after this long without a client. |

The idle row has two defaults because two programs choose. The editor's option `--idle-timeout` accepts 0 to a week in seconds, and 0 means never. The command `launch` passes the option on only when you give it, so a launched editor never closes itself by default. The command `mcp` passes 600 unless you say otherwise.

## The MCP server

The command `StrataCLI mcp` speaks the Model Context Protocol (MCP), which lets a program built on artificial intelligence (AI), an :term[AI agent]{id=ai-agent}, use the editor as a set of tools. [The MCP server](../automation/mcp.md) teaches how commands become tools. Five tools are always present, whatever the toolsets are.

The table is written by hand from the tool definitions in `StrataCLI/src/CLI/McpServer.cpp`.

| Tool | What it does |
| --- | --- |
| `strata_status` | Tells whether an editor is connected, with its session and the known sessions. |
| `strata_launch_editor` | Starts an editor, for a project if given, and connects to it. |
| `strata_describe` | Without arguments, lists the toolsets. With a toolset, lists its commands. With a command, gives its full description and :term[JSON Schema]{id=json-schema}. |
| `strata_toolsets` | Enables or disables toolsets, and returns the enabled ones and the number of editor tools. |
| `strata_call` | Calls any editor method by name, enabled as a tool or not. |

The server still answers an older tool name, `strata_list_methods`, but it does not list it.

A **toolset** is a named group of editor commands that the MCP server lists as tools. The generated table below names each group, and the table that follows it in the generated file lists the commands of every group. The default is `core`, and the option `--toolsets` takes names separated by commas, or `all`.

The size of the list matters because an agent reads it at the start of every conversation. The default list holds at most 32 tools and 30 KiB of JSON, and the test suite `CLI.McpToolsets` keeps it so. At the pin that is :value{key="toolsets.core.count"} commands of `core` plus the five tools above. The server shortens each description to its first sentence, so the opening sentence of each command's description has to say what the command does. `strata_describe` gives the full text.

::include{file="commands-toolsets.md"}

## Environment variables

A program reads these variables when it starts or when it first needs the thing they name. None holds a secret except the token. The table is written by hand from the places that read them, which are listed at the end of the page, because no generated table lists them.

| Variable | Read by | What it changes |
| --- | --- | --- |
| `STRATA_EDITOR_PORT` | `StrataCLI` | The explicit port of an editor, instead of discovery. |
| `STRATA_EDITOR_TOKEN` | `StrataCLI` | The token that goes with the port. Preferred over `--token`. |
| `STRATA_EDITOR_PATH` | `StrataCLI` | The editor program that `launch` and `mcp` start, instead of the one next to `StrataCLI`. |
| `STRATA_SESSION_DIR` | the editor and `StrataCLI` | The private folder of session files, instead of the user's default. |
| `STRATA_EXTERNAL_EDITOR` | the editor | The command that opens script files in the user's own :term[code editor]{id=code-editor}. |
| `STRATA_RECENT_PROJECTS` | the editor | The file that holds the list of recent projects. |
| `STRATA_SCRIPT_BUILDS_DIR` | the editor | The root folder of script builds, instead of the :term[user data folder's]{id=user-data-folder} `Builds`. |
| `STRATA_RUNTIME_DIR` | every program | The user's :term[runtime]{id=runtime} folder, instead of the system default. It must pass the same safety checks. |
| `STRATA_ERROR_DIALOG_FILE` | every program | A file that receives the text of a fatal error, instead of a dialog window. Tests use it. |

Strata also reads variables of the system. Another table, written by hand from `StrataEditor/src/Editor/ScriptToolchain.cpp` and `Strata/src/Platform/Posix/PosixPlatform.cpp`, lists them.

| Variable | Read by | What it changes |
| --- | --- | --- |
| `CXX` | the editor | The :term[compiler]{id=compiler} of script builds, when the compiler the engine was configured with is missing from the machine. A path or a program name. |
| `XDG_DATA_HOME` | every program, on Linux | The user data folder. A relative path is ignored. |
| `XDG_RUNTIME_DIR` | every program, on Linux | The first choice for the runtime folder. |
| `XDG_CACHE_HOME` | every program, on Linux | The next choice for the runtime folder. When it is not set, the `.cache` folder of the home folder takes its place. |

The variable `STRATA_SLANG_ROOT` belongs to the build, not to a running program: [the build reference](../reference/build.md) describes it.

## Where it lives in Strata

- `StrataCLI/src/CLI/CliApplication.cpp`: the usage text, the options, the exit codes and the variables of the client.
- `StrataCLI/src/CLI/EditorLauncher.cpp`: `STRATA_EDITOR_PATH` and the launch of an editor.
- `StrataCLI/src/CLI/McpServer.cpp`: the generic tools of the MCP server.
- `StrataCLI/src/CLI/McpToolsets.cpp`: the toolsets and the shortening of descriptions.
- `Strata/src/Strata/Network/JsonRpc.h`: the error codes, the message size and the depth limit.
- `Strata/src/Strata/Network/RpcServer.h`: the limits of clients, the stalled-client timeout and the built-in methods.
- `Strata/src/Strata/Network/RpcServer.cpp`: the limits before sign-in and the id length.
- `Strata/src/Strata/Network/EditorSession.cpp`: `STRATA_SESSION_DIR`.
- `StrataEditor/src/Editor/EditorAutomation.cpp`: how a command's error becomes a code, and the idle check.
- `StrataEditor/src/Editor/ExternalEditor.cpp`: `STRATA_EXTERNAL_EDITOR`.
- `StrataEditor/src/Editor/ScriptBuild.cpp`: `STRATA_SCRIPT_BUILDS_DIR`.
- `Strata/src/Platform/Posix/PosixPlatform.cpp`: `STRATA_RUNTIME_DIR` and the `XDG_` variables.
- `Strata/src/Platform/Windows/WindowsPlatform.cpp`: `STRATA_RUNTIME_DIR` on Windows.
- `StrataEditor/src/Editor/ScriptToolchain.cpp`: `CXX`.
- `StrataEditor/src/Editor/RecentProjects.h`: `STRATA_RECENT_PROJECTS`.
- `Strata/src/Strata/Core/Application.cpp`: `STRATA_ERROR_DIALOG_FILE`.
- `StrataTests/src/CLI/McpServerTests.cpp`: the suite `CLI.McpToolsets`, which keeps the default list within its budget.
