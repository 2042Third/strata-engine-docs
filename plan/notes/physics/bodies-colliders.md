# Notes: physics/bodies-colliders

## New terms

None. The thirteen terms of the brief are defined in bold on the page.

## Requests

- Figures `colliders-gizmos` (variants off and on) and `rigid-body-inspector` wait for editor screenshots (tier 2); recipes settled with the provisional build (see Figures).
- No external hosts requested; Further reading entries are cited without links.

## Since

0.3.0: bodies, the four collider components and the composition rule exist since the first physics module (inventory physics:28-32); box3d replaced Jolt in 0.5.0, and the page does not depend on the library.

## Not verified

- The viewport's label "All Colliders": the pin has the setting `allColliders` (EditorViewportCommands.cpp) but no UI string was found; the page writes it as plain text.
- The Physics Playground's crate stack as the figure scene: the sample's scene was not opened.
- Claims about Unity (Rigidbody with child colliders) and Godot (body node with shape nodes) are from general knowledge and the brief; no source was opened.
- The kinematic body's refusal of velocities, forces and impulses is from the brief; the header says only that SetLinearVelocity and SetAngularVelocity are for dynamic bodies.
- Float spacing near 100,000 m (about 8 mm) is the page's own arithmetic, not an engine fact.
- The step of 1/60 s is not used on the page; no timing claim is made.

## Findings not applied

- The brief lists no open findings. Item `new:11` (exercises): applied as a sketch for the mixing rule and ramp and as paper exercises for the hierarchy; the doctest with `PhysicsStats` counts and the editor ramp task were not written (no patch or tutorial file), because the card asks for the sketch form on track E and the page does not teach the engine change.

## Figures

2026-11-23, pin v0.8.0 (319075e3): both recipes taken again without `--provisional` in one hold, unchanged, one round
each; `waitsFor` removed as `check` asked. Published: `colliders-gizmos` (off and on) and `rigid-body-inspector`. The
pictures match the provisional takes described below: off shows the crates only, on adds green wires on every crate's
edges, the crate column and the walls' tops, nothing else changes; the Inspector shows `Crate (20)` whole (Rigid Body
Dynamic, mass 20, damping 0.05 and 0.5, gravity scale 1, friction 0.8, restitution 0.05, ticks clear, Layer 0; Box
Collider half extents 0.5, offset 0), with the Script section's "No script module is loaded" line below. Captions, alt
and shows hold. Never published before, so nothing to compare.

Earlier, with the provisional build only (2026-11-18):

- `colliders-gizmos` (1 round): the Viewport panel of `layouts/scene-view.ini`, nothing selected, the editor camera on
  the crate pyramid (target -7.95, 2.6, -12; yaw 25, pitch -15, 10 m, fov 40). Off: crates only. On: green wire boxes
  on every crate, the crate column and the tops of the walls. The crates' mesh is the built-in Cube, so each wire box
  lies on its mesh's edges; the Ground's box (offset 0.5 m down) is not seen at this distance. Caption and alt say so.
  The page's sentence "the crate is a detailed mesh, and its collider is a plain box" is not true of this sample: it
  needs a crate with a modelled mesh, or the words "the crate's mesh is a cube, and its collider is a box drawn on the
  cube's edges". No other object can stand in: the sample has no model asset (no `Models` folder) and its 641 Mesh
  Renderers use only the built-in meshes (handles ...01, ...02, ...03, ...05), so the words are the page writer's fix.
  Round 2 (review, same recipe, provisional build, under the lock): retaken because the inspector-only take had emptied
  the shots. Off and on checked side by side: the stepped crate pyramid, the crate column at the left and the brick
  walls behind; on adds green lines on every crate's edges and along the walls' tops, nothing else changes. Caption,
  alt and shows hold.
- `rigid-body-inspector` (2 rounds): `Crate (20)` selected through `entity.find`. Round 1, `layouts/make-animation-tall.ini`
  (1280 x 960): cut at Lock Rotation Y. Round 2, `layouts/make-look.ini` (1280 x 1360): the whole Inspector, with
  Rigid Body (type to layer) and Box Collider (half extents 0.5, offset 0) open, Script below. The provisional
  picture also shows the Script section's line "No script module is loaded", since the sample's scripts are not built.
  No layout `inspector.ini` was made: an existing one serves.

## Clerk

- Nothing to admit.
