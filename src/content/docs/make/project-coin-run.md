---
id: make/project-coin-run
title: "Project: Coin Run, a first finished game"
description: "Finish Coin Run as a game with a round that is won, lost and started again, polish it, check it by playing and ship it again."
kind: tutorial
size: L
tracks: [G, B]
needs: [make/export, make/sound, make/play-test-debug]
time: 150
learn:
  - id: round-state
    text: build a script that keeps a round's state and time left in one place and ends the round when the coins or the time run out
  - id: freeze-restart
    text: explain how a time scale of zero freezes the world while a restart action still works, and what reloading the scene does
  - id: end-panels
    text: build a win panel and a lose panel that a script hides and shows
  - id: check-game
    text: run a checking list on a finished game and read the Console for warnings
  - id: ship-again
    text: export the finished game with its sound kept, run it windowed and headless, and credit every asset
since: 0.3.0
status: final
---

## What you will make

Coin Run becomes a game: a round that starts, ends in a win or a loss, and starts again at a key press. You check it by playing and ship it as version 1.0.0.

::figure{id=result}

## What you need

- The end of [Exporting and shipping](export.md): Coin Run with its heads-up display (HUD), sounds, an identity and a first export. Download checkpoint 4, at the end of that page's last section, [Prune the export and fix what it loses](export.md#prune-the-export-and-fix-what-it-loses), or continue your own project. The zip holds a folder with `CoinRun.stproj`: open that file with **File ▸ Open Project...**.
- The three versions of the script this page writes. Each checkpoint download of this page holds the version of its section as `Scripts/CoinRunGame.cpp`: checkpoint 1 the first, checkpoint 2 the second, checkpoint 3 the last. The listings below show parts of these files, with their own line numbers.
- One sound: `Complete.ogg` from the `Samples/ThirdPerson/Assets/Sounds/` folder of the release. It is a short winning chime by Kenney, in the public domain (:term[CC0]{id=cc0}), credited in that sample's `CREDITS.md`. Import it as you did in [Sound](sound.md), into the folder `Sounds`.
- About two and a half hours.

### The plan of a small game

A game is finished when a stranger can play it from the first second to the last without you. Coin Run has one round: collect every coin before the time runs out. Write down what makes that round, and what is still missing.

What the game has now:

- a ball that the player rolls, with a jump;
- five coins that the ball collects, placed when the game starts;
- a HUD that counts the coins left and the seconds left.

What is missing:

- a way to win: nothing happens when the last coin goes;
- a way to lose: the timer counts down below zero and never stops;
- a way to start again: you press Stop and Play in the editor, and a player cannot;
- polish: the look and the feel of the small things.

Each missing part is one section below. A fifth section checks the result and ships it.

## Keep the round in one script

Right now two things know about the round. The HUD script counts the coins and shows the time, and the coins delete themselves. Nothing owns the question "is the round still going?". A win, a loss and a restart all need that question answered in one place, or they will disagree.

The state of a round is the one fact that says what the game does now. Coin Run has three: playing, won and lost. A :term[scoped enumeration]{id=scoped-enumeration}, an `enum class`, names them, as you learned in [Programming from zero I](../basics/programming-1.md). A variable of that type holds exactly one of the three, so the round cannot be won and lost at once.

The same script owns the time. The HUD script of the last page also showed a timer, and two scripts that each count seconds drift apart. The new script, `CoinRunGame`, takes over the timer's text and the time bar, and the old `CoinHud` leaves the HUD.

:::example
The time limit is 40 seconds. After 10 seconds the time left is 30. The text reads `Time: 30`, and the bar's fill amount is 30 / 40 = 0.75, three quarters of the bar. With 2 of 5 coins collected, the text reads `Coins left: 3`.
:::

The script has a catch that a test round shows quickly. `CoinPlacer` adds the coins a few frames after the game starts, because the coin :term[prefab]{id=prefab-make} has to load first. In the first frames the level holds no coin. A rule "no coin left means a win" would end the round before it began, so the script remembers whether it has ever seen a coin.

:::question
What are `: public Script` and `override`? A :term[script class]{id=script-class} extends the engine's `Script` class and replaces the :term[callbacks]{id=callback} it needs; [Classes and inheritance](../basics/cpp-classes.md) teaches both.
:::

The first part of the script holds the state, the field and the three :term[callbacks]{id=callback} that matter: creation, the reload after a build, and the update of every frame.

```cpp src="book:tutorials/make/project-coin-run/CoinRunGame.step1.cpp#L11-L29"
enum class RoundState
{
	Playing,
	Won,
	Lost
};

class CoinRunGame : public Script
{
public:
	float TimeLimit = 40.0f; // Seconds the player has

	void OnCreate() override
	{
		m_TimeLeft = TimeLimit;
		FindParts();
	}

	void OnReload() override { FindParts(); }
```

1. **Lines 11-16:** the three states of a round, named once.
2. **Line 21:** the time limit is a field, so you can change it in the Inspector without a build.
3. **Lines 23-27:** `OnCreate` starts the clock and finds the HUD's parts.
4. **Line 29:** after a build while playing, `OnReload` finds the parts again and leaves the clock alone.

The update is the heart of the script. Read it as a list of questions asked every frame.

```cpp src="book:tutorials/make/project-coin-run/CoinRunGame.step1.cpp#L31-L47"
void OnUpdate(float deltaTime) override
{
	if (m_State != RoundState::Playing)
		return;

	// A coin destroyed in this frame still counts until the frame ends: the round sees it gone one frame later.
	const size_t coinsLeft = Scene::FindEntitiesByTag("Coin").size();
	// CoinPlacer adds the coins after the first frames: an empty level is not a won round.
	m_CoinsSeen = m_CoinsSeen || coinsLeft > 0;
	m_TimeLeft = std::max(0.0f, m_TimeLeft - deltaTime);
	ShowHud(coinsLeft);

	if (m_CoinsSeen && coinsLeft == 0)
		Finish(RoundState::Won);
	else if (m_TimeLeft <= 0.0f)
		Finish(RoundState::Lost);
}
```

