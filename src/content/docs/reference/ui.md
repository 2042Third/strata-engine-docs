---
id: reference/ui
title: "Game UI reference"
description: "The conventions, enums, events, limits and statistics of Strata's game UI, in tables for looking things up."
kind: reference
size: M
tracks: []
needs: [ui/layout]
status: final
---

This page holds the facts of the game user interface (UI) that the catalogue pages do not: the conventions of every property, the values of each enum, the events, the limits and the statistics. A row of a table is one fact; the first column names it and the others say what it means. Each table has a short introduction that names the page teaching its subject.

The catalogue pages hold the rest. The eleven UI components are in [Components](../reference/components.md): the canvas and the rect, the image, the text and the mask, the selectable with its button, toggle and slider, the layout and the input field. `Text` is the text drawn in the world, beside them. The `ui.*` commands are in [Commands](../reference/commands.md), and the classes `UIElement` and `UI` and the `UIAction` list of the software development kit (SDK) are in [the script reference](../reference/script-api.md). Strata has no drop-down, scroll view, tab bar or progress widget of its own, and [what a game UI does](../ui/what-game-ui-does.md) says how to build them from the parts it has.

## Conventions of every property

A canvas is the root of one screen of UI, and an element is an entity with a `UIRect` below a canvas. A **canvas unit** is the length that all UI numbers use; a canvas turns canvas units into pixels with its scale. [Rects, anchors and layout](../ui/layout.md) teaches the scale, the anchors and the pivot with worked numbers. The table lists the rules that every UI component follows, as the comment at the top of `GameUIComponents.h` and the comments of the fields state them.

| Subject | Convention |
| --- | --- |
| Length | Canvas units, for positions, sizes, padding, spacing, corner radius and border width |
| Axes | +Y points down, and (0, 0) is the top left, like `Text` `ScreenAnchor` and the mouse position |
| Anchors and pivot | `AnchorMin`, `AnchorMax` and `Pivot` are fractions from 0 to 1 of the parent rect, where (0, 0) is its top left and (1, 1) its bottom right |
| Position and size | `Position` is the pivot's offset from the anchor point; `Size` is added to the span between the anchors |
| Colors | Display (sRGB) colors as four values from 0 to 1 (red, green, blue, alpha), like the color of `Text`; scripts read and write them the same way |
| Edge groups | `SafeAreaPadding`, `Padding` and `SliceBorders` list left, top, right, bottom; `UVRect` lists u0, v0, u1, v1 |
| Text size | `FontSize` is canvas units per em; `OutlineWidth` is in em; `LineSpacing` multiplies the font's line height |
| Time | `FadeDuration` is in seconds of unscaled time, so menus react while the game is paused |
| Element | A UI component draws only with a `UIRect` and a :term[root canvas]{id=root-canvas} that is the entity itself or one of its ancestors |
| Nested canvas | A canvas below another canvas is an element of the outer one, and its scale settings are ignored |
| World canvas | `ReferenceResolution` canvas units wide and high, each `WorldUnitsPerUnit` world units (default 0.01, so 100 units are a metre), in the plane of the entity's x and y axes, facing +Z |
| Changes | Code that writes a field directly signals it with `Entity::MarkModified` or `registry.patch`; the [UI contract](../ui/contract.md) explains why |

A worked reading: a canvas with `ScaleWithScreen`, a `ReferenceResolution` of 1920 by 1080 and a screen of 1280 by 720 has a scale of 2/3 pixel per canvas unit. A rect 300 units wide is then 200 pixels wide. On a screen of 2560 by 1080, `MatchWidthOrHeight` of 0 gives a scale of 4/3, and 1 gives a scale of 1.

## The enums

An **enum** is a type whose value is one of a short list of names; a component stores the name as a small number and the inspector shows it as a choice. The table lists all eleven enums of `GameUIComponents.h` with every value. The meaning comes from the source's own comment where one exists; for a value without a comment, the text says how the code uses it. The first value of each enum is the default of the property that uses it, except four: a canvas starts with `ScaleWithScreen`, a text with `Middle`, a selectable with `ColorTint` and a layout with `Vertical`.

