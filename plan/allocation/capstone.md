# Allocation: capstone

## `capstone/plan` — Capstone I: designing a feature the way Strata does

**Covers.** What the reader makes: a written design (a spec) for the WindZone as a finished feature, in the shape the
engine's own specs take, and a map of where each of its parts lives. The spec is the page's one lasting change: its
patch adds it to the engine's tree, a document under `Docs/Plans/` in the form of `Docs/Plans/Wave8/specs/`
(`pipelines.md` §6.6). The WindZone so far, the chain of patches in one line: the component and its system
(`world/tutorial-component`), its gizmo, a sphere of its radius (the solution of `gpu/debug-drawing`'s exercise), the
wind's scene service, `Wind::GetStrength` and a callback (`scripting/tutorial-host-function`), `wind.list`, `wind.set`
and the `wind.` prefix in the MCP toolset table (`editor/tutorial-command`). The page decides what the finished feature
does: a Directional zone has no radius and pushes every dynamic body along the zone entity's local -Z, Strata's forward,
as a directional light shines along its entity's -Z, so turning the entity turns the wind; a Spherical zone pushes the
bodies inside its Radius away from its centre; Strength is in newtons. The step sections, in teaching order:

1. Who meets the feature and what "done" means: the game maker (Add Component, the Inspector, a gizmo in the Scene view,
   the wind in Play and Simulate), the script (the wind at a point), the agent (a command that reads the wind without
   playing), the test suite (unit tests, the feature test, a perf metric). Written as the spec's goal and acceptance.
2. Each part's layer: the rows of `StrataTests/Architecture/Layers.json` read for Physics, Scripting and the Renderer;
   the WindZone's code in Physics may include Core, Asset, Reflection and Scene; scripts reach it only through a scene
   service whose interface is in the Scene layer; the Renderer never names it, so its gizmo goes through
   `ComponentInfoBuilder::Gizmo`; the commands are editor code, outside the table, and games link no tooling. Physics
   is an optional module (`STRATA_WITH_PHYSICS`), and CI builds the engine without it, so nothing outside the module may
   name the WindZone, and `#if ST_WITH_PHYSICS` stands only where the rule allows it (the composition root, the asset
   pipeline, the runtime and tests). The experiment: include `Strata/Physics/PhysicsComponents.h` from a file of the
   Scripting layer, run `Architecture.Layering`, read the failure, and take the include back. The tutorial file holds
   it as `patch.experiment`, a run that expects failure: the runner applies it, keeps the failing output of
   `Architecture.Layering` for the page's text capture and takes it back (`pipelines.md` §6.6). The figure places every
   part.
3. The registries it joins, found with the searches of `core/reading-code`: from the composition root
   (`Engine::RegisterBuiltinModules` calls `RegisterPhysicsModule`) to the component registry (properties, a gizmo
   function, an inactive reason), the scene system registry (soft order before Physics, Simulate mode, a profile
   stage), the scene services the system uses and offers (services exist only while a scene runs), the host function
   table and the SDK, the editor's command groups and the MCP toolset table, the feature test's coverage, the component
   schema snapshot and the perf budget file. For each: its layer, when it is open and when it freezes, and the check
   that fails when the feature forgets it. The page names all seven services `PhysicsSystem` offers (an erratum).
4. The rules that apply, as a table with one line per rule: the rule, where it bites in the WindZone, and what enforces
   it. Each rule links its home.
5. The decisions, each with what it costs: one function gives the wind at a point and is shared by the system, the
   script API and the command (the command runs while editing, when no service exists); which bodies a zone visits
   (`OverlapSphere` for a Spherical zone, the dynamic bodies for a Directional one); a force wakes its body, so a zone
   keeps what it pushes awake, and a zone of Strength 0 pushes nothing; the gizmo has four shape kinds and one group, so
   a Directional zone's arrow needs a new shape kind in Reflection that the Renderer draws; Radius does nothing in
   Directional mode, so it gets an inactive reason; the order of zones and bodies is fixed, so runs repeat.
6. The spec written down: the sections of the engine's specs (the goal in priority order, where we start, decisions,
   steps, tests with must-fail checks, acceptance, perf, docs, risks, the order of delivery), filled for the WindZone,
   whose steps `capstone/build` and `capstone/land` carry out; the page's patch adds it under `Docs/Plans/`.

Exercises: trace one click in the Scene view to a pixel with the method of `core/reading-code` (the worked solution
names each file and function on the path); a design question: where would the wind's sound be played, when Audio may
not include Physics? At the end the reader can place a new feature's parts in Strata's layers, list the registries and
rules it meets, and write its spec before writing its code.

**Leaves out.**

- The forces, the gizmo, the inactive reason, the script API and the command, written → `capstone/build`
- The tests, the feature test, the perf metric, the review and CI → `capstone/land`
- The layer table's rules and the composition root's code → `core/layers-registries`
- How scene services are registered and found → `world/systems`
- Picking: the asynchronous readback of the entity-ID buffer → `editor-ui/scene-view`
- The method of reading a large codebase → `core/reading-code`
- The checklist and the way a change lands → `engineering/contributing`

