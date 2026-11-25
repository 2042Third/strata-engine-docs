# Brief: `make/script-fields`

| Field | Value |
| --- | --- |
| Title | Tuning scripts from the editor: fields, references and prefabs |
| Kind | H |
| Size | M |
| Tracks | G |
| Needs | `make/project-coin-run` |
| From | scripting "Your first script" (fields) and "The gameplay API, part 1" (entity and asset fields, `Instantiate` by handle); Manual/Scripting "Create a script"; the field types (`bool`, `int32_t`, `float`, vectors, quaternions, strings, `Entity`, `AssetHandle`); fields through hot reload and in prefab overrides |
| Unit | `plan/allocation/make-b1.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/script-fields` — Tuning scripts from the editor: fields, references and prefabs

**Covers.** A how-to on a crate spawner built from a new Basic 3D project. The goal: tune a script from the Inspector
instead of the code. It starts with a `Spawner` class that has one field of each of the ten types (`bool`, `int32_t`,
`float`, `glm::vec2`, `glm::vec3`, `glm::vec4`, `glm::quat`, `std::string`, `Entity`, `AssetHandle`), and the steps show
how the Inspector's Script section shows each one: the class picker, the default that the class gives, the value set on
one entity, and the reset button. No other type exists: a `std::vector`, an array, an enum, a `double`, an `int64_t` or
a struct fails to compile with "Unsupported script field type", and the usual ways around it are several fields, an
`int32_t` for an enum, or a string. An `Entity` field takes an entity of the scene (the spawn point); an `AssetHandle`
field takes an asset (the crate prefab). Then the spawner works: it asks for the prefab in `OnCreate`, instantiates it by its
handle at the spawn point at an interval given by a float field, and handles "not loaded yet": `Scene::Instantiate`
returns a null entity until the prefab is in, and never waits. Then values while playing: a field changed during Play
takes effect at once, and Stop brings back the edited value, because Play runs on a copy. Hot reload keeps every field
whose name and type stay the same; a renamed or retyped field loses its stored value and the log says so. A renamed
class is lost the same way: an entity whose Script entry names a class the module no longer has gets no instance, and
the log says so; so after renaming a class, the reader picks it again on each entity. Last, fields
in prefabs: the spawner made into a prefab, a field's value overridden on one instance (shown as an override, like any
property), applied to the prefab or reverted; an entity field that points inside the prefab follows each instance. The
exercises, done in the editor and in a script: a second spawner whose interval and prefab are overridden on the
instance and then reverted, and an `Entity` field left empty, which the spawner checks with `IsValid` and replaces with
its own position. At the end the reader can expose any value of a script to the editor, wire entities and assets into
scripts without code, and spawn prefabs safely.

**Leaves out.**

- Writing a script class, `ST_SCRIPT_FIELD` and building, the first time → `make/first-script`
- Hot reload as a workflow → `make/first-script`
- Timers → `make/timers-events`
- Many instances in one call (`Scene::InstantiateMany`) → `make/performance`
- Prefabs, overrides, apply and revert in general → `make/prefabs`
- How the Inspector is built from registered properties → `editor-ui/inspectors`
- How fields and their defaults cross the binary interface → `scripting/abi-sdk`
- How prefab overrides are stored and kept exact → `world/prefabs`

