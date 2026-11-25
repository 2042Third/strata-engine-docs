# Brief: `automation/rpc-server`

| Field | Value |
| --- | --- |
| Title | The editor's RPC server |
| Kind | I |
| Size | XL |
| Tracks | E |
| Needs | `automation/json-rpc`, `editor/deferred-commands`, `core/jobs` |
| From | automation ch. 6 (the network thread, the request queue, responders, `ProcessRequests`, backpressure, limits, orderly close and graceful stop, how commands become methods in `EditorAutomation`) |
| Unit | `plan/allocation/automation.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `built-in-methods` | Built-in methods | - |
| `graceful-stop` | Graceful stop | grace period |
| `network-thread` | Network thread | - |
| `requests-in-flight` | Requests in flight | - |
| `responder` | Responder | RpcResponder |
| `self-pipe-trick` | Self-pipe trick | notifier |
| `stall-timeout` | Stall timeout | - |
