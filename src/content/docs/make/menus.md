---
id: make/menus
title: "Menus: buttons, navigation, pause and settings screens"
description: "Give the course a main menu, a pause menu, a settings screen, a rebinding screen and a name field that work with a mouse, a keyboard and a gamepad."
kind: tutorial
size: L
tracks: [G]
needs: [make/timers-events, make/script-fields]
time: 120
learn:
  - id: event-routing
    text: explain how a click on a widget reaches a script, and what an event target is for
  - id: navigation
    text: choose the First Selected element and the Focus call that make a menu work with a keyboard and a gamepad
  - id: pause-menu
    text: build a pause menu that stops the game at time scale 0 and draws over the heads-up display
  - id: settings-screen
    text: write a settings screen whose toggle group acts only on a value of 1
  - id: rebind-screen
    text: build a rebinding screen with binding capture, a timeout and saved bindings
since: 0.4.0
status: final
---

## What you will make

The course gets a main menu with Play, Settings and Quit. In the course, a pause menu stops the game, a settings screen changes the volume, the window and the vsync, and a rebinding screen lets players choose their own keys. A name field and scrolling credits finish the job.

::figure{id=result}

## How a widget reaches a script

A click lands on a rectangle on the screen, and your code lives somewhere else. Your script has to learn which rectangle, once, in a place where it may change the game.

A **widget** is an element of the user interface (UI) that the player clicks, drags or types into: a button, a toggle, a slider or an input field. You make each from the Hierarchy's **+** menu, under **UI**. When the player uses a widget, Strata calls a function of a script. It calls the scripts on the widget's own entity first.

Then it calls the scripts on the widget's **event target**: another entity that the widget names in its **Event Target** field, so that the widget's events reach it too.

The event target is the reason a whole menu needs one script. Give each of ten buttons the same event target, the entity that holds a `MainMenu` script, and the ten clicks arrive in one place. The script tells the buttons apart by the entity it receives.

```mermaid caption="A click travels from the widget to its own scripts, then to the scripts of its event target, before the update of the frame." alt="A flow from a player's click through the widget, the scripts on the widget's own entity and the scripts on its event target, ending at the frame's update."
flowchart LR
  A[Player click] --> B[Widget]
  B --> C[Scripts on the widget's entity]
  C --> D[Scripts on the event target]
  D --> E[OnUpdate of the frame]
```

Four functions of a `Script` receive these events. `OnUIClick` gets the widget that was clicked. `OnUIValueChanged` gets the widget and its new value: a slider's number, or 0 or 1 for a toggle. `OnUIFocusChanged` gets the widget and whether it gained the focus. `OnUISubmit` comes when the player presses Enter in an input field.

All four run before the frame's `OnUpdate`, in the order the inputs happened. A click happens when the player releases the mouse button over the button they pressed on. Pressing on a button and moving away before the release cancels the click, as in every menu you have used.

One more rule matters: the events report the player's actions only. When your own code sets a slider with `SetValue`, no `OnUIValueChanged` follows. A settings screen that shows the current volume therefore does not trigger itself.

## What you need

- The end of [Animation](animation.md): the course with the animated robot as the player and the follow camera. Continue your own project, or download Checkpoint 9 at the end of [Animate only what is seen](animation.md#animate-only-what-is-seen).
- The course's scene (the checkpoints' `Scenes/Main.stscene`) and the action `Gameplay/Jump`. This page adds `Gameplay/Pause` and, where missing, `Gameplay/Boost`.
- Six script files, which come with the checkpoints of this page: `MainMenu.cpp`, `PauseMenu.cpp`, `SettingsMenu.cpp`, `RebindMenu.cpp`, `NameField.cpp` and `Credits.cpp`.
- About two hours.

Each checkpoint offers two downloads: use one or the other. Open the project and continue there, or run the editor commands on your own project from the checkpoint before. They write no file, so first copy the section's one script file from that checkpoint's `Scripts` into yours, and nothing else: the commands refuse a scene or :term[prefab]{id=prefab-make} that already exists.

## Make a main menu that works

A scene that holds only a menu needs no camera: with a canvas and no camera it shows the user interface over black, without the cost of drawing a world.

The canvas, its layout and its rectangles are the subject of [Text, score and bars](hud.md); here you only place them.

:::::steps

1. Make a new scene and name it `MainMenu`. Add a canvas, a panel with a vertical layout and, inside it, a title and three buttons.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **File ▸ New Scene**, then save it as `MainMenu`. Press the **+** button of the Hierarchy and choose **UI**, then `Canvas`. Select the canvas, press **+**, choose **UI**, then `Panel`, and add a vertical layout to the panel with **+ ▸ UI**, then `Vertical Layout`. Add one `Text` and three `Button` entities under the layout, and rename the buttons `Play`, `Settings` and `Quit`.
   :::
   :::tab[With a command]

   ```json
   { "command": "ui.create", "parameters": { "type": "canvas", "name": "Menu" } }
   ```

   Run `ui.create` again with `type` set to `panel`, `verticalLayout`, `text` and `button`, each with the `parent` of the one before.
   :::
   ::::

   **You should see:** the buttons stacked in a column, one under the other, because the vertical layout places its children for you.

   **If you do not see it:** a button sits outside the layout. Drag it onto the layout in the Hierarchy.

2. Look at the Game view. It is black behind the buttons.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open the Game view. The menu draws over black, since the scene holds no camera.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command `viewport.capture` and read the picture it returns.
   :::
   ::::

   **You should see:** your menu over a black field.

   **If you do not see it:** the Game view is empty. Check that the canvas is a **Screen Space** canvas, which draws on the screen.