| Enum | Value | Meaning |
| --- | --- | --- |
| `UICanvasScaleMode` | `ConstantPixelSize` | One canvas unit is `ScaleFactor` pixels |
| `UICanvasScaleMode` | `ScaleWithScreen` | The canvas keeps the proportions of `ReferenceResolution` on every screen; `MatchWidthOrHeight` of 0 scales with the width, 1 with the height |
| `UICanvasScaleMode` | `ConstantPhysicalSize` | One canvas unit is `ScaleFactor` pixels at 96 dots per inch (DPI): the screen's content scale times `ScaleFactor` |
| `UICanvasRenderMode` | `ScreenSpace` | Over the scene, laid out for the screen by the scale mode |
| `UICanvasRenderMode` | `WorldSpace` | A plane in the scene at the entity's transform, such as a sign or a name tag |
| `UIFitContent` | `None` | The rect keeps its own size |
| `UIFitContent` | `Width` | The rect takes its content's width: its text, or its layout's children |
| `UIFitContent` | `Height` | The rect takes its content's height |
| `UIFitContent` | `Both` | The rect takes its content's width and height |
| `UIImageType` | `Simple` | The texture fills the rect, or keeps its aspect ratio when `PreserveAspect` is on |
| `UIImageType` | `Sliced` | Nine-slice: the borders keep their size while the edges and the center stretch |
| `UIImageType` | `Filled` | Cut to `FillAmount` along `FillDirection`, as in a health bar |
| `UIFillDirection` | `LeftToRight` | The filled part grows from the left edge |
| `UIFillDirection` | `RightToLeft` | The filled part grows from the right edge |
| `UIFillDirection` | `TopToBottom` | The filled part grows from the top edge |
| `UIFillDirection` | `BottomToTop` | The filled part grows from the bottom edge |
| `UITextVerticalAlignment` | `Top` | The text block touches the top of the rect |
| `UITextVerticalAlignment` | `Middle` | The text block is centered in the rect |
| `UITextVerticalAlignment` | `Bottom` | The text block touches the bottom of the rect |
| `UITextOverflow` | `Overflow` | Lines beyond the rect's height are drawn outside it |
| `UITextOverflow` | `Truncate` | Lines that do not fit are omitted |
| `UITextOverflow` | `Ellipsis` | Like `Truncate`, with "..." ending the last line shown |
| `UISelectableTransition` | `None` | The selectable shows no change of state |
| `UISelectableTransition` | `ColorTint` | The target image's color is multiplied by the state's color, fading over `FadeDuration` |
| `UISelectableTransition` | `ImageSwap` | The target image shows the state's texture, and its own texture in the normal state |
| `UINavigation` | `Automatic` | The nearest selectable in the direction |
| `UINavigation` | `Explicit` | The entities named by `NavigateUp`, `NavigateDown`, `NavigateLeft` and `NavigateRight` |
| `UINavigation` | `None` | Never reached or left by navigation |
| `UILayoutType` | `Horizontal` | Children stand in a row, in sibling order, at their :term[preferred sizes]{id=preferred-size} |
| `UILayoutType` | `Vertical` | Children stand in a column, in sibling order, at their preferred sizes |
| `UILayoutType` | `Grid` | Children fill cells of `CellSize`, in `Columns` columns (0 fits as many as the width holds) |
| `UIChildAlignment` | `TopLeft` | The block of children sits in the top left corner of the padded rect |
| `UIChildAlignment` | `TopCenter` | The block sits at the top, centered across |
| `UIChildAlignment` | `TopRight` | The block sits in the top right corner |
| `UIChildAlignment` | `MiddleLeft` | The block sits at the left, centered down |
| `UIChildAlignment` | `MiddleCenter` | The block sits in the center |
| `UIChildAlignment` | `MiddleRight` | The block sits at the right, centered down |
| `UIChildAlignment` | `BottomLeft` | The block sits in the bottom left corner |
| `UIChildAlignment` | `BottomCenter` | The block sits at the bottom, centered across |
| `UIChildAlignment` | `BottomRight` | The block sits in the bottom right corner |

