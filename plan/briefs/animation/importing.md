# Brief: `animation/importing`

| Field | Value |
| --- | --- |
| Title | Importing animated models |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `animation/clips`, `animation/skinning`, `assets/models-gltf` |
| From | animation ch. 6; 1.4 (skeleton building, clips, entities, attachments, stable handles, import scale) |
| Unit | `plan/allocation/animation.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `animation/importing` — Importing animated models

**Covers.** The job: the animation part of `GltfImporter` turns a glTF file's skins, animated nodes and animations into
one `Skeleton` sub-asset, one clip per animation, the meshes' skin bindings and the model's entities; it is built only
with the animation module (`#if ST_WITH_ANIMATION`; without it the import reports the animations skipped). The problem
(the authoring pipeline): glTF's nodes, skins and samplers do not say which nodes are joints and which are objects, and
a reimport must keep every handle. Building the skeleton (the excerpt): the joints of every skin, the nodes the
animations move and their ancestors, parents first by an iterative walk, duplicate names made unique, the root motion
joint as the topmost joint of any skin, the sub-asset "Skeleton". The clips (the excerpt): one per animation, keyed
"Animation/<name>" or by index when the name is not unique, channels animated twice warned about and skipped, keys
reduced with cancellation checks, morph-target weights skipped and reported. The skins (the excerpt of
`ReadSkinVertices`, with `ReadSkin` before it): a skin needs 1 to 4,096 joints and finite affine inverse bind matrices,
or its meshes import without skinning, with a warning; for each vertex the importer keeps the four strongest of up to
eight influences (JOINTS_0/1, WEIGHTS_0/1), renormalizes them and quantizes them to 16 bits that sum to 65535, and the
strongest takes the rounding error; weights that are negative, not finite or name a joint outside the skin count as
none; a vertex with no weight follows the skin's first joint, with a warning; zero weights point at joint 0, which keeps
the rule of `animation/skinning` that every influence names a joint of the skin. The model's entities (the excerpt): the
root is the animator (`AnimatorComponent` with the skeleton and the first clip); skinned meshes under it carry a
`SkinComponent` naming it; joints with content (a rigid mesh, a camera, a light, a foreign child) become entities with
an `AttachToJointComponent` at the joint's rest pose; plain joints are no entities; entity ids derive from the model's
handle, so a reimport gives the same ids. A table of the three components field by field (each field's behaviour is
taught on its own page). The import scale is baked: the root keeps scale 1; meshes, joints, bind matrices and clips are
scaled. The asset types and their loaders: skeletons and clips from their cooked bytes, controllers from their JSON
source. The importer's version is 11 (`GltfImporter.h:39`), and the page states that number, not the 9 of
`Docs/Architecture.md`; the rule to bump the version whenever the output changes. The toy: a walk that marks joints in a
node tree, in about 40 lines. How it is tested: `GltfSkinImportTests.cpp` (six cases, the import scale at line 384). The
exercise is a trace in the debugger: one vertex's influences before and after quantization. At the end the reader can
predict the sub-assets and the entity tree that a rigged glTF file produces.

**Leaves out.**

- The glTF importer's meshes, materials and textures, and models as entity templates → `assets/models-gltf`
- What the three components do while a scene plays → `animation/state-machines`, `animation/root-motion`, `animation/system`, `animation/culling`
- Importing and placing a rigged model in the editor → `make/animation`
- Sub-assets and derived handles in general → `assets/handles-meta`