3. Create the script `MainMenu` and read it.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **Scripts ▸ New Script...** and make a class `MainMenu`. Replace the file's text with the listing below and build with **Scripts ▸ Build Scripts** (Ctrl+B).
   :::
   :::tab[With a command]
   Save the listing below as `Scripts/MainMenu.cpp`, then save the scene and build.

   ```json
   { "command": "scene.save" }
   { "command": "script.build" }
   ```

   After a restart, `scene.open` with the `scene` `Scenes/MainMenu.stscene` reopens the menu.
   :::
   ::::

   **You should see:** the build finish without errors.

   **If you do not see it:** the :term[Problems panel]{id=problems-panel} lists the error and its line.

:::::

:::question
The listings use classes and calls such as `widget.GetName()`. If a word is new, read [Programming: classes and calls](../basics/programming-3.md) and [Classes and inheritance](../basics/cpp-classes.md) first.
:::

The Manual of Strata shows a `MainMenu` that names a button by its entity name and acts on it. Search for the two functions and what each does with its widget.

```cpp src="Docs/Manual/GameUI.md#L69-L87"
class MainMenu : public Script
{
public:
	AssetHandle Level;

	void OnUIClick(Entity widget) override
	{
		if (widget.GetName() == "Play")
			Game::LoadScene(Level);
		else if (widget.GetName() == "Quit")
			Game::Quit(0);
	}

	void OnUIValueChanged(Entity widget, float value) override
	{
		if (widget.GetName() == "Volume")
			Audio::SetMasterVolume(value / 10.0f);
	}
};
```

1. **Lines 74-80:** `OnUIClick` reads the clicked widget's name, then loads a level or quits. The name is the one you gave the button in the Hierarchy.
2. **Lines 82-86:** `OnUIValueChanged` acts on a slider named `Volume`.
3. **Line 85:** the volume line divides the value by 10, so a slider that runs from 0 to 1, as the Hierarchy's Slider does, would never set more than a tenth of the full volume.

The excerpt has no registration, so its class appears in no picker. The page's file registers the class and its fields. For a slider with another range, set its Max Value to that range, or divide by it.

The script of this page is below. It reads the name once, keeps the focus on Play when the menu opens and switches scene with `Game::LoadScene`, which [Levels and saving](levels-saves.md) teaches.

```cpp src="book:tutorials/make/menus/MainMenu.cpp#L8-L28"
class MainMenu : public Script
{
public:
	AssetHandle Level;
	Entity PlayButton;

	void OnCreate() override
	{
		if (PlayButton.IsValid())
			PlayButton.GetUI().Focus();
	}

	void OnUIClick(Entity widget) override
	{
		const std::string name = widget.GetName();
		if (name == "Play")
			Game::LoadScene(Level);
		else if (name == "Quit")
			Game::Quit(0);
	}
};
```

1. **Lines 11-12:** the fields are an asset and an entity. You set them in the Inspector, as you did for :term[script fields]{id=script-field}.
2. **Lines 14-18:** the focus goes to the Play button when the scene starts. The next section, on the keyboard and the gamepad, says why.
3. **Lines 22-26:** `Game::LoadScene` switches to another scene, and `Game::Quit(0)` ends the game with the exit code 0.

The two registration lines complete the class.

```cpp src="book:tutorials/make/menus/MainMenu.cpp#L30-L34"
ST_SCRIPT_CLASS(MainMenu)
{
	ST_SCRIPT_FIELD(Level);
	ST_SCRIPT_FIELD(PlayButton);
}
```

The macro `ST_SCRIPT_CLASS` makes the class appear in the picker, and each `ST_SCRIPT_FIELD` makes a field appear in the Inspector.

:::::steps

1. Attach the script and connect the buttons.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select the canvas and use **Add Component ▸ Script** to attach `MainMenu`. In its `Level` field choose the course scene, and in `Play Button` choose the `Play` entity. Select each button in turn and set **Event Target** in its **UI Button** component to the canvas.
   :::
   :::tab[With a command]
   This step has no menu or button: run `script.add` with the canvas and the class `MainMenu`, then `component.set` on each button's `UIButton` to name the canvas as `EventTarget`.
   :::
   ::::

   **You should see:** each button's Event Target showing the canvas.

   **If you do not see it:** a click does nothing. The usual cause is an empty Event Target; the widget then has only its own scripts.

