# Brief: `animation/system`

| Field | Value |
| --- | --- |
| Title | The Animation system |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `animation/blending`, `animation/root-motion`, `world/systems`, `core/jobs`, `assets/residency` |
| From | animation ch. 11; 1.8, 1.9 (records, asset sets, job phases, the ordered publish, attachments, events, the scene services `ISkinningPoses`, `IAnimatorControl`, `IAnimationEventSource`) |
| Unit | `plan/allocation/animation.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `iskinningposes` | `ISkinningPoses` | - |
| `animator-record` | animator record | - |
| `asset-set` | Asset set | - |
| `attachment-socket` | Attachment (socket) | - |
| `provider-of-poses` | Provider (of poses) | - |
