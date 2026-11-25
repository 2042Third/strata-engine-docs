# Brief: `make/commands`

| Field | Value |
| --- | --- |
| Title | Driving the editor from outside: the CLI and command scripts |
| Kind | H |
| Size | M |
| Tracks | G |
| Needs | `make/automated-playtests`, `make/animation` |
| From | automation "Driving the editor from outside" (use side); skill `strata-make-a-game` §1; StrataCLI against a running editor, finding a command and its schema, parameters from a file (`@file`) or from standard input (`-`) because quoting JSON on a Windows command line is fragile (skill `strata-editor-automation`), steps with no UI (`prefab.instantiate` with many instances, `animation.createController`), command scripts that build content |
| Unit | `plan/allocation/make-b2.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/commands` — Driving the editor from outside: the CLI and command scripts

**Covers.** The goal: drive a running editor from a terminal, run any command (also those no menu or button has) and
write scripts that build content. What must be true first: the terminal of `start/install`, command scripts as
`make/automated-playtests` wrote them, and the reader's Coin Run project open in the editor. The steps. One sentence on
the idea, linking `editor/commands`: every menu and button runs a command, and the same commands answer a terminal. Find
the editor: the status bar's automation pill ("port N · no agent"), `StrataCLI status`; or start one with `StrataCLI
launch --project <dir>` (`--headless`, `--no-gpu`). `StrataCLI list` for the commands and their one-line descriptions;
`StrataCLI list --json` for a command's parameters as a JSON Schema (which names are required, their types). Call one:
`StrataCLI call editor.status`; parameters from a file (`@params.json`) or from standard input (`-`), because quoting
JSON on a Windows command line breaks; read the answer and the exit codes (0, 1 with the error's `data`, 2 no editor, 4
no answer in time, which is no failure: never start a second editor). Read an error: a misspelled parameter and the
error's list of the parameters the command takes. Steps with no menu or button: 200 coins scattered with one
`prefab.instantiate {instances: [...]}` in one undo step; a controller made with `animation.createController` (the step
`make/animation` named), and a pose previewed with `animation.preview` (the viewport's preview chip names it, and a
click on it stops it); a world's layers changed with `world.setLayers`, with one warning line: removing a layer that has
cells, or changing a layer's cell size, is refused unless `deleteCells` moves those cells to the trash; store-page
screenshots with `viewport.capture --save-image` at a quality and size, overlays off; probes baked with
`lighting.bakeProbes` and a GI view captured (`viewport.capture` with `debugView`), the agent route of
`make/reflections` and `make/gi`. A script that builds content: `editor.batch` with `bind` and `$ref`, atomic, so a
failed step undoes the batch, and the same steps as a `--commands` file. Commands that replace the scene refuse unsaved
changes unless `force`, and a script never forces away a person's work. What Strata does not do here: no place in the
editor's window types and runs any command (the Activity panel re-runs only commands the journal recorded). Result: a
scene changed from the terminal and a build script that repeats it. Variations: a wrapper script for a long command; a
headless editor with no window. The exercise: the scatter undone and redone from the terminal.

**Leaves out.**

- What a command is in the editor, and how the registry checks parameters → `editor/commands`
- The MCP server and its toolsets → `make/with-an-agent`
- Sockets, JSON-RPC and the editor's server → `automation/json-rpc`, `automation/rpc-server`
- Who may connect, tokens and session files → `automation/security`, `automation/sessions`
- StrataCLI's own structure → `automation/mcp`
- Every command with its schema → `reference/commands`

**Fit.** `fits`: about 3,700 words against M (3,000): about 17 steps with their terminal captures, one error read and
one batch, of which seven are steps no menu or button can do, two variations and the exercise take the most. The counts
of commands are never typed (the erratum below).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:247` | feature | home | StrataCLI: `launch --headless` and `--no-gpu`, `list`, `call cmd @p.json`; its MCP half (`StrataCLI mcp`, toolsets) is used on `make/with-an-agent` |
| `scene-ecs:600` | hands-on | home | Scattering 200 instances of a prefab with `prefab.instantiate {instances: [...]}` in one undo step (Coin Run's coin in place of the crates) |
| `render-core:667` | hands-on | home | Screenshots for a store page with `viewport.capture`: path, quality, size, overlays off |
| `render-indirect:540` | hands-on | home | G10: the probe bake and the GI view through StrataCLI (`lighting.bakeProbes`, `viewport.capture` with `debugView: "gi"`) |
| `new:6` | not-done | home | A place in the editor's UI to type and run any command; the Activity panel re-runs only commands the journal recorded. Evidence: `EditorLayer::DrawMenuBar`, `StrataEditor/src/EditorLayer.cpp:1449-1627`, has no such item; `StrataEditor/src/Panels/ActivityPanel.cpp:368-397` (Copy as script, Re-run, Undo to here) |
| `automation:656`, `automation:658`, `automation:660` | hands-on | home | First contact (`launch`, `status`, `list`, `call editor.status`, `call editor.quit`), a scene built from the shell with parameters from `@file`, a misspelled parameter's error read and fixed |
| `automation:664` | hands-on | home | A capture saved with `--save-image` from the scene's camera, with and without lights (preview lighting) |
| `automation:671` | hands-on | home | An atomic `editor.batch` with `bind` and `$ref`; one failing step undoes the batch |
| `new:7` | erratum | home | The inventories count 151, 153 and 154 editor commands; the page never types a count and writes `:value{key="commands.count"}`. Evidence: `StrataTests/src/Editor/CommandJournalTests.cpp:102-164` lists the commands of `StrataEditorCore` and `:234` checks the number; `StrataEditor/src/EditorLayer.cpp:177, 233` add `editor.showPanel` and `editor.showDialog` |
| `new:25` | hands-on | home | Exercise, done with StrataCLI: the scatter of 200 coins undone with one `StrataCLI call edit.undo`, checked with `entity.find`, and brought back with `edit.redo`. Evidence: `StrataEditor/src/Editor/EditorStateCommands.cpp:364`, `:376` (`edit.undo`, `edit.redo`); `StrataEditor/src/Editor/Commands/EntityCommands.cpp:401` (`entity.find`) |
| `gamedev:246` | feature | use | Commands are the API: one registry with a JSON Schema and a description per command (home `make/editor-tour`) |
| `automation:192-193`, `automation:195`, `automation:197`, `automation:199` | feature | use | StrataCLI's commands, exit codes, image results, finding the editor, launching one |
| `automation:148-150` | feature | use | `editor.status`, `editor.commands`, `editor.batch` |
| `automation:269` | concept | use | Why automate an editor at all |
| `automation:534`, `automation:577`, `automation:586` | figure | use | Commands are the API (fan-in); the status bar's automation pill; terminal sessions |
| `automation:642-643` | rule | use | A CLI timeout is no failure, never start another editor; never force away a person's unsaved changes (the second's home is `make/with-an-agent`) |
| `editor-core:175` | feature | use | `prefab.instantiate` and its `instances` |
| `editor-core:241` | feature | use | `editor.batch {steps, atomic}` (home `editor/command-scripts`) |
| `animation:185` | feature | use | `animation.createController` |
| `animation:190` | feature | home | The viewport's preview chip (`ViewportPanel::DrawPreviewChip`, `StrataEditor/src/Panels/ViewportPanel.cpp:464`): it names the pose that `animation.preview` shows, and a click on it stops the preview |
| `worlds-runtime:111` | feature | use | The world commands, `world.setLayers` among them: removing a layer that has cells, or changing a layer's cell size, is refused unless `deleteCells` moves those cells to the trash (`StrataEditor/src/Editor/EditorWorldCommands.cpp:670-675`) |
| `render-scene:181` | feature | use | `renderStats` in a capture's answer |
| `automation:705`, `automation:713`, `automation:766-767` | term | link | Command, binding and `$ref`, StrataCLI, exit code |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| A terminal: running a program with arguments, quoting a path | `start/install` | must |
| JSON written by hand; command scripts with `expect`, `bind` and `$ref` | `make/automated-playtests` | must |
| Reading a command and its JSON result | `start/how-to-read` | must |
| Prefabs and their instances | `make/prefabs` | must |
| Undo | `make/project-files` | must |
| Unsaved changes and saving | `make/project-files` | must |
| Reflection probes and the GI views | `make/reflections` | helps |
| A world's layers | `make/large-worlds` | helps |
| An animation controller | `make/animation` | helps |

