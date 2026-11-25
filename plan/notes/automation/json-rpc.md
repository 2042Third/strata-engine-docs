# Notes: automation/json-rpc

## New terms

None proposed. The page defines the 17 glossary terms of its brief in bold (socket, TCP, port, ephemeral port, listener, accept, loopback, non-blocking I/O, poll, Nagle's algorithm, half-close, connection reset, SIGPIPE, framing, RPC, JSON-RPC 2.0, batch). RPC is bold with the expansion "remote function call", because the lint refuses "procedure". Notification is explained in plain words, not bold (not in the page's term table).

## Requests

- A text figure of real wire traffic (the two lines of one `entity.create` request and answer, and the mistyped-parameter error) was not made: no figure kind captures raw socket bytes. The page shows the lines as `text` fences derived from `MakeRequest`, `Serialize` and the sorted key order of the JSON library, with an invented identifier. If the planner wants a captured version: tier 3, a capture of the wire; no debug view shows it.
- Words: none requested.

## Not verified

- The lines of the example request and answers were constructed from the builders (`MakeRequest`, `MakeResult`, `MakeError`), the key order of the JSON library (sorted map) and `EditorCommandRegistry::CheckParameters`, not captured from a running editor. The identifier value is invented; its form (16 upper-case hexadecimal digits) is from `UUID::ToString`.
- That the method name on the wire equals the command name `entity.create` rests on AGENTS.md's statement that every command is a method; `EditorAutomation::SyncMethods` was not read.
- The statement that a client's connection stays open after an `InvalidParams` error was not confirmed in `RpcServer.cpp` (the handshake's rejections close the connection; command errors were not traced).
- The server's reaction to a reader error (closing the connection) was left out of the page; only the client's reaction (`ConnectionClosed`) was verified in `RpcClient.cpp`.

## Since

0.3.0: `Strata/src/Strata/Network/JsonRpc.cpp` was added in commit 2319313f, contained in tag v0.3.0.

## Findings not applied

The brief lists no open findings. Left out by the size limit: the `SocketNotifier` (assigned to `automation/rpc-server`), the Windows loopback twin as a second quote, and the `Network.Socket` case list beyond one sentence in "Where it lives". The exercise is a patch (`tutorials/automation/json-rpc/exercise-2.patch`: one new case of `Network.JsonRpc`); it was checked against the pin by the patch's context, not built.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
