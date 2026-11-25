# Notes: automation/sessions

## New terms

None proposed. The four terms homed here (discovery, pinning, idle timeout, no-gpu) are defined in bold on the page.

## Since

0.3.0: `Strata/src/Strata/Network/EditorSession.cpp` first appears in a commit contained in the tag v0.3.0 (2026-10-08 commit 2319313f at the pin's history). Later refinements (sceneLoad section, stall timer) not dated.

## Requests

- Words (none added). The page avoids "handshake", "authenticate", "reconnect", "retry" and "SIGTERM" in prose because they are on no word list.
- Link targets planned by id: `automation/security`, `automation/rpc-server`, `core/first-frame`, `core/platform`, `editor/deferred-commands`.
- No figures file: the three pictures are Mermaid diagrams (map, pin states, launch over time).

## Not verified

- The launch's progress lines on screen are given from the code's format strings, not from a captured run.
- The 600 second default of the agent server's editors is read from the usage text of `StrataCLI mcp`, not traced to code.
- The launch cases' fake editor is started as a child process of the test program (named by the environment variable `STRATA_TEST_FAKE_EDITOR` in the test); not read in full.
- The "Who uses it" column of the alternatives table (databases, language servers, service meshes) is general knowledge, not cited.
- Further reading entries (Language Server Protocol, Kubernetes probes, Kleppmann chapter 8) are named from memory without links.

## Findings not applied

- Brief item automation:381 ("pid only"): applied as the code says; the pointer holds five fields (`EditorSession.cpp:53-63`). The page does not mention the stale inventory text.
- Brief figures automation:553, 551, 586 (uses of figures homed on other pages, and the terminal capture of the launch): not placed; the launch's lines are described in prose because no captured output exists and invented output is not allowed.
- Brief rows for the editor's automation options (`--no-automation`, `--automation-port`) and the interrupt handler are covered briefly; the full option list is left to `reference/editor`.
- A "What went wrong before" section is omitted: no regression history was found for this area.

## Clerk

- Nothing to admit.
- handshake entered extra-words.txt (asked by automation/security).
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