**Fit.** `fits`: about 4,800 words against L (5,000). Six step sections of two to four short steps (sixteen) with text
captures, four excerpts, two figures, the rules as one-line rows that link their homes, and two exercises; written for
E1 at the end of track E, so the steps take the guide's lower values. The registries of section 3 and the decisions of
section 5, with their excerpts, take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:1` | concept | home | How Strata designs a feature before writing it: a spec whose sections come in a fixed order (the goal in priority order, where we start, decisions that hold for every step, the steps, tests with must-fail checks, acceptance numbers, perf metrics and targets, docs, risks and open questions, the order of delivery); the page's patch adds the WindZone's spec in this form under `Docs/Plans/` (`pipelines.md` §6.6). Evidence: `Docs/Plans/Wave8/specs/physics-timing.md:35`, `:62`, `:214`, `:257`, `:811`, `:874`, `:887`, `:944`, `:1034`, `:1090` (the section headings) |
| `new:2` | code | home | `StrataTests/Architecture/Layers.json:49-79`: the rows of Physics, Audio, Animation, GameUI and Scripting, what each layer may include; read to place each part of the WindZone |
| `new:3` | code | home | `Strata/src/Strata/Reflection/ComponentGizmo.h:13-44`: the four shapes (box, sphere, capsule, mesh bounds) and the one group a module can ask for; why a Directional zone's arrow needs a new shape kind |
| `new:4` | code | home | `Strata/src/Strata/Physics/PhysicsWorld.cpp:5156-5167`: `AddPendingForce` queues a force for the next step and wakes the body, so a zone keeps the bodies it pushes awake |
| `new:5` | code | home | `Strata/src/Strata/Scene/SceneServices.h:19-33`: services exist from the first `OnRuntimeStart` to the last `OnRuntimeStop`, so a command that reads the wind while editing calls the Physics module's function, not a service |
| `new:6` | erratum | home | The comment at `SceneServices.h:28-29` names six services that `PhysicsSystem` offers; the system registers seven, `IPhysicsDiagnostics` too. The page names seven (process.md's table of errata, kind `engine`). Evidence: `Strata/src/Strata/Scene/SceneServices.h:28-29`; `Strata/src/Strata/Physics/PhysicsSystem.cpp:61-67`; `Strata/src/Strata/Physics/PhysicsSystem.h:54-55` |
| `new:7` | figure | home | The WindZone's parts on the layer diagram: the component, system and force function in Physics; the wind service's interface in Scene; the arrow shape kind in Reflection, drawn by the Renderer; the host function in Scripting; the SDK in StrataScriptCore; the commands in the editor's core. Evidence: `StrataTests/Architecture/Layers.json:5-124` |
| `new:8` | hands-on | home | Exercise (trace it yourself): one click in the Scene view followed to a pixel: `ViewportPanel` calls `EditorViewport::RequestPick`, the entity-ID readback finishes in `UpdatePicking`, `ApplyPick` changes the selection, the viewport renderer hands the selection to the scene renderer, and the outline overlay colors the pixels around the silhouette. Evidence: `StrataEditor/src/Panels/ViewportPanel.cpp:245-263`; `StrataEditor/src/Editor/EditorViewport.cpp:415-456`; `StrataEditor/src/Editor/ViewportRenderer.cpp:240`; `Strata/src/Strata/Renderer/SceneRenderer.h:466-471`; `Strata/shaders/Overlay/Outline.frag.slang:5-8` |
| `new:9` | hands-on | home | Exercise (design): where the wind's sound would be played. Audio may include Core, App, Asset, Reflection and Scene but not Physics, so the sound needs a service or data in the Scene layer. Evidence: `StrataTests/Architecture/Layers.json:55-61` |
| `scene-ecs:580` | hands-on | link | The tutorial that made the component and its system |
| `scripting:534`, `scripting:538` | hands-on | link | The tutorial that added `Wind::GetStrength` and the callback |
| `editor-core:625` | hands-on | link | The tutorial that added `wind.list` and `wind.set` |
| `foundation:33`, `foundation:37` | feature | use | The composition root and its registration state machine: where `RegisterPhysicsModule` is called and when the registries freeze |
| `foundation:173`, `foundation:175` | feature | use | The layer table and the `Architecture.Layering` test that the experiment fails |
| `foundation:36` | feature | use | Physics as an optional module: a build without it must still compile |
| `foundation:468` | rule | use | `#if ST_WITH_<MODULE>` only in the composition root, the asset pipeline, the runtime and tests |
| `foundation:259`, `foundation:264` | concept | use | Dependency inversion and registries: why the Renderer can draw the WindZone's gizmo without naming it |
| `foundation:465` | rule | use | Registration only through the composition root: a row of the rules table |
| `foundation:487` | rule | use | A profile stage around a unit of frame work: the system's stage, a row of the rules table |
| `foundation:526` | hands-on | use | Breaking the layering on purpose, done here with a Physics header in a Scripting file: the tutorial file's `patch.experiment`, a run that expects failure |
| `scene-ecs:196`, `scene-ecs:197` | feature | use | The component registry's lifecycle and builder, which the WindZone's registration extends |
| `scene-ecs:198` | feature | link | `SetInactiveReason`, named as the registry the inactive reason joins |
| `scene-ecs:203` | feature | use | The gizmo shapes a component asks for |
| `scene-ecs:101-104` | feature | use | Simulate mode, the descriptor with soft constraints, `MakeSceneSystemDescriptor` and the system registry |
| `scene-ecs:118` | feature | use | Scene services: the system uses `IBodyControl` and `IPhysicsQueries` and offers the wind service |
| `scene-ecs:326` | concept | use | Decoupling modules through services and layers |
| `scene-ecs:501` | rule | use | The transform contract: the WindZone writes no transform; physics moves the bodies |
| `scene-ecs:520`, `scene-ecs:522`, `scene-ecs:524`, `scene-ecs:526` | rule | use | Rows of the rules table: the module's header, registration while the root runs, names never renamed, ranges that forbid bad states |
| `scene-ecs:531`, `scene-ecs:533`, `scene-ecs:535`, `scene-ecs:537` | rule | use | Rows of the rules table: the inactive reason, soft order toward Physics, descriptors made by the helper, modules meeting through services |
| `physics:93` | feature | use | Forces act during the next step only, so the system pushes in every fixed step |
| `physics:114` | feature | use | `OverlapSphere`, the query a Spherical zone uses |
| `physics:255` | concept | use | Sleeping and islands: what a force that wakes its body costs |
| `physics:394` | rule | use | Forces in `OnFixedUpdate`, every step they should act |
| `physics:34` | feature | use | The collider gizmos, whose group the WindZone's gizmo joins |
| `render-core:222` | feature | use | `DrawSceneGizmos` draws every component that registered a gizmo |
| `render-core:616` | rule | use | The renderer reaches higher modules only through registries |
| `scripting:200`, `scripting:201` | feature | use | The scene services the host API goes through, and the Scripting layer's includes |
| `scripting:450`, `scripting:459` | rule | use | Host functions are appended and wrapped in `HostCall`: rows of the rules table |
| `scripting:496` | rule | use | Every new host function and SDK name is exercised by the feature test |
| `editor-core:54`, `editor-core:60` | feature | use | A command's metadata, and its kind as a tested decision |
| `editor-core:546`, `editor-core:558` | rule | use | Commands refuse bad input without side effects and declare their kind |
| `automation:613` | rule | use | Commands are the API: the command reaches agents with no RPC code |
| `automation:211` | feature | use | MCP toolsets: the table a new command group must find a place in |
| `build-test:156` | feature | use | What the feature test counts, for the spec's test section |
| `build-test:494` | rule | use | Never widen `MayInclude`: invert the dependency |
| `build-test:523` | rule | use | Perf limits live in `Budgets.json` and only go down: the spec's perf section |
| `build-test:247` | feature | use | The pre-commit checklist the spec plans for |
| `editor-ui:201` | feature | use | Picking on the trace's path |
| `render-core:165` | feature | use | The entity-ID prepass the pick reads |
| `render-core:201` | feature | use | `TextureReadback`, polled until the pick's pixel arrives |
| `render-core:220` | feature | use | The overlay set and its selection outline, the end of the trace |
| `editor-core:44` | feature | use | The editor's selection, which the pick changes |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The WindZone component and its system | `world/tutorial-component` | must |
| `Wind::GetStrength`, the wind's scene service and the appended callback | `scripting/tutorial-host-function` | must |
| The `wind.list` and `wind.set` commands | `editor/tutorial-command` | must |
| The method: searches, go to definition, the tests as descriptions | `core/reading-code` | must |
| The layer table, optional modules (`ST_WITH_*`) and "no tooling in games" | `core/layers-registries` | must |
| The composition root and registries that open, accept and freeze | `core/layers-registries` | must |
| Reflection: one registration, `ComponentInfoBuilder` | `world/reflection` | must |
| Scene systems, soft constraints and scene services | `world/systems` | must |
| The transform contract and change signals | `world/scene-graph` | must |
| Forces and impulses in one fixed step | `physics/world-step` | must |
| Physics queries: overlaps | `physics/queries` | must |
| Sleeping and islands | `physics/dynamics` | helps |
| Gizmos through `ComponentInfoBuilder::Gizmo` and `DrawSceneGizmos` | `gpu/debug-drawing` | must |
| Inactive reasons in the Inspector | `editor-ui/inspectors` | must |
| The host API: `HostCall`, `ResolveContext`, the X-macro table | `scripting/host-api` | must |
| Commands are the API: three clients, one registry | `editor/commands` | must |
| The MCP server and its toolsets | `automation/mcp` | helps |
| The feature test's coverage | `engineering/feature-test` | must |
| Perf budgets and the reference machine | `engineering/perf-lab` | must |
| The review checklist and the way a change lands | `engineering/contributing` | must |
| The coordinate conventions: -Z forward | `gpu/coordinates` | must |
| Parallel work is deterministic | `core/jobs` | helps |
| Picking and gizmos in the Scene view | `editor-ui/scene-view` | helps |
| Readback without stalls | `gpu/readback-timing` | helps |
| The overlay order and the selection outline | `gpu/debug-drawing` | helps |
| The terminal | `basics/tools` | must |
| git | `basics/git` | must |

