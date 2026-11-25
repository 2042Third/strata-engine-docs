# Outline 4: Scripting, Game UI, Large worlds and shipping, The editor's core, The editor's interface, Automation, Engineering, Capstone, Reference, Appendices

Columns as in [outline-1.md](outline-1.md).

## Part 15 — Scripting (`scripting`)

Tracks: E

Needs of the part: `basics/cpp-classes`, `basics/cpp-generic`, `basics/build`, `core/first-change`, `core/conventions`, `core/engine-modules`, `core/layers-registries`, `core/platform`, `core/files`, `core/debugging`, `world/ecs`, `world/systems`, `world/reflection`, `world/tutorial-component`, `assets/residency`, `physics/contacts-triggers`, `animation/time-events`

Writing, building and attaching scripts is in part `make`. This part is how the engine loads, calls, guards and
reloads them.

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `scripting/why-scripts` | Why game code lives outside the engine | C | M | E | `world/ecs` | scripting ch. 1 "Game code and the engine: why scripts"; how other engines script (interpreted, managed, visual, native) |
| `scripting/shared-libraries` | Shared libraries and binary interfaces | C | L | E | `basics/build`, `basics/cpp-classes`, `scripting/why-scripts` | scripting ch. 9 "Shared libraries and binary interfaces"; home of shared libraries and ABIs |
| `scripting/abi-sdk` | Inside the ABI and the SDK | I | L | E | `scripting/shared-libraries`, `basics/cpp-generic`, `world/reflection` | scripting ch. 10 (`ScriptABI.h`, the host table, descriptors, the SDK's thunks, registration, override detection; excerpts 1-13) |
| `scripting/loading` | Loading, calling and validating modules | I | L | E | `scripting/abi-sdk`, `core/platform`, `core/files` | scripting ch. 11 (`ScriptModule`, load modes and copies, validation, `Call`, `ScriptEngine`, the active engine) |
| `scripting/crash-containment` | Crash containment | I | L | E | `scripting/loading`, `core/conventions`, `core/debugging` | scripting ch. 12 without symbolization (hardware exceptions, SEH and signals, `CrashGuard` on Windows and POSIX, abort, what is not contained, exceptions against crashes, the watchdog; excerpts 16-19, figures 8 and 11) |
| `scripting/symbolization` | From an address to a file and line | I | M | E | `scripting/crash-containment` | scripting ch. 12, the symbolization half (concept 13, code #21: DbgHelp with inline frames, ELF `.symtab`, `dladdr`, the choice of the fault frame) |
| `scripting/script-system` | The script system | I | L | E | `scripting/loading`, `world/systems`, `assets/residency`, `physics/contacts-triggers`, `animation/time-events` | scripting ch. 13 "ScriptSystem" (instances, sync points, reconciliation, update order and dispatch lists, prefetching, contact, animation and UI events, asset pins; excerpts 26-29, figure 10); the code of the script lifecycle: the lifecycle and its callbacks have their home in `make/script-loop`, which track E does not read, so this page names the callbacks and their order before it shows their code |
| `scripting/hot-reload` | Hot reload | I | L | E | `scripting/script-system`, `core/files` | scripting ch. 14 (the watcher, copies, the reload protocol in the engine and in scenes, what survives, failures; excerpt 28, figure 9); home of hot reload |
| `scripting/host-api` | The host API: engine services behind a C table | I | L | E | `scripting/script-system`, `core/engine-modules`, `core/layers-registries` | scripting ch. 15, the internals half (`ResolveContext`, `HostCall`, validation and `ReportProblem`, the X-macro table `ST_SCRIPT_HOST_FUNCTIONS` in `Scripting/ScriptHostAPI.cpp` and its `static_assert`, call counters and Dist, services and layering; code #22-#24, concept 16) |
| `scripting/tutorial-host-function` | Tutorial: adding a host function and a callback | T | L | E | `scripting/host-api`, `world/tutorial-component`, `core/first-change` | scripting ch. 15, the tutorial half (hands-on E2-E3): the WindZone gets `Wind::GetStrength`, and a callback is appended to `StrataScriptClassDesc` |

## Part 16 — Game UI (`ui`)

Tracks: E

Needs of the part: `basics/math-geometry`, `world/scene-graph`, `gpu/binding`, `gpu/debug-drawing`, `gpu/text`, `draw/mirrors-camera-relative`, `input/devices-state`, `input/mouse-cursor`, `input/actions`, `scripting/script-system`

Making HUDs and menus is `make/hud` and `make/menus`. Testing game UI through editor commands (`ui.create`,
`ui.layout`, `ui.hitTest`, `input.click`) is `make/automated-playtests`.

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `ui/what-game-ui-does` | What a game UI must do | C | M | E | `world/scene-graph` | gameui ch. 1 (the problem, retained and immediate UIs compared and why the game UI is retained, a menu from components to pixels); home of the comparison |
| `ui/layout` | Rects, anchors and layout | I | L | E | - | gameui ch. 4 (the coordinate space, the scale formula, rect math, measure and arrange per axis, groups, grids, fit content, slider parts, clip rects) |
| `ui/contract` | The UI contract | I | M | E | `ui/layout` | gameui ch. 5 (signals, dirty marks, re-layout roots, the hierarchy and activity journals, the layout cache, validation, the tests that pin it) |
| `ui/input` | UI input | I | XL | E | `ui/layout`, `input/actions`, `input/mouse-cursor`, `scripting/script-system`, `basics/math-geometry` | gameui ch. 8 without input-field editing (hit grids, world-space rays, gestures and capture, widget states, navigation, UI actions and repeat, event dispatch, the script bridge) |
| `ui/text` | Text and text fields | I | M | E | `ui/layout`, `ui/input`, `gpu/text`, `input/devices-state` | gameui ch. 6 (how rects, sizes and overflow modes drive `ShapeText`) and input-field editing (concept 20, §1.9's input-field row, `GameUISystem.cpp` 557-747, code #18); glyph rendering is `gpu/text` |
| `ui/drawing` | Drawing the UI | I | XL | E | `ui/contract`, `ui/text`, `gpu/binding`, `gpu/debug-drawing`, `draw/mirrors-camera-relative` | gameui ch. 7 (`UIQuad`, slots and journals, indirection tables, uploads, runs, the shaders, world-space canvases on the GPU, the overlay registry) |

## Part 17 — Large worlds and shipping (`worlds`)

Tracks: E

Needs of the part: `basics/numbers`, `basics/data-formats`, `basics/color`, `core/windows-events`, `core/engine-modules`, `core/jobs`, `core/files`, `world/serialization`, `world/sub-scenes`, `world/projects-settings`, `assets/handles-meta`, `assets/residency`, `assets/packs-export`, `assets/robustness`, `image/quality-settings`, `physics/scale-streaming`, `scripting/abi-sdk`, `scripting/script-system`

Building a world in the editor is `make/large-worlds`, exporting a game `make/export`, measuring a shipped game
`make/performance`. Editing a streamed world is `editor/worlds`; the launcher's templates are `editor/projects`.

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `worlds/why-streaming` | Why levels must stream | C | M | E | `world/sub-scenes`, `assets/residency`, `basics/numbers` | worlds-runtime ch. 1 (the memory problem, the industry's approaches, Strata's choice, float precision and HLOD as open problems); home of the 20 km limit |
| `worlds/grids` | Grids, keys and layers | I | M | E | `assets/handles-meta`, `world/serialization`, `worlds/why-streaming` | worlds-runtime ch. 3 (`WorldData`, validation, grid math, key packing, file layout and derived handles, the index) |
| `worlds/streamer` | The streamer | I | L | E | `worlds/grids`, `core/jobs` | worlds-runtime ch. 5 (sources, wanted and keep sets, hysteresis, view bias, total order, concurrency, failures, adoption, idle cost, determinism tests) |
| `worlds/physics-scripts` | Worlds meet physics and scripts | I | L | E | `worlds/streamer`, `physics/scale-streaming`, `scripting/abi-sdk` | worlds-runtime ch. 6 (the World system, the prepared start, what a world reserves through the streamer, the cook's `MaxBodiesInRadius`, `IWorldStreaming` and the SDK's `World`, prefetch before teleport); capacity, growth and parking are `physics/scale-streaming` |
| `worlds/export` | Shipping a game: the export | I | M | E | `worlds/physics-scripts`, `assets/packs-export`, `world/projects-settings`, `core/files` | worlds-runtime ch. 8, the internals half (the export's state machine, up-front checks, "fail before writing", planning, world cooking at export, what the folder holds); the pack is `assets/packs-export`, the use side `make/export` |
| `worlds/game-identity` | A game's identity: the manifest, icons and platform files | I | M | E | `worlds/export`, `basics/data-formats`, `basics/color`, `assets/robustness` | worlds-runtime §1.8 and ch. 8 (manifest v5 and why it is untrusted, `ProjectGameInfo`, `GamePresentation`, saves keyed by the manifest's Name, `GameIcon`, `PEResources`, `DesktopEntry`, the Dock icon, signing after export) |
| `worlds/runtime` | The runtime | I | XL | E | `worlds/game-identity`, `core/engine-modules`, `core/windows-events`, `scripting/script-system`, `image/quality-settings` | worlds-runtime ch. 9 (`StrataRuntime` startup, options and exit codes, `GameRuntime`, `GameRenderer` fallbacks, the window and graphics services, headless runs, no tooling); home of scene switches in a shipped game (`GameRuntime` carries out `Game::LoadScene` with the `SceneLoader` of `world/sub-scenes`, which is the home of loading scenes; the editor's switches are `editor/play-mode`'s) |

## Part 18 — The editor's core (`editor`)

Tracks: E

Needs of the part: `basics/build`, `basics/data-formats`, `basics/math-rotations`, `basics/math-geometry`, `core/first-change`, `core/time`, `core/windows-events`, `core/layers-registries`, `core/jobs`, `core/files`, `world/systems`, `world/reflection`, `world/serialization`, `world/prefabs`, `world/sub-scenes`, `world/projects-settings`, `gpu/coordinates`, `gpu/frame-tour`, `gpu/readback-timing`, `assets/importing`, `assets/residency`, `assets/references`, `draw/bounds-culling`, `input/simulated`, `scripting/script-system`, `scripting/hot-reload`, `scripting/tutorial-host-function`, `worlds/streamer`

The editor without its UI: the code these pages explain is in `StrataEditorCore` (`StrataEditor/src/Editor/`). How the
editor is drawn is part `editor-ui`.

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `editor/program` | The editor is a program: core, UI and host | C | M | E | `world/systems`, `core/windows-events`, `core/layers-registries` | editor-core ch. 1 (`EditorContext`, the core and UI libraries, the frame order); home of what an editor is and why it is not the game |
| `editor/commands` | Commands | I | L | E | `world/reflection`, `basics/data-formats`, `editor/program` | editor-core ch. 2 "Commands: one API for people, agents and tests" and §1.2.1 (every command group); running one command from a terminal with `StrataCLI call`, parameters from a file (`@file`), which later pages of track E use for a step that has no menu or button (`style.md` §10); home of "commands are the API" |
| `editor/deferred-commands` | Commands that take frames | I | M | E | `editor/commands`, `core/time`, `assets/importing` | editor-core ch. 11 (`Defer`, the runner, poll rules, `FrameTimeRecorder`, `editor.wait` and `editor.perf`, `MayDefer`, `WaitsForAssets` and the asset-scan wait); opening scenes and projects is `editor/projects` |
| `editor/undo` | Undo and redo | I | XL | E | `editor/commands`, `world/serialization` | editor-core ch. 3 (`EditorAction`, `UndoStack`, `SceneEditTransaction`, `ApplyEntities`, merging, groups, save points; four approaches compared) |
| `editor/saving` | Saving without stalling | I | L | E | `editor/undo`, `editor/deferred-commands`, `core/files`, `core/jobs` | editor-core ch. 4 (`DocumentSaver`, `SettingsFileWriter`, atomic writes, save points under concurrent edits, the unsaved-changes guard, `AfterSaves`, `ResetScene` and `ReleaseProject`); home of "no silent data loss"; asking the person is `editor-ui/shell` |
| `editor/recovery` | Autosave and crash recovery | I | M | E | `editor/saving` | editor-core ch. 5 (the recovery journal, folding, discards, recovering as one undo step); the use side is `make/project-files` |
| `editor/projects` | Opening projects and scenes: templates, background loads and migration | I | L | E | `editor/saving`, `world/projects-settings`, `world/sub-scenes` | editor-core §1.9 (templates and `scene.new {template}`, samples as copies without `.strata`, recent projects, `BeginOpenProject`, `ProjectMigration`, opening scenes in the background and the read-only guard, `project.create`, `project.open`, `project.close`, `project.openSample`); worlds-runtime ch. 11 "The launcher, templates and samples" (the code side); it stands after `editor/saving` and `editor/recovery` because opening and closing a project release the edited scene (the unsaved-changes guard and `AfterSaves` are `editor/saving`'s, the recovery question `editor/recovery`'s) |
| `editor/trash-references` | The trash and references | I | M | E | `editor/undo`, `assets/references` | editor-core ch. 6 (asset file actions, reference checks, undo steps that check their preconditions) |
| `editor/prefab-instances` | How prefab instances stay linked | I | L | E | `editor/saving`, `world/prefabs` | editor-core ch. 8 (`PrefabSync`, `UpdatePrefabOverrides` in `CommitEdit`, baselines, catch-up by versions and hashes, apply and revert as undo steps); the data model is `world/prefabs` |
| `editor/play-mode` | Play mode: the running copy | I | L | E | `editor/deferred-commands`, `editor/undo`, `scripting/script-system` | editor-core ch. 9 (the running copy, edits while playing, the game shell, scene switches and quitting); home of Play and Simulate; the Game view's drawing is `editor-ui/game-view` |
| `editor/worlds` | Editing a streamed world | I | L | E | `editor/play-mode`, `editor/recovery`, `worlds/streamer` | worlds-runtime ch. 7 (`EditorWorld`, pins, dirty marks through the undo observer, re-celling, the two-phase save, the play copy, recovery, the cell map and overlay caching) |
| `editor/script-builds` | Building scripts from the editor: toolchains, CMake, diagnostics | I | L | E | `editor/play-mode`, `scripting/hot-reload`, `basics/build` | new; no inventory surveyed the editor's script builds: scripting §1.3 and §1.7, and `ScriptBuild*`, `ScriptToolchain*`, `ScriptProject*`, `ScriptSources*`, `ExternalEditor*` read at the pin (finding compilers, running CMake, diagnostics for the Problems panel, building before Play) |
| `editor/stepping` | Pausing, stepping and exact tests | I | M | E | `editor/play-mode`, `input/simulated` | editor-core ch. 10 "Time in steps" (fixed steps, time dilation, `play.step`); home of holds counted in fixed steps, `input.sequence` and `input.click` (`SimulatedInput`, `InputSequence`, `EditorInputCommands.cpp`); the simulated device and its merge rules are `input/simulated` |
| `editor/command-scripts` | Command scripts and batches | I | M | E | `editor/stepping` | editor-core ch. 12 (`--commands` scripts with `expect`, `bind` and `$ref`, `until`; `editor.batch`) |
| `editor/journal` | The activity journal and replays | I | M | E | `editor/undo`, `editor/command-scripts` | automation ch. 4 "Recording and replaying"; editor-core §1.11 (`CommandJournal`, `BuildReplayScript`, command origins and kinds, agent presence) |
| `editor/placement` | Placing content | I | M | E | `editor/undo`, `basics/math-geometry`, `draw/bounds-culling`, `editor/deferred-commands` | editor-core ch. 13 (raycasts against the scene, fallbacks, snapping, resting boxes, `asset.place` and the Scene view's drop sharing one request) |
| `editor/thumbnails` | Thumbnails | I | M | E | `editor/projects`, `gpu/frame-tour`, `gpu/readback-timing`, `assets/residency` | editor-core ch. 15 (caches keyed by content, offscreen rendering, readback without stalls, `ThumbnailCache::c_Version`, project pictures) |
| `editor/camera-viewport` | The editor camera and viewport state | I | L | E | `gpu/coordinates`, `basics/math-rotations`, `draw/bounds-culling`, `editor/commands` | editor-core ch. 14 (orbit, pan, dolly and fly, `FitBounds`, per-scene cameras, which camera each view uses, viewport settings); last before the tutorial so that `editor-ui/scene-view` builds on it |
| `editor/tutorial-command` | Tutorial: adding a command | T | L | E | `editor/undo`, `scripting/tutorial-host-function`, `core/first-change` | new; from editor-core ch. 2 and the Developer Guide's command conventions: the WindZone gets `wind.*` commands; it starts from the end state of `scripting/tutorial-host-function` |

## Part 19 — The editor's interface (`editor-ui`)

Tracks: E

Needs of the part: `basics/color`, `core/first-change`, `core/windows-events`, `core/engine-modules`, `core/profiling`, `world/reflection`, `world/projects-settings`, `gpu/resources-lifetimes`, `gpu/binding`, `gpu/frame-tour`, `gpu/readback-timing`, `gpu/text`, `image/quality-settings`, `physics/collision-layers`, `input/mouse-cursor`, `input/rebinding`, `ui/what-game-ui-does`, `worlds/streamer`, `worlds/export`, `editor/program`, `editor/projects`, `editor/saving`, `editor/recovery`, `editor/trash-references`, `editor/prefab-instances`, `editor/play-mode`, `editor/script-builds`, `editor/journal`, `editor/placement`, `editor/thumbnails`, `editor/camera-viewport`

How the editor is drawn: the code is in `StrataEditorUI` (`StrataEditor/src/UI/`, `StrataEditor/src/Panels/`,
`EditorLayer`) and in the engine's ImGui module (`Strata/src/Strata/ImGui/`) it draws with.

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `editor-ui/immediate-mode` | Why immediate mode | C | M | E | `editor/program`, `ui/what-game-ui-does` | editor-ui ch. 2 (why the editor's UI is immediate: tools against the game, Tooling layers, why Dear ImGui); what an editor is: `editor/program`; the general comparison: `ui/what-game-ui-does` |
| `editor-ui/imgui` | Dear ImGui from first principles | C | L | E | `core/windows-events`, `editor-ui/immediate-mode` | editor-ui ch. 3 (frames, windows, items, IDs, popups, docking; exercises in a scratch layer) |
| `editor-ui/imgui-backends` | ImGui backends | I | L | E | `editor-ui/imgui`, `core/engine-modules`, `gpu/binding`, `gpu/resources-lifetimes`, `basics/color` | editor-ui ch. 4 "Plugging ImGui into an engine" (`ImGuiModule`, `ImGuiLayer`, `ImGuiPlatform`, `ImGuiRenderer`, the two shaders, frames in flight, dynamic textures, texture display modes) |
| `editor-ui/ui-scale` | Pixels, points and UI scale | I | M | E | `editor-ui/imgui-backends` | editor-ui ch. 5 (content scale, `ToUIScale`, even base sizes, fonts' DPI, Preferences > Interface, `--ui-scale`) |
| `editor-ui/design-system` | The design system: theme, fonts, icons | I | L | E | `editor-ui/ui-scale`, `gpu/text` | editor-ui ch. 6 (Bedrock tokens, `ApplyTheme`, the font atlas and the icon merge, the CJK fallback, the `Icons.h` generator, the source scans); home of the editor's font loading (ImGui's own atlas, not `FontAtlasCache`) |
| `editor-ui/widget-kit` | The widget kit | I | L | E | `editor-ui/design-system` | editor-ui ch. 7 (the anatomy of a widget, chips and the chip strip, pills, modals, the item probe) |
| `editor-ui/shell` | The editor shell: host, layer, docking and panels | I | XL | E | `editor-ui/widget-kit`, `editor/saving` | editor-ui ch. 8 and §1.2 (`EditorApplication`, `EditorHost`, `EditorShell`, `EditorLayer`'s frame, the panel registry, the default layout and its versions, menus and toolbar); the anatomy of editor-ui ch. 1 "A tour of the editor"; home of asking the person (modals, the re-ask rule, `DrawDiscardQuestion`) |
| `editor-ui/lists` | Lists that scale | I | L | E | `editor-ui/shell`, `editor/thumbnails` | editor-ui ch. 9 (`HierarchyView` and `AssetBrowserView`, core code drawn here; `ImGuiListClipper`, multi-select, drop zones, thumbnails per tile, background tables) |
| `editor-ui/inspectors` | Inspectors from reflection | I | XL | E | `editor-ui/shell`, `editor/prefab-instances`, `world/reflection` | editor-ui ch. 10 "Inspectors generated from reflection" and the Asset tab (`AssetInspectorPanel`, `MaterialEditor`, `AnimationAssetViews`, `AudioPreview`); examples chosen outside wave 8 subjects |
| `editor-ui/scene-view` | The Scene view | I | XL | E | `editor-ui/shell`, `editor/camera-viewport`, `editor/placement`, `gpu/frame-tour`, `gpu/readback-timing` | editor-ui ch. 11 (`ViewportPanel`, toolbar and chips, async picking, ImGuizmo and `TransformDrag`, debug view legends, the drop and its ghost, the agent chip, canvas mode); home of picking and gizmos |
| `editor-ui/game-view` | The Game view, shortcuts and who owns the keyboard | I | L | E | `editor-ui/scene-view`, `editor/play-mode`, `input/mouse-cursor` | editor-ui ch. 12 "The Game view and who owns input" and ch. 13 "Shortcuts and focus" (resolution modes, letterboxing, `Input::SetViewport`, cursor lock, Shift+F1, Play and Stop tab switching; global and focused shortcuts and their guards) |
| `editor-ui/status` | Status bar, toasts and idle throttling | I | L | E | `editor-ui/shell`, `core/profiling` | editor-ui ch. 14 (pills and hysteresis, toasts, work time against frame rate, `Editor.FrameRate`); home of notifications, their model (`EditorNotifications`) and their drawing |
| `editor-ui/launcher-dialogs` | Launcher and dialogs | I | L | E | `editor-ui/shell`, `editor/projects`, `editor/recovery`, `editor/trash-references`, `worlds/export` | editor-ui §1.11 (the Welcome panel, New Project, Open Sample, About, Export, Recover Unsaved Changes, Delete and New Script dialogs) |
| `editor-ui/settings-windows` | Settings windows from schemas | I | L | E | `editor-ui/inspectors`, `world/projects-settings`, `physics/collision-layers`, `input/rebinding`, `image/quality-settings` | editor-ui §1.12 and concept 26 (the settings browser, pages generated from settings fields, the custom pages for Graphics Quality, Collision Layers and Input Actions, `BindingCapture`, Preferences) |
| `editor-ui/instrument-panels` | Instrument panels | I | L | E | `editor-ui/lists`, `editor-ui/status`, `editor/journal`, `editor/script-builds`, `worlds/streamer` | editor-ui ch. 16 (Console, Problems, Activity, Streaming and Performance: what each shows and how each keeps its cost low); home of the Activity panel's drawing |
| `editor-ui/ui-testing` | Testing a UI without a screen | I | L | E | `editor-ui/shell`, `core/first-change` | editor-ui ch. 17 (`ImGuiHarness`, `FakeEditorHost`, probes, clicks over frames, source scans, panel perf tests) |
| `editor-ui/tutorial-panel` | Tutorial: adding a panel | T | L | E | `editor-ui/ui-testing` | new; from editor-ui ch. 7 and ch. 8: a panel registered through `EditorPanelRegistry`, drawn with the widget kit and tested without a screen |

## Part 20 — Automation and AI agents (`automation`)

Tracks: E

Needs of the part: `basics/data-formats`, `basics/threads`, `core/jobs`, `core/platform`, `core/files`, `editor/deferred-commands`, `editor/journal`

Track E only. Driving the editor from a terminal is `make/commands`; making a game with an agent is
`make/with-an-agent`.

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `automation/agents` | How the editor makes games with agents | C | M | E | `editor/journal` | automation concepts 2.1 (why automate an editor), 2.12 (the design of tools), 2.13 (accountability), 2.14 (determinism for agents); gamedev ch. 30 (the agent path diagram) |
| `automation/json-rpc` | Sockets, framing and JSON-RPC | C | L | E | `basics/data-formats`, `basics/threads`, `core/platform`, `automation/agents` | automation ch. 5 (loopback TCP, non-blocking I/O and poll, newline framing, `JsonLineReader`, JSON-RPC 2.0 and Strata's error codes) |
| `automation/rpc-server` | The editor's RPC server | I | XL | E | `automation/json-rpc`, `editor/deferred-commands`, `core/jobs` | automation ch. 6 (the network thread, the request queue, responders, `ProcessRequests`, backpressure, limits, orderly close and graceful stop, how commands become methods in `EditorAutomation`) |
| `automation/security` | The security model | I | XL | E | `automation/rpc-server`, `core/files` | automation ch. 7 (the threat model of loopback, tokens, HMAC challenge and response, the server's proof first, limits before authentication, private session files, the untrusted pointer, pid reuse and TOCTOU-safe file handling) |
| `automation/sessions` | Sessions, discovery and launching | I | L | E | `automation/security` | automation ch. 8 (session files, discovery order, pinning, `LaunchEditor` readiness by progress, the idle timeout, shutdown order) |
| `automation/mcp` | StrataCLI and its MCP server | I | L | E | `automation/sessions` | automation ch. 9 (the MCP protocol, commands mapped to tools, results and images, toolsets and the token budget, compact definitions, descriptions written for agents); StrataCLI's structure (`StrataCLILib`, stdout for the protocol and stderr for logs, `ImageOutput`'s strict base64) |

## Part 21 — Building, testing and releasing the engine (`engineering`)

Tracks: E

Needs of the part: `basics/numbers`, `core/first-change`, `core/layers-registries`, `core/profiling`, `world/reflection`, `gpu/shaders`, `gpu/first-triangle`, `gpu/frame-tour`, `scripting/abi-sdk`, `editor/command-scripts`

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `engineering/building` | Building Strata | H | M | E | `core/first-change` | build-test ch. 2 (every preset, configuration and option, where binaries land, when to configure again, the validation layer); the short source build is `core/first-change` |
| `engineering/cmake` | Inside Strata's CMake | I | L | E | `core/layers-registries` | build-test ch. 3 (targets and usage requirements, `strata_add_layer_libraries`, `strata_layer_link`, the link closure, the linker map, `LayerLibraries.json`, optional modules and `ST_WITH_*`) |
| `engineering/flags-portability` | Compiler flags, compile time and portability | I | L | E | `engineering/cmake`, `basics/numbers` | build-test ch. 4 (the warning policy, instruction sets, precompiled headers, header weight, compiler caches, three compilers and their traps, CompatLint); home of FMA contraction and floating-point determinism |
| `engineering/third-party` | Third-party code and pinned tools | I | L | E | `engineering/flags-portability` | build-test ch. 5 (submodules, the vendor wrapper, box3d and zstd, licenses and notices, the Slang pin and its fetch) |
| `engineering/generated-code` | Generated code: shaders, embedded files, version stamps and committed generators | I | L | E | `engineering/cmake`, `gpu/shaders` | build-test ch. 6, §1.4 and §1.13 (`strata_add_shaders`, StrataShaderTool's SPIR-V patch, the registry, `strata_embed_file`, version and commit headers; `GenerateBlueNoise.py`, `FitFilmic.py`, `FitAOMultiBounce.py`, `GenerateAreaTable.py`, `GenerateWhiteBalance.py`, `GenerateBrandAssets.py`, `GenerateShowcase*.py`, `GenerateIslandTerrain.py`, `GenerateIconHeader.py`, the feature test's `GenerateAssets.py`); render-image §1.11 |
| `engineering/testing` | Testing an engine | C | M | E | - | build-test ch. 7, the concept half (test kinds, determinism and flakiness, regression tests that fail without their fix, coverage by construction, sweeps as an idea); home of testing |
| `engineering/test-program` | Inside StrataTests | I | L | E | `engineering/testing`, `engineering/cmake` | build-test ch. 7, the program half, and §1.6 (`TestMain`, helper modes, the fake CMake and editor, `CoreShards.json` and `Testing.Shards`, labels, fixtures, locks, `SelectSweepOffsets` and `StrataTests.Fuzz`, `TestCrashReporter.cpp`, test helpers; excerpts 19-23); home of corruption sweeps and fuzzing |
| `engineering/test-kinds` | GPU, end-to-end and package tests | I | L | E | `engineering/test-program`, `gpu/first-triangle`, `editor/command-scripts` | build-test ch. 8 (`GPUContext`, validation errors, readback: writing a GPU test is `gpu/first-triangle`'s, this page is the suites; `EndToEnd` suites, the editor's smoke and export chains, sample runners, package and install tests) |
| `engineering/feature-test` | The feature test | I | M | E | `engineering/test-kinds`, `world/reflection`, `scripting/abi-sdk` | build-test ch. 9 "The feature test: coverage by construction" (the project, the coverage checks, the runners, extending it) |
| `engineering/perf-lab` | Measuring performance honestly: noise, percentiles, budgets and the perf lab | I | L | E | `engineering/test-kinds`, `core/profiling` | build-test ch. 10 and concept 21; foundation concept 20 (benchmark statistics, noise, budgets, confirmed checks, results files, the canary, the ratchet, provisional metrics, PerfStability, PerfLock, A/B and layout effects); home of "measured on the reference machine" |
| `engineering/look-dev` | The look-dev harness | I | M | E | `engineering/test-kinds`, `gpu/frame-tour` | build-test ch. 11 (capture, compare, signed images, metrics, the harness's own tests) |
| `engineering/ci` | Continuous integration | I | L | E | `engineering/flags-portability`, `engineering/test-program` | build-test ch. 12 (the CI matrix, caches and eviction, shader steps, annotations, the Dist job, `ci/<name>` branches, CIStatus) |
| `engineering/releasing` | Packaging and releasing | I | L | E | `engineering/ci` | build-test ch. 13 (the install layout, the marker, CPack, versions, the release workflow and procedure, verifying an archive) |
| `engineering/contributing` | The review checklist and the way a change lands | H | M | E | `engineering/ci`, `engineering/feature-test` | build-test ch. 14 (the golden rules, the pre-commit checklist, verification in a clean worktree, commit hygiene, the third-party rule) |

## Part 22 — Capstone: one feature through every layer (`capstone`)

Tracks: E

Needs of the part: `core/reading-code`, `world/tutorial-component`, `gpu/debug-drawing`, `physics/world-step`, `scripting/tutorial-host-function`, `editor/tutorial-command`, `editor-ui/inspectors`, `engineering/feature-test`, `engineering/perf-lab`, `engineering/ci`, `engineering/contributing`

The WindZone of `world/tutorial-component`, which `scripting/tutorial-host-function` and `editor/tutorial-command`
extend, becomes a feature that lands the way every change of Strata lands.

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `capstone/plan` | Capstone I: designing a feature the way Strata does | T | L | E | `world/tutorial-component`, `scripting/tutorial-host-function`, `editor/tutorial-command`, `engineering/contributing`, `core/reading-code` | new; the book's running example for track E grown into a feature: its layers, its registries and the rules that apply; a trace exercise: one click in the Scene view followed to a pixel, with the method of `core/reading-code` |
| `capstone/build` | Capstone II: from component to pixel | T | L | E | `physics/world-step`, `gpu/debug-drawing`, `editor-ui/inspectors`, `capstone/plan` | new; the system's forces on bodies, a debug gizmo, an inactive reason in the inspector, the script API and the command, in one change |
| `capstone/land` | Capstone III: tests, the feature test, a budget, the review and CI | T | L | E | `capstone/build`, `engineering/feature-test`, `engineering/perf-lab`, `engineering/ci` | new; the change made ready to land: unit tests, the feature test, a perf budget, the review checklist and a `ci/<name>` branch |

## Part 23 — Reference (`reference`)

Tracks: -

Needs of the part: `make/first-script`, `basics/programming-3`, `basics/build`, `basics/data-formats`, `world/what-a-world-is`, `world/projects-settings`, `gpu/frame-tour`, `assets/handles-meta`, `physics/bodies-colliders`, `animation/state-machines`, `input/actions`, `ui/layout`, `worlds/runtime`, `editor/commands`, `editor-ui/shell`, `automation/json-rpc`, `engineering/perf-lab`

Generated from the engine, or parsed from its sources and checked by a tool ([pipelines.md](pipelines.md)). Never
hand-typed tables of things the engine can list. Reference pages are on no track: readers reach them by links and
search.

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `reference/script-api` | The complete script API | R | XL | - | `basics/programming-3` | scripting ch. 16; `StrataScriptHostAPI` and `StrataScriptClassDesc` (`ScriptABI.h`), the SDK headers of `StrataScriptCore/Include/StrataScript/`, `ST_SCRIPT_CLASS` and `ST_SCRIPT_FIELD`; `ST_SCRIPT_HOST_FUNCTIONS` is in the engine (`Strata/src/Strata/Scripting/ScriptHostAPI.cpp`), not in the SDK |
| `reference/commands` | The command catalogue | R | XL | - | `editor/commands`, `basics/data-formats` | editor-core ch. 16; the editor's command registry (`editor.commands`: name, description, parameter schema, kind); may be split into one page per command group |
| `reference/components` | Components and their properties | R | XL | - | `world/what-a-world-is` | the component registry (`component.list`; defaults from a dump, inactive reasons parsed from the sources); scene-ecs, gameui, physics, animation, audio-input |
| `reference/settings` | Project settings and preferences | R | L | - | `world/projects-settings` | the settings sections (`project.settings` on an empty project, `preferences.get`, the schemas' defaults); scene-ecs, render-image |
| `reference/scene` | Scene, reflection and settings: types, flags, formats, limits | R | M | - | `basics/programming-3` | scene-ecs ch. 12 (the Scene and Entity API, `ComponentFlags`, `PropertyType` and `PropertyFlags`, `SettingsField` types, file formats, the `c_Max*` limits, the 512 KiB settings cap), generated from the headers |
| `reference/assets` | Asset types, file formats, importer versions, budgets and statistics | R | M | - | `assets/handles-meta` | assets ch. 14 "Reference"; `AssetResidencyBudgets`, `AssetManagerStats`; importer versions parsed from each importer's `GetVersion` |
| `reference/renderer` | Passes, bindings, switches, statistics, debug views, quality rows, device requirements | R | L | - | `gpu/frame-tour` | the references of render-core, render-scene, render-direct, render-indirect and render-image; `renderStats` keys (`EditorStateCommands.cpp`), `SceneRendererSpecification` and `SceneRendererStats` fields (`SceneRenderer.h`), fallback textures and samplers; the renderer's rules in one hand-checked table, each linking its home page |
| `reference/physics` | Physics reference | R | M | - | `physics/bodies-colliders` | physics ch. 13 |
| `reference/animation` | Animation reference | R | M | - | `animation/state-machines` | animation ch. 15 |
| `reference/audio-input` | Audio and input reference | R | M | - | `input/actions` | audio-input ch. 14 |
| `reference/ui` | Game UI reference | R | M | - | `ui/layout` | gameui ch. 10 |
| `reference/worlds-runtime` | Worlds, export, runtime options, manifest | R | M | - | `worlds/runtime` | worlds-runtime ch. 12 (`.stworld`, `.stgame` v1-v5, `GraphicsOptions.json`, `world.*` and `project.*` commands, the runtime's command line from `c_Arguments` in `StrataRuntime/src/RuntimeApplication.cpp`); the runtime perf log's columns, generated from `FramePerfLog` and `GameRenderer::MakePerfLogColumns` |
| `reference/editor` | Editor reference: panels, shortcuts, arguments | R | M | - | `editor-ui/shell` | editor-ui ch. 18, editor-core §1.1, automation §1.7; the option table generated from `c_Arguments` in `StrataEditor/src/EditorApplication.cpp` |
| `reference/automation` | Protocol, errors, CLI | R | M | - | `automation/json-rpc` | automation ch. 10 |
| `reference/core` | Core utilities | R | M | - | `basics/programming-3` | foundation ch. 13 "Core utilities reference" |
| `reference/build` | CMake options, presets, test labels, tools | R | S | - | `basics/build` | build-test ch. 15 "Tools reference" |
| `reference/performance` | Measured costs and their budgets | R | M | - | `engineering/perf-lab` | new; every perf budget in one table: generated from `StrataTests/Perf/Budgets.json`, with the catalogue of perf suites (build-test ch. 10); names the reference machine the values were measured on, as `Docs/DeveloperGuide.md` ("Perf tests") states it; why budgets are measured there is `engineering/perf-lab`'s |
| `reference/game-makers` | Cheat sheet for game makers | R | M | - | `make/first-script` | gamedev ch. 31 (components, commands, the SDK, runtime options and the project file, for game makers) |
| `reference/notation` | Conventions and notation | R | M | - | - | new; axes, handedness, units, matrix order, depth and color spaces and the symbols of the rendering parts in one place, checked against `gpu/coordinates` and `basics/math-matrices` |
| `reference/glossary` | Glossary | R | XL | - | - | all inventories' glossaries (about 1,590 terms before merging); one definition list, without a table of contents |
| `reference/term-index` | Index of terms and engine identifiers | R | XL | - | - | new; generated from the glossary's home pages and the excerpt fences' symbols, so a reader finds the page that defines a name; not `reference/index`, which is the part's generated map |
| `reference/figures` | Index of figures and their recipes | R | L | - | - | generated from the figure manifests; names the GPU of the machine that rendered them |

## Part 24 — Appendices (`appendix`)

Tracks: -

Needs of the part: `basics/trees-graphs`, `basics/math-geometry`, `core/time`, `automation/json-rpc`

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `appendix/not-in-strata` | What Strata does not do, and how engines do it | C | L | - | - | the "absent" notes of all inventories; the curricula checklist; `Docs/Releases/0.8.0.md` "Known issues" and "Not in this release" |
| `appendix/networking` | Networking for games, in general | C | L | - | `automation/json-rpc`, `core/time` | curricula; Strata has no gameplay networking: its network code serves editor automation only, in a Tooling layer games never link |
| `appendix/game-ai` | Game AI in general: steering, pathfinding, navigation meshes and behaviour trees | C | L | - | `basics/trees-graphs`, `basics/math-geometry` | new; how engines do navigation and behavior, which Strata leaves to scripts (curricula 1.13); the OpenWorld sample's `Wander.cpp` as the one example |
| `appendix/math-cheatsheet` | Math cheat sheet | R | M | - | - | the basics pages; a "how to read the symbols" table (Σ, ∫, ‖v‖, ·, ×, θ) that names the page teaching each symbol |
| `appendix/history` | Which release brought what | R | M | - | - | `Docs/Releases/` of the engine |
| `appendix/further-reading` | Further reading | R | M | - | - | research/curricula sources, per part |
| `appendix/credits` | Credits and licenses | R | S | - | - | the book's copyright statement, "All rights reserved" with its two exceptions (holder and year from `site.json`); the permission for the book's code, in the reader's words, taught here; of the engine's own terms only what its repository says at the pin; the credits: sample assets shown in figures (`CREDITS.md`), with the full entry of the Open World sample's fox (its CC BY 4.0 parts, with their two copyright lines and the link to the Khronos commit), the vendored libraries a page quotes with their licenses and a link to `third-party-notices.txt`, quoted sources; no license text of its own |
