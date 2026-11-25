# Notes: draw/mirrors-camera-relative

## New terms

None proposed. The page defines the four terms the glossary homes on it: camera-relative rendering, mirrored transform, origin rebasing, tangent handedness.

## Since

0.4.0: the inventory dates camera-relative space to 0.4.0 and mirrored instances to 0.3.0; the page is dated by its later subject.

## Requests

- Figure, not drawn: a mirrored asymmetric Showcase prop beside the original, with correct faces and normal map (items render-scene:442, render-core:538). The page has no figures file; the planner needs the Showcase prop's name and a recipe.
- Figure, not taken: the scene of `GPU.SceneRenderer.CameraRelative` at the origin and 100 km out. The "without" half is the page's Mermaid diagram of the flow; no switch turns camera-relative rendering off (render-core:839).
- Links to `batching.md`, `render-scene-gpu.md`, `skinned.md` and `motion-vectors.md` assume those pages exist.

## Not verified

- Whether the Showcase has an asymmetric prop suited for the mirror picture.
- The GPU-driven mode named Auto runs the GPU path in the test's scene (the test runs `Auto` and `Off`).
- `RenderScene.cpp` line 1596 computes the determinant a second time (another upload path); the page says only that placement sets the flag.

## Findings not applied

None open in the brief besides render-core:839, which the page applies.

## Clerk

- Nothing asked.
