# Brief: `ui/input`

| Field | Value |
| --- | --- |
| Title | UI input |
| Kind | I |
| Size | XL |
| Tracks | E |
| Needs | `ui/layout`, `input/actions`, `input/mouse-cursor`, `scripting/script-system`, `basics/math-geometry` |
| From | gameui ch. 8 without input-field editing (hit grids, world-space rays, gestures and capture, widget states, navigation, UI actions and repeat, event dispatch, the script bridge) |
| Unit | `plan/allocation/ui.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `event-target` | Event target | - |
| `gesture` | Gesture | - |
| `half-open-rect` | Half-open rect | - |
| `hit-test` | Hit test | - |
| `raycast-target` | Raycast target | - |
| `selectable` | Selectable | - |
| `spatial-navigation` | Spatial navigation | - |
| `transition-ui` | Transition (ui) | - |
| `uniform-grid` | Uniform grid | - |
| `visual-state` | Visual state | - |
