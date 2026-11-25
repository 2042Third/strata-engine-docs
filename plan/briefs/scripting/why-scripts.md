# Brief: `scripting/why-scripts`

| Field | Value |
| --- | --- |
| Title | Why game code lives outside the engine |
| Kind | C |
| Size | M |
| Tracks | E |
| Needs | `world/ecs` |
| From | scripting ch. 1 "Game code and the engine: why scripts"; how other engines script (interpreted, managed, visual, native) |
| Unit | `plan/allocation/scripting.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `scripting/why-scripts` — Why game code lives outside the engine

**Covers.** The page opens on what the reader did in `start/first-game`: the `Spinner` script was changed, built with
**Ctrl+B** and run again while the editor kept running, and the engine was never rebuilt. From it the problem: an
engine is large and general, a game's rules change by the hour, and a bug in game code should not take the editor
down. The naive answer, game code compiled into the engine, and where it breaks (a rebuild and a restart for every
change; every game links the engine's internals). The idea in one paragraph and one diagram, the layers of the part:
game code, the SDK, the module's entry points, the C line, then `ScriptModule`, `ScriptEngine`, `ScriptSystem` and the
host API with the scene and engine services below, each box named with the page that opens it. The approaches engines
use, each brought in by the flaw of the one before: an embedded interpreted language (Lua), a managed runtime (C# in
Unity and Godot), a language of the engine's own (GDScript; UnrealScript in its time), visual scripting (Blueprints),
and native code in plug-in libraries (Unreal's C++ modules with Live Coding, the DLL reload of in-house engines), with
a table of speed, time to see a change, safety, tools and who uses them. Where game code attaches to objects: script
components (Unity's MonoBehaviour), scripts as systems in a pure ECS, actor subclasses (Unreal), and Strata's Script
component, an ordered list of class names whose instances live outside the registry. Strata's choice in a `:::why`
aside: native C++20 in a shared library behind a C ABI, so one language for engine and game, full speed, and the
debuggers and IDEs people already use; and its three costs, which the rest of the part pays: crashes (containment),
the binary boundary (the ABI and the SDK), compile time (hot reload). What Strata does not do: visual scripting, and
any script language but C++. Common mistakes: reading "script" as "interpreted", and underestimating what a native
choice costs. At the end the reader can say why an engine loads game code as a module, compare the five approaches
by cost, and name the page of the part that answers each cost.

**Leaves out.**

- What a shared library and a binary interface are → `scripting/shared-libraries`
- Writing, building and attaching a script → `make/first-script`
- The script lifecycle and its callbacks → `make/script-loop`, `scripting/script-system`
- How a crash in game code is contained → `scripting/crash-containment`
- How a module is replaced while the game runs → `scripting/hot-reload`
- The index of everything Strata does not have → `appendix/not-in-strata`

**Fit.** `fits`: about 3,700 words against M (3,000). The five approaches with their table and the four object models
take the most words, with the exercises about 250; the ABI stays with `scripting/shared-libraries`.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scripting:243` | concept | home | Why games need scripts: engine code against game code, the five approaches with their costs, Strata's native choice and what it costs; the mistake "script means interpreted" |
| `scripting:285` | concept | home | Where scripts attach: script components, scripts as systems, actor subclasses; Strata's ordered entry list per entity, one instance per entry, instances outside the registry |
| `scripting:398` | figure | home | The layers of the part (a redraw of `Docs/Architecture.md:3138-3146`), calls in each direction, each box naming its page |
| `new:1` | not-done | home | Visual scripting: game logic is C++ script classes. Evidence: `git grep -niE "visual ?script" 822a7a46 -- Strata/src StrataEditor/src StrataScriptCore` and `git grep -niw "blueprints\?" 822a7a46 -- Strata/src StrataEditor/src StrataScriptCore` find nothing (run at the pin); `AGENTS.md:269-271` |
| `new:2` | not-done | home | Script languages other than C++. Evidence: `git grep -niE "lua_" 822a7a46 -- Strata/src StrataEditor/src StrataScriptCore StrataRuntime`, the same with `mono_` and with `coreclr`, find nothing (run at the pin); `Strata/vendor` holds no interpreter or runtime |
| `new:20` | hands-on | home | The page's exercises (R32, D27): a design exercise, three games (rules that change every day, a game that players extend, a console game that may load no code at run time) each matched to an approach of the page's table with the cost that decides it; and one done on the workbench: change the `Spinner` of `start/first-game`, build with **Ctrl+B**, and note which file the build wrote (the module, in the project's build folder) and how long the change took to show, against a build of the engine from `core/first-change` (about 250 words). Evidence: `StrataEditor/src/Editor/ScriptProject.cpp:241-254` (the `Spinner`); `StrataEditor/src/EditorLayer.cpp:983`, `:1591` (Ctrl+B builds the scripts); `StrataScriptCore/CMake/StrataScriptModule.cmake:106-107` (the module's output folder); `Docs/Roadmap.md:1709` (a console port would link modules statically) |
| `scripting:154` | feature | use | The Script component, named as the place scripts attach |
| `scripting:201` | feature | link | The layer rule of Scripting, named once as the reason for the host API |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| What a game engine is; the frame map | `start/what-an-engine-is` | must |
| Writing and building a script in the editor (the `Spinner` of the first game) | `start/first-game` | must |
| Object models: inheritance, components, ECS | `world/what-a-world-is` | must |
| Handles instead of pointers; UUIDs as stable identities | `world/ecs` | helps |
| How a C++ program is built: compiling, linking, static and shared libraries | `basics/build` | must |
| C++ classes in depth: inheritance and virtual calls | `basics/cpp-classes` | helps |
| "Module", "layer", "registry" and "service" | `core/map` | helps |
| The layer table, optional modules, no tooling in games | `core/layers-registries` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.
