# Notes: make/scenes-entities

## New terms

None. The page defines scene, transform and built-in mesh in bold.

## Requests

- Layout file `layouts/make-scenes-entities.ini` for the six editor figures (Hierarchy and Inspector side by side).
- Figure `create-menu` needs the open plus menu: `waitsFor` is `tier 2: editor screenshot`.
- The tutorial starts from `make/editor-tour`, whose tutorial file does not exist yet (written by that page).
- Names the dumps lack at the pin: the labels Mesh only and Core (menu entry and category heading of `SceneHierarchyPanel.cpp` and `InspectorPanel.cpp`).

## Not verified

- The native file dialogs of Save Scene As and Open Scene (what they show, how a folder is chosen).
- That the Inspector's check box of a child under a switched-off parent keeps its own state (the page does not claim it).
- That entity.find returns inactive entities (the tutorial finds before switching off).
- Quaternion order x, y, z, w in `component.set` values (taken from the first-script tutorial's checks).
- The `entityName` key and `selection.set` with an empty list in figure setups.

## Since

0.3.0: Hierarchy, Inspector, components and reflection-driven editing 0.3.0 (inventory gamedev:50, :51, :68); colliders on presets 0.4.0.

## Findings not applied

- critic-make-a-7: applied in one sentence (Create Child beside the plus button, step 4 of the walls).
- critic-make-a-15 and critic-make-a-19: applied (Translation named; camera step with Translation 0, 16, 13 and Rotation -55, 0, 0).
- The built-in mesh and component counts: no count written (new:1).

## Clerk

- No term or word asked.
- Left for the planner: the layout file, figure `create-menu`, the tutorial's start (`make/editor-tour`) and the names the dumps lack (Mesh only, Core).
- The build's checkpoint rule (pages.py now reports it): the section that explains entities and components moved before "## What you need", and the note after the Ground's checkpoint moved before it.

## Figures

- `result`, `level-walls`: taken with the recipe's raised camera (0, 16, 13, pitch -55) and published in round 1;
  only the shows and alt changed: the ground renders mid grey, not dark, and the walls pale.
- `level-ball-coin`: round 1 from the same raised camera repeated `result` (only the wall height differs) and showed
  the coin at about 20 pixels; round 2 (camera low at 4, 2.5, 9) put the ball at the frame's edge and the white coin
  against the white back wall; round 3 (camera 4, 5, 9 toward 0, 1.05, 3.3, fov 45) shows the ball close by and the
  upright coin against the floor, its edge and detached shadow visible. Published; caption rewritten to this view.
- The coin (centre 0.8, radius 0.4) hovers 0.4 m above the ground: its shadow lies apart from it. The page's
  "a flat disc standing on its edge" names the orientation; the caption says it stands a little above its shadow.
- Viewer's review (2026-11-18), words only, no retake: `result` shows the coin about 35 px wide of 1920 (some 12 px
  at page width), too small to read as upright, so caption, alt and shows call it the small coin near the back;
  `level-ball-coin`'s "stands on its edge" read as resting on the floor, so the caption now says the coin hangs upright
  with its centre 0.8 m up and its shadow apart (`numbers` gives the setup's Translation and Scale). Pictures unchanged.
- Editor figures (2026-11-18), taken with the provisional build only; not published, each keeps `waitsFor`:
  - `ground-inspector`: round 1 pictured the Inspector alone (`panel`) in a 1280 x 800 window: readable, but the
    caption's "a name ... one section each" was wrong (the name sits in the header beside the ID, three sections
    follow) and the lower fifth was empty. Round 2: layout `make-scenes-entities-inspector.ini` (1280 x 660, Inspector
    380 px); caption, alt and shows name the header and the three sections. Good.
  - `walls-mixed`: the Inspector alone, same layout: "4 entities", Translation and Scale show two dashes on X and Z
    and 0.75 and 1.5 on Y. Good in both rounds; alt and shows now give the values.
  - `nothing-selected`: round 1 (960 x 540, Inspector 300 px) cut "entities per frame" and counted 10 entities: the
    recipe lacked the ball and the coin that the page's reader has. Round 2 adds them (12 entities) and uses layout
    `make-scenes-entities-short.ini` (960 x 440, Inspector 380 px): nothing cut. Good.
  - `walls-off`: round 1 showed the dimmed Walls row, but the Scene view's editor camera saw the ball and the coin as
    dots near the horizon. Round 2 adds `viewport.setSettings {pilotGameCamera: true}`, the Game camera chip the
    page's walls step 5 turns on: the whole ground, the ball and the coin, no walls. The Inspector's check box shows
    clear; caption and alt say so. Good.
  - `scenes-two`: good in round 1: the Hierarchy reads "The scene is empty" with Cube and Light buttons, the Scene
    view only the grid, the Inspector "Test", 0 entities. Alt rewritten to that. The figure stands after step 2,
    which opens `Main` again, while the picture shows step 1's empty `Test`: the page's words would need the figure
    after step 1, or the caption read as step 1's state (it does).
    Viewer's review (2026-11-18): the Hierarchy (180 px) cut the third quick-add button, Camera, and the Inspector cut
    Streaming's "5000 / 5000 entities per frame"; the caption did not say the picture is step 1's state. Round 2: own
    layout `make-scenes-entities-wide.ini` (960 x 540, Hierarchy 260 px, Inspector 340 px, the shared layout left to
    `walls-off` and `create-menu`): Cube, Light and Camera whole, the Streaming line whole; the narrower Scene view
    wraps its toolbar onto two rows and cuts the Content Browser tab, neither named by the caption. The caption now
    starts "After the first step" (a digit there fails `check`), the alt names a cube, a light or a camera. Good.
  - `create-menu`: commands cannot open the plus menu (an open menu is a popup), so the picture cannot show it; the
    recipe is left as written, waiting. What the page can get instead: the state after choosing **Cube** (a `Cube`
    row selected and the Inspector with Transform, Mesh Renderer and Box Collider), with a caption that names the
    menu's entries in words, or a diagram that lists the menu's groups (shapes with a collider, Mesh only, Camera,
    lights, interface items).