**Fit.** `fits`: about 3,200 words against M (3,000). Ten numbered steps with their results and the table of the ten
types (about 1,900 words), three rules (assets asked for early, what hot reload keeps, a renamed class) and the two
exercises take the most; the absence of other field types is one short paragraph.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:131` | feature | home | Attaching a class (Add Component > Script) and its fields per entity, with defaults and reset, and their live values while the game plays |
| `scripting:432` | figure | home | The Inspector with a Script component: the class picker and one field of every type with its default and reset button |
| `scripting:515` | hands-on | home | The spawner: a prefab field asked for early, `Scene::Instantiate` by handle, "not loaded yet" handled; its 100 instances in one call are `make/performance`' |
| `scripting:114` | feature | use | `ST_SCRIPT_CLASS` and `ST_SCRIPT_FIELD`, which register the fields |
| `scripting:115` | feature | use | The ten field types |
| `scripting:117` | feature | use | `AssetHandle`, the type of an asset field |
| `scripting:118` | feature | use | `Entity` as the type of an entity field, and `IsValid` |
| `scripting:121` | feature | use | `Assets::RequestLoad`, `Assets::IsLoaded` and `Scene::Instantiate` by handle |
| `scripting:154` | feature | use | The Script component: the classes of an entity and their field values, saved with the scene |
| `scripting:326` | concept | use | Serialized fields: stored per entity by name and type; a renamed field's values are ignored with a warning |
| `scripting:472` | rule | use | Only fields survive hot reload |
| `scripting:481` | rule | use | Request assets early; `Instantiate` never waits |
| `gamedev:494` | rule | use | The same rule as game makers meet it (its home is `make/scripting-scene`) |
| `scene-ecs:174` | feature | use | Prefab overrides per property, script fields among them (`Script` and `<Class>.<Field>`) |
| `new:15` | not-done | home | Script field types beyond the ten: no `std::vector`, array, enum, `double`, `int64_t` or struct; such a field fails to compile with "Unsupported script field type"; the ways around it are several fields, an `int32_t` for an enum, or a string. Evidence: `StrataScriptCore/Include/StrataScript/Script.h:133-137` (`c_IsFieldType`), `:785-786` (the `static_assert` and its message) |
| `new:36` | rule | home | After renaming a script class, pick it again on each entity: an entry whose class the module lacks gets no instance and a problem is reported, and a hot reload removes the vanished class's instances from the playing entities, so a rename detaches the class everywhere, as renaming a field loses its value. Evidence: `Strata/src/Strata/Scripting/ScriptSystem.cpp:619-624` (a class the module lacks: no instance, a problem reported), `:1290-1295` (on reload, a class that no longer exists is removed from the entity); `Strata/src/Strata/Scripting/ScriptEngine.h:60-62` (classes that no longer exist lose their instances); `Docs/DeveloperGuide.md:2129-2131` |
| `new:16` | hands-on | home | Exercises, done in the editor and in a script: a second spawner instance whose interval and prefab are overridden and then reverted; an `Entity` field left empty, which the spawner checks with `IsValid` and replaces with its own position. Evidence: `StrataScriptCore/Include/StrataScript/Entity.h:39` (`IsValid`); `StrataScriptCore/Include/StrataScript/Script.h:133-137` (the field types) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| A script class, `ST_SCRIPT_CLASS`, `ST_SCRIPT_FIELD` and a float field | `make/first-script` | must |
| Hot reload | `make/first-script` | must |
| Prefabs, instances, overrides, apply and revert | `make/prefabs` | must |
| Asset handles, in one paragraph | `make/assets` | must |
| `Instantiate` never waits: asking for assets early | `make/scripting-scene` | must |
| A rotation stored as a quaternion | `make/transforms-units` | must |
| `std::string` | `basics/programming-2` | must |
| Play on a copy, and Stop | `make/play-test-debug` | must |
| `Timer` | `make/timers-events` | helps |

**Starting state.** A new project from the Basic 3D template; no checkpoint. The first step makes a crate prefab from a
cube with a dynamic RigidBody, as `make/prefabs` and `make/physics` taught, and an empty entity named "Spawn Point".

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
| critic-make-b1-3 | should | shape | `make/gameplay-math`, `make/timers-events`, `make/script-fields`, `make/script-builds`, `make/levels-saves` | style.md gives a how-to a `## Variations` section: the same goal under other conditions. The Covers of these five how-tos name no variation, so the writer has nothing to fill it with. The how-tos of `make-a` and `make-b2` name theirs. (`make/recipes` has its "what to change" per recipe.) | Each Covers names two variations (about 250 words a page). From the pin: gameplay-math, aiming with the right stick through the Look action instead of the cursor (`FollowCamera.cpp:57-60`), and a turret that turns at a limited speed (critic-make-b1-16); timers-events, a timer in `OnFixedUpdate` fed with the fixed delta, for gameplay that keeps step with physics, and a held gamepad direction repeated (critic-make-b1-5); script-fields, tuning many spawners at once through their prefab (critic-make-b1-4); script-builds, the plain `cmake -S` and `-B` build as a check that the code compiles on another machine (critic-make-b1-1); levels-saves, three save slots named "Slot 1" to "Slot 3" and listed with `ListSaveFiles`. The five Fit lines count them. | `style.md:535-541`; `allocation/make-b1.md:5-24`, `:91-111`, `:174-193`, `:420-440`, `:922-962`; `allocation/make-a.md:130`, `:424`; `allocation/make-b2.md:393`; `StrataScriptCore/Include/StrataScript/Game.h:104-107`, `:157-158` |
| critic-make-b1-4 | should | missing-item | `make/script-fields` | The page shows the Script section with a class picked, but not what the Inspector says when something is wrong, nor a limit a tuner meets at once. With several entities selected, the section shows only "Select one entity to edit its scripts". Before a build it shows "No script module is loaded: build the scripts (Scripts > Build Scripts) to edit their fields." After a class rename the old entry stays, marked "The script module has no class '<name>'", with its stored values as text; they come back if the old name comes back. A value is stored on an entity only once it is set, so a new default in the code reaches every entity that has no value of its own, and only those. | Add a short section "What the Inspector tells you" with the three messages, and add to the rename rule `new:36` that the old entry is removed with its X button (about 150 words). Add the multi-selection limit and its way around: the script on a prefab, its value changed on the prefab (the Variation of critic-make-b1-3). Add one sentence after the reset button: a changed default reaches the entities without a value of their own. | `allocation/make-b1.md:177-187`, `:229`; `StrataEditor/src/Panels/InspectorPanel.cpp:141`, `:170`, `:183-188`, `:763-768`, `:1224-1227`, `:1250-1254`; `StrataEditor/src/Editor/ScriptEdit.cpp:180-195` |
