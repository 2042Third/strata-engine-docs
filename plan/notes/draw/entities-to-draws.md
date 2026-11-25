# Notes: draw/entities-to-draws

## Since

The render scene and its proxies are 0.3.0 features (render-scene:30); the GPU-driven path is 0.4.0 but the page's learn lines concern the retained design of 0.3.0.

## New terms

- Instancing: one draw call that draws the same mesh many times, each copy with its own data (home: this page).
- Indirect draw: a draw call that reads its arguments from a buffer instead of from the CPU (home: this page).
- Immediate representation: a list of drawables built again each frame by walking the scene (home: this page).
- Retained representation: one persistent record per drawable, updated from change signals (home: this page).
- GPU scene: the retained records kept in GPU memory, with the GPU building the draws (home: this page).

## Requests

- Layout: none new; `stats-overlay` uses `layouts/scene-view.ini` (1280 x 720) and pictures the Scene view panel alone.
- Hosts and words: none; the Further reading entries carry no links.

## Not verified

- The Showcase's own numbers on the Stats overlay: no capture was taken, so the page shows none.
- The claims about Unity's built-in pipeline, Unreal Engine's proxies and GPU scene come from general knowledge, not from the pin.
- The cost of a draw call on the CPU and the GPU is described in general terms, without a measurement.
- The Further reading titles are cited from memory and need a check by the planner.

## Findings not applied

- The brief names `editor.state` for `renderStats`; at the pin the command is `editor.perf` (`EditorStateCommands.cpp`), and the page says `editor.perf`.

## Clerk

- Admitted terms homed here: immediate representation, retained representation, GPU scene.
- Refused as terms: instancing (homed on ui/drawing) and indirect draw (homed on draw/batching): only their homes word them.

## Figures

- `stats-overlay`, round 1 (provisional build): the Showcase's saved editor camera looked at the haze above the ground, so the overlay stood over an empty picture. Round 2 adds the camera of `editor-ui/scene-view`'s `scene-view-layers` (drums and tires before the old bus) and waits 300 frames: the overlay reads at 1:1, counts visible proxies out of all proxies and shows 0.0 KB of instances uploaded, as the paragraph says of a still frame. Caption and alt name no counts, since the pin's numbers can differ. Keeps `waitsFor` until the pin moves.
- `stats-overlay`, viewer's review (provisional build): the picture is right, but the paragraph after the figure says "The scene holds thousands of entities" while the overlay reads 99 visible of 472 proxies, and the Outpost scene document holds 331 entities (about 800 entity IDs with its children). No sample holds thousands, and the page's first paragraph sends the reader to the Showcase, so no recipe change can make the sentence true. The page's words need "A scene can hold thousands of entities" (or "hundreds"); this pass may not edit them. Nothing retaken.
- `stats-overlay`, taken at the pin v0.8.0 (319075e3), one round: the same view; the overlay reads 59 draw calls,
  90 instances, 99 visible of 472 proxies, 0 updated, 0.0 KB instances uploaded, in twelve lines at the top left. A
  third, dim blue drum stands behind the overlay, so the alt now names the red and the blue drum in front instead of
  "two drums". Published. The page now says "hundreds of entities", true of the picture.

## Pin move to v0.8.0

Rechecked every number and name the page shares with `reference/renderer`; none changed, so the page is unchanged.
The overlay lines and their order match `StrataEditor/src/Panels/ViewportToolbar.cpp:131-146` (the GPU line with its
three largest stages, two or three frames late, `:95-114`; the shadowed-lights line is not in the page's table, which
lists the lines that matter here). Every `renderStats` key of the page's group table is still in
`StrataEditor/src/Editor/EditorStateCommands.cpp:244-286`, and `sceneMirrorMB` still doubles while a scene plays (its
comment, `:284`). The draw-call fields keep their meaning (`Strata/src/Strata/Renderer/SceneRenderer.h:556-572`),
`GPUDrivenMode` keeps `Auto` and `Off` (`:113-117`), the gathering chunks keep 2,048 proxies
(`SceneRendererExtraction.cpp:70`), the batch key leaves the material out by default (`BatchAcrossMaterials`,
`:1033`), every stage of the two-lane diagram is still a function of `SceneRenderer`, and `Docs/Architecture.md:2264`
still gives about 36 ms for 100,000 mesh renderers (Release).
- Pin move to v0.8.0: `waitsFor` removed, since the pin has `editor.screenshot` (pagecheck asked for it); the picture is taken by the figure pass.
