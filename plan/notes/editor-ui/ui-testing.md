# Notes: editor-ui/ui-testing

## New terms

- source scan: a test that reads source files as text and fails on a pattern that a rule forbids. Home: this page. Aliases: source scans.

## Since

0.3.0: `StrataTests/src/Editor/ImGuiHarness.cpp` was added in commit f4a956ae (2026-10-09), which is an ancestor of the tag v0.3.0-rc1, so it ships in v0.3.0.

## Requests

- No figures file: the only picture is a Mermaid diagram.
- Link targets used that other pages must provide: `../editor-ui/shell.md`, `../editor-ui/widget-kit.md`, `../editor-ui/tutorial-panel.md`, `../engineering/test-kinds.md`, `../engineering/test-program.md`, `../engineering/perf-lab.md`, `../reference/performance.md`.
- Further reading cites Fowler's "Test Pyramid" and Beck's "Test-Driven Development: By Example" without links; no host is requested.

## Not verified

- The test names of `Editor.UI.Hierarchy`, `Editor.UI.Inspector`, `Editor.UI.AssetInspector`, `Editor.UI.Notifications`, `Editor.UI.Text` are taken from the inventory; `names` passes them.
- That values of 16 px or less are always allowed by the size rule: taken from the inventory ("literals above 16 px").
- Exercise 3's test names and `FindConsoleOutput` are a design for the reader, not engine code.

## Findings not applied

None: the brief lists no open findings beyond its settled item (the five panel budgets, one provisional), which the page applies.

## Clerk

- Admitted the term source scan (alias source scans), homed here.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
