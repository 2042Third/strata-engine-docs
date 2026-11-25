---
id: ui/what-game-ui-does
title: "What a game UI must do"
description: "Why a game's menus and HUD are a retained tree of rectangles made of entities, and how Strata takes a menu from components to pixels."
kind: concept
size: M
tracks: [E]
needs: [world/scene-graph]
time: 35
learn:
  - id: why-retained
    text: explain why Strata's game UI is retained and made of entities, while the editor's panels are immediate mode
  - id: name-components
    text: name the eleven UI components and say what each one does
  - id: trace-tour
    text: trace one frame of a menu through the "UI" scene system and the overlay pass, and name the page that explains each step
since: 0.4.0
status: final
---

Open the main menu of the Third-Person sample. It has a Play button, a Settings button that opens toggles and `UISlider` controls, and a Credits panel whose text scrolls past. Four demands decide how this user interface (UI) works.

First, the menu must look the same at 1280x720, at 2560x1440 and on a 21:9 monitor. Second, it must answer the mouse, the keyboard and a gamepad. Third, a pause menu must keep moving while the game itself runs at time scale 0, so its buttons still fade when you hover them. Fourth, the click on Play must never also reach the game: the player who presses a button does not also fire a weapon.

None of these demands is about drawing a rectangle. Each one is about what the program remembers between frames and who decides what happens next. This page builds the answer from the problem up and ends with a map of the module that Strata uses.

## Pixel positions break on other screens

The first idea every programmer has is the direct one. Each frame, the game code draws the text and the images of the menu at fixed pixel positions. Strata worked this way at first: before version 0.4.0 its only UI was text that you placed on the screen in pixels.

Try it with one button. You design on a 1920x1080 screen and place a button 400 pixels wide and 70 pixels tall with its top-left corner at x = 760, y = 500, which centres it. Now run the game at 1280x720. The button still sits at x = 760 and is still 400 pixels wide, so it spans 760 to 1160 on a screen that is only 1280 wide. It is off-centre and about one and a half times too big.

The same approach fails in three more ways.

- **No focus.** A mouse points at a place, so any position works. A gamepad has no pointer. The player presses "down" and the game must know which button comes next, so the buttons need a remembered current choice and a known order. A bag of draw calls has neither.
- **No order for clicks.** Two panels overlap, and the player clicks where both lie. Only the one drawn on top should answer. Drawing code has no record of what lies where, so each button would have to test the click against all the others.
- **Work in every frame.** The code lays out and draws the whole menu every frame, even when nothing moves. A menu changes a few times a minute.

Each failure has the same cause. The program has pictures but no model of what the pictures mean. The fix is a model: a structure that says what the elements are, where they lie in relation to each other, and which one is on top.

## A UI is a tree of rectangles

Think of a form on paper. A page contains boxes, and a box contains a label and a field. Each inner box sits relative to the box around it, not relative to the corner of the page. Change the page and every inner box moves with its parent. Every game UI uses this model.

The page is a **canvas**: an entity with a `UICanvas` component, which marks the root of one screen of UI (or one plane in the world).

Everything below a canvas is a **UI element**: an entity with a `UIRect` that stands under a root canvas. A rectangle's position is a rule relative to its parent, such as "centred, 400 by 70", and never a pixel number.

From that tree, three jobs follow, and each one has a fixed order.

- **Layout** turns the rules into one box per element for the current screen.
- **Drawing** walks the tree and paints the boxes in tree order, so later siblings and children land on top.
- **Hit testing** answers "what is under this point?" by taking the topmost box that contains it.

```mermaid caption="A menu as a tree: the canvas holds a column, the column holds the buttons, and each button holds a label. Layout runs down the tree, drawing runs in tree order, and a click is tested from the topmost box." alt="A tree with a canvas at the top, a column below it, three buttons below the column and one label under each button."
flowchart TD
    C["Canvas"] --> Col["Column"]
    Col --> B1["Play button"]
    Col --> B2["Settings button"]
    Col --> B3["Quit button"]
    B1 --> L1["Label"]
    B2 --> L2["Label"]
    B3 --> L3["Label"]
```

Layout needs the tree because a child's box depends on its parent's. Drawing needs it because order in the tree is order on the screen, and hit testing reads that order backwards. The tree works like the hierarchy of [the scene graph page](../world/scene-graph.md): parents, children and sibling order mean the same.

### The sizes that survive any screen

