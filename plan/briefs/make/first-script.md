# Brief: `make/first-script`

| Field | Value |
| --- | --- |
| Title | Your first script |
| Kind | T |
| Size | M |
| Tracks | G, B |
| Needs | `make/lighting`, `basics/tools`\|`start/install` |
| From | gamedev "Your first script" (§1.9, concepts 11, 13; hands-on G6); scripting "Your first script"; Manual/Scripting "Create a script" to "When a script crashes" (the code editor, IntelliSense, the Problems panel, the crash toast); the C++ special to scripts (the `Script` base class, `override`, `ST_SCRIPT_CLASS`, `ST_SCRIPT_FIELD`, no work in the constructor); `deltaTime` named; `Log::Info`; use home of hot reload; Coin Run's coins spin |
| Unit | `plan/allocation/make-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/first-script` — Your first script

**Covers.** The page makes Coin Run's coins spin with a script of the reader's own, and is the reader's first meeting
with code: on tracks G and B the reader has never programmed (`basics/programming-1` comes next), so every line the
page shows gets a sentence on what it does, at the level of names, as `start/how-to-read` taught for code one does not
understand yet. The steps. (1) Choose the code editor: **File ▸ Preferences ▸ External Editor** lists the editors found
(VS Code, Visual Studio, CLion); the page tells why the editor opens files without a shell. (2) **Scripts ▸ New
Script...**: the class name `Coin` (the dialog refuses names the SDK or the project already use); `Scripts/Coin.cpp`
opens in the code editor and the scripts start building ("Building" in the status bar). The template is read line by
line: the SDK's include, `using namespace Strata`, `class Coin : public Script` (a script class is built on the
SDK's `Script`), a field with its default, `OnCreate` and `OnUpdate` marked `override`, `deltaTime` as the frame's game
time in seconds, and `ST_SCRIPT_CLASS` with `ST_SCRIPT_FIELD` at the end. (3) Replace the template's body with the
spin: a field `DegreesPerSecond` and the two lines of the `Spinner` of `start/first-game` (the turn, from
`make/transforms-units`), shown whole as the generated `Spinner` has them. (4) Build with **Ctrl+B** (**Scripts ▸ Build
Scripts**): the first build configures CMake, later ones are quick; the Problems panel stays empty; IntelliSense works
once a build ran. (5) Attach: on one coin, **Add Component ▸ Script** and pick `Coin`, then **Apply to Prefab** so every
coin spins (`make/prefabs`); the Content Browser's **Scripts** root lists `Coin.cpp` with the class it registers. (6)
**Play**: Play builds changed sources first ("Building to play"); the coins spin; change `DegreesPerSecond` in the
Inspector for one coin, which is what a field is for. (7) One line of `Log::Info` in `OnCreate`, read in the Console.
(8) A build error on purpose: delete a `;`, build, read the toast and the Problems panel (file and line), double-click
to open the line, fix it. (9) Hot reload: while the game plays, change the spin (another axis), build again: the
coins change without stopping; each instance is made again, fields keep their values, `OnReload` runs instead of
`OnCreate`, and a plain member starts over. (10) A crash on purpose: a line the page gives, a write through a null
pointer as in `scripting/crash-containment`'s example, which faults on every platform (a division by zero would not:
on ARM64, the Apple silicon of Strata's macOS releases, integer division by zero gives 0); build and play: the script's
module is switched off, play stops, the toast and the Problems panel show the crash and its stack, and the editor goes
on; remove the line. One warning sentence: on Linux and macOS, `abort()`, a failed `assert()` or `std::terminate` in a
script ends the whole editor with its unsaved work (Windows contains them in the modules the editor builds), so a script
reports a broken state with `Log::Error`, not `assert`. Three rules in `:::rule` asides, each with its reason: do the
game's setup in `OnCreate`, not the constructor (the module makes one instance without an entity to read the defaults);
`ST_SCRIPT_CLASS` once per class, in a `.cpp`, never in a header; only members registered with `ST_SCRIPT_FIELD` survive
hot reload. The other field types are named in one sentence for `make/script-fields`. At the end the reader can write,
build, attach and change a script, read a build error and a crash, and use hot reload; the next four pages teach
programming from zero on this script.

