# Brief: `animation/problem`

| Field | Value |
| --- | --- |
| Title | The animation problem |
| Kind | C |
| Size | S |
| Tracks | E |
| Needs | `world/scene-graph` |
| From | animation ch. 1 (rigid, vertex, morph and skeletal animation; what Strata chose; the Third-Person sample's robot as the running example) |
| Unit | `plan/allocation/animation.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `morph-target-blend-shape` | Morph target (blend shape) | - |
