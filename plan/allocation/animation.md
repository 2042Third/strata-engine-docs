# Allocation: animation

## `animation/problem` — The animation problem

**Covers.** The page opens on the Third-Person sample's robot running across the Sky Islands course and asks what has
to change from one frame to the next: thousands of vertices bend at the knees and elbows while the entity itself moves
little. The naive answer, storing every vertex of every frame, is priced in bytes for one short clip. Then the four
approaches in the order of their flaws: vertex animation (baked positions, used for crowds and cloth bakes), morph
targets (blend shapes, used for faces), rigid hierarchies (robot parts on nodes) and skeletal animation (a few dozen
joints drive every vertex), with one table of memory, quality, authoring work and who uses them. Strata's choice:
skeletal animation, plus rigid parts placed on joints; morph targets are not imported (the importer reports them
skipped, `GltfImporter.cpp` 1379 and 1639). The part's running example is introduced: `RobotExpressive.glb`, its
controller `Robot.stanimator` (parameters Speed, Grounded, Jump, Wave and Dance; six states; Footstep events), the
scripts that drive it, the menu robot with its flag, and the other animated content of the samples (the Open World
sample's foxes, the only animated content outside the Third-Person sample). The end-to-end data-flow diagram is the
map of the part: the glTF file, the importer and its sub-assets, the controller, the Animation system, the pose
service, the render scene's palettes and the vertex shader, with root motion and events as side branches; each box
names the page that explains it. The common mistake: thinking that animation means moving the entity. The exercise
prices the naive answer for the robot with a short program on the workbench. At the end the reader can name the four
kinds of animation, say which one Strata uses and why, and follow a pose from the file to the screen on the map.

**Leaves out.**

- Joints, parents and forward kinematics → `animation/skeletons`
- How the vertices follow the joints → `animation/skinning`
- Every absence in one place, with how other engines provide it → `animation/limits`
- Animating a character in the editor, step by step → `make/animation`

**Fit.** `fits`: about 2,225 words against S (1,500). The four approaches with their table and the running example take
the most, and the exercise about 250; the estimate is 25 words below S's top, so no section of the page can grow.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `animation:245` | concept | home | What animation must do in a game: the four approaches, Strata's choice (skeletal plus rigid parts, no morph targets), the "animation is moving the entity" mistake |
| `animation:212` | feature | home | The robot as the part's running example: the model and its licence, the controller's parameters, states and events, `ThirdPersonPlayer.cpp`, `Footsteps.cpp`, `MenuRobot.cpp`, the flag in `MainMenu.stscene`, the faces not imported |
| `animation:219` | feature | home | The other animated content: the Open World sample's foxes with their controller (`Fox.stanimator`), the only animated content outside the Third-Person sample (`git grep -l '"Animator":{' 822a7a46 -- Samples` finds files of those two samples only) |
| `animation:374` | figure | home | Diagram 1, the data flow end to end, as the part's map |
| `animation:589` | term | home | Morph target (blend shape), defined with the approaches |
| `new:14` | erratum | home | `plan/inventory/animation.md:219` names a "Showcase Fox (0.5.0 notes 38)" among the animated content of the samples; the page names only the Open World sample's foxes (process.md's table of errata, kind `inventory`). Evidence: `grep -rIil fox Samples/Showcase` and `grep -rIl '"Animator"' Samples/Showcase` find nothing; `Docs/Releases/0.5.0.md:38` names the Fox among the Open World sample's assets; `Samples/OpenWorld/Assets/Prefabs/Fox.stprefab:2` |
| `new:15` | hands-on | home | Exercise (done, track E): a short program on the workbench prices the naive answer for the robot, every vertex of every frame against its joints' keys, from the joint count, key counts and durations that `animation.info` reports for `RobotExpressive.glb` and the vertex count that the exercise gives (no command reports one); the answer shows the program and its output. Evidence: `StrataEditor/src/Editor/EditorAnimationCommands.cpp:91-105` (a clip's duration, channels and `keyCount`) and `:218-284` (`animation.info` on a model); `Samples/ThirdPerson/Assets/Models/Robot/RobotExpressive.glb`; `git grep -n -i "vertexcount" 822a7a46 -- StrataEditor/src` finds nothing |
| `animation:223` | feature | link | What Strata's animation does not do, in one sentence |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Transforms and hierarchies: local and world transforms, parent and child | `world/scene-graph` | must |
| Entities and components | `world/ecs` | must |
| The frame map: one frame, start to finish | `start/what-an-engine-is` | must |
| What a mesh is: vertices and triangles that the GPU draws | `gpu/how-a-gpu-frame-works` | must |
| Rotations as quaternions | `basics/math-rotations` | helps |
| Models and the glTF importer | `assets/models-gltf` | helps |
| Opening a copy of a sample from the launcher | `start/first-game` | helps |

## `animation/skeletons` — Skeletons and forward kinematics

