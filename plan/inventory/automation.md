# Inventory: Automation (editor JSON-RPC server, StrataCLI, MCP)

Area key: `automation`. Surveyed at `main` 822a7a46 (2026-11-10). All paths are relative to the repository root
(`G:/GameEngineAI`). Line numbers are those of this commit.

The area is the way an outside program (a shell script, CI, or an AI agent such as Claude Code) drives the Strata editor.
It has four layers:

1. **Transport** (`Strata/src/Strata/Network/`, the `Network` layer, a *Tooling* layer that games never link): TCP
   sockets on loopback, newline-delimited JSON-RPC 2.0, a multi-client server with a network thread, a synchronous
   client, and session files through which clients find editors.
2. **Editor binding** (`StrataEditor/src/Editor/EditorAutomation.*`, `CommandJournal.*`): every editor command becomes an
   RPC method; requests run on the main thread through the command runner; every command is journalled with who ran it.
3. **Clients** (`StrataCLI/`): the `StrataCLI` command-line client (`call`, `list`, `status`, `launch`) and an MCP
   (Model Context Protocol) server on stdio (`StrataCLI mcp`) that turns commands into tools, grouped in toolsets.
4. **People's side of it**: the launcher's "Connect an AI agent" card, the status bar's automation pill, the viewport's
   agent chip and flash, the Activity panel, and the skills that teach agents (`.claude/skills/strata-editor-automation`,
   `strata-make-a-game`).

The big idea the book must carry: *commands are the API*. The editor has about 151 commands (each a name, a description
written for agents, a JSON Schema and a kind). The UI, `--commands` scripts, JSON-RPC and MCP all run the same
commands; automation adds no per-feature code. A feature reaches agents the moment it registers a command.

---

## 1. Features

Document references: DG = `Docs/DeveloperGuide.md`, AR = `Docs/Architecture.md`, SK-A =
`.claude/skills/strata-editor-automation/SKILL.md`, SK-G = `.claude/skills/strata-make-a-game/SKILL.md`, PR =
`Docs/Releases/PackageReadme.md`. Releases: the first release note is 0.3.0 (`Docs/Releases/0.3.0.md` lines 90-98,
"AI agents"), which already has StrataCLI, MCP, the Activity journal, presence and the skills; earlier waves (1-2) built
the RPC core before any release file exists. Toolsets and compact definitions arrived in 0.4.0
(`Docs/Releases/0.4.0.md` lines 76-82; `Docs/Roadmap.md` 1262), the `settings` toolset in 0.6.0 (`0.6.0.md` line 108).
The roadmap names the stream `agent-activity` (wave 3, `Roadmap.md` 1173-1175).

### 1.1 Sockets (Network layer, platform code)

| Feature | What it is | Where | Docs |
| --- | --- | --- | --- |
| `TcpSocket` | Move-only connected TCP stream; non-blocking inside, every "blocking" call waits for readiness with a timeout; never raises SIGPIPE | `Strata/src/Strata/Network/Socket.h` 44-97; `Socket.cpp` (SendAll 42-...); `Strata/src/Platform/Windows/WindowsSocket.cpp` 185-343; `Strata/src/Platform/Posix/PosixSocket.cpp` 166-318 | AR 533-537 ("Network") |
| `TcpListener` | Listening socket; port 0 picks an ephemeral port; default bind 127.0.0.1; `SO_EXCLUSIVEADDRUSE` on Windows (no port hijack), `SO_REUSEADDR` on POSIX | `Socket.h` 99-128; `WindowsSocket.cpp` 345-416; `PosixSocket.cpp` 320-441 | AR 533 |
| `SocketPoller::Poll` | Waits on many sockets at once (`WSAPoll` / `poll`); errors and hang-ups count as readable so the next read reports them | `Socket.h` 130-148; `WindowsSocket.cpp` 466-507; `PosixSocket.cpp` 443-489 | - |
| `SocketNotifier` | Wakes a polling thread from another thread: `socketpair()` on POSIX, a *verified* loopback TCP pair on Windows (a random cookie proves the pair is ours, since another local process could connect first) | `Socket.h` 150-176; `WindowsSocket.cpp` 528-582; `PosixSocket.cpp` 506-536 | - |
| `IsLoopbackAddress` | Numeric check only (127.0.0.0/8, ::1); host names, even "localhost", are refused because they may resolve elsewhere | `Socket.h` 32-34; `WindowsSocket.cpp` 513-526; `PosixSocket.cpp` 491-504 | DG 6333 |
| Timeout clamping | `c_MaxSocketTimeout` = 24 h; `ClampSocketTimeout` keeps `now + timeout` from overflowing | `Socket.h` 23-30 | - |
| Handle hygiene | Sockets not inherited by child processes (`WSA_FLAG_NO_HANDLE_INHERIT`, `FD_CLOEXEC`), Winsock started on first use | `WindowsSocket.cpp` 28-95; `PosixSocket.cpp` 26-90 | - |
| Layer placement | `Network` layer: `Strata/Network/**` and `Platform/*/*Socket.cpp`, Tooling, may include only Core; links `ws2_32` on Windows | `StrataTests/Architecture/Layers.json` 99-104; `Strata/CMakeLists.txt` 52 | AR 117, 146 |

### 1.2 JSON-RPC 2.0 framing and messages

| Feature | What it is | Where | Docs |
| --- | --- | --- | --- |
| Newline-delimited framing | One compact JSON document per line; compact serialization escapes control characters, so a message never contains a raw newline; batches unsupported (server) | `JsonRpc.h` 13-15 | DG 6263 |
| `JsonLineReader` | Reassembles lines from chunks; accepts `\n` and `\r\n`, skips blank lines; amortized O(1) compaction; a line over the limit puts the reader into a permanent error (cannot resynchronize) | `JsonRpc.h` 25-52; `JsonRpc.cpp` 55-160 | - |
| Message size limit | 64 MiB default per message, both directions (`c_DefaultMaxRpcMessageSize`) | `JsonRpc.h` 20 | - |
| Depth limit | `c_MaxJsonDepth` = 256; raw-text scan rejects deep nesting before any value is built (copy/compare/serialize recurse) | `JsonRpc.h` 81; `JsonRpc.cpp` 13-47, 213-223 | - |
| Builders | `MakeRequest`, `MakeNotification`, `MakeResult`, `MakeError` | `JsonRpc.h` 84-87; `JsonRpc.cpp` 166-205 | - |
| Total serialization | `Serialize` never throws: invalid UTF-8 replaced by U+FFFD | `JsonRpc.cpp` 207-211 | - |
| `ValidateRequest` | Checks object, `"jsonrpc": "2.0"`, string method, valid id (string/number/null), params object or array; recovers the id for the error | `JsonRpc.h` 99-110; `JsonRpc.cpp` 235-281 | - |
| Error codes | Standard -32700/-32600/-32601/-32602/-32603 plus Strata's -32001 Unauthorized, -32002 ConnectionClosed, -32003 Timeout, -32004 ServerBusy, -32005 OperationFailed, -32006 Cancelled | `JsonRpc.h` 59-76 | DG 6310-6314 "Errors" |

### 1.3 RpcServer (the editor's server)

| Feature | What it is | Where | Docs |
| --- | --- | --- | --- |
| Threading model | A network thread owns all I/O and answers built-ins; registered methods are queued and run on the thread that calls `ProcessRequests` (the main thread, once per frame); responses may come from any thread | `RpcServer.h` 154-160; `RpcServer.cpp` 574-641 (`RunNetworkThread`), 643-744 (`RunIteration`), 1604-1681 (`ProcessRequests`) | AR 1414, 1437; DG 6401-6405 |
| Built-in methods | `rpc.handshake`, `rpc.authenticate`, `rpc.ping`, `rpc.listMethods` (name, description, paramsSchema); `rpc.` prefix reserved | `RpcServer.h` 175-179; `RpcServer.cpp` 98-131, 982-998 | DG 6401 |
| Method registry | `RegisterMethod` (async `RpcHandler` or sync `RpcSyncHandler`), `ReplaceMethod` (atomic swap), `UnregisterMethod` (waits for a running handler so captures may be destroyed), `GetMethods` (built-ins first, then sorted) | `RpcServer.h` 210-222; `RpcServer.cpp` 1539-1602 | DG 6401-6405 |
| `RpcResult`, `RpcError` | Value-or-error outcome type | `RpcServer.h` 28-33, 51-71; `RpcServer.cpp` 219-232 | - |
| `RpcResponder` | Completes one request, from any thread, once; a responder destroyed unanswered replies "request dropped" so clients never hang; holds the client's info | `RpcServer.h` 73-100; `RpcServer.cpp` 235-280 | DG 6403 |
| Weak shared state | Responders hold a `WeakRef<RpcServerShared>`: a responder that outlives the server becomes inert | `RpcServer.cpp` 372-406, 1620-1636 | - |
| Handler exception containment | Exceptions from handlers (e.g. nlohmann accessors) become InternalError answers | `RpcServer.cpp` 1650-1664 | - |
| Per-connection guard | Allocation failures in one connection's work close that connection, not the thread | `RpcServer.cpp` 531-547 | - |
| Pre-auth limits | 4 KiB messages, 16 KiB pending output, deadline `AuthenticationTimeout` (5 s) | `RpcServer.cpp` 35-37, 1197-1218, 1271-1278 | DG 6333-6343 |
| Pending-slot eviction | At most `MaxPendingConnections` (8) unauthenticated; a new one evicts the oldest that *had a chance to send*, preferring ones that have not started the handshake; a burst turns the newcomer away | `RpcConnectionLimits.h` 1-23; `RpcServer.cpp` 550-563, 789-875, 877-888 | `RpcServer.h` 162-173 |
| Client limit | `MaxClients` (8) authenticated; beyond it ServerBusy | `RpcServer.h` 140; `RpcServer.cpp` 1133-1141 | - |
| Backpressure | A client's requests are read only while it has fewer than 64 in flight, under 1 MiB waiting output, and the global queue has room (1024 requests, 256 MiB) | `RpcServer.h` 143-148; `RpcServer.cpp` 39, 1362-1388, 1013-1024 | - |
| Stalled-client timeout | A client that accepts no output for 30 s is dropped | `RpcServer.h` 150; `RpcServer.cpp` 1250-1263 | - |
| Bounded replies | Reply larger than the limit becomes an error; ids longer than 256 characters refused, not echoed; method names quoted to 64 chars | `RpcServer.cpp` 47-66, 1172-1190 | `RpcServer.h` 171-173 |
| Orderly close | Closing connection sends its answers, half-closes (`ShutdownSend`), waits for the peer's end of stream, then closes (avoids a reset destroying the last response); lingers 2 s after errors, 30 s after a client half-closes | `RpcServer.cpp` 27-33, 441-451, 1280-1306 | - |
| Closing-connection cap | At most 16 connections finishing a close beyond the limits (flood protection) | `RpcServer.cpp` 43-44, 833-845 | - |
| Rate-limited warnings | `WarningLimiter`: one log line per 5 s per kind, with a count of suppressed ones | `RpcServer.cpp` 45, 159-186 | - |
| Graceful stop | `Stop(gracePeriod)`: stop accepting and reading, cancel queued requests with -32006, keep delivering answers (also from other threads) until clients have them or the period ends | `RpcServer.h` 192-199; `RpcServer.cpp` 746-787, 1465-1504 | DG 6316-6331 |
| Client presence | `RpcClientInfo {Id, Name, ConnectedAt}`, `GetClients`, `GetClientsVersion` (change counter, so UI copies only on change); `SanitizeRpcClientName` (64 code points, control and bidi characters removed, invalid UTF-8 replaced) | `RpcServer.h` 35-49, 204-208; `RpcServer.cpp` 282-324, 1332-1360 | DG 6296-6308; AR 3891-3906 |
| Wake-up notifier option | `UseWakeupNotifier` (diagnostics); fallback polling every 5 ms | `RpcServer.h` 151; `RpcServer.cpp` 23-26, 1446-1447 | - |
| Start checks | Refuses non-loopback bind and empty token | `RpcServer.cpp` 1422-1463 | DG 6333 |

