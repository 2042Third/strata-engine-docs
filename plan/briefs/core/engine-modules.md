# Brief: `core/engine-modules`

| Field | Value |
| --- | --- |
| Title | Engine modules |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `core/frame-loop`, `basics/trees-graphs` |
| From | foundation "Engine modules" (§1.3; device creation in detail is `gpu/vulkan-nvrhi`'s); home of engine services and of the topological sort (Kahn); the exercise: write a `FrameCounterModule` |
| Unit | `plan/allocation/core.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `core/engine-modules` — Engine modules

**Covers.** The job: how the services that live as long as the program (the graphics device, audio, ImGui, the
project) start in order, run their hooks every frame, stop in reverse, fail cleanly, and are found by other code. The
problem in the part's full section on it: subsystems and their lifecycles (init calls written out in `main`, singleton
managers with start and stop functions, module systems such as Unreal's `IModuleInterface`, service locators), the
order problem, and a module that frees GPU resources after the device is gone. Then the topological sort from zero, as
its home: a graph of "starts after", in-degrees, Kahn's algorithm worked on the test's four modules (C needs A; A; B
after C, optional; D after a missing module, optional: the order A, C, B, D), stability (the first ready module in the
program's listing order) and cycles reported by their members only. The map is the hook order of two modules where B
depends on A. The contract: the `EngineModule` hooks (`OnInit`, `GetStartFailure`, `OnBeginFrame` with Continue, Skip
or Close, `OnUpdate`, `OnRenderUI`, `OnEndFrame`, `OnEvent`, `OnStop`, `OnRelease`, `OnShutdown`), `c_Name` and
`GetDependencies` with `Required`; `EngineContext`, `EngineFrame`, `EngineFrameAction` and `EngineModuleStartFailure`;
`EngineModuleRegistry` (made from factories; it refuses null factories, duplicate names, missing required dependencies
and cycles; `Find<T>()` finds by `T::c_Name`, without RTTI); the rules (`Application` never names a module, and
`Find<T>()` may return null; a module that fails `OnInit` cleans up and describes the failure; `OnRelease` comes before
`JobSystem::Shutdown`, `OnShutdown` after). The built-in modules (Graphics, Audio, ImGui and Project) and the programs'
module lists (the editor with a window, headless and without a GPU; the runtime with a window and headless); where the
device is made, in one paragraph. Engine services, as their home: typed slots for the whole process (`Register<T>`,
`Get<T>`, `ScopedProvider<T>`) for what a module cannot include (`IGameWindow`, `IGameSaves`, `IGameGraphics`,
`IProjectSettings`, `IAudioOutput`, `IAssetGraphics`), a minimal service locator. The toy is Kahn's sort in 30 lines;
the real code is the hook interface, the registry's sort and its cycle report, `EngineServices.h`, and `ProjectModule`,
the smallest real module. The required exercise: write a `FrameCounterModule` (`c_Name`, `Factory`, `OnUpdate`
counting frames, `OnStop` logging), find it with `Find<T>()`, and test it in the style of `EngineModuleTests.cpp`'s
journaling module; two more exercises: a module that depends on "Graphics" and one whose optional dependency is
missing, with a cycle's message; a module that skips every tenth frame; and a trace of the editor's module list from
`EditorApplication.cpp` through the registry's sort to `StartModules`, with breakpoints. At the end the reader can
write, order and test an engine module, and find a service without naming its module.

**Leaves out.**

- How the graphics device and the swapchain are made → `gpu/vulkan-nvrhi`
- The audio engine behind the Audio module → `audio/engine`
- ImGui's module and backends → `editor-ui/imgui-backends`
- Projects and their settings, behind the Project module → `world/projects-settings`
- Registration into registries and the composition root → `core/layers-registries`
- Scene services → `world/systems`
- Graphs and their costs in general → `basics/trees-graphs`

**Fit.** `fits`: about 5,150 words against L (5,000). The two concepts taught from zero (Kahn's algorithm has its home
here) and the hooks' contract with four quotes take the most; the four exercises, the required one with a patch as its
worked solution, take about 1,000.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:249` | concept | home | Subsystems and their lifecycles: the approaches engines use and their costs; the module that frees GPU resources too late |
| `foundation:256` | concept | home | Topological sorting from zero: graphs, in-degrees, Kahn's algorithm, stability, cycles and their report |
| `foundation:65` | feature | home | The `EngineModule` interface and its hooks |
| `foundation:66` | feature | home | `EngineContext`, `EngineFrame`, `EngineFrameAction` and `EngineModuleStartFailure` |
| `foundation:67` | feature | home | `EngineModuleRegistry`: the stable sort, the refusals, `Find<T>()` without RTTI |
| `foundation:68` | feature | home | The built-in modules Graphics, Audio, ImGui and Project, a paragraph each; each module's details are its part's |
| `foundation:69` | feature | home | The programs' module lists |
| `foundation:71` | feature | home | `EngineServices`: typed provider slots, scoped providers and the interfaces they hold |
| `foundation:348` | code | home | `Strata/src/Strata/Core/EngineModule.h:22-106`: a lifecycle interface whose comments state the hooks' contract |
| `foundation:349` | code | home | `Strata/src/Strata/Core/EngineModule.cpp:49-186`: the registry's `Create`, with Kahn's sort taking the first ready module in listing order and a report that names only a cycle's members |
| `foundation:371` | code | home | `Strata/src/Strata/Core/EngineServices.h:21-69`: a minimal typed service locator with variable templates and scoped providers |
| `foundation:399` | figure | home | The hook order in two lanes, A and B where B depends on A, as `EngineModuleTests.cpp` proves it |
| `foundation:402` | figure | home | Kahn's algorithm worked on the test's four modules |
| `foundation:456` | rule | home | `Application` never names a module; `GetModules().Find<T>()` may return null |
| `foundation:458` | rule | home | A module that fails `OnInit` cleans up what it started and describes the failure |
| `foundation:461` | rule | home | `OnRelease` comes before `JobSystem::Shutdown`, `OnShutdown` after |
| `foundation:515` | hands-on | home | The required exercise: a `FrameCounterModule`, found with `Find<T>()` and tested in the style of `EngineModuleTests.cpp`; its worked solution is a patch against the pin |
| `foundation:516` | hands-on | home | A module that depends on "Graphics", one whose optional dependency is missing, and a cycle's message |
| `foundation:517` | hands-on | home | A module that skips every tenth frame, and the frame count that results |
| `new:26` | hands-on | home | Trace it yourself: the editor's modules followed with breakpoints from the list `EditorApplication.cpp` builds (Graphics unless `--no-gpu`, Audio, ImGui with a window, Project) through `EngineModuleRegistry::Create`'s sort to `StartModules`, the order written down and compared with the dependencies. Evidence: `StrataEditor/src/EditorApplication.cpp:330-345`; `Strata/src/Strata/Core/EngineModule.cpp:49-186`; `Strata/src/Strata/Core/Application.cpp:126-160` |
| `foundation:557` | term | home | Hook |
| `foundation:566` | term | home | Service locator |
| `foundation:567` | term | home | Topological sort |
| `foundation:568` | term | home | Kahn's algorithm |
| `foundation:554` | term | home | Engine module (`EngineModule`): a service that lives as long as the program; `core/map` sets it against the module's registration |
| `foundation:565` | term | home | Engine service (`EngineServices::Get<T>`), the engine's meaning of "service"; `core/map` sets it against the scene service |
| `scene-ecs:646`, `scripting:580` | term | home | Engine service, the same entry as `foundation:565`'s second term |
| `foundation:373` | code | use | Its pieces about modules: `Strata/src/Strata/Project/ProjectModule.cpp` 10-24 (the smallest real module, the exercise's model), `Strata/src/Strata/Renderer/GraphicsModule.cpp` 26-85 (a module that reports waits and start failures) and `StrataTests/src/Core/EngineModuleTests.cpp` 62-120 and 289-334 (the journaling test module); the item's home is `core/math` |
| `foundation:70` | feature | use | Where the device is made, in one paragraph; the detail is `gpu/vulkan-nvrhi`'s |
| `render-core:52` | feature | use | `GraphicsModule`, the module with the most hooks, as the example of a real module's frame |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Graphs and dependency graphs | `basics/trees-graphs` | must |
| Virtual functions and interfaces | `basics/cpp-classes` | must |
| `Scope`, `unique_ptr` and factories | `basics/cpp-memory` | must |
| Templates and `std::function` | `basics/cpp-generic` | must |
| The startup that makes, orders and starts the modules | `core/first-frame` | must |
| The frame loop that calls the hooks | `core/frame-loop` | must |
| Writing and running one test case | `core/first-change` | must |
| Events and `Handled`, for `OnEvent` | `core/windows-events` | helps |
| The graphics device | `gpu/vulkan-nvrhi` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `engine-module` | Engine module | EngineModule |
| `hook` | Hook | - |
| `kahns-algorithm` | Kahn's algorithm | - |
| `service` | Service | - |
| `service-locator` | Service locator | - |
| `topological-sort` | Topological sort | - |