**Starting state.** The end state of `editor/tutorial-command`: the source build of `core/first-change` at the pin with
the WindZone chain's patches applied in its one line, `world/tutorial-component`, the solution patch of
`gpu/debug-drawing`'s exercise, `scripting/tutorial-host-function` and `editor/tutorial-command` (`pipelines.md` §6.6),
configured and built in Debug. The tutorial file starts from `editor/tutorial-command` (`startsFrom` names that page).
For the trace exercise, a project made from the Basic 3D template as `start/first-game` made it, opened in the editor of
that build. The page's patch adds only the spec under `Docs/Plans/`; the layering experiment is the tutorial file's
`patch.experiment`, taken back before the page's checkpoint.

**Command-only steps.** none

## `capstone/build` — Capstone II: from component to pixel

**Covers.** What the reader makes: the one change that turns the WindZone into a feature. Wind pushes bodies in Play and
Simulate, the Scene view shows every zone, the Inspector says why Radius does nothing in a Directional zone, scripts read
the wind at a point, and agents ask for it with a command. Each step section is a stage of the page's patch and ends with
a checkpoint and its build or test output as a text capture; engine code that the reader's change follows is quoted
beside it. The sections, in teaching order:

1. The wind at a point, written once: a function of the Physics module that gives the force a zone applies at a
   position (Directional: Strength along the zone entity's local -Z, Strata's forward, turned by its world rotation, so
   turning the entity turns the wind; Spherical: Strength away
   from the centre inside Radius, nothing at the centre itself and nothing outside), and its sum over a scene's active
   zones; a degenerate transform or a non-finite position gives no force.
