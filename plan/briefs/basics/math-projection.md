# Brief: `basics/math-projection`

| Field | Value |
| --- | --- |
| Title | Cameras and projection: perspective, homogeneous coordinates and depth |
| Kind | P |
| Size | L |
| Tracks | B, E |
| Needs | `basics/math-matrices` |
| From | foundation "The math toolkit" (the mathematics: projections); view and projection matrices, perspective and orthographic, homogeneous coordinates, frustums, depth and reversed Z as mathematics (Lengyel, *Foundations of Game Engine Development* vol. 2 ch. 6); Strata's conventions are `gpu/coordinates`', the code `core/math`'s |
| Unit | `plan/allocation/basics-b.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/math-projection` — Cameras and projection: perspective, homogeneous coordinates and depth

**Covers.** In order: (1) the camera as an entity with a transform, view space (the camera at the origin, looking
along -Z), and the view matrix as the inverse of the camera's world transform; (2) perspective by similar triangles: a
point's place on the image plane is x divided by its distance, so far things look smaller; the field of view and the
aspect ratio, and tan(fov / 2) as the half-height of the picture at a distance of 1 (the mathematics behind the recipe
of `make/gameplay-math`); from a direction to a point on the screen; a cube face as a square view with a 90° field of
view, six of which see every direction; (3) homogeneous coordinates: the projection matrix writes the distance to
divide by into w, its result is clip space, and the perspective divide gives normalized device coordinates (NDC), with
x and y from -1 to 1 and +Y up, then pixels, with row 0 at the top; (4) depth: the near plane and the far plane, the
view frustum that they and the field of view bound (a pyramid with its top cut off), the depth buffer that keeps the
nearest surface for each pixel, and why depth after the divide is not spread evenly over the distance; (5) reversed Z:
the near plane stored at 1 and the far plane at 0, and in one paragraph why this suits floating-point numbers, which are
dense near 0 (the precision plot, Strata's depth precision and the far plane at infinity are named with their page,
`gpu/coordinates`); (6) the orthographic projection, where nothing gets
smaller with distance (shadow maps, side views); (7) going back: from a pixel and its depth to a position in view space
(the inverse projection), and the ray through a pixel, read in the Physics Playground's `GetPointerRay`. The page uses
the conventions of `style.md` §4 (NDC +Y up, depth from 0 to 1, reversed Z, origin at the top left) and says that other
graphics APIs differ, with a link to `reference/notation`.

Figures: similar triangles from the side, the frustum with its six sides, depth after the divide against distance, NDC
to pixels. The common mistakes: a field of view in degrees where radians go, the aspect ratio inverted, a near plane at
0, depth read as a distance, a depth range of -1 to 1 expected. Practice (three to eight exercises, `style.md` §8) ends
with the optional Coin Run item: count the coins the camera sees, by taking each coin's offset from the camera along
the camera's right, up and forward (three dot products) and testing it against tan(fov / 2) and the aspect ratio.
"Where the book uses it" names `gpu/coordinates`, `draw/bounds-culling`, `light/shadow-basics` and `image/taa`.

**Leaves out.**

- Strata's clip space, the viewport flip, the precision plot of reversed Z, depth precision in the engine and the far plane at infinity → `gpu/coordinates`
- `PerspectiveReverseZ`, `PerspectiveReverseZInfinite`, `OrthographicReverseZ` and `Ray::FromNDC` in code → `core/math`
- Planes, and testing spheres and boxes against the frustum's planes → `basics/math-geometry`
- Extracting the frustum's planes from a matrix, and culling → `draw/bounds-culling`
- Jitter and reprojection with the previous frame's matrices → `image/taa`
- Cube shadow maps → `light/local-shadows`
- The camera's lens and field of view, for makers → `make/look`
- Cube maps as a way to store directions → `basics/math-sphere`