1. **Lines 33-34:** once the round is over, nothing below runs.
2. **Line 37:** the coins left are the entities tagged `Coin`. A coin destroyed in this frame still counts until the frame ends, so the script sees it gone one frame later, which no player notices.
3. **Line 39:** `m_CoinsSeen` becomes true with the first coin and stays true.
4. **Lines 43-46:** a win is checked before a loss, so the last coin collected in the last frame wins.

The two helpers write the HUD and end the round. In this step, ending only logs a line; the next section gives it a face.

```cpp src="book:tutorials/make/project-coin-run/CoinRunGame.step1.cpp#L57-L68"
void ShowHud(size_t coinsLeft)
{
	m_CoinText.GetUI().SetText("Coins left: " + std::to_string(coinsLeft));
	m_TimerText.GetUI().SetText("Time: " + std::to_string(static_cast<int>(std::ceil(m_TimeLeft))));
	m_TimeBar.SetProperty("UIImage", "FillAmount", m_TimeLeft / TimeLimit);
}

void Finish(RoundState state)
{
	m_State = state;
	Log::Info(state == RoundState::Won ? "Round won" : "Round lost");
}
```

1. **Lines 59-60:** the texts are written every frame; Strata changes a text only when the words differ.
2. **Line 61:** the bar's fill is a property of the `UIImage`, set by name, as on [HUDs: text, score and bars](hud.md).
3. **Lines 64-68:** `Finish` stores the new state once; the checks at the top of the update never run again.

:::why
One script owns the round, and the other scripts only draw and move things. The cost is that `CoinRunGame` finds the HUD's parts by name, so a renamed text silently stops updating. The gain is that a rule such as "the round ends at zero" has one place to change. [Patterns for game code](patterns.md) names this shape.
:::

:::::steps

1. Find the entity that holds the round. [Sound](sound.md) made an entity `Game` for `VolumeKeys`, and it takes the round's script too: one entity can hold several scripts.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Game` in the Hierarchy. If your scene has none, press **+**, choose **Empty** and rename the new entity `Game`.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.find", "parameters": { "name": "Game" } }
   ```

   :::
   ::::

   **You should see:** one entity `Game` at the top level of the Hierarchy, with a Transform and the `VolumeKeys` script.

   **If you do not see it:** two entities are named `Game`, and the script would land on the first. Delete the one without `VolumeKeys`.

2. Take the old HUD script off the HUD. `CoinRunGame` writes the same texts now, and two writers of one text would fight.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `HUD`. In the Inspector, press the **X** at the right end of the `CoinHud` script's header. Leave the file `Scripts/CoinHud.cpp`: a :term[script class]{id=script-class} that no entity uses costs nothing.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.remove", "parameters": { "entity": "<HUD id>", "class": "CoinHud" } }
   ```

   :::
   ::::

   **You should see:** no `CoinHud` on the `HUD` entity.

   **If you do not see it:** you removed another component. Press **Ctrl+Z** and use the **X** on the `CoinHud` header.

3. Save the scene, then create the script and build it. Saving first keeps the scene's edits on disk while you work on code outside the editor.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+S**. Choose **Scripts ▸ New Script...** and make a class `CoinRunGame`. Open the new file in a text editor and replace all of its text with `Scripts/CoinRunGame.cpp` of checkpoint 1's download, at the end of this section; save it. Build with **Scripts ▸ Build Scripts** (**Ctrl+B**).
   :::
   :::tab[With a command]

   ```json
   { "command": "scene.save" }
   { "command": "script.create", "parameters": { "class": "CoinRunGame" } }
   { "command": "script.build" }
   ```

   No command writes a file's text. Between the last two commands, replace the text of the file that `script.create` answers with checkpoint 1's `Scripts/CoinRunGame.cpp`, in a text editor.

   :::
   ::::

   **You should see:** the build ends without errors.

   **If you do not see it:** the :term[Problems panel]{id=problems-panel} lists the error and its line. A missing `#include` is the usual one.

4. Attach the script to `Game` and play.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Game` and use **Add Component ▸ Script** to attach `CoinRunGame`. Press **Play** (**Ctrl+P**) and roll the ball into a coin. Press **Stop** when you have seen both ends of a round.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.add", "parameters": { "entity": "<Game id>", "class": "CoinRunGame", "fields": { "TimeLimit": 40 } } }
   { "command": "play.start", "parameters": { "paused": true, "build": false } }
   { "command": "play.step", "parameters": { "steps": 90 } }
   { "command": "entity.find", "parameters": { "tag": "Coin" } }
   { "command": "entity.delete", "parameters": { "entities": ["<the five IDs>"] } }
   { "command": "play.step", "parameters": { "steps": 2 } }
   { "command": "log.read", "parameters": { "newest": true, "limit": 20 } }
   { "command": "play.stop" }
   ```

   No command rolls the ball over every coin. Deleting the five coins of the running copy ends the round as collecting
   them would, so `log.read` then holds `Round won`. A second play runs 2,490 :term[fixed steps]{id=fixed-step}, 41.5 seconds of game time,
   and its `log.read` holds `Round lost`:

   ```json
   { "command": "play.start", "parameters": { "paused": true, "build": false } }
   { "command": "play.step", "parameters": { "steps": 2490 } }
   { "command": "log.read", "parameters": { "newest": true, "limit": 20 } }
   { "command": "play.stop" }
   ```

   :::
   ::::

   **You should see:** the coin count fall with each coin, the seconds count down from 40 and the bar shrink. When the last coin goes, the Console shows `Round won`. Wait out a second game and the Console shows `Round lost` at zero.

   **If you do not see it:** the Console shows `Round won` at once. The coins are not tagged `Coin`, or `CoinPlacer` is missing; check the **Tag** of a coin.

