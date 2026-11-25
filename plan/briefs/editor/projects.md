# Brief: `editor/projects`

| Field | Value |
| --- | --- |
| Title | Opening projects and scenes: templates, background loads and migration |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `editor/saving`, `world/projects-settings`, `world/sub-scenes` |
| From | editor-core §1.9 (templates and `scene.new {template}`, samples as copies without `.strata`, recent projects, `BeginOpenProject`, `ProjectMigration`, opening scenes in the background and the read-only guard, `project.create`, `project.open`, `project.close`, `project.openSample`); worlds-runtime ch. 11 "The launcher, templates and samples" (the code side); it stands after `editor/saving` and `editor/recovery` because opening and closing a project release the edited scene (the unsaved-changes guard and `AfterSaves` are `editor/saving`'s, the recovery question `editor/recovery`'s) |
| Unit | `plan/allocation/editor.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor/projects` — Opening projects and scenes: templates, background loads and migration

**Covers.** The problem: a project of tens of thousands of assets, or a start scene of a million entities, must open
without freezing the editor, and opening or closing a project lets go of the edited scene, so it must not lose work. The
naive answers: load everything before the first frame (the window stays empty for minutes), or keep editing the old
scene while the new one loads (the edits vanish at the swap). The idea: open content in the background while the old
scene is shown, keep the old scene read-only, swap between two frames, and cancel a load when a newer request comes. The
code follows a project's life. `project.create` with a template (`empty`, or `basic3d` with its camera, sun, sky, ground
and post process) and `scene.new {template}`. `project.open` wraps `BeginOpenProject` in the guard and `AfterSaves`,
then `OpenProjectInternal`: the project file is read before the open project closes; the asset manager scans in the
background; the trash is purged of what is older than 30 days; the recovery scan waits for the asset scan; the script
engine opens; a project saved by 0.5.0 or older is migrated once (`ProjectMigration` reads every scene's collision
layers on a job, merges them into the project's table with the start scene's names first, reports conflicts, and the
file is written as version 3); the start scene waits for the scan and the migration; the project joins the recent
projects (at most 12, shared by every editor, read-only for scripted runs). The recent projects share `<user
data>/Strata/` with the person's other file, the preferences store (`EditorPreferences`, `Preferences.json`, format 1,
at most 64 KiB): the values of the settings registry's user sections for every project, each validated by its section
and kept as stored when its section refuses it, written in the background so that a failed write leaves the file
unwritten and the change in memory, a file that a later editor wrote left alone with changes refused, and 0.5.0's
`EditorSettings.json` imported once; `preferences.set` and `preferences.save` are Session commands and record no undo
step. Opening a scene: `BeginOpenScene` asks `SceneLoader` for the file as it is now and prepares the render proxies
while the old scene is shown; `CheckSceneEditable` is the read-only guard for code that edits outside `CommitEdit`;
`UpdateSceneLoad` swaps in `FinishOpenScene` (through `ResetScene`, a residency trim, the scene's stored camera or a
framing), then runs the prefab catch-up before anyone sees the scene; `scene.open` answers one frame after the swap with
the frames' times; `scene.loadStatus` reports progress; a newer request cancels. Samples open as copies without
`.strata` (`project.samples`, `project.openSample`), and `project.close` takes the same guard. The rules: a scene being
opened is read-only; scenes load through `SceneLoader`, never `LoadAssetSync`, and are let go with
`Scene::ReleaseInBackground`. The example opens a copy of `Samples/OpenWorld` with `project.openSample`, polls
`scene.loadStatus`, and tries an edit while the start scene opens to read the refusal. The trace exercise follows a
scene's open from `BeginOpenScene` to the frame `FinishOpenScene` swaps it in. Afterwards the reader can open, create
and close projects from code without a stalled frame or a lost edit.

**Leaves out.**

- The guard, `AfterSaves` and `ResetScene` themselves → `editor/saving`
- The launcher and the project dialogs as they are drawn → `editor-ui/launcher-dialogs`
- The scene loader's states, slices and prepared loads → `world/sub-scenes`
- The project file, its versions and settings sections → `world/projects-settings`
- The settings file writer and the Editor discard scope → `editor/saving`
- The Preferences window as it is drawn → `editor-ui/settings-windows`
- Project pictures → `editor/thumbnails`
- The default template's lighting → `make/lighting`
- The project folder as a game maker sees it → `make/project-files`