### 1.4 Authentication (the handshake)

| Feature | What it is | Where | Docs |
| --- | --- | --- | --- |
| Mutual challenge-response | `rpc.handshake {clientNonce, clientName?} -> {serverNonce, serverProof}`, `rpc.authenticate {clientProof} -> {authenticated}`; proofs are HMAC-SHA256(token, label + nonces); token never sent | `RpcServer.h` 107-133; `RpcServer.cpp` 326-364, 1027-1156 | DG 6333-6343 "Security model" |
| Server proves first | The client checks the server's proof before proving anything, so a process that took over a dead editor's port gets nothing | `RpcClient.cpp` 66-114 | `RpcServer.h` 115-117 |
| Domain separation | Labels `strata-server` / `strata-client` keep one side's proof from being valid for the other | `RpcServer.cpp` 133-136 | - |
| Fixed-format nonces | 128-bit from the OS CSPRNG, exactly 32 lower-case hex chars, so concatenations are unambiguous; equal nonces refused (reflection) | `RpcServer.cpp` 330-347, 1090-1096; `RpcClient.cpp` 97-98 | - |
| Constant-time compare | `Crypto::ConstantTimeEquals` on both sides | `Strata/src/Strata/Core/Crypto.h` 47-50; `RpcServer.cpp` 1125; `RpcClient.cpp` 99 | - |
| One handshake per connection | Second handshake or any other method before authentication closes the connection | `RpcServer.cpp` 1028-1031, 1108-1115 | - |
| Session token | `EditorSession::GenerateSessionToken`: 128 bits, 32 hex chars; empty when the RNG fails, which `Start` refuses | `EditorSession.h` 113-115; `EditorSession.cpp` 425-439 | DG 6333 |
| HMAC and SHA-256 | Engine's own SHA-256 (FIPS 180-4) and HMAC (RFC 2104/4231) | `Strata/src/Strata/Core/Crypto.h` 15-54 (implementation `Crypto.cpp`, not in this area) | - |

### 1.5 RpcClient

| Feature | What it is | Where | Docs |
| --- | --- | --- | --- |
| Synchronous client | One request in flight; thread-safe by a mutex; `Connect` (with handshake), `Call`, `Notify`, `CheckConnection`, `Close` | `RpcClient.h` 1-65; `RpcClient.cpp` 1-243 | AR 535 |
| Late-response tolerance | A timed-out call keeps the connection; the late answer with an old id is skipped; a null-id error belongs to the current call | `RpcClient.cpp` 137-177 | `RpcClient.h` 38-41 |
| Partial-send rule | A failed send drops the connection (the stream would be unusable) | `RpcClient.cpp` 133-135 | - |
| Client name | Optional `clientName` sent in the handshake | `RpcClient.h` 35-36; `RpcClient.cpp` 81-83 | DG 6305-6308 |

### 1.6 Editor sessions and discovery

| Feature | What it is | Where | Docs |
| --- | --- | --- | --- |
| `EditorSessionInfo` | ProcessId, ProcessStartTime, Address, Port, Token, ProjectPath, EditorVersion, Headless, StartedAt; `ToJson`/`FromJson` (rejects missing pid/port/token) | `EditorSession.h` 16-36; `EditorSession.cpp` 88-127 | DG 6345-6354 "Session files" |
| Per-user session file | `<user data>/Strata/Sessions/<pid>.json`, owner-only (0600 / protected DACL), in a private directory; no fallback to shared temp | `EditorSession.h` 46-64; `EditorSession.cpp` 146-220 | DG 6345; SK-A 14-18 |
| Untrusted project pointer | `<project>/.strata/EditorSession.json` holds only pid, project, version, headless, start time; never port or token; it only *chooses* which per-user file to read, which must agree | `EditorSession.cpp` 53-63, 375-391 | DG 6351-6354; AGENTS.md "Automation" |
| Process identity | `SessionProcessState` Running / Exited / Unverifiable from pid + recorded start time (pid reuse detection) | `EditorSession.h` 38-44; `EditorSession.cpp` 393-409 | DG 6349 |
| Stale-file pruning, race-safe | `RemoveStaleSessionFile` renames the file aside with a random suffix, judges it again, deletes only if still stale, else `RenameNoReplace` back | `EditorSession.cpp` 315-342 | DG 6350 |
| Pointer removal, race-safe | `RemoveProjectPointer` takes the pointer aside atomically, keeps it if another editor's | `EditorSession.cpp` 230-254 | - |
| Write order | Pointer first, then the session; a session that cannot be written leaves no pointer | `EditorSession.cpp` 185-220 | - |
| Discovery order | `FindSessions` newest first (ISO timestamps sort lexically; pid breaks ties); deletes exited, skips unverifiable and untrusted | `EditorSession.cpp` 256-313 | - |
| Trusted reads | `Platform::ReadTrustedFile` / `ReadRegularFile` check and read through one handle (no swap to FIFO/link), 64 KiB cap | `EditorSession.cpp` 20-21, 43-51, 344-365; `Strata/src/Strata/Core/Platform.h` 92-191 | AGENTS.md (Platform private files) |
| `STRATA_SESSION_DIR` | Overrides the session directory for editor and clients (tests isolate themselves) | `EditorSession.cpp` 17, 149-152 | DG 6366-6370 "Environment" |
| `IsSameProject` | `filesystem::equivalent`, then lexical normalized comparison | `EditorSession.cpp` 411-423 | - |

### 1.7 EditorAutomation (editor binding)

| Feature | What it is | Where | Docs |
| --- | --- | --- | --- |
| Commands as methods | `SyncMethods` mirrors the `EditorCommandRegistry` whenever its revision changes: each command becomes a method with its name, description and schema; changed ones replaced atomically (`ReplaceMethod`), removed ones unregistered | `StrataEditor/src/Editor/EditorAutomation.cpp` 240-289; `EditorCommands.h` 136 (`GetRevision`) | DG 6279-6294 "Commands and requests" |
| Requests through the runner | `HandleRequest` runs the command through `EditorCommandRunner::Run` with `CommandOrigin {Automation, client name}`; deferred commands answer when they complete; a disconnected client loses only the answer | `EditorAutomation.cpp` 291-330; `EditorCommandRunner.h` 28-55 | DG 6290-6294 |
| Error mapping | `ToRpcResult`: UnknownCommand -> -32601, InvalidParameters -> -32602 with `data {command, parameters: schema}`, Failed -> -32005 with `ErrorData`, Cancelled -> -32006, Internal -> -32603 | `EditorAutomation.cpp` 216-238; `EditorCommands.h` 32-40 | DG 6310-6314; SK-A 319-323 |
| Named parameters only | Positional (array) params refused with InvalidParameters | `EditorAutomation.cpp` 299-308 | - |
| Session follows the project | `UpdateSession` rewrites the session when the editor opens/creates/closes a project, also *before* each answer goes out (so the client that just created a project can find the editor by it at once) | `EditorAutomation.cpp` 117-118, 312-323, 332-349 | DG 6316-6320 |
| Start/Stop | `Start` generates a token, syncs methods before listening, publishes the session (fails if it cannot: nobody could find it); `Stop` removes the session files first, then stops the server with a grace period (default 2 s) | `EditorAutomation.h` 25-41, 63-69; `EditorAutomation.cpp` 71-141 | DG 6316-6331 |
| Idle timeout | `--idle-timeout <s>`: `HasIdledOut` after that long without a client or a pending request; the editor closes (unsaved changes discarded with a warning, kept in recovery) | `EditorAutomation.h` 38-40, 87-89; `EditorAutomation.cpp` 148-159, 191-196; `StrataEditor/src/EditorLayer.cpp` 683-691 | DG 6322-6327 |
| Status section | `editor.status {"sections": ["automation"]}`: running, address, port, clients, connectedClients, methods, completed/pending requests, pendingCommands, sessionPublished | `EditorAutomation.cpp` 198-214 | AR 3899-3901 |
| Trace log | `Automation: #<n> <method> <params> -> <outcome> (<frames>, <ms>)`, params cut to 256 bytes | `EditorAutomation.cpp` 16-57 | DG 6292-6294 |
| Frame placement | `EditorLayer::OnUpdate`: context update, `EditorCommandRunner::Update`, then `EditorAutomation::Update`, then the command script | `StrataEditor/src/EditorLayer.cpp` 610-650 (646-648) | AR 830-843 |
| Shutdown order | `OnDetach`: `CancelAll` first (clients get Cancelled), then `m_Automation.Stop()` | `EditorLayer.cpp` 596-614 | DG 6320-6322 |
| Editor options | `--no-automation`, `--automation-port <port>`, `--idle-timeout <seconds>`, `--headless`, `--no-gpu`; a headless editor whose automation fails without `--frames` exits with 1 | `StrataEditor/src/EditorApplication.cpp` 64-82, 107-120; `EditorLayer.cpp` 528-547 | DG 6316-6327; SK-A 32-40 |
| Interrupt handling | Ctrl+C/SIGTERM become an orderly close (cancel commands, remove session) | `Platform::InstallInterruptHandler` (see AR 168-176) | AR 168-176 |

### 1.8 Commands relevant to automation (registered elsewhere, used here)

