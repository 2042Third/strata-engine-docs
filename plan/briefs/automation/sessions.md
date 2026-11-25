# Brief: `automation/sessions`

| Field | Value |
| --- | --- |
| Title | Sessions, discovery and launching |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `automation/security` |
| From | automation ch. 8 (session files, discovery order, pinning, `LaunchEditor` readiness by progress, the idle timeout, shutdown order) |
| Unit | `plan/allocation/automation.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `discovery` | Discovery | - |
| `idle-timeout` | Idle timeout | - |
| `no-gpu` | no-gpu | - |
| `pinning` | Pinning | - |