## Events and script callbacks

An event is a record that the player did something to a widget: clicked it, moved a slider, changed the focus or submitted a field. The UI system queues events while it handles the frame's input and delivers them before the scripts' `OnUpdate` of the same frame, in the order the inputs happened: pointer, then navigation, then submit. [UI input](../ui/input.md) teaches how the input becomes events. The table lists the four values of `UIEventType`, the script :term[callback]{id=callback} that carries each to game code, and the moment it fires.

| Event type | Callback of `StrataScriptClassDesc` and of `Script` | Arguments | Fires when |
| --- | --- | --- | --- |
| `Click` | `OnUIClick` | The widget | A button is released over itself after a press on it, or Submit is pressed while it has the focus |
| `ValueChanged` | `OnUIValueChanged` | The widget and the new value | A slider's value or a toggle's state changes through input, never through code; a toggle's value is 0 or 1 |
| `FocusChanged` | `OnUIFocusChanged` | The widget and whether it gained the focus | A selectable gains or loses the keyboard and gamepad focus |
| `Submit` | `OnUISubmit` | The widget | An input field's text is submitted: Enter, or a gamepad's Submit, while it is edited |

Each callback reaches the scripts on the widget's entity first, then those on its event target when that names another entity, once per script instance. The engine reads each of the four only when the `StructSize` of the class description covers it. A module built against an older header therefore keeps working. Engine code listens through `IUIEvents` instead of a script; its two functions are in the next table.

| Service function | Meaning |
| --- | --- |
| `IUIEvents::AddUIEventListener` | Registers a function that receives every `UIEventInfo` (type, widget, its unique identifier, event target, value, focus flag) and returns an identifier |
| `IUIEvents::RemoveUIEventListener` | Removes the listener of an identifier; a removed listener is never called again, and one added during dispatch gets only the next events |

## Reaching elements from code

`IUIControl` is the service that gameplay code, and so the script host, uses to read and change elements while the scene plays. Every element function fails, with the reason in an optional error string, for an invalid entity or one without the component it needs. Values set through it raise no events, because events report only the player's input. The table lists its functions; the SDK's `UIElement` and `UI` classes wrap them.

| Function | Needs | Meaning |
| --- | --- | --- |
| `GetText`, `SetText` | `UIInputField` or `UIText` | The text; an input field's is cut to its character limit |
| `GetImage`, `SetImage` | `UIImage` | The texture handle; a null handle draws the color alone, and other handles must be textures |
| `GetColor`, `SetColor` | `UIImage` or `UIText` | The color, taken from the image's tint first |
| `IsInteractable`, `SetInteractable` | `UISelectable` | Whether the selectable reacts to the player |
| `GetValue`, `SetValue` | `UISlider` or `UIToggle` | A slider's value, clamped and snapped like input, or a toggle's 0 or 1; switching one toggle on switches the others of its group off |
| `GetFocus`, `SetFocus` | `UISelectable` | The focused selectable, or an invalid entity; setting focuses a selectable that reacts to the player, on a canvas that receives input, and an invalid entity clears it |
| `IsPointerOverUI` | none | Whether the pointer is over a raycast target of a canvas that receives input, as of the UI's latest update |
| `IsActionPressed`, `IsActionDown` | none | Whether a UI action, given by its index from `Submit` 0 to `Right` 5, was pressed or is held, as of the UI's latest update; false for other indices |

## The reserved action map

An input action is a named control that the player can rebind, and a map is a group of them (see [UI input](../ui/input.md)). The game UI reads one reserved map named `UI` with six actions, written `UI/<name>`. Players rebind them like any other action, and the full table of maps and bindings is in [Audio and input reference](../reference/audio-input.md). A game's own action called `Left` never interferes, because the UI looks the actions up by their qualified names.