**Covers.** The job: the `Skeleton` asset holds a model's joints (unique names, parents, the rest pose, the root motion
joint) and turns a local pose into model-space matrices; it plays nothing. The problem and how engines solve it: joints
as entities of the scene (what many beginners build) against one array of joints sorted parents first (most engines, and
Strata); the rule that poses are not entities, with its reason (one character would add dozens of transform changes per
frame to the scene's caches, its hierarchy and its interpolation). The map: `AnimationTypes.h`, `Skeleton.h` and `.cpp`,
`RestPose.h` and `.cpp`, and the robot's skeleton as the Asset tab shows it (screenshot). Then in the order data flows:
`JointPose` as translation, rotation and scale applied scale first (the wrong multiplication order turns a joint about
the world origin instead of about itself), root joints relative to the animator (in a clause: the entity that carries
the Animator component, taught on `animation/importing`); `JointIndex` and `c_NoJoint`; `AnimationMath::Normalize`,
which returns the identity for degenerate input; `ToMatrix` and `MultiplyAffine` and why the fourth row is skipped; the
memory-layout diagram (arrays of names, parents and rest poses, every parent arrow pointing left); forward kinematics in
one pass (`ComputeModelTransforms`), which works because `Skeleton::Create` validates parents before children, finite
poses, normalized rotations, unique names and at most 4,096 joints; the rest pose against the bind pose (the bind pose
belongs to a skin: `animation/skinning`); `ComputeRestPose`, which an animator shows when nothing plays. The cooked form
STSK v1 (a header, 44-byte joints, then the names) and `Deserialize` as the part's first loader of untrusted bytes:
magic and version, every count bounded by the bytes left before anything is allocated, the order of the joints, no
trailing data. The toy: a three-joint arm in about 40 lines. How it is tested: `Animation.Assets` ("Skeletons validate,
round trip and find joints by name"; "Skeleton loading rejects truncated and garbage bytes") and the arm skeleton of
`AnimationTestUtils.h`. Exercise E1: build a three-joint skeleton by hand, check the tip's position, then put a child
before its parent and read the error; and a trace: step through `Skeleton::Deserialize` while the corruption test runs.
At the end the reader can compute a pose's model transforms by hand and explain why the joint order makes that a single
loop.

**Leaves out.**

- Quaternions, slerp and TRS as mathematics → `basics/math-rotations`, `basics/math-matrices`
- How the importer builds a skeleton from a glTF node tree → `animation/importing`
- The bind pose and inverse bind matrices → `animation/skinning`
- Untrusted input in general (checksums, bounded sizes, fuzzing) → `assets/robustness`, `engineering/test-program`

**Fit.** `over`: about 4,650 words against M (3,000). At or over M's top of 4,000, the page takes the next size, L (S2:
the estimate is inside L's range); five excerpts, the two concepts, two figures and three rules take the most, and the
trace beside E1 (about 250) is among what puts it over.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `animation:33-35` | feature | home | `JointPose` (relative to the parent, root joints to the animator entity, scale first), `JointIndex` and `c_NoJoint`, `AnimationMath::Normalize` |
| `animation:37` | feature | home | `ToMatrix` and `MultiplyAffine` |
| `animation:43-45` | feature | home | The `Skeleton` asset and its limits, the STSK v1 format and what `Deserialize` validates, `ComputeModelTransforms` |
| `animation:98` | feature | home | The rest pose with nothing playing: `Evaluate` returns `ComputeRestPose` (`RestPose.cpp` 9-13) |
| `animation:207` | feature | home | The test helpers: the arm skeleton and clips of `AnimationTestUtils.h`, and the skinned helpers that later pages use |
| `animation:251` | concept | home | A joint's local pose as TRS applied scale, rotation, translation; the order mistake (the mathematics is `basics/math-matrices`') |
| `animation:261` | concept | home | Skeletons: joints, parents, topological order, rest pose against bind pose, forward kinematics; arrays against scene nodes |
| `animation:334` | code | home | `Strata/src/Strata/Animation/AnimationTypes.h:15-22`: `JointPose`, the unit of animation |
| `animation:336` | code | home | `Strata/src/Strata/Animation/AnimationTypes.h:61-85`: `ToMatrix` and `MultiplyAffine`, a small optimization with its reason |
| `animation:337` | code | home | `Strata/src/Strata/Animation/Skeleton.cpp:178-187`: forward kinematics in one pass |
| `animation:338` | code | home | `Strata/src/Strata/Animation/Skeleton.cpp:61-75`: parents before children, finite poses, normalized rotations |
| `animation:339` | code | home | `Strata/src/Strata/Animation/Skeleton.cpp:121-161`: loading untrusted bytes safely |
| `animation:379` | figure | home | Diagram 2, the skeleton's memory layout |
| `animation:420` | figure | home | Screenshot 6: the Asset tab with the robot's skeleton (joint tree, root motion joint) and a clip's channels; `animation/clips` uses its clip half |
| `animation:437` | rule | home | Poses are not entities |
| `animation:465` | rule | home | Loaders reject truncated and garbage bytes: shown on the skeleton's loader, applied to clips on `animation/clips` |
| `animation:469` | rule | home | Skeleton joints are parents first |
| `animation:498` | hands-on | home | E1 |
| `new:16` | hands-on | home | Trace it yourself (track E): with a breakpoint in `Skeleton::Deserialize`, run "Skeleton loading rejects truncated and garbage bytes" in the engine's source build, and name for three corrupted inputs the check that refuses them (magic and version, a count bounded by the bytes left, a parent after its child). Evidence: `Strata/src/Strata/Animation/Skeleton.cpp:121-161`; `StrataTests/src/Animation/AnimationAssetTests.cpp:99-116` |
| `animation:527-530` | term | home | Joint (bone), skeleton (rig), topological order (parents first), rest pose |
| `animation:533-534` | term | home | Local and model space of a pose, forward kinematics |
| `animation:588` | term | home | STSK, defined here; STAC is named here and taught on `animation/clips`, where the glossary step homes its own entry (animation-q5) |
| `render-scene:636` | term | home | Skin, joint, skeleton, passed by `draw`: one glossary entry with `animation:527-528`; "skin" is defined on `animation/skinning` with `animation:553` |
| `animation:531` | term | link | The bind pose, against the rest pose; its home is `animation/skinning` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Quaternions, their normalization, q and -q | `basics/math-rotations` | must |
| Matrices and transforms: TRS, hierarchies, spaces, matrix order | `basics/math-matrices` | must |
| Asset handles and sub-assets (the skeleton is a model's sub-asset) | `assets/handles-meta` | must |
| Importing: from source files to engine data | `assets/importing` | must |
| Bytes and binary formats | `basics/bytes` | must |
| Errors returned, not thrown; `Ref<T>` | `core/conventions` | must |
| Arrays and what they cost | `basics/data-structures` | helps |
| Untrusted input: validate before use, bounded sizes | `assets/robustness` | helps |
| Writing one doctest test case | `core/first-change` | helps |
| The animator: the entity that carries the Animator component | `animation/importing` | helps |

## `animation/clips` — Clips: sampling motion

**Covers.** The job: an `AnimationClip` holds keys for the joints it moves and answers "what is this joint's local
pose at time t"; it knows joints by name only, until it is bound to a skeleton. The problem and how engines solve it:
the cost of finding keys and of storing them; keyframe reduction (Strata), quantization and curve fitting, and uniform
sampling with compression, each with its cost; Strata reduces only, and compression waits until it is measured to help
(the absence itself is `animation/limits`'). Clips and channels: one channel per joint and path (translation,
rotation, scale), Step, Linear and CubicSpline keys, the duration as the last key, the first and last values held
outside the keys; the clip-storage diagram (one shared array of times, one array of values, cubic triplets of
in-tangent, value and out-tangent). Sampling, in the order data flows: `FindKey`'s binary search with `upper_bound`;
glTF's three samplers in `SampleChannel`; slerp along the shorter arc with an nlerp fallback when the arc is short;
glTF's cubic Hermite with tangents scaled by the key span (the forgotten scale is the classic mistake); the
interpolation-curves figure; `Sample` and `SampleRootMotionJoint`. Binding by name, once per clip and skeleton
(`AnimationClipBinding`: missing targets skipped, root motion channels recorded), so a clip plays on any skeleton with
the same joint names and on no other; the three ways engines bind a clip (by index, fast and fragile; by name, as
Strata does; through retargeting tables, as Unreal and Unity's humanoid rigs do) and the mistake of looking joints up
by name every frame; the rule of unique joint names. Building a clip: `Create` shares identical
key-time arrays (an FNV-1a hash, then an exact compare); `ReduceKeys` drops the keys that interpolation reproduces
(tolerance 1e-5, 1e-4 of quaternion distance for rotations, a window of 256 keys, a cancel check every 256 keys,
cubic splines untouched). The cooked form STAC v1 and its loader, which applies the skeleton page's rule: every count
bounded before allocation, channels outside the data, invalid times and duplicate channels rejected. The toy: a
linear-only sampler in about 50 lines. How it is tested: `Animation.Sampling` ("Step, linear and cubic spline channels
interpolate as glTF defines"; "Rotations interpolate along the shorter arc and stay normalized"; the two reduction
cases) and the clip cases of `Animation.Assets`. Exercises E2 (sample by hand, from `AnimationAssetTests.cpp` 317),
E3 (corrupt a cooked clip byte by byte, in the style of `AnimationAssetTests.cpp` 161) and a trace (find with a search
every place a clip is bound to a skeleton). At the end the reader can
sample a channel by hand for each interpolation and say what reduction and shared times save.

**Leaves out.**

- Interpolation as mathematics: lerp, curves through keys, Hermite curves → `basics/math-interpolation`
- Where the importer reads glTF samplers and calls the reduction → `animation/importing`
- Blending several sampled poses → `animation/blending`
- Clip compression and retargeting beyond names, as absences → `animation/limits`

**Fit.** `fits`: about 5,270 words against L (5,000). Five excerpts and three concepts (the three ways to bind a clip
among them) take the most; the three exercises take about 750.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `animation:36` | feature | home | `AnimationMath::Slerp`: the shorter arc, the nlerp fallback above cos 0.9995 |
| `animation:46-51` | feature | home | The clip asset, STAC v1, shared key times, `ReduceKeys`, binding by name, sampling |
| `animation:258` | concept | home | Interpolation as glTF's three samplers: step, linear (lerp, slerp against nlerp), cubic Hermite with span-scaled tangents |
| `animation:267` | concept | home | Clips and channels: keys per joint and path, holding outside the keys, binding by name and what it cannot retarget; the three ways to bind a clip (by index, fast and fragile; by name, Strata's; through retargeting tables, Unreal's and Unity's humanoid rigs) and the mistake of looking joints up by name every frame (about 120 words) |
| `animation:271` | concept | home | Sampling cost and storage: binary search, reduction, quantization and curve fitting, compression deferred |
| `animation:335` | code | home | `Strata/src/Strata/Animation/AnimationTypes.h:43-58`: slerp with the shorter-arc flip and the nlerp fallback |
| `animation:340` | code | home | `Strata/src/Strata/Animation/AnimationClip.cpp:459-536`: the key search and the three interpolations |
| `animation:341` | code | home | `Strata/src/Strata/Animation/AnimationClip.cpp:438-457`: binding by name once, recording the root motion channels |
| `animation:342` | code | home | `Strata/src/Strata/Animation/AnimationClip.cpp:206-222`: sharing identical key-time arrays |
| `animation:343` | code | home | `Strata/src/Strata/Animation/AnimationClip.cpp:231-315`: keyframe reduction with its window and cancellation |
| `animation:383` | figure | home | Diagram 4, the clip's storage |
| `animation:386` | figure | home | Diagram 5, step, linear and cubic curves through the same keys; slerp against lerp |
| `animation:467` | rule | home | Joint names are unique and clips bind by name |
| `animation:499-500` | hands-on | home | E2 and E3 |
| `new:17` | hands-on | home | Trace it yourself (track E): starting from `AnimationClip::Bind`, find with a search every place that binds a clip to a skeleton (once per clip of an asset set, once for a clip played directly), and say why no joint is looked up by name while the clip plays. Evidence: `Strata/src/Strata/Animation/AnimationClip.cpp:438-457`; `Strata/src/Strata/Animation/AnimationSystem.cpp:485`, `:529` |
| `animation:539-540` | term | home | Clip, channel and path |
| `animation:542-547` | term | home | Step, linear and cubic spline; tangent (in and out); keyframe reduction; clip compression; binding; retargeting |
| `animation:465` | rule | use | The skeleton page's rule, applied to the STAC loader (`AnimationClip.cpp` 357-361) |
| `animation:420` | figure | use | The clip half of screenshot 6 |
| `animation:52` | feature | link | No clip compression, stated on `animation/limits` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Skeletons, joint names and local poses | `animation/skeletons` | must |
| Curves through keys: step, linear, cubic Hermite; lerp and its weight | `basics/math-interpolation` | must |
| Quaternions, slerp, q and -q | `basics/math-rotations` | must |
| Loading without stalling: loaders and cancellation | `assets/loading` | must |
| Hashes | `basics/data-formats` | must |
| Binary search and what it costs | `basics/data-structures` | must |
| `std::function` (the cancel check) | `basics/cpp-generic` | helps |
| Untrusted input | `assets/robustness` | helps |

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

## `animation/state-machines` — State machines

**Covers.** The job: the `AnimationController` asset (a `.stanimator` JSON document) declares parameters, states and
transitions, and `AnimatorInstance` runs it for one animator without a scene. The problem and how engines solve it:
what plays must follow the game (speed, ground, a jump); hand-written switches in scripts, flat state machines with
parameters (Unity's Mecanim, whose model Strata's is close to: parameters, Any State, exit times, triggers), and state
machines inside graphs (Unreal's animation blueprints, Esoterica, Morpheme); Strata: one flat state machine,
transitions from any state first, at most one transition per update. The document, on the robot's controller (the
excerpt: the Walk state with its Footstep events, the Jump transition from any state with `CanTransitionToSelf`, Idle
to Walk on Speed > 0.1), its state-machine diagram, and the same controller as the Asset tab's tables (screenshot).
Validation in `Create`: the limits (256 parameters, 1,024 states, 4,096 transitions, 16 conditions, 256 events per
state, speeds up to 100, fades up to 60 s), names, a condition's mode against its parameter's type, events
stable-sorted by time. Transitions grouped by source state with a counting sort (a CSR layout, the excerpt). Playback
without a scene: simple mode (no controller: the component's clip plays, and the Inspector greys `Clip` while a
controller is set); the state machine (the excerpt): after each advance, the transitions from any state, then the
current state's, and the first whose conditions hold and whose exit time was reached fires (the exit-time test itself
is `animation/time-events`'); the conditions Greater, Less, True, False and Set, all of which must hold; triggers
consumed by the transition that fires, and the pitfall of a trigger that stays set; `CanTransitionToSelf`; a state
without a clip is over at once and shows the rest pose; a transition with no condition and no exit time fires in the
first update of its state, so that state hardly plays. Commands and parameters: `Play`, `CrossFade` and `PlayClip`
(after `PlayClip` the controller's transitions do not run until `Play` or `CrossFade` names a state);
`SetFloat`, `SetBool` and `SetTrigger` by name, refused for a wrong type or a value that is not finite; commands given
while the controller loads wait for it (the rule that script commands never block on loading); a reloaded controller
keeps the values of parameters with the same name and type; a controller that lost a state restarts its entries at the
default state. `AnimatorSettings` (Speed, Loop, ApplyRootMotion, and Transitions, off for previews). The Inspector of
the playing robot shows the live state, `Walk -> Run` during a fade (screenshot). The toy: a state machine with two
states and one float condition, in about 60 lines. How it is tested: `Animation.StateMachine` in `AnimatorTests.cpp`
(conditions, triggers, commands while the controller loads) and the controller cases of `Animation.Assets`. The
exercise is a trace in the debugger: the update in which a trigger is consumed. At the end the reader can read a
`.stanimator` document and predict, update by update, which state the robot is in.

**Leaves out.**

- Weights and blended poses during a transition's cross-fade → `animation/blending`
- Exit times on looping states, normalized time and events → `animation/time-events`
- Editing a controller in the Asset tab and driving it from a script → `make/animation`
- The animation graph and blend trees, which Strata does not have → `animation/limits`

**Fit.** `fits`: about 4,355 words against L (5,000). Three excerpts, three figures, the concept and four rules take the
most; the two behaviours that trap game makers take one sentence each.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `animation:53-55` | feature | home | The controller asset and its document, its validation, transitions grouped by source |
| `animation:75` | feature | home | The `Clip` inactive reason while a controller is set |
| `animation:84-87` | feature | home | Simple mode, the state machine, conditions, triggers consumed |
| `animation:89` | feature | home | `CanTransitionToSelf` |
| `animation:92-95` | feature | home | Commands; waiting for the controller; a reload keeps parameter values; a controller changed under the animator |
| `animation:99-100` | feature | home | A state without a clip; `AnimatorSettings` |
| `animation:283` | concept | home | State machines for animation: states, transitions, conditions, consumed triggers, any-state priority; Mecanim, graphs; the mistakes |
| `animation:344` | code | home | `Strata/src/Strata/Animation/AnimationController.cpp:223-245`: a counting sort groups transitions by source state |
| `animation:348` | code | home | `Strata/src/Strata/Animation/AnimatorInstance.cpp:725-763`: any state first, the exit test, conditions, consuming triggers |
| `animation:365` | code | home | `Samples/ThirdPerson/Assets/Animations/Robot.stanimator:36-51` with lines 91-115: the Walk state and its Footstep events, the Jump transition from any state, Idle to Walk. The JSON reader and writer are `AnimationController.cpp` 248-553, which the survey only outlined |
| `animation:387` | figure | home | Diagram 6, the robot's controller as a state machine, drawn once with the Footstep event times; the one file of this figure, which `make/animation` uses (gamedev figure 14, `gamedev:422`, is the same figure; R34, D42) |
| `animation:416` | figure | home | Screenshot 4: the Inspector of the playing robot, its live state during a fade |
| `animation:418` | figure | home | Screenshot 5: the Asset tab with `Robot.stanimator`: parameters, states, transitions; captured once, and `make/animation` uses the same file (gamedev screenshot 20, `gamedev:458`, is the same picture; R34, D42) |
| `animation:471` | rule | home | Script commands never block on loading |
| `animation:485` | rule | home | Triggers stay set until consumed (`ResetTrigger`) |
| `new:20` | rule | home | A transition with no condition and no exit time fires in the first update of its source state, so that state hardly plays (one sentence). Evidence: `Strata/src/Strata/Animation/AnimationController.h:77-80` ("None: it fires as soon as they hold"); `Strata/src/Strata/Animation/AnimatorInstance.cpp:426-444` (no condition is all conditions holding), `:734-737` (no exit time counts as reached) |
| `new:21` | rule | home | After `PlayClip` the controller's transitions do not run until `Play` or `CrossFade` names a state (one sentence). Evidence: `Strata/src/Strata/Animation/AnimatorInstance.h:144-146`; `Strata/src/Strata/Animation/AnimatorInstance.cpp:727` (a played clip returns before the state machine), `:306` and `:333` (`Play` and `CrossFade` clear it), `:348-350` (`PlayClip` sets it) |
| `new:22` | hands-on | home | Trace it yourself (done, track E): with a breakpoint in the state machine's loop, run "Triggers are consumed by the transition that fires, once" in the engine's source build, and note in which update the trigger is consumed, by which transition, and why the next transition does not fire on it. Evidence: `Strata/src/Strata/Animation/AnimatorInstance.cpp:725-763`; `StrataTests/src/Animation/AnimatorTests.cpp:188-222` |
| `animation:557-563` | term | home | Animation controller, state, transition, Any State, condition, parameter, trigger |
| `animation:587` | term | home | `.stanimator` |
| `animation:212` | feature | use | The robot's controller and the scripts that set its parameters |
| `animation:88` | feature | link | Exit times, taught on `animation/time-events` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Clips, sampling and binding | `animation/clips` | must |
| JSON documents | `basics/data-formats` | must |
| Asset handles | `assets/handles-meta` | must |
| Loading without stalling (a controller arrives later) | `assets/loading` | must |
| Prefix sums and arrays of indices | `basics/data-structures` | helps |
| Hot reload of assets (a reloaded controller) | `assets/importing` | helps |
| The editor's Inspector and Asset tab, as far as the first game shows them | `start/first-game` | helps |
| Inactive reasons (`ComponentRegistry::SetInactiveReason`) and the properties they turn off | `world/reflection` | helps |
| Play mode: the running copy | `editor/play-mode` | helps |
| Normalized time and exit times | `animation/time-events` | helps |

## `animation/blending` — Blending and cross-fades

**Covers.** The job: while a cross-fade runs, `AnimatorInstance` plays up to four entries at once and blends their
poses into one; when the fade ends only the target is left. The problem and how engines solve it: a cut from one state
to the next pops; cross-fades with weight schedules (Strata), blend trees and blend spaces (which Strata does not
have), and inertialization, which decays the difference to the previous pose instead of evaluating both (not used);
the writer gives the sources for who uses which. Cross-fades, in the order data flows: `StartState` (the excerpt)
saves each playing entry's share, drops the faintest when a fifth would start and renormalizes the others;
`UpdateWeights` (the excerpt) grows the target's weight linearly with the fade's progress and scales the others by what
is left, so the weights always sum to 1; the timeline of three fades that interrupt each other. Blending poses in
`Evaluate` (the excerpt): one entry samples straight over the rest pose; several entries sum translations and scales
linearly and rotations as a weighted sum on the first entry's hemisphere, then normalize (blending matrices instead of
TRS shears the joints; the sign test is there because q and -q are one rotation); then forward kinematics; the root hold
at the end of `Evaluate` is `animation/root-motion`'s. A cross-fade halfway, captured at fixed steps with `play.step`
(screenshot). Phase mismatch: the robot's walk and run are 27% of a cycle apart in their cross-fade (`Docs/Roadmap.md`
1619-1620), so the feet slide; there are no sync markers. The toy: two poses and a fade, in about 40 lines. The
alternatives not chosen: slerp applied pair by pair, inertialization, sync markers, blend spaces. How it is tested:
"Cross-fade weights add up to 1, also when fades interrupt each other" and "A cross-fade blends the poses by the
weights" (`AnimatorTests.cpp`). Exercises E6 (start the target at the source's normalized phase and measure the robot's
foot sliding), E7 (slerp pair by pair against the weighted sum, for three entries or more) and a trace (a cross-fade
from the system's command to the weights, found with a search). At the end the reader can
compute every entry's weight while fades interrupt each other and explain why rotations are summed on one hemisphere.

**Leaves out.**

- Normalized time, which a phase-matched fade would use → `animation/time-events`
- Where the root's travel is weighted by the same shares → `animation/root-motion`
- Blend trees, layers, additive clips and sync markers as absences → `animation/limits`
- Slerp and the double cover as mathematics → `basics/math-rotations`

**Fit.** `fits`: about 3,750 words against M (3,000). Three excerpts, two figures and the concept take the most; the
three exercises take about 750.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `animation:90-91` | feature | home | Cross-fades (`c_MaxPlaying` = 4, linear growth, kept proportions, the faintest dropped) and pose blending |
| `animation:289` | concept | home | Blending and cross-fades: weighted pose blending, weight schedules, interrupted fades, inertialization, phase mismatch; blending matrices as the mistake |
| `animation:345` | code | home | `Strata/src/Strata/Animation/AnimatorInstance.cpp:247-288`: starting a cross-fade, saved shares, dropping the faintest of four |
| `animation:346` | code | home | `Strata/src/Strata/Animation/AnimatorInstance.cpp:587-609`: the weights of a fade and its end |
| `animation:349` | code | home | `Strata/src/Strata/Animation/AnimatorInstance.cpp:766-848`: evaluating a pose, one clip or several on one hemisphere, then forward kinematics; `animation/root-motion` reads its last part |
| `animation:389` | figure | home | Diagram 7, cross-fade weights over time |
| `animation:426` | figure | home | Screenshot 10, a cross-fade halfway, captured at fixed steps |
| `animation:487` | rule | home | Cross-fading walk to run without phase matching slides the feet |
| `animation:503-504` | hands-on | home | E6 and E7 |
| `new:23` | hands-on | home | Trace it yourself (track E): follow a cross-fade with a search from `AnimationSystem::CrossFade` through `AnimatorInstance::CrossFade` to `StartState` and `UpdateWeights`, and name the line that drops the faintest of four entries and the one that keeps the weights' sum at 1. Evidence: `Strata/src/Strata/Animation/AnimationSystem.cpp:989-993`; `Strata/src/Strata/Animation/AnimatorInstance.cpp:315-346`, `:247-288`, `:587-609` |
| `animation:538` | term | home | Hemisphere (quaternion) |
| `animation:567-570` | term | home | Cross-fade, blend weight, sync markers and phase matching, inertialization |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| State machines, transitions and their fade durations | `animation/state-machines` | must |
| Forward kinematics | `animation/skeletons` | must |
| Quaternions: q and -q, normalization, slerp | `basics/math-rotations` | must |
| Lerp and its weight | `basics/math-interpolation` | must |
| Normalized time (for E6) | `animation/time-events` | helps |
| Pausing and stepping a game (`play.step`) | `editor/stepping` | helps |

## `animation/time-events` — Time, loops and events

**Covers.** The job: `AdvanceEntry` moves one playing entry's playhead by the update's time, wraps it across the loop
boundary in both directions, counts the crossings, keeps the normalized time and collects the events the playhead
passed; the state machine reads the normalized time for its exit times. The problem and how engines solve it: `fmod`
keeps the place in the loop and loses the count of loops, so exit times and events at the boundary fail; events as
notifies stored in clips (Unreal) against events on controller states (Strata, because glTF carries none); comparing
`time == eventTime` never fires. Time: the state's speed times the animator's (negative speeds play backwards), and
clips that do not loop stop at their ends. Loop accounting (the excerpt, read in three parts): the event window
(from, to] forwards and [to, from) backwards, with an event at time 0 firing at the start and once per loop; the walk
across the boundary; steps of more than four loops skipped arithmetically, so the work per update stays bounded.
Normalized time is loops plus time over duration (1.5 is halfway through the second loop): the playhead-across-loops
diagram. Exit times (the exit test of the state machine's excerpt, read again): on a looping state, an exit time below
1 lets the transition fire at that point of every loop (0.4, 1.4, 2.4: the second diagram); otherwise it fires once the
normalized time reaches it. Only the current state's events fire, never those of states fading out; this page only
collects them, and the Animation system dispatches them after all poses. An event whose time is past its clip's
duration never fires, and nothing warns: validation checks only that the time is not negative, and the playhead stops
or wraps at the duration. The toy: a playhead with loops and events, in
about 50 lines. How it is tested: "Looping clips wrap and other clips stop at their end", "Events fire once each when
the playhead passes them, in order, also across a loop boundary", "An event at the start of a looping clip fires when it
starts and once per loop" and "Exit times fire in the update that reaches them, at every loop of a looping state"
(`AnimatorTests.cpp`). Exercise E5: a test matrix of exit times on states that do not loop, each firing frame
predicted before the run; and a trace in the debugger of the event windows of one test. At the end the reader can
trace a playhead through a large backward step and list the events and exit times it fires.

**Leaves out.**

- Dispatching events to listeners and scripts → `animation/system`
- Reacting to an event in a script (footstep sounds) → `make/animation`
- Typed clip events and sync markers, as absences → `animation/limits`
- Frame time and the fixed step in general → `core/time`

**Fit.** `fits`: about 3,690 words against M (3,000). The long excerpt quoted in three parts, two timelines and the two
concepts take the most; the dispatch of events is left to `animation/system`.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `animation:88` | feature | home | Exit times: normalized time with loops; once per loop below 1 on a looping state |
| `animation:96-97` | feature | home | Loop accounting (`Playing::Loops`, at most `c_MaxEventLoops` = 4 loops of events per update) and events |
| `animation:293` | concept | home | Time, loops and normalized time; speeds below zero; large steps; the `fmod` mistake |
| `animation:296` | concept | home | Animation events (notifies): clip notifies against state events, firing across loops and backwards; the mistakes |
| `animation:347` | code | home | `Strata/src/Strata/Animation/AnimatorInstance.cpp:455-585`: advancing a playhead with loops both ways, event windows, loop counts, bounded work |
| `animation:391` | figure | home | Diagram 8, the playhead across loops |
| `animation:393` | figure | home | Diagram 9, an exit time on a looping state |
| `animation:502` | hands-on | home | E5 |
| `new:24` | rule | home | An event whose time is past its clip's duration never fires, and nothing warns (one sentence). Evidence: `Strata/src/Strata/Animation/AnimationController.cpp:187-188` (validation refuses only a negative or non-finite time); `Strata/src/Strata/Animation/AnimatorInstance.cpp:505-511` (a clip that does not loop stops at its duration), `:524-536` (a looping one wraps there) |
| `new:25` | hands-on | home | Trace it yourself (track E): with a breakpoint in `AdvanceEntry`'s `fire`, run "Events fire once each when the playhead passes them, in order, also across a loop boundary" in the engine's source build, and write down each update's window and the events it fires. Evidence: `Strata/src/Strata/Animation/AnimatorInstance.cpp:455-585` (`fire` at line 480); `StrataTests/src/Animation/AnimatorTests.cpp:363-394` |
| `animation:564-566` | term | home | Exit time, normalized time, playhead |
| `animation:571` | term | home | Animation event (notify) |
| `animation:348` | code | use | The exit test (`AnimatorInstance.cpp` 734-745), read again |
| `animation:127` | feature | link | Event dispatch, taught on `animation/system` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| State machines: states, transitions, an exit time as a field | `animation/state-machines` | must |
| Clips: duration, holding outside the keys | `animation/clips` | must |
| Floating point, rounding and precision (normalized time in double) | `basics/numbers` | must |
| Delta time | `core/time` | must |

## `animation/root-motion` — Root motion

**Covers.** The job: when an animator applies root motion, its root joint's horizontal travel and its turn about +Y
are taken out of the pose and move the entity, through a character controller when the entity has one. The problem and
how engines solve it: clips in place moved by code (the feet slide when the speeds differ) against root motion (the
clip decides the travel); the double-motion mistake (the root moves in the pose and the entity moves too), drift at
loop boundaries, vertical root motion that fights gravity (Strata keeps the vertical part in the pose), the entity's
scale. The setup: `RootMotionSetup`, the ancestors' rest transform and rotation above the root motion joint, and the
mask of its subtree. Extraction (the excerpts): the yaw of a quaternion with `atan2`; `RootTravel::Append` adds each
stretch in the frame the root faced at the clip's start; `Advance` splits the travel at loop crossings (to the end,
whole loops up to 64, from the start; mirrored backwards) and weights each entry's travel by its share of the blend;
the extraction diagram, seen from above. Holding the root: the pose moves the root's subtree back by the offset and
the yaw (`HoldRoot` at the end of `Evaluate`), so the mesh does not run ahead of the entity. Applying it (the excerpt):
`AnimationSystem::ApplyRootMotion` is the one place that moves the entity: the move through the entity's world
transform (its scale included) and the parent's inverse, the turn multiplied into the rotation, the change signalled
with `MarkModified<TransformComponent>`; on an entity with a character controller, the controller walks the move at its
next fixed step (`ICharacterControl::AddCharacterMotion`: it collides, climbs steps and keeps to the ground) and only
the turn is written; the move reaches a controller only on the animator's own entity, so a model under the entity
that carries the controller walks away from its capsule. The toy: a root that walks a circle, in about 50 lines. How it
is tested: `Animation.RootMotion` (the travel and the held root; the turn; the same amount every update across loop
boundaries; a character controller that collides). The exercise is a trace in the debugger of one update's move into
the controller. At the end the reader can say where every centimetre of a looping walk's travel goes in one update.

**Leaves out.**

- How the character controller walks a move → `physics/character-controllers`
- Turning root motion on for a character in the editor → `make/animation`
- Blend weights themselves → `animation/blending`
- When the system applies root motion in its frame → `animation/system`

**Fit.** `fits`: about 3,565 words against M (3,000). Three excerpts, the concept with its four mistakes and the
extraction diagram take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `animation:107-111` | feature | home | `RootMotionSetup`, extraction, holding the root, `ApplyRootMotion`, root motion through a character controller, which the move reaches only on the animator's own entity (one sentence, about 40 words: `AnimationSystem.cpp` 804; `CharacterControllers.cpp` 816-822 and 1050-1056 look the controller up by that entity) |
| `animation:300` | concept | home | Root motion: in place against root motion, extraction, holding the root, applying it through a controller; the four mistakes |
| `animation:350` | code | home | `Strata/src/Strata/Animation/AnimatorInstance.cpp:17-24` with lines 82-97: the yaw of a rotation, root travel added up in the clip-start frame |
| `animation:351` | code | home | `Strata/src/Strata/Animation/AnimatorInstance.cpp:652-723`: root motion split at loop crossings, weighted by the blend |
| `animation:354` | code | home | `Strata/src/Strata/Animation/AnimationSystem.cpp:788-827`: applying root motion through the world and parent transforms, or handing it to a character controller |
| `animation:394` | figure | home | Diagram 10, root motion extraction from above |
| `animation:445` | rule | home | Root motion moves entities only in `AnimationSystem::ApplyRootMotion`, signalled through the transform contract |
| `animation:448` | rule | home | The root's subtree is held back when root motion applies |
| `animation:572-573` | term | home | Root motion, root motion joint |
| `animation:575` | term | home | In-place animation |
| `new:26` | hands-on | home | Trace it yourself (done, track E): with a breakpoint in `AnimationSystem::ApplyRootMotion`, run "Root motion walks a character controller, which collides, and turns its entity" in the engine's source build, note which branch runs and the move handed to `AddCharacterMotion`, then follow it to the lookup that finds the controller on the animator's own entity. Evidence: `Strata/src/Strata/Animation/AnimationSystem.cpp:788-827`; `Strata/src/Strata/Physics/CharacterControllers.cpp:1050-1056`, `:816-822`; `StrataTests/src/Animation/AnimationSystemTests.cpp:832` |
| `animation:349` | code | use | The root hold at the end of `Evaluate` (`AnimatorInstance.cpp` 826-847) |
| `physics:138` | feature | use | `ICharacterControl::AddCharacterMotion`, the hook `physics/character-controllers` teaches |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Character controllers and their root-motion hook | `physics/character-controllers` | must |
| Normalized time and loop crossings | `animation/time-events` | must |
| The transform contract and change signals | `world/scene-graph` | must |
| World and parent transforms and their inverses | `basics/math-matrices` | must |
| Angles, `atan2` and radians | `basics/math-vectors` | must |
| Rotating a direction by a quaternion | `basics/math-rotations` | must |
| The fixed step | `core/time` | must |
| Blend weights of the playing entries | `animation/blending` | must |

## `animation/system` — The Animation system

**Covers.** The job: `AnimationSystem` is the "Animation" scene system of a playing scene: one record per animator,
shared assets, a parallel and deterministic update, and the only place where animation changes the scene (root motion,
attachments, events); through three scene services it is also the module's face to the rest of the engine. The problem
and how engines solve it: many animators per frame on many cores without data races, with results that do not depend on
the number of threads. The module and its place (the layer diagram): a layer above Scene that may include Core, Asset,
Reflection and Scene; only the Engine and AssetPipeline layers include it; a build can leave it out
(`STRATA_WITH_ANIMATION`); `RegisterAnimationModule` registers the components, the three loaders and the system (after
Scripting and before Physics, both soft, not in Simulate, profile stage `Scene.Animation`). Where it runs in the frame
(the frame-order diagram): after the scripts that set parameters, before physics so that root motion moves bodies before
the step, with the frame's delta time, in Play mode only; a scene that does not play has no system, and the editor
installs a preview instead. Records: one `AnimatorRecord` per `AnimatorComponent`, added on the construct signal,
flagged on destroy, compacted in one pass that keeps the order; sorted by entity at the start, then in the order they
were added; deactivated animators reset and reactivated ones start again; animators of additive sub-scenes and of the
prefabs that `InstantiateMany` makes get records of their own. Asset sets: animators with the same skeleton, controller
and clip share one set, whose assets are requested once per update and held while used, with bindings and reaches once
per skeleton and clip and failures logged once (the rule: hold handles, request every update, never block); a clip
played directly has its own binding; a table of what a character shows while something is missing (no pose and the bind
pose until the skeleton, controller and clips are in; a skeleton that does not load keeps it so, with one warning; a
controller that does not load plays the component's Clip; a state whose clip does not load shows the rest pose; a
skeleton with fewer joints than the skin needs leaves the bind pose). The update (the long excerpt, with the timeline
across threads): the sets are resolved on the main thread; a `ParallelFor` in batches of 8 classifies each record (None,
Waiting, Sync, Step) and steps it in place; Sync records are queued, synchronized on the main thread in record order and
stepped in a second `ParallelFor`; then the main thread publishes in record order (pose versions, events queued, root
motion last), places attachments, compacts and dispatches the events. Determinism: jobs read the registry and the sets
and write only their own record, and a test compares 0, 1 and 7 threads bit for bit (the excerpt). Attachments (the
excerpt, and the menu robot's flag as the screenshot): the local transform that puts the entity at the joint, skipped
when nothing changed, refused for an entity above its animator, written through the transform contract, and overwriting
the entity's translation, rotation and scale every update (an offset goes on a child, as the flag's holder shows); an
attachment under an interpolated character stays on its joint on frames without a step. Event dispatch (the excerpt):
after all poses, outside the jobs, over a snapshot of the listeners, with names copied and removed listeners skipped;
the script system is one listener (`scripting/script-system`). The scene services (the excerpt of `SceneServices.h`):
`SkeletonPose` and `ISkinningPoses` for renderers, `IAnimatorControl` for scripts and other modules,
`IAnimationEventSource` for listeners; the system registers all three in its constructor and is the playing scene's
poses provider. The idle cost: with no records an update returns after resetting its stats and compacting, so a scene
without animators pays next to nothing. `AnimationSystemStats`. What the code does at the pin: the system finds its
assets through the active asset manager (`AnimationSystem.cpp` 42, 53, 64 and 983), and the page says so without calling
it a rule. The toy: a sequential system with records and a publish loop, in about 70 lines. How it is tested: the
`Animation.*` suites (Assets, Sampling, StateMachine, System, RootMotion, Streaming, Preview, Interpolation) and their
neighbours in the renderer, scripting and editor tests, the perf tests `Perf.Animation.Evaluate1000` and
`Perf.Animation.CulledAnimators10k` (their budgets are read from `reference/performance`, never typed), and the feature
test's arm rig (`AnimationFeatures.cpp`). Exercise E9: break determinism on purpose and watch the test fail; and a
trace: find every write to the scene and the thread it runs on. At the end the reader can say which thread does what in
one animation update, and why the result is the same on every machine.

**Leaves out.**

- The threading model and deterministic parallel work in general → `core/jobs`
- Scene services and the order of scene systems in general → `world/systems`
- What the script host does with `IAnimatorControl` → `scripting/host-api`
- How a script receives an event (`OnAnimationEvent`) → `scripting/script-system`
- Skipping poses that nobody sees → `animation/culling`
- How perf budgets are set and measured → `engineering/perf-lab`

**Fit.** `over`: about 6,660 words against L (5,000). At or over L's top of 6,500, the page takes the next size, XL (S2:
the estimate is inside XL's range, which an internals page of track E may take); five excerpts, five concepts and four
figures take the most, and the table of missing assets and the trace (about 400) are among what puts it over.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `animation:24-27` | feature | home | The module as a layer, the optional module, `RegisterAnimationModule`, only Engine and AssetPipeline include it |
| `animation:117-128` | feature | home | Records, record order, activity, asset sets, a clip played directly, parallel evaluation, determinism, publishing, the idle cost, attachments (which overwrite the entity's translation, rotation and scale every update: `AnimationSystem.cpp` 866-880), event dispatch, stats |
| `animation:133` | feature | home | Animators of additive sub-scenes and of `InstantiateMany` (`AnimationSystemTests.cpp` 900, 982, 1101) |
| `animation:140-144` | feature | home | `SkeletonPose`, `ISkinningPoses`, `IAnimatorControl`, `IAnimationEventSource`, their registration |
| `animation:197` | feature | home | The unit suites by name, without case counts (counts the engine can change are never typed), for the page's "How it is tested" |
| `animation:202` | feature | home | The perf tests (`Perf/AnimationPerfTests.cpp` 156-240), their budgets taken from `reference/performance` |
| `animation:204` | feature | home | The feature test's arm rig, its controller and model |
| `animation:305` | concept | home | Attachments (sockets): written each update through the transform contract; joints never become entities |
| `animation:307` | concept | home | Where animation runs in the frame |
| `animation:310` | concept | home | Parallel, deterministic evaluation as the system applies it (the general idea is `core/jobs`') |
| `animation:314` | concept | home | Asset sharing and lifetime: sets keyed by handles, requests every update, reloads and rebinding, failures logged once |
| `animation:320` | concept | home | Decoupling through services; providers that can be swapped, versions per provider |
| `animation:352` | code | home | `Strata/src/Strata/Animation/AnimationSystem.cpp:572-716`: the system's update, from the sets to the dispatch |
| `animation:355` | code | home | `Strata/src/Strata/Animation/AnimationSystem.cpp:829-888`: attachments, unchanged writes skipped, the cycle guard |
| `animation:356` | code | home | `Strata/src/Strata/Animation/AnimationSystem.cpp:890-917` with lines 1093-1113: dispatch over a snapshot, the removed flag |
| `animation:357` | code | home | `Strata/src/Strata/Scene/SceneServices.h:270-376`: the three services as the module's public contract |
| `animation:362` | code | home | `StrataTests/src/Animation/AnimationSystemTests.cpp:1036-1096`: the same bytes with 0, 1 and 7 threads |
| `animation:396` | figure | home | Diagram 11, the system's update across threads, with what each phase reads and writes |
| `animation:399` | figure | home | Diagram 12, the frame order of the systems and the renderer's report |
| `animation:405` | figure | home | Diagram 15, the module's layers |
| `animation:421` | figure | home | Screenshot 7, the menu robot holding the flag |
| `animation:440-443` | rule | home | Only scene services cross the module's boundary; jobs write only their own record |
| `animation:474-476` | rule | home | Events are dispatched after all poses; hold handles, request every update, never block |
| `animation:479` | rule | home | The animation system is Play-only |
| `animation:506` | hands-on | home | E9 |
| `animation:576` | term | home | Attachment (socket) |
| `animation:579-580` | term | home | Asset set, record |
| `animation:585` | term | home | Provider (of poses) |
| `render-scene:641` | term | home | `ISkinningPoses`, passed by `draw`: defined with the scene services |
| `animation:638` | open | home | The static asset-manager access at the pin (`AnimationSystem.cpp` 42, 53 and 64 call `AssetManager::GetActive()`, 983 `AssetManager::GetAssetType`), stated as what the code does and called no rule; the engine hears of it through pipelines.md §11 (R34, D37) |
| `new:27` | feature | home | What a character shows while something is missing, as a table in the asset-sets section (about 150 words): no pose and the bind pose until the skeleton, controller and clips are in; a skeleton that does not load keeps the bind pose, with one warning; a controller that does not load plays the component's Clip; a state whose clip does not load shows the rest pose; a skeleton with fewer joints than the skin needs leaves the bind pose. Evidence: `Strata/src/Strata/Animation/AnimationSystem.cpp:403-404`, `:418-428`, `:474-479`, `:559-566`, `:923-927`; `Strata/src/Strata/Renderer/RenderScene.cpp:1292`, `:1374-1384`; `StrataTests/src/Animation/AnimationSystemTests.cpp:257` |
| `new:28` | open | home | Check: Simulate and skinned meshes. In Simulate the running copy has no Animation system and the editor's preview serves only the edited scene, so the running copy's skinned meshes draw in their bind pose; after the capture, the Play-only rule (`animation:479`) says what Simulate shows in one sentence (read from the code, not run; the photographer's capture in the pin's editor settles it and blocks the page's brief, R39). Evidence: `Strata/src/Strata/Animation/AnimationRegistration.cpp:33-36`; `Strata/src/Strata/Scene/Scene.cpp:2114-2115`; `StrataEditor/src/Editor/EditorContext.cpp:1382`, `:1399`, `:2697-2704`; `StrataEditor/src/Editor/EditorContext.h:313`, `:823`; `Strata/src/Strata/Renderer/RenderScene.cpp:1286`, `:1348`, `:1374-1384` |
| `new:29` | hands-on | home | Trace it yourself (track E): find with a search every place where the Animation system writes the scene (`MarkModified<TransformComponent>`), and show in `OnUpdate` that each runs on the main thread after both `ParallelFor` phases. Evidence: `Strata/src/Strata/Animation/AnimationSystem.cpp:809`, `:826`, `:880`; `:572-716` (`ParallelFor` at 608 and 648; root motion, attachments and dispatch at 707, 712 and 715) |
| `animation:134` | feature | use | The attachment half: on its joint on frames without a step (`AnimationSystemTests.cpp` 1704) |
| `scene-ecs:105` | feature | use | The built-in update order of the scene systems |
| `foundation:36` | feature | use | Optional modules |
| `animation:178` | feature | link | `OnAnimationEvent`, taught on `scripting/script-system` |
| `animation:176` | feature | link | The animator host functions, taught on `scripting/host-api` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Systems, phases and fixed steps; scene services; the order of scene systems | `world/systems` | must |
| The threading model; deterministic parallel work; `ParallelFor` | `core/jobs` | must |
| Residency, pins and eviction; requests every frame | `assets/residency` | must |
| The transform contract and change signals | `world/scene-graph` | must |
| The layer table, optional modules, registries and the composition root | `core/layers-registries` | must |
| EnTT's construct and destroy signals | `world/scene-graph` | must |
| Interfaces and virtual calls | `basics/cpp-classes` | must |
| Lambdas and `std::function` | `basics/cpp-generic` | must |
| Atomics and `thread_local` | `basics/threads` | must |
| What one step computes: blending, events, root motion | `animation/root-motion` | must |
| Loading scenes additively | `world/sub-scenes` | helps |
| Profiling stages | `core/profiling` | helps |
| Play and Simulate: the running copy | `editor/play-mode` | helps |
| The script system as an event listener | `scripting/script-system` | helps |
| Perf budgets and how they are measured | `engineering/perf-lab` | helps |
| The feature test | `engineering/feature-test` | helps |

## `animation/culling` — Animating only what is seen

**Covers.** The job: an animator with `CullingMode` WhenVisible skips computing its pose while no renderer reports it
seen, and keeps everything that gameplay can observe (time, transitions, events, root motion). The problem and how
engines solve it: posing thousands of animators that nobody sees; lower update rates by distance or screen size, culling
modes based on visibility, and Strata's WhenVisible, with the writer's sources for who uses which; why a frozen pose
cannot be culled by its own bounds (the character would never be seen again once its clip carried it elsewhere). The
loop (the feedback diagram): the renderer culls skinned proxies with posed bounds grown by the reach; extraction
collects the animators of visible skin proxies, and of shadow casters whose shadow can fall into the view, and reports
each once (`ISkinningPoses::ReportVisible`); the next update evaluates the animators seen in the previous one (the
decision excerpt: seen, rigid parts, and the first pose always computed). The reach (the excerpt of
`AnimationReach::Compute`): each clip sampled 15 times a second (2 to 48 samples), boxes of the joints' origins with and
without root motion and the largest scale, published with the pose; worked out again only when the play revision, the
set's reach version, the culling mode or root motion change; the play revision counts every change of what plays. The
rules: WhenVisible keeps time, events, transitions and root motion, because gameplay must not depend on the camera (one
exception: a joint read with `GetJointTransform` while the animator is unseen gives its stale pose, placed at the
entity's current transform; and scripts always read the previous update's pose, because Animation runs after Scripting);
publish a reach with poses that may be skipped; animators that only move rigid parts pose every update, because no
skinned mesh could report them (the Course's chest, a clip on two rigid parts, is the example). Stale poses and paused
frames (the excerpt): `ReportVisible` returns whether the drawn pose is older than the animator's time (the renderer
counts `StalePoses`), and `OnPausedUpdate` poses those animators at their time without advancing them, so
`viewport.capture` renders again until it shows the pose of the moment. Many animators: the Open World foxes, which the
sample sets to AlwaysAnimate, switched to WhenVisible by the figure's recipe and seen from afar (screenshot, whose
caption names the fox's authors and license). The toy: visibility flags and a frozen pose, in about 40 lines. How it is
tested: the WhenVisible cases of `Animation.System` and the `GPU.Animation` suite (casters out of view report their
animators only when their shadows can fall into the view; a clip that carries the mesh into a view its first pose is not
in is posed there; the suite's other cases are read by `draw/skinned` and `animation/editor`); the release of each
refinement is checked for the page's `since`. Exercise E4: a `SampleCount` stat, read with WhenVisible on and off; and a
trace: a visibility report from the renderer to the next update's decision. At the end the reader can say why an unseen
robot keeps its footsteps, and how it reappears posed where its clip took it.

**Leaves out.**

- Posed bounds and the renderer's culling of skinned proxies → `draw/skinned`
- The GPU's visibility feedback → `draw/gpu-driven`
- Which shadow casters can reach a view → `light/sun-shadows-1`
- Measuring a game with many characters → `make/performance`

**Fit.** `fits`: about 3,915 words against M (3,000). Three excerpts, the concept and three rules take the most; the
estimate is 85 words below M's top, and the renderer's half of the loop is linked, not taught.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `animation:76` | feature | home | `AnimatorCullingMode`: AlwaysAnimate, WhenVisible |
| `animation:101` | feature | home | The play revision as the key of the reach's cache |
| `animation:129-132` | feature | home | WhenVisible culling, the reach, rigid-part animators, stale-pose reports and paused posing |
| `animation:156` | feature | home | The renderer's visibility report and its `StalePoses` stat (`SceneRendererExtraction.cpp` 286-309, 1306-1321) |
| `animation:200` | feature | home | The `GPU.Animation` suite, for the page's "How it is tested" |
| `animation:316` | concept | home | Animation LOD and culling: update rates, culling modes, reach boxes, stale-pose feedback; the two mistakes |
| `animation:353` | code | home | `Strata/src/Strata/Animation/AnimationSystem.cpp:739-755`: the culling decision |
| `new:4` | code | home | `Strata/src/Strata/Animation/AnimatorInstance.cpp:125-166`: `AnimationReach::Compute`, the boxes a clip takes the joints through |
| `new:5` | code | home | `Strata/src/Strata/Animation/AnimationSystem.cpp:935-968`: `ReportVisible` and `OnPausedUpdate`, posing stale animators while paused |
| `animation:401` | figure | home | Diagram 13, the WhenVisible feedback loop |
| `animation:427` | figure | home | Screenshot 11: the Open World foxes from afar; the sample sets them to AlwaysAnimate (`Samples/OpenWorld/Assets/Prefabs/Fox.stprefab:2`), so the recipe sets WhenVisible; its caption names the fox's authors and license (model by PixelMannen, CC0 1.0; rigging and animation by tomkranis and glTF conversion by @AsoboStudio and @scurest, CC BY 4.0), and `appendix/credits` holds the full credit (R22; R32, D18) |
| `animation:450-454` | rule | home | WhenVisible keeps time, events, transitions and root motion; publish a reach; rigid-part animators pose every update |
| `new:30` | feature | home | A joint read while a WhenVisible animator is unseen: `GetJointTransform` returns its stale pose, placed at the entity's current transform, so a joint that gameplay reads does depend on the camera; scripts read the previous update's pose, because Animation runs after Scripting (one sentence beside the rule of `animation:450`). Evidence: `Strata/src/Strata/Animation/AnimationSystem.cpp:739-755` (unseen animators skip their poses), `:1075-1087` (`GetJointTransform` reads the last pose times the current world transform); `Strata/src/Strata/Animation/AnimationRegistration.cpp:33-37` (after Scripting) |
| `new:31` | open | home | Check: The recipe that sets WhenVisible on every fox. The sample sets `CullingMode` AlwaysAnimate on its 30 foxes, instances of `Fox.stprefab` in ten cells of the Island world, each named once (`Fox`, `Fox (1)` and on); screenshot 11's recipe must set WhenVisible on every fox while a setup step's `entityName` names exactly one entity (pipelines.md §5.2). The photographer settles how; the check blocks the page's brief (R39; animation-q8). Evidence: `Samples/OpenWorld/Assets/Prefabs/Fox.stprefab:2`; `grep -oh '"CullingMode":"[A-Za-z]*"' -r Samples/OpenWorld/Assets/Worlds/Island/Wildlife` finds AlwaysAnimate 30 times and nothing else; `Tools/LookDev.py:720-731` (a setup step's `entityName` takes the first entity of that name) |
| `animation:501` | hands-on | home | E4 |
| `new:32` | hands-on | home | Trace it yourself (track E): follow a visibility report with a search from the renderer's extraction to `ReportVisible`, which records the update that saw the animator, and to `PrepareStep`, which reads it in the next update to decide whether to pose. Evidence: `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:1306-1321`; `Strata/src/Strata/Animation/AnimationSystem.cpp:935-940`, `:739-755` |
| `animation:555` | term | home | Reach |
| `animation:577-578` | term | home | Culling mode, stale pose |
| `render-scene:642` | term | home | WhenVisible animator, passed by `draw`: one glossary entry with `animation:577` |
| `animation:645` | open | home | The release of each WhenVisible refinement, for the page's `since` |
| `render-scene:164` | feature | use | The renderer's side of the visibility reports |
| `render-scene:159` | feature | use | Posed bounds grown by the reach |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The Animation system's records and update | `animation/system` | must |
| Skinning and palettes | `animation/skinning` | must |
| CPU and GPU culling paths; frustum and box tests | `draw/bounds-culling` | must |
| Skinned meshes in the renderer; posed bounds | `draw/skinned` | must |
| Visibility feedback | `draw/gpu-driven` | helps |
| Shadow mapping | `light/shadow-basics` | helps |
| Readback (a capture renders again) | `gpu/readback-timing` | helps |
| Pausing and stepping a game | `editor/stepping` | helps |

## `animation/editor` — Edit-mode poses and previews

**Covers.** The job: `AnimationPreview` is the poses provider of scenes that do not play (the edited scene, and the
scenes that thumbnails render): it shows rest poses or the first frame of what each animator plays on start, answers
preview requests, and never writes the scene. Why it is needed (edit-mode posing): a scene that does not play has no
Animation system, and without a provider a skinned mesh is drawn in its bind pose, which in many files lies along an
axis (a Z-up export under an "Armature" node); the page shows it with a diagram or a GPU test capture, because the
editor always installs a preview. The providers diagram: `AnimationPreview` for the edited scene and thumbnails,
`AnimationSystem` for the play copy; pose versions belong to their provider, so the render scene recomputes every
palette when the provider changes. The same evaluation as play (the excerpt): `EvaluateAnimator` runs an
`AnimatorInstance` with transitions off. Rest poses shared per skeleton (the excerpt): an edit-pose key of skeleton,
controller, clip and root motion; animators looked at only on component signals; poses computed again only when a
reimport changes their sources, so an idle editor pays nothing (`AnimationPreviewStats`). The ClipStart edit pose and
`viewport.setSettings {editPose: "rest" | "clipStart"}`, the Scene view's camera chip (the robot both ways, as a
screenshot). Render transforms (the excerpt): attachments, and the meshes under them, drawn at their joints through
`ISkinningPoses::GetRenderTransforms`, never written (the rule: previews change no scene data). Posed bounds in the
editor's tools: `SceneBounds::GetPosedMeshBounds` for framing, focus, drop to ground and placement. Thumbnails make a
rest-pose preview for each scene they render. The animation commands, the editor's API for this part:
`animation.createController` makes a `.stanimator` from JSON sections; `animation.setController` replaces the given
sections as one undo step (`AssetEdit::SetControllerData`); `animation.info` (a Query) describes a model, a skeleton, a
clip, a controller, or a live animator's state and parameters; `animation.preview` (Session) is deferred until the
requested pose shows and refuses while the game plays (screenshot, with the preview chip). Each command is given as
the line to paste, with a link forward to `editor/commands`. The toy: a provider that returns rest poses, in about 40
lines. How it is tested: `Animation.Preview` (a request is posed once its own pose is computed; rest poses are what
animators evaluate with nothing playing; computed once per skeleton and again only after a reimport; a request wins
over the rest pose; the clip-start edit pose), the GPU case "Skinned models stand in their rest pose in edited scenes
as they do in play before their first animation, on both paths", and `EditorAnimationTests.cpp`. The exercise is a
trace in the debugger: how often the clip-start pose is computed for animators that share a skeleton and a clip. At
the end the reader can explain what draws a character in the editor before Play, and why editing it writes nothing to
the scene.

**Leaves out.**

- Using the preview chip → `make/commands`
- Using the Asset tab's tables and the Inspector's live state → `make/animation`
- Commands, their kinds and deferred results in general → `editor/commands`, `editor/deferred-commands`
- How thumbnails are rendered and cached → `editor/thumbnails`
- Placing content and its ghost → `editor/placement`

**Fit.** `over`: about 4,410 words against M (3,000). At or over M's top of 4,000, the page takes the next size, L (S2:
the estimate is inside L's range); three excerpts of the preview, four figures and the four commands take the most, and
the Simulate case and the trace are among what puts it over.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `animation:153` | feature | home | A new provider recomputes every palette: versions are a provider's own (`RenderScene.cpp` 1357-1360, 1390) |
| `animation:164-170` | feature | home | The preview provider, the same evaluation as play, rest poses, the ClipStart edit pose, render transforms, the idle cost, posed bounds in editor tools |
| `animation:185-189` | feature | home | `animation.createController`, `animation.setController`, `animation.info`, `animation.preview`, `viewport.setSettings {editPose}` |
| `animation:193` | feature | home | Thumbnails make a rest-pose preview per scene they render |
| `animation:322` | concept | home | Edit-mode posing: bind pose against rest pose, rest poses per skeleton, requests that change no scene data, render transforms |
| `new:6` | code | home | `Strata/src/Strata/Animation/AnimationPreview.cpp:39-80`: `EvaluateAnimator`, the play-mode evaluation with transitions off |
| `new:7` | code | home | `Strata/src/Strata/Animation/AnimationPreview.cpp:266-304`: the edit-pose key and the animators examined only when they change |
| `new:8` | code | home | `Strata/src/Strata/Animation/AnimationPreview.cpp:440-502`: render transforms for attachments and the meshes under them |
| `animation:403` | figure | home | Diagram 14, the providers of `ISkinningPoses` |
| `animation:410` | figure | home | Screenshot 1: the robot in edit mode, rest pose and clip start side by side |
| `animation:412` | figure | home | Screenshot 2: the bind pose without a provider, as a diagram or a GPU test capture |
| `animation:415` | figure | home | Screenshot 3: `animation.preview` with the preview chip |
| `animation:461` | rule | home | Pose versions belong to their provider |
| `animation:478` | rule | home | Previews change no scene data |
| `animation:581-583` | term | home | Edit pose, pose preview, render transform |
| `animation:643` | open | home | Screenshot 2 cannot be made by editor use: the figure is a diagram or a test capture |
| `new:33` | open | home | Check: Simulate and skinned meshes. The page plans "the editor always installs a preview", and `animation:643` says the bind pose cannot be shown by editor use; both fail while Simulate runs: the running copy has no Animation system and the preview serves only the edited scene, so the viewport draws the copy's skinned meshes in their bind pose (read from the code, not run). After the photographer's capture in the pin's editor, the page states the Simulate case beside the providers (about 60 words) and screenshot 2 (`animation:412`) is made in Simulate; the check blocks the page's brief (R39). Evidence: `Strata/src/Strata/Animation/AnimationRegistration.cpp:33-36`; `Strata/src/Strata/Scene/Scene.cpp:2114-2115`; `StrataEditor/src/Editor/EditorContext.cpp:1382`, `:1399`, `:2697-2704`; `StrataEditor/src/Editor/EditorContext.h:313`, `:823`; `Strata/src/Strata/Renderer/RenderScene.cpp:1286`, `:1348`, `:1374-1384` |
| `new:34` | hands-on | home | Trace it yourself (done, track E): with a breakpoint on the call of `EvaluateAnimator` in `UpdateRestPoses`, run "The clip-start edit pose shows the first frame of what animators play on start, once per skeleton and clip" in the engine's source build, and count the hits for animators that share a skeleton and a clip. Evidence: `Strata/src/Strata/Animation/AnimationPreview.cpp:306-406` (the call at line 389), `:266-304` (the edit-pose key); `StrataTests/src/Animation/AnimationSystemTests.cpp:1540` |
| `editor-core:90` | feature | use | The `animation.*` command group |
| `animation:190` | feature | link | The preview chip, taught on `make/commands` |
| `animation:191-192` | feature | link | The Asset tab's views and the Inspector's live state, taught on `make/animation` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The Animation system, its scene services and the poses provider | `animation/system` | must |
| Skinning: bind pose and palettes | `animation/skinning` | must |
| Content versions and reimports (hot reload of assets) | `assets/importing` | must |
| Reading and running a command | `start/how-to-read` | helps |
| Commands are the API: the registry, kinds, schemas | `editor/commands` | helps |
| Commands that take frames (`Defer`, `MayDefer`) | `editor/deferred-commands` | helps |
| Undo and redo | `editor/undo` | helps |
| Play and Simulate: the running copy | `editor/play-mode` | helps |
| Thumbnails | `editor/thumbnails` | helps |
| Placing content | `editor/placement` | helps |

## `animation/limits` — What Strata's animation does not do yet

**Covers.** The problem as a reader meets it: someone who comes from another engine looks for a blend tree, an IK
foot or a facial blend shape and does not find one. Each absence gets one paragraph, in the order of the pages that
would hold it: what Strata does not have, how engines usually do it (with a source in Further reading), and what
Strata offers instead. Blend trees and blend spaces, animation layers and masks (Strata offers cross-fades of up to
four entries); additive clips, sync markers and phase matching, float curves, inertialization and motion matching (the
robot's walk-to-run slide is the example); IK, and ragdolls, for which physics has no joints (`physics/why`); morph
targets (the importer reports them skipped, and the robot's faces are not imported); clip compression (Strata has
keyframe reduction and shared key times); retargeting beyond matching joint names; compute skinning and dual-quaternion
skinning (linear blend skinning runs per draw in the vertex shader); a skeleton overlay in the viewport (only the Asset
tab's joint tree shows joints). What the engine's documents plan is quoted only from the Roadmap's wave 9 entries
(`Docs/Roadmap.md:1645-1653`: `animation-tools`, `animation-runtime-2` and the ragdoll nodes), never from its tranche 2
line on `animation-graph` (`:1616-1620`), and never as a date or a promise; the writer runs each entry's evidence again
at the pin. The page's example is the design exercise E8: an Additive flag for states, its reference pose, and where it
would enter `Evaluate`; an editor task comes before it: the importer's report of the morph targets it skips. The page
links `appendix/not-in-strata`. At the end the reader knows where Strata's animation
stops and what a game or an engine change would have to add.

**Leaves out.**

- The general techniques behind every absence of the engine, indexed → `appendix/not-in-strata`
- Joints and ragdolls as a physics absence → `physics/why`
- Creating an animation controller without a command → `make/animation`

**Fit.** `fits`: about 2,150 words against S (1,500). The eight absences, one paragraph each, take the most; the two
exercises take about 500, and the estimate is 100 words below S's top.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `animation:52` | feature | home | No clip compression: raw float32 keys, reduction and shared times only |
| `animation:223` | feature | home | The list of what is not in Strata yet, and the Roadmap's wave 9 entries (`Docs/Roadmap.md:1645-1653`), quoted |
| `animation:505` | hands-on | home | E8 |
| `new:35` | hands-on | home | Editor task (done, track E), before E8: import a copy of the robot's model into the playground project, find in the **Console** the importer's warning "Not imported: morph targets" (the robot's faces), then find with a search the two lines that skip morph targets and their animation. Evidence: `Strata/src/Strata/Asset/GltfImporter.cpp:283-284` (each skipped feature becomes a warning "Not imported: ..."), `:1378-1379`, `:1637-1640`; `Strata/src/Strata/Asset/EditorAssetManager.cpp:2274-2275` (import warnings are logged); `Samples/ThirdPerson/Assets/Models/Robot/RobotExpressive.glb` (its meshes carry morph targets) |
| `animation:641` | open | home | No bounds overlay or skeleton gizmo in the viewport; the search, run again at the pin, is `new:12` |
| `animation:650` | open | home | The animation graph: no code at the pin; the page quotes only the Roadmap's wave 9 entries (`Docs/Roadmap.md:1645-1653`), never the tranche 2 line (`:1616-1620`), which names a stream that left wave 8 (animation-q6; R32, D43) |
| `new:9` | not-done | home | Blend trees, animation layers, IK, morph targets, clip compression. Evidence: `Strata/src/Strata/Asset/GltfImporter.cpp:1031` (weight channels skipped), `:1379` and `:1639` (morph targets reported skipped); `Docs/Roadmap.md:1649-1652` (Blend2D, IK and compressed clips listed for wave 9); `git grep -niE "blend ?(tree\|space\|1d\|2d)\|\bik\b\|inverse kinematic\|compress\|mask" 822a7a46 -- Strata/src/Strata/Animation` finds nothing; `git grep -niE "layer"` there finds only a comment on the Scene layer (`AnimationComponents.cpp:32`) |
| `new:10` | not-done | home | Additive clips, sync markers, float curves, inertialization, motion matching. Evidence: `Docs/Roadmap.md:1647-1651`; `git grep -niE "additive\|sync ?mark\|curve\|inertiali\|motion matching" 822a7a46 -- Strata/src/Strata/Animation` finds nothing |
| `new:11` | not-done | home | Retargeting beyond matching joint names. Evidence: `Strata/src/Strata/Animation/AnimationClip.h:38` ("clips bind to skeletons by name"); `Strata/src/Strata/Animation/AnimationClip.cpp:438-457` (`Bind` looks each target up by name); `git grep -niE "retarget" 822a7a46 -- Strata/src/Strata/Animation` finds nothing |
| `new:12` | not-done | home | A skeleton overlay in the viewport (`book.md`, "What Strata does not do"; the search run again at 822a7a46). Evidence: `git grep -nilE "joint" 822a7a46 -- StrataEditor/src Strata/src/Strata/Renderer Strata/shaders` finds the Asset tab's joint and channel views, the animation commands, the editor's bounds code, the `AttachToJoint` entity icon and the skinning code, and other words (`JoinTypeNames` in `StrataEditor/src/Editor/EditorUICommands.cpp`, "disjoint" in `Strata/src/Strata/Renderer/GlobalIlluminationLayout.h` and `.cpp`); nothing draws joints in a view |
| `new:13` | not-done | home | Compute skinning and dual-quaternion skinning: skinning runs per draw in the vertex shader. Evidence: `Docs/Roadmap.md:675`; `git grep -niE "dual[ -]?quat" 822a7a46 -- Strata/src Strata/shaders` finds nothing |
| `animation:569-570` | term | link | Sync markers and inertialization, defined on `animation/blending` |
| `animation:545` | term | link | Clip compression, defined on `animation/clips` |
| `animation:550` | term | link | Dual quaternion skinning, defined on `animation/skinning` |
| `animation:589` | term | link | Morph target, defined on `animation/problem` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The Animation system | `animation/system` | must |
| Cross-fades and blend weights | `animation/blending` | must |
| Linear blend skinning (the paragraph on compute and dual-quaternion skinning names it and links it) | `animation/skinning` | helps |
| Keyframe reduction and binding by name | `animation/clips` | must |
| Why games need physics (no joints) | `physics/why` | helps |
| Overlay passes and debug drawing | `gpu/debug-drawing` | helps |

## Passed on

| Item | Type | To | Why |
| --- | --- | --- | --- |
| `animation:152` | feature | `draw/skinned` | Change-driven palette updates are the render scene's work (`render-scene:160` is the same feature) |
| `animation:155` | feature | `draw/motion-vectors` | The previous palettes serve motion vectors and their history |
| `animation:157` | feature | `draw/skinned` | `HasSkinProxies` gates the renderer's skinning checks (`render-scene:163` is the same feature) |
| `animation:176` | feature | `scripting/host-api` | The 12 animator host functions are host functions (`scripting:78` lists them too) |
| `animation:177` | feature | `make/animation` | The SDK's `Animator` is taught where game makers drive animators, as the outline's row says; `reference/script-api` lists it |
| `animation:178` | feature | `scripting/script-system` | The callback flag, its thunk and the dispatch to the scripts of the animator's entity are the script system's; `animation/system` links it |
| `animation:179` | feature | `scripting/host-api` | `HostCall`, `ResolveContext` and `ReportProblem` are the host API's pattern |
| `animation:190` | feature | `make/commands` | The preview chip names the pose that `animation.preview` shows, and that command is run where game makers learn to call commands (R31, D40) |
| `animation:191-192` | feature | `make/animation` | The Asset tab's tables and the Inspector's live state are the how-to half the outline gives `make/animation` |
| `animation:254` | concept | `basics/math-rotations` | Why quaternions, the double cover and normalization are mathematics (the outline names this inventory's chapter 2 as that primer's source); Strata's `Normalize` and `Slerp` stay on `animation/skeletons` and `animation/clips` |
| `animation:280` | concept | `draw/skinned` | `book.md` makes `draw/skinned` the home of posed bounds |
| `animation:360` | code | `nowhere` | Repeats the scene vertex shader's lines 35-60 (`Mesh.vert.slang`), which `gpu/geometry-pool` quotes as `render-core:463` (the merge "Scene vertex shader excerpt" of `duplicates.md`); `draw/mirrors-camera-relative` quotes lines 50-56 and 76-81 of the same shader (`render-scene:370`). `animation/skinning` links the excerpt where it shows where `BlendJoints` is called |
| `animation:363` | code | `make/animation` | The game's side (setting parameters, footsteps on events) is taught where game makers write it; hands-on G3 copies `Footsteps.cpp` |
| `animation:422` | figure | `draw/skinned` | A limb outside its bind bounds, drawn and shadowed, illustrates posed bounds (`render-scene:444` is a similar picture) |
| `animation:458` | rule | `draw/skinned` | The prepass and the forward pass agree through the `ST_SKINNED` variants, which `draw/skinned` owns (`render-scene:479`) |
| `animation:460` | rule | `draw/skinned` | Unskinned scenes pay nothing (`render-scene:493` is the same rule) |
| `animation:483` | rule | `scripting/host-api` | Appending host functions, never inserting them, is the ABI's rule |
| `animation:508` | hands-on | `scripting/tutorial-host-function` | E11 needs a host function, the SDK and a `Scripting.*` test, which part 15 teaches after this part |
| `animation:514-519`, `animation:521` | hands-on | `make/animation` | G1 to G6 and G8 are the game maker's tasks: import, controller, events, any-state jump, sockets, root motion, editing the robot |
| `animation:520` | hands-on | `make/performance` | G7, 500 characters measured with each culling mode, is done where the frame time is read (R31, D40) |
| `animation:535` | term | `basics/math-matrices` | The glossary seed gives TRS its home there |
| `animation:536-537` | term | `basics/math-rotations` | The seed gives quaternion and slerp their home there; nlerp belongs beside slerp |
| `animation:541` | term | `basics/math-interpolation` | The seed gives keyframe its home there |
| `animation:554` | term | `draw/skinned` | Home of posed bounds |
| `animation:574` | term | `basics/math-rotations` | The seed gives yaw its home there |
| `animation:584` | term | `world/systems` | `book.md` makes `world/systems` the home of scene services |
| `animation:586` | term | `assets/handles-meta` | `book.md` makes `assets/handles-meta` the home of sub-assets |
| `animation:631` | open | `nowhere` | A note on files the survey did not read line by line; the writer of `animation/state-machines` reads the JSON reader and writer (`AnimationController.cpp` 248-553), as its row of `animation:365` says |
| `animation:647` | open | `nowhere` | A note that the survey did not read the GPU-driven path of skinned proxies; `render-scene:126` and `render-scene:162` hold it |
| `animation:649` | open | `nowhere` | A note on files the survey did not open; the allocator opened the fox prefab (AlwaysAnimate), recorded in the row of `animation:427` on `animation/culling` |

## Not taken

none

## Questions for the planner

none