**Starting state.** The end checkpoint of `make/project-coin-run`, downloadable, open in the editor (its coin prefab is
what the scatter step places).

**Command-only steps.**

- Every step: the page teaches running commands from a terminal, and its steps are `StrataCLI` lines.
- The steps no menu or button can do: `prefab.instantiate {instances: [...]}`, `animation.createController`,
  `animation.preview`, `world.setLayers`, `viewport.capture --save-image` and `lighting.bakeProbes` from the terminal,
  `editor.batch`; the page itself teaches calling a command with StrataCLI (R33, D20).
- The batch's steps run again as a `--commands` file: a command script, run as `make/automated-playtests` (a Need)
  taught.

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-b2-1 | must | missing-item | `make/commands` (Covers; `gamedev:247`, `automation:656-660`) | The page's call line `StrataCLI call <command> @params.json` fails in Windows PowerShell: an unquoted `@params.json` is a parse error (the splatting operator), and `StrataCLI` is no command of the terminal but a program in the Strata folder. A params file written with PowerShell 5's `>` is UTF-16, which StrataCLI refuses. | The page is track G's teacher of StrataCLI, so its first call step gives the lines in OS tabs, run from the Strata folder: `.\StrataCLI call <command> '@params.json'` in PowerShell (the quotes keep the `@`), `./StrataCLI call <command> @params.json` in a POSIX shell, and the form with `-`; the params file is saved as UTF-8 from the code editor; "If you do not see it" quotes the parse error and StrataCLI's UTF-16 message. critic-start-1 asks the same of `start/how-to-read`; here it holds for every call of the page. About 120 words. With critic-make-b2-2, -18 and -19 the estimate reaches about 3,970 words, M's top, so the page takes L by S2 and S5. | `allocation/make-b2.md:796-799`, `:831`, `:836`; `allocation/completeness/start.md:7` (critic-start-1); pin: `StrataCLI/src/CLI/CliApplication.cpp:126-160`; `Docs/Releases/PackageReadme.md:17`; `.claude/skills/strata-editor-automation/SKILL.md:60`; run here in Windows PowerShell 5.1: `cmd /c echo @params.json` fails with ParserError SplattingNotPermitted, `cmd /c echo '@params.json'` prints `@params.json` |
| critic-make-b2-2 | must | shape | `make/commands` (Starting state; `animation:185`, `animation:190`, `worlds-runtime:111`, `render-indirect:540`) | The page starts from Coin Run's end checkpoint: a rolling ball and coins. That project has no skinned model with clips, no world, no reflection probe and no global illumination, so the steps `animation.createController`, `animation.preview`, `world.setLayers`, `lighting.bakeProbes` and the GI capture have nothing to act on. | The Starting state names the project each section opens, each a download of the book (the end checkpoints are planned already; the last two are states of those pages' steps, which the book adds as downloads): Coin Run's end for the scatter, the batch and the store-page captures; the end checkpoint of `make/animation` (its robot and clips) for the controller and the preview; the end checkpoint of `make/large-worlds` for `world.setLayers`; the courtyard of `make/reflections` with its probe, and the room of `make/gi` with Global Illumination on, for the bake and the GI view. About 60 words. | `allocation/make-b2.md:800-807`, `:869-870`, `:875-876`; `outline-1.md:196` (Coin Run as a rolling ball); pin: `StrataEditor/src/Editor/EditorAnimationCommands.cpp:153-157` (each state plays an animation clip); `StrataEditor/src/Editor/EditorWorldCommands.cpp:670-673` (a world's layer list); `StrataEditor/src/Editor/EditorLightingCommands.cpp:872-883` (the scene's probes) |
| critic-make-b2-18 | should | shape | `make/commands` (`scene-ecs:600`, `new:25`) | The scatter step places 200 coins with one `prefab.instantiate {instances: [...]}`, and each instance gives its own Transform. A reader of track G can write 200 positions only by hand: no page teaches a tool that writes JSON. | The book offers the params file (200 positions over the level) among the page's downloads; the page shows its first two entries and runs it with `@file`, and the exercise undoes and redoes that call. About 40 words. | `allocation/make-b2.md:800-801`, `:832`, `:840`; pin: `StrataEditor/src/Editor/EditorPrefabCommands.cpp:341-351` |
| critic-make-b2-19 | could | thin-home | `make/commands` (`automation:192-193`) | The page lists the exit codes 0, 1, 2 and 4, but not 3 (an invalid command line) or 5 (`--save-image` could not save the image), and the page itself uses `--save-image`. `StrataCLI list --json` prints the schema of every command at once, with no way to ask for one. | Name codes 3 and 5 in the exit-code step, and say how to find one command's schema: save the output to a file and search it in the code editor, or look it up on `reference/commands`. About 50 words. | `allocation/make-b2.md:796-799`, `:842`; pin: `StrataCLI/src/CLI/CliApplication.cpp:589`, `:620-622`; `StrataEditor/src/Editor/EditorCommands.cpp:66-79` |
