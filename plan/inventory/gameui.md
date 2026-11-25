# Inventory: Game UI (canvases, layout, widgets, text, input and navigation)

Survey of `Strata/src/Strata/GameUI/` at `main` 822a7a46, with the pieces outside the folder that the area needs to be
understood: `Input/UIActions`, the scene services `IUIEvents`/`IUIControl` (`Scene/SceneServices.h`), the overlay
interface (`Renderer/SceneOverlay.h`), text shaping (`Renderer/TextLayout.h`), the shaders
(`Strata/shaders/GameUI/UIQuad*.slang`), the script SDK (`StrataScriptCore/include/StrataScript/UI.h`, `Script.h`),
the script host (`Scripting/ScriptHostAPI.cpp`, `ScriptSystem.cpp`) and the editor authoring (`StrataEditor/src/Editor/
EditorUICommands.cpp`, `GameUIPresets`, `UIRectEdit`, `CanvasEdit`, `Panels/CanvasModeView`, `UI/UIRectDrawer.cpp`).

Line numbers are at this commit. "Arch" = `Docs/Architecture.md`, "DG" = `Docs/DeveloperGuide.md`, "Manual" =
`Docs/Manual/GameUI.md`.

Document sections used:

- Arch "## Game UI", lines 2974-3132 (components table 2985-2995, Layout 3003-3036, UI contract 3038-3053, Text and
  quads 3055-3064, The pass 3066-3096, Input 3098-3121, Input fields 3123-3132). Also Arch 589 (layer table), 652
  (registration table), 881 (`Render.UI` stage), 946 (`GPU.UI` stage), 967 (scene systems table), 1229-1230 (scene
  services table).
- DG "## Game UI" 2625-2729: intro 2625-2636, "### The UI contract" 2637-2647, "### The UI pass" 2648-2680,
  "### UI input" 2681-2729. DG "### Game UI commands" 3809-3846 (inside "## Editor"). DG "### Input actions" 1442 (the
  UI map). DG "### Simulated input" 3742.
- Manual `Docs/Manual/GameUI.md` (133 lines): Make a menu 9-18, Place elements 20-46, Make it look right 48-61, Make it
  do something 63-107, UI in the world 109-121, A main menu scene 123-126, Test it 128-133.
- Skill `.claude/skills/strata-scripting/SKILL.md` "### Game UI" (line 322); skill
  `.claude/skills/strata-editor-automation/SKILL.md` line 641 ("Build the game UI").