The model also repairs the first failure. A canvas does not use pixels. It uses its own length, the canvas unit, and one number converts units to pixels. In the mode `ScaleWithScreen` the canvas keeps the proportions of a reference resolution, by default 1920x1080, and chooses that number from the real screen. The setting `MatchWidthOrHeight` weighs the screen's width against its height; its default 0.5 is an even blend.

:::example[One button on three screens]
The button is 400 by 70 canvas units. The scale is the number of pixels in one canvas unit. With the default blend, Strata takes the base-2 :term[logarithm]{id=logarithm} of the width ratio and of the height ratio, averages them, and raises 2 to the result. That is the geometric mean of the two ratios.

At 1280x720 both ratios are 1280 / 1920 = 0.667 and 720 / 1080 = 0.667, so the scale is 0.667. The button is 266.7 by 46.7 pixels, and the canvas still measures 1920 by 1080 units.

At 2560x1440 both ratios are 1.333, so the button is 533.3 by 93.3 pixels and the canvas again measures 1920 by 1080 units.

At 21:9, take 2560x1080. The width ratio is 1.333 and the height ratio is 1.0, so the scale is the square root of 1.333, which is 1.155. The button is 461.9 by 80.8 pixels, and the canvas measures 2217 by 935 units: wider than the design, with room for anchors to spread the layout.
:::

## Two ways to keep a UI around

The tree must live somewhere. Engines answer in two ways, and the difference decides who owns the state of every button.

In **immediate-mode GUI** (IMGUI) code describes the UI again every frame, and the library keeps little state. You write `if (Button("Play"))` each frame; the call draws the button, checks the mouse and returns whether the player clicked, all at once. There is no button object to create or delete.

The next fence shows a whole menu in a made-up language, not any real library's. Look at how the loop itself holds everything.

```text
every frame:
    BeginWindow("Menu")
    if Button("Play"):     StartGame()
    if Button("Settings"): OpenSettings()
    Slider("Volume", volume)
    EndWindow()
```

The sketch needs no tree and no names for buttons, so it is short to write. That is why Dear ImGui, a well-known library of this kind, runs the Strata editor's own panels; [the immediate mode page](../editor-ui/immediate-mode.md) gives the reasons.

The flaw shows when the menu grows. The code runs every frame, so you pay for the whole menu every frame, even when nothing changed. A fade over a quarter of a second needs a timer that you must store, because the library keeps none. A designer who wants to move a button must change code.

**Retained-mode GUI** answers each flaw. It keeps the UI as a tree of widgets that stores its own state, and the engine lays it out and draws it. You build the tree once, and the engine remembers it. Unity's canvas UI, Unreal's widget system, Godot's Control nodes and the web's document tree all work this way.

A retained UI has its own cost. The program must create and connect objects, then keep them in step with the game: a score label needs the score. Data lives in two places, the game and the widget, and they can disagree. The UI also needs a way to learn what changed, so that it does not work on all of it every frame.

| Approach | Cost per frame | Quality | Complexity | Used by |
| --- | --- | --- | --- | --- |
| Pixel positions drawn by game code | Everything, always | Breaks on other screens, no focus | Lowest to start, highest to fix | Early prototypes, Strata before 0.4.0 |
| Immediate mode | The whole UI, always | Fine for tools, weak for fades, navigation and art | Low | Dear ImGui panels, debug overlays, the Strata editor |
| Retained mode | Only what changed | Strong: states, navigation, authoring, animation | Higher: an object model and change tracking | Unity's canvas UI, Unreal's widgets, Godot's Control nodes, the web |

## Strata's game UI is retained and made of entities

Strata's game UI is retained, and its tree is made of entities. A UI element is an entity with a `UIRect` under a root canvas. The canvas, the rect and the widgets are components, so the editor's Inspector, the scene file, prefabs and scripts handle UI exactly as they handle a mesh or a light.

:::why[Why entities, and not a separate widget tree?]
A UI with its own object model would need its own saving, its own undo, its own copy and paste and its own editor. Components already have all of these. A button in a scene can be duplicated, put into a prefab, changed in the Inspector with undo and saved with the scene, because it is an entity like any other.

References between widgets, such as a slider's fill bar or a button's event target, are entity properties. When you duplicate or paste a group, or place a prefab instance, those references point at the copies, and a menu that you duplicate stays wired to itself. Out-of-range values in a saved file are clamped when the scene loads.

The cost is that the UI must follow the scene's change rules. A script or tool that writes a UI field directly has to signal the change, and the layout, the text shaping and the hit grids rebuild only for what changed. The same signal serves the transform contract in [the scene graph page](../world/scene-graph.md). The details are in [the UI contract page](contract.md).
:::