**Fit.** `fits`: about 3,880 words against M (3,000). Four excerpts from the importer (the skins' among them, about 250)
and the table of the components' fields take the most; the estimate is 120 words below M's top.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `animation:56-57` | feature | home | The three loaders (cooked skeletons and clips, controllers from JSON) and the three asset types |
| `animation:63-64` | feature | home | One skeleton per model; one clip per animation |
| `animation:66-68` | feature | home | The model's entities; the baked import scale; the importer's version (11) |
| `animation:74` | feature | home | `AnimatorComponent` and its fields (Skeleton, Controller, Clip, Speed, Loop, PlayOnStart, ApplyRootMotion, CullingMode) |
| `animation:77-78` | feature | home | `SkinComponent` (its type in `Scene/Components.h`, registered by the animation module) and `AttachToJointComponent` |
| `animation:325` | concept | home | The authoring pipeline: glTF skins, nodes and samplers; joints against entities; sub-asset keys; handles stable across reimports |
| `animation:361` | code | home | `Strata/src/Strata/Asset/GltfImporter.cpp:1012-1123`: building a skeleton from a glTF node tree |
| `new:2` | code | home | `Strata/src/Strata/Asset/GltfImporter.cpp:1606-1676`: `ImportAnimations`, one clip per animation, skipped channels and weights, reduction with cancellation |
| `new:3` | code | home | `Strata/src/Strata/Asset/GltfImporter.cpp:1921-1963`: skinned meshes get a `SkinComponent`, joints with content an `AttachToJointComponent` at the rest pose; with lines 1988-1995, the root's `AnimatorComponent` |
| `new:18` | code | home | `Strata/src/Strata/Asset/GltfImporter.cpp:1189-1287`: `ReadSkinVertices` keeps the four strongest of up to eight influences, renormalizes and quantizes them to 16 bits that sum to 65535 (the strongest takes the rounding error), counts negative, non-finite and out-of-skin weights as none, sends unweighted vertices to the skin's first joint with a warning, and points zero weights at joint 0; with lines 1144-1187, `ReadSkin` (1 to `MeshSkinBinding::c_MaxJoints` joints, finite affine inverse bind matrices, or no skinning). About 250 words with the paragraph. Evidence: `Strata/src/Strata/Renderer/Mesh.h:46` (`c_MaxJoints = 4096`); `StrataTests/src/Asset/GltfSkinImportTests.cpp:151` (weights sum to 65535), `:343` (broken skins skipped with a warning) |
| `animation:481` | rule | home | Bump the importer's version when its output changes |
| `animation:636` | open | home | The drift between `Docs/Architecture.md` and the importer's version, settled by `new:1` |
| `new:1` | erratum | home | `Docs/Architecture.md:2626` says that `GltfImporter` is version 9; the importer returns 11, and the page states 11. Evidence: `Strata/src/Strata/Asset/GltfImporter.h:39` (`GetVersion() const override { return 11; }`); `Docs/Architecture.md:2626` ("`GltfImporter` (version 9)") |
| `animation:556` | term | home | Animator |
| `animation:65` | feature | use | The skin bindings the importer fills (`GltfImporter.cpp` 1144-1287, the excerpt of `new:18`) |
| `animation:456` | rule | use | Every skin influence names a joint of the skin: the importer points zero weights at joint 0 |
| `animation:49` | feature | use | Keys reduced as each channel is imported |
| `animation:437` | rule | use | Plain joints are no entities |
| `animation:25` | feature | use | The `#if ST_WITH_ANIMATION` guards of the importer |
| `new:19` | hands-on | home | Trace it yourself (done, track E): with a breakpoint in `ReadSkinVertices`, run "Skinned glTF files import a skeleton, clips and a skinned mesh without skipping anything" in the engine's source build, and read one vertex's influences before and after quantization: the four strongest kept, the weights summing to 65535, the strongest holding the rounding. Evidence: `Strata/src/Strata/Asset/GltfImporter.cpp:1189-1287`; `StrataTests/src/Asset/GltfSkinImportTests.cpp:112`, `:151` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Models and the glTF importer: nodes, meshes, the model as an entity template | `assets/models-gltf` | must |
| Asset handles, `.meta` files and sub-assets; derived handles | `assets/handles-meta` | must |
| Importing: import records, background imports, cancellation, importer versions | `assets/importing` | must |
| Clips, channels and keyframe reduction | `animation/clips` | must |
| Skin bindings and inverse bind matrices | `animation/skinning` | must |
| Prefabs: entity templates and instantiation | `world/prefabs` | helps |
| Optional modules (`ST_WITH_*`) | `core/layers-registries` | helps |
| Components and their registered properties | `world/reflection` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `animator` | Animator | - |
