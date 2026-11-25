# Brief: `world/tutorial-component`

| Field | Value |
| --- | --- |
| Title | Tutorial: adding a component and a system |
| Kind | T |
| Size | L |
| Tracks | E |
| Needs | `core/first-change`, `start/first-game`, `world/systems`, `world/serialization` |
| From | scene-ecs; skill `strata-add-component`; creates the WindZone component, track E's running example that the capstone completes; at this stage the WindZone has no asset property (the skill's example has a `Sound` property, which the feature test would need a resolving asset with its `.meta` for, and assets come in a later part); a later stage (`capstone/build`) may add one; ends with a serialization round trip and the feature test's minimum (`engineering/feature-test` has the rest); moved to the end of the part (the skill needs serialization) |
| Unit | `plan/allocation/world.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `world/tutorial-component` — Tutorial: adding a component and a system

**Covers.** What you will make: the WindZone, the first stage of track E's running example: a component that will push
bodies with wind (`capstone/build` adds the forces), declared in the Physics module, registered with ranges, tooltips and
an enum, with a scene system that runs in fixed steps, a serialization round trip and the feature test's minimum. What
you need: the source build of `core/first-change`, the engine's own checklist (the skill `strata-add-component`), and
the time it takes. The step sections, each a stage of the page's patch, which starts from the pin:

1. Declare the data: `WindZoneComponent` in `Physics/PhysicsComponents.h`, each member with a default and a comment with
   its unit (Strength in newtons, Radius in meters, Mode Directional or Spherical); why the module's header and not
   `Scene/Components.h`; no asset property at this stage.
2. Register it: in `RegisterPhysicsComponents`, a stable name, the category Physics, a description written for people
   and agents, `Range` and `WithTooltip`, an `EnumProperty`; why a name is never renamed; build, then open the editor:
   the Add Component menu lists Wind Zone under Physics, and the Inspector clamps a negative radius (the page teaches each
   click it uses beyond `start/first-game`).
3. A system: `WindZoneSystem`, built with `MakeSceneSystemDescriptor`, overriding only `OnFixedUpdate`, registered in
   `RegisterPhysicsModule` beside the Physics system with `BeforeIfPresent = { "Physics" }` and its result checked, its
   place read in the update-order line that the engine logs at startup (`world/systems`); at
   this stage it gathers the active zones and their world transforms from the scene's cache each fixed step, writes no
   transform, and a test reads what it gathered through `GetSystem<T>`; the scene service that serves the zones it
   gathers (for the script SDK's `Wind::GetStrength`) comes on `scripting/tutorial-host-function`, and the forces on
   bodies at `capstone/build` (D38).
4. Test it: a reflection test (the properties and their ranges exist; invalid values are refused), a serialization round
   trip (every value kept; an unknown property warns; a value out of range is clamped), and the system stepped with
   `OnUpdateRuntime` in a real `Scene` (`CallsUpdate` is false; the zones are gathered), in a suite that an existing
   shard runs.
5. The feature test's minimum: an entity of `StrataTests/FeatureTest/Assets/Scenes/Feature.stscene` with every property
   at a value other than its default; the component schema snapshot written again with the test program's
   `--strata-test-helper=write-component-schema`; `ctest -L feature` and the `Architecture.Layering` check passing.

Each section ends with a checkpoint (the patch so far), and its "You should see" is build or test output shown as a
text capture. The exercise: rename the WindZone's registered name and load a scene saved before the change, predicting
first what happens. At the end the reader can add a component and a system to Strata that pass the engine's own checks.

**Leaves out.**

- Forces on bodies, the gizmo, the inactive reason, the script API and the command in one change → `capstone/build`
- Designing the WindZone as a feature: its layers and registries → `capstone/plan`
- What the feature test counts, its runners and how to extend it beyond the minimum → `engineering/feature-test`
- The WindZone's gizmo as an exercise → `gpu/debug-drawing`
- The host function `Wind::GetStrength` → `scripting/tutorial-host-function`
- The `wind.*` commands → `editor/tutorial-command`
- Every preset and option of the build → `engineering/building`

**Fit.** `fits`: about 5,150 words against L (5,000). Five step sections of two to four steps, six quoted hunks, two
pictures of the editor and the exercise.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scene-ecs:580` | hands-on | home | The tutorial is this exercise: declare, register with ranges and tooltips, round trip, feature test; the inactive reason waits for `capstone/build`, and the WindZone needs no `Requires` |
| `scene-ecs:520` | rule | home | New components live in their module's components header, not in `Scene/Components.h` |
| `gamedev:560` | hands-on | home | The game makers' survey's form of the same exercise: a component with tooltips that give units, and the feature test's coverage |
| `new:11` | code | home | `Strata/src/Strata/Physics/PhysicsRegistration.cpp:12-27`: `RegisterPhysicsModule`, the place the WindZone's registration joins: components, a settings section, the Physics system's descriptor with a soft constraint, a profile stage and a preparation hook |
| `physics:70` | feature | use | The Physics system's registration, beside which the WindZone's system is registered |
| `scene-ecs:392` | code | use | `Register<T>` behind the registration the reader writes |
| `scene-ecs:524`, `scene-ecs:526` | rule | use | Never rename a registered name; choose ranges that make bad states impossible |
| `scene-ecs:533`, `scene-ecs:535` | rule | use | Soft constraints toward another module's system; descriptors made with `MakeSceneSystemDescriptor` |
| `scene-ecs:501` | rule | use | The transform contract: the system reads the cache and writes no transform |
| `scene-ecs:581` | hands-on | use | The Spinner's checks of order and `CallsUpdate`, which the system's test repeats |
| `new:28` | hands-on | home | The page's exercise (style.md §6.3, one to four on a tutorial; R32, D27), predict then run: a scene with a WindZone is saved, the registered name is changed in `RegisterPhysicsComponents`, and the scene is loaded again; the old name is now an unknown component, kept unchanged and written back, with one warning, and the zone has no component the system gathers; the answer ties it to the rule never to rename a registered name (`scene-ecs:524`) (about 250 words). Evidence: `Strata/src/Strata/Scene/SceneSerializer.cpp:504`; `Strata/src/Strata/Scene/EntitySink.cpp:180`; `Strata/src/Strata/Reflection/ComponentRegistry.h:242-246` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Building Strata from source, writing and running one test | `core/first-change` | must |
| A project in the editor, the Hierarchy and the Inspector | `start/first-game` | must |
| Scene systems, descriptors, soft constraints and the runtime frame | `world/systems` | must |
| Registration with ranges, tooltips and enums | `world/reflection` | must |
| Scene documents and the round trip | `world/serialization` | must |
| The world transform cache and the transform contract | `world/scene-graph` | must |
| The layer table, and which module a component belongs to | `core/layers-registries` | must |
| The feature test | `engineering/feature-test` | helps |
| Rigid bodies, which the WindZone will push | `physics/bodies-colliders` | helps |

**Starting state.** The engine at the pin (`822a7a46`), unchanged, with the source build of `core/first-change` (in phase
B the patch runner's build folder `build/docs-patch`); the page's patch starts from the pin and is the first of the
WindZone's chain. For the editor step of section 2, a project made from the Basic 3D template as `start/first-game` made
it.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.
