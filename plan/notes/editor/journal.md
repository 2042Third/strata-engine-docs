# Notes: `editor/journal`

## New terms

None proposed. The page defines the glossary's four entries: activity journal, edits outside commands, presence, replay script. It also defines "origin" in bold in one sentence.

## Since

0.3.0: the inventory (editor-core:242-244) dates `CommandJournal`, `editor.activity` and `editor.activity.export` to 0.3.0.

## Requests

- Figure `activity-panel` (editor): layout `layouts/editor-activity.ini` showing the Activity panel with rows from the person, a named agent and a command script; waits for the editor screenshot tier.
- No new words or hosts. Further reading cites two sources without links (Fowler on event sourcing, Game Programming Patterns).

## Not verified

- The exported JSON in the example is derived from `BuildReplayScript` and `MakeBindingName`, not captured from a run; the entry number 12 is illustrative.
- The "Who uses it" column of the alternatives table is general knowledge, not read at the pin.
- The CTest test is named `StrataEditor.Replay` in the pin's generated CTest file; the brief calls it `ReplaySession` (the script's name).
- Presence is described only as the journal's latest automation activity; the chip and flash drawing was not read.

## Findings not applied

None: the brief carried no open findings. Omitted by design: a "What went wrong before" section (no history of a bug found).

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

- activity-panel (2026-11-18, provisional build 5b975ad2831e, nothing published; `waitsFor: tier 2: editor screenshot` kept): good in round 1. The recipe's project, layout and steps were placeholders (the ThirdPerson sample, the missing `layouts/editor-activity.ini`, no steps). It now opens a basic3d project in `layouts/make-with-an-agent-activity.ini` (960 × 540, the layout `editor-ui/instrument-panels` uses for this panel) and pictures the Activity panel alone (596 × 340): `entity.create` (Create 'Crate'), `entity.rename` (Rename 'Crate' to 'Box', the page's own example), `component.set` (Set Scale of 'Box') and `scene.new` with `force` (discarded changes, in yellow), then the take's `editor.wait`, `editor.showPanel` and `editor.screenshot`; the take's `scene.loadStatus` row is above them (9 of 9 rows). A take runs its steps as a command script in an editor started with `--no-automation`, so every row carries the script's scroll icon: rows of the person (pointer) and of a named agent (robot) cannot show, nor an error's first line (a failed step fails the take). Caption, alt and shows say what is there. What the page's words would need for the person's and an agent's rows: a take with a connected automation client and a UI-origin command, or a diagram of three rows with their icons.
- activity-panel, mend (2026-11-18, nothing published; `waitsFor` kept): a viewer found half the rows unexplained (the take's `scene.loadStatus` at the top; `editor.wait` at 1021.9 ms, `editor.showPanel` and `editor.screenshot` at the bottom, the last "running" with an empty time, against "each row shows the time"). The take's rows cannot be left out: the take runs them in the same command script. Caption, alt and shows now say that the four rows reading done or running belong to the take and that the screenshot was still running, so it has no time yet. The recipe's steps are unchanged, so the round 1 picture stands; no retake.
- activity-panel, at v0.8.0 (2026-11-24, pin 319075e3, published, `waitsFor` removed as `check` asked): good in round 1. The take's `scene.open` row now sits above `scene.loadStatus`, scrolled out of the 340 px panel, so eight of the nine rows show (`editor.wait` 985.9 ms, the screenshot running with no time). Caption and alt now say the ninth row is scrolled out above; alt split to keep sentences under 36 words.
