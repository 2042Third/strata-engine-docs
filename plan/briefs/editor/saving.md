# Brief: `editor/saving`

| Field | Value |
| --- | --- |
| Title | Saving without stalling |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `editor/undo`, `editor/deferred-commands`, `core/files`, `core/jobs` |
| From | editor-core ch. 4 (`DocumentSaver`, `SettingsFileWriter`, atomic writes, save points under concurrent edits, the unsaved-changes guard, `AfterSaves`, `ResetScene` and `ReleaseProject`); home of "no silent data loss"; asking the person is `editor-ui/shell` |
| Unit | `plan/allocation/editor.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor/saving` — Saving without stalling

**Covers.** The problem: in 0.3.0, saving a scene of a million entities froze the editor for 22 seconds on the
development machine (`Docs/Releases/0.4.0.md:60-62`), and a command that replaces the scene can drop edits nobody has
saved. The naive answers are named with their failure: save
on the main thread, set a dirty bit, mark everything saved when the save ends, write the file in place. The first idea,
saving safely: take a snapshot in the frame, serialize it on a job, write it atomically under a claim so that the file
watcher and moves leave it alone, publish the written document on the main thread, and let a newer save of the same
documents replace a queued one. The second idea, no silent data loss: every command that would discard work checks
first, waits for saves in flight, and discards only what it was told to. The code follows that order. `DocumentSaver` is
the one path (snapshot, `SceneDocumentWriter` on a job, reference scan, hash, atomic write under a claim, publish in
`Update`). A scene save runs `BeginSaveScene`, then `SubmitSceneSave` (break the merge, take the save point, copy the
scene's serialized state, take the recovery token), then `OnSceneSaveEnded` (mark that save point saved, the project
picture, the recovery journal; a failed Save As restores the scene's handle and name). `SavePoint` lets edits go on during
a save: what was copied is marked saved, later edits stay unsaved. `scene.save {wait}` and the `saving` section of
`editor.status` show it to clients. `SettingsFileWriter` writes the project file and the preferences the same way, and
`ProjectSettingsAction` makes a settings change an undo step whose file is written in the background. Then the guard:
`CheckUnsavedChanges` with `force`, its action and its `DiscardScope`; `AfterSaves`, a function that wraps a handler so
that `force` never discards a save in flight; `scene.new` as the pattern of guard, `AfterSaves` and `MayDefer` in one
command; `ResetScene`, every scene replacement in its order (the recovery journal first); `ReleaseProject`. What the
design cannot do yet: prefab and asset documents (`prefab.apply`, the Asset tab) are still written in the frame. The
example saves a large world scene with `scene.save {wait: false}`, edits on while the saving pill shows, then tries
`scene.open` without `force` and reads the refusal. Exercises: trace a held background save in a test; remove
`AfterSaves` from `scene.new` on a scratch branch and find the test of `Editor.Saves` or `Editor.DataSafety` that fails.
Afterwards the reader can add a command that replaces the scene without losing a save or an edit.

**Leaves out.**

- How the UI asks the person (modals, the re-ask rule, `DrawDiscardQuestion`) → `editor-ui/shell`
- The recovery journal that `ResetScene` writes first → `editor/recovery`
- Atomic writes, private files and UTF-8 paths → `core/files`
- The streamed scene document → `world/serialization`
- The world's two-step save → `editor/worlds`
- The project file and its settings sections → `world/projects-settings`
- Saving as a game maker does it → `make/project-files`

**Fit.** `fits`: about 5,200 words against L (5,000). Two concepts, five excerpts (the saver's is long), three figures,
three rules and two exercises; the asset manager's document writes take one paragraph.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:326` | concept | home | Saving safely: snapshot, job, atomic write, claims, coalescing, publish; save points under concurrent edits |
| `editor-core:330` | concept | home | No silent data loss: guards, `force`, waiting for saves in flight, unwritten settings |
| `editor-core:107` | feature | home | `SavePoint` for background saves: marking the saved step wherever the history moved |
| `editor-core:123` | feature | home | `ProjectSettingsAction`: settings as undo steps whose file is written in the background |
| `editor-core:130-137` | feature | home | `DocumentSaver`, the scene save, `scene.save {wait}`, `SettingsFileWriter`, the guard, `AfterSaves`, `ResetScene`, `ReleaseProject` |
| `editor-core:139` | feature | home | What the design cannot do yet: asset documents are written in the frame |
| `assets:143` | feature | home | The asset manager's native document writes: create, save, reserve, the write claim and its commit, publish |
| `editor-core:804` | open | home | Checked at the pin: `prefab.apply` writes through `AssetEdit::ApplyDocument` (`StrataEditor/src/Editor/EditorPrefabCommands.cpp:570`), which saves in the frame (`StrataEditor/src/Editor/AssetEdit.cpp:95`) |
| `editor-core:414` | code | home | `StrataEditor/src/Editor/CommandUtils.cpp:276-332`: `CheckUnsavedChanges` and `AfterSaves` |
| `editor-core:416` | code | home | `StrataEditor/src/Editor/EditorSceneCommands.cpp:379-406`: `scene.new`, the guard, `AfterSaves` and `MayDefer` together |
| `editor-core:418` | code | home | `StrataEditor/src/Editor/EditorContext.cpp:1045-1103`: `SubmitSceneSave` and `OnSceneSaveEnded` |
| `editor-core:420` | code | home | `StrataEditor/src/Editor/DocumentSaver.cpp:114-211`: the job; with `:218-268` (submit and coalescing) and `:293-343` (collect and publish) |
| `editor-core:423` | code | home | `StrataEditor/src/Editor/EditorContext.cpp:688-717`: `ResetScene`, everything a scene replacement does, in order |
| `editor-core:476` | figure | home | The background save timeline |
| `editor-core:478` | figure | home | The decision tree of the data-loss guard |
| `editor-core:517` | figure | home | The saving pill and the saving dialog while a large scene saves |
| `editor-core:561` | rule | home | Never serialize a document on the main thread for a save |
| `editor-core:563` | rule | home | Take the save point after `BreakMerge` |
| `editor-core:565` | rule | home | Commands that replace the scene, close the project or quit: `CheckUnsavedChanges`, `AfterSaves`, `MayDefer` |
| `editor-core:633` | hands-on | home | Exercise: trace a held background save |
| `editor-core:635` | hands-on | home | Exercise: break the guard and find the failing test |
| `editor-core:701` | term | home | Snapshot (of a save) |
| `editor-core:703-708` | term | home | Document claim, publish, coalescing, unwritten settings, discard scope, `force` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The undo stack, save points and `BreakMerge` | `editor/undo` | must |
| Deferred commands and `MayDefer` | `editor/deferred-commands` | must |
| Atomic writes and files you can trust | `core/files` | must |
| Jobs and returning results to the main thread | `core/jobs` | must |
| Atomics with acquire and release | `basics/threads` | must |
| Streamed scene documents (`SceneDocumentWriter`) | `world/serialization` | must |
| References an asset records | `assets/references` | helps |
| `Scene::Copy` with `SerializedOnly`, the snapshot a save writes | `world/systems` | helps |
| Releasing a scene in the background | `world/sub-scenes` | helps |
| The project file and its settings sections | `world/projects-settings` | must |
| A function that takes and returns a function | `basics/cpp-generic` | must |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `coalescing` | Coalescing | - |
| `discard-scope` | Discard scope | - |
| `document-claim` | Document claim | - |
| `publish-editor` | Publish (editor) | - |
| `snapshot-save` | Snapshot (save) | - |
| `unwritten-settings` | Unwritten settings | - |