| Command | Why it matters for automation | Where |
| --- | --- | --- |
| `editor.status` | Entry point for every agent; compact default, `sections` for more (automation, editor, sceneLoad, recovery...) | `StrataEditor/src/Editor/EditorStateCommands.cpp` 733 |
| `editor.commands` | Lists the registry (kind, MayDefer...) | `StrataEditor/src/Editor/EditorCommands.cpp` 66 |
| `editor.batch` | Many commands in one frame and one undo step, atomic by default, with `bind`/`$ref`; refuses `MayDefer` commands, nested batches and `until` | `StrataEditor/src/Editor/Commands/BatchCommands.cpp` 33-121 |
| `editor.activity` | Reads the journal (since/before/newest/limit/source/command) | `EditorStateCommands.cpp` 397 |
| `editor.activity.export` | Turns the journal into a replayable command script | `EditorStateCommands.cpp` 489 |
| `editor.wait`, `editor.quit` | Deferred (`MayDefer`); quit answers before closing, refuses unsaved changes unless `force` | `EditorStateCommands.cpp` 856-905 |
| `log.read` | Reads the log (marks errors read for `editor.status errors.unread`) | `EditorStateCommands.cpp` 981 |
| Command contract | `EditorCommand {Name, Description, Parameters, Handler, Kind, Results, WaitsForAssets, MayDefer}`; `EditorCommandResult {..., Pending, ErrorData, JournalId, RunningCopy}`; `CheckParameters` (unknown/missing parameters are errors) | `StrataEditor/src/Editor/EditorCommands.h` 26-112; `EditorCommands.cpp` 105-221 |
| Commands wait for the asset scan | Edit commands and `WaitsForAssets` ones are deferred by the registry until the background scan ends | `EditorCommands.cpp` 119-132 | DG 2881-2900 "Command conventions" |
| Command scripts | `StrataEditor --commands script.json` with `expect`, `bind`, `until`; the same format `editor.batch` and the export use | `StrataEditor/src/Editor/EditorCommandRunner.h` 57-110 | DG 3176-3216 "Deferred commands and command scripts" |

(The complete catalogue of the 151 commands belongs to the editor-core inventory; this area needs only the contract
and the commands above.)

### 1.9 Activity journal and replay

| Feature | What it is | Where | Docs |
| --- | --- | --- | --- |
| `CommandJournal` | Ring of at most 2,000 entries and 8 MB; each entry: id, parent, time, source, client, command, kind, parameters (kept whole up to 256 KiB, else shortened and marked), status, error, warning, result summary, result IDs, duration, frames, entities touched (<=256), undo step and serial | `StrataEditor/src/Editor/CommandJournal.h` 72-111, 142-239; `CommandJournal.cpp` | DG 6296-6308 "Activity journal" |
| `CommandSource` / `CommandOrigin` | UI, Automation (with client name), CommandScript, Internal; nested commands become children (Internal) | `CommandJournal.h` 44-61; `CommandJournal.cpp` 422-466 | DG 6296-6305 |
| `EditorCommandKind` | Edit / Query / Session: what replays repeat; unmarked counts as Edit (safe default) | `CommandJournal.h` 24-31; `EditorCommands.h` 93-96 | DG 2881-2890 |
| `EditorCommandResults` | Content / Session: whether result IDs may be bound by replays | `CommandJournal.h` 35-42 | - |
| Recording in `Execute` | Every `EditorCommandRegistry::Execute` begins an entry, notes the undo step, completes it at once or on the deferred result's final poll | `EditorCommands.cpp` 105-151; `CommandJournal.cpp` 422-586 | AR 3438-3440 |
| Edits outside commands | Undo steps recorded directly by continuous UI edits are counted (a replay cannot repeat them) | `CommandJournal.h` 167-174; `CommandJournal.cpp` 496-510 | - |
| ID collection | Bounded walk of each result collecting 16-hex-digit IDs by JSON pointer | `CommandJournal.cpp` 238-321 | - |
| Replay script (`BuildReplayScript`) | Forward pass: which entry first produced each ID, rewrite later parameters to `{"$ref"}`; backward pass: which lookups the edits need and what to bind; fails when entries are gone or parameters were truncated | `CommandJournal.h` 126-140, 214-224; `CommandJournal.cpp` 697-819 | DG 6305; SK-G 404-448 |
| Latest automation activity | The last finished mutating top-level automation command (command, client, outcome, entities) for presence UI | `CommandJournal.h` 113-124, 175; `CommandJournal.cpp` 572-584 | DG 6327-6331 |
| Summaries | `Summarize` ("Rename 'Crate' to 'Box'", error line, warning, "discarded changes", running/done); `Describe` for `editor.activity` | `CommandJournal.cpp` 629-695 | - |
| Activity panel | Rows per entry with summary, expandable raw params/result, filters, JSON details, Copy as script, Re-run, Undo to here; rows rebuilt only when the journal version or filters change | `StrataEditor/src/Panels/ActivityPanel.h` 9-109; `ActivityPanel.cpp` | DG 6296-6302 |

### 1.10 Presence in the editor UI

| Feature | What it is | Where | Docs |
| --- | --- | --- | --- |
| Automation pill | Status bar: "port N · no agent", "Agent connected · <name>", "N agents connected"; tooltip lists clients and request counts; text rebuilt only when `GetClientsVersion` changes | `StrataEditor/src/EditorLayer.cpp` 2134-2175 | DG 6327; AR 3903-3905 |
| Agent chip | Viewport toolbar: "Agent: entity.create · 3 s ago" while a client is connected or `c_AgentChipSeconds` after; click shows it in the Activity panel | `StrataEditor/src/Panels/ViewportPanel.cpp` 495-534 | AR 3906-3913 |
| Agent flash | Outlines the entities the latest automation edit touched for 600 ms, fading; bounds taken once | `ViewportPanel.cpp` 303, 350, 536-570 | AR 3909-3913 |
| "Connect an AI agent" card | Launcher card with the exact `claude mcp add strata -- <StrataCLI> mcp` line and the server's state (ready on port, N agents, off, failed with reason) | `StrataEditor/src/Panels/WelcomePanel.cpp` 758-830; `UI/EditorShell.h` 30-38 (`EditorAutomationState`); `EditorLayer.cpp` 1143-1153 | AR 3249-3250; PR 108-121 |

### 1.11 StrataCLI (command-line client)

| Feature | What it is | Where | Docs |
| --- | --- | --- | --- |
| Executable structure | Thin `main` (binary stdio, logging to stderr) over `StrataCLILib`, which tests link; links only `Strata::Network` | `StrataCLI/CMakeLists.txt` 1-23; `StrataCLI/src/Main.cpp` 11-28 | AR 57, 117, 146 |
| Commands | `call <method> [params | - | @file] [--save-image]`, `list [--json]`, `status`, `launch`, `mcp`, `--help`, `--version` | `StrataCLI/src/CLI/CliApplication.cpp` 172-360, 567-626, 642-680 | DG 6356-6365 "Clients and environment"; SK-A 45-73 |
| Exit codes | 0 success, 1 RPC error (JSON on stderr), 2 connection failure, 3 usage, 4 timeout (command may still run), 5 image not saved | `CliApplication.h` 15-27 | DG 6363-6365 |
| Argument parsing | `--name value` and `--name=value`; `BuildConnectionOptions` with env fallbacks | `CliApplication.cpp` 362-565 | - |
| Image results | `{"Image": {"MimeType", "Data"}}`; `--save-image` writes the file and replaces Data with `{File, Size}`; strict base64 decoder | `StrataCLI/src/CLI/ImageOutput.h` 1-25; `ImageOutput.cpp` 1-129 | DG 6286-6289 |
| Logging | `InitializeCliLogging`: stdout carries results/protocol, logs go to stderr | `CliApplication.cpp` 628-640 | - |
| Endpoint discovery | Explicit `--port`/`STRATA_EDITOR_PORT` + token, else `--project` (pointer, then sessions naming it), else every session newest first; non-loopback sessions ignored | `StrataCLI/src/CLI/EditorConnection.h` 22-55; `EditorConnection.cpp` 47-86 | DG 6356-6360 |
| Pinned editor | After the first connection a client stays with that process (also after it opens another project) or, after a restart, an editor of the same project; never silently switches | `EditorConnection.h` 58-111; `EditorConnection.cpp` 104-142, 238-294 | DG 6358-6360; SK-A 93-94 |
| Launching | `LaunchEditor`: validate paths, start detached with `--project/--headless/--no-gpu/--idle-timeout`, wait for the session (poll the session file every 50 ms and authenticate), then wait for the project (poll `editor.status {sections: ["sceneLoad"]}` every 250 ms) while it progresses; stop the editor on failure | `StrataCLI/src/CLI/EditorLauncher.h` 1-83; `EditorLauncher.cpp` 57-262 | DG 6268-6277 |
| Editor path | `--editor`, else `STRATA_EDITOR_PATH`, else next to StrataCLI; made absolute so the validated path is the launched one | `EditorLauncher.cpp` 40-55 | DG 6368-6370 |
| Token on the command line | `--token` allowed but discouraged (visible to other processes); env var preferred | `CliApplication.cpp` 602-609 | - |

### 1.12 MCP server (`StrataCLI mcp`)

| Feature | What it is | Where | Docs |
| --- | --- | --- | --- |
| Protocol | MCP over stdio: `initialize` (versions 2024-11-05, 2025-03-26, 2025-06-18; unknown -> newest), `notifications/initialized`, `ping`, `tools/list`, `tools/call`; batches answered for 2025-03-26 clients; `instructions` text for the model | `StrataCLI/src/CLI/McpServer.h` 23-26, 44-126; `McpServer.cpp` 34-46, 306-424 | DG 6372-6399 "MCP toolsets" |
| Generic tools | `strata_status`, `strata_launch_editor` (project, headless, noGpu), `strata_describe`, `strata_toolsets`, `strata_call`; `strata_list_methods` callable but unlisted | `McpServer.cpp` 23-28, 68-118, 495-768 | SK-A 75-94 |
| Commands become tools | `rpc.listMethods` -> tools named by `MakeToolName` (non `[A-Za-z0-9_-]` -> `_`, max 64), `inputSchema` from the params schema (forced to object) | `McpServer.cpp` 180-208, 770-811 | DG 6281-6286 |
| Result mapping | Errors -> `isError` text with code and data; objects -> text + `structuredContent`; `Image` field -> MCP image content | `McpServer.cpp` 210-261 | DG 6286-6289 |
| Toolsets | `core` (27 commands) by default; groups by exact name then prefix, unknown group -> its prefix; `--toolsets a,b | all`; `strata_toolsets {enable, disable}`; `notifications/tools/list_changed` when the set changes | `StrataCLI/src/CLI/McpToolsets.h` 1-44; `McpToolsets.cpp` 17-137; `McpServer.cpp` 267-304, 690-740, 813-825 | DG 6372-6392 |
| Compact definitions | First sentence of the description (<=160 chars, "(details: strata_describe)" when cut), property descriptions to first sentence (<=100), schema structure kept | `McpToolsets.cpp` 12-15, 71-111, 153-184 | DG 6393-6399 |
| Budget | Default list <= 32 tools and 30 KiB (`CLI.McpToolsets` test); 27 core + 5 generic = 32, about 18.6 KB; all 151 commands about 99 KB | `StrataTests/src/Editor/EditorMcpToolsetsTests.cpp` 28-156 | DG 6396-6399; AGENTS.md "Automation" |
| `strata_describe` | Toolsets, a toolset's commands, or one command's full description and schema | `McpServer.cpp` 623-688 | SK-A 85-89 |
| Launch from MCP | Reuses an editor that has the project, or an empty one this server started; launched editors get `--idle-timeout 600`; progress notifications (monotonic percent: scan registering 0-50, applying 50-90, scene 90-100) when the call has `_meta.progressToken` | `McpServer.cpp` 513-621, 827-850 | DG 6268-6277, 6360-6362 |
| Client name forwarding | `initialize`'s `clientInfo.name` becomes the handshake name (reconnects to the same editor) | `McpServer.cpp` 408-416; `EditorConnection.cpp` 162-173 | AR 3901-3903 |
| Stream runner | `RunMcpServer`: a reader thread queues stdin lines; the main loop handles them and calls `Tick` every 2 s when idle (reconnect, reap launched editors, announce tool changes) | `McpServer.cpp` 860-917 | AR 1420 |