:::::

::checkpoint{stage=1}

::figure{id=round-playing}

## Win, lose and start again

A round that ends with a line in the Console ends for you, not for the player. This section gives the end three things: a panel that says what happened, a frozen world, and a key that starts again.

The panels are elements of the user interface (UI), made as on the HUD page. Each panel is a plain rectangle that holds two texts. Make them as children of the `HUD` canvas by the right-click menu **Create Child**. Never use the **+** button: it creates at the top level, and a UI element made outside a canvas gets a new canvas of its own.

The script hides a panel with `SetActive(false)` and shows it with `SetActive(true)`. An inactive entity is not drawn and gets no updates. You can leave both panels visible while you lay them out, because the script hides them when the round starts. A hidden panel is still found by its name: `Scene::FindEntityByName` does not skip inactive entities, so the script finds `WinPanel` at creation and again after a reload.

The world stops through the :term[time scale]{id=time-scale}. `Time::SetTimeScale(0.0f)` makes every frame's delta time zero for the scripts and the physics, so the ball, the coins and the clock stand still. The unscaled input still arrives, and `OnUpdate` still runs, so the restart key works. A restart loads the scene again; the script sets the scale back to 1 at creation, so a new round never starts frozen.

:::example
At 60 frames per second the delta time of a frame is 1 / 60 = 0.0167 seconds. At time scale 0 the scripts get 0 × 0.0167 = 0 seconds, and the physics adds 0 to its step timer, so it takes no step. The ball keeps its position and its velocity: no step runs that would change either.
:::

The restart is an input action, as on [Input and input actions](input.md). A button action `Restart` in the `Gameplay` map gets the key **Enter** and the gamepad's **Start** button. The ball's own script already uses **R** to put the ball back, so the new action takes another key. A script reads it with `Input::IsActionPressed("Gameplay/Restart")`, which is true in the one frame of the press.

`Game::ReloadScene()` starts the round again in one step. In the editor, it starts again what play mode runs: your edited scene with the changes you did not save. In an exported game, it loads the scene from its asset.

Every entity of the old scene goes away, and each script receives `OnDestroy`. A :term[script field]{id=script-field} that held an `Entity` of the old scene is dead; the new scene makes new entities with new ids. A script that must survive a load cannot hold entities across it, and [Levels, loading and saves](levels-saves.md) teaches how to pass state on.

The second version of the script adds the panels, the sound, the freeze and the restart. Three parts are new. The first is the creation, which resets the clock and the scale, asks early for the sound and hides the panels.

```cpp src="book:tutorials/make/project-coin-run/CoinRunGame.step2.cpp#L24-L35"
void OnCreate() override
{
	// A restart loads the scene again; the time scale of the finished round must not follow it.
	Time::SetTimeScale(1.0f);
	m_TimeLeft = TimeLimit;
	m_WinSound = Assets::Find("Sounds/Complete.ogg");
	Assets::RequestLoad(m_WinSound);
	FindParts();
	// The panels stay visible in the editor while you lay them out; the round hides them at its start.
	m_WinPanel.SetActive(false);
	m_LosePanel.SetActive(false);
}
```

1. **Line 27:** the time scale returns to 1 in every new round.
2. **Lines 29-30:** the clip is requested early, so that `Audio::PlayOneShot` finds it loaded at the win, as on [Sound](sound.md).
3. **Lines 33-34:** both panels start hidden.

The second part is the update, which now answers the restart first.

```cpp src="book:tutorials/make/project-coin-run/CoinRunGame.step2.cpp#L39-L61"
void OnUpdate(float deltaTime) override
{
	// Read before the state check: the frozen game still hears the action.
	if (Input::IsActionPressed("Gameplay/Restart"))
	{
		Game::ReloadScene();
		return;
	}
	if (m_State != RoundState::Playing)
		return;

	// A coin destroyed in this frame still counts until the frame ends: the round sees it gone one frame later.
	const size_t coinsLeft = Scene::FindEntitiesByTag("Coin").size();
	// CoinPlacer adds the coins after the first frames: an empty level is not a won round.
	m_CoinsSeen = m_CoinsSeen || coinsLeft > 0;
	m_TimeLeft = std::max(0.0f, m_TimeLeft - deltaTime);
	ShowHud(coinsLeft);

	if (m_CoinsSeen && coinsLeft == 0)
		Finish(RoundState::Won);
	else if (m_TimeLeft <= 0.0f)
		Finish(RoundState::Lost);
}
```

1. **Lines 42-46:** the restart is read before the state check, so it works in a round that is over and in the middle of one.
2. **Line 44:** `Game::ReloadScene()` asks again harmlessly: while a load is under way, asking again changes nothing.
3. **Lines 47-48:** the update ignores a finished round after the restart check.

The third part is `Finish`, which now shows a panel and plays the win sound.

```cpp src="book:tutorials/make/project-coin-run/CoinRunGame.step2.cpp#L81-L93"
void Finish(RoundState state)
{
	m_State = state;
	// Scale 0 stops the ball, the coins and the timer; Update still runs, so Restart still works.
	Time::SetTimeScale(0.0f);
	if (state == RoundState::Won)
	{
		m_WinPanel.SetActive(true);
		Audio::PlayOneShot(m_WinSound);
	}
	else
		m_LosePanel.SetActive(true);
}
```

