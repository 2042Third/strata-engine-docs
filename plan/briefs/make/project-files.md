# Brief: `make/project-files`

| Field | Value |
| --- | --- |
| Title | Projects, saving, undo and recovery |
| Kind | H |
| Size | M |
| Tracks | G, B |
| Needs | `make/editor-tour` |
| From | gamedev §1.2 (the project file, creation), concept 3, diagram 2, pitfall 1; editor-core "Undo and redo", "Autosave and crash recovery" (use side); editor-ui §1.11 (the recovery dialog); file extensions, hidden files and folders (`.strata/`, `.meta` files) and a path copied as text; a Variation section on opening a project of an older release (gamedev §1.2 "migration", release notes "Upgrading"); use home of the project folder, undo, autosave and recovery |
| Unit | `plan/allocation/make-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/project-files` — Projects, saving, undo and recovery

**Covers.** The goal: know what Coin Run's project folder holds, and never lose work. What must be true first: the
Coin Run project of `make/editor-tour` is open. Nine steps, each with what to see and the way back. (1) The launcher's
card of the project: **File ▸ Show Launcher**, the recent projects as cards (and **File ▸ Open Recent**; missing
projects are hidden), then right-click the CoinRun card for **Show in Folder** and **Copy Path**; the path is pasted
and read in its parts (the drive or the home folder, the folders, the separators `\` and `/`). (2) Make the system's
file browser show file extensions and hidden files (tabs per OS: File Explorer's View menu, Finder's Cmd+Shift+., the
Files app's Ctrl+H), with one paragraph from zero on what an extension is (`.stproj`, `.stscene`, `.stmat`) and why
some names start with a dot and hide. (3) Read the folder with the anatomy diagram: `CoinRun.stproj`, `Assets/` with a
`.meta` file beside every asset, `Scripts/` with `CMakeLists.txt` and the example `Spinner.cpp`, the `.strata/` folder
the editor rebuilds (cache, script builds, saves, thumbnail) and `.gitignore`, which keeps `.strata/` out of version
control; what the reader needs of git is one sentence (git keeps every version of the folder's files that one saves
with it, and `.gitignore` names what it leaves out), with `basics/git` linked as a side step. The rule in a `:::rule`
aside: never edit `.stscene`, `.stmat`, `.stproj` or `.meta` files by hand, and move, rename and delete them only in the
editor, because the editor indexes handles and references and a hand edit bypasses undo. (4) Open `CoinRun.stproj` in a
text editor only to look: its `Project` part (Name, StartScene, AssetDirectory, Scripts, Game, Export) and its
`Settings` part, read as JSON the way `start/how-to-read` taught. (5) **File ▸ Project Settings**: the pages Game,
Export, Collision Layers, Simulation, Timing, Graphics Quality and Input Actions, each named with the page of the book
that uses it; a settings change is one undo step and is written to the `.stproj`. (6) Save the scene with Ctrl+S (**File
▸ Save Scene**) and watch the saving pill: saves are written in the background and quitting waits for them; **Save Scene
As** for a copy. (7) Undo and redo: rename the Ground, move the Sun, then **Edit ▸ Undo** (the menu names each step),
Ctrl+Z and Ctrl+Y (or Ctrl+Shift+Z); one step per action, a whole drag is one step. (8) The question before changes are
lost: with an unsaved change, **File ▸ Open Scene** asks Save, Don't Save or Cancel. (9) Recover after a crash: make a
change, wait a few seconds, end the editor from the system (Task Manager, Force Quit, `kill`, in OS tabs), start it
again and open Coin Run: the **Recover Unsaved Changes** dialog (also **File ▸ Recover Unsaved Changes**) applies or
discards what the recovery journal kept; the step discards it, so Coin Run stays as `make/editor-tour` left it. `##
Result`: the reader knows every file of the folder and keeps work with save, undo and recovery; the page changes nothing
in Coin Run, so it has no end-state download. `## Variations`: opening a project made by an older release (0.5.0
projects get their collision layers moved into the project and are saved in the new format; make a copy first; the
release notes' "Upgrading" sections); a project kept in a folder that a cloud drive syncs; the scene file under version
control: a `.stscene` holds one entity per line, so after one entity is moved in the editor and the scene saved, a diff
of the file shows the one entity that moved, read in a text editor and never edited. The exercises (`new:16`) are two
editor tasks.

**Leaves out.**

- How undo steps are recorded and merged → `editor/undo`
- How saves run off the main thread, and the unsaved-changes guard inside → `editor/saving`
- The recovery journal's file and its folding → `editor/recovery`
- The recovery dialog's drawing → `editor-ui/launcher-dialogs`
- Settings sections, their versions and validation → `world/projects-settings`
- Templates and samples as data → `editor/projects`
- Each settings page in use → `make/input`, `make/physics`, `make/script-loop`, `make/quality`, `make/export`
- Moving, renaming and deleting assets, the trash → `make/assets`
- The terminal and paths in commands → `basics/tools`
- Git and version control, a side step that track G does not read in its order → `basics/git`

**Fit.** `fits`: about 3,900 words against M (3,000). Nine steps, two of them with OS tabs, take most of it, with the
paragraph from zero on extensions, hidden files and paths, three Variations, the folder diagram, six pictures and two
exercises. It is near M's top: a tenth step would not fit.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:33-34` | feature | home | What a new project writes, and the `.stproj` file's parts, read but not edited |
| `gamedev:36` | feature | home | Recent projects: the launcher's cards and **File ▸ Open Recent**; missing projects are hidden |
| `gamedev:37` | feature | home | The Variation: a project of an older release, migrated and saved in the new format |
| `gamedev:57` | feature | home | Undo and redo for every change: one step per action, project settings included |
| `gamedev:58` | feature | home | Autosave into the recovery journal a few seconds after an edit; **File ▸ Recover Unsaved Changes** |
| `gamedev:59` | feature | home | Saves written in the background; the saving pill; quitting waits |
| `gamedev:294` | concept | home | Projects and files: one folder of text documents with `.meta` handles beside them, edited only through the editor; the mistake of editing or moving files by hand |
| `gamedev:398` | figure | home | The project folder's anatomy |
| `gamedev:451` | figure | home | Project Settings: the page list with the Game page open; each other page is shown on its own page of the book |
| `gamedev:481` | rule | home | Never edit `.stscene`, `.stmat`, `.stproj` or `.meta` by hand; move, rename and delete in the editor |
| `gamedev:513` | rule | home | An unsaved scene stops opening another scene, closing the project and quitting until the person answers |
| `gamedev:659` | term | home | Recovery journal |
| `editor-core:604` | hands-on | home | Undo is your friend: changes, undone and redone, named in the Edit menu |
| `editor-core:614` | hands-on | home | Recover after a crash: the editor ended from the system, the dialog on the next open |
| `new:16` | hands-on | home | Exercises, two editor tasks: **Basic.** rename the Ground, move the Sun and change the Timing page's FixedRate, predict the three names that **Edit ▸ Undo** shows in turn, and undo all three to check; **Medium.** with a change unsaved, predict which of **File ▸ New Scene**, **File ▸ Open Scene** and closing the window ask Save, Don't Save or Cancel first, try each and answer Cancel. Evidence: `StrataEditor/src/Editor/EditorStateCommands.cpp:387` (`edit.history`, the named steps); `StrataEditor/src/Editor/EditorContext.cpp:694` (the unsaved-changes dialog's Don't Save) |
| `editor-core:124` | feature | use | `edit.undo`, `edit.redo` and `edit.history` in the command tabs |
| `editor-core:131` | feature | use | Saving a scene, in the steps' command tab (`scene.save`) |
| `editor-core:134` | feature | use | The unsaved-changes guard, as the person meets it |
| `editor-core:145` | feature | use | The recovery journal, a few seconds after an edit |
| `editor-core:153-154` | feature | use | `scene.recoveryStatus` and `scene.recover` in the command tab; the Recover dialog |
| `editor-core:210` | feature | use | Recent projects |
| `editor-core:310` | concept | use | Undo and redo, at the user's level: a history of named steps |
| `editor-core:330` | concept | use | No silent data loss, as the person meets it: the question, the saving pill |
| `editor-core:333` | concept | use | Autosave and crash recovery, at the user's level |
| `editor-core:515-517` | figure | use | The Edit menu with named steps; the unsaved-changes dialog; the saving pill |
| `editor-core:519` | figure | use | The Recover Unsaved Changes dialog after a simulated crash |
| `editor-core:671` | term | use | Undo step |
| `editor-ui:120` | feature | use | The unsaved-changes question: Save, Don't Save, Cancel |
| `editor-ui:218` | feature | use | The Recover Unsaved Changes dialog |
| `editor-ui:228` | feature | use | The Project Settings panel and its pages |
| `scene-ecs:212` | feature | use | The `.stproj` and the project's layout on disk |
| `scene-ecs:464` | figure | use | The project on disk, the source of the anatomy diagram |
| `scene-ecs:605` | hands-on | use | The Variation of a scene under version control: one entity moved, the scene saved, and the diff shows the one entity that moved, because a `.stscene` holds one entity per line. Evidence: `Strata/src/Strata/Scene/SceneDocumentWriter.h:77-78` (read at the pin) |
| `scene-ecs:685-686` | term | use | Project; the intermediate folder `.strata/` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The editor's panels, menus and the launcher | `make/editor-tour` | must |
| Reading JSON: objects, names and values | `start/how-to-read` | helps |
| The Basic 3D project and its five entities | `start/first-game` | helps |
| The terminal and paths in commands (the `kill` of step 9's Linux tab) | `basics/tools` | helps |
| Git and version control | `basics/git` | helps |

**Starting state.** The end state of `make/editor-tour`: Coin Run's fresh project from Basic 3D (`startsFrom
{"tutorial": "make/editor-tour"}`). Every change the steps make is undone, discarded or not saved, so the project ends
as it began and `make/scenes-entities` starts from the same checkpoint.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `recovery-journal` | Recovery journal (use) | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-a-1 | must | stale-item | `make/project-files` (step 1) | Step 1 opens the launcher with **File ▸ Show Launcher** while Coin Run is open. At the pin that item is greyed whenever a project is open; only **File ▸ Close Project** (after the unsaved-changes question) leads to the launcher and its cards. | Step 1 closes the project with **File ▸ Close Project**, reads the CoinRun card there (right-click: **Show in Folder**, **Copy Path**), and opens Coin Run again by clicking its card. **File ▸ Show Launcher** stays only on `make/editor-tour`, for the way back after "Continue without a project" (about 40 words more). | `allocation/make-a.md:105-108`; `StrataEditor/src/EditorLayer.cpp:1476-1484` (the comment at `:1481`: "with a project open, Close Project leads there"); `StrataEditor/src/Panels/WelcomePanel.cpp:630-637` |
| critic-make-a-24 | could | missing-item | `make/project-files` (step 3) | The anatomy lists `Scripts/` with `CMakeLists.txt` and `Spinner.cpp`. A new project's `Scripts/` also holds `CMakePresets.json`, which the editor writes and rewrites for code editors (IntelliSense), and a `.gitignore` that keeps it out of version control; the reader sees both once step 2 shows hidden files. | Step 3 names the two files in one sentence each and links `basics/git` for `.gitignore` (about 40 words). | `allocation/make-a.md:111-114`; `allocation/basics-a.md:493`; `StrataEditor/src/Editor/EditorContext.cpp:261-263`; `StrataEditor/src/Editor/ScriptProject.cpp:396-403`; `StrataEditor/src/Editor/ScriptBuild.cpp:613-614` |
| critic-make-a-30 | could | order | `make/project-files` (step 9) | Step 9's Linux tab ends the editor with `kill`, which needs a process number and a terminal skill that `basics/tools` teaches after this page on track B (and as a side step on track G). Plain `kill` sends SIGTERM, and at the pin that is no crash: the editor closes in order through its main loop and logs "Interrupted (Ctrl+C or a request to terminate): closing". | The Linux tab ends the editor with the System Monitor's Kill, or gives a whole line to paste, `pkill -KILL StrataEditor`; the Assumes row of `basics/tools` goes (no words added). | `allocation/make-a.md:126`, `:200`; `outline-1.md:77-79`; `Strata/src/Strata/Engine/EntryPoint.h:22-23`; `Strata/src/Platform/Posix/PosixPlatform.cpp:981-990`; `Strata/src/Strata/Core/Application.cpp:261-268` |