- Releases: `Docs/Releases/0.4.0.md` 52-59 (headline), 148-154, 300-317 (known limits); `0.6.0.md` 95-115 (UI map of
  input actions, `UI::IsActionPressed` fix). `Docs/Roadmap.md` 386-393 (what wave 4's `game-ui` stream landed, with
  timings), 708-709 (open limits), 1247-1253 (the stream's goal: "Before this wave the only UI was screen-space text
  sized in raw pixels").

The whole module arrived in **0.4.0** (wave 4, stream `game-ui`, landed 2026-10-19). The rebindable UI action map
arrived in **0.6.0**; before it navigation used fixed keys (0.4.0 notes, line 319-320).

---

## 1. Features

### 1.1 Module shape and registration

| Feature | Where | Docs |
| --- | --- | --- |
| The GameUI module, a layer of its own that may include only Core, Input, Asset, Reflection, Scene, Renderer; only the composition root (Engine) includes it | `StrataTests/Architecture/Layers.json` 69-74; `Engine/BuiltinModules.cpp` 76 (`{ "GameUI", RegisterGameUIModule }`) | Arch 589, 2976-2979; DG 2625-2629 |
| `RegisterGameUIModule`: components, overlay pass, "UI" scene system (`BeforeIfPresent = {"Scripting"}`, `ProfileStage = "Scene.UI"`) | `GameUIRegistration.cpp` 13-27, `.h` 6-11 | Arch 652, 967 |
| `RegisterGameUIComponents`: 12 components in category "UI", each but `UIRect` `Requires("UIRect")`, descriptions, tooltips, ranges, entity properties | `GameUIComponents.cpp` 209-406 | DG 2631-2632; Arch 2997-3001 |
| Inactive reasons: Inspector rows greyed with a reason when another property turns them off (e.g. `MatchWidthOrHeight` only with ScaleWithScreen; slice borders only when Sliced; navigate neighbours only Explicit) | `GameUIComponents.cpp` 51-205, 237-242, 276-280, 300, 327-331, 381-382 | AGENTS.md Editor rules ("InactiveReason") |
| Engine without the module still renders and plays (renderer reaches it only via `SceneOverlayRegistry`, scripts via services) | — | Arch 2976-2979 |

### 1.2 Components (data, `GameUIComponents.h`)

| Component | What | Lines |
| --- | --- | --- |
| Coordinate and color conventions; the UI contract comment | canvas units, +Y down, (0,0) top-left; display (sRGB) colors | 15-26 |
| `UICanvasComponent` | a screen of UI: `ScaleMode`, `ReferenceResolution`, `MatchWidthOrHeight`, `ScaleFactor`, `SafeAreaPadding`, `SortOrder`, `PixelSnap`, `ReceivesInput`, `FirstSelected`, `RenderMode`, `WorldUnitsPerUnit` | 28-64 |
| `UICanvasScaleMode` | ConstantPixelSize, ScaleWithScreen, ConstantPhysicalSize | 28-33 |
| `UICanvasRenderMode` | ScreenSpace, WorldSpace | 35-39 |
| `UIRectComponent` | anchors (min/max), pivot, position, size, `FitContent`, `IgnoreLayout` | 66-88 |
| `UIImageComponent` | texture or solid color, `Type` Simple/Sliced/Filled, `UVRect`, `SliceBorders`, `SliceScale`, `FillAmount`, `FillDirection`, `PreserveAspect`, `CornerRadius`, `BorderWidth`, `BorderColor`, `RaycastTarget` (default on) | 90-122 |
| `UITextComponent` | UTF-8 text, `Font`, `FontSize` (canvas units per em), `Color`, `Alignment`, `VerticalAlignment`, `Wrap`, `Overflow` (Overflow/Truncate/Ellipsis), `LineSpacing`, `OutlineWidth` (em), `OutlineColor`, `RaycastTarget` (default off) | 124-153 |
| `UISelectableComponent` | interaction states and their look: `Interactable`, `Transition` (None/ColorTint/ImageSwap), `TargetImage`, five state colors, four state images, `FadeDuration`, `Navigation` (Automatic/Explicit/None) and four neighbours | 155-191 |
| `UIButtonComponent` | a click; `EventTarget` | 193-197 |
| `UIToggleComponent` | `IsOn`, `Checkmark`, exclusive `Group`, `EventTarget` | 199-206 |
| `UISliderComponent` | `MinValue`, `MaxValue`, `Value`, `WholeNumbers`, `Direction`, `Fill`, `Handle`, `KeyboardStep`, `EventTarget` | 208-220 |
| `UILayoutComponent` | Horizontal/Vertical/Grid, `Padding`, `Spacing`, `ChildAlignment` (9 values), `StretchChildren`, `CellSize`, `Columns` | 222-253 |
| `UIInputFieldComponent` | a line the player types: `Text`, `TextElement`, `Placeholder`, `CharacterLimit`, `CaretColor`, `SelectionColor`, `EventTarget` | 255-270 |
| `UIMaskComponent` | clips descendants to the rect inset by `Padding`, with `Softness`; masks nest | 272-279 |
| Entity references are reflected entity properties (remapped by duplicate, paste, prefab instance; kept by play copy) | registration `EntityProperty(...)` | Arch 2999-3001; test `GameUIComponentTests.cpp` 362 |
| Serialization round-trip and clamping of out-of-range document values | generic reflection | tests `GameUIComponentTests.cpp` 242, 342 |

### 1.3 The per-scene UI model (`GameUIScene`)

| Feature | Where | Docs |
| --- | --- | --- |
| One `GameUIScene` per scene, in the registry's context, created on first use; holds handles, never Refs or GPU objects | `GameUIScene.h` 109-124, 132-136; `GameUIScene.cpp` 26-32, 58-78 | Arch 3003-3005; DG 2647 |
| Root canvases (a canvas with no canvas among ancestors) in hierarchy order; nested canvas = plain element | `RebuildCanvasList` `GameUIScene.cpp` 504-555; `FindRootCanvas` 441-460 | Arch 2997-2999 |
| Elements of a canvas in depth-first order (parents before children = draw order), `SubtreeEnd` ranges | `GameUISceneData.h` 21-53 (`Element`); `RebuildCanvas` 557-729 (walk 566-592, subtree ends 594-602) | Arch 3005-3006 |
| Widget parts resolved by UUID (slider fill/handle, toggle checkmark, selectable target image, input field text/placeholder) | `ResolveParts` 731-819 | Arch 3030-3033 |
| Scale per screen (`ComputeScale`) and size in canvas units (screen / scale) | `GameUIScene.cpp` 80-104; `EnsureLayout` 974-1023 | Arch 3007-3010 |
| `UIScreen` (pixel size + content scale), `UICanvasView` (scale, unit size, sort order, flags) | `GameUIScene.h` 26-33, 58-70 | — |
| Up to 4 layouts per canvas keyed by unit size, LRU replacement (`c_MaxLayoutsPerCanvas`) | `GetLayout` 1025-1062; `GameUISceneData.h` 70-104 | Arch 3034-3036 |
| Lazy layout (`EnsureLayout`), draw order by `SortOrder` then hierarchy (stable sort) | 974-1023 | Arch 3048-3049 |
| Incremental change tracking: entt signals per component, hierarchy moves, activity changes, asset content changes | constructor 106-149; handlers 161-389; `ProcessChanges` 821-931; `RefreshAssetUsers` 933-959 | Arch 3038-3049; DG 2637-2645 |
| Dirty marks per layout for layout, quads, clips, hit stamp | `MarkElementLayoutDirty` 391-400, `MarkElementQuadsDirty` 402-411, `MarkSubtreeQuadsDirty` 413-418, `MarkCanvasDirty` 420-429, `TouchHits` 431-435 | — |
| Re-layout from the highest ancestor whose rect depends on its children | `DependsOnChildren` 961-969; `UpdateLayout` `GameUILayout.cpp` 121-158 | Arch 3042-3044 |
| Gameplay reparenting of plain entities costs no canvas | `MarkCanvasesOfMovedSubtree` 462-502 | Arch 3045-3048 |
| Visibility: active in hierarchy, toggle checkmark off hides, placeholder hides when field has text | `IsVisible` 1210-1228 | Arch 3032-3033 |
| Queries: element count, entity, box, subtree end, visible, raycast target, clip, visible box, `FindElement` | 1147-1247 | — |
| World-space canvas plane matrix | `GetCanvasWorldMatrix` 1101-1113 | Arch 3011-3014 |
| Input screen (game window pixels, content scale, input-to-pixel factor) | `GetInputScreen` 1125-1145 | DG 2683-2690 |
| Selectable visual states stored for the system (state + tint) | `SetSelectableState` etc. 1249-1310 | Arch 3115-3117 |
| Input field editing state (caret, anchor, blink), caret from a point | 1312-1374 | Arch 3123-3132 |
| `Validate`: full recomputation compared with caches; Debug builds assert after every `EnsureLayout` | 1394-1459; assert 1016-1020 | Arch 3049-3051; DG 2642-2645 |
| `GameUISceneStats` / `TakeStats` (ElementsLaidOut, TextsShaped, QuadsBuilt, FullRebuilds) | `GameUIScene.h` 49-56; `.cpp` 1383-1388 | Arch 3052-3053 |
| Root/world canvas counts cached per hierarchy version (hidden UI cost) | `GetRootCanvasCount` 1064-1093, `GetWorldCanvasCount` 1095-1099 | DG 2658-2659 |

### 1.4 Layout (`GameUILayout.cpp`)

| Feature | Where | Docs |
| --- | --- | --- |
| Root rect = canvas units inset by safe-area padding | `GetRootBox` 55-63 | Arch 3010 |
| Anchor/pivot/position/size rect math per axis | `LayOutAxis` 236-272 | Arch 3015-3017; `GameUIComponents.h` 74-78 |
| Two passes (x then y), each top-down for boxes and bottom-up (memoized) for preferred sizes | `LayOutSubtree` 202-214; file comment 10-12 | Arch 3022-3024 |
| Layout groups: stack main axis, cross axis stretch or align, nine-way child alignment | `PlaceGroupChildren` 287-367; `GetAlignment` 25-30 | Arch 3018-3021 |
| Grids: fixed columns or as many as fit | `GetGridColumns` 65-76; grid branch 312-333 | Arch 3020-3021 |
| `IgnoreLayout`, inactive children skipped | `IsPlacedByGroup` 78-85 | test `GameUILayoutTests.cpp` 209 |
| Fit content: text (unwrapped width; height at given width) or layout children + padding | `GetPreferredSize` 369-384; `GetContentSize` 386-407; `GetGroupContentSize` 409-444 | Arch 3022-3024 |
| Slider fill and handle anchored to the normalized value; reversed directions | 245-263; helpers 33-51 | Arch 3030-3033 |
| Non-finite results zeroed | 273-277 | — |
| Mask clip rects: mask box inset by padding, met with outer clip; recomputed only on change | `UpdateClips` 161-173; `ComputeClips` 175-200 | Arch 3025-3029 |
| Only elements whose box changed rewrite quads / bump hit stamp | `UpdateLayout` 133-156 | — |

### 1.5 Text (`GameUIText.cpp`, uses `Renderer/TextLayout.h`)

| Feature | Where | Docs |
| --- | --- | --- |
| Shaping from font metrics (`FontFace`, `ShapeText`) without rasterizing | `ShapeElementText` 144-164; `TextLayout.h` 112-115 | DG 2635-2636; Arch 3055-3057 |
| Default engine font while the font loads; font loading reshapes (font requested at High priority, watched) | `GetTextFace` 42-63 | Arch 3057-3058 |
| Shape cache per element per layout keyed by options and font | `ShapeElementText` 155-163; `ElementText` in `GameUISceneData.h` 55-62 | — |
| Wrapping, max width, box height and overflow (truncate / ellipsis) from the rect | `GetShapeOptions` 78-89; `GetMeasureOptions` 65-76 | Manual 53-54 |
| Input field text is one line, never wrapped or cut; scrolls to keep the caret in view | `GetElementShapeOptions` 100-109; `PlaceFieldLine` 111-142 | Arch 3127-3131 |
| Caret stops (`MeasureCaretStops`) | `TextLayout.h` 98-110; used `GameUIScene.cpp` 1338-1374, `GameUIQuads.cpp` 455-466 | Arch 3130 |

### 1.6 Quads (`GameUIQuads.cpp`, `GameUIRenderData.h`)

| Feature | Where | Docs |
| --- | --- | --- |
| `UIQuad` (64 bytes): rect, UV (or glyph pen), color, resource, flags (kind + font index), border, corner radius, clip | `GameUIRenderData.h` 32-45; flags 11-23 | Arch 3058-3060; DG 2677-2680 |
| `UIClipRect` (32 bytes) | `GameUIRenderData.h` 47-55 | — |
| `UIDrawParameters` push constants (64 bytes), `c_MaxBoundAtlases = 4` | `GameUIRenderData.h` 57-78 | — |
| Per-element quad slots with spare room for texts (`GetTextCapacity`: +25%, at least 4; +2 for an input field's caret and selection) | `GameUIQuads.cpp` 31-35, 236-259 | Arch 3060-3062 |
| Change journal of quad ranges (merged, at most 256, floor) | `RecordQuadChange` 142-159; `GetQuadChanges` 179-190 | Arch 3062-3063 |
| Full repack when a slot overflows or elements change (new `QuadArrayId`) | `BuildQuads` 192-267 | — |
| Indirection: quads reference UI texture indices and scene font indices, never GPU slots/atlas positions | `GetTextureIndex` 44-56, `GetFontIndex` 58-71; `c_MaxUIFonts = 256` | Arch 3063-3064 |
| Use counting of glyphs, fonts, textures (resource version) | `CountQuadUses` 73-114 | — |
| Image quads: tint from the selectable's state, image swap, solid color, preserve aspect, filled (cut rect and UV), nine-slice (borders shrink together when larger than rect) | `WriteElementQuads` 278-408 | Manual 50-52 |
| Text quads: one per glyph, pen on baseline in UV.xy for pixel snapping, outline clamped to 0.1 em; input field selection quad behind glyphs and caret quad after | 410-491 | Arch 3127-3131 |
| Quads carry their element's clip index | 492-495 | DG 2672-2676 |

### 1.7 The UI pass (`GameUIRenderer`, shaders)

| Feature | Where | Docs |
| --- | --- | --- |
| Overlay registry: modules add passes to every `SceneRenderer` without the renderer including them | `Renderer/SceneOverlay.h` 91-136; `GameUIRenderer.cpp` 68-81 (`RegisterGameUIRenderer`); `SceneRenderer.cpp` 606-609 | Arch 3066-3076; DG 2650-2654 |
| `Prepare` (layout, uploads, glyphs, textures, runs), `DrawWorld` (depth-tested, after world text), `Draw` (after screen text), `HasScreenContent` | `GameUIRenderer.h` 38-50; `.cpp` 125-132, 169-257, 750-760 | Arch 3069-3075 |
| Screen-space canvases follow `DrawScreenSpaceText` (editor views/thumbnails hide them; counted, not laid out) | `Prepare` 195-203 | DG 2655-2659 |
| Scene without camera but with screen UI shows the UI over black (main menus) | `HasScreenContent` 125-132; `SceneRenderOptions::OverlayScene` | Arch 3094-3096; DG 2659-2662; Manual 123-126 |
| Upload only changed ranges (merged with gap 16); whole arrays on rebuild or other scene; idle frame uploads nothing | `UploadQuads` 259-362 | Arch 3082-3083; DG 2668-2670 |
| Clip rects uploaded beside quads when changed | `UploadClips` 417-451 | Arch 3088-3091 |
| World-space transforms computed per frame, camera-relative subtraction in double, uploaded when changed | `UploadTransforms` 364-394 | Arch 3091-3094; DG 2663-2667 |
| Texture slot table (bindless slot + grayscale/sRGB bits), requested at High priority, white while loading; mip-streaming report at the pixels a UV unit spans | `UpdateTextures` 453-504; density 276-296; `GetProjectedUnitPixels` 396-415 | DG 2664-2668 |
| Glyph table per font, from the renderer's `FontAtlasCache`; asking rasterizes within budget and keeps from eviction | `UpdateGlyphs` 506-609 | Arch 3084-3086 |
| Draw runs: one draw per canvas with up to 4 fonts; split runs beyond | `BuildRuns` 611-689 | Arch 3086-3088 |
| Pipelines: alpha blending in display values, no culling, world pipeline depth test GreaterOrEqual (reversed-Z) without writes, TAA jitter depth bias | `GetPipeline` 691-722; `SceneOverlay.h` `SetJitteredDepthBias` | Arch 3091-3092 |
| Binding sets keyed by the four atlases, released when unused a frame; buffers released when the scene has no canvases | `GetBindingSet` 724-748; `Prepare` 176-192; `ReleaseResources` 153-167 | Arch 3092-3096 |
| Instanced draw: 6 vertices per quad, no vertex buffer | `DrawRuns` 762-803 | Arch 3086-3087 |
| GPU timing stage `GPU.UI`, CPU stage `Render.UI` | `GameUIRenderer.cpp` 56-81, 768-772 | Arch 881, 946 |
| Vertex shader: canvas units to pixels, pixel snapping of rect edges and glyph baselines, clip rect culling, world transform | `shaders/GameUI/UIQuad.vert.slang` 41-143 | — |
| Fragment shader: rounded rect SDF with border, sRGB/grayscale texture decode, SDF glyph with outline (shared `Include/SDFText.slang`), mask coverage with softness; single late discard to keep derivatives | `shaders/GameUI/UIQuad.frag.slang` 49-120 | DG 2677-2680 |
| Shared data layout with C++ (keep in step) | `shaders/GameUI/UIQuad.slang` 1-71 | DG 2677-2678 |
| Screen view (editor canvas mode zoom/pan) via `SceneScreenView` | `SceneOverlay.h` 22-39; `Prepare` 208-211; push constants `Origin`, `Scale * zoom` | DG 3836-3846 |
| Shader entries registered | `Strata/CMakeLists.txt` 171-172 | — |

### 1.8 Hit testing and the pointer (`GameUIHitTest`)

| Feature | Where | Docs |
| --- | --- | --- |
| `GameUIHitTester`: uniform grid per canvas of raycast-target visible boxes (about 2 targets per cell, max 64x64), counting-sort build, rebuilt on layout id / hit stamp change | `GameUIHitTest.cpp` 18-20, 24-112 | Arch 3101-3104 |
| Hit test: topmost canvas by sort order, within it the last drawn, half-open rects; non-input canvases skipped | `HitTest` 145-169; `HitTestGrid` 114-129; `UIBox::Contains` `GameUIScene.h` 43-46 | DG 2716-2727 |
| `HitTestAll` (every element under a point, for tools) | 171-194 | DG 3809 (`ui.hitTest` all) |
| Raycast targets: image with RaycastTarget, text with RaycastTarget, or a selectable | `ComputeRaycastTarget` `GameUIScene.cpp` 275-284 | `GameUIHitTest.h` 237-243 |
| World-space canvases: camera ray (`GetGameViewProjection`, `MakeRay` with reversed-Z), plane intersection, projection back to pixels; after every screen-space canvas, nearest first; scene geometry does not block | `GameUIPointer` 196-255; `FindWorldCrossings` 131-143 | Arch 3104-3109; DG 2716-2727 |

### 1.9 Input system (`GameUISystem`, Play mode, "UI" scene system)

| Feature | Where | Docs |
| --- | --- | --- |
| Update order: actions, layout for input screen, hit grids, drop unusable focus, pointer, editing, navigation, visual states, dispatch | `OnUpdate` `GameUISystem.cpp` 183-231 | Arch 3098-3101 |
| Scene without canvases: one storage-size check, releases captures | 189-202 | — |
| Gestures: a press that starts over the UI is the UI's until all buttons are released; otherwise the game's; pointer capture hides mouse buttons and scroll from gameplay | `UpdatePointer` 254-328 (capture 323-327); `Gesture` enum `GameUISystem.h` 91-96 | Arch 3109-3112; DG 2691-2695 |
| Binding capture (rebinding menu) left press presses no widget | 281-286 | test `GameUIInputTests.cpp` 597 |
| Hover recomputed only when something that changes it changed | 270-279 | — |
| Click on release over the pressed selectable; press focuses; slider drag (also outside its rect), whole numbers | 287-321; `Click` 384-391; `DragSlider` 428-446; `ClampSliderValue` 140-150 | DG 2697-2702 |
| Toggles flip; groups exclusive (switching the on one off does nothing) | `SetToggle` 393-415 | — |
| Values written with `registry.patch` (running scene, no undo) | 408-425, 729-730 | Arch 3113-3114 |
| Focus and `FocusChanged` events; focused input field is the edited one | `Focus` 493-507; `SetFocus` 462-491 | — |
| UI action map `UI/Submit`, `UI/Cancel`, `UI/Up/Down/Left/Right`, repeat after 0.4 s every 0.1 s on unscaled time; idle update costs a comparison | `Input/UIActions.h` 11-64; `UIActions.cpp` 39-87 | DG 2703-2710; Arch 3114-3115 |
| Navigation: start at topmost input canvas's `FirstSelected` else top-left selectable (screen canvases before world ones) | `FindStartSelectable` 769-807 | DG 2710-2712 |
| Automatic navigation: score along + 2 x across between centers in screen pixels; Explicit neighbours; None; world canvases navigate within themselves | `Navigate` 809-861 | DG 2707-2709, 2724-2726 |
| Focused slider steps with direction keys (`KeyboardStep`, 0 = tenth of range) | `StepSlider` 749-767 | DG 2712-2713 |
| Submit clicks focused button / flips toggle / submits a field; Cancel stops editing (scripts read Cancel themselves) | `UpdateNavigation` 539-550 | Manual 102-106 |
| Visual states (Disabled > Pressed > Hover > Focused > Normal), tint fades over unscaled time, records only while not at rest | `GetDesiredState` 867-878; `UpdateVisualStates` 880-931 | DG 2714-2716 |
| Input field editing: keyboard capture, typed text at caret within character limit, control chars dropped, Backspace/Delete/arrows/Home/End with repeat, Shift select, Ctrl/Cmd+A, Enter submits, Escape ends (capture kept to frame end), caret blink 0.53 s, UTF-8 boundaries | `BeginEditing` 557-568, `EndEditing` 570-579, `IsEditKeyRepeated` 589-611, `MoveCaret` 613-628, `UpdateEditing` 630-747; UTF-8 helpers 68-138 | Arch 3123-3132; DG 2717-2721 |
| Click on input field places caret at nearest character (also on world canvases through the ray) | 296-309; `FindInputFieldCaret` `GameUIScene.cpp` 1338-1374 | — |
| Events queued in input order, dispatched at end of update before scripts; event target resolution; listener add/remove safe during dispatch | `QueueEvent` 1171-1194; `DispatchEvents` 1196-1213; `Add/RemoveUIEventListener` 1215-1234 | Arch 3117-3118; `SceneServices.h` 532-545 |
| `OnRuntimeStop` restores input and rest states; `OnEntityDestroying` clears references | 167-181, 233-248 | — |
| Typed text source (`Input::GetTypedText`, `GetUncapturedTypedText`, `c_MaxTypedTextBytes = 1024`) | `Input/Input.h` 89-108 | DG 2722-2724 |

### 1.10 Gameplay services and scripts

| Feature | Where | Docs |
| --- | --- | --- |
| `UIEventType` (Click, ValueChanged, FocusChanged, Submit), `UIEventInfo`, `IUIEvents` | `Scene/SceneServices.h` 511-545 | Arch 1229 |
| `IUIControl` (text, image, color, interactable, value, focus, pointer over UI, action state); values set raise no events | `SceneServices.h` 547-584; implemented `GameUISystem.cpp` 938-1165 | Arch 1230 |
| Host functions (15 UI host functions: `UIGetText` ... `UIIsActionDown`) appended to the ABI | `StrataScriptCore/include/StrataScript/ScriptABI.h` 613-637; host `Scripting/ScriptHostAPI.cpp` 2395-2616 | AGENTS.md Scripting; Roadmap 389 says "18 host functions" for the stream (includes non-UI ones like unscaled time, typed text: not verified) |
| Script callbacks `OnUIClick`, `OnUIValueChanged`, `OnUIFocusChanged`, `OnUISubmit` (read only when `StructSize` covers them) | `ScriptABI.h` 814-828; `Script.h` 43, 61-66, 94-97, 307-336 | — |
| Dispatch to the widget's scripts then the event target's | `ScriptSystem.cpp` 103 (listener), 415-449 (`OnUIEvent`) | `ScriptSystem.h` 72-74 |
| SDK `UIElement` (`entity.GetUI()`), `UI` (focus, pointer, actions), `UIAction` | `StrataScript/UI.h` 1-183 | Manual 63-107; skill scripting "### Game UI" |
| `Motion` helpers (SmoothDamp etc.) shipped with the stream | `StrataScript/Gameplay.h` 222+ | Roadmap 389-390 |
| `Time::GetUnscaledDeltaTime` for pause menus | SDK Time.h | Manual 107 |

### 1.11 Editor and automation (authoring)

| Feature | Where | Docs |
| --- | --- | --- |
| `ui.create` (presets in one transaction, new canvas if needed, anchor presets), `ui.layout` (rects at any screen without rendering), `ui.hitTest` | `StrataEditor/src/Editor/EditorUICommands.cpp` 222-487 | DG 3809-3817; Manual 128-133 |
| Presets: Canvas, Panel, Image, Text, Button, Toggle, Slider, InputField, Horizontal/Vertical/Grid Layout | `Editor/GameUIPresets.h` 17-71, `.cpp` | DG 3811-3813 |
| 16 anchor presets; keep a rect in place while anchors change; margins along stretched axes; game screen; editor picking | `Editor/UIRectEdit.h` 95-175, `.cpp` (`ApplyPreset` ~280) | DG 3818-3829 |
| UI Rect drawer in the Inspector (anchor grid, pixels at game screen, margin rows, prefab overrides) | `UI/UIRectDrawer.cpp`, `UI/ComponentDrawers.*` | DG 3820-3829; Manual 22-36 |
| Viewport "Game UI" chip, click selects topmost element | — | Manual 38-39 |
| 2D canvas mode: letterboxed canvas, outlines/handles, drag/resize with snap, zoom about pointer, pan, F, Home; cropped camera; `SceneScreenView` | `Panels/CanvasModeView.*`, `Editor/CanvasEdit.*` | DG 3830-3846; Manual 41-46 |
| `input.click` clicks an element where the player sees it (projects world canvases), fails when covered; `input.type` | `Editor/EditorInputCommands.cpp` ~1238-1280 | Manual 130-133; tests `EditorUICommandTests.cpp` 304, 563, 580 |

### 1.12 Samples and feature test

- Tetris HUD on a canvas (`Samples/Tetris/Assets/Scenes/Main.stscene`, `Scripts/TetrisBoard.cpp`; GPU test
  `GPUGameUITests.cpp` 959 checks it covers the same fraction at 1280x720 and 2560x1440).
- ThirdPerson main menu with focus, Cancel, a credits panel scrolling inside a `UIMask`, settings panel
  (`Samples/ThirdPerson/Scripts/MainMenu.cpp`, `SettingsMenu.*`, `Assets/Scenes/MainMenu.stscene`), loading screens
  (`LoadingScreen.cpp` in ThirdPerson and OpenWorld), OpenWorld HUD (`IslandHud.cpp`), PhysicsPlayground
  (`Playground.cpp`), Showcase `Outpost.stscene` and `Loading.stscene`.
- Feature test: `StrataTests/FeatureTest/Scripts/UIFeatures.cpp` (256 lines; a scripted frame-by-frame player:
  click, toggle, slider drag, navigation, typed text, input field editing) and `Assets/Scenes/Feature.stscene`.

### 1.13 Tests (intended behaviour)

- `StrataTests/src/GameUI/GameUILayoutTests.cpp` (suites `GameUI.Layout`, `.Scale`, `.Dirty`, `.Mask`).
- `GameUIInputTests.cpp` (`GameUI.HitTest`, `.Capture`, `.Events`, `.Navigation`, `.InputField`, `.WorldSpace`).
- `GameUITextTests.cpp` (`GameUI.Text`), `GameUIComponentTests.cpp` (`GameUI.Components`, `.Serialization`).
- `StrataTests/src/Renderer/GPUGameUITests.cpp` (`GPU.GameUI`: pixels, snapping, colors, masks, world canvas,
  100 km precision, TAA stability, screen view, mip streaming, resource release).
- `StrataTests/src/Scripting/ScriptUITests.cpp` (`Scripting.UI`).
- `StrataTests/src/Perf/GameUIPerfTests.cpp` (`Perf.GameUI.Layout10k` budget 0.6088 ms measured 0.4059,
  `Perf.GameUI.IdleFrame10k` 0.000405 ms, `PerfGPU.GameUI.Render10k` 0.1508 ms; `Budgets.json` 193-196).
- Editor: `EditorGameUITests.cpp`, `EditorUICommandTests.cpp`, `GPUCanvasEditTests.cpp`; also `SceneSystemTests`,
  `CookedSceneTests`, `BuiltinModulesTests` touch the module.

### How completeness was checked

- Every file of `Strata/src/Strata/GameUI/` (17 files, 6,668 lines) is accounted for above: Components (.h/.cpp),
  HitTest (.h/.cpp), Layout.cpp, Quads.cpp, Registration (.h/.cpp), RenderData.h, Renderer (.h/.cpp), Scene (.h/.cpp),
  SceneData.h, System (.h/.cpp), Text.cpp.
- Every registered component (12: UICanvas, UIRect, UIImage, UIText, UISelectable, UIButton, UIToggle, UISlider,
  UILayout, UIInputField, UIMask; plus every enum) is listed in 1.2. Registered: 1 scene system ("UI"), 1 overlay
  pass ("GameUI"), 2 profiler stages (`Render.UI`, `GPU.UI`) plus the scene stage `Scene.UI`, 2 scene services
  (`IUIEvents`, `IUIControl`), 2 shader entries (`GameUI/UIQuad.vert`, `.frag`), 15 UI host functions and 4 callbacks,
  3 editor commands (`ui.create`, `ui.layout`, `ui.hitTest`) plus the UI paths of `input.click`/`input.type`. No
  settings section and no asset type belongs to the module (it uses Texture and Font assets).
- Every public method of `GameUIScene.h`, `GameUISystem.h`, `GameUIHitTest.h`, `GameUIRenderer.h` was matched to an
  implementation that was read.

---

## 2. Concepts to teach (dependency order)

1. **What a game UI is, and why it differs from an editor UI.** Games draw menus and HUDs inside the game's own
   image, at any resolution and aspect, driven by mouse, keyboard, gamepad and touch, often while the game is paused.
   Industry approaches: *immediate mode* (Dear ImGui, used by the Strata editor: the UI is re-declared every frame by
   code) versus *retained mode* (Unity uGUI, Unreal UMG, Godot Control nodes, web DOM: a persistent tree of elements
   with properties, laid out and drawn by the engine). Strata's game UI is retained and entity-based: UI elements are
   ECS entities in the scene with `UIRect` and other components, authored in the editor like any entity, saved with the
   scene, prefab-able. Why: games author UI in the editor, need designers to place it, and want layout cost only on
   change. Newcomer mistake: thinking the editor's ImGui panels and the game UI are the same system (they are not:
   `StrataEditorUI` is ImGui; `GameUI` is the shipped game's).

2. **Coordinate spaces: pixels, canvas units, +Y down.** Screens differ in pixels; UI is designed in an abstract unit
   space that maps to pixels by a scale. Strata: canvas units, origin top-left, +Y down (like the mouse), colors in
   display sRGB. Contrast with the 3D world's +Y up and the NDC conventions the book teaches elsewhere. Mistake: mixing
   +Y up and +Y down; dividing pixels by the scale for a world-space canvas (DG 2718-2721 forbids it).

3. **Resolution independence: canvas scale modes.** Approaches: fixed pixels, scale with screen (reference
   resolution), physical size (DPI). Strata copies Unity's three modes; ScaleWithScreen interpolates *logarithmically*
   between matching width and height (`s = 2^lerp(log2(W/Rw), log2(H/Rh), match)`, `GameUIScene.cpp` 88-96). Teach why
   log space (a screen twice as wide and half as tall should average to 1, not 1.25). Content scale (96 DPI = 1) for
   ConstantPhysicalSize. Safe-area padding for TV overscan and notches. Mistake: designing at 1920x1080 with
   ConstantPixelSize and seeing a tiny UI at 4K.

4. **Anchors and pivots (the rect model).** Approaches: absolute positions; anchor/offset (Unity RectTransform, Unreal
   anchors, Godot anchors+offsets); constraint solvers (Auto Layout, Cassowary); flexbox (Yoga). Strata uses anchors
   (fractions of the parent), a pivot, a position offset and a size *added to* the anchored span. Point anchors = fixed
   size; stretched anchors = margins. Formula in `GameUIComponents.h` 74-78 and `LayOutAxis` 264-271. Mistake: setting
   `Size` to the full width on a stretched rect (it adds to the span: 0 fills it); confusing pivot with anchor.

5. **The UI as a tree; draw order is hierarchy order.** Depth-first order: parents first, children over them; sibling
   order matters. Flattening a tree into an array with subtree ranges (`SubtreeEnd`) so a subtree is `[i, end)`: a
   standard data-oriented trick. Nested canvases are plain elements. Mistake: expecting a z-index per element (only
   canvases have `SortOrder`).

6. **Layout groups and measure/arrange.** Two-phase layout (WPF "measure and arrange", Unity's ILayoutElement, Flutter's
   constraints down / sizes up). Strata: per axis, preferred sizes bottom-up (memoized) and boxes top-down, widths before
   heights because wrapped text height depends on width (`GameUILayout.cpp` 10-12). Horizontal/vertical stacks, grids,
   nine-way alignment, stretch on the cross axis, `FitContent`, `IgnoreLayout`. Mistake: expecting a child's anchors to
   matter inside a group (the group ignores them); expecting a group's children to shrink to fit (no flex shrink).

7. **Text: shaping vs. rasterizing; signed-distance-field fonts.** Teach glyphs, advances, kerning, line breaking,
   alignment, overflow/ellipsis; that layout needs only metrics (shaping) while drawing needs pixels (atlas). Strata
   shapes with `ShapeText` on `FontFace` (no GPU), and draws glyphs from a per-renderer SDF atlas (`FontAtlasCache`,
   `Include/SDFText.slang`) that rasterizes within a frame budget. SDF gives crisp scaling and cheap outlines. Font
   files are untrusted input (AGENTS.md Rendering). Mistake: measuring text by rendering it; assuming a glyph is ready
   the frame it is asked for (it may draw a frame later: `PendingGlyphs`).

8. **Images: nine-slice, fill, rounded rects by SDF.** Nine-slice for scalable panels; filled images for health bars;
   preserve aspect; rounded corners and borders as an analytic signed distance in the pixel shader (no textures
   needed: editor presets need no assets). Mistake: setting slice borders in canvas units (they are texels, scaled by
   `SliceScale`).

9. **Retained mode needs change tracking: dirty flags and the "UI contract".** The central engineering idea: do work only
   for what changed. Observers (entt `on_construct/on_update/on_destroy`), dirty marks per element and per layout,
   choosing the re-layout root (highest ancestor that depends on its children), journals of changes (hierarchy moves,
   activity, asset content). Consequence for users of the engine: code that writes a component field directly must
   signal it (`MarkModified`, `registry.patch`); Debug builds compare caches against a full recomputation
   (`Validate`). Same shape as the scene's transform contract (taught elsewhere). Mistake: `GetComponent<UIRect>().Size
   = ...` without `MarkModified` (silently stale in Release; asserts in Debug).

10. **Caching layouts per screen size.** Keyed by size in units, LRU of 4: a window resized at the same aspect under
    ScaleWithScreen lays out nothing. Mistake: assuming resizing always costs a layout.

11. **Batching for the GPU: quads, instancing, indirection tables.** Turn the tree into a flat array of 64-byte quads in
    draw order; one storage buffer; instanced draw with six vertices per quad and no vertex buffer; one draw per canvas
    (up to 4 fonts bound). Indirection (UI texture index -> bindless slot table; glyph index -> atlas placement table)
    so quads never change when mip streaming or atlas packing changes. Per-element slots with headroom plus a journal
    of dirty ranges for partial uploads. Mistake: issuing a draw per element; baking GPU slots into cached data.

12. **Clipping and masks without breaking batches.** Approaches: scissor rectangles (split draws), stencil masks, shader
    clipping. Strata clips in the shader: each quad names a clip rect; fully outside quads are degenerate in the vertex
    shader; soft edges via coverage. Derivative safety: one late `discard` (frag 108-120 comment). Mistake: using
    `discard` early in a shader that later needs derivatives.

13. **Pixel snapping and display-value blending.** Rect edges and glyph baselines on whole pixels for crispness; glyphs
    move by their baseline offset so shapes keep. UI blends in display (sRGB) values over the tone-mapped image; sRGB
    textures sample linear and are converted back. Mistake: blending UI in linear HDR before tone mapping (colors
    shift).

14. **Overlay passes and dependency inversion.** The renderer must not depend on the UI module: a registry of overlay
    factories (`SceneOverlayRegistry`), each `SceneRenderer` makes one pass per factory. Ties to the book's layering
    chapter. Mistake: adding `#include "GameUI/..."` in Renderer code (`Architecture.Layering` test fails).

15. **World-space UI.** A canvas as a plane in the scene: canvas units to world matrix (pivot at origin, +Y flipped,
    `WorldUnitsPerUnit`), depth-tested against the scene (reversed-Z, no writes), camera-relative transforms computed in
    double, antialiasing via `fwidth`, mip streaming from projected unit size, TAA depth bias. Unlit, drawn after post
    (known limitation). Mistake: expecting it to be lit or to cast shadows.

16. **Hit testing: picking the topmost element.** Raycast targets (what blocks), reverse draw order, sort order,
    half-open rects, masks reduce the hit area, spatial acceleration with a uniform grid (counting sort into cells).
    World-space: unproject a ray from the camera (reversed-Z NDC, near = 1, the far point at 0.5 for infinite far
    planes), intersect the canvas plane, then grid. Mistake: hit-testing the visual rect of an element outside its mask;
    making labels raycast targets (texts default off so labels don't steal clicks from buttons... they belong to the
    button's selectable anyway via `FindSelectable`).

17. **Input routing between UI and gameplay.** Who owns a click? Gestures: a press that starts over UI belongs to UI until
    release; pointer capture hides mouse buttons and scroll from gameplay; keyboard capture while typing. System order:
    UI before scripts so they see this frame's events. Mistake: a click on a button also firing the gun; reading
    `Input::IsKeyPressed` in a script and wondering why it is silent while the player types a name.

18. **Widgets as state machines.** Selectable states (Normal, Hover, Pressed, Focused, Disabled) with priority;
    button click semantics (press and release over the same button); toggle groups (radio buttons); slider drag and
    stepping; tint fades. Mistake: clicking on press instead of release (cannot cancel by dragging off).

19. **Focus and spatial navigation (keyboard, gamepad, TV).** Focus model, start selection, explicit vs automatic
    navigation, the scoring heuristic (along + 2 x across), repeat timing (0.4 s delay, 0.1 s interval), input actions
    rather than raw keys so players can rebind. Mistake: a menu unusable with a gamepad because nothing is focused
    (`FirstSelected`, or `Focus()` from script).

20. **Text input.** Caret, selection anchor, UTF-8 byte offsets at character boundaries, IME-less typed text per frame,
    repeat of editing keys, scrolling a single line to keep the caret visible, placeholder. Mistake: moving the caret by
    bytes and splitting a multi-byte character.

21. **Events and decoupling game logic from widgets.** Observer pattern; queued events dispatched at a defined point in
    the frame, in input order; event targets so one menu script handles all its buttons; values set by code raise no
    events (avoids feedback loops). Mistake: setting a slider from script in `OnUIValueChanged` and expecting another
    event.

22. **Time: scaled vs unscaled.** Pause menus at time scale 0: the UI runs on unscaled time. Mistake: animating a pause
    menu with `Time::GetDeltaTime()`.

23. **Testing UI headlessly.** Simulated input, layout without rendering (`ui.layout`), hit tests (`ui.hitTest`),
    work counters (`TakeStats`), validation against full recomputation, perf budgets. Agents build UI through
    commands.

---

## 3. Code worth showing

| # | File and lines | Teaches | Reader must know |
| --- | --- | --- | --- |
| 1 | `Strata/src/Strata/GameUI/GameUIComponents.h` 74-88 (`UIRectComponent` with its comment) | the rect model in one comment: anchors, size added to span, pivot | concept 2, plain structs |
| 2 | `GameUIComponents.h` 41-64 (`UICanvasComponent`) | what a canvas configures; screen vs world space | concept 3 |
| 3 | `Strata/src/Strata/GameUI/GameUIScene.cpp` 80-104 (`ComputeScale`) | the three scale modes, log interpolation, clamping and NaN guards | logarithms, `std::exp2` |
| 4 | `Strata/src/Strata/GameUI/GameUILayout.cpp` 216-285 (`LayOutAxis`) | the central algorithm: per-axis anchored rect, fitted sizes, groups placing children, slider parts | concepts 4-6; arrays of boxes |
| 5 | `GameUILayout.cpp` 287-367 (`PlaceGroupChildren`) | stack and grid layout, alignment, stretch | 4 |
| 6 | `GameUILayout.cpp` 369-407 (`GetPreferredSize`, `GetContentSize`) | measure pass, memoization, text height depends on width | 4, text shaping basics |
| 7 | `GameUILayout.cpp` 87-159 (`UpdateLayout`) | incremental layout: walk up to the re-layout root, dedupe nested roots, mark only moved boxes | concept 9 |
| 8 | `GameUIScene.cpp` 106-149 (constructor: signal connections) | observing component changes with entt signals; which component change costs what | ECS basics, entt signals |
| 9 | `GameUIScene.cpp` 198-242 (`OnLayoutChanged`, `OnVisualChanged`, `OnTextChanged`) | different changes, different costs (layout vs quads only) | 8 |
| 10 | `GameUIScene.cpp` 566-602 (depth-first walk and subtree ends in `RebuildCanvas`) | flattening a tree into an array with subtree ranges, explicit stack | trees, stacks |
| 11 | `GameUIScene.cpp` 961-969 (`DependsOnChildren`) + 974-1023 (`EnsureLayout`) | lazy layout, views sorted by sort order, Debug validation | 7-10 |
| 12 | `GameUIScene.cpp` 1394-1459 (`Validate`) | verifying a cache by recomputation, error naming the culprit entity | 9 |
| 13 | `StrataTests/src/GameUI/GameUILayoutTests.cpp` 485-557 and 575-586 | the contract as tests: an idle frame does zero work; an unsignaled write fails validation | doctest basics |
| 14 | `Strata/src/Strata/GameUI/GameUIRenderData.h` 32-45 (`UIQuad`) and 57-78 (`UIDrawParameters`) | GPU data layout, `static_assert(sizeof == 64)`, flag packing, C++/shader sync | structs, bit packing |
| 15 | `Strata/src/Strata/GameUI/GameUIQuads.cpp` 321-357 (nine-slice) | nine-slice geometry and UVs, shrinking borders | 8 |
| 16 | `GameUIQuads.cpp` 192-267 (`BuildQuads`) | slots with headroom, partial rewrite vs repack, change journal | 11 |
| 17 | `GameUIQuads.cpp` 467-484 (glyph quads) | turning shaped glyphs into quads, pen in UV for baseline snapping | 7 |
| 18 | `Strata/src/Strata/GameUI/GameUIText.cpp` 111-142 (`PlaceFieldLine`) | scrolling a single-line text field to keep the caret visible | 20 |
| 19 | `Strata/shaders/GameUI/UIQuad.vert.slang` 41-143 (`st_Main`) | vertex pulling from a structured buffer, instancing without a vertex buffer, pixel snapping, clip culling, world transform | basic shaders, NDC |
| 20 | `Strata/shaders/GameUI/UIQuad.frag.slang` 76-106 (`ShadeImage`) | rounded-rect signed distance, border band, sRGB decode, `fwidth` AA for world canvases | SDF basics, sRGB |
| 21 | `UIQuad.frag.slang` 62-73 and 108-120 (`ShadeGlyph`, `st_Main`) | SDF glyph coverage and outline; why discard comes last (derivatives) | 7, 12 |
| 22 | `Strata/src/Strata/GameUI/GameUIRenderer.cpp` 259-362 (`UploadQuads`) | uploading only changed ranges, merging, whole-array fallback; mip density | 11 |
| 23 | `GameUIRenderer.cpp` 611-689 (`BuildRuns`) | batching constraint (4 atlases) and run splitting | 11 |
| 24 | `GameUIRenderer.cpp` 364-394 (`UploadTransforms`) | camera-relative world UI, subtraction in double | camera-relative chapter |
| 25 | `Strata/src/Strata/GameUI/GameUIHitTest.cpp` 50-129 (`Build`, `HitTestGrid`) | uniform grid via counting sort, topmost-first search | arrays, prefix sums |
| 26 | `GameUIHitTest.cpp` 208-253 (`MakeRay`, `IntersectCanvas`, `ProjectCanvasPoint`) | unprojecting a pixel with reversed-Z, ray-plane in the plane's own space | matrices, inverse |
| 27 | `Strata/src/Strata/GameUI/GameUISystem.cpp` 254-328 (`UpdatePointer`) | gesture ownership, pointer capture, click-on-release, drag | 17-18 |
| 28 | `GameUISystem.cpp` 809-861 (`Navigate`) | spatial navigation scoring | 19, dot products |
| 29 | `GameUISystem.cpp` 880-931 (`UpdateVisualStates`) + `Strata/src/Strata/Input/UIActions.cpp` 39-87 (`UIActionState::Update`) | state fades on unscaled time, keeping records only while needed; key repeat | 18, 22 |
| 30 | `Samples/ThirdPerson/Scripts/MainMenu.cpp` 34-137 | a real menu script: focus on create, Cancel closes panels, event target handling all buttons, scrolling credits in a mask on unscaled time | SDK basics |

Also short ones for the game-developer track: `Docs/Manual/GameUI.md` 68-88 (the manual's `MainMenu` sample),
`StrataScriptCore/include/StrataScript/UI.h` 34-133 (the `UIElement` API surface), `Script.h` 61-66, 94-97 (the
callbacks), `GameUIRegistration.cpp` 13-27 (registering a module's system with ordering).

---

## 4. Figures

Diagrams:

1. **Module map**: GameUI layer and its neighbours: Scene (components, signals), Renderer (via `SceneOverlayRegistry`),
   Input (`UIActions`, capture), Scripting (via `IUIEvents`/`IUIControl` services), Editor (`ui.*`, drawers). Arrows
   show who includes whom and that Renderer/Scripting do not include GameUI.
2. **Frame timeline**: one Play frame: Input frame -> "UI" scene system (actions, layout for input screen, hit grids,
   pointer, editing, navigation, states, dispatch events) -> Scripting `OnUpdate` (events already delivered) -> ... ->
   SceneRenderer: world geometry, world text, `DrawWorld` (world canvases), post/tonemap, screen text, `Draw`
   (screen canvases). Mark where `EnsureLayout` is called twice (system and pass) with different screens possible.
3. **Rect math**: parent box, AnchorMin/AnchorMax points, span, Size added, pivot point, Position offset; two cases
   side by side (point anchors 200x50, stretched anchors with Size (-20,-20)).
4. **Anchor preset grid** (the 4x4 of `UIAnchorPreset`) and what happens to a HUD element at three aspect ratios.
5. **Scale modes chart**: scale vs screen width for the three modes; ScaleWithScreen log-lerp with match 0, 0.5, 1 at
   several aspect ratios.
6. **Layout passes**: a small tree with a vertical group containing a fitted text; arrows bottom-up (preferred sizes)
   then top-down (boxes), x axis then y axis.
7. **Element array**: the depth-first flattened array with Parent and SubtreeEnd fields, a subtree highlighted as
   `[i, end)`; Clip and MaskSlot columns.
8. **Dirty propagation**: a change event -> mark element -> walk up to the highest ancestor that depends on children ->
   re-layout subtree -> compare boxes -> mark quads -> journal range -> renderer partial upload.
9. **Data flow from component to pixel**: components -> `GameUIScene` (elements, layouts, shaped texts) -> quad array
   (slots) -> renderer buffers (quads, texture slot table, glyph table, clips, transforms) -> shader.
10. **Memory layout of `UIQuad`** (64 bytes, field offsets, flag bits: kind bits 0-1, font bits 8-15) and of the glyph
    table entries (`x | y<<16`, `w | h<<8 | page<<16`) and texture slot entries (slot bits 0-23, sRGB bit 30, grayscale
    bit 31).
11. **Indirection tables**: quad Resource -> UI texture index -> slot table -> bindless array; glyph index -> per-font
    region of glyph table -> atlas page and texels.
12. **Draw runs**: a canvas's quad range split into runs by the 4-atlas limit.
13. **Rounded-rect SDF**: the distance field picture with radius, border band and 1-pixel coverage ramp.
14. **Hit-test grid**: canvas divided into cells, rects inserted into the cells they overlap, query looks at one cell in
    reverse draw order.
15. **World-space pointer ray**: camera, pixel, ray, canvas plane, crossing point in canvas units; ordering of screen
    canvases first, then world crossings by distance.
16. **Gesture state machine**: None -> UI (press over UI) / Game (press elsewhere) -> None when all buttons released;
    pointer capture on in UI or hovering-over-UI states.
17. **Selectable state priority and fade**: Disabled > Pressed (pressed and hovered) > Hover > Focused > Normal, with a
    tint curve fading from current to target over `FadeDuration`.
18. **Navigation scoring**: from-center, candidate centers, along and across components, score along + 2|across|.
19. **Key repeat timeline**: press at 0, repeats at 0.4, 0.5, 0.6...; the same for edit keys.
20. **Input field model**: text bytes, caret and anchor, selection quad, caret quad, scroll window over the line.
21. **Event dispatch**: queued events in input order, listeners snapshot, ScriptSystem routing to widget then target.

Screenshots (every one taken in the editor or the runtime; how to isolate given):

1. A canvas at 1280x720 and at 2560x1440 and at 21:9, ScaleWithScreen: use the Tetris sample HUD
   (`Samples/Tetris`, the HUD canvas) or `ui.layout` + viewport capture; switch `ScaleMode` to ConstantPixelSize to
   show the contrast.
2. Anchors: a score anchored top-right and a bar stretched along the bottom at two aspect ratios (`ui.create` text and
   image with `anchor` "topRight" and "bottomStretch").
3. The Inspector's UI Rect drawer with the anchor preset grid open and margin rows on a stretched element.
4. The viewport's 2D canvas mode with outlines and handles on the selection (the viewport's "2D" chip,
   `viewport.setSettings {canvasMode}`), zoomed in with F.
5. Images: solid, rounded with border, nine-sliced panel, filled health bar at 0.3, preserve aspect (the GPU test
   `GPUGameUITests.cpp` 168 sets these up; reproduce with `ui.create image` and component edits).
6. Text: alignment variants, wrapping, Truncate vs Ellipsis, an outline over a busy background.
7. Pixel snapping on vs off (`UICanvas.PixelSnap`) at a fractional scale, zoomed crop to show crisp vs blurry edges.
8. A vertical layout menu (Title, Play, Settings, Quit) and the same buttons in a grid layout; `StretchChildren` on/off.
9. Selectable states: one button each in Normal, Hover, Pressed, Focused, Disabled (play mode, `input.click`, focus
   from script, `Interactable` off).
10. Toggle group (radio) and a slider with fill and handle at two values.
11. Input field: empty with placeholder, typing with selection highlighted and caret, long text scrolled
    (`GPUGameUITests.cpp` 508 has the scene; in play mode use `input.click` + `input.type`).
12. Mask: the ThirdPerson credits panel scrolling inside a `UIMask`, Softness 0 vs 20 (`Samples/ThirdPerson`
    MainMenu scene, Credits button).
13. World-space canvas: a sign on a wall in the Showcase (`Samples/Showcase/Assets/Scenes/Outpost.stscene` contains a
    canvas; confirm it is world-space) seen in perspective, partly hidden by geometry in front; and the same canvas
    switched to ScreenSpace.
14. Main menu scene without a camera shown over black (`Samples/ThirdPerson/Assets/Scenes/MainMenu.stscene` if it has
    no camera; otherwise a new scene with one canvas).
15. Editor viewport with the "Game UI" chip off vs on (screen canvases hidden in editor views; world canvases still
    drawn).
16. Gamepad navigation: focus highlight moving through a 3x3 grid (capture three frames).
17. The Performance panel showing `Render.UI` and `GPU.UI` stages on a UI-heavy scene (optional, for the engine track).

---

## 5. Rules and pitfalls ("why" boxes)

1. **Signal every direct write to a UI component** (`MarkModified`, `registry.patch`). Why: `GameUIScene` recomputes only
   what it was told changed; an unsignaled write leaves stale rects, quads and hit grids. Debug builds catch it in
   `Validate` and name the entity (DG 2639-2645; test `GameUILayoutTests.cpp` 575).
2. **Values written right after `AddComponent` need no signal** (the construct signal covers them; `GameUIComponents.h`
   26). Why: the element is laid out fresh.
3. **New UI components go in `GameUIComponents.h`, category "UI", `Requires("UIRect")`**, never in `Scene/Components.h`
   (DG 2631-2632). Why: the module must be removable, and a component without a rect draws nothing.
4. **The renderer never includes GameUI**; the UI pass registers through `SceneOverlayRegistry` (DG 2650). Why: layering
   (`Architecture.Layering`), builds without the module.
5. **`GameUIScene` holds handles, never `Ref`s or GPU objects** (DG 2647). Why: scenes are released on background
   threads; GPU objects must die on the main thread with the device.
6. **Layout never rasterizes glyphs**; text is measured with `ShapeText` (DG 2635). Why: layout runs headless (editor
   commands, servers, tests) and must not depend on GPU atlas state or budgets.
7. **Quads refer to UI texture and font indices, never bindless slots or atlas positions** (Arch 3063-3064). Why: mip
   streaming moves slots and each renderer has its own atlas; quads would otherwise rebuild every time.
8. **Masks clip in the shader, never by splitting draws** (DG 2672). Why: one draw per canvas; scissor changes would
   break batches.
9. **Code that tests where an element is shown or hit uses `GetVisibleBox`** (DG 2674-2676). Why: what a mask hides must
   not be clicked; tests, `input.click` and editor picking must agree with the player.
10. **`UIQuad` and the shader structs change together** (`GameUIRenderData.h` 9; `UIQuad.slang` 4). Why: a silent layout
    mismatch corrupts every UI draw; the `static_assert`s guard the size only.
11. **Only `GameUISystem` reads the pointer for the UI and sets keyboard capture** (DG 2683, 2717). Why: one owner of
    capture state; any other setter leaves the game deaf to keys or clicks.
12. **Hit-test against the layout of the game's input screen (`GetInputScreen`)**, i.e. the pixels the game renders, not
    the window's logical size. Why: on Retina or at a fixed Game view resolution the hit would miss what is drawn
    (DG 2683-2690; test `GameUIInputTests.cpp` 502).
13. **World-space canvases: project or ray-intersect, never divide pixels by the scale** (DG 2718-2721). Why: their scale
    is 1 canvas unit = 1 unit in their own plane; perspective has no single scale.
14. **The UI runs on unscaled time** (DG 2714). Why: pause menus at time scale 0 must still fade, repeat keys and blink
    carets. Scripts animating UI use `Time::GetUnscaledDeltaTime`.
15. **Widget values change with `registry.patch` in the running scene, without undo** (DG 2697). Why: play mode is a copy;
    player input is not an editor edit.
16. **Values set from code raise no events** (`SceneServices.h` 547-551). Why: no feedback loops between script and UI;
    events report the player.
17. **Read navigation through the UI action map, not raw keys** (DG 2703-2706). Why: players rebind; a game's own
    `Left` action does not interfere because names are qualified `UI/Left`.
18. **The UI system runs before Scripting (soft order)** (`GameUIRegistration.cpp` 15-19). Why: scripts see this frame's
    events and an already-captured pointer, so a click on a button never also fires a weapon.
19. **Disabled selectables still block** what is under them (DG 2700-2702). Why: a greyed button over the world must not
    let clicks through.
20. **An idle frame costs a pointer comparison** (tests `GameUIInputTests` / perf budgets). Why: every scene updates the
    UI system; HUD-heavy games must not pay per element per frame. Only selectables showing a non-rest state keep a
    record.
21. **Keep `UIInputField.TextElement` a `UIText` element and give the field a `UIMask`** to clip long lines (Manual
    93-98; `GameUIComponents.h` 255-260). Why: the field's text element draws the field's text, caret and selection;
    without a mask a scrolled line spills.
22. **Text default `RaycastTarget` is off, image default on** (component defaults). Why: a label should not steal or block
    clicks; a panel background should block the game.
23. **Hierarchy changes go through `Scene`** (`SetParent`) as everywhere; reparenting plain entities is free for the UI
    (Arch 3045-3048).
24. **Known limitation (do not promise more):** world-space canvases are unlit, drawn after post-processing, and the
    game's hit tests on them ignore scene geometry in front (editor picks do check meshes) (Roadmap 708-709; 0.4.0
    notes 316-317). The 2D mode edits screen-space canvases only.

---

## 6. Hands-on

Game developers:

1. **First menu** (easy): Hierarchy > + > UI: canvas, panel, vertical layout, title and three buttons; a `MainMenu`
   script handling `OnUIClick` via the buttons' Event Target; make it the start scene without a camera. Proves: the
   entity model of UI, event targets, the camera-less menu scene.
2. **HUD that survives every screen** (easy): score top-right, health bar stretched along the bottom with a filled
   image driven by `SetValue`/`FillAmount`; check with `ui.layout` at 1280x720, 2560x1440 and 3440x1440. Proves:
   anchors, ScaleWithScreen, Match Width Or Height.
3. **Pause menu at time scale 0** (medium): open on Cancel, `Time::SetTimeScale(0)`, a fading panel on unscaled time,
   volume slider wired to `Audio::SetMasterVolume`, gamepad navigation with `FirstSelected`. Proves: unscaled time,
   focus, UI actions, values from code raising no events.
4. **Settings screen** (medium): toggle group for quality presets (exclusive group), sliders with `WholeNumbers`, a name
   input field with `CharacterLimit`, `OnUISubmit`. Proves: toggles/groups, sliders, input fields, keyboard capture.
5. **Scrolling credits / list** (medium): the ThirdPerson pattern: content moved inside a `UIMask` with Softness.
   Proves: masks clip drawing and hits; moving content via `SetProperty` (signals automatically).
6. **A shop sign in the world** (medium): world-space canvas with `WorldUnitsPerUnit`, a clickable button on it through
   the game camera. Proves: world-space canvases, ray hit testing.
7. **Agent-built UI** (medium): build exercise 1 entirely with `ui.create` and verify with `ui.hitTest` and
   `input.click` in play mode. Proves: commands are the API; testing UI without eyes.

Engine developers:

1. **Trace a frame** (easy, reading): set breakpoints in `GameUISystem::OnUpdate` and `GameUIRenderer::Prepare`, change
   one label and record which counters of `TakeStats` move. Proves: incremental model.
2. **Break the contract on purpose** (easy): write a `UIRect` field without `MarkModified` in a test; observe the Debug
   assert and the `Validate` message. Proves: the UI contract and why it exists.
3. **Add a fill direction "Radial360"** (hard): a new `UIFillDirection` value; quads cannot represent a pie by cutting
   a rect, so add a shader path (a new quad flag, angle in a spare field) and keep `UIQuad` 64 bytes; register the enum
   value, inactive reasons, tests in `GameUILayoutTests`/`GPUGameUITests`, feature test coverage. Proves: the
   C++/shader data contract, the quad pipeline, the feature-test rule.
4. **Add a `UIScrollView` component** (hard): content offset driven by the wheel (pointer capture already hides scroll
   from gameplay), clamped to content size via `FitContent`, masked; signal changes; extend hit tests and tests.
   Proves: layout, masks, input routing, the contract.
5. **Spacing between grid rows only** or **reverse-order stacking** in `UILayoutComponent` (medium): change
   `PlaceGroupChildren`/`GetGroupContentSize` consistently; add layout tests and a `Validate` pass. Proves: the
   measure/arrange symmetry.
6. **Explain the navigation heuristic** (medium): change the weight 2 in `Navigate` to 1 and to 4, run
   `GameUI.Navigation` tests, explain which fail and why. Proves: spatial navigation trade-offs.
7. **Measure** (medium, Release): run `Perf.GameUI.*` and `PerfGPU.GameUI.*`, then make every text a raycast target in
   the generator and compare hit-test candidate counts (`GetLastCandidateCount`). Proves: grids and budgets (and the
   rule that budgets only go down).
8. **Glyph outline thickness in pixels instead of em** (medium, design exercise): argue why em was chosen (scales with
   font size; SDF spread limits it to 0.1 em, `GameUIQuads.cpp` 473). Proves: SDF limits.

---

## 7. Glossary

- **Canvas**: an entity with `UICanvasComponent`; a root canvas defines a screen of UI (or a plane in the world).
- **Root canvas**: a canvas with no canvas among its ancestors; nested canvases are ordinary elements.
- **UI element**: an entity with a `UIRect` under (or being) a root canvas.
- **Canvas unit**: the UI's length unit; pixels = units x scale.
- **Scale (s)**: pixels per canvas unit for a screen, from the scale mode.
- **Reference resolution**: the screen size the layout is designed for (ScaleWithScreen) or the world canvas's size in units.
- **Match width or height**: 0..1 blend (in log space) between following the screen's width or height.
- **Content scale / DPI scale**: display density relative to 96 DPI; Retina is 2.
- **Safe area**: insets that keep UI away from screen edges (TV overscan, notches).
- **Screen space / world space (render mode)**: drawn over the image vs as a plane in the 3D scene.
- **Anchor (min/max)**: fractions of the parent rect that the element's edges follow.
- **Pivot**: the point of the rect that `Position` places and around which it lies.
- **Stretched axis**: an axis where AnchorMin != AnchorMax; the rect's size follows the parent (margins).
- **Margin**: distance between an element's edge and its anchors' edge along a stretched axis.
- **Fit content**: the rect takes its content's size (text or layout children) on chosen axes.
- **Layout group**: `UILayoutComponent`, places its children in a stack or grid.
- **Preferred size**: what an element asks of a layout group (its Size, or its content size when fitted).
- **Measure / arrange**: the two phases of layout: sizes bottom-up, positions top-down.
- **Depth-first order**: parent before children, siblings in order; the UI's draw order.
- **Subtree range**: `[index, SubtreeEnd)`, the contiguous elements of one subtree.
- **Sort order**: integer ordering of root canvases; higher draws on top and gets input first.
- **Dirty flag / dirty mark**: a record that something must be recomputed.
- **UI contract**: the rule that direct writes to UI components must be signaled.
- **entt signal (on_construct/on_update/on_destroy)**: callbacks EnTT fires when a component is added, patched or removed.
- **`registry.patch` / `MarkModified`**: ways of writing a component that fire `on_update`.
- **Validation**: comparing cached results with a full recomputation.
- **Layout (cached)**: a canvas laid out for one size in units; up to four kept.
- **Shaping**: turning text into positioned glyphs from font metrics.
- **Glyph / advance / kerning / baseline / em**: a character's shape / its pen step / pair spacing / line it sits on / the font-size unit.
- **SDF (signed distance field)**: a texture storing distance to a shape's edge; crisp at any scale, cheap outlines.
- **Glyph atlas**: a texture packing rasterized glyphs; per renderer here, with a raster budget per frame.
- **Ellipsis / truncate / overflow**: what text does when it does not fit.
- **Nine-slice**: a texture cut into 3x3 pieces so corners keep size while edges and center stretch.
- **Filled image**: an image cut to a fraction along a direction (bars, cooldowns).
- **Quad**: a rectangle drawn as two triangles; the UI's unit of drawing (`UIQuad`, 64 bytes).
- **Instancing / vertex pulling**: one draw of N instances, the shader reading per-instance data from a buffer by index.
- **Bindless texture / slot**: a texture reached by an index into a global table instead of a binding per draw.
- **Draw run / batch**: a range of quads drawn in one call.
- **Push constants**: small per-draw data passed directly to shaders.
- **Clip rect / mask**: a rectangle outside which descendants are neither drawn nor hit.
- **Softness**: fade distance of a mask edge.
- **Pixel snapping**: rounding edges and baselines to whole pixels for crispness.
- **Display (sRGB) values**: gamma-encoded colors as shown; the UI blends in them.
- **Overlay pass**: a pass a module adds to every scene renderer via `SceneOverlayRegistry`.
- **Reversed-Z**: depth convention near = 1, far = 0 (taught in rendering chapters).
- **Camera-relative transform**: positions offset by the camera before going to the GPU, for precision far from origin.
- **Raycast target**: an element the pointer can hit (image/text with RaycastTarget, or a selectable).
- **Hit test**: finding the element under a point.
- **Uniform grid**: spatial index dividing space in equal cells.
- **Half-open rect**: min edges inside, max edges outside, so neighbours never both hit.
- **Gesture**: a press-to-release sequence owned by the UI or by the game.
- **Pointer capture / keyboard capture**: hiding mouse or keyboard input from gameplay while the UI owns it.
- **Selectable**: `UISelectableComponent`, the state and navigation part of every widget.
- **Visual state**: Normal, Hover, Pressed, Focused, Disabled.
- **Transition**: how a state shows: color tint or image swap.
- **Focus**: the selectable that receives Submit and navigation.
- **Spatial (automatic) navigation**: choosing the next focus by geometry.
- **UI actions / UI map**: the rebindable input actions `UI/Submit`, `UI/Cancel`, `UI/Up/Down/Left/Right`.
- **Key repeat**: synthetic repeated presses while held (0.4 s, then every 0.1 s).
- **Hysteresis (stick)**: different press and release thresholds so a stick near the threshold does not flicker.
- **Caret / selection anchor**: insertion point / the other end of a selection.
- **Code point / UTF-8 continuation byte**: a Unicode character / a byte `10xxxxxx` inside a multi-byte character.
- **Placeholder**: text shown while a field is empty.
- **Event target**: another entity whose scripts also receive a widget's events.
- **Scene service**: an interface a scene system offers to others (`IUIEvents`, `IUIControl`).
- **Unscaled time**: real time unaffected by time scale.
- **Scene system**: a per-scene update unit with declared order (here "UI").
- **Canvas mode (2D)**: the editor viewport view that edits one canvas at its reference aspect.
- **Screen view**: zoom and offset of the game's screen within an image (`SceneScreenView`).

---

## 8. Proposed chapters

1. **"What a game UI must do"** (concept, both, S): the problem, retained vs immediate mode, Strata's choice, a tour of
   a menu from components to pixels. Prereq: ECS basics.
2. **"Making menus and HUDs in the editor"** (tutorial, game, L, ~10 screenshots): canvases, anchors, scale modes, images,
   text, layout groups, masks, 2D mode, Game UI chip, camera-less main menu. Prereq: editor basics.
3. **"Making UI do things: widgets, events and scripts"** (tutorial, game, M, ~4 screenshots): buttons, toggles, sliders,
   input fields, event targets, `GetUI()`, focus, gamepad navigation, pause menus on unscaled time, world-space signs.
   Prereq: scripting basics, chapter 2.
4. **"Rects, anchors and layout: the algorithm"** (internals, engine, L, 0-1 screenshots): coordinate space, scale
   formula, rect math, measure/arrange per axis, groups, grids, fit content, slider parts, clip rects. Prereq: chapter 1,
   vectors.
5. **"Doing only what changed: the UI contract"** (internals, engine, M): signals, dirty marks, re-layout roots,
   hierarchy and activity journals, multi-layout cache, validation, stats; the tests that pin it. Prereq: chapter 4,
   transform contract chapter.
6. **"Text in the UI"** (internals, both, M, ~2 screenshots): shaping vs rasterizing, overflow, field lines and carets;
   pointers to the font/atlas chapter for SDF atlases. Prereq: chapter 4, text rendering chapter.
7. **"Drawing the UI: quads, batching and the overlay pass"** (internals, engine, L, ~4 screenshots): `UIQuad`, slots
   and journals, indirection tables, uploads, runs, the shaders (SDF rects, glyph outlines, masks, snapping, sRGB),
   world-space canvases on the GPU, overlay registry. Prereq: chapters 4-6, GPU basics, bindless, reversed-Z,
   camera-relative space.
8. **"Pointing, clicking and focus: UI input"** (internals, engine, L, ~2 screenshots): hit testing and grids,
   world-space rays, gestures and capture, widget state machines, navigation, UI actions and repeat, input fields,
   event dispatch, the script bridge. Prereq: chapter 4, input and input actions chapter, scripting ABI chapter.
9. **"Testing and automating game UI"** (tutorial/reference, both, S): `ui.create`, `ui.layout`, `ui.hitTest`,
   `input.click`/`input.type`, simulated input in doctest, perf budgets. Prereq: chapters 3 and 8, editor automation
   chapter.
10. **"Game UI reference"** (reference, both, M): every component and property with defaults and ranges, enums,
    `UIElement`/`UI` API, callbacks, commands. Prereq: none (lookup).

---

## 9. Not determined

- **Not read in full**: `GameUIComponents.cpp` inactive-reason helpers (120-205 skimmed), the bodies of
  `EditorUICommands.cpp` (only registration headers), `GameUIPresets.cpp` (what each preset's look is), `UIRectEdit.cpp`
  beyond `ApplyPreset`/margins, `CanvasEdit.*`, `Panels/CanvasModeView.*`, `UI/UIRectDrawer.cpp`,
  `UI/ComponentDrawers.*`, `Editor/EditorInputCommands.cpp` (only the UI branch of `input.click` at ~1238-1280),
  `Input/Input.cpp` (capture implementation), `Include/SDFText.slang`, `FontAtlasCache`/`FontAtlas`, `ShapeText`
  implementation (`Renderer/TextLayout.cpp`), the test bodies beyond the ones cited, `UIFeatures.cpp` beyond its header,
  sample scenes' contents.
- **Which sample scenes have world-space canvases**: `Samples/Showcase/Assets/Scenes/Outpost.stscene` and
  `OpenWorld/Assets/Worlds/Island.stscene` contain `UICanvas`; whether any is `WorldSpace` was not checked. Screenshot
  13 needs this confirmed (or a purpose-built scene).
- **Whether `MainMenu.stscene` (ThirdPerson) has a camera** (for the "UI over black" screenshot): not checked.
- **"18 host functions"** (Roadmap 389) vs the 15 UI host functions counted in `ScriptABI.h` 623-637: the other three are
  presumably unscaled time and typed text etc. from the same stream; not verified.
- **Touch input**: no touch support was found in the module; the book should not claim it (confirm with the input area).
- **Stick hysteresis values** for the UI map live in `InputActionSet::GetDefaultUIActions` (input area), not read.
- **Exact `Space` binding for Submit**: SDK `UI.h` 17-18 and the Manual say Enter, keypad Enter, Space or gamepad A;
  `UIActions.h` 12-13 says Enter, Escape, arrows: the default set should be confirmed in `InputActionSet`.
- **Release history inside 0.4.0-0.7.0** for individual sub-features (masks, input fields, world space all appear in
  0.4.0 notes; any later refinements to the UI between 0.5.0 and 0.7.0 beyond the 0.6.0 action map were not traced in
  git history).
- **IME / composition text** for East Asian input: nothing found; presumably unsupported.
