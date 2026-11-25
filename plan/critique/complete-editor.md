# Critique `complete-editor`: completeness against worlds-runtime, editor-core, editor-ui, automation

Lens: completeness of the plan against four inventories (`inventory/worlds-runtime.md`, `editor-core.md`,
`editor-ui.md`, `automation.md`), read whole, walked section by section (Features, Concepts to teach, Rules and
pitfalls, Proposed chapters) against `outline-1.md` … `outline-4.md`, `book.md`'s one-home table and its "What Strata
does not do", and `process.md`'s order of waves. Doubtful facts were checked in the engine at `822a7a46` (read only,
`git show 822a7a46:<path>`).

Verdict in short: almost every item of the four inventories has a plausible page, but the editor and worlds material is
placed so that pages are written and read before what they build on (`worlds/editing` before the editor's undo and
saving, `editor/command-scripts` before the journal it replays, `editor/deferred-commands` after three pages that defer),
several concepts are still claimed by two pages with no row in the one-home table (the editor camera, picking, the
Game view, the unsaved-changes question, export, packs and identity, physics reservation), and the game-maker track has
lost what these inventories gave it (undo, saving and recovery for people; connecting and working with an AI agent).
The first change: move `worlds/editing` and `automation/journal` into the editor part, move
`editor/deferred-commands` up to third, and give part 18 real prerequisites.

Severity as the task defines it: **blocker** (the book fails its goal or the process breaks), **major** (a reader or
the process is clearly hurt), **minor** (worth fixing). No finding here is a blocker.

---

## Findings

### F1 (major) `worlds/editing` is written and read before the editor pages it is made of

