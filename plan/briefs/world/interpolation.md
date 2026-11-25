# Brief: `world/interpolation`

| Field | Value |
| --- | --- |
| Title | Drawing between fixed steps |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `world/scene-graph`, `world/systems`, `basics/math-interpolation` |
| From | scene-ecs "Interpolating fixed steps"; physics "Interpolating fixed steps"; M→L; home of interpolation (`core/time` names it in one paragraph); + what it does not do yet (`Docs/Roadmap.md`, "Interpolation, the rest") |
| Unit | `plan/allocation/world.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `world/interpolation` — Drawing between fixed steps

**Covers.** The job: draw fixed-step motion between its last two poses, so that it does not judder when the frame rate
is above the step rate, while the simulation never reads what is drawn. This page carries the full section on the
problem: judder shown as numbers (a body stepped at 60 Hz and drawn at 144 Hz), the approaches (interpolate with one step
of latency, extrapolate and overshoot, a variable step and its lost determinism) and a table of their costs; `core/time`'s
paragraph is linked. The map: the interpolated set beside the world transforms; the fixed steps write it, the render
scene reads it. Then, in this order:

1. The switch: `SetInterpolation`, and `IsInterpolating` as the switch and the project's `Scene.Timing.Interpolation`
   and a running scene.
2. The set: parallel arrays by slot (entities, entries, drawn matrices) with a slot map by entity index; the roles
   Blend, Compose and Exact.
3. The capture after the steps: `UpdateWorldTransforms` in its capture pass records every matrix it overwrites, and the
   set is rebuilt in four phases.
4. The step alpha: the drawn time `T + a - h` and the formula `1 - (1 - a/h)/n`, from a timeline.
5. Writes to members of the set outside the steps, and the per-frame rules.
6. The pose blend: lerp of translation and scale, a normalized lerp of the quaternion on the shorter arc, and why not
   `glm::mix` or slerp.
7. Drawn matrices: computed lazily when the render scene syncs; `FindDrawnTransform`, `GetDrawnTransform` (exact at any
   time) and the drawn version.
8. Breaks and clears: teleports (`BreakInterpolation`); pause, a step, a changed step, the project turning it off,
   start and stop; the safety net at 400 m/s (box3d's top speed) that makes an entry Exact; stats and validation.
9. The rules for renderer code (draw drawn transforms, never simulate with them) and for game code (follow moving bodies
   with their drawn positions in `OnLateUpdate`, because a camera that follows the world position makes the body judder
   against it above the step rate; move carriers in fixed steps).
10. What it does not do yet: drawn poses for world-space game UI, gizmos and picking, reflection probes, fog,
    post-process volumes, the sky and the sun; attachments placed outside their animator's hierarchy following its
    drawn pose; a cap on interpolated bodies (the Roadmap's "Interpolation, the rest").

The figure of interpolation off and on (a body's drawn screen position per frame, from a sample at a high frame rate),
the tests (`Scene.Timing` and its sweep, and the capture's cost, `Perf.Scene.InterpolatedStepFrame100k.Ratio` at 2.1
against its 1.5 target, a movable claim: `Docs/Roadmap.md:1702`, `StrataTests/Perf/Budgets.json:270`), changing it
safely, and the exercises: the Spinner of `world/systems` drawn
smoothly, its entities reported as Blend and a child light as Compose; and the "trace it yourself" exercise, which
follows the child light's drawn matrix from `RenderScene::Sync` through `UpdateDrawnTransforms` and
`FindDrawnTransform` to the Compose case of `ComputeDrawnTransform`. At the end the reader can explain the drawn time
and the three roles, and write renderer or game code that reads the right transform.

**Leaves out.**

- The fixed step and the accumulator → `core/time`
- The runtime frame that captures and computes the alpha → `world/systems`
- Lerp and smoothing as mathematics → `basics/math-interpolation`
- Interpolating rotations as mathematics → `basics/math-rotations`
- How the render scene reads drawn transforms → `draw/render-scene`
- Following a body with a camera in a game → `make/characters-cameras`
- Teleporting physics bodies → `physics/world-step`
- The project's switch as a settings section → `world/projects-settings`

**Fit.** `fits`: about 5,900 words against L (5,000). Four excerpts and the lines of `OnUpdateRuntime` that compute the
alpha, the problem section with its table and two exercises take most of it; phase B reads the page again at the move
to v0.8.0 (`process.md`, step 11), because interpolation is new in 0.8.0.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scene-ecs:130-139` | feature | home | The switch, the set and its roles, the capture pass, the step alpha, per-frame writes, the pose blend, drawn matrices, breaks and clears, the safety net, stats and validation |
| `scene-ecs:357` | concept | home | Why motion judders; interpolate, extrapolate or vary the step; Strata's state interpolation of only what the steps moved; drawn transforms apart from simulated ones; the mistakes |
| `scene-ecs:390` | code | home | `Strata/src/Strata/Scene/SceneInterpolation.cpp:104-116`: `BlendPose`, lerp and nlerp on the shorter arc, why not `glm::mix` or slerp |
| `scene-ecs:391` | code | home | `Strata/src/Strata/Scene/SceneInterpolation.cpp:240-374`: `CaptureInterpolation`, the set built from the capture pass: roles, exits, parent slots, breaks |
| `new:2` | code | home | `Strata/src/Strata/Scene/TransformInterpolation.h:15-38`: the roles and an entry of the set, with each role's rule in its comment |
| `new:3` | code | home | `Strata/src/Strata/Scene/SceneInterpolation.cpp:410-525`: `UpdateDrawnTransforms`, `FindDrawnTransform`, `GetDrawnTransform` and `ComputeDrawnTransform`: drawn matrices made lazily and exact at any time |
| `scene-ecs:388` | code | use | Lines 2313-2321 of `OnUpdateRuntime`: the step alpha computed after the capture |
| `scene-ecs:442`, `scene-ecs:489` | figure | home | The timeline of poses, drawn time and alpha with a body (Blend), its child light (Compose) and a teleported crate (Exact); interpolation off against on as a plotted trace or a strip of frames |
| `scene-ecs:543`, `scene-ecs:546` | rule | home | Renderers draw drawn transforms, simulation never reads them, teleports break; follow moving bodies in `OnLateUpdate` with drawn positions, move carriers in fixed steps |
| `scene-ecs:582` | hands-on | home | The Spinner drawn smoothly: Blend and Compose in `GetInterpolationStats` |
| `new:19` | hands-on | home | The "trace it yourself" exercise (D27): the Spinner's child light followed with a debugger from `RenderScene::Sync`, which makes the drawn matrices first, through the proxy's `FindDrawnTransform` to `ComputeDrawnTransform`, where a Compose entry is its parent's drawn matrix times its own local transform (about 250 words). Evidence: `Strata/src/Strata/Renderer/RenderScene.cpp:316-321`, `:425`; `Strata/src/Strata/Scene/SceneInterpolation.cpp:410`, `:457-463`, `:479-495` |
| `scene-ecs:679-683` | term | home | State interpolation (the qualified entry, against the mathematical interpolation of the seed), step alpha, Blend, Compose and Exact, drawn transform, teleport and break |
| `scene-ecs:684` | term | link | nlerp, used by the pose blend of section 6; taught in `basics/math-rotations` |
| `scene-ecs:759` | open | home | The sample of the off-and-on figure is chosen when its recipe is written (`Samples/ThirdPerson` or `Samples/PhysicsPlayground`; the survey ran nothing) |
| `new:4` | not-done | home | Drawn poses for world-space game UI, editor gizmos and picking, reflection probes, fog and post-process volumes, the sky and the sun; attachments placed outside their animator's hierarchy do not follow its drawn pose; there is no cap on interpolated bodies. Evidence: `Docs/Roadmap.md:1698-1702` |
| `scene-ecs:222` | feature | link | `Scene.Timing`'s `Interpolation` field, taught as a section in `world/projects-settings` |
| `foundation:188` | feature | home | Interpolation as the foundation survey lists it (drawn transforms between the last two step poses, `m_StepAlpha`): the same mechanism as `scene-ecs:130-139`, taught once |
| `scripting:341` | concept | home | The scripting survey's concept: why a follow camera reads the drawn pose in `OnLateUpdate` (`Docs/Manual/Scripting.md:157-175`), taught once in section 9's rule for game code; `make/characters-cameras` uses it |
| `foundation:576`, `scripting:579` | term | home | The foundation survey's entry for interpolation (render) and the scripting survey's for drawn transform: one glossary entry each with `scene-ecs:679` and `scene-ecs:682` |
| `physics:159-161` | feature | home | The physics survey's rows on the same mechanism: the roles, the alpha and breaks; the readers (`GetStepAlpha`, `GetDrawnTransform`, `FindDrawnTransform`, `BreakInterpolation`, `c_MaxInterpolatedSpeed`); and the script SDK's side, named in the rule for game code (`GetDrawnPosition` and `GetDrawnRotation`, `ResetInterpolation`, `Time::GetStepAlpha`; their use home is `make/characters-cameras`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Lerp, its weight, and blending two values | `basics/math-interpolation` | must |
| Quaternions, slerp and the shorter arc | `basics/math-rotations` | must |
| The fixed step, and interpolation in one paragraph (one step of latency) | `core/time` | must |
| The runtime frame, `OnFixedUpdate` and `OnLateUpdate` | `world/systems` | must |
| World transforms, the dirty walk and its passes | `world/scene-graph` | must |
| Floating-point spacing far from the origin | `basics/numbers` | helps |
| The render scene and its sync | `draw/render-scene` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `blend` | Blend | - |
| `drawn-transform` | drawn transform | - |
| `interpolation` | interpolation | state interpolation, Interpolation (render) |
| `step-alpha` | step alpha | - |
| `teleport` | Teleport | - |
