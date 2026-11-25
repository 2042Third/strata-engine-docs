# Brief: `scripting/tutorial-host-function`

| Field | Value |
| --- | --- |
| Title | Tutorial: adding a host function and a callback |
| Kind | T |
| Size | L |
| Tracks | E |
| Needs | `scripting/host-api`, `world/tutorial-component`, `core/first-change` |
| From | scripting ch. 15, the tutorial half (hands-on E2-E3): the WindZone gets `Wind::GetStrength`, and a callback is appended to `StrataScriptClassDesc` |
| Unit | `plan/allocation/scripting.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `scripting/tutorial-host-function` — Tutorial: adding a host function and a callback

**Covers.** What the reader makes: the WindZone of `world/tutorial-component` becomes readable from scripts through a
new host function behind `Wind::GetStrength`, and scripts hear about wind through a callback appended to
`StrataScriptClassDesc`. Every step follows the newest group of the table (`GetStepAlpha` and its neighbours, wave 8) as
its model, quoted beside the reader's change. Section 1, the host function: append the member at the end of
`StrataScriptHostAPI` and see the build fail at the `static_assert` of `ST_SCRIPT_HOST_FUNCTIONS` (a text capture);
reach the zones through a new scene service, because the WindZone is the Physics module's and Scripting may include only
Core, Input, Asset, Reflection and Scene (`StrataTests/Architecture/Layers.json:76-78`): an interface in
`Scene/SceneServices.h` that the WindZone's system registers in its constructor and unregisters in its destructor, as
`PhysicsSystem` does with its services, and that the host function looks up with `GetService`, reporting the absent
service when no system offers it, so that `Architecture.Layering` passes; implement the host function with `HostCall`,
`ResolveContext` and `ReportProblem`; list it at the end of the X-macro; wrap it in the SDK with
`ST_SCRIPT_DETAIL_HOST_WITH`, so a module built for this engine still runs on an older one; call it from the API test
module with the "older engine" check, and from a `Scripting.*` test; call it from a feature script and run the feature
test, which fails before the call and passes after it (two sentences say what the feature test checks of a new host
function and link `engineering/feature-test`, which teaches it). Section 2, the callback: append it to
`StrataScriptClassDesc` and to `ScriptCallback` (whose `c_ScriptCallbackCount` follows the last value); in the SDK, its
virtual function, `CallbackFlag`, override check, thunk and slot in `BuildClassRecord`; in the engine, its member of
`ClassFunctions`, read only when the module's `StructSize` covers it; dispatch it from the system that raises it; test
it, with a module that lacks it. Each section ends with its patch's checkpoint and the test output as a text capture.
Every step is a code change, a build or a test run from a terminal; no step needs an editor command. Exercises: a second
host function of the reader's choice (a `Game::GetLanguage`), and the WindZone's `ReportProblem` cases. At the end the
reader has a patch that keeps `ST_SCRIPT_ABI_VERSION` at 1 and passes `Architecture.Layering`, `Physics.WindZone`, the
new tests and the feature test.

**Leaves out.**

- The WindZone component and its system → `world/tutorial-component`
- The WindZone's gizmo, the exercise whose solution this page starts from → `gpu/debug-drawing`
- Scene services in general and where each is implemented → `world/systems`
- The rules and guards of host functions → `scripting/host-api`
- The feature test in full → `engineering/feature-test`
- The `wind.*` commands → `editor/tutorial-command`
- Forces on bodies and the WindZone as a whole feature → `capstone/build`

**Fit.** `fits`: about 5,300 words against L (5,000). Two changes end to end, about 16 steps with their build or test
output and eight short model excerpts take the most words, the scene service's step of D38 the longest.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scripting:534` | hands-on | home | Add a host function end to end: the ABI, the implementation, the X-macro (the `static_assert` failing first), the SDK wrapper, the API module, a `Scripting.*` test, a feature script |
| `scripting:538` | hands-on | home | Add a callback: the descriptor, `ScriptCallback`, `CallbackFlag`, `ClassFunctions` with `ST_SCRIPT_HAS_MEMBER`, a thunk, the dispatch |
| `gamedev:558` | hands-on | home | The page's "make it yours" exercise: a second host function (`Game::GetLanguage`) added the same way |
| `animation:508` | hands-on | home | A harder exercise: a new `IAnimatorControl` query (`GetStateDuration`) end to end, through the scene service, the system, the host function, the SDK, a `Scripting.*` test and a feature script |
| `scripting:345` | concept | use | The feature test's coverage of host functions, SDK functions and callbacks, applied in the feature-script step: two sentences say what the reader adds and link forward to `engineering/feature-test`, the concept's home |
| `scripting:496` | rule | use | Every new host function, SDK function, callback and field type is exercised by the feature test, applied in the feature-script step; the rule box is on `engineering/feature-test` |
| `new:11` | code | home | `StrataScriptCore/Include/StrataScript/ScriptABI.h:739-755`: the newest group with its "check `ST_SCRIPT_HAS_MEMBER` before use" comment, and the line where new functions are appended |
| `new:12` | code | home | `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:3378-3386`: `HostGetStepAlpha`, the model of a small host function and its failure value |
| `new:13` | code | home | `StrataScriptCore/Include/StrataScript/Time.h:70-76`: the SDK's wrapper with `ST_SCRIPT_DETAIL_HOST_WITH` and its fallback value |
| `new:14` | code | home | `StrataTests/Scripts/API/TransformScripts.cpp:93-116`: the API module checks what an older engine gives (a table cut before the function, and null entries) |
| `new:15` | code | home | `StrataTests/src/Scripting/ScriptAPITests.cpp:231-266`: the `Scripting.API` test case of the newest group |
| `new:16` | code | home | `Strata/src/Strata/Scripting/ScriptModule.cpp:998-1016`: appended callbacks read only when the module's descriptor holds them |
| `new:17` | code | home | `Strata/src/Strata/Scripting/ScriptTypes.h:16-41`: `ScriptCallback` and `c_ScriptCallbackCount`, defined from the last value |
| `new:19` | code | home | `Strata/src/Strata/Scene/SceneServices.h:19-33`: the contract of scene services (a system registers its interface while it exists, others look it up and get null when no system offers it), the model of the WindZone's service (R32, D38); with `Strata/src/Strata/Physics/PhysicsSystem.cpp:58-80` (services registered in the constructor and unregistered in the destructor) and `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:1176-1180` (a host function's lookup) |
| `scripting:450` | rule | use | Append, never insert: the reason the reader appends at both ends |
| `scripting:452` | rule | use | `ST_SCRIPT_HAS_MEMBER` before an appended function or callback |
| `scripting:459` | rule | use | `HostCall` and `ResolveContext` in the new function |
| `scripting:201` | feature | use | The layer rule of Scripting, which is why the WindZone needs a scene service: Physics is no layer that Scripting may include |
| `scripting:377` | code | use | The X-macro table and its check, whose end the reader extends (`ScriptHostAPI.cpp:3594-3596`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Building Strata from source; one test case written and run | `core/first-change` | must |
| The WindZone component and its system; the feature test's minimum | `world/tutorial-component` | must |
| `HostCall`, `ResolveContext`, `ReportProblem`, the X-macro table and its `static_assert` | `scripting/host-api` | must |
| `ST_SCRIPT_HAS_MEMBER`, `StructSize`, append-only structs, the SDK's thunks and callback flags | `scripting/abi-sdk` | must |
| Dispatch lists and the order of callbacks | `scripting/script-system` | must |
| Scene services | `world/systems` | must |
| The layer table and dependency inversion | `core/layers-registries` | must |
| The feature test's coverage checks | `engineering/feature-test` | helps |
| A patch and git | `basics/git` | helps |
| The WindZone's gizmo, the solution of `gpu/debug-drawing`'s exercise | `gpu/debug-drawing` | helps |

**Starting state.** The source build of `core/first-change` at the pin with the WindZone chain applied up to the
solution of `gpu/debug-drawing`'s exercise: the tutorial file's `startsFrom` is `{"tutorial": "gpu/debug-drawing",
"exercise": <n>}` (R41; `pipelines.md` §6), so the runner replays `gpu/debug-drawing`, which starts from
`world/tutorial-component`, and applies its `exercise-<n>.patch`, the one that gives the WindZone its gizmo. The
WindZone component and its system are registered, the zone draws its gizmo, and its serialization round trip and the
feature test's minimum pass (`Physics.WindZone`). A reader who skipped the exercise applies its solution patch. No
project or editor checkpoint is used.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.
