---
id: make/quality
title: "Graphics quality and options for players"
description: "Choose how your game smooths its edges and how much the renderer spends, then give players a Graphics row that keeps their choice."
kind: how-to
size: M
tracks: [G]
needs: [make/look, make/menus]
time: 60
learn:
  - id: choose-aa
    text: choose the anti-aliasing method and the TAA preset that suit a game's look
  - id: read-presets
    text: compare the four Graphics Quality presets and say what a preset changes and what it never changes
  - id: where-chosen
    text: find where the quality of a view or a run is chosen, and which choice wins
  - id: graphics-row
    text: build a Graphics row of four toggles that sets the preset and saves it
  - id: player-file
    text: explain where a player's choice is kept and why it hides the project's preset in the editor
since: 0.7.0
status: final
---

Your game draws edges and shadows, and players own machines of very different strength. By the end of this page you choose how the game smooths its edges, you choose how much the :term[renderer]{id=renderer} spends, and you let players choose too. Before you start:

- You have the project of [Menus and settings screens](./menus.md) with its settings screen working in play (volume, window mode and vsync). No download starts this page: open the project of that page's last checkpoint, Checkpoint 7. Its folder `Menus` holds the project file `CharactersCameras.stproj`, named after the page where the course began.
- You know the Post Process component and its effects ([Lighting](./lighting.md) and [Look](./look.md)).
- You can export the game and start it from a terminal ([Export](./export.md)).

## What you choose

A screen is a grid of squares. A slanted edge between a dark roof and a bright sky crosses squares only in part, yet each square can show one color, so the edge looks like a staircase. **Anti-aliasing** is any technique that hides those stairs by giving each edge pixel a color between its two sides.

A worked example shows the idea. Take a pixel that a black line covers for 3 eighths of its area, on a white background. If the pixel is drawn black or white, the edge is a stair. A pixel that is 3 eighths black is 37.5 % gray: it has 62.5 % of white's brightness. Every method below tries to reach that gray, and they differ in how.

Strata offers three methods, set on the Post Process component:

- **Fast approximate anti-aliasing** (FXAA) looks at one finished frame, finds edges and blurs along them. It costs little and never trails behind moving things. Thin details such as wires still flicker.
- **Morphological** looks at one frame too. It finds the stair shape of each edge, rebuilds the straight line the stairs stand for and gives each pixel along the line its true share of color. Pixels away from edges stay exactly as drawn.
- **Temporal anti-aliasing** (TAA) moves the picture by a fraction of a pixel in every frame, in eight positions in turn, and blends the frame with the frames before it. The black line above covers the pixel in 3 of the 8 positions, so the blend settles at 3 eighths. TAA steadies thin detail, and fast motion can leave faint trails.

The other half of this page is about cost. A **Graphics Quality preset** is a named set of cost settings, such as shadow detail, how many lights cast shadows and how finely reflections are traced. A preset decides how much the renderer spends on a scene. The presets are Low, Medium, High (the default) and **Ultra**, and a fifth, Custom, holds values you set one by one.

:::why
A preset changes what the renderer spends, never what a scene stores: the lights, the Post Process and the sky stay yours. Strata keeps the look (a scene) apart from the cost (a machine), so one scene serves every player.
:::

## What the presets change

The presets differ in cost rows. Here is how they compare, in words and in counts of lamps:

| Setting | Low | Medium | High | **Ultra** |
| --- | --- | --- | --- | --- |
| Sun shadow detail | small maps, three cascades | larger maps, four cascades | fine maps, five cascades | the finest maps |
| Lamps with shadows | 4 | 16 | 64 | 256, larger tiles |
| Lamp shadows drawn each frame | 12 | 12 | 24 | 48 |
| Ambient occlusion samples | fewest | more | more still | most |
| Screen-space reflections | off | half resolution (needs TAA) | every pixel | every pixel, longer rays |
| Global illumination | off | off | on, when the scene asks | on, when the scene asks |

