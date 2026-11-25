# Notes: animation/skeletons

## New terms

None proposed: the eight glossary terms of the brief are defined in bold on the page.

## Requests

- Figure `robot-skeleton` (Asset Inspector with the ThirdPerson robot's skeleton selected, Joints section): waits for `tier 2: editor screenshot` (see `## Figures`).
- Further reading cites Gregory, "Game Engine Architecture", the glTF 2.0 specification and Lengyel, "Foundations of Game Engine Development, Volume 1", without links; no host was added.

## Since

0.3.0: the skeleton asset and its STSK v1 format are listed as release 0.3.0 in the animation inventory.

## Not verified

- The Further reading entries (chapter and section names) come from general knowledge, not from the pin.
- The step count of "a quarter of the multiplications" is arithmetic on `MultiplyAffine` (48 of 64 scalar products), not a measurement.
- The page states the glTF importer makes entities only for joints with content from the engine's guide, not from `GltfImporter.cpp`.
- Mermaid diagrams are not rendered.

## Findings not applied

- The brief's size note (over M, take L) was overridden by the task: the page is size M and sits at the top of the range (4,000 words); the trace exercise is short.
- Brief item `animation:420` (screenshot with a clip's channels): only the skeleton half is requested; the clip half belongs to `animation/clips`.
- Item `animation:207` (skinned test helpers): only `CreateArmSkeleton` is described; the skinned helpers were not read.
- Exercise E1's "tip's position" is exercise 1 and the toy; the "child before parent" error is exercise 2 (a sketch).

## Clerk

- Lint warnings left: passive 25, noun-stack 5.

## Figures

- `robot-skeleton`, round 1 (provisional build 5b975ad2831e, not published): the recipe now uses the existing
  `layouts/materials.ini` (1280 × 800, Inspector column 380 px; no `skeleton-inspector.ini` was needed), finds the
  skeleton sub-asset with `asset.list {type: Skeleton, path: "Models/Robot/"}` and inspects it with
  `selection.set {asset}`, then waits 60 frames. The Asset tab shows the header, two yellow import warnings (morph
  targets not imported), "45 joints · root motion from Bone" and the joint list from RootNode down to the left hand,
  set in by depth, the icon of Bone in the accent color. Caption and alt were rewritten to that and shortened (the page
  sat over size M; the caption holds no number). Passed by eye; keeps `waitsFor` until the pin moves.
