---
id: make/levels-saves
title: "Levels, loading screens and save files"
description: "Split the course into levels with a main menu, show a loading bar, load a room beside a level and keep a best time, settings and a checkpoint between runs."
kind: how-to
size: L
tracks: [G]
needs: [make/menus]
time: 90
learn:
  - id: split-scenes
    text: explain how a game is a set of scenes and why no entity survives a scene switch
  - id: pass-state
    text: choose between a scene field, module state and a save file for what must last longer than a scene
  - id: loading-bar
    text: build a loading bar from the progress of a scene switch
  - id: additive-room
    text: write a script that loads a room beside a level, shows its progress and unloads it
  - id: keep-progress
    text: write code that saves and reads back a best time and a checkpoint and survives a damaged file
since: 0.3.0
status: final
---

You turn the course of [Menus](menus.md) into a game of several scenes: a second level, a loading bar and a room that loads beside a level. A player also keeps a best time, settings and a checkpoint between runs. Before you start:

- You have the end of [Menus](menus.md): the course with its main menu, pause menu, settings screen, rebinding screen and name field. Continue your own project, or download Checkpoint 7 at the end of [Add credits and a sign](menus.md#add-credits-and-a-sign) and open it.
- You can put a scene in a :term[script field]{id=script-field}, as [Script fields](script-fields.md) shows, and you know the project folder and its hidden `.strata` folder from [Projects, saving, undo and recovery](project-files.md).
- You have about an hour and a half.

This page offers no downloads of its own: each step says what to make, in the editor or with commands, and gives the code.

## How a game moves between scenes

A game you play has more than one place: a title screen, a level, perhaps a second level and a loading screen between them. Strata makes each place a **scene**: a file that holds entities and what they carry. The main menu is a scene, every level is a scene, and the game is the moves between them.

A script moves the game with `Game::LoadScene`. You give it a scene, as an :term[asset handle]{id=asset-handle} that a field holds or as a path, and the engine does three things. It loads the new scene and everything it uses in the background while the current scene continues. When all is in, it swaps the two between frames: every entity of the old scene goes away, its scripts receive `OnDestroy`, and the new scene starts. A call returns false when the asset is not a scene.

Because the old scene keeps running while the new one loads, a script may ask again in every update while a condition holds. Asking again for the scene that is loading changes nothing. A request for another scene replaces the first one. `Game::Quit` ends the game, and it wins over a switch: an exported game exits with the code you give, and the editor stops play mode.

Both take effect after the frame's update, so the lines after the call still run. A script that calls `Game::LoadScene` and then moves an entity moves an entity of the scene that is about to go away.

:::rule
Entities do not survive `Game::LoadScene`. Anything that must last longer than a scene goes into the next scene's fields, into module state, or into a save file. The engine destroys the old scene as a whole, so no script can keep a reference to an entity that no longer exists.
:::

Three places hold what must last longer than a scene, and each lasts a different time. A field of the next scene's script holds a choice you make in the editor, such as which level comes next. Module state, explained below, holds what the scripts of one run share. A save file, explained after it, stays after the game ends.

The Third-Person sample is a good picture of the flow. Its main menu starts the course when the player presses play. After ten seconds without input, the main menu starts the **attract mode**: the course plays itself as a show, until the player touches anything and the game returns to the menu. The course has a pause menu and a completion panel with two buttons, one that starts it again and one that returns to the menu.

```mermaid caption="The scenes of the Third-Person sample and the moves between them. Module state sits beside them and stays while the scenes change." alt="A flow chart with the main menu, a loading scene and the course. The main menu leads to the course when the player starts, and after ten idle seconds as the attract mode. The course returns to the menu when the player finishes, and starts again from its own completion panel. A box named module state is joined to the menu and the course."
flowchart LR
  M[Main menu] -->|Play| C[Course]
  M -->|10 s idle: attract mode| C
  C -->|menu button| M
  C -->|play again| C
  S[(Module state: settings, attract mode)] --- M
  S --- C
```

The rest of the page builds the same shape in the course, one piece at a time. Play in the editor runs a copy of the scene that is open, not the main menu, so playing the course skips the menu and the module state that the menu sets. To test a flow, open the main menu scene first.

## Module state

Scripts are code, and code can hold variables of its own. A variable declared at :term[namespace]{id=namespace} scope in a :term[script module]{id=script-module} belongs to the module, not to any entity. The scenes come and go, and the module stays loaded, so the variable keeps its value. The sample's header says so in its first lines.

```cpp src="Samples/ThirdPerson/Scripts/ThirdPerson.h#L1-L5"
#pragma once

// What the sample's scripts share across its scenes. The script module stays loaded while the game switches scenes
// (Game::LoadScene), so the main menu tells the course through it that the course runs as the attract mode's demo, and
// the settings are read from their save file once and kept here.
```

The sample puts its variables in a namespace without a name of one `.cpp` file and gives the other files functions to reach them. The header only declares those functions.

```cpp src="Samples/ThirdPerson/Scripts/ThirdPerson.cpp#L15-L21"
namespace
{

	GameSettings s_Settings;
	bool s_SettingsRead = false;
	bool s_DisplayApplied = false;
	bool s_AttractMode = false;
```

Here is why the variables live in the `.cpp` file. If you wrote `GameSettings s_Settings;` in a header that two `.cpp` files include, each file would define it once and the build would fail at the link step. If you added `static`, every file would get a copy of its own, so the menu would change one copy and the course would read another, with no warning at all. One definition and a function that returns it is the way that works.

How long does such a variable live? As long as the module's library stays loaded. In the editor that is from the first build until the project closes, so a score or a flag such as `s_SettingsRead` survives **Stop** and **Play**. Every :term[hot reload]{id=hot-reload} and every reload after a crash loads a new library, and the variables start over. An exported game starts them fresh at each run.

A player never sees the difference. You do, when a test passes only because the flag kept a value from your last Play.

:::why
Module state is plain C++ and costs nothing to read, so the sample keeps its settings and its attract-mode flag there. It is not saved to the disk. A value that must survive the end of the game belongs in a save file.
:::

## Save files

A **save file** is a named file of bytes in the game's save folder that a script writes and reads with `Game`. In the editor the folder is `.strata/Saves` inside the project. On the disk the file's name ends in `.save` after the name you gave: `best-time.txt` is the file `best-time.txt.save`. In an exported game it is `Saves` in the user data folder, under a folder named after the project's name, not its title, so a rename of the title keeps every player's saves. Both folders are hidden from a player's normal view, and your game never needs a path: it works with names.

A name has 1 to 64 characters: letters of the English alphabet, digits, spaces, `-`, `_` and `.`. No dot or space stands at the start or the end, no `..` inside, and no device name that Windows keeps, such as `CON`, is allowed. `best-time.txt`, `Slot 1` and `settings.json` are good names. A bad name makes the call fail, so check what `WriteSaveFile` returns.

The four calls you need:

| Call | What it does |
| --- | --- |
| `Game::WriteSaveFile(name, text)` | Replaces the whole file; false when the write failed |
| `Game::ReadSaveText(name)` | The text, or an empty `std::optional` when there is no such file yet |
| `Game::ListSaveFiles()` | The names of the files, sorted |
| `Game::DeleteSaveFile(name)` | Removes a file; false when it was not there |

A write never leaves half a file, and it waits for the disk before it returns. A game that writes on every frame would slow, so it saves at quiet moments: at a checkpoint, when a menu closes, when a level ends.

A save file holds text, and you choose its shape. The simplest shape is one value per line. `std::to_string` turns a number into text, and `std::stoi` turns text back into a number.

The second call has a trap. A file can be missing, damaged by a crash, or edited by a player, and `std::stoi` throws an exception on text that is no number. An exception that leaves a script turns the script off. So the code must check the text before it converts.

:::question
What is a `std::optional`, and what does `if` do with one? [Modern C++ features](../basics/cpp-modern.md) explains it.
:::

Here is the page's own code, which the steps below use. It reads a whole number that may be negative from a text and gives back nothing for anything else.

```pseudocode
std::optional<int> ParseWhole(const std::string& text)
{
	const size_t start = (!text.empty() && text[0] == '-') ? 1 : 0;
	const size_t digits = text.size() - start;
	if (digits < 1 || digits > 9)
		return std::nullopt;
	for (size_t i = start; i < text.size(); i++)
		if (text[i] < '0' || text[i] > '9')
			return std::nullopt;
	return std::stoi(text);
}
```

1. **Line 3:** a leading minus sign is allowed, so `start` is 1 for such a text and 0 for any other.
2. **Lines 5–6:** an empty text, or one of more than nine digits, ends here with no number.
3. **Lines 7–9:** a character that is no digit ends the function too.
4. **Line 10:** only text that passed every test reaches `std::stoi`, which cannot throw now.

The limit of 9 digits keeps the number inside the range of an `int`, which `std::stoi` needs; ten digits could pass the check and still throw. Take the text "1250": it has four digits, all between 0 and 9, so the function returns 1250. The text "12a" returns nothing at the letter, and the empty text returns nothing at the first test. A function that cannot throw is worth more than one that is short.

The sample's course reads its best time with `std::strtof` and checks where the number ended and its range, which is the same idea with a decimal number.

## A loading bar

:::question
What do `override` and `public` mean in a :term[script class]{id=script-class}? [Classes and inheritance](../basics/cpp-classes.md) explains them.
:::

A switch can take a while: the new scene and every mesh, material and texture it uses must load. `Game::GetSceneLoadProgress` tells how far it has come, from 0 to 1, and a negative number when no switch is under way. A script turns that number into a bar and a text. The sample's loading screen does it in one script.

```cpp src="Samples/ThirdPerson/Scripts/LoadingScreen.cpp#L18-L27" symbol="LoadingScreen::OnUpdate"
void OnUpdate(float) override
{
	const float progress = Game::GetSceneLoadProgress();
	if (progress < 0.0f)
		return; // Nothing loads (yet)
	if (Bar.IsValid())
		Bar.SetProperty("UIImage", "FillAmount", std::clamp(progress, 0.0f, 1.0f));
	if (Label.IsValid())
		Label.GetUI().SetText("Loading... " + std::to_string(static_cast<int32_t>(std::lround(progress * 100.0f))) + "%");
}
```

1. **Line 20:** the progress is negative while no switch is under way.
2. **Lines 21–22:** the script does nothing then, so the bar keeps its last look.
3. **Lines 23–24:** `std::clamp` keeps the fill between 0 and 1.
4. **Line 26:** the label shows the progress as a whole percentage.

The bar is an image of the type **Filled**, as in [the tutorial of the heads-up display](hud.md), and the script sets its `FillAmount`. The text shows the progress as a whole percentage.

How fast the bar fills is not up to the script. The engine moves data to the :term[graphics card]{id=gpu} in steps that a frame's budgets limit, and a game cannot raise them for a loading screen. [Uploads](../assets/uploads.md) explains the budgets and the limit on staging memory.

The project can also name a **loading scene**: a scene that an exported game plays while its :term[start scene]{id=start-scene} loads. It is for the first load only. Between two levels the bar belongs to the scene that is playing, because that scene continues while the next one loads. The loading scene is not shown between levels.

## Rooms that load beside a level

A level does not have to be one scene. A **sub-scene (additive load)** is a scene asset that a script loads into the playing scene next to what is there. The call that loads it is `Scene::LoadAdditive`, and the loading is an additive load. A room behind a door, a boss area and a far part of a map are good uses.

The call starts the load and returns a `SubScene` at once, with the entities appearing over the next frames, a few each frame. `SubScene::IsLoaded` is true when all of them exist. `Assets::GetLoadProgress` of the room's asset shows how much has loaded, from 0 to 1. Its first call also starts the loading, so a door can ask early and the room is ready when the player arrives.

`SubScene::Unload` takes the room out. Its entities go inactive at once, so nothing draws, updates or simulates them, and the engine destroys them over the following frames. Each entity keeps the identity it has in the file, so loading the same room twice fails, and loading it again after an unload waits until the old entities are gone.

What Strata does not do here. The editor edits one scene at a time, together with the loaded cells of a world, so you do not see a sub-scene in the editor before you play. Additive loads work in play mode only. [Sub-scenes](../world/sub-scenes.md) explains the loader's states and the frame's work budget.

## A checkpoint file

A checkpoint keeps the place the player reached and the coins collected there. A position has three numbers, so the file needs four values, one per line. A value that holds a decimal point is a risk for the reader, so the code writes the position in whole centimetres.

Take a player at the position 12.5, 0.4 and -3.1 metres with 7 coins. Multiplied by 100 and rounded, the position is 1250, 40 and -310, and the file holds the text `1250`, `40`, `-310` and `7` on four lines. Reading divides by 100 again and gets the same position back, because rounding to a centimetre moves a place by half a centimetre at most.

```pseudocode
void SaveCheckpoint(const glm::vec3& position, int coins)
{
	const glm::ivec3 cm = glm::ivec3(glm::round(position * 100.0f));
	Game::WriteSaveFile("checkpoint.txt", std::to_string(cm.x) + "\n" + std::to_string(cm.y) + "\n" + std::to_string(cm.z) + "\n" + std::to_string(coins));
}
```

The writer joins the four numbers with line ends. The reader must take the lines apart again, and it must treat every kind of damage as no checkpoint at all.

```pseudocode
std::optional<glm::vec3> ReadCheckpoint(int& coins)
{
	const std::optional<std::string> text = Game::ReadSaveText("checkpoint.txt");
	if (!text.has_value())
		return std::nullopt;
	int values[4];
	size_t start = 0;
	for (int i = 0; i < 4; i++)
	{
		const size_t end = text->find('\n', start);
		if (end == std::string::npos && i < 3)
			return std::nullopt;
		const std::optional<int> value = ParseWhole(text->substr(start, end - start));
		if (!value.has_value())
			return std::nullopt;
		values[i] = *value;
		start = end + 1;
	}
	coins = values[3];
	return glm::vec3(values[0], values[1], values[2]) / 100.0f;
}
```

1. **Lines 3–5:** a missing file is the normal case on the first run, so the function says nothing, and the game starts at the beginning.
2. **Lines 8–12:** the loop finds the end of each line; a text with fewer than four lines fails here.
3. **Lines 13–15:** every line passes the check of `ParseWhole`, so no line can throw.
4. **Lines 19–20:** the coins and the position come out only when all four lines were good.

The caller moves the player there with `Teleport` of the player's `CharacterController` after it reads a position, never by writing its transform, as [Characters and cameras](characters-cameras.md) explains. In a world, the player must also stay in the saved scene with its streaming source, and the cells around the restored position must load before the player stands there. A world starts with the cells around its sources as the scene was saved, so a restored player would fall through ground that is not there yet. [Large worlds](large-worlds.md) shows how a script asks for the cells first.

## Settings that last

The settings of the menu need the same care, and one more. A slider reports a new value on many frames while a player drags it, and every write waits for the disk. Writing at each report would pause the game for the length of a drag. The sample marks a save as pending, notes the real time of the change, and writes once the slider has rested for 0.4 seconds.

```cpp src="Samples/ThirdPerson/Scripts/SettingsMenu.cpp#L14-L18"
void SettingsMenu::OnUpdate(float)
{
	if (m_SavePending && Time::GetRealTime() - m_LastChange >= static_cast<double>(SaveDelaySeconds))
		Save(false);
}
```

Every update, the menu checks whether a save is pending and whether the last change is old enough. Only then does it write the file.

The settings live in module state and are read once. The first call of `GetSettings` reads the file and parses what it holds. A file that is missing leaves the defaults, and every later call returns the value in memory.

```cpp src="Samples/ThirdPerson/Scripts/ThirdPerson.cpp#L68-L77" symbol="ThirdPerson::GetSettings"
GameSettings& GetSettings()
{
	if (!s_SettingsRead)
	{
		s_SettingsRead = true;
		if (const std::optional<std::string> text = Game::ReadSaveText(c_SettingsFile))
			s_Settings = ParseSettings(*text);
	}
	return s_Settings;
}
```

1. **Lines 70–72:** only the first call continues to read the file; the flag is set before the read.
2. **Lines 73–74:** a file that exists is parsed; with none, the settings keep their defaults.
3. **Line 76:** every call returns the same variable, so the menu and the course share it.

The rebinding screen of [Menus](menus.md) needs no such code, because the engine keeps the players' bindings itself.

## Build it

You make the changes in this order, one goal at a time. Each step gives the editor path and the command, and the code you write sits in the script's file in `Scripts/` of the project. After a code change, build and load the scripts as you did in [Script fields](script-fields.md): in the editor the **Play** button rebuilds changed sources for you.

:::::steps

1. Give the course a goal, and the player a tag. The course of [Menus](menus.md) has no goal yet: a box at the far end that the player walks through. A script can only tell the player from a crate by something the player carries, so give it the tag `Player`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open `Scenes/Main.stscene`. Create an empty entity `Goal` at the position (0, 1, -8) with the scale (2, 2, 2). Add a **Mesh Renderer** with the mesh `Builtin/Cube`, a **Box Collider**, and a **Rigid Body** with **Type** Static and **Is Trigger** on. Select `Player`, choose **Add Component ▸ Tag** and type `Player`. Save with **Ctrl+S**.
   :::
   :::tab[With a command]
   The tag needs the player's identifier (ID), which `entity.find` with the name `Player` returns.

   ```json
   { "command": "scene.open", "parameters": { "scene": "Scenes/Main.stscene" } }
   { "command": "entity.create", "parameters": { "name": "Goal", "components": { "Transform": { "Translation": [0, 1, -8], "Scale": [2, 2, 2] }, "MeshRenderer": { "Mesh": "Builtin/Cube" }, "BoxCollider": { "HalfExtents": [0.5, 0.5, 0.5] }, "RigidBody": { "Type": "Static", "IsTrigger": true } } } }
   { "command": "component.add", "parameters": { "entity": "<the Player's ID>", "component": "Tag", "values": { "Tag": "Player" } } }
   { "command": "scene.save" }
   ```

   :::
   ::::

   **You should see:** a grey cube 2 m wide on the path straight ahead of the player, between the low steps and the 40 degree ramp, and a **Tag** section on `Player`.

   **If you do not see it:** in play the player stops at the cube as at a wall. **Is Trigger** is off: a trigger reports a body that enters it and stops nothing.

2. Make a second course scene. Save the course as `Scenes/Level2.stscene` and move its goal, so that the second course is not the first.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **File ▸ Save Scene As...** and type `Scenes/Level2.stscene`. Set the Translation of `Goal` to (6, 1, 2), to the right of the start, then save with **Ctrl+S**.
   :::
   :::tab[With a command]
   The goal's ID is the one `entity.find` with the name `Goal` returns.

   ```json
   { "command": "scene.saveAs", "parameters": { "path": "Scenes/Level2.stscene" } }
   { "command": "component.set", "parameters": { "entity": "<the Goal's ID>", "component": "Transform", "values": { "Translation": [6, 1, 2] } } }
   { "command": "scene.save" }
   ```

   :::
   ::::

   **You should see:** `Level2` as the open scene's name, and `Level2.stscene` in the **Content Browser**.

   **If you do not see it:** the save failed, and the log names the reason. The path is relative to the project's asset folder, as `Scenes/Level2.stscene` is.

3. Give each goal a field for the next level: a script `NextLevel`, whose field `Next` holds a scene that the trigger loads when the player enters. The goal of `Level2` leads to the main menu, the goal of `Main` to `Level2`.

   ```cpp src="book:tutorials/make/levels-saves/NextLevel.cpp#L1-L22"
   // The goal's next level: the player entering the goal's trigger loads the scene in the field Next.

   #include "StrataScript/StrataScript.h"

   using namespace Strata;

   class NextLevel : public Script
   {
   public:
   	AssetHandle Next;

   	void OnTriggerEnter(const Collision& collision) override
   	{
   		if (collision.Other.IsValid() && collision.Other.GetTag() == "Player")
   			Game::LoadScene(Next);
   	}
   };

   ST_SCRIPT_CLASS(NextLevel)
   {
   	ST_SCRIPT_FIELD(Next);
   }
   ```

   1. **Line 10:** the field `Next`, a scene you choose in the Inspector.
   2. **Lines 12–16:** a body that enters the trigger and carries the tag `Player` starts the switch.
   3. **Lines 19–22:** the registration makes the class and its field appear in the editor.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Save the listing as `Scripts/NextLevel.cpp` and build with **Ctrl+B**. In `Level2`, attach `NextLevel` to `Goal` and choose `Scenes/MainMenu.stscene` in `Next`; save. Open `Scenes/Main.stscene`, attach `NextLevel` to its `Goal` with `Scenes/Level2.stscene` in `Next`, and save.
   :::
   :::tab[With a command]
   Save the listing as `Scripts/NextLevel.cpp` first. Each scene has its own `Goal`: find its ID with `entity.find` after you open the scene.

   ```json
   { "command": "script.build" }
   { "command": "script.add", "parameters": { "entity": "<the Goal's ID>", "class": "NextLevel", "fields": { "Next": "Scenes/MainMenu.stscene" } } }
   { "command": "scene.save" }
   { "command": "scene.open", "parameters": { "scene": "Scenes/Main.stscene" } }
   { "command": "script.add", "parameters": { "entity": "<the Goal's ID>", "class": "NextLevel", "fields": { "Next": "Scenes/Level2.stscene" } } }
   { "command": "scene.save" }
   ```

   `scene.saveAs` takes a `path`, but `scene.open` takes a `scene`.
   :::
   ::::

   **You should see:** a field `Next` on each goal in the **Inspector**. Play `Main` and walk straight ahead with **W**: when the player touches the goal, `Level2` plays. With commands, start paused, hold **W** with `input.key` for 240 :term[fixed steps]{id=fixed-step}, run them with `play.step`, and `play.state` names `Level2`.

   **If you do not see it:** the field is empty, or the player has no tag `Player`. A scene that no scene uses is cut from a :term[pruned export]{id=pruned-export}, but a scene named in a field counts as used and stays in.

4. Start the level again after a fall, and return to the menu. A fall is a position below the course. Call `Game::ReloadScene` for it; a button that goes to the main menu calls `Game::LoadScene` with the menu in a field.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Add to the script of the player or a manager this test in `OnUpdate`.

   ```pseudocode
   if (Scene::FindEntityByName("Player").GetTransform().GetWorldPosition().y < -5.0f)
   	Game::ReloadScene();
   ```

   For the button, handle `OnUIClick(Entity widget)` as the pause menu does: when the widget is the menu button, set the :term[time scale]{id=time-scale} to 1 and load the menu scene.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command that builds the changed scripts.

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** the player falls off the course and appears at the start of the same level; the button leads to the main menu.

   **If you do not see it:** the check runs in a script that is on no entity, or the limit lies below the lowest ground. It must also lie above -8 m, the `FallHeight` at which the course's `PlayerController` teleports the player first. A paused scene keeps a scale of 0 until it goes, so the sample sets 1 before it leaves; every new scene starts at 1.

5. Keep state between the scenes in a `.cpp` file. Add a file `GameState.h` with the declarations and `GameState.cpp` with the variables in a namespace without a name, as the sample does.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the header declare `bool IsAttractMode();` and `void SetAttractMode(bool attract);` in a namespace that you name. In the `.cpp` file keep `bool s_AttractMode = false;` in a namespace without a name and let both functions read and write it.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command that builds the scripts.

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** the main menu sets the flag, and the level it starts reads it with the function `IsAttractMode`; the level shows what the menu did.

   **If you do not see it:** the build fails with two definitions, so the variable stands in the header; move it to the `.cpp` file. Or the two scenes disagree, so the variable is `static` in a header; both mistakes are the ones named above. A value that is gone after a hot reload is the normal life of module state.

6. Show the loading bar. Make a scene `Scenes/Loading.stscene` with a canvas, an image of the type **Filled** and a text, and the sample's script `LoadingScreen` on the canvas. Copy that script first: the file `Samples/ThirdPerson/Scripts/LoadingScreen.cpp` of the folder you unpacked Strata into goes into your project's `Scripts`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **File ▸ New Scene** and save it as `Scenes/Loading.stscene`. Add a canvas from the Hierarchy's **+ ▸ UI**, and under it an `Image` named `Bar` and a `Text` named `Label`. Set the image's **Type** to **Filled** and its **Fill Amount** to 0. Attach `LoadingScreen` to the canvas, set its field `Bar` to the image and `Label` to the text, and save. Then choose the scene in **Loading Scene** on the page **Game** of **File ▸ Project Settings...**.
   :::
   :::tab[With a command]
   Each `ui.create` answers the new element's ID as `entity`; the later commands name those IDs.

   ```json
   { "command": "scene.new", "parameters": { "name": "Loading" } }
   { "command": "scene.saveAs", "parameters": { "path": "Scenes/Loading.stscene" } }
   { "command": "ui.create", "parameters": { "type": "canvas", "name": "LoadingCanvas" } }
   { "command": "ui.create", "parameters": { "type": "image", "name": "Bar", "parent": "<the canvas's ID>", "size": [600, 40] } }
   { "command": "component.set", "parameters": { "entity": "<the Bar's ID>", "component": "UIImage", "values": { "Type": "Filled", "FillAmount": 0 } } }
   { "command": "ui.create", "parameters": { "type": "text", "name": "Label", "parent": "<the canvas's ID>", "position": [0, 60], "size": [600, 50], "text": "Loading..." } }
   { "command": "script.build" }
   { "command": "script.add", "parameters": { "entity": "<the canvas's ID>", "class": "LoadingScreen", "fields": { "Bar": "<the Bar's ID>", "Label": "<the Label's ID>" } } }
   { "command": "scene.save" }
   ```

   Then name the scene as the loading scene of an exported game.

   ```json
   { "command": "project.setExportSettings", "parameters": { "loadingScene": "Scenes/Loading.stscene" } }
   ```

   :::
   ::::

   **You should see:** an empty bar and the text `Loading...` in the Game view of the scene, and the scene's handle in the answer of `project.setExportSettings`. An exported game shows the scene while its start scene loads. To see a bar between levels too, build the same canvas in `Main`: a switch keeps `Main` running while `Level2` loads. Making the loading scene the start scene clears the loading scene.

   **If you do not see it:** nothing loads long enough to see. A small project loads in a blink; the bar needs more than a few frames. Test with the exported game, as [Export](export.md) describes.

7. Load a room beside the level, and show its progress. The room is a small scene; the door is a box trigger in `Main` with this script.

   ```cpp src="book:tutorials/make/levels-saves/RoomDoor.cpp#L8-L27"
   class RoomDoor : public Script
   {
   public:
   	AssetHandle Room; // The room's scene
   	Entity Bar;       // A UI image of the type Filled

   	void OnTriggerEnter(const Collision& collision) override
   	{
   		if (IsPlayer(collision) && !m_Room.IsValid())
   			m_Room = Scene::LoadAdditive(Room);
   	}

   	void OnTriggerExit(const Collision& collision) override
   	{
   		if (IsPlayer(collision) && m_Room.IsValid())
   		{
   			m_Room.Unload();
   			m_Room = SubScene();
   		}
   	}
   ```

   1. **Lines 14–18:** the player enters, and the room starts to load, once.
   2. **Lines 20–27:** the player leaves, and the room goes; `m_Room` is empty again, so the next visit loads it again.

   The rest of the class updates the bar and tells the player from other bodies by its tag.

   ```cpp src="book:tutorials/make/levels-saves/RoomDoor.cpp#L29-L42"
   	void OnUpdate(float) override
   	{
   		if (Bar.IsValid())
   			Bar.SetProperty("UIImage", "FillAmount", Assets::GetLoadProgress(Room));
   	}

   private:
   	static bool IsPlayer(const Collision& collision)
   	{
   		return collision.Other.IsValid() && collision.Other.GetTag() == "Player";
   	}

   	SubScene m_Room;
   };
   ```

   1. **Lines 29–33:** the bar, an image of the type **Filled** such as the loading bar, shows how far the room has loaded.
   2. **Lines 36–39:** only a body with the tag `Player` opens the door.

   The file starts as `NextLevel.cpp` does, with the line that includes `StrataScript/StrataScript.h` and `using namespace Strata;`. It ends with the registration: `ST_SCRIPT_CLASS(RoomDoor)` with the fields `Room` and `Bar`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **File ▸ New Scene**, save it as `Scenes/Room.stscene`, add a cube `RoomBlock` at (-8, 0.5, 0) with a **Box Collider**, and save. Open `Scenes/Main.stscene`. Create an entity `Door` at (-3, 1, 2) with the scale (2, 2, 2), a **Box Collider** and a **Rigid Body** with **Type** Static and **Is Trigger** on. Save the listing as `Scripts/RoomDoor.cpp`, build, attach `RoomDoor` to `Door` with `Scenes/Room.stscene` in `Room`, and save.
   :::
   :::tab[With a command]
   Save the listing as `Scripts/RoomDoor.cpp` first. The door's ID is the `id` that `entity.create` answers.

   ```json
   { "command": "scene.new", "parameters": { "name": "Room" } }
   { "command": "scene.saveAs", "parameters": { "path": "Scenes/Room.stscene" } }
   { "command": "entity.create", "parameters": { "name": "RoomBlock", "components": { "Transform": { "Translation": [-8, 0.5, 0] }, "MeshRenderer": { "Mesh": "Builtin/Cube" }, "BoxCollider": { "HalfExtents": [0.5, 0.5, 0.5] } } } }
   { "command": "scene.save" }
   { "command": "scene.open", "parameters": { "scene": "Scenes/Main.stscene" } }
   { "command": "entity.create", "parameters": { "name": "Door", "components": { "Transform": { "Translation": [-3, 1, 2], "Scale": [2, 2, 2] }, "BoxCollider": { "HalfExtents": [0.5, 0.5, 0.5] }, "RigidBody": { "Type": "Static", "IsTrigger": true } } } }
   { "command": "script.build" }
   { "command": "script.add", "parameters": { "entity": "<the Door's ID>", "class": "RoomDoor", "fields": { "Room": "Scenes/Room.stscene" } } }
   { "command": "scene.save" }
   ```

   :::
   ::::

   **You should see:** play `Main` and walk left with **A** into the door: over the next frames the cube `RoomBlock` appears beyond it, and `entity.find` with that name finds it while the game plays. Walk out with **D**, and it goes again.

   **If you do not see it:** loading the same room again fails while its old entities exist. Unload it first: a load after the unload waits until the old entities are gone.

8. Save a best time, settings and a checkpoint. At the end of a level write the time, then read it back at the start. Settings follow the rule of the section above.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Use `ParseWhole` from the section on save files.

   ```pseudocode
   void SaveBest(int seconds)
   {
   	if (!Game::WriteSaveFile("best-time.txt", std::to_string(seconds)))
   		Log::Warn("The best time could not be saved");
   }
   int ReadBest()
   {
   	return ParseWhole(Game::ReadSaveText("best-time.txt").value_or("")).value_or(0);
   }
   ```

   These two functions, `ParseWhole` and the checkpoint's two functions stand above your script's class in its `.cpp` file, `ParseWhole` first. Below the line that includes `StrataScript/StrataScript.h` add `#include <optional>` and `#include <string>`. Write the checkpoint with `SaveCheckpoint` and place the player from `ReadCheckpoint` when it returns a position.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command that builds the scripts.

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** after a run, a file `best-time.txt.save` in `.strata/Saves` of the project with one number, and the same best time after you stop and play again.

   **If you do not see it:** the log has the warning `The best time could not be saved`, which means the name is not valid or the disk refused. A file with the text `abc` gives 0 without a crash: that is the check at work.

   **Why:** a game reads a save file because a player expects it to remember. Reading it once and keeping the value in module state, as the sample's `GetSettings` does, costs the disk once.

:::::

## Result

The course has two levels, a goal that leads from one to the next, a new start after a fall, a way back to the menu and a bar that fills while a scene loads. A room loads and unloads beside a level, and a best time stays after the game closes. Its flags and settings live in the module for the length of a run, and its progress lives in files that the game can read when it starts.

## Variations

- **Three slots.** Name the files `Slot 1`, `Slot 2` and `Slot 3`, show them in a list of three buttons, and write the chosen name into module state. `Game::ListSaveFiles` tells which slots hold a save, so an empty slot shows as new.
- **A save that survives an update.** Write a first line with a version number. A reader that finds a version it does not know falls back to the defaults and does not crash.
- **Attract mode.** Count the idle seconds in the main menu's `OnUpdate`, as the sample does with `AttractDelaySeconds`, and load the course with the flag set. Any key press ends it.

## Summary

- A game is a set of scenes and the moves between them, and no entity survives `Game::LoadScene`.
- What must last longer than a scene goes in a field, in module state or in a save file, by how long it must last.
- `Game::GetSceneLoadProgress` drives a loading bar, and the loading scene covers the first load of an exported game.
- `Scene::LoadAdditive` loads a room beside a level, `Assets::GetLoadProgress` shows its progress, and `SubScene::Unload` removes it.
- A save file holds one value per line, is read as an optional, and is checked before it is converted.

## Check yourself

1. A script of an entity in `Level1` counts five coins in one of its own variables and then calls `Game::LoadScene`. What does `Level2` know about the five coins, and where would you keep the number?

   :::answer{tests="split-scenes pass-state"}
   The entity is gone, so the value is gone. Keep it in module state, since it only has to last while the game runs, or in a save file, if it must survive the end of the game.
   :::

2. You play `Level1` in the editor and the attract mode never starts. Why?

   :::answer{tests="split-scenes"}
   Play runs a copy of the open scene, not the main menu, so the code of the menu never ran. Open the main menu scene and play from it.
   :::

3. The text of `best-time.txt` is `12:30`. What does `ParseWhole` return, and what would `std::stoi` have done without the check?

   :::answer{tests="keep-progress"}
   The function returns nothing, because the colon is no digit. `std::stoi` would read 12 and ignore the rest, but for the text `abc` it would throw and turn the script off.
   :::

4. You call `Scene::LoadAdditive` in every update and keep what it returns in `m_Room`. The room appears, but `m_Room` soon turns invalid and the log reports problems. What goes wrong?

   :::answer{tests="additive-room"}
   Each entity keeps its identity from the file, so a call fails once the room's entities exist: a sub-scene cannot load twice. A failed call returns an invalid `SubScene`, which replaces the good one. Call it once and keep the `SubScene`.
   :::

5. Your loading bar shows nothing during a switch from `Level1` to `Level2`, but works in the loading scene of the exported game. What is the likely cause?

   :::answer{tests="loading-bar"}
   The bar sits in the loading scene, which plays only while the start scene loads. A switch between levels keeps `Level1` running, so the bar must be in a scene that plays then.
   :::

6. Players say a rename of the game's title lost their saves. Is that possible in Strata?

   :::answer{tests="keep-progress"}
   No. The saves folder is named after the project's name, not its title.
   :::

## Exercises

1. **Basic.** Add a third level: save a scene as `Scenes/Level3.stscene`, and name it in the goal of `Level2`.

   :::answer[Worked solution]{tests="split-scenes" solution="tutorials/make/levels-saves/exercise-1.tutorial.json"}
   Save the scene with `scene.saveAs`, then set the field `Next` of the goal in `Level2` to `Scenes/Level3.stscene` and the goal of `Level3` to the main menu. Play from `Level2` and touch the goal.
   :::

2. **Medium.** Add a **Delete save** button to the main menu. It calls `Game::DeleteSaveFile("best-time.txt")` and then shows that no best time is kept.

   :::answer[Worked solution]{tests="keep-progress"}
   In `OnUIClick`, when the widget is the new button, call `Game::DeleteSaveFile`, then `Game::ReadSaveText("best-time.txt")`; its result is empty, so the text shows "No best time". The delete call returns false when there was no file.
   :::

## Where it lives in Strata

- `StrataScriptCore/Include/StrataScript/Game.h`: the scene switches and the save files.
- `StrataScriptCore/Include/StrataScript/Scene.h`: `Scene::LoadAdditive` and `SubScene`.
- `Samples/ThirdPerson/Scripts/ThirdPerson.cpp`: the sample's module state and its settings.
- `Strata/src/Strata/Core/SaveFiles.cpp`: the names and the folders of the save files.

## Further reading

- The documentation of `std::optional` at cppreference.com: the type that `Game::ReadSaveText` returns (intermediate).
