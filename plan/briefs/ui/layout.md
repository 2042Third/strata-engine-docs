# Brief: `ui/layout`

| Field | Value |
| --- | --- |
| Title | Rects, anchors and layout |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | - |
| From | gameui ch. 4 (the coordinate space, the scale formula, rect math, measure and arrange per axis, groups, grids, fit content, slider parts, clip rects) |
| Unit | `plan/allocation/ui.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `anchor` | Anchor | - |
| `canvas-unit` | Canvas unit | - |
| `clip-rect` | Clip rect | - |
| `depth-first-order` | Depth-first order | - |
| `fit-content` | Fit content | - |
| `layout-group` | Layout group | - |
| `margin` | Margin | - |
| `measure` | Measure | - |
| `pivot-ui` | Pivot (ui) | - |
| `preferred-size` | Preferred size | - |
| `reference-resolution` | Reference resolution | - |
| `root-canvas` | Root canvas | - |
| `safe-area` | Safe area | - |
| `scale-s` | Scale (s) | - |
| `sort-order` | Sort order | - |
| `subtree-range` | Subtree range | - |
