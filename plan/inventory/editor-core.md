# Inventory: the editor as a program (StrataEditorCore)

Area key: `editor-core`. Surveyed at `main` 822a7a46 (2026-11-10). Scope: `StrataEditor/src/Editor/` and
`StrataEditor/src/Editor/Commands/` (the editor without UI), with the engine pieces it leans on where the code
cannot be understood without them (`Strata/src/Strata/Scene/PrefabInstances.h`, `PrefabOverrides.h`,
`Components.h`'s `PrefabInstanceComponent`) and the one UI file that sets the frame order (`StrataEditor/src/EditorLayer.cpp`).
Out of scope here (other readers): Editor UI rules, Inspectors, Shortcuts and editor status, Viewport panel, the ImGui
panels themselves, automation transport (RPC/MCP), script builds in depth, worlds in depth, export in depth.

Document abbreviations used below:

- **DG** = `Docs/DeveloperGuide.md`, **AR** = `Docs/Architecture.md`, **AG** = `AGENTS.md` (its "## Editor" digest
  starts at line 336), **MP** = `Docs/Manual/Prefabs.md`, **MG** = `Docs/Manual/GameView.md`,
  **RN x.y** = `Docs/Releases/x.y.md`, **RM** = `Docs/Roadmap.md`.
- DG heading lines: Editor 2730, Changes go through commands 2833, Asset files are never lost 2840, Prefab instances
  2854, Command conventions 2881, No silent data loss 2911, Autosave and recovery 2948, Undo 2972, Exporting games 3009,
  Play mode and scene switches 3091, Opening scenes 3116, Scripts through commands 3135, Deferred commands and command
  scripts 3176, Hierarchy, Content Browser and thumbnails 3260, Asset streaming commands 3372, Edits while playing and
  value ranges 3451, Viewport state 3464, Templates and recent projects 3483, Launcher 3508, Placing content 3525, View
  commands 3610, Materials 3692, Animation commands 3703, Stepping a paused game 3723, Simulated input 3742, Game UI
  commands 3809, Output paths 3847. Related: Project settings 1146, Preferences 1581, Interpolation 2468, Fixed rate 1384.
- AR "## Editor" runs 3217-4071 as one section of bold-titled bullets; their lines: layer diagram 3219-3237, UI 3239,
  EditorContext 3342, Commands 3361, Command line 3388, Notifications 3397, Import failures 3427, Activity journal 3437,
  Replays 3452, Runner 3478, Command scripts 3486, Opening scenes 3494, The project file's writes 3514, Background saves
  3524, Undo 3557, Autosave and recovery 3582, Hierarchy model 3645, Asset files 3659, Content Browser 3676, Thumbnails
  3712, Asset documents 3744, Prefab instances 3753, Authoring panels 3816, Automation 3891, Viewport 3913, Project
  pictures 3965, Placement 3974, Script builds 3999. Related: "Scene runtime lifecycle" AR 959.
- Releases: 0.3.0 = waves 1-3 (completed 2026-10-12), 0.4.0 = wave 4 (2026-10-19), 0.5.0 = wave 5, 0.6.0 = wave 6
  (2026-10-23), 0.7.0 = wave 7 (2026-10-28). Wave 8 is in progress and unreleased (would be 0.8.0; RM "Wave 8" 1536).

---

## 1. Features

### 1.1 The editor's architecture: core without UI, one API

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Core/UI split | `StrataEditorCore` (`src/Editor/`) is the editor with no UI; `StrataEditorUI` (`src/UI`, `src/Panels`, `EditorLayer`) draws it and reaches the app only through `EditorHost`. Tests link both. | `StrataEditor/src/Editor/*`, `StrataEditor/src/EditorLayer.h` | DG Editor 2730; AR 3219-3237 (layer table), 3239 | 0.3.0 |
| `EditorContext` | All editor state: project, `EditorAssetManager`, edited scene, running copy, play state, selection, inspection target, undo stack, prefab sync, recovery journal, document saver, viewport, simulated input, game shell, journal, notifications, thumbnails, script engine/builder, export. Main thread only. | `Editor/EditorContext.h` (class at 169-1030), `EditorContext.cpp` (2945 lines) | AR 3342 | 0.3.0 |
| `EditorContextSpecification` | Construction switches that make tests deterministic: file watching, hot reload, toolchain, recent-projects file, preferences file, samples dir, `TimeDilation`, `Interpolation`, `ImportInBackground`, settings registry. | `EditorContext.h` 91-131 | DG 3091 (time dilation), 2881 (background scan) | — |
| Per-frame update | `EditorContext::Update`: script hot reload/builds, asset manager update, document saver/settings writers publish, migration and scan completion, scene load swap, export, runtime update and game requests or prefab sync + world streaming + editor update, animation preview, input sequence, simulated input, picking, thumbnails, project picture, scene-move following, recovery journal. | `EditorContext.cpp` 2712-2808 | AR 3342 (pieces scattered) | — |
| Frame order | `EditorLayer::OnUpdate`: record last frame time → `EditorContext::Update` → `EditorCommandRunner::Update` (polls) → automation (new requests) → command script → panels draw/render. So every command poll runs before the views render in its frame. | `StrataEditor/src/EditorLayer.cpp` 614-668 | DG 3610 (View commands: "Every command poll runs before the views render") | — |
| Selection | Ordered vector + hash set (`IsSelected` O(1)), version counter, prune of deleted entities. | `EditorContext.h` 421-438, `.cpp` 1769-1845 | AR 3557 ("The selection keeps its order…") | 0.3.0 |
| Inspection target | Inspectors show selected entities or one asset (`SetInspectedAsset`), `GetInspectionVersion`. | `EditorContext.h` 440-454, `.cpp` 1847-1873 | AR 3342 | — |
| Notifications | Toast model: level, title, message, journal entry, asset, group merging, max 4 active, lifetimes; feeds from command outcomes, builds, crashes, exports, import failures, discarded changes, agent deletes. | `Editor/EditorNotifications.h`, `.cpp`; `EditorContext::NotifyDiscardedChanges` 2150, `NotifyAssetsTrashed` 2188 | AR 3397 | — |
| Status providers | Extra `editor.status` sections registered by owners (e.g. automation). | `EditorContext.h` 668-679 | — | — |
| Command line | `--commands`, `--frames`, `--screenshot`, `--no-gpu`, `--quit-after-commands`, `--ui-scale`, `--layout`, `--no-automation`, `--automation-port`, `--idle-timeout`; table `c_Arguments` in `EditorApplication.cpp`, exit code 3 on bad args. | `StrataEditor/src/EditorApplication.cpp` (not read in full) | DG 3176 (second bullet); AR 3388 | — |

### 1.2 Commands

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `EditorCommand` | Name `<group>.<action>`, one-line description for agents, JSON Schema, handler, `Kind` (Edit/Query/Session), `Results` (Content/Session), `WaitsForAssets`, `MayDefer`. | `Editor/EditorCommands.h` 84-113 | DG Command conventions 2881; AR 3361 | 0.3.0 (kinds, flags later) |
| `EditorCommandResult` | Value or error with `EditorCommandError` kind (UnknownCommand, InvalidParameters, Failed, Cancelled, Internal), `Pending` poll, `ErrorData`, `JournalId`, `RunningCopy`, `Announced`. | `EditorCommands.h` 26-80 | DG 2881 | — |
| `EditorCommandRegistry::Execute` | Journal begin, asset-scan deferral (registry's own), run, Debug assert that only `MayDefer` commands defer, undo attribution, journal complete/suspend. | `EditorCommands.cpp` 105-151 | DG 2881 (second bullet), 3176 | — |
| Schema check before handler | Unknown parameter, missing required parameter → `InvalidParameters`; exceptions from third-party code → `Internal`. | `EditorCommands.cpp` 174-221 | DG 2881 | — |
| `CommandArguments` | Exception-free parameter reader recording the first problem (`GetString`, `GetBool`, `GetInt` with range, `GetUUID`, `GetEntity`, `FindEntity`, `GetEntities`). | `EditorCommands.h` 156-188, `.cpp` 227-421 | DG 2881 | — |
| `CommandUtils` | Schema helpers, `FindAsset`/`ResolveAsset`, `DescribeEntity`, `ApplyComponents` (validated like the inspector, range checks), `InstantiateTemplate`, `FrameTimeRecorder`, `CheckUnsavedChanges`, `AfterSaves`, `FinishEdit`, `RollBackEdit`, `GetRunningCopyWarning`, `ResolveOutputPath`, `MakeUniqueAssetPath`, many `Describe*`. | `Editor/CommandUtils.h` 41-224, `CommandUtils.cpp` | DG 2881, 3451, 3847 | — |
| Command kinds as a tested decision | Every built-in command is listed in exactly one of three lists (63 Edit, 46 Query, 42 Session at this commit), plus lists for `Results::Session` (20), `MayDefer` (44), `WaitsForAssets` (10). | `StrataTests/src/Editor/CommandJournalTests.cpp` 98-205, test at 211-240 | DG 2881; AR 3361 | — |
| Commands wait for the asset scan | While a project's assets scan in the background, Edit commands and `WaitsForAssets` commands are deferred by the registry; `DescribeAssetScanWait` gives the UI's refusal reason. | `EditorCommands.cpp` 119-132, 153-172; `EditorContext::IsWaitingForAssets` (`.cpp` 579) | DG 2881 (second bullet) | 0.4.0 (RN 0.4.0 "Projects of tens of thousands of assets open while their assets are scanned") |
| `editor.commands` | Lists every command with description, schema, kind. | `EditorCommands.cpp` 66-79 | AR 3361 | 0.3.0 |
| UI-only commands | `editor.showPanel`, `editor.showDialog` registered by the UI. | `StrataEditor/src/EditorLayer.cpp` 177, 233 | AR 3361 | — |
| Value ranges | Out-of-range property values are `InvalidParameters`, nothing changed (`PropertyInfo::IsInRange`). | `CommandUtils::ApplyComponents` (`CommandUtils.cpp` 510+) | DG 3451 | — |
| Output paths | Files written for clients: relative to project dir, no UNC/device paths, no reserved names (CON, COM1...), extension must match, overwrite only with `overwrite: true`. | `CommandUtils.cpp` 457-508 | DG 3847; AG "Files commands write…" | — |

#### 1.2.1 Every command group and what it is for (153 commands: 151 core + 2 UI)

Registered by `EditorCommandRegistry::EditorCommandRegistry()` (`EditorCommands.cpp` 41-80), declarations in
`EditorCommands.h` 195-217. Kind per command: the lists in `CommandJournalTests.cpp` 101-165.

| Group | Commands | Purpose | File |
| --- | --- | --- | --- |
| `scene.*` | info, hierarchy, new, open, loadStatus, loadAdditive, unloadAdditive, save, saveAs, setSettings, raycast, recoveryStatus, recover | Edited scene lifecycle, its settings, background loads, additive sub-scenes in play, recovery | `EditorSceneCommands.cpp` (322-569), `Commands/PlacementCommands.cpp` 392, `EditorStateCommands.cpp` 559-589 |
| `entity.*` | create, delete, duplicate, copy, paste, get, find, setParent, rename, setActive, dropToGround | Scene edits on entities (multi-entity, one undo step each) | `Commands/EntityCommands.cpp` 170-554 |
| `component.*` | list, add, remove, get, set | Reflection-driven component edits | `Commands/EntityCommands.cpp` 613-721 |
| `prefab.*` | create, instantiate, status, apply, revert, unpack, select | Prefabs and linked instances | `EditorAssetCommands.cpp` 1182 (create), `EditorPrefabCommands.cpp` 341-676 |
| `asset.*` | list, info, import, reimport, setImportSettings, move, findReferences, delete, createFolder, moveFolder, deleteFolder, place, stats, setBudget | Project files with undo and trash; placement; streaming stats | `EditorAssetCommands.cpp` 637-1053, `PlacementCommands.cpp` 463, `EditorStreamingCommands.cpp` |
| `material.*` | get, create, set | Asset-document edits with undo (`AssetEdit`) | `EditorAssetCommands.cpp` 1089-1147 |
| `project.*` | info, templates, create, open, close, samples, openSample, setStartScene, export, exportStatus, cancelExport, setExportSettings, settings, setSettings, save, setGameInfo, setCollisionLayers | Project lifecycle, settings as undo steps, export | `EditorAssetCommands.cpp` 246-567, `EditorProjectSettingsCommands.cpp` |
| `edit.*` | undo, redo, history | The undo history | `EditorStateCommands.cpp` 364-387 |
| `editor.*` | commands, status, activity, activity.export, recentProjects, removeRecentProject, quit, wait, perf, batch (+ UI: showPanel, showDialog) | The editor's own session, journal, replay, waiting, profiling, batches | `EditorStateCommands.cpp` 397-912, `Commands/BatchCommands.cpp` 34 |
| `selection.*` | get, set | Selection (Session) | `EditorStateCommands.cpp` 304-318 |
| `log.read` | — | Read the log since a sequence | `EditorStateCommands.cpp` 981 |
| `play.*` | start, simulate, stop, pause, step, state | Play mode | `Commands/PlayCommands.cpp` 131-258 |
| `input.*` | key, mouseButton, mouseMove, scroll, gamepadButton, gamepadAxis, action, releaseAll, state, sequence, click, type | Simulated input timed in fixed steps | `EditorInputCommands.cpp` |
| `camera.*` | get, set, focus | Editor camera (no undo) | `EditorViewportCommands.cpp` 1000-1073 |
| `viewport.*` | getSettings, setSettings, capture | View settings and captures | `EditorViewportCommands.cpp` 1093-1211 |
| `script.*` | status, build, reload, load, init, create, list, open, setExternalEditor, add, remove, setField, get | Game scripts through commands (other area) | `EditorScriptCommands.cpp` |
| `animation.*` | createController, setController, info, preview | Animation assets and edit-time previews (other area) | `EditorAnimationCommands.cpp` |
| `world.*`, `physics.*` | world.cook, create, info, status, edit, loadCells, moveEntities, setLayers; physics.stats, setDetailedStats | Worlds and physics diagnostics (other area) | `EditorWorldCommands.cpp` |
| `lighting.*` | applySkyPreset, bakeProbes, extractSun | Lighting tools (other area) | `EditorLightingCommands.cpp` |
| `ui.*` | create, layout, hitTest | Game UI authoring (other area) | `EditorUICommands.cpp` |
| `audio.state` | — | Audio diagnostics | `Commands/AudioCommands.cpp` |
| `preferences.*` | get, set, save | Person's preferences (Session) | `EditorPreferencesCommands.cpp` |
| `inputActions.*` | setAction, setMap, resetPlayerBindings | Project input actions | `EditorInputActionsCommands.cpp` |
| `graphics.resetPlayerOptions` | — | Players' graphics options in play | `EditorGraphicsCommands.cpp` |

### 1.3 Undo and redo

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `EditorAction` | Virtual undo step: `Execute`, `Undo` (either may fail with a reason, changing nothing), `MergeWith`, `IsNoOp`, `ChangesScene`, `GetSceneChange` (None/Entities/Settings/Other), `GetEntityStates`. | `Editor/UndoStack.h` 17-56 | AR 3557; DG Undo 2972 | 0.3.0 |
| `UndoStack` | Linear history, capacity 512, merge (until `BreakMerge`), no-op drop, save point, serials (`FindSerial`, `GoTo`), record count vs step count, version, observers, groups. | `UndoStack.h` 98-227, `UndoStack.cpp` 1-325 | AR 3557; DG 2972 | 0.3.0 |
| Failure semantics | Undo that fails keeps the step applied (retry later); redo that fails drops it and everything after. | `UndoStack.cpp` 156-221 | DG Asset files 2840; AR 3659 (end) | — |
| Save point / modified flag | `IsModified` walks only actions between save point and position that `ChangesScene()`; trims and discarded redo make the save point unreachable (`c_NoSavePoint`). | `UndoStack.cpp` 48-106, 271-311 | AR 3557 | 0.3.0 |
| `SavePoint` for background saves | `{Position, Serial, Generation, SceneTrims}`; `MarkSaved(point)` marks the step with that serial, wherever the history has moved; another generation (history cleared) marks nothing. | `UndoStack.h` 173-192, `.cpp` 278-296 | DG Undo 2972 (second bullet) | 0.4.0 (background saves) |
| `EditorActionGroup` | Several actions as one step, all-or-nothing in both directions; scene change described by its single scene-changing member. | `UndoStack.h` 70-96, `.cpp` 331-420 | AR 3557; DG Prefab instances 2854 | — |
| Groups for batches | `BeginGroup`/`EndGroup`/`CancelGroup`: collected actions are applied as they come, observers hear each, undo/redo refused while open. | `UndoStack.h` 155-167, `.cpp` 108-154 | DG Undo 2972 (third bullet) | 0.4.0 |
| `UndoStackObserver` | Hears every applied/merged/undone step (recovery journal, world dirty cells). | `UndoStack.h` 58-68 | AR 3557 | — |
| `EntityState` | Entity's components as JSON (+ unknown components), parent, sibling index, sub-scene cell. | `Editor/SceneEdit.h` 21-37 | AR 3557 | 0.3.0 |
| `SceneEditTransaction` | Captures "before" of tracked entities (`Track`, `TrackSubtree`, `TrackCreated`), `Commit` records a `SceneEditAction` only if something changed, `Rollback`, `TakeAction` for groups. | `SceneEdit.h` 132-169, `SceneEdit.cpp` 388-463 | DG 2972; AG Editor bullet 1 | 0.3.0 |
| `SceneEditAction` | Before/after state vectors shared immutably (`Ref<const vector>`), merge by key + same entities, no-op when equal. | `SceneEdit.h` 88-114, `.cpp` 327-363 | AR 3557 | — |
| `SceneEdit::ApplyEntities` | Makes the scene match states in batches: one destroy batch, one recreation (deserialize with same UUIDs), component diffs, one `PlaceEntities` batch per changed sibling list, sub-scene membership. | `SceneEdit.cpp` 187-281 | AR 3557 | — |
| Cells in undo | Steps that touch an unloaded world cell fail, ask the world to load it (`ISceneCellLoader`), retry. | `SceneEdit.h` 39-50, 78-84; `.cpp` 283-323 | AR 3557 (implicitly); worlds chapter | — |
| Names in steps | "Create 'Wall'", "Delete 3 entities"; `QuoteName` cuts at 40 chars on UTF-8 boundaries; `MakeNameUnique` ("Crate (1)"). | `SceneEdit.h` 59-72, `.cpp` 109-167 | DG 2972; AR 3557 | — |
| `SceneSettingsAction` | Undo of `scene.setSettings`. | `SceneEdit.h` 116-130 | — | — |
| `CommitEdit` | The one gate: refused while playing (not recorded), rolled back while a scene opens, world re-celling, prefab override upkeep, then record. | `EditorContext.cpp` 1875-1891 | DG 2972, Opening scenes 3116 | — |
| `FinishEdit` / `RollBackEdit` | How a command ends: check editable, commit, add running-copy warning while playing. | `CommandUtils.cpp` 433-455 | DG Edits while playing 3451 | — |
| `PropertyEdit` | `SetPropertyWithUndo` (single and multi-entity, merge key `Property/<id>/<component>/<property>`), `GetSharedProperty`, `RotationAnglesEdit`, `GetDefaultComponentValues`. | `Editor/PropertyEdit.h`, `PropertyEdit.cpp` 98, 135-155, 267 | DG 2972 | — |
| `TransformDrag` | Gizmo drag as one undo step (merge key `TransformDrag/<random UUID>`), values from drag start so no drift. | `Editor/TransformEdit.h` 53-99, `TransformEdit.cpp` 146, 260 | AR 3816 (authoring) | — |
| `AssetDocumentAction` | Undo of asset document edits (bytes before/after), merge key `Material/<handle>/<property>`, `ChangesScene() == false`. | `Editor/AssetEdit.h` 113-144, `AssetEdit.cpp` 243-253, 392-430 | DG Materials 3692; AR 3744 | — |
| `ProjectSettingsAction` | Undo of project settings; queues a background write of the project file. | `Editor/ProjectSettingsAction.h` 19-74 | AR 3514; DG Project settings 1146 | 0.6.0 |
| `edit.undo`/`redo`/`history` | Commands; refused while playing and while a scene opens. | `EditorStateCommands.cpp` 364-396; `EditorContext::Undo/Redo` 1983-2012 | DG 2972 | 0.3.0 |

### 1.4 Saving without stalling and without losing data

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `DocumentSaver` | The one path for saving engine-native documents: main thread takes a snapshot, a background job serializes (`SceneDocumentWriter`), scans references, hashes, writes atomically under a file claim; `Update` publishes on the main thread. Queued saves of the same documents coalesce. | `Editor/DocumentSaver.h` 26-172, `DocumentSaver.cpp` 90-437 | AR Background saves 3524; DG No silent data loss 2911 (second bullet); AG "Saves never serialize on the main thread" | 0.4.0 (RN 0.4.0 "Background saves and large projects") |
| Scene save | `BeginSaveScene`/`BeginSaveSceneAs` → `SubmitSceneSave` (BreakMerge, `GetSavePoint`, `Scene::Copy` SerializedOnly, recovery `BeginSave` token) → `OnSceneSaveEnded` (MarkSaved, project picture, recovery `OnSaved`; failed save-as restores handle/name). Blocking `SaveScene` for tools/tests. | `EditorContext.cpp` 982-1103, 1286-1329 | AR 3524-3556 | 0.4.0 |
| `scene.save {wait}` | Answers when published (default) or at once with `saveId`; `editor.status` lists `saving`. | `EditorSceneCommands.cpp` 509-568 | DG 2911 | 0.4.0 |
| `SettingsFileWriter` | Project file and preferences written off the main thread, coalescing, failed write leaves state `Unwritten`. | `Editor/SettingsFileWriter.h` 13-81 | AR 3514; DG Project settings 1146 | 0.6.0 |
| Unsaved-changes guard | `CheckUnsavedChanges(context, force, action, DiscardScope)`: refuses while the scene is modified (also while its copy plays), and for Project/Editor scope while project file/preferences are unwritten, unless `force`. | `CommandUtils.h` 161-178, `.cpp` 276-317 | DG No silent data loss 2911; AG Editor bullet 4 | 0.3.0 (guard), 0.6.0 (settings/preferences scopes) |
| `AfterSaves` | Wrapper that defers a handler while saves are in flight, then runs it (so `force` never discards a save). | `CommandUtils.cpp` 319-332 | DG 2911; AG Editor bullet 5 | 0.4.0 |
| `ResetScene` | Every scene replacement: stop play, follow moves, recovery `EndScene` (write unsaved changes as discarded), notify who discarded, store camera, clear history, attach world, release previous scene in background, start new journal. | `EditorContext.cpp` 688-717 | AR 3582; DG 2948 | — |
| `ReleaseProject` | Finishes saves and project-file write, cancels export/loads/migration, saves viewport state, resets scene (journal written), closes scripts, thumbnails, asset manager. | `EditorContext.cpp` 608-682 | DG 2911 (end) | — |
| UI questions | `EditorShell::RequestDiscardChanges`, `RequestReleaseProject`, `RequestQuit` ask the person and pass `force` only for what was asked (UI files, other area). | `StrataEditor/src/UI/*` (not read) | DG 2911 | — |
| Asset documents saved in the frame | `AssetEdit::ApplyDocument` writes on the main thread (`EditorAssetManager::SaveNativeAsset`). | `Editor/AssetEdit.h` 37-60 | RN 0.7.0 Editor limitations ("Prefabs and the Asset tab's editors still save in the frame") | known limitation |

### 1.5 Autosave and crash recovery

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `SceneRecovery` journal | Observes the undo stack; keeps the entity states of steps since the last save; writes `<project>/.strata/Recovery/<scene>-<session>.strecovery` 2 s after edits stop and at least every 10 s; text built on a background worker, file written on an I/O job, operations serialized. | `Editor/SceneRecovery.h` 109-371, `SceneRecovery.cpp` (1133 lines; `OnApplied` 629, `Update` 671, `Write` 697) | AR 3582-3644; DG 2948 | 0.3.0 |
| Base hash | SHA-256 of the saved scene file the changes apply to, hashed a megabyte at a time on an I/O job. | `SceneRecovery.cpp` ~30-54; `RecoveryData::BaseHash` (`.h` 53) | AR 3582 | — |
| Folding | Steps that create/remove/move no entity fold into the previous segment (`IsStructural`). | `SceneRecovery.cpp` 61-77, 754-767 | AR 3582 | — |
| Complete journals | Never-saved scenes snapshot all entities (only up to `c_MaxSnapshotEntities` = 256); steps of kind Other force a snapshot. | `SceneRecovery.h` 121-125, 145 | AR 3582 | — |
| Discards are kept | Forced discards and Don't Save write the journal marked `Discarded` and re-scan; newest 8 discards offered (`c_MaxOfferedDiscards`), older moved to `Recovery/Discarded` (20 kept). | `SceneRecovery.h` 126-130, 146-149; `EndScene` `.cpp` 403 | AR 3582 | 0.3.0 (journal), later (discard limits; release not stated) |
| Saves during journaling | `RecoverySaveToken`: edits during a background save are carried into the journal of the saved document. | `SceneRecovery.h` 101-107, 181-195 | AR 3524 | 0.4.0 |
| Ownership | Files of a still-running editor process (pid + start time) are left out of offers. | `SceneRecovery.h` 132-135 | AR 3582 | — |
| Follow moves | Journal and entries follow a renamed/moved scene by handle (`FollowSceneMoves`, `SetSceneLocator`). | `EditorContext.cpp` 2810; `SceneRecovery.h` 154-157, 196-198 | DG 2948 | — |
| `scene.recoveryStatus`, `scene.recover {scene, action: apply/discard, force}` | Apply opens the scene in background then applies one undo step (`SceneRecoveryAction`) back to the saved state. | `EditorStateCommands.cpp` 559-732; `EditorContext::BeginRecovery` 2018, `ApplyRecovery` 2058; `SceneRecovery.h` 81-99 | DG 2948; AR 3582 | 0.3.0 |
| Recover dialog | `UI/RecoveryDialog` (UI, other area), opens itself for crash leftovers; toasts for discards. | — | AR 3582 | — |

### 1.6 Asset file actions and the trash

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `AssetFileAction` family | Undo steps for project files that never change the scene and hold the asset manager weakly: `AssetTrashAction`, `AssetMoveAction`, `AssetCreateAction`, `AssetFolderCreateAction`. | `Editor/AssetFileAction.h` 17-100, `AssetFileAction.cpp` | AR 3659; DG 2840 | 0.3.0 |
| Delete to trash | `asset.delete`/`deleteFolder` move files + `.meta` + cached import to `<project>/.strata/Trash` (30 days); undo restores the handle. | `EditorAssetCommands.cpp` 899-939, 988; `EditorAssetManager::MoveToTrash` (engine) | DG 2840 | 0.3.0 |
| Reference check | `AssetReferences::Find`: index of recorded referencers + walk of the edited scene in memory + the project's own references (start/loading scene, icon, settings); failure lists `referencedBy` in `ErrorData`. | `Editor/AssetReferences.h` 19-77 | AR 3659; DG 2840 | 0.3.0 (project refs: 0.6.0, RN 0.6.0 171-175) |
| Precondition checks | Undo of a delete fails if something else is at the path; redo only if the path still holds exactly those assets and the delete would be allowed now. | `AssetFileAction.cpp` 62-107 | AR 3659 | — |
| Agent deletes are announced | `NotifyAssetsTrashed` for agents/scripts, not for the person's own deletes. | `EditorContext.cpp` 2188 | AR 3397 | — |
| Files a save writes are locked | `MoveAsset`, `MoveFolder`, `MoveToTrash` refuse claimed/reserved paths. | engine `EditorAssetManager` (`FindDocumentWriteLocked`) | AR 3524 | 0.4.0 |
| Panels never touch files | A source scan test fails panels that write/move/remove files. | `StrataTests/src/Editor/EditorUISourceTests.cpp` 631 | DG 2833; AR 3659 | — |

### 1.7 Prefabs

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Instance link | `PrefabInstanceComponent {Prefab, PrefabEntityID, PrefabVersion, SyncedHash, Overrides}`; instance root = linked entity whose parent is not linked to the same prefab. | `Strata/src/Strata/Scene/Components.h` 104-118; `Scene/PrefabInstances.h` 29-97 | AR 3753; MP 1-7 | 0.3.0 (link), 0.4.0 (overrides) |
| Root's own transform and name | Never an override, kept by `Replace`, replaced in `MakeTemplate`. | `PrefabInstances.h` 34-35 | MP 31; AR 3753 | — |
| `prefab.create` | Captures entities into a `.stprefab`, links them (unless `link: false`), one step = `AssetCreateAction` + scene change in a group. | `EditorAssetCommands.cpp` 1182 | DG 2854; AR 3753 | 0.3.0 |
| `prefab.instantiate` | One or many (`instances: [...]`, checked up front, one undo step), names made unique, `MarkSynced`. | `EditorPrefabCommands.cpp` 341; `CommandUtils::InstantiateTemplate` | DG 2854 | 0.3.0; many: 0.4.0 |
| `prefab.status` | Changed/added/removed entities, overrides, modified, outdated. | `EditorPrefabCommands.cpp` 395-435 | DG 2854 | — |
| `prefab.apply` | Writes the instance (or one override) into the prefab, links added entities, propagates to other instances except their overrides; one step (`PrefabApplyAction` wrapping a group of `AssetDocumentAction` + scene action); refused for models, while playing, for outdated instances unless `force`. | `EditorPrefabCommands.cpp` 39-72, 436-583 | DG 2854; AR 3753; MP 47-57 | 0.3.0; per-override 0.4.0 |
| `prefab.revert`, `prefab.unpack`, `prefab.select` | Revert whole/component/property (UUIDs kept); unpack removes links; select. | `EditorPrefabCommands.cpp` 585-703 | MP 59-63 | 0.3.0 |
| Overrides | `PrefabOverride {Entity, Component, Property, Kind}`; `ComputeOverrides`, incremental `UpdateOverrides`, `Propagate`, `Revert`, `ApplyToPart`. | `Strata/src/Strata/Scene/PrefabOverrides.h` 22-125 | AR 3753 (Overrides part) | 0.4.0 |
| Override upkeep on every edit | `EditorContext::UpdatePrefabOverrides` inside `CommitEdit`: touched instance roots tracked (so drags merge), incremental unless reshaped; `OverrideUpkeep::Current` for edits that already updated lists. | `EditorContext.cpp` 1893-1981 | DG 2854 | 0.4.0 |
| `PrefabSync` | Per-frame (edit mode, not while opening): baseline snapshot per used prefab, watches source revisions, propagates file changes to instances in one undo step; editor writes set the baseline first; marks cached, settle over runs of edits (`c_SettleFrames` = 12). | `Editor/PrefabSync.h` 35-143, `PrefabSync.cpp` 87-458 | AR 3753; DG 2854 | 0.3.0 (sync), 0.4.0 (overrides) |
| Catch-up when a scene opens | `OnSceneOpened` → `CatchUp`: instances whose recorded `PrefabVersion` differs and whose `SyncedHash` still matches take the new values; modified ones become *outdated*; model import-scale special case. | `PrefabSync.cpp` 205-241, 336-383 | AR 3753; MP 47-57 | — |
| Perf instrumentation | `GetOverrideUpkeepStats`, perf tests `Perf.Editor.DragInPrefabInstance5kMedian` etc. | `EditorContext.h` 494-501 | DG 2854 | — |
| No prefab edit mode | Not implemented (change via instance + apply). | — | RN 0.7.0 Editor limitations; RN 0.7.0 "later" list | missing |

### 1.8 Placing content

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `SceneRaycast::Cast` | Ray vs mesh renderers through the render scene's spatial index, then loaded triangles (or bounds while loading); ignores entities being placed. | `Editor/SceneRaycast.h` 17-41 | AR Placement 3974; DG Placing content 3525 | 0.3.0 era (file 2026-10-11) |
| `EditorPlacement::Place` | Point → surface hit → grid plane y=0 within 500 m → in front (fallback distance); snap across the normal's dominant axis, re-cast down on upward ground; `RestOn` box support. | `Editor/EditorPlacement.h` 24-120, `EditorPlacement.cpp` 125-213 | DG 3525; AR 3974 | wave 8 (unreleased; RM "Lane Editor" ~1564) for `Place`/ray requests; pivot placement earlier |
| `FindPivotSurface` | Surface under the camera's target (down ray), else view-center ray, else target: where create menus put new entities. | `EditorPlacement.h` 99-105 | DG 3525 | — |
| `MakeRayRequest` / `MakeViewRay` | One request for the drop and `asset.place`, bit-identical floats; camera-relative ray. | `EditorPlacement.h` 82-94 | DG 3525 | wave 8 |
| `PlacementPreview` | Ghost of a dragged asset (box, ring, label), writes nothing, recasts only when its key changes. | `Editor/PlacementPreview.h` 23-136 | DG 3525 ("The drop and its ghost") | wave 8 |
| `AssetBounds` | What a prefab/model/mesh draws around its origin, cached per content stamp, pending results kept without re-measuring every frame. | `Editor/AssetBounds.h` 16-63 | DG 3525, 3610 | — |
| `scene.raycast`, `asset.place` | Commands; `asset.place` is the model Edit command that waits (clock, never frames). | `Commands/PlacementCommands.cpp` 392-600 | DG View commands 3610; DG 3176 | wave 8 |
| `entity.dropToGround` | Moves entities down onto what is below (five rays from the bounds' bottom), one step. | `Commands/EntityCommands.cpp` 554 | DG 3525; AR 3974 | — |
| `SceneBounds` | Bounds of what renders for framing and placement (skinned in pose, placeholders). | `Editor/SceneBounds.h` | DG 3610 (World queries) | — |

### 1.9 Opening scenes and projects

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `BeginOpenScene` | Reads the scene again through `SceneLoader` in the background; edited scene read-only meanwhile; `Update` swaps between frames (`FinishOpenScene`); cancellable. | `EditorContext.h` 242-265; `.cpp` 770-962 | DG Opening scenes 3116; AR 3494 | 0.4.0 (RN 0.4.0 "loads can be cancelled") |
| `CheckSceneEditable` | The read-only guard for code that edits outside `CommitEdit`. | `EditorContext.cpp` 869 | AG Editor bullet 7; AR 3494 | — |
| `scene.open` | `AfterSaves` + guard + deferred answer one frame after the swap (with `frameTimes`). | `EditorSceneCommands.cpp` 101, 408-427 | DG 3116 | — |
| `scene.loadStatus` | Progress of open / play switch / sub-scenes / world streaming. | `EditorSceneCommands.cpp` 249-273, 429 | DG 3116 | — |
| `BeginOpenProject` | Project open at once, start scene opens in background after the asset scan and migration. | `EditorContext.cpp` 351-487 | AR 3494 (end) | 0.4.0 |
| Templates and samples | `empty`, `basic3d`; `project.openSample` copies a sample without `.strata`. | `Editor/ProjectTemplates.h`, `ProjectSamples.h` | DG 3483; AR 3342 | 0.4.0 (launcher templates, RN 0.4.0 101), samples with pictures 0.5.0 |
| Recent projects | User-shared JSON list, max 12, scripted runs read-only. | `Editor/RecentProjects.h` | DG 3483 | — |

### 1.10 Play mode, the Game view, stepping, edits while playing

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `SceneState` | Edit, Play, Simulate (physics only). | `EditorContext.h` 75-82 | MG 1-5 | 0.3.0 |
| `Play`/`StartRuntime`/`Stop` | Copy of the edited scene (`Scene::Copy`), world pins, session counter, reset simulated input and game shell, load players' bindings/graphics, time dilation and interpolation from the specification, `OnRuntimeStart`; Stop releases the copy in the background and restores master volume. | `EditorContext.cpp` 1331-1433 | AR 3342 (`GetActiveScene`); DG Play mode 3091 | 0.3.0 |
| `GetActiveScene` | Running copy while playing, else edited scene: commands work on it. | `EditorContext.h` 312-313 | AR 3342 | — |
| Edits while playing | Scene edits change the running copy, are not recorded, results carry a `warning` and `RunningCopy`; settings changes stay. | `EditorContext::CommitEdit` 1877; `CommandUtils::FinishEdit` 433-449 | DG 3451; AR 3557 | — |
| Runtime requests | Quit (`Scene::RequestQuit`) stops play; scene switch (`RequestSceneLoad`) loads in background, swaps once ready, journal event `play.sceneSwitched`. | `EditorContext.cpp` 1435-1553 | DG 3091 | 0.4.0-ish (RN not checked) |
| Time dilation | Running game slows down instead of spiraling into catch-up steps; off in tests/scripted runs. | `EditorContextSpecification::TimeDilation` (`.h` 116-119) | DG 3091 | not stated |
| Pause / step | `SetPaused`, `Step(n)` (one fixed step per frame), resume drops pending steps, counters (`GetResumeCount`, `GetFixedStepCountAtResume`, `GetFixedStepCountAtStop`), input suspension while paused without steps. | `EditorContext.cpp` 1560-1624; `.h` 332-372 | DG Stepping 3723 | 0.4.0 (RN 0.4.0 "Exact play-testing") |
| `play.start {build, paused}` | Builds scripts first when needed (defers), can start paused at step 0. | `Commands/PlayCommands.cpp` 20-157 | DG 3723 | — |
| `play.step {steps, wait}` | Deferred; answers when its last step ran; stacked calls; fails with `stepsRun` on resume/stop. | `PlayCommands.cpp` 191-256 | DG 3723 | 0.4.0 |
| Stepping lifts frame cap | `EditorLayer::UpdateSteppingFrameRate`. | `EditorLayer.cpp` 650 | DG 3723 | — |
| Simulated input | Holds per command, durations in fixed steps (`SimulatedInput`), `input.sequence` (`InputSequence`). | `Editor/SimulatedInput.h`, `InputSequence.h`, `EditorInputCommands.cpp` | DG Simulated input 3742 | 0.4.0 |
| Game shell | `EditorGameWindow` records the game's window requests instead of applying them; saves to `<project>/.strata/Saves`; players' bindings and graphics options. | `Editor/EditorGameWindow.h` 15-57; `EditorContext.h` 384-419 | MG 28-40 | — |
| Game input focus | `SetGameInputActive` (only in Play, Game view focused); edit shortcuts off meanwhile. | `EditorContext.h` 373-383 | MG 36-40 | — |
| Game view resolution | `GameViewMode` (Free, aspects, fixed sizes, custom, game's request), `ComputeGameViewFrame`. | `Editor/EditorViewport.h` 36-85, `EditorViewport.cpp` 248 | MG 28-34; AR 3913 | 0.4.0 |
| View resolution | `ResolveViewportView` (Automatic/Editor/Scene), `ResolveSceneView` ("Game camera", F8), `ResolveGameView` (UI over black without a camera), `GetViewportRenderOptions` (preview lighting, hidden HUD in editor views). | `Editor/ViewportRenderer.cpp` 24-95 | DG Viewport state 3464; AR 3913 | — |

### 1.11 Deferred commands, the runner, scripts, batches, the journal, replays

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `Defer(poll)` | A command that waits returns a poll function polled once per frame from the next frame; it must own its data and allocate nothing per frame. | `EditorCommands.h` 26-28, 50-53, 78-79 | DG 3176; AG Editor "Commands never block a frame" | 0.3.0 |
| `EditorCommandRunner` | Runs commands, keeps pending ones in issue order, polls in `Update`, completions, `CancelAll`, notifications for UI origin. | `Editor/EditorCommandRunner.h` 24-72, `.cpp` 274-369 | AR Runner 3478 | 0.3.0 |
| `FrameTimeRecorder` | Reserved storage for frame times so polls don't allocate. | `CommandUtils.h` 118-145 | DG 3176 | — |
| `editor.wait {frames}`, `editor.perf` | Frame waits with CPU frame-time stats; profiler statistics. | `EditorStateCommands.cpp` 883-980 | DG 3176 | — |
| `EditorCommandScript` | `--commands` file: steps with `expect` (JSON pointers, equals/min/max), `bind`/`{"$ref"}`, `until {steps, seconds}`; references checked before anything runs; failed step marks script failed, exit code 1. | `EditorCommandRunner.h` 74-205, `EditorCommandRunner.cpp` | DG 3176 (second bullet); AR 3486 | 0.3.0; `until` 0.5.0 (RN 0.5.0 69) |
| `editor.batch {steps, atomic}` | Steps run in one frame through `RunStepNow`; `MayDefer`, unknown, nested and `until` steps refused up front; ≤1000 steps; one undo step via group; atomic failure cancels the group. | `Commands/BatchCommands.cpp` 12-119 | DG Undo 2972 (third bullet); AR 3361 | 0.4.0 |
| `CommandJournal` | Activity journal of every command: origin (UI, Automation+client, CommandScript, Internal), parameters (≤256 KB), playing flag, result summary with IDs, error, duration, undo step; ring of 2,000 entries / 8 MB. | `Editor/CommandJournal.h` 24-241, `CommandJournal.cpp` | AR Activity journal 3437 | 0.3.0 |
| `editor.activity`, `editor.activity.export` | Query the journal; export a replay script (`BuildReplayScript`): Edit commands not on the running copy, IDs bound and referenced, lookups included; counts `editsOutsideCommands`, `unrepeatableEdits`. | `EditorStateCommands.cpp` 397-558; `CommandJournal.h` 224 | AR Replays 3452; DG 3176 | 0.3.0 |
| Replay end-to-end test | `StrataEditor.Replay` (`StrataTests/Editor/ReplaySession.cmake`), `Editor.Replay` in-process (51 commands). | `StrataTests/src/Editor/ReplayTests.cpp`, `SceneComparison.h` | AR 3452 | — |
| Smoke command script | Real `--commands` file used by CTest. | `StrataTests/Editor/SmokeCommands.json.in` 1-30 | DG 3176 | — |

### 1.12 The editor camera, viewport state, thumbnails, project pictures

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `EditorCamera` | Orbit camera: target (pivot), distance, yaw/pitch (degrees, pitch ±89), FOV, clip planes, fly speed; Orbit, Look, Pan (units per pixel at target depth), Dolly (0.85 per step, double precision), Move, Focus (sphere), FitBounds (corners), LookAt, reversed-Z projection, JSON. | `Editor/EditorCamera.h` 15-139, `EditorCamera.cpp` | DG Viewport state 3464; MG 7-15 | 0.3.0 |
| `EditorViewport` | Camera, per-scene cameras (`StoreSceneCamera`/`RestoreSceneCamera`), `ViewportSettings`, three renderers (Scene view, Game view, captures), async ID-buffer picking with timeout, `FrameScene`, `PlacementPreview`, save/load to `<project>/.strata/EditorViewport.json`. | `Editor/EditorViewport.h` 87-286 | DG 3464; AR 3913 | 0.3.0; per-scene cameras later |
| `ViewportSettings` | Grid, outline, gizmos, all colliders, stats, preview lighting, game UI, canvas mode, gizmo mode/space, snap steps, debug view, cell bounds, Game view mode, pilot game camera, edit pose, quality. | `EditorViewport.h` 87-148 | DG 3610 (`viewport.setSettings`) | — |
| First view framing | `FrameScene` along the primary camera with `FitBounds`, refined once loading meshes arrive unless the camera moved (`UpdatePendingFrame`). | `EditorContext.cpp` 963-981 | DG 3464 | — |
| View commands | `camera.get/set/focus`, `viewport.getSettings/setSettings/capture` (no undo). | `EditorViewportCommands.cpp` 1000-1401 | DG View commands 3610 | 0.3.0 |
| `ThumbnailCache` | Textures from the mip tail by byte range; materials/meshes/models/prefabs rendered offscreen one at a time with non-stalling readback; PNG cache keyed by content stamps; `c_Version` = 11; large previews. | `Editor/ThumbnailCache.h` 29-246, `.cpp` | AR Thumbnails 3712; DG 3260 (third bullet); AG Editor last bullet | 0.3.0 |
| `ProjectThumbnail` | Launcher picture after each save, rendered at 3× 480x270 and averaged down, waits for loads/exposure/TAA. | `Editor/ProjectThumbnail.h` 16-88 | AR 3965; DG 3508 | — |
| Hierarchy and asset views | `HierarchyView`, `AssetBrowserView`: cached rows rebuilt on version change (core models of UI lists). | `Editor/HierarchyView.h`, `AssetBrowserView.h` | DG 3260; AR 3645, 3676 | — |

### 1.13 Other headers in the folder (listed for completeness, owned by other areas)

`AudioPreview`, `CanvasEdit`, `UIRectEdit`, `GameUIPresets` (game UI); `CellBoundsOverlay`, `EditorWorld`,
`WorldCellIO`, `WorldCook` (worlds); `DesktopEntry`, `GameExport`, `GameIcon`, `PEResources` (export);
`ExternalEditor`, `ScriptBuild`, `ScriptEdit`, `ScriptProject`, `ScriptSources`, `ScriptToolchain` (scripting);
`EditorAutomation` (automation transport); `EditorFrameRate`, `EditorInterface`, `EditorPreferences` (preferences);
`ProbeBake` (lighting); `ProjectMigration` (0.5.0 project migration); `StreamingView` (debug views);
`DisplayImage` (RGBA8 textures for UI). Each is named in the command table above where it has commands.

### How completeness was checked

- Every header of `StrataEditor/src/Editor/` (70 headers, 142 files) was listed (`ls`) and accounted for in 1.1-1.13;
  the ones in scope were read (EditorCommands, CommandUtils, UndoStack, SceneEdit, EditorContext in full, DocumentSaver,
  SceneRecovery (first 250 lines), PrefabSync, AssetFileAction, EditorCommandRunner, EditorPlacement, EditorCamera,
  EditorViewport); the others by their leading comments.
- Every command name was extracted from the registrations and cross-checked against the authoritative kind lists in
  `StrataTests/src/Editor/CommandJournalTests.cpp` 101-165 (63 + 46 + 42 = 151 core commands; the test asserts the lists
  match the registry exactly), plus the 2 UI commands in `EditorLayer.cpp`.
- Every DG heading under "## Editor" (2730-3852) was read except the four reserved for another reader (Editor UI rules
  2738, Inspectors 3282, Shortcuts and editor status 3346, Viewport panel 3568); every AR "## Editor" bullet in scope
  was read (3217-3240, 3342-3646, 3659-3675, 3712-3815, 3913-3998); both manuals were read whole.
- Test suites of the area were listed with their case names (Editor.Undo, Editor.SceneEdit, Editor.Saves,
  Editor.DataSafety, Editor.Recovery, Editor.Prefab, Editor.CommandRunner, Editor.CommandScript, Editor.Replay,
  Editor.Placement, Editor.Camera, Editor.SceneLoad, Editor.GameFlow, Editor.Journal...).
- This area has no shaders. Its tools are the command scripts in `StrataTests/Editor/*.json(.in)`.

---

## 2. Concepts to teach (dependency order)

1. **What an editor is, and why it is a separate program from the game.** Problem: a game needs content
   (levels, objects, settings) made by people who are not programming. Approaches: in-engine editors that run the game
   code (Unity, Unreal, Godot), external DCC tools plus exporters, text/data files edited by hand. Strata: an in-engine
   editor that links the same engine and plays the game in place, with an exported runtime separate. Newcomers think the
   editor *is* the engine; it is a client of it.
2. **Model/view separation: an editor core without UI.** Approaches: UI code mutating state directly (simple, untestable),
   MVC/MVVM, a headless core with thin UI. Strata: `StrataEditorCore` holds all state and logic, `StrataEditorUI` only
   draws and calls commands (AG Editor bullet 1, DG 2833); this makes the editor testable headless and drivable by
   agents. Newcomers put logic in a button handler.
3. **The command pattern and a single API.** Problem: three clients (person, AI agent, test) must do the same thing in
   the same way. Approaches: in-process command objects (Qt `QUndoCommand`, Unreal transactions), scripting APIs (Unity
   Editor scripting, Blender Python), RPC. Strata: every operation is a named JSON command with a JSON Schema and a kind,
   and automation exposes the registry unchanged (AR 3361; DG 2881). Teach: schema as contract, unknown parameters
   rejected (`CheckParameters`), error kinds (request wrong vs. state wrong). Newcomers silently ignore extra parameters
   or report every failure the same way.
4. **Validate first, change nothing on failure.** Transactions and rollback; `CommandArguments` collects the first
   problem; `RollBackEdit`. Newcomers apply half a change and return an error.
5. **Stable identity.** Entities have UUIDs, assets have handles kept in `.meta` files; undo, prefabs, replays and
   recovery all rely on recreating entities with the same UUID. Newcomers use pointers or indices (which change), or
   regenerate IDs on restore and break references.
6. **Undo/redo.** Approaches: (a) command objects with inverse operations (each command writes its own undo), (b)
   memento: snapshot state before and after, (c) transaction buffers that serialize touched objects (Unreal's
   `FTransaction`, Unity's `Undo.RecordObject`), (d) persistent data structures. Strata: (b)/(c) at entity granularity:
   `SceneEditTransaction` snapshots touched entities as JSON (`EntityState`), `ApplyEntities` makes the scene match
   (SceneEdit.h 21-37, 132-169). Non-scene steps are polymorphic `EditorAction`s (files, documents, settings). Teach:
   linear history and the redo branch being discarded on a new edit, capacity, merging continuous edits by key (a drag
   is one step), dropping a merged no-op, groups (all-or-nothing), failure semantics when the world changed outside the
   history (files). Newcomers: record one step per mouse-move; forget descendants when deleting; forget sibling order;
   assume undo always succeeds.
7. **The "modified" flag as a save point in the history.** Approaches: dirty bit set on every edit (wrong after undo),
   save point index (Strata), content hash comparison. Strata: `IsModified` compares positions and counts only steps that
   `ChangesScene` (material edits save their own file). Newcomers: dirty bit that never clears on undo.
8. **Never block a frame: the frame loop and asynchronous work.** Problem: an interactive tool must keep drawing at
   ~60 fps; saving or loading a million entities takes seconds. Approaches: progress modal (blocks), worker threads with
   callbacks (races), job + main-thread publish (Strata's rule, AG Threading). Teach: snapshot on the main thread, heavy
   work on a job, publish on the main thread; polling instead of callbacks into engine state.
9. **Saving safely.** Atomic writes (write a temp file beside the target, then rename), file claims so the watcher and
   moves don't interfere, coalescing repeated saves, publishing the written document without re-reading it. Save
   points let edits continue during a save: what was snapshotted is marked saved, later edits stay unsaved (UndoStack.h
   173-192). Newcomers: save on the main thread; mark everything saved when the save finishes; write in place.
10. **No silent data loss.** Guards on every command that would discard work (`CheckUnsavedChanges`, `force`), wait for
    saves in flight (`AfterSaves`), unwritten settings/preferences scopes, UI questions that pass `force` only for what
    the person was asked. Newcomers: a "force" flag a UI sets always; asking once and acting later on a changed scene.
11. **Autosave and crash recovery.** Approaches: periodic full autosave copies (common in DCC tools and engines),
    journaling/write-ahead logs (databases), snapshot+delta. Strata: a journal of entity states since the last save
    against a base hash, folded so it grows with structural edits only, written on a quiet timer, plus "discard is never
    loss" (DG 2948; AR 3582). Teach the observer pattern (journal follows the undo stack without copying the scene).
    Newcomers: autosave over the user's file; journals that grow unbounded; offering recovery that no longer applies.
12. **Files are part of the history too.** Trash instead of delete, references checked first (including unsaved uses in
    memory), handles preserved, undo that re-checks preconditions (AR 3659). Newcomers: `std::filesystem::remove`.
13. **Prefabs (reusable templates with linked instances).** Problem: many copies of one thing that should stay in sync.
    Approaches: copy-paste (no link), Unity prefabs (property modifications, nested prefabs, variants), Unreal Blueprints
    and level instances, Godot instanced scenes with editable children. Strata: a link component per entity, instance
    roots owning transform and name, an override list kept on every edit, propagation of prefab changes except
    overrides, versions and hashes so closed scenes catch up, "outdated" when both sides changed (AR 3753; MP). No nested
    edit mode. Newcomers: treat the root transform as an override; propagate twice (file watcher + own write: hence
    `SetBaseline`); overwrite newer prefab values with an outdated instance.
14. **Play-in-editor.** Approaches: duplicate the world in memory (Unreal PIE), serialize/reload (Unity play mode),
    separate process (Godot). Strata: `Scene::Copy` of the edited scene, the running copy is what commands act on, edits
    are not recorded and vanish on Stop, the game's window requests are recorded not applied (EditorContext.cpp
    1363-1433; MG). Scene view vs Game view (editor camera vs primary camera). Newcomers: edit while playing and expect
    changes to persist; let game volume or cursor leak into the editor.
15. **Fixed-step simulation, pausing and stepping.** Fixed timestep vs variable frames, catch-up steps, time dilation,
    interpolation; why tests count steps, not frames (determinism across frame rates; DG 3723, 3742). Newcomers: wait N
    frames in a test.
16. **Asynchronous commands.** A command returns `Defer(poll)`; a runner polls once per frame, journal entry stays
    pending; `MayDefer` declaration lets batches refuse what cannot finish in a frame (DG 3176). Poll functions own
    copies, allocate nothing per frame, wait by the clock. Newcomers: capture parameters by reference; busy-wait; call
    `LoadAssetSync`.
17. **Scripts of commands, record and replay.** Data-driven test scripts (`expect`, `bind`/`$ref`, `until`), batches as
    one undo step, journal → replay script on a copy of the project → compare (AR 3452, 3486). Newcomers: hard-code IDs.
18. **Opening content in the background.** Load while showing the old scene, read-only guard, swap between frames,
    cancel on a newer request (AR 3494).
19. **Placing objects in 3D.** Ray casting from a camera (NDC → ray), BVH/spatial index broad phase, triangle narrow phase,
    fallbacks (ground plane, in front), snapping, resting a box on a plane via its support function (EditorPlacement.cpp
    125-213). Preview/drop parity (same request bits). Newcomers: place at origin; use the box center not its support;
    drop at a different point than the ghost showed.
20. **Editor cameras.** Orbit/pan/dolly/fly controls, spherical coordinates (yaw/pitch/distance around a target), pitch
    clamping, units-per-pixel panning, framing bounds (sphere vs. corners), reversed-Z projection; per-scene view state
    (EditorCamera.cpp 70-170).
21. **Caches keyed by content.** Thumbnails keyed by content stamps of an asset and its dependencies, version constant
    to invalidate on look changes, non-stalling GPU readback (AR 3712).
22. **Telling the person what happened.** Activity journal with origins, toasts for what agents did (deletes, discards),
    never toasting the person's own actions (AR 3397).

---

## 3. Code worth showing

Line ranges are at 822a7a46.

1. `StrataEditor/src/Editor/EditorCommands.h` 44-80 — `EditorCommandResult`: value/error/kind/defer in one struct, the
   factories. Teaches the shape of a command API. Before: structs, `std::function`, JSON basics.
2. `StrataEditor/src/Editor/EditorCommands.h` 84-113 — `EditorCommand` and `MayDefer`: metadata as decisions (kind,
   results, scan wait, defer). Before: excerpt 1.
3. `StrataEditor/src/Editor/Commands/EntityCommands.cpp` 514-528 — `entity.rename`: the smallest complete mutating
   command (schema, arguments, transaction, `MarkModified`, `FinishEdit`). Before: ECS components, transform contract.
4. `StrataEditor/src/Editor/Commands/EntityCommands.cpp` 170-218 — `entity.create` and `entity.delete`: `TrackCreated`
   after creating, `TrackSubtree` before destroying, `RollBackEdit` on failure. Before: excerpt 3.
5. `StrataEditor/src/Editor/EditorCommands.cpp` 105-151 — `EditorCommandRegistry::Execute`: journal, asset-scan
   deferral, Debug assertion on `MayDefer`, undo attribution. Before: excerpts 1-2, lambdas capturing by value.
6. `StrataEditor/src/Editor/EditorCommands.cpp` 174-221 — `Run` and `CheckParameters`: schema as contract, exceptions
   only at the third-party boundary. Before: JSON Schema basics.
7. `StrataEditor/src/Editor/UndoStack.h` 27-56 — `EditorAction`: the undo interface, including failure and merge.
   Before: virtual functions, `unique_ptr`.
8. `StrataEditor/src/Editor/UndoStack.cpp` 48-106 — `UndoStack::Push`: discard redo branch, merge, drop no-op, trim
   capacity while keeping the save point right. The central algorithm of undo. Before: excerpt 7, `std::deque`.
9. `StrataEditor/src/Editor/UndoStack.cpp` 156-221 — `Undo`/`Redo` with their different failure semantics. Before: 8.
10. `StrataEditor/src/Editor/UndoStack.cpp` 278-311 — `GetSavePoint`, `MarkSaved(point)`, `IsModified`. Before: 8.
11. `StrataTests/src/Editor/UndoStackTests.cpp` 17-69 and 262-374 — a toy `AddAction` and tests of merging, no-op drop,
    save points across background saves: the best way to explain the behaviour with integers. Before: 7-10, doctest.
12. `StrataEditor/src/Editor/SceneEdit.h` 21-37 and 132-169 — `EntityState` and `SceneEditTransaction` API. Before:
    UUIDs, serialization of components.
13. `StrataEditor/src/Editor/SceneEdit.cpp` 187-281 — `SceneEdit::ApplyEntities`: batch destroy, batch recreate with
    UUIDs, component diff, sibling list re-placement (and why every recorded entity of a changed list is placed). The
    central algorithm of scene undo. Before: 12, hierarchy (parent/children/sibling index).
14. `StrataEditor/src/Editor/SceneEdit.cpp` 351-363 and 388-463 — merge rule and the transaction's capture/commit.
    Before: 12-13.
15. `StrataEditor/src/Editor/PropertyEdit.cpp` 135-155 — `SetPropertyWithUndo`: the inspector's path, merge key per
    entity/component/property. Before: 14, reflection (`ComponentInfo`, `PropertyInfo`).
16. `StrataEditor/src/Editor/EditorContext.cpp` 1875-1891 — `CommitEdit`: the gate (playing, opening, world, overrides).
    Before: 14, play mode concept.
17. `StrataEditor/src/Editor/Commands/BatchCommands.cpp` 45-119 — `editor.batch`: up-front refusal, `BeginGroup`,
    `CancelGroup` on atomic failure. Before: 8, groups.
18. `StrataEditor/src/Editor/CommandUtils.cpp` 276-332 — `CheckUnsavedChanges` and `AfterSaves`: data-loss guard and
    the deferral wrapper (a higher-order function). Before: 1, deferral.
19. `StrataEditor/src/Editor/EditorSceneCommands.cpp` 379-406 — `scene.new`: the guard, `AfterSaves`, `MayDefer`
    together in a real command. Before: 18.
20. `StrataEditor/src/Editor/EditorContext.cpp` 1045-1103 — `SubmitSceneSave`/`OnSceneSaveEnded`: snapshot, save point,
    recovery token, completion handling every outcome. Before: 10, threads/jobs.
21. `StrataEditor/src/Editor/DocumentSaver.cpp` 114-211 and 218-268 and 293-343 — job run (per-item atomic write,
    loader validation of ready bytes), submit (coalescing queued requests), collect (publish in one step, completions).
    Central algorithm of background saves (long). Before: 20, atomics with acquire/release, `std::function`.
22. `StrataEditor/src/Editor/EditorContext.cpp` 688-717 — `ResetScene`: everything that must happen when a scene is
    replaced, in order (recovery first). Before: 11 concepts.
23. `StrataEditor/src/Editor/SceneRecovery.cpp` 61-77, 629-688, 754-767 — `IsStructural`, `OnApplied` (merge replaces
    pending states), the quiet-timer `Update`, and folding. Before: observer pattern, 13.
24. `StrataEditor/src/Editor/EditorAssetCommands.cpp` 899-939 and `AssetFileAction.cpp` 94-107 — `asset.delete` with
    references in `ErrorData`, recording `AssetTrashAction`; trash/restore as undo. Before: 7, asset handles.
25. `StrataEditor/src/Editor/EditorContext.cpp` 1893-1981 — `UpdatePrefabOverrides`: finding touched instances,
    reshaped vs. incremental, tracking roots so drags merge. Before: prefab concepts, 14.
26. `StrataEditor/src/Editor/EditorPrefabCommands.cpp` 436-583 (with 39-72) — `prefab.apply`: template conversion,
    propagation, one undo step for file and scene, baseline. Long but the heart of prefabs. Before: 25,
    `PrefabInstances`/`PrefabOverrides` APIs.
27. `StrataEditor/src/Editor/PrefabSync.cpp` 336-383 — `CatchUp`: version and hash decide updated vs. outdated.
    Before: 26.
28. `StrataEditor/src/Editor/EditorContext.cpp` 1363-1433 — `StartRuntime`/`Stop`: what play mode copies, resets and
    restores. Before: scene copy, play mode concept.
29. `StrataEditor/src/Editor/Commands/PlayCommands.cpp` 191-256 — `play.step`: a deferred Session command with a
    stateful poll that detects resume/stop. Before: 16 concepts, 28.
30. `StrataEditor/src/Editor/EditorCommandRunner.cpp` 274-309 and 337-369 — polling pending results and the runner's
    update loop (why it copies the count, why completions issue commands for the next frame). Before: 1, vectors that
    reallocate.
31. `StrataEditor/src/Editor/EditorPlacement.cpp` 125-213 — `Place` and `RestOn` (box support function along a normal).
    Before: rays, AABBs, dot products.
32. `StrataEditor/src/Editor/EditorCamera.cpp` 70-91, 136-170, 256-259 — orbit, pan by units-per-pixel, `FitBounds`
    over 8 corners, position = target − forward·distance. Before: spherical coordinates, FOV.
33. `StrataEditor/src/Editor/ViewportRenderer.cpp` 24-95 — which camera a view uses and what editor views change.
    Before: cameras, play mode.
34. `StrataEditor/src/EditorLayer.cpp` 614-668 — the editor's frame order. Before: game loop.
35. `StrataTests/Editor/SmokeCommands.json.in` 1-30 — a real command script with `bind`, `$ref` and `expect`. For both
    audiences. Before: commands concept.

(35 listed; a chapter author picks 10-30. Must-haves: 3, 5, 8, 13, 18, 21, 26, 29, 31, 35.)

---

## 4. Figures

### Diagrams

1. **Layer stack** of the editor: StrataEditor (app, `EditorHost`) / StrataEditorUI (`EditorLayer`, panels, UI kit) /
   StrataEditorCore (`EditorContext`, registry, runner, automation) / engine. Source: AR 3219-3237.
2. **Three clients, one registry**: person (panels → `RunEditorCommand`/runner), agent (RPC → `EditorAutomation` →
   runner), test/script (`EditorCommandScript` → runner) all into `EditorCommandRegistry::Execute` → `EditorContext`.
3. **Command lifecycle** (sequence diagram): Execute → journal Begin → (scan wait?) → CheckParameters → handler →
   result Ok/Fail or Defer → runner keeps it → polls each frame → final → journal Complete → completion/notification.
4. **Editor frame timeline**: record frame time → `EditorContext::Update` (saves publish, scene swap, runtime update or
   prefab sync, recovery) → runner polls → automation requests → command script → panels render. Mark "polls run before
   views render" (EditorLayer.cpp 614-668; EditorContext.cpp 2712-2808).
5. **Undo stack state** (memory layout): deque of entries with serials, position cursor, save-point marker, merge
   flag; show record after undo dropping the redo branch, merge, no-op drop, capacity trim (UndoStack.cpp 48-106).
6. **SceneEditTransaction flow**: constructor captures before → edits → `TrackCreated` → `Commit` captures after →
   `SceneEditAction{before, after}`; undo/redo = `ApplyEntities(before|after)`.
7. **ApplyEntities batches**: three phases (destroy batch, recreate batch, components, placement batch of affected
   sibling lists) with a small hierarchy example where positions "agree by chance".
8. **Background save timeline**: frame N snapshot + save point + token; job writes; edits continue in frames N+1..; publish
   at frame M; `MarkSaved(point)` leaves later edits unsaved; recovery `OnSaved` carries them over.
9. **Data-loss guard decision tree**: command → saves in flight? (AfterSaves defers) → scene modified? → scope Project
   and project file unwritten? → scope Editor and preferences unwritten? → force? → proceed (ResetScene writes recovery
   first).
10. **Recovery journal file**: header (scene handle, path, base hash, owner pid+start, discarded) + body (settings,
    steps as segments); show folding of non-structural steps; and the lifecycle (written after 2 s quiet / every 10 s,
    removed on save or undo to save point, discarded → offered → Recovery/Discarded).
11. **Asset delete with trash and undo**: referencers (index + scene in memory + project) → refuse or move to
    `.strata/Trash` → `AssetTrashAction`; undo restore with precondition checks.
12. **Prefab instance anatomy**: prefab snapshot (template ids) vs. scene subtree (UUIDs, `PrefabInstanceComponent`
    on each linked entity, added unlinked entity, instance root with own transform/name and `Overrides`,
    `PrefabVersion`, `SyncedHash`).
13. **Prefab instance states**: synced → modified (overrides) → outdated (prefab changed while modified and closed);
    transitions apply, revert, unpack, propagation, catch-up.
14. **Prefab change propagation** (sequence): instance A edited → `prefab.apply` → file written + `SetBaseline` → other
    instances `Propagate` except overrides → one undo step; vs. a change on disk → `PrefabSync::Update` detects revision
    → propagate.
15. **Play mode state machine**: Edit ↔ Play/Simulate; Paused sub-state; stepping; scene switch loading; Stop discards
    the copy; quit request.
16. **Fixed steps vs frames timeline**: frames of varying length, fixed steps due on the clock, catch-up, time dilation;
    paused + `play.step` = one step per frame; input tap of N steps.
17. **Placement decision flow and RestOn geometry**: point → surface → grid (≤500 m) → in front; snapping; and a 2D
    sketch of a box resting on a slanted surface with the support distance `|n|·extents − n·center`.
18. **Editor camera model**: target, distance, yaw around +Y, pitch, position = target − forward·distance; pan plane at
    target depth; FitBounds with corners against the frustum.
19. **Scene open in the background** timeline: request → read-only edited scene (banner, refused edits) → load progress
    → swap between frames → prefab catch-up → `scene.open` answers one frame later.
20. **Record and replay**: journal entries with origins → `BuildReplayScript` (bind/$ref) → run on a project copy →
    compare documents.

### Screenshots (editor UI; this area has no rendering features of its own)

All taken in the editor on a copy of a sample (`project.openSample`) or the `basic3d` template.

1. The editor as a whole with the Scene view, Hierarchy, Inspector, Content Browser, Activity panel docked
   (`Samples/Showcase` or `ThirdPerson`), to name the parts.
2. Activity panel listing commands from the person, an agent (by name) and a command script, with an undo step
   attributed (run a few `entity.*` through StrataCLI and a few by hand).
3. Edit menu or `edit.history` result showing named steps ("Create 'Wall'", "Delete 3 entities", "Batch of 4 commands").
4. The unsaved-changes dialog (edit, then File > Open Scene).
5. The saving status pill and the saving dialog while a large scene saves (any big world sample, `scene.save`, then
   try to open another scene).
6. The Recover Unsaved Changes dialog after a simulated crash (edit, kill the process, reopen the project), and the
   toast after a forced `scene.open {force: true}` from an agent ("discarded by ...", Recover).
7. Content Browser delete refusal (Delete Asset dialog listing users) and the toast of an agent's delete with Undo hint.
8. Inspector prefab bar with overrides marked (bold label, accent bar) and the Overrides menu (change a light's
   intensity on an instance of a prefab in `Samples/PhysicsPlayground` or `ThirdPerson`).
9. Hierarchy marks of a modified and an outdated instance (apply a prefab from one scene, change an instance in another,
   open it).
10. Placement ghost: dragging a prefab over the Scene view, (a) on a surface with the ring and label "Crate on
    'Ground'", (b) over empty sky with the dimmed guess box (wave 8 feature).
11. Scene view and Game view side by side while playing (drag the Game tab beside the Scene tab), status bar in play
    color; and the Game view letterboxed at 4:3 with its resolution menu open.
12. Paused game after `play.step {steps: 30}` with the status bar showing the step count (or `play.state` result).
13. Scene opening in the background: viewport load card and the Hierarchy/Inspector read-only banner (open a large
    world scene).
14. Launcher with project cards showing `ProjectThumbnail` pictures; Content Browser grid showing thumbnails of
    materials, meshes and prefabs.
15. Command script run: terminal output of `StrataEditor --commands SmokeCommands.json --no-gpu --quit-after-commands`
    and its exit code (text capture, not a window).

---

## 5. Rules and pitfalls (the book's "why" boxes)

1. **Every change goes through a command (or `SceneEditTransaction`/`SetPropertyWithUndo`).** Otherwise the UI,
   agents and tests diverge, and the change has no undo step, no journal entry and no replay (DG 2833; AG Editor 1).
2. **Panels never write, move or remove files.** Files changed behind the history break undo, the trash, references
   and the file watcher; a source-scan test enforces it (EditorUISourceTests.cpp 631).
3. **Reject invalid input without side effects; one undo step per successful mutation.** A half-applied command
   leaves the scene in a state no undo step describes (DG 2881).
4. **Track before you change, track created entities after you create them; `TrackSubtree` before deleting.** A
   transaction compares before/after states of *tracked* entities only; untracked changes are invisible to undo (SceneEdit.h 132-146).
5. **Signal component writes (`MarkModified`).** Scene caches (names, transforms) go stale otherwise; `entity.rename`
   shows the pattern (AG Scene caches).
6. **Give continuous edits a merge key and break the merge when the drag ends.** Otherwise a drag is hundreds of undo
   steps, or two drags merge into one (UndoStack.h 40-45, 152-153).
7. **Undo can fail; design for it.** Files change outside the history; an undo that cannot be done keeps the step, a
   redo that cannot be done drops the rest (UndoStack.cpp 156-221).
8. **Steps that don't change the scene say so (`ChangesScene() == false`).** Otherwise a material edit marks the scene
   unsaved and triggers questions on close (UndoStack.h 46-48).
9. **Mark every command's kind; mark session queries; mark `MayDefer` and `WaitsForAssets`.** Replays repeat Edit
   commands only, never bind IDs from session results, batches refuse deferring commands; Debug asserts and the kind
   lists in CommandJournalTests catch a missing mark (DG 2881, 3176).
10. **Never serialize a document on the main thread for a save.** A million entities would hold the frame for seconds
    (RN 0.4.0: 22 s before background saves); use `DocumentSaver`/`SettingsFileWriter` (AG Editor 5).
11. **Take the save point after `BreakMerge`.** A drag continuing during a save would otherwise merge into the saved
    step and the saved state would be unreachable (EditorContext.cpp 1047-1050).
12. **Commands that replace the scene, close the project or quit: `CheckUnsavedChanges` + `AfterSaves` + `MayDefer`.**
    Otherwise `force` discards a save in flight, or a save and an open race (DG 2911).
13. **The UI passes `force` only for what the person was asked about.** The scene may change while a dialog waits (an
    agent keeps working); asking again when `UndoStack::GetVersion` moved prevents discarding unseen edits (DG 2911).
14. **Only `SceneRecovery` writes recovery files; every scene replacement goes through `ResetScene`.** That is what
    makes "discard" mean "kept as recovery data" (AG Editor last bullet; EditorContext.cpp 688-717).
15. **A scene being opened is read-only: check `CheckSceneEditable` outside `CommitEdit`.** The opened scene will
    replace it between frames; an edit now would be lost silently (AR 3494).
16. **Edits while playing are not recorded and are discarded by `play.stop`; say so in the result.** People and agents
    otherwise lose work they thought they made (DG 3451).
17. **Commands never block a frame; polls own their data, allocate nothing per frame, wait by the clock.** Capturing
    parameters by reference crashes when the request is gone; allocations in a frame can wait milliseconds for the heap
    while a scene is freed in the background (DG 3176; CommandUtils.h 118-123).
18. **Never `LoadAssetSync` in the editor or a game; load scenes through `SceneLoader`, release with
    `Scene::ReleaseInBackground`.** (DG 3091; AG Editor last bullet.)
19. **Tools count game time in fixed steps, never frames.** Frames differ per machine; steps make tests exact
    (DG 3723; AG Editor "Tools count game time").
20. **Code that writes a prefab sets the sync's baseline (`SetBaseline`) and marks instances synced (`MarkSynced`).**
    Otherwise the file watcher propagates the editor's own change a second time, or closed scenes never catch up
    (DG 2854).
21. **Code that records a scene step outside `CommitEdit` keeps override lists current (`UpdatePrefabOverrides`, or
    `OverrideUpkeep::Current`).** Otherwise undo restores stale overrides (DG 2854).
22. **Never apply an outdated instance without `force`.** Its older values would overwrite the prefab's newer changes
    (MP 47-57).
23. **Place content through `EditorPlacement::Place`; the drop and its ghost use one request.** A person's drop and an
    agent's call must land identically; hovering must write nothing (DG 3525; AG Editor "Content is placed through").
24. **Files written for clients go through `ResolveOutputPath`.** Relative paths would otherwise resolve against the
    editor's working directory; reserved device names and UNC paths are security and correctness hazards (DG 3847).
25. **Bump `ThumbnailCache::c_Version` when thumbnails would look different.** Cached PNGs are keyed by content stamps,
    which do not see a change of how they are rendered (DG 3260).
26. **Never walk the scene or the asset directory per frame in UI code; use the cached views.** (AG Editor; core
    models `HierarchyView`, `AssetBrowserView`.)

---

## 6. Hands-on

### For game developers (using the editor)

1. **Undo is your friend** (easy): make a small scene from `basic3d`, delete a parent with children, undo, check names
   and order; drag a value in the Inspector and see one undo step. Proves: what one undo step is.
2. **Prefab round trip** (easy-medium): make a crate prefab from entities, place three instances (drag into the Scene
   view; use Snap), override one's material, Apply another, observe propagation except the override, Revert All on the
   overridden one, Unpack the third. Proves: link, override, apply, revert, unpack (MP).
3. **Outdated instances** (medium): two scenes using one prefab; change an instance in scene B, close it, apply from
   scene A, reopen B; read `prefab.status`. Proves: catch-up and outdated semantics.
4. **Play, pause, step** (easy): play a sample, pause, step 10 times, change a light while playing, stop and see it
   gone. Proves: running copy, edits while playing.
5. **Game view resolutions** (easy): set 4:3 and a fixed 1280x720, check a HUD button is hit where drawn (MG 28-34).
6. **Recover after a crash** (medium): edit, kill the editor process, reopen, recover. Proves: autosave journal.
7. **A first command script** (medium): write a `--commands` file that creates a project, builds a scene with `bind`
   and `$ref`, plays, pauses, `play.step {steps: 60}` with an `expect` on a transform, and quits; run it headless.
   Proves: commands as an API, deterministic tests (model: `StrataTests/Editor/SmokeCommands.json.in`).
8. **Export your session as a regression script** (medium): do work by hand and by StrataCLI, `editor.activity.export`,
   run it on a copy; note `editsOutsideCommands`. Proves: journal and replay, why inspector drags are not replayed.

### For engine developers (changing the editor)

1. **Read the undo tests** (easy): run `StrataTests --test-suite=Editor.Undo`, then add a test that a merged drag
   followed by `MarkSaved` and another drag yields two steps. Proves: merge and save point rules.
2. **Add a mutating command** (medium): e.g. `entity.setTag {entities, tag}` with schema, `CommandArguments`,
   multi-entity transaction, `FinishEdit`, a kind entry in `CommandJournalTests.cpp`, a unit test, and the feature-test
   exercise. Proves: command conventions end to end.
3. **Add a deferred command** (medium-hard): e.g. `editor.waitSeconds {seconds}` that waits by `steady_clock`, marked
   `MayDefer`, listed in `c_DeferringCommands`; test it with the runner and check `editor.batch` refuses it. Proves:
   deferral, ownership in polls, batch rules.
4. **Write a non-scene undo action** (medium): an `EditorAction` for a hypothetical asset rename that checks its
   precondition in `Undo`; test the "undo fails, step stays" path. Proves: failure semantics, `ChangesScene`.
5. **Trace a background save** (medium): add a temporary test that edits during a held save (DocumentSaveTests has a
   hook pattern) and checks `IsSceneModified` after publish. Proves: save points.
6. **Break and fix the guard** (exercise): remove `AfterSaves` from `scene.new` in a scratch branch and find which
   `Editor.Saves`/`Editor.DataSafety` test fails and why. Proves: why the wrapper exists.
7. **Extend placement** (hard): add a `stackOn` option that rests a placed asset on top of a given entity's bounds;
   reuse `RestOn`; keep drop/command parity. Proves: ray/box math, parity rule.
8. **Recovery folding exercise** (hard, paper first): given a sequence of steps (create, three value edits, reparent,
   value edit), write the segments the journal produces; then verify with a `Editor.Recovery` test. Proves: `IsStructural`.
9. **Camera math exercise** (easy-medium): derive `Pan`'s units-per-pixel from FOV and distance; derive why `FitBounds`
   uses `margin·x/tan − z`. Proves: projection geometry.

---

## 7. Glossary

- **Editor core (`StrataEditorCore`)**: the editor's state and logic without any UI.
- **`EditorContext`**: the object holding all editor state; every operation goes through it.
- **`EditorHost`**: the interface the UI uses to reach the application (window, frame count, close).
- **Command**: a named operation (`<group>.<action>`) taking a JSON object, returning JSON or an error.
- **Command registry**: the table of all commands (`EditorCommandRegistry`).
- **JSON Schema**: a JSON description of the parameters a command accepts.
- **Command kind**: Edit (changes the project), Query (changes nothing), Session (changes the editor's session).
- **Session results**: query results that depend on the editor's session (selection, journal), never bound in replays.
- **`InvalidParameters` / `Failed`**: the request was wrong / the request was valid but impossible now.
- **Deferred command**: one that answers in a later frame by returning a poll function (`Defer`).
- **Poll function**: the callable polled once per frame until it returns a final result.
- **`MayDefer`**: the declaration that a command's handler may defer.
- **`WaitsForAssets`**: a command that waits for the background asset scan.
- **Command runner**: polls pending commands each frame (`EditorCommandRunner`).
- **Command script**: a JSON array of command steps run at startup (`--commands`).
- **`expect`**: conditions on a step's result by JSON pointer.
- **`bind` / `$ref`**: name a value of a result / use it in later parameters.
- **`until`**: repeat a query step until its expectation holds, bounded by steps or seconds.
- **JSON pointer**: a path into a JSON document like `/values/Translation/1`.
- **Batch**: several commands in one frame as one undo step (`editor.batch`); **atomic** batch reverts on failure.
- **Activity journal**: the record of every command run, with its origin.
- **Origin**: who ran a command: UI, Automation (agent), CommandScript, Internal.
- **Replay script**: a command script built from the journal to repeat a session.
- **Undo step / action**: an `EditorAction` that can be executed and undone.
- **Undo stack / history**: the linear list of steps with a position.
- **Redo branch**: undone steps, discarded when a new step is recorded.
- **Merge / merge key**: absorbing a continuous edit into the previous step when keys match.
- **No-op step**: a merged step that ended where it started; dropped.
- **Break the merge**: force the next edit to start a new step.
- **Action group**: several actions as one all-or-nothing step.
- **Serial**: a step's unique number that survives merges.
- **Save point**: the history position matching the file on disk; "modified" means elsewhere.
- **Generation**: a counter of history clears, telling one scene's history from the next.
- **Memento / snapshot**: stored state used to restore; here `EntityState`.
- **`EntityState`**: one entity's components (JSON), parent, sibling index and cell.
- **Scene edit transaction**: captures tracked entities before an edit and records the difference.
- **Rollback**: restoring tracked entities to their state before a failed edit.
- **Sibling index**: an entity's position among its parent's children.
- **UUID / asset handle**: stable 64-bit identifiers of entities / assets.
- **`.meta` file**: the file beside an asset holding its handle.
- **Running copy**: the copy of the edited scene that runs in play mode.
- **Edited scene**: the scene being authored (`GetEditScene`); **active scene**: running copy while playing, else edited.
- **Play / Simulate**: run with scripts, physics, audio / physics only.
- **Fixed step**: one simulation update of fixed duration.
- **Time dilation**: slowing the game when steps cannot keep up instead of running catch-up steps.
- **Stepping**: running a chosen number of fixed steps while paused.
- **Game view / Scene view**: what the player sees (primary camera) / the editor camera with overlays.
- **Primary camera**: the scene camera marked Primary.
- **Editor view**: a view of the editor camera outside play (preview lighting, hidden HUD).
- **Preview lighting**: a sun and sky the editor adds to unlit scenes in editor views.
- **Game shell**: the editor's stand-in for the game's window and saves (`EditorGameWindow`, save directory).
- **Simulated input**: keys/buttons/actions held by commands, timed in fixed steps.
- **Input sequence**: a timeline of input events per fixed step (`input.sequence`).
- **Snapshot (save)**: a copy of the scene taken in the frame, written by a background job.
- **Atomic write**: writing to a temporary file and replacing the target in one rename.
- **Document claim**: the asset manager's lock on a file a save writes.
- **Publish**: making a written document the asset's state on the main thread.
- **Coalescing**: replacing a queued save of the same documents by the newer one.
- **Unwritten settings**: project or preference changes whose last write failed.
- **Discard scope**: what a replacing command lets go of: Scene, Project or Editor.
- **`force`**: the parameter that lets a command discard unsaved changes.
- **Recovery journal**: the file of unsaved changes for crash recovery.
- **Base hash**: SHA-256 of the saved scene file a journal applies to.
- **Structural step**: a step that creates, removes or moves an entity; others fold.
- **Discarded (recovery)**: changes written on purpose when a scene was replaced; still offered.
- **Trash**: `<project>/.strata/Trash`, where deleted assets go for 30 days.
- **Referencer**: something that uses an asset (another asset, the open scene, the project).
- **Prefab**: a saved group of entities (`.stprefab`) placed as linked instances.
- **Instance / instance root**: a placed copy / its top linked entity.
- **Template id (`PrefabEntityID`)**: an entity's id inside the prefab.
- **Override**: a value an instance keeps of its own against its prefab.
- **Apply / Revert / Unpack**: write instance into prefab / take prefab's values / remove the link.
- **Propagation**: giving instances a prefab's change except their overrides.
- **Baseline**: the prefab snapshot the sync compares instances with.
- **Catch-up**: updating unmodified instances of prefabs changed while their scene was closed.
- **Outdated**: an instance modified while its prefab changed elsewhere.
- **Part version / synced hash**: hash of the prefab's part / of the instance's values when it last synced.
- **Raycast**: finding what a ray from the camera hits.
- **Spatial index / broad phase**: a structure that finds candidates near a ray before exact tests.
- **Support function**: how far a box extends along a direction; used to rest it on a surface.
- **Snapping**: rounding a position to a grid step.
- **Placement ghost**: the box preview of where a dragged asset will land.
- **Orbit camera**: a camera rotating around a target at a distance.
- **Pivot**: the editor camera's target point.
- **Dolly / pan / fly**: move toward target / move parallel to view / move freely with keys.
- **Reversed-Z**: depth mapping with near = 1, far = 0 for precision.
- **Framing**: moving the camera so bounds fill the view.
- **Thumbnail cache**: rendered asset previews kept as PNG keyed by content stamps.
- **Content stamp**: a summary of an asset's source size, time, settings and importer version.
- **Readback**: copying GPU image data to the CPU without stalling.
- **Notification / toast**: a transient message to the person with actions.
- **Headless**: running without a window or GPU (`--no-gpu`).
- **Asset scan**: background registration of a project's assets when it opens.

---

## 8. Proposed chapters (teaching order)

1. **The editor is a program** — concept, both, S-M. Purpose: explain what an in-engine editor is, Strata's core/UI
   split, `EditorContext`, the frame order. Prereqs: game loop, ECS scene basics. Screens: 1.
2. **Commands: one API for people, agents and tests** — internals, engine (with a game-dev sidebar), L. Purpose:
   write and register a command with schema, kind, validation and errors; know every group. Prereqs: ch. 1, JSON,
   `std::function`. Screens: 1 (Activity panel).
3. **Undo and redo** — internals, engine, L. Purpose: explain and extend `EditorAction`, `UndoStack`,
   `SceneEditTransaction`, `ApplyEntities`, merging, groups, save points. Prereqs: ch. 2, UUIDs, scene hierarchy,
   serialization. Screens: 1.
4. **Saving without stalling, closing without losing** — internals, engine, L. Purpose: background saves
   (`DocumentSaver`, `SettingsFileWriter`), atomic writes, save points under concurrent edits, the unsaved-changes guard
   and `AfterSaves`, `ResetScene`/`ReleaseProject`. Prereqs: ch. 3, job system, atomics. Screens: 2.
5. **Autosave and crash recovery** — internals, both, M. Purpose: the recovery journal, folding, discards, recovering
   as one undo step; how to recover as a user. Prereqs: ch. 3-4, observer pattern. Screens: 2.
6. **Project files as history: the trash and references** — internals, both, M. Purpose: asset file actions, reference
   checks, precondition-checking undo. Prereqs: ch. 3, asset handles and `.meta` (asset pipeline chapter). Screens: 1.
7. **Using prefabs** — tutorial, game, M. Purpose: make, place, override, apply, revert, unpack prefabs; understand
   outdated instances. Prereqs: editor basics (UI chapters). Screens: 3.
8. **How prefab instances stay linked** — internals, engine, L. Purpose: links, instance roots, override upkeep,
   propagation, baselines, catch-up with versions and hashes. Prereqs: ch. 3, 7, scene serialization. Screens: 1.
9. **Play mode and the Game view** — concept + tutorial, both, M. Purpose: the running copy, Scene vs Game view,
   edits while playing, the game shell, scene switches and quitting. Prereqs: ch. 1, scene runtime lifecycle. Screens: 2.
10. **Time in steps: pausing, stepping and exact tests** — internals + tutorial, both, M. Purpose: fixed steps,
    time dilation, `play.step`, simulated input and `input.sequence` for deterministic tests. Prereqs: ch. 9, fixed
    timestep (engine chapter). Screens: 1.
11. **Commands that take frames** — internals, engine, M-L. Purpose: `Defer`, the runner, poll rules, `MayDefer`,
    asset-scan waits, opening scenes and projects in the background and the read-only guard. Prereqs: ch. 2, 4.
    Screens: 1 (scene load overlay).
12. **Scripting the editor: command scripts, batches, record and replay** — tutorial + internals, both, M. Purpose:
    write `--commands` scripts with `bind`/`expect`/`until`, use `editor.batch`, export a session as a regression
    script. Prereqs: ch. 2, 10, 11. Screens: 1 (terminal).
13. **Placing content** — internals (math), both, M. Purpose: raycasts against the scene, fallbacks, snapping,
    resting boxes, drop/command parity. Prereqs: vectors, rays, AABBs (math chapters), ch. 2. Screens: 2.
14. **The editor camera and viewport state** — internals, engine, M. Purpose: orbit/pan/dolly/fly math, framing,
    per-scene cameras, which camera each view uses. Prereqs: camera/projection math. Screens: 0-1.
15. **Thumbnails and project pictures** — internals, engine, S. Purpose: caches keyed by content, offscreen rendering
    with non-stalling readback, version bumps. Prereqs: renderer basics, residency. Screens: 1.
16. **Reference: the editor command catalogue** — reference, both, XL. Purpose: every command with kind, parameters
    and what it is for (generated from `editor.commands`). Prereqs: ch. 2. Screens: 0.

---

## 9. Not determined

- Not read in full: `EditorContext.cpp` beyond the functions cited (project open 365-487, scene load 770-962, recovery
  2018-2149, scripts 2213-2696, export); `SceneRecovery.cpp` beyond 50-90, 591-700, 740-790; `PrefabSync.cpp` beyond
  CatchUp; `CommandJournal.cpp` (820 lines) and `BuildReplayScript`; `EditorCommandRunner.cpp`'s `EditorCommandScript`
  implementation (until/bind code); `ThumbnailCache.cpp` (1253 lines); `EditorViewportCommands.cpp` (`viewport.capture`
  logic); `EditorInputCommands.cpp`, `SimulatedInput.cpp`, `InputSequence.cpp`; `AssetReferences.cpp`;
  `SettingsFileWriter.cpp`; `ProjectSettingsAction.cpp`; `AssetEdit.cpp`; `EditorStateCommands.cpp` handlers;
  `EditorApplication.cpp` (command-line table); the UI side of the questions (`EditorShell`, `RecoveryDialog`,
  `DeleteAssetDialog`, `GameViewPanel`).
- The engine pieces the area relies on were read only by their headers: `Scene::Copy`/`SceneCopyOptions`,
  `SceneDocumentWriter`, `AtomicFileWriter`, `EditorAssetManager::ClaimDocumentWrite`/`PublishWrittenDocument`/
  `MoveToTrash`, `SceneLoader`, `PrefabInstances.cpp`, `PrefabOverrides.cpp`.
- Release of arrival not determined for: time dilation, per-scene editor cameras, scene switches in play mode
  (`play.sceneSwitched`), the recovery discard limits (`c_MaxOfferedDiscards`), `asset.findReferences`/folder commands,
  canvas mode details. Placement by ray (`asset.place`, `scene.raycast`, the ghost) is dated from git (files added
  2026-11-02) and RM's wave 8 lane, i.e. after 0.7.0 and not yet in a release.
- Whether the "Prefabs and the Asset tab's editors still save in the frame" limitation (RN 0.7.0) still holds at this
  commit for prefab documents written by `prefab.apply` (it calls `AssetEdit::ApplyDocument`, which reads as a
  main-thread write): believed yes, not verified by running.
- No screenshots were taken (no editor may be run in this survey); the screenshot list is a specification.
- I did not check the feature test project (`StrataTests/FeatureTest/`) for which editor commands it exercises.
