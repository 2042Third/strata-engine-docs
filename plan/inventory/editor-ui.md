# Inventory: the editor's interface (ImGui, widget kit, panels, inspectors, viewport, shortcuts)

Surveyed at `main` 822a7a46 (2026-11-10). Scope: `Strata/src/Strata/ImGui/` (4 headers, 4 sources, ~1,330 lines),
`StrataEditor/src/UI/` (34 headers and sources plus the generated `Icons.h`), `StrataEditor/src/Panels/` (30 files),
`StrataEditor/src/EditorLayer.{h,cpp}`, `EditorHost.h`, `EditorApplication.cpp`, and the editor-core files the UI is built
on where they carry UI ideas (`Editor/HierarchyView`, `AssetBrowserView`, `EditorCamera`, `EditorViewport`,
`TransformEdit`, `EditorNotifications`, `EditorFrameRate`, `EditorInterface`, `ThumbnailCache`). Total of the area proper:
about 35,000 lines, of which 4,254 are the generated icon table.

Documents referred to below by short names:

- **DG** = `Docs/DeveloperGuide.md`: "Editor" (line 2730), "Editor UI rules" (2738), "Hierarchy, Content Browser and
  thumbnails" (3260), "Inspectors" (3282), "Shortcuts and editor status" (3346), "Viewport state" (3464), "Templates and
  recent projects" (3483), "Launcher" (3508), "Placing content" (3525), "Viewport panel" (3568), "View commands" (3610),
  "Materials" (3692), "Project settings" (1146), "Collision layers" (1292), "Input actions" (1442), "Preferences" (1581),
  "Quality settings" (4009).
- **AR** = `Docs/Architecture.md`, "Editor" (line 3217; the layer table at 3219-3237, the UI paragraph 3239-3345).
- **MS** = `Docs/Manual/Settings.md` ("Project Settings" 13, "Preferences" 132); **MG** = `Docs/Manual/GameView.md`
  ("The Scene view and the Game view" 7, "Resolution" 28, "Input and the mouse" 36, "Pausing and stepping" 42).
- **R0.x** = `Docs/Releases/0.x.0.md`; **RM** = `Docs/Roadmap.md` (wave 8 editor lane at 1564).

Third-party pieces: Dear ImGui **1.92.9, docking branch** (`Strata/vendor/imgui`, core only, built with
`IMGUI_DISABLE_OBSOLETE_FUNCTIONS`, `Strata/vendor/CMakeLists.txt:89-100`), ImGuizmo (`vendor/ImGuizmo`, linked only by
`StrataEditorUI`), nativefiledialog-extended (`vendor/nfd`), fonts Inter, JetBrains Mono (OFL) and Lucide 1.47.0 (ISC)
committed in `StrataEditor/Resources/Fonts`.

---

## 1. Features

### 1.1 The engine's ImGui module (`Strata/src/Strata/ImGui`, layer "ImGui", Tooling: games contain no ImGui)

