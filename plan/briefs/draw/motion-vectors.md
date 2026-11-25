# Brief: `draw/motion-vectors`

| Field | Value |
| --- | --- |
| Title | Motion vectors and motion history |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `draw/render-scene-gpu`, `draw/skinned` |
| From | render-scene; says in one sentence what motion vectors are for and links forward to `image/taa`, without needing it; the motion view |
| Unit | `plan/allocation/draw.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `draw/motion-vectors` — Motion vectors and motion history

**Covers.** The job: give every drawn pixel the screen motion since the renderer's previous frame, for objects that
move, deform or stay still under a moving camera. One sentence says what motion vectors are for (temporal anti-aliasing
and motion blur) and links forward to `image/taa`, which the page does not need. The problem section teaches the
approaches: camera-only reprojection from depth, previous transforms per object, previous skinning. Strata's choice: a
per-renderer motion history of the instance and palette buffers, and velocity variants of the scene vertex shaders. The
toy computes a pixel's motion from two positions and two view-projection matrices.

The real code. The RG16F velocity target, which the prepass writes: unjittered current minus previous position in UV
units. The `ST_VELOCITY` variants of `Mesh.vert`: the instance as the previous frame drew it, used only when it is the
same entity's, posed by its previous palette (`u_PreviousJoints`) when that is the same range, and the unjittered clip
positions of both frames (the part of the vertex shader that `draw/mirrors-camera-relative` left for here). The rule
that motion uses unjittered matrices built in double: a still camera gives exactly zero motion, and jitter never appears
as motion. Where nothing was drawn, the camera's motion alone (`Include/Motion.slang`). The motion history: each
renderer keeps its own copy of the instance and palette buffers as its last frame drew them, never in the shared GPU
copy, because renderers render at different times. The GPU copy's write logs by process-unique write version, and
`RecordMotionCopy`, which copies only what the GPU copy wrote since, with `MotionCopy.comp`, one thread per listed
element. A frame with motion draws both the prepass and the forward pass with the velocity variant, so their depths
agree. The motion debug view colours each pixel by its motion's direction. How it is tested:
`GPU.SceneRenderer.MotionVectors`, whose cases check that the history holds what the renderer's latest frame drew and
copies only what was written since, a still view without motion, moved, skinned and mirrored instances with their own
motion, slots that change hands, cross-fades, two renderers of one scene, the motion view, and an image left
bit-identical on both paths. The exercise moves one cube by a known step and traces what the history copies. The page
runs on the Third-Person sample with the camera panning while the robot runs. At the end the reader can say where a
pixel's previous position comes from, and why the history belongs to the renderer.

**Leaves out.**

- What temporal anti-aliasing does with motion → `image/taa`
- Motion blur → `image/motion-blur`
- The pipeline key's velocity flag in the pipeline cache → `gpu/binding`
- The depth prepass and the `EQUAL` test → `gpu/frame-tour`
- The palettes being compared → `draw/skinned`

**Fit.** `fits`: about 3,700 words against M (3,000). Three excerpts and the seven features of the velocity target, the
variants and the history take the most; the items the image and animation units passed here are the same features seen
from their side and add little.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-scene:326` | concept | home | Motion vectors: camera reprojection, previous transforms, previous skinning; the "previous in the shared copy" mistake |
| `render-image:368` | concept | home | Motion vectors and reprojection as the image part recalls them: camera motion for the sky, unjittered against jittered |
| `render-scene:173-175` | feature | home | Motion vectors, the motion history, velocity in both passes |
| `render-scene:117` | feature | home | The GPU copy's write logs for readers |
| `render-image:171` | feature | home | The velocity target as the post chain reads it: RG16F, unjittered current minus previous UV |
| `render-image:174` | feature | home | The motion debug view (`ShowMotionVectors`, `Overlay/MotionView.frag.slang`) |
| `animation:155` | feature | home | Skinned motion vectors: the previous palettes (`u_PreviousJoints`, t21) |
| `render-image:555` | rule | home | Motion vectors use unjittered matrices built in double |
| `render-image:512` | figure | home | The motion view while the camera turns: one figure with `render-scene:450` |
| `render-image:702-703` | term | home | Motion vector (velocity target); motion history: one glossary entry each with `render-scene:648-649` |
| `new:10` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:1286-1393`: `RecordMotionCopy`, copying only what the GPU copy wrote since the history's version |
| `new:11` | code | home | `Strata/shaders/Scene/MotionCopy.comp.slang:5-30`: one thread per listed element of the history copy |
| `render-scene:419` | figure | home | The motion history: write versions, per-renderer histories, the copy, the velocity shaders reading both |
| `render-scene:450` | figure | home | The motion debug view while the camera pans and the robot runs |
| `render-scene:497` | rule | home | Never store "previous frame" data in the shared GPU copy |
| `new:21` | hands-on | home | Exercise (done, with a "trace it yourself"): in the pattern of the test "Moved entities, skinned poses and mirrored instances carry their own motion", move one cube by a known step between two frames under a still camera, read the motion back and check its pixels against the step worked out by hand from the two view-projection matrices, and that the still pixels have exactly zero motion; then, with a breakpoint in `RecordMotionCopy`, find which elements the history copies in that frame (the moved cube's instance, listed from the write log); the solution is the test and the path. Evidence: `StrataTests/src/Renderer/GPUSceneMotionTests.cpp:494-528`, `:460`; `Strata/src/Strata/Renderer/SceneRenderer.cpp:1286-1393` |
| `render-scene:648-650` | term | home | Motion vector (velocity target); motion history; write version and write log |
| `render-scene:370` | code | use | The velocity part of `Mesh.vert` (lines 61-81) |
| `render-scene:161` | feature | use | The skinned variants, whose velocity forms blend the previous palette |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Clip space, the view-projection matrix and UVs | `gpu/coordinates` | must |
| The render scene's GPU copy | `draw/render-scene-gpu` | must |
| Palettes and the skinned variants | `draw/skinned` | must |
| The depth prepass and the `EQUAL` test | `gpu/frame-tour` | must |
| Compute dispatches | `gpu/compute` | must |
| Half-float formats | `basics/color` | must |
| The scene vertex shader | `draw/mirrors-camera-relative` | must |
| Temporal anti-aliasing and the jitter | `image/taa` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `motion-history` | Motion history | - |
| `motion-vector` | Motion vector | velocity target, Motion vectors |
| `write-version` | Write version | write log |