1. **Line 85:** the freeze. The world stops, and the update continues.
2. **Lines 86-90:** a win shows its panel and plays `Complete.ogg`.
3. **Lines 91-92:** a loss shows the other panel.

:::::steps

1. Import the sound and make the win panel.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Import `Complete.ogg` into `Sounds`. Right-click `HUD`, choose **Create Child ▸ UI** and then the panel entry. Rename it `WinPanel`.

   In **Anchors** choose the preset "Middle Center" and set **Size** to 700 and 300. Right-click `WinPanel`, choose **Create Child ▸ UI ▸ Text** and rename it `WinTitle`. Set **Text** to `You win` and **Font Size** to 72. Add a second child text, `WinHint`, with `Press Enter to play again` and size 36, anchored "Bottom Center".
   :::
   :::tab[With a command]

   ```json
   { "command": "asset.import", "parameters": { "file": "<release folder>/Samples/ThirdPerson/Assets/Sounds/Complete.ogg", "directory": "Sounds" } }
   { "command": "ui.create", "parameters": { "type": "panel", "parent": "<HUD id>", "name": "WinPanel", "anchor": "middleCenter", "size": [700, 300] } }
   { "command": "ui.create", "parameters": { "type": "text", "parent": "<WinPanel id>", "name": "WinTitle", "text": "You win", "anchor": "middleCenter", "size": [660, 100] } }
   { "command": "component.set", "parameters": { "entity": "<WinTitle id>", "component": "UIText", "values": { "FontSize": 72 } } }
   { "command": "ui.create", "parameters": { "type": "text", "parent": "<WinPanel id>", "name": "WinHint", "text": "Press Enter to play again", "anchor": "bottomCenter", "position": [0, -24], "size": [660, 60] } }
   { "command": "component.set", "parameters": { "entity": "<WinHint id>", "component": "UIText", "values": { "FontSize": 36 } } }
   ```

   :::
   ::::

   **You should see:** a panel in the middle of the Game view with the words `You win` over it.

   **If you do not see it:** the Hierarchy shows a second canvas. You used **+**: delete that canvas and use **Create Child** on `HUD`.

2. Make the lose panel. The quickest way is to duplicate the first one.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `WinPanel` and press **Ctrl+D**. Rename the copy `LosePanel`, and change its title to `Time's up`. Check that the copy is a child of `HUD`, with its two texts inside.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.duplicate", "parameters": { "entity": "<WinPanel id>" } }
   { "command": "entity.rename", "parameters": { "entity": "<WinPanel (1) id>", "name": "LosePanel" } }
   { "command": "entity.get", "parameters": { "entity": "<LosePanel id>" } }
   { "command": "component.set", "parameters": { "entity": "<the first of its children>", "component": "UIText", "values": { "Text": "Time's up" } } }
   ```

   The copy's title is also named `WinTitle`, so the last command names it by the first of the `children` that `entity.get` answers.

   :::
   ::::

   **You should see:** two panels on top of each other in the Game view. Their names must be exactly `WinPanel` and `LosePanel`.

   **If you do not see it:** the script cannot find a panel whose name has a space or another letter, and it does nothing without a message. Check the spelling.

3. Add the restart action.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open **File ▸ Project Settings ▸ Input Actions** and select the map `Gameplay`. Press **Add Action** and name it `Restart`. Select the new action, press the bind button and press **Enter** on the keyboard. Add a second binding and press the button `Start` on a gamepad, if you have one.
   :::
   :::tab[With a command]

   ```json
   { "command": "inputActions.setAction", "parameters": { "action": "Gameplay/Restart", "kind": "Button", "bindings": ["Key/Enter", "Gamepad/Start"] } }
   ```

   :::
   ::::

   **You should see:** `Restart` in the list of the `Gameplay` actions, with its bindings.

   **If you do not see it:** the action sits in another map. Its full name must read `Gameplay/Restart`.

4. Save the scene, replace the script with the second version and build.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+S**. Replace the text of `Scripts/CoinRunGame.cpp` with the same file of checkpoint 2's download, at the end of this section, and press **Ctrl+B**.
   :::
   :::tab[With a command]

   ```json
   { "command": "scene.save" }
   { "command": "script.build" }
   ```

   Between the two commands, replace the text of `Scripts/CoinRunGame.cpp` with checkpoint 2's file, in a text editor.

   :::
   ::::

   **You should see:** the build ends without errors, and both panels hide when you play.

   **If you do not see it:** a panel stays visible. Its name does not match the script's; compare them letter by letter.

5. Play a won round and a lost round. For the lost round, set `TimeLimit` on `Game` to 8 in the Inspector while the game is stopped.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Play**, collect all five coins and listen. Press **Enter**, then **Stop**. Select `Game`, type 8 in `TimeLimit`, press **Play**, do nothing until the time is up, and press **Enter** again.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start", "parameters": { "paused": true, "build": false } }
   { "command": "play.step", "parameters": { "steps": 120 } }
   { "command": "entity.find", "parameters": { "tag": "Coin" } }
   { "command": "entity.delete", "parameters": { "entities": ["<the five IDs>"] } }
   { "command": "play.step", "parameters": { "steps": 2 } }
   { "command": "input.key", "parameters": { "key": "Enter" } }
   { "command": "play.step", "parameters": { "steps": 120 } }
   { "command": "play.stop" }
   ```

   Deleting the coins of the running copy stands in for collecting them. The lost round sets the shorter time first:

   ```json
   { "command": "script.setField", "parameters": { "entity": "<Game id>", "class": "CoinRunGame", "field": "TimeLimit", "value": 8 } }
   { "command": "play.start", "parameters": { "paused": true, "build": false } }
   { "command": "play.step", "parameters": { "steps": 600 } }
   { "command": "input.key", "parameters": { "key": "Enter" } }
   { "command": "play.step", "parameters": { "steps": 10 } }
   ```

   Read a panel between two steps with `entity.find` and `{"name": "WinPanel"}`, then `entity.get` with its identifier
   (ID): `active` is true while it shows. Find the panel again after **Enter**, since the new round makes new entities. `input.key` presses **Enter** for one fixed
   step; a paused game gets it in the next `play.step`.

   :::
   ::::

   **You should see:** with all coins, the win sound and `You win`, and the ball standing still. With no coins, `Time's up` after 8 seconds. **Enter** starts the round again with five coins and a full bar.

   **If you do not see it:** **Enter** does nothing. The Game view must have the focus: click it once. If the new round starts frozen, the script is the old version: build again.

