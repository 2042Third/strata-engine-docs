# Brief: `core/map`

| Field | Value |
| --- | --- |
| Title | How Strata is put together: programs, libraries, modules and layers |
| Kind | C |
| Size | M |
| Tracks | E |
| Needs | `basics/build`, `start/what-an-engine-is` |
| From | foundation "What an engine is, and how Strata is put together" (second half); home of "module", "layer", "registry" and "service" (two meanings each) |
| Unit | `plan/allocation/core.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `core/map` — How Strata is put together: programs, libraries, modules and layers

**Covers.** The page starts from what the reader did in `start/first-game`: they started the editor, played a copy of
Tetris and built the `Spinner` script. It asks where "the engine" was in all that. The naive picture, that the editor
is the engine and everything is one big program, breaks at once: a shipped game runs without the editor. The idea: an
engine is a set of libraries, programs are built on them, and game code is a module of its own. The approaches engines
use, with a table of their costs: one program with the tools inside; engine libraries under several programs; modules
and plugins loaded while the program runs. Strata's choice: one static library per architecture layer
(`Strata_<Layer>`), under three programs (`StrataEditor`, `StrataRuntime`, `StrataCLI`) and the test program
`StrataTests`; game code in script modules built against `StrataScriptCore` alone; and a runtime that holds no editor
code, which a test proves (named in one sentence). The repository's top folders are drawn onto that picture. Then the
four words with two meanings each: "module" (the code of an engine module and its `Register<Module>Module`, against
the `EngineModule` service that lives as long as the program; and the script module, a third use), "layer" (a row of
the layer table and a static library, against an application `Layer` in the `LayerStack`), "registry" (Strata's tables
that modules fill at startup, of which the component and settings registries then freeze, against EnTT's registry of
a scene's entities) and "service" (an engine service of `EngineServices`, against a scene service of `Scene`), each
with the page that teaches it. The common mistakes: taking the editor for the engine, and reading one meaning of a word
where the other is meant. The exercises: files placed in their program and library from the layer table, and the
installed programs' `--help` compared in a terminal. At the end the reader can say which program and which library a
piece of Strata belongs to, and uses the four words without mixing their meanings.

**Leaves out.**

- How the layer table is enforced and what each layer may include → `core/layers-registries`
- The CMake that makes one library per layer, and the proof that games hold no tooling → `engineering/cmake`
- What the `EngineModule` hooks do and in which order → `core/engine-modules`
- How a script module is loaded and called → `scripting/loading`
- The tree below the top folders → `core/reading-code`
- Compiling, linking and libraries in general → `basics/build`

**Fit.** `fits`: about 3,700 words against M (3,000). The four words with their two meanings take the most, about 800,
then the approaches with their table and Strata's choice; the two exercises take about 500.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:208` | concept | home | What a program is and what an engine adds, the Strata half: three programs over one set of static layer libraries, game code in separately loaded script modules, the runtime without editor code; the general half (process, `main`, static and shared libraries) comes from `basics/build` |
| `foundation:385` | figure | home | The diagram of executables and layer libraries: the editor, the runtime, the CLI and the tests over `Strata_<Layer>`, the tooling layers to the side, script modules linking only `StrataScriptCore` |
| `foundation:555` | term | home | Engine module registration (`Register<Module>Module`), the meaning of "module" that is set against the `EngineModule` object; the page adds the script module as a third use |
| `foundation:558` | term | home | Two glossary entries: layer (application), a slice of a program in the `LayerStack`, and architecture layer, a row of `Layers.json` and a static library |
| `scene-ecs:648` | term | home | Architecture layer, the same entry as the second term of `foundation:558` |
| `build-test:651` | term | home | Layer (Strata), the build's name for the architecture layer: a group of engine folders in `Layers.json` with the layers it may include; the same entry as the second term of `foundation:558` |
| `foundation:554` | term | use | Engine module, the other meaning of "module", defined here in one sentence; its entry's home is `core/engine-modules` |
| `foundation:551` | term | use | Registry in Strata's meaning, set against EnTT's registry (`world/ecs`); its entry's home is `core/layers-registries` |
| `foundation:565` | term | use | Service and engine service, set against the scene service of `world/systems`; the entry's home is `core/engine-modules` |
| `foundation:173` | feature | link | The layer table, named as what turns the folders into libraries |
| `foundation:177` | feature | link | The check that the runtime links no tooling, named in one sentence |
| `new:1` | feature | use | The repository's top folders (`Strata/`, `StrataEditor/`, `StrataRuntime/`, `StrataScriptCore/`, `StrataCLI/`, `StrataTests/`), drawn onto the programs and libraries |
| `new:17` | hands-on | home | Exercises: Basic, six files (`EntryPoint.h`, a panel of `StrataEditor/src/Panels/`, a Tetris script, `GLFWWindow.cpp`, `JobSystem.cpp`, a test) each placed in its program and its layer's library from the `Paths` of `Layers.json`; Medium, done in a terminal: the installed `StrataEditor --help` and `StrataRuntime --help` compared, and which program holds the editor's tools. Evidence: `StrataTests/Architecture/Layers.json:5-24`; `StrataEditor/src/EditorApplication.cpp:64-80`; `StrataRuntime/src/RuntimeApplication.cpp:340-354`; `CMake/StrataPackaging.cmake:55` (the three programs installed) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Executables, static and shared libraries, linking | `basics/build` | must |
| What a game engine is, and one frame from start to finish | `start/what-an-engine-is` | must |
| The editor, a project, a script built and attached | `start/first-game` | helps |
| A process: a running program | `basics/computer` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `engine-module-registration-register-module-module` | Engine module registration (Register<Module>Module) | - |
| `layer-application` | Layer (application) | Layer (Strata), Layer (architecture) |