Retained mode also gives the performance Strata wants. Layout and drawing cost work only when something changes. A menu that sits still costs one comparison to check, not a rebuild. Compare the immediate-mode loop above, which pays in full every frame.

The editor's panels stay immediate mode, and that is no contradiction. A person edits them, a tool changes constantly, and nobody ships them. Do not confuse the two. The game UI described on this page is what players see, and it lives in the scene.

## From components to pixels

Here the page follows the Third-Person main menu from its components to the screen. Each stop names the page that explains it in depth.

### Eleven components

All eleven components share the category "UI" in the editor, and every one except `UIRect` requires `UIRect` on the same entity. The menu uses ten of them; the input field is the one it lacks.

- `UICanvas` marks a root, and sets the scale mode, the reference resolution, the draw order and where a world-space canvas stands. It is explained in [rects, anchors and layout](layout.md).
- `UIRect` holds the rule for the box: anchors, pivot, position and size, relative to the parent.
- `UILayout` arranges its children in a row, a column or a grid with padding and spacing, so a menu column needs no hand-placed buttons. Its page is [rects, anchors and layout](layout.md) too.
- `UIImage` paints a texture or a solid colour, with rounded corners, borders, nine-slice stretching or a fill amount for bars. Drawing is explained in [drawing the UI](drawing.md).
- `UIMask` clips its descendants to its box, which is how the credits scroll inside a window. Its page is [drawing the UI](drawing.md).
- `UIText` shows one text in a font, size and colour. Shaping it into lines is in [text and text fields](text.md).
- `UISelectable` gives an element states: normal, hovered, pressed, focused and disabled, with a colour or image for each, plus the rules for moving the focus.
- `UIButton` raises a click. `UIToggle` holds an on or off value, in groups if needed. `UISlider` holds a number between two limits. All three need a `UISelectable` to be touched, and all three are explained in [UI input](input.md).
- `UIInputField` is a line that the player types, with a caret. It is explained in [text and text fields](text.md).

The Third-Person menu uses buttons for Play, Settings, Credits and Quit, toggles and `UISlider` controls in the settings, and a mask around the credits. Other samples use the same components for their heads-up displays (HUD) and loading screens. To make menus and a HUD in the editor, see [the menus page](../make/menus.md) and [the HUD page](../make/hud.md).

### Screen space and world space

A canvas draws in one of two places. A canvas in **screen space** is painted over the finished picture, with the pixels of the window as its size. A canvas in world space, the other render mode, is a flat plane that stands in the 3D scene: a sign, a computer screen or a name tag. It is depth-tested, so a wall can hide it.

A scene can hold many canvases. Root canvases draw in the order of their `SortOrder`.

### Focus

A mouse needs no help to choose a button. A keyboard or gamepad does. **Focus** is the one widget that Submit and the direction keys act on. The player presses a direction, and the focus moves to a neighbour; the player presses Submit, and the focused widget is clicked.

The `UISelectable` of each widget chooses how neighbours are found: `Automatic` picks the nearest widget in that direction, `Explicit` uses four named neighbours and `None` makes the widget a dead end. The menu's script focuses Play in `OnCreate`, so a gamepad player can press Submit at once. A focused widget that becomes disabled, hidden or gone loses the focus.

The keys come from the built-in input map named UI, with Submit, Cancel and four directions. The map is the subject of [the input actions page](../input/actions.md). Holding a direction repeats after 0.4 seconds and then every 0.1 seconds, counted in unscaled time. Since 0.6.0 the player can rebind these keys like any other action; before that, navigation used fixed keys.

### One frame

Follow one frame while the game plays.

1. The input system reads the devices.
2. The "UI" scene system runs. It reads the actions, lays out each canvas for the screen that takes input, and rebuilds the hit grids that changed, the tables that find which boxes lie under a point. It then drops a focus that can no longer act, finds what the pointer is over, handles typing, moves the focus, updates every widget's state and delivers the queued widget events.
3. Scripts run `OnUpdate`. The events of this frame, such as `OnUIClick`, are already delivered.
4. The :term[renderer]{id=renderer} draws the scene and runs the post-processing and tone mapping. Over that finished picture it paints world-space text and the world-space canvases, tested against the scene's depth, then screen text, and last the screen-space canvases over it all.

