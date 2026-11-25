# Brief: `scripting/script-system`

| Field | Value |
| --- | --- |
| Title | The script system |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `scripting/loading`, `world/systems`, `assets/residency`, `physics/contacts-triggers`, `animation/time-events` |
| From | scripting ch. 13 "ScriptSystem" (instances, sync points, reconciliation, update order and dispatch lists, prefetching, contact, animation and UI events, asset pins; excerpts 26-29, figure 10); the code of the script lifecycle: the lifecycle and its callbacks have their home in `make/script-loop`, which track E does not read, so this page names the callbacks and their order before it shows their code |
| Unit | `plan/allocation/scripting.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `scripting/script-system` — The script system

**Covers.** The job: `ScriptSystem` runs the scripts of one playing scene: it creates instances from Script components,
calls their callbacks in a fixed order and stays consistent while scripts change the scene under it. The problem in one
paragraph that links `scripting/why-scripts`. Registration: the Script component (its entries, field overrides,
serialization, references for entity and asset fields) and the "Scripting" scene system (Play only, not Simulate;
profile stage `Scene.Scripts`; before physics). The callbacks and their order, named here for track E (their home for
game makers is `make/script-loop`), on a frame timeline (figure): UI events, `OnUpdate`, the fixed steps with contacts
and `OnFixedUpdate`, animation events, `OnLateUpdate`, where the step alpha is final, so a camera reads drawn poses
there and a ridden platform moves in `OnFixedUpdate`, and destruction at the end of the frame; why press edges are read
in `OnUpdate`; the 15 callbacks of the class descriptor and when each arrived. The map: the instance's states (figure):
constructed with its fields, pending start, created, disabled after an exception, removed and destroyed at a sync point.
The toy: a system with a list of instances, a frame and a deferred destroy, about 60 lines. Then the real code: the
start of play (the scripted entities marked in hierarchy order, their instances created and `OnCreate` run at the first
sync point, once every scene system has started) and its stop (`OnDestroy` in the reverse of the update order,
descendants first, then the asset pins released); what a call's result does (an exception disables its instance, a
faulted module gets no further calls); the three update phases and the sync-point loop, bounded at 64 rounds (deferred
destroys, dirty entities reconciled, `OnReload`, `OnCreate`); what reconciliation does with entries the module cannot
serve (a class the module lacks gets no instance and a problem, a class listed twice on one entity runs once, so
renaming a class detaches it from every entity, as renaming a field loses its value); deferred mutation through
`ScriptSystem::DestroyEntity` and the copies of lists taken before script code runs; the dispatch loop over lists of
only the implementing instances, its skip conditions, activity read from the scene's cache (inactive entities get no
`OnUpdate`, `OnFixedUpdate` or `OnLateUpdate` and no new contacts or animation events, while `OnCreate` and `OnDestroy`
run anyway) and the software prefetch, with why the hardware prefetcher did not help. Update order and its cost:
hierarchy order, then entry order, kept by binary-search insertion, the re-placement of moved entities and lazy
compaction at one eighth destroyed (figure). Contact delivery (every Enter gets its Exit; normals flipped for the other
side); animation and UI events. Fields: per-entity overrides by name and type, live get and set for the inspector and
`script.get`. Assets from game code: an `AssetPin` for each requested asset and a group request for each progress query,
released when play stops, so `Instantiate` never waits; the requests are the scene's, not the script's, and do not add
up, so one `Assets::Release` ends a request that two scripts made. The rule against keeping a `T*` from `GetScript<T>()`
across frames. Tests: `Scripting.Lifecycle`, `Scripting.Order`, `Scripting.Collisions` and the `Perf.Scripting` dispatch
tests. The example is the ThirdPerson sample's `Coin`: its three fields, `OnCreate` that finds the model,
`OnTriggerEnter` and its call to `CourseState`. At the end the reader can predict the order of a scene's callbacks, and
say why a script may destroy the entity whose callback is running.

**Leaves out.**

- The lifecycle as a game maker uses it → `make/script-loop`
- How contacts are found and folded → `physics/contacts-triggers`
- How the UI raises its events → `ui/input`
- How animation events are found → `animation/time-events`
- Replacing instances on a reload → `scripting/hot-reload`
- The host functions that scripts call (`Instantiate` among them) → `scripting/host-api`
- Residency and pins in general → `assets/residency`
- The running copy of Play mode → `editor/play-mode`
- The inspector's Script drawer → `editor-ui/inspectors`

**Fit.** `over`: about 6,700 words against L (5,000). Four concepts, three excerpts, three figures and five rules, with
the callbacks named for track E, take the most words; by S2 the next size, XL (8,000).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scripting:153-154` | feature | home | `RegisterScriptingModule` (the Script component and the "Scripting" scene system) and the Script component itself |
| `scripting:164-169` | feature | home | `ScriptSystem`, update order, dispatch lists, sync points, field values, asset requests |
| `scripting:92` | feature | home | The 15 class callbacks, when each arrived, and the four lists that agree (`StrataScriptClassDesc`, `ScriptCallback`, `CallbackFlag`, `ClassFunctions`) |
| `animation:178` | feature | home | `OnAnimationEvent`: its flag, its thunk and the dispatch from the system's listener to the active scripts on the animator's entity (`Strata/src/Strata/Scripting/ScriptSystem.cpp:389-407`), the example of an event callback |
| `scripting:294` | concept | home | Deferred mutation and safe points: deferred destruction, flagged removals, copies of lists, bounded sync rounds; the mistakes |
| `scripting:299` | concept | home | Update order and its cost: a deterministic order against cache use, incremental maintenance, dispatch lists, prefetching |
| `scripting:326` | concept | home | Serialized fields and the editor: per-entity overrides by name and type; renaming or retyping a field |
| `scripting:334` | concept | home | Asynchronous assets from game code: request early, spawn when loaded, pins, progress of a closure |
| `scripting:379` | code | home | `Strata/src/Strata/Scripting/ScriptSystem.cpp:195-221`: the three update phases; with lines 482-505, the sync point and its bound |
| `scripting:380` | code | home | `Strata/src/Strata/Scripting/ScriptSystem.cpp:241-287`: the dispatch loop, its skip conditions, activity from the cache, software prefetch and why; beside it the rule for inactive entities: no update callbacks and no new contacts or animation events, but `OnCreate` and `OnDestroy` run anyway (`ScriptSystem.h:55-56`; `ScriptSystem.cpp:347-351`, `:394`, `:664-680`; no `Scripting.*` test plays a script on an entity inactive at its start, so the `OnCreate` half is read, not tested) |
| `scripting:382` | code | home | `Strata/src/Strata/Scripting/ScriptSystem.cpp:340-383`: contact delivery, every Enter with its Exit, copies of lists, normals flipped |
| `new:27` | feature | home | Script entries the module cannot serve, beside reconciliation (critic-scripting-8): an entry whose class the module lacks (renamed or deleted) gets no instance and a problem is reported; the same class listed twice on one entity runs once, the duplicate reported; on a hot reload a class that no longer exists loses its instances, with a problem, while its entries stay and get an instance again once a module has the class; so renaming a class detaches it from every entity, as renaming a field loses its value (about 100 words). Evidence: `Strata/src/Strata/Scripting/ScriptSystem.cpp:611-625`, `:1290-1297`, `:1346-1347`; `Strata/src/Strata/Scripting/ScriptEngine.h:60-62` |
| `new:28` | feature | home | A script's asset requests belong to the scene, not to the script, and do not add up: one `Assets::Release` ends a request that two scripts made, and the asset may then be evicted while the other script still uses it; one sentence beside the pins (critic-scripting-17). Evidence: `Strata/src/Strata/Scripting/ScriptSystem.h:131-132`; `StrataScriptCore/Include/StrataScript/Scene.h:44-47` |
| `scripting:411` | figure | home | The instance's states, from constructed to destroyed, with the disabled and the reload branches |
| `scripting:414` | figure | home | A frame from the scripts' side, and where `Time::GetStepAlpha` becomes final |
| `scripting:422` | figure | home | Update order maintenance: the hierarchy, the flat order with its placed part and appended tail, a binary-search insertion, tombstones and the compaction |
| `scripting:464` | rule | home | Script code never runs while engine state it could invalidate is in use: destroy through `ScriptSystem::DestroyEntity` |
| `scripting:474` | rule | home | Never keep a `T*` from `GetScript<T>()` across frames; store the `Entity` |
| `scripting:481` | rule | home | Request assets early; `Instantiate` never waits |
| `scripting:483` | rule | home | Read press and release edges in `OnUpdate`: `OnFixedUpdate` runs zero or more times per frame |
| `scripting:485` | rule | home | Read the drawn pose in `OnLateUpdate`; move ridden platforms in `OnFixedUpdate` (the drawn transforms are `world/interpolation`'s) |
| `scripting:546` | hands-on | home | Measure dispatch: `Perf.Scripting.TrivialUpdate100k` in Release with and without the prefetch lines |
| `scripting:548` | hands-on | home | Why copy the list: find each "A copy" comment of `ScriptSystem.cpp` and build the bug it prevents |
| `scripting:565` | term | link | `AssetPin`: a script's request holds one; the term's entry is on `assets/residency` |
| `scripting:577` | term | home | Dispatch list |
| `scripting:586` | term | home | Field override |
| `scripting:594` | term | home | Instance (of a script class) |
| `scripting:602` | term | home | Prefetch (the CPU's) |
| `scripting:614` | term | home | Sync point |
| `scripting:619` | term | home | Update order |
| `scripting:289` | concept | use | The script lifecycle and its callbacks, named for track E; its home is `make/script-loop` |
| `scripting:385` | code | use | The `Coin` script as the page's example |
| `scripting:341` | concept | link | Interpolation of fixed-step motion, one sentence and a link to `world/interpolation` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Systems, phases and fixed steps in `Scene`; scene services | `world/systems` | must |
| The fixed step, the accumulator and time dilation | `core/time` | must |
| The transform contract and the hierarchy | `world/scene-graph` | must |
| Residency, pins and eviction | `assets/residency` | must |
| Contacts and triggers reaching scripts | `physics/contacts-triggers` | must |
| Animation events | `animation/time-events` | must |
| Calls into a module through `ScriptModule` | `scripting/loading` | must |
| Caches, and why the order of data in memory matters | `basics/computer` | must |
| Arrays, binary search and their costs | `basics/data-structures` | must |
| Interpolation of fixed steps: drawn transforms | `world/interpolation` | helps |
| Reflection and the registry's signals | `world/reflection` | helps |
| UI events reaching scripts | `ui/input` | helps |
| The script lifecycle as game makers learn it | `make/script-loop` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `dispatch-list` | Dispatch list | - |
| `field-override` | Field override | - |
| `instance-scripting` | Instance (scripting) | - |
| `prefetch-scripting` | Prefetch (scripting) | - |
| `sync-point` | Sync point | - |
| `update-order` | Update order | - |
