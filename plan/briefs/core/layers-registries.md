# Brief: `core/layers-registries`

| Field | Value |
| --- | --- |
| Title | Layers, registries and the composition root |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `core/engine-modules`, `basics/data-formats` |
| From | foundation "Layers, registries and the composition root" (§1.1: the composition root, options, state machine, optional modules; §1.10); home of the layer table's rules, optional modules (`ST_WITH_*`), "no tooling in games", registries that open, accept and freeze, and dependency inversion (the CMake that enforces the layers is `engineering/cmake`'s) |
| Unit | `plan/allocation/core.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `core/layers-registries` — Layers, registries and the composition root

**Covers.** The job: how Strata keeps lower code from depending on higher code, and how every module registers once, in
one place, before anything reads a registry. The problem in the part's full section on it: layered architecture and why
lower code must not call higher code; dependency inversion (interfaces below and implementations above, registries
filled from above, services); self-registration through static constructors, common and fragile (the linker drops
objects of a static library that nothing references, and the order of static initialization is undefined), against an
explicit composition root. The map is the layer DAG: 19 layers, the arrows of `MayInclude`, the tooling layers to the
side. The contract, the layers first: `Layers.json` (each layer's `Paths`, `Exclude`, `MayInclude`, `Tooling`, `Option`
and `Notes`; `ExternalOwners`, which keeps GLFW, Vulkan and OS headers in their Platform folders; `MaxAllowlistEntries`
0 and an empty allowlist); the `Architecture.Layering` test, which reads every include and also fails on an allowlist
line that matches no forbidden include, with `Architecture.Libraries` beside it, which checks that every engine source
is in the library of its one layer and that each library links exactly the built layers its layer may include; and the
rule: never widen `MayInclude` or add an allowlist line, invert the dependency. Then the composition root:
`Engine::RegisterBuiltinModules` (it opens the registries, runs the nine modules' registrations from a table in layer
order, refuses to exclude Input, Scene and Renderer, runs the asset pipeline and the `Extra` registrations, freezes the
component and settings registries, logs the order of the scene systems; a second call does nothing but log an error);
`ModuleRegistrationOptions` (`AssetPipeline`, handed in so that games never link the importers; `Extra`; `Exclude`); the
functions that report what registered; the registration state machine (atomic; a registry used before registration fails
a verify that names the root); the two kinds of registry: the component and settings registries open, accept and then
freeze, and a frozen registry needs no lock; the asset loader, asset-manager extension, built-in asset, mesh geometry
and scene-system registries, which the root opens, and the importer registry, which the asset pipeline opens, never
freeze, each with its own lock or rule (tools and tests register more later, a later loader or importer overrides the
built-in one, the loader registry locks on every lookup, a scene system is refused only while a scene runs); optional
modules (`ST_WITH_PHYSICS`, `_AUDIO`, `_ANIMATION`) with `#if` only in the root, the asset pipeline, the runtime and
tests; "no tooling in games" as a rule (its proof in CMake is `engineering/cmake`'s). What Strata does not do here:
engine plugins loaded while the program runs, and a build without scripting. The errata the page must not repeat are
listed below. The toy is a composition root with two registries in 40 lines; the real code is the module table, the body
of `RegisterBuiltinModules` and the start of `Layers.json`. The page's example is the editor's own registration as its
startup log reports it. The exercises: a GLFW include in a Scene file, read from the test's failure and fixed by
inversion; a game component registered through `Extra`, then once more after the freeze; a test helper with
`Exclude = {"Physics"}`; a trace of `RegisterBuiltinModules` from `main` with breakpoints, which writes down which
registries it opens and which two it freezes. At the end the reader can say which layer may include which, fix a
forbidden include by inverting the dependency, and register a game's component or settings section in the right place.

**Leaves out.**

- The CMake that makes the layer libraries and proves that games hold no tooling → `engineering/cmake`
- Precompiled headers and the weight of headers → `engineering/flags-portability`
- `ComponentRegistry`'s builder → `world/reflection`
- The scene-system registry and the order of systems → `world/systems`
- The importer and loader registries → `assets/importing`
- Settings sections and their validation → `world/projects-settings`
- Platform headers in their folders, as a rule of platform code → `core/platform`
- Script modules, the one kind of code loaded while the program runs → `scripting/loading`

**Fit.** `fits`: about 5,800 words against L (5,000). The composition root with the two kinds of registry, and the layer
table with its tests, take the most; four errata, two absences and four exercises follow.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:259` | concept | home | Layered architecture and dependency inversion: interfaces below, registries filled from above, services; the layer table that is the build; the mistake of widening `MayInclude` |
| `foundation:264` | concept | home | The composition root against self-registration through static constructors (dropped by linkers, run in undefined order); the two kinds of registry, those that open, accept and freeze (components and settings, which need no lock once frozen) and those the root opens and leaves open, each with its own lock or rule (asset loaders, importers, built-in assets, manager extensions, mesh geometry, scene systems); the mistakes (registering a component or a settings section after the freeze, or registering from a static constructor) |
| `foundation:173` | feature | home | The layer table and its fields, and the empty allowlist |
| `foundation:175` | feature | home | The `Architecture.*` tests: `Layering`'s include analyzer and `Libraries`; the precompiled-header and header-weight tests are named and left to `engineering/flags-portability` |
| `foundation:176` | feature | home | `ExternalOwners`: GLFW, Vulkan and OS headers only in their Platform folders |
| `foundation:33` | feature | home | The composition root `Engine::RegisterBuiltinModules` |
| `foundation:34` | feature | home | `ModuleRegistrationOptions`: `AssetPipeline`, `Extra` and `Exclude` |
| `foundation:35` | feature | home | `GetBuiltinModuleNames`, `GetRegisteredModules` and `AreBuiltinModulesRegistered` |
| `foundation:36` | feature | home | The optional modules `ST_WITH_PHYSICS`, `_AUDIO` and `_ANIMATION` |
| `foundation:37` | feature | home | The registration state machine and the verify that names the root |
| `foundation:343` | code | home | `Strata/src/Strata/Engine/BuiltinModules.cpp:61-77`: the table of registration functions in layer order, with `#if ST_WITH_*` only here; with `BuiltinModules.cpp:118-174`, open, register and freeze |
| `new:11` | code | home | `StrataTests/Architecture/Layers.json:1-24`: the table's description, `MaxAllowlistEntries` and its first three layers (Core, Input and App) with their `Paths`, `Exclude` and `MayInclude` |
| `foundation:388` | figure | home | The layer DAG: 19 layers, the arrows of `MayInclude`, tooling to the side, the dependencies of Audio and Project on App marked |
| `scene-ecs:447` | figure | home | The registration lifecycle as a state machine, labelled as the component registry's (the settings registry freezes too; the other registries stay open): closed, open (the modules in table order, then the asset pipeline, then `Extra`), frozen, and what fails in each state |
| `worlds-runtime:140` | feature | home | No tooling in games: the runtime links no editor, asset-pipeline or network layer, as the rule this page states |
| `worlds-runtime:453` | rule | home | Games link no tooling: shipped games read cooked packs only |
| `scripting:693` | open | home | Whether a build without scripting is possible: it is not, as `new:10` states with its evidence |
| `foundation:465` | rule | home | Registration only through the composition root, before anything reads a registry; nothing after the freeze of the component and settings registries, the two that freeze (the others stay open, and tools and tests register more into them later) |
| `foundation:468` | rule | home | `#if ST_WITH_<MODULE>` only in the composition root, the asset pipeline, the runtime and tests |
| `foundation:470` | rule | home | Never widen `MayInclude` or add an allowlist line to let a sideways or upward include pass; invert the dependency |
| `foundation:526` | hands-on | home | A GLFW include in a Scene file: the `Architecture.Layering` failure read, then fixed by inversion |
| `foundation:527` | hands-on | home | A game component registered through `ModuleRegistrationOptions::Extra`, then once after the freeze, and the error read |
| `foundation:528` | hands-on | home | `Exclude = {"Physics"}` in a test helper: unknown components and the scripts' message |
| `foundation:549` | term | home | Composition root |
| `scene-ecs:647` | term | home | Composition root, the same entry as `foundation:549` |
| `foundation:551` | term | home | Registry: a table that modules fill at startup; the component and settings registries then freeze, and the others stay open (the definition corrected, R33, D34); `core/map` sets it against EnTT's registry |
| `foundation:553` | term | home | Freeze |
| `foundation:561` | term | home | Layer table (`Layers.json`) |
| `foundation:562` | term | home | Allowlist |
| `foundation:563` | term | home | Tooling layer |
| `foundation:564` | term | home | Dependency inversion |
| `foundation:702` | open | home | The drift the survey saw in the comments of `Engine/BuiltinModules.h`, stated as `new:6`; its other half, the roadmap's count of built-in stages, is `new:15` on `core/profiling` |
| `new:6` | erratum | home | The comment at `BuiltinModules.h:26-27` names six modules (Scene, Renderer, Physics, Audio, Animation, Scripting); the table registers nine, with Input, World and GameUI; `BuiltinModules.cpp:80` refuses to exclude Input, Scene and Renderer, while `BuiltinModules.h:21-22` names only Scene and Renderer. The page states the table's facts. Evidence: `Strata/src/Strata/Engine/BuiltinModules.h:21-27`; `Strata/src/Strata/Engine/BuiltinModules.cpp:61-80` |
| `new:7` | erratum | home | `SceneRegistration.h:6-8` names one settings section, the collision layers; `SceneRegistration.cpp:22` also registers `Scene.Timing`. Where the page shows a module's registration, it names both. Evidence: `Strata/src/Strata/Scene/SceneRegistration.h:6-8`; `Strata/src/Strata/Scene/SceneRegistration.cpp:22` |
| `new:8` | erratum | home | The foundation inventory counts 21 layers (its line 173); the table has 19, three of them tooling. Evidence: `StrataTests/Architecture/Layers.json:5-125`, which holds 19 `"Name"` entries (`grep -c '"Name"' StrataTests/Architecture/Layers.json` prints 19) |
| `new:9` | not-done | home | No engine plugins loaded while the program runs: modules are chosen when the engine is compiled (`ST_WITH_*`), and only script modules load at run time. Evidence: `Strata/src/Strata/Engine/BuiltinModules.cpp:61-77`, a table fixed at compile time; `git grep -lw DynamicLibrary 822a7a46 -- Strata/src` finds it only in its own files (`Core/DynamicLibrary.*`, `Platform/*/*DynamicLibrary.cpp`), in the script modules' code (`Scripting/ScriptModule.cpp`, `Scripting/ScriptModule.h`, `Scripting/ScriptEngine.cpp`, `Project/Project.cpp`) and in the Vulkan loader (`Platform/Vulkan/VulkanLoader.cpp`) |
| `new:10` | not-done | home | No build without scripting: physics, audio and animation can be left out, scripting cannot. Evidence: `Docs/Releases/0.7.0.md:404`; `Strata/src/Strata/Engine/BuiltinModules.cpp:74`, Scripting outside every `#if` |
| `new:27` | erratum | home | `plan/inventory/foundation.md:264-266`, `:465-466` and `:551-552` say that Strata's registries open, accept and then freeze: only the component and settings registries freeze; the asset loader, asset-manager extension, built-in asset, mesh geometry and scene-system registries, which the root opens beside the component registry, and the importer registry, which the asset pipeline opens, stay open. The page teaches the two kinds (process.md's row of kind `inventory`). Evidence: `Strata/src/Strata/Engine/BuiltinModules.cpp:134-139`, `:159-160`; `Strata/src/Strata/Asset/AssetImporters.cpp:161`; `Strata/src/Strata/Asset/AssetManager.cpp:105-124` (the loader registry locks on every lookup); `Strata/src/Strata/Scene/SceneSystem.cpp:166-178`; `Docs/Architecture.md:703-705`; `git grep -n "void Freeze\|::Freeze()" 822a7a46 -- Strata/src` finds only `ComponentRegistry` and `SettingsRegistry` |
| `new:28` | hands-on | home | Trace it yourself: `Engine::RegisterBuiltinModules` followed with breakpoints from `main`, the registries it opens, the modules in table order, the asset pipeline and `Extra`, and the two registries it freezes, written down and compared with the startup log's line of modules and scene systems. Evidence: `Strata/src/Strata/Engine/EntryPoint.h:29-30`; `Strata/src/Strata/Engine/BuiltinModules.cpp:118-174` |
| `foundation:174` | feature | use | `strata_add_layer_libraries`, named as what makes a library of each layer; `engineering/cmake` teaches it |
| `foundation:177` | feature | use | The link closure and the linker-map check, named as the proof of "no tooling in games"; `engineering/cmake` teaches them |
| `build-test:180` | feature | home | `Architecture.Layering`, as the build's inventory describes it: includes checked against `Layers.json`, a stale allowlist line fails, `ExternalOwners`; taught with `foundation:175` |
| `build-test:181` | feature | home | `Architecture.Libraries`: every engine source in the library of its one layer, and each library linking exactly the built layers its layer may include, read from the `LayerLibraries.json` that the configure step writes (`engineering/cmake` teaches the writing) |
| `build-test:494` | rule | home | Never widen `MayInclude` or add an allowlist line to make an include pass; invert the dependency: the same rule as `foundation:470`, with the build's reason that the table is the build |
| `build-test:652` | term | home | Four entries: layer table, `MayInclude`, `Tooling` and `Option` (the CMake option that builds a layer); the first and the third are the entries of `foundation:561` and `foundation:563` |
| `build-test:654` | term | home | Composition root, the same entry as `foundation:549` |
| `build-test:32` | feature | use | The CMake options that leave the optional modules out |
| `build-test:491` | rule | use | `ST_WITH_*` are compile definitions, never macros of a header |
| `build-test:496` | rule | use | Games link no tooling, the same rule from the build's side |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Engine modules: `EngineModule` against `Register<Module>Module` | `core/engine-modules` | must |
| "Module", "layer", "registry" and "service" in their two meanings | `core/map` | must |
| Static libraries and linking | `basics/build` | must |
| `#include`, `#if` and macros | `basics/cpp-modern` | must |
| Interfaces and virtual calls | `basics/cpp-classes` | must |
| Atomics, acquire and release | `basics/threads` | must |
| JSON | `basics/data-formats` | must |
| Writing and running one test case | `core/first-change` | must |
| Function pointers | `basics/cpp-generic` | helps |
| Static initialization and its order | `basics/build` | helps |
| Components, asset loaders and scene systems, as what the registries hold | `world/ecs` | helps |
| The test program's helpers, for the third exercise | `engineering/test-program` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `allowlist` | Allowlist | - |
| `composition-root` | Composition root | - |
| `dependency-inversion` | Dependency inversion | - |
| `freeze` | Freeze | - |
| `layer-table` | Layer table | `Layers.json`, layering test |
| `registry` | Registry | - |
| `tooling-layer` | Tooling layer | - |