The order has a purpose. The UI runs before the scripts so that a script already knows whether the pointer is over the UI. While the UI holds a click, it marks the pointer as captured, and the game's mouse-button queries report nothing. That is how the click on Play never reaches the game. A script that aims with the mouse asks `UI::IsPointerOverUI()` too.

Every canvas draws after post-processing, so colour grading never changes the text. The whole system runs on unscaled time, which is how a pause menu keeps fading at time scale 0. Detail for each step: [UI input](input.md) for the system's order, [the UI contract](contract.md) for what stays valid, and [drawing the UI](drawing.md) for the pass.

```mermaid caption="One frame of a menu: input, then the UI system, then the scripts, then the renderer's post-processing, world canvases, text and screen canvases." alt="A flow from input through the UI system and the scripts to the renderer, where post-processing comes first, then world canvases, then text, then screen canvases."
flowchart LR
    In["Input frame"] --> UI["UI system"]
    UI --> Sc["Script OnUpdate"]
    Sc --> P["Post-processing"]
    P --> W["World canvases"]
    W --> T["Screen text"]
    T --> S["Screen canvases"]
```

### The module and its neighbours

All of this code lives in one module, `Strata/src/Strata/GameUI/`. The module forms its own layer, and its files may include only the Core, Input, Asset, Reflection, Scene and Renderer layers. Only the composition root includes it: `Strata/src/Strata/Engine/BuiltinModules.cpp`, the one file that lists every module the engine starts with.

`RegisterGameUIModule` registers the eleven components, the overlay pass and the "UI" scene system. The renderer reaches the UI only through the overlay registry, and scripts reach it only through scene services. An engine built without the module therefore still renders and plays.

```mermaid caption="The game UI layer includes the layers below it; the composition root includes the module; the renderer and scripting reach it only through registries and services." alt="Boxes for the game UI layer, the layers it may include, the composition root that includes it, and the renderer and scripting layers that never include it."
flowchart TD
    Root["Composition root"] -->|includes| G["Game UI"]
    G --> Below["Core, Input, Asset, Reflection, Scene, Renderer"]
    R["Renderer"] -. "overlay registry" .-> G
    S["Scripting"] -. "scene services" .-> G
```

The solid arrows are includes; the dotted ones are links at run time through a registry or a service. No include arrow reaches the module from the renderer or scripting.

## What this choice cannot do

Strata's UI is small by design. It has no scroll views, drop-down lists, rich text or multi-line input fields. The eleven components are all there is. A mask clips a list that you scroll yourself with a script, as the credits do, and an input field is one line.

Retained mode also means a game must keep the UI in step with its data. Nothing updates a score label by itself; a script sets it. For the wider list of what the engine omits, see [what Strata does not do](../appendix/not-in-strata.md).

## Common mistakes

- **Mistake: designing in pixels.** Symptom: the menu is off-centre or tiny on another screen. Fix: size in canvas units, anchor to the parent and choose a scale mode.
- **Mistake: taking the editor's panels for the game UI.** Symptom: a game maker searches the editor's panels for a menu tool. Fix: build menus from the eleven components in the scene; games link no editor code.
- **Mistake: drawing UI from a script every frame.** Symptom: cost without change, no focus, no order for clicks. Fix: make the UI as entities and react to events such as `OnUIClick`.
- **Mistake: reading the mouse for a click on a button.** Symptom: the game also fires on a click the UI took. Fix: let the UI raise the event, and ask `UI::IsPointerOverUI()` before game-side mouse actions.

## Summary

- Strata's game UI is retained and made of entities, because components give a UI saving, undo, prefabs and Inspector editing for free, and because layout and drawing cost work only for what changes. The editor's panels are immediate mode, a different tool for a different job.
- The eleven components are `UIRect`, `UICanvas`, `UILayout`, `UIMask`, `UIImage`, `UIText`, `UISelectable`, `UIButton`, `UIToggle`, `UISlider` and `UIInputField`. Every one but `UIRect` requires `UIRect`.
- One frame runs the "UI" scene system before the scripts and draws screen canvases after post-processing. Each step has a page: layout, the contract, text, drawing and input.

## Check yourself

1. A designer lays out a menu at 1920x1080 in pixels and ships it. Which result do you expect at 1280x720?

   a) The menu scales down to fit.
   b) The menu keeps its pixel sizes, so it is off-centre and about one and a half times too large.
   c) The menu stays correct, because the engine scales pixel positions.

   :::answer{tests="why-retained"}
   The answer is b. Pixel positions are fixed numbers, so nothing scales them. Option a would need a canvas with a scale mode and rules, which is the point of the tree. Option c names a scaling that pixel-based drawing never does.
   :::

