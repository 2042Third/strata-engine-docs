# Brief: `scripting/host-api`

| Field | Value |
| --- | --- |
| Title | The host API: engine services behind a C table |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `scripting/script-system`, `core/engine-modules`, `core/layers-registries` |
| From | scripting ch. 15, the internals half (`ResolveContext`, `HostCall`, validation and `ReportProblem`, the X-macro table `ST_SCRIPT_HOST_FUNCTIONS` in `Scripting/ScriptHostAPI.cpp` and its `static_assert`, call counters and Dist, services and layering; code #22-#24, concept 16) |
| Unit | `plan/allocation/scripting.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `scripting/host-api` — The host API: engine services behind a C table

**Covers.** The job: give game code the engine's services through one C table, without letting it see an engine
header. The pattern, the full section: a table of function pointers and an opaque context, as plug-in SDKs and
Vulkan's loader do, and why (isolation, safe reloads, testing by counting calls). A host call round trip in the order
data flows (figure), walked from the SDK's side (`Entity::SetProperty` and `GetProperty`, `ValueTraits`, the second
read for long strings) to the counted thunk, `HostSetProperty`, `HostCall`, `ResolveContext` and the component access,
with every failure exit. The toy: a table of two functions with a context check, about 50 lines. Then the real code.
The two guards every host function starts with: `ResolveContext` against the registry of contexts (no context, another
thread, a stale context, no call in progress, a faulted module) and `HostCall` (no exception unwinds into the module).
Validation and `ReportProblem`: what the host reports (the list), a warning that names the calling script and entity,
once per message, at most 1,024 per scene; and why a host function never asserts. A tiny host function
(`SetTimeScale`) and a real one (`Instantiate`, which starts the load and returns no entity until the asset is
loaded, and creates the new entities' instances at once). The X-macro table `ST_SCRIPT_HOST_FUNCTIONS`, the `constexpr`
check that it covers the struct exactly, the counted thunks, and Dist builds without counters. The gameplay API as a
facade: Scripting may include only Core, Input, Asset, Reflection and Scene, so every gameplay function goes through
a scene service or an engine service and fails, reported, when the service is absent, as the host's own messages say:
an engine without the physics, audio or animation module ("the scene plays without physics (the engine has no physics
module)"), a scene that streams no world ("the scene streams no world"), a program with no window or no save directory
("the program running the game has no save directory"); scripts never run in Simulate; the table's 27
groups, the service each reaches and the wave each arrived in, up to 165 functions. Player-facing services: save
files, rebindable input, graphics options and the window, each with one owner of its file. The save service as the
example: the save functions ask `IGameSaves` for the directory and call `SaveFiles`, which checks a name in the engine
before any path is formed (1 to 64 ASCII characters, no `..`, no device name), writes atomically, refuses more than
64 MiB and blocks the main thread; `SaveDirectory` is what a shipped game provides, found on first use, and the
editor's play mode keeps saves in the project's `.strata/Saves`. Value conversion: exact for
fields, lenient for component properties (integers for enums, three or four numbers for colors, a vector or a
quaternion for rotations). Tests: the `Scripting.*` suites, which page each belongs to, and the call counters the
feature test reads. The example is `Time::SetTimeScale`, followed from the SDK to `HostSetTimeScale` (the trace
exercise). At the end the reader can say what a host function must do before it touches the engine, which service it
must go through, and where a new one must be listed.

**Leaves out.**

- Every host function and SDK call with its failure value → `reference/script-api`
- Adding a host function step by step → `scripting/tutorial-host-function`
- Scene services and where each is implemented → `world/systems`
- Engine services and engine modules → `core/engine-modules`
- The script face of physics queries → `physics/queries`
- The script face of audio → `audio/scene-system`
- The script face of animators → `animation/system`
- The script bridge of the game UI → `ui/input`
- The script face of world streaming → `worlds/physics-scripts`
- Players' graphics options → `image/quality-settings`
- The feature test's coverage checks → `engineering/feature-test`

**Fit.** `fits`: about 6,200 words against L (5,000). Four excerpts, the round-trip figure, the table of 27 groups and
the save service take the most words; the subsystems' script faces are linked, not taught.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scripting:63-90` | feature | home | The 27 groups of the host table as one table: their functions, the service each reaches, the wave each arrived in |
| `scripting:170-174` | feature | home | `ReportProblem`, the host API's implementation, the registry of contexts, the call counts, value conversion |
| `scripting:177` | feature | home | The problems the host reports |
| `scripting:199-201` | feature | home | The engine services and the scene services the host API goes through, and the layer rule that forces them |
| `scripting:216` | feature | home | The `Scripting.*` suites and the other tests of the part, each named with its page |
| `scripting:273` | concept | home | The host API as a service table: the pattern, why, and the mistake of calling the engine from other threads or outside callbacks |
| `scripting:330` | concept | home | The gameplay API as a facade over engine services, taught once; each subsystem's page shows its script face |
| `scripting:338` | concept | home | Player-facing systems: saves, rebindable input, graphics options, the window; one service owns each file |
| `foundation:130` | feature | home | The save service behind the save functions: `SaveFiles` (names checked before a path is formed, atomic writes, the 64 MiB cap, calls that block) and `SaveDirectory`, the `IGameSaves` a shipped game provides (`Strata/src/Strata/Core/SaveFiles.h:14-65`, `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:2224-2262`); where an exported game's saves go is `worlds/game-identity`'s |
| `audio-input:365` | concept | home | Crossing the script ABI for audio and input: action names and bindings as strings, the text buffer protocol, failure values and `ReportProblem`; one instance of the facade, whose audio and input sides `audio/scene-system` and `input/actions` show |
| `animation:176` | feature | home | The twelve animator host functions, one row of the groups table |
| `animation:179` | feature | home | The animator functions' misuse reporting (`RequireAnimation`, `RequireAnimator`, `ControlAnimator` inside `HostCall`), an example of a subsystem's guards |
| `audio-input:543` | rule | home | Host functions report misuse and return failure values, as the input area states it; one rule box with `scripting:459` |
| `scripting:375` | code | home | `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:67-116`: `ResolveContext` and `HostCall` |
| `scripting:376` | code | home | `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:356-370`: `SetTimeScale`, input checked and reported; with lines 830-897, `Instantiate`, which never waits |
| `scripting:377` | code | home | `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:3598-3622`: the `constexpr` check that the list covers the struct; with lines 3427-3437 (the head of the X-macro) and 3624-3672 (counted thunks, and Dist without counters) |
| `gamedev:363` | code | home | `StrataScriptCore/Include/StrataScript/Entity.h:358-396`: `GetProperty` and `SetProperty`, the SDK's side of a host call, with the stack buffer and the second read; with `Host.h:19-24` and `105-111` (the table pointer and `ST_SCRIPT_DETAIL_HOST_WITH`), which `scripting/abi-sdk` showed |
| `scripting:408` | figure | home | A host call round trip, with the failure exits |
| `scripting:459` | rule | home | Host functions wrap their body in `HostCall`, start with `ResolveContext`, report misuse, return failure values and never assert |
| `scripting:462` | rule | home | The engine is single-threaded towards scripts: call it only from callbacks, never from your own threads |
| `scripting:487` | rule | home | Input actions for anything a player might rebind; one owner for the bindings file, the graphics options file and the saves |
| `scripting:498` | rule | home | Field values convert exactly, component properties leniently |
| `scripting:532` | hands-on | home | Trace one host call: `Time::SetTimeScale` from the SDK to `HostSetTimeScale` and its counted thunk, each guard explained |
| `scripting:590` | term | home | Host function |
| `gamedev:607` | term | home | Host function, as a game maker's guide names it; one entry with `scripting:590` |
| `audio-input:692` | term | home | Host function, as the input area names it; one entry with `scripting:590` |
| `scripting:604` | term | home | ReportProblem |
| `scripting:621` | term | home | X-macro |
| `scripting:687` | open | home | When the first groups arrived (physics, queries, audio, game flow before 0.3.0): the page checks the release notes and the Roadmap at the pin, and states only what they say |
| `new:18` | erratum | home | Concept 16 of `plan/inventory/scripting.md` (lines 330-333) gives Simulate as the case where a gameplay service is absent (`process.md`'s table of errata, kind `inventory`); scripts never run in Simulate, since the Scripting system runs only in Play, and a host function reports an absent service when the engine has no physics, audio or animation module, when the scene streams no world, or when the program has no window or no save directory. Evidence: `Strata/src/Strata/Scripting/ScriptingRegistration.cpp:15-17`; `Strata/src/Strata/Scripting/ScriptSystem.h:37-38`; `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:1172-1174`, `:2150`, `:2230`, `:2649` |
| `scripting:53` | feature | use | The host table as a struct (its home is `scripting/abi-sdk`) |
| `scripting:118-136` | feature | link | The SDK's gameplay classes, each named with its group and linked to its home: the subsystems' pages for the classes with a twin, `make/scripting-scene`, `basics/programming-1`, `make/levels-saves`, `make/recipes` and `make/timers-events` for the others, `image/quality-settings` for `Graphics`, `worlds/physics-scripts` for `World`; `reference/script-api` lists their facts |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Engine services and engine modules | `core/engine-modules` | must |
| The composition root, dependency inversion and the layer table | `core/layers-registries` | must |
| Scene services | `world/systems` | must |
| The host table, the buffer protocol and `ST_SCRIPT_DETAIL_HOST_WITH` | `scripting/abi-sdk` | must |
| Contexts, call sites and instances of the script system | `scripting/script-system` | must |
| Reflection: components and properties by name | `world/reflection` | must |
| Macros and `constexpr` | `basics/cpp-modern` | must |
| Atomics and relaxed counters | `basics/threads` | helps |
| Residency and loading without stalling | `assets/residency` | helps |
| Input actions | `input/actions` | helps |
| Players' graphics options | `image/quality-settings` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `host-function` | Host function | - |
| `reportproblem` | ReportProblem | - |
| `x-macro` | X-macro | - |
