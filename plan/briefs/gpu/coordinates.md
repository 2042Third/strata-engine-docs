# Brief: `gpu/coordinates`

| Field | Value |
| --- | --- |
| Title | Coordinate systems and the camera: clip space, reversed depth, UVs |
| Kind | C |
| Size | M |
| Tracks | E |
| Needs | `basics/math-projection`, `basics/numbers`, `core/math`, `world/scene-graph`, `gpu/how-a-gpu-frame-works` |
| From | render-core; retitled; + `CameraComponent` (scene-ecs §1.2: projection, `GetProjection`); home of the camera and of Strata's depth conventions and precision (the math is `basics/math-projection`'s, the code `core/math`'s, the depth-of-field fields `image/depth-of-field`'s); states the counter-clockwise convention only (mirroring and camera-relative space are `draw/mirrors-camera-relative`'s) |
| Unit | `plan/allocation/gpu.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `gpu/coordinates` — Coordinate systems and the camera: clip space, reversed depth, UVs

**Covers.** The problem as a reader meets it: a cube placed in the editor lands on some pixels at some depth; which
ones, and what happens when a textbook's OpenGL formulas are used (an image upside down, far surfaces that fight). The
idea is the chain of spaces in one figure: object, world (right-handed, +Y up, −Z forward), camera, clip, NDC,
framebuffer and UVs, and the way back from a pixel and its depth to a position through the inverse projection.
Strata's conventions follow, each with its reason (the words clip space, NDC and reversed Z are taught on
`basics/math-projection` and linked): Direct3D-style NDC through NVRHI's viewport flip
(+Y up, row 0 at the top, depth from 0 to 1), and why slangc is not asked to flip; fullscreen UVs and the fullscreen
triangle made from the vertex index; depth and reversed Z, with the precision argument shown as a plot computed from the
projection formulas, depth cleared to 0, tests with `GreaterOrEqual`, the sky at depth 0 and the infinite far plane;
front faces counter-clockwise as glTF has them, with mirrored instances named and linked forward.

The camera closes the concept: `CameraComponent`'s projection, field of view, near and far planes, orthographic size,
Primary and clear color, and `GetProjection`, which builds the reversed-Z matrices and guards bad values; then
`SceneCamera`, what every renderer is given (view, projection in Strata's clip space, position, near, far, the field of
view used for levels of detail, orthographic, clear color, `FromEntity`), kept apart from the lens because it is the
shadow cascades' cache key, and why a clear color shows changed: it is linearized into the HDR image, so exposure and
tone mapping apply to it. The approaches
table compares standard depth, reversed Z with float depth, the infinite far plane and logarithmic depth. What Strata's
choice cannot do here, and two exercises: derive the fullscreen triangle by hand, and measure the float depth step from
0.1 m to 10 km for both mappings.

**Leaves out.**

- The mathematics of projection and homogeneous coordinates → `basics/math-projection`
- The code of `PerspectiveReverseZ*` and `Ray::FromNDC` → `core/math`
- Mirrored transforms, clockwise pipelines and flipped tangents → `draw/mirrors-camera-relative`
- Camera-relative rendering and float precision far from the origin → `draw/mirrors-camera-relative`
- The lookup of the primary camera → `world/scene-graph`
- The camera's depth-of-field fields → `image/depth-of-field`
- The projection's jitter for TAA → `image/taa`
- The editor camera and its viewport → `editor/camera-viewport`

**Fit.** `over`: about 4,750 words against M (3,000). Six conventions with the precision plot, the camera with
`SceneCamera` and the two exercises pass M's top; the page takes L by S2 (4,750 is inside L's range), and the fullscreen
triangle stays here.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-core:378` | concept | home | Coordinate systems and clip space; Vulkan's +Y down against Direct3D's +Y up; the mistake of GLSL's UV formula |
| `render-core:382` | concept | home | Depth buffers and reversed Z; the approaches; the mistake of clearing to 1 or testing `Less` |
| `render-core:137`, `render-core:138`, `render-core:139` | feature | home | Direct3D-style clip space through NVRHI; reversed Z in Strata; fullscreen UVs |
| `render-core:140` | feature | home | Front faces counter-clockwise (glTF); `setFrontCounterClockwise(!Mirrored)` named, mirroring linked |
| `render-core:141` | feature | home | Right-handed, +Y up, −Z forward |
| `foundation:139` | feature | home | The same conventions as the math code states them (`Math/Math.h`), with Direct3D-style clip space and reversed Z |
| `render-core:464` | code | home | `Strata/shaders/PostProcess/Fullscreen.vert.slang:8-13`: one triangle from the vertex index; the exercise derives its three vertices |
| `new:8` | code | home | `Strata/src/Strata/Scene/Components.cpp:7-24`: `CameraComponent::GetProjection`: the aspect ratio, near and far guarded, `PerspectiveReverseZ` and `OrthographicReverseZ` |
| `render-core:505` | figure | home | The chain of spaces, from object to framebuffer and UVs |
| `foundation:426` | figure | home | The conventions' figure (axes, NDC, depth, the framebuffer's origin), drawn as the start and end of the chain above |
| `render-core:507` | figure | home | The reversed-Z precision plot, computed from the projection formulas |
| `render-core:597` | rule | home | Reversed Z: clear depth to 0, test `GreaterOrEqual`, the sky at depth 0 |
| `render-core:602` | rule | home | Fullscreen UVs `(ndc.x * 0.5 + 0.5, 0.5 - ndc.y * 0.5)` |
| `render-core:636`, `render-core:638` | hands-on | home | Derive the fullscreen triangle; the reversed-Z precision experiment (CPU only) |
| `render-core:729`, `render-core:731`, `render-core:732` | term | home | Viewport flip; infinite far plane; depth test functions |
| `foundation:635` | term | home | Infinite far plane, as the core part words it; one entry with `render-core:731` (R31 D33) |
| `render-core:728`, `render-core:730` | term | link | Clip space and NDC; reversed Z: homed on `basics/math-projection` (the mathematics); this page keeps Strata's convention and the precision argument |
| `render-image:724` | term | home | Fullscreen triangle: one oversize triangle that covers the viewport, made from the vertex index (`render-core:464`); "post source" (`render-image:723`) stays with `image/why-post` |
| `render-core:736` | term | home | Winding order, front face and back-face culling |
| `render-scene:644` | term | home | Winding and front face, as the drawing part words it |
| `editor-core:695` | term | home | Primary camera |
| `render-indirect:609` | term | home | Depth buffer, as the indirect part words it; reversed Z in it linked to `basics/math-projection` |
| `editor-core:733`, `render-direct:716`, `render-scene:608` | term | link | Reversed Z, as other parts' glossaries word it; one entry with `render-core:730` on `basics/math-projection` |
| `scene-ecs:58` | feature | home | `CameraComponent`: projection, field of view, near and far, orthographic size, Primary, clear color and `GetProjection`; its inactive reasons named; the depth-of-field fields and the primary-camera lookup linked |
| `new:33` | feature | home | `SceneCamera`, what every renderer is given (`Render(scene, camera, ...)`): view, projection in Strata's clip space, position, near, far, a vertical field of view for levels of detail, orthographic, clear color, and `FromEntity`; it stays apart from `CameraLens` because its whole value is the shadow cascades' cache key. The clear color rule: it is linearized into the HDR image, pre-exposed, so exposure and tone mapping change it (about 150 words). Evidence: `Strata/src/Strata/Renderer/SceneRenderer.h:62-81, 83-84, 851`; `Strata/src/Strata/Renderer/SceneRenderer.cpp:187-211, 3423-3425` |
| `scene-ecs:474` | figure | use | The Inspector of a Camera, beside the fields it shows |
| `foundation:424` | figure | home | The same precision plot, drawn once with `render-core:507` |
| `foundation:632` | term | home | Right-handed coordinates, +Y up, −Z forward |
| `foundation:370` | code | link | The reversed-Z projections in `Math.cpp`, quoted by `core/math` |
| `render-core:387` | concept | link | Winding and mirrored transforms, linked forward |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Projection: view and projection matrices, homogeneous coordinates, frustums, depth and reversed Z (the mathematics) | `basics/math-projection` | must |
| Matrices, transforms and spaces; axes and handedness | `basics/math-matrices` | must |
| Floating point and its precision | `basics/numbers` | must |
| Strata's math code: `PerspectiveReverseZ*` | `core/math` | must |
| The pipeline at a glance: rasterization, the depth test, the framebuffer | `gpu/how-a-gpu-frame-works` | must |
| Components and the transform | `world/scene-graph` | helps |
| A vertex shader and its system values (`SV_VulkanVertexID`) | `gpu/shaders` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `depth-test-functions` | Depth test functions | - |
| `fullscreen-triangle` | Fullscreen triangle | - |
| `infinite-far-plane` | Infinite far plane | - |
| `primary-camera` | Primary camera | - |
| `viewport-flip` | Viewport flip | - |
| `winding` | Winding | - |
| `winding-order` | Winding order | front face, back-face culling |
