# Allocation: ui

## `ui/what-game-ui-does` — What a game UI must do

**Covers.** The page opens with the problem as a player meets it, on the part's running example: the Third-Person
sample's main menu (`Samples/ThirdPerson/Assets/Scenes/MainMenu.stscene`, its script `Scripts/MainMenu.cpp`). The menu
must look the same at 1280x720, 2560x1440 and 21:9; answer the mouse, the keyboard and a gamepad; keep moving while the
game runs at time scale 0; and never let the click on Play also reach the game. The naive answer is text and sprites at
pixel positions, drawn by game code every frame (before 0.4.0 Strata's only UI was screen-space text sized in pixels).
The page shows where it breaks: other resolutions, no focus for a gamepad, no order for clicks, work in every frame.

Then the idea: a UI is a tree of rectangles, laid out for one screen, drawn in tree order and hit topmost first. The
approaches follow, each from the flaw of the one before, with a table of cost, quality and who uses them: immediate
mode (Dear ImGui, which the Strata editor uses: code declares the UI again every frame) and retained mode (Unity's uGUI,
Unreal's UMG, Godot's Control nodes, the web's DOM: a tree that stays, laid out and drawn by the engine). Strata's
choice, in a `:::why` aside: retained, and made of entities. A UI element is an entity with a `UIRect` under a root
canvas, authored in the editor, saved with the scene, made into a prefab; references between widgets are entity
properties that duplicating and pasting remap; layout and drawing cost work only when something changes. The tour then
takes the menu from components to pixels: the eleven components and what each one does (the menu uses ten of them; the
input field is the eleventh), screen-space and world-space canvases, the focus as the one widget that keys act on, and
one frame (the "UI" scene system before the scripts, the overlay pass after post-processing). The module map shows the
GameUI layer, which only the composition root includes, so an engine without it still renders and plays. The page
ends with what the choice cannot do (no scroll views, drop-downs, rich text or multi-line fields) and with common
mistakes. Its three exercises search for the module's one include outside its folder, play a playground button at time
scale 0, and design the menu in immediate mode. At the end the reader can say why a game UI is retained here, name the
eleven components, and say which page of the part explains each step of the tour.

**Leaves out.**

- Making a HUD and a menu in the editor → `make/hud`, `make/menus`
- Why the editor's own interface is immediate mode, and Dear ImGui itself → `editor-ui/immediate-mode`, `editor-ui/imgui`
- The algorithms behind each step of the tour → `ui/layout`, `ui/contract`, `ui/text`, `ui/drawing`, `ui/input`
- Fonts, text shaping and glyph atlases → `gpu/text`
- The UI map of input actions and its bindings → `input/actions`
- Building and testing a UI through editor commands → `make/automated-playtests`
- Every property with its default and range → `reference/components`

**Fit.** `fits`: about 3,500 words against M (3,000). The tour from components to pixels takes the most words: each of
the eleven components in one sentence with a link, the module map and the frame timeline; the approaches and their
table come next.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gameui:264` | concept | home | What a game UI must do; immediate against retained mode; why Strata's is retained and made of entities; the mistake of taking the editor's ImGui panels for the game UI |
| `gameui:42` | feature | home | The GameUI module is a layer of its own (Core, Input, Asset, Reflection, Scene and Renderer below it); only the composition root includes it |
| `gameui:43-44` | feature | home | `RegisterGameUIModule` registers the components, the overlay pass and the "UI" scene system; the components share the category "UI", and every one but `UIRect` requires `UIRect` |
| `new:2` | erratum | home | The page says eleven components, never twelve. Evidence: `Strata/src/Strata/GameUI/GameUIComponents.cpp:211-397` holds eleven `ComponentRegistry::Register` calls (UICanvas, UIRect, UIImage, UIText, UISelectable, UIButton, UIToggle, UISlider, UILayout, UIInputField, UIMask); `plan/inventory/gameui.md:44` counts 12 |
| `gameui:46` | feature | home | An engine without the module still renders and plays: the renderer reaches the UI only through the overlay registry, scripts only through scene services |
| `gameui:66-67` | feature | home | Widget parts and event targets are entity properties, remapped by duplicate, paste and prefab instances; the UI is saved and loaded like any component, out-of-range values clamped |
| `gameui:226` | feature | home | The part's running example: the Third-Person main menu (its buttons, settings sliders and toggles, the credits in a mask); the other samples' HUDs and loading screens in one sentence |
| `new:3` | feature | home | The module's history for the page's `since`: the whole module arrived in 0.4.0; the rebindable UI map in 0.6.0, before which navigation used fixed keys. Evidence: `Docs/Releases/0.4.0.md:52-59`, `Docs/Releases/0.4.0.md:319-320`, `Docs/Releases/0.6.0.md:99-100` |
| `gameui:435` | figure | home | Module map: the GameUI layer and its neighbours, with the arrows that show that Renderer and Scripting do not include it |
| `gameui:438` | figure | home | Frame timeline: the "UI" scene system (actions, layout for the input screen, hits, focus, events) before the scripts' `OnUpdate`, then the renderer's world canvases, post-processing, screen text and screen canvases |
| `new:1` | not-done | home | No scroll views, drop-downs, rich text or multi-line input fields: a mask clips a scrolling list, and an input field is one line. Evidence: `Strata/src/Strata/GameUI/GameUIComponents.cpp:211-397` registers no such component; `Strata/src/Strata/GameUI/GameUIComponents.h:255-260, 272-279`; `git grep -niE "scrollview\|scroll view\|dropdown\|drop-down\|richtext\|rich text" 822a7a46 -- Strata/src/Strata/GameUI` finds nothing (the one match of "multiline" is the Inspector flag of `UIText`'s Text, `GameUIComponents.cpp:287`) |
| `gameui:617`, `gameui:619` | term | home | Canvas; UI element |
| `gameui:626` | term | home | Screen space and world space (the canvas's render mode) |
| `gameui:672` | term | home | Focus, at the level of the tour: the one widget that Submit and the direction keys act on |
| `editor-ui:700`, `editor-ui:701` | term | home | Immediate-mode GUI (code describes the UI every frame, the library keeps little state) and retained-mode GUI (a tree of widgets that keeps its state), defined with the approaches table; `editor-ui/immediate-mode` uses both |
| `new:14` | hands-on | home | Exercises (D27), from easy to hard: Basic, trace: predict which engine files outside `Strata/src/Strata/GameUI` include a GameUI header, then search (only the composition root, which lists the module beside the others); Medium, predict then run (done): in the playground, a button made with Hierarchy > + > UI > Button and a script on it that sets the time scale to 0 in `OnCreate` and logs `UI::IsPointerOverUI()` and `Input::IsMouseButtonPressed` in `OnUpdate`: say first whether the hover tint still fades, whether `OnUIClick` still comes and which presses the game sees, then play; Hard, design: the same menu in immediate mode, and what each approach does on a frame where nothing changes and when a gamepad moves the focus. Evidence: `Strata/src/Strata/Engine/BuiltinModules.cpp:61-77` (`git grep -l '#include "Strata/GameUI/' 822a7a46 -- Strata/src` finds `BuiltinModules.cpp` and the module's own files); `StrataEditor/src/Editor/GameUIPresets.cpp:112`; `StrataScriptCore/Include/StrataScript/UI.h:156-162`; `Strata/src/Strata/Input/Input.h:94-97`; `Strata/src/Strata/GameUI/GameUISystem.cpp:880-931` |
| `gameui:53-65` | feature | link | The tour names each component in a sentence and links the page that explains it |
| `gameui:142` | feature | link | The overlay pass that draws the canvases (`ui/drawing`) |
| `gameui:176` | feature | link | The UI system's order in one frame (`ui/input`) |
| `gameui:185` | feature | use | The UI map that menus navigate with, in one sentence (its home is `input/actions`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Entities, components and the registry | `world/ecs` | must |
| The hierarchy: parents, children, sibling order, active in hierarchy | `world/scene-graph` | must |
| One frame from start to finish, frame time | `start/what-an-engine-is` | must |
| Reflection: one registration for the Inspector, files and scripts | `world/reflection` | helps |
| Scenes saved as documents | `world/serialization` | helps |
| Prefabs and instances | `world/prefabs` | helps |
| Scene systems and their order; scene services | `world/systems` | helps |
| Layers, the composition root and optional modules | `core/layers-registries` | helps |
| Overlay passes drawn over the finished image | `gpu/debug-drawing` | helps |
| Time scale and unscaled time | `core/time` | helps |
| Input actions and maps | `input/actions` | helps |
| Script callbacks | `scripting/script-system` | helps |
| Post-processing and tone mapping, which the screen UI draws over | `image/why-post` | helps |
| Dear ImGui, for the comparison | `editor-ui/imgui` | helps |

## `ui/layout` — Rects, anchors and layout

**Covers.** The job: turn the UI components of a canvas into one box per element for one screen, in canvas units.
Drawing and input read the boxes; this page makes them. The page carries the part's full section on the problem and
how engines solve it: absolute pixel positions; anchors with offsets (Unity's RectTransform, Unreal's anchors, Godot's
anchors and offsets); constraint solvers (Cassowary, Auto Layout); flexbox (Yoga); and the measure-and-arrange split of
WPF and Flutter. The map shows `GameUIScene`, one per scene in the registry's context, holding handles and never GPU
objects, with its root canvases, their element arrays and their layouts, and the code that asks for a layout (the UI
system for the input screen, the UI pass for its view, and the editor's tools: the `ui.*` commands, `input.click` and
the canvas mode). A toy of about 50 lines lays out one axis of anchored rects and a vertical stack.

The real code follows in the order the data flows, on the Third-Person main menu. First the coordinate space: canvas
units, +Y down, (0, 0) at the top left, display colors, against the world's +Y up. Then the scale: the three scale
modes, `ComputeScale` with its interpolation in log space (why a screen twice as wide and half as tall keeps the scale
1), the content scale of Constant Physical Size (the window's factor, said in one sentence with a link to
`core/windows-events`), the safe area, and the Tetris HUD at three screen sizes. Then the
rect: anchors as fractions of the parent, the pivot, the position, and a size added to the anchored span, so that point
anchors give a fixed size and stretched anchors give margins. Then the tree as an array: a depth-first walk with an
explicit stack, parents before children, each subtree the range `[i, SubtreeEnd)`; nested canvases are plain elements,
and only root canvases have a sort order. Then the two passes, widths before heights because a wrapped text's height
depends on its width, each with preferred sizes bottom-up (memoized) and boxes top-down in `LayOutAxis`. Then layout
groups and grids in `PlaceGroupChildren`, fit content in `GetPreferredSize`, a slider's fill and handle anchored to
its value, results that are not finite set to zero, and the clip rects of masks. The page ends with the queries other
code reads, the alternatives Strata did not choose, the tests (`GameUI.Layout`, `.Scale`, `.Mask` and the GPU test of
the Tetris HUD), changing it safely: where a new UI component goes, and keeping measure and arrange in step, and two
exercises (the menu's layout traced with breakpoints, a group's spacing changed). At the end the reader can compute any
element's box by hand from its components and the screen, and find the line of code that does each step.

**Leaves out.**

- How a change reaches the layout, and the layouts kept per screen size → `ui/contract`
- Shaping text and measuring it → `gpu/text`, `ui/text`
- Drawing the boxes and clipping pixels to the masks → `ui/drawing`
- What the pointer hits inside a mask → `ui/input`
- The Inspector's anchor presets and the UI Rect drawer → `editor-ui/inspectors`
- The viewport's canvas mode → `editor-ui/scene-view`
- Placing a HUD in the editor → `make/hud`
- A world-space canvas's plane in the scene → `ui/drawing`

**Fit.** `over`: about 7,300 words against L (5,000). Seven excerpts (the rect comment, the canvas, `ComputeScale`, the
walk, `LayOutAxis`, `PlaceGroupChildren`, `GetPreferredSize`), five concepts taught from zero, seven figures, the
part's full section on the problem and two exercises pass L's top of 6,500; by S2 the page takes XL, whose range holds
the estimate.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gameui:274` | concept | home | Coordinate spaces: pixels, canvas units, +Y down; the contrast with the world's +Y up; the mistake of mixing them |
| `gameui:279` | concept | home | Resolution independence: the three scale modes, interpolation in log space, content scale, safe areas; the mistake of a tiny UI at 4K |
| `gameui:286` | concept | home | Anchors and pivots: size added to the span, point and stretched anchors; the approaches (absolute, anchors, solvers, flexbox); the mistake of giving a stretched rect its full width as Size, which doubles it (along a stretched axis Size 0 fills the parent and a negative Size leaves margins) |
| `gameui:292` | concept | home | The UI as a tree: draw order is hierarchy order, a tree flattened into an array with subtree ranges; only canvases have a sort order |
| `gameui:297` | concept | home | Measure and arrange per axis: preferred sizes bottom-up, boxes top-down, widths before heights; no flex shrink; the mistake of setting a child's anchors inside a layout group, where they do nothing unless the child sets `IgnoreLayout` |
| `gameui:52` | feature | home | The coordinate and color conventions of `GameUIComponents.h` |
| `gameui:53-54` | feature | home | `UICanvasComponent` and its scale modes |
| `gameui:56` | feature | home | `UIRectComponent`: anchors, pivot, position, size, `FitContent`, `IgnoreLayout` |
| `gameui:63` | feature | home | `UILayoutComponent`: horizontal, vertical, grid, padding, spacing, nine-way alignment, stretch, cell size, columns |
| `gameui:65` | feature | home | `UIMaskComponent`: the clip rect it makes, its padding, nested masks |
| `gameui:45` | feature | home | The Inspector greys out a property that another turns off, with its reason (Match Width Or Height only with Scale With Screen; slice borders only when Sliced; neighbours only for Explicit navigation); the mechanism, `SetInactiveReason`, is `world/reflection`'s, and how the Inspector shows a reason is `editor-ui/inspectors`' |
| `gameui:73-78` | feature | home | `GameUIScene`: one per scene, handles only; root canvases; the element array with `SubtreeEnd`; widget parts resolved by UUID, each an element of the widget's own canvas, and a slider's fill and handle only after the slider in draw order (the slider itself or an ancestor is ignored, because it would move what places it); the scale per screen and the size in units; `UIScreen` and `UICanvasView` |
| `gameui:86` | feature | home | The queries other code reads: element count, entity, box, subtree end, visibility, raycast target, clip, visible box, `FindElement` |
| `gameui:99-108` | feature | home | The root rect and safe area, the rect math per axis, the two passes, groups, grids, `IgnoreLayout`, fit content, slider parts, finite results, clip rects |
| `gameui:224` | feature | home | The Tetris HUD on a canvas, and the GPU test that checks it covers the same fraction at 1280x720 and 2560x1440 |
| `gameui:235` | feature | home | The suites `GameUI.Layout`, `.Scale` and `.Mask` of `GameUILayoutTests.cpp` (`.Dirty` is `ui/contract`'s) |
| `gameui:394` | code | home | `Strata/src/Strata/GameUI/GameUIComponents.h:74-88`: `UIRectComponent` and the comment that states the rect model in five lines |
| `gameui:395` | code | home | `Strata/src/Strata/GameUI/GameUIComponents.h:41-64`: `UICanvasComponent`, what a canvas configures, screen and world space |
| `gameui:396` | code | home | `Strata/src/Strata/GameUI/GameUIScene.cpp:80-104`: `ComputeScale`, the three modes, `exp2` of the interpolated `log2`, clamps and the guard against values that are not finite |
| `gameui:403` | code | home | `Strata/src/Strata/GameUI/GameUIScene.cpp:566-602`: the depth-first walk with an explicit stack, children pushed in reverse, and the subtree ends computed backwards |
| `gameui:397` | code | home | `Strata/src/Strata/GameUI/GameUILayout.cpp:216-285`: `LayOutAxis`, the anchored rect per axis, fitted sizes, slider parts, groups placing their children |
| `gameui:398` | code | home | `Strata/src/Strata/GameUI/GameUILayout.cpp:287-367`: `PlaceGroupChildren`, stacks, grids, alignment and stretch |
| `gameui:399` | code | home | `Strata/src/Strata/GameUI/GameUILayout.cpp:369-407`: `GetPreferredSize` and `GetContentSize`, the memoized measure pass, a text's height at the width it has |
| `gameui:442` | figure | home | Rect math: the parent box, the anchor points, the span, the size added, the pivot and the position; point anchors 200x50 beside stretched anchors with size (-20, -20) |
| `gameui:444` | figure | home | The 4x4 anchor presets and what each does to a HUD element at three aspect ratios |
| `gameui:445` | figure | home | Scale against screen width for the three modes; Scale With Screen with match 0, 0.5 and 1 |
| `gameui:449` | figure | home | The element array with its Parent and SubtreeEnd fields, one subtree marked as `[i, end)` |
| `gameui:447` | figure | home | The layout passes on a vertical group that holds a fitted text: sizes up, boxes down, x before y |
| `gameui:477` | figure | home | The Tetris HUD at 1280x720, 2560x1440 and 21:9 under Scale With Screen, and the same at Constant Pixel Size (`Samples/Tetris`, or `ui.layout` and a viewport capture) |
| `gameui:489` | figure | home | A vertical menu (Title, Play, Settings, Quit) and the same buttons in a grid; Stretch Children off and on |
| `gameui:516` | rule | home | A new UI component goes in `GameUIComponents.h`, category "UI", `Requires("UIRect")`, never in `Scene/Components.h`: the module stays removable, and a component without a rect draws nothing |
| `gameui:520` | rule | home | `GameUIScene` holds handles, never `Ref`s or GPU objects: scenes are released on background threads |
| `gameui:602` | hands-on | home | Exercise: spacing between grid rows only, or reverse-order stacking, changed in `PlaceGroupChildren` and `GetGroupContentSize` together, with layout tests and a `Validate` pass |
| `gameui:618`, `gameui:620-623`, `gameui:625` | term | home | Root canvas; canvas unit; scale; reference resolution; match width or height; safe area |
| `gameui:627-637` | term | home | Anchor; pivot; stretched axis; margin; fit content; layout group; preferred size; measure and arrange; depth-first order; subtree range; sort order |
| `gameui:656` | term | home | Clip rect and mask |
| `new:15` | hands-on | home | Trace it yourself (D27): breakpoints in `LayOutAxis` and `GetPreferredSize` while the Third-Person main menu's vertical group is laid out show every width found before any height, each preferred size measured once, and the box of one button, which the reader first computes by hand from its rect and the screen. Evidence: `Strata/src/Strata/GameUI/GameUILayout.cpp:216-285`, `:369-407` |
| `gameui:624` | term | link | Content scale, said in one sentence with Constant Physical Size (its home is `core/windows-events`) |
| `gameui:315` | concept | link | The UI contract, which keeps these boxes current (`ui/contract`) |
| `gameui:528` | rule | link | Code that asks where an element is shown uses its visible box (`ui/input`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| What a canvas, an element and each UI component are | `ui/what-game-ui-does` | must |
| Trees, depth-first walks and stacks | `basics/trees-graphs` | must |
| Powers of two and logarithms | `basics/numbers` | must |
| Lerp and its weight | `basics/math-interpolation` | must |
| The hierarchy: parents, children, sibling order, active in hierarchy | `world/scene-graph` | must |
| Components, the registry, UUIDs as references | `world/ecs` | must |
| Shaping a text from font metrics with `ShapeText`, and the size it reports | `gpu/text` | must |
| Floating-point values that are not finite (NaN, infinity) | `basics/numbers` | helps |
| Boxes as a minimum and a size | `basics/math-geometry` | helps |
| A window's content scale | `core/windows-events` | helps |
| Inactive reasons (`SetInactiveReason`) | `world/reflection` | helps |
| A test case with doctest | `core/first-change` | helps |
| A GPU test that reads pixels back | `gpu/first-triangle` | helps |

## `ui/contract` — The UI contract

**Covers.** The job: keep the layouts, shaped texts, quads, clip rects and hit grids of `GameUIScene` true to the
scene while doing work only for what changed. The problem section is one paragraph: a retained UI must learn what
changed, and the scene's transform contract (`world/scene-graph`) already has the same shape. The map is the dirty
propagation: a signal, a mark on the element, the walk up to the re-layout root, the subtree laid out again, the boxes
compared, the quads marked, a range in the journal. The contract comes before the code, each rule with its reason:
every direct write to a UI component is signaled (`MarkModified`, `registry.patch`), and the writers that already
signal are named (`ComponentAccess`, the script API, the UI system), with `SetText`'s skip of a text that did not
change; values written right after `AddComponent` need none (the scene's rule, in one sentence with a link to
`world/scene-graph`); hierarchy changes go through `Scene`. A toy of about 40 lines caches a computed value behind a
dirty flag and shows how an unsignaled write goes stale.

The real code, on the Third-Person menu's Play label: the signals `GameUIScene` connects in its constructor, one set
per component, and how a change costs by its kind (`OnLayoutChanged` marks layout and quads, `OnVisualChanged` quads
only, `OnTextChanged` a reshape and a layout only when the rect fits its text); the hierarchy, activity and asset
content journals, activity read from the scene's transform change log, and what the UI does when a journal no longer
reaches back; `UpdateLayout`, which walks each mark up to the highest ancestor whose rect depends on its children,
drops nested roots and marks only the boxes that moved; why moving plain entities costs no canvas; `EnsureLayout`, with
up to four layouts per canvas keyed by the size in units, so a window resized at the same aspect lays out nothing; and
`Validate`, the full recomputation that Debug builds compare after every `EnsureLayout`, whose message names the entity
written without a signal. The tests pin it: an idle frame lays out, shapes and builds nothing, a label's text costs one
shaping, and an unsignaled write fails validation; the perf budgets of 10,000 elements and the idle frame show the
cost. The page ends with the alternatives (re-layout every frame, immediate mode, polling versions), changing it safely
(a new UI component connects its signals and states what each costs) and two exercises: trace a frame through the work
counters, and break the contract on purpose. At the end the reader can predict which counters a given change moves, and
explain why an unsignaled write is stale in Release and an assert in Debug.

**Leaves out.**

- The transform contract, which this contract mirrors → `world/scene-graph`
- The quads' journal and the partial uploads it drives → `ui/drawing`
- Hit grids rebuilt from hit stamps → `ui/input`
- Perf budgets, the reference machine and the rule that budgets only go down → `engineering/perf-lab`
- Edits from the editor, which signal through commands and undo → `editor/undo`

**Fit.** `over`: about 4,800 words against M (3,000). Six excerpts (the signals, the change handlers, `UpdateLayout`,
`EnsureLayout`, `Validate`, the tests) with two concepts, four rules, the writers that already signal and the internals
sections pass M's top of 4,000; by S2 the page takes L, whose range holds the estimate.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gameui:315` | concept | home | A retained UI needs change tracking: observers, dirty marks per element and per layout, the re-layout root, journals; the mistake of writing `UIRect.Size` without `MarkModified` |
| `gameui:323` | concept | home | Layouts cached per screen size in units, four kept, the least recently used replaced; the mistake of thinking every resize costs a layout |
| `gameui:79-84` | feature | home | The layout cache; lazy layout and draw order by sort order; change tracking through signals, hierarchy moves, activity and asset content; activity read from the scene's world-transform change log and filtered by the element index, so every moving body costs the UI one lookup; when the hierarchy log no longer reaches back, the canvas list and every canvas's elements are found again (the layouts kept for elements that stay), and when the transform log does not, every element's activity is checked; dirty marks; the re-layout root; reparenting plain entities for free |
| `gameui:91-92` | feature | home | `Validate` and the Debug assert after every `EnsureLayout`; `GameUISceneStats` and `TakeStats` |
| `gameui:109` | feature | home | Only elements whose box changed rewrite their quads and bump the hit stamp |
| `gameui:241` | feature | home | The perf tests `Perf.GameUI.Layout10k`, `Perf.GameUI.IdleFrame10k` and `PerfGPU.GameUI.Render10k`, and their budgets; `PerfGPU.GameUI.RenderIdle10k`, the UI pass of an idle frame, which checks that it uploads nothing at 10,000 elements and whose budget is provisional, with no measured value (the page says so and names no `perf.<name>` key for it, R41) |
| `gameui:401` | code | home | `Strata/src/Strata/GameUI/GameUIScene.cpp:106-149`: the constructor connecting `on_construct`, `on_update` and `on_destroy` of every UI component |
| `gameui:402` | code | home | `Strata/src/Strata/GameUI/GameUIScene.cpp:198-242`: `OnLayoutChanged`, `OnVisualChanged` and `OnTextChanged`, different changes at different costs |
| `gameui:400` | code | home | `Strata/src/Strata/GameUI/GameUILayout.cpp:87-159`: `UpdateLayout`, the walk up to the re-layout root, nested roots dropped, only moved boxes marked |
| `gameui:404` | code | home | `Strata/src/Strata/GameUI/GameUIScene.cpp:961-1023`: `DependsOnChildren` and `EnsureLayout`, the lazy layout, views sorted by sort order, the Debug validation |
| `gameui:405` | code | home | `Strata/src/Strata/GameUI/GameUIScene.cpp:1394-1459`: `Validate`, a cache checked by recomputation, the error that names the entity |
| `gameui:406` | code | home | `StrataTests/src/GameUI/GameUILayoutTests.cpp:485-586`: the idle frame that does no work, a change that costs its element, and the unsignaled write that fails validation |
| `gameui:451` | figure | home | Dirty propagation: change, mark, walk up, re-layout, compare boxes, mark quads, journal range, partial upload |
| `gameui:505` | figure | home | The Performance panel with the `Render.UI` and `GPU.UI` stages on a scene of many elements, idle and after one change |
| `gameui:511` | rule | home | Signal every direct write to a UI component: the scene's UI recomputes only what it was told; Debug builds name the culprit |
| `gameui:514` | rule | link | Values written right after `AddComponent` need no signal: the UI components follow the scene's rule, said in one sentence (its home is `world/scene-graph`) |
| `new:16` | feature | home | The writers that already signal: `ComponentAccess::SetProperty` (which the editor's property edits go through), the script API and the UI system; `IUIControl::SetText` patches only when the text changed, because games set their HUD every frame and a signal would reshape it, and on an input field it writes one line cut to the character limit. Evidence: `Strata/src/Strata/GameUI/GameUIComponents.h:24-26`; `Strata/src/Strata/Scene/ComponentAccess.cpp:117-146` (the signal at 144); `StrataEditor/src/Editor/PropertyEdit.cpp:104`, `:148`; `Strata/src/Strata/GameUI/GameUISystem.cpp:970-992` (the comment at 988); `StrataScriptCore/Include/StrataScript/UI.h:54` |
| `gameui:559` | rule | home | Hierarchy changes go through `Scene` (`SetParent`), as everywhere; reparenting plain entities costs the UI nothing |
| `gameui:551` | rule | home | An idle frame costs a pointer comparison: every scene runs the UI system, so a HUD must not cost per element per frame |
| `gameui:591` | hands-on | home | Exercise: trace a frame with breakpoints in `GameUISystem::OnUpdate` and `GameUIRenderer::Prepare`, change one label, and record which counters of `TakeStats` move |
| `gameui:593` | hands-on | home | Exercise: write a `UIRect` field without `MarkModified` in a test and read the Debug assert and the message of `Validate` |
| `gameui:639`, `gameui:642-643` | term | home | UI contract; validation; layout (cached) |
| `gameui:75` | feature | use | The element array and its subtree ranges, from `ui/layout` |
| `gameui:235` | feature | use | The suite `GameUI.Dirty` of `GameUILayoutTests.cpp` |
| `scene-ecs:28` | feature | use | `MarkModified` as `registry.patch`, the engine-wide signal of a change (`world/scene-graph`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The transform contract and change signals (`on_construct`, `on_update`, `on_destroy`; `MarkModified`, `registry.patch`) | `world/scene-graph` | must |
| The hierarchy version, and activity read through the transform change log | `world/scene-graph` | must |
| EnTT's registry, storages and context | `world/ecs` | must |
| The element array, the boxes and the two layout passes | `ui/layout` | must |
| Asserts compiled into Debug builds only | `core/conventions` | must |
| Asset content that changes when a font finishes loading | `assets/loading` | helps |
| Profiler stages and the Performance panel | `core/profiling` | helps |
| Breakpoints in a debugger attached to the engine | `core/debugging` | helps |
| Perf tests and their budgets | `engineering/perf-lab` | helps |
| A test case with doctest | `core/first-change` | helps |

## `ui/input` — UI input

**Covers.** The job: decide who owns each press, find what the pointer is over, keep the focus, turn presses into widget
events and hand them to the scripts, all in the "UI" scene system, on unscaled time, before the scripts run. Typing into
a field is `ui/text`'s. The page carries the full section on the problem and how engines solve it: hit tests by a
linear scan, a grid or a tree; routing by event bubbling (the DOM) or by raycasters (Unity's EventSystem); focus and
spatial navigation for keyboards, gamepads and televisions. The map is the system's update in order: the UI actions,
the layout for the input screen, the hit grids, dropping a focus that became unusable, the pointer, editing,
navigation, visual states, dispatch. The contract, each rule with its reason: only this system reads the pointer for
the UI and sets capture; hit tests use the game's input screen in rendered pixels; widgets write with `registry.patch`
and no undo; values set by code raise no events; navigation reads the UI map, not raw keys; the system runs before the
scripts; the UI runs on unscaled time. A toy of about 60 lines hit-tests a list of rects topmost first and keeps a
gesture.

The real code, on the Third-Person main menu, in the order of the update. Hit testing: raycast targets (images on by
default, texts off, every selectable), the uniform grid built by a counting sort with about two targets per cell, the
topmost canvas by sort order, the last drawn element first, half-open rects, what a mask hides never hit, every element
under a point for tools, and the hit resolved to its nearest selectable ancestor within its canvas, so that a button's
icon presses the button; one `ui.hitTest` line shows the editor's command running this same hit test.
World-space canvases: the ray from the game camera through the pointer (reversed-Z, the far
point at depth 0.5 so infinite far planes stay finite), the crossing in the canvas's own plane, the projection back to
pixels, after every screen canvas and nearest first, with geometry in front not checked. Gestures: a press over the UI
is the UI's until every button is up, pointer capture hides buttons and scroll from the game, only the left button
presses widgets, a binding capture's left press presses no widget, hover recomputed only when something that changes it
changed. Widgets as state machines: the selectable's states by priority, a click on release over the pressed widget, a
press that focuses, sliders dragged also outside their rect and not clicked on release, toggles and exclusive groups,
disabled widgets that still block, tint fades kept only while a state shows. Focus and navigation: the start selectable,
which the first direction press or Submit focuses when nothing has the focus (that press only focuses), Automatic
navigation scored by along plus two times across in screen pixels, Explicit and None, world canvases that navigate
within themselves, slider steps, Submit and Cancel, the UI map's default bindings. Events and the script bridge: events
queued in input order and dispatched at the end of the update, listeners safe to add and remove during dispatch,
`IUIEvents` and `IUIControl`, the 15 UI host functions, the four callbacks read only when `StructSize` covers them,
dispatch to the widget's scripts and then the event target's, the SDK's `UIElement` and `UI`, and the sample's
`MainMenu` script that handles every button through one event target. What went wrong before: `UI::IsActionPressed` kept
reporting a press while no canvas existed. The page ends with the alternatives, the tests (`GameUI.HitTest`, `.Capture`,
`.Events`, `.Navigation`, `.WorldSpace`, `Scripting.UI`, the feature script `UIFeatures`), changing it safely, and four
exercises, the first a trace of one click from the hit to `OnUIClick`. At the end the reader can say for any click which
element gets it and why the game does not, and trace a gamepad press to a script's `OnUIClick`.

**Leaves out.**

- Input actions, the UI map's bindings and the repeat timing → `input/actions`
- Pointer and keyboard capture and typed text inside `Input` → `input/devices-state`
- Coordinate spaces, the render resolution and content scale → `input/mouse-cursor`
- The Game view's resolution and who owns the keyboard in the editor → `editor-ui/game-view`
- Editing an input field → `ui/text`
- `input.click`, holds counted in fixed steps → `editor/stepping`
- Binding capture and the players' bindings file → `input/rebinding`
- The script system's dispatch in general and the host API's rules → `scripting/script-system`, `scripting/host-api`
- Building a menu with focus, a pause screen and a settings screen → `make/menus`

**Fit.** `fits`: about 9,000 words against XL (8,000). The real code takes the most words, in the order of the update:
hit testing, gestures, widgets, focus and navigation, events and the script bridge, each with its concept, excerpt and
figures; the eleven rules of the contract come next.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gameui:351` | concept | home | Hit testing: raycast targets, reverse draw order, sort order, half-open rects, masks, a uniform grid; world-space rays; what is pressed is not the element hit but its nearest ancestor with a `UISelectable`, never beyond its canvas (`FindSelectable`, `Strata/src/Strata/GameUI/GameUISystem.cpp:330-343`), so a button's icon presses the button and `ui.hitTest` reports both; only the left button presses widgets (the other buttons over the UI are still hidden from the game), and a dragged slider is not clicked on release; the mistakes of hitting outside a mask and of labels as targets |
| `gameui:358` | concept | home | Who owns a click: gestures, pointer capture, keyboard capture, the UI before the scripts; the mistakes of a button click that also fires the gun, and of a silent key while the player types |
| `gameui:363` | concept | home | Widgets as state machines: the states by priority, click on release, toggle groups, slider drag and steps, tint fades; the mistake of clicking on press |
| `gameui:367` | concept | home | Focus and spatial navigation: the start, Explicit against Automatic, the along plus two times across score, repeat, actions instead of keys; the mistake of a menu that shows no focus: nothing shows focus until the first press, which only focuses; without First Selected the start is the top-left selectable, so set First Selected or call `Focus()` when a menu opens |
| `gameui:376` | concept | home | Events that decouple game logic from widgets: queued and dispatched at one point in input order, event targets, values from code raise none; the mistake of expecting an event from a value a script set |
| `gameui:59-62` | feature | home | `UISelectableComponent`, `UIButtonComponent`, `UIToggleComponent`, `UISliderComponent` |
| `gameui:88-89` | feature | home | The input screen (the game window's pixels, content scale, input-to-pixel factor); the visual states stored for the system |
| `gameui:166-170` | feature | home | `GameUIHitTester`'s grids; the hit test's order; `HitTestAll` for tools; raycast targets; world-space canvases through the camera's ray |
| `gameui:176-184` | feature | home | The update order; a scene without canvases; gestures and capture; binding capture; hover only when needed; click, press and drag; toggles and groups; values through `registry.patch`; focus and `FocusChanged` |
| `audio-input:190` | feature | home | Taken from `audio-input`: the game UI's side of the captures (the UI system alone sets pointer and keyboard capture) and its reading of `UIActionState` once per update |
| `gameui:186-190` | feature | home | The start of navigation; Automatic navigation; slider steps; Submit and Cancel; visual states and their fades on unscaled time |
| `gameui:193-194` | feature | home | Events queued in input order, dispatched at the end of the update, listeners safe during dispatch; `OnRuntimeStop` and `OnEntityDestroying` |
| `gameui:201-205` | feature | home | `UIEventType`, `UIEventInfo` and `IUIEvents`; `IUIControl`; the 15 UI host functions; the four callbacks; dispatch to the widget's scripts, then the event target's |
| `gameui:206`, `scripting:131` | feature | home | The SDK's `UIElement` (`entity.GetUI()`), `UI` (focus, the pointer, the actions) and `UIAction`: one entry for the engine's item and the SDK's classes, which `reference/script-api` lists with a link (R31, D26) |
| `gameui:230` | feature | home | The feature script `UIFeatures.cpp`, a frame-by-frame player that clicks, toggles, drags, navigates, types and edits |
| `gameui:236` | feature | home | The suites of `GameUIInputTests.cpp`: `GameUI.HitTest`, `.Capture`, `.Events`, `.Navigation`, `.InputField`, `.WorldSpace` |
| `gameui:240` | feature | home | The suite `Scripting.UI` (`ScriptUITests.cpp`) |
| `gameui:418` | code | home | `Strata/src/Strata/GameUI/GameUIHitTest.cpp:50-129`: `Build` and `HitTestGrid`, a uniform grid by counting sort, the last drawn first |
| `gameui:419` | code | home | `Strata/src/Strata/GameUI/GameUIHitTest.cpp:208-253`: `MakeRay`, `IntersectCanvas` and `ProjectCanvasPoint`, unprojecting a pixel with reversed-Z, the plane met in its own space |
| `gameui:420` | code | home | `Strata/src/Strata/GameUI/GameUISystem.cpp:254-328`: `UpdatePointer`, gestures, pointer capture, click on release, drag |
| `gameui:422` | code | home | `Strata/src/Strata/GameUI/GameUISystem.cpp:880-931`: `UpdateVisualStates`, fades on unscaled time, records kept only while a state shows (the UI actions' repeat, `UIActionState::Update`, is `input/actions`') |
| `gameui:421` | code | home | `Strata/src/Strata/GameUI/GameUISystem.cpp:809-861`: `Navigate`, Explicit neighbours and the Automatic score in screen pixels |
| `gameui:423` | code | home | `Samples/ThirdPerson/Scripts/MainMenu.cpp:34-137`: the focus on create, Cancel closing panels, one event target for every button, the credits scrolled in their mask on unscaled time |
| `gameui:462` | figure | home | The hit-test grid: rects in the cells they overlap, a query in one cell in reverse draw order |
| `gameui:464` | figure | home | The world-space pointer ray: camera, pixel, ray, canvas plane, the crossing in canvas units; screen canvases first, then crossings by distance |
| `gameui:466` | figure | home | The gesture state machine: None, UI and Game, and when pointer capture is on |
| `gameui:468` | figure | home | The selectable states by priority, and a tint fading over the fade duration |
| `gameui:470` | figure | home | The navigation score: the centers, the along and across parts, along plus two times across |
| `gameui:473` | figure | home | Event dispatch: queued in input order, the listeners' snapshot, the script system's routing to the widget and then its target |
| `gameui:490` | figure | home | One button each in Normal, Hover, Pressed, Focused and Disabled (play mode, a click, focus from a script, Interactable off) |
| `gameui:504` | figure | home | Gamepad navigation: the focus moving through a 3x3 grid, three frames |
| `gameui:528` | rule | home | Code that tests where an element is shown or hit uses `GetVisibleBox`: what a mask hides is not clicked, and tests, `input.click` and the editor's picking agree with the player |
| `gameui:532` | rule | home | Only `GameUISystem` reads the pointer for the UI and sets keyboard capture: one owner of the capture state |
| `gameui:534` | rule | home | Hit-test against the game's input screen in rendered pixels, not the window's logical size: on a Retina display or a fixed Game view resolution a hit would miss what is drawn |
| `gameui:537` | rule | home | For world-space canvases project or intersect the ray, never divide pixels by the scale: perspective has no single scale |
| `gameui:539` | rule | home | The UI runs on unscaled time: pause menus at time scale 0 still fade, repeat and blink |
| `gameui:541` | rule | home | Widget values change with `registry.patch` in the running scene, without undo: play mode is a copy, and a player's input is no edit |
| `gameui:543` | rule | home | Values set from code raise no events: no loops between scripts and widgets |
| `gameui:545` | rule | home | Navigation reads the UI map, not raw keys: players rebind, and the qualified names keep a game's own `Left` apart |
| `gameui:547` | rule | home | The UI system runs before the scripts (a soft order): scripts see this frame's events and a captured pointer |
| `gameui:549` | rule | home | Disabled selectables still block what is under them |
| `gameui:557` | rule | home | Texts are no raycast targets by default and images are: a label must not take a button's click, and a panel must block the game |
| `new:12` | erratum | home | The UI map's default bindings are those of `InputActionSet`: Submit is Enter, keypad Enter, Space or gamepad A; Cancel is Escape or gamepad B; the directions are the arrows, the d-pad and the left stick. The comment at `Strata/src/Strata/Input/UIActions.h:12-13` names only Enter, Escape and the arrows for the keyboard. Evidence: `Strata/src/Strata/Input/InputActionSet.cpp:147-152`; `StrataScriptCore/Include/StrataScript/UI.h:16-18` |
| `gameui:738` | open | home | Settled at the pin: Space is a default binding of Submit (`new:12`) |
| `new:17` | erratum | home | The inventory gives as a mistake "a menu unusable with a gamepad because nothing is focused" (`plan/inventory/gameui.md:369-370`); at the pin, with nothing focused the first direction press or Submit focuses the topmost input canvas's First Selected, else its top-left selectable: the menu works, and that first press only focuses (process.md's table of errata, kind `inventory`). Evidence: `Strata/src/Strata/GameUI/GameUISystem.cpp:526-531`, `:539-542`, `:769-807`; the test "Navigation starts at the topmost input canvas's FirstSelected, else its top-left selectable", `StrataTests/src/GameUI/GameUIInputTests.cpp:881` |
| `gameui:734` | open | home | Settled at the pin: the stream's 18 host functions are the 15 UI ones and `GetUnscaledDeltaTime`, `GetRealTime` and `GetTypedText` (`StrataScriptCore/Include/StrataScript/ScriptABI.h:623-645`); the page says 15 UI host functions |
| `new:11` | not-done | home | The game's clicks on world-space canvases do not check for scene geometry in front (the editor's picks do). Evidence: `Docs/Releases/0.7.0.md:389-390`; `Docs/Releases/0.4.0.md:316-317` |
| `new:13` | rule | home | What went wrong before: `UI::IsActionPressed` kept reporting the last press while no canvas existed; the UI actions now follow the input also without a canvas. Evidence: `Docs/Releases/0.6.0.md:112-115`; `Strata/src/Strata/GameUI/GameUISystem.cpp:185-188`; the regression test "UI actions do not stay pressed while no canvas exists", `StrataTests/src/GameUI/GameUIInputTests.cpp:1057` |
| `gameui:599` | hands-on | home | Exercise: a `UIScrollView` component, its content offset driven by the wheel, clamped by fit content, masked, signaled, with hit tests and tests |
| `gameui:605` | hands-on | home | Exercise: change the weight 2 of `Navigate` to 1 and to 4, run `GameUI.Navigation`, and explain which tests fail |
| `gameui:607` | hands-on | home | Exercise (Release): run `Perf.GameUI.*` and `PerfGPU.GameUI.*`, make every text a raycast target and compare the hit tests' candidate counts |
| `new:18` | hands-on | home | Trace it yourself (D27): breakpoints in `UpdatePointer`, `FindSelectable`, `Click` and `DispatchEvents` while the Third-Person main menu's Play is clicked: the element hit and the walk up to its selectable, the gesture that hides the press from the game, the click on release, and the event dispatched at the end of the update to `MainMenu`'s `OnUIClick`. Evidence: `Strata/src/Strata/GameUI/GameUISystem.cpp:254-343`, `:384-391`, `:1196-1213`; `Samples/ThirdPerson/Scripts/MainMenu.cpp:85-95` |
| `gameui:663-667` | term | home | Raycast target; hit test; uniform grid; half-open rect; gesture |
| `gameui:669-671` | term | home | Selectable; visual state; transition |
| `gameui:673` | term | home | Spatial (automatic) navigation |
| `gameui:680` | term | home | Event target |
| `gameui:185` | feature | use | The UI map `UI/Submit`, `UI/Cancel` and the four directions, with their repeat (its home is `input/actions`) |
| `gameui:191` | feature | link | Editing a focused field (`ui/text`) |
| `gameui:220` | feature | link | `input.click`, which clicks an element where the player sees it (`editor/stepping`) |
| `gameui:214` | feature | use | One `ui.hitTest` line (R44): the editor's command runs this page's hit test, `GameUIHitTester::HitTest`, or `HitTestAll` with `all`, with the ray of `GameUIPointer::MakeRay` (`StrataEditor/src/Editor/EditorUICommands.cpp:414-484`), and reports the element hit and the selectable a click would press; the `ui` commands' home is `make/automated-playtests`, and their handlers get no code home |
| `audio-input:166` | feature | use | The UI actions as input actions of the reserved map |
| `audio-input:391` | code | link | `UIActionState::Update`, the repeat after 0.4 s and every 0.1 s |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The element array, the boxes, root canvases, sort order and clip rects | `ui/layout` | must |
| Rays, planes and where a ray meets a plane | `basics/math-geometry` | must |
| Inverting a matrix | `basics/math-matrices` | must |
| NDC and reversed-Z depth | `gpu/coordinates` | must |
| The dot product and the part of a vector along an axis | `basics/math-vectors` | must |
| The pointer state, pointer capture and keyboard capture | `input/devices-state` | must |
| Input pixels, the render resolution and content scale | `input/mouse-cursor` | must |
| The UI map, its actions and their repeat | `input/actions` | must |
| Scene systems, their order and scene services | `world/systems` | must |
| Script callbacks and how the script system dispatches them | `scripting/script-system` | must |
| Time scale and unscaled time | `core/time` | must |
| Writing a component with `registry.patch` | `world/scene-graph` | must |
| The primary camera of a scene | `world/scene-graph` | helps |
| Hit stamps and layout ids that tell the grids to rebuild | `ui/contract` | helps |
| Editing a focused field | `ui/text` | helps |
| Host functions: `HostCall`, `ResolveContext`, failure values | `scripting/host-api` | helps |
| The SDK's classes over the C table | `scripting/abi-sdk` | helps |
| Binding capture | `input/rebinding` | helps |
| Simulated input in tests | `input/simulated` | helps |
| `Input::SetViewport`: positions relative to the viewport, scaled to the rendered resolution | `input/mouse-cursor` | helps |
| The Game view's resolution | `editor-ui/game-view` | helps |
| The feature test | `engineering/feature-test` | helps |
| Perf tests and their budgets | `engineering/perf-lab` | helps |

## `ui/text` — Text and text fields

**Covers.** The job: give every `UIText` its shaped lines from its rect, and let a player type one line into a field.
Fonts, shaping and the glyph atlas are `gpu/text`'s; drawing the glyphs, the caret and the selection is
`ui/drawing`'s. The problem section is one paragraph that links `gpu/text`: layout needs only a font's metrics, never
its pixels. The map shows `GameUIText.cpp` beside `Renderer/TextLayout.h` and the editing code of `GameUISystem`. The
contract: layout never rasterizes a glyph (it runs headless, in commands and tests), and a field's text element is a
`UIText` that a mask clips. A toy of about 40 lines keeps a one-line field: insert at the caret, delete one character
backwards by its UTF-8 bytes, scroll to keep the caret in view.

The real code comes in two halves. First a text in its rect, on the Third-Person menu's titles and labels: how the rect
sets the shaping options in `GetMeasureOptions` and `GetShapeOptions` (wrap at the rect's width in em, a maximum width
and a box height for Truncate and Ellipsis, a fitted rect measured unwrapped), the default font while the text's font
loads and the reshape when it arrives, and the shape cache per element and layout, so a text is shaped once for
measuring and drawing. Then the field, on the GPU test's field scene: one line, never wrapped or cut; a field needs a
`UISelectable` on its entity, since editing starts when the focused selectable holds the field (the preset adds it and
the mask); `PlaceFieldLine` scrolls it so the caret stays inside; the caret stops; the editing state (caret, anchor,
blink). Editing: the field takes the keyboard while it is edited (keyboard capture), so the UI map's keyboard bindings
go quiet (Space types a space and submits nothing, the field reads its own keys) while a gamepad still edits (its
Submit submits, its Cancel ends editing, its Left and Right move the caret); typed text goes in at the
caret within the character limit counted in code points, control characters are dropped, Backspace, Delete, the arrows,
Home and End repeat like the UI actions, Shift selects, Ctrl+A or Cmd+A selects all, Enter submits, Escape ends editing
but keeps the capture to the end of the frame, the caret blinks every 0.53 s, and every caret move stops on a character
boundary. A click on the field puts the caret at the nearest character, also on a world-space canvas. The page then says
what Strata does not do: localization and right-to-left text, and showing the text an input method is composing. It ends
with the alternatives, the tests (`GameUI.Text`, the `GameUI.InputField` suite), changing it safely, and two exercises
(a typed character traced through the editing code, and word-wise caret moves added). At the end the reader can say how
a rect's size and overflow mode become shaping options, and follow one key press from `Input` to a changed field.

**Leaves out.**

- Fonts, shaping, glyph atlases and signed distance fields → `gpu/text`
- Glyph quads, the selection and caret quads, the glyph table → `ui/drawing`
- The focus model, Submit and navigation → `ui/input`
- Typed text and keyboard capture inside `Input` → `input/devices-state`
- Composed text in the editor's own text fields → `editor-ui/imgui-backends`
- A name field in a game's menu → `make/menus`

**Fit.** `over`: about 4,600 words against M (3,000). Four excerpts (the shaping options, `PlaceFieldLine`, the UTF-8
boundaries, the editing loop), the concept of text input, three figures, three rules, the UI map while a field is
edited, two absences and the internals sections pass M's top of 4,000; by S2 the page takes L, whose range holds the
estimate.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gameui:58` | feature | home | `UITextComponent`: text, font, size in canvas units per em, color, alignments, wrap, overflow, line spacing, outline, raycast target off by default |
| `gameui:115-120` | feature | home | Shaping from metrics without rasterizing; the default font while a font loads, and the reshape; the shape cache; wrapping, maximum width, box height and overflow from the rect; a field's line, never wrapped, scrolled to the caret; caret stops |
| `new:4` | code | home | `Strata/src/Strata/GameUI/GameUIText.cpp:65-89`: `GetMeasureOptions` and `GetShapeOptions`, how the rect's size, wrap and overflow mode become the options of `ShapeText` |
| `gameui:64` | feature | home | `UIInputFieldComponent`: text, text element, placeholder, character limit in code points, caret and selection colors, event target |
| `gameui:90` | feature | home | The field's editing state in `GameUIScene` (caret, anchor, blink), and the caret found from a point |
| `gameui:411` | code | home | `Strata/src/Strata/GameUI/GameUIText.cpp:111-142`: `PlaceFieldLine`, a single line scrolled to keep the caret in view |
| `gameui:372` | concept | home | Text input: caret and selection anchor, byte offsets on character boundaries, typed text per frame without an input method, repeated edit keys, one scrolled line, the placeholder; the mistake of moving the caret by bytes |
| `gameui:191-192` | feature | home | Editing in `GameUISystem` (capture, typed text at the caret, limit, edit keys with repeat, Shift, Ctrl+A or Cmd+A, Enter, Escape, the 0.53 s blink, UTF-8 boundaries), and a click that puts the caret at the nearest character |
| `new:5` | code | home | `Strata/src/Strata/GameUI/GameUISystem.cpp:68-94`: `IsContinuationByte`, `PreviousBoundary` and `NextBoundary`, moving over UTF-8 one character at a time |
| `new:6` | code | home | `Strata/src/Strata/GameUI/GameUISystem.cpp:708-747`: typed text inserted at the caret within the character limit, the field written with `registry.patch`, the caret's blink, Enter and Escape |
| `new:19` | feature | home | The UI map while a field is edited: keyboard capture silences `Input::IsKeyDown`, which the input actions read, so the map's keyboard bindings go quiet (Space types a space and submits nothing; the field reads Enter, Escape, Left, Right, Home and End itself, and the keyboard's Up and Down do nothing), while a gamepad still edits: its Submit submits, its Cancel ends editing, its Left and Right move the caret, and its Up and Down navigate away. The page cites `UpdateNavigation`. Evidence: `Strata/src/Strata/GameUI/GameUISystem.cpp:509-551` (the comments at 516 and 548), `:589-592`, `:740-746`; `Strata/src/Strata/Input/InputActions.cpp:349`, `:390`; `Strata/src/Strata/Input/Input.h:101-104` |
| `gameui:237` | feature | home | The suite `GameUI.Text` (`GameUITextTests.cpp`); `GameUIComponentTests.cpp`'s suites, which round-trip every UI component, in one sentence |
| `gameui:472` | figure | home | The input field model: the text's bytes, caret and anchor, the selection quad, the caret quad, the scroll window over the line |
| `gameui:487` | figure | home | Text alignments, wrapping, Truncate against Ellipsis, an outline over a busy background |
| `gameui:493` | figure | home | An input field empty with its placeholder, while typing with a selection and the caret, and a long text scrolled (the scene of `GPUGameUITests.cpp`'s field test; no sample has an input field) |
| `gameui:522` | rule | home | Layout never rasterizes glyphs: it runs headless and must not depend on the atlas or its budget |
| `gameui:554` | rule | home | Keep the field's text element a `UIText` and give the field a `UIMask`: the text element draws text, caret and selection, and a scrolled line would spill |
| `new:20` | rule | home | Give the field a `UISelectable` on its own entity: only selectables take the focus, and editing starts when the focused selectable holds a `UIInputField`, so a field built by hand without one never takes the keyboard; the Input Field preset adds the selectable and the mask. Evidence: `Strata/src/Strata/GameUI/GameUIComponents.h:255`; `Strata/src/Strata/GameUI/GameUISystem.cpp:493-507`; `StrataEditor/src/Editor/GameUIPresets.cpp:179-200` |
| `new:21` | hands-on | home | Exercises (D27): Trace it yourself: breakpoints in `UpdateEditing` while "é" is typed into a playground field made with Hierarchy > + > UI > Input Field and Backspace is pressed show the two bytes inserted at the caret, `PreviousBoundary` stepping back over both, and the patch that signals the change; Hard, extend (done): word-wise caret moves on Ctrl+Left and Ctrl+Right that stop on character boundaries, with Shift selecting, and tests in the `GameUI.InputField` suite. Evidence: `Strata/src/Strata/GameUI/GameUISystem.cpp:630-747`, `:68-94`, `:613-628` (`MoveCaret` moves one character or to an end, never by words); `StrataTests/src/GameUI/GameUIInputTests.cpp:1132` |
| `gameui:648` | term | home | Ellipsis, truncate and overflow |
| `gameui:677`, `gameui:679` | term | home | Caret and selection anchor; placeholder |
| `new:7` | not-done | home | No localization and no right-to-left text. Evidence: `Docs/Releases/0.7.0.md:413-416` lists localization as not in the release; `Docs/Roadmap.md:1713` ("Localization with string tables and font fallback chains"); `git grep -niE "locali[sz]\|right-to-left\|\brtl\b\|bidi" 822a7a46 -- Strata/src` finds nothing |
| `new:8` | not-done | home | Game UI shows no text that an input method is still composing, and no candidate window; committed text arrives. Evidence: `Strata/src/Strata/Input/Input.h:148` (characters arrive with input methods applied); no "preedit" in `Strata/vendor/glfw/include/GLFW/glfw3.h`; the editor's fields take composed text, `Strata/src/Strata/ImGui/ImGuiPlatform.h:25-26` |
| `gameui:743` | open | home | Settled at the pin: games receive committed text; composition is not shown (`new:8`) |
| `gameui:303` | concept | use | Shaping against rasterizing, from `gpu/text`: the page uses that layout needs metrics only |
| `gameui:135` | feature | link | The glyph quads, and the selection quad behind them and the caret quad after them (`ui/drawing`) |
| `gameui:195` | feature | use | The typed text of the input frame and its 1,024-byte limit (its home is `input/devices-state`) |
| `gameui:236` | feature | use | The `GameUI.InputField` suite of `GameUIInputTests.cpp` (its home is `ui/input`) |
| `render-core:235` | feature | use | `ShapeText` and `MeasureCaretStops` of `Renderer/TextLayout.h` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Shaping: glyphs, advances, line breaks and the options of `ShapeText` | `gpu/text` | must |
| UTF-8, code points and multi-byte characters | `basics/bytes` | must |
| Typed text per input frame, and keyboard capture | `input/devices-state` | must |
| The rect, fit content and masks | `ui/layout` | must |
| Focus: the one widget that keys act on | `ui/what-game-ui-does` | must |
| Writing a component with `registry.patch` | `world/scene-graph` | must |
| The repeat timing of the UI actions | `input/actions` | helps |
| Font assets that load later, at a priority | `assets/residency` | helps |
| How Submit and focus changes become events | `ui/input` | helps |
| How the glyphs, caret and selection are drawn | `ui/drawing` | helps |
| Input methods in the editor's text fields | `editor-ui/imgui-backends` | helps |

## `ui/drawing` — Drawing the UI

**Covers.** The job: turn the laid-out elements into 64-byte quads and draw every canvas of a scene in each view, the
screen-space ones over the finished image and the world-space ones in the scene, in about one draw per canvas. The page
carries the full section on the problem and how engines solve it: a draw per element; batched quads; clipping by
scissor rectangles, by stencil masks or in the shader; buffers kept on the GPU against buffers written again every
frame. The map is the data flow from component to pixel: components, `GameUIScene`'s elements and shaped texts, the
quad array in slots, the renderer's buffers (quads, texture slots, glyph table, clip rects, transforms), the shaders.
The contract, each rule with its reason: the renderer never includes GameUI and reaches it through the overlay
registry; quads name UI texture and font indices, never bindless slots or atlas places; masks clip in the shader,
never by splitting draws; `UIQuad` and the shader's structs change together; the pass asks for each texture and font
once per frame. A toy of about 50 lines turns a list of rects into a quad array and splits it into runs.

The real code, on the Third-Person main menu, in the order data flows. The quad: `UIQuad` and `UIDrawParameters`, their
flag bits and the `static_assert` of their size. Quads per element in slots with room to spare (a text gets a quarter
more, a field two for its caret and selection), rewritten in place or repacked when a slot overflows, with a journal of
changed ranges. Image quads: tint, image swap, solid color, preserve aspect, filled images, the nine-slice cut whose
borders shrink together; glyph quads with the pen on the baseline; every quad carrying its clip. The indirection that
keeps quads still when mip streaming moves a slot or an atlas packs a glyph, and its limit: a scene's UI gives every
distinct font an index that is never freed, so once 256 fonts hold them (the default among them), texts in any further
font draw nothing, without a log. The pass:
registered through `SceneOverlayRegistry`; `Prepare`, `DrawWorld` and `Draw`; screen canvases hidden where the view
hides screen text; a scene with no camera that shows its UI over black; uploads of changed ranges only; texture slots
requested at High priority, white while loading, reported to mip streaming; glyphs from the renderer's `FontAtlasCache`;
runs of up to four atlases; the pipelines (display-value blending, no culling, the world pipeline's reversed-Z depth
test without writes and its TAA depth bias); binding sets and buffers released when unused; six vertices per quad and no
vertex buffer; the `GPU.UI` and `Render.UI` stages; `SceneOverlayStats`, what the pass reports each frame, which the GPU
tests read and `viewport.capture` returns and waits on. The shaders: the vertex shader pulls its quad by instance index,
snaps edges and baselines to whole pixels and culls quads outside their clip; the fragment shader shades a rounded rect
by its signed distance with a border, decodes sRGB textures back to display values, shades SDF glyphs with an outline,
fades masks by their softness, and keeps its one discard last so derivatives stay defined. World-space canvases: the
canvas-to-world matrix, camera-relative transforms subtracted in double, antialiasing by `fwidth`, mip streaming from
the pixels a unit projects to; they are unlit and drawn after post-processing, and placed by the last fixed step's pose,
not the drawn one (in one sentence with a link to `world/interpolation`). The page ends with the alternatives, the GPU
tests of `GPU.GameUI`, changing it safely, and three exercises (an upload traced, a radial fill, an outline measured in
pixels). At the end the reader can follow one button from its components to its pixels, and say which buffer an edit
uploads.

**Leaves out.**

- The overlay registry in general and debug drawing → `gpu/debug-drawing`
- Bindless, push constants and pipelines → `gpu/binding`
- Glyph atlases, distance fields and font validation → `gpu/text`
- Camera-relative rendering in general → `draw/mirrors-camera-relative`
- How textures stream their mips → `draw/mip-streaming`
- The canvas mode (its zoom and pan, and that it edits screen-space canvases only) and the viewport's Game UI chip →
  `editor-ui/scene-view`
- `SceneScreenView`, the frame's option that zooms and pans the screen canvases → `gpu/debug-drawing`
- The tone mapping the screen UI draws over → `image/tone-mapping`

**Fit.** `fits`: about 9,300 words against XL (8,000). Ten excerpts, five concepts, nine figures and six rules make it
the part's fullest page, and the pass and the shaders take the most words; at 700 words below XL's top, a further item
would need the split into "Drawing the UI: quads, batches and the pass" and "The UI's shaders and world-space canvases".

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gameui:326` | concept | home | Batching for the GPU: a flat array of quads in draw order, one buffer, instancing without a vertex buffer, one draw per canvas, indirection tables, slots and a journal; the mistakes of a draw per element and of GPU slots baked into cached data |
| `gameui:310` | concept | home | Images: nine-slice, fill, preserve aspect, rounded rects and borders by a signed distance (no texture needed); the mistake of slice borders in canvas units |
| `gameui:332` | concept | home | Clipping without breaking batches: scissor, stencil and shader clipping; quads that name a clip rect; soft edges; the one late discard |
| `gameui:337` | concept | home | Pixel snapping and blending in display values over the tone-mapped image; the mistake of blending UI in linear HDR |
| `gameui:346` | concept | home | World-space UI: a canvas as a plane, depth-tested without writes, camera-relative in double, `fwidth` antialiasing, mip streaming from the projected unit, TAA depth bias, unlit |
| `gameui:57` | feature | home | `UIImageComponent`: texture or solid color, simple, sliced or filled, UV rect, slice borders and scale, fill, preserve aspect, corner radius, border, raycast target on by default |
| `gameui:55` | feature | home | `UICanvasRenderMode`: screen space and world space |
| `gameui:85` | feature | home | What is visible: active in the hierarchy, a toggle's checkmark only while it is on, a placeholder only while the field is empty |
| `gameui:87` | feature | home | The world-space canvas's plane matrix, `GetCanvasWorldMatrix` |
| `gameui:93` | feature | home | Root and world canvas counts cached per hierarchy version, so hidden canvases are counted, not laid out |
| `gameui:126-136` | feature | home | `UIQuad`, `UIClipRect` and `UIDrawParameters`; slots with headroom; the journal; repacks; indirection to UI texture and font indices; use counts; image quads; glyph quads with the selection and caret quads; the clip index on every quad |
| `new:24` | feature | home | The limit of the font indices, said with the indirection tables: a scene's UI gives every distinct font it uses an index that is never freed (index 0 is the default font), and `c_MaxUIFonts` is 256, so once the default and 255 others hold them, texts in any further font draw nothing, without a log. Evidence: `Strata/src/Strata/GameUI/GameUIQuads.cpp:58-71`, `:467`; `Strata/src/Strata/GameUI/GameUIScene.cpp:145-147`; `Strata/src/Strata/GameUI/GameUIRenderData.h:18-19`; no line of `Strata/src/Strata/GameUI` erases from `m_Fonts` |
| `gameui:142-158` | feature | home | The pass: its registration, `Prepare`, `DrawWorld`, `Draw` and `HasScreenContent`; screen canvases and `DrawScreenSpaceText`; the UI over black; uploads; clips; transforms; textures; glyphs; runs; pipelines; binding sets; the instanced draw; the stages; both shaders; the layout shared with C++ |
| `new:22` | feature | home | `SceneOverlayStats`, what the UI pass reports each frame in `SceneRendererStats::Overlays`, beside `GameUISceneStats` of `ui/contract`: root canvases drawn and hidden, elements, quads (empty slots included), draw calls, glyphs waiting for the raster budget, fonts and textures still loading, bytes uploaded; the GPU tests read it to show one draw per canvas and an idle frame that uploads nothing, `viewport.capture` returns part of it as `ui` and waits while UI glyphs are pending, and project thumbnails wait for them too. Evidence: `Strata/src/Strata/Renderer/SceneOverlay.h:41-54`; `Strata/src/Strata/Renderer/SceneRenderer.h:619`; `Strata/src/Strata/GameUI/GameUIRenderer.cpp:200`, `:243-252`; `StrataEditor/src/Editor/EditorViewportCommands.cpp:801`, `:808`, `:978-979`; `StrataEditor/src/Editor/ProjectThumbnail.cpp:169`; `StrataTests/src/Renderer/GPUGameUITests.cpp:301-313`, `:1080-1083` |
| `gameui:160` | feature | home | The shader entries registered in `Strata/CMakeLists.txt` |
| `gameui:238` | feature | home | The suite `GPU.GameUI`: pixels, snapping, colors, masks, the world canvas, 100 km from the origin, stable under TAA, the screen view, mip streaming, resource release |
| `gameui:407` | code | home | `Strata/src/Strata/GameUI/GameUIRenderData.h:28-78`: `UIQuad`, `UIClipRect` and `UIDrawParameters`, the flag bits, `static_assert(sizeof(UIQuad) == 64)` |
| `gameui:409` | code | home | `Strata/src/Strata/GameUI/GameUIQuads.cpp:192-267`: `BuildQuads`, slots rewritten in place, a repack when one outgrows its room, the journal reset |
| `gameui:408` | code | home | `Strata/src/Strata/GameUI/GameUIQuads.cpp:321-357`: the nine-slice cut, its UVs, borders that shrink together |
| `gameui:410` | code | home | `Strata/src/Strata/GameUI/GameUIQuads.cpp:467-484`: shaped glyphs become quads, the pen on the baseline kept in `UV.xy`, the outline clamped to 0.1 em |
| `gameui:415` | code | home | `Strata/src/Strata/GameUI/GameUIRenderer.cpp:259-362`: `UploadQuads`, only changed ranges, merged, the whole array as fallback |
| `gameui:416` | code | home | `Strata/src/Strata/GameUI/GameUIRenderer.cpp:611-689`: `BuildRuns`, the limit of four atlases and runs split beyond it |
| `gameui:417` | code | home | `Strata/src/Strata/GameUI/GameUIRenderer.cpp:364-394`: `UploadTransforms`, world canvases relative to the camera, the subtraction in double |
| `gameui:412` | code | home | `Strata/shaders/GameUI/UIQuad.vert.slang:41-143`: the vertex shader pulls its quad by instance index, snaps to pixels, culls by clip, places world canvases |
| `gameui:413` | code | home | `Strata/shaders/GameUI/UIQuad.frag.slang:76-106`: `ShadeImage`, the rounded rect's signed distance, the border band, the sRGB decode, `fwidth` for world canvases |
| `gameui:414` | code | home | `Strata/shaders/GameUI/UIQuad.frag.slang:108-120`: `st_Main`, why the clip multiplies and the one discard comes last; with `ShadeGlyph` (62-73), the glyph's fill and outline |
| `gameui:453` | figure | home | Data flow from component to pixel (the page's map) |
| `gameui:455` | figure | home | The memory layout of `UIQuad` (64 bytes, the kind and font bits), the glyph table and the texture slot entries |
| `gameui:458` | figure | home | Indirection: quad, UI texture index, slot table, bindless array; glyph index, the font's glyph table, atlas page and texels |
| `gameui:460` | figure | home | A canvas's quads split into runs by the four-atlas limit |
| `gameui:461` | figure | home | The rounded rect's distance field: radius, border band and the one-pixel coverage ramp |
| `gameui:485` | figure | home | Images: solid, rounded with a border, a nine-sliced panel, a health bar filled to 0.3, preserve aspect (the scene of `GPUGameUITests.cpp`'s image test) |
| `gameui:488` | figure | home | Pixel snapping off and on at a fractional scale, as a zoomed crop |
| `gameui:495` | figure | home | The Third-Person credits scrolling in their mask, softness 0 against 20 |
| `gameui:497` | figure | home | A world-space canvas seen in perspective, partly behind nearer geometry, and the same canvas in screen space; a recipe's project is a sample, a template, the look-dev project or a lab (pipelines.md §5.2), so the recipe builds the canvas on a copy of a sample with `setup` steps (`ui.create` makes a canvas, `component.set` gives it the `RenderMode` WorldSpace, `Strata/src/Strata/GameUI/GameUIComponents.cpp:232`), after the GPU test's scene (a 4 x 2 m sign, a HUD square, geometry in front) or the feature scene's world-space canvas (`gameui:730`) |
| `gameui:518` | rule | home | The renderer never includes GameUI: the pass registers through `SceneOverlayRegistry`, so the layer rule holds and builds without the module work |
| `gameui:524` | rule | home | Quads name UI texture and font indices, never slots or atlas places: mip streaming and atlas packing would otherwise rebuild them |
| `gameui:526` | rule | home | Masks clip in the shader, never by splitting draws: a canvas stays one draw |
| `gameui:530` | rule | home | `UIQuad` and the shader's structs change together: the `static_assert` guards only the size |
| `new:10` | rule | home | The pass requests each distinct UI texture and font once per frame, never per element, at High priority. Evidence: `AGENTS.md:331-332`; `Docs/DeveloperGuide.md:2665-2668` |
| `gameui:561` | rule | home | The known limits, stated and not exceeded: world canvases are unlit and drawn after post-processing; the game's clicks on them ignore geometry in front (`ui/input`) |
| `new:9` | not-done | home | No lit world-space UI: world canvases are drawn unlit, without shadows, after post-processing. Evidence: `Docs/Releases/0.7.0.md:389-390` |
| `new:23` | not-done | link | No drawn (interpolated) poses for world-space game UI, an entry of "What Strata does not do" homed on `world/interpolation`: a canvas is placed by the scene's world transform, the last fixed step's pose, so a name tag on an interpolated body moves in fixed steps against it, and hits use the same matrix; one sentence in the world-space section, with the link. Evidence: `Docs/Roadmap.md:1698-1699` (the entry's evidence, book.md); `Strata/src/Strata/GameUI/GameUIScene.cpp:1101-1113` (`m_Scene->GetWorldTransform`); `Strata/src/Strata/GameUI/GameUIHitTest.cpp:38`; `Strata/src/Strata/GameUI/GameUISystem.cpp:380` |
| `gameui:730` | open | home | Settled at the pin: no sample has a world-space canvas (the Showcase's `Outpost.stscene` holds two screen-space canvases), but the tests have two: `git grep -lE '"RenderMode": *"WorldSpace"' 822a7a46 -- Samples StrataTests` finds `StrataTests/FeatureTest/Assets/Scenes/Feature.stscene` (line 4825, 0.005 m a unit), and the GPU test at `StrataTests/src/Renderer/GPUGameUITests.cpp:569-696` builds a 4 x 2 m sign and a HUD square, with a cube in front of the sign at 669-676; the recipe of figure `gameui:497` rebuilds one of them on a copy of a sample |
| `new:25` | hands-on | home | Trace it yourself (D27): a breakpoint in `UploadQuads` while the pointer moves onto the Third-Person main menu's Play (its tint fades) shows the journal's few changed ranges, merged, and the bytes that `SceneOverlayStats::UploadedBytes` then reports; once the fade has ended, a frame uploads nothing. Evidence: `Strata/src/Strata/GameUI/GameUIRenderer.cpp:259-362`; `Strata/src/Strata/Renderer/SceneOverlay.h:53`; `StrataTests/src/Renderer/GPUGameUITests.cpp:304-313` |
| `gameui:595` | hands-on | home | Exercise: a fill direction `Radial360`, a quad flag and a shader path, `UIQuad` kept at 64 bytes, with enum, inactive reason, tests and feature test |
| `gameui:610` | hands-on | home | Exercise: argue why a glyph outline is measured in em and limited to 0.1 em by the distance field's spread |
| `gameui:649-652` | term | home | Nine-slice; filled image; quad; instancing and vertex pulling |
| `gameui:654` | term | home | Draw run (the UI's batch) |
| `gameui:657-659` | term | home | Softness; pixel snapping; display (sRGB) values |
| `gameui:342` | concept | use | Overlay passes and the dependency inversion behind them, from `gpu/debug-drawing` |
| `gameui:303` | concept | use | Glyphs drawn from the renderer's distance-field atlas, from `gpu/text` |
| `gameui:159` | feature | link | The screen view that zooms and pans the canvases in the canvas mode (`editor-ui/scene-view`) |
| `render-core:223` | feature | use | `ISceneOverlayPass`, `SceneOverlayRegistry` and `SceneOverlayFrame` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Overlay passes and `SceneOverlayRegistry` | `gpu/debug-drawing` | must |
| Structured buffers, push constants, bindless textures and pipelines | `gpu/binding` | must |
| Instanced draws | `draw/batching` | must |
| Vertex and fragment shaders in Slang | `gpu/shaders` | must |
| Distance-field glyphs from the `FontAtlasCache` | `gpu/text` | must |
| Camera-relative positions, subtracted in double | `draw/mirrors-camera-relative` | must |
| Clip space, NDC and reversed-Z depth | `gpu/coordinates` | must |
| Where overlays draw in the frame | `gpu/frame-tour` | must |
| sRGB values and the transfer function | `basics/color` | must |
| The element array, the boxes and the clip rects | `ui/layout` | must |
| Dirty marks and the change journal | `ui/contract` | must |
| Shaped texts, caret stops, the field's state | `ui/text` | must |
| Pixel derivatives and why a discard breaks them | `light/brdf` | helps |
| Tone mapping, which the screen UI draws over | `image/tone-mapping` | helps |
| The TAA jitter | `image/taa` | helps |
| Mip streaming's reports of drawn textures | `draw/mip-streaming` | helps |
| Asset requests at a priority | `assets/residency` | helps |
| Releasing GPU resources | `gpu/resources-lifetimes` | helps |
| GPU stages and timestamps | `gpu/readback-timing` | helps |
| A GPU test that reads pixels back | `gpu/first-triangle` | helps |

## Passed on

| Item | Type | To | Why |
| --- | --- | --- | --- |
| `gameui:159` | feature | `editor-ui/scene-view` | The screen view exists for the canvas mode's zoom and pan; the canvas mode is taught there |
| `gameui:185` | feature | `input/actions` | `book.md` makes `input/actions` the home of UI actions and menu key repeat (`UIActions.h`); `ui/input` uses them |
| `gameui:195` | feature | `input/devices-state` | Typed text is `Input`'s (`GetTypedText`, `GetUncapturedTypedText`, the 1,024-byte limit); `book.md` puts typed text with input ownership there; repeats `audio-input:123` |
| `gameui:207` | feature | `make/gameplay-math` | The SDK's `Motion` helpers (`SmoothDamp`) are a game maker's smoothing tools, whose use home is there |
| `gameui:208` | feature | `make/timers-events` | `Time::GetUnscaledDeltaTime` is one of the `Time` clocks for timers and pauses taught there |
| `gameui:214` | feature | `make/automated-playtests` | `book.md` makes that page the home of testing game UI through `ui.create`, `ui.layout` and `ui.hitTest` |
| `gameui:215` | feature | `make/hud` | The presets of the Hierarchy's + > UI menu are how a game maker makes canvases, panels and widgets |
| `gameui:216-217` | feature | `editor-ui/inspectors` | The anchor presets, margin rows and the UI Rect drawer are the Inspector's custom drawer (`editor-ui:182`) |
| `gameui:218-219` | feature | `editor-ui/scene-view` | The Game UI chip and the 2D canvas mode are parts of the Scene view (`editor-ui:155`, `editor-ui:198`) |
| `gameui:220` | feature | `editor/stepping` | `book.md` makes that page the home of `input.click`; its UI branch projects world canvases and fails when the element is covered |
| `gameui:243` | feature | `editor-ui/scene-view` | The editor's UI tests (`EditorGameUITests`, `EditorUICommandTests`, `GPUCanvasEditTests`) test the canvas mode, the chip and UI picking taught there |
| `gameui:303` | concept | `gpu/text` | Shaping against rasterizing and distance-field fonts have their home there (`book.md`); repeats `render-core:425`; `ui/text` and `ui/drawing` use it |
| `gameui:342` | concept | `gpu/debug-drawing` | Overlay passes have their home there (`book.md`); the UI's own rule is `gameui:518` on `ui/drawing` |
| `gameui:381` | concept | `make/menus` | A pause menu animated on unscaled time is a game maker's task; the engine's rule is `gameui:539` on `ui/input` |
| `gameui:384` | concept | `make/automated-playtests` | Testing UI without eyes through commands has its home there (`book.md`) |
| `gameui:425` | code | `make/menus` | Short excerpts "for the game-developer track": the Manual's `MainMenu`, `UI.h`'s `UIElement`, the callbacks of `Script.h` |
| `gameui:471` | figure | `input/actions` | The repeat timeline of the UI actions belongs with menu key repeat |
| `gameui:480` | figure | `make/hud` | Anchors at two aspect ratios, made with `ui.create`, show a game maker's HUD |
| `gameui:482` | figure | `editor-ui/inspectors` | The UI Rect drawer is the Inspector's |
| `gameui:483` | figure | `editor-ui/scene-view` | The canvas mode is the Scene view's |
| `gameui:492` | figure | `make/menus` | The toggle group and the slider belong to the settings screen built there |
| `gameui:500` | figure | `make/menus` | The main menu scene without a camera is built there; `gameui:733` says the picture needs a scene of its own |
| `gameui:502` | figure | `editor-ui/scene-view` | The Game UI chip is the Scene view's |
| `gameui:514` | rule | `world/scene-graph` | The construct signal covers values written right after `AddComponent` for every component; homed beside `scene-ecs:507` (R29, duplicates.md:68); `ui/contract` says the UI components follow it and links |
| `gameui:571` | hands-on | `make/menus` | The first menu with a `MainMenu` script and a scene without a camera |
| `gameui:574` | hands-on | `make/hud` | A HUD checked at three screens |
| `gameui:577` | hands-on | `make/menus` | A pause menu at time scale 0 |
| `gameui:580` | hands-on | `make/menus` | A settings screen with a toggle group, sliders and a name field |
| `gameui:582` | hands-on | `make/menus` | Scrolling credits in a mask |
| `gameui:584` | hands-on | `make/menus` | A world-space sign with a button clicked through the game camera |
| `gameui:586` | hands-on | `make/automated-playtests` | A menu built with `ui.create` and checked with `ui.hitTest` and `input.click` |
| `gameui:624` | term | `core/windows-events` | Content scale is the window's factor from the OS, taught from zero there, one entry with `editor-ui:721` (R31, D33); `ui/layout` says it in one sentence and links |
| `gameui:638` | term | `nowhere` | Repeats `scene-ecs:631` (dirty flag) |
| `gameui:640` | term | `nowhere` | Repeats `scene-ecs:622` (EnTT's signals) |
| `gameui:641` | term | `nowhere` | Repeats `scene-ecs:623` (patch and `MarkModified`) |
| `gameui:644` | term | `nowhere` | Repeats `render-core:766` (text shaping) |
| `gameui:645` | term | `gpu/text` | Glyph, advance, kerning, baseline and em are font terms; `render-core:762` and `render-core:765` hold glyph and kerning only |
| `gameui:646` | term | `nowhere` | Repeats `render-core:767` (signed distance field) |
| `gameui:647` | term | `nowhere` | Repeats `render-core:768` (glyph atlas) |
| `gameui:653` | term | `nowhere` | Repeats `render-core:712` (bindless) |
| `gameui:655` | term | `nowhere` | Repeats `render-core:707` (push constants) |
| `gameui:660` | term | `gpu/debug-drawing` | The overlay pass and its registry have their home there |
| `gameui:661` | term | `nowhere` | Repeats `render-core:730` (reversed-Z) |
| `gameui:662` | term | `nowhere` | Repeats `render-core:741` (camera-relative rendering) |
| `gameui:668` | term | `nowhere` | Repeats `audio-input:691` (pointer and keyboard capture) |
| `gameui:674` | term | `nowhere` | Repeats `audio-input:684` (the UI map) |
| `gameui:675` | term | `nowhere` | Repeats `audio-input:663` (key repeat) |
| `gameui:676` | term | `nowhere` | Repeats `audio-input:677` (hysteresis) |
| `gameui:678` | term | `basics/bytes` | Code points and UTF-8 continuation bytes belong to the primer on text encodings; `audio-input:667` holds code points only |
| `gameui:681` | term | `nowhere` | Repeats `scene-ecs:645` (scene service) |
| `gameui:682` | term | `nowhere` | Repeats `scene-ecs:641` (time scale and unscaled time) |
| `gameui:683` | term | `nowhere` | Repeats `scene-ecs:635` (scene system) |
| `gameui:684` | term | `editor-ui/scene-view` | The canvas mode is taught there |
| `gameui:685` | term | `gpu/debug-drawing` | `SceneScreenView`, the frame's option that the canvas mode drives, is taught there beside `render-core:223`; the glossary entry follows the teaching page (critic-gameui-18) |
| `gameui:723` | open | `nowhere` | A note about files the survey did not read in full |
| `gameui:733` | open | `make/menus` | Settled at the pin: `Samples/ThirdPerson/Assets/Scenes/MainMenu.stscene` has a primary camera (its first entity), so "the UI over black" needs a scene made for the picture |
| `gameui:736` | open | `input/how-input-works` | Touch input: `book.md`'s "What Strata does not do" puts it there |
| `gameui:737` | open | `input/actions` | Settled at the pin: the stick's thresholds are those of every button action (on from 0.5, off below 0.35, `Strata/src/Strata/Input/InputActions.h:43-52`), not values of the UI map |
| `gameui:740` | open | `nowhere` | A note about history the survey did not trace; `ui/what-game-ui-does` dates the module by its `new:3` |

## Not taken

none

## Questions for the planner

none
