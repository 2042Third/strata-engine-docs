# Brief: `make/script-builds`

| Field | Value |
| --- | --- |
| Title | Building and shipping script modules |
| Kind | H |
| Size | M |
| Tracks | G |
| Needs | `make/project-coin-run`, `basics/tools`\|`start/install` |
| From | scripting "Building and shipping script modules" (use side): building outside the editor, other compilers and their warnings, long paths, shared libraries next to the module; what a module is, at the use level; Manual/Scripting "Where builds happen", "IntelliSense and building in the IDE" (the `strata` preset the editor writes into `Scripts/CMakePresets.json`); every command it teaches is given exactly, with what the reader should see after it |
| Unit | `plan/allocation/make-b1.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/script-builds` — Building and shipping script modules

**Covers.** A how-to for the reader who wants to build the game's scripts outside the editor: from a terminal, from an
IDE, or with a library of someone else's. It starts with what a module is, at the use level, in two sentences and a
diagram: every `.cpp` and `.h` file under `Scripts/` is compiled into one shared library, which the editor and the
exported game load, and which talks to the engine through a C interface of version 1 that only grows, so that modules
keep loading across releases. Then the game's `CMakeLists.txt` as the editor writes it (`find_package` of the
`StrataScriptCore` package from the folder `STRATA_ENGINE_DIR` names, and `strata_add_script_module`), read line by line.
The numbered steps: open a terminal in the project's folder; configure the scripts with `cmake -S Scripts -B <build
folder> -DSTRATA_ENGINE_DIR=<Strata folder>`; build them with `cmake --build <build folder>`; watch the running editor
load the new module, as after its own build. Each command is given exactly, with what the terminal prints, per OS in
tabs. Then the IDE: open the `Scripts` folder in Visual Studio or in VS Code with the CMake Tools extension and pick the
"strata" preset that the editor wrote into `Scripts/CMakePresets.json`; build there; the editor hot reloads it; the
presets hold paths of this machine, so the project's `.gitignore` keeps them out of version control. Then what can go
wrong: other compilers (the same scripts built on another platform, and the warnings each compiler gives, such as a
missing include that one accepts and another refuses); a project in a deep folder on Windows, which builds in a folder of
the user data instead and is refused only when even that is too deep; and libraries: prefer static ones, and a shared
library the module links must sit next to the module on Windows or be found through its RUNPATH on Linux and macOS,
where `$ORIGIN` fails under hot reload because the editor runs a private copy. The exercise, done in a terminal and
the editor: a small static library of the reader's own, in a folder beside `Scripts` (sources under `Scripts` belong to
the module itself), linked with `target_link_libraries` after `strata_add_script_module`, called from a script, and hot
reloaded. At the end the reader can build the module by hand and in an IDE, read the build's folders, and add a
third-party library without breaking hot reload.

**Leaves out.**

- Building in the editor, the Problems panel and the crash toast → `make/first-script`
- How the editor finds a toolchain, configures and reports diagnostics → `editor/script-builds`
- Shared libraries and binary interfaces in depth → `scripting/shared-libraries`
- The C interface and the SDK inside → `scripting/abi-sdk`
- How modules load, and hot reload inside → `scripting/loading`, `scripting/hot-reload`
- The module shipped with the exported game → `make/export`
- Compiling, linking and CMake from zero → `basics/build`
- Building the engine itself from source → `core/first-change`

**Fit.** `fits`: about 2,800 words against M (3,000). Seven numbered steps with tabs per OS and what the terminal prints
(about 1,000 words) take the most, then the three rules with their reasons, the exercise, the excerpt of the generated
`CMakeLists.txt` and the module's diagram.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:124` | feature | home | The script module: every `.cpp` and `.h` under `Scripts/` compiled into one shared library through the `StrataScriptCore` package |
| `scripting:145` | feature | home | The package a game project finds: `find_package(StrataScriptCore CONFIG ... PATHS <Strata folder>/StrataScriptCore/CMake)`, glm with it, a `Dist` configuration |
| `gamedev:364` | code | home | `StrataEditor/src/Editor/ScriptProject.cpp:207-226`: the game's `CMakeLists.txt` as the editor writes it, with its comment on building by hand, to `find_package` and `strata_add_script_module` and the function's end |
| `gamedev:134` | feature | home | The code editor and IDE: the "strata" preset of `Scripts/CMakePresets.json` for Visual Studio, VS Code and clangd; an IDE's build hot reloads too |
| `gamedev:136` | feature | home | The long-path fallback: a deep project builds in `<user data>/Strata/Builds/<hash>` |
| `gamedev:521` | rule | home | Windows path length: deep folders build elsewhere, extremely deep ones are refused with a shorter folder named |
| `gamedev:137` | feature | home | The script interface is C, of version 1, its host functions only appended, so modules keep loading across releases |
| `gamedev:606` | term | home | ABI |
| `gamedev:410` | figure | home | The module boundary: game code, CMake, the shared library, the C table of host functions and class descriptions, the engine; hot reload swapping copies; the crash guard |
| `gamedev:524` | rule | home | Shared libraries a module links sit next to it, or are found through RUNPATH; `$ORIGIN` fails under hot reload |
| `scripting:144` | feature | use | `strata_add_script_module` and what it sets, in one sentence each |
| `scripting:143` | feature | use | `StrataScriptCore`, the headers and glm that a module builds against |
| `scripting:494` | rule | use | Hot reload runs a copy, so `$ORIGIN` points at the copy's folder |
| `scripting:596` | term | use | Module (script module) |
| `new:21` | hands-on | home | Exercise, done in a terminal and the editor: a small static library in a folder beside `Scripts`, linked to the module with `target_link_libraries(<module> PRIVATE <library>)` after `strata_add_script_module`, called from a script, built and hot reloaded. Evidence: `StrataScriptCore/CMake/StrataScriptModule.cmake:21` (`strata_add_script_module(target)`), `:89-90` (the module is a `MODULE` library target of that name); `StrataEditor/src/Editor/ScriptProject.cpp:213-215` (every `.cpp` and `.h` under the folder belongs to the module) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The terminal: a folder, a program with arguments, a quoted path, pasting a command | `start/install` | must |
| A code editor, and opening a folder in it | `start/install` | must |
| Building scripts in the editor, Ctrl+B, the Problems panel, hot reload | `make/first-script` | must |
| Files of code: headers and sources, compile errors | `basics/programming-3` | must |
| The project folder, its hidden `.strata` folder and file extensions | `make/project-files` | must |
| Compiling, linking, static and shared libraries, CMake | `basics/build` | helps |
| Environment variables and the user data folder | `basics/tools` | helps |
| Exporting a game | `make/export` | helps |

