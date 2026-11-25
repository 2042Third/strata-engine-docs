# Notes: editor/tutorial-command

## New terms

None.

## Requests

- `../automation/mcp.md` and `../engineering/feature-test.md` are linked; both pages are written by others (pages check passed at this run).
- The patch (`tutorials/editor/tutorial-command.patch`, 7 hunks) was written with git and passes `git apply --check` against the pin; the two new files are also kept whole in `tutorials/editor/tutorial-command/` (quoted by line range). Exercise 3's patch is `tutorials/editor/tutorial-command/exercise-3.patch`, against the end state of this patch.
- No figures file: the one picture is a Mermaid diagram.
- Brief asked for checkpoints and a checkpoint project with two zones; the card says a patch tutorial has none, so the last section creates the zones with `entity.create`.

## Not verified

- The patch was never compiled: the pin has no WindZoneComponent (it comes from the world/tutorial-component patch).
- Range 0 to 1000 of Strength and 0.01 of Radius come from the world/tutorial-component patch, not the pin.
- Exact wording of the range error ("must be between 0 and 1000, not 5000") is derived from `PropertyInfo::IsInRange` and `ReadValue`.
- That play.start works in an EditorContext without a project in tests (the lighting tests do the same).

## Findings not applied

None open in the brief.

## Since

0.8.0: the wind zone chain is written for this book against the 0.8.0 pin.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Tutorial run

- 2026-11-24, pin v0.8.0 319075e3, `tutorials.py patch` (round 1): after the chain (world/tutorial-component,
  gpu/debug-drawing exercise 3, scripting/tutorial-host-function) the tutorial's patch and exercise 3's patch apply as
  written, build, and pass Architecture.Layering, Editor.WindCommands (4 test cases, 5 with the exercise),
  Editor.Journal (11), CLI.McpToolsets (3) and the feature test; stamps written. This settles the first, second and
  fourth items of `## Not verified` (the patch compiles against the chain's WindZoneComponent and its ranges, and
  play.start works in the test's EditorContext); the third holds as far as the range test refuses 5000.