| Action | Qualified name | Default bindings and use |
| --- | --- | --- |
| `Submit` | `UI/Submit` | Enter, the number pad's Enter, Space and the gamepad's A: clicks the focused selectable |
| `Cancel` | `UI/Cancel` | Escape, and the gamepad's B: stops editing an input field; the UI raises no event for it, so game code reads it to close a menu |
| `Up`, `Down`, `Left`, `Right` | `UI/Up`, `UI/Down`, `UI/Left`, `UI/Right` | The arrow keys, and the d-pad and left stick of every gamepad: move the focus |

A held action repeats: it fires on the press, again after 0.4 seconds, and every 0.1 seconds after that. The repeat counts unscaled time, so a menu keeps repeating while the time scale is 0.

## Limits

Each limit is a constant of the source, and the table gives what happens at it. They are small because the UI keeps its work proportional to what changes. A quad is a rectangle the :term[graphics card]{id=gpu} draws, and a font atlas is one texture that holds the glyphs of a font. [How the UI is drawn](../ui/drawing.md) teaches the quads, atlases and layouts behind them.

| Constant | Value | Meaning |
| --- | --- | --- |
| `c_MaxLayoutsPerCanvas` | 4 | Layouts kept per root canvas, one for each canvas size in units; a fifth size replaces the layout used longest ago |
| `c_MaxQuadChanges` | 256 | Changed ranges of quads remembered per layout; more mean a full upload of the layout's quads |
| `c_MaxBoundAtlases` | 4 | Font atlases bound to one draw, so a canvas with up to four fonts is one draw call |
| `c_MaxUIFonts` | 256 | Fonts one scene's UI can use at once; a text without room gets no glyphs |

## Statistics and stages

`GameUISceneStats` counts the work the UI did since the last call of `GameUIScene::TakeStats`, which also resets them. The work follows what changed, so a still screen leaves every counter at 0. The unit tests and the speed tests of the UI read the counters to prove that.

For example, a window that shrinks from 1920 by 1080 to 1280 by 720 under `ScaleWithScreen` keeps the same size in canvas units. The kept layout then serves it, and `ElementsLaidOut` stays 0. A window that changes its shape needs a new layout, and `FullRebuilds` counts it. Read the counters over several frames: a `FullRebuilds` that grows every frame points at a screen that keeps changing shape.

| Field | Meaning |
| --- | --- |
| `ElementsLaidOut` | Elements whose rects were computed |
| `TextsShaped` | Calls of `ShapeText`, for measuring and for drawing |
| `QuadsBuilt` | Quads written |
| `FullRebuilds` | Layouts of a whole canvas, after a new screen size or when the scene no longer knew what changed |

The UI also reports its time to the frame profiler under two stages. The :term[central processing unit]{id=processor} (CPU) stage covers building and recording the draws; the :term[graphics processing unit]{id=gpu} (GPU) stage covers the draws on the graphics card. [Measured costs and their budgets](../reference/performance.md) lists the budgets of the UI's speed tests.

| Stage | Kind | Covers |
| --- | --- | --- |
| `Render.UI` | CPU | The UI pass's preparation and the recording of its draw runs |
| `GPU.UI` | GPU | The UI pass's world-space and screen-space draws, inside the :term[renderer's]{id=renderer} overlays |

## Where it lives in Strata

- `Strata/src/Strata/GameUI/GameUIComponents.h`: the components, the eleven enums and the conventions comment.
- `Strata/src/Strata/GameUI/GameUIScene.h`: `GameUISceneStats`, `c_MaxLayoutsPerCanvas` and `c_MaxQuadChanges`.
- `Strata/src/Strata/GameUI/GameUIRenderData.h`: `c_MaxBoundAtlases` and `c_MaxUIFonts`.
- `Strata/src/Strata/GameUI/GameUIRenderer.cpp`: the stages `Render.UI` and `GPU.UI`.
- `Strata/src/Strata/Scene/SceneServices.h`: `UIEventType`, `UIEventInfo`, `IUIEvents` and `IUIControl`.
- `Strata/src/Strata/Input/UIActions.h`: the six UI actions and their repeat times.
- `StrataScriptCore/Include/StrataScript/ScriptABI.h`: the four UI callbacks of `StrataScriptClassDesc`.
- `StrataEditor/src/Editor/EditorUICommands.cpp`: the `ui.*` commands.
