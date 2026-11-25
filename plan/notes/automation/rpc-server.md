# Notes: automation/rpc-server

## Since

`since: 0.3.0`: `Docs/Releases/0.3.0.md` (line 113) names headless automation, and line 172 an editor that answers "automation requests"; the server is in the 0.3.0 release.

Rechecked at v0.8.0 (319075e3): the options-cli table only gained `launch --window-size` and `--ui-scale`, and the page takes none of its numbers from it. The limits of the page's table and excerpts (8 clients, 64 in flight, 1024 requests, 256 MiB, 30 s stall, 5 s authentication) still stand in `RpcServer.h`, and `Strata/src/Strata/Network`, `EditorAutomation.cpp` and `WindowsSocket.cpp` did not change since 822a7a46, so every quoted range holds. Nothing on the page changed.

## New terms

None proposed. The seven terms the brief names (built-in methods, graceful stop with grace period, network thread, requests in flight, responder, self-pipe trick with notifier, stall timeout) are defined in bold on the page.

## Requests

- No new names or words. The page avoided "handshake", "authenticated", "unregistered", "iteration" and similar by wording (an unlisted word is written around, not requested).
- Sketches: `sketches/automation-rpc-server-toy.cpp` (about 100 lines because of the standalone program; the card's rules win) and `sketches/automation-rpc-server-stall.cpp`.
- No figures file: all five pictures are Mermaid diagrams (connection states, threads and hand-offs, backpressure tests, graceful stop order, deferred request over frames).

## Not verified

- How a reader enables trace-level log output of the editor, for the `Automation: #<n> ...` lines (the page only says "at trace level").
- The exact "frames" number the trace line prints for `editor.wait`: by reading the code the counter may read one lower than the command's count; the page claims only "about N frames".
- That the journal entry carries the client's name as the origin (the page follows the call `CommandOrigin { Automation, client name }`; the journal page owns the entry).
- Which systems use `PosixSocket.cpp` (the page says Linux and macOS).
- The default message size limit value (`c_DefaultMaxRpcMessageSize`); the table says "the message limit".
- The "Who uses it" column of the alternatives table is general knowledge, not checked against sources.

## Findings not applied

- `automation:847` (open): settled as the brief says; the page names the suites as the tests and says the feature test does not exercise automation (`AGENTS.md` kinds list). Applied.
- No other open finding was listed in the brief.
- Not covered by design: "What went wrong before" (no history with a regression test was found at the pin; the section is optional).

## Clerk

- Nothing to admit.
- handshake entered extra-words.txt (asked by automation/security), so the page may use it.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
