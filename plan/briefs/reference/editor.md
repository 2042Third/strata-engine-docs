# Brief: `reference/editor`

| Field | Value |
| --- | --- |
| Title | Editor reference: panels, shortcuts, arguments |
| Kind | R |
| Size | M |
| Tracks | - |
| Needs | `editor-ui/shell` |
| From | editor-ui ch. 18, editor-core §1.1, automation §1.7; the option table generated from `c_Arguments` in `StrataEditor/src/EditorApplication.cpp` |
| Unit | `plan/allocation/reference.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `reference/editor` — Editor reference: panels, shortcuts, arguments

**Covers.** The paragraph on top says what the page is: the editor's surfaces as facts to look up, for a reader who
needs a panel's id, a key or an option. The tables, in this order. (1) The editor's command line, generated from
`c_Arguments` in `EditorApplication.cpp` (every option, its value and help text: `--project`, `--commands`,
`--quit-after-commands`, `--frames`, `--screenshot`, `--headless`, `--no-gpu`, `--windowed`, `--ui-scale`,
`--layout`, `--no-automation`, `--automation-port`, `--idle-timeout`, `--imgui-demo`, `--version`, `--help`), the
three ways the editor runs (window, headless, scripted) and the exit code of a bad argument
(`CommandLineOptions::c_UsageExitCode`). (2) The panels, generated from the built-in registrations in drawing order:
id (as `editor.showPanel` takes it), title, icon, menu path, whether it opens by default and where it docks. (3) The
menus of the menu bar with their items and shortcuts, parsed from `EditorLayer::DrawMenuBar`. (4) A hand-checked table
of the shortcuts: each key, its route (global, focused on the Hierarchy or the Scene view, local to a panel), what it
does, and when it is refused (behind a modal, or while the running game has the input), checked against
`EditorLayer.cpp`, `UI/EditorActions.cpp` and `ViewportPanel.cpp`. (5) A hand-checked table of the Scene view's chips
and the status bar's pills, each with what it shows and where it leads. (6) The drag payload names and the probe-key
conventions of the UI tests, for a contributor. Hand-written besides: one introduction per table, a line that sends
preferences to `reference/settings` and environment variables to `reference/automation`, and `## Where it lives in
Strata` (`EditorApplication.cpp`, `EditorLayer.cpp`, `StrataEditor/src/Panels/`, `UI/EditorActions.cpp`). The tools
are `tools/reference.py parse` (route "program options", and the parse of the panels and the menu bar that the answer to
reference-q3 adds to `../pipelines.md` §7.1) and the commands dump (`editor.showPanel`'s panel names).

**Leaves out.**

- The editor as a program: core, UI and host → `editor/program`
- The shell, docking and the panel registry → `editor-ui/shell`
- Shortcuts and who owns the keyboard, with the reasons → `editor-ui/game-view`
- The Scene view's tools and chips, as a design → `editor-ui/scene-view`
- The status bar and toasts → `editor-ui/status`
- The instrument panels → `editor-ui/instrument-panels`
- A tour of the editor for game makers → `make/editor-tour`
- Preferences and their fields → `reference/settings`

**Fit.** `fits`: about 1,700 words against M (3,000). The generated tables give the page its size: 16 options, 13 panels
and some 60 menu items, about 1,200 words. The prose is the paragraph on top, six introductions, the shortcuts table
(about 35 rows), the chips and pills table (about 15 rows), one line and the strip.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:48` | feature | link | The ways the editor runs and the exit code of a bad argument |
| `automation:141` | feature | link | The editor's automation options |
| `editor-ui:54` | feature | link | The options that matter to the UI |
| `editor-ui:112-117` | feature | link | The default layout, the panels that dock when opened, the menu bar, the main toolbar and the status pills |
| `editor-ui:122` | feature | link | `editor.showPanel` and `editor.showDialog` |
| `editor-ui:130` | feature | link | `EditorPanelDescriptor`, the columns of the panels table |
| `editor-ui:136` | feature | link | The built-in panels in drawing order with their ids |
| `editor-ui:142-155` | feature | link | Every panel, and the canvas mode view inside the Scene view |
| `editor-ui:197-199` | feature | link | The view toolbar, its chips and the debug view legend |
| `editor-ui:203` | feature | link | The Scene view's keys |
| `editor-ui:238-242` | feature | link | The global, focused and panel-local shortcuts, the shared Edit actions and the drag payloads |
| `editor-ui:257` | feature | link | The test editor whose probes the conventions name |
| `gamedev:43-46` | feature | link | The panels, menus, look and pills as a game maker meets them |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The editor's windows and panels: the shell, docking and the panel registry | `editor-ui/shell` | must |
| A command line with options | `basics/tools` | helps |
| Shortcuts and keyboard focus | `editor-ui/game-view` | helps |

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
| critic-reference-2 | should | shape | `reference/physics`, `reference/animation`, `reference/audio-input`, `reference/ui`, `reference/worlds-runtime`, `reference/editor`, `reference/automation`; some tables of `reference/renderer`, `reference/assets`, `reference/build` | The catalogue pages and `reference/scene`, `reference/core` and `reference/settings` name the teaching page of each group or table. These area pages plan only "one introduction per table", and their Covers never says that an introduction names where the subject is taught, so a reader who looks up a limit, a format or a service cannot go on to the page that explains it. | Each of these Covers says that every table introduction names the page that teaches its subject, one sentence each (about 20 words a table, about 40 tables, about 800 words in all; kind R has no size check). On `reference/renderer` this concerns the bindings, switches, fallbacks and device tables; on `reference/assets` the types, importers, budgets and statistics; on `reference/build` the options, presets, labels and shards. | `allocation/reference.md:480`, `:567`, `:629-630`, `:689`, `:744-745`, `:801`, `:867`, `:930`, `:1050`, `:394-395`; compare `:110-111`, `:190`, `:263`, `:328`, `:989` |
| critic-reference-7 | should | missing-item | new item on `reference/editor` | No page lists the files Strata keeps outside a project's assets. In `<project>/.strata/`: `Cache` with `ImportRecords.log`, `Scripts/Build`, `Scripts/IDE` and `Scripts/Bin`, `Saves` with `GraphicsOptions.json` and `InputBindings.json`, `Trash` (kept 30 days), `Recovery`, `Bake`, `Thumbnails`, `Thumbnail.png`, `EditorSession.json` and `EditorViewport.json`; in the user data folder `Strata/`: `Logs/StrataEditor.log`, `Preferences.json`, `EditorSettings.json`, `RecentProjects.json`, `Sessions/`, `Builds/` and `Projects/`; and a game's `<Name>/Logs/Game.log` and `<Name>/Saves`. Teaching pages name them one at a time, and `RecentProjects.json` on no page. | `reference/editor` adds a hand-checked table "Files outside the assets": the path (with the user data folder of each system), who writes it, what it holds, the variable that moves it (`STRATA_SESSION_DIR`, `STRATA_RECENT_PROJECTS`, `STRATA_SCRIPT_BUILDS_DIR`, `STRATA_RUNTIME_DIR`), whether it may be deleted, and the page that teaches it. `reference/worlds-runtime`'s table (4) and `reference/game-makers`' project folder link it. About 250 words. | `allocation/reference.md:855-871`, `:795-796`, `:1166-1168`; `Strata/src/Strata/Core/Platform.h:71-77`, `:115-129`; `StrataEditor/src/EditorApplication.cpp:283-286`; `StrataEditor/src/Editor/EditorPreferences.cpp:61-67`; `StrataEditor/src/Editor/ExternalEditor.cpp:207-213`; `StrataEditor/src/Editor/RecentProjects.cpp:21`, `:57-63`; `Strata/src/Strata/Network/EditorSession.cpp:146-156`; `StrataEditor/src/Editor/ScriptBuild.cpp:490-492`, `:509`; `StrataEditor/src/UI/ProjectDialogs.cpp:138`; `Strata/src/Strata/Project/Project.h:109-117`; `StrataEditor/src/Editor/EditorContext.cpp:71-75`, `:1647`; `StrataRuntime/src/RuntimeApplication.cpp:458`; `Strata/src/Strata/Core/SaveFiles.cpp:222` |
| critic-reference-10 | should | thin-home | `reference/editor`, table (1); `reference/worlds-runtime`, table (5) | `reference/editor` gives one exit code, 3 for a bad argument. At the pin the editor also exits with 1 when its command script cannot be read, fails, or has not finished at `--frames` or at `editor.quit`, when a screenshot fails, and when a headless editor without `--frames` has no automation; every program exits with 130 after an interrupt. CI runs and agents read these codes. | Table (1) lists every exit code of the editor with its causes, hand-checked against `EditorLayer.cpp` (about 80 words); the runtime's exit codes on `reference/worlds-runtime` name 3 and 130 beside 1, 2 and the game's own. This is the reference side of critic-foundation-11, which changes `core/first-frame`. | `allocation/reference.md:859-860`, `:796-797`; `allocation/completeness.md:184`; `StrataEditor/src/EditorLayer.cpp:521`, `:544`, `:557`, `:589`, `:679`, `:697`; `Strata/src/Strata/Core/CommandLineOptions.h:27`; `Strata/src/Strata/Core/Application.h:71`; `StrataRuntime/src/RuntimeApplication.cpp:36`, `:432-438` |
| critic-reference-13 | should | duplicate | `reference/game-makers`, sections (1), (4) and (7) | `tools/data/game-makers.json` chooses rows only of commands, components, SDK names and runtime options, so the cheat sheet's editor section (panels, shortcuts, chips), its conventions and its project folder can only be typed by hand. They copy facts that `reference/editor` (panels, shortcuts, chips) and `reference/notation` (conventions) hold as tables, and two hand-kept copies drift at each pin move. | The cheat sheet takes those rows from the tables that hold them: `game-makers.json` gains lists for panels, shortcuts and conventions, which `render` reads from data files that also make the tables of `reference/editor` and `reference/notation`; or the three sections become links to those tables with one line of use each. `../pipelines.md` §7.2 says which. No words added. | `allocation/reference.md:1153-1170`, `:861-866`, `:1219-1224`; `../pipelines.md:1145-1147` |
