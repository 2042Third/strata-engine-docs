# Notes: animation/system

## Since

`since: 0.3.0`: the Animation module and its scene system landed in wave 3 (inventory `animation:24-27`, released 0.3.0).

## New terms

None proposed. The five glossary terms homed here are defined in bold: `ISkinningPoses`, animator record, asset set, attachment (socket), provider (of poses).

## Requests

- Layout `layouts/scene-hierarchy.ini` for the figure `menu-robot` (Scene view and hierarchy of the ThirdPerson sample's MainMenu scene, flag holder and flag visible).
- Figure `menu-robot` is not taken yet (screenshot 7).
- The three Mermaid diagrams (layers, frame order, update across threads) are for the site build to render.

## Not verified

- The `scene.open` parameter form `Assets/Scenes/MainMenu.stscene` in the figure recipe, and the layout name.
- What skinned meshes show in Simulate (brief item new:28): the page says only that no system and no service exist there; the capture decides the rest.
- Exercise 3 (break determinism by pushing events from the jobs) was not run; the page says so and says the failure may be intermittent.
- The Unreal and Unity statements in the alternatives table and Further reading (named, not linked, not checked against their documents).
- The `ozz-animation` row: that it samples compressed clips, taken from the inventory, not checked.

## Findings not applied

- `new:28` (Simulate and skinned meshes): not stated beyond the service rule; it waits for the capture.
- The perf budgets are not typed; the page links the performance reference.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

- `menu-robot` (editor, taken with the provisional build only; `waitsFor` kept). The recipe was a placeholder: its layout
  did not exist, `scene.open` named `Assets/…` and `play.start` came without steps, so the robot would be posed at no
  known frame. Round 1: the whole window at 960 × 540 on the new `layouts/scene-hierarchy.ini` (Hierarchy 220 px,
  Scene view 400 × 380, Inspector 336), the scene in the recipe's `scene` field, `play: {steps: 450}` (paused 1 s into
  the wave, which starts at 6.5 s), the flag selected then its holder; `camera.focus` came too close and the transform
  gizmo and the "Scripts built" toast covered the hand. Round 2: gizmo, scene gizmos and grid off
  (`viewport.setSettings`), a 600-frame wait for the toast, a set camera: still too close. Round 3: the editor camera
  at the menu camera's place, fov 32: the whole robot, its raised right hand, the flag outlined in orange (mostly
  behind the forearm), the Hierarchy with the holder selected and the flag as its child, and the Inspector with the
  holder's Attach To Joint (Animator Robot, Joint Palm2.R, scale 40). Caption, alt and shows rewritten to that picture;
  the flag itself is small and partly hidden, so the caption names the orange outline that shows where it is.
  Mend (viewer: from the front the flag showed only as two pole ends and a sliver of red behind the forearm): three
  editor cameras taken in one hold, from the robot's right side (-2.0, 1.8, -1.0), its right rear (-1.3, 1.9, -2.8)
  and its rear (2.0, 1.9, -3.1), each aimed at (1.0 to 1.1, 1.25, -0.2). The right side won: the dark pole and the
  red cloth stand clear of the forearm, outlined in orange, with the robot's head and raised arm beside them; the
  right rear showed the flag too but less of the robot, the rear only the pole. The alt now says the side view and
  names the pole and the cloth; caption and shows stay true.

## Pin move to v0.8.0

- Performance reference: the page names the metrics `Evaluate1000` and `CulledAnimators10k` of `Perf.Animation` and takes no number from the table (budgets appear only on the reference); both metrics still exist at 319075e3 (`StrataTests/Perf/Budgets.json`, `AnimationPerfTests.cpp`), and the `Perf.Animation` row still describes them. The 16.7 ms frame is 1/60 s, not from the table. No prose change.
- Figures: the `waitsFor` "tier 2: editor screenshot" entry is removed, since the pin has `editor.screenshot`.
- `menu-robot` taken at the pin's Release build (v0.8.0, not provisional), one round, unchanged recipe, and
  published: the game is paused, FlagHolder is selected in the Hierarchy with Flag as its child, and the Inspector shows
  scale 40 and Attach To Joint (Animator Robot, Joint Palm2.R). The dark pole and red cloth are outlined in orange in
  the raised hand, seen from the robot's right side. Caption, alt and shows hold. No earlier file was published, so
  there was nothing to compare.