**Fit.** `fits`: about 5,650 words against L (5,000). Counted again from the sections, with the person's preferences
store and the trace exercise: a project's open, a scene's open and the migration with four excerpts take the most,
beside templates, samples, recent projects and the preferences.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:361` | concept | home | Opening content in the background: read-only while loading, swap between frames, cancel on a newer request |
| `editor-core:204-208` | feature | home | `BeginOpenScene`, `CheckSceneEditable`, `scene.open`, `scene.loadStatus`, `BeginOpenProject` |
| `editor-core:209-210` | feature | home | Templates (`empty`, `basic3d`) and samples as copies without `.strata`; recent projects |
| `new:70` | feature | home | The person's preferences store (`EditorPreferences`), beside the recent projects in `<user data>/Strata/`: `Preferences.json` (format 1, at most 64 KiB) holds the values of the settings registry's user sections for every project; a stored section is validated by its section and kept as stored when refused; writes run in the background, and a failed one keeps the change in memory and the file unwritten; a file a later editor wrote is left alone and changes are refused; 0.5.0's `EditorSettings.json` is imported once; `preferences.set` and `preferences.save` are Session commands with no undo step (about 250 words; the writer and the Editor discard scope stay `editor/saving`'s). Evidence: `StrataEditor/src/Editor/EditorPreferences.h:23-35`, `:37`, `:43-48`, `:64-79`; `StrataEditor/src/Editor/EditorContext.h:107-112`; `StrataEditor/src/EditorApplication.cpp:304`, `:363`; `StrataEditor/src/Editor/EditorPreferencesCommands.cpp:121-156`, `:158-183` |
| `new:5` | feature | home | The migration of projects saved by 0.5.0 or older: the scenes' collision layers read on a job and merged into the project's table, conflicts reported, the file written as version 3. Evidence: `StrataEditor/src/Editor/ProjectMigration.h:15-57`; `StrataEditor/src/Editor/EditorContext.cpp:488-550` |
| `new:6` | code | home | `StrataEditor/src/Editor/EditorContext.cpp:365-451`: `OpenProjectInternal`, a project that opens at once while its assets scan and its start scene waits |
| `new:7` | code | home | `StrataEditor/src/Editor/EditorContext.cpp:770-807`: `BeginOpenScene`; with `:869-879` (`CheckSceneEditable`) and `:899-942` (the swap and the prefab catch-up) |
| `new:8` | code | home | `StrataEditor/src/Editor/EditorContext.cpp:505-550`: `UpdateProjectMigration`, the merge on the main thread and the file written once |
| `editor-core:502` | figure | home | A scene opening in the background, from the request to `scene.open`'s answer |
| `editor-core:531` | figure | home | The viewport's load card and the read-only banner while a large scene opens |
| `editor-core:571` | rule | home | A scene being opened is read-only: check `CheckSceneEditable` outside `CommitEdit` |
| `editor-core:578` | rule | home | Never `LoadAssetSync`; load scenes through `SceneLoader`; release them with `Scene::ReleaseInBackground` |
| `worlds-runtime:177-179` | feature | home | Templates, recent projects and samples, as the worlds survey lists them |
| `worlds-runtime:181` | feature | home | The project and template commands |
| `gamedev:365` | code | home | `StrataEditor/src/Editor/ProjectTemplates.cpp:31-95`: what `basic3d` puts in a new scene |
| `gamedev:555` | hands-on | home | Exercise: read `PopulateBasic3D` and add a third template |
| `new:53` | hands-on | home | Trace it yourself (D27): open a copy of a sample with `project.openSample`, with breakpoints in `BeginOpenScene`, `UpdateSceneLoad` and `FinishOpenScene`; count the frames between the request and the swap, and name what runs after the swap before anyone sees the scene. Evidence: `StrataEditor/src/Editor/EditorContext.cpp:770-807`, `:899-942`, `:944` |
| `worlds-runtime:567-568` | term | home | Template, sample |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The unsaved-changes guard, `AfterSaves` and `ResetScene` | `editor/saving` | must |
| Deferred commands | `editor/deferred-commands` | must |
| `SceneLoader`, its states, prepared loads and `ReleaseInBackground` | `world/sub-scenes` | must |
| The project file, its versions and settings sections | `world/projects-settings` | must |
| Settings sections of user scope | `world/projects-settings` | helps |
| The settings file writer and unwritten settings files | `editor/saving` | helps |
| The project's collision layer table | `physics/collision-layers` | helps |
| The background asset scan | `assets/importing` | must |
| Residency, trims and pins | `assets/residency` | helps |
| Render proxies built before a scene is shown | `draw/render-scene` | helps |
| The recovery scan and its offer | `editor/recovery` | helps |
| The prefab catch-up when a scene opens | `editor/prefab-instances` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `sample-editor` | Sample (editor) | - |
| `template` | Template | - |
