# Brief: `automation/json-rpc`

| Field | Value |
| --- | --- |
| Title | Sockets, framing and JSON-RPC |
| Kind | C |
| Size | L |
| Tracks | E |
| Needs | `basics/data-formats`, `basics/threads`, `core/platform`, `automation/agents` |
| From | automation ch. 5 (loopback TCP, non-blocking I/O and poll, newline framing, `JsonLineReader`, JSON-RPC 2.0 and Strata's error codes) |
| Unit | `plan/allocation/automation.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `accept` | accept | - |
| `batch-automation` | Batch (automation) | - |
| `connection-reset` | Connection reset | - |
| `ephemeral-port` | ephemeral port | - |
| `framing-automation` | Framing (automation) | - |
| `half-close` | Half-close | - |
| `json-rpc-2-0` | JSON-RPC 2.0 | - |
| `listener-automation` | Listener (automation) | - |
| `loopback` | Loopback | - |
| `nagles-algorithm` | Nagle's algorithm | - |
| `non-blocking-i-o` | Non-blocking I/O | - |
| `poll` | poll | - |
| `port` | Port | - |
| `rpc` | RPC | - |
| `sigpipe` | SIGPIPE | - |
| `socket` | Socket | - |
| `tcp` | TCP | - |
