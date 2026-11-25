# Brief: `capstone/build`

| Field | Value |
| --- | --- |
| Title | Capstone II: from component to pixel |
| Kind | T |
| Size | L |
| Tracks | E |
| Needs | `physics/world-step`, `gpu/debug-drawing`, `editor-ui/inspectors`, `capstone/plan` |
| From | new; the system's forces on bodies, a debug gizmo, an inactive reason in the inspector, the script API and the command, in one change |
| Unit | `plan/allocation/capstone.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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
| critic-capstone-1 | must | stale-item | `capstone/build` (Covers, section 3, `new:16`, `new:17`, `new:19`) | The page says the Scene view shows every zone, and its pictures show both zones' gizmos. At the pin the editor draws the gizmos of the collider group, which the WindZone's joins, only for the selected entities and their children: `ViewportSettings::AllColliders` is false by default, and no toolbar control turns it on; only `viewport.setSettings {"allColliders": true}` does. A reader who follows section 3 sees neither the sphere nor the arrow until a zone is selected. | Section 3 gets a step: select both zones in the Hierarchy; its "You should see" shows both shapes, and its "If you do not see it" names the selection rule and the command, with a link to `editor/commands` (about 80 words). In Covers, "the Scene view shows every zone" becomes "the Scene view shows the selected zones". The recipes of `new:16` and `new:17` select both zones. The gizmo's path in section 7 and in `new:19` adds `ViewportRenderer`, which hands the selection to `DrawSceneGizmos` as `ColliderEntities` (one clause). `gpu/debug-drawing`'s exercise, which draws the sphere first, says the same in its "You should see" (one sentence). | `allocation/capstone.md:171`, `:189-193`, `:206-210`, `:242-245`; `allocation/gpu.md:1083-1086`, `:1121`; `StrataEditor/src/Editor/EditorViewport.h:96-99`; `StrataEditor/src/Editor/ViewportRenderer.cpp:241-248`; `Strata/src/Strata/Renderer/SceneGizmos.h:34-36`; `StrataEditor/src/Editor/EditorViewportCommands.cpp:1117`; `StrataEditor/src/Panels/ViewportPanel.cpp:428` (the only gizmo control: Gizmos on or off) |
| critic-capstone-2 | must | missing-item | `capstone/build` (section 2) and `capstone/land` (section 2) | When the forces arrive, the WindZone that `world/tutorial-component` put into `Feature.stscene` starts to push bodies in every run of the feature test, and `capstone/land` adds a zone of each mode. The scene has seven active dynamic bodies. Their feature scripts, and the editor's command script, expect exact motion: the Ball's X between -4.05 and -3.95 after 150 steps, and each body at rest where it fell. An active Directional zone pushes every one of them, so the feature test fails. The patch runner runs that test after `capstone/build`'s patch. Neither page says where the zones stand. | Section 2 of `capstone/build` gets a step: the feature scene's zone must push no probe. A Spherical zone stands where its Radius reaches none of the seven bodies; a Directional one sits on an inactive entity. Then the feature test runs (about 60 words). Section 2 of `capstone/land`: the Directional zone sits on an inactive entity, as the "Moon" light holds alternate values. The behaviour check uses a body of its own inside the Spherical zone, away from the seven probes, and the feature script expects that body pushed away from the centre, not along an axis (about 70 words). | `allocation/capstone.md:201-202`, `:333-336`; `allocation/world.md:963-964`; `pipelines.md:1058-1059`; `StrataTests/FeatureTest/Assets/Scenes/Feature.stscene:727`, `:802`, `:892`, `:1196`, `:1257`, `:1318`, `:1899` (the seven dynamic bodies, each with a feature script); `StrataTests/Editor/FeatureCommands.json.in:22-29`; `StrataTests/FeatureTest/Scripts/PhysicsFeatures.cpp:42-52`; `Docs/DeveloperGuide.md:833-838` (200 frames, three runs); `.claude/skills/strata-add-component/SKILL.md:107-109` |
| critic-capstone-8 | should | missing-item | `capstone/plan` (section 5), `capstone/build` (sections 1 and 2) | The decisions never say whether the zone entity's scale scales Radius, nor which collision layers a zone pushes. At the pin collider gizmos follow the entity's scale (a sphere's radius by the largest axis), a gizmo function gets the world matrix, and `OverlapSphere` takes a layer mask. The chain's sphere gizmo, the force function, the overlap query and `wind.sample` must follow one rule, or a scaled zone draws a sphere that is not where it pushes. | `capstone/plan` section 5 adds two decisions with their costs: whether Radius is scaled by the world transform (one rule for the gizmo, the force, the query and the command), and the layers a zone pushes (every layer, or a mask property) (about 70 words). `capstone/build` applies the scale rule in section 1 and the mask in section 2 (one clause each), and `capstone/land` section 1 adds a scaled zone to the force function's cases. | `allocation/capstone.md:38-44`, `:176-187`; `allocation/gpu.md:1121`; `Strata/src/Strata/Renderer/SceneGizmos.h:61-63`; `Strata/src/Strata/Reflection/ComponentGizmo.h:41-43`; `Strata/src/Strata/Scene/SceneServices.h:172-173`, `:187` |
| critic-capstone-11 | could | duplicate | `capstone/land` (exercises, row `build-test:591`) | The first exercise, reading a CI failure from its annotations only, is the exercise that `engineering/ci` homes (`build-test:591`), and `engineering/contributing`'s exercise ends the same way (a `ci/<name>` push read with `CIStatus.py`). Both pages are in the page's Needs closure, so the track E reader does it a third time, from the same angle. style.md asks a tutorial for open "make it yours" extensions. | Replace it with an extension: land the Falloff of `capstone/build`'s exercise the way the page landed the WindZone (its unit test seen failing first, a value off its default in `Feature.stscene`, the schema snapshot written again because the registration changed, its own commit, a green `ci/<name>` run); the solution is a patch. The row of `build-test:591` becomes `link` (about the same words). | `allocation/capstone.md:355`, `:415`; `allocation/engineering.md:1094`, `:1252`; `style.md:529-530` |
| critic-capstone-15 | could | missing-item | `capstone/build` (section 7) | Section 7 follows a Strength edit, made while the crates drift in Play, through `SetPropertyWithUndo`. At the pin, scene edits while playing change the running copy: they get no undo step and are gone at Stop. The page does not warn a reader who tunes the wind in Play and then stops. | One sentence in section 7: an edit while playing changes the running copy, so it has no undo step and is discarded at Stop; the same edit made while editing is kept, can be undone, and acts from the next Play (about 40 words, with a link to `editor/play-mode`). | `allocation/capstone.md:206-210`; `Docs/DeveloperGuide.md:2976-2977`, `:3453-3455` |