2. Play the scene and click the buttons `Quit` and `Play`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Play**. Click `Play`: the course loads. Return to the menu scene and click `Quit`: the game ends.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start", "parameters": { "paused": true } }
   ```

   Then click `Play` by its identifier (ID), which `entity.find` with the name `Play` returns, and run five :term[fixed steps]{id=fixed-step}.

   ```json
   { "command": "input.click", "parameters": { "entity": "<the Play button's ID>" } }
   { "command": "play.step", "parameters": { "steps": 5 } }
   { "command": "play.state" }
   ```

   `play.state` names the course. Stop, play again and click `Quit` the same way: in the editor a quit ends play mode.
   :::
   ::::

   **You should see:** the course after Play, and the end of the game after `Quit`.

   **If you do not see it:** nothing happens on Play. The field `Level` is empty: the script cannot load a scene it does not know.

:::::

::checkpoint{stage=1}

::figure{id=menu-works}

## Move through the menu with a keyboard and a gamepad

Many players use no mouse. A gamepad has no pointer at all, and a keyboard user wants to press an arrow and Enter. Strata handles both through the **focus**: the one selectable element that a keyboard or a gamepad is on now. A **selectable** is an element that takes input, such as a button, a toggle or a slider.

The focus moves with six **UI actions**. They are the six actions of the project's UI map: Submit, Cancel and the four directions. By default Submit is Enter (also the one on the number pad), Space or gamepad A.

Cancel is Escape or gamepad B. The directions are the arrow keys, the directional pad and the left stick. Players and the project may change the bindings of all six.

A held direction repeats. Strata moves once on the press, waits 0.4 s, and then moves every 0.1 s. Hold Down for one second and the focus moves once at 0 s and again at 0.4, 0.5, 0.6, 0.7, 0.8, 0.9 and 1.0 s: eight moves. The repeat runs on :term[unscaled time]{id=unscaled-time}, which the section on pausing comes back to.

A selectable shows its state through its **UI Selectable** component: normal, hover, pressed, focused or disabled. Each has a color or an image, and a fade time between them. A disabled element, with **Interactable** off, never takes the focus or raises an event.

Here is the surprise that costs menu makers the most time. With nothing focused, the first press of a direction or of Submit only focuses: Strata picks a start and puts the focus there, and the Submit does not click it. The start is the **First Selected** of the topmost canvas that takes input; without one it is the top-left selectable. Nothing shows the focus before that first press.

So a menu should decide its start. Either set **First Selected** in the canvas, or call `Focus()` on the first button when the menu opens, as the script of the last section did. A player on a gamepad then sees the first button lit at once, and the first press of Submit clicks it.

Read navigation through the UI map, never through raw keys. A script that tests `Input::IsKeyPressed` for Enter breaks when a player changes the bindings of Submit. `UI::IsActionPressed(UIAction::Cancel)` answers for the player's own Cancel.

:::::steps

1. Set the canvas's First Selected and look at the focus.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select the canvas. In **UI Canvas**, set **First Selected** to `Play`. Select the three buttons and open **UI Selectable**: give **Focused Color** a visible tint.
   :::
   :::tab[With a command]
   This step has no menu or button: run `component.set` on the canvas with the component `UICanvas` and the value `FirstSelected` set to the entity of `Play`, and on each button's `UISelectable` with a `FocusedColor`.
   :::
   ::::

   **You should see:** nothing yet in edit mode. The focus exists only in play.

   **If you do not see it:** the **Focused Color** is the same as the normal one. Choose a different tint. The tint multiplies the button's image color, so over a dark or blue image it only darkens it; a white image shows the tint best.

2. Play and use only the keyboard.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Play**. Press **Down** twice, and then **Enter**.
   :::
   :::tab[With a command]
   This step has no menu or button: press each key with `input.key` and run three fixed steps after it.

   ```json
   { "command": "play.start", "parameters": { "paused": true, "build": false } }
   { "command": "input.key", "parameters": { "key": "Down" } }
   { "command": "play.step", "parameters": { "steps": 3 } }
   ```

   Press `Down` once more, then `Enter`. `ui.layout` with the `entity` of a button shows whether it has the focus.
   :::
   ::::

   **You should see:** the tint move from Play to Settings, then Quit; Enter then ends the game.

   **If you do not see it:** the tint never appears. The script calls `Focus()` only when `PlayButton` is set, so check that field in the Inspector.

:::::

::checkpoint{stage=2}

::figure{id=focus-shown}

## Pause the game

A pause menu does two things at once: it stops the game and it shows a menu. Strata stops the game with the **time scale**, a number that multiplies the time a game passes each frame. At 1 the game runs at its normal speed, at 0.5 at half speed, and at 0 nothing that depends on scaled time moves.

The menu itself must not stop. A fade that waits for the game's time would wait forever at scale 0. The game's UI therefore runs on unscaled time, the real time that passes: buttons fade, the held direction repeats and the focus moves while the game is frozen. Anything you animate in a pause menu must do the same, and read `Time::GetUnscaledDeltaTime()` where it would read `Time::GetDeltaTime()`. The delta time at scale 0 is 0, so a bar animated with it never moves.

A pause menu sits on its own canvas. Canvases draw in the order of their **Sort Order**: one with a higher number draws over one with a lower number, and takes the input first. Give the pause canvas a higher order than the heads-up display (HUD). The Third-Person sample does so: its `HUD` canvas has order 0 and **Receives Input** off, so it draws but never takes a click, and its `Menus` canvas has order 10.

Your script's first quote is the update and the click; the sample's pause has the same shape.

```cpp src="book:tutorials/make/menus/PauseMenu.cpp#L19-L29"
void OnUpdate(float) override
{
	if (Input::IsActionPressed("Gameplay/Pause"))
		SetPaused(!m_Paused);
}

