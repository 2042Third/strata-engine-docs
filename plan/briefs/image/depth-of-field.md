# Brief: `image/depth-of-field`

| Field | Value |
| --- | --- |
| Title | Depth of field |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `image/taa`, `gpu/coordinates` |
| From | render-image ch. 10 (second half); 1.7 (the five shaders, thin-lens CoC, `CameraLens::FromEntity`, the camera's fields), concept 17, diagram 20; split from `image/motion-blur-dof` |
| Unit | `plan/allocation/image.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `image/depth-of-field` — Depth of field

**Covers.** The job: blur what is out of focus as a real lens does, and stay stable under the TAA's jitter. The page
starts from `render-image:514`: the Third-Person robot at f/2 against depth of field off, then f/1.4 against f/8, then
the focus held on an entity. The full section "The problem and how engines solve it": the thin lens and the circle of
confusion with its formula (diagram `render-image:473`), near and far fields, scatter as gather, a premultiplied near
field, tile dilation, and the two classic faults, a halo of sharp foreground over the background and flicker at
in-focus silhouettes. The camera's fields (`CameraComponent::DepthOfField`, `FocusDistance`, `FocusEntity`, `Aperture`,
`SensorHeight`) and `CameraLens::FromEntity`, which turns the field of view and the sensor into a focal length (code
#29). The toy is a gather over a disk of each pixel's own circle in about 40 lines.

The five passes in the order data flows: Prepare (half resolution, the signed circle of confusion from
`Include/DepthOfField.slang` in alpha), Tiles and Dilate (the near field's maxima), Gather (`new:9`: 48 Vogel samples on
a disk turned per pixel; the pixel's own field and the near field, each with its cover weights), and Composite
(`new:10`: the sharp image kept exactly within a pixel of focus, a fade from in-focus depth that keeps it stable under
the jitter, the near field over everything, alpha 1 where it changed, which stops the sharpening). Depth of field runs
only for perspective views and when the players' row allows it, and it shows in every view and capture through a scene
camera, playing or not (`new:32`, taught with motion blur's views). No circle of confusion is wider than 2% of the image
height (`c_DepthOfFieldMaxDiameter`), the page's limit. How it is tested: `Renderer.CameraLens`, and
`GPU.SceneRenderer.DepthOfField`, whose cases prove the focus plane bit-identical to depth of field off and an in-focus
silhouette under TAA no more flickering than without the lens. The exercises are a racing camera with both motion blur
and depth of field, and the programs that set a lens traced (`new:25`). At the end the reader can compute a circle of
confusion by hand, set a lens for a shot, and explain why the composite fades from in-focus depth.

**Leaves out.**

- The camera component as a whole, its projection and Primary → `gpu/coordinates`
- How the scene finds its primary camera → `world/scene-graph`
- Motion blur, the other effect that writes the blur mask → `image/motion-blur`
- The players' row that turns it off → `image/quality-settings`
- Depth of field in a game's look → `make/look`

**Fit.** `fits`: about 4,300 words against L (5,000). The thin lens and its circle of confusion, taught from zero, and
the five passes in a short section each take the most words, with three excerpts, one diagram, one figure with its
sweep and two exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-image:381` | concept | home | Depth of field: the thin lens, the circle of confusion, near and far fields, scatter as gather on a Vogel disk, a premultiplied near field, tile dilation, the interaction with TAA's jitter; the errors (haloing, flicker at in-focus silhouettes) |
| `render-image:182` | feature | home | The five shaders and `Include/DepthOfField.slang`; `CameraLens` (`SceneRenderer.h:85-102`), `FromEntity` and the circle's math; `RenderDepthOfField` (`SceneRendererPost.cpp:815-860`); the camera's fields (`Strata/src/Strata/Scene/Components.h:142-150`); the limit: no circle of confusion wider than 2% of the image height (`c_DepthOfFieldMaxDiameter`, `Strata/src/Strata/Renderer/PostProcessData.h:111-113`; `Docs/Manual/Camera.md:145`); tested by `Renderer.CameraLens` and `GPU.SceneRenderer.DepthOfField`, whose cases prove the focus plane bit-identical to depth of field off and no more flicker under TAA than without the lens (`StrataTests/src/Renderer/GPUSceneDepthOfFieldTests.cpp:179, 181, 268`) |
| `render-image:423` | code | home | `Strata/src/Strata/Renderer/SceneRendererPost.cpp:254-299`: the thin lens's focal length from the field of view and the sensor; the circle of confusion |
| `new:9` | code | home | `Strata/shaders/PostProcess/DepthOfFieldGather.comp.slang:26-110`: Vogel samples turned per pixel; the pixel's own field and the near field, each with cover weights; the near field's coverage |
| `new:10` | code | home | `Strata/shaders/PostProcess/DepthOfFieldComposite.comp.slang:5-82`: the composite at full resolution: sharp within a pixel of focus, the fade from in-focus depth through group-shared memory that keeps the image stable under the jitter, the premultiplied near field over everything, alpha 1 where it changed |
| `render-image:473` | figure | home | Diagram: the thin lens, the circle of confusion against distance, near and far fields, the composite's fade near in-focus depth |
| `render-image:514` | figure | home | Depth of field off and on at f/2 on `tp.dof`, the sweep f/1.4 against f/8, focus on an entity |
| `render-image:601` | hands-on | home | Exercise: a racing camera with a 180 against a 90 degree shutter, focus on the car at f/2.8, and the players' rows |
| `new:25` | hands-on | home | Exercise (trace it yourself): with a search for `Lens =`, find every program that gives the renderer a lens (the runtime's `GameRenderer`, the editor's viewport renderer) and the conditions under which `RenderFrame` runs the depth of field; the reader says why a Scene view through the editor camera is never defocused. Evidence: `Strata/src/Strata/Runtime/GameRenderer.cpp:125`; `StrataEditor/src/Editor/ViewportRenderer.cpp:34, 227`; `Strata/src/Strata/Renderer/SceneRenderer.cpp:3588` |
| `render-image:718-720` | term | home | Circle of confusion; thin lens, f-number, focal length and sensor height; near field and far field |
| `render-image:722` | term | home | Scatter-as-gather |
| `scene-ecs:58` | feature | use | `CameraComponent`: this page teaches its depth-of-field fields, and `gpu/coordinates` the rest |
| `render-image:721` | term | use | The Vogel disk; its home is `basics/math-probability` |
| `render-image:189` | feature | use | The blur mask that the composite writes; its home is `image/motion-blur` |
| `render-image:238` | feature | use | The players' `DepthOfField` row, read in `RenderFrame` (`SceneRenderer.cpp:3588`) |
| `new:32` | feature | use | Which views show depth of field: every view and capture through a scene camera, playing or not; the editor camera never does |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The camera: `CameraComponent`, projection, field of view | `gpu/coordinates` | must |
| Temporal anti-aliasing: jitter and history | `image/taa` | must |
| Noise and sampling patterns: the Vogel disk | `basics/math-probability` | must |
| Compute shaders: shared memory, group barriers | `gpu/compute` | must |
| Projection: inverse projection and depth | `basics/math-projection` | must |
| Transparency, blending and premultiplied alpha | `light/clearcoat-transmission` | helps |
| The blur mask | `image/motion-blur` | helps |
| Handles instead of pointers; UUIDs as stable identities | `world/ecs` | helps |
| Players' graphics options and their rows | `image/quality-settings` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `circle-of-confusion` | Circle of confusion | CoC |
| `far-field` | far field | - |
| `near-field` | Near field | - |
| `scatter-as-gather` | Scatter-as-gather | - |
| `thin-lens` | Thin lens | f-number, focal length, sensor height |
