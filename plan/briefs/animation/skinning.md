# Brief: `animation/skinning`

| Field | Value |
| --- | --- |
| Title | Skinning |
| Kind | C |
| Size | L |
| Tracks | E |
| Needs | `animation/skeletons`, `draw/skinned` |
| From | animation ch. 5 (joint palettes, linear blend skinning, normals: how the joint matrices that `draw/skinned` takes as given are made) |
| Unit | `plan/allocation/animation.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `animation/skinning` — Skinning

**Covers.** The problem as the reader meets it: the robot's elbow bends, but its mesh was modelled in another pose
(the bind pose), and the skeleton's pose is in the animator's space (in a clause: the animator is the entity that
carries the Animator component, taught on `animation/importing`). The naive answer, moving each vertex with one
joint (rigid binding), cracks the mesh at every joint. The idea, in one diagram of the spaces with every matrix of
`ComputePalette` labelled: a vertex goes from bind space into a joint's space by the joint's inverse bind matrix, then
out by the joint's posed model transform, then from the animator's space into the proxy's (AnimatorToProxy); the
product is the joint's palette entry. Linear blend skinning: a vertex blends up to four influences; a skin stores, per
skin joint, the skeleton joint, the inverse bind matrix and the joint's bind-pose bounds, plus one `MaxJointExtent`
for the whole skin, and per vertex four 16-bit joint indices and four 16-bit weights that sum to 65535
(`MeshSkinBinding`, `MeshSkinVertex`); a glTF vertex may carry eight influences, and the importer keeps the four
strongest (one sentence, linked to `animation/importing`); a worked example skins one vertex between two joints by
hand. Normals go through the cofactor of the blended 3x3, never the plain matrix. The deformation models, each
introduced by the flaw of the one before, with a table of their costs: rigid binding, linear blend skinning and its
candy-wrapper collapse, dual-quaternion skinning (no collapse when a joint twists, at a higher cost); the writer gives
the sources for who uses which. Where skinning runs (on the CPU, in the vertex shader, in a compute pre-pass) is
`draw/skinned`'s, linked in one sentence. Strata's choice: linear blend skinning per draw in the vertex shader, with
palettes computed on the CPU for each posed proxy (the palette excerpt, then the shader's `BlendJoints`,
`SkinPosition`, `SkinDirection` and `SkinNormal`, and a link to the scene vertex shader that calls them, quoted on
`gpu/geometry-pool`); the inputs of a palette in `EvaluatePose`: the animator's pose from `ISkinningPoses` and the
animator's drawn transform, so that an interpolated character is skinned where it is drawn; every influence must name a
joint of the skin even with zero weight, because the shader reads all four entries. What the choice cannot do: the
candy-wrapper collapse of a twisting joint; no dual quaternions and no compute skinning (`animation/limits`); physics'
mesh colliders keep the bind pose while the entity-ID buffer (picking, outlines) shows the pose, as the feature test's
arm shows in the entity-ID view. Common mistakes: forgetting the inverse bind matrix (the mesh explodes), transforming
normals by the plain matrix, culling with bind-pose bounds (`draw/skinned`). Exercise E10: a CPU skinning reference for
one vertex compared with `ComputePalette`, as `GPUAnimationTests.cpp` 117 does. At the end the reader can compute a
skinned vertex by hand and name every matrix of a palette entry.

**Leaves out.**

- Skin proxies, the `ST_SKINNED` variants, bucketing, posed bounds and when palettes are recomputed → `draw/skinned`
- Where skinning runs: on the CPU, in the vertex shader or in a compute pre-pass → `draw/skinned`
- Previous palettes for motion vectors → `draw/motion-vectors`
- Where a skinned mesh's influences and bind matrices come from in a glTF file → `animation/importing`
- The reach that grows posed bounds for animators that skip poses → `animation/culling`

**Fit.** `fits`: about 4,170 words against L (5,000). The idea with its diagram of the spaces, the worked vertex and the
two excerpts take the most; where skinning runs is linked to `draw/skinned`, not taught.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `animation:274` | concept | home | Skinning as a deformation model: rigid binding, linear blend skinning, the candy-wrapper artifact, dual quaternions; bind pose, inverse bind matrices, the palette, four weighted influences, normals by cofactor; one vertex skinned by hand; the mistakes. Where skinning runs (CPU, vertex shader, compute pre-pass) is linked to `draw/skinned` |
| `animation:65` | feature | home | `MeshSkinBinding` and the skin stream `MeshSkinVertex` (`Renderer/Mesh.h` 28-56); how the importer fills them is `animation/importing`'s, named in one sentence (the four strongest of up to eight influences) |
| `animation:134` | feature | home | Interpolated characters: skins posed against the animator's drawn transform; the attachment half (on its joint on frames without a step) is shown on `animation/system` |
| `animation:150-151` | feature | home | `EvaluatePose`'s inputs and the palette per skin joint (3x4 rows); the posed bounds it also computes are `draw/skinned`'s, the reach margin `animation/culling`'s |
| `animation:154` | feature | home | Linear blend skinning in the shaders: `BlendJoints` (four influences), `SkinPosition`, `SkinDirection`, `SkinNormal` (cofactor); the variants that hold them are `draw/skinned`'s |
| `animation:158` | feature | home | Mesh colliders use the bind pose; the entity-ID buffer shows the pose |
| `animation:358` | code | home | `Strata/src/Strata/Renderer/RenderScene.cpp:1322-1339`: the palette entry `AnimatorToProxy * pose[joint] * inverseBind` (the bounds lines are read as a reminder of `draw/skinned`) |
| `animation:359` | code | home | `Strata/shaders/Include/Scene.slang:168-235`: linear blend skinning on the GPU, normals by cofactor |
| `animation:381` | figure | home | Diagram 3, the spaces of skinning |
| `animation:424` | figure | home | Screenshot 9: the feature test's arm in the entity-ID view, showing the pose (`GPUFeatureTests.cpp` 212) |
| `animation:456` | rule | home | Every skin influence names a joint of the skin, even with zero weight |
| `animation:463` | rule | home | Skins are posed against the animator's drawn transform |
| `animation:507` | hands-on | home | E10 |
| `animation:531-532` | term | home | Bind pose, inverse bind matrix |
| `animation:548-553` | term | home | Skinning, linear blend skinning, dual quaternion skinning, influence and weight, palette, skin and skin binding |
| `render-scene:637-639` | term | home | Inverse bind matrix, palette, linear blend skinning, passed by `draw`: one glossary entry each with `animation:532`, `animation:552` and `animation:549` |
| `render-scene:158` | feature | home | Palettes, passed by `draw`: the same feature as `animation:151`, taught with it |
| `render-scene:491` | rule | home | Every skin influence names a joint of the skin, passed by `draw`: the same rule as `animation:456`, taught with it |
| `render-scene:157` | feature | use | Skin proxies, as `draw/skinned` teaches them |
| `render-scene:159` | feature | use | Posed bounds, as `draw/skinned` teaches them |
| `render-core:463` | code | link | The scene vertex shader that calls `BlendJoints`, `SkinPosition` and `SkinNormal` under `ST_SKINNED` (`Mesh.vert.slang` 40-44), quoted on `gpu/geometry-pool` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Skinned meshes in the renderer: skin proxies, the `ST_SKINNED` variants, posed bounds | `draw/skinned` | must |
| Skeletons, the rest pose, model-space joint transforms | `animation/skeletons` | must |
| Matrices, spaces, inverses and affine transforms | `basics/math-matrices` | must |
| The cross product | `basics/math-vectors` | must |
| The cofactor matrix (normals through the inverse transpose) | `basics/math-bases` | must |
| Vertex shaders and the pipeline | `gpu/how-a-gpu-frame-works` | must |
| Slang shaders and their registers | `gpu/shaders` | must |
| Drawn transforms between fixed steps | `world/interpolation` | must |
| Mesh colliders | `physics/building-bodies` | helps |
| Picking through the entity-ID buffer | `editor-ui/scene-view` | helps |
| Motion vectors | `draw/motion-vectors` | helps |
| The animator: the entity that carries the Animator component | `animation/importing` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `bind-pose` | Bind pose | - |
| `dual-quaternion-skinning` | Dual quaternion skinning | - |
| `influence` | Influence | - |
| `inverse-bind-matrix` | Inverse bind matrix | - |
| `linear-blend-skinning` | Linear blend skinning | LBS |
| `skin-gltf` | Skin (glTF) | skin binding |
| `skinning` | Skinning | - |
| `skinning-palette` | skinning palette | - |
