# Brief: `reference/game-makers`

| Field | Value |
| --- | --- |
| Title | Cheat sheet for game makers |
| Kind | R |
| Size | M |
| Tracks | - |
| Needs | `make/first-script` |
| From | gamedev ch. 31 (components, commands, the SDK, runtime options and the project file, for game makers) |
| Unit | `plan/allocation/reference.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `reference/game-makers` — Cheat sheet for game makers

**Covers.** The paragraph on top says what the page is: the names a game maker uses every day on one page, each row
linking its full entry in the catalogue pages, for a reader who has made Coin Run and wants a name back without
searching. It is written for that reader: no internals, every term linked to its use home in `make`. The rows are
chosen by hand in the selection file `tools/data/game-makers.json` (`../pipelines.md` §7.2: the ids per table, for
commands, components, SDK names and runtime options), which the part's brief lists and this page's writer writes in
phase B; their facts (names, descriptions, defaults, options) come from the dumps and the parsed tables, so nothing is
typed twice, and `tools/reference.py check` fails when a chosen id leaves them at a pin move. The sections, in this
order. (1) The editor: the panels, the shortcuts a maker uses most (play and stop, save, undo and redo, the gizmo tools,
frame selection), the Scene view's chips. (2) The components a maker adds most (`Transform`, `Camera`, `MeshRenderer`,
the lights, `SkyLight`, `PostProcess`, `RigidBody` and the colliders, `CharacterController`, `AudioSource`, `Animator`,
`Script`, `Text`, the UI components), each with the few properties that matter first. (3) The script SDK in one table:
the callbacks in the order they run, `ST_SCRIPT_CLASS` and `ST_SCRIPT_FIELD` with the field types, and the calls of
`Entity`, `TransformComponent`, `Input`, `Time`, `Physics`, `RigidBody`, `CharacterController`, `Audio`, `Animator`,
`UI`, `Game` and the helpers that the `make` pages use. (4) The conventions a maker must know: metres, +Y up, -Z forward
for cameras, lights and `GetForward()`, glTF models facing +Z, Euler angles in degrees in the Inspector and in commands
but radians in `SetEulerAngles`. (5) The commands a maker runs from the CLI or a command script (play, input, capture,
export, batches). (6) The runtime's options a maker passes to an exported game. (7) The project folder: the `.stproj`
file, `Assets/` with its `.meta` files, `Scripts/`, `.strata/` (the import cache and script builds, which the
`.gitignore` that `Project::Create` writes leaves out), and what to keep under version control. Hand-written: one
sentence per section linking its `make` page, the conventions, the project folder table, and `## Where it lives in
Strata` (the panels, menus, commands and files a maker opens). The tool is `tools/reference.py render`, which reads
`tools/data/game-makers.json`.

**Leaves out.**

- Everything about each name beyond one line → `reference/components`, `reference/script-api`, `reference/commands`,
  `reference/editor`, `reference/worlds-runtime`
- Making the first game → `start/first-game`
- Positions, rotations and units, taught → `make/transforms-units`
- The editor, taught → `make/editor-tour`
- Projects and saving → `make/project-files`

**Fit.** `fits`: about 1,800 words against M (3,000). The generated facts of the about 80 rows that
`tools/data/game-makers.json` chooses give the page its size, about 1,500 words. The prose is the paragraph on top,
seven section sentences, a one-line use for each chosen row, the conventions and project tables and the strip.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:30-36` | feature | link | The launcher, templates, project creation, the project file, samples and recent projects |
| `gamedev:43-56` | feature | link | The editor's windows, from the panel set to the Streaming and Performance panels |
| `gamedev:67-71` | feature | link | The components, reflection-driven editing, built-in meshes, scene settings and the conventions a maker must know |
| `gamedev:124-128` | feature | link | The script module, script classes and fields, the 15 callbacks, the SDK namespaces and generic component access |
| `gamedev:131` | feature | link | Attaching scripts and editing their fields |
| `gamedev:222` | feature | link | Play, Simulate, Stop, Pause and Step |
| `gamedev:224` | feature | link | Simulated input |
| `gamedev:226-227` | feature | link | Viewport capture, command scripts and expectations |
| `gamedev:236` | feature | link | Export |
| `gamedev:239` | feature | link | The runtime's options |
| `gamedev:246-247` | feature | link | Commands are the API; `StrataCLI` and MCP |
| `gamedev:254-258` | feature | link | The five samples, named where each shows a row's name in use |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The editor's windows | `make/editor-tour` | must |
| Entities and components | `make/scenes-entities` | must |
| Writing and attaching a script | `make/first-script` | must |
| The game loop from a script's side | `make/script-loop` | helps |
| Positions, rotations and units | `make/transforms-units` | helps |
| Running a command from the CLI | `make/commands` | helps |
| Exporting a game | `make/export` | helps |

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
| critic-reference-7 | should | missing-item | new item on `reference/editor` | No page lists the files Strata keeps outside a project's assets. In `<project>/.strata/`: `Cache` with `ImportRecords.log`, `Scripts/Build`, `Scripts/IDE` and `Scripts/Bin`, `Saves` with `GraphicsOptions.json` and `InputBindings.json`, `Trash` (kept 30 days), `Recovery`, `Bake`, `Thumbnails`, `Thumbnail.png`, `EditorSession.json` and `EditorViewport.json`; in the user data folder `Strata/`: `Logs/StrataEditor.log`, `Preferences.json`, `EditorSettings.json`, `RecentProjects.json`, `Sessions/`, `Builds/` and `Projects/`; and a game's `<Name>/Logs/Game.log` and `<Name>/Saves`. Teaching pages name them one at a time, and `RecentProjects.json` on no page. | `reference/editor` adds a hand-checked table "Files outside the assets": the path (with the user data folder of each system), who writes it, what it holds, the variable that moves it (`STRATA_SESSION_DIR`, `STRATA_RECENT_PROJECTS`, `STRATA_SCRIPT_BUILDS_DIR`, `STRATA_RUNTIME_DIR`), whether it may be deleted, and the page that teaches it. `reference/worlds-runtime`'s table (4) and `reference/game-makers`' project folder link it. About 250 words. | `allocation/reference.md:855-871`, `:795-796`, `:1166-1168`; `Strata/src/Strata/Core/Platform.h:71-77`, `:115-129`; `StrataEditor/src/EditorApplication.cpp:283-286`; `StrataEditor/src/Editor/EditorPreferences.cpp:61-67`; `StrataEditor/src/Editor/ExternalEditor.cpp:207-213`; `StrataEditor/src/Editor/RecentProjects.cpp:21`, `:57-63`; `Strata/src/Strata/Network/EditorSession.cpp:146-156`; `StrataEditor/src/Editor/ScriptBuild.cpp:490-492`, `:509`; `StrataEditor/src/UI/ProjectDialogs.cpp:138`; `Strata/src/Strata/Project/Project.h:109-117`; `StrataEditor/src/Editor/EditorContext.cpp:71-75`, `:1647`; `StrataRuntime/src/RuntimeApplication.cpp:458`; `Strata/src/Strata/Core/SaveFiles.cpp:222` |
| critic-reference-13 | should | duplicate | `reference/game-makers`, sections (1), (4) and (7) | `tools/data/game-makers.json` chooses rows only of commands, components, SDK names and runtime options, so the cheat sheet's editor section (panels, shortcuts, chips), its conventions and its project folder can only be typed by hand. They copy facts that `reference/editor` (panels, shortcuts, chips) and `reference/notation` (conventions) hold as tables, and two hand-kept copies drift at each pin move. | The cheat sheet takes those rows from the tables that hold them: `game-makers.json` gains lists for panels, shortcuts and conventions, which `render` reads from data files that also make the tables of `reference/editor` and `reference/notation`; or the three sections become links to those tables with one line of use each. `../pipelines.md` §7.2 says which. No words added. | `allocation/reference.md:1153-1170`, `:861-866`, `:1219-1224`; `../pipelines.md:1145-1147` |
| critic-reference-14 | could | order | `reference/game-makers` | The page uses version control, in (7) "what to keep under version control", and command scripts, in (5), but its Assumes has no row for either. It is written for the game maker, whose list has neither. | Two `helps` rows: "Version control with git", taught by `basics/git`; "Running a command script", taught by `make/automated-playtests`. No words added. | `allocation/reference.md:1165-1168`, `:1203-1213`; `allocation/basics-a.md:457`; `style.md:66`; `allocation/README.md:311-312` |
| critic-reference-22 | could | missing-item | `reference/game-makers`, section (7) | `tools/reference.py dump` writes `templates.json` and `samples.json`, but no page shows them; only the names lint reads them. The two templates (`empty`, the default, and `basic3d` with its start scene) and the five samples with their names and descriptions are facts a maker looks up when creating a project or choosing a sample. | Section (7) adds a generated table of the templates and the samples from the two dumps, naming `make/project-files` and `make/samples`. About 40 words. | `../pipelines.md:1120-1127`; `allocation/reference.md:1166-1168`; `StrataEditor/src/Editor/EditorAssetCommands.cpp:254-269`; `StrataEditor/src/Editor/ProjectTemplates.cpp:23`; `Samples/Samples.json:6-37` |