Two rules help. A row can switch a feature off at a low preset, so a scene that asks for reflections shows none at the lowest. Memory grows with the resolution: a view at 3840 by 2160 has 4 times the pixels of one at 1920 by 1080, so the same preset costs far more memory on a large screen.

:::why
Strata has no render scale. A render scale draws the picture smaller and stretches it, which is softer and smears in motion, so no setting trades sharpness for speed. To spend less, lower the presets' costs, such as shadows, lights and detail ([Quality settings](../image/quality-settings.md)).
:::

## What Strata does not do here

- No command sets a player's options. The only command in this area, `graphics.resetPlayerOptions`, deletes them.
- No `MSAA` (a method that stores several samples in each pixel) and no supersampling, which would draw above the screen's resolution. FXAA, Morphological and TAA smooth the edges instead.
- No high dynamic range display output. The back buffer is an 8-bit sRGB picture, so a game looks the same on every display.

A render scale slider is not hiding in the menus, and TAA on flat pixel art softens the art: choose FXAA, Morphological or no anti-aliasing there.

## Choose the anti-aliasing and the quality

:::::steps

1. Open the scene and select the entity with the Post Process component. Switch on anti-aliasing and choose a method.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the Inspector, switch **Anti Aliasing** on, then open **Anti Aliasing Method** and choose **FXAA**, **Morphological** or **TAA**.
   :::
   :::tab[With a command]

   ```json
   { "command": "scene.open", "parameters": { "scene": "Scenes/Main.stscene" } }
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "AntiAliasing": true, "AntiAliasingMethod": "Morphological" } } }
   ```

   A command takes an entity's identifier (ID), not its name: each `<the ID of …>` on this page is what `entity.find` returns for that name.
   :::
   ::::

   **You should see:** the method name in the field, and the edges of the Game view change a little.

   **If you do not see it:** the field is grey when **Anti Aliasing** is off. Switch it on first.

