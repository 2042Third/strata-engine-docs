# Brief: `editor-ui/launcher-dialogs`

| Field | Value |
| --- | --- |
| Title | Launcher and dialogs |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `editor-ui/shell`, `editor/projects`, `editor/recovery`, `editor/trash-references`, `worlds/export` |
| From | editor-ui §1.11 (the Welcome panel, New Project, Open Sample, About, Export, Recover Unsaved Changes, Delete and New Script dialogs) |
| Unit | `plan/allocation/editor-ui.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor-ui/launcher-dialogs` — Launcher and dialogs

**Covers.** The screens around the editing: the launcher and the dialogs. The job, then the problem in one paragraph
(a start screen and dialogs that never block a frame and never lose work). The map: the launcher is a panel of the
Launcher placement, drawn instead of the dock space while no project is open; the dialogs are drawn by `EditorLayer`
every frame and run commands. The contract: a dialog's action is a command; a dialog that replaces the scene asks
through `EditorShell` and asks again when the scene changed after the answer; no file is read in a frame. The toy is a
modal dialog of about 30 lines that runs one command.

The real code: the launcher's recent projects, read with their pictures on an I/O thread (a path out of reach can take
seconds) and applied only when the list did not change meanwhile; the project dialogs' answered version, and the
re-ask through `RequestReleaseProject`; the Export dialog's progress, Cancel and Hide (closing it leaves the export
running). Then each screen: the launcher (the hero band, New and Open Project, Open Sample, recent projects as picture
cards with search and a context menu, template and sample cards, "Connect an AI agent" with its command line to copy
and the automation server's state in four forms (ready on a port, agents connected, off, failed with its reason), the
footer with version, commit, GPU and startup time, errors shown on it, Continue without a project, File ▸ Show
Launcher); New Project and Open Sample (template cards, the name, a location remembered in `imgui.ini`); About Strata
(build, GPU, driver, startup, UI scale, Copy Details, the third-party notices drawn from Markdown); Export Game (the
fields of `project.export`, the result with Open Folder); Recover Unsaved Changes; the Delete asset confirmation that
lists what uses the asset; New Script (the External Editor page of Preferences is `editor-ui/settings-windows`').
Pictures: the launcher and the two project dialogs, taken with the recipe of `start/first-game`'s pictures; the agent
card in its four states; About and Export, the Export dialog from the one capture set it shares with
`assets/packs-export`. At the end the reader can name the command each button runs and say why a dialog asks again.

**Leaves out.**

- What projects, templates, samples and recent projects are → `editor/projects`
- The export's work and its state machine → `worlds/export`
- The recovery journal → `editor/recovery`
- Why a delete is refused and the trash → `editor/trash-references`
- Connecting an agent through MCP → `automation/mcp`
- The Preferences dialog → `editor-ui/settings-windows`
- The External Editor page → `editor-ui/settings-windows`
- Project pictures → `editor/thumbnails`

**Fit.** `fits`: about 5,725 words against L (5,000). Seven screens and three excerpts take the most; the launcher's and
the project dialogs' pictures follow the recipe of `start/first-game`, and the Export dialog's set is shared with
`assets/packs-export`.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:154` | feature | home | The Welcome panel of the Launcher placement |
| `editor-ui:214-219` | feature | home | The launcher; New Project and Open Sample; About Strata; Export Game; Recover Unsaved Changes; the Delete asset confirmation |
| `new:12` | code | home | `StrataEditor/src/Panels/WelcomePanel.cpp:225-279`: the recent projects read on an I/O thread, one read at a time, applied only when the list did not change meanwhile |
| `new:13` | code | home | `StrataEditor/src/UI/ProjectDialogs.cpp:221-258`: the undo version and project-file writes noted when the person answered; a changed scene or a save in flight asks again over the dialog |
| `new:14` | code | home | `StrataEditor/src/UI/ExportDialog.cpp:186-215`: the dialog shows an export's progress whoever started it; Cancel runs `project.cancelExport`, Hide leaves it running |
| `editor-ui:580` | figure | home | About Strata; Export Game during an export: the Export dialog's pictures are one capture set with `assets:512` and `worlds-runtime:400`, made once (R34, D42) and first shown on `assets/packs-export`; this page's caption explains the dialog's code |
| `editor-ui:745` | term | home | Launcher |
| `new:42` | open | home | Check: A capture step that opens the launcher's card. The claim, read from the code and not run: the launcher and its "Connect an AI agent" card show only while no project is open, so a whole-editor figure, which opens a project copy, needs a `project.close` step (after which "the editor shows its launcher"); the card is drawn last in the launcher's one scrolling region, after the recent projects and the template and sample cards, so at 1600x900 it may stand below the region's edge, and the launcher's code sets no scroll position. The figure `automation:574` waits for the result (automation-q4). Evidence: `StrataEditor/src/EditorLayer.cpp:1069-1072`; `StrataEditor/src/Editor/EditorAssetCommands.cpp:346-347`; `StrataEditor/src/Panels/WelcomePanel.cpp:461-497`; `grep -n SetScroll StrataEditor/src/Panels/WelcomePanel.cpp` finds nothing |
| `new:43` | hands-on | home | Exercises (D27): the command each button of New Project and Open Sample runs, found with a search for `project.create` and `project.openSample` in `ProjectDialogs.cpp` (Basic, trace); `editor.showDialog {dialog: "about"}` sent from a terminal to a running editor, then Copy Details pasted and read (Medium, command); Don't Save answered in New Project, an entity created with `entity.create` from a terminal while the dialog is open, then Create pressed, to see the question come again (Hard, predict then run). Evidence: `StrataEditor/src/UI/ProjectDialogs.cpp:221-228`, `:335`, `:415`; `StrataEditor/src/EditorLayer.cpp:233-243` |
| `editor-ui:549` | figure | use | The launcher with recent projects and their pictures, template and sample cards, "Connect an AI agent" and the footer: the figure recipe of `start/first-game` (`gamedev:438`), or a crop of what this page's code explains (start-q8) |
| `editor-ui:550` | figure | use | The New Project dialog; the Open Sample dialog: the figure recipe of `start/first-game` (`gamedev:439`) (start-q8) |
| `editor-ui:220` | feature | use | The New Script dialog, drawn by `EditorLayer` among the dialogs; the External Editor page of the same item is homed on `editor-ui/settings-windows` (critic-editor-ui-3) |
| `editor-ui:102` | feature | use | `Markdown`, which draws the notices in About |
| `editor-ui:90` | feature | use | The kit's modals |
| `editor-core:154` | feature | home | The Recover dialog opens itself for a crash's leftovers; toasts tell of discards |
| `worlds-runtime:168` | feature | home | The Export dialog: File ▸ Export Game and the toolbar's Export, the loading-scene choice, the identity summary, exports that agents started |
| `worlds-runtime:175-176` | feature | home | The launcher; the project dialogs and the remembered location (first `<home>/StrataProjects`) |
| `worlds-runtime:400` | figure | home | The Export dialog before, during and after: one capture set with `editor-ui:580` and `assets:512` (`assets/packs-export`), made once (R34, D42); the caption says what this page teaches |
| `worlds-runtime:405-406` | figure | home | The launcher; New Project with the basic3d template and the scene it makes: taken with the recipe of `start/first-game`'s pictures (`gamedev:438-439`, which `editor-ui:549-550` use; start-q8) |
| `worlds-runtime:566` | term | home | Launcher: one glossary entry with `editor-ui:745` |
| `automation:185` | feature | home | The "Connect an AI agent" card: the `claude mcp add strata -- <StrataCLI> mcp` line with its copy button (a warning in its place when StrataCLI is not next to the editor), and the server's state as a pill from `EditorAutomationState`: ready on port N, N agents connected, off, failed with its reason: taught with `editor-ui:214` |
| `automation:574` | figure | home | The card in its four states: ready on a port, one agent connected, off (`--no-automation`), failed (a taken `--automation-port`); its capture waits for the check of `new:42` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Launcher, templates and samples: the model, recent projects, `project.create`, `project.open`, `project.openSample` | `editor/projects` | must |
| Autosave and crash recovery | `editor/recovery` | must |
| The trash, references and refused deletes | `editor/trash-references` | must |
| The export as a whole: `GameExport`, its stages and options | `worlds/export` | must |
| Asking the person: modals, the re-ask rule, `DrawDiscardQuestion` | `editor-ui/shell` | must |
| Jobs on I/O threads | `core/jobs` | must |
| Project pictures | `editor/thumbnails` | helps |
| Script templates and the external editor | `editor/script-builds` | helps |
| The MCP server (`StrataCLI mcp`) | `automation/mcp` | helps |
| The editor's automation options: `--no-automation`, `--automation-port` | `automation/sessions` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `launcher` | Launcher | - |
