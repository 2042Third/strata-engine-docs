# Notes: make/project-files

## New terms

None proposed. The page defines **recovery journal** (glossary home) in bold; "project" and "handle" are explained in plain words.

## Since

0.3.0: projects, undo and recovery date from the first tag (`gamedev` rows 33-34, 57, 58 at release 0.3.0).

## Requests

- Words "unsaved", "Notepad" and others were avoided; none requested.

## Not verified

- No step was run in the editor; every menu label, dialog text and button name was read in `StrataEditor/src/EditorLayer.cpp`, `WelcomePanel.cpp` and `UI/RecoveryDialog.cpp` at the pin.
- The undo name `Move Entity` of a gizmo drag is read in `Editor/TransformEdit.cpp`; the Inspector's own step name was not read, so the page uses the gizmo.
- That Windows hides files by attribute (so `.strata` may show), and the labels of File Explorer, Finder and the Files app, are general knowledge, not checked.
- That Task Manager's "End task" ends the editor without a clean quit; the page gives `taskkill /F` beside it.
- That the Coin Run project's `.stproj` omits `Game` and `Settings` until a page changes: read from `Project::MakeFileText`, not from a created project.
- The three figures (`project-settings`, `edit-menu`, `recovery-dialog`) wait for editor screenshots (tier 2); none was taken.
- Which page of the book uses **Timing** (`make/script-loop` is assumed from the brief's list).

## Findings not applied

- critic-make-a-1 applied: step 1 closes the project with **File ▸ Close Project** and reads the card in the launcher; **Show Launcher** is not used.
- critic-make-a-24 applied: step 3 lists `CMakePresets.json` and the `.gitignore` of `Scripts/`.
- critic-make-a-30 applied: the Linux tab uses `pkill -KILL StrataEditor`; the `basics/tools` row is not needed.

## Clerk

- No term or word asked (recovery journal is the glossary's).

## Figures

Taken once with the provisional build (engine 5b975ad2831e, `--provisional`); nothing published, `waitsFor` kept.

- `project-settings`: round 1 good. The recipe pictures the ProjectSettings panel (layout `first-game.ini`); the panel opens on Game, which shows Start Scene Main, an empty Title and Version 1.0.0, as a basic3d project has them. Caption and alt now say so. The panel's list differs from step 5's sentence: it groups the pages under Project (Game, Export), Input (Input Actions), Physics (Collision Layers, Timing, Simulation) and Rendering (Graphics Quality), so Input Actions comes second and Timing before Simulation. Round 2 (a viewer's report): the picture is right and the recipe and caption stay; the fault is in step 5's words, which this take may not edit. The page's writer should reword its "You should see" to the panel's order and groups: Project (**Game**, **Export**), Input (**Input Actions**), Physics (**Collision Layers**, **Timing**, **Simulation**), Rendering (**Graphics Quality**).
- `edit-menu`: cannot. No command opens a menu, so the item `Undo Move Entity` cannot be pictured; the recipe is left as written (it takes the plain window). What the page gets instead: either a drawn diagram of the Edit menu with `Undo Move Entity` and a grey `Redo`, or the state after step 7's changes, the Hierarchy panel (`entity.rename` of `Ground` to `Floor`, then `selection.set` of the Sun, `editorWindow.panel: Hierarchy`), with a caption about the renamed row instead of the menu. A move through `component.set` would be named `Set Transform`, not `Move Entity`, so no command makes the gizmo's step name.
- `recovery-dialog`: cannot as the page describes it. A take's editor always quits in order, and an editor that closes in order marks its unsaved changes as discarded, so commands cannot leave an entry of a crash. The recipe takes the nearest honest picture: rename Ground, `scene.open` Main with `force` (the changes become a discarded entry), `scene.recoveryStatus`, `editor.showDialog recovery`, in a 960 × 540 window (`dialogs.ini`). It shows the dialog with one entry for Main, Recover, Discard and Later, readable; its detail line reads `discarded on purpose` where the reader's reads `left when the editor closed unexpectedly`. Caption and alt now say so. Publishing it needs the page to accept that line, or a crash entry that a take could copy into `.strata/Recovery` (a recovery file of a killed editor, kept beside the tutorial).
- Settled 2026-11-18 (page words): step 5's "You should see" names the four groups in the editor's order (`SettingsBrowser::BuildEntries`: Game and Export first, then categories in registration order).

Taken 2026-11-23 at the pin v0.8.0 (319075e3), without `--provisional`; one round each.

- `project-settings`: published. The panel shows the four groups as step 5 now names them, Game open with Start Scene Main, Loading Scene None, an empty Title and Version 1.0.0; caption and alt hold. `waitsFor` removed.
- `recovery-dialog`: published. The dialog lists Main, `Scenes/Main.stscene · 1 entity · just now · discarded on purpose`, Recover, Discard and Later, readable at 960 × 540; the caption says the entry was discarded on purpose and how a crash's line reads, so the picture matches it. `waitsFor` removed.
- `edit-menu`: waits. v0.8.0 still has no command that opens a menu (`editor.showDialog` lists dialogs only), so its `waitsFor` is now `tier 3: the Edit menu open; no editor command opens a menu or popup`, and `take` skips it. The nearest honest pictures are those proposed above: a drawn Edit menu with `Undo Move Entity` and a grey Redo, or the Hierarchy after the rename, with a caption about the renamed row.

Finished 2026-11-24 at the final pin v0.8.0 (319075e3).

- `edit-menu`: still cannot be taken (no command opens a menu or popup); `waitsFor` kept as the request for a later edition, `standIn` is `edit-menu-drawing`.
- `edit-menu-drawing` (new, diagram): the Edit menu open after step 7's changes with the Sun selected, drawn from `EditorLayer.cpp:1824-1853`: `Undo Move Entity` highlighted with Ctrl+Z, Redo grey (nothing to redo), the selection's items, Paste grey (no entity copied, `EditorActions::CanPaste`), Select All; notes beside the grey items. Chosen over the Hierarchy after the rename because the paragraph teaches that the menu names the step, which only the menu shows. The page places it where `edit-menu` stood, and step 7's "You should see" now ends by introducing it. Rendered in both themes and looked at; `drawings.mjs check` passes.

## Tutorial run

- 2026-11-18, pin build: exercise 1 passed. `edit.history` names the steps `Rename 'Ground' to 'Floor'`,
  `Set Translation of 'Sun'` and `Set Timing`; the file now checks all three, and the answer says that a gizmo drag is
  `Move Entity` and an Inspector edit `Edit Transform Translation` (`TransformEdit.cpp:46`, `PropertyEdit.cpp:147`).
- 2026-11-18, second run (pin build): exercise 1 passed. The file now also checks the page's values: after
  `project.setSettings`, `scene.info` reads `settings.fixedRate` 120 steps a second from `project`; after the three
  undos, the source is `scene` again and `entity.find` finds `Ground`. The worked solution says so.
- 2026-11-24, final run (plan/process.md step 15): the pin-build run in the stamp was still current; exercise 1 passed
  as written with the official v0.8.0 package (Strata-0.8.0-windows-x64.zip), so `tutorials.py check --release` finds
  nothing for the page.

## Track walk G-final-2 (2026-11-24)

Answers in `plan/walks/G-final-2.md` (WK11 to WK18). The tree lists `Materials/Ground.stmat`; `Scripts/CMakePresets.json`
and `Scripts/.gitignore` are written only once the toolchain is known (`StrataEditor/src/Editor/ScriptBuild.cpp:582-622`,
called at project creation and at each build), and the page says so. The book's code blocks draw tabs as two spaces
(Expressive Code's default), said in step 4. Step 5's tab names `sections[].title` and the `project` fields; step 7's
tab gives the commands and their step names; step 8's tab says not to pass `force`; step 9 warns that `taskkill /IM`
and `pkill` end every editor, gives the PID form, names `scene.recover`'s `scene` and `action`, and says discarded
changes stand as more entries. Exercise 1's answer shows `project.setSettings` with `value` and `"120"` as text.