2. Choose a TAA preset. The presets matter only while the method is TAA.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **TAA** as the method, then open **TAA Preset** and choose **Sharp**, **Original** or **Custom**.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Post Process>", "component": "PostProcess", "values": { "AntiAliasingMethod": "TAA", "TAAPreset": "Original" } } }
   ```

   :::
   ::::

   **You should see:** the Inspector lists the TAA settings, grey unless the preset is **Custom**.

   **If you do not see it:** the TAA fields are grey for FXAA and Morphological. Choose TAA again.

   **Why:** Sharp, the default, crisps the picture and gives back detail that blending softens. Original is the first, softer TAA, and Custom sets every value yourself ([TAA](../image/taa.md)).

3. Compare the methods while things move. Move the camera, because a still frame hides the differences.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press Play and look at the Game view. Change **Anti Aliasing Method** in the Inspector while you pan the camera across thin detail.
   :::
   :::tab[With a command]
   Run `viewport.capture` once per method and compare the pictures.
   :::
   ::::

   **You should see:** TAA steadier on thin detail and in motion, FXAA and Morphological smooth but crawl a little, and TAA a little soft on a flat picture.

   **If you do not see it:** zoom in on the picture, or look at a wire, a fence or a distant branch. Wide, plain edges look alike under every method.

4. Open the presets. They live in the Project Settings window.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open **Project Settings ▸ Graphics Quality**.
   :::
   :::tab[With a command]
   Run `project.settings` with `{"section": "Renderer.Quality"}`.
   :::
   ::::

   **You should see:** a row of chips for Low, Medium, High and **Ultra**, with Custom beside them. Below them a table has one row per setting and one column per preset. It also shows the memory each preset needs and the time that the :term[graphics processing unit]{id=gpu} (GPU) needs now for the Scene view's shadows and meshes.

   **If you do not see it:** use the search of the settings window, or choose the **Renderer** group.

5. Choose a preset for the whole project. The page applies it at once and records an undo step.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click the chip of the preset you want: **Low** for an old laptop, **High** for a mid-range machine, **Ultra** for a large graphics card.
   :::
   :::tab[With a command]
   Run `project.setSettings` with `{"section": "Renderer.Quality", "value": {"Preset": "Low"}}`.
   :::
   ::::

   **You should see:** the chip stays lit, and the Game view draws with softer shadows at Low or finer ones at High.

   **If you do not see it:** in play, a saved player's choice replaces the project's preset (step 11). Reset it there.

6. Give the Scene view its own quality. Your computer may handle **Ultra** while the project says High.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open the quality chip in the top bar of the Scene view. **Project** follows the page; choose a preset to change this view alone.
   :::
   :::tab[With a command]
   Run `viewport.setSettings` with `{"quality": "ultra"}`.
   :::
   ::::

   **You should see:** the chip names your choice, and only the Scene view changes. The Game view stays at the game's quality.

   **If you do not see it:** the Scene view looking through the scene's camera draws as the game will, and its chip then names the game's preset.

7. Try the quality of one run of the exported game. This changes nothing that the game saves.

   ::::tabs{sync=how}
   :::tab[In the editor]
   This step has no menu or button: run the command.
   :::
   :::tab[With a command]
   Start the exported game from a terminal with an option:

   ```text
   <Game> --quality low
   ```

   :::
   ::::

   **You should see:** the game opens at Low, and its log has the line `Graphics quality: Low (--quality)`.

   **If you do not see it:** the option takes `low`, `medium`, `high` or `ultra`, never `custom`, and needs a window.

:::::

::figure{id=aa-compare variant=fxaa}

::figure{id=aa-compare variant=taa}

::figure{id=aa-compare variant=fxaa crop=seams}

::figure{id=aa-compare variant=taa crop=seams}

::figure{id=quality-compare variant=low}

::figure{id=quality-compare variant=high}

## Give players a Graphics row

The next steps put the choice in the players' hands. A **toggle group** is a row of toggles of which only one is on. When the player switches one on, the game switches the others off first, and each switch raises an event of its own.

<!-- markdownlint-disable MD029 -->
:::::steps

8. Add a row of four toggles to the settings screen, one per preset. Open `Scenes/MainMenu.stscene`, which holds the screen's :term[prefab]{id=prefab-make} `SettingsPanel`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Add a horizontal layout named `GraphicsRow` to `SettingsColumn`, as [Menus and settings screens](./menus.md) built its other rows. Add four toggles to it: `GraphicsLow`, `GraphicsMedium`, `GraphicsHigh` and `GraphicsUltra`, with the texts Low, Medium, High and Ultra. In each toggle's **UI Toggle**, choose `GraphicsRow` as **Group** and `SettingsPanel` as **Event Target**, and clear **Is On**.
   :::
   :::tab[With a command]

   ```json
   { "command": "scene.open", "parameters": { "scene": "Scenes/MainMenu.stscene" } }
   { "command": "ui.create", "parameters": { "type": "horizontalLayout", "name": "GraphicsRow", "parent": "<the ID of SettingsColumn>", "size": [480, 50] } }
   { "command": "ui.create", "parameters": { "type": "toggle", "name": "GraphicsLow", "parent": "<the ID of GraphicsRow>", "text": "Low", "size": [115, 50] } }
   { "command": "component.set", "parameters": { "entity": "<the ID of GraphicsLow>", "component": "UIToggle", "values": { "Group": "<the ID of GraphicsRow>", "EventTarget": "<the ID of SettingsPanel>", "IsOn": false } } }
   ```

   Send the last two lines again for `GraphicsMedium`, `GraphicsHigh` and `GraphicsUltra`. Each `ui.create` answers the new element's ID as `entity`.
   :::
   ::::

   **You should see:** a row of four toggles at the end of the settings column, all off.

   **If you do not see it:** the toggles overlap when they are not children of `GraphicsRow`. The row is a group of its own, because the window toggles already name `SettingsPanel` as their group.

9. Give the settings script the Graphics row. Copy `Scripts/SettingsMenu.cpp` from this page's download, in the box after the Result, over your own. It keeps every line of the Menus script and adds four `Entity` fields, `GraphicsLow` to `GraphicsUltra`, with the parts below.

   :::question
   Do `std::optional`, `override` or the call `x.f(` look strange? Read [Programming 1](../basics/programming-1.md), [Programming 3](../basics/programming-3.md), [C++ classes](../basics/cpp-classes.md) and [Modern C++](../basics/cpp-modern.md) first.
   :::

   The first part runs when a toggle changes. It tests whether the toggle is one of the row's and ignores the value 0.

   ```cpp src="book:tutorials/make/quality/SettingsMenu.cpp#L32-L43"
   void OnUIValueChanged(Entity widget, float value) override
   {
   	// The Graphics row is one toggle group: act only on the toggle that switched on.
   	if (const std::optional<QualityPreset> preset = GetGraphicsPreset(widget))
   	{
   		if (value == 0.0f)
   			return;
   		Graphics::SetPreset(*preset);
   		if (!Graphics::Save())
   			Log::Warn("The graphics options were not saved");
   		return;
   	}
   ```

   1. **Line 35:** `GetGraphicsPreset` returns the toggle's preset, or nothing for another widget.
   2. **Lines 37-38:** a toggle that its group switched off raises a 0, which the script ignores.
   3. **Lines 39-41:** `Graphics::SetPreset` sets the preset, and `Graphics::Save` keeps it for the next run.

   The helper compares the widget with the four fields.

   ```cpp src="book:tutorials/make/quality/SettingsMenu.cpp#L65-L79"
   // The preset of a Graphics toggle, or nothing for another widget.
   std::optional<QualityPreset> GetGraphicsPreset(Entity widget) const
   {
   	if (!widget.IsValid())
   		return std::nullopt;
   	if (widget == GraphicsLow)
   		return QualityPreset::Low;
   	if (widget == GraphicsMedium)
   		return QualityPreset::Medium;
   	if (widget == GraphicsHigh)
   		return QualityPreset::High;
   	if (widget == GraphicsUltra)
   		return QualityPreset::Ultra;
   	return std::nullopt;
   }
   ```

   1. **Lines 68-69:** an entity that is not valid has no preset.
   2. **Lines 70-77:** each field gives one of the four presets.

   The last part runs when the screen opens and switches on the toggle of the preset in effect. `Graphics::GetPreset` returns nothing for a Custom preset, so the code tests it before use.

   ```cpp src="book:tutorials/make/quality/SettingsMenu.cpp#L18-L30"
   void OnCreate() override
   {
   	// Values set from code raise no OnUIValueChanged, so showing the volume and the preset sets nothing.
   	if (VolumeSlider.IsValid())
   		VolumeSlider.GetUI().SetValue(Audio::GetMasterVolume());
   	// The preset in effect switches its toggle on; a Custom preset switches none on.
   	const std::optional<QualityPreset> preset = Graphics::GetPreset();
   	for (const Entity toggle : { GraphicsLow, GraphicsMedium, GraphicsHigh, GraphicsUltra })
   	{
   		if (toggle.IsValid())
   			toggle.GetUI().SetValue(preset && GetGraphicsPreset(toggle) == preset ? 1.0f : 0.0f);
   	}
   }
   ```

   1. **Line 24:** the preset in effect, from the project, the player's choice or `--quality`.
   2. **Lines 25-29:** each toggle is set on when its preset is the one in effect. A value set from code raises no event.

   **You should see:** your `Scripts/SettingsMenu.cpp` names `GraphicsLow` near its top, after `VolumeSlider`.

   **If you do not see it:** the file went to another folder. The download's `Scripts` folder matches your project's.

10. Build, fill the four fields of `SettingsMenu` on `SettingsPanel`, apply the panel to its prefab and save. Then play and click `GraphicsLow`.

    ::::tabs{sync=how}
    :::tab[In the editor]
    Press **Ctrl+B**. Select `SettingsPanel` and drag each toggle onto its field. In the `Overrides` menu choose **Apply All to Prefab**, so that the course's pause screen gets the row too, and save. Press **Play** and click **Low**.
    :::
    :::tab[With a command]

    ```json
    { "command": "script.build" }
    { "command": "script.setField", "parameters": { "entity": "<the ID of SettingsPanel>", "class": "SettingsMenu", "field": "GraphicsLow", "value": "<the ID of GraphicsLow>" } }
    { "command": "prefab.apply", "parameters": { "entity": "<the ID of SettingsPanel>" } }
    { "command": "scene.save" }
    { "command": "play.start", "parameters": { "paused": true, "build": false } }
    { "command": "play.step", "parameters": { "steps": 2 } }
    { "command": "input.click", "parameters": { "entity": "<the ID of GraphicsLow>", "wait": false } }
    { "command": "play.step", "parameters": { "steps": 3 } }
    ```

    Send the `script.setField` line for the other three fields too. `component.get` of each toggle's `UIToggle` shows its `IsOn`.
    :::
    ::::

    **You should see:** at the start `GraphicsHigh` is on, the project's preset. After the click `GraphicsLow` is on and the others are off, and the game draws with Low from the next frame.

    **If you do not see it:** look in the editor's log for a script build error. Without the `value == 0.0f` test, the switched-off toggles undo the player's click.

    An anti-aliasing choice works the same way. A button's handler calls `Graphics::Set` with the name `AntiAliasing` and a choice, then `Graphics::Save`:

    ```cpp pseudocode
    Graphics::Set("AntiAliasing", "FXAA");
    Graphics::Save();
    ```

    The choice names are `Scene`, `Off`, `FXAA`, `TAA` and `Morphological`, and `Scene` keeps the method of the Post Process. `Set` returns false and logs a message when a name is wrong.

11. Check what the game kept, then reset it. Stop the game and look in the project's `.strata/Saves` folder.

    ::::tabs{sync=how}
    :::tab[In the editor]
    Press **Stop**. Open **Project Settings ▸ Graphics Quality** again. A banner names the saved choices; click **Reset Player Options**.
    :::
    :::tab[With a command]

    ```json
    { "command": "play.stop" }
    { "command": "graphics.resetPlayerOptions" }
    ```

    :::
    ::::

    **You should see:** a file `GraphicsOptions.json` appeared after the click, and vanished after the reset. The banner is gone. The command answers `reset` with the one choice the click saved, and a second reset answers an empty list.

    **If you do not see it:** `Graphics::Save` returns false when the game has nowhere to keep files. Check the :term[return value]{id=return-value}.

:::::
<!-- markdownlint-enable MD029 -->

## Result

Your settings screen has a Graphics row that works in the exported game: a click switches the preset from the next frame, and the game keeps it for the next run. The project's own choices (the anti-aliasing method, the preset) remain the defaults of every player who has chosen nothing.

The project's preset is the chip you chose on the Graphics Quality page in step 5. The drawing shows that page with some of its rows.

::figure{id=graphics-page-drawing}

Three layers decide the quality in effect, and the later one wins.

```mermaid caption="The project's preset is the base, a saved player's choice replaces it, and the command line replaces both for one run." alt="Three boxes in a row. The project's Graphics Quality is followed by the player's saved options and then by the command line option, with arrows pointing to the quality in effect."
flowchart LR
  A[Project Settings: Graphics Quality] --> D[Quality in effect]
  B[Player's GraphicsOptions.json] --> D
  C[--quality on the command line] --> D
```

The file sits beside the game's saves. In the editor that folder is the project's `.strata/Saves`. Only the engine's graphics service reads and writes it, so your script never opens it.

## Variations

- **A Custom preset, one row at a time.** In the table, edit a value of the Custom column. The page switches to Custom and starts from the values the column shows. Choose a preset again and your Custom values wait for later. From a script, `Graphics::Set("ShadowCascades", 3)` does the same: the preset becomes Custom, starting from the values in effect.
- **A full options screen.** `Graphics::Options()` returns each setting with a title, a description and its list of choices, and `Graphics::FindOption("name")` finds one by name. Build a row for each setting of that list.
- **Players' rows only.** Anti-aliasing, motion blur, depth of field, film grain and chromatic aberration are the players' own rows, and every preset leaves them alone. Anti-aliasing offers every method; for the other four, a player may only remove an effect the scene already uses, never add one the scene lacks.

## Summary

- Choose TAA Sharp for thin detail and moving cameras; choose FXAA, Morphological or none for flat colors and pixel art.
- A preset (Low, Medium, High, **Ultra**, Custom) changes what the renderer spends and never what a scene stores.
- The project's page, the Scene view's chip and `--quality` set the quality for a project, a view and a run.
- A Graphics row is one :term[toggle group]{id=toggle-group} whose handler ignores switched-off toggles, calls `Graphics::SetPreset` and then `Graphics::Save`.
- A player's saved options sit in `GraphicsOptions.json` and replace the project's preset until **Reset Player Options** deletes them.

## Check yourself

1. A game of flat-colored blocks has a soft look under TAA. Which method do you choose, and why?

   :::answer{tests="choose-aa"}
   FXAA or Morphological, or none. TAA blends each frame with earlier ones and softens crisp pixels. The two single-frame methods touch only the pixels along edges.
   :::

2. You set the project's preset to Low, yet the Game view in the editor still draws at **Ultra**. Name two causes.

   :::answer{tests="where-chosen,player-file"}
   A saved player's choice replaces the project's preset in play, so open the Graphics Quality page and click **Reset Player Options**. The Scene view's chip may also hold an own preset, but that changes the Scene view only. Search for the banner first.
   :::

3. What does a preset never change?

   :::answer{tests="read-presets"}
   The settings a scene holds: the lights, the Post Process and the sky stay as they are. A preset decides only how finely they are drawn, and it may omit a costly effect, such as reflections at Low.
   :::

4. A toggle group raises two events when a player clicks a toggle. What breaks if the handler acts on both?

   :::answer{tests="graphics-row"}
   The old toggle's event has value 0. Acting on it sets a preset and switches the toggle off again, so the click is undone. The handler returns when the value is 0.
   :::

5. Name the three places that choose the quality, and which wins in the exported game.

   :::answer{tests="where-chosen"}
   The project's preset, a player's saved options and `--quality`. The command line wins for its run, a saved choice then replaces the project's, and the project is last.
   :::

## Exercises

1. **Basic.** A player says the game looks "too soft" with TAA on a calm scene. Which TAA preset do you try first?

   :::answer[Worked solution]{tests="choose-aa"}
   Sharp, if it is not set. Original is softer, and Sharp restores detail by sharpening the displayed image. If it is already Sharp, try FXAA.
   :::

2. **Medium.** Open the Physics Playground and compare the anti-aliasing of its floor under Off, FXAA, Morphological and TAA. Do it with commands and note which one changes the floor's far edge most.

   :::answer[Worked solution]{tests="choose-aa" solution="tutorials/make/quality/exercise-2.tutorial.json"}
   Select the **Post Process** entity and run `component.set` once per method, with a `viewport.capture` after each. The file sets and checks the four in that order; it leaves the captures to you, as they need a GPU. Off shows full stairs, FXAA and Morphological smooth them, and TAA is steadiest while you pan.
   :::

3. **Hard.** Add a **Reset Graphics** button to your settings screen. It should return the player to the project's quality.

   :::answer[Worked solution]{tests="graphics-row,player-file"}
   In the button's click handler, call `Graphics::Reset()` with no name, then `Graphics::Save()`, then show `Graphics::GetPreset()` again. `Reset` removes the player's choices, so the project's values apply from the next frame.
   :::

## Where it lives in Strata

- The page: `StrataEditor/src/UI/GraphicsQualityPage.cpp`.
- The presets: `Strata/src/Strata/Renderer/RendererQuality.cpp`.
- The script functions: `StrataScriptCore/Include/StrataScript/Graphics.h`.
- The options file's service: `Strata/src/Strata/Runtime/GameGraphicsService.cpp`.
- The sample row: `Samples/ThirdPerson/Scripts/SettingsMenu.cpp`.

## Further reading

- The manual's anti-aliasing and graphics chapters: what each method and setting costs (beginner).
- Temporal anti-aliasing in game engines: the idea of jitter and history (advanced).