2. Forces on bodies: `WindZoneSystem::OnFixedUpdate` takes `IPhysicsQueries` and `IBodyControl` from the scene (null
   without a physics world: nothing to push); a Spherical zone asks `OverlapSphere` for the bodies inside it (in a
   deterministic order, triggers left out), a Directional zone visits the dynamic bodies; each gets `AddForce`, in every
   fixed step, because a force acts during the next step only; the soft order before Physics from
   `world/tutorial-component` keeps the forces in the step they belong to, and the system runs in Simulate mode too
   (`RunsInSimulateMode`), since wind is physics; a zone of Strength 0 is skipped, since a force wakes its body; the
   descriptor gets its profile stage. The system still writes no transform: physics moves the bodies and writes them
   back.
3. The arrow: the WindZone's gizmo is already in the chain, a sphere of its radius in the collider group, from the
   solution of `gpu/debug-drawing`'s exercise; this section adds only what a Directional zone needs. An `Arrow` kind
   joins `ComponentGizmoShape` in Reflection, `DrawShape` in the Renderer draws it with `DebugDraw::Arrow`, and the
   gizmo function fills it for a Directional zone, along the zone's -Z. The lower layers learn a shape, never the
   WindZone. A whole-editor picture shows both zones.
4. The inactive reason: after the registration, `SetInactiveReason<WindZoneComponent>("Radius", ...)` returns
   "Directional zones have no radius" for a Directional zone, as the engine's own checklist writes it; the Inspector
   draws Radius disabled with the reason as its tooltip, and `component.get` lists it under `inactive`. A picture of the
   Inspector.
5. The script API: the wind service of `scripting/tutorial-host-function` gains the force at a point; a host function
   appended after the one behind `Wind::GetStrength`, with `HostCall`, `ResolveContext` and `ReportProblem` for a
   non-finite position and a zero vector as its failure value; the SDK's `Wind::GetForceAt` with
   `ST_SCRIPT_DETAIL_HOST_WITH` and its fallback; one call from a feature script, so that the feature test of the patch
   runner passes.
6. The command: `wind.sample {position}`, a Query beside `wind.list`, which calls the function of section 1 directly, so
   that it answers while editing too, when no service exists; its schema, a description written for agents, its kind in
   the kind lists, and a run from the terminal.
7. From component to pixel: in the editor built from the patch, the checkpoint scene's crates drift in Play. Then one
   Strength edit is followed to the pixels: the Inspector's `SetPropertyWithUndo`, `ComponentAccess` and its signal, the
   system's next fixed step, `AddForce`, `Simulate`, the write-back with `MarkTransformsChanged`, the transform cache,
   the render scene's sync and the drawn transform, the frame. The gizmo's path is followed too: the registry,
   `DrawSceneGizmos`, `DebugDraw`, the overlays. A diagram draws both paths.

