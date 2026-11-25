# Notes: `basics/math-projection`

## New terms

- **view space**: the coordinate system whose origin is the camera, with +X to its right, +Y up and -Z straight ahead. Home: `basics/math-projection`. Aliases: camera space, eye space.
- **image plane**: the flat surface at distance 1 in front of the camera, at a right angle to its view direction, on which every point is drawn. Home: `basics/math-projection`. Aliases: none.
- **aspect ratio**: the width of the picture divided by its height. Home: `basics/math-projection`. Aliases: none.
- **ray**: the line of points, from the camera, that all draw to one pixel. Home: `basics/math-projection`. Aliases: none (`basics/math-geometry` may widen it).

The page also defines in bold the sixteen terms the brief lists (clip space, depth, depth buffer, far plane, field of view, homogeneous coordinates, near plane, NDC, orthographic projection, perspective divide, perspective projection, projection, projection matrix, reversed Z, view frustum, view matrix).

## Requests

- `tools/data/extra-words.txt`: none needed; the lint passes.
- `tools/external-hosts.txt`: `registry.khronos.org`, for the OpenGL specification cited (unlinked) in Further reading.
- Figures: four diagram requests in `src/content/figures/basics/math-projection.json` (similar triangles, the frustum, depth against distance, NDC to pixels). None is drawn yet. The pipeline of spaces is a Mermaid diagram on the page.
- Links to pages not yet written: `gpu/coordinates`, `draw/bounds-culling`, `light/shadow-basics`, `light/local-shadows`, `image/taa`, `core/math`, `basics/math-geometry`, `basics/programming-3`, `reference/notation`.

## Not verified

- That the editor's Inspector shows the Camera fields as `PerspectiveFOV` and so on: the page writes the property names of `ComponentRegistration.cpp`, not their displayed labels.
- That Coin Run has a camera with the default field of view, and how its coins are placed: `make/project-coin-run` is not written; the Coin Run item is a standalone sketch plus a prose description of the script.
- That a renderer using reversed Z clears its depth buffer to 0 and keeps the larger value: stated as the mathematics of reversed Z, not as something checked in Strata's renderer.
- OpenGL's depth range of -1 to 1 and the other APIs' differences: general knowledge, cited in Further reading only.
- The yaw direction of the quarter-turn example (a camera looking along -X is turned to the left): follows from the right-handed axes, not from a run.

## Findings not applied

- None. critic-basics-b-3: Practice has six exercises, one run as a sketch (the Coin Run item). critic-basics-b-11: the paragraph of the Camera fields stands in the orthographic section, with `GetProperty<float>("Camera", "PerspectiveFOV")`. critic-basics-b-13: the caution beside reversed Z names `GLM_FORCE_DEPTH_ZERO_TO_ONE` (checked in `StrataScriptCore/CMake/StrataScriptCoreConfig.cmake:31`), the swapped `glm::perspectiveRH_ZO` of `Math.cpp:71-75`, and the float aspect ratio with the 0 check.

## Remaining pagecheck notes

- Lint passes with 23 warnings (passive voice, two noun stacks), left as natural wording.
- The `sketches` check fails on `sketches/basics-bytes-bounds.cpp`, another page's file; this page's four sketches compile.

## Clerk

- Admitted: view space (aliases camera space, eye space), image plane. Refused: ray (homed on `basics/math-geometry`).
- `external-hosts.txt`: `registry.khronos.org` (front page fetched: the Khronos Registry).
- Not admitted, because the page check would then fail and the page is the writer's: aspect-ratio (the section "Perspective divides by the distance" would define 5 terms (term-section)). The part's reviewer splits the paragraph or section or bolds the term; the next clerk admits it then.

## Track walk E, final, segment 3 (2026-11-24)

- WK6 (`plan/walks/E-final-3.md`): the definition of Depth broke its line before "1.", which markdown read as the start
  of a numbered list, so the sentence ended at "from 0 to". The line now breaks before "to 1.", and the depth buffer has
  its own paragraph (lint's `term-paragraph` saw the two terms once the list was gone).
- WK1: Practice 6, the Coin Run item, is a program on its own and needs no project, so it names no checkpoint.