| Feature | Where | Doc / release |
| --- | --- | --- |
| **ImGuiModule**: the engine module of Dear ImGui; needs Graphics and a presentable window, pushes `ImGuiLayer` as the top overlay, draws every frame's UI in the `Editor.UI` profile stage: `Begin`, every layer's `OnImGuiRender`, `Renderer::PrepareBackBuffer`, `End` into the back buffer | `ImGuiModule.h:113-144`, `ImGuiModule.cpp:25-64` | AR 3219 (table); `StrataTests/Architecture/Layers.json:105-111` |
| **ImGuiLayer**: owns the ImGui context; enables keyboard navigation and docking; persists layout to an ini file (or none); blocks mouse/keyboard events ImGui wants (`WantCaptureMouse/Keyboard`); rebuilds the style for the UI scale on attach, on `WindowContentScaleEvent` and when pixels-per-unit change | `ImGuiLayer.h:33-96`, `ImGuiLayer.cpp:36-149` | AR 3239 |
| **UI scale**: content scale less what point-based window coordinates apply already (`ToUIScale`), times the person's factor (`SetContentScaleFactor`), or an override (`--ui-scale`), clamped to [0.5, 4]; style rebuilt from unscaled defaults each time; fonts scaled by `ImGuiStyle::FontScaleDpi` | `ImGuiLayer.cpp:157-232` | DG 2738 (sizes bullet); R0.4 ("On Retina displays the editor's UI has its intended size") |
| **Style callback**: `ImGuiStyleCallback(ImGuiStyle&, float scale)` receives ImGui's dark style unscaled; editor installs `UI::ApplyTheme` | `ImGuiLayer.h:20-22,54-55` | AR 3239 |
| **ImGuiPlatform** (platform backend written by Strata, fed by the window's events, no polling): keys by keyboard layout name, both keys of each modifier counted and queued before the key, a release queued as the key its press was queued as, typed text incl. IME, mouse moves/buttons (5)/wheel (2 axes), leaving the window, focus loss releasing everything, cursor shapes only while the cursor mode is Normal and only when changed, system clipboard, delta time with a first-frame and minimum step | `ImGuiPlatform.h:164-221`, `ImGuiPlatform.cpp` (OnKey 162-184, NewFrame 186-204, UpdateCursorShape 206-221, ToImGuiKey 239-301) | R0.3 line 160 (keyboard layouts, cursor shapes, clipboard) |
| **ImGuiRenderer** (renderer backend on NVRHI written by Strata): ImGui 1.92's dynamic texture protocol (`ImGuiBackendFlags_RendererHasTextures`: font atlas pages created/updated/destroyed on request), `RendererHasVtxOffset`, user textures as `nvrhi::ITexture*` in `ImTextureID`, one pipeline per framebuffer format, binding sets cached per texture and filter and dropped after 8 unused frames, a ring of up to 8 mapped vertex/index buffer sets reused once an event query says the GPU is done, scissor per draw command, standard draw callbacks (reset, linear/nearest sampler) | `ImGuiRenderer.h:55-126`, `ImGuiRenderer.cpp:126-518` | none (code comments only) |
| **Texture display modes** (`ImGuiTextureDisplay`: Direct, EncodeSRGB, Grayscale, NormalXY) chosen from a texture's format, set through a draw callback whose *user data address* identifies it | `ImGuiRenderer.h:24-53`, `ImGuiRenderer.cpp:73-119`; shader `Strata/shaders/ImGui.frag.slang:26-46` | DG 3282 (last part: "draw textures in UI code through `UI::TextureImage`") |
| **Shaders** `ImGui.vert` (pixel to NDC by scale/translate push constants) and `ImGui.frag` (texel times vertex color, display conversions) | `Strata/shaders/ImGui.vert.slang` (53 lines), `ImGui.frag.slang` (68 lines; note it includes `Common.slang` twice, lines 1 and 3) | AGENTS "Shaders" |
| GPU stage `GPU.ImGui` registered lazily by the first program that draws UI | `ImGuiLayer.cpp:140-148` | DG "GPU timing" (not read) |

### 1.2 Editor application wiring and the host boundary

| Feature | Where | Doc / release |
| --- | --- | --- |
| Two libraries: `StrataEditorCore` (no UI) and `StrataEditorUI` (ImGui UI: `UI/`, `Panels/`, `EditorLayer`, `EditorHost.h`); the executable is one file | `StrataEditor/CMakeLists.txt:1-60` | DG 2730; AR 3219 |
| Fonts and `ThirdPartyNotices.md` embedded with `strata_embed_file` | `StrataEditor/CMakeLists.txt:52-60` | DG 2738 (fonts bullet) |
| `EditorApplication` installs the Bedrock theme (`SetStyleCallback(UI::ApplyTheme)`), loads the fonts, starts the CJK fallback read, applies `--ui-scale`, keeps the layout in `<user data>/EditorLayout.ini` unless `--layout` or `--frames` | `EditorApplication.cpp:215-240, 325-344`; options table `c_Arguments` 63-79 | AR 3219 |
| **EditorHost**: the only way `EditorLayer` reaches the application (close, exit code, frame count, time, uptime, GPU info, window title/size/focus, UI scale and factor, frame rate cap, last frame work time, screenshots); implemented by `ApplicationEditorHost` and faked by tests | `EditorHost.h:17-64`, `EditorApplication.cpp:127-213` | DG 2730; AR 3239 |
| **EditorShell**: what panels may ask of the window (dialogs, unsaved-changes question, release/quit questions, panels, activity, asset, rename, environment, automation state), implemented by `EditorLayer` | `UI/EditorShell.h:83-163` | DG 2738 (panels bullet); AR 3239 |
| Command-line options that matter to the UI: `--windowed` (1600x900), `--ui-scale`, `--layout`, `--imgui-demo`, `--screenshot`, `--frames`, `--commands`, `--headless` | `EditorApplication.cpp:63-79` | DG "Repository layout" (not read) |

### 1.3 The look: theme, fonts, icons, brand

| Feature | Where | Doc / release |
| --- | --- | --- |
| **Bedrock palette**: 16 named sRGB tokens (Basalt, Shale, Slate, Flint, Seam; Limestone, Ash, Dust; Ochre, Sandstone, Rust, Umber; Malachite, Azurite, Sulfur, Cinnabar) | `UI/Theme.h:10-34`, `Theme.cpp:16-58` | DG 2738 |
| **ThemeColors**: meanings (accent and its states, selection hover, success/info/warning/error, axis X/Y/Z, play states, text levels, chrome/panel/raised/control/border/overlay) | `Theme.h:36-73`, `Theme.cpp:66-90` | DG 2738 |
| **ApplyTheme**: a role table mapping every `ImGuiCol_` to a token and alpha, `static_assert` that it covers `ImGuiCol_COUNT` (an ImGui upgrade with new colors fails the build), even base sizes scaled by `ScaleAllSizes`, square windows, 4 px rounding, no dock-node close/menu buttons, Ochre tab overline | `Theme.cpp:92-270` | DG 2738 |
| Token list for tests (`GetThemePaletteTokens`), `ToColorU32`, `WithAlpha` | `Theme.h:78-97` | — |
| **EditorFonts**: Inter Regular (default) and Inter SemiBold with Lucide icons merged into the Private Use Area (U+E000-F8FF, icons 0.9x and offset 2 px down, advancing a whole text size), JetBrains Mono without icons; type scale Caption 12, Body 14, Title 17, Display 24; `UI::PushFont(font, size)` | `UI/EditorFonts.h:106-159`, `EditorFonts.cpp:36-129, 214-231` | DG 2738 (fonts bullet) |
| **CJK fallback**: system fonts (`Platform::FindFallbackFontFiles`) read once per process on an I/O job, merged behind the editor's glyphs between frames, excluded from the icon range; `GetGlyphGeneration` invalidates measured text widths | `EditorFonts.cpp:131-212` | DG 2738; R0.3 line 160 |
| **Icons.h**: every Lucide icon as a UTF-8 string constant plus `c_All`, generated from the font's cmap and codepoint JSON by `StrataEditor/Tools/GenerateIconHeader.py` | `UI/Icons.h` (generated), `StrataEditor/Tools/GenerateIconHeader.py` | AGENTS "Working with third-party code"; DG 2738 |
| **EntityIcons**: a component type's icon; an entity's icon from the component that says most about it (camera, light, sky, sound, text, mesh...), groups and placeholders | `UI/EntityIcons.h`, `.cpp` | — |
| Asset type icons and display names (`GetAssetTypeIcon`, `GetAssetTypeDisplayName`) | `UI/PropertyWidgets.h:95-98` | — |
| **Brand mark** drawn as vectors (four staggered bands; three below 24 px) and the strata progress bar | `Widgets.h:200-214`, `Widgets.cpp:892-922, 1003-1047`; `Tools/GenerateBrandAssets.py` | — |

### 1.4 The widget kit (`UI/Widgets.h`) and its helpers

Every kit widget is sized from the font, colored from the theme and records its rectangle in `UI::ItemProbe` (DG 2738,
"Controls come from the widget kit").

| Widget | Where (`Widgets.h` / `Widgets.cpp`) |
| --- | --- |
| `ButtonStyle` (Enabled, Active, ActiveColor, Primary) | h 28-37 |
| `IconButton`, `ToolbarButton`, `GetToolbarButtonWidth` (custom-drawn on an `InvisibleButton`) | h 39-47; cpp 62-122, 198-216 |
| `Chip`, `ToggleChip` (on / on-but-not-in-effect states), `ChipWidth`; chips never take focus (`ImGuiButtonFlags_NoFocus`) | h 49-57; cpp 124-189, 281-299 |
| `ChipStripState` / `ChipStrip`: a strip that turns its last chips into icons and wraps onto extra rows, decided from the previous frame | h 58-91; cpp 218-279 |
| `Pill`, `CalcPillWidth` (status pills) | h 93-97; cpp 301-334 |
| `IsTooltipDue` (write costly tooltips only while showing) | h 99-102; cpp 193-196 |
| `Banner`, `CenteredText` | h 104-110; cpp 336-396 |
| `SearchField` (icon hint, clear button, `reload` for caller-replaced text) | h 112-117; cpp 398-428 |
| `PushSelectionColors` / `PopSelectionColors` (selected rows keep the accent under the mouse) | h 119-124; cpp 430-440 |
| `SectionHeader` (SemiBold collapsing header with a right-aligned summary) | h 126-130; cpp 442-476 |
| `Heading` | h 132-133; cpp 478-502 |
| `Card`, `CardPicture`, `GetCardHeight` | h 135-148; cpp 504-609 |
| `OpenModal` / `BeginModal` / `EndModal` (centered, kept inside the viewport, title heading, close button), `DialogButton`, `DialogButtonWidth` | h 150-160; cpp 611-661, 998-1069 |
| `ActionButton` (1.6 frame heights) | h 162-165; cpp 663-720 |
| `LinkButton` | h 167-170; cpp 722-752 |
| `TextField` (caption label above) | h 172-175; cpp 754-768 |
| `CopyableCode` (monospace with copy button and 1.5 s check mark) | h 177-182; cpp 770-810 |
| `EntryCard`, `EntryCardContent` (badge or picture, title, elided subtitle, detail) | h 184-198; cpp 812-890 |
| `ElideStart`, `ElideEnd` | h 205-209; cpp 924-996 |
| `Legend` (swatches, labels, right-aligned counts over an image) | h 216-226; cpp 1071-1114 |
| `TextureImage` (draws a texture as its content looks, through `AddImGuiTextureDisplay`) | h 228-233; cpp 1116-1131 |
| `CancelDragDropOnEscape` | h 235-237; cpp 1133-1144 |
| **ItemProbe** / `NumberedProbeKey`: per-frame map of widget rectangles, enabled state, meaning color and text, keyed by hashed id; `Duplicate` flags ids recorded twice in a frame | `UI/ItemProbe.h:174-216`, `ItemProbe.cpp:25-66` |
| **TextFormat**: platform path display, "5 minutes ago", short ages, initials for badges | `UI/TextFormat.h`, `.cpp` |
| **Markdown**: block parser (headings, paragraphs, lists, pipe tables) and renderer, used for About's notices | `UI/Markdown.h:20-41`, `.cpp` |
| **FileDialogs**: native file/folder pickers (nfd), blocking, main thread | `UI/FileDialogs.h`, `.cpp` |

### 1.5 The editor shell (`EditorLayer`)

| Feature | Where | Doc / release |
| --- | --- | --- |
| `EditorLayer : Layer, EditorShell`: owns `EditorContext`, the command registry, runner, automation, settings pages, panel registry and dialogs | `EditorLayer.h:125-384` | AR 3219-3239 |
| Frame of the UI: input tracking, binding capture, Escape cancels drags, launcher **or** shortcuts + dock space + tool-panel docking + inspection tab switch + Problems focus + panels; then every dialog, the unsaved-changes modal, toasts, ImGui demo, frame rate | `EditorLayer.cpp:726-795` | AR 3239 |
| **Dock space host** (menu bar, main toolbar, dock space) and a separate **status bar** window at the caption size | `EditorLayer.cpp:1383-1447` | AR 3239 |
| **Default layout** built with DockBuilder: Hierarchy left (15%, at least 16 font sizes, at most 30%), Inspector + Asset right (20%, at least 18 font sizes), bottom 22% (Console, Problems, Content Browser, Streaming, Performance, Activity), Scene + Game + Project Settings in the center; replaced when the saved layout's version differs (`c_LayoutVersion = 5`) | `EditorLayer.cpp:76-83, 1320-1360, 1404-1422`; `EditorLayer.h:129-132` | DG 2738; AR 3239 |
| `DockNewToolPanels`: panels closed by default dock beside the Console (Project Settings beside the Scene view) in layouts saved before them | `EditorLayer.cpp:2114-2131` | AR 3239 |
| **Menu bar**: File (New/Open Project, Open Recent, Open Sample, Close Project, Show Launcher, New/Open/Save/Save As Scene, Recover Unsaved Changes, Set as Start Scene, Export Game, Project Settings, Preferences, Exit), Edit (Undo/Redo with step names, Cut, Copy, Paste, Duplicate, Rename, Delete, Drop to Ground, Select All), View (panel toggles from the registry, Reset Layout), Entity, Scripts (Build, Reload, Create Script Build, New Script, Open Scripts Folder, Show Problems, External Editor), Help (About, ImGui Demo) | `EditorLayer.cpp:1449-1677` | DG 3346 |
| **Main toolbar**: gizmo tools (Select Q, Move W, Rotate E, Scale R), World/Local space, Snap and snap steps popup, Play/Simulate/Pause/Step/Stop, script build and export buttons | `EditorLayer.cpp:1679-1858` | DG 3568 |
| **Status bar pills**: play state, frame (`ms · FPS · J jobs`, opens Performance), assets (`N ready · M streaming · <pool> X/Y MB`, `K importing`, Sulfur at 85%, Cinnabar over or failed; opens Streaming), saving progress (opens Activity), physics "N bodies without collision", automation, scripts (build / failed / crashed), input holds (click releases), unread errors (opens Console) | `EditorLayer.cpp:1872-2264` | DG 2738 ("Status pills"); R0.3 line 103 |
| **Compact pill texts** with hysteresis (compact while full texts overflow, full again with a margin of 2 font sizes) through `StatusPillText` | `EditorLayer.cpp:1890-1898, 1938-1944`; `c_StatusBarMarginFontSizes` 86 | DG 2738 |
| **Idle throttling**: `TrackInput`, `IsBusy`, `RunsUncapped`, `UpdateFrameRate`, `UpdateSteppingFrameRate`, preferences `Editor.FrameRate` (idle after 0.5 s, 30 fps idle, 10 unfocused, unlimited active; 0 never idles; minimum 5 fps) | `EditorLayer.cpp:842-919`; `Editor/EditorFrameRate.h:12-46` | DG 2738 (idle bullet); MS 132; R0.3 line 172 (30/10 fps); RM 1564-1565 (preferences: wave 8, after 0.7.0) |
| **Frame stats**: work time averaged over 60 frames (`GetLastFrameWorkTime`, excludes waits), ImGui's framerate, idle flag, passed to panels in `EditorPanelContext::Frame` | `EditorLayer.cpp:929-949`; `EditorPanelRegistry.h:25-32` | DG 2738 |
| **Unsaved-changes question** and its relatives (release project with unwritten settings, quit with unwritten preferences, a saving dialog while saves write; Don't Save re-asks if the undo version moved; `DrawDiscardQuestion` inside other modals) | `EditorLayer.cpp:987-1048, 2277-2506`; `EditorLayer.h:317-339` | AR 3239 (the question paragraph); DG "No silent data loss" (2911) |
| Window close asks first; files dropped on the window (a `.stproj` opens it, others import into the Content Browser's folder) | `EditorLayer.cpp:797-840` | DG 3508 |
| `editor.showPanel {panel, scripts?, search?}` and `editor.showDialog {dialog, section?}`: window commands only the UI registers | `EditorLayer.cpp:168-336` | DG 2738 (status pills bullet); AR 3239 |
| Window title, `--screenshot` of the final frame, command-script progress, startup time measurement | `EditorLayer.cpp:549-595, 703-724` | DG 3346 |

### 1.6 The panel registry

| Feature | Where | Doc / release |
| --- | --- | --- |
| `EditorPanel` interface: `OnUpdate` (every frame, even closed), `GetWindowOptions`, `OnImGuiRender` (visible only), `OnHidden`, `OnDetach` (no ImGui), `IsAnimating` | `UI/EditorPanelRegistry.h:60-81` | DG 2738 (panels bullet) |
| `EditorPanelDescriptor` (Id, Title, Icon, MenuPath, OpenByDefault, Placement Docked/Launcher, factory); `Register` validates ids (ini-safe), titles, factories, one launcher | `EditorPanelRegistry.h:46-110`, `.cpp:30-...` | DG 2738 |
| `EditorPanelContext` (Context, Commands, Runner, Frame, Shell) | `EditorPanelRegistry.h:34-44` | DG 2738 |
| Windows begun by the registry as `<icon> <title>###<id>`; tab close button; View menu items by MenuPath | `EditorPanelRegistry.cpp:168-246`, `DrawMenuItems` | DG 2738 |
| Open states and layout version in imgui.ini through a custom settings handler (`[StrataPanels][Open]`, `[StrataPanels][Layout]`); states of unregistered panels kept | `EditorPanelRegistry.cpp:330-424` | DG 2738; AR 3239 |
| `Focus` (open + bring to front, retried up to 4 frames until the docked tab shows, deferred behind a modal, survives a layout reset and the first-frame ini read) vs `ShowTab` (select the tab without stealing keyboard focus) vs `SelectTab` | `EditorPanelRegistry.h:124-136`, `.cpp:126-160, 180-230, 360-367` | DG 2738 (end of status pills bullet) |
| `GetShownWindowRect` (where a visible panel was drawn; used to place toasts) | `EditorPanelRegistry.h:141-148` | AR 3239 |
| Built-in panels registered in drawing order with ids in `EditorPanels::` | `EditorLayer.h:91-107`, `EditorLayer.cpp:337-401` | AR 3219 |

### 1.7 The panels (`StrataEditor/src/Panels/`)

| Panel (id, title) | What it is | Where | Doc / release |
| --- | --- | --- | --- |
| `Viewport`, "Scene" | the Scene view (see 1.10) | `ViewportPanel.{h,cpp}` | DG 3568; MG 7 |
| `Game`, "Game" | the Game view (see 1.10) | `GameViewPanel.{h,cpp}` | DG 3568; MG 7-41; R0.4 line 68 |
| `Hierarchy` | the scene tree: multi-select, drag/drop reparenting, rename in place, eye toggle, prefab badge, search with `c:` `t:` `l:` `cell:`, create menu, empty-scene hint, world strip | `SceneHierarchyPanel.{h,cpp}` | DG 3260, 3525; R0.3 line 32 |
| `Inspector` | the selected entities from reflection, or the scene's settings (see 1.9) | `InspectorPanel.{h,cpp}` | DG 3282; R0.3 line 32 |
| `AssetInspector`, "Asset" | the inspected asset: header and actions, material editor, animation views, import settings draft with Apply/Revert, texture/thumbnail preview, model summary, audio waveform with Play/Stop, import outcome, world cook | `AssetInspectorPanel.{h,cpp}`, `UI/MaterialEditor`, `UI/AnimationAssetViews` | DG 3260 (thumbnails bullet), 3282, 3692 |
| `ContentBrowser` | folder tree, grid/list (clipped), breadcrumbs, search, type chips, tile slider, New (folder, material, world), Import, drag sources and folder drop targets, rename popup, delete dialog, Scripts root | `ContentBrowserPanel.{h,cpp}`, `UI/ScriptBrowser`, `UI/DeleteAssetDialog` | DG 3260 |
| `Console` | recent log with level filters and search; messages with a source reference open the external editor; counts unread errors | `ConsolePanel.{h,cpp}` | DG 2738 (status pills) |
| `Problems` | last script build's diagnostics and the crash that stopped play; double-click opens the source | `ProblemsPanel.{h,cpp}` | R0.3 line 73 |
| `Streaming` (closed by default) | memory pools vs budget, loads, queues, upload sparkline, sortable asset table built on a job, Physics section, World section with the cell map | `StreamingPanel.{h,cpp}`, `UI/CellMap` | AR 3239 ("Instruments"); R0.3 line 103; R0.4 line 37 |
| `Performance` (closed by default) | stacked CPU timeline of 600 frames + GPU timeline, spikes, per-stage table, what bounds the frame, Pause/Space snapshot, Copy as JSON | `PerformancePanel.{h,cpp}` | AR 3239; R0.3 line 103; R0.4 line 51; R0.7 line 83 |
| `Activity` (closed by default) | the command journal as a clipped table, filters, details JSON, Copy as script, Re-run, Undo to here | `ActivityPanel.{h,cpp}` | AR 3239; R0.3 line 97 |
| `ProjectSettings` (closed by default) | the settings browser for the project (see 1.12) | `ProjectSettingsPanel.{h,cpp}` | MS 13; R0.6 line 84 |
| `Welcome` (Launcher placement) | the launcher (see 1.11) | `WelcomePanel.{h,cpp}` | DG 3508 |
| Canvas mode view (not a panel; inside the Scene view) | 2D layout of a UI canvas at its reference aspect, element outlines, handles, zoom/pan | `CanvasModeView.{h,cpp}`, `UI/UIRectDrawer.cpp` | R0.4 line 153 (Game UI chip, canvas) |

### 1.8 Cached views, virtualized lists and selection

| Feature | Where | Doc |
| --- | --- | --- |
| **HierarchyView** (core, no UI): flat rows of visible entities (depth-first walk of sibling links into expanded entities only), rebuilt only when the scene, its hierarchy version, expansion or filter changes (while filtering also names/tags/components through entt signals); `FindRow`, `GetRowRange`, `Reveal`, expansion per UUID across play mode | `Editor/HierarchyView.h:26-202`, `.cpp:134-327` | DG 3260 |
| **HierarchyFilter**: whitespace terms, all must hold; word, `c:`, `t:`, `l:` (layer, `l:persistent`), `cell:x,z`; unknown component terms reported | `HierarchyView.h:49-69`, `.cpp:79-...` | DG 3260; editor.showPanel's `search` |
| **Drop zones** (top quarter before, bottom quarter after, middle inside) mapped to `entity.setParent {entities, parent, index}`, accounting for entities leaving the list before the insertion point and refusing cycles | `HierarchyView.h:82-97,157-163`, `.cpp:555-610` | DG 3260 |
| `GetTopmostInHierarchyOrder` (what drag, copy, duplicate pass to commands) | `HierarchyView.h:165-167` | — |
| **Hierarchy drawing**: one `BeginMultiSelect` scope (ClearOnEscape, ClearOnClickVoid, BoxSelect1d, SelectOnClickRelease), rows identified by `entt::entity` handle in `SetNextItemSelectionUserData`, `ImGuiListClipper` with `IncludeItemByIndex` for the range source and the rename row, requests applied to `EditorContext::SetSelection` (matches only while filtering), deferred actions after drawing | `SceneHierarchyPanel.cpp:655-842, 1135-1192` | DG 3260 |
| **AssetBrowserView** (core): folder rows and items (folders first, then assets by name, a model's sub-assets after it when expanded; search below the folder, type filter) rebuilt only on `EditorAssetManager::GetChangeVersion` or view-state change | `Editor/AssetBrowserView.h` | DG 3260 |
| Content Browser grid clipped by rows of tiles; labels and elided tile titles cached per rebuild and width | `ContentBrowserPanel.cpp:858-1008`; `ContentBrowserPanel.h:110-123, 165-170` | DG 3260 |
| **Thumbnails**: `ThumbnailCache::Request` every frame a tile shows, type icon until ready; `RequestPreview` for the Asset tab; `c_Version = 11` | `Editor/ThumbnailCache.h:109-132`; used at `ContentBrowserPanel.cpp:933` | DG 3260 (thumbnails bullet) |
| Other cached/clipped lists: Activity rows (journal version), Problems rows (build/crash change), Streaming table (job, refreshed at most every `c_TableRefreshSeconds`), ScriptBrowser (I/O-thread listing), AnimationAssetViews joint tree, asset picker list | panel headers above | AR 3239; DG 2738 |

### 1.9 Inspectors generated from reflection

| Feature | Where | Doc / release |
| --- | --- | --- |
| Component sections for components every selected entity has; header with icon, name (rename in place), active toggle, ID with copy; multi-entity count | `InspectorPanel.h:22-34`, `.cpp` | DG 3282 |
| **Property rows** from `ComponentInfo::Properties` (`Strata/Reflection/Property.h:22-112`): hidden/transient skipped, grouped by `PropertyInfo::Section` (made once per type), label column + widget column | `InspectorPanel.cpp:915-1025` | DG 3282 ("Sections") |
| **Mixed values** across entities (`SharedPropertyValue`, "--"), partial writes of changed axes (`SetPropertyComponentsWithUndo`), rotations through `RotationAnglesEdit` | `InspectorPanel.cpp:974-1033`; `PropertyWidgets.h:21-52` | DG 3282 |
| **Undo merging**: drags merge into one undo step; `Finished` breaks the merge | `InspectorPanel.cpp:1018-1024` | DG 2972 "Undo" |
| `DrawPropertyWidget` by `PropertyType`: Bool, Int, UInt (power-of-two limits, physics layer, zero label), Float (people's formatting), Vec2/3/4 and Quat with axis labels in axis colors that reset an axis, Color3/4 with channel fields and swatch picker, String, Enum, Asset (searchable virtualized picker, drag target), Entity (searchable list, drag target) | `UI/PropertyWidgets.h:54-65`, `.cpp:892-...` | DG 3282 (last sentence) |
| `BeginPropertyTable` / `PropertyLabel` (ellipsis + tooltip, overridden mark, inactive reason) / `PropertyGroupHeading` | `PropertyWidgets.h:67-93` | DG 3282 |
| **Inactive reasons** (`PropertyInfo::InactiveReason`, `ComponentRegistry::SetInactiveReason`): disabled row with the reason as tooltip; shared across a multi-selection | `Property.h:89-101`; `InspectorPanel.cpp:985-1009` | DG 3282; R0.4 line 88 |
| **ComponentDrawers** (whole-component drawers above the rows, e.g. UIRect's anchor grid) and **PropertyDrawers** (one property's value, e.g. `PostProcess.TAAPreset`) | `UI/ComponentDrawers.h:126-202`, `.cpp`, `UI/UIRectDrawer.cpp` | DG 3282 |
| Component menu: Reset, Copy Values, Paste Values (clipboard JSON `{"Strata":{"Format":"ComponentValues"}...}`), Remove (not for engine-added components); Add Component popup with filter; missing-requirement notices with Add | `InspectorPanel.h:72-85, 138`; `UI/EditorActions.h:84-89` | DG 3282; R0.4 line 88 |
| **Prefab bar and overrides**: Select/Open/Overrides menu (Apply All, Revert All, each override, rows found once per list/history/hierarchy version), SemiBold label with accent bar, right-click Apply/Revert, prefab commands scheduled after drawing | `InspectorPanel.h:41-107, 233-246` | DG 3282; DG "Prefab instances" (2854) |
| Material section on mesh renderers: New Material, inline shared material editor | `InspectorPanel.cpp:1035-1100`; `UI/MaterialEditor.h:22-58` | DG 3692 |
| **MaterialEditor**: drag previews in the loaded material, release saves (one undo step, one write), texture-usage mismatch warnings with a Fix button | `UI/MaterialEditor.h:22-58` | DG 3692; R0.4 line 84-86 |
| Scene settings with nothing selected (physics, streaming, collision layers link, fixed rate link, Graphics Quality link, sky with Extract Sun / Add Height Fog / Bake Reflection Probes) in closed sections with summaries | `InspectorPanel.h:186-200` | DG 3282 |
| Live lines: sun shadow maps ("Shadow maps: 5 x 8192 (Graphics Quality: High)"), reflections quality | `InspectorPanel.h:142-150, 172-217` | DG 3282 |
| Script fields drawer, animator state while playing | `InspectorPanel.h:151-162` | DG 3282 |
| Inspection target switch (entities vs one asset) brings the matching tab forward without stealing focus | `EditorLayer.cpp:745-751` | DG 3282 |

### 1.10 The Scene view and the Game view

| Feature | Where | Doc / release |
| --- | --- | --- |
| **Render to texture**: the panel's pixel size (`ViewportImageArea`, framebuffer scale), `ViewportRenderer::Render`, image drawn with `AddImage` | `ViewportPanel.cpp:164-280` | DG 3568 |
| **ViewportToolbar**: a strip above the image (never covering the game's HUD) with rows for wrapped chips, play-state colored bottom border, text boxes, stats overlay | `ViewportToolbar.h:22-52`, `.cpp` | DG 3568; R0.4 |
| **Chips**: camera settings, grid, outline, gizmos, stats, preview lighting, game UI, debug view (Lit, Streaming, LOD, Mip...), quality chip (project/own preset), Game camera (F8), animation preview chip, agent chip at the right | `ViewportPanel.cpp:370-736` | DG 3568; R0.7 line 39-42 |
| **Debug view legend** with entity counts per color | `ViewportPanel.cpp:737-815`; `UI::Legend` | DG 3568 |
| **Editor camera** (core): target/distance/yaw/pitch, orbit (Alt+LMB), pan (MMB, world units per pixel at target depth), dolly (wheel, 0.85 per step), fly (RMB + WASD/QE, Shift x4, wheel = speed, cursor locked), Focus/FitBounds, saved per scene | `Editor/EditorCamera.h:15-139`, `.cpp:43-259`; `ViewportPanel.cpp:867-930` | DG 3464, 3568; MG 7 |
| **Picking**: a click requests a one-pixel async readback of the entity-ID buffer (`RequestPick`, applied in a later frame by `UpdatePicking`, dropped if the scene changed or timed out); Ctrl toggles, Shift adds; UI elements picked first by `UIRectEdit::PickElement` | `ViewportPanel.cpp:244-268`; `Editor/EditorViewport.cpp:415-470` | DG 3568 |
| **Gizmo**: ImGuizmo themed with axis colors; `Manipulate` on the primary entity's world matrix; `TransformDrag` moves the topmost selected entities, recomputes locals under parents, one undo step per drag (none while playing); snap per toolbar toggle inverted by Ctrl; the image is a `Dummy` while over the gizmo | `ViewportPanel.cpp:111-162, 936-995`; `Editor/TransformEdit.h:21-90` | DG 3568; test "Gizmo drags snap..." `EditorUITests.cpp:1828` |
| **Shortcuts in the view**: Q/W/E/R gizmo, F frame selection, Home frame all, F8 game camera, selection shortcuts and F2 rename | `ViewportPanel.cpp:816-866` | DG 3346, 3568 |
| **Agent chip and flash**: latest mutating automation command ("Agent: entity.create · 3 s ago"), outline of changed entities for 0.6 s | `ViewportPanel.h:32-49`, `.cpp:499-602` | R0.5 line 216 ("The status bar and the viewport show when an agent is connected") |
| **Drop and ghost**: an asset dragged over the image feeds `PlacementPreview` a ray; the release runs `asset.place` (or `component.set` of a material); label at the pointer | `ViewportPanel.cpp:1063-1150`; `Editor/PlacementPreview` | DG 3525; RM 1564 (wave 8) |
| Scene-load overlay card (scene read-only while it opens) | `ViewportPanel.cpp:1020-1061` | DG "Opening scenes" (3116) |
| **Game view**: primary camera with HUD, no overlays/picking/gizmos; resolution menu (free, 16:9, 16:10, 4:3, 21:9, 1920x1080, 1280x720, custom, game's request) letterboxing aspects and scaling fixed sizes; targets freed while hidden; "no camera" message as the game shows it | `GameViewPanel.h:17-75`; `Editor/EditorViewport.h:36-86` | DG 3568; MG 28 |
| **Game input ownership**: `Input` enabled only while the Game view is shown, focused and playing; `Input::SetViewport` with the rendered resolution; a locked cursor sets `ImGuiConfigFlags_NoMouse`; Shift+F1 leaves; hint for `c_MouseHint` seconds; Play brings the Game tab forward with the keyboard, Stop the Scene view back | `GameViewPanel.cpp:241-281`; `EditorLayer.cpp:1243-1276` | DG 3568 ("Game input"); MG 36 |

### 1.11 Launcher, dialogs

| Feature | Where | Doc / release |
| --- | --- | --- |
| **Launcher** (`WelcomePanel`, drawn instead of the dock space under File/Help): hero band, New/Open Project, Open Sample, recent projects as picture cards (read on an I/O thread, search over names and paths, context menu), template and sample cards, "Connect an AI agent" (`claude mcp add strata -- "<bin>/StrataCLI" mcp` with copy button, automation state), footer (version, commit, GPU, startup), errors shown on it; Continue without a project; File > Show Launcher | `Panels/WelcomePanel.h:19-136`, `.cpp`; `EditorLayer.cpp:1362-1381` | DG 3508, 3483; AR 3239; R0.3 line 28, 93; R0.5 line 33 (sample pictures); R0.6 line 160 |
| **New Project / Open Sample** dialogs (template cards, name, location remembered in imgui.ini `StrataLauncher`, first `<home>/StrataProjects`), re-ask if the scene changed meanwhile | `UI/ProjectDialogs.h:17-60` | DG 3508; AR 3239 |
| **About Strata** (build, GPU, driver, API, startup, UI scale, Copy Details, compiled-in third-party notices through Markdown) | `UI/AboutDialog.h:13-40` | DG 3508 |
| **Export Game** dialog (fields of `project.export`, progress bar with stage and Cancel, result with Open Folder) | `UI/ExportDialog.h:15-88` | DG "Exporting games" (3009) |
| **Recover Unsaved Changes** dialog | `UI/RecoveryDialog.h:14-47` | DG "Autosave and recovery" (2948) |
| **Delete asset** confirmation listing referencers, "Delete Anyway" | `UI/DeleteAssetDialog.h:16-44` | DG 2840 "Asset files are never lost" |
| **New Script** dialog and the **External Editor** page | `UI/ScriptDialogs.h:17-68` | DG "Scripts through commands" (3135) |

### 1.12 Settings windows

| Feature | Where | Doc / release |
| --- | --- | --- |
| `SettingsBrowser` (page list grouped by category with search, selected page beside it), `SettingsPage`, `EditorSettingsPageRegistry` (custom pages for complex sections), `SettingsWindowKind` | `UI/SettingsPages.h:23-121`, `.cpp` | DG 1146; MS |
| Generic page for simple sections: fields drawn as properties through `SettingsFieldProperty` + `DrawPropertyWidget` | `UI/SettingsFieldProperty.{h,cpp}` | DG 1146 |
| **Project Settings panel**: Game page (start/loading scene, title, version, company, copyright, icon), Export page (kept paths), registered sections (Collision Layers, Simulation, Timing, Graphics Quality, Input Actions...) | `Panels/ProjectSettingsPanel.h:12-30` | MS 13-131; R0.6 line 84 |
| **Graphics Quality page**: preset chips, rows x presets table, editable Custom column, memory at 1080p/2160p, GPU time, players' options banner and reset | `UI/GraphicsQualityPage.h:17-60` | DG 4009; R0.7 line 39 |
| **Collision Layers page**: names, matrix | `UI/CollisionLayersPage.h:18-53` | DG 1292; MS 13 |
| **Input Actions page** and **BindingCapture** (listening takes the keyboard from ImGui, locks keys until released, timeout, owner must ask each frame) | `UI/InputActionsPage.h:19-83`, `UI/BindingCapture.h:12-42` | DG 1442 |
| **Preferences dialog** (modal, works on the launcher): External Editor, Interface (scale factor, `Editor.Interface`), Frame Rate (`Editor.FrameRate`) | `UI/PreferencesDialog.h:11-33`; `Editor/EditorInterface.h:10-24`; `Editor/EditorFrameRate.h` | DG 1581; MS 132; R0.6 line 89-90 (preferences and interface size) |

### 1.13 Shortcuts, focus and drag and drop

| Feature | Where | Doc |
| --- | --- | --- |
| Global shortcuts (`ImGuiInputFlags_RouteGlobal`, nothing behind a modal): Ctrl+P play/stop always; Ctrl+Z, Ctrl+Y / Ctrl+Shift+Z (through `edit.undo`/`edit.redo`), Ctrl+S, Ctrl+Shift+S, Ctrl+O, Ctrl+B unless the running game has the input (`AcceptsEditShortcuts`) | `EditorLayer.cpp:951-985` | DG 3346 |
| Focus-routed selection shortcuts (`ImGuiInputFlags_RouteFocused`) of the Hierarchy and the Viewport: Delete, Ctrl+D, Ctrl+C, Ctrl+X, Ctrl+V, End (drop to ground), Ctrl+A, F2 | `UI/EditorActions.cpp:318-338`; `ViewportPanel.cpp:816-823` | DG 3346 |
| Panel-local keys: Content Browser arrows/Enter/F2/Delete/Backspace; Hierarchy F2 / double click rename, Enter/Escape; Performance Space (pause); Game view Shift+F1; Escape cancels any drag (`CancelDragDropOnEscape`) | panel headers; `Widgets.h:235-237` | DG 3260; AR 3239 |
| Edit-menu actions share code with shortcuts (`EditorActions::*`), clipboard is JSON text (`entity.copy` data) | `UI/EditorActions.h:48-98` | DG 3346 |
| Drag payloads `STRATA_ENTITIES`, `STRATA_ASSET`, `STRATA_ASSET_FOLDER` | `UI/PropertyWidgets.h:14-19`; `ContentBrowserPanel.h:107` | — |

### 1.14 Notifications

| Feature | Where | Doc / release |
| --- | --- | --- |
| `EditorNotifications` (core): at most 4, merged when identical or of a `Group`, lifetimes 5/8/12 s by level, `Replace` in place, `KeepAlive` on hover, versioned | `Editor/EditorNotifications.h:17-86` | DG 2738 (toasts bullet); AR 3239 ("Notifications") |
| `NotifyCommandOutcome` for the person's commands; `EditorCommandResult::Announced` avoids double toasts | `EditorNotifications.h:83-86` | DG 2738 |
| `UI::DrawNotifications`: one no-focus, no-nav window at the bottom right of the shown Scene/Game view (else the work area above the status bar), actions Show in Activity / Show Asset / Show Problems / Show in Console / Recover, close; nothing drawn while empty | `UI/Notifications.h:111-123`, `.cpp:72-205`; `EditorLayer.cpp:771-790` | DG 2738; R0.4 line 88 |

### 1.15 Testing infrastructure of the area

| Feature | Where |
| --- | --- |
| `ImGuiHarness`: ImGui context with the editor's fonts and theme (styled by an unattached `ImGuiLayer`), texture requests honored without a renderer, injected mouse/keys/text, own clipboard, `ClickItem(probeKey)` over three frames, id-conflict detection, fallback glyph counting | `StrataTests/src/Editor/ImGuiHarness.h:28-160`, `.cpp:55-207` |
| `FakeEditorHost`, `HarnessEditor` (an editor on the harness; temporary default project location) | `ImGuiHarness.h:28-85`; `HarnessEditor.h` |
| **Editor.UI.Source** scans (empty allowlists): colors only from the theme, sizes scale with the font (literals above 16 px judged by the product they are part of, size-holding names followed), panels draw through the registry, no `AddFontDefault`, UTF-8 encoded once, panels change files only through commands | `StrataTests/src/Editor/EditorUISourceTests.cpp:499-660` |
| Suites: `ImGui.Layer`, `ImGui.Platform` (`StrataTests/src/ImGui/`), `Editor.Theme`, `Editor.UI` (45 cases in `EditorUITests.cpp`, 26 in `EditorObservatoryUITests.cpp`), `Editor.UI.Hierarchy` / `.Inspector` / `.AssetInspector` (`EditorAuthoringUITests.cpp`, 62 cases), `Editor.HierarchyView`, `Editor.Notifications` / `Editor.UI.Notifications`, `Editor.UI.Text`, launcher (`EditorLauncherTests.cpp`, 23), settings UI (`EditorSettingsUITests.cpp`, 19), Graphics Quality page, Content Browser UI (12), Activity UI (9), `Editor.UI` commands (12), viewport and camera tests | `StrataTests/src/Editor/*.cpp` |
| Perf: `Perf.EditorPanels` (Streaming with 10,000 assets, Performance panel; Content Browser with 10,001 assets and thumbnails: "a fraction of a millisecond per frame"), `PerfGPU.Editor`; HierarchyView test with 100,000 top-level entities rebuilding nothing on idle frames | `EditorPanelPerfTests.cpp:94-215`; `HierarchyViewTests.cpp:137` |

### How completeness was checked

- Every header of `Strata/src/Strata/ImGui` (4), `StrataEditor/src/UI` (32 headers incl. `Icons.h`; `UIRectDrawer.cpp`
  has none) and `StrataEditor/src/Panels` (15 headers) is named in a row above; the file list came from `ls` and
  `wc -l` of the three folders.
- Every panel registered in `EditorLayer::RegisterBuiltinPanels` (`EditorLayer.cpp:354-370`, 13 panels) has a row; the
  ids match `EditorPanels::` (`EditorLayer.h:92-107`).
- The two commands the UI registers itself (`editor.showPanel`, `editor.showDialog`) are listed; all other commands the
  UI runs belong to editor-core.
- The menu items were extracted from `EditorLayer::DrawMenuBar` with a grep of `BeginMenu`/`MenuItem`.
- Every `ImGui::Shortcut` / `IsKeyPressed` in `EditorLayer.cpp`, `EditorActions.cpp`, `ViewportPanel.cpp`,
  `GameViewPanel.cpp` was read; other panels' keys come from their header comments.
- Every widget declared in `Widgets.h` has a row (located by a grep of top-level definitions in `Widgets.cpp`).
- The settings sections the UI owns pages for (External Editor, Collision Layers, Input Actions, Graphics Quality) and
  the user sections (`Editor.ExternalEditor`, `Editor.Interface`, `Editor.FrameRate`) are listed.
- Shader entries of the area: `ImGui.vert`, `ImGui.frag` (the only two the ImGui renderer loads, `ImGuiRenderer.cpp:128-129`).
- No component, asset type or host function belongs to this area.

---

## 2. Concepts to teach (dependency order)

1. **What an editor is, and why it is not the game.** Problem: building content needs tools (place, tune, inspect,
   play-test) that the shipped game must not carry. Approaches: separate tool applications (Source's Hammer), an editor
   that embeds the runtime (Unity, Unreal, Godot), web-based or external tools. Strata: one editor executable embedding
   the engine, but the UI lives in Tooling layers (`ImGui` layer `Tooling: true`, `Layers.json:105-111`;
   `StrataEditorUI` library), so exported games link neither ImGui nor the editor. A second split inside the editor: the
   core (`StrataEditorCore`, no UI) and the UI (`StrataEditorUI`) so tests and automation drive the editor without a
   window. Newcomers get wrong: putting logic in the UI ("the button does it"); in Strata the button runs a command.
2. **Retained-mode versus immediate-mode UI.** Retained: a tree of widget objects with state and callbacks (Qt, WPF,
   HTML DOM, Unreal's Slate, Unity's UI Toolkit). Immediate: every frame the code *describes* the UI by calling
   functions; the library keeps only minimal state keyed by IDs (Dear ImGui, Unity's legacy IMGUI, Casey Muratori's
   original IMGUI talk). Trade-offs: immediate mode is code-first, needs no synchronization between app state and widget
   state, is ideal for tools that change weekly; it re-runs layout every frame (cost proportional to what is submitted),
   makes accessibility and complex layout harder, and "layout from the previous frame" artifacts appear. Strata takes
   Dear ImGui (docking branch). Newcomers get wrong: thinking ImGui stores the value (it edits the caller's variable in
   place); expecting callbacks; forgetting that a widget call both draws and returns the interaction.
3. **ImGui's model in detail: frames, windows, items, IDs.** `NewFrame` → widgets → `Render` produce draw data. Windows
   (`Begin`/`End`), child windows, popups and modals (one popup per level: opening a modal over the window closes
   another), the "last item" that queries (`IsItemHovered`, `GetItemRectMin`) refer to, the ID stack (`PushID`),
   `"##hidden"` labels and `"###stable id"` window names, hovered/active/focused, keyboard navigation. Strata examples:
   rows push the entity UUID bytes as ID (`SceneHierarchyPanel.cpp:742`), panel windows are `"<icon> <title>###<id>"`
   (`EditorPanelRegistry.h:138-140`), the harness detects ID conflicts (`ImGuiHarness.h:95`). Pitfalls: two buttons
   "OK" in one scope share an ID; changing a window title loses its docking unless `###` is used.
4. **Backends: how a UI library meets an engine.** ImGui is platform- and GPU-agnostic; a *platform backend* feeds input
   and display size and serves cursor and clipboard; a *renderer backend* turns draw data into GPU work and owns
   textures. Most engines use the stock backends (`imgui_impl_glfw`, `imgui_impl_vulkan`); Strata writes both
   (`ImGuiPlatform` on its own `Window` events, `ImGuiRenderer` on NVRHI) because the engine owns the window abstraction
   (GLFW is sealed in `Platform/`), renders through NVRHI, and wants layout-aware keys and a game-aware cursor. Pitfalls:
   polling input in a backend while also receiving events (double input); forgetting focus-loss releases (stuck keys).
5. **Drawing a UI on the GPU.** Draw data = per-window draw lists of vertices (pos, uv, packed color), 16-bit indices
   and commands (clip rectangle, texture, element count, offsets). The renderer: orthographic mapping from pixels to NDC
   (`Scale = (2/w, -2/h)`, flipped Y), alpha blending (src alpha / inverse src alpha), no depth, no culling, scissor per
   command, one texture binding per command, the font atlas as just another texture. Frames in flight: the CPU writes
   next frame's vertices while the GPU may still read the last; Strata keeps a ring of mapped buffer sets guarded by
   event queries instead of staging copies (`ImGuiRenderer.h:77-91`, `.cpp:314-342`). ImGui 1.92's *dynamic textures*
   (the backend creates/updates/destroys atlas pages on request) vs the old "build the atlas once" model. Pitfalls:
   reusing a buffer the GPU still reads; destroying a user texture before the frame rendered; identifying draw callbacks
   by function address (identical-code folding merges them, so Strata identifies them by user-data address,
   `ImGuiRenderer.cpp:49-51, 73-83`).
6. **Color spaces in UI.** ImGui colors are display (sRGB) values; textures sampled through an sRGB format arrive
   linear; two-channel normal maps need Z reconstructed; single-channel textures are gray. Strata's
   `ImGuiTextureDisplay` modes encode on the way out (`ImGui.frag.slang:26-46`). Pitfall: showing a texture "as stored"
   and judging an asset by a wrong preview.
7. **Pixels, points and the UI scale (DPI).** Displays differ in density; OSes report a content scale; macOS and
   Wayland measure windows in points (framebuffer twice as large), Windows and X11 in pixels. Approaches: scale
   everything at draw time, or lay out in points and rasterize fonts at the framebuffer density. Strata: lay out in
   window units, scale the *style* by the UI scale (`ToUIScale` divides out the points factor,
   `ImGuiLayer.cpp:169-177`), build the style from unscaled defaults every time (`217-232`), even base sizes so 150% and
   200% give whole pixels (`Theme.cpp:173-234`), fonts by `FontScaleDpi`, a person's factor (Preferences > Interface)
   and `--ui-scale`. Rule: sizes are multiples of the font size. Pitfalls: scaling twice (compounding); fixed pixel
   widths that clip text at 200%.
8. **A design system for tools.** Tokens (named raw colors) vs semantic colors (what a color means), a type scale, an
   icon set, spacing and rounding rules, consistency enforced mechanically. Strata: the Bedrock palette and
   `ThemeColors`, the 12/14/17/24 type scale, Lucide icons as text, a `static_assert` over every `ImGuiCol_`, and the
   `Editor.UI.Source` scan with an empty allowlist. Why: a UI built by many agents stays one UI; colors carry meaning
   (axis colors equal gizmo colors; play-state colors on toolbar and border). Pitfall: "just this once" hex colors.
9. **Text rendering for tools: font atlases, icon fonts, fallback scripts.** Glyphs are rasterized into an atlas; fonts
   can be merged (icons in Unicode's Private Use Area), excluded ranges keep a text font from shadowing icons; scripts
   the bundled fonts lack (Chinese, Japanese, Korean) come from system fonts loaded off the main thread; missing glyphs
   show a fallback glyph. Strata: `EditorFonts` (`EditorFonts.cpp:39-197`), `Icons.h` generated from the font's cmap.
   Pitfalls: icons in the monospace font (no icons there: fallback glyph), UTF-8 encoded twice ("Â·"), loading tens of
   megabytes of fonts on the main thread.
10. **Writing custom widgets in an immediate-mode library.** Pattern: reserve an item (`InvisibleButton`) for hit
    testing and navigation, read hovered/held, draw with the window's draw list, render the nav cursor, show a tooltip,
    record for tests (`Widgets.cpp:62-122`). Layout that depends on its own result ("do the chips fit?") is decided
    from the previous frame and settles one frame later (`ChipStrip`, `Widgets.cpp:218-279`; status bar hysteresis).
    Pitfalls: `BeginDisabled` fading what must stay vivid (Strata's `vivid` flag), chips that steal focus from the game
    view.
11. **Docking and layout persistence.** Dock spaces split into nodes holding tabbed windows; layouts are saved per
    window name in an ini file; programs add their own ini sections. Strata: a default layout built with DockBuilder
    proportional to width with font-size minimums, a layout version that replaces outdated layouts, a custom
    `[StrataPanels]` handler for open states (`EditorPanelRegistry.cpp:330-424`). Pitfall: shipping a new default panel
    without bumping the version (it floats over the viewport in old layouts).
12. **Panel architecture and dependency inversion.** A registry of panel descriptors with lifecycle hooks (update even
    when closed, render only when visible, hidden hook to end drags, animating flag for the idle throttle); panels
    talk to the window through an interface (`EditorShell`), the window to the application through another
    (`EditorHost`), so the whole UI runs in tests with fakes. Pitfall: a panel calling `ImGui::Begin` itself (loses View
    menu, persistence, focus handling).
13. **UI as a client of commands (model-view separation).** The UI draws state and runs named commands; undo,
    automation (agents through MCP), the activity journal and replay all see the same operation. Deferred actions:
    never mutate what you are iterating while drawing (`SceneHierarchyPanel::m_Deferred`,
    `InspectorPanel::SchedulePrefabCommand`). Commands that take frames go through the runner. Pitfall: writing a
    component directly from a panel (no undo, no journal, breaks the transform contract).
14. **Scaling UI to large data.** Cost per frame must follow the screen, not the data: cached views rebuilt only when a
    version number changes, virtualized lists (`ImGuiListClipper`: only rows in view are submitted; items needed off
    screen are included explicitly), stable identities (entity handles, not row indices) for selection, background jobs
    for sorting big tables, request-per-frame thumbnails. Strata's `HierarchyView` walk is linear in visible rows
    (`HierarchyView.cpp:230-264`), its filter marks ancestors once (`266-327`). Pitfall: walking the scene or listing the
    asset directory per frame; selecting by row index.
15. **Multi-selection semantics.** Click, Ctrl+click toggle, Shift range from an anchor, Ctrl+A, box selection, clear on
    void; primary selection is the last clicked; range ends are items not positions. ImGui 1.91+ `BeginMultiSelect`
    returns requests the app applies to its own selection storage (`SceneHierarchyPanel.cpp:1135-1192`). Pitfall:
    letting ImGui own the selection; ranges taking filtered-out context rows.
16. **Reflection-driven inspectors.** Problem: hundreds of component properties should not each need UI code.
    Approaches: code generation from headers (Unreal's UPROPERTY/UHT), runtime reflection with attributes (Unity's
    serialized fields), hand-written registration tables (Strata's `ComponentRegistry`/`PropertyInfo`). Strata: metadata
    (type, range, speed, sections, tooltips, flags, inactive reason) drives a generic widget per type
    (`DrawPropertyWidget`), with escape hatches (component drawers, property drawers). Multi-edit (mixed values, per-axis
    writes), undo merging across a drag, prefab override marks. Pitfalls: writing every frame of a drag as its own undo
    step; reading Euler angles back from a quaternion (they fold), which `PropertyEditResult` avoids by carrying the
    angles the widget showed (`PropertyWidgets.h:28-32`).
17. **The viewport: render-to-texture inside a UI.** The 3D view renders offscreen at the panel's pixel size and is shown
    as an image item; input goes to the view only while hovered/focused; overlays (gizmos, legends, labels) are UI drawn
    over the image. Editor cameras: orbit around a pivot, pan at the pivot's depth (`2·d·tan(fov/2)/height` units per
    pixel), multiplicative dolly, fly mode with locked cursor; framing a bounding sphere in the narrower field of view
    (`EditorCamera.cpp:70-134`). Pitfalls: mouse deltas on the first frame of a drag; non-finite deltas; dragging the
    window instead of the camera.
18. **Picking.** Approaches: CPU ray casts against bounds/triangles, or a GPU entity-ID buffer read back at the pixel.
    Strata: the ID buffer, read *asynchronously* (no stall) and applied a few frames later only if the same scene is
    still shown (`EditorViewport.cpp:415-452`); UI elements are picked on the CPU first. Pitfall: blocking readbacks
    (a frame-long stall per click); picking against a resized image.
19. **Transform gizmos.** Screen-space handles that turn mouse motion into translation/rotation/scale of a matrix;
    world vs local axes; snapping; multi-object edits relative to a primary; recomputing local transforms under parents;
    one undo step per drag computed from the drag's start state (no drift). Strata: ImGuizmo + `TransformDrag`
    (`TransformEdit.h:53-90`). Pitfalls: ImGui items stealing the click (Strata swaps the image item for a `Dummy` over
    the gizmo, `ViewportPanel.cpp:149-162, 198-206`); a drag continuing after its entity was deleted.
20. **Scene view vs game view, and who owns input.** The editor's camera vs the game's camera; aspect-ratio
    letterboxing and fixed resolutions; mouse positions in the game's pixels; cursor lock that must not trap the person
    (Shift+F1); play-mode edits apply to a copy. Pitfall: the game reading input while the person types in the
    Inspector.
21. **Keyboard shortcuts and focus.** Global vs focus-scoped shortcuts; text fields keep their keys; modals block;
    play mode filters edit shortcuts; layouts and macOS Cmd. Strata routes with `ImGui::Shortcut` flags
    (`EditorLayer.cpp:951-985`, `EditorActions.cpp:318-338`). Pitfall: Delete in the Content Browser deleting entities.
22. **Feedback without interruption.** Status bars with pills that lead somewhere, toasts that never take focus, errors
    counted as unread, compact text when space runs out. Pitfall: modal error dialogs for routine failures.
23. **Power: idle throttling.** An immediate-mode UI redraws every frame; editors idle at a low rate when nothing
    happens and run uncapped while someone waits by frames. The displayed frame time must be work time, not the
    capped interval. Strata: `EditorLayer::UpdateFrameRate` (`900-919`). Pitfall: an animation that freezes because
    its panel did not report `IsAnimating`.
24. **Modality and data safety in UI.** The UI half of "never lose work": ask before replacing a scene, re-ask if it
    changed while asking, draw nested questions inside the current modal. Pitfall: opening a modal from inside a modal
    at the top level (it closes the first).
25. **Testing a UI without a screen.** A real ImGui context without window or GPU, injected input over frames (hover,
    press, release), widgets found by probe keys, lints over the source for rules a compiler cannot check, perf budgets
    for panels with huge data. Strata: `ImGuiHarness`, `ItemProbe`, `Editor.UI.Source`. Pitfall: tests that click by
    coordinates.
26. **Settings UIs from schemas.** Settings sections registered with fields generate pages; complex sections get custom
    pages; edits run commands; pages draw from copies refreshed by version. Strata: `SettingsBrowser` and the page
    registry (`SettingsPages.h:23-121`).

---

## 3. Code worth showing

| # | File and lines | What it teaches | Reader must know first |
| --- | --- | --- | --- |
| 1 | `Strata/src/Strata/ImGui/ImGuiModule.cpp:54-64` | The whole UI frame in ten lines: Begin, layers draw, back buffer, End | Layers, engine modules, frame loop |
| 2 | `Strata/src/Strata/ImGui/ImGuiLayer.cpp:88-109` | Event capture: the overlay sees events first and swallows what ImGui wants | Events and the layer stack |
| 3 | `ImGuiLayer.cpp:169-177` and `217-232` | DPI: `ToUIScale` and rebuilding the style from unscaled defaults | Content scale, points vs pixels |
| 4 | `Strata/src/Strata/ImGui/ImGuiPlatform.cpp:162-184` | Modifiers queued before keys; a release matches its press across layout changes | Keyboard layouts, ImGui input queue |
| 5 | `ImGuiPlatform.cpp:206-221` | Cursor shape set only on change and only while the game does not own the cursor | Cursor modes |
| 6 | `Strata/src/Strata/ImGui/ImGuiRenderer.cpp:407-518` (central algorithm) | Rendering draw data: buffer acquisition, texture updates, ortho push constants (457-462), clip to scissor (491-503), draw callbacks, global offsets | Draw data layout, NVRHI command lists, push constants |
| 7 | `ImGuiRenderer.cpp:314-342` | Frames in flight without staging: a bounded ring of mapped buffers guarded by event queries | GPU/CPU asynchrony, fences |
| 8 | `ImGuiRenderer.cpp:216-253` | ImGui 1.92 dynamic textures: WantCreate/WantUpdates/WantDestroy | Font atlas idea, textures |
| 9 | `ImGuiRenderer.cpp:73-107` | Why callbacks are told apart by data address (identical code folding) | Function pointers, linkers |
| 10 | `Strata/shaders/ImGui.vert.slang:20-25` + `ImGui.frag.slang:26-46` | The tiniest shader pair; sRGB encode and normal-map Z reconstruction for previews | Shaders, color spaces |
| 11 | `StrataEditor/src/UI/Theme.cpp:92-171` and `253-270` | Role table + `static_assert(std::size(c_ColorRoles) == ImGuiCol_COUNT)`; tokens to meanings | Pointers to members, constexpr |
| 12 | `StrataEditor/src/UI/EditorFonts.cpp:77-97` | Merging an icon font into a text font with excluded ranges, offset and min advance | Font atlas, Unicode PUA |
| 13 | `EditorFonts.cpp:131-197` | Background font loading on an I/O job, merged between frames; glyph generation counter | Job system, ownership with `Ref` |
| 14 | `StrataEditor/src/UI/Widgets.cpp:62-122` | Anatomy of a custom immediate-mode widget (InvisibleButton, states, draw list, nav cursor, tooltip, probe) | ImGui items, draw lists |
| 15 | `Widgets.cpp:218-279` | Layout decided from the previous frame (chip strip); a subtle IMGUI technique | #14 |
| 16 | `StrataEditor/src/UI/ItemProbe.cpp:25-52` | A test hook that costs one hash-map write per widget and frame | Hash maps, frame counters |
| 17 | `StrataEditor/src/UI/EditorPanelRegistry.h:60-93` | The panel interface and descriptor: lifecycle hooks as a contract | Virtual interfaces, `std::function` |
| 18 | `StrataEditor/src/UI/EditorPanelRegistry.cpp:168-246` | Drawing panels: focus requests deferred behind modals and retried, tab selection without focus, `OnHidden` | Docking, focus |
| 19 | `EditorPanelRegistry.cpp:330-345, 386-424` | Extending imgui.ini with a custom settings handler | ImGui settings |
| 20 | `StrataEditor/src/EditorLayer.cpp:726-795` | The editor's UI frame, top to bottom, and where toasts go | #1, #17 |
| 21 | `EditorLayer.cpp:1320-1360` | A default dock layout from proportions with font-size minimums | DockBuilder |
| 22 | `EditorLayer.cpp:951-985` + `StrataEditor/src/UI/EditorActions.cpp:318-338` | Global vs focus-routed shortcuts and their guards | ImGui shortcut routing |
| 23 | `EditorLayer.cpp:848-919` | Idle throttling as a policy: busy detection, uncapped work, idle caps | Frame pacing |
| 24 | `EditorLayer.cpp:1872-1898, 1938-1944` | Status bar with hysteresis between full and compact texts | #15 |
| 25 | `StrataEditor/src/Editor/HierarchyView.cpp:134-151, 230-264` (central algorithm) | Version-gated rebuild; iterative depth-first walk of first-child/next-sibling links with a resume stack | ECS hierarchy component, versions |
| 26 | `HierarchyView.cpp:266-327` | Filtering with ancestors marked once (linear in the scene) | #25 |
| 27 | `HierarchyView.cpp:555-610` | Mapping a drop position to (parent, index), with the off-by-leaving correction and cycle refusal | Scene hierarchy edits |
| 28 | `StrataEditor/src/Panels/SceneHierarchyPanel.cpp:655-731` and `1135-1192` | `BeginMultiSelect` + `ImGuiListClipper` + selection requests applied to the app's storage | #25, ImGui multi-select |
| 29 | `StrataEditor/src/Panels/ContentBrowserPanel.cpp:858-933` | Clipping a grid by rows; thumbnails requested per visible tile | #28 |
| 30 | `StrataEditor/src/Panels/InspectorPanel.cpp:915-1025` (central algorithm) | Generated inspector: groups by section once per type, label + drawer or generic widget, mixed values, per-axis multi-edit, undo merge break | Reflection (`Property.h:22-112`), undo |
| 31 | `StrataEditor/src/UI/PropertyWidgets.cpp:892-960` | Type switch from `PropertyType` to widgets (Bool, Int, UInt special cases, Float, vectors) | `std::variant`, #30 |
| 32 | `StrataEditor/src/Panels/ViewportPanel.cpp:149-162, 198-206` | Cooperating with ImGuizmo: no item under the gizmo, no window move | ImGui hovering, gizmos |
| 33 | `ViewportPanel.cpp:867-920` + `StrataEditor/src/Editor/EditorCamera.cpp:43-91, 117-134` | Camera drags and the orbit/pan/dolly/focus math | Vectors, yaw/pitch, field of view |
| 34 | `ViewportPanel.cpp:936-995` | Gizmo drag lifecycle with `TransformDrag`, snapping inverted by Ctrl, cancelling | Matrices, undo |
| 35 | `StrataEditor/src/Editor/EditorViewport.cpp:415-452` | Asynchronous picking with a readback and stale-result rejection | GPU readback |
| 36 | `StrataEditor/src/Panels/GameViewPanel.cpp:241-281` | Input ownership between editor and game; cursor lock and `NoMouse` | Input module, cursor modes |
| 37 | `StrataTests/src/Editor/ImGuiHarness.cpp:118-132` | Clicking a widget in a test: hover, press, release over three frames | ImGui's frame-delayed hover |
| 38 | `StrataTests/src/Editor/EditorUISourceTests.cpp:499-545` | Lint rules as tests (colors, sizes, panels, fonts) | Regex/source scanning |

(38 rows: the planner can keep the 30 best; #6, #25 and #30 are the area's central algorithms.)

---

## 4. Figures

### Diagrams

1. **Architecture stack** (layer diagram): `EditorApplication` → `EditorLayer` (EditorShell) → `EditorPanelRegistry` →
   panels; `EditorHost` arrow to `Application`; core underneath (`EditorContext`, commands, runner, automation); engine
   `ImGuiModule` → `ImGuiLayer` → `ImGuiPlatform` / `ImGuiRenderer` → NVRHI; Tooling boundary marking what games omit.
   Source: AR 3219-3237.
2. **Retained vs immediate mode** (side-by-side data flow): widget tree with callbacks vs per-frame code → ImGui state
   by ID → draw data.
3. **One editor frame** (timeline): window events (ImGuiLayer first) → layers' `OnUpdate` (panels' `OnUpdate`) →
   `Editor.UI` stage: `ImGuiLayer::Begin` (scale check, `NewFrame`) → `EditorLayer::OnImGuiRender` (TrackInput,
   BindingCapture, CancelDragDrop, launcher or shortcuts/dockspace/panels, dialogs, modal, toasts, UpdateFrameRate) →
   `PrepareBackBuffer` → `ImGui::Render` → `ImGuiRenderer::Render` → execute.
4. **Draw data memory layout**: `ImDrawData` → `CmdLists[]` each with `VtxBuffer` (pos 8 B, uv 8 B, col 4 B = 20 B per
   vertex), `IdxBuffer` (u16) and `CmdBuffer` (ClipRect, TexID, ElemCount, IdxOffset, VtxOffset, UserCallback) → all lists
   copied into one mapped vertex and one index buffer, with the global offsets the draw arguments add.
5. **Pixel → NDC mapping**: a window rectangle with y down and its NDC square with y up; the scale/translate formula.
6. **Buffer ring state machine**: Free → Written (this frame) → Pending (event query set after submit) → Free when the
   query is done; growth up to 8 sets; wait on the oldest beyond that.
7. **UI scale computation**: content scale, framebuffer/window ratio (points platforms), factor (Preferences), override
   (`--ui-scale`), clamp [0.5, 4] → `ScaleAllSizes` + `FontScaleDpi`.
8. **Theme mapping**: 16 palette tokens → `ThemeColors` meanings → `ImGuiCol_` roles (a few arrows each), plus where the
   axis colors reappear (gizmo, vector fields).
9. **Font atlas composition**: Inter Regular + Lucide (PUA E000-F8FF, 0.9 scale, +2 px) + CJK fallback (merged behind,
   PUA excluded); SemiBold same; Mono without icons.
10. **Anatomy of a kit widget**: InvisibleButton rectangle, background, icon, label, nav cursor, tooltip, probe entry.
11. **Chip strip over two frames**: frame N measures widths, destructor decides `FirstIcon` and `RowStarts`; frame N+1
    draws icons / rows.
12. **Panel lifecycle** (state machine): registered → open/closed (View menu, tab close, ini) → each frame OnUpdate;
    visible → OnImGuiRender; hidden/collapsed/behind tab → OnHidden; Focus request → retried ≤ 4 frames, deferred while
    a modal is open.
13. **Default dock layout** with proportions (Hierarchy 15%, Inspector/Asset 20%, bottom 22% with its six tabs, center
    Scene/Game/Project Settings) and the layout-version rule.
14. **HierarchyView: tree to rows to screen**: scene tree with expanded/collapsed nodes → flat row vector with depths
    (resume stack shown) → clipper window over the rows; filtered variant: matches (solid) and marked ancestors (dim).
15. **Drop zones on a row**: quarters → Before / Inside / After, and the special "after an expanded row" case.
16. **Multi-select request flow**: ImGui → `ImGuiMultiSelectIO` requests (SetAll, SetRange) → `ApplySelectionRequests`
    → `EditorContext::SetSelection` → next frame's `IsSelected`.
17. **Generated inspector pipeline**: `ComponentRegistry` → `ComponentInfo::Properties` (with Section, flags,
    InactiveReason) → `GetPropertyGroups` → `DrawPropertyRow` → PropertyDrawer? or `DrawPropertyWidget` →
    `SetPropertyWithUndo` / components / rotation edit → `UndoStack` (merge until `Finished`).
18. **Viewport composition**: toolbar strip (chips, agent chip) over the image; image = offscreen render target; overlays
    (gizmo, legend, labels, text boxes, toasts in the view's corner).
19. **Editor camera geometry**: target, distance, yaw around +Y, pitch clamp ±89°, position = target − forward·distance;
    pan's units per pixel at the target's depth; focus distance r·1.1/sin(halfAngle).
20. **Async pick timeline**: click at frame N → `ReadEntityIDAsync` → readback ready at N+k → scene still active? →
    `ApplyPick`; timeout path.
21. **Gizmo drag sequence**: `Manipulate` changed → `TransformDrag::Begin` (snapshot) → `Update` per frame
    (WorldToLocal under parent) → release → `End` (one undo step); while playing no undo.
22. **Input ownership in play mode**: who gets keyboard/mouse (Game view focused, playing → `Input` enabled; cursor
    locked → ImGui NoMouse; Shift+F1 → editor); chips with NoFocus.
23. **Shortcut routing**: global (modal check → Ctrl+P → AcceptsEditShortcuts → others) vs focused (Hierarchy/Viewport
    windows) vs text fields.
24. **Idle throttling decision** (flowchart): throttling enabled? → uncapped work? → busy? → cap = active / idle /
    unfocused idle; plus the stepping lift.
25. **Status bar hysteresis**: available width vs full width with the 2-font-size margin, states Full/Compact.
26. **Notification lifecycle**: Post (merge/group, count) → shown (expiry by level, KeepAlive on hover) → Replace →
    Dismiss/Expire; at most 4.
27. **Unsaved-changes question**: RequestDiscardChanges → saves in flight? (saving modal) → modified? → modal (Save /
    Don't Save / Cancel) → version changed? re-ask → action with `force: true`.
28. **Test harness**: FakeEditorHost + ImGui context + EditorLayer; input queue; ItemProbe lookup; `ClickItem` over three
    frames.

### Screenshots

All editor screenshots can be produced by a command script: `StrataEditor --project <copy of a sample> --windowed
--ui-scale <s> --commands shots.json --screenshot out.png --quit-after-commands` (`EditorApplication.cpp:63-79`;
`EditorLayer::TakeScreenshot`), with `editor.showPanel`, `editor.showDialog`, `selection.set`, `viewport.setSettings`,
`camera.set` and the Hierarchy's `search` parameter steering what shows. Use a copy of `Samples/ThirdPerson` or
`Samples/Showcase` (`Tests::CopySampleProject` style; never the sample in place).

1. The whole editor in its default layout on a sample, 1600x900 at 100%, annotated with panel names.
2. The same at `--ui-scale 2` (same layout, crisp sizes) beside 100%, to show UI scaling.
3. ImGui's default dark style (`--imgui-demo`, Help > ImGui Demo) beside Bedrock, to show what the theme changes.
4. A zoomed crop of the widget kit: toolbar buttons (normal, active, primary, disabled), chips (off, on, on-but-idle),
   pills in each meaning color, section header with summary, cards, entry card, progress bar, legend.
5. The launcher with recent projects (pictures), template and sample cards, "Connect an AI agent" and footer.
6. New Project dialog; Open Sample dialog.
7. Hierarchy: a tree with expanded groups, prefab badges, an inactive dimmed entity; then the same with search
   `c:Light` (matches plus dimmed ancestors); rename in place.
8. Hierarchy drag in progress showing the drop line (before/after) and the inside highlight.
9. Content Browser grid with thumbnails, an expanded model's sub-asset band; the list view; the Scripts root.
10. Inspector with one entity (Transform axis labels in X/Y/Z colors, sections); with three entities selected showing
    mixed "--" values.
11. Inspector on a prefab instance: prefab bar, overridden labels with the accent bar, the Overrides menu open.
12. An inactive property with its tooltip (e.g. Bloom threshold while Bloom is off); Directional Light's "Shadow maps"
    line.
13. Post Process TAA preset drawer; Add Component popup with filter.
14. Asset tab: a material being edited; a normal-map texture preview (NormalXY display) next to a raw view for contrast;
    an audio clip waveform.
15. Scene view with the translate, rotate and scale gizmos on a selected crate (three crops), World vs Local.
16. Scene view toolbar wide (labels) vs narrow (icons, wrapped rows) to show `ChipStrip`.
17. Scene view with the LOD debug view and its legend (`viewport.setSettings {debugView: "lod"}`), and the stats overlay
    (`stats: true`).
18. The agent chip and the accent outline flash after an automation command (take with a live command script).
19. Dragging a prefab from the Content Browser over the Scene view: the box ghost and its label.
20. Canvas mode on a UI canvas (handles, outlines).
21. Game view in play mode: 16:9 letterboxed in a tall panel; 1920x1080 fixed scaled to fit; the "no camera" notice;
    the locked-cursor hint.
22. Status bar: full texts and compact texts (narrow window at 150%); the errors pill; the assets pill in Sulfur.
23. Toasts stacked at the bottom right of the Scene view with their action buttons.
24. Project Settings: Graphics Quality page; Collision Layers matrix; Input Actions page with a binding capture
    listening.
25. Preferences: Interface and Frame Rate pages.
26. Activity panel with a selected entry's JSON and its buttons; Problems panel after a failed build; Console with a
    clickable source reference.
27. Performance panel timeline (CPU and GPU) and Streaming panel with the World cell map.
28. About Strata dialog; Export Game dialog during an export.
29. The unsaved-changes question (Save / Don't Save / Cancel).
30. A CJK project name rendering through the fallback fonts (launcher card or window title).

---

## 5. Rules and pitfalls ("why" boxes)

1. **Colors only from theme tokens** (`Theme.h`); no numbers spelled as colors outside `Theme.cpp`. *Why:* one look
   across a UI many people and agents write; colors carry meaning (axis, play state, errors); an ImGui upgrade with new
   color slots fails the build instead of shipping default colors. Enforced by `static_assert` (`Theme.cpp:171`) and
   `Editor.UI.Source`.
2. **Sizes relative to the font**, no fixed pixels above 16. *Why:* the UI must follow display density and the
   person's interface scale; fixed widths clip text at 200%. Even base sizes keep 150%/200% pixel-exact.
3. **Panels never call `ImGui::Begin`**: they register with `EditorPanelRegistry`. *Why:* the registry gives View menu
   toggles, open states in imgui.ini, stable `###id` window names, focus and tab handling, `OnHidden`.
4. **Text through the editor's fonts; never ImGui's built-in font; icons are text.** *Why:* consistent type, icons
   align with text; the monospace font has no icons (fallback glyph), so draw swatches as rectangles.
5. **UTF-8 once**: non-ASCII as `\x` escapes or plain UTF-8. *Why:* text pasted through a Latin-1 tool turns "·" into
   "Â·".
6. **Controls from the widget kit**, every kit widget recorded in `ItemProbe`. *Why:* consistent behavior and tests
   that find widgets by key, not coordinates.
7. **Every change through a command** (or `SceneEditTransaction`/`SetPropertyWithUndo` for continuous edits); panels
   never write, move or remove files. *Why:* undo, the activity journal, automation parity and data safety. Enforced
   for files by a scan.
8. **UI commands carry `CommandOrigin { CommandSource::UI }`** (through `RunEditorCommand`). *Why:* the journal says
   who did what; toasts show the person's failures only.
9. **Never walk the scene or the asset directory per frame; draw cached views rebuilt on version changes; clip long
   lists.** *Why:* a 100,000-entity scene or 10,000-asset project must cost what the screen shows (tests prove an idle
   frame rebuilds nothing).
10. **Rows identify themselves by entity handle/UUID, never by row index.** *Why:* rows appear and disappear as the tree
    expands; an index range would select the wrong entities.
11. **Don't change the scene while iterating its rows**: schedule (`m_Deferred`, `SchedulePrefabCommand`). *Why:*
    commands may destroy or remake entities the rest of the frame still reads.
12. **Selection shortcuts are focus-routed; global shortcuts check modals and `AcceptsEditShortcuts`.** *Why:* Delete
    in the Content Browser must not delete entities; keys the running game uses (Ctrl+D to crouch) must not edit.
13. **Chips never take focus** (`ImGuiButtonFlags_NoFocus`). *Why:* clicking a chip over the Game view must not hand
    the keyboard away from the game, or to it.
14. **Toasts never take focus and cost nothing while empty.** *Why:* information without interruption, no frame cost.
15. **A modal that asks while open draws the question inside itself** (`DrawDiscardQuestion`). *Why:* ImGui keeps one
    popup per level; a modal opened over the whole window closes the one that is open.
16. **Focusing a panel while a modal waits is deferred.** *Why:* focusing a window closes popups above it.
17. **Write costly tooltips only while due** (`UI::IsTooltipDue`). *Why:* widgets drawn every frame would format
    statistics every frame for nothing.
18. **Draw textures through `UI::TextureImage`.** *Why:* sRGB, grayscale and two-channel normal maps look wrong as
    stored; previews must show what materials read.
19. **Show work time, not the frame interval.** *Why:* an idle editor capped at 30 fps would read as a slow one.
20. **A panel that animates without input reports `IsAnimating`.** *Why:* the idle throttle would otherwise drop it to
    the idle frame rate.
21. **Frames that run work someone waits for by frames are never capped** (`RunsUncapped`). *Why:* stepping a paused
    game or an agent waiting for N frames must not take N/10 seconds.
22. **Build the style from unscaled defaults every time.** *Why:* scaling an already-scaled style compounds.
23. **The renderer's user textures must outlive the frame's draw data**; binding sets keep them 8 frames. *Why:* the GPU
    reads them after `Render` returns.
24. **Never identify draw callbacks by function address.** *Why:* linkers merge identical functions (ICF); Strata uses
    the user-data address.
25. **A key release is the key its press was queued as**; modifiers are queued before keys. *Why:* a layout switch
    between press and release would leave a key stuck; chords read the modifiers queued before.
26. **ImGuizmo starts a drag only while no item is hovered**: the viewport image becomes a `Dummy` over the gizmo.
    *Why:* otherwise the image button wins the click and the gizmo never moves.
27. **A gizmo drag is one undo step computed from its start state.** *Why:* incremental application drifts and floods
    the undo history.
28. **Picking never stalls**: async readback, dropped when the scene changed. *Why:* a blocking readback costs a frame
    per click; a late result must not select in another scene.
29. **The game gets input only while the Game view is focused in play; Shift+F1 always leaves.** *Why:* typing in the
    Inspector must not move the character; a locked cursor must never trap the person.
30. **An active `InputText` keeps its own copy of the text**: replacing it from outside needs a reload
    (`SearchField`'s `reload`). *Why:* otherwise the field writes its old text back over the new.
31. **Thumbnails are requested every frame they are on screen**, the type icon drawn until ready. *Why:* the cache
    renders what is wanted now and lets the rest go.
32. **Settings pages draw from copies refreshed by version, never parsing per frame.** *Why:* cost and consistency.
33. **Scripted runs never overwrite the user's layout** (no layout file with `--frames`). *Why:* a test must not change a
    person's editor.
34. **Bump `c_LayoutVersion` when the default layout gains a panel open by default.** *Why:* old layouts would show it
    floating over the viewport.
35. **A property another property can switch off gets an `InactiveReason`.** *Why:* the person sees why a value does
    nothing instead of tuning it in vain.

---

## 6. Hands-on

### For engine developers

| Exercise | Difficulty | Proves |
| --- | --- | --- |
| Trace one frame: set breakpoints in `ImGuiModule::OnRenderUI`, `EditorLayer::OnImGuiRender`, `ImGuiRenderer::Render`; count draw lists and commands for the default layout | Easy | The frame pipeline (concepts 3-5) |
| Compute by hand the push constants for a 1600x900 display and check them against `ImGuiRenderer.cpp:457-462` | Easy | Pixel → NDC mapping |
| Add a theme meaning (e.g. `ThemeColors::Highlight`) and use it; then try a hex color in a panel and watch `Editor.UI.Source` fail | Easy | Tokens vs meanings, the lint |
| Write a new kit widget (e.g. a segmented toggle) in `Widgets.h/.cpp` with probe keys, and a harness test that clicks it | Medium | Custom IMGUI widgets, `ItemProbe`, harness |
| Add a docked panel ("Selection Summary") through `RegisterBuiltinPanels`, open by default: see it in the View menu, `editor.showPanel`, persistence; then bump `c_LayoutVersion` and dock it | Medium | Panel registry, layout versioning |
| Add a status pill with a compact text through `StatusPillText`, clicking it focusing a panel; test at 150% in a narrow window | Medium | Status bar hysteresis |
| Add a hierarchy filter term (e.g. `a:` for inactive entities) in `HierarchyFilter::Parse`/`Matches` with `Editor.HierarchyView` tests | Medium | Cached views, signals |
| Measure: generate 100,000 entities and compare frame cost with and without the clipper (scratch build, do not commit) | Medium | Virtualization |
| Register a `PropertyDrawer` for some property (e.g. a light's color temperature as a gradient bar) | Medium-hard | Reflection escape hatches |
| Add an inactive reason to a component property next to its registration and see the Inspector disable it | Easy | `SetInactiveReason` |
| Add a viewport key (e.g. G toggles the grid) following the routing guards in `ViewportPanel::HandleShortcuts` | Easy | Shortcut routing and focus |
| Write a panel that animates (a spinner) and observe idle throttling; fix it with `IsAnimating` | Easy | Idle throttling |
| Write a toy renderer backend for ImGui in a separate tiny program (any API) from `ImGuiRenderer::Render`'s logic | Hard | Renderer backends end to end |
| Add a source-scan rule to `EditorUISourceTests.cpp` (e.g. no `ImGui::Text` with a literal colored via `TextColored` numbers) with its self-test | Hard | Lints as tests |

### For game developers

| Tutorial | Difficulty | Proves |
| --- | --- | --- |
| First launch: New Project with Basic 3D, find each panel, reset the layout, set Preferences > Interface to 125% | Easy | Navigating the editor |
| Build a small scene with the Hierarchy and Inspector: create, rename (F2), reparent by drag, multi-select and edit mixed values, Copy/Paste Values, undo/redo | Easy | Hierarchy and Inspector workflow |
| Move around the Scene view (orbit, pan, dolly, fly, F, Home), use the gizmos (W/E/R/Q), World/Local, snapping with Ctrl inversion | Easy | Viewport controls |
| Import assets, browse thumbnails, drag a model into the view (ghost), make and tweak a material | Easy | Content Browser and Asset tab |
| Play, switch Game view resolutions, use Pause/Step, leave a locked cursor with Shift+F1, F8 game camera | Easy | Play testing |
| Make a prefab, override values on an instance, Apply/Revert through the Inspector | Medium | Prefab overrides UI |
| Name collision layers, bind an input action by pressing the key, choose a Graphics Quality preset | Medium | Project Settings |
| Break a script build and follow the pills and toasts to Problems; use Activity's Undo to here and Copy as script | Easy-medium | Reading the editor's feedback |
| Search the Hierarchy with `c:`, `t:` (and `l:`/`cell:` in a world) | Easy | Filters |
| Connect an AI agent from the launcher; watch the agent chip and the outline flash; inspect its commands in Activity | Easy | Working alongside agents |

---

## 7. Glossary

- **Immediate-mode GUI (IMGUI)**: UI described by code every frame; the library keeps little state, keyed by IDs.
- **Retained-mode GUI**: UI kept as a tree of widget objects with state and callbacks.
- **Dear ImGui**: the C++ immediate-mode library Strata uses (1.92.9, docking branch).
- **ImGui context**: all of ImGui's state for one UI (windows, settings, input queue, fonts).
- **ID / ID stack**: the hash ImGui identifies a widget by, built from labels and pushed scopes.
- **`##` / `###`**: label suffixes: text after `##` is hidden but part of the ID; `###` makes only what follows the ID.
- **Item**: anything ImGui submitted (a button, a text field); "last item" queries refer to the most recent one.
- **Window / child window**: top-level or nested scrolling regions; panels are windows.
- **Popup / modal**: a temporary window; a modal blocks input to everything below it.
- **Dock space / dock node / tab bar**: the area panels dock into, its split nodes and their tabs.
- **DockBuilder**: ImGui's internal API to build a layout from code.
- **imgui.ini**: ImGui's settings file (windows, docking); Strata's is `EditorLayout.ini` with extra sections.
- **Settings handler**: a hook that reads and writes a program's own sections of imgui.ini.
- **Draw list / draw command / draw data**: per-window vertices and indices, the commands that draw ranges of them with
  a clip rectangle and texture, and the frame's collection of lists.
- **Clip rectangle / scissor**: the pixel rectangle a draw command is limited to.
- **Font atlas**: a texture holding rasterized glyphs.
- **Glyph / fallback glyph**: a character's shape; what is drawn for characters a font lacks.
- **Private Use Area (PUA)**: Unicode range U+E000-F8FF where icon fonts put their glyphs.
- **Merge mode**: adding a font's glyphs into another font.
- **Icon font**: a font whose glyphs are icons (Lucide).
- **Content scale / DPI**: the OS's factor for display density.
- **Points vs pixels**: window units on macOS/Wayland (points) vs physical pixels; framebuffer scale relates them.
- **UI scale**: the factor Strata styles the UI with (content scale less the points factor, times preference, or
  override).
- **FontScaleDpi**: ImGui's style field scaling font sizes.
- **Style / style var / style color**: ImGui's appearance settings and the push/pop stacks that change them temporarily.
- **Theme / Bedrock**: Strata's editor look.
- **Token / palette / semantic color**: a named raw color, the set of them, and a color named by its meaning.
- **Type scale**: the fixed set of text sizes (12, 14, 17, 24).
- **Widget kit**: Strata's library of styled controls (`UI/Widgets.h`).
- **InvisibleButton**: an ImGui item with hit testing but no drawing, the base of custom widgets.
- **Nav cursor**: ImGui's keyboard-navigation highlight.
- **Hovered / active / focused**: under the mouse / being interacted with / receiving keyboard input.
- **Shortcut routing (RouteGlobal, RouteFocused)**: which window a key chord goes to.
- **ImGuiListClipper**: helper that computes which rows of a uniform list are visible.
- **Virtualization**: drawing only the visible part of a large list.
- **Multi-select (BeginMultiSelect)**: ImGui's selection protocol that sends selection requests to the app.
- **Selection user data**: the app's identity for an item in multi-select (Strata: the entity handle).
- **Range selection / anchor / box select**: Shift-selection from a first item; dragging a rectangle to select.
- **Primary selection**: the last selected entity, which the gizmo and single-entity UI use.
- **Drag and drop payload**: typed data carried by a drag (`STRATA_ENTITIES`, `STRATA_ASSET`).
- **Item probe**: Strata's per-frame record of widget rectangles for tests.
- **UI harness**: Strata's headless ImGui test rig.
- **Panel / panel registry / descriptor**: a dockable editor window, the object that owns them, its registration record.
- **Launcher**: the start screen shown while no project is open.
- **Editor shell (EditorShell)**: what panels may ask of the editor window.
- **Editor host (EditorHost)**: what the editor UI needs from the application.
- **Toast / notification**: a transient message at the bottom right.
- **Pill**: a small colored status label in the status bar.
- **Chip**: a rounded toggle or menu button on the viewport toolbar.
- **Chip strip**: a row of chips that turns labels into icons and wraps when narrow.
- **Banner, card, entry card, section header**: kit widgets for notices, clickable tiles, list entries, collapsible
  headers.
- **Property table**: the two-column label/widget layout of inspectors.
- **Reflection**: runtime metadata about types and their fields (`ComponentRegistry`, `PropertyInfo`).
- **PropertyInfo / ComponentInfo**: a property's metadata; a component type's registration with its properties.
- **Section (property)**: a heading grouping properties in the inspector.
- **Mixed value**: a property that differs across selected entities, shown as "--".
- **Override (prefab)**: a value an instance holds differently from its prefab.
- **Inactive reason**: why a property has no effect now.
- **Component drawer / property drawer**: custom UI for a whole component / one property.
- **Undo merge**: combining a drag's many changes into one undo step.
- **Viewport / Scene view / Game view**: the editor's 3D view through the editor camera; the game's view through its
  primary camera.
- **Render target / render to texture**: drawing into an offscreen image then shown in the UI.
- **Editor camera; orbit, pan, dolly, fly**: rotating around a pivot; sliding parallel to the view; moving toward the
  pivot; free first-person movement.
- **Framing (Focus, FitBounds)**: moving the camera so bounds fill the view.
- **Gizmo / ImGuizmo**: on-screen handles to translate, rotate and scale; the library Strata uses.
- **World / local space**: gizmo axes along the world or along the entity.
- **Snapping**: rounding drags to steps.
- **Picking / entity-ID buffer / readback**: finding the entity under the cursor from a GPU image of entity IDs copied
  back to the CPU.
- **Debug view / legend**: coloring the image by a property (LOD, streaming, mip) and the key to its colors.
- **Letterboxing**: bars around an image kept at an aspect ratio.
- **Game camera (pilot)**: the Scene view looking through the scene's primary camera (F8).
- **Cursor lock**: the game hiding and capturing the mouse.
- **Idle throttling**: lowering the editor's frame rate when nothing happens.
- **Frame work time**: CPU time a frame costs without waits.
- **Status provider**: a section of `editor.status` an editor part reports.
- **Notification group**: notifications merged into one toast with a count.
- **Binding capture**: listening for the next control pressed to bind an input action.
- **Settings section / settings page / settings browser**: a registered block of settings, its page, the window listing
  pages.
- **ImGuiTextureDisplay**: Strata's display modes for previews (Direct, EncodeSRGB, Grayscale, NormalXY).
- **Binding set**: NVRHI's group of resources bound for a draw.
- **Event query**: an NVRHI GPU fence-like object telling when submitted work finished.
- **Frames in flight**: frames the GPU is still working on while the CPU prepares the next.
- **Push constants**: small data sent with a draw without a buffer.
- **Dynamic textures (ImGui 1.92)**: textures ImGui asks the backend to create, update and destroy.
- **NVRHI**: NVIDIA's rendering hardware interface Strata renders through.
- **nfd**: nativefiledialog-extended, the native file picker library.
- **Inter, JetBrains Mono, Lucide**: the editor's text, monospace and icon fonts.
- **CJK**: Chinese, Japanese and Korean scripts.

---

## 8. Proposed chapters (teaching order)

1. **A tour of the Strata editor** (game devs; tutorial; L; ~18 screenshots). Purpose: launch, create a project, find
   every panel, move in the Scene view, edit with Hierarchy/Inspector, play in the Game view, read the feedback.
   Prerequisites: installing Strata.
2. **What an editor is, and why its UI is immediate mode** (both; concept; S). Tools vs runtime, Tooling layers,
   retained vs immediate mode, why Dear ImGui. Prerequisites: none.
3. **Dear ImGui from first principles** (engine; concept + tutorial; M). Frames, windows, items, IDs, popups, docking;
   small exercises in a scratch layer. Prerequisites: C++ basics, chapter 2.
4. **Plugging ImGui into an engine: the platform and renderer backends** (engine; internals; L; 0 screenshots, 5
   diagrams). `ImGuiModule`, `ImGuiLayer`, `ImGuiPlatform`, `ImGuiRenderer`, shaders, frames in flight, dynamic
   textures, texture display modes. Prerequisites: chapter 3, Window/events, NVRHI basics, shaders, color spaces.
5. **Pixels, points and the UI scale** (engine; internals; S-M). Content scale, `ToUIScale`, even base sizes, fonts'
   DPI, Preferences > Interface, `--ui-scale`. Prerequisites: chapter 4.
6. **A design system for tools: theme, fonts, icons** (engine; internals; M; 3 screenshots). Bedrock tokens and
   meanings, `ApplyTheme`, font atlas and icon merge, CJK fallback, `Icons.h` generator, the source scans.
   Prerequisites: chapters 3, 5.
7. **The widget kit: writing custom immediate-mode widgets** (engine; tutorial + internals; M; 2 screenshots).
   Anatomy of a widget, chips and the chip strip, pills, modals, the item probe. Prerequisites: chapter 6.
8. **The editor shell: host, layer, docking and panels** (engine; internals; L). `EditorHost`, `EditorShell`,
   `EditorLayer`'s frame, the panel registry, default layout and versions, menus and toolbar, dialogs and the
   unsaved-changes question. Prerequisites: chapter 7; editor core (context, commands, undo).
9. **Lists that scale: cached views, clipping and multi-select** (engine; internals; L). `HierarchyView`,
   `AssetBrowserView`, `ImGuiListClipper`, multi-select requests, drop zones, thumbnails per frame, background tables.
   Prerequisites: chapter 8; ECS hierarchy; asset manager versions.
10. **Inspectors generated from reflection** (engine, with a game-dev sidebar; internals; L; 4 screenshots). Property
    metadata to widgets, mixed values, undo merge, sections, inactive reasons, drawers, prefab overrides, material
    editor, scene settings. Prerequisites: reflection chapter, undo, prefabs.
11. **The Scene view: render to texture, cameras, picking and gizmos** (both; internals; XL; 8 screenshots).
    `ViewportPanel`, toolbar and chips, editor camera math, async picking, ImGuizmo + `TransformDrag`, debug view
    legends, drop and ghost, agent chip, canvas mode. Prerequisites: chapter 8; renderer overview (scene renderer,
    readbacks); transforms and matrices; placement.
12. **The Game view and who owns input** (both; internals; M; 3 screenshots). Resolution modes, letterboxing,
    `Input::SetViewport`, cursor lock, Shift+F1, Play/Stop tab switching. Prerequisites: chapter 11; Input module.
13. **Shortcuts and focus** (both; concept + reference; S). Global vs focused routing, guards, the full shortcut table.
    Prerequisites: chapter 8.
14. **Telling the person what happens: status bar, toasts and idle throttling** (engine; internals; M; 3 screenshots).
    Pills and hysteresis, notifications core and UI, work time vs frame rate, `Editor.FrameRate`. Prerequisites:
    chapter 8; profiler/frame pacing.
15. **The launcher, dialogs and settings windows** (both; internals + tutorial; M; 6 screenshots). Welcome panel, New
    Project/Open Sample, About, Export, Recovery, Delete; Settings browser, generic and custom pages, binding capture,
    Preferences. Prerequisites: chapter 8; settings registry; project/recent projects.
16. **The instrument panels: Console, Problems, Activity, Streaming, Performance** (both; internals; M; 5 screenshots).
    What each shows and how each keeps its cost low. Prerequisites: chapters 9, 14; profiler; asset streaming;
    command journal. (Could be split across the profiler, streaming and automation chapters instead.)
17. **Testing a user interface without a screen** (engine; internals; M). `ImGuiHarness`, `FakeEditorHost`, probes,
    click over frames, source scans, panel perf tests. Prerequisites: chapters 7, 8; testing chapter.
18. **Editor UI reference** (both; reference; M). Panels and ids, menus, shortcuts, chips, pills, preferences, command
    line options, probe-key conventions. Prerequisites: none (lookup).

---

## 9. Not determined

- **Read only in part** (header and the parts named above): `InspectorPanel.cpp` (read ~250 of 1,728 lines),
  `PropertyWidgets.cpp` (dispatch only), `ContentBrowserPanel.cpp` (grid only), `SceneHierarchyPanel.cpp` (rows and
  selection only), `EditorLayer.cpp` (menus, pills, dialogs' bodies skimmed), `ViewportPanel.cpp` (chips, legend, agent
  flash, placement skimmed), `Notifications.cpp`, `Widgets.cpp` (cards, links, elision, legend not read line by line).
- **Not read beyond the header comment**: `WelcomePanel.cpp`, `StreamingPanel.cpp`, `PerformancePanel.cpp`,
  `ActivityPanel.cpp`, `ProblemsPanel.cpp`, `ConsolePanel.cpp`, `AssetInspectorPanel.cpp`, `GameViewPanel.cpp` (except
  input routing), `CanvasModeView.cpp`, `ViewportToolbar.cpp`, `AnimationAssetViews.cpp`, `CellMap.cpp`,
  `InputActionsPage.cpp`, `GraphicsQualityPage.cpp`, `CollisionLayersPage.cpp`, `SettingsPages.cpp`,
  `ExportDialog.cpp`, `RecoveryDialog.cpp`, `ProjectDialogs.cpp`, `ScriptDialogs.cpp`, `ScriptBrowser.cpp`,
  `Markdown.cpp`, `UIRectDrawer.cpp`, `MaterialEditor.cpp`, `BindingCapture.cpp`, `DeleteAssetDialog.cpp`,
  `AboutDialog.cpp`, `TextFormat.cpp`, `EntityIcons.cpp`, `FileDialogs.cpp`, `ComponentDrawers.cpp`,
  `SettingsFieldProperty.cpp`; `Icons.h` (generated) and `GenerateIconHeader.py` beyond its docstring.
- **Editor-core files** used by the UI were read only where they carry UI ideas (`HierarchyView`, `EditorCamera`,
  picking in `EditorViewport`, `TransformEdit.h`, `EditorNotifications.h`, `EditorFrameRate.h`, `EditorInterface.h`,
  `ThumbnailCache.h`, `AssetBrowserView.h`); `PlacementPreview`, `EditorPlacement`, `ViewportRenderer`,
  `PropertyEdit` (SetPropertyWithUndo), `RotationAnglesEdit` were not read: the viewport's render path and placement
  belong to the rendering and editor-core inventories.
- **Tests**: names and counts listed; bodies read only for `ImGuiHarness.{h,cpp}` and the `Editor.UI.Source` rules.
  `Perf/Budgets.json` entries for `Perf.EditorPanels` were not looked up.
- **Docs**: DG sections listed were read except "Project settings", "Collision layers", "Input actions" and "Quality
  settings" (skimmed for their UI parts); AR "Editor" read for the UI paragraph only (lines 3217-3345 of 3217-4071);
  MS middle (lines 40-131) not read.
- **Release of arrival** is stated by the documents only for: idle throttling at 30/10 fps, launcher, Hierarchy and
  Inspector multi-edit, Activity, Streaming, Performance, Problems, keyboard layouts/cursor/clipboard, CJK fonts (0.3.0);
  Game view, Retina sizing, File > Open Scene, inactive properties, missing-requirement notices, toasts placement, UI
  canvas editing (0.4.0); sample pictures (0.5.0); agent indication in status bar and viewport (0.5.0); Project Settings,
  Preferences, interface size (0.6.0); Graphics Quality page and quality chip (0.7.0); placement ghost and frame rate
  preferences (wave 8, after 0.7.0). When the Bedrock theme, the widget kit, the item probe, the panel registry and
  the chip strip arrived is not stated anywhere I read.
- Whether `ImGui.frag.slang` including `Include/Common.slang` twice (lines 1 and 3) is intentional was not determined
  (harmless if the include is guarded; not checked).
- How the per-platform Cmd/Ctrl mapping is configured (ImGui's macOS behaviors) was seen only in a test name
  (`ImGuiPlatformTests.cpp:147`), not in code.
- Exact pixel/frame-time figures for the panels' perf budgets (for the book's "how cheap is cheap" sidebar).