## Settled with the editor (2026-11-18)

- `scenes-two` now stands inside step 1 of "Keep more than one scene", whose state (the empty `Test`) it shows. Checkpoint 5 shows `result`, the finished level with `Main` open again, as the last checkpoint of make/lighting does.
- Step 1 of reading the Ground: the header holds the name and the ID, and the page counts three sections after it; no change.

## Tutorial run

- 2026-11-18, pin build, `tools/tutorials.py run`: passed unchanged, with exercises 1 and 2, once
  `make/editor-tour` passed.
- 2026-11-23, pin v0.8.0 (319075e3): the tutorial (5 stages) and exercises 1 and 2 passed as written in round 1,
  the chain before it replayed. Pagecheck's only failures are not the tutorial's: `excerpts` stopped on another
  agent's unfinished `tools/excerpts.py` (the committed tool finds 0 problems), and `figures` lists the six editor
  figures still carrying `waitsFor "tier 2: editor screenshot"`, which the pin's `editor.screenshot` now serves.
- Pin v0.8.0 (319075e3, 2026-11-23), one hold, one round:
  - `result`, `level-walls`, `level-ball-coin`: retaken and compared with the published originals (`figures.py
    compare`): identical, 0 of 3 differ; `publish` left the files and stamps unchanged (same original).
  - `ground-inspector`, `walls-mixed`, `nothing-selected`, `walls-off`, `scenes-two`: taken at the pin without
    `--provisional` (the pin has `editor.screenshot`; `waitsFor` removed) and published. Each shows what its caption,
    alt and shows say: the Ground's header with ID and three sections; 4 entities with dashes on X and Z and 0.75 and
    1.5 on Y; Main, 12 entities and the closed Physics, Streaming and Sky sections; the dimmed Walls row, the clear
    check box and the walled-off ground seen through the game camera; Test with the empty Hierarchy (Cube, Light,
    Camera buttons) and 0 entities.
  - `create-menu`: not taken. No editor command opens the Hierarchy's plus menu (a popup), so `waitsFor` is now
    `tier 3: the Hierarchy's plus menu open; ...`. The page does not place this figure. Nearest honest picture: the
    state after choosing **Cube** (a `Cube` row selected, the Inspector with Transform, Mesh Renderer and Box
    Collider) with the menu's entries named in words, or a diagram of the menu's groups.
- Last pass (2026-11-24, pin 319075e3, final): `create-menu` still cannot be taken (no editor command opens the plus
  menu, a popup); it keeps its `waitsFor` as the request for a later edition and names its stand-in
  `create-menu-drawing`, a sketch of the menu drawn from `GetPresets`, `GetMeshPresets`, `GetMeshOnlyPresets` and
  `DrawCreateMenu` (SceneHierarchyPanel.cpp): Empty, the seven shapes with the collider each adds (Box, Sphere, Box,
  convex Mesh, Capsule, convex Mesh, convex Mesh), the Mesh only list without colliders, Camera, five lights, Post
  Process, 3D Text, Audio Source and the closed UI list. Chosen over the state after choosing Cube, which
  `ground-inspector` and step 1's words already show. It stands after the opening paragraph of "Add the ball and the
  coin", whose sentence now introduces the menu and its Mesh only list; rendered in both themes, `drawings.mjs check`
  passes.
- Final runs (2026-11-24, pin 319075e3): the pin-build stamps were current (`tutorials.py check` found nothing); the
  official v0.8.0 package (`Strata-0.8.0-windows-x64.zip`) ran the tutorial (5 stages) and exercises 1 and 2, the
  chain before it replayed: all passed as written in round 1. `check --release` finds nothing; pagecheck passes.

## Track walk G-final-2 (2026-11-24)

Answers in `plan/walks/G-final-2.md` (WK19 to WK25). What you need offers the tour's last checkpoint. The tabs say that
`component.get` returns Rotation as the stored quaternion and `entity.get` with `world` gives the angles; step 4's tab
creates `Walls` with `entity.create` and names its `parent`; the search tab says `entity.find`'s name is exact and
names `editor.showPanel` with `search`. The tutorial file checks the four stored numbers (stage 1) and that
`entity.find {"name": "Wall"}` finds one entity (stage 4).
