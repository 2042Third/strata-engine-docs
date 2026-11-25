# Brief: `animation/skeletons`

| Field | Value |
| --- | --- |
| Title | Skeletons and forward kinematics |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `basics/math-rotations`, `assets/importing` |
| From | animation ch. 3; 1.2, 1.3 (the skeleton asset) |
| Unit | `plan/allocation/animation.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `forward-kinematics` | Forward kinematics | FK |
| `joint-bone` | Joint (bone) | - |
| `local` | Local | - |
| `model-space-of-a-pose` | model space (of a pose) | - |
| `rest-pose` | Rest pose | - |
| `skeleton-rig` | Skeleton (rig) | - |
| `stsk` | STSK | STAC |
| `topological-order-parents-first` | Topological order (parents first) | - |