**Leaves out.**

- Values, variables, decisions, loops, functions, classes and the rest of C++ from zero → `basics/programming-1`, `basics/programming-2`, `basics/programming-3`
- Finding bugs with a debugger attached to the editor → `basics/debugging`
- The lifecycle: when each callback runs, fixed updates → `make/script-loop`
- Fields of every type, references and prefab overrides of fields → `make/script-fields`
- Building outside the editor, the `strata` preset, what a module is → `make/script-builds`
- How the editor builds scripts → `editor/script-builds`
- What `ST_SCRIPT_CLASS` and `ST_SCRIPT_FIELD` do inside → `scripting/abi-sdk`
- Hot reload inside → `scripting/hot-reload`
- Crash containment and symbolization inside → `scripting/crash-containment`, `scripting/symbolization`

**Fit.** `fits`: about 3,950 words against M (3,000). Ten steps at B0's length take most of it, with the template read
line by line, the `Spinner` excerpt, three rules with their reasons, six pictures and the hot reload exercise. B0 meets
code here for the first time, so no line goes unexplained, and the page is near M's top.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:359` | code | home | `StrataEditor/src/Editor/ScriptProject.cpp:230-257`: the generated `Spinner`, the smallest complete script (class, field, `OnUpdate`, the turn, the registration) |
| `gamedev:360` | code | home | `Docs/Manual/Scripting.md:14-37`: what **New Script...** writes, with a comment on when each callback runs |
| `gamedev:47` | feature | home | The toasts of a failed build and of a crash, with **Show Problems** |
| `gamedev:54` | feature | home | The Console's clickable file and line; the Problems panel's build errors and crashes |
| `gamedev:61` | feature | home | Preferences: the External Editor page |
| `gamedev:125` | feature | home | The script class and its fields: `class X : public Script`, `ST_SCRIPT_CLASS`, `ST_SCRIPT_FIELD`; the field types named |
| `gamedev:129` | feature | home | **Scripts ▸ New Script...** and its validation |
| `gamedev:130` | feature | home | **Ctrl+B**; Play builds changed sources first |
| `gamedev:132` | feature | home | Hot reload: instances made again, fields kept, `OnReload` |
| `gamedev:133` | feature | home | Crash containment as the maker sees it: the module switched off, play stopped, the report |
| `gamedev:323` | concept | home | Hot reload and state: fields survive, plain members do not |
| `gamedev:449` | figure | home | The New Script dialog; the generated file in the code editor |
| `gamedev:450` | figure | home | The Problems panel with a build error; the crash toast and the crash with its stack |
| `gamedev:453` | figure | home | Preferences: the External Editor page with the editors found |
| `gamedev:484` | rule | home | Do setup in `OnCreate`, not the constructor |
| `gamedev:486` | rule | home | Only public members registered with `ST_SCRIPT_FIELD` survive hot reload |
| `gamedev:523` | rule | home | `ST_SCRIPT_CLASS` once per class, in a `.cpp` |
| `gamedev:539` | hands-on | home | G6 on Coin Run: the script attached, its field changed, the code changed during Play |
| `gamedev:605` | term | home | SDK |
| `gamedev:608` | term | home | Field |
| `gamedev:609` | term | home | Hot reload (the meaning of scripts) |
| `gamedev:610` | term | home | Crash containment |
| `gamedev:612` | term | home | External editor |
| `gamedev:613` | term | home | Problems panel |
| `scripting:208` | feature | home | The Scripts menu (New Script..., Build Scripts, External Editor..., Open Scripts Folder, Show Problems), the Script component's class picker, the build pills |
| `scripting:509` | hands-on | home | Hello script: the steps of the page are this exercise on Coin Run |
| `scripting:584` | term | home | Field, as the scripting inventory defines it (`ST_SCRIPT_FIELD`'s home) |
| `scripting:105` | feature | use | The `Script` base class |
| `scripting:114-115` | feature | use | `ST_SCRIPT_CLASS` and `ST_SCRIPT_FIELD`; the field types |
| `scripting:124` | feature | use | `Log` |
| `scripting:154` | feature | use | The Script component that holds the class |
| `scripting:190` | feature | use | An exception switches off one instance, a crash the module |
| `scripting:205` | feature | use | The `script.*` commands in the steps' command tabs |
| `scripting:303` | concept | use | Crash containment, at the maker's level; step 10's warning: on Linux and macOS `abort()`, a failed `assert()` or `std::terminate` ends the editor, so a script reports a broken state with `Log::Error`. Evidence: `Strata/src/Strata/Scripting/ScriptEngine.h:40-44`; `StrataScriptCore/CMake/StrataScriptModule.cmake:104` (the modules link the C runtime statically on Windows); `.claude/skills/strata-scripting/SKILL.md:654-655` (read at the pin) |
| `scripting:319` | concept | use | Hot reload, at the maker's level |
| `scripting:326` | concept | use | Fields shown and saved by the editor |
| `scripting:435` | figure | use | The Problems panel with a compiler error and with a crash |
| `scripting:437-438` | figure | use | The crash in the Console with its toast; hot reload in action |
| `scripting:467` | rule | use | Constructors without side effects |
| `scripting:470` | rule | use | One `ST_SCRIPT_CLASS` per class, in a `.cpp` |
| `scripting:472` | rule | use | Only fields survive hot reload |
| `scripting:476` | rule | use | Exceptions disable an instance; crashes fault the module |
| `scripting:511` | hands-on | use | Hot reload a running game, as an exercise on a ThirdPerson copy |
| `scripting:525` | hands-on | use | Crash on purpose: step 10 writes through a null pointer, which faults on every platform (integer division by zero does not trap on ARM64), and its exercise with an exception. Evidence: `StrataTests/Scripts/Faults/FaultScripts.cpp:57-60`; `StrataTests/src/Scripting/ScriptFaultTests.cpp:31-33` (read at the pin) |
| `editor-ui:149` | feature | use | The Problems panel |
| `editor-ui:220` | feature | use | The New Script dialog and the External Editor page |
| `editor-ui:232` | feature | use | The Preferences dialog |
| `editor-ui:573` | figure | use | Toasts with their action buttons |
| `editor-ui:692` | hands-on | use | A broken build followed through the pills and toasts to Problems |
| `editor-ui:748` | term | use | Toast |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The C++ build tools and a code editor installed and checked | `start/install` | must |
| The `Spinner` built and attached once; Play and the Console | `start/first-game` | must |
| Components, Add Component and the Inspector | `make/scenes-entities` | must |
| A rotation as an axis and an angle; degrees and radians | `make/transforms-units` | must |
| Applying an instance's change to its prefab | `make/prefabs` | must |
| How to read code you do not understand yet | `start/how-to-read` | must |
| Frame time: one frame's seconds | `start/what-an-engine-is` | helps |
| Values, variables, classes and members as programming | `basics/programming-3` | helps |

**Starting state.** The end state of `make/lighting` (`startsFrom {"tutorial": "make/lighting"}`): Coin Run lit for
play with five coin instances. The script `Coin.cpp` of each stage is a file of the tutorial
(`tutorials/make/first-script/`), copied by the runner and typed by the reader. The page ends with the coins spinning;
this checkpoint is the start of the Coin Run practice items of `basics/programming-1` to `basics/debugging`
(`critique/rulings-4.md`, R11).

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `crash-containment` | Crash containment | - |
| `external-editor` | External editor | - |
| `field` | Field | - |
| `hot-reload` | hot reload | - |
| `problems-panel` | Problems panel | - |
| `script-class` | script class | - |
| `script-field` | script field | - |
| `script-module` | script module | - |
| `sdk` | SDK (use) | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-a-23 | could | thin-home | `make/first-script` (step 2) | The page promises a sentence for every line it shows, but the template's `public:` and the `[[maybe_unused]]` of `OnUpdate([[maybe_unused]] float deltaTime)` are not in its list. The attribute is the first B0 meets, and every callback of `Script.h` carries it. | Step 2 adds one sentence each: `public:` makes what follows usable from outside the class, which fields need; `[[maybe_unused]]` tells the compiler that the body may leave the parameter unused (about 40 words). | `allocation/make-a.md:822-825`; `StrataEditor/src/Editor/ScriptProject.cpp:350`, `:365-367`; `StrataScriptCore/Include/StrataScript/Script.h:84` |