### 1.13 Agent-facing documentation (skills, readme)

| Item | What it is | Where |
| --- | --- | --- |
| `strata-editor-automation` skill | How an agent gets an editor, calls commands (CLI and MCP), discovers state, conventions (IDs, assets, component values, undo, unsaved changes, saves, recovery, play mode, errors), workflows, troubleshooting | `.claude/skills/strata-editor-automation/SKILL.md` (775 lines; sections at 20, 45, 75, 98, 274, 329, 757) |
| `strata-make-a-game` skill | End-to-end playbook: editor, project and plan, assets, scripts, scene, verify by playing and capturing, regression script, export; Tetris made this way | `.claude/skills/strata-make-a-game/SKILL.md` (533 lines; sections at 17, 42, 64, 112, 268, 369, 404, 451, 479, 519) |
| Package readme | "Connect an AI agent": the `claude mcp add` line, toolsets, where skills go | `Docs/Releases/PackageReadme.md` 108-121 |
| Shipping | `StrataCLI` and the skills ship in release archives | AR 4184-4190 |

### 1.14 Tests (what they pin down)

| Suite | File | Cases |
| --- | --- | --- |
| `Network.Socket` | `StrataTests/src/Network/SocketTests.cpp` | 15 (ephemeral port, half-close, SIGPIPE-free write, clamped timeouts, loopback recognition, poller and notifier) |
| `Network.JsonRpc` | `StrataTests/src/Network/JsonRpcTests.cpp` | 8 (line reassembly, CRLF split, size limit, builders, single-line serialization, parse without throwing, request validation) |
| `Network.RpcServer`, `Network.RpcPresence` | `StrataTests/src/Network/RpcServerTests.cpp` | 47 (handshake both ways 496-538, replayed proof refused 540, impostor server 564, auth timeout 673, slot hoarding 772, eviction 831-889, backpressure 1015-1297, unregister waits 1349, graceful stop 1516-1664, names 1768-1847) |
| `Network.EditorSession` | `StrataTests/src/Network/EditorSessionTests.cpp` | 18 (pid reuse 118, stale deletion race 175, owner-only files 205, untrusted pointer 317, follows project 367, symlinked directory refused 509) |
| `CLI.Commands` | `StrataTests/src/CLI/CliApplicationTests.cpp` | 14 |
| `CLI.Discovery` | `StrataTests/src/CLI/EditorDiscoveryTests.cpp` | 20 (precedence, IPv6, pinning, launch waits and stalls) |
| `CLI.Mcp`, `CLI.McpToolsets`, `CLI.McpPresence` | `StrataTests/src/CLI/McpServerTests.cpp`; `StrataTests/src/Editor/EditorMcpToolsetsTests.cpp` | 19 + 1 (budget: 32 tools, 30 KiB; every command in a known toolset) |
| `Editor.Automation` | `StrataTests/src/Editor/EditorAutomationTests.cpp` | 11 (methods = commands 153, error kinds 258, deferred 300, disconnect 324, cancel on close 347, quit answered 374, session follows project 393, idle timeout 435) |
| `Editor.Journal` | `StrataTests/src/Editor/CommandJournalTests.cpp` | 11 (every command declares its kind 209) |
| `Editor.CommandScriptBindings`, `Editor.Replay` | `StrataTests/src/Editor/ReplayTests.cpp` | 3 + 10 |
| `EndToEnd.EditorAutomation` | `StrataTests/src/Editor/EditorAutomationProcessTests.cpp` | 5 (an agent builds, plays, saves and exports through StrataCLI 341; MCP exposes commands 439; 10,000-asset project answers while scanning 629) |
| CTest `ReplaySession` | `StrataTests/Editor/ReplaySession.cmake`, `ReplaySessionCommands.json.in` | Export a session, replay on a copy, compare documents |
| Test helpers | `StrataTests/src/Network/NetworkTestHelpers.h` (`PumpedRpcServer` 35-79, `RawRpcConnection`, `LiveProcess` 200-224); `FakeEditorProcess.h/.cpp` (`STRATA_TEST_FAKE_EDITOR`); `StrataTests/src/CLI/FakeEditor.h`, `McpTestClient.h` | - |

### How completeness was checked

- Every file of `Strata/src/Strata/Network/` (Socket, JsonRpc, RpcConnectionLimits, RpcServer, RpcClient, EditorSession:
  11 files) and both platform socket files read or outlined; every public declaration of their headers is in 1.1-1.6.
- Every file of `StrataCLI/` (CMakeLists, Main, CliApplication, EditorConnection, EditorLauncher, McpServer, McpToolsets,
  ImageOutput: 13 files) accounted for in 1.11-1.12.
- `EditorAutomation.h/.cpp` read whole; `CommandJournal.h` read whole, `CommandJournal.cpp` read for Begin, Complete,
  ID collection and BuildReplayScript.
- Every user of `EditorAutomation`, `GetLatestAutomationActivity` and `GetClientsVersion` in `StrataEditor/src` found by
  search (EditorLayer, WelcomePanel, ViewportPanel, EditorShell, EditorContext) and listed in 1.7 and 1.10.
- `RegisterMethod`/`ReplaceMethod` callers searched outside Network: only `EditorAutomation` (and the test fake editor),
  so there are no hand-written RPC endpoints besides the four built-ins.
- Every MCP generic tool constant (McpServer.cpp 23-28) and every toolset of the table (McpToolsets.cpp 56-69) listed.
- Every editor command-line option of automation in `c_Arguments` (EditorApplication.cpp 64-82) listed.
- Test files found by searching `StrataTests/src` for the area's class names; every `TEST_CASE` name listed by grep.

---

## 2. Concepts to teach

In dependency order. Each concept: the problem, the general approaches, Strata's choice and why, and the usual newcomer
mistakes.

### 2.1 Why automate an editor at all

- **Problem.** An editor is a GUI; tests, CI, batch jobs and AI agents cannot click. Anything only the GUI can do cannot
  be tested or delegated.
- **Approaches.** (a) Embedded scripting inside the editor (Python in Unreal, Blender, Maya; Unity's C# editor
  scripting). (b) Command-line batch modes (Unity `-batchmode -executeMethod`, Godot `--headless --script`). (c) A
  remote-control protocol over a socket (Unreal Remote Control API over HTTP/WebSocket, Godot's debugger protocol,
  language servers, browser DevTools protocol). (d) UI automation (simulated clicks), which is brittle.
- **Strata.** (b) and (c) on one foundation: every operation is a *command* (name, description, JSON Schema, kind);
  `--commands` scripts run them in-process, JSON-RPC runs them remotely, MCP turns them into tools for language models.
  "Commands are the API" (DG 6281-6289; AGENTS.md "Automation"): no RPC code per feature. Roadmap pillar
  "Agent-native and crash-contained" (`Docs/Roadmap.md` 26-28).
- **Mistakes.** Thinking automation is a separate API to maintain; writing an RPC endpoint instead of a command; writing
  command descriptions for humans in the UI rather than for agents that read nothing else.

### 2.2 Processes, sockets and ports (from nothing)

- **Problem.** Two programs (StrataCLI and the editor) must talk. They share no memory.
- **Approaches.** Pipes/stdio (parent-child only), Unix domain sockets / Windows named pipes (local, file-system or
  namespace permissions), TCP on loopback (portable, but any local process can connect), shared memory.
