# Notes: make/editor-tour

## New terms

None. Plain definitions (not bold): panel, pill, command, entity (homed on `make/scenes-entities`).

## Since

`since: 0.3.0`: the panels, menus and Scene view date from 0.3.0 (inventory `gamedev:43`, `gamedev:48-49`); the Game view is 0.4.0.

## Requests

- Layout files: `layouts/first-game-960.ini` (reused) and `layouts/editor-tour-side.ini` (Scene and Game views side by side, made by the photographer), named by `src/content/figures/make/editor-tour.json`.
- Figure `layout` needs labels drawn on the picture (panels, button strip, status bar); the recipe takes the plain editor.
- Figure `resolution-menu` (brief `gamedev:442`, the open menu) is not requested: the pin's recipes cannot open a chip's menu (tier 2: editor screenshot). The menu is described in prose.
- Tutorial: stage 1 to 3 are all end states of the same project; stage 3 runs `play.start` paused with `build: false`. Exercise 3's solution `tutorials/make/editor-tour/exercise-3.tutorial.json` starts from this page's tutorial. Exercises 1 and 2 are window tasks that no command does (`editor.showPanel` fails without a window).
- Further reading names the Strata manual page on the Scene and Game views without a link.

## Not verified

- The editor opens on `Scenes/Main.stscene` after Create: read from the `project.create` command text, not run.
- The Game tab drag to the right edge of the Scene view docks it beside: ImGui docking behavior, not run.
- A tab's close button (exercise 1's hint) and the empty tick box in **View** for a closed panel: read in `EditorPanelRegistry::DrawMenuItems` (tick = open), the close button is ImGui's.
- The editor camera saved with each scene (`editor-core:251`) is left out: not checked at the pin.
- Activity rows for `play.start` and `component.set` with source UI: the UI passes `CommandOrigin { CommandSource::UI }`; the journal's exact rows were not run.
- "Changes only" in the Activity panel hides query commands: from its tooltip.

## Findings not applied

- critic-make-a-1 (`make/project-files`, step 1) names another page; this page applies its half: **File ▸ Show Launcher** is grey while a project is open (`EditorLayer.cpp:1482`), and step 1 names **File ▸ Close Project** as the way.
- Brief item `gamedev:442` figure of the resolution menu: not drawn, see Requests.
- Brief says two exercises; the page has three (a Hard one done with commands) so that one exercise has a worked solution file.

## Clerk

- No term or word asked.
- Left for the planner: the layout files, the figures `layout` and `resolution-menu`, the tutorial's stages and exercises, and the manual link in Further reading.

## Figures

Taken 2026-11-18 with the provisional build (engine 5b975ad2831e, `--provisional`); every recipe keeps `waitsFor: tier 2: editor screenshot`, and nothing is published until the pin moves. All five use a 960 × 540 window.