**Fit.** `fits`: about 5,900 words against L (5,000). The seven ideas take the most: six from zero at 500 words each,
the upper value for B0, and reversed Z, now the mapping and one paragraph on floats, at 300 (3,300). The four figures
(600), the five common mistakes (600), the pointer-ray excerpt (200), the opening (100) and the fixed parts with the
Test out box, Practice and the Coin Run item (1,100) take the rest.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:26` | concept | home | The view matrix and view space: the camera at the origin, looking along -Z; the view matrix as the inverse of the camera's world transform. General knowledge. |
| `new:27` | concept | home | Perspective by similar triangles: the image plane, the field of view, the aspect ratio, tan(fov / 2); a direction to a point on the screen; a cube face as a 90° square view. Figure: similar triangles. General knowledge. |
| `new:28` | concept | home | Homogeneous coordinates and the projection matrix: clip space, the perspective divide, normalized device coordinates, then pixels. Figure: NDC to pixels. General knowledge. |
| `new:29` | concept | home | Depth: the near plane, the far plane, the view frustum, the depth buffer, depth that is not linear in distance. Figures: the frustum, depth after the divide against distance. General knowledge. |
| `new:30` | concept | home | Reversed Z as mathematics: the near plane at 1 and the far plane at 0, and in one paragraph why it suits floats, which are dense near 0. The precision plot, Strata's depth precision and the far plane at infinity are `gpu/coordinates`' (book.md's row of projection). General knowledge. |
| `new:31` | concept | home | The orthographic projection, which keeps sizes at every distance. General knowledge. |
| `new:32` | concept | home | Going back: the inverse projection from a pixel and its depth to a position, and the ray through a pixel. General knowledge. |
| `new:33` | hands-on | home | Coin Run practice, from `make/project-coin-run`'s end state: count the coins the camera sees from the offset along the camera's right, up and forward and from tan(fov / 2) and the aspect ratio. Evidence: `StrataScriptCore/Include/StrataScript/Entity.h:227-229` (`GetForward`, `GetRight`, `GetUp`), `StrataScriptCore/Include/StrataScript/Game.h:95` (`GetWindowSize`), `Samples/PhysicsPlayground/Scripts/Playground.cpp:200` (the camera's `PerspectiveFOV` in degrees) |
| `foundation:633` | term | home | NDC, after the projection and the divide; one glossary entry with the seed's and `render-core:728` |
| `render-core:728` | term | home | Clip space and NDC as the GPU part's glossary words them: the coordinates after the projection, then after the division by w, x and y from -1 to 1; one glossary entry each with the seed's and `foundation:633`; Strata's convention stays on `gpu/coordinates` |
| `foundation:634` | term | home | Reversed Z, near at 1 and far at 0, for the precision of floats; one glossary entry with the seed's and the four items of the next row |
| `render-core:730`, `editor-core:733`, `render-direct:716`, `render-scene:608` | term | home | Reversed Z as the GPU, editor, lighting and drawing parts word it (depth 1 at the near plane and 0 at the far plane; nearer to the light is larger; the farthest is the smallest value); one glossary entry with `foundation:634` and the seed's; the precision argument stays on `gpu/coordinates` |
| `render-scene:593` | term | home | The frustum as the volume the camera sees, bounded by six planes; homed here, where the seed homes the view frustum, and tested against on `basics/math-geometry` |
| `gamedev:382` | code | use | `Playground::GetPointerRay` (`Samples/PhysicsPlayground/Scripts/Playground.cpp:183-207`): a pixel taken back to a direction from the field of view, the aspect ratio and the camera's axes; its home is `make/gameplay-math` |
| `foundation:370` | code | link | The reversed-Z projections of `Math.cpp` 71-91, which `core/math` walks through |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Matrices, the inverse, 4×4 matrices with w, local and world space | `basics/math-matrices` | must |
| Vectors, the dot product, sine, cosine, the tangent function and radians | `basics/math-vectors` | must |
| Floating-point numbers, whose spacing grows with their size | `basics/numbers` | must |
| A pixel and a frame | `start/what-an-engine-is` | helps |
| The camera entity in the editor | `make/look` | helps |

**Starting state.** The optional Coin Run item of Practice starts from the download of `make/project-coin-run`'s end
state, as the outline's introduction of part `basics` says for every primer after `basics/debugging`: Coin Run as
`make/project-coin-run` finishes it, with the rolling ball, the spinning coins, the HUD, the sounds, winning, losing and
the restart. The page's other examples and exercises run in the playground (`style.md` §8), which is no checkpoint.

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `clip-space` | clip space | - |
| `depth` | depth | - |
| `depth-buffer` | depth buffer | z-buffer |
| `far-plane` | far plane | far clip plane |
| `field-of-view` | field of view | FOV |
| `homogeneous-coordinates` | homogeneous coordinates | - |
| `near-plane` | near plane | near clip plane |
| `normalized-device-coordinates` | normalized device coordinates | NDC |
| `orthographic-projection` | orthographic projection | - |
| `perspective-divide` | perspective divide | perspective division |
| `perspective-projection` | perspective projection | - |
| `projection` | projection | - |
| `projection-matrix` | projection matrix | - |
| `reversed-z` | reversed Z | reverse Z, Reversed-Z |
| `view-frustum` | view frustum | frustum |
| `view-matrix` | view matrix | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-b-3 | should | shape | the Practice of all twelve pages | Each page's Practice is named only by its optional Coin Run item. No row holds the other two to seven exercises (style.md asks three to eight), nor the exercise that runs code in the playground, which track E needs and which an optional item for track B cannot be. basics-a gives each primer a row "Practice before the Coin Run item" and counts the fixed parts at 1,300 to 1,450 words; basics-b counts them at 1,100. R32 D27 asked every unit to add the missing exercises as items. | Each page gets a hands-on row for its Practice, from easy to hard, run in the playground's script and read in the Console, at least one of them run and logged (about 250 words a page, D27's measure). The Fit lines count the fixed parts again. `basics/math-matrices` (6,000), `basics/math-projection` (5,900) and `basics/math-geometry` (5,800) then reach the top of L and go to the second size pass by S5. | `allocation/basics-b.md:28`, `:101-103`, `:175`, `:253`, `:330`, `:417`, `:496`, `:570`, `:652`, `:743`, `:825`, `:925`; Fit lines `:44`, `:118`, `:269`, `:435`; `allocation/basics-a.md:192`, `:211`, `:266`, `:285`; `style.md:584`, `:598-606`; `critique/rulings-7.md:206`; `outline-1.md:242` |
| critic-basics-b-11 | should | order | the Assumes row "The camera entity in the editor", and `new:27`, `new:29`, `new:31` on `basics/math-projection` | The Assumes row names `make/look`, which is on neither of the page's tracks (B, E). The Camera component's fields are homed on `gpu/coordinates`, after the page. So no reader of the page has met the fields that hold its ideas: Perspective FOV, vertical and in degrees (60 by default), Perspective Near 0.1 and Far 1000, and Orthographic Size, the vertical extent. The Coin Run item reads `PerspectiveFOV` by name. | Replace the row with a `use` row of `scene-ecs:58`, and tie ideas (2), (4) and (6) to these fields in one paragraph, with `GetProperty<float>("Camera", "PerspectiveFOV")` as `Playground.cpp:200` reads it (about 100 words). | `allocation/basics-b.md:233-247`, `:285`, `:302`; `tracks.md:132-208`, `:210`; `allocation/gpu.md:405`; `Strata/src/Strata/Scene/Components.h:130-139`; `Samples/PhysicsPlayground/Scripts/Playground.cpp:200` |
| critic-basics-b-13 | could | missing-item | `new:28` and `new:30` on `basics/math-projection` | A script can call `glm::perspective`, and scripts build with `GLM_FORCE_DEPTH_ZERO_TO_ONE`, so it gives depth 0 at the near plane and 1 at the far plane: not Strata's reversed Z. Strata's own projection is that glm function with near and far swapped. Also, `Game::GetWindowSize` returns whole numbers: `size.x / size.y` divides as integers (1 for 1920 by 1080), and the size is 0 while unknown. | Idea (5) shows reversed Z as glm's call with near and far swapped, beside what `glm::perspective` gives in a script (about 60 words). The aspect ratio in the Coin Run item is computed in floats and checked for 0, as `GetPointerRay` does (about 30 words). | `allocation/basics-b.md:242-245`, `:285`; `StrataScriptCore/CMake/StrataScriptCoreConfig.cmake:31`; `Strata/vendor/glm/glm/gtc/quaternion.hpp:18`; `Strata/vendor/glm/glm/gtc/matrix_transform.hpp:29`; `Strata/src/Strata/Math/Math.cpp:71-75`; `StrataScriptCore/Include/StrataScript/Game.h:94-95`; `Samples/PhysicsPlayground/Scripts/Playground.cpp:194-201` |
