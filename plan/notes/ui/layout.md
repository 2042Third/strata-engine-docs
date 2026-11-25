# Notes: `ui/layout`

## New terms

None proposed. The sixteen glossary terms homed here are defined in bold: anchor, root canvas, canvas unit, scale, reference resolution, safe area, pivot, margin, depth-first order, subtree range, sort order, measure, preferred size, layout group, fit content, clip rect. Match width or height is written plainly in a sentence that also describes it; it is a field name, not proposed as a term.

## Requests

- Figures: the brief's editor and scene figures are not requested. The page carries one Mermaid diagram (the map) and tables for the scale, array and menu numbers. Wanted if the planner adds pictures: the Tetris HUD at 1280x720, 2560x1440 and 21:9 on Scale With Screen and on Constant Pixel Size (needs a Tetris project recipe), the 4x4 anchor presets, and a vertical menu against a grid with Stretch Children off and on.
- Hosts: Further reading names Unity, Unreal, Yoga, Microsoft and Flutter documentation and the Cassowary paper without links; no host asked.
- Words avoided: "Cassowary", "flexbox", "WPF", "UMG" (spelled out or left to Further reading).

## Since

`since: 0.4.0`: `Docs/Releases/0.4.0.md` lists Game UI (canvases that scale with the screen, rects with anchors) as new in that release.

## Not verified

- That the sample's four menu buttons are in the order Play, Settings, Credits, Quit as siblings (they are listed in that order in `MainMenu.stscene`, all with the Buttons group as parent; the sibling order was not read from the hierarchy fields).
- The line height 1.2 em and the two wrapped lines in the "label that wraps" example are invented numbers (the page says so).
- Claims about other engines (Unity, Unreal, Godot anchors; Auto Layout on a solver; Yoga and flexbox; WPF and Flutter measure and arrange) are general knowledge, not checked against sources.
- The Tetris HUD's canvas settings were not read; the page states only what the GPU test checks.

## Findings not applied

None: the brief lists no open findings. Not carried from the brief's items: the editor-run figures (see Requests), the Inspector's inactive reasons (`gameui:45`, left to `editor-ui/inspectors`) and the Tetris HUD at three sizes as pictures (the page gives the numbers in a table for the main menu instead).

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
