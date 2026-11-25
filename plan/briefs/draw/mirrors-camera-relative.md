# Brief: `draw/mirrors-camera-relative`

| Field | Value |
| --- | --- |
| Title | Mirrors, normals and camera-relative positions |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `draw/batching`, `basics/numbers`, `gpu/coordinates` |
| From | render-scene; home of mirrored transforms and of camera-relative rendering (float precision is `basics/numbers`', the 20 km limit `worlds/why-streaming`'s) |
| Unit | `plan/allocation/draw.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `draw/mirrors-camera-relative` — Mirrors, normals and camera-relative positions

**Covers.** Two problems that every scene shader meets, and the scene vertex shader that solves both. First, handedness
and mirrored transforms: a negative scale (an odd number of them) makes the determinant negative, reverses the winding
of every triangle on screen and the handedness of the tangent frame; back-face culling then shows the mesh inside out.
The answer is to detect the sign, flip the front face and the bitangent's sign. Strata marks the proxy `Mirrored` when
it is placed, gives mirrored instances their own sort-key bit and GPU bucket bit, draws them with clockwise-front
pipelines (`GetScenePipeline`) and flips the tangent's handedness in `Mesh.vert`, which reads the instance from the
render scene's GPU copy (one sentence: a new proxy draws once its upload arrived; `draw/render-scene-gpu` teaches the
copy). The page explains a tangent frame in one paragraph (normal maps are `light/materials`'). Normals come from the
instance's rows through the cofactor matrix, with no inverse on the CPU: the page recalls in two sentences why the
cofactor works under non-uniform scale, links `basics/math-bases`, which derives it and homes the term, and shows how
the shader builds it from the rows.

Second, floating-point precision far from the origin: a float32 position 100 km out has steps of millimetres, so
vertices jitter. The approaches: origin rebasing (which Strata does not use), double precision on the CPU,
camera-relative rendering, large world coordinates. Strata renders camera-relative in every scene shader: view matrices
are rotation only, the vertex shader subtracts the camera's position from the instance's translation before anything is
added, positions the CPU uploads are subtracted in double, and GPU culling tests camera-relative boxes; the scene's
transforms stay float32, so an entity's origin still moves in steps of about 7.8 mm at 100 km. The two answers meet in
two shader functions, read whole: `TransformPositionRelative`, and `TransformNormal`, whose cofactor normal is negated
for a mirrored instance. The walk ends in the scene vertex shader, `Mesh.vert`, where the two functions are called: the
page quotes only the lines of the relative position, the normal and the mirrored handedness, and of the previous
relative position, and links `gpu/geometry-pool`, which reads the shader from the draw list to the clip position; the
skinning and velocity parts are named for `draw/skinned` and `draw/motion-vectors`. The page runs on an asymmetric
Showcase prop beside its mirror image, and on the scene of `GPU.SceneRenderer.CameraRelative` at the origin and 100 km
out (the "without" picture is a diagram, since no switch turns camera-relative rendering off). The exercise is a
camera-relative audit: draw a debug line 100 km out and check that the renderer uploads it relative to the camera,
subtracted in double, then reproduce `GPU.SceneRenderer.CameraRelative` with the reader's own mesh. At the end the
reader can say what a mirrored instance changes in the pipeline and the shader, and why a new pass must never upload a
world position.

**Leaves out.**

- Floating-point numbers and their spacing → `basics/numbers`
- The 20 km limit of worlds → `worlds/why-streaming`
- The counter-clockwise convention and clip space → `gpu/coordinates`
- Normal maps and tangent space → `light/materials`
- Flipped tangents in the material record → `light/material-data`
- The scene vertex shader read from the draw list to the clip position → `gpu/geometry-pool`
- The skinning and velocity parts of the vertex shader → `draw/skinned`, `draw/motion-vectors`
- Mirroring a prop with a negative scale, for game makers → `make/transforms-units`

**Fit.** `fits`: about 3,650 words against M (3,000). Two concepts and Strata's two answers take the most, then two
excerpts and the quoted lines of the vertex shader; the cofactor's derivation is `basics/math-bases`', recalled here in
two sentences.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-scene:317` | concept | home | Handedness and mirrored transforms; the inside-out mistake |
| `render-scene:321` | concept | home | Precision far from the origin: rebasing, doubles, camera-relative rendering, large world coordinates |
| `render-scene:170-172` | feature | home | Mirrored instances; the normal matrix from the rows; camera-relative space |
| `render-scene:358` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:2464-2469`: the mirrored winding and double-sided culling in pipeline state |
| `render-scene:370` | code | home | `Strata/shaders/Scene/Mesh.vert.slang:50-56`, with lines 76-81: the relative position, `TransformNormal`, the mirrored handedness and the previous relative position; the rest of the shader is linked (lines 35-60 are quoted on `gpu/geometry-pool`, the merge "Scene vertex shader excerpt") |
| `render-scene:442` | figure | home | A mirrored asymmetric prop beside the original, with correct faces and normal map |
| `render-scene:451` | figure | home | The same scene at the origin and 100 km out; the "without" case drawn as a diagram |
| `render-scene:499` | rule | home | Mirrored instances need clockwise pipelines and flipped tangents |
| `render-scene:501` | rule | home | Positions uploaded to scene shaders are camera-relative, subtracted in double |
| `render-scene:643` | term | home | Mirrored transform |
| `render-scene:645`, `render-scene:647` | term | home | Tangent handedness; camera-relative space |
| `render-core:387` | concept | home | Winding, culling and mirrored transforms: the render-core inventory's form of `render-scene:317` |
| `render-core:391` | concept | home | Precision far from the origin and camera-relative rendering: the render-core inventory's form of `render-scene:321`; scene transforms stay float32, 7.8 mm steps at 100 km |
| `render-core:142` | feature | home | Camera-relative space as the render-core inventory lists it: rotation-only view matrices (`GetRelativeView`), CPU uploads computed in double, `InstanceData` kept in world space, tested at 20 and 100 km |
| `render-direct:68` | feature | home | Mirrored instances as the light inventory lists them: the same feature as `render-scene:170` |
| `render-core:462` | code | home | `Strata/shaders/Include/Scene.slang:238-261`: `TransformPositionRelative`, which subtracts the camera from the instance's translation first, and `TransformNormal`, the cofactor normal negated for mirrored instances |
| `render-core:533` | figure | home | The scene at the origin and 100 km out: one figure with `render-scene:451` |
| `render-core:538` | figure | home | The mirrored asymmetric mesh beside the original: one figure with `render-scene:442` |
| `render-core:598` | rule | home | Front faces are counter-clockwise; mirrored instances use clockwise pipelines and flipped tangents; normals go through `TransformNormal`: the render-core form of `render-scene:499` |
| `render-core:600` | rule | home | Never upload a world position to a scene shader: the render-core form of `render-scene:501` |
| `render-core:648` | hands-on | home | The camera-relative audit: a debug line 100 km out, uploaded relative to the camera and subtracted in double (`Strata/src/Strata/Renderer/SceneRenderer.cpp:4105-4110`), then `GPU.SceneRenderer.CameraRelative` with the reader's own mesh |
| `render-core:738-739`, `render-core:741` | term | home | Mirrored transform; tangent handedness; camera-relative rendering: one glossary entry each with `render-scene:643`, `render-scene:645` and `render-scene:647` |
| `render-core:742` | term | home | Origin rebasing, named among the approaches as one Strata does not use |
| `worlds-runtime:546` | term | home | Origin rebasing as the worlds inventory defines it (shifting the world so the player stays near the origin; not in Strata): one glossary entry with `render-core:742`, passed by `worlds` (the merge "Origin rebasing"); `worlds/why-streaming` keeps its not-done line and links |
| `render-core:839` | open | home | No switch turns camera-relative rendering off, so the "without" half of the 100 km figure is a diagram |
| `render-scene:373` | code | use | `Strata/shaders/Include/Scene.slang:238-261`: `TransformPositionRelative` and `TransformNormal` (the item's home is `draw/gpu-driven`) |
| `render-scene:345` | code | use | Where placement sets the `Mirrored` flag |
| `render-scene:646` | term | use | The cofactor matrix, used for the normal in `TransformNormal` and `Mesh.vert`; the term is taught from zero on `basics/math-bases` (R43, R46) |
| `render-core:740` | term | use | Normal matrix (the render-core inventory's "normal matrix / cofactor matrix"), used where `TransformNormal` carries normals from the instance's rows; its glossary home is `basics/math-bases` (R43, R46) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Floating point and the spacing of floats; double precision | `basics/numbers` | must |
| The determinant and its sign; normals through the cofactor matrix | `basics/math-bases` | must |
| Transforms and their rows | `basics/math-matrices` | must |
| The counter-clockwise convention, clip space and the camera's matrices | `gpu/coordinates` | must |
| Batches, sort keys and the draw list | `draw/batching` | must |
| Vertex shaders and their inputs | `gpu/shaders` | must |
| Cross products | `basics/math-vectors` | must |
| Normal maps and tangent space | `light/materials` | helps |
| Why worlds stay within 20 km | `worlds/why-streaming` | helps |
| The instances live in the render scene's GPU copy; a new proxy draws once its upload arrived | `draw/render-scene-gpu` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `camera-relative-rendering` | Camera-relative rendering | Camera-relative transform, Camera-relative space |
| `mirrored-transform` | Mirrored transform | - |
| `origin-rebasing` | Origin rebasing | - |
| `tangent-handedness` | Tangent handedness | - |