The patch is not yet a commit: it lands in `capstone/land`, with its tests. Exercises: a Falloff for Spherical zones,
with its own inactive reason in Directional mode; a gusting wind whose strength changes over fixed steps, never over
frames. At the end the reader has carried one feature through Physics, Scene, Reflection, the Renderer, Scripting, the
SDK and the editor, each through its own extension point.

**Leaves out.**

- The design and its reasons → `capstone/plan`
- Unit tests, the feature test's checks, the perf metric, the review and CI → `capstone/land`
- How one fixed step syncs, steps and writes back → `physics/world-step`
- `DebugDraw`, the overlay order and `DrawSceneGizmos` → `gpu/debug-drawing`
- How the Inspector draws rows from reflection → `editor-ui/inspectors`
- Appending a host function, step by step → `scripting/tutorial-host-function`
- Adding a command, step by step → `editor/tutorial-command`
- How the render scene follows the scene → `draw/render-scene`

**Fit.** `fits`: about 6,050 words against L (5,000). Seven step sections with fourteen steps and seven quoted hunks of
the patch, five quoted engine excerpts, four figures and two exercises, at the guide's lower values for E1; the forces
of section 2 and the two paths of section 7, from a Strength edit and from the gizmo's registration to the pixels, take
the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:10` | code | home | `Strata/src/Strata/Scene/SceneServices.h:135-157`: `IBodyControl`: forces act on dynamic bodies only, during the next step only, and are refused when not finite |
| `new:11` | code | home | `Strata/src/Strata/Scene/SceneServices.h:172-190`: `IPhysicsQueries`: overlaps in a deterministic order, triggers skipped unless asked for |
| `new:13` | code | home | `Strata/src/Strata/Renderer/SceneGizmos.cpp:120-157`: `DrawShape`, where the new arrow kind is drawn beside the four others |
| `new:14` | code | home | `Strata/src/Strata/Animation/AnimationComponents.cpp:17-45`: a reason function and `SetInactiveReason` called after the registration, the pattern of the WindZone's |
| `new:15` | code | home | `.claude/skills/strata-add-component/SKILL.md:69-73`: the engine's own checklist gives the WindZone's Radius exactly this inactive reason |
| `new:16` | figure | home | What you will make: crates pushed by a Directional zone and scattered by a Spherical one, with the zones' gizmos. Evidence: `Strata/src/Strata/Renderer/SceneGizmos.h:57-66` |
| `new:17` | figure | home | The Scene view with a Spherical zone's sphere and a Directional zone's arrow, drawn with the colliders in their color. Evidence: `Strata/src/Strata/Renderer/SceneGizmos.h:29-46` |
| `new:18` | figure | home | The Inspector of a Directional zone: Radius disabled, its reason as the tooltip. Evidence: `Strata/src/Strata/Reflection/Property.h:89-92` |
| `new:19` | figure | home | From component to pixel: the path of one Strength edit to moving pixels, and the path of the gizmo to its lines. Evidence: `StrataEditor/src/Editor/PropertyEdit.cpp:135-155`; `Strata/src/Strata/Physics/PhysicsSystem.cpp:158-177`; `Strata/src/Strata/Renderer/SceneGizmos.h:57-66` |
| `new:26` | hands-on | home | Exercise (extend): a Falloff property for Spherical zones that weakens the force toward Radius, with its own inactive reason in Directional mode; the solution is a patch of the chain, `exercise-<n>.patch` of the page's tutorial file. Evidence: `.claude/skills/strata-add-component/SKILL.md:69-73`; `Strata/src/Strata/Animation/AnimationComponents.cpp:17-45` |
| `new:27` | hands-on | home | Exercise (extend): a gusting wind whose strength changes with the fixed steps run, never with frames, so that runs repeat; the solution is a patch of the chain, `exercise-<n>.patch` of the page's tutorial file. Evidence: `Strata/src/Strata/Scene/Scene.h:436-438` (`GetFixedStepCount`, the game's own time base) |
| `physics:89-93` | feature | use | The fixed step: changes applied, `Simulate`, sync before it, write-back after it, forces queued for the next step |
| `physics:114` | feature | use | `OverlapSphere` for a Spherical zone |
| `physics:394` | rule | use | Forces in `OnFixedUpdate`, every step they should act |
| `physics:255` | concept | use | Sleeping: a pushed body stays awake |
| `physics:267` | concept | use | Two copies of the truth: the wind changes bodies, physics writes the entities |
| `physics:34` | feature | use | The collider gizmos, beside which the WindZone's are drawn |
| `scene-ecs:100-104` | feature | use | The system's interface, Simulate mode, its descriptor and the system registry |
| `scene-ecs:118` | feature | use | Taking `IBodyControl` and `IPhysicsQueries` from the scene, and offering the wind service |
| `scene-ecs:537` | rule | use | Modules meet through services, which is how the script host reaches the wind |
| `scene-ecs:203` | feature | use | The gizmo shapes, which the arrow kind extends |
| `scene-ecs:198` | feature | use | `SetInactiveReason`, called for Radius |
| `scene-ecs:531` | rule | use | A property another turns off gets an inactive reason |
| `scene-ecs:501` | rule | use | The transform contract: the system writes no transform |
| `scene-ecs:28`, `scene-ecs:80` | feature | use | `MarkModified` and `MarkTransformsChanged` on the path from the edit to the pixel |
| `scene-ecs:136` | feature | use | Drawn matrices, made when the render scene syncs |
| `scene-ecs:206` | feature | use | `ComponentAccess`, the one validated path of the Inspector's write |
| `foundation:139` | feature | use | The conventions: -Z is forward, which a Directional zone blows along |
| `render-core:220-222` | feature | use | The overlay set, `DebugDraw`'s arrows and `DrawSceneGizmos` |
| `render-scene:33`, `render-scene:35` | feature | use | Signal-driven sync and drawn transforms, on the path to the pixel |
| `editor-core:408` | code | use | `SetPropertyWithUndo`: the Inspector's path into the scene |
| `editor-ui:180`, `editor-ui:181` | feature | use | The property row and its inactive reason as the Inspector draws them |
| `scripting:171` | feature | use | The host API's implementation the new function joins |
| `scripting:377` | code | use | The X-macro table whose end the new function joins |
| `scripting:104` | feature | use | Graceful degradation: the SDK's fallback on an older engine |
| `scripting:450`, `scripting:452`, `scripting:459` | rule | use | Append, check `ST_SCRIPT_HAS_MEMBER`, wrap in `HostCall` |
| `scripting:496` | rule | use | The feature script's call of the new function |
| `editor-core:54-60` | feature | use | The command's metadata, result, registry, schema check, arguments, utilities and kind |
| `editor-core:546`, `editor-core:558` | rule | use | Refuse bad input without side effects; declare the kind |
| `foundation:96` | feature | use | `ST_PROFILE_STAGE` and the frame profiler: the system's profile stage |
| `foundation:487` | rule | use | A stage around a unit of frame work |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The WindZone's spec: its parts, layers, registries and decisions | `capstone/plan` | must |
| The component and its system | `world/tutorial-component` | must |
| One fixed step: sync, forces, write-back | `physics/world-step` | must |
| Physics queries: overlaps and masks | `physics/queries` | must |
| Sleeping and islands | `physics/dynamics` | helps |
| Gizmos, `DebugDraw` and the overlays | `gpu/debug-drawing` | must |
| Inactive reasons in the Inspector | `editor-ui/inspectors` | must |
| Scene systems, soft constraints and scene services | `world/systems` | must |
| Reflection: properties, ranges and tooltips | `world/reflection` | must |
| Change signals and the transform contract | `world/scene-graph` | must |
| Drawn transforms | `world/interpolation` | must |
| The render scene and its sync | `draw/render-scene` | must |
| The coordinate conventions: -Z forward | `gpu/coordinates` | must |
| The host API: `HostCall`, `ResolveContext`, `ReportProblem` | `scripting/host-api` | must |
| Appending a host function and its SDK wrapper | `scripting/tutorial-host-function` | must |
| Adding a command, its kind and its test | `editor/tutorial-command` | must |
| `SetPropertyWithUndo` and undo steps | `editor/undo` | must |
| Running a command from a terminal with `StrataCLI call` | `editor/commands` | must |
| Profile stages | `core/profiling` | helps |

**Starting state.** The end state of `capstone/plan`: the chain's patches applied, the sphere gizmo of
`gpu/debug-drawing`'s exercise among them, built in Debug, and the spec written. The tutorial file has
`patch.pictures`, since the page shows the patched editor (the Scene view with both zones, the Inspector): the patch
runner builds `StrataEditor` and makes those pictures with it, as it builds the editor for any patch that changes files
under `StrataEditor/` (`pipelines.md` §6.6). For the editor steps, a checkpoint project of its own: the scene of
`editor/tutorial-command`'s checkpoint (two WindZones, one of each mode) with a floor and a row of dynamic crates, so
that no step creates them.

**Command-only steps.**

- Reading the wind at a point has no menu or button: `StrataCLI call wind.sample @sample.json`. `editor/commands`, which
  teaches running a command, is in the page's Needs closure through `editor/tutorial-command`.

## `capstone/land` — Capstone III: tests, the feature test, a budget, the review and CI

**Covers.** What the reader makes: the WindZone change made ready to land the way every change of Strata lands, and
then landed as commits. Each step section ends with a checkpoint of the patch and the test or tool output as a text
capture. The sections, in teaching order:

1. Unit tests, in a suite named after the module (`Physics.WindZone`, which the Systems shard runs; `Testing.Shards`
   fails a suite no shard runs): the force function's cases (each mode, the centre, outside the radius, Strength 0, a
   degenerate transform); the system in a real scene stepped in fixed steps, never frames: a box in a zone gains the
   speed a force gives in one step (dv = F / m * dt, as the force test of `Physics.Simulation` checks it), a static body
   and a box outside are not pushed, a sleeping box wakes, Simulate mode pushes too; a twin run with and without three
   workers gives the same poses; the gizmo's lines, read without a GPU as the character controller's gizmo test reads
   them; the inactive reason in each mode; the host function in `Scripting.API` and the API module's check of an older
   engine; `wind.sample` while editing, a refused position that changes nothing, and its kind in the kind lists. Tests
   that need Physics live in the files a build without the module leaves out (`src/Physics/` and the others listed in
   `STRATA_TESTS_OF_PHYSICS`) or behind `#if ST_WITH_PHYSICS`. Each new test is seen failing without the line it guards,
   then passing with it.