**Starting state.** A new project from the Basic 3D template whose `Scripts` folder holds the generated `Spinner`
script, built once in the editor (as `start/first-game` did); no checkpoint.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `abi` | ABI (use) | application binary interface |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-b1-1 | must | stale-item | `gamedev:364` and the numbered steps of `make/script-builds` | The steps configure with `cmake -S Scripts -B <build folder> -DSTRATA_ENGINE_DIR=<Strata folder>` and build with `cmake --build <build folder>`, as the comment in the generated `CMakeLists.txt` says, and then "watch the running editor load the new module". At the pin that build writes the module into the build folder (or its `Debug` folder with Visual Studio), in the generator's default configuration, and the editor never loads it. The editor loads and watches only `.strata/Scripts/Bin/<module>`, which its own configure step and the "strata" preset pass as `CMAKE_LIBRARY_OUTPUT_DIRECTORY`, with its generator and configuration. On Windows the CMake the editor uses may also be the one inside Visual Studio, which a plain terminal does not find. | The steps become: open a terminal in the project's `Scripts` folder; `cmake --preset strata`; `cmake --build --preset strata`; the editor hot reloads the module (about 150 words with the OS tabs). One sentence per OS on finding CMake: the preset's `cmakeExecutable` names the one the editor uses; on Windows the Developer PowerShell of Visual Studio also has it. A new item of type erratum: the comment in the generated `CMakeLists.txt` gives a hand build whose module the editor does not load; that line suits a check that the code compiles elsewhere (a Variation, critic-make-b1-3). About 250 words in all. | `allocation/make-b1.md:426-428`, `:463`; `StrataEditor/src/Editor/ScriptProject.cpp:216-218`; `StrataEditor/src/Editor/ScriptBuild.cpp:417-449` (the editor's configure: generator, configuration, `CMAKE_LIBRARY_OUTPUT_DIRECTORY`), `:530-575` (the "strata" configure and build presets carry the same variables and `cmakeExecutable`); `StrataScriptCore/CMake/StrataScriptModule.cmake:8`, `:13-14`, `:106-108`; `Strata/src/Strata/Project/Project.h:117`; `Strata/src/Strata/Scripting/ScriptEngine.h:75-78`; `Docs/Manual/Scripting.md:94-107`, `:208-214` |
| critic-make-b1-3 | should | shape | `make/gameplay-math`, `make/timers-events`, `make/script-fields`, `make/script-builds`, `make/levels-saves` | style.md gives a how-to a `## Variations` section: the same goal under other conditions. The Covers of these five how-tos name no variation, so the writer has nothing to fill it with. The how-tos of `make-a` and `make-b2` name theirs. (`make/recipes` has its "what to change" per recipe.) | Each Covers names two variations (about 250 words a page). From the pin: gameplay-math, aiming with the right stick through the Look action instead of the cursor (`FollowCamera.cpp:57-60`), and a turret that turns at a limited speed (critic-make-b1-16); timers-events, a timer in `OnFixedUpdate` fed with the fixed delta, for gameplay that keeps step with physics, and a held gamepad direction repeated (critic-make-b1-5); script-fields, tuning many spawners at once through their prefab (critic-make-b1-4); script-builds, the plain `cmake -S` and `-B` build as a check that the code compiles on another machine (critic-make-b1-1); levels-saves, three save slots named "Slot 1" to "Slot 3" and listed with `ListSaveFiles`. The five Fit lines count them. | `style.md:535-541`; `allocation/make-b1.md:5-24`, `:91-111`, `:174-193`, `:420-440`, `:922-962`; `allocation/make-a.md:130`, `:424`; `allocation/make-b2.md:393`; `StrataScriptCore/Include/StrataScript/Game.h:104-107`, `:157-158` |
| critic-make-b1-12 | should | thin-home | `new:21` and the libraries of `make/script-builds` | The exercise links a static library from a folder beside `Scripts`. Track G never reads `basics/build`, so the reader has never seen a library or a line of CMake, and the Covers reads only the editor's `CMakeLists.txt`. Two pitfalls also lie in the exercise. CMake refuses `add_subdirectory` of a folder outside `Scripts` unless a binary folder is given. And Play builds first only when a file under `Scripts` changed, so after an edit to the library Play runs the old code; only **Scripts > Build Scripts** (Ctrl+B) builds it. | The libraries section teaches, at the use level, what a static and a shared library are (copied into the module; a file loaded beside it), and the four lines that the exercise adds (`add_library`, `add_subdirectory` with its binary folder, `target_include_directories`, `target_link_libraries`), each in one sentence (about 250 words). The exercise's steps add the two pitfalls (about 60 words). The Assumes row of `basics/build` stays `helps`, and the page teaches what it uses (rule N2). | `allocation/make-b1.md:432-438`, `:475`, `:486`; `tracks.md:56-130` (no `basics/build` on track G); `StrataEditor/src/Editor/EditorContext.cpp:2300-2338`; `StrataEditor/src/Editor/ScriptSources.h:54-55`; `StrataEditor/src/Editor/ScriptProject.cpp:383-391` (an edited `CMakeLists.txt` is kept); CMake asks for a binary directory with a source directory outside the current one (general knowledge) |
