# Allocation: automation

## `automation/agents` — How the editor makes games with agents

**Covers.** The problem as a reader meets it: an AI agent in a terminal is asked to build a level, and an editor is
windows and clicks that a program cannot use. The naive answers break: simulated clicks fail when the layout moves, and
a second API written for agents drifts away from what the UI does. The idea: every editor operation is already a
command (its home is `editor/commands`: one sentence and a link), so the editor only has to offer the same commands to
other programs. The approaches engines use, each brought in by the flaw of the one before: an embedded script language
(Python in Unreal and Blender, C# editor scripts in Unity), a batch mode (Unity's `-batchmode -executeMethod`, Godot's
`--headless --script`), a remote-control protocol over a socket (Unreal's Remote Control API, the browser DevTools
protocol, language servers) and UI automation, ending with a table of their costs. Strata's choice and its reason: a
batch mode (`--commands` scripts) and a remote protocol on one registry, so a feature reaches agents the moment it
registers a command, with no code for automation. The map of the part: the four layers (transport, editor binding,
clients, the person's view) in one diagram, each with the page that explains it. Then what an agent is: a program built
on a language model that reads tool descriptions and calls tools. What it sees (names, descriptions and schemas only),
what every definition costs (tokens of its context) and what its clients allow (about 128 tools); the ways to design
tools for it (one tool per operation, one generic call, sets that change, a tool that describes the others) and
Strata's mix of a small default set and generic tools, with a bridge to `automation/mcp`. What an agent reads first:
`editor.status`, compact unless it asks for sections, and `log.read`; the skills that ship in the release archive as
its manual (three; the scripting skill's subject, the script SDK, is taught in the part `scripting`). Accountability:
the person must see what the agent did, undo it and keep its work as a test; Strata journals every command with its
origin, shows that an agent is present and exports a session as a script (the mechanism is `editor/journal`'s).
Determinism for agents: a call takes about a tenth of a second and frame rates differ from machine to machine, so tools
count game time in fixed steps (`editor/stepping`). The worked example reads the end-to-end test in which an agent
builds, plays, undoes, saves and exports a game through StrataCLI, call by call. What the choice cannot do: an exported
game cannot be driven this way (`worlds/runtime`). The page never types the number of commands (`:value`). Afterwards
the reader can say why Strata offers commands instead of a scripting API, name the four layers and their pages, and
judge a command's description and kind as an agent will read them.

**Leaves out.**

- Running one command from a terminal → `editor/commands`
- The journal entry, command origins and the replay export → `editor/journal`
- Fixed steps, `play.step` and `input.sequence` → `editor/stepping`
- Command scripts and `editor.batch` → `editor/command-scripts`
- Connecting Claude Code and making a game with it, step by step → `make/with-an-agent`
- How the status bar shows connected agents → `editor-ui/status`
- The viewport's agent chip and flash → `editor-ui/scene-view`
- Sockets, framing and JSON-RPC → `automation/json-rpc`
- The MCP protocol, the toolsets and their code → `automation/mcp`
- Why an exported game has no automation → `worlds/runtime`

**Fit.** `fits`: about 3,900 words against M (3,000). The four approaches with their table, the design of tools for
language models and the worked example take the most, then the exercise; accountability and determinism are a
paragraph each that links its home.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `automation:269` | concept | home | Why automate an editor: embedded scripting, batch modes, remote control, UI automation; their table; Strata's batch mode and remote protocol on one registry |
| `automation:415` | concept | home | Tool design for language models: what an agent sees and pays for, the four ways to offer tools, Strata's mix of a core toolset and generic tools; the protocol and its code are `automation/mcp`'s |
| `automation:430` | concept | home | Accountability as a design goal: see what the agent did, undo it, replay it; logs, undo histories, macro recorders and event sourcing compared; the journal itself is linked |
| `automation:444` | concept | home | Why an agent's play-test counts fixed steps, never frames |
| `automation:148` | feature | home | `editor.status` as an agent's first call: compact by default, sections (`automation`, `editor`, `sceneLoad`, `recovery`) on request |
| `automation:154` | feature | home | `log.read`, and the unread errors that `editor.status` counts |
| `automation:223-224` | feature | home | The skills `strata-editor-automation` and `strata-make-a-game`: what each teaches an agent; the third skill that ships, `strata-scripting`, is named here, and its subject, the script SDK, is taught in the part `scripting` |
| `automation:226` | feature | home | StrataCLI and three skills (`strata-editor-automation`, `strata-make-a-game`, `strata-scripting`) ship in the release archive's `Skills/`, next to the editor (`CMake/StrataPackaging.cmake:84-85`) |
| `automation:242` | feature | home | The suite `EndToEnd.EditorAutomation`: real processes, an agent's whole session, MCP's tools, answers while a large project scans |
| `automation:520` | code | home | `StrataTests/src/Editor/EditorAutomationProcessTests.cpp:341-437`: an agent's session as a test (list, status, create a project, entities, a deferred wait, play, undo, errors, save, export, quit); the handshake test of the same item is read on `automation/security` |
| `automation:530` | figure | home | The four layers: MCP client, StrataCLI, loopback TCP, the server's threads, the binding and the registry, with `call` and `--commands` as other ways in |
| `new:8` | hands-on | home | The page's exercise (D27), done on the workbench with commands from a terminal (about 250 words): read the editor as an agent does: `editor.status` compact, then with the sections `automation` and `sceneLoad`, and `log.read` from level Error, through `StrataCLI call`; say what each answer tells an agent before it acts and why reading the errors clears `errors.unread`; then judge the first sentence of three commands' descriptions in `StrataCLI list` as an agent reads them. Evidence: `StrataEditor/src/Editor/EditorStateCommands.cpp:733-750` (`editor.status`: compact by default, its sections), `:981-984` (`log.read` marks the errors read for `editor.status`); `StrataCLI/src/CLI/CliApplication.cpp:587` (`list`: the methods and their descriptions) |
| `automation:703-704` | term | home | Automation; agent (AI agent) |
| `automation:771` | term | home | Tool (of a language model) |
| `automation:776` | term | home | Tokens (of a language model), with a qualifier: the session token is `automation/security`'s |
| `automation:613` | rule | use | Commands are the API: no RPC endpoint per feature, named as the reason for the part; its home is `automation/rpc-server` |
| `editor-core:299` | concept | use | The command pattern and one API for three clients, as the base of the part |
| `editor-core:463` | figure | link | Three clients, one registry |
| `editor-core:359` | concept | link | Command scripts, record and replay |
| `editor-core:372` | concept | link | Telling the person what happened |
| `gamedev:433` | figure | link | The agent path, drawn for game makers on `make/with-an-agent` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Commands are the API: one registry, a description, a JSON Schema and a kind per command | `editor/commands` | must |
| Running a command from a terminal with `StrataCLI call` | `editor/commands` | must |
| Command scripts with `expect`, `bind` and `$ref`; `editor.batch` | `editor/command-scripts` | must |
| The activity journal, command origins and the replay export | `editor/journal` | must |
| Fixed steps, `play.step` and `input.sequence` | `editor/stepping` | must |
| JSON objects, arrays, strings and numbers | `basics/data-formats` | must |
| Commands that answer in a later frame (`editor.wait`) | `editor/deferred-commands` | helps |
| Play mode and the running copy that `play.stop` discards | `editor/play-mode` | helps |
| Undo steps and their names | `editor/undo` | helps |
| The unsaved-changes guard and `force` | `editor/saving` | helps |
| A process | `basics/computer` | helps |
| The status bar's pills | `editor-ui/status` | helps |
| Exporting a game | `worlds/export` | helps |

## `automation/json-rpc` — Sockets, framing and JSON-RPC

**Covers.** The problem as a reader meets it: `StrataCLI call entity.create` runs in one process and the editor in
another, and they share no memory; a capture of the bytes on the wire shows what travels between them. The naive
answers break: a file that both poll is slow and racy, and "one read is one message" fails because a stream has no
message boundaries. Processes that talk, from zero: pipes and standard streams (parent and child only), local sockets
and named pipes, TCP on the loopback address and shared memory, with a table of their costs. Strata's choice and its
reasons: TCP on loopback for one code path on three systems, and standard streams only where an MCP client starts
StrataCLI as its child. Sockets from zero: a port and an ephemeral port; bind, listen, accept and connect; a byte
stream without boundaries; half-close and reset; SIGPIPE; non-blocking sockets and `poll`; Nagle's algorithm. Strata's
socket layer: the `TcpSocket` contract (move-only, every wait with a timeout, no SIGPIPE), `TcpListener` with its
loopback default and port 0, `SocketPoller::Poll`, timeouts clamped to 24 hours, sockets that child processes do not
inherit, the numeric loopback check that refuses even "localhost", and the `Network` layer, a Tooling layer that games
never link, with one sentence on gameplay networking, which Strata does not have, and a link to `appendix/networking`.
Framing from zero (length prefixes, delimiters, self-delimiting formats, HTTP) and Strata's newline-delimited compact
JSON, which is safe because compact JSON escapes every newline: `JsonLineReader` rebuilding lines from chunks, the size
limit that is permanent once broken, the depth check over raw text before any value is built, and serialization that
never throws. Remote procedure calls from zero (REST, gRPC, JSON-RPC, XML-RPC) and JSON-RPC 2.0: requests,
notifications, ids, results and errors, batches refused; `ValidateRequest`; the standard error codes and Strata's six;
the synchronous `RpcClient`, whose late answers show why ids exist. The example follows one `entity.create` from the
client's bytes to the answer, then a misspelled parameter and its error with the schema in `data`. Afterwards the
reader can read Strata's wire traffic, say why a newline is a safe boundary here, and tell a transport error from a
command's failure.

**Leaves out.**

- The server's network thread, queue and limits → `automation/rpc-server`
- Waking a thread that waits in `poll` (the notifier) → `automation/rpc-server`
- The handshake, and why loopback is not private → `automation/security`
- How a client finds the editor's port → `automation/sessions`
- The same framing over standard streams for MCP → `automation/mcp`
- Networking for games: replication, prediction, latency → `appendix/networking`
- Every error code and limit in one table → `reference/automation`
- JSON itself → `basics/data-formats`

**Fit.** `fits`: about 6,350 words against L (5,000). Three concepts from zero (processes and sockets, framing,
JSON-RPC) and seven excerpts take the most, then two figures and the exercise; the notifier and its Windows excerpt
went to `automation/rpc-server` to make room, and nothing more can come here.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `automation:284` | concept | home | Processes, ports and sockets from zero; four ways for processes to talk; why TCP on loopback, and standard streams for MCP |
| `automation:298` | concept | home | Framing: length prefixes, delimiters, self-delimiting formats; Strata's newline-delimited compact JSON and its mistakes |
| `automation:310` | concept | home | Remote procedure calls and JSON-RPC 2.0: requests and notifications, why ids, errors with `data`; a timeout is not a failure |
| `automation:40-42` | feature | home | `TcpSocket`, `TcpListener` (port 0, the loopback default, exclusive bind on Windows), `SocketPoller::Poll` |
| `automation:44-47` | feature | home | The numeric loopback check, timeout clamping, handle hygiene, the `Network` layer and its place among the layers |
| `automation:53-60` | feature | home | Newline framing, `JsonLineReader`, the 64 MiB and depth limits, the builders, total serialization, `ValidateRequest`, the error codes |
| `automation:105-107` | feature | home | The synchronous `RpcClient`: one request in flight, late answers skipped by id, a failed send drops the connection |
| `automation:232-233` | feature | home | The suites `Network.Socket` and `Network.JsonRpc`: what their cases pin down |
| `automation:458` | code | home | `Strata/src/Strata/Network/JsonRpc.h:13-20`: the framing in a comment and the message limit in a constant |
| `automation:460` | code | home | `Strata/src/Strata/Network/JsonRpc.cpp:65-114`: `Append` and `NextLine`, the scan offset, `\r\n`, blank lines and the oversize error |
| `automation:462` | code | home | `Strata/src/Strata/Network/JsonRpc.cpp:13-47`: the depth check over raw text (strings, escapes, brackets); with `:213-223`, `Parse` runs it first |
| `automation:464` | code | home | `Strata/src/Strata/Network/JsonRpc.cpp:235-279`: `ValidateRequest`, and the id recovered for the error |
| `automation:466` | code | home | `Strata/src/Strata/Network/JsonRpc.h:59-76`: the error codes, a plain enum in a struct so that they convert to integers |
| `automation:468` | code | home | `Strata/src/Strata/Network/Socket.h:44-97`: the `TcpSocket` contract, move-only, timeouts everywhere, no SIGPIPE |
| `automation:472` | code | home | `Strata/src/Platform/Posix/PosixSocket.cpp:491-504`: `IsLoopbackAddress` by numeric parsing only; the Windows twin is `WindowsSocket.cpp:513-526` |
| `automation:536` | figure | home | Message framing: a stream cut into arbitrary chunks, the reader's buffer with its read and scan offsets, a partial line |
| `automation:590` | figure | home | Raw wire traffic: a text capture of the two handshake lines and one request with its answer (the handshake is read on `automation/security`) |
| `new:9` | hands-on | home | The page's exercise (D27), predict then run, on the workbench's engine build (about 250 words): for chunks that split a message, carry two messages and a blank line, end a line with `\r` and `\n` in two chunks, or grow past the size limit, predict what each `NextLine` returns and when the reader's error starts and stays, then write the chunks as a case of `Network.JsonRpc` and run the suite; the answer is the case as a patch. Evidence: `StrataTests/src/Network/JsonRpcTests.cpp:21-108` (the suite's line reader cases); `Strata/src/Strata/Network/JsonRpc.cpp:65-114` (`Append` and `NextLine`) |
| `automation:716-725` | term | home | Socket, TCP, port and ephemeral port, loopback, listener and accept, non-blocking I/O and poll, half-close, connection reset, SIGPIPE, Nagle's algorithm |
| `automation:727` | term | home | Framing (of messages; the camera's framing is another entry) |
| `automation:731-734` | term | home | RPC, JSON-RPC 2.0, notification (JSON-RPC) and batch (JSON-RPC), each qualified |
| `new:1` | not-done | link | Gameplay networking, in one sentence with a link: Strata's network code serves editor automation only, in the Tooling layer `Network`, which games never contain; the absence and the general technique are homed on `appendix/networking` (R31, D40). Evidence: `StrataTests/Architecture/Layers.json:2` ("Tooling marks the layers games never contain") and `:99-103` (`Network`, `"Tooling": true`); `git grep -ni "socket" 822a7a46 -- StrataScriptCore StrataRuntime/src` and `git grep -ni "network" 822a7a46 -- StrataScriptCore StrataRuntime/src` find nothing |
| `foundation:132` | feature | home | Sockets (passed by `core`): `WindowsSocket.cpp` and `PosixSocket.cpp` live under `Platform/` but belong to the `Network` layer |
| `automation:597` | rule | use | Loopback only, in one sentence: the server binds only loopback, and clients follow only loopback sessions; the rule and its reason are `automation/security`'s |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Bytes, UTF-8 text and JSON | `basics/data-formats` | must |
| A process and its own memory; the stack | `basics/computer` | must |
| Standard streams and pipes between programs | `basics/tools` | must |
| RAII and types that can only be moved | `basics/cpp-memory` | must |
| Move semantics, `std::optional`, `std::span` and `std::string_view` | `basics/cpp-modern` | must |
| Platform code behind a seam, one file per system; signals | `core/platform` | must |
| Errors returned, not thrown; exceptions of third-party code caught at the call site | `core/conventions` | must |
| Binary and hexadecimal; bit shifts | `basics/numbers` | helps |
| A thread that waits | `basics/threads` | helps |
| Layers, Tooling layers and what a game links | `core/layers-registries` | helps |
| Commands and `StrataCLI call`, the page's example | `editor/commands` | helps |

## `automation/rpc-server` — The editor's RPC server

**Covers.** The job: the server that lets other processes run the editor's commands without ever stalling a frame, and
the binding that turns every command into a method; the handshake is `automation/security`'s and the session file
`automation/sessions`'. The problem and how servers solve it (this page carries the part's full section): a handler
that touches the scene must run on the main thread, but network input must never wait for a frame. The designs: handle
requests on the network thread with locks everywhere, a thread per connection, an event loop on the main thread, or a
network thread that queues requests for the main thread; and how a server stays bounded under a slow or hostile peer
(fixed buffers, flow control, rate limits, timeouts, load shedding). The map: the network thread that owns every socket
and answers the built-ins, the bounded request queue, `ProcessRequests` on the main thread once per frame, responders
that answer from any thread, the notifier that wakes the network thread. The contract, rule by rule with its reason:
handlers run on the main thread and the network thread never touches engine state; every request gets exactly one
answer; everything a peer controls is bounded; slow readers are throttled and only stalled ones dropped; a connection
closes in order; a feature never gets an RPC endpoint of its own. A toy of about 60 lines: one thread, one listening
socket, a queue drained once per "frame". The real code in the order a request flows: `RunIteration` (answers moved
into send buffers, the poll set with its deadlines, reads, writes and accepts); the notifier, a loopback pair verified
by a random cookie on Windows beside POSIX's `socketpair`; the backpressure predicates and their comment on memory
order (the idea of backpressure is `assets/loading`'s, said in one sentence with a link; this page teaches only its
network form: the server stops reading, and TCP's window passes the pressure on to the peer); `ProcessRequests` (the
queue swapped, the handler looked up again, a responder with a weak reference, exceptions contained, `UnregisterMethod`
waiters signalled); `RpcResponder`, whose destructor answers a dropped request so that no client hangs;
`CheckDeadlines` (the stall timeout, half-close, waiting for the peer's end). Then the editor's side: `SyncMethods`
(commands become methods when the registry's revision changes, replaced in one step), `HandleRequest` (named parameters
only, the runner with `CommandOrigin {Automation, client name}`, the session refreshed before the answer) and
`ToRpcResult` (command errors to wire codes, the schema in `data`). The limits that need no excerpt go into one table:
built-in methods, the method registry, the client limit, bounded replies and ids, the cap on closing connections,
rate-limited warnings, graceful stop, client presence and its version counter, the notifier option, the `automation`
section of `editor.status`, the trace log, and where automation runs in `EditorLayer::OnUpdate`. The examples: one
`entity.create` traced from `RunIteration` to its journal entry with the trace log, and a deferred `editor.wait
{frames: 10}` drawn over frames with a client that disconnects meanwhile. Alternatives Strata did not choose; how it is
tested (`Network.RpcServer`, `Editor.Automation`, the test helpers; automation is tested by its suites, not by the
feature test); changing it safely. Afterwards the reader can follow any request through both threads, say which limit
answers a misbehaving client and how, and add behaviour without breaking the one-answer rule.

**Leaves out.**

- The handshake, the limits before authentication and the eviction of pending connections → `automation/security`
- Starting and stopping automation, the idle timeout and the session file → `automation/sessions`
- Deferred commands themselves (`Defer`, the runner, `MayDefer`) → `editor/deferred-commands`
- The journal entry that every request makes → `editor/journal`
- The MCP server's own loop → `automation/mcp`
- The job system and the engine's threads → `core/jobs`
- Backpressure as an idea, and its glossary entry → `assets/loading`
- What the feature test covers → `engineering/feature-test`
- Every limit's value in one table → `reference/automation`

**Fit.** `fits`: about 7,900 words against XL (8,000). Nine excerpts take the most, then six rules, five figures and
three exercises; the limits that need no excerpt share one table, and the problem section stays within a fifth of the
prose.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `automation:324` | concept | home | Threads and the main-thread rule: four server designs and Strata's network thread with a queue for the main thread |
| `automation:350` | concept | home | Robustness under load: per-message, queue, in-flight and output bounds, throttling, stall timeouts, `ServerBusy`, orderly close; backpressure only in its network form (reading stops, TCP's window passes it on), the idea itself linked to `assets/loading` |
| `automation:43` | feature | home | `SocketNotifier`: the self-pipe trick, `socketpair` on POSIX, a loopback pair verified by a cookie on Windows |
| `automation:66-73` | feature | home | The threading model, the built-in methods, the method registry, `RpcResult`, `RpcResponder`, weak shared state, handler exceptions contained, the per-connection guard |
| `automation:76-85` | feature | home | The client limit, backpressure, the stall timeout, bounded replies, orderly close, the closing cap, rate-limited warnings, graceful stop, client presence, the notifier option |
| `automation:130-133` | feature | home | Commands as methods, requests through the runner, error mapping, named parameters only |
| `automation:137-139` | feature | home | The `automation` section of `editor.status`, the trace log, where automation runs in the editor's frame |
| `automation:234` | feature | home | The suites `Network.RpcServer` and `Network.RpcPresence`: what their cases pin down; the handshake cases are read on `automation/security` |
| `automation:239` | feature | home | The suite `Editor.Automation`: methods are the commands, error kinds, deferred answers, disconnects, cancel on close, quit answered |
| `automation:244` | feature | home | The test helpers: `PumpedRpcServer`, `RawRpcConnection`, `LiveProcess`, the fake editor process |
| `automation:470` | code | home | `Strata/src/Platform/Windows/WindowsSocket.cpp:528-582`: `SocketNotifier::Open`, why Windows needs a TCP pair and why it is verified with a cookie; POSIX's `socketpair` is `PosixSocket.cpp:506-534` |
| `automation:481` | code | home | `Strata/src/Strata/Network/RpcServer.cpp:643-744`: `RunIteration`, the network thread's loop |
| `automation:486` | code | home | `Strata/src/Strata/Network/RpcServer.cpp:1362-1388`: `CanProcessRequests`, `HasQueueRoom` and `WantsInput`, backpressure in three predicates, with the memory-order comment |
| `automation:488` | code | home | `Strata/src/Strata/Network/RpcServer.cpp:1604-1681`: `ProcessRequests` on the main thread |
| `automation:490` | code | home | `Strata/src/Strata/Network/RpcServer.cpp:241-280`: `RpcResponder`, exactly one answer by an atomic exchange, and the destructor that answers a dropped request |
| `automation:492` | code | home | `Strata/src/Strata/Network/RpcServer.cpp:1250-1297`: `CheckDeadlines`, the stall timeout, the authentication deadline, half-close and the wait for the peer's end |
| `automation:500` | code | home | `StrataEditor/src/Editor/EditorAutomation.cpp:240-281`: `SyncMethods`, the revision check, `ReplaceMethod` in one step, the rest unregistered |
| `automation:502` | code | home | `StrataEditor/src/Editor/EditorAutomation.cpp:291-330`: `HandleRequest`, named parameters, the runner, the session refreshed before the answer, the client's name as the origin |
| `automation:504` | code | home | `StrataEditor/src/Editor/EditorAutomation.cpp:216-238`: `ToRpcResult`, command error kinds to wire codes and the schema in `data` |
| `automation:541` | figure | home | The connection's states: accepted, handshake started, authenticated, closing, send side shut, closed; the edges of eviction, timeouts, a wrong proof, a peer's half-close, a stall and `ServerBusy` |
| `automation:544` | figure | home | Threads and hand-offs: the network thread, the queue with its byte budget and flag, the main thread's frame, responders on any thread, the notifier |
| `automation:546` | figure | home | A deferred request over frames: arrival, queue, handler, `Defer`, polls, the answer, and a client that disconnects meanwhile |
| `automation:549` | figure | home | Backpressure: the in-flight counter, the output threshold, the global queue, where reading stops and how TCP passes it on |
| `automation:551` | figure | home | Graceful stop: commands cancelled, the session removed, the listener closed, queued requests cancelled, answers delivered, half-close; the order before `Stop` is `automation/sessions`' |
| `automation:613` | rule | home | Commands are the API: register a command with a description for agents and a complete schema, never an RPC endpoint; what such a description and schema hold is the rule "Write commands for agents" of `editor/commands`, which the page links |
| `automation:615` | rule | home | Handlers run on the main thread; the network thread never touches engine state |
| `automation:620` | rule | home | Every request gets exactly one answer: the responder's destructor, cancellation on close, graceful stop |
| `automation:622` | rule | home | Bound everything a peer controls: message size, depth, echoed ids, the queue, output, connections, warnings |
| `automation:624` | rule | home | Throttle slow readers, drop only stalled ones |
| `automation:626` | rule | home | Close in order: answers, half-close, wait for the peer, close |
| `automation:685` | hands-on | home | Exercise: make a command wait N frames and watch with the trace log that its answer comes N frames later while other requests go on |
| `automation:687` | hands-on | home | Exercise: raise the output threshold in a scratch build, run the pipelined large responses test and explain the growth of memory |
| `automation:694` | hands-on | home | Exercise ("trace it yourself"): follow one `entity.create` from `RunIteration` to `HandleRequest` to its journal entry |
| `automation:726` | term | home | Self-pipe trick; notifier |
| `automation:735-737` | term | home | Built-in methods, responder, network thread |
| `automation:740-742` | term | home | Requests in flight, stall timeout, graceful stop and grace period |
| `automation:739` | term | link | Backpressure, said in one sentence with a link: the glossary's one entry, with `assets:668`, is `assets/loading`'s (R31, D33); this page teaches its network form with `automation:77` and `automation:549` |
| `automation:847` | open | home | Settled at the pin: no automation case in `StrataTests/FeatureTest`, and the kinds the feature test counts do not include commands (`AGENTS.md:121-124`), so the page names the suites above as the tests |
| `editor-core:355` | concept | use | Asynchronous commands, as the server answers them later |
| `editor-core:575` | rule | use | Commands never block a frame; polls own their data |
| `editor-core:465` | figure | link | The command lifecycle, whose deferred branch the timeline above continues |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Sockets, `poll`, framing, JSON-RPC requests and error codes | `automation/json-rpc` | must |
| Commands, the registry and its revision, `EditorCommandResult` and its error kinds | `editor/commands` | must |
| `Defer`, the command runner, polls, `MayDefer`, `CancelAll` | `editor/deferred-commands` | must |
| The threading model, the main thread and results returned to it | `core/jobs` | must |
| Mutexes, condition variables, atomics and memory order | `basics/threads` | must |
| Lambdas, captures and `std::function` | `basics/cpp-generic` | must |
| Shared and weak ownership (`Ref`, `WeakRef`) | `basics/cpp-memory` | must |
| Exceptions of third-party code caught at the call site; log levels | `core/conventions` | must |
| The editor's frame order | `editor/program` | helps |
| A journal entry per command, with its origin | `editor/journal` | helps |
| Steady clocks and deadlines | `core/time` | helps |
| Backpressure: refusing new work while too much is pending | `assets/loading` | helps |

## `automation/security` — The security model

**Covers.** The job: deciding who may drive the editor, and keeping the secret that decides it. The problem and how
programs solve it (this page carries the full section): loopback is not private, because every local process and every
web page in a local browser can open a connection to the port, and the editor can write files, build code and load it;
the threat model in one sentence, "only holders of the token are trusted"; the approaches (endpoints that the operating
system protects, bearer tokens, mutual challenge and response, TLS client certificates) and their costs. From zero, on
top of the cryptographic hash of `basics/data-formats`: a message authentication code and HMAC, nonces and the replay
attack, the reflection attack, timing side channels and comparison in constant time, and the system's secure random
generator. The map: the token's life, from `GenerateSessionToken` to the private session file and the client that reads
it, and the two proofs that travel in its place. The contract, rule by rule with its reason: loopback only (the server
binds only loopback; clients follow only loopback sessions); no server without a token, and the token never on the
wire, in a log or in printed output; the server proves first; secrets are compared in constant time; client names are
shown, never trusted, and cleaned; the project's pointer is untrusted and holds no port or token; session files are
private; a pid is not an identity; shared files are never checked and then deleted. A toy handshake of about 50 lines
that the reader breaks in three ways (send the token, compare with `==`, let the client prove first). The real code, in
two halves. The handshake: the protocol as the header's comment states it; the proofs (labels, nonces of a fixed
format, HMAC-SHA256 in hexadecimal); the server's `HandleHandshakeMessage` (two steps, the reject helper, equal nonces
refused, the client limit, the message limit raised after authentication); the client's `AuthenticateLocked`, which
checks the server's proof before it proves anything; the limits before authentication (4 KiB messages, 16 KiB of
output, 5 seconds) and the eviction of pending connections made a pure function; the checks of `Start`. The files that
keep the secret: what a session file holds and where it lives, the private directory with no shared fallback and no
symbolic link, reads that check and read through one handle, the project pointer that only chooses which file to read,
process identity by pid and start time (an unverifiable process is skipped, never deleted), stale files taken aside,
judged again and put back with `RenameNoReplace`, the pointer removed the same way, and why a token on the command line
is discouraged. The example: the handshake computed by hand as the test recomputes it with `Crypto`, then an impostor
on a dead editor's port that fails at the client's first check. Alternatives Strata did not choose; how it is tested
(the handshake cases of `Network.RpcServer`, `Network.EditorSession`); changing it safely. Afterwards the reader can
explain each step of the handshake and the attack it stops, and change how session files are written or removed without
opening a race.

**Leaves out.**

- How clients find an editor, pin it and launch one → `automation/sessions`
- How private files are created and read on each system → `core/files`
- SHA-256 as a hash → `basics/data-formats`
- The server's limits after authentication and its backpressure → `automation/rpc-server`
- Every limit's value in one table → `reference/automation`

**Fit.** `fits`: about 8,250 words against XL (8,000). Eight excerpts in two halves with their own anchors, "The
handshake" and "Files that keep the secret", take the most, then nine rules and HMAC, nonces and two attacks taught
from zero; four exercises close the page.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `automation:363` | concept | home | The security model: the threat model of loopback, four approaches, Strata's token, handshake and private files; hashes, MACs, nonces, replay and reflection, timing |
| `automation:74-75` | feature | home | The limits before authentication and the eviction of pending connections |
| `automation:86` | feature | home | `Start` refuses a bind address that is not loopback and an empty token |
| `automation:92-99` | feature | home | The mutual challenge and response, the server first, labels, nonces of a fixed format, constant-time comparison, one handshake per connection, the session token, the engine's own SHA-256 and HMAC |
| `automation:108` | feature | home | The client's optional name, sent in the handshake and proving nothing |
| `automation:114-119` | feature | home | `EditorSessionInfo`, the per-user session file, the untrusted project pointer, process identity, race-safe pruning of stale files and of the pointer |
| `automation:122` | feature | home | Trusted reads: checked and read through one handle, 64 KiB at most |
| `automation:201` | feature | home | `--token` is allowed but discouraged: other processes can read a command line |
| `automation:235` | feature | home | The suite `Network.EditorSession`: pid reuse, the stale-file race, owner-only files, the untrusted pointer, a session directory reached through a symbolic link |
| `automation:474` | code | home | `Strata/src/Strata/Network/RpcServer.h:107-133`: the whole handshake specified in a comment |
| `automation:476` | code | home | `Strata/src/Strata/Network/RpcServer.cpp:1027-1156`: `HandleHandshakeMessage`, the server's two steps |
| `automation:479` | code | home | `Strata/src/Strata/Network/RpcClient.cpp:66-114`: `AuthenticateLocked`, the server's proof checked first |
| `automation:480` | code | home | `Strata/src/Strata/Network/RpcServer.cpp:330-363`: nonces and the two proofs, labels and `Crypto::HmacSha256` |
| `automation:484` | code | home | `Strata/src/Strata/Network/RpcConnectionLimits.h:10-21`: the eviction policy as a pure function; its body is `RpcServer.cpp:550-563` |
| `automation:494` | code | home | `Strata/src/Strata/Network/EditorSession.cpp:393-404`: `GetSessionProcessState`, pid and start time; unverifiable is not exited |
| `automation:496` | code | home | `Strata/src/Strata/Network/EditorSession.cpp:315-342`: `RemoveStaleSessionFile`, take aside, judge again, restore with `RenameNoReplace` |
| `automation:498` | code | home | `Strata/src/Strata/Network/EditorSession.cpp:375-391`: `ReadProjectSession`, the pointer only chooses, the per-user file must agree |
| `automation:538` | figure | home | The handshake as a sequence, with the inputs of each HMAC and its label, and a second lane where an impostor on a dead editor's port fails at the first check |
| `automation:553` | figure | home | Session files: the private per-user directory with `<pid>.json` (port, token, start time) beside the project's pointer (process id, project, version, headless, start timestamp; no port, no token), with the arrows of trust; `automation/sessions` adds the order of discovery |
| `automation:556` | figure | home | Stale-file removal with two processes: take aside, judge again, restore, and the race it prevents |
| `automation:597-611` | rule | home | Loopback only, worded as "the server binds only loopback; clients follow only loopback sessions" (an explicit endpoint is not checked, `automation/sessions`); no server without a token and the token never on the wire, logged or printed; the server proves first; constant-time comparison; the pointer untrusted; session files private; a pid is not an identity; never check and then delete |
| `automation:640` | rule | home | Client names are shown, never trusted, and cleaned of control and bidirectional characters |
| `automation:678` | hands-on | home | Exercise: a raw client in Python or C++ that performs the handshake by hand, calls `rpc.listMethods`, then sends an HTTP request and sees the connection close |
| `automation:689` | hands-on | home | Exercise: a fake server on a stale port that relays proofs, against the test "The client refuses a server that cannot prove it knows the token" |
| `automation:696` | hands-on | home | Exercise: a test in which a new process takes the pid's path between the read and the delete |
| `new:10` | hands-on | home | The "trace it yourself" exercise (D27), the first and easiest of the page's four (with `automation:678`, `:689` and `:696`; about 150 words): a search for `Crypto::HmacSha256` and `Crypto::ConstantTimeEquals` in `Strata/src/Strata/Network` names, for each call, the proof it computes or compares and the side that runs it; a breakpoint in `RpcClient::AuthenticateLocked` during `StrataCLI status` then shows the server's proof checked before the client sends its own. Evidence: `Strata/src/Strata/Network/RpcClient.cpp:66`, `:99`; `Strata/src/Strata/Network/RpcServer.cpp:354`, `:362`, `:1132` |
| `automation:715` | term | home | Process start time |
| `automation:743-744` | term | home | Token (session token), qualified against the tokens of a language model; nonce |
| `automation:746-756` | term | home | HMAC, challenge and response, mutual authentication, replay attack, reflection attack, constant-time comparison, domain separation label, CSPRNG, threat model, session file, project pointer |
| `automation:761` | term | home | Stale session |
| `automation:234` | feature | use | The handshake cases of `Network.RpcServer`: both ways, a replayed proof, an impostor server, the authentication timeout, slot hoarding and eviction |
| `automation:520` | code | use | The other half of the item: the handshake recomputed independently in `StrataTests/src/Network/RpcServerTests.cpp`, as the page's example |
| `automation:590` | figure | use | The two handshake lines of the raw capture |
| `foundation:156` | feature | home | `Crypto` (passed by `core`): the engine's own SHA-256, HMAC-SHA256, constant-time comparison and hexadecimal, as the handshake calls them; the implementation is named, not walked |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The RPC server: connections, the network thread, built-in methods, limits | `automation/rpc-server` | must |
| Loopback, ports and sockets; JSON-RPC requests and error codes | `automation/json-rpc` | must |
| Private files and directories, trusted reads, `RenameNoReplace`, TOCTOU | `core/files` | must |
| Cryptographic hashes such as SHA-256 | `basics/data-formats` | must |
| Hexadecimal digits | `basics/numbers` | must |
| Processes and process ids | `basics/computer` | must |
| Command-line arguments and environment variables | `basics/tools` | must |
| Unicode text and UTF-8 | `basics/bytes` | helps |
| Random numbers and seeds | `basics/math-probability` | helps |
| The operating system's seams (`Platform::*`) | `core/platform` | helps |

## `automation/sessions` — Sessions, discovery and launching

**Covers.** The job: how a client finds the right editor, starts one when none runs and stays with it, and how an
editor's automation starts and stops. The problem and how programs solve it (this page carries the full section): the
editor picks a free port when it starts, several editors may run, and a client must reach the right one; the approaches
(a fixed well-known port, a registry or service discovery, a file in a known place, environment variables handed to a
child) and their costs. Two more problems follow from it: an agent's client reconnects after the editor restarts and
must not end up in another editor, and an editor is not ready when its process starts, because it must publish its
session, scan the project's assets and open the start scene, which can take minutes. The map: the per-user session
directory and the project's pointer (drawn on `automation/security`), who writes them and in which order, and who reads
them. The contract, rule by rule with its reason: a connection never silently switches editors; readiness is judged by
progress, never by a fixed timeout; pending commands are cancelled first, then the session is removed, then the server
stops; tests and agents never use a person's own session directory. A toy discovery of about 40 lines that reads the
files and picks the newest live editor. The real code: `DiscoverEditorEndpoints` (an explicit port and token, else the
project's pointer and then the sessions that name the project, else every session newest first; a session on another
address is ignored, while the host of an explicit endpoint is not checked, so `--host` with `--port` reaches an editor
through a forwarded port and the handshake still authenticates it), with `IsPinnedEditor` beside it;
`WaitForEditorProject`, which polls `editor.status` with the `sceneLoad` section, resets its stall timer whenever the
scan or the load moves, and falls back for older editors. Around them: the write order (pointer first, then the
session), the discovery order, `STRATA_SESSION_DIR`, `IsSameProject`, `LaunchEditor` (paths checked, a detached start
through `Process` with `--project`, `--headless`, `--no-gpu` and `--idle-timeout`, the session awaited, the editor
stopped on failure), where the editor program is found, the session that follows the project before each answer,
`EditorAutomation::Start` and `Stop`, the idle timeout, the shutdown order in `EditorLayer::OnDetach`, the editor's
automation options, and Ctrl+C or SIGTERM turned into an orderly close. The example: two editors and one project, a
call made by `--project`, then the editor restarted while the client stays pinned; then `StrataCLI launch --headless
--project` with its progress lines. Alternatives Strata did not choose; how it is tested (`CLI.Discovery`, the
idle-timeout and session cases of `Editor.Automation`); changing it safely. The exercise traces which editor a client
reaches when two run. Afterwards the reader can predict which editor a client will reach, start an editor for an agent
and know when it is ready, and close one without losing an answer.

**Leaves out.**

- What a session file holds and why it can be trusted → `automation/security`
- Graceful stop inside the server → `automation/rpc-server`
- Launching from MCP and its progress notifications → `automation/mcp`
- Opening a project and its start scene in the background → `editor/projects`
- Every option of the editor's command line → `reference/editor`
- Signals and console control handlers → `core/platform`

**Fit.** `fits`: about 5,150 words against L (5,000). Three problems (finding, pinning, the lifecycle) and the
features of the client and of the editor's lifecycle around two long excerpts take the most, then four rules, two
figures of its own and the exercise.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `automation:381` | concept | home | Discovery: four approaches and Strata's session files, with the trust taken from `automation/security`; the project's pointer holds the process id, project, version, headless flag and start timestamp, never the port or the token (the item's "pid only" is stale: `Strata/src/Strata/Network/EditorSession.cpp:53-63`, `EditorSession.h:54-55`) |
| `automation:395` | concept | home | Pinning: staying with the first editor; "connect to whatever runs" as the mistake |
| `automation:404` | concept | home | The lifecycle: launch, readiness by progress, the idle timeout, shutdown in order |
| `automation:120-121` | feature | home | The write order (pointer first, a session that cannot be written leaves no pointer); the discovery order |
| `automation:123-124` | feature | home | `STRATA_SESSION_DIR`; `IsSameProject` |
| `automation:134-136` | feature | home | The session follows the project, before each answer; `Start` and `Stop`; the idle timeout |
| `automation:140-142` | feature | home | The shutdown order; the editor's automation options; interrupts turned into an orderly close |
| `automation:197-200` | feature | home | Endpoint discovery, the pinned editor, `LaunchEditor`, where the editor program is found |
| `new:13` | feature | home | The explicit endpoint, under discovery (about 70 words): `--port` (or `STRATA_EDITOR_PORT`) names it and turns discovery off, `--host` is accepted only with a port, the token comes from `STRATA_EDITOR_TOKEN` (or `--token`), and the client does not check that host for loopback (the test uses 10.1.2.3): only sessions found by discovery must name a loopback address. The handshake still authenticates the editor, so this is the way to reach one through a forwarded port. Evidence: `StrataCLI/src/CLI/CliApplication.cpp:520-558`, `:606`; `StrataCLI/src/CLI/EditorConnection.cpp:34-57`; `StrataTests/src/CLI/EditorDiscoveryTests.cpp:65`, `:94-104` |
| `automation:237` | feature | home | The suite `CLI.Discovery`: precedence, IPv6, pinning, launches that wait and stall |
| `automation:511` | code | home | `StrataCLI/src/CLI/EditorConnection.cpp:47-86`: `DiscoverEditorEndpoints`; with `:271-283`, `IsPinnedEditor` |
| `automation:512` | code | home | `StrataCLI/src/CLI/EditorLauncher.cpp:139-221`: `WaitForEditorProject`, readiness by progress, with the fallback for older editors |
| `automation:558` | figure | home | Pinning as states: unpinned, pinned to a pid, start time and project; what is accepted and what is refused |
| `automation:560` | figure | home | Launch and readiness over time: the process starts, the session appears, authentication, the scan's phases, the start scene, ready; the stall timer reset on progress |
| `automation:628-632` | rule | home | Cancel, then remove the session, then stop the server; a connection never silently switches editors; readiness by progress |
| `automation:647` | rule | home | Tests never use a person's session directory and need no real editor for CLI tests |
| `new:11` | hands-on | home | The page's exercise (D27), the "trace it yourself" that Covers names, done on the workbench (about 250 words): two headless editors started with `StrataCLI launch` into one scratch `STRATA_SESSION_DIR`, one of them with `--project`; predict which editor `StrataCLI status` and a `call` reach with `--project` and without it, then follow `DiscoverEditorEndpoints` with a debugger, or read the case "Endpoints are discovered in precedence order", to confirm; the answer names the files and functions and shows the order. Evidence: `StrataCLI/src/CLI/EditorConnection.cpp:47-86`; `StrataTests/src/CLI/EditorDiscoveryTests.cpp:48`; `Strata/src/Strata/Network/EditorSession.h:51` (`STRATA_SESSION_DIR`, which tests use to isolate themselves) |
| `automation:762-763`, `automation:765` | term | home | Discovery; pinning; idle timeout |
| `automation:764` | term | home | No-gpu only: a run without a graphics device, which implies headless; headless (a run without a window that keeps the graphics device) is linked, its one entry being `foundation:583` on `core/first-frame` (duplicates.md, merge "Headless") |
| `automation:553` | figure | use | The session files, with the order of discovery added |
| `automation:551` | figure | use | Graceful stop, for the order before `Stop` |
| `automation:586` | figure | use | The launch with its progress lines, from the terminal captures |
| `foundation:128` | feature | use | `Process`, as `LaunchEditor` uses it: a detached start with its output discarded, `IsRunning` while the session is awaited, `Terminate` when the editor cannot be reached (`StrataCLI/src/CLI/EditorLauncher.cpp:82-123`); the class is taught on `core/platform` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The session file, the project's pointer, process identity, the private session directory | `automation/security` | must |
| The RPC client, `rpc.listMethods` and JSON-RPC errors | `automation/json-rpc` | must |
| Graceful stop with a grace period | `automation/rpc-server` | must |
| `editor.status` and its sections | `automation/agents` | must |
| `CancelAll` and pending commands | `editor/deferred-commands` | must |
| Starting a child process; signals and console control handlers; exit codes | `core/platform` | must |
| Environment variables | `basics/tools` | must |
| Opening a project and its start scene in the background | `editor/projects` | helps |
| The background asset scan and its phases | `assets/importing` | helps |
| Unsaved changes discarded at close and kept for recovery | `editor/recovery` | helps |
| Headless runs | `core/first-frame` | helps |

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

## Passed on

| Item | Type | To | Why |
| --- | --- | --- | --- |
| `automation:149` | feature | `editor/commands` | `editor.commands` lists the registry, which that page teaches |
| `automation:150` | feature | `editor/command-scripts` | `editor.batch` is taught with command scripts, its home in book.md |
| `automation:151-152` | feature | `editor/journal` | Reading the journal and exporting a replay script are the journal's |
| `automation:153` | feature | `editor/deferred-commands` | `editor.wait` and `editor.quit` are deferred commands; the page already uses the item |
| `automation:155` | feature | `editor/commands` | The command contract is that page's subject; the page already uses the item |
| `automation:156` | feature | `editor/deferred-commands` | The registry's own wait for the asset scan is taught there; the page already uses the item |
| `automation:157` | feature | `editor/command-scripts` | Command scripts are that page's subject |
| `automation:166-175` | feature | `editor/journal` | The journal, origins, kinds, result kinds, recording in `Execute`, edits outside commands, ID collection, `BuildReplayScript`, the latest automation activity and the summaries: the outline gives automation chapter 4 to that page, and book.md makes it the home of agent presence |
| `automation:176` | feature | `editor-ui/instrument-panels` | The home of the Activity panel's drawing |
| `automation:182` | feature | `editor-ui/status` | The status bar's pills are drawn there |
| `automation:183-184` | feature | `editor-ui/scene-view` | The outline gives that page the agent chip; the flash is drawn in the same viewport |
| `automation:185` | feature | `editor-ui/launcher-dialogs` | The Welcome panel's cards are drawn there |
| `automation:225` | feature | `make/with-an-agent` | The package readme's "Connect an AI agent" is the game maker's setup step |
| `automation:240-241` | feature | `editor/journal` | The journal's and the replay's suites test that page's code (`Editor.CommandScriptBindings` may be cited on `editor/command-scripts`) |
| `automation:243` | feature | `editor/journal` | The CTest `ReplaySession`: an exported session replayed on a copy and compared |
| `automation:338` | concept | `nowhere` | Repeats `editor-core:355` (asynchronous commands, taught on `editor/deferred-commands`); `automation/rpc-server` uses that item |
| `automation:506` | code | `nowhere` | Repeats `editor-core:389`, the same excerpt of `EditorCommands.cpp:105-151` |
| `automation:508` | code | `editor/journal` | `BuildReplayScript`, the replay's central algorithm |
| `automation:534` | figure | `nowhere` | Repeats `editor-core:463` (three clients, one registry) |
| `automation:564` | figure | `editor/journal` | The replay export's data flow, beside the code of `BuildReplayScript` |
| `automation:574` | figure | `editor-ui/launcher-dialogs` | The launcher's card in its four states, beside the card's code |
| `automation:577` | figure | `editor-ui/status` | The automation pill and its tooltip, beside the pills' code |
| `automation:579` | figure | `editor-ui/scene-view` | The agent chip and flash, beside the viewport's code |
| `automation:581` | figure | `make/with-an-agent` | The details pane with Copy as script, Re-run and Undo to here, which that page teaches |
| `automation:584` | figure | `make/with-an-agent` | Steering an agent safely: what a forced discard looks like, with Recover |
| `automation:617` | rule | `nowhere` | Repeats `editor-core:575` (commands never block a frame) |
| `automation:619` | rule | `nowhere` | Repeats `editor-core:575` (polls own their data) |
| `automation:637` | rule | `nowhere` | Repeats `editor-core:558` (mark every command's kind and its session results) |
| `automation:639` | rule | `editor/journal` | Command origins are the journal's; no other item states this rule |
| `automation:643` | rule | `make/with-an-agent` | Steering an agent safely: an agent never forces away a person's work |
| `automation:656-660` | hands-on | `make/commands` | First contact, a scene built from the shell, reading an error |
| `automation:662` | hands-on | `make/with-an-agent` | Connecting Claude Code and watching its presence |
| `automation:664` | hands-on | `make/commands` | A capture saved with `--save-image`, with and without lights |
| `automation:666-668` | hands-on | `make/automated-playtests` | A play-test in fixed steps, and a session turned into a regression test |
| `automation:671` | hands-on | `make/commands` | An atomic batch that builds content with `bind` and `$ref` |
| `automation:673` | hands-on | `make/with-an-agent` | A whole game made the agent's way |
| `automation:705` | term | `nowhere` | Repeats `editor-core:651` (command) |
| `automation:707-708` | term | `nowhere` | Repeat `editor-core:652` (command registry) and `editor-core:654` (command kind) |
| `automation:709-710` | term | `nowhere` | Repeat `editor-core:657` (deferred command) and `editor-core:659` (`MayDefer`) |
| `automation:711` | term | `nowhere` | Repeats `editor-core:662` (command script) |
| `automation:713` | term | `nowhere` | Repeats `editor-core:664` (`bind` and `$ref`) |
| `automation:714` | term | `basics/computer` | Process; the glossary seed's entry `process` has its home there |
| `automation:728` | term | `basics/data-formats` | JSON's home |
| `automation:729-730` | term | `nowhere` | Repeat `editor-core:653` (JSON Schema) and `editor-core:666` (JSON pointer) |
| `automation:738` | term | `nowhere` | Repeats `foundation:588` (main thread) |
| `automation:739` | term | `assets/loading` | Backpressure is one idea, taught from zero there with `assets:668` (R31, D33); `automation/rpc-server` teaches the server's form and links |
| `automation:745` | term | `basics/data-formats` | The seed holds "hash" and "cryptographic hash" there; `automation/security` builds HMAC on it |
| `automation:757` | term | `core/files` | Private files are that page's in book.md |
| `automation:759-760` | term | `nowhere` | Repeat `foundation:630` (DACL) and `foundation:629` (TOCTOU) |
| `automation:767` | term | `nowhere` | Repeats `foundation:626` (exit code); StrataCLI's codes are a feature of `automation/mcp` |
| `automation:768` | term | `basics/tools` | The standard streams' home |
| `automation:780-781` | term | `nowhere` | Repeat `editor-core:668` (activity journal) and `editor-core:669` (origin) |
| `automation:782` | term | `editor/journal` | Presence; book.md makes that page the home of agent presence |
| `automation:783` | term | `nowhere` | Repeats `editor-core:670` (replay script) |
| `automation:784` | term | `editor/journal` | Edits outside commands are counted by the journal |
| `automation:785` | term | `nowhere` | Repeats `editor-core:688` (running copy) |
| `automation:786` | term | `nowhere` | Repeats `foundation:572` (fixed timestep) and `editor-core:691` (fixed step) |
| `automation:829` | open | `nowhere` | A note on the files the survey read in part |
| `automation:836` | open | `nowhere` | A note on the files the survey did not read |
| `automation:850` | open | `nowhere` | A note on how pictures of the editor's own interface can be made: it instructs the photographer, so it belongs to pipelines.md §5.5, not to a page (R44) |

## Not taken

none

## Questions for the planner

none
