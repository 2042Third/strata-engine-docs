# Brief: `animation/culling`

| Field | Value |
| --- | --- |
| Title | Animating only what is seen |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `animation/system`, `animation/skinning`, `draw/bounds-culling`, `draw/gpu-driven` |
| From | animation ch. 12; 1.8 (`WhenVisible`, reach, the renderer's visibility report, stale poses, paused frames) |
| Unit | `plan/allocation/animation.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `culling-mode` | Culling mode | WhenVisible animator |
| `reach` | Reach | - |
| `stale-pose` | Stale pose | - |
