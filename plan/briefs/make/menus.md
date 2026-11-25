# Brief: `make/menus`

| Field | Value |
| --- | --- |
| Title | Menus: buttons, navigation, pause and settings screens |
| Kind | T |
| Size | L |
| Tracks | G |
| Needs | `make/timers-events`, `make/script-fields` |
| From | gameui "Making UI do things: widgets, events and scripts", "Making menus and HUDs in the editor" (the main menu scene); scripting "The gameplay API, part 3": the UI callbacks (`OnUIClick`, `OnUIValueChanged`, `OnUIFocusChanged`, `OnUISubmit`), `UIElement` interactable, value and focus, `UIAction`, the pointer over UI, `Game`'s window mode, resolution, vsync and window size; scripting "The gameplay API, part 3": `Input`'s binding capture, saving the bindings and typed text; audio-input "Controls players can change" (the rebinding side); hands-on G10, G14: a pause menu at time scale 0, a settings screen (volume, window, vsync), a rebinding screen (binding capture and saving) and a name field (typed text); use home of binding capture and of the rebinding screen |
| Unit | `plan/allocation/make-b1.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/menus` — Menus: buttons, navigation, pause and settings screens

**Covers.** A tutorial: the course of `make/animation` gets a main menu, a pause menu, a settings screen, a rebinding
screen and a name field. It opens with how a widget reaches a script: a button, toggle, slider or input field calls the
scripts on its own entity and then those on its Event Target, before the frame's `OnUpdate`, so that one menu script
handles a whole menu. The step sections, each ending in a checkpoint:

1. A main menu scene: a new scene with a canvas and no camera, a panel with a vertical layout group, a title and three
   buttons from the Hierarchy's **+ > UI** presets. A scene without a camera shows its UI over black.
2. Make the buttons work: a `MainMenu` script (the Manual's example), the buttons' Event Target set to its entity,
   `OnUIClick` telling the buttons apart; Play switches to the course with `Game::LoadScene` and Quit ends the game with
   `Game::Quit`, one line each, given with a link to `make/levels-saves`, which teaches scene switches.
3. Keyboard and gamepad: the canvas's First Selected, the focus, navigation with the UI map's Submit, Cancel and four
   directions (rebindable, and repeating when held), the states a selectable shows (normal, hover, pressed, focused,
   disabled). Nothing shows focus until the first press, which only focuses (Submit clicks nothing yet); without First
   Selected the start is the top-left selectable, so the menu sets First Selected or calls `Focus()` when it opens.
4. A pause menu at time scale 0: a Pause action, a panel on a canvas of its own in the course, `Time::SetTimeScale(0)`,
   the cursor freed and the focus put on Resume; Resume undoes it. The pause canvas's Sort Order is above that of the
   game's other canvases, such as a HUD, so that it draws over them and takes the input first, as the sample's Menus
   canvas (10) does over its HUD (0). The UI keeps fading and repeating at time scale 0 because it runs on unscaled
   time, and so must anything a pause menu animates; the excerpt is the Third-Person pause menu. A test that taps the
   paused menu through simulated input still sees its taps end, since they count the frames a game updates at time
   scale 0 as well as its fixed steps (`editor/stepping`).
5. A settings screen, made a prefab and placed in both scenes: a volume slider whose `OnUIValueChanged` calls
   `Audio::SetMasterVolume`, a toggle group for the window mode (Windowed, Borderless, Fullscreen) that acts only on a
   toggle's value 1, with one sentence on what the modes do (Fullscreen switches the display to the resolution asked
   for, Borderless covers the display at the desktop's mode without a switch, Windowed restores the last windowed place
   and size, and a game whose manifest says Fullscreen starts Borderless), and a vsync toggle; values set from code raise
   no events, so showing the current values triggers nothing. In the editor's play mode the window requests are only
   recorded and shown over the Game view; the exported game applies them between frames. The settings last for the
   session; `make/levels-saves` keeps them for the next, and `make/quality` adds the Graphics row.
6. A rebinding screen: one row per action with its bindings as text (`Input::GetActionBindings`), whose key names are
   those of the keys' US positions, since a game's key names do not follow the player's keyboard layout; a button that
   listens for the next control (`BeginBindingCapture`, then `PollBindingCapture` every frame, `CancelBindingCapture`
   after a timeout); `SetActionBindings`; `SaveBindings` when the screen closes; and Reset to defaults. While it listens
   no action reacts, so the key pressed does not also close the menu. In the editor the players' bindings are kept in the
   project's `.strata/Saves` folder, and the Input Actions page marks them "In play".
