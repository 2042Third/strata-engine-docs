# Notes: `editor/deferred-commands`

## New terms

None proposed. The page defines the glossary's five entries: deferred command, poll function, command runner, `MayDefer`, `WaitsForAssets`.

## Since

0.3.0: the inventory (editor-core:236-238) dates `Defer(poll)`, `EditorCommandRunner` and `editor.wait` to 0.3.0; the scan wait is 0.4.0.

## Requests

- No new words or hosts. Further reading cites three sources without links (Game Programming Patterns, Microsoft's message loop documentation, Boost.Asio).
- No figures file: the one picture is a Mermaid sequence diagram.

## Not verified

- The "Who uses it" column of the alternatives table (blocking tools, callbacks, futures, coroutines) is general knowledge, not read at the pin.
- What the three Further reading entries say: not fetched.
- The editor's frame order is stated only as far as `EditorLayer::OnUpdate` calls `m_CommandRunner.Update` after `m_Context.Update`.

## Findings not applied

None: the brief carried no open findings.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
