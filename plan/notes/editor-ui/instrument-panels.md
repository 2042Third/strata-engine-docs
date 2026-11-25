# Notes: editor-ui/instrument-panels

## New terms

None.

## Requests

- The cell map capture is shared with `editor/worlds` (brief item `editor-ui:579`).
- Link targets of pages that did not exist yet when written: `../editor-ui/lists.md`, `../editor-ui/inspectors.md`, `../editor-ui/ui-testing.md`.

## Not verified

- That the status bar's Console pill shows the unread error count (the Console collects it; the pill's drawing was not read).
- That `StreamingPanel::OnImGuiRender` calls `UpdateTable` only while the panel is drawn (line 851 calls it; the surrounding condition was not read).
- The doctest summary line the runner prints after a suite.

## Findings not applied

None: the brief lists no open findings.

## Since

0.3.0: the panels belong to the editor's first releases; no per-panel release evidence was checked.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

Settled 2026-11-18 with the provisional build (engine 5b975ad2), each picture checked by eye; all five keep `waitsFor` and are published only once the pin has `editor.screenshot`. The planned layout `layouts/instrument-panels.ini` now serves only streaming-cell-map; the others reuse layouts of the same size that other pages proved.

Published 2026-11-23 at the pin v0.8.0 (319075e3): one take each, `waitsFor` removed as `check` asked, every picture checked by eye and matching the notes below (the Problems row C2143 at line 13; the Console's red message naming `Scripts\Coin.cpp(13,2)` under the take's work folder, no user name; the Activity rows and the take's own last three; one red spike marker on the CPU chart; 52 loaded and 45 unloaded cells). Only the performance-timeline alt changed: the GPU columns barely rise above the base line at 5 ms full scale, so it no longer says "two charts of colored columns".

- problems-failed-build (round 1): the basic3d template with `tutorials/make/first-script/CoinNoSemicolon.cpp` as `Scripts/Coin.cpp` (a smaller build than ThirdPerson's 15 files), the Problems panel at 673 by 240 px: "Build 1 failed: 1 error, 0 warnings." and one row, C2143 in `Scripts/Coin.cpp` at line 13. Matches the page and exercise 2.
- console-source-reference (round 1): same failed build, the Console at 673 by 300 px. Commands cannot hover, so the hand cursor and the "Click to open ... at line ..." tooltip the page describes cannot show; the recipe pictures the state before the hover: the red "Script build 1 failed" message whose second line names `...\Scripts\Coin.cpp(13,2): error C2143`, the message that holds the source reference. Caption and alt were rewritten to that. The message shows the take's absolute project path (the work folder under the engine checkout, no user name); the pin's take will show its own work folder there. The page's words would need a diagram or a hand-taken picture for the tooltip.
- activity-details (round 1): no command selects an Activity row (`ActivityPanel::Select` is called only by the toasts' **Show in Activity** button, a click), so the selected entry's JSON details and the **Copy as script**, **Re-run** and **Undo to here** buttons cannot show. The recipe pictures the rows instead: five edit commands (create, set scale, create, delete, undo) and, last, the take's own `editor.wait`, `editor.showPanel` and `editor.screenshot`, with the filter field, **Every source** and **Changes only** above; caption, alt and shows describe the rows. The id stays. For the details, the page would need a diagram of the details area, or a command that selects an entry (a request for the engine: `editor.showPanel {panel: "Activity", entry: <id>}`).
- performance-timeline (round 1): ThirdPerson, `play.start` (it builds the scripts), 300 frames, the Performance panel at 860 by 760 px (`layouts/make-performance-tall.ini`). The CPU chart carries one red spike marker at the top, the frame where play started (max 46.5 ms against a median near 1 ms); under the charts the stage table and the "Capped: 8.3 ms frames ..." line (vsync), which is the line that says what bounds the frame. Caption names the red marker.
- streaming-cell-map (round 2): round 1 opened OpenWorld's Island world with the editor camera away from every cell: 0 loaded, an empty map. Round 2 sets the camera to (40, 45, 90) looking at the origin and waits 300 frames: 52 cells loaded in orange, 45 unloaded in dark gray, inside the blue circle. `layouts/instrument-panels.ini` (1280 by 1040, bottom tabs 920 by 760 px) makes the panel wide enough to put the asset table beside the overview (`c_SideBySideWidthInFontSizes`), so the caption's "beside it" holds; the Mip column does not fit at that width.