6. Set `TimeLimit` back to 40.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Stop the game, select `Game` and type 40 in `TimeLimit` in the Inspector.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.stop" }
   { "command": "script.setField", "parameters": { "entity": "<Game id>", "class": "CoinRunGame", "field": "TimeLimit", "value": 40 } }
   ```

   :::
   ::::

   **You should see:** `TimeLimit` 40 in the Inspector.

   **If you do not see it:** the field shows 8 in a new round: the script field of the scene kept it. Type 40 again.

:::::

::checkpoint{stage=2}

::figure{id=win-panel}

## Polish the round and check it by playing

Polish is the work after the game works. Each change here is small, and each answers a question a player asks without words: can I see the whole level, is this too hard, what does the game feel like?

A difficulty setting is a number that scales one thing the player feels. Coin Run scales the time. The field `Difficulty` is 0, 1 or 2, and the time limit is the base limit times 1.5, 1.0 or 0.67. On the lowest level the 40 seconds become 60; on the highest level they become 26.8, shown as 27 because the text rounds up.

Time running low needs a signal. The timer text and the bar go white, then yellow at 20 seconds, then red at 10. The script writes a color only when the stage changes, so it costs nothing in the other frames. The third version of the script adds both ideas.

```cpp src="book:tutorials/make/project-coin-run/CoinRunGame.cpp#L84-L104"
// Easy gives half as much time again, Hard a third less.
float GetTimeFactor() const
{
	static const float c_Factors[] = { 1.5f, 1.0f, 0.67f };
	return c_Factors[std::clamp(Difficulty, 0, 2)];
}

// White, then yellow at 20 seconds left, then red at 10; the colors change only when the stage does.
void ShowTimeColor()
{
	glm::vec4 color(1.0f);
	if (m_TimeLeft <= 10.0f)
		color = glm::vec4(1.0f, 0.2f, 0.2f, 1.0f);
	else if (m_TimeLeft <= 20.0f)
		color = glm::vec4(1.0f, 0.85f, 0.2f, 1.0f);
	if (color == m_TimeColor)
		return;
	m_TimeColor = color;
	m_TimerText.GetUI().SetColor(color);
	m_TimeBar.GetUI().SetColor(color);
}
```

1. **Lines 84-89:** the factor table; `std::clamp` keeps a wrong field value of 7 from reading past the end.
2. **Lines 94-98:** the color starts white and changes at the two thresholds.
3. **Lines 99-100:** the same color as before ends the function; nothing is written.
4. **Lines 102-103:** the text and the bar change together.

:::::steps

1. Check the camera. The whole level must read in the Game view.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click the **Game camera** chip above the Scene view, or press **F8**. The five coins, the walls and the ball must all be in view. If you moved the `Main Camera`, put it back: **Translation** 0, 16, 13 and **Rotation** -55, 0, 0.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<Main Camera id>", "component": "Transform", "values": { "Translation": [0, 16, 13], "Rotation": [-0.4617, 0, 0, 0.887] } } }
   ```

   :::
   ::::

   **You should see:** the whole 20 m level inside the frame with a margin on each side.

   **If you do not see it:** a wall is cut at the bottom. The camera is too low or tilted too far: raise **Translation** Y by 2 and try again.

2. Save the scene, replace the script with the final version and build. The file is `Scripts/CoinRunGame.cpp` of checkpoint 3's download, at the end of this section.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+S**. Replace the text of `Scripts/CoinRunGame.cpp` and press **Ctrl+B**.
   :::
   :::tab[With a command]

   ```json
   { "command": "scene.save" }
   { "command": "script.build" }
   ```

   Between the two commands, replace the text of `Scripts/CoinRunGame.cpp` with checkpoint 3's file, in a text editor.

   :::
   ::::

   **You should see:** a field `Difficulty` of 1 on `Game` next to `TimeLimit`.

   **If you do not see it:** the Inspector still shows the old fields. Select another entity and select `Game` again.

3. Try the three difficulties. Set `Difficulty` to 0, play and read the timer; then set it to 2. Set it back to 1 when you are done.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Game`, type 0 in `Difficulty` and press **Play**. Press **Stop**, type 2 and play again. Stop, and type 1.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.setField", "parameters": { "entity": "<Game id>", "class": "CoinRunGame", "field": "Difficulty", "value": 0 } }
   { "command": "play.start", "parameters": { "build": false } }
   { "command": "play.stop" }
   { "command": "script.setField", "parameters": { "entity": "<Game id>", "class": "CoinRunGame", "field": "Difficulty", "value": 2 } }
   { "command": "play.start", "parameters": { "build": false } }
   { "command": "play.stop" }
   { "command": "script.setField", "parameters": { "entity": "<Game id>", "class": "CoinRunGame", "field": "Difficulty", "value": 1 } }
   ```

   :::
   ::::

   **You should see:** `Time: 60` at level 0 and `Time: 27` at level 2 in the first second, and the colors change at 20 and 10 seconds left.

   **If you do not see it:** the timer starts at 40. The field kept its value because you changed it while playing: stop the game first.