- **Where:** `outline-4.md` line 44 (`worlds/editing`), line 36 (part 17's prerequisites), `process.md` lines 78 and 80
  (worlds in wave 4, editor in wave 6).
- **Problem:** every feature of worlds-runtime §1.6 is editor-core machinery: cells in undo steps (`EntityState::Cell`,
  `SceneEdit::LinkCells`, `ISceneCellLoader`), dirty tracking as an `UndoStackObserver`, the two-request save through
  `DocumentSaver`, the play copy (`PrepareRuntimeCopy` on top of `Scene::Copy`), recovery (`CollectCells`,
  `PrepareRecoveredCells` for `scene.recover`), re-celling inside `CommitEdit`. The inventory's chapter 7 lists its
  prerequisites as "5, editor commands and undo, document saver" (worlds-runtime §8). Part 17 names none of them, and
  the page is written in wave 4, two waves before `editor/commands`, `editor/undo`, `editor/saving`,
  `editor/recovery` and `editor/play-mode` exist; `process.md` step 5 promises the opposite order.
- **Same for `worlds/runtime`** (line 46): `GameRuntime` rests on `core/first-frame`/`core/engine-modules` (the
  application/layer model, worlds-runtime §8 ch 9 prereqs), `scripting/script-system` (own `ScriptEngine`, no hot
  reload), `image/quality-settings` (`GameGraphicsService`, written in wave 5) and `gpu/frame-tour` (`GameRenderer`).
- **Proposal:** move `worlds/editing` to part 18 as `editor/worlds` ("Editing a streamed world"), placed after
  `editor/prefab-instances`, written in wave 6; `make/large-worlds` stays the G page. Give `worlds/runtime` the
  prerequisites `core/engine-modules`, `scripting/script-system`, `image/quality-settings`, and write `worlds/runtime`
  and `worlds/export` in wave 5 or 6 (not 4). Add to part 17's prerequisite line: `physics/scale-streaming`,
  `scripting/abi-sdk`, `basics/numbers` (F12).

### F2 (major) Part 18's prerequisites cover a fraction of what its 32 pages need

- **Where:** `outline-4.md` line 52: "`world/reflection`, `world/serialization`, `core/jobs`".
- **Problem:** the inventories name, per proposed chapter (editor-core §8, editor-ui §8): game loop and scene runtime
  lifecycle (`world/systems`), fixed timestep (`core/time`), prefabs (`world/prefabs`), asset handles and `.meta`
  (`assets/handles-meta`), atomics (`basics/threads`), camera and projection math (`gpu/coordinates`), rays and AABBs
  (`basics/math-vectors`, `draw/bounds-culling`), residency (`assets/residency`); for the UI half: window and events
  (`core/windows-events`: `ImGuiLayer` is an overlay layer that swallows events), NVRHI, shaders, binding sets and push
  constants (`gpu/vulkan-nvrhi`, `gpu/shaders`, `gpu/binding`: `ImGuiRenderer`), color spaces (`basics/color`:
  `ImGuiTextureDisplay`), readbacks (`gpu/readback-timing`: picking, thumbnails), the Input module
  (`input/mouse-cursor`: `Input::SetViewport`, cursor lock), settings sections (`world/projects-settings`), and the
  testing chapter (`engineering/testing`, part 20, for `editor/ui-testing`). `book.md` line 22 says a part "is readable
  once its prerequisites (listed on its first page) are read"; with this list it is not.
- **Proposal:** two lists. Chapters 1-15: `world/systems`, `world/reflection`, `world/serialization`, `world/prefabs`,
  `assets/handles-meta`, `core/time`, `core/jobs`, `basics/threads`. Chapters 16-32 add `core/windows-events`,
  `gpu/vulkan-nvrhi`, `gpu/binding`, `gpu/readback-timing`, `basics/color`, `input/mouse-cursor`,
  `world/projects-settings`. Per-page front matter adds the rest (`gpu/coordinates` for `editor/camera-viewport`,
  `draw/bounds-culling` for `editor/placement`, `engineering/testing` for `editor/ui-testing`).

### F3 (major) The journal and replay have two homes, and the replay page comes before the journal

- **Where:** `book.md` lines 77-78 ("Command scripts, record and replay → `editor/command-scripts`"; "Activity journal →
  `automation/journal`"); `outline-4.md` line 67 (`editor/command-scripts`) and line 98 (`automation/journal`).
- **Problem:** the replay export *is* the journal: `editor.activity.export` runs `BuildReplayScript` in
  `CommandJournal.cpp` 697-819, which both inventories teach (editor-core §1.11 rows `editor.activity.export`,
  `CommandJournal`; automation §1.9 and code #26, "third central algorithm"). `CommandJournal` is editor-core code
  (`StrataEditor/src/Editor/`) that records every command, the person's included; command kinds (Edit/Query/Session)
  exist for it (editor-core concept 17, automation 2.13). With the plan's order, `editor/command-scripts` (part 18,
  chapter 11) must teach replay before `automation/journal` (part 19) explains the journal.
- **Proposal:** move `automation/journal` to part 18 as `editor/journal` ("The activity journal and replays"),
  directly before `editor/command-scripts`; replace the two rows by: "Activity journal, command origins, replay export
  (`BuildReplayScript`), agent presence (status pill, viewport chip and flash, launcher card) → `editor/journal`;
  command scripts (`expect`, `bind`/`$ref`, `until`) and `editor.batch` → `editor/command-scripts`; the Activity panel's
  drawing → `editor/instrument-panels`". Retitle `editor/command-scripts` "Command scripts and batches".

### F4 (major) `editor/deferred-commands` comes after three pages that defer

- **Where:** `outline-4.md` line 66 (tenth page of part 18); lines 60, 64, 65.
- **Problem:** `EditorCommandResult::Defer` and `EditorCommand::MayDefer` are part of the command contract
  (`EditorCommands.h` 26-113, editor-core §1.2). `editor/saving` needs it (`AfterSaves` "defers a handler while saves are
  in flight", `scene.save {wait}`, editor-core §1.4), `editor/play-mode` needs it (`play.start {build}` defers, scene
  switches), `editor/stepping` needs it (`play.step` is "a deferred Session command with a stateful poll", code #29).
  The inventory lists ch 11 with prereqs "ch. 2, 4" but its own ch 4 and ch 10 already use deferral.
- **Proposal:** make `editor/deferred-commands` the third page of part 18 (after `editor/commands`, before
  `editor/undo`). Its allocation: `Defer`, the runner, poll rules (own data, no allocation per frame, wait by the
  clock), `FrameTimeRecorder`, `editor.wait`/`editor.perf`, `MayDefer`, `WaitsForAssets` and the asset-scan deferral.
  Opening scenes and projects goes to the page of F7.

### F5 (major) Editor concepts still claimed by two pages, missing from the one-home table

- **Where:** `book.md` lines 56-83 (table); `outline-4.md` lines 57, 64, 69, 72, 78, 81, 82, 84.
- **Problem (evidence per pair):**
  - *Editor camera math* (orbit, pan by units per pixel, dolly, focus, `FitBounds`): editor-core code #32
    (`EditorCamera.cpp` 70-91, 136-170, 256-259), concept 20, figure 18 → `editor/camera-viewport`; editor-ui code #33
    (`EditorCamera.cpp:43-91, 117-134`), concept 17, figure 19 → `editor/scene-view`.
  - *Picking* (async entity-ID readback): editor-core §1.12 `EditorViewport` → `editor/camera-viewport`; editor-ui
    §1.10, concept 18, code #35, figure 20 → `editor/scene-view`.
  - *Gizmo drag as one undo step* (`TransformDrag`): editor-core §1.3 → `editor/undo`; editor-ui code #34, figure 21,
    rule 27 → `editor/scene-view`.
  - *The Game view*: editor-core §1.10 (`GameViewMode`, `ComputeGameViewFrame`, `SetGameInputActive`, game shell) →
    `editor/play-mode`, titled "Play mode **and the Game view**"; editor-ui §1.10, concept 20 → `editor/game-view`,
    "**The Game view** and input ownership".
  - *The unsaved-changes question and its re-ask rule*: editor-core rule 13 and figure 9 → `editor/saving`; editor-ui
    §1.5, concept 24, rule 15, figure 27 → `editor/shell`.
  - *What an editor is, and why it is not the game*: editor-core concept 1 → `editor/program`; editor-ui concept 1 and
    its chapter 2 "What an editor is, and why its UI is immediate mode" → `editor/immediate-mode`.
  - *Commands are the API (three clients, one registry)*: editor-core figure 2, concept 3 → `editor/commands`;
    automation figure 2, concept 2.1 → `automation/agents`.
  - *Notifications*: core model (editor-core §1.1) and drawing (editor-ui §1.14), both meant for `editor/status`, fine;
    `HierarchyView`/`AssetBrowserView` in both (editor-core §1.12, editor-ui §1.8), fine as `editor/lists`: state it.
- **Proposal:** add rows: "Editor camera (controls and math), per-scene cameras, viewport settings → `editor/camera-viewport`;
  `editor/scene-view` links"; "Picking and gizmos (`TransformDrag`) → `editor/scene-view`; `editor/undo` names
  `TransformDrag` as a merge-key example only"; "Game view: resolutions, letterboxing, input ownership → `editor/game-view`;
  running copy, game shell, edits while playing → `editor/play-mode`" and retitle `editor/play-mode` "Play mode: the
  running copy"; "No silent data loss: guards, `AfterSaves`, `ResetScene` → `editor/saving`; asking the person (modals,
  re-ask, `DrawDiscardQuestion`) → `editor/shell`"; "What an editor is → `editor/program`; `editor/immediate-mode` only
  compares retained and immediate UIs"; "Commands are the API → `editor/commands`; automation links";
  "Hierarchy and asset views, clipping, multi-select → `editor/lists`; notifications (model and drawing) →
  `editor/status`". Move `editor/camera-viewport` next to `editor/scene-view` (end of the core half, or first of the
  view pages) so the two read in sequence.

### F6 (major) Export, packs, pruning, patches, manifest and identity: four claimants, no row

- **Where:** `outline-1.md` line 57 (`make/export`), `outline-2.md` line 21 (`world/projects-settings`) and line 39
  (`assets/packs-export`), `outline-4.md` lines 45-46 (`worlds/export`, `worlds/runtime`); `book.md` table.
- **Problem:** pruning, `Export.AlwaysInclude`, patch packs and cooked documents are in worlds-runtime §1.9 and in
  assets' chapter 11 ("pack format, validation, range reads, writer, planning and pruning, cooked scenes, mounts, patch
  tutorial"); the manifest and game identity are in worlds-runtime §1.8 and in scene-ecs' chapter 11 ("project layout
  and file, game identity, manifest, … export"); manifest discovery and patch mounting are runtime (`GameRuntime.cpp`
  73-84). `make/export`'s From names gamedev only, so worlds-runtime's use-side hands-on 7 ("Export and ship") and 9
  ("Prune safely") have no named G home.
- **Related rows missing (same kind):**
  - *Physics capacity and reservation*: physics chapter 11 "capacities and growth … reservation by the streamer" →
    `physics/scale-streaming` (`outline-3.md` line 76); worlds-runtime chapter 6, concept 9, code #13, #18, figure 9
    → `worlds/physics-scripts`. Each part lists the other's subject as a prerequisite (physics ch 11 needs "World
    partition").
  - *Prepared loads* (`SceneLoadOptions::PrepareSystems`, the `Preparing` state, systems' `PrepareLoadedScene` hooks):
    worlds-runtime §1.2, §1.4, concept 16, code #16, figure 8; scene-ecs chapter 8 (the load state machine).
  - *Loading scene and scene switches*: worlds-runtime §1.7 (`GameRuntime` non-blocking loads, `ScheduleTrim`, loading
    scene) vs `assets/references` ("prefetch and loading screens", `outline-2.md` line 36) vs `make/levels-saves`.
  - *Atomic writes; private files and TOCTOU*: foundation concept 16 (`core/platform`), editor-core concept 9
    (`editor/saving`), assets "crash safety" (`assets/robustness`), automation 2.9 and rules 6-8 (`automation/sessions`).
- **Proposal:** rows: "Export: use → `make/export` (From: add worlds-runtime 'Shipping a game: the export', use side);
  pack format, planning, pruning, `AlwaysInclude`, cooked documents, patches → `assets/packs-export`; the export's state
  machine, up-front checks, world cooking at export, what the folder holds → `worlds/export`; manifest and identity →
  `worlds/game-identity` (F8); `world/projects-settings` links"; "Physics capacity, growth limit, `Reserve` →
  `physics/scale-streaming`; what a world reserves, `MaxBodiesInRadius`, the cook → `worlds/physics-scripts`";
  "Prepared loads → `world/serialization` (the loader's states), `worlds/physics-scripts` shows the World hook";
  "Loading scene and scene switches → `worlds/runtime`; load progress and prefetch → `assets/references`; use →
  `make/levels-saves`"; "Atomic writes, private files, TOCTOU → `core/platform`; `editor/saving`, `assets/robustness`,
  `automation/sessions` link".

### F7 (major) `worlds/templates` sits in the wrong part, and opening projects and scenes has no named home

- **Where:** `outline-4.md` line 48; `book.md` line 81; editor-core §1.9.
- **Problem:** `ProjectTemplates`, `ProjectSamples`, `RecentProjects` and `ProjectThumbnail` are editor-core files
  (`StrataEditor/src/Editor/`), unrelated to large worlds; a reader looking for "how the launcher makes a project" opens
  the editor part. The page is thin (two templates, a JSON list of 12 recent projects, a samples index, a thumbnail that
  `editor/thumbnails` also claims: editor-core §1.12 `ProjectThumbnail`). Meanwhile editor-core §1.9 "Opening scenes and
  projects" (`BeginOpenScene` in the background, the read-only guard `CheckSceneEditable`, `scene.open` answering one
  frame after the swap, `scene.loadStatus`, `BeginOpenProject` after the asset scan and migration) and
  `ProjectMigration` (0.5.0 projects, gamedev §1 row "Project migration") are allocated nowhere by name; the inventory
  put opening into "Commands that take frames", which is already full (F4).
- **Proposal:** replace `worlds/templates` with `editor/projects`, "Projects: creating, opening and migrating" (I, M),
  placed after `editor/deferred-commands`: templates and `scene.new {template}`, samples as copies without `.strata`,
  recent projects, `BeginOpenProject`, `ProjectMigration`, opening scenes in the background and the read-only guard,
  `project.create/open/close/openSample`. Row 81 becomes "use: `start/first-game`, `make/samples`; code:
  `editor/projects` (model), `editor/launcher-dialogs` (UI); project pictures: `editor/thumbnails`".

### F8 (major) `worlds/export` holds two chapters' worth: split off the game's identity

- **Where:** `outline-4.md` line 45 (`worlds/export`, I, L).
- **Problem:** allocated from worlds-runtime §1.8-1.9: the export state machine, up-front checks, waiting and planning,
  world cooking at export, pack (link), pruning, patches, script module and PDB, the game icon (square, resized in linear
  light with premultiplied alpha to 10 sizes), `PEResources` (a PE32+ resource section parsed and rewritten without the
  Win32 API, 1188 lines; signed images refused), the Linux desktop entry, the macOS Dock icon, the export commands and
  dialog, the installed layout, the manifest v5 with its plain-file-name rule, `ProjectGameInfo` limits, saves keyed by
  the manifest's Name; concepts 14 and 17; rules 16-19 and 25; code #28-29. Five thousand words cannot walk both the
  pipeline and the platform file formats, which are among the best "how real files work" lessons in the book.
- **Proposal:** split: `worlds/export` (I, L: state machine, checks, ordering "fail before writing", planning, world
  cooking at export, what the folder holds) and new `worlds/game-identity` (I, M: manifest v5 and why it is untrusted,
  `ProjectGameInfo`, `GamePresentation`, saves keyed by Name, `GameIcon`, `PEResources`, `DesktopEntry`, the Dock icon,
  signing after export). Order: `worlds/export`, `worlds/game-identity`, `worlds/runtime`.

### F9 (major) The game-maker track has no page on undo, saving, recovery and the trash

- **Where:** `outline-1.md` part 1 (lines 27-61); `outline-4.md` lines 59-62 (E-only internals).
- **Problem:** editor-core proposed "Autosave and crash recovery" and "Project files as history: the trash" for **both**
  audiences ("how to recover as a user", §8 ch 5-6), with G hands-on 1 ("Undo is your friend") and 6 ("Recover after a
  crash"); editor-ui gives the dialogs (Recover Unsaved Changes, Delete asset listing referencers, the unsaved-changes
  question, the saving pill: §1.5, §1.11). In the outline these live only in part 18, which track G never reads
  (`book.md` line 30: "A game maker never has to read internals"), and no `make/*` row names them. A game maker never
  learns that deleted assets wait 30 days in `.strata/Trash`, that Don't Save is recoverable, how to recover after a
  crash, or that edits made while playing vanish on Stop.
- **Proposal:** add `make/undo-save-recover`, "Undo, saving and getting work back" (H, S), after `make/prefabs`: undo
  and the named history, saving and the saving pill, the unsaved-changes question, edits while playing, Recover Unsaved
  Changes, the trash and refused deletes. From: editor-core "Autosave and crash recovery", "Project files as history"
  (use side); editor-ui §1.11. Part 1 becomes 34 pages.

### F10 (major) Three automation chapters for game makers were folded into one how-to

- **Where:** `outline-1.md` line 56 (`make/automated-playtests`, H, M: "gamedev; automation 'Connecting an AI agent',
  'Making a game as an agent'").
- **Problem:** automation §8 proposes "Connecting an AI agent (MCP)" (tutorial, M, 5 screenshots) and "Making a game as
  an agent" (tutorial, L, 3 screenshots); gamedev adds its own chapter 24. One M how-to (about 3,000 words) now carries
  all three. Lost: toolsets as a user sees them (`strata_toolsets`, `strata_describe`, `strata_call`, enabling `scene`),
  presence (pill, chip, flash, Activity), steering an agent safely (unsaved changes, `force`, never a second editor after
  a CLI timeout), the `strata-make-a-game` playbook to an exported game with a regression script (automation hands-on
  G4, G5, G7, G9; gamedev G15). The engine's pillar is "Agent-native" (`Docs/Roadmap.md` 26-28) and every sample was made
  this way, so this is a headline feature for game makers.
- **Proposal:** three rows in part 1: `make/ai-agent` "Working with an AI agent" (T, M: connect Claude Code, toolsets,
  presence, Activity, Undo to here, safe steering); `make/agent-game` "Project: a game made by an agent" (T, L:
  the playbook, Tetris as the model); `make/automated-playtests` (H, M: command scripts with `play.step`,
  `input.sequence`, `expect`, `until`, replay export as a regression test).

### F11 (major) Part 19 is badged for game makers, but its first page requires engine internals

- **Where:** `outline-4.md` line 92 (prerequisites `editor/commands`, …) and line 96 (`automation/outside`, T);
  `book.md` line 124 (part 19 track "E, G") and line 27 (track G is *Start here* then *Making games*).
- **Problem:** `automation/outside` is the automation inventory's game-maker tutorial (§8 ch 1: "game developers;
  tutorial"), yet the part's prerequisite is `editor/commands` (E internals), and track G's "next" chain never enters
  part 19. A game maker either cannot meet the prerequisites or never reaches the page.
- **Proposal:** move `automation/outside` to part 1 as `make/command-line` "Driving the editor from a terminal" (T, M),
  before `make/ai-agent` (F10), prerequisites `make/editor-tour`, `make/scenes-entities`. Mark part 19 track E, with
  prerequisites `editor/commands`, `editor/deferred-commands`, `editor/journal` (F3), `basics/bytes`,
  `basics/threads`, `basics/computer` (processes, F21), `core/platform` (private files).

### F12 (major) No page teaches how numbers are stored, though the 20 km rule and bit-packed keys depend on it

- **Where:** `outline-1.md` lines 69-80 (part 2); `book.md` table (no row).
- **Problem:** worlds-runtime concept 11 ("float32 has 24 bits of mantissa: precision ~2 mm at 20 km"), figure 19 (a
  float spacing chart), rule 5, and code #2 (cell keys packed into 64 bits, "Reader must know: integer bit operations,
  two's complement") need a primer that no basics page has: `basics/computer` is CPU, memory, stack, heap, caches;
  `basics/bytes` is bytes, files, text, hashes. `research/curricula.md` §1.1 marks floating point a gap with exactly
  these consequences ("camera-relative rendering, the 20 km world limit"). Reversed-Z precision and camera-relative
  rendering (`gpu/coordinates`, `draw/mirrors-camera-relative`) need it too.
- **Proposal:** add `basics/numbers`, "Numbers in a computer: integers, bits and floating point" (C, M), after
  `basics/bytes`: two's complement, shifts and masks, packing keys, IEEE 754 single and double, spacing grows with
  magnitude (with the chart), rounding and determinism. Row: "Floating-point precision → `basics/numbers`; the 20 km
  limit → `worlds/why-streaming`; camera-relative positions → `draw/mirrors-camera-relative`". Part 2 becomes 11 pages.

### F13 (major) "What Strata does not do": one claim is wrong for the editor, several absences are missing

- **Where:** `book.md` lines 95-99.
- **Wrong:** "touch and IME". The editor's text fields take what an input method composed, and on Windows ImGui places
  the candidate list: `Strata/src/Strata/ImGui/ImGuiPlatform.h` 25-26 ("Text: typed characters (KeyTypedEvent), also
  those an input method composed. On Windows ImGui's own input method support places the candidate list…"),
  `ImGuiPlatform.cpp` 81 (`PlatformHandleRaw`). What is absent is composition text in *game* UI text fields (gameui
  inventory: "IME-less typed text", "nothing found"). Reword: "touch input; input-method composition in game UI".
- **Confirmed absent (keep):** nested prefabs and variants: `Scene/PrefabInstances.h` (`MakeTemplate` builds templates
  "without PrefabInstance components") and `prefab.create`'s description "Links of another prefab they had are
  replaced" (`StrataEditor/src/Editor/EditorAssetCommands.cpp` 1185). HLOD and origin rebasing: `Docs/Roadmap.md` 1693
  and 1706 ("Later"), `Docs/Releases/0.7.0.md` 386 ("Distant cells are not drawn at all"). Gameplay networking: correct, but the page must say the engine
  *has* network code, for editor automation only, in a Tooling layer games never link
  (`StrataTests/Architecture/Layers.json` 99-102).
- **Missing (add):** a prefab edit mode (`0.7.0.md` 380, 414); editing several scenes at once (`scene.loadAdditive` is
  "play mode only", `EditorSceneCommands.cpp` 458-460; the editor edits one scene plus a world's cells); panels torn out
  into windows of their own (`ImGuiPlatform.h`: "Single main viewport"; Roadmap 1715 "ImGui multi-viewports"); editor
  extensions written by a game project (panels are registered only by `EditorLayer.cpp` 350, and no header of
  `StrataScriptCore/Include/StrataScript/` reaches the editor); automating an exported game (Roadmap 1697; `0.7.0.md`
  414); exports for another platform, a macOS app bundle, signed exports and crash reports in shipped games
  (`0.7.0.md` 411-412; the export copies the runtime "next to the editor executable", `GameExport.h` 30); bodies that
  move between world cells (`0.7.0.md` 387).

### F14 (major, outside my four inventories) Wave 8's animation graph would falsify "blend trees, animation layers"

- **Where:** `book.md` lines 96-97; `outline-3.md` lines 90, 91, 97 (no animation page marked W8).
- **Problem:** `Docs/Roadmap.md` 1551 ("Tranche 2 is intended") and 1616-1621: `animation-graph`, "first claim on the
  tranche": "Blend1D, masked layers and state machines as nodes, authored by agents in `.stanimator` version 2". Nothing
  of it is on main at the pin (`git grep -i blend1d 822a7a46 -- Strata/src` finds nothing), so if tranche 2 runs, 0.8.0
  has blend trees (1D) and layers, `animation/state-machines`, `animation/blending` and `animation/limits` change, and
  the editor's animator drawer and Asset tab animation views change with them.
- **Proposal:** mark `animation/state-machines`, `animation/blending`, `animation/limits` (and `make/animation`) W8
  until tranche 2 is decided; keep "blend trees, animation layers" out of the not-in list until then. (For the
  animation critic to confirm.)

### F15 (minor) `automation/agents` is sourced from the wrong inventory; four automation concepts have no named home

- **Where:** `outline-4.md` line 97 (From: gamedev "How the editor makes games (internals)").
- **Problem:** automation concepts 2.1 (why automate an editor: embedded scripting, batch modes, remote control, UI
  automation), 2.12's tool-design half (tool count and token cost, compact definitions, describe tools), 2.13
  (accountability) and 2.14 (determinism for agents) are not named on any page; `automation/outside` is a tutorial and
  `automation/json-rpc` is about sockets. Gamedev's chapter 30 is about how the editor makes games in general, which
  `editor/program` already holds.
- **Proposal:** From of `automation/agents`: "automation 2.1, 2.12 (tool design), 2.13, 2.14; gamedev ch 30 (the agent
  path diagram)". It becomes the concept page the rest of part 19 builds on.

### F16 (minor) Four pages are sized below what their inventory measured

- **Where:** `outline-4.md` line 74 (`editor/imgui-backends`, M), line 79 (`editor/lists`, M), line 59 (`editor/undo`,
  L); `outline-1.md` line 29 (`make/editor-tour`, M).
- **Evidence:** `editor/imgui-backends`: inventory L with 5 diagrams; holds `ImGuiModule`, `ImGuiLayer`,
  `ImGuiPlatform`, `ImGuiRenderer`, the two shaders, frames in flight, dynamic textures, display modes; ten excerpts
  (editor-ui code #1-10) including the central `ImGuiRenderer.cpp:407-518`; rules 22-25. `editor/lists`: inventory L;
  holds the central `HierarchyView` walk, filtering, drop zones, `BeginMultiSelect`, the Content Browser grid,
  thumbnails per tile (code #25-29, figures 14-16). `editor/undo`: 22 feature rows of editor-core §1.3, two central
  algorithms (`UndoStack::Push`, `SceneEdit::ApplyEntities`), four approaches compared, the save point, ten excerpts
  (code #7-16). `make/editor-tour`: inventory L with about 18 screenshots.
- **Proposal:** `editor/imgui-backends` L (or split `editor/imgui-platform` M + `editor/imgui-renderer` L);
  `editor/lists` L; `editor/undo` XL; `make/editor-tour` L.

### F17 (minor) `editor/launcher-dialogs` mixes the launcher with the settings UI

- **Where:** `outline-4.md` line 85.
- **Problem:** editor-ui §1.11 (launcher of 895 lines, New Project, Open Sample, About, Export, Recover, Delete, New
  Script dialogs) and §1.12 (settings browser, pages generated from settings fields, custom pages for Graphics Quality,
  Collision Layers, Input Actions, `BindingCapture`, Preferences; concept 26 "Settings UIs from schemas") are two
  subjects; a reader who wants "how the Project Settings window is generated" does not look under "launcher".
- **Proposal:** split into `editor/launcher-dialogs` (M) and `editor/settings-windows` "Settings windows from schemas"
  (M), the latter with prerequisite `world/projects-settings`.

### F18 (minor) Wave 8 and my areas: no W8 marks needed, but four things must be re-checked at the pin move

- **Where:** `outline-4.md` lines 47, 68, 81, 84, 103, 142; `pipelines.md` "Moving the pin".
- **Findings:** the editor lane of wave 8 (placement by ray, the box ghost, frame-rate preferences, the Performance
  panel's pause) landed in step 0 (`Docs/Roadmap.md` 1564) and is on main at the pin, so `editor/placement`,
  `editor/scene-view` and `editor/status` need no W8, only "new in 0.8.0". But (a) tranche 3's `editor-ux` (Roadmap
  1630: "a mesh ghost in an overlay pass and a live material preview") may still land in 0.8.0 and change both pages;
  (b) the runtime perf log's `LocalShadowLights`/`LocalShadowViewsDrawn` columns (`GameRenderer.cpp` 181-200) belong to
  the `local-lights` stream (Roadmap 1624, tranche 2), so `worlds/measuring` and `reference/worlds-runtime` can change;
  (c) counts quoted in prose (151 or 153 commands, 63/46/42 kinds, 27 core commands and 18.6 KB in `automation/mcp`)
  move with every command a stream adds, and the pin tool reports only quotes that moved, not prose numbers;
  (d) `editor/inspectors`' natural examples (the sun's shadow-map line, reflections quality, the animator drawer) are
  wave 8 subjects.
- **Proposal:** write `editor/placement` and `editor/scene-view` last in wave 6 and list them for re-reading at the pin
  move; generate the perf-log column table (add "runtime perf-log columns" to `pipelines.md`'s generated list, from
  `FramePerfLog` and `GameRenderer::MakePerfLogColumns`, `GameRenderer.cpp` 178); state counts through the tests that pin them
  (`CommandJournalTests.cpp` 101-165, `EditorMcpToolsetsTests.cpp` 113) or through generated values, and add a check
  that flags prose numbers on pages whose reference tables changed; choose inspector examples outside wave 8 subjects.

### F19 (minor) `make/large-worlds` exports before `make/export`

- **Where:** `outline-1.md` lines 53 and 57.
- **Problem:** worlds-runtime chapter 2 ("Building a World in the Editor") ends with "export with Load Before Start";
  hands-on G3 "export and see the game wait for the ground". In reading order `make/export` comes four pages later.
- **Proposal:** keep the in-editor Play check in `make/large-worlds`, and move the exported-start check to
  `make/export` as a variation ("A world that waits for its ground").

### F20 (minor) The Asset tab has no named home

- **Where:** `outline-4.md` line 80 (`editor/inspectors`, From "editor-ui").
- **Problem:** editor-ui §1.7's `AssetInspector` ("Asset" tab: import settings as a draft with Apply/Revert, texture
  previews through display modes, model summary, audio waveform with Play/Stop, import outcome, a world's Cook button)
  and editor-core §1.13's `AudioPreview` are in no proposed chapter by name; editor-ui's chapter 10 lists only the
  material editor.
- **Proposal:** From of `editor/inspectors`: "editor-ui 'Inspectors generated from reflection' and the Asset tab
  (`AssetInspectorPanel`, `MaterialEditor`, `AnimationAssetViews`, `AudioPreview`)".

### F21 (minor) Processes are used throughout automation and the runtime, but no primer teaches them

- **Where:** `outline-1.md` line 71 (`basics/computer`).
- **Problem:** automation teaches pid plus process start time (§1.6, rule 7), exit codes (StrataCLI 0-5), stdio as
  MCP's transport, environment variables (`STRATA_SESSION_DIR`, `STRATA_EDITOR_TOKEN`), handles not inherited by child
  processes; the runtime and editor have exit codes (1/2/game's; 3 on bad arguments) and console vs GUI runs. Concept 2.2
  says "from nothing", but `basics/computer`'s scope names only CPU, memory, stack, heap and caches.
- **Proposal:** add "processes: pid, exit code, standard streams, environment, child processes" to `basics/computer`'s
  scope (or to F12's `basics/numbers` sibling), and list it as a prerequisite of part 19 and `worlds/runtime`.

### F22 (minor) `reference/editor` is sourced from one of three inventories that define editor options

- **Where:** `outline-4.md` line 143.
- **Problem:** the editor's command line is in editor-core §1.1 (`--commands`, `--frames`, `--no-gpu`,
  `--quit-after-commands`, exit code 3), editor-ui §1.2 (`--windowed`, `--ui-scale`, `--layout`, `--imgui-demo`,
  `--screenshot`) and automation §1.7 (`--no-automation`, `--automation-port`, `--idle-timeout`, `--headless`), all in
  `c_Arguments` (`EditorApplication.cpp` 63-82); the runtime's in `RuntimeApplication.cpp` (worlds-runtime §1.7).
- **Proposal:** From: "editor-ui, editor-core, automation"; generate both option tables from the `c_Arguments` arrays
  (add to `pipelines.md`'s generated list).

---

## Where each proposed chapter of the four inventories went

| Inventory chapter | Outline page | Note |
| --- | --- | --- |
| worlds-runtime 1 Why levels must stream | `worlds/why-streaming` | float precision needs F12 |
| worlds-runtime 2 Building a world (T, G) | `make/large-worlds` | export step: F19 |
| worlds-runtime 3 Grids, keys and layers | `worlds/grids` | |
| worlds-runtime 4 Sub-scenes and the frame budget | `world/sub-scenes` | row exists |
| worlds-runtime 5 The streamer | `worlds/streamer` | |
| worlds-runtime 6 Worlds meet physics and scripts | `worlds/physics-scripts` | capacity row: F6 |
| worlds-runtime 7 Editing a streamed world | `worlds/editing` | move: F1 |
| worlds-runtime 8 Shipping a game: the export (T+I) | `make/export` + `worlds/export` | split identity: F8; rows F6 |
| worlds-runtime 9 The runtime | `worlds/runtime` | prerequisites F1 |
| worlds-runtime 10 Measuring shipped games | `worlds/measuring` | columns F18 |
| worlds-runtime 11 Launcher, templates, samples | `start/first-game`, `make/samples`, `worlds/templates`, `editor/launcher-dialogs` | F7 |
| worlds-runtime 12 Reference | `reference/worlds-runtime` | |
| editor-core 1 The editor is a program | `editor/program` | |
| editor-core 2 Commands | `editor/commands` (+ `editor/tutorial-command`) | |
| editor-core 3 Undo and redo | `editor/undo` | size F16 |
| editor-core 4 Saving | `editor/saving` | after deferral: F4 |
| editor-core 5 Autosave and recovery (both) | `editor/recovery` | G side lost: F9 |
| editor-core 6 Trash and references (both) | `editor/trash-references` | G side lost: F9 |
| editor-core 7 Using prefabs (T, G) | `make/prefabs` | |
| editor-core 8 How prefab instances stay linked | `editor/prefab-instances` | |
| editor-core 9 Play mode and the Game view (both) | `editor/play-mode` + `editor/game-view` + `make/play-test-debug` | title clash F5 |
| editor-core 10 Time in steps (both) | `editor/stepping` | |
| editor-core 11 Commands that take frames | `editor/deferred-commands` | order F4; opening F7 |
| editor-core 12 Command scripts, batches, record and replay | `editor/command-scripts` | journal F3 |
| editor-core 13 Placing content | `editor/placement` | re-check F18 |
| editor-core 14 Editor camera and viewport state | `editor/camera-viewport` | overlap F5 |
| editor-core 15 Thumbnails and project pictures | `editor/thumbnails` | |
| editor-core 16 Command catalogue | `reference/commands` | |
| editor-ui 1 Tour (T, G, L) | `make/editor-tour` (M) | size F16 |
| editor-ui 2 What an editor is, immediate mode | `editor/immediate-mode` (+ `editor/program`) | F5 |
| editor-ui 3 Dear ImGui | `editor/imgui` | |
| editor-ui 4 Backends (L) | `editor/imgui-backends` (M) | size F16 |
| editor-ui 5 UI scale | `editor/ui-scale` | |
| editor-ui 6 Design system | `editor/design-system` | |
| editor-ui 7 Widget kit | `editor/widget-kit` | |
| editor-ui 8 Shell | `editor/shell` | |
| editor-ui 9 Lists (L) | `editor/lists` (M) | size F16 |
| editor-ui 10 Inspectors | `editor/inspectors` | Asset tab F20 |
| editor-ui 11 Scene view (XL) | `editor/scene-view` | F5, F18 |
| editor-ui 12 Game view | `editor/game-view` | F5 |
| editor-ui 13 Shortcuts | `editor/shortcuts` | |
| editor-ui 14 Status, toasts, idle | `editor/status` | |
| editor-ui 15 Launcher, dialogs, settings | `editor/launcher-dialogs` | split F17 |
| editor-ui 16 Instrument panels | `editor/instrument-panels` | |
| editor-ui 17 Testing a UI | `editor/ui-testing` | prereq `engineering/testing` F2 |
| editor-ui 18 Reference | `reference/editor` | sources F22 |
| automation 1 Driving the editor from outside (T, G) | `automation/outside` | track F11 |
| automation 2 Connecting an AI agent (T, G) | folded into `make/automated-playtests` | F10 |
| automation 3 Making a game as an agent (T, G, L) | folded into `make/automated-playtests` | F10 |
| automation 4 Recording and replaying | `automation/journal` | move F3 |
| automation 5 Sockets, framing, JSON-RPC | `automation/json-rpc` | processes F21 |
| automation 6 RPC server | `automation/rpc-server` | |
| automation 7 Security model | `automation/security` | |
| automation 8 Sessions, discovery, launching | `automation/sessions` | |
| automation 9 MCP server | `automation/mcp` | counts F18 |
| automation 10 Reference | `reference/automation` | |

Items of "Features", "Concepts" and "Rules" checked without a finding (each has a plausible single home): the World
asset, grid math, key packing and the index (`worlds/grids`); sources, hysteresis, view bias, total order, pins,
failures, adoption (`worlds/streamer`); `IWorldStreaming`, the SDK `World` class, prefetch before teleport
(`worlds/physics-scripts`); `GameWindowService` (`worlds/runtime`), `GameGraphicsService` (`image/quality-settings`);
every command group of editor-core §1.2.1 (`reference/commands`, plus the owning area's page); every editor-core rule
1-26, editor-ui rule 1-35, automation rule 1-28 and worlds-runtime rule 1-25 maps to one of the pages above; every
widget of editor-ui §1.4 (`editor/widget-kit`), every panel of §1.7 (with F20), the menu bar and toolbar
(`editor/shell`), the CJK fallback and icon font (`editor/design-system`; the `gpu/text` row of `book.md` line 73
should say the editor uses ImGui's own atlas, not `FontAtlasCache`, so `editor/design-system` is the home of its font
loading); sockets, framing, handshake, backpressure, graceful stop, sessions, pinning, launch readiness, MCP mapping and
toolsets (part 19).

## Smaller notes (not in the structured result)

- `editor/shortcuts` (M) and `editor/game-view` (M) are both about who gets the keyboard (`AcceptsEditShortcuts` depends
  on game input); a merged L page "The Game view, shortcuts and who owns the keyboard" would read better than two.
- StrataCLI's own structure (`StrataCLILib` for tests, stdout carries protocol and logs go to stderr, `ImageOutput`'s
  strict base64) is named on no page; `automation/mcp` (stdio discipline, automation rule 27) is the natural home.
- The Windows "Properties > Details" and OS file-browser pictures of worlds-runtime screenshot 11 cannot be taken by any
  capture kind of `pipelines.md`; they need a manual kind or a diagram.
- `editor/ui-testing` (part 18) builds on `engineering/testing` (part 20); both are written in wave 6, so only the
  prerequisite line is affected (F2).

## Not checked

- Inventories other than the four named were read only where an overlap had to be confirmed (assets, physics,
  scene-ecs, gamedev proposed chapters; foundation for atomic writes and floats; gameui for IME).
- `Docs/Plans/Wave8/` was not read; wave 8 status comes from `Docs/Roadmap.md` at the pin (lines 609-660, 1536-1636).
- Whether `light/area-lights`' "W8 (wave 8, stages 1 to 3)" matches the roadmap (which lists area lights under
  "Rendering after wave 8") is outside this lens.
