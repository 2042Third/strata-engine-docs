# Brief: `capstone/plan`

| Field | Value |
| --- | --- |
| Title | Capstone I: designing a feature the way Strata does |
| Kind | T |
| Size | L |
| Tracks | E |
| Needs | `world/tutorial-component`, `scripting/tutorial-host-function`, `editor/tutorial-command`, `engineering/contributing`, `core/reading-code` |
| From | new; the book's running example for track E grown into a feature: its layers, its registries and the rules that apply; a trace exercise: one click in the Scene view followed to a pixel, with the method of `core/reading-code` |
| Unit | `plan/allocation/capstone.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-capstone-3 | must | stale-item | `capstone/plan` (section 2) and `capstone/land` (section 6) | `capstone/plan` says that nothing outside the Physics module may name the WindZone. `capstone/land` says that CI's Linux job without Audio, Physics and GLFW proves it. At the pin the editor can only be configured with every module (CMake stops otherwise), that job also sets `-DSTRATA_BUILD_EDITOR=OFF`, and the editor's tests are left out without the editor. So the `wind.*` commands, which name the component, and `wind.sample`, which calls the Physics function directly, are allowed, and that job never builds them. The rule as written contradicts the capstone's own command. | `capstone/plan` section 2 states the rule exactly: nothing that a build without Physics compiles names the WindZone (the other layers, the runtime, the tests outside `STRATA_TESTS_OF_PHYSICS`); `#if ST_WITH_PHYSICS` stays where `AGENTS.md` allows it; the editor may name it, because it is built only with every module (about 50 words). `capstone/land` section 6 says what the job proves: the Scene layer's service, the host function and the guarded tests compile without the module, and the other jobs build the editor's commands (about 40 words). | `allocation/capstone.md:22-25`, `:203-205`, `:350-352`; `CMakeLists.txt:36-47`; `.github/workflows/ci.yml:52-60`; `StrataTests/CMakeLists.txt:65-70`, `:76-77` |
| critic-capstone-6 | should | thin-home | `capstone/land` (section 4) and `capstone/plan` (section 6, the spec's docs) | The documents step names only the Developer Guide's physics section and `AGENTS.md`, which is what the skill `strata-add-component` asks for a component. But the WindZone change also adds script API and a command. At the pin the engine documents such a change in more places, and its own spec lists them under "Docs, skills and release notes": the Guide's "Gameplay API" with its host function order (each appended group named), `Docs/Manual/Scripting.md` for game makers, the API overview of the skill `strata-scripting`, and a line in the running wave's release notes. | Section 4 of `capstone/land` lists these places and what each gets: the component and its system in "Physics"; `Wind::GetStrength` and `Wind::GetForceAt` in "Gameplay API" and in the host function order; a paragraph in the Manual's scripting page; the two functions in the skill's overview; one line in the draft release notes (about 90 words). The docs section of the spec on `capstone/plan` names the same list (one sentence). | `allocation/capstone.md:45-47`, `:342-343`; `Docs/Plans/Wave8/specs/physics-timing.md:944`, `:955-956`, `:973`, `:975`; `Docs/DeveloperGuide.md:1867`, `:1950-1955`; `.claude/skills/strata-scripting/SKILL.md:140-146`; `Docs/Manual/Scripting.md:172`; `Docs/Plans/Wave8/ReleaseNotes.md:114`; `.claude/skills/strata-add-component/SKILL.md:117-120` |
| critic-capstone-7 | should | stale-item | `new:1` on `capstone/plan` (section 6) | The row says the engine's specs have sections "in a fixed order" and lists ten. At the pin the wave-8 specs differ in their sections and their order. `physics-timing.md`, the row's own evidence, has thirteen sections and a closing "Review corrections", and the row leaves out four of them: "Settings and defaults", "What the stream shares and how merges resolve", "The first hour" and "Review corrections". Every wave-8 spec ends with a first hour and with an independent review against the code before the work starts. That review is part of designing a feature the way Strata does. | `new:1` says "the sections the wave-8 specs share, in about this order". It adds settings and defaults (the WindZone's defaults and ranges), the first hour (what to read, and the baseline run of `Physics.WindZone` and the feature test) and the review (each file, function and line the spec names is checked at the pin, and the corrections are written down). Section 6 gets the review as its last step (about 150 words). The row's evidence adds `:797`, `:1115` and `:1132`. | `allocation/capstone.md:45-47`, `:73`; `Docs/Plans/Wave8/specs/physics-timing.md:797`, `:1003`, `:1115`, `:1132-1135`; `Docs/Plans/Wave8/specs/reflections.md:1360`, `:1377`; `Docs/Plans/Wave8/specs/showcase.md:1433`, `:1454`; `Docs/Plans/Wave8/specs/step0-editor.md:1360`, `:1372` |
| critic-capstone-8 | should | missing-item | `capstone/plan` (section 5), `capstone/build` (sections 1 and 2) | The decisions never say whether the zone entity's scale scales Radius, nor which collision layers a zone pushes. At the pin collider gizmos follow the entity's scale (a sphere's radius by the largest axis), a gizmo function gets the world matrix, and `OverlapSphere` takes a layer mask. The chain's sphere gizmo, the force function, the overlap query and `wind.sample` must follow one rule, or a scaled zone draws a sphere that is not where it pushes. | `capstone/plan` section 5 adds two decisions with their costs: whether Radius is scaled by the world transform (one rule for the gizmo, the force, the query and the command), and the layers a zone pushes (every layer, or a mask property) (about 70 words). `capstone/build` applies the scale rule in section 1 and the mask in section 2 (one clause each), and `capstone/land` section 1 adds a scaled zone to the force function's cases. | `allocation/capstone.md:38-44`, `:176-187`; `allocation/gpu.md:1121`; `Strata/src/Strata/Renderer/SceneGizmos.h:61-63`; `Strata/src/Strata/Reflection/ComponentGizmo.h:41-43`; `Strata/src/Strata/Scene/SceneServices.h:172-173`, `:187` |
| critic-capstone-10 | could | duplicate | `new:6` on `capstone/plan` | The erratum about the comment of `SceneServices.h:28-29` (six services named, seven registered) has two homes: here, and as `new:17` on `world/systems`, the home of scene services, which comes first on track E. R46 keeps the row of the page that comes first in the outline when two units place one erratum. | `capstone/plan` drops `new:6`. Its Covers keeps "names all seven services `PhysicsSystem` offers", with a link to `world/systems` (no words added). | `allocation/capstone.md:36`, `:78`; `allocation/world.md:331`; `critique/rulings-10.md:72-74`; `Strata/src/Strata/Scene/SceneServices.h:28-29`; `Strata/src/Strata/Physics/PhysicsSystem.cpp:61-67` |
| critic-capstone-12 | could | shape | `capstone/plan` | A tutorial opens with "What you will make" and a picture of the result. The page's only figure item is `new:7` (the WindZone's parts on the layer diagram), but its Fit counts two figures. The list does not say whether `new:7` is the picture of the result or whether a second figure is missing. | Either `new:7` is named the picture of "What you will make" and the Fit says one figure, or a figure item is added: the finished spec's first screen, with its sections, beside the parts map (about 100 words with its paragraph). | `allocation/capstone.md:64-66`, `:79`; `style.md:520` |