4. Tune the coins' spin and bob. You find the values while playing, then set them in the prefab, because edits of a running game vanish at **Stop**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Play**, select a coin in the Hierarchy and change `DegreesPerSecond` and `BobHeight` in the Inspector until they look right. Note the values and press **Stop**. Drag `Prefabs/Coin.stprefab` into the Scene view, set the two values on the instance, right-click the changed label and choose **Apply to Prefab**. Delete the instance: `CoinPlacer` makes the coins while the game plays.
   :::
   :::tab[With a command]

   ```json
   { "command": "prefab.instantiate", "parameters": { "prefab": "Prefabs/Coin.stprefab", "components": { "Transform": { "Translation": [0, 0.8, 6] } } } }
   { "command": "script.setField", "parameters": { "entity": "<Coin id>", "class": "Coin", "field": "DegreesPerSecond", "value": 90 } }
   { "command": "script.setField", "parameters": { "entity": "<Coin id>", "class": "Coin", "field": "BobHeight", "value": 0.25 } }
   { "command": "prefab.apply", "parameters": { "entity": "<Coin id>" } }
   { "command": "entity.delete", "parameters": { "entities": ["<Coin id>"] } }
   ```

   :::
   ::::

   **You should see:** in the next play, all five coins turning and bobbing with your values.

   **If you do not see it:** the coins keep the old look. The apply failed because the game was still playing: Apply works in edit mode only.

