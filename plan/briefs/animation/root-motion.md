# Brief: `animation/root-motion`

| Field | Value |
| --- | --- |
| Title | Root motion |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `animation/time-events`, `physics/character-controllers`, `animation/blending` |
| From | animation ch. 10; 1.7 (extraction, holding the root, applying it, the character controller's hook) |
| Unit | `plan/allocation/animation.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `in-place-animation` | In-place animation | - |
| `root-motion` | Root motion | - |
| `root-motion-joint` | Root motion joint | - |