- `result`: round 1 good with `layouts/first-game-960.ini` (was the 1280 × 720 `first-game.ini`, too small at the column's width). The ground is a light grey, not dark: alt rewritten.
- `layout`: cannot. The picture the recipe takes is the plain default layout (the same as `result`); no command draws labels on it. What the page needs: this take plus labels drawn over it (Hierarchy, Scene and Game, Inspector and Asset, Console, Problems and Content Browser, button strip, status bar), or a diagram of the four areas. The recipe is left as the base picture; caption and alt still say "marked".
- `ground-selected`: round 1 good. `camera.set` pitch is degrees up: the recipe's +25 would look up at the floor from below, so it uses -25. Caption and alt now say what shows: the floor from above at an angle, orange outline, arrows, the Inspector's parts.
- `no-camera`: round 2 good. New layout `layouts/editor-tour-side.ini` (Scene and Game views side by side, 277 px each; Hierarchy 180 px so that "Main Camera" is not cut, as it was at 150 px in round 1). Steps clear Primary and select Main Camera (step 10 clicks it); the Game view's text "No camera to show" reads at 1:1. The Inspector's Primary box is below the window's edge; the caption does not name it.
- `side-by-side`: round 2 good, same layout. `play.start` (no build: the template's scripts are unused), Game camera on; the status bar says Playing, the camera chip is lit, and the Scene view shows the Game view's picture with grid and axis lines. The editor camera of a new Basic 3D project starts where the Main Camera stands, so the Scene view looks the same with the chip off.

Mended 2026-11-18 after a viewer's report (provisional build, `--provisional`, still unpublished):

- `ground-selected`: the white wire box over the floor is the Main Camera's view lines (scene gizmos draw camera shapes). Every angle that shows the whole floor shows them, since the camera stands over the floor, so caption, alt and shows now name them; the picture is unchanged.
- `ground-selected`: step 6 of the page says "Click the dark floor in the **Scene** view", but the floor is light grey-brown in this picture and in `result`. The page's words need "grey floor"; left to the writer (photographers do not edit pages).
- `no-camera`: round 3 good. The Primary box was below the Inspector's edge at 960 × 540. New layout `layouts/editor-tour-side-600.ini` (the side-by-side layout for a 960 × 600 window, 60 px taller): the Inspector now shows the Camera component down to Primary (empty box) and Clear Color, and the Hierarchy reads "Main Camera" whole. Caption, alt and shows name the empty Primary box.

Taken and published 2026-11-23 at the pin v0.8.0 (319075e3), without `--provisional`; `check` asked to drop `waitsFor: tier 2: editor screenshot`, removed from the four published recipes. Nothing was published before, so nothing to compare.

- `result`, `ground-selected`, `no-camera`, `side-by-side`: round 1 good at the pin, the same as the provisional takes. Each claim of caption and alt is in the picture (five Hierarchy rows; the orange outline, arrows, white view lines and the Inspector's Transform, Mesh Renderer and Box Collider; "No camera to show" and the empty Primary box; status bar Playing, camera chip lit, the two views from the same place).
- `layout`: blocked, not published. The take is the plain default layout, the same picture as `result`; no command draws the labels the caption and alt name. `waitsFor` now reads `tier 3: labels drawn over the editor picture; no command marks the panels by name`. Nearest honest picture: `result.webp` with labels drawn over it (Hierarchy, Scene and Game, Inspector and Asset, Console, Problems and Content Browser, button strip, status bar), or a diagram of the four areas.
- `side-by-side`, viewer's fault 2026-11-23 (unclear: the lit camera chip sits beside three other lit chips and the caption never named it): stands, words only. The published picture shows the Game camera chip (photo-camera icon) lit, last in the Scene view's second chip row; the first row opens with a video-camera chip. Caption now names the Game camera chip and its place, alt says "Game camera chip". Picture kept, no retake: the take is right, only the words were unclear.

Finished 2026-11-24 at the pin v0.8.0 (the edition's last pin):

- `layout`: keeps `waitsFor` (tier 3, labels over the editor picture) as the request for a later edition; `standIn: layout-areas`.
- `layout-areas` (new, diagram): the default layout's areas drawn as boxes, each labeled with its tabs and share, the menus, button strip and status bar named with their contents. Read in `EditorLayer.cpp` (lines 79-81, 1610-1637): the bottom area is split from the center after both side columns, so it lies under the views only and the side columns run full height (the `result` picture agrees). Placed after the paragraph on the four areas, which now says the shares are of the space between the button strip and the status bar and that the bottom area lies under the views only (split into two paragraphs for the lint).
- The stage 1 checkpoint now shows `result` again (the project is unchanged by stage 1), as `make/scenes-entities` places its result twice.

## Settled with the editor (2026-11-18)

- Step 6 now says "gray floor" (the Basic 3D ground is light gray-brown). Step 7's `camera.set` and tutorial stage 2 use pitch -30: `EditorCamera` counts a positive pitch as looking up (`EditorCamera.h`, default -30), and a sentence after the fence says so.

## Tutorial run

- 2026-11-18, pin build, `tools/tutorials.py run`: passed, with exercise 3. Stage 2 now does what steps 6 to 8 tell:
  `selection.set` on `Ground`, `camera.set` (distance 10) and `camera.focus {entities: [Ground]}`, which answers a
  distance of 31.11 (the 20 by 20 floor fills the view). The file had called `camera.focus` without entities and
  expected 10; without a selection the command frames the whole scene.

## Track walk G-final-2 (2026-11-24)

Answers in `plan/walks/G-final-2.md` (WK1 to WK10). The walker drove the editor by command only, so each command tab
now says what its answer holds and what shows only in the window (`editor.screenshot` named once in What you need).
Step 3 says the layout is kept per user (`EditorLayout.ini` in the user's data, `StrataEditor/src/EditorApplication.cpp:401-407`),
so an editor used before opens with that layout. Step 11's tab and exercise 3 show `editor.activity {"source": "Automation"}`
and say the answer lists queries too; **Changes only** keeps only Edit commands (`ActivityPanel.cpp:186`), so it hides
`play.start`. Both tutorial files call `editor.activity`; exercise 3 checks a `command` filter.

## Engine

- No command closes a panel or resets the layout (`editor.showPanel` only opens one); a command reader cannot do
  exercises 1 and 2, and the page says so.