2. Which of these is not one of the eleven components?

   a) `UISlider`
   b) `UIMask`
   c) `UIScrollView`
   d) `UIInputField`

   :::answer{tests="name-components"}
   The answer is c. The module registers no scroll view; a mask clips a list that a script moves. The other three are components: a number control, a clip box and a typed line.
   :::

3. Put these in the order they run in one frame: the scripts' `OnUpdate`, the screen-canvas draw, the "UI" scene system, post-processing.

   :::answer{tests="trace-tour"}
   The "UI" scene system, the scripts' `OnUpdate`, post-processing, the screen-canvas draw. The UI runs first so that scripts know about the pointer, and draws last so that post-processing never alters it. [UI input](input.md) explains the first step.
   :::

4. Why does a pause menu still fade its hover colour at time scale 0?

   :::answer{tests="why-retained, trace-tour"}
   The "UI" system reads the unscaled delta time of the scene, not the scaled one. Fades, key repeat and hover all run on that clock, so the menu is alive while the game is frozen.
   :::

## Exercises

1. **Basic.** Predict which engine files outside `Strata/src/Strata/GameUI/` include a header of the game UI module. Then search to check your guess.

   :::answer[Worked solution]{tests="trace-tour, why-retained"}
   Only the composition root should, because the layer table lets only the Engine layer include the module. Run `git grep -l '#include "Strata/GameUI/' -- Strata/src` in the engine's :term[repository]{id=repository}. Apart from the module's own files, the search finds `Strata/src/Strata/Engine/BuiltinModules.cpp`, which lists `RegisterGameUIModule` beside the other modules. No renderer or scripting file appears, so removing that one line removes the UI.
   :::

2. **Medium.** In a new project, make a canvas with one button and attach a script that sets the time scale to 0 in `OnCreate` and logs `UI::IsPointerOverUI()` and the left mouse press in `OnUpdate`. Before you play, predict three things: whether the hover tint still fades, whether `OnUIClick` still comes, and which presses the game sees.

   :::answer[Worked solution]{tests="why-retained, trace-tour" solution="tutorials/ui/what-game-ui-does/exercise-2.tutorial.json"}
   In the editor, use the Hierarchy's **+ > UI** to create a canvas and a button, write the script from the file, build it and play. The hover tint fades, because the UI runs on unscaled time. `OnUIClick` still comes for the same reason. The game sees no left press while the pointer is over the button, because the UI captures the pointer; it sees the press when you click on empty space. The file holds the script and the commands that do all this.
   :::

3. **Hard.** Design the same menu in immediate mode. Say what each approach does on a frame where nothing changes, and on a frame where a gamepad moves the focus.

   :::answer[Worked solution]{tests="why-retained"}
   The immediate-mode loop runs all its calls every frame, so a still frame costs the whole menu. It must store the focus itself, in a variable that the code owns, and move it by reading the pad before it draws the buttons. The retained UI checks that no canvas changed and does almost nothing. On a pad frame it moves the focus entity, changes the two widgets' states and draws again only what changed. The immediate version is shorter to write, and the retained one is cheaper to run and easier to author.
   :::

## Where it lives in Strata

- The module: `Strata/src/Strata/GameUI/`, with `GameUIComponents.cpp` for the eleven registrations and `GameUIRegistration.cpp` for `RegisterGameUIModule`.
- The composition root: `Strata/src/Strata/Engine/BuiltinModules.cpp`.
- The system: `GameUISystem` ("UI"), registered before "Scripting" when it is present.
- The renderer's side: `Strata/src/Strata/Renderer/SceneOverlay.h` and `GameUIRenderer`.
- The layer table: `StrataTests/Architecture/Layers.json`.
- The example: `Samples/ThirdPerson/Assets/Scenes/MainMenu.stscene` and its script `Samples/ThirdPerson/Scripts/MainMenu.cpp`.
- In the editor: the Hierarchy's **+ > UI** menu creates ready elements.

## Further reading

- Dear ImGui's readme and wiki (beginner to intermediate): the immediate-mode model in a library's own words.
- Unity manual, "Unity UI" and its Canvas and Rect Transform pages (beginner): a retained canvas with anchors.
- Unreal Engine documentation, "UMG UI Designer" (beginner): widget trees.
- Godot documentation, "Using Containers" and "Size and anchors" (beginner): control nodes.
- Casey Muratori, "Immediate-Mode Graphical User Interfaces" (intermediate): the original talk on the idea.