2. The feature test: `Feature.stscene` holds a zone of each mode with every property away from its default; the
   feature script that only called `Wind::GetForceAt` now expects a body pushed along the axis; `wind.sample` joins the
   editor's feature command script with an `expect`; the component schema snapshot is written again if the
   registration changed (`Reflection.ComponentSchema`); `ctest -L feature` passes.
3. A perf metric: a `Perf.Physics` test of bodies inside zones, built like the test of 1,000 character controllers: the
   median of the scene's fixed step and the wind system's part of it, in a Release build without the validation layer.
   Its `Budgets.json` entry: on any machine but the reference machine the metric is `Provisional`, measured and
   recorded, never checked; on the reference machine it gets Measured and a budget of at most 1.5 times that, and
   `Tools/PerfStability.py --runs 5` runs before it merges; budgets only go down.
4. The documents: the Developer Guide's physics section names the component and its system; `AGENTS.md` changes only if
   a rule changes, and `Docs.AgentGuide` keeps it under its limit.
5. The review: the full run of `ctest --preset <platform>-debug` stays the change's check, since it runs every suite,
   not only those the patch names: `CLI.McpToolsets` among them, which fails for a command in no toolset of the table
   and passes for `wind.sample` because `editor/tutorial-command` gave the `wind.` group its toolset; the six items of
   the pre-commit checklist walked over `git diff --staged`; `Tools/CompatLint.py --changed-since main`; the staged
   patch verified in a clean worktree in Debug and Release; the change split into commits, one logical change each, the
   perf commit's message stating the measured values.