void OnUIClick(Entity widget) override
{
	if (widget == ResumeButton)
		SetPaused(false);
}
```

1. **Lines 21-22:** the Pause action opens the menu when it is closed and closes it when it is open.
2. **Lines 27-28:** Resume closes the menu, so a click on the button works as the action does.

The change of state undoes each of its steps on the way back.

```cpp src="book:tutorials/make/menus/PauseMenu.cpp#L32-L48"
void SetPaused(bool paused)
{
	m_Paused = paused;
	Time::SetTimeScale(paused ? 0.0f : 1.0f);
	Panel.SetActive(paused);
	if (paused)
	{
		m_CursorBefore = Input::GetCursorMode();
		Input::SetCursorMode(CursorMode::Normal);
		ResumeButton.GetUI().Focus();
	}
	else
	{
		Input::SetCursorMode(m_CursorBefore);
		UI::ClearFocus();
	}
}
```

1. **Line 35:** the :term[time scale]{id=time-scale} is 0 while paused, so the game stops.
2. **Line 36:** the panel is shown or hidden to match.
3. **Lines 39-41:** the cursor mode is saved, freed so the mouse can click, and the focus goes to Resume.
4. **Lines 45-46:** on the way back the cursor returns to its earlier mode and the focus clears.

Gameplay that aims with the mouse should ask `UI::IsPointerOverUI()` first. The UI hides its clicks from `Input`, but a script that reads the mouse position still sees the pointer over a menu.

:::::steps

1. Add the action `Gameplay/Pause`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **File ▸ Project Settings...**, select **Input Actions**, select the map `Gameplay` and press **Add Action**. Name it `Pause`, set its **Kind** to `Button` and add the bindings `Key/Escape` and `Gamepad/Start`.
   :::
   :::tab[With a command]

   ```json
   { "command": "inputActions.setAction", "parameters": { "action": "Gameplay/Pause", "kind": "Button", "bindings": [ "Key/Escape", "Gamepad/Start" ] } }
   ```

   :::
   ::::

   **You should see:** the action `Pause` in the list of `Gameplay`.

   **If you do not see it:** you are in the map `UI`. Select `Gameplay` first.

2. In the course scene, make a canvas `Pause` with a panel `PausePanel` that fills it, a title and a button `Resume`. Set its **Sort Order** to 10; a HUD keeps 0.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Build it as in the first section, the panel anchored to stretch. In its **UI Canvas**, set **Sort Order** to 10. A HUD's canvas keeps **Receives Input** off.
   :::
   :::tab[With a command]
   This step has no menu or button: run `ui.create` for the pieces (the panel's `anchor` `stretch`) and `component.set` on the `UICanvas` of the new canvas with `SortOrder` set to 10.
   :::
   ::::

   **You should see:** the panel over the course in the Game view.

   **If you do not see it:** the panel hides behind the HUD. The **Sort Order** of the pause canvas is not higher than the HUD's.

3. Attach `PauseMenu` to the canvas `Pause`, with the `Panel` and the `Resume Button` fields set, and set the event target of `Resume` to the canvas. Not on the panel itself, which the script hides when play starts.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Attach the script as in the last section and build. Select `Resume`, and set **Event Target** of **UI Button** to the same entity.
   :::
   :::tab[With a command]
   This step has no menu or button: run `script.add` with the class `PauseMenu` and its fields.
   :::
   ::::

   **You should see:** the fields holding your entities in the Inspector.

   **If you do not see it:** a field is empty and the script does nothing. Set it in the Inspector.

4. Play, press **Escape**, move with the arrows and press **Enter** on Resume.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Play**, then **Escape**: the world stops and Resume lights. Press **Enter**.
   :::
   :::tab[With a command]

   ```json
   { "command": "input.action", "parameters": { "action": "Gameplay/Pause", "steps": 2 } }
   ```

   :::
   ::::

   **You should see:** the robot freeze, the panel appear and the cursor return, then the game continue when you resume.

   **If you do not see it:** the pause does not open. Check that `Gameplay/Pause` has a binding and that the script is attached.

   **Why:** a test that taps the paused menu through simulated input still sees its taps end, since the count of simulated steps adds the frames a game updates at time scale 0.

:::::

::checkpoint{stage=3}

::figure{id=paused}

## Make a settings screen

The screen holds a slider for the volume, a row of toggles for the window mode, three buttons for the window's size and a toggle for the vsync. **Vsync** makes the game wait for the display's refresh, so it draws no half-finished frames.

A **toggle group** is a set of toggles that name the same Group: turning one on turns the others off, and clicking the one that is on does nothing. The window modes are such a group, since a window has one mode at a time. When the player turns `Borderless` on, Strata first turns Windowed off, which raises a value of 0 for Windowed, and then raises a value of 1 for `Borderless`. Both reach `OnUIValueChanged`.

The rule of this section: in a toggle group, act only on a value of 1. Act on the 0 as well and the script asks for Windowed, then for `Borderless`, in one frame. The window still ends `Borderless`, but only because a later window request replaces an earlier one. Anything else the script does for a mode, such as a sound or a saved choice, happens twice, once for the wrong mode.

**Fullscreen** switches the display to the resolution asked for. **`Borderless`** covers the display at the desktop's own mode, with no switch. **Windowed** restores the last windowed place and size. A game whose manifest says Fullscreen starts `Borderless`.

The window changes are requests. In the editor's play mode they are only recorded and shown over the Game view, since the editor has a window of its own. An exported game applies them between frames, and only when they change something.

:::question
The listing below passes a `std::string` and returns nothing from several functions. See [Programming: classes and calls](../basics/programming-3.md) for both.
:::

The first function reads the widget's name and decides what to do. Search for the `else if (value != 0.0f)` line: it is the rule.

```cpp src="book:tutorials/make/menus/SettingsMenu.cpp#L20-L29"
void OnUIValueChanged(Entity widget, float value) override
{
	const std::string name = widget.GetName();
	if (name == "Volume")
		Audio::SetMasterVolume(value);
	else if (name == "VSync")
		Game::SetVSync(value != 0.0f);
	else if (value != 0.0f)
		ChooseWindowMode(name);
}
```

1. **Lines 23-24:** the volume goes to `Audio::SetMasterVolume`. The slider's range is 0 to 1, so the value passes as it is.
2. **Lines 25-26:** the vsync toggle sets `Game::SetVSync` from its value, 0 or 1.
3. **Lines 27-28:** any other toggle is a window mode, and the script acts only when its value is not 0.

The resolution buttons call `Game::SetResolution` with a size in pixels. In Windowed mode it sets the window's size, and in Fullscreen it switches the display to the mode asked for. Game scripts cannot ask a display which modes it has, and Strata has no drop-down element, so a game offers fixed sizes as buttons.

```cpp src="book:tutorials/make/menus/SettingsMenu.cpp#L31-L40"
void OnUIClick(Entity widget) override
{
	const std::string name = widget.GetName();
	if (name == "Size720")
		Game::SetResolution(1280, 720);
	else if (name == "Size1080")
		Game::SetResolution(1920, 1080);
	else if (name == "Size1440")
		Game::SetResolution(2560, 1440);
}
```

1. **Lines 34-35:** a click on `Size720` asks for 1280 by 720 pixels.
2. **Lines 36-39:** the other two buttons ask for 1920 by 1080 and 2560 by 1440.

The mode itself needs its own function, so that the rule stays in one place.

```cpp src="book:tutorials/make/menus/SettingsMenu.cpp#L43-L52"
// Called only for a toggle that turned on: its group turned the others off and raised their 0 first.
void ChooseWindowMode(const std::string& name)
{
	if (name == "Windowed")
		Game::SetWindowMode(WindowMode::Windowed);
	else if (name == "Borderless")
		Game::SetWindowMode(WindowMode::Borderless);
	else if (name == "Fullscreen")
		Game::SetWindowMode(WindowMode::Fullscreen);
}
```

1. **Lines 43-44:** the comment is the rule: the function is called only for a toggle that switched on.
2. **Lines 45-52:** one branch for each of the three window modes.

The scene shows the starting volume with `SetValue`. Because values set from code raise no events, nothing is triggered when the screen opens.

:::::steps

1. Build the settings screen as a :term[prefab]{id=prefab-make}, so both scenes can use it.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In `MainMenu`, beside the column, make a panel `SettingsPanel`. Its vertical layout `SettingsColumn` holds a slider `Volume`, toggles `Windowed`, `Borderless` and `Fullscreen`, a toggle `VSync` and buttons `Size720`, `Size1080` and `Size1440`. Select the three window toggles and, in **UI Toggle**, choose the same entity as **Group**, for example the panel. Drag the panel into the Assets panel to make the prefab, as on [Prefabs](prefabs.md).
   :::
   :::tab[With a command]
   This step has no menu or button: run `ui.create` for each element, `component.set` for the toggles' `Group`, and `prefab.create`.
   :::
   ::::

   **You should see:** the prefab in the Assets panel.

   **If you do not see it:** drag the panel itself, not a child.

2. Attach `SettingsMenu` to the panel and set `Volume Slider` to the slider. Select every widget and set **Event Target** to the panel. New toggles start on, and a group acts only when one switches on: turn **Is On** off for `Borderless` and `Fullscreen`. Give the slider a **Value** of 1. Apply to the prefab, and place an instance under the course's `PausePanel`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Use **Add Component ▸ Script**, build, and fill the field in the Inspector. In the `Overrides` menu choose **Apply All to Prefab**. Save, open the course and drag the prefab onto `PausePanel`.
   :::
   :::tab[With a command]
   This step has no menu or button: run `script.add`, `component.set`, `prefab.apply`, `scene.save`, `scene.open` and `prefab.instantiate`.
   :::
   ::::

   **You should see:** the fields holding your entities.

   **If you do not see it:** a widget has no event target and its change is never heard.

3. Play and move the slider.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In `MainMenu`, press **Play** and drag the slider. Click **Fullscreen**.
   :::
   :::tab[With a command]
   Click the `Fullscreen` toggle, then the slider `Volume`, which a click sets to its middle, 0.5.

   ```json
   { "command": "play.start", "parameters": { "paused": true, "build": false } }
   { "command": "input.click", "parameters": { "entity": "<the Fullscreen toggle's ID>" } }
   { "command": "play.step", "parameters": { "steps": 3 } }
   ```

   `component.get` shows `IsOn` of each `UIToggle` and `Value` of the `UISlider`.
   :::
   ::::

   **You should see:** the sound change with the slider. In the editor, a notice over the Game view says what window the game asked for.

   **If you do not see it:** your window stays as it is: the editor only records the request, and an exported game ([Export](export.md)) applies it.

:::::

The settings last for the session only. [Levels and saving](levels-saves.md) keeps them for the next run, and [Quality](quality.md) adds the Graphics row.

::checkpoint{stage=4}

::figure{id=settings-screen}

## Make a rebinding screen

Players use different keyboards, hands and pads, and a game that fixes its controls shuts some of them out. **Rebinding** is letting players choose the controls of the game's actions themselves, and keeping their choice apart from the project's. [Input](input.md) taught the actions; this screen gives their bindings to the player.

A rebinding screen needs one new idea. The player presses a control, and the game must learn which. **Binding capture** is that step: you ask the engine to listen for the next control the player presses, and later ask what it heard. The functions come in a short row.

- `Input::BeginBindingCapture` starts listening on all devices, or on the ones you name.
- `Input::PollBindingCapture` returns the captured binding once, and nothing until it comes. Call it every frame.
- `Input::CancelBindingCapture` stops listening; a timeout uses it.
- `Input::SetActionBindings` replaces an action's bindings with the text you pass.
- `Input::SaveBindings` keeps the players' bindings for later sessions.
- `Input::ResetActionBindings` restores the project's bindings.

During a capture, each action reports no press. The captured control stays hidden from actions until the player lets go of it. So the press that chooses a key does not also trigger an action, not even Cancel, and a captured left click presses no button.

A binding is text. `Key/Space`, `Gamepad/A` and `Mouse/Right` are bindings, and `GetActionBindings` returns them for an action, the players' own after a rebinding and the project's before. The key names are those of the keys' American positions, so a player with a French keyboard who presses the key that shows the letter A sees `Key/Q`.

An action takes up to 8 bindings. `SetActionBindings` returns false, and changes nothing, when a binding is not valid for the action: a `Button` takes keys, mouse buttons, gamepad buttons and half axes, never a whole stick.

:::question
The screen's script keeps an array and a pointer to text, which the lesson calls `const char*`. See [Memory and pointers](../basics/cpp-memory.md) and [Modern C++](../basics/cpp-modern.md) if they are new.
:::

The click function starts a listening row, resets or closes. Search for the order: `CancelBindingCapture` before `SaveBindings` when the screen closes.

```cpp src="book:tutorials/make/menus/RebindMenu.cpp#L29-L44"
void OnUIClick(Entity widget) override
{
	if (widget == ResetButton)
	{
		Input::ResetActionBindings();
		ShowBindings();
	}
	else if (widget == BackButton)
	{
		Input::CancelBindingCapture();
		Input::SaveBindings();
		Panel.SetActive(false);
	}
	else
		StartListening(widget);
}
```

1. **Lines 31-35:** Reset restores every action to the project's bindings and shows them.
2. **Lines 36-41:** Back cancels a listening that is under way, saves the players' bindings, and hides the panel. Saving on close is the rule: one write, when the player finishes.
3. **Lines 42-43:** any other button is a row, and starts a listening.

The update asks the engine each frame whether it heard something. A timeout ends a listening nobody answers.

```cpp src="book:tutorials/make/menus/RebindMenu.cpp#L46-L59"
void OnUpdate(float) override
{
	if (m_Listening < 0)
		return;
	const std::optional<std::string> binding = Input::PollBindingCapture();
	if (binding)
		Input::SetActionBindings(m_Rows[m_Listening].Action, { *binding });
	else if (Time::GetRealTime() - m_ListenStart < TimeoutSeconds)
		return;
	else
		Input::CancelBindingCapture();
	m_Listening = -1;
	ShowBindings();
}
```

1. **Lines 50-52:** a captured binding replaces the action's bindings with that one binding.
2. **Lines 53-54:** without a binding and before the timeout, the function leaves and asks again next frame.
3. **Lines 55-57:** after the timeout, the capture ends without a change.

The two helpers start a capture and show the bindings of every row as text.

```cpp src="book:tutorials/make/menus/RebindMenu.cpp#L69-L79"
void StartListening(Entity widget)
{
	for (size_t i = 0; i < m_Rows.size(); i++)
	{
		if (widget != m_Rows[i].Button || !Input::BeginBindingCapture())
			continue;
		m_Listening = static_cast<int>(i);
		m_ListenStart = Time::GetRealTime();
		m_Rows[i].Text.GetUI().SetText("Press a control...");
	}
}
```

1. **Line 73:** `BeginBindingCapture` returns false when the engine cannot listen; the row then does nothing.
2. **Lines 75-77:** the row shows that it is listening, and the time of the start is kept for the timeout.

```cpp src="book:tutorials/make/menus/RebindMenu.cpp#L81-L90"
void ShowBindings()
{
	for (const Row& row : m_Rows)
	{
		std::string text;
		for (const std::string& binding : Input::GetActionBindings(row.Action))
			text += (text.empty() ? "" : ", ") + binding;
		row.Text.GetUI().SetText(text.empty() ? "Unbound" : text);
	}
}
```

1. **Lines 86-87:** the bindings of an action are joined into one text.
2. **Line 88:** an action with no binding shows `Unbound`.

In the editor, the players' bindings live in the project's `.strata/Saves` folder, and the :term[Input Actions]{id=input-action} page of the project settings marks the actions the players changed with **In play**. That page has a **Reset Player Bindings** button that deletes the saved file. The project's own bindings never change.

:::::steps

1. In `MainMenu`, build a panel `RebindPanel` whose vertical layout holds a button per action that shows its bindings (`JumpRow`, `BoostRow`), `Reset` and `Back`. Add `Gameplay/Boost` (`Key/LeftShift`) if missing.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Build it as before. The text that shows the bindings is the button's **Label** child: its entity goes in the script's `JumpText` and `BoostText` fields.
   :::
   :::tab[With a command]

   ```json
   { "command": "inputActions.setAction", "parameters": { "action": "Gameplay/Boost", "kind": "Button", "bindings": [ "Key/LeftShift" ] } }
   ```

   Then run `ui.create` for each element; `parts.label` names a button's label.
   :::
   ::::

   **You should see:** a panel with four buttons.

   **If you do not see it:** the panel is behind another. Check its canvas's **Sort Order**.

2. Attach `RebindMenu` to the panel and fill its fields, then set every button's **Event Target** to the panel.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Add the component, build and fill the fields in the Inspector. Keep `Timeout Seconds` at 5.
   :::
   :::tab[With a command]
   This step has no menu or button: run `script.add` with the fields.
   :::
   ::::

   **You should see:** each row holding its entities.

   **If you do not see it:** a row shows no text because its text field is empty.

3. Play, click the Jump row and press a key.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Play**, open the screen, click the Jump row and press **K**.
   :::
   :::tab[With a command]
   This step has no menu or button: click the row, then press the key.

   ```json
   { "command": "input.click", "parameters": { "entity": "<the JumpRow button's ID>" } }
   { "command": "play.step", "parameters": { "steps": 3 } }
   { "command": "input.key", "parameters": { "key": "K" } }
   { "command": "play.step", "parameters": { "steps": 3 } }
   ```

   `component.get` of the row text's `UIText` shows what it says.
   :::
   ::::

   **You should see:** "Press a control..." for the moment you wait, then `Key/K` in the row.

   **If you do not see it:** the text stays "Press a control..." for 5 s and then returns. No key arrived within the timeout.

:::::

::checkpoint{stage=5}

::figure{id=rebind-capturing}

## Add a name field

A name for the player, a code for a cheat, a message to a friend: all need text, and a button cannot give it. An **input field** is a widget the player types a line of text into. It shows a **Placeholder** while empty, and its **Character Limit** caps the length; 0 means no limit.

While the player edits the field, the keyboard belongs to the UI. The game's scripts read no keys while the player types, so typing a name never moves the character. Escape stops editing. Enter calls `OnUISubmit` on the field's scripts and on those of its event target, and the script reads what was typed with `GetUI().GetText()`. A field is one line: Strata has no multi-line field.

The script of this page is short.

```cpp src="book:tutorials/make/menus/NameField.cpp#L13-L20"
void OnUISubmit(Entity widget) override
{
	const std::string name = widget.GetUI().GetText();
	if (name.empty())
		return;
	NameLabel.GetUI().SetText("Player: " + name);
	UI::ClearFocus();
}
```

The function reads the text of the widget it receives, ignores an empty name, puts the name on the HUD and clears the focus, which stops editing.

:::::steps

1. Add an input field to the course's HUD canvas and a text for the result. Without a HUD, make a canvas `HUD`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select the HUD, press **+**, choose **UI**, then `Input Field` and rename it `NameInput`. Select its `Placeholder` child and set its text to `Your name`, then set the field's **Character Limit** to 12. Add a `Text` named `NameLabel`.
   :::
   :::tab[With a command]
   This step has no menu or button: run `ui.create` with the type `inputField` and the `text` `Your name`, then `component.set` with `CharacterLimit` set to 12.
   :::
   ::::

   **You should see:** the field with the words "Your name" in it.

   **If you do not see it:** the placeholder is empty text. Type it in its element.

2. Attach `NameField` to the HUD canvas and set `NameLabel`, and set the field's event target to the canvas. Enable **Receives Input** for the canvas that holds the field.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Use **Add Component ▸ Script**, and set **Event Target** of **UI Input Field**.
   :::
   :::tab[With a command]
   This step has no menu or button: run `script.add` and `component.set`.
   :::
   ::::

   **You should see:** the script on the entity.

   **If you do not see it:** the field never takes a click. Its canvas has **Receives Input** off, as the HUD's has by design.

3. Play, click the field, type `Ana` and press **Enter**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Play**, click the field and type the name.
   :::
   :::tab[With a command]
   This step has no menu or button: click the field, type, and press **Enter**.

   ```json
   { "command": "input.click", "parameters": { "entity": "<the NameInput field's ID>" } }
   { "command": "play.step", "parameters": { "steps": 3 } }
   { "command": "input.type", "parameters": { "text": "Ana" } }
   { "command": "play.step", "parameters": { "steps": 2 } }
   { "command": "input.key", "parameters": { "key": "Enter" } }
   { "command": "play.step", "parameters": { "steps": 3 } }
   ```

   :::
   ::::

   **You should see:** `Player: Ana` in the label.

   **If you do not see it:** the label stays empty. Enter was never pressed in the field.

:::::

::checkpoint{stage=6}

::figure{id=name-shown}

## Add credits and a sign

Credits scroll. A **mask** keeps the children of an element inside its rectangle; what it hides is not drawn and not clicked. The credits text sits inside a masked panel and moves up each frame.

The movement runs on unscaled time, like the rest of the menu, so credits shown from a paused game keep moving. The code moves the text by its speed times the unscaled delta. At 45 canvas units per second a text 900 units tall that starts at the mask's bottom edge at 360 leaves the top after (360 + 900) / 45 = 28 s, and starts again.

```cpp src="book:tutorials/make/menus/Credits.cpp#L13-L23"
void OnUpdate(float) override
{
	if (!Content.IsValid())
		return;
	glm::vec2 position = Content.GetProperty<glm::vec2>("UIRect", "Position").value_or(glm::vec2(0.0f));
	const float height = Content.GetProperty<glm::vec2>("UIRect", "Size").value_or(glm::vec2(0.0f)).y;
	position.y -= Speed * Time::GetUnscaledDeltaTime();
	if (position.y < -height)
		position.y = ViewHeight;
	Content.SetProperty("UIRect", "Position", position);
}
```

1. **Lines 17-18:** the text's position and height are read from its rectangle.
2. **Line 19:** a smaller y moves the text up.
3. **Lines 20-21:** when the whole text has left, it jumps back below the mask.

:::::steps

1. Add a panel `CreditsPanel` to the main menu with a **UI Mask**, and a text `CreditsText` inside it with your credits.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Add the panel and the text as before. Select the panel and use **Add Component ▸ UI Mask**. Attach `Credits` to the canvas and set `Content` to the text.
   :::
   :::tab[With a command]
   This step has no menu or button: run `ui.create`, `component.add` of `UIMask` and `script.add`.
   :::
   ::::

   **You should see:** the credits scroll upward inside the panel and nothing outside it.

   **If you do not see it:** the text spills over the panel. The mask is on the wrong element.

2. Add a sign in the course: a world-space canvas on a wall, with a button that the player clicks through the game camera.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Add a canvas `Sign`, set its **Render Mode** to **World Space** and place it with the move tool in the Scene view. Add a button under it.
   :::
   :::tab[With a command]
   This step has no menu or button: run `ui.create`, then `component.set` on the canvas with `RenderMode` set to `WorldSpace` and on its `Transform`.
   :::
   ::::

   **You should see:** a sign in the world with its button.

   **If you do not see it:** you cannot lay the sign out in the 2D canvas mode, which edits screen-space canvases only. Lay it out in the viewport, or turn the canvas to Screen Space while you build it.

:::::

A world canvas draws a canvas unit as 0.01 m by default, so a sign of 400 by 200 units is 4 by 2 metres. The player clicks it with the mouse when the cursor is free. Strata hits the button through the game camera's ray.

Game UI has no scroll views, so a mask clips a scrolling list that you move yourself. It has no drop-downs, no rich text and no multi-line fields. A menu's texts are the strings its elements hold, in one language, written left to right: there is no translation and no right-to-left text. [What Strata does not have](../appendix/not-in-strata.md) lists these and more.

::checkpoint{stage=7}

::figure{id=credits-sign}

## Summary

- A widget calls the scripts on its own entity and then those on its event target, before the frame's update, so one script handles a whole menu.
- A menu with a keyboard or a gamepad needs a First Selected element or a `Focus()` call when it opens, because the first press only focuses.
- A pause menu sets the time scale to 0, frees the cursor, focuses Resume and sits on a canvas with a higher Sort Order, and its animations use unscaled time.
- A settings screen sets values from code without events, and a toggle group acts only on a value of 1.
- A rebinding screen listens with binding capture, stops after a timeout, saves the bindings when it closes and offers a reset.

## Check yourself

1. Ten buttons have the same event target, an entity that holds `MainMenu`. A player clicks the button `Quit`. Which scripts get `OnUIClick`, and in what order?

   :::answer{tests="event-routing"}
   The scripts on the `Quit` button's own entity come first, and then those on the event target, `MainMenu`. Both run before the frame's `OnUpdate`. `MainMenu` tells the button by its name.
   :::

2. A gamepad player starts your menu and presses Submit once. Nothing is clicked. Why, and what do you change?

   :::answer{tests="navigation"}
   With nothing focused, the first press only focuses. Strata puts the focus on the canvas's First Selected, or else on the top-left selectable. Set First Selected, or call `Focus()` on the first button when the menu opens, and the first Submit clicks it.
   :::

3. The pause panel fades in over 0.25 s, driven by `Time::GetDeltaTime()`. How long does it take at time scale 0, and what do you read instead?

   :::answer{tests="pause-menu"}
   The fade never finishes: the delta is 0 at scale 0. Read `Time::GetUnscaledDeltaTime()`, and the fade takes 0.25 s at any scale. The pause canvas also needs a higher Sort Order than the HUD's.
   :::

4. A script acts on every `OnUIValueChanged` of the window-mode toggles. The player turns `Borderless` on while Windowed is on. What goes wrong?

   :::answer{tests="settings-screen"}
   Strata turns Windowed off first and raises a 0 for it; the script acts on that, too, and asks for Windowed, then `Borderless`. The window ends right only because the later request replaces the earlier one, and any other work for a mode runs twice. Act only when the value is 1.
   :::

5. A rebinding row shows "Press a control..." and never changes. Name two causes.

   :::answer{tests="rebind-screen"}
   The row's text returns after the timeout, so the update never ends the capture. Either the script's `OnUpdate` does not run, so `PollBindingCapture` is never called, or `Timeout Seconds` is far too large.
   :::

## Exercises

1. **Basic.** Add a Back button to the settings screen that closes it and returns the focus to the button that opened it. Hint: the panel is hidden with `SetActive(false)`.

   :::answer[Worked solution]{tests="settings-screen" solution="tutorials/make/menus/exercise-1.tutorial.json"}
   Add a button `Back` to the panel's layout, with the panel as its event target. Give `SettingsMenu` a field `OpenedFrom` holding the Settings button. In `OnUIClick`, when the name is `Back`, call `GetEntity().SetActive(false)` and `OpenedFrom.GetUI().Focus()`. Players on a gamepad then land where they started.
   :::

2. **Medium.** Make Quit ask first: a panel with `Yes` and `No`. The `No` button takes the focus when the panel opens, and the UI map's Cancel closes it.

   :::answer{tests="navigation,event-routing"}
   Show the panel and call `Focus()` on `No`, in `OnUIClick` for `Quit`. In `OnUpdate`, when the panel is open and `UI::IsActionPressed(UIAction::Cancel)` is true, hide the panel and focus `Quit`. The UI raises no event for Cancel, so the script asks.
   :::

3. **Hard.** Add a Pause row to the rebinding screen. A player binds Pause to a key that is also Cancel. What happens to the key pressed during the capture?

   :::answer{tests="rebind-screen,pause-menu"}
   Nothing: during the capture no action sees a press, and the captured control stays hidden from actions until released. The press neither pauses nor cancels. The binding takes effect from the next frame.
   :::

## Where it lives in Strata

The script ABI's UI functions are in `StrataScriptCore/Include/StrataScript/UI.h`, and the binding functions in `StrataScriptCore/Include/StrataScript/Input.h`. The window functions are in `StrataScriptCore/Include/StrataScript/Game.h`. The widgets' components are in `Strata/src/Strata/GameUI/GameUIComponents.h`, and the code that moves the focus and dispatches the events in `Strata/src/Strata/GameUI/GameUISystem.cpp`.

The default bindings of the UI map are in `Strata/src/Strata/Input/InputActionSet.cpp`. The Third-Person sample's menus are in `Samples/ThirdPerson/Scripts/`. How widgets work inside is the subject of the User interface part.

## Further reading

- The engine's own manual, `Docs/Manual/GameUI.md` in the Strata release: the widgets in short form (beginner).
- The manuals of other engines describe the same widgets as selectable states and navigation graphs (intermediate).