5. Clear an old field of the ball. Press **Play** and read the **Console**. If it shows `Script fields: script 'BallControl' has no field 'Speed'; the stored value is ignored`, the scene still stores the `Speed` of the first `BallControl` of [Input](input.md). The version of [Physics](physics.md) has no such field, and the Inspector shows only the fields the class has, so nothing there removes it. Removing the script and adding it again stores no old value: the new script starts with the class's own defaults, the values Physics uses.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Stop** and select `Ball`. Press the **X** on the `BallControl` header, then use **Add Component ▸ Script** to attach `BallControl` again.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.remove", "parameters": { "entity": "<Ball id>", "class": "BallControl" } }
   { "command": "script.add", "parameters": { "entity": "<Ball id>", "class": "BallControl" } }
   ```

   :::
   ::::

   **You should see:** no `Script fields` line in the **Console** at the next **Play**, and the ball rolling as before.

   **If you do not see it:** the warning names another field or script. Remove and add that script the same way, then set again any field you had changed in the Inspector.

:::::

The game now has what a player feels. The sound when a coin goes was made on [Sound](sound.md). The glow of [Scripting the scene](scripting-scene.md) left with the `Coin.cpp` of Physics, which no longer swaps the material; bring it back as an exercise of your own.

### Check the game by playing it

A game you only played while building it works on the path you walked. A checking list makes you walk the others. Play each check with the Console panel open, and read it for warnings after each.

| Check | What you expect |
| --- | --- |
| Win | Collect every coin and let the win sound end: the win panel, the frozen world, the sound. |
| Loss | Let the time run out with coins left: the lose panel and no sound. |
| New starts | Press **Enter** twice in a row, once from each end panel and once in the middle of a round: a full bar and five coins each time. |
| Screens | Play at 16:9, 4:3 and 21:9 with the Game view's resolution chip: the panels in the middle, the texts in their corners. |
| Console | Read it after each check: no warning and no error, once step 5 above cleared the old field. A warning names what is wrong, such as `there is no asset at 'Sounds/Complete.ogg'` for a clip in another folder. |
| Light | A scene without a light is dark in the game even when the editor's preview looks lit, so judge by the Game view, never by the Scene view alone. |

:::::steps

1. Walk the table.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Play** and do the six checks in order, then press **Stop**.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command.

   ```json
   { "command": "play.start", "parameters": { "paused": true, "build": false } }
   { "command": "play.step", "parameters": { "steps": 120 } }
   { "command": "play.stop" }
   ```

   :::
   ::::

   **You should see:** each check behave as its expectation says, and a clean Console.

   **If you do not see it:** one line fails. Fix it before you export; the failing check names the part: win and loss the script, new starts the scene reload, screens the anchors, Console an asset path.

:::::

::checkpoint{stage=3}

::figure{id=polished}

## Ship the finished game

You exported Coin Run on [Exporting and shipping](export.md). That export knew nothing of the win sound or the panels. The game's identity is already in place: the title `Coin Run`, the version `1.0.0` and the icon. Check the **Game** page of **File ▸ Project Settings** shows them, and change the version only when you ship a new one.

A :term[pruned export]{id=pruned-export} packs only what the scenes use. The win sound is loaded by path from a script, so no scene names it. The **Always Include** list of the **Export** page keeps what scripts load by path, and it takes folders. If the list still holds the folder `Sounds`, as the last page left it, `Complete.ogg` is kept, because you imported it there. A clip in another folder is lost.

Strata reports a lost path in the game's log, `Logs/Game.log`, as a warning that starts `FindAsset` and names the path. Reading that log is how you find what a pruned export lacks.

:::::steps

1. Check the list of assets kept by every export.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open **File ▸ Project Settings ▸ Export**. The list must hold the coin prefab (`Prefabs` or `Prefabs/Coin.stprefab`), the glow material `Materials/GoldGlow.stmat` that the last page kept, and `Sounds`, which holds `Coin.ogg`, `Complete.ogg`, `Impacts/Soft.ogg` and `Music/Complete.ogg`. Add what is missing in the text field and press **Add**.
   :::
   :::tab[With a command]

   ```json
   { "command": "project.setExportSettings", "parameters": { "alwaysInclude": ["Prefabs", "Materials/GoldGlow.stmat", "Sounds"] } }
   ```

   :::
   ::::

   **You should see:** each path listed with a remove button.

   **If you do not see it:** the field refuses a path. It must name an asset or a folder of the project, relative to its assets, with `/`.

2. Save the scene, build the scripts, then export with the unused assets omitted. The export reads the saved files.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+S**, then **Ctrl+B**. Choose **File ▸ Export Game...**, pick a folder outside the project, enable `Leave out unused assets` and press **Export**. When the bar reads **Done**, press **Open Folder**.
   :::
   :::tab[With a command]

   ```json
   { "command": "scene.save" }
   { "command": "script.build" }
   { "command": "project.export", "parameters": { "directory": "<a folder outside the project>", "prune": true } }
   ```

   :::
   ::::

   **You should see:** a folder with `CoinRun`, `CoinRun.stgame`, a `.stpak` pack, the :term[script module]{id=script-module} and `ThirdPartyNotices.md`.

   **If you do not see it:** the export refuses. The scene has changes you did not save, another export is running, no script module is loaded, or the folder lies inside the project. The message names which.

3. Run the game windowed, then headless.

   ::::tabs{sync=os}
   :::tab[Windows]

   Run the windowed game for ten seconds with a screenshot, then the headless run, from PowerShell in the export folder.

   ```powershell
   .\CoinRun.exe --windowed --seconds 10 --screenshot shot.png
   .\CoinRun.exe --headless --frames 600 | Write-Output
   ```

   The pipe to `Write-Output` makes PowerShell wait for the program.

   :::
   :::tab[Linux]

   ```sh
   ./CoinRun --windowed --seconds 10 --screenshot shot.png
   ./CoinRun --headless --frames 600
   ```

   The same two runs, in a terminal.

   :::
   :::tab[macOS]

   ```sh
   ./CoinRun --windowed --seconds 10 --screenshot shot.png
   ./CoinRun --headless --frames 600
   ```

   :::
   ::::

   The first run shows the game for ten seconds of game time; the second draws nothing. A headless run has no window, so no player can collect a coin in it: it checks that the game starts, loads its assets and exits with code 0.

   **You should see:** a window titled `Coin Run` with the HUD and five coins, a `shot.png`, and exit code 0 for the second run. The window is 1280 by 720 at a display scale of 100 %. The game grows it with the scale, so at 150 % the window and `shot.png` are 1920 by 1080 pixels; add `--resolution 1280x720` for exact pixels.

   **If you do not see it:** no coins appear. The coin prefab is missing from the pack: return to the first step of this section.

4. Read the game's log.

   Open `Logs/Game.log` in the game's data folder, named after the game: on Windows `%LOCALAPPDATA%\CoinRun\Logs\Game.log`; on Linux `~/.local/share/CoinRun/Logs/Game.log`. No command reads this log: open it in a text editor.

   **You should see:** the lines of the game and no warning that starts `FindAsset` or `Script fields`.

   **If you do not see it:** a warning names a path. Add that path or its folder to the **Always Include** list and export again.

5. Credit every asset. Open `CREDITS.md` in the project folder, the file that [Bringing in assets](assets.md) started, and add a row for each file the game uses that you did not make. The checkpoint downloads hold no `CREDITS.md`: if your project has none, create it in the project folder, beside `CoinRun.stproj`.

   Edit the file in a text editor. The rows, in the table form of Bringing in assets:

   | Files | Source | Author | License | Changes |
   | --- | --- | --- | --- | --- |
   | `Sounds/Coin.ogg`, `Sounds/Complete.ogg`, `Sounds/Music/Complete.ogg` | Kenney's Interface Sounds pack | Kenney | CC0-1.0 | renamed |
   | `Sounds/Impacts/Soft.ogg` | Kenney's Impact Sounds pack | Kenney | CC0-1.0 | renamed |
   | the coin model and its texture | Kenney's Platformer Kit | Kenney | CC0-1.0 | none |
   | `Textures/Metal/` | `ambientCG`, Metal032 | `ambientCG` | CC0-1.0 | as the Physics Playground sample packed them |
   | the sky in `Environment/` | Poly Haven | the authors that the Third Person sample's `CREDITS.md` names | CC0-1.0 | none |
   | the HUD's image | Kenney's UI Pack | Kenney | CC0-1.0 | none |
   | `Icon.png` | the Third Person sample | Strata | Strata | none |

   The music of [Sound](sound.md) is the win chime again: `Sounds/Music/Complete.ogg` is a copy of the same file under the same name, in another folder. A music file of your own gets its own row, with the credit text its license asks for.

   **You should see:** one row for every file in `Environment`, `Models`, `Sounds`, `Textures` and `UI`.

   **If you do not see it:** a file has no row. A :term[CC-BY]{id=cc-by} file without its credit text is a broken license: replace the file or add the text.

:::::

The export folder already holds `ThirdPartyNotices.md`, which names the engine's own libraries: keep it beside the game when you give the game away. You may ship the game with the book's code in it, by the permission that [Credits and licenses](../appendix/credits.md) states.

You own a finished, exported game. Track G continues at [The math of moving things](gameplay-math.md): the vectors and angles behind the movement you wrote by feel. Track B continues at [Version control with git](../basics/git.md), the first of the other pages of the basics. A reader on track B may also take track G from The math of moving things at once, and read the rest of the programming and mathematics basics later. At the bottom of the page, **Next on your track** names the next page of the track you chose.

[Designing a game](designing-a-game.md) plans the next game before you build it, and the projects of block C make a Tetris game and a platformer with what you know now.

::checkpoint{stage=4}

::figure{id=shipped}

## Summary

- A round's state and its time left live in one script, and the round ends when the coins or the time run out, with a guard against an empty level.
- A time scale of zero freezes the world while the update and the restart action continue, and a scene reload starts the round again in one step.
- Win and lose panels are UI elements that the script hides and shows with `SetActive`; the finds see hidden entities.
- A checking list covers the win, the loss, the new starts, three screen shapes and the Console.
- A pruned export keeps the sound by the **Always Include** list, runs windowed and headless, and every asset has a credit.

## Check yourself

1. Remove the variable `m_CoinsSeen` from the script. What happens when you press **Play**, and why?

   :::answer{tests="round-state"}
   The round is won in the first frame. `CoinPlacer` adds the coins a few frames later, so the level holds no coin at the start, and "no coin left" is true.
   :::

2. At time scale 0, what delta time does `OnUpdate` get, and why does the restart still work?

   :::answer{tests="freeze-restart"}
   The delta time is 0. The update still runs every frame and the input arrives unscaled, so `Input::IsActionPressed` sees the key; the restart reads it before the state check.
   :::

3. The script hides `LosePanel` at creation. How does it find the panel later, and what breaks if you delete the panel?

   :::answer{tests="end-panels"}
   `Scene::FindEntityByName` also finds inactive entities, so the name is enough. A deleted panel is not found: the `Entity` is invalid and `SetActive` does nothing, so a lost round shows no panel.
   :::

4. The Console shows a warning at every start: `there is no asset at 'Sounds/Complete.ogg'`. Which check of the table finds it, and what do you do?

   :::answer{tests="check-game"}
   The Console check. The clip is not at that path: import it into the folder `Sounds`, or change the path in the script.
   :::

5. A pruned export plays without the win sound, and `Game.log` has a `FindAsset` warning. What is the cause and the fix?

   :::answer{tests="ship-again"}
   No scene uses the clip, so the pruned pack omitted it. Add `Sounds` or `Sounds/Complete.ogg` to **Always Include** and export again.
   :::

## Exercises

1. **Basic.** Make one coin worth 5 points. Tag it `BigCoin`, show a `Score` text in the HUD, and let the win wait for both tags to run out. What is the score when the ball has collected all five small coins and the big one?

   :::answer[Worked solution]{tests="round-state" solution="tutorials/make/project-coin-run/exercise-1.tutorial.json"}
   A tag holds one word, so the big coin has no `Coin` tag and the script counts a second tag with `Scene::FindEntitiesByTag("BigCoin")`. The score is the small coins collected plus 5 times the big ones: 5 + 5 = 10. The solution file `exercise-1/CoinRunGame.cpp` does this.
   :::

2. **Medium.** Add a sixth coin on a platform that the ball reaches only by a jump. The jump gives the ball 5 metres per second upward, and gravity is 9.81 metres per second squared. How high may the platform be?

   :::answer{tests="round-state"}
   The ball rises $v^2 / (2g)$, where $v$ is the speed and $g$ the gravity: $25 / 19.62 = 1.27$ metres. The ball's centre must rise by the platform's height, so a platform 1 metre high works and one of 1.5 metres does not. Place the coin by hand, since the edited scene has no coin: a coin 0.8 metres above the platform's top counts like the others.
   :::

3. **Hard.** Add a kinematic obstacle that moves from side to side in `OnFixedUpdate`, and sends the ball back to its start when it touches the ball. What must the script do besides `Teleport`?

   :::answer{tests="freeze-restart"}
   `Teleport` keeps the body's velocities, so the script sets the linear and the angular velocity to zero too, or the ball starts again still rolling. The sketch shows the two callbacks.

   ```cpp pseudocode
   void OnFixedUpdate(float fixedDeltaTime) override
   {
       m_Time += fixedDeltaTime;
       position.x = m_StartX + Reach * sin(Speed * m_Time);
       GetTransform().SetTranslation(position);
   }

   void OnCollisionEnter(const Collision& collision) override
   {
       if (collision.Other.GetName() == "Ball")
       {
           RigidBody body = collision.Other.GetRigidBody();
           body.Teleport(SendBackTo);
           body.SetLinearVelocity(glm::vec3(0.0f));
           body.SetAngularVelocity(glm::vec3(0.0f));
       }
   }
   ```

   1. **Lines 1-6:** the obstacle moves in the :term[fixed step]{id=fixed-step}, where the physics reads a body's target.
   2. **Line 10:** only the ball is sent back.
   3. **Lines 12-15:** the body goes to the start and loses its speed.
   :::

## Where it lives in Strata

The script functions of this page are in `StrataScriptCore/Include/StrataScript/`: `Game.h` for `Game::ReloadScene`, `Time.h` for the time scale, `Entity.h` for `SetActive`, and `UI.h` for text and color. The scene's time scale is `Scene::SetTimeScale` in `Strata/src/Strata/Scene/Scene.h`. The export is `Strata/src/Strata/Scripting/ScriptHostAPI.cpp` for the `FindAsset` warning and `StrataEditor/src/Editor/GameExport.cpp` for the export itself. The finished Tetris sample, whose round works the same way, is `Samples/Tetris/Scripts/TetrisGame.cpp`.

## Further reading

- Kenney's asset pages: the sources of the sounds and the coin, with their licenses (beginner).
- Jesse Schell, The Art of Game Design: how a round, its goal and its feedback fit together (intermediate).