- **Strata.** TCP on loopback (127.0.0.1 or ::1), ephemeral port picked by the OS, published in a session file
  (`Socket.h`, `RpcServerSpecification`). Stdio only for MCP, where the MCP client launches StrataCLI as a child (that
  is what MCP's stdio transport is). Why TCP: one code path on Windows, Linux, macOS; why loopback only: "Automation
  grants full control over the editor, so it is never exposed beyond this machine" (`RpcServer.cpp` 1432).
- **Teach.** What a port is, `bind`/`listen`/`accept`/`connect`, a stream has no message boundaries, half-close,
  connection reset, SIGPIPE, non-blocking sockets and `poll`, Nagle's algorithm (`SetNoDelay`) for request/response.
- **Mistakes.** Assuming one `recv` is one message; binding 0.0.0.0 "to make it work"; trusting "localhost" (a name that
  may resolve elsewhere: `Socket.h` 32-33); blocking calls without timeouts; letting child processes inherit sockets.

### 2.3 Framing and serialization

- **Problem.** A TCP stream is bytes; messages need boundaries and a format both sides parse.
- **Approaches.** Length prefixes (binary protocols, LSP's `Content-Length` headers), delimiters (newline-delimited
  JSON, used by MCP stdio), self-delimiting formats (protobuf with varint lengths), HTTP/WebSocket.
- **Strata.** Newline-delimited compact JSON (`JsonRpc.h` 13-15): compact serialization escapes newlines inside strings,
  so `\n` is a safe delimiter, humans can read the wire with a terminal, and the same framing serves MCP stdio.
  `JsonLineReader` handles chunks, `\r\n`, blank lines, a size limit that is permanent once broken (you cannot find the
  next boundary in a stream you stopped reading).
- **Mistakes.** Pretty-printing JSON on the wire (raw newlines break framing); unbounded buffers; recursive parsing of
  untrusted input (stack exhaustion: `c_MaxJsonDepth`); throwing on invalid UTF-8 (`Serialize` replaces).

### 2.4 Remote procedure calls and JSON-RPC 2.0

- **Problem.** Ask another process to run a function and get a result or an error, matched to the request.
- **Approaches.** REST over HTTP, gRPC (protobuf, HTTP/2), JSON-RPC (tiny: `method`, `params`, `id`, `result`/`error`),
  XML-RPC, message queues.
- **Strata.** JSON-RPC 2.0 without batches: request ids, notifications (no id, no answer), standard error codes plus a
  reserved range for Strata's (-32001..-32006). Small enough to implement fully in two files; it is also the base of MCP
  and LSP, so one protocol serves both the CLI and the AI side.
- **Teach.** Request/response vs notification; why ids (pipelining, late answers after timeouts: `RpcClient.cpp`
  145-153); error objects with `data` (Strata sends the parameter schema on -32602 so a client can fix its request in
  one round trip: `EditorAutomation.cpp` 225-227).
- **Mistakes.** Treating a timeout as "the command did not run" (CLI exit 4: it may still finish; never start a second
  editor); confusing transport errors (-32002 connection closed) with command failures (-32005).

### 2.5 Threads and the main-thread rule

- **Problem.** Network I/O must never stall a frame, but command handlers touch the scene, which belongs to the main
  thread (AGENTS.md "Threading").
- **Approaches.** Handle requests on the network thread with locks everywhere (data races, deadlocks); one thread per
  connection; an event loop on the main thread (stalls frames on slow clients); a network thread that queues requests for
  the main thread (message passing).
- **Strata.** A network thread owns every socket and answers only the built-ins; registered methods go into a bounded
  queue that the main thread drains once per frame in `ProcessRequests` (AR 1414, 1437). Answers can come later from any
  thread through a `RpcResponder`, which holds a weak reference to the server's shared state. A `SocketNotifier` wakes the
  network thread when an answer is ready. `UnregisterMethod` waits for a running handler so its captures may be destroyed.
- **Mistakes.** Calling engine code from the network thread; capturing references in deferred work; forgetting that a
  responder can outlive the server (weak refs make it inert); polling with sleeps instead of a wake-up.

### 2.6 Deferred (asynchronous) commands

- **Problem.** Some commands take frames (wait 60 frames, build scripts, capture the viewport, load a scene). A frame
  must never block (AGENTS.md "Commands never block a frame").
- **Approaches.** Futures/promises, coroutines, callbacks, polled state machines.
- **Strata.** A command returns `EditorCommandResult::Defer(poll)`; `EditorCommandRunner` polls it once per frame and
  calls the completion, which answers the RPC responder (`EditorAutomation.cpp` 312-323). `MayDefer` marks such
  commands so `editor.batch` can refuse them (a batch must finish within its frame). Commands that need the asset scan
  are deferred by the registry itself (`EditorCommands.cpp` 119-132).
- **Mistakes.** A poll that captures parameters by reference; allocating per frame in a poll; forgetting `MayDefer`
  (Debug asserts).

### 2.7 Robustness under load: limits and backpressure

- **Problem.** A server that buffers without limit can be exhausted by one slow or hostile client.
- **Approaches.** Fixed per-connection buffers, flow control (TCP windows, HTTP/2 credit), rate limiting, timeouts,
  load shedding (503 / "busy").
- **Strata.** Per-message size, a global queue (count and bytes), requests in flight per client (64), output waiting
  (1 MiB) above which the client's requests are not read (TCP then pushes back on the client), a stall timeout (30 s),
  ServerBusy for a full queue or too many clients, orderly close with lingering, a cap on closing connections, rate
  limited warnings (`RpcServerSpecification`, `RpcServer.cpp` 23-51). Answers are serialized only when the send buffer
  has room, so a slow reader holds at most its in-flight answers as values (`TransferResponses` 1158-1170).
- **Mistakes.** Disconnecting a slow reader instead of throttling it (test "A client that stops reading is throttled,
  not dropped"); closing a socket with unsent data (a reset can destroy the last response: half-close first).

### 2.8 Security model: who may drive the editor

- **Problem.** Loopback is not private: every local process, and any web page in a local browser (which can open
  connections to localhost), can reach the port. The editor can write files, build and load native code: full control.
- **Approaches.** OS-protected endpoints (Unix socket file mode, named-pipe ACLs), bearer tokens (send a secret), mutual
  challenge-response (prove the secret without sending it), TLS client certificates.
- **Strata.** A per-session 128-bit token stored only in an owner-only per-user file; a challenge-response handshake
  where each side proves knowledge of the token with HMAC-SHA256 over fresh nonces, server first; constant-time
  comparisons; domain-separation labels; the token never on the wire, never logged or printed (`DescribeSession` drops
  it); before authentication only the handshake is served with tiny limits, and anything else (an HTTP request from a
  web page, a port scanner) closes the connection (`RpcServer.cpp` 1029-1031). Why server first: a process that grabbed
  the port of a crashed editor must learn nothing usable (`RpcClient.cpp` 91-93).
- **Teach.** Hash functions, MACs, HMAC, nonces and replay attacks, reflection attacks (equal nonces refused), timing
  side channels, the threat model ("only holders of the token are trusted").
- **Mistakes.** Sending the token as a bearer value; comparing secrets with `==`; logging tokens; trusting a client's
  self-reported name (Strata shows it, never trusts it); putting tokens in command-line arguments (visible to other
  processes: `CliApplication.cpp` 609).

### 2.9 Discovery and session files

- **Problem.** The editor picks a random port at start; clients must find it, and the right one when several run.
- **Approaches.** Fixed well-known ports (collide, guessable), registries or service discovery, a file in a known place,
  environment variables passed to children.
- **Strata.** Per-user session files `<user data>/Strata/Sessions/<pid>.json` (port, token, start time) in a private
  directory, plus an *untrusted* project pointer `<project>/.strata/EditorSession.json` (pid only) to find the editor by
  project. Liveness by pid **and** process start time (pid reuse). Stale files pruned with an atomic take-aside-and-check
  to avoid deleting a new editor's file. Explicit endpoint by `--port` + `STRATA_EDITOR_TOKEN`. `STRATA_SESSION_DIR`
  isolates tests and agents (SK-G 20).
- **Mistakes.** Trusting files in a project directory (projects are shared, cloned, synced); check-then-act races
  (TOCTOU) on files; following symlinks into attacker-chosen places; deleting a session whose process "looks" dead when
  its start time cannot be read.

### 2.10 Client connection policy: pinning

- **Problem.** An agent's MCP server reconnects after the editor restarts; it must not silently end up talking to a
  *different* editor (other project, other state).
- **Strata.** `EditorConnection` pins the first editor: later reconnects accept the same process (with the same start
  time), even with another project open, or another process with the same project; otherwise calls fail with a clear
  "Disconnected..." message until an explicit choice (`EditorConnection.h` 138-144; `EditorConnection.cpp` 271-294).
- **Mistakes.** "Connect to whatever is running" logic.

### 2.11 Lifecycle: launch, readiness, idle, shutdown

- **Problem.** Starting an editor is not "process started": it must publish its session, then scan the project's assets
  and open the start scene, which can take minutes on big projects; an editor started for an agent that went away must
  not run forever; on quit the last answer must reach its client.
- **Strata.** `LaunchEditor` waits for the session (bounded), then for progress (stall timeout, not a total timeout),
  with progress notifications in MCP; `--idle-timeout` (600 s for MCP-launched editors); `CancelAll` then
  `Stop(gracePeriod)` so cancelled commands and `editor.quit` are answered; headless editors close on signals in order.
- **Mistakes.** Fixed sleeps or total timeouts for readiness; killing the editor instead of `editor.quit`; leaving
  launched editors orphaned.

### 2.12 The Model Context Protocol and tool design for language models

- **Problem.** Language-model agents call "tools" described by name, description and JSON Schema. They see only those
  descriptions; every tool definition costs context tokens; clients cap the number of tools (about 128).
- **Approaches.** One tool per operation (precise, expensive), one generic "call anything" tool (cheap, the model must
  know names), dynamic tool sets, search/describe tools.
- **Strata.** Hybrid: a `core` toolset of 27 commands a game is made with, plus 5 generic tools (`strata_status`,
  `strata_launch_editor`, `strata_describe`, `strata_toolsets`, `strata_call`): 32 tools, about 18.6 KB, against about 99
  KB for all 151 commands. Compact definitions (first sentence) and `strata_describe` for the full text; toolsets enabled
  on demand with `notifications/tools/list_changed`. Results: text plus `structuredContent`; images as image content so
  the model can *see* captures. `instructions` in `initialize` orient the model (McpServer.cpp 34-46). Budget enforced by
  a test.
- **Mistakes.** Writing descriptions whose first sentence does not say what the command does (it is all most agents
  see); adding a command to `core` without removing one; returning images as text.

### 2.13 Accountability: the activity journal, presence and replay

- **Problem.** When an agent and a person share an editor, the person must see what the agent did, undo it, and the
  agent's work should become a reproducible regression test.
- **Approaches.** Logs, undo history, macro recorders, event sourcing.
- **Strata.** Every command is journalled once with its origin and client name, outcome, duration and undo step; the
  status bar, viewport chip and flash show presence; the Activity panel offers Re-run and Undo to here;
  `editor.activity.export` rebuilds a command script, binding IDs created during the session (`bind` / `$ref`) so it
  replays on a fresh copy. Command kinds (Edit/Query/Session) decide what a replay repeats; unmarked commands count as
  edits so nothing is missed.
- **Mistakes.** Recording UI drags as commands (they record undo steps directly and are counted as "edits outside
  commands"); assuming IDs are stable across runs (new entities get new UUIDs: that is why binding exists); taking IDs
  from the selection in a session meant for replay.

### 2.14 Determinism for agents

- **Problem.** An agent's calls take about 0.1 s each; game time keeps running between them; frame rates differ by
  machine.
- **Strata.** Tools count game time in fixed steps (`play.step`, `input.sequence`, `until {steps}`), never frames
  (AGENTS.md "Editor"; SK-G 383-400). This belongs mostly to the editor/scripting areas but the automation chapter must
  explain why an agent's play-test is written this way.

---

## 3. Code worth showing

Line ranges at 822a7a46. "Needs" = what the reader must know first.

1. **Framing in three lines** - `Strata/src/Strata/Network/JsonRpc.h` 13-20. Newline-delimited JSON and the message
   limit. Needs: what JSON is.
2. **`JsonLineReader::Append` and `NextLine`** - `JsonRpc.cpp` 65-114. Turning a byte stream into messages, scan offsets,
   the permanent oversize error. Needs: streams vs messages.
3. **Rejecting deep JSON before parsing** - `JsonRpc.cpp` 13-47 with `Parse` 213-223. A tiny state machine over raw text
   (strings, escapes, brackets). Needs: recursion and the stack.
4. **`ValidateRequest`** - `JsonRpc.cpp` 235-281. What makes a JSON-RPC request valid; recovering the id for the error.
   Needs: JSON-RPC basics.
5. **Error codes** - `JsonRpc.h` 59-76. Standard and implementation-defined codes; plain enum in a struct so they
   convert to ints.
6. **The non-blocking socket contract** - `Socket.h` 44-97. Move-only RAII handle, timeouts everywhere, no SIGPIPE.
   Needs: RAII, move semantics.
7. **The self-pipe trick on Windows** - `WindowsSocket.cpp` 528-582 (`SocketNotifier::Open`). Why Windows needs a TCP
   pair, why it must be verified with a cookie. Needs: poll, threads.
8. **`IsLoopbackAddress`** - `WindowsSocket.cpp` 513-526 (or `PosixSocket.cpp` 491-504). Numeric parsing only. Needs:
   IP addresses.
9. **The handshake specification as a comment** - `RpcServer.h` 107-133. The whole protocol in 27 lines. Needs: HMAC,
   nonces.
10. **Server side of the handshake** - `RpcServer.cpp` 1027-1156 (`HandleHandshakeMessage`). Step 1/step 2 state on the
    connection, the reject helper, equal-nonce refusal, constant-time compare, the client limit, raising the message
    limit after authentication. Central algorithm; long but worth it.
11. **Client side of the handshake** - `RpcClient.cpp` 66-114 (`AuthenticateLocked`). Verify the server's proof first.
12. **Proof computation** - `RpcServer.cpp` 326-364. Labels, fixed-format nonces, `Crypto::ToHex(HmacSha256(...))`.
13. **The network thread's iteration** - `RpcServer.cpp` 643-744 (`RunIteration`). Move answers into buffers, flush
    eagerly, build the poll set (notifier, listener, connections), compute the next deadline, poll, read/write, accept.
    The second central algorithm. Needs: poll, deadlines.
14. **Eviction policy as a pure function** - `RpcConnectionLimits.h` 9-21 and `RpcServer.cpp` 550-563. A security
    policy made testable by extracting it. Needs: none beyond C++.
15. **Backpressure in one predicate** - `RpcServer.cpp` 1362-1388 (`CanProcessRequests`, `HasQueueRoom`, `WantsInput`),
    with the memory-ordering comment at 1374-1376. Needs: atomics.
16. **`ProcessRequests`** - `RpcServer.cpp` 1604-1681. Swap the queue, look the handler up again, build a responder with
    a weak reference, contain exceptions, signal `UnregisterMethod` waiters. Needs: `std::function`, weak pointers.
17. **`RpcResponder` and the "never hang" destructor** - `RpcServer.cpp` 240-280. Exactly-once answers with an atomic
    exchange; the destructor answers dropped requests.
18. **Orderly close** - `RpcServer.cpp` 1250-1297 (`CheckDeadlines`). Stall timeout, auth deadline, half-close then wait
    for the peer's end.
19. **Session process identity** - `EditorSession.cpp` 393-404 (`GetSessionProcessState`). pid + start time,
    Unverifiable is not Exited.
20. **Race-safe stale removal** - `EditorSession.cpp` 315-342 (`RemoveStaleSessionFile`). Take aside, judge again,
    restore with `RenameNoReplace`. Needs: TOCTOU.
21. **Untrusted pointer, trusted file** - `EditorSession.cpp` 375-391 (`ReadProjectSession`). The pointer only chooses;
    everything comes from the per-user file and must agree.
22. **Commands become methods** - `StrataEditor/src/Editor/EditorAutomation.cpp` 240-281 (`SyncMethods`). Revision
    check, atomic replace, unregister the rest. Needs: the command registry.
23. **A request runs a command** - `EditorAutomation.cpp` 291-330 (`HandleRequest`). Runner, completion that refreshes
    the session before answering, `CommandOrigin` with the client's name.
24. **Error mapping** - `EditorAutomation.cpp` 216-238 (`ToRpcResult`). Command error kinds to wire codes; schema in
    `data`.
25. **Execute journals every command** - `StrataEditor/src/Editor/EditorCommands.cpp` 105-151. Begin, maybe defer for
    the scan, NoteUndo, Suspend or Complete. Needs: deferred commands.
26. **Replay script construction** - `StrataEditor/src/Editor/CommandJournal.cpp` 697-819 (`BuildReplayScript`).
    Forward pass for produced IDs, backward pass for needed lookups and bindings. Third central algorithm (dependency
    analysis over a log).
27. **Endpoint discovery and pinning** - `StrataCLI/src/CLI/EditorConnection.cpp` 47-86 and 271-282.
28. **Readiness by progress, not time** - `StrataCLI/src/CLI/EditorLauncher.cpp` 139-221 (`WaitForEditorProject`),
    with the fallback for older editors that refuse `sections`.
29. **Commands as MCP tools** - `StrataCLI/src/CLI/McpServer.cpp` 180-208 (`MakeToolName`, `MakeToolInputSchema`) and
    210-254 (`MakeToolResult`, image content).
30. **Toolset mapping and compaction** - `StrataCLI/src/CLI/McpToolsets.cpp` 17-69 (tables), 123-137
    (`GetGroupToolset`), 153-184 (`FirstSentence`, `MakeCompactToolDefinition`, UTF-8-safe cut).
31. **Stdio runner with ticks** - `McpServer.cpp` 860-917 (`RunMcpServer`): a reader thread and a condition variable
    with `wait_until`.
32. **Tests as documentation** - `StrataTests/src/Network/RpcServerTests.cpp` 496-538 (the handshake recomputed
    independently with `Crypto`), and `StrataTests/src/Editor/EditorAutomationProcessTests.cpp` 341-437 (an agent's whole
    session through StrataCLI: list, status, create project, entities, play, undo, save, export).

---

## 4. Figures

### Diagrams

1. **The four layers** (component diagram): MCP client (Claude Code) -> stdio -> `StrataCLI mcp` (McpServer,
   EditorConnection, RpcClient) -> TCP loopback -> editor (RpcServer network thread -> request queue -> main thread
   `ProcessRequests` -> EditorAutomation -> EditorCommandRunner -> EditorCommandRegistry -> commands -> scene/assets),
   with `StrataCLI call` and `--commands` scripts as other entry points onto the same registry.
2. **Commands are the API** (fan-in): UI menus, panels, `--commands`, `editor.batch`, JSON-RPC, MCP tools all pointing at
   one `EditorCommandRegistry`, and the journal recording all of them.
3. **Message framing** (byte layout): a TCP stream chunked arbitrarily, `JsonLineReader` buffer with `m_ReadOffset`,
   `m_ScanOffset`, terminators, a partial line.
4. **Handshake sequence** (sequence diagram): client nonce -> server nonce + server proof -> client verifies -> client
   proof -> authenticated; annotate HMAC inputs and labels; a second lane showing an impostor on a dead editor's port
   failing at the first check.
5. **Connection state machine**: Accepted (pending, pre-auth limits, deadline) -> HandshakeStarted -> Authenticated ->
   Closing (answers flushed) -> SentShutdown -> Closed; edges for eviction, timeout, wrong proof, peer half-close, stall,
   ServerBusy.
6. **Threads and hand-offs** (data flow): network thread, queue (mutex, byte budget, backpressure flag), main thread
   frame steps (AR 830-843), responders on any thread, `Shared->Outgoing`, notifier wake-up.
7. **A deferred request timeline** (timeline over frames): request arrives (frame N network thread), queued, handler runs
   (frame N+1 main), `Defer`, polls on N+2..N+k, completion answers, network thread sends; parallel lane for a client that
   disconnects meanwhile.
8. **Backpressure** (flow diagram): per-client in-flight counter, output threshold, global queue; where reading stops and
   how TCP propagates it.
9. **Graceful stop** (timeline): CancelAll -> remove session files -> Stop(grace): listener closed, queued requests
   cancelled, answers delivered, half-close, end.
10. **Session files and discovery** (file-system diagram): per-user private directory with `<pid>.json` (port, token,
    start time) vs project `.strata/EditorSession.json` (pid only); arrows of trust; discovery order explicit -> project
    -> newest.
11. **Stale-file removal** (sequence with two processes): take aside, re-judge, restore with RenameNoReplace; the race it
    prevents.
12. **Pinning** (state diagram): unpinned -> pinned(pid, start, project) -> accept same process / same project; refuse
    others.
13. **Launch and readiness** (timeline): process start, session file appears, authenticated, scan Walking/Registering/
    Applying, OpeningScene, ready; stall timer resets on progress; MCP progress percentages (0-50, 50-90, 90-100).
14. **Toolsets** (table/tree): core 27 commands, other toolsets by group, exact-name exceptions, generic tools; token
    budget bar (18.6 KB of 30 KiB vs 99 KB for all).
15. **Replay export** (data-flow over a journal): entries with produced IDs, parameters rewritten to `$ref`, backward
    marking of needed lookups, resulting script with `bind`.
16. **Error code map**: EditorCommandError kinds -> JSON-RPC codes -> CLI exit codes -> MCP `isError`.

### Screenshots

The area has no rendering feature; screenshots show the editor's presence UI and agent workflows. All can be produced
with a headless or windowed editor driven by StrataCLI (`viewport.capture` cannot capture the editor's own chrome; use a
window capture of a `--windowed` editor or `StrataEditor --screenshot` at the end of a command script).

1. **Launcher, "Connect an AI agent" card** - editor started without a project (`StrataEditor --windowed`); states: ready
   on port, 1 agent connected (connect `StrataCLI mcp` or run `StrataCLI call editor.status` repeatedly), automation off
   (`--no-automation`), automation failed (`--automation-port` of a taken port).
2. **Status bar automation pill** - "port N · no agent" and "Agent connected · claude-code" (an MCP client named via
   `initialize.clientInfo`), with its tooltip open.
3. **Viewport agent chip and flash** - a sample (Samples/Tetris or the basic3d template) with an agent running
   `entity.create`/`component.set`; capture during the 600 ms outline (or a sequence of frames showing the fade).
4. **Activity panel** - after an agent session: rows from UI, Automation (client name), CommandScript, an expanded entry
   with params/result, the details pane with Copy as script, Re-run, Undo to here (`editor.showPanel {"panel":
   "Activity"}`).
5. **Toast naming the agent** - "Claude Code discarded unsaved changes" with Recover (run `scene.open {force: true}` from
   a named client over unsaved changes).
6. **Terminal sessions** (text screenshots or code blocks): `StrataCLI status`, `StrataCLI launch --headless --project`
   with progress lines, `StrataCLI list`, a `call` with an error and exit code 1, `--save-image`.
7. **An MCP client's view** - Claude Code's tool list after `claude mcp add strata -- StrataCLI mcp` (32 tools), and a
   `viewport_capture` result shown as an image to the model.
8. **Raw wire traffic** (text): the handshake lines and a request/response captured with a raw TCP client (as
   `RawRpcConnection` does in tests).

---

## 5. Rules and pitfalls ("why" boxes)

1. **Loopback only, never another address.** `RpcServer::Start` refuses non-loopback binds and clients ignore sessions
   naming other addresses. Why: automation is full control of the editor (write files, build and load native code).
   (`RpcServer.cpp` 1431-1434; `EditorConnection.cpp` 34-43.)
2. **No server without a token; the token never crosses the wire, is never logged or printed.** Why: every local
   process and local web page can reach the port; a token sent in clear could be captured by an impostor on a stale port;
   logs and command lines are readable by others. (AGENTS.md "Automation"; `DescribeSession` drops it; `--token` warned.)
3. **Server proves first.** Why: a process that took over a crashed editor's port must not get a proof it could relay.
4. **Compare secrets in constant time.** Why: early-exit comparisons leak how much matched through timing.
5. **The project's `.strata/EditorSession.json` is untrusted and never holds port or token.** Why: project folders are
   shared, cloned and synced; a planted pointer must not redirect clients or reveal secrets.
6. **Session files are private (owner-only, private directory, no shared fallback, no symlinked directory).** Why: they
   hold the token. (`EditorSession.cpp` 157-162; test "A session directory reached through a symbolic link is refused".)
7. **A pid is not an identity: check the start time.** Why: pids are reused; an unverifiable process is skipped but never
   deleted (it may be a live editor).
8. **Never check-then-delete shared files: take them aside atomically and judge again.** Why: another editor may write
   the same path in between (TOCTOU).
9. **Commands are the API: never write an RPC endpoint for a feature; register a command with an agent-ready description
   and a complete schema.** Why: one implementation serves UI, scripts, RPC and MCP; descriptions are all an agent sees.
10. **Handlers run on the main thread; the network thread never touches engine state.** Why: the scene is single-threaded
    by design (AGENTS.md "Threading").
11. **Commands never block a frame; use `Defer` and mark `MayDefer`.** Why: a blocked frame freezes the editor and every
    other client; `editor.batch` relies on the flag.
12. **Poll functions own their data.** Why: the request's params die with the frame; the poll runs frames later.
13. **Every request gets exactly one answer.** Why: a client waiting for an answer that never comes hangs; hence the
    responder's destructor, cancellation on close, graceful stop.
14. **Bound everything a peer controls** (message size, depth, ids echoed, queue, output, connections, warnings). Why: a
    hostile or broken peer must cost bounded memory, CPU and log space.
15. **Throttle slow readers, drop only stalled ones.** Why: a big capture over a slow pipe is legitimate; a client that
    reads nothing for 30 s is not.
16. **Close in order: answers, half-close, wait for the peer, close.** Why: closing with unread input sends a reset that
    can destroy the last response in flight.
17. **Remove the session before stopping the server; cancel pending commands before that.** Why: no new client should
    find an editor going away, and cancelled commands' clients must still hear.
18. **A connection never silently switches editors.** Why: another editor has other state; an agent would edit the wrong
    project.
19. **Readiness by progress, not by a fixed timeout.** Why: projects of 30,000 assets take minutes; a fixed 60 s
    timeout gave up on every fresh copy (Roadmap 323-324).
20. **MCP: at most 32 tools and 30 KiB by default; a command added to core takes another's place.** Why: clients cap
    tools (about 128) and pay tokens for every definition.
21. **The first sentence of a command's description must say what it does.** Why: compact definitions keep only it.
22. **Mark every command's kind (Edit/Query/Session) and session-following results.** Why: replays repeat Edit commands
    and bind result IDs; a wrong kind breaks exported regression scripts. Unmarked defaults to Edit so nothing is missed.
23. **UI code passes `CommandOrigin { CommandSource::UI }`.** Why: the journal must say who did what.
24. **Client names are shown, never trusted, and sanitized.** Why: a name can carry control or bidi characters that
    reorder text in the UI (spoofing).
25. **A CLI timeout (exit 4) does not mean failure; never start another editor.** Why: the command may still finish.
26. **Commands that replace the scene refuse unsaved changes unless `force`; never force away a person's work.** (SK-A
    291-297.)
27. **Stdout of StrataCLI is protocol; logs go to stderr; stdio is binary.** Why: a stray log line or newline translation
    corrupts MCP messages (`Main.cpp` 13-15; `CliApplication.cpp` 628-640).
28. **Tests never use a real user's session directory and never need a real editor for CLI/MCP tests.** Why: isolation
    from editors on the machine (`STRATA_SESSION_DIR`, `PumpedRpcServer`, `STRATA_TEST_FAKE_EDITOR`).

---

## 6. Hands-on

### For game developers (using automation)

1. **First contact** (easy). Launch a headless editor with `StrataCLI launch --no-gpu`, run `status`, `list`,
   `call editor.status`, then `call editor.quit`. Proves: discovery, session files, exit codes.
2. **Build a scene from the shell** (easy). `project.create` with `basic3d`, `entity.create` with components,
   `component.set`, `scene.save`, params from `@file` (Windows quoting). Proves: commands, IDs, schemas, undo steps.
3. **Read an error** (easy). Call `component.set` with a misspelled parameter; read `data.parameters` and fix it.
   Proves: error codes and schema-in-data.
4. **Connect Claude Code** (easy). `claude mcp add strata -- <bin>/StrataCLI mcp`; ask the agent to make a scene; watch
   the pill, chip and Activity panel; enable the `scene` toolset with `strata_toolsets`. Proves: MCP, toolsets, presence.
5. **Capture and look** (medium). `viewport.capture --save-image` from the scene's camera, with and without lights.
   Proves: image results, preview lighting pitfall.
6. **Deterministic play-test** (medium). Pause, `input.sequence` with observations, assert on samples. Proves: fixed
   steps vs frames.
7. **Turn a session into a regression test** (medium). Note `journal.latest`, build something, `editor.activity.export`,
   run it with `StrataEditor --no-gpu --no-automation --quit-after-commands --commands` on a copy, add `expect`.
   Proves: journal, kinds, bindings.
8. **Atomic batch** (medium). `editor.batch` creating a crate stack with `bind`/`$ref`; make one step fail and see the
   undo. Proves: batches, one undo step, MayDefer refusal.
9. **Make a whole game the agent way** (hard). Follow SK-G (Tetris as reference): scripts, scene, verify, regression
   script, export, run the exported game headless. Proves: the full pipeline.

### For engine developers (changing the engine)

1. **Write a raw client** (medium). With a plain TCP socket (Python or C++), perform the handshake by hand (HMAC-SHA256
   over labels and nonces), call `rpc.listMethods`, then send an HTTP request and watch the connection close. Proves:
   framing, handshake, pre-auth rules.
2. **Add an editor command and see it everywhere** (medium). Register a Query command with a schema and agent-ready
   description; see it in `StrataCLI list`, as an MCP tool when its toolset is enabled, in the journal; add an
   `Editor.Automation`-style test and put it in a toolset (the `CLI.McpToolsets` test fails otherwise). Proves: commands
   are the API, kinds, toolset table.
3. **Make it deferred** (medium). Change the command to wait N frames with `Defer`, forget `MayDefer`, see the Debug
   assert and `editor.batch` behaviour; fix. Proves: deferred commands.
4. **Break backpressure on purpose** (hard). In a scratch build, raise `c_OutputBackpressureThreshold` to infinity and run
   the "Pipelined large responses" test; explain the memory growth. Proves: flow control.
5. **Remove the server-first check** (hard, thought experiment then test). Write a fake server on a stale port that
   relays proofs; show why `RpcClient` must verify first; read test "The client refuses a server that cannot prove it
   knows the token" (RpcServerTests.cpp 564). Proves: the threat model.
6. **A new MCP generic tool** (medium). Add a tool to `GetGenericTools` (e.g. a search over descriptions), keep the
   32-tool budget by design, extend `CLI.Mcp` tests. Proves: MCP server structure and budget.
7. **Trace a request end to end** (easy). With `--verbose` and trace logging, follow one `entity.create` from
   `RunIteration` to `HandleRequest` to the journal entry. Proves: the threading model.
8. **Session file race** (hard). Read `RemoveStaleSessionFile`, then write a test where a new process takes the pid's
   path between the read and the delete (as EditorSessionTests.cpp 175 does). Proves: TOCTOU reasoning.

---

## 7. Glossary

- **Automation** - driving the editor from another program instead of its UI.
- **Agent (AI agent)** - a language-model program that reads tool descriptions and calls tools to reach a goal.
- **Command** - a named editor operation (`<group>.<action>`) with a description, a JSON Schema of its parameters, a kind
  and a handler; the single way to change editor state from outside the UI.
- **Command registry** (`EditorCommandRegistry`) - the table of all commands; has a revision counter.
- **Command kind** - Edit (changes project content), Query (changes nothing), Session (changes the editor's session).
- **Deferred command** - one that answers over later frames (`EditorCommandResult::Defer`), polled by the runner.
- **`MayDefer`** - registration flag of commands that may defer; `editor.batch` refuses them.
- **Command script** - a JSON array of steps (`command`, `parameters`, `expect`, `bind`, `until`) run by
  `StrataEditor --commands`.
- **Binding / `$ref`** - naming a value of a step's result and using it in later steps' parameters.
- **Process** - a running program with its own memory; identified by a process id (pid).
- **Process start time** - an OS value that tells one run of a pid from a later process reusing the pid.
- **Socket** - an OS handle for a network connection endpoint.
- **TCP** - a reliable, ordered byte-stream protocol; has no message boundaries.
- **Port** - a 16-bit number selecting a listening service on a machine; **ephemeral port** - one picked by the OS.
- **Loopback** - the machine talking to itself (127.0.0.0/8, ::1); traffic never leaves the machine.
- **Listener / accept** - a socket that waits for connections; accepting yields a connected socket.
- **Non-blocking I/O, poll** - calls that return at once; `poll` waits for any of many sockets to be ready.
- **Half-close** - ending one's sending direction (`shutdown`) while still receiving.
- **Connection reset** - abrupt close that can discard data in flight.
- **SIGPIPE** - POSIX signal raised by writing to a closed connection; kills the process unless suppressed.
- **Nagle's algorithm** - TCP batching of small writes; disabled (`TCP_NODELAY`) for request/response.
- **Self-pipe trick / notifier** - waking a thread blocked in `poll` by writing to a socket it also polls.
- **Framing** - how message boundaries are marked on a stream; here, one JSON document per line.
- **JSON** - text data format of objects, arrays, strings, numbers, booleans, null.
- **JSON Schema** - a JSON description of what a JSON value must look like (types, properties, required, ranges).
- **JSON pointer** - a path into a JSON value (`/values/Translation/1`).
- **RPC** - remote procedure call: run a function in another process.
- **JSON-RPC 2.0** - a minimal RPC protocol of `method`, `params`, `id`, `result`/`error`.
- **Notification** - a JSON-RPC request without id; no answer.
- **Batch** - several JSON-RPC messages in one array (Strata's server refuses them; the MCP server answers them).
- **Built-in methods** - `rpc.handshake`, `rpc.authenticate`, `rpc.ping`, `rpc.listMethods`.
- **Responder** (`RpcResponder`) - the object that answers one request, once, from any thread.
- **Network thread** - the server's thread that owns all socket I/O.
- **Main thread** - the thread that owns scene, input, scripts and rendering submission.
- **Backpressure** - slowing a producer when the consumer cannot keep up, instead of buffering without limit.
- **Requests in flight** - requests of a client accepted but not yet answered and sent.
- **Stall timeout** - how long a client may accept no output before it is dropped.
- **Graceful stop / grace period** - shutting down while still delivering owed answers for a bounded time.
- **Token (session token)** - a random 128-bit secret per editor session, shared through the private session file.
- **Nonce** - a random value used once, so a recorded proof cannot be replayed.
- **Hash (SHA-256)** - a one-way function producing a fixed-size digest.
- **HMAC** - a message authentication code: a keyed hash proving knowledge of the key for a given message.
- **Challenge-response** - authentication by answering a fresh challenge with a proof derived from a secret.
- **Mutual authentication** - both sides prove the secret (server first, in Strata).
- **Replay attack** - re-sending a recorded valid message; defeated by nonces.
- **Reflection attack** - getting a party to answer its own challenge; defeated by labels and unequal nonces.
- **Constant-time comparison** - comparing without early exit so timing reveals nothing.
- **Domain separation label** - a fixed prefix (`strata-server`, `strata-client`) so proofs of different roles differ.
- **CSPRNG** - cryptographically secure random number generator of the OS.
- **Threat model** - who might attack and what they can do (here: any local process or web page can reach the port).
- **Session file** - `<user data>/Strata/Sessions/<pid>.json` describing a running editor's endpoint and token.
- **Project pointer** - `<project>/.strata/EditorSession.json`, an untrusted hint naming the editor's pid.
- **Private directory / owner-only file** - accessible and modifiable only by the current user (mode 0700/0600, protected
  DACL).
- **DACL** - Windows discretionary access control list on a file or directory.
- **TOCTOU** - time-of-check to time-of-use race: the state changes between a check and the action.
- **Stale session** - a session file of an editor that exited (crash, kill).
- **Discovery** - how a client finds an editor: explicit endpoint, project, newest session.
- **Pinning** - staying with the editor first connected to.
- **Headless** - running without a window (rendering still available); **no-gpu** - without a graphics device too.
- **Idle timeout** - the editor closes after this long without a client or pending request.
- **StrataCLI** - the command-line client and MCP server.
- **Exit code** - the number a process returns to its caller (StrataCLI: 0-5).
- **stdio / stdin / stdout / stderr** - a process's standard streams.
- **MCP (Model Context Protocol)** - a JSON-RPC-based protocol by which AI clients discover and call tools of servers.
- **MCP client / server** - the AI application (Claude Code) / the program offering tools (`StrataCLI mcp`).
- **Tool** - an MCP operation with name, description and input schema.
- **Toolset** - a group of commands listed together as tools (core, scene, assets, play, ...).
- **Core toolset** - the 27 commands listed by default.
- **Generic tools** - `strata_status`, `strata_launch_editor`, `strata_describe`, `strata_toolsets`, `strata_call`.
- **Compact definition** - a tool definition reduced to first sentences to save tokens.
- **Tokens (LLM)** - units of text a model reads; every tool definition costs some of the model's context.
- **`structuredContent`** - MCP field carrying a tool's result as JSON beside its text.
- **`tools/list_changed`** - MCP notification that the tool list changed.
- **Progress token / notifications/progress** - MCP mechanism for reporting progress of a long call.
- **Activity journal** - the editor's record of every command run, by whom and with what outcome.
- **Command origin / source** - who ran a command: UI, Automation (with client name), CommandScript, Internal.
- **Presence** - UI showing that, and what, an agent is doing (pill, chip, flash).
- **Replay script / export** - a command script rebuilt from the journal to repeat a session.
- **Edits outside commands** - changes recorded directly as undo steps by continuous UI edits; not replayable.
- **Running copy** - the copy of the scene that plays; changes to it are discarded by `play.stop`.
- **Fixed step** - one tick of the game's fixed-rate simulation; agents count game time in them.

---

## 8. Proposed chapters

1. **"Driving the editor from outside"** - game developers; tutorial; prerequisites: the editor basics (editor-core
   area), commands concept. Purpose: start an editor with StrataCLI, discover commands, build and save a scene from a
   shell, read errors and exit codes. Size M. Screenshots: 2 (status pill, terminal session).
2. **"Connecting an AI agent (MCP)"** - game developers; tutorial; prerequisites: chapter 1. Purpose: connect Claude Code,
   understand tools, toolsets, `strata_describe`/`strata_call`, presence, the Activity panel, and steer an agent safely
   (unsaved changes, force). Size M. Screenshots: 5 (launcher card, pill with agent, viewport chip/flash, Activity
   panel, tool list in the client).
3. **"Making a game as an agent"** - game developers; tutorial; prerequisites: chapters 1-2, scripting and scene
   chapters. Purpose: follow the strata-make-a-game playbook to a playable, exported game with a regression script;
   deterministic play-testing. Size L. Screenshots: 3 (captures of the game, regression run output, exported game).
4. **"Recording and replaying: the activity journal"** - both; concept + tutorial; prerequisites: chapter 1, undo
   (editor-core). Purpose: explain journal entries, command kinds, export to a command script with bindings, and use it
   as a regression test. Size M. Screenshots: 1 (Activity panel with expanded entry).
5. **"Processes talking: sockets, framing and JSON-RPC"** - engine; concept + internals; prerequisites: C++ basics,
   threads (foundation area). Purpose: explain loopback TCP, non-blocking I/O and poll, newline framing,
   `JsonLineReader`, JSON-RPC 2.0 and Strata's error codes, with the socket layer's code. Size L. Screenshots: 0.
6. **"The editor's RPC server"** - engine; internals; prerequisites: chapter 5, main-thread rule and deferred commands
   (editor-core). Purpose: explain the network thread, the request queue, responders, `ProcessRequests`, backpressure,
   limits, orderly close and graceful stop; how commands become methods (`EditorAutomation`). Size XL. Screenshots: 0.
7. **"Who may drive the editor: the security model"** - engine (and curious game developers); concept + internals;
   prerequisites: chapter 5. Purpose: threat model of loopback, tokens, HMAC challenge-response, server-first proof,
   pre-auth limits, private session files, untrusted pointer, pid reuse and TOCTOU-safe file handling. Size L.
   Screenshots: 0.
8. **"Finding editors: sessions, discovery, launching"** - engine; internals; prerequisites: chapters 5 and 7. Purpose:
   session files, discovery order, pinning, `LaunchEditor` readiness by progress, idle timeout, shutdown order. Size M.
   Screenshots: 1 (launch progress in a terminal).
9. **"Tools for language models: the MCP server"** - engine; internals; prerequisites: chapters 5 and 8. Purpose: MCP
   protocol, mapping commands to tools, result and image mapping, toolsets and the token budget, compact definitions,
   writing command descriptions for agents. Size M. Screenshots: 1 (tool list).
10. **"Automation reference"** - both; reference; prerequisites: none. Purpose: CLI usage and exit codes, editor
    options, environment variables, error codes, built-in methods, MCP generic tools and toolsets table, limits table.
    Size M. Screenshots: 0.

---

## 9. Not determined

- **Read only in part:** `RpcServer.cpp` lines 160-186 (WarningLimiter body), 1300-1360 (BeginClose,
  RemoveClosedConnections, UpdateClientCount), 1390-1420 (CountConnections, FindConnection, constructor); `Socket.cpp`
  beyond SendAll's start; `JsonRpc.cpp` 140-206; most of `WindowsSocket.cpp`/`PosixSocket.cpp` (Connect, Receive,
  Accept bodies outlined only); `CommandJournal.cpp` 1-230 and 345-420 (byte estimates, shortening, summary writer,
  ReplaceProducedIds helper), 587-695; `CliApplication.cpp` 1-171 and 362-565 (argument parsing details);
  `EditorLauncher.cpp` 120-138; `McpServer.cpp` 120-175, 690-768; `ActivityPanel.cpp` (header only);
  `ViewportPanel.cpp` chip/flash bodies; `WelcomePanel.cpp` beyond line 812; `EditorCommandRunner.cpp` (header only).
- **Not read:** `Strata/src/Strata/Core/Crypto.cpp` (SHA-256/HMAC implementation; belongs to the foundation area),
  `Platform` implementations of `WritePrivateFile`, `ReadTrustedFile`, `EnsurePrivateDirectory`,
  `GetProcessStartTime` (foundation area); the editor's `editor.status` handler in full; the full skills beyond the
  sections cited (SK-A sections 5-6 skimmed by heading; SK-G sections 3-5 not read); the test bodies except the handshake
  test and the start of the end-to-end agent test; `StrataTests/src/CLI/FakeEditor.h` and `McpTestClient.h`.
- **Release history:** release notes start at 0.3.0, where the area already exists; when the RPC server, the handshake
  form (HMAC challenge-response rather than an earlier scheme, if any) and session pinning first appeared is not stated
  in the documents I read (wave 1-2 sections of `Docs/Roadmap.md` were only searched, not read).
- **Counts quoted from the guide, not recomputed:** 151 commands, 27 core commands (confirmed by
  `EditorMcpToolsetsTests.cpp` line 113 `GetCoreCommands().size() == 27`), 18.6 KB default tool list, 99 KB for all
  commands.
- **Feature test:** no automation-specific coverage found in `StrataTests/FeatureTest` (automation is covered by the
  `Editor.Automation`, `CLI.*`, `Network.*` and `EndToEnd.*` suites instead); whether the feature test is meant to cover
  RPC methods was not determined.
- **Screenshots:** whether the docs project can capture the editor's own chrome (status bar, panels) automatically is
  not determined: `viewport.capture` renders the scene only; `StrataEditor --screenshot` saves the last frame of a
  scripted run, which may serve.
