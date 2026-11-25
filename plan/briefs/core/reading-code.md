# Brief: `core/reading-code`

| Field | Value |
| --- | --- |
| Title | Finding your way in a large codebase |
| Kind | H |
| Size | M |
| Tracks | E |
| Needs | `core/first-change`, `core/conventions` |
| From | new (curricula gap: reading a big codebase); Strata's own tree, with an example inside `core`: one command-line option followed from `CommandLine` to its effect; following a click to a pixel needs the later parts and is an exercise of `capstone/plan` |
| Unit | `plan/allocation/core.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `core/reading-code` — Finding your way in a large codebase

**Covers.** The goal: find the file and line where something happens in a codebase too large to read whole. What must
be true first: the source build of `core/first-change`, and a code editor that reads `compile_commands.json` or the
Visual Studio solution. The steps: (1) read the map, the repository's tree: the top folders, the engine's modules in
`Strata/src/Strata/<Module>/`, the platform code in `Strata/src/Platform/<OS>/`, the editor's `Editor/`, `UI/` and
`Panels/`, the tests in `StrataTests/src/<Module>/`, and the names that say where a module's registration, components
and tests are; (2) read the documents as maps: `AGENTS.md` and its table "Where the details are", `Docs/README.md`,
then the matching section of `Docs/DeveloperGuide.md` and `Docs/Architecture.md`; (3) search for a name or a message
with `git grep` or the code editor's search in files; (4) jump with "go to definition" and "find references"; (5) the
worked trail: the editor's `--frames` option followed from its usage line and `GetIntOption("--frames")` in
`StrataEditor/src/EditorApplication.cpp`, to `ApplicationSpecification::MaxFrames`, to the frame count that ends
`Application::Run`; (6) read the tests of what was found, as its most exact description; (7) ask the history why, with
`git log -S` and `git blame`. The result is the trail written down as files and lines. Variations: from a log message
to the code that logs it; from a label in the editor's UI to the command it runs; from a runtime option
(`StrataRuntime --seconds`) to its effect; a call stack in the debugger as a trail. At the end the reader can find,
for a name, an option or a message, where in the code it acts. The exercises are three more trails, each written down
as files and lines: a startup log line to the code that logs it, the editor's `--idle-timeout` to where it closes the
editor, and `git log -S` on the headless frame cap to the commit that set it. Following a click to a pixel needs the
later parts; it is an exercise of `capstone/plan`.

**Leaves out.**

- What `CommandLine`, `ApplicationSpecification` and the frame count do → `core/first-frame`
- Breakpoints and the call stack as a way to read code → `core/debugging`
- Following a click to a pixel → `capstone/plan`
- The terminal in general → `basics/tools`
- git in general → `basics/git`

**Fit.** `fits`: about 3,450 words against M (3,000). The seven steps and the worked trail take the most; the three
exercises, each a trail of its own, take about 750.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:1` | feature | home | The repository's tree: the top folders, the engine's module folders, the platform folders, the editor's three folders, the tests' folders by module. Evidence: `AGENTS.md:33-47`; `Docs/DeveloperGuide.md:127-147` |
| `new:5` | feature | home | The engine's own documents as maps: `AGENTS.md` with its digests and its table "Where the details are", `Docs/README.md`, `Docs/DeveloperGuide.md` and `Docs/Architecture.md`. Evidence: `Docs/README.md:1-16`; `AGENTS.md:446-455` |
| `foundation:56` | feature | use | `CommandLine` and `CommandLineOptions` as the start of the trail; what they do in full is `core/first-frame`'s |
| `foundation:43` | feature | use | `ApplicationSpecification::MaxFrames`, the middle of the trail |
| `foundation:46` | feature | use | The frame count that ends `Application::Run`, the end of the trail |
| `build-test:40` | feature | use | `compile_commands.json`, which code editors read to jump to definitions |
| `new:21` | hands-on | home | Exercises, each done in the reader's clone and written down as a trail of files and lines: Basic, the startup line "Engine modules: ..." found with `git grep` and followed to `RegisterBuiltinModules`; Medium, the editor's `--idle-timeout` from its usage line to the automation's idle close; Hard, `git log -S c_HeadlessFrameRate` and `git blame` asked why headless runs are capped, down to the commit that set the cap. Evidence: `Strata/src/Strata/Engine/BuiltinModules.cpp:172`; `StrataEditor/src/EditorApplication.cpp:41`, `:77`, `:113-115`; `StrataEditor/src/Editor/EditorAutomation.h:39`; `git log --oneline -S c_HeadlessFrameRate 822a7a46 -- StrataEditor/src/EditorApplication.cpp` prints `d9116fc5 Pace the frames of headless applications` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The source build and the test program | `core/first-change` | must |
| The code style and its naming prefixes | `core/conventions` | must |
| A terminal and git | `basics/git` | must |
| A code editor | `basics/tools` | must |
| Breakpoints and the call stack | `basics/debugging` | helps |
| `std::optional` | `basics/cpp-modern` | helps |

**Starting state.** The end state of `core/first-change`: the repository at the pin, configured with the OS's preset
and built in Debug. No project and no editor run are needed.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `trail` | trail | code trail |