6. CI: the branch `ci/windzone` pushed to the reader's fork, since CI runs on pushes to `ci/**`; the matrix on Windows,
   Linux and macOS with warnings as errors, including the Linux job without Audio, Physics and GLFW, which proves that
   nothing outside the Physics module names the WindZone; a failure read from its annotations with `Tools/CIStatus.py`;
   green before main.

Exercises: read a CI failure from its annotations only; say, by the ratchet's rule, what a later commit that makes the
wind cheaper must change in `Budgets.json`, and why the reader's own machine cannot set the numbers. At the end the reader has walked one feature from its design to a green CI run, and can land a change in
Strata the way its own changes land.

**Leaves out.**

- How the test program, its shards and labels work → `engineering/test-program`
- What the feature test counts and how its runners run → `engineering/feature-test`
- Noise, percentiles, confirmed checks and the canary → `engineering/perf-lab`
- The CI matrix, its caches and the Dist job → `engineering/ci`
- The checklist's reasons, clean worktrees and commit hygiene → `engineering/contributing`
- Packaging and releases → `engineering/releasing`
- The change itself → `capstone/build`

**Fit.** `fits`: about 4,800 words against L (5,000). Six step sections of two to six short steps (twenty-four), each
with its test output as a text capture, five quoted excerpts, one figure and two exercises, at the guide's lower values
for E1; the unit tests of section 1 take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:20` | code | home | `StrataTests/src/Physics/PhysicsSimulationTests.cpp:223-250`: a force acts over one step, dv = F / m * dt: the pattern of the system's test |
| `new:21` | code | home | `StrataTests/src/Renderer/DebugDrawTests.cpp:252-284`: a gizmo's lines read back without a GPU, the pattern of the WindZone's gizmo test |
| `new:22` | code | home | `StrataTests/src/Perf/PhysicsPerfTests.cpp:478-515`: the median of a scene's fixed step under a confirmed check, the pattern of the WindZone's perf test |
| `new:23` | code | home | `StrataTests/src/Editor/EditorMcpToolsetsTests.cpp:54-59`: every command must map to a toolset the table names, which the full run checks, `wind.sample` too through the `wind.` prefix of `editor/tutorial-command` |
| `new:24` | code | home | `StrataTests/Editor/FeatureCommands.json.in:1-7`: the editor's feature command script with its `expect` steps, which `wind.sample` joins |
| `new:25` | figure | home | The way a change lands: tests, the feature test, the perf metric, the documents, the review, a clean worktree, a `ci/<name>` branch, then main. Evidence: `AGENTS.md:78-81`; `AGENTS.md:457-474` |
| `build-test:113`, `build-test:114` | feature | use | The shards and `Testing.Shards`, which the new suite must satisfy |
| `build-test:396` | code | use | `CoreShards.json`: the Systems shard runs `Physics*` |
| `build-test:508` | rule | use | Every test case in a suite, every new suite prefix in a shard |
| `build-test:107` | feature | use | Module-dependent test files: a build without Physics leaves the WindZone's tests out |
| `build-test:491` | rule | use | `ST_WITH_*` are definitions; `#if ST_WITH_PHYSICS` only in tests and the composition root |
| `build-test:520` | rule | use | A new test fails without its fix |
| `scene-ecs:541` | rule | use | Tests count game time in fixed steps, never frames |
| `physics:149` | feature | use | Determinism with any number of threads |
| `physics:323` | code | use | The twin runs, the pattern of the wind's determinism test |
| `scripting:345` | concept | use | Testing game code and the API |
| `scripting:146` | feature | use | The API test module, which checks an older engine |
| `scripting:173` | feature | use | Host call counts, which the feature test reads |
| `editor-core:60` | feature | use | Command kinds as a tested decision |
| `automation:238` | feature | use | `CLI.McpToolsets`, which the full run runs and which finds `wind.sample` in a toolset |
| `build-test:155-158` | feature | use | The feature project, its coverage checks, its runners and the script side |
| `build-test:356` | concept | use | Coverage by construction |
| `build-test:532` | rule | use | Keep the feature test current |
| `build-test:584` | hands-on | use | A component that satisfies the feature test, carried from the minimum to behaviour checks |
| `build-test:135`, `build-test:137`, `build-test:138` | feature | use | The perf suites, the budget file and confirmed checks |
| `build-test:146-149` | feature | use | The perf suites by area, the ratchet, `Tools/PerfStability.py` and `Tools/PerfLock.py` |
| `build-test:404` | code | use | The format of `Budgets.json`, provisional entries included |
| `build-test:523`, `build-test:525`, `build-test:527` | rule | use | Budgets only go down; a busy machine proves nothing; numbers only from optimized builds |
| `build-test:578` | hands-on | use | Adding a perf metric, done here for the wind |
| `physics:173` | feature | use | The `Perf.Physics` tests the new metric joins |
| `build-test:186` | feature | use | `Docs.AgentGuide`, which checks `AGENTS.md` |
| `build-test:246-248` | feature | use | The golden rules, the pre-commit checklist and verifying in a clean worktree |
| `build-test:369` | concept | use | Process discipline: review, commit hygiene, clean-worktree verification |
| `build-test:543` | rule | use | Verify exactly what is staged, in Debug and Release |
| `build-test:566` | hands-on | use | `Tools/CompatLint.py --changed-since main` on the change |
| `build-test:192`, `build-test:193`, `build-test:199`, `build-test:201` | feature | use | CI's triggers, its matrix, failure annotations and `Tools/CIStatus.py` |
| `build-test:408` | code | use | `ci.yml`: the jobs and the test step the branch runs |
| `build-test:483`, `build-test:500`, `build-test:539` | rule | use | Warnings as errors in CI; `ci/<name>` before main; annotations carry the failures |
| `build-test:591` | hands-on | use | The exercise: a CI failure read from annotations only |
| `new:28` | hands-on | home | Exercise (design): what a later commit that makes the wind cheaper must change in `Budgets.json` by the ratchet's rule (measure again, lower Measured and Budget in the same commit, state the values in its message), and why the reader's own machine cannot set the numbers (only the reference machine measures; elsewhere the metric stays `Provisional`). Evidence: `StrataTests/Perf/Budgets.json:16-25`; `AGENTS.md:109-112` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The WindZone change | `capstone/build` | must |
| Test kinds, regression tests that fail without their fix | `engineering/testing` | must |
| Suites, shards, labels and `Testing.Shards` | `engineering/test-program` | must |
| Optional modules (`ST_WITH_*`) | `core/layers-registries` | must |
| The test files a build without a module leaves out | `engineering/test-program` | must |
| The feature test's coverage and runners | `engineering/feature-test` | must |
| Perf tests, budgets, provisional metrics and the reference machine | `engineering/perf-lab` | must |
| CI, its triggers, matrix and annotations | `engineering/ci` | must |
| The review checklist, clean worktrees and commit hygiene | `engineering/contributing` | must |
| Determinism with threads; twin runs | `physics/world-step` | must |
| Game time counts fixed steps, never frames | `core/time` | must |
| The API test module and older engines | `scripting/tutorial-host-function` | must |
| A command's kind lists and its unit test | `editor/tutorial-command` | must |
| Gizmo lines read from `DebugDraw` | `gpu/debug-drawing` | must |
| Medians and percentiles | `core/profiling` | helps |
| The MCP toolsets | `automation/mcp` | helps |
| CompatLint and the three compilers | `engineering/flags-portability` | helps |
| git: branches, commits and pushing | `basics/git` | must |

**Starting state.** The end state of `capstone/build`: the chain's patches and the WindZone change applied, built in
Debug and in Release (the perf step needs Release). The repository is the reader's own clone with a fork to push to,
for the CI section. No editor project is needed.

**Command-only steps.** none

## Passed on

none

## Not taken

none

## Questions for the planner

none
