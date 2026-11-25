# Brief: `make/hud`

| Field | Value |
| --- | --- |
| Title | HUDs: text, score and bars |
| Kind | T |
| Size | M |
| Tracks | G, B |
| Needs | `make/sound` |
| From | gameui "Making menus and HUDs in the editor" (the HUD half: canvases, anchors, text, images); render-core "Text: fonts, shaping and signed distance fields" (use side: `TextComponent`, text without a canvas); scripting "The gameplay API, part 3": `UIElement` text, image, color and value; Coin Run's coin count and timer |
| Unit | `plan/allocation/make-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/hud` — HUDs: text, score and bars

**Covers.** The page gives Coin Run its coin count and timer on the screen, and teaches the game's UI at the maker's
level. The ideas from zero, in short paragraphs with the anchoring figure: a canvas is the root of a UI drawn over the
screen (or placed in the world); it scales with the screen from a reference resolution, so the HUD keeps its look on
any window; every element is a rect with anchors (where it attaches to its parent), a pivot and a size; text and
images are elements on rects. The steps. (1) **+ ▸ UI ▸ Canvas**: Screen Space, **Scale With Screen** at 1920 x 1080.
(2) The viewport's **2D** chip and the **Game UI** chip: the canvas drawn flat at its reference aspect, with handles to
drag rects. (3) **+ ▸ UI ▸ Text** for the coin count, anchored to the top-left corner with the anchor presets, a font
size and a left alignment, because a UIText is centred by default and a centred count is cut at the edge. (4) A second
text for the timer anchored top-right. (5) A panel behind them (**+ ▸ UI ▸ Panel**) with a sliced image, so its corners
keep their size as it stretches. Then one paragraph: an image is hit by the pointer by default, so the panel would take
the game's mouse clicks in its corner; the HUD's canvas turns **Receives Input** off, which keeps it drawn but never hit
or navigated (the menus' canvases of `make/menus` keep it on). (6) A bar along the bottom for the time left, stretched
between two anchors: an image of type **Filled**, whose **Fill Amount** (0 to 1) shows the part left; along a stretched
axis **Size** is added to the span between the anchors, so Size 0 fills it and a negative Size leaves margins. (7) The
script: a `CoinHud` script finds the texts and writes `GetUI().SetText` with the count of coins left (it counts the
entities tagged `Coin`) and the time from `Time`, every frame, which costs nothing while a text stays the same
(`new:49`); it sets the bar with `SetProperty("UIImage", "FillAmount", ...)`, never `SetValue`, which moves only a
slider or a toggle, and changes colors with `SetColor` when time runs low. (8) Check every screen: the Game
view's resolution menu at 16:9, 4:3 and 21:9; the corner texts stay in their corners and the bar stretches. (9) Text
without a canvas: a `TextComponent` (**+ ▸ 3D Text**) floating over the start, in the world and facing the camera, and
why a HUD is never built from screen-space text: it does not scale with the screen. The exercises (`new:39`) are done
in the editor and in a script. At the end the reader can lay out a HUD that survives every screen and drive it from a
script; buttons, focus and menus are `make/menus`'.

**Leaves out.**

- What a game UI must do; retained against immediate UIs → `ui/what-game-ui-does`
- Rects, anchors and layout inside → `ui/layout`
- Text in game UI inside: shaping, overflow → `ui/text`
- Fonts, the glyph atlas and signed distance fields → `gpu/text`
- How the UI is drawn → `ui/drawing`
- Buttons, toggles, sliders that take input, focus and navigation, menus → `make/menus`
- UI events and the UI action map → `make/menus`
- Testing a UI through commands → `make/automated-playtests`

**Fit.** `over`: about 4,050 words against M (3,000). Nine steps at B0's length, canvases and anchors taught from zero
with the anchoring figure, the script, the two HUD mistakes, three pictures and two exercises take it over M's top. L
(5,000) by S2; no split, because steps 1 to 9 build and check one layout.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:339` | concept | home | UI for makers: canvas scaling, anchors and pivots, nine-slice; the HUD mistakes (screen-space text, the centred default) |
| `gamedev:424` | figure | home | UI anchoring: a corner count, a stretched bar and a centred panel at two resolutions |
| `gamedev:456` | figure | home | The viewport's 2D canvas mode with the Game UI chip on |
| `gamedev:509` | rule | home | Do not build HUDs from screen-space `Text`; use a UI canvas |
| `gamedev:510` | rule | home | UIText alignment defaults to Center |
| `gamedev:637` | term | home | Canvas (screen space, world space) |
| `gamedev:638` | term | home | Reference resolution and scale mode |
| `gamedev:639` | term | home | Rect, anchor, pivot |
| `gamedev:640` | term | home | Nine-slice (sliced image) |
| `gameui:215` | feature | home | The presets of **+ ▸ UI**: Canvas, Panel, Image, Text and the widgets, as a maker makes them |
| `gameui:480` | figure | home | A score anchored top-right and a bar stretched along the bottom at two aspect ratios |
| `gameui:574` | hands-on | home | Step 8: a HUD checked at three screens. The item's health bar "driven by SetValue/FillAmount" is set with `SetProperty("UIImage", "FillAmount", ...)`, never `SetValue`, which fails on an image. Evidence: `StrataScriptCore/Include/StrataScript/UI.h:113-119` (`SetValue`: a slider or a toggle only) (read at the pin) |
| `new:49` | feature | home | Step 7: setting a text to what it already shows costs nothing, so a HUD may set its texts every frame: `SetText` changes the component only when the text differs. Evidence: `Strata/src/Strata/GameUI/GameUISystem.cpp:988-990`; `StrataScriptCore/Include/StrataScript/UI.h:54` (read at the pin) |
| `render-core:665` | hands-on | home | Step 9: world and screen text with `TextComponent`; the use home of text without a canvas |
| `scripting:513` | hands-on | home | Pickup and score, ending in the HUD's coin count (the trigger and the sound came on the two pages before) |
| `new:39` | hands-on | home | Exercises: **Basic.** move the timer to the top centre with the anchor presets and check it at 4:3 and 21:9 in the Game view's resolution menu; **Medium.** a second Filled bar that shows the part of the coins collected, its `FillAmount` set from the script with `SetProperty("UIImage", "FillAmount", ...)`, with a prediction of its value after two of five coins. Evidence: `Strata/src/Strata/GameUI/GameUIComponents.h:94`, `:115` (Filled and `FillAmount`, 0 to 1) |
| `gameui:53-58` | feature | use | The canvas, its scale and render modes, the rect, the image and the text components; step 5's paragraph: an image is a raycast target by default, so the HUD's canvas turns **Receives Input** off (drawn, never hit or navigated). Evidence: `Strata/src/Strata/GameUI/GameUIComponents.h:60`, `:121`; `Docs/Manual/GameUI.md:57-58` (read at the pin) |
| `gameui:77` | feature | use | The scale per screen and the size in canvas units |
| `gameui:100` | feature | use | Anchor, pivot, position and size, at the maker's level; step 6: along a stretched axis Size is added to the span, so 0 fills it and a negative Size leaves margins. Evidence: `Strata/src/Strata/GameUI/GameUIComponents.h:74-78`, `:85` (read at the pin) |
| `gameui:118` | feature | use | Wrapping and overflow from the rect |
| `render-core:536` | figure | use | Text in the world and on the screen |
| `scripting:131` | feature | use | The SDK's `UIElement`: text, image and color; a slider's value named for `make/menus` |
| `editor-ui:155` | feature | use | The canvas mode inside the Scene view |
| `editor-ui:569` | figure | use | Canvas mode on a UI canvas |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Finding entities and counting the coins left from a script | `make/scripting-scene` | must |
| `Time` and `OnUpdate` | `make/script-loop` | must |
| The Game view's resolution menu | `make/editor-tour` | must |
| `std::string` and numbers turned into text | `basics/programming-2` | must |
| Importing a font or an image | `make/assets` | helps |

**Starting state.** The end state of `make/sound` (`startsFrom {"tutorial": "make/sound"}`): the rolling ball, trigger
coins with their sound, the bump and the music. The sliced image of step 5 comes from the release's
`Samples/ThirdPerson/Assets/UI/` (Kenney's UI Pack, CC0, credited in that sample). The page ends with the coin count,
the timer and the time bar on the screen.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `nine-slice-sliced-image` | Nine-slice (sliced image) | - |
| `scale-mode` | scale mode | - |
| `canvas` | Canvas (use) | - |
| `reference-resolution` | Reference resolution (use) | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-a-6 | should | missing-item | `make/scripting-scene` (step 7), `make/hud` (step 7) | `GetProperty` and `SetProperty` take their type from the value, and the SDK converts only `bool`, `int32_t`, `uint32_t`, `int64_t`, `float`, the glm vectors, `glm::quat`, `std::string`, `Entity` and `AssetHandle`. A `double` (the literal `0.5`, or arithmetic on `Time::GetElapsedTime()`, which returns `double`) or a bare text literal does not compile, with an error about an incomplete `ValueTraits`. A float property takes an integer; an integer property refuses a float at run time. | Step 7 states the rule with its fixes (`0.5f`, `std::string("...")`, or the type named: `SetProperty<float>(...)`); `make/hud` step 7 sets the bar from a `float` and says why (about 70 words). | `allocation/make-a.md:1063-1064`, `:1519-1521`; `StrataScriptCore/Include/StrataScript/Value.h:40-41` (the template only declared), `:44-229`; `StrataScriptCore/Include/StrataScript/Entity.h:67-72`, `:388-395`; `StrataScriptCore/Include/StrataScript/Time.h:28-33`; `Strata/src/Strata/Scripting/ScriptValue.cpp:153-171` |
| critic-make-a-7 | should | stale-item | `make/hud` (steps 3 to 5), `make/project-coin-run` (steps 2 and 3) | After the canvas of step 1, steps 3 to 5 make the texts and the panel with **+ ▸ UI ▸ ...**. The Hierarchy's **+** button (and the Entity menu) always creates at the top level, and a UI element made outside a canvas gets a new canvas of its own, so each step adds another canvas. An element goes into the canvas through the canvas's right-click **Create Child ▸ UI ▸ Text**, which no page names. | Step 3 makes its text with a right-click on the canvas ▸ **Create Child ▸ UI ▸ Text** and says why; steps 4 and 5 and the win and lose panels of `make/project-coin-run` do the same; `make/scenes-entities` names **Create Child** beside the "+" menu in one sentence (about 70 words). | `allocation/make-a.md:1509-1513`, `:1808-1810`; `StrataEditor/src/Panels/SceneHierarchyPanel.cpp:560`, `:929-931`; `StrataEditor/src/EditorLayer.cpp:1582`; `StrataEditor/src/Editor/GameUIPresets.cpp:301-310`; `Docs/Manual/GameUI.md:11-14` |
| critic-make-a-8 | should | stale-item | `make/hud` (steps 3, 4 and 6) | The Inspector's UI Rect section does two things the steps do not say. An anchor preset keeps the rect where it is unless the grid's **Position** box is ticked (off by default; **Pivot** is on), so the count stays in the middle after "top-left" is chosen. Along a stretched axis the section shows **Left** and **Right** margins (positive inside) in place of Position and Size, so step 6's "Size added to the span" is not what the editor tab shows. | Step 3 ticks **Position** before choosing the preset and says what both boxes do; step 6's editor tab sets the bar's **Left**, **Right**, **Pos Y** and **Height**, and the sentence on Size added to the span goes to its command tab and to the script exercise (about 80 words). | `allocation/make-a.md:1511-1518`, `:1566`; `StrataEditor/src/UI/UIRectDrawer.cpp:33-38`, `:113-123`, `:224-236`, `:259`; `Docs/Manual/GameUI.md:22-33` |
| critic-make-a-9 | should | stale-item | `render-core:665` on `make/hud` (step 9) | **+ ▸ 3D Text** adds a `Text` component with its defaults, and by default it is Screen Space, at the middle of the screen. In the world its Font Size counts world units per em (32 by default, at least 1), and the text lies in its entity's XY plane facing +Z: it does not turn to the camera. The step's "in the world and facing the camera" needs the reader to change all three. | Step 9 clears **Screen Space**, sets **Font Size** near 1 and turns the entity so that its +Z faces the Main Camera, with one sentence that the text does not follow the camera; the page writes the component's name, `Text`, where it says `TextComponent` (about 60 words). | `allocation/make-a.md:1524-1526`, `:1561`; `StrataEditor/src/Panels/SceneHierarchyPanel.cpp:112`; `Strata/src/Strata/Renderer/RendererComponents.h:380-394`; `Strata/src/Strata/Renderer/RendererComponents.cpp:646-648`; `.claude/skills/strata-make-a-game/SKILL.md:355-356` |
| critic-make-a-19 | should | order | `make/scenes-entities`; `make/project-coin-run` (step 5) | Coin Run's camera is framed only on `make/project-coin-run`. Until then the Game view shows Basic 3D's camera, 6 m back and 2 m up, aimed at the centre with a vertical view of 60 degrees. The ground nearest the camera, from about z = 4 to the wall at z = 10, almost a third of the 20 m level, and that wall are out of view, so the ball and coins leave the screen on `make/input` to `make/hud`. | `make/scenes-entities` adds a step after the walls: the Main Camera set high and tilted down over the level (for example Translation (0, 16, 13), Rotation (-55, 0, 0)), checked with the Game camera chip (F8); `make/project-coin-run` step 5 then only adjusts it (about 120 words). | `allocation/make-a.md:221-223`, `:1812`; `StrataEditor/src/Editor/ProjectTemplates.cpp:31`, `:51-55`; `Strata/src/Strata/Scene/Components.h:133`; `StrataEditor/src/Panels/ViewportPanel.cpp:460-461` |
| critic-make-a-29 | could | other | `make/play-test-debug` (step 8) | The planted bug, "the HUD counts a coin that was destroyed in the same frame", shows only if `CoinHud` counts after the fixed steps. A frame runs every `OnUpdate`, then the fixed steps (where `OnTriggerEnter` collects and destroys the coin), then `OnLateUpdate`, and destroys at its end; a count in `OnUpdate`, as `make/hud` step 7 writes it, never sees a destroyed coin. | The row says that the tutorial's planted `CoinHud` counts in `OnLateUpdate`, so the breakpoint shows the coin still valid after its `Destroy`, and that the fix counts in `OnUpdate` or skips collected coins (about 40 words). | `allocation/make-a.md:1610-1612`, `:1519-1520`; `Strata/src/Strata/Scene/Scene.cpp:2253-2330`; `StrataScriptCore/Include/StrataScript/Script.h:35`, `:54-59` |