7. A name field: an Input Field with a placeholder and a character limit; `OnUISubmit` when the player presses Enter,
   the text read with `GetUI().GetText()` and shown on the HUD; while the field is edited the keyboard is the UI's.
8. Scrolling credits: the main menu's credits move inside a mask, on unscaled time, as the Third-Person main menu's do.
9. A sign in the world: a world-space canvas on a wall with a button that the player clicks through the game camera.
   The Scene view's 2D canvas mode edits screen-space canvases only, so the sign is laid out in the viewport, or turned
   to Screen Space while it is built.

It ends with what game UI does not have (scroll views, drop-downs, rich text, multi-line fields; localization and
right-to-left text; key names that follow the player's keyboard layout), linking `appendix/not-in-strata`. The
exercises extend the menus: a confirmation panel on Quit that takes the focus when it opens and that Cancel closes, and
a Back button on the settings screen. At the end the reader can build menus that work with a mouse, a keyboard and a
gamepad, pause a game, and let players change their volume, window and controls.

**Leaves out.**

- Canvases, rects, anchors, images and text, and a HUD → `make/hud`
- Scene switches, loading screens and saving the settings for the next run → `make/levels-saves`
- The Graphics row and players' graphics options → `make/quality`
- How widgets, focus, navigation and events work inside → `ui/input`
- Text fields and typed text inside → `ui/text`
- The UI map and its key repeat inside → `input/actions`
- The players' bindings file and capture inside → `input/rebinding`
- Building and testing a menu through commands → `make/automated-playtests`

**Fit.** `over`: about 6,850 words against L (5,000). Nine step sections of about 29 steps (about 5,400 words with
their two excerpts, rules and figures), the opening on how a widget reaches a script and the exercises reach L's top.
The next size is XL (8,000) by S2; the split of the earlier line stays the other way: `make/menus` "Menus: buttons,
navigation, pause and settings screens" (sections 1 to 5, 8 and 9) and `make/rebinding` "Controls players can change: a
rebinding screen and a name field" (sections 6 and 7).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:185` | feature | home | The widgets and navigation of game UI for a maker: selectable states, buttons, toggles in groups, sliders, input fields, layout groups and masks, the **+ > UI** presets, navigation through the UI map, pause menus at time scale 0, the pause canvas's Sort Order above the other canvases' so that it draws over them and takes the input first, a main menu scene with no camera (canvases, rects, images and text are `make/hud`'s) |
| `gamedev:204` | feature | home | The window from a script: `Game::SetWindowMode` (Windowed, Fullscreen, Borderless), `SetResolution`, `SetVSync`, `GetWindowSize`; the editor records the requests |
| `gamedev:145` | feature | home | Player rebinding: `GetActionBindings`, `SetActionBindings`, `ResetActionBindings`, `SaveBindings` and binding capture; saved per player; "In play" and Reset Player Bindings on the Input Actions page |
| `gamedev:426` | figure | home | UI event routing: a widget, its own scripts, then its Event Target's scripts, before `OnUpdate` |
| `gamedev:520` | rule | home | In a toggle group act only on value 1 |
| `gamedev:543` | hands-on | home | G10: the main menu scene without a camera, the settings screen with a volume slider, the pause menu at time scale 0; its Graphics row is `make/quality`'s and its best score `make/levels-saves`' |
| `gamedev:547` | hands-on | home | G14: the rebinding screen: list, capture, save, reset |
| `gamedev:641-644` | term | home | Layout group and mask; selectable, focus and navigation; event target; toggle group |
| `gamedev:646` | term | home | Rebinding and binding capture |
| `gameui:381` | concept | home | Scaled against unscaled time for a pause menu; the mistake of animating it with `Time::GetDeltaTime()` |
| `gameui:425` | code | home | `Docs/Manual/GameUI.md:69-87`: the Manual's `MainMenu`: `OnUIClick` telling buttons apart by name, `OnUIValueChanged` for a volume slider |
| `new:9` | code | home | `Samples/ThirdPerson/Scripts/PauseMenu.cpp:97-122`: pause and resume: the time scale, the panel, the focus and the cursor. No inventory surveyed the file (`plan/inventory/gamedev.md:694-696`) |
| `gameui:492` | figure | home | A toggle group and a slider with its fill and handle at two values, from the page's settings screen |
| `gameui:500` | figure | home | A main menu scene without a camera, its UI over black (its capture waits for the check `new:26`) |
| `gameui:733` | open | home | Settled at the pin: the Third-Person `MainMenu.stscene` has a primary camera, so the picture over black is made from the page's own main menu scene, which has none |
| `gameui:571` | hands-on | home | The first menu: canvas, panel, vertical layout, title and buttons, a `MainMenu` script through the Event Target, a scene without a camera |
| `gameui:577` | hands-on | home | The pause menu at time scale 0, with a volume slider and gamepad navigation from First Selected |
| `foundation:540` | hands-on | home | The same task as the foundation survey gives it: time scale 0 for a pause menu, and a fade driven by the unscaled delta |
| `gameui:580` | hands-on | home | The settings screen: a toggle group, sliders and a name field with `OnUISubmit` |
| `gameui:582` | hands-on | home | Scrolling credits inside a mask |
| `gameui:584` | hands-on | home | A sign in the world: a world-space canvas whose button is clicked through the game camera, laid out in the viewport or turned to Screen Space while it is built, since the 2D canvas mode edits screen-space canvases only |
| `scripting:442` | figure | home | The page's settings screen with its rebinding row capturing a control (the Graphics row appears on `make/quality`) |
| `scripting:520` | hands-on | home | The pause and settings menu: time scale 0, unscaled time, `OnUIClick`, a rebinding row with capture; the graphics preset row is `make/quality`'s |
| `audio-input:570` | hands-on | home | The rebinding menu: bindings listed, capture with a timeout, `SetActionBindings`, `SaveBindings`, reset; "In play" in the editor |
| `new:7` | not-done | home | No scroll views, drop-downs, rich text or multi-line input fields: a mask clips a scrolling list, and an input field is one line. Evidence: `Strata/src/Strata/GameUI/GameUIComponents.cpp:211-397` registers no such component; `Strata/src/Strata/GameUI/GameUIComponents.h:255-260, 272-273` |
| `new:8` | erratum | home | The UI map's default bindings are those of `Strata/src/Strata/Input/InputActionSet.cpp:147-152`: Submit is Enter, keypad Enter, Space or gamepad A; Cancel is Escape or gamepad B; the directions are the arrows, the d-pad and the left stick. Evidence: the comment at `Strata/src/Strata/Input/UIActions.h:12-13` gives Enter, Escape and the arrows and leaves out keypad Enter and Space; `StrataScriptCore/Include/StrataScript/UI.h:17-18` agrees with the code |
| `new:26` | open | home | Check: A capture of the Game view without a camera. The claim: the figure `gameui:500` is taken from the page's own main menu scene, which has no camera, as the Game view shows it, its UI over black, with a live `viewport.capture` of the Game view (`live`, `camera` "scene"), which reads back the frame that view rendered; a capture that is not live resolves its view without that fallback and finds no camera. The photographer runs it, and the page's brief waits for the result (R39). Evidence: the Game view's fallback, `StrataEditor/src/Panels/GameViewPanel.cpp:112-116` and `StrataEditor/src/Editor/ViewportRenderer.cpp:72-86`; the live capture reads the Game view's renderer, `StrataEditor/src/Editor/EditorViewportCommands.cpp:516-520, 538-555`; the capture that is not live, `StrataEditor/src/Editor/EditorViewportCommands.cpp:430-433` and `StrataEditor/src/Editor/ViewportRenderer.h:58-61` (nullopt for the Game view without a camera) |
| `new:27` | not-done | home | Key names that follow the player's keyboard layout: a game shows a key's name by its US position, so the rebinding screen of step 6 does too; only the editor's shortcuts follow the layout. Evidence: `Docs/Releases/0.7.0.md:361-362`; `git grep -n GetLayoutKey 822a7a46 -- Strata/src StrataScriptCore` finds only the window's own code (`Strata/src/Platform/GLFW/GLFWWindow.cpp:626`, `GLFWWindow.h:48`, `Strata/src/Strata/Core/Window.h:117`) and the ImGui platform's (`Strata/src/Strata/ImGui/ImGuiPlatform.cpp:180` and a comment of its header) |
| `new:28` | not-done | home | Localization and right-to-left text: a menu's texts are the strings its elements hold, in one language and written left to right. Evidence: `Docs/Releases/0.7.0.md:415` (localization among what the release does not have); `Docs/Roadmap.md:1713`; `git grep -niE -e "locali[sz]" -e "right-to-left" 822a7a46 -- Strata/src StrataScriptCore` finds nothing |
| `new:29` | erratum | home | The game UI survey's mistake "a menu unusable with a gamepad because nothing is focused" (`plan/inventory/gameui.md:369-370`) is wrong: with nothing focused, the first direction press or Submit focuses the topmost input canvas's First Selected, else its top-left selectable; the menu works, and that first press only focuses. Evidence: `Strata/src/Strata/GameUI/GameUISystem.cpp:526-531, 539-542` (no focus: `Focus(FindStartSelectable(...))`), `:769-807` |
| `new:30` | hands-on | home | Exercises (make it yours), done in the editor and in a script: a confirmation panel on Quit whose No button takes the focus when it opens and which the UI map's Cancel closes; a Back button on the settings screen. Evidence: `StrataScriptCore/Include/StrataScript/UI.h:123-127` (`UIElement::Focus`), `:165-169` (`UI::IsActionPressed`) |
| `gameui:59-62` | feature | use | `UISelectable`, `UIButton`, `UIToggle` (and its group) and `UISlider`, in a maker's words (their home is `ui/input`) |
| `gameui:63-65` | feature | use | `UILayout`, `UIInputField` and `UIMask` |
| `gameui:145` | feature | use | A scene with no camera but with screen UI shows the UI over black |
| `gameui:182` | feature | use | Toggles flip, groups are exclusive, switching the one that is on off does nothing |
| `gameui:185-190` | feature | use | The UI map, the start of navigation, automatic navigation, slider steps, Submit and Cancel, visual states and their fades on unscaled time |
| `gameui:201-206` | feature | use | The four callbacks, dispatch to the widget's scripts then the Event Target's, and the SDK's `UIElement` and `UI` |
| `gameui:226` | feature | use | The Third-Person main menu, the model the page's menu follows |
| `gameui:363` | concept | use | Widgets as state machines: the states by priority, click on release, toggle groups |
| `gameui:367` | concept | use | Focus and navigation for keyboard and gamepad; with nothing focused the first press only focuses, so the menu sets First Selected or calls `Focus()` when it opens (the survey's "unusable" is corrected by `new:29`) |
| `gameui:372` | concept | use | Text input in a field |
| `gameui:376` | concept | use | Events that decouple game logic from widgets |
| `gameui:423` | code | use | The Third-Person `MainMenu.cpp`: focus on create, Cancel, credits scrolled in their mask (its home is `ui/input`) |
| `gameui:539` | rule | use | The UI runs on unscaled time |
| `gameui:543` | rule | use | Values set from code raise no events |
| `gameui:545` | rule | use | Read navigation through the UI map, not raw keys |
| `gameui:554` | rule | use | Keep the field's text element a `UIText` and give the field a `UIMask` |
| `gamedev:380` | code | use | The comment of `SettingsMenu.cpp` on a toggle group's 0 events (its home is `make/quality`) |
| `gamedev:198-199` | feature | use | `Game::LoadScene` and `Game::Quit`, one line each for Play and Quit (their home is `make/levels-saves`) |
| `audio-input:162` | feature | use | The players' bindings, kept apart from the project's |
| `audio-input:165-166` | feature | use | Binding capture; the UI actions and their repeat |
| `audio-input:458` | figure | use | Binding capture as a state machine, the idea behind the page's capture button |
| `audio-input:478` | figure | use | "In play" markers and Reset Player Bindings on the Input Actions page |
| `audio-input:525` | rule | use | Gameplay reads rebindable controls as input actions |
| `audio-input:533` | rule | use | A capture's press triggers nothing |
| `scripting:122` | feature | use | `Input`'s binding capture and its rebinding functions |
| `scripting:129` | feature | use | `Game`'s window functions |
| `scripting:131` | feature | use | `UIElement`, `UI` and `UIAction` |
| `scripting:338` | concept | use | Player-facing systems: rebindable input, the window applied after the frame |
| `worlds-runtime:91` | feature | use | The game window from scripts, through `IGameWindow` |
| `worlds-runtime:449` | rule | use | Window changes apply between frames, and only when they change something |
| `foundation:80` | feature | use | One sentence of the window modes' contract beside the window-mode toggle of step 5: Fullscreen switches the display to the resolution asked for, Borderless covers the display at the desktop's mode, Windowed restores the last windowed place and size, and a Fullscreen manifest starts Borderless (its home is `core/windows-events`) |
| `gameui:219` | feature | link | The 2D canvas mode edits screen-space canvases only, which step 9 meets (its home is `editor-ui/scene-view`) |
| `audio-input:521` | rule | link | Simulated taps on the paused menu of step 4 end, since the input step count adds the frames a game updates at time scale 0 to its fixed steps (`EditorContext::GetInputStepCount`, taught on `editor/stepping`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Canvases, rects, anchors, images and text; the Hierarchy's UI presets | `make/hud` | must |
| Time scale, unscaled time, and scripts that find each other | `make/timers-events` | must |
| Entity and asset fields set in the Inspector | `make/script-fields` | must |
| Input actions, their bindings and the Input Actions page | `make/input` | must |
| Making a scene and opening it | `make/scenes-entities` | must |
| Prefabs and their instances | `make/prefabs` | must |
| Master volume and one-shot sounds | `make/sound` | must |
| `std::string`, `std::vector` and `std::optional` | `basics/programming-3` | must |
| Scene switches and quitting | `make/levels-saves` | helps |
| The exported game, where the window changes show | `make/export` | helps |
| Players' graphics options | `make/quality` | helps |

**Starting state.** The end checkpoint of `make/animation`, downloadable: the course with the animated robot as the
player and the follow camera. The steps add a Pause action to the Gameplay map, as `make/input` taught.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `rebinding` | Rebinding | - |
| `toggle-group` | Toggle group | - |
| `binding-capture` | Binding capture (use) | - |
| `event-target` | Event target (use) | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-b1-15 | should | stale-item | `gameui:425` on `make/menus` (steps 2 and 5) | The Manual's `MainMenu` excerpt has no `ST_SCRIPT_CLASS(MainMenu) { ST_SCRIPT_FIELD(Level); }`, so a reader who types it gets no class in the picker and no `Level` field. Its volume line divides the slider's value by 10, but the Hierarchy's Slider preset runs from 0 to 1, so with it the volume never passes a tenth. The sample's own volume slider runs from 0 to 1 and passes the value as it is. | After the excerpt, a sketch shows the two registration lines, and the page either sets the slider's Max Value to 10 or uses the value as it is (one sentence each; about 60 words). The excerpt keeps its place; the sketch carries the difference. | `allocation/make-b1.md:772-774`, `:786-787`, `:844`; `Docs/Manual/GameUI.md:69-87` (line 85: `value / 10.0f`); `StrataEditor/src/Editor/GameUIPresets.cpp:173-174`; `Strata/src/Strata/GameUI/GameUIComponents.h:209-213`; `Samples/ThirdPerson/Scripts/SettingsMenu.cpp:41-44`; `StrataScriptCore/Include/StrataScript/Script.h:840-852` |
| critic-make-b1-17 | could | thin-home | `gamedev:204` on `make/menus` (step 5) | The home row takes `SetResolution`, but no step uses it, and no other page does. A game maker expects a resolution on a settings screen. At the pin, in Windowed mode it sets the window's size in pixels, and Fullscreen switches the display to the resolution asked for, else to the desktop's. No script function lists the resolutions a display offers, so a game offers fixed sizes. | Step 5 adds a Resolution row of three fixed sizes as buttons (there are no drop-downs) with `Game::SetResolution` (about 120 words), and a not-done line: no list of the display's modes, with the search below as its evidence. | `allocation/make-b1.md:786-793`, `:835`; `StrataScriptCore/Include/StrataScript/Game.h:72-86`; `Strata/src/Platform/GLFW/GLFWWindow.cpp:495-500`, `:509-523`; `git grep -n -i -e glfwGetVideoModes -e DisplayModes 822a7a46 -- Strata/src StrataScriptCore StrataRuntime/src` finds nothing |
| critic-make-b1-18 | could | missing-item | `make/menus` | The outline's From for the page names "the pointer over UI", but the Covers does not take `UI::IsPointerOverUI`. Gameplay that aims or shoots with the mouse asks it, so that a click on a menu or a HUD does not also fire, as the Physics Playground does. | One sentence and one line of code in step 4: gameplay that reads the mouse asks `UI::IsPointerOverUI()` first (about 50 words); the row `scripting:131` already covers it. | `outline-1.md:210`; `allocation/make-b1.md:891`; `StrataScriptCore/Include/StrataScript/UI.h:156-158`; `Samples/PhysicsPlayground/Scripts/Playground.cpp:91` |
