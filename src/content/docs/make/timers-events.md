---
id: make/timers-events
title: "Timers, time scale and events between scripts"
description: "Time things in game time or real time, repeat a held key, slow and pause a game, and let scripts call each other safely."
kind: how-to
size: M
tracks: [G]
needs: [make/project-coin-run]
time: 90
learn:
  - id: pick-clock
    text: choose the right clock of Time for a job in game time or real time
  - id: use-timers
    text: build a repeating timer, a one-shot delay and a dash cooldown with Timer
  - id: repeat-key
    text: write a held-key repeat with KeyRepeat and predict when it fires
  - id: slow-pause
    text: set the time scale for slow motion and a pause and blink a text on unscaled time
  - id: call-scripts
    text: name how one script calls another through GetScript and AddScript without keeping a pointer
since: 0.3.0
status: final
---

You will build a small room. Crates drop from the ceiling, and a player cube dashes along the floor to collect them. A marker steps along a row of cubes, and the keys **1**, **2** and **P** slow and freeze the game. Before you start:

- You made a project from the Basic 3D template, and you can write a script, build it and attach it, as in [First script](first-script.md).
- You know `OnUpdate` and the time scale from [The script loop](script-loop.md).
- You can find an entity by name from a script, and you made a prefab and a text on a canvas ([Scripts and the scene](scripting-scene.md), [Prefabs](prefabs.md), [the on-screen display page](hud.md)).

## The clocks a script can read

A game measures time in more than one way. Suppose a crate must drop every two seconds. Do those two seconds continue while the player pauses? A clock on the wall says yes, and a clock of the game says no. A script can read both.

`Time` gives a script these clocks, all in seconds except the frame index:

| Call | What it measures | At time scale 0 |
| --- | --- | --- |
| `Time::GetDeltaTime()` | The length of this :term[frame times]{id=frame-time} the time scale: the `deltaTime` of `OnUpdate`. | It is 0 |
| `Time::GetFixedDeltaTime()` | The length of one :term[fixed step]{id=fixed-step}. | It does not change |
| `Time::GetElapsedTime()` | The game time since play started. | It stops |
| `Time::GetFrameIndex()` | The count of finished frames since play started. | It continues |
| `Time::GetUnscaledDeltaTime()` | The length of this frame before the time scale. | It continues |
| `Time::GetRealTime()` | The sum of the unscaled deltas since play started. | It continues |

**Unscaled time** is time that ignores the time scale: it moves at the real speed of the frames, also while the game is slowed or frozen. Game time is the other kind, and the time scale multiplies it. `Time::GetTimeScale()` reads the scale and `Time::SetTimeScale()` writes it. Strata refuses a scale that is negative or not a finite number, and it logs a problem.

:::example
At 60 frames per second a frame lasts 0.0167 s. At time scale 1 the delta and the unscaled delta are both 0.0167 s. At 0.25 the delta is $0.0167 \times 0.25 = 0.0042$ s, a quarter of the frame, and the unscaled delta is still 0.0167 s. At 0 the delta is 0. After 2 s of the wall clock at 0.25, the game time is 0.5 s and the real time is 2 s.
:::

Which clock for which job? Follow these three rules:

- What belongs to the game world (movement, cooldowns, crate drops) uses the delta or the game time, so that a pause stops it.
- What belongs to the player's screen (a blinking "Paused" text, a fade, a menu animation) uses the unscaled delta or the real time, so that it keeps moving.
- A count of frames serves diagnostics only: at 144 frames per second it grows faster than at 60.

## Build the room

:::::steps

1. Make the crate: a cube with a collider and a dynamic Rigid Body ([Physics](physics.md)), turned into a prefab ([Prefabs](prefabs.md)).

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **+** in the Hierarchy, choose **Cube** and rename it `Crate`; the cube comes with a Box Collider. Choose **Add Component ▸ Rigid Body**. Right-click `Crate`, choose **Create Prefab**, then delete the `Crate` in the scene: the script makes the crates from now on.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "Crate", "components": { "MeshRenderer": { "Mesh": "Builtin/Cube" }, "BoxCollider": { "HalfExtents": [0.5, 0.5, 0.5] }, "RigidBody": {}, "Transform": { "Translation": [0, 6, 0] } } } }
   { "command": "prefab.create", "parameters": { "entities": ["<Crate id>"], "path": "Prefabs/Crate.stprefab" } }
   { "command": "entity.delete", "parameters": { "entities": ["<Crate id>"] } }
   ```

   :::
   ::::

   **You should see:** the file `Prefabs/Crate.stprefab` in the Content Browser and no crate in the Hierarchy.

   **If you do not see it:** the prefab is missing. Create it before you delete the entity: nothing remains to turn into a prefab afterwards.

2. Make the player, the entity that holds the score, the row of cubes and the canvas with two texts.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Make a **Cube** named `Player` at 0, 0.5, 0, an **Empty** named `Game`, and a **Cube** named `Marker` at 0, 1.5, -4 with scale 0.5. Make five cubes `Slot1` to `Slot5` at x of -4, -2, 0, 2 and 4, y 0.5, z -4. Add a canvas `HUD` with the texts `ScoreText` (`Score: 0`, top left) and `PausedText` (`Paused`, middle) as in [the on-screen display page](hud.md).
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "Player", "components": { "MeshRenderer": { "Mesh": "Builtin/Cube" }, "Transform": { "Translation": [0, 0.5, 0] } } } }
   { "command": "entity.create", "parameters": { "name": "Game" } }
   { "command": "entity.create", "parameters": { "name": "Marker", "components": { "MeshRenderer": { "Mesh": "Builtin/Cube" }, "Transform": { "Translation": [0, 1.5, -4], "Scale": [0.5, 0.5, 0.5] } } } }
   { "command": "entity.create", "parameters": { "name": "Slot1", "components": { "MeshRenderer": { "Mesh": "Builtin/Cube" }, "Transform": { "Translation": [-4, 0.5, -4] } } } }
   { "command": "ui.create", "parameters": { "type": "canvas", "name": "HUD" } }
   { "command": "ui.create", "parameters": { "type": "text", "parent": "<HUD id>", "name": "ScoreText", "text": "Score: 0", "anchor": "topLeft", "position": [24, 24], "size": [360, 48] } }
   { "command": "ui.create", "parameters": { "type": "text", "parent": "<HUD id>", "name": "PausedText", "text": "Paused", "anchor": "middleCenter", "size": [360, 48] } }
   ```

   Repeat the `Slot1` line for `Slot2` to `Slot5` with the other x values.
   :::
   ::::

   **You should see:** the cubes in the Scene view, `Score: 0` at the top left of the Game view and `Paused` in the middle.

   **If you do not see it:** a text is missing. Its entity is not a child of `HUD`: drag it onto the canvas in the Hierarchy.

:::::

## Read the clocks and set the time scale

The script `TimeControl` sets the scale with keys and writes the clocks to the log. `OnUpdate` runs at every time scale, also at 0, so the script still reads keys while the game is frozen.

:::question
What are `override` and `: public`? See [C++ classes](../basics/cpp-classes.md).
:::

<!-- markdownlint-disable MD029 -->
:::::steps

3. Create the script `TimeControl` with **Scripts ▸ New Script...** and write its `OnUpdate`. The class shell is the template's.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Replace the body of `OnUpdate` with the lines below. Press **Ctrl+B**, select `Game`, and choose **Add Component ▸ Script** then `TimeControl`. Press **Play** (**Ctrl+P**), then **2**, then **L**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.create", "parameters": { "class": "TimeControl", "open": true } }
   { "command": "script.build" }
   { "command": "script.add", "parameters": { "entity": "<Game id>", "class": "TimeControl" } }
   { "command": "play.start" }
   { "command": "input.key", "parameters": { "key": "D2" } }
   { "command": "input.key", "parameters": { "key": "L" } }
   { "command": "input.key", "parameters": { "key": "P", "action": "press" } }
   { "command": "input.key", "parameters": { "key": "L", "action": "press" } }
   { "command": "log.read", "parameters": { "newest": true, "limit": 50 } }
   ```

   At scale 0 no step runs to end a tap, so **P** and the second **L** use `press`.
   :::
   ::::

   The method changes the scale on three keys and logs every clock on a fourth.

   ```cpp src="book:tutorials/make/timers-events/TimeControl.step2.cpp#L9-L21"
   void OnUpdate(float deltaTime) override
   {
   	if (Input::IsKeyPressed(Key::D1))
   		Time::SetTimeScale(1.0f);
   	if (Input::IsKeyPressed(Key::D2))
   		Time::SetTimeScale(0.25f);
   	if (Input::IsKeyPressed(Key::P))
   		Time::SetTimeScale(Time::GetTimeScale() > 0.0f ? 0.0f : 1.0f);

   	if (Input::IsKeyPressed(Key::L))
   		Log::Info("scale ", Time::GetTimeScale(), " delta ", deltaTime, " unscaled ", Time::GetUnscaledDeltaTime(),
   			" elapsed ", Time::GetElapsedTime(), " real ", Time::GetRealTime());
   }
   ```

   1. **Lines 11–12:** key **1** sets the scale to 1, normal speed.
   2. **Lines 13–14:** key **2** sets 0.25, a quarter of the speed.
   3. **Lines 15–16:** key **P** toggles between 0 and 1.
   4. **Lines 18–20:** key **L** writes the clocks with `Log::Info`, which joins its arguments.

   **You should see:** after **2** and **L**, a line in the Console with `scale 0.25` and a `delta` a quarter of the `unscaled`, which is your frame's length: near 0.017 at 60 frames per second. After **P** and **L**, `delta 0` and an `unscaled` that still moves.

   **If you do not see it:** nothing is logged. The Game view does not have the keyboard: click it once, and check that the build succeeded.

:::::
<!-- markdownlint-enable MD029 -->

## Drop a crate with a repeating timer

A **timer** counts down the time you give it and tells you when the time is up. Strata's `Timer` runs inside your :term[script module]{id=script-module}, and you feed it the `deltaTime` of the frame. A repeating timer starts again by itself.

Why feed it the frame's delta? Then the timer follows the game: a pause gives a delta of 0, so the timer stops where it is. A timer fed with the unscaled delta would continue.

`Update` returns how many times the timer ended during that step. Usually the answer is 0 or 1, but a frame longer than the period can end it twice. The loop `for (int32_t i = timer.Update(deltaTime); i > 0; i--)` runs once for each end, so no crate is lost.

:::example
A timer has a period of 0.5 s, and each frame lasts 0.3 s. The remaining time is 0.5 s, then 0.2 s after the first frame, then $0.2 - 0.3 = -0.1$ s after the second. The period ended at 0.5 s, and the second frame, which closes at 0.6 s, sees it with 0.1 s of overshoot. A timer that started again from that frame would end next at 1.1 s.

Strata's timer keeps the overshoot, so the next period has $0.5 - 0.1 = 0.4$ s left and ends at 1.0 s. The frame that closes at 1.2 s sees it, and the period does not drift with the frame rate.
:::

The lines below are the part of `Timer::Update` that keeps the overshoot: it takes the time past zero, counts the whole periods in it, and puts the rest into the next period.

```cpp src="StrataScriptCore/Include/StrataScript/Gameplay.h#L157-L162"
// The period that ended, and every further one that fit into the step, elapsed; the next one is partly over.
const float overshoot = -m_Remaining;
const float periods = std::floor(overshoot / m_Duration);
m_Remaining = m_Duration - (overshoot - periods * m_Duration);
if (!(m_Remaining > 0.0f) || m_Remaining > m_Duration)
	m_Remaining = m_Duration; // Rounding
```

A frame of 1.3 s with the same period shows the whole periods: $0.5 - 1.3 = -0.8$ s, so one more period fits and the call returns 2.

<!-- markdownlint-disable MD029 -->
:::::steps

4. Create the script `Dropper` and attach it to `Game`. Its `OnCreate` finds the prefab, asks the engine to load it, and starts a repeating timer.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Write `Period`, `OnCreate`, `OnReload` and `OnUpdate` as below, with the members `AssetHandle m_Crate;`, `Timer m_Timer;` and `int32_t m_Count = 0;`, build with **Ctrl+B**, and add `Dropper` to `Game` with **Add Component ▸ Script**. Set `Period` to 2 in the Inspector.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.create", "parameters": { "class": "Dropper" } }
   { "command": "script.build" }
   { "command": "script.add", "parameters": { "entity": "<Game id>", "class": "Dropper", "fields": { "Period": 2 } } }
   ```

   :::
   ::::

   `OnCreate` below starts the timer, and `OnUpdate` makes one crate for each end of the timer.

   ```cpp src="book:tutorials/make/timers-events/Dropper.step3.cpp#L11-L30"
   void OnCreate() override
   {
   	m_Crate = Assets::Find("Prefabs/Crate.stprefab");
   	Assets::RequestLoad(m_Crate);
   	m_Timer.Start(Period, true);
   }

   void OnReload() override { OnCreate(); }

   void OnUpdate(float deltaTime) override
   {
   	for (int32_t i = m_Timer.Update(deltaTime); i > 0; i--)
   	{
   		if (!Assets::IsLoaded(m_Crate))
   			continue;
   		const float x = static_cast<float>(m_Count % 5 - 2) * 3.0f;
   		Scene::Instantiate(m_Crate, glm::vec3(x, 6.0f, 0.0f));
   		m_Count++;
   	}
   }
   ```

   1. **Lines 11–16:** `OnCreate` finds the prefab, asks the engine to load it, and starts a timer of `Period` seconds that repeats (`true`).
   2. **Line 18:** after a :term[hot reload]{id=hot-reload}, `OnReload` starts the timer again in the same way.
   3. **Line 22:** the loop runs once for each period that ended.
   4. **Lines 24–25:** the prefab may not be loaded yet, and a script never waits for it: that crate is skipped.
   5. **Lines 26–27:** the position cycles over five columns 3 m apart, and `Scene::Instantiate` makes a crate 6 m up.

   **You should see:** in play mode, a crate every two seconds, falling to the ground. Press **2**: crates come every eight seconds. Press **P**: they stop until you press it again.

   **If you do not see it:** no crate appears. Check that `Prefabs/Crate.stprefab` exists and that the Console shows no script error.

:::::
<!-- markdownlint-enable MD029 -->

A :term[one-shot]{id=one-shot} timer, made with `Start(duration)` and no repeat, ends once and stops: `m_Delay.Start(3.0f)` and `if (m_Delay.Update(deltaTime) > 0)` run something three game seconds later. A duration that is zero, negative or not a number stops the timer instead, because a repeating timer without a length would end without limit.

`IsRunning()`, `GetRemaining()` and `GetProgress()` ask how the timer stands, and `GetProgress()` goes from 0 to 1 in each period. A `Timer` is a plain member, not a field, so a :term[hot reload]{id=hot-reload} starts it again from nothing: start it in `OnReload`, as the scripts here do.

## Give the dash a cooldown

A **cooldown** is the wait before an action can be used again. A one-shot timer makes one: start it when the player dashes, and allow the next dash only while it is not running.

<!-- markdownlint-disable MD029 -->
:::::steps

5. Create the script `Player` and attach it to `Player`. The keys **A** and **D** move the cube, and `Left Shift` dashes 3 m. This page reads keys so that the new project needs no setup. A real game reads input actions, as [Input](input.md) taught.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Create the script, replace all of its text with the listing below, build, add `Player` to the `Player` entity, and play.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.create", "parameters": { "class": "Player" } }
   { "command": "script.build" }
   { "command": "script.add", "parameters": { "entity": "<Player id>", "class": "Player" } }
   ```

   Between the first two commands, replace the text of `Scripts/Player.cpp` with the listing, in a text editor.
   :::
   ::::

   Lines 1–3 are the template's, and `ST_SCRIPT_CLASS(Player)` after the class registers the three fields.

   ```cpp src="book:tutorials/make/timers-events/Player.cpp#L6-L23"
   class Player : public Script
   {
   public:
   	float Speed = 4.0f;
   	float DashDistance = 3.0f;
   	float DashCooldown = 1.5f;

   	void OnUpdate(float deltaTime) override
   	{
   		if (Time::GetTimeScale() == 0.0f)
   			return;
   		float move = 0.0f;
   		if (Input::IsKeyDown(Key::A))
   			move -= 1.0f;
   		if (Input::IsKeyDown(Key::D))
   			move += 1.0f;
   		if (move != 0.0f)
   			m_Facing = move;
   ```

   1. **Lines 9–11:** the speed, the dash and the cooldown are fields, set in the Inspector.
   2. **Lines 15–16:** a frozen game takes no move and no dash.

   The dash is the `if` below: a press counts only while the cooldown is not running.

   ```cpp src="book:tutorials/make/timers-events/Player.cpp#L25-L40"
   		glm::vec3 position = GetTransform().GetTranslation();
   		position.x += move * Speed * deltaTime;
   		if (Input::IsKeyPressed(Key::LeftShift) && !m_Cooldown.IsRunning())
   		{
   			position.x += m_Facing * DashDistance;
   			m_Cooldown.Start(DashCooldown);
   		}
   		m_Cooldown.Update(deltaTime);
   		position.x = glm::clamp(position.x, -8.0f, 8.0f);
   		GetTransform().SetTranslation(position);
   	}

   private:
   	Timer m_Cooldown;
   	float m_Facing = 1.0f;
   };
   ```

   1. **Lines 27–31:** `Start` begins a wait of `DashCooldown` seconds.
   2. **Line 32:** `Update` feeds the cooldown every frame.

   **You should see:** the cube moves with **A** and **D**. A press of `Left Shift` jumps it 3 m, and a second press within 1.5 s does nothing.

   **If you do not see it:** the cube does not move. It has no `Player` script, or the game is frozen: press **P** again.

:::::
<!-- markdownlint-enable MD029 -->

The cooldown takes the scaled delta, so at scale 0.25 it lasts six seconds of the wall clock, and at 0 it never ends.

## Repeat a held key

Hold an arrow key in a text field: one letter appears, a pause follows, and then letters come quickly. A menu or a marker wants the same. `Input::IsKeyDown` every frame would move a marker 60 times a second, and `Input::IsKeyPressed` would move it once for each press.

`KeyRepeat` does the third thing. Its `Update` returns true in the frame the key goes down, again after a delay, and then at an interval while the key stays down, at most once per frame. The defaults are a delay of 0.25 s and an interval of 0.05 s.

:::example
At 60 frames per second a frame lasts 0.0167 s. You press the key in frame 0 and `Update` returns true. The next repeat is due at 0.25 s, which is frame 15, so it returns true there. Then it returns true at 0.30 s, 0.35 s and on: every third frame, since three frames last 0.05 s.

Now a frame of 0.2 s arrives when the held time is 0.25 s and the next repeat is due at 0.30 s. The held time becomes 0.45 s and `Update` returns true once. The next repeat moves to 0.50 s, not 0.35 s: a long frame repeats once and does not fire a burst.
:::

The helper is a small state machine with three states: key up, key newly down, key held.

```cpp src="StrataScriptCore/Include/StrataScript/Gameplay.h#L189-L211"
bool Update(float deltaTime)
{
	if (!Input::IsKeyDown(m_Key))
	{
		m_Held = false;
		return false;
	}
	if (!m_Held || Input::IsKeyPressed(m_Key))
	{
		m_Held = true;
		m_HeldTime = 0.0f;
		m_NextRepeat = m_Delay;
		return true;
	}
	m_HeldTime += deltaTime > 0.0f ? deltaTime : 0.0f;
	if (m_HeldTime < m_NextRepeat)
		return false;
	m_NextRepeat += m_Interval;
	// A long frame repeats once, then continues from now.
	if (m_NextRepeat < m_HeldTime)
		m_NextRepeat = m_HeldTime + m_Interval;
	return true;
}
```

1. **Lines 191–195:** a key that is up clears the held flag and returns false.
2. **Lines 196–201:** the first frame, or a new press, resets the held time and sets the first repeat to the delay.
3. **Lines 203–205:** a held key adds the frame's time and waits until the repeat is due.
4. **Lines 206–210:** the next repeat moves by one interval, and a long frame skips ahead from now.

<!-- markdownlint-disable MD029 -->
:::::steps

6. Create the script `Marker` and attach it to `Marker`. It keeps two `KeyRepeat` members and an index from 0 to 4.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Write `OnUpdate` as below, with the members `KeyRepeat m_Left = KeyRepeat(Key::Left);`, the same `m_Right` on `Key::Right`, and `int32_t m_Index = 2;` for the middle cube. Build, add `Marker` to the `Marker` entity, and play.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.create", "parameters": { "class": "Marker" } }
   { "command": "script.build" }
   { "command": "script.add", "parameters": { "entity": "<Marker id>", "class": "Marker" } }
   ```

   :::
   ::::

   The method moves the index at each true answer and puts the marker above its cube.

   ```cpp src="book:tutorials/make/timers-events/Marker.cpp#L9-L19"
   void OnUpdate(float deltaTime) override
   {
   	if (m_Left.Update(deltaTime))
   		m_Index = glm::max(m_Index - 1, 0);
   	if (m_Right.Update(deltaTime))
   		m_Index = glm::min(m_Index + 1, 4);

   	glm::vec3 position = GetTransform().GetTranslation();
   	position.x = static_cast<float>(m_Index - 2) * 2.0f;
   	GetTransform().SetTranslation(position);
   }
   ```

   1. **Lines 11–12:** the left helper decides whether to move one cube left, and the index never goes below 0.
   2. **Lines 13–14:** the same to the right, up to 4.
   3. **Lines 16–18:** the marker's x is two metres for each index, from -4 at the first cube.

   **You should see:** the marker steps one cube at the press of an arrow, waits a moment, and then runs along the row while you hold the key.

   **If you do not see it:** the marker does not move. Click the Game view first, so that it has the keyboard.

:::::
<!-- markdownlint-enable MD029 -->

`KeyRepeat` takes a key code and reads that key. It cannot repeat an input action or a gamepad button, so a repeat built on it ignores the player's rebinding and the gamepad. For a held action or a gamepad direction, write the same three states on `Input::IsActionDown` and `Input::IsActionPressed`, with a delay, an interval and a `float` for the held time.

## Slow the game and freeze it

The time scale makes slow motion and a pause with one number. At 0.25 everything that uses the delta runs at a quarter of the speed, at 0 it stops, and scripts still run and read keys. The pause menu is the subject of [Menus](menus.md); here you make only the freeze and a blinking word.

The word must blink while the game is frozen, so its timer cannot use the delta, which is 0 then. It uses `Time::GetUnscaledDeltaTime()`.

<!-- markdownlint-disable MD029 -->
:::::steps

7. Extend `TimeControl` with a repeating timer of 0.5 s on the unscaled delta, and a text that shows only while the scale is 0.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Add the members `Entity m_PausedText;`, `Timer m_Blink;` and `bool m_BlinkOn = true;`. Write an `OnCreate` with `m_PausedText = Scene::FindEntityByName("PausedText");` and `m_Blink.Start(0.5f, true);`, and an `OnReload` that calls `OnCreate();`. Add the lines below at the end of `OnUpdate`. Build and play.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   { "command": "play.start" }
   ```

   :::
   ::::

   These lines flip a flag every half second and draw the word only while the game is frozen and the flag is on.

   ```cpp src="book:tutorials/make/timers-events/TimeControl.cpp#L30-L34"
   if (m_Blink.Update(Time::GetUnscaledDeltaTime()) % 2 == 1)
   	m_BlinkOn = !m_BlinkOn;
   const bool paused = Time::GetTimeScale() == 0.0f;
   if (m_PausedText.IsValid())
   	m_PausedText.GetUI().SetColor(glm::vec4(1.0f, 1.0f, 1.0f, paused && m_BlinkOn ? 1.0f : 0.0f));
   ```

   **You should see:** at the press of **P**, the world freezes (crates stop in the air, the cooldown stops) and `Paused` blinks once a second. A second press hides it.

   **If you do not see it:** the word is always on or always off. Check the name `PausedText`, and check that the timer takes `GetUnscaledDeltaTime` and not `deltaTime`.

:::::
<!-- markdownlint-enable MD029 -->

## Let scripts call each other

The score belongs in one place: a `Scoreboard` script on the entity `Game`. A crate that the player touches must tell it. A script finds the entity that holds the other one, and asks that entity for the script: `Scene::FindEntityByName("Game").GetScript<Scoreboard>()` returns a pointer to the `Scoreboard`, or `nullptr` when the entity has none.

:::question
What are `*`, `->` and `nullptr`? See [C++ memory](../basics/cpp-memory.md).
:::

<!-- markdownlint-disable MD029 -->
:::::steps

8. Split the class from its registration. **Scripts ▸ New Script...** writes one `.cpp` file for each class, and a second file cannot see a class that lives in the first. Put the class in `Scoreboard.h`, its code and its registration in `Scoreboard.cpp`, and write `#include "Scoreboard.h"` in every script that calls it.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Create the class `Scoreboard`. Move its class definition, with the `Score` field and `void AddPoint();`, into a new file `Scripts/Scoreboard.h` that starts with `#pragma once`. Keep `AddPoint` and `ST_SCRIPT_CLASS(Scoreboard)` in `Scoreboard.cpp`. Build, and add `Scoreboard` to `Game`.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.create", "parameters": { "class": "Scoreboard" } }
   { "command": "script.build" }
   { "command": "script.add", "parameters": { "entity": "<Game id>", "class": "Scoreboard" } }
   ```

   :::
   ::::

   The header declares the class and the method that others call.

   ```cpp src="book:tutorials/make/timers-events/Scoreboard.h#L8-L14"
   class Scoreboard : public Strata::Script
   {
   public:
   	int32_t Score = 0;

   	void AddPoint();
   };
   ```

   The method itself, in the `.cpp`, changes the score and the text.

   ```cpp src="book:tutorials/make/timers-events/Scoreboard.cpp#L7-L13"
   void Scoreboard::AddPoint()
   {
   	Score++;
   	const Entity text = Scene::FindEntityByName("ScoreText");
   	if (text.IsValid())
   		text.GetUI().SetText("Score: " + std::to_string(Score));
   }
   ```

   The text is found at each call, never kept: it may not exist yet.

   **You should see:** the build succeeds and `Game` lists the `Scoreboard` script with its `Score` field.

   **If you do not see it:** no script runs, and the log says `class 'Scoreboard' is registered twice`. The `ST_SCRIPT_CLASS` line stands in the header, so every file that includes the header registers the class again. Move it to the `.cpp`.

9. Give each crate a `Pickup`, written in `Pickup.h` and `Pickup.cpp` like `Scoreboard`. The `Dropper` calls `crate.AddScript<Pickup>()` after it makes a crate, so the prefab needs no script.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Create `Pickup`. Write the class into a new file `Scripts/Pickup.h`, the first listing below, and keep in `Pickup.cpp` the method of the second listing with `ST_SCRIPT_CLASS(Pickup)` and the `Reach` field. In `Dropper.cpp`, include `Pickup.h` and change the line that makes the crate as the third listing shows. Build and play.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.create", "parameters": { "class": "Pickup" } }
   { "command": "script.build" }
   { "command": "play.start" }
   ```

   Between the first two commands, write the three files as the editor tab says, in a text editor.
   :::
   ::::

   `Pickup.h` starts with `#pragma once` and `#include "Scoreboard.h"`, then declares the class:

   ```cpp src="book:tutorials/make/timers-events/Pickup.h#L6-L12"
   class Pickup : public Strata::Script
   {
   public:
   	float Reach = 1.2f;

   	void OnUpdate(float deltaTime) override;
   };
   ```

   The `Pickup` method finds the player, measures the distance, and then calls the score and removes the crate.

   ```cpp src="book:tutorials/make/timers-events/Pickup.cpp#L5-L17"
   void Pickup::OnUpdate([[maybe_unused]] float deltaTime)
   {
   	const Entity player = Scene::FindEntityByName("Player");
   	if (!player.IsValid())
   		return;
   	const float distance = glm::distance(player.GetTransform().GetWorldPosition(), GetTransform().GetWorldPosition());
   	if (distance > Reach)
   		return;

   	if (Scoreboard* scoreboard = Scene::FindEntityByName("Game").GetScript<Scoreboard>())
   		scoreboard->AddPoint();
   	GetEntity().Destroy();
   }
   ```

   1. **Lines 7–9:** the player is found again in each frame, and the method returns when it is missing.
   2. **Lines 10–12:** the method returns while the player is farther than `Reach`.
   3. **Lines 14–15:** `Game` is asked for its `Scoreboard`, which is called only when the pointer is not `nullptr`.
   4. **Line 16:** `Destroy` removes the crate at the end of the frame.

   In the loop of `Dropper`, the new crate gets its `Pickup` at once:

   ```cpp src="book:tutorials/make/timers-events/Dropper.cpp#L27-L29"
   Entity crate = Scene::Instantiate(m_Crate, glm::vec3(x, 6.0f, 0.0f));
   if (crate.IsValid())
   	crate.AddScript<Pickup>();
   ```

   `crate` is no `const Entity`: `AddScript` changes the entity, and on a `const` one the build fails with C2662.

   **You should see:** when the cube comes within 1.2 m of a crate, the crate vanishes and `Score: 1` appears.

   **If you do not see it:** the score stays at 0. The entity is not named `Game`, `Scoreboard` is not attached to it, or the crate got no `Pickup`: check the call of `AddScript` in `Dropper`.

:::::
<!-- markdownlint-enable MD029 -->

Never keep a `GetScript<T>()` pointer from one frame to the next. The other script may be destroyed, and a hot reload makes every script instance again and leaves the old pointer on memory that is gone. Keep the `Entity` in a member, check `IsValid()` and ask again each time you need the script, as `Pickup` does.

`AddScript<T>()` gives an entity a behaviour while the game runs and returns its pointer, or `nullptr` when it cannot. `HasScript("Pickup")` asks whether an entity has the script, and `RemoveScript("Pickup")` takes it away. Both take the class name as text.

Strata has no `coroutines`: each :term[callback]{id=callback} returns at once, and a timer or a state machine does the waiting.

## Result

You have a room with four things. Crates fall on a repeating timer, and a cube dashes on a cooldown. A marker repeats a held key, and a `Scoreboard` counts the crates the cube collects. The game slows with **2** and freezes with **P** while a text blinks on unscaled time.

## Variations

- **A timer on the fixed step.** Gameplay that keeps step with physics runs in `OnFixedUpdate`: feed the timer there with its `fixedDeltaTime` argument, the length of one step ([The script loop](script-loop.md)).

## Summary

- Game time (the delta and the game time since the start) follows the time scale and stops at 0; unscaled time and the real time continue, so the screen's own animations use them.
- A repeating `Timer` fed with the delta keeps its overshoot and returns how many periods ended; a duration that is not positive stops it; a cooldown is a one-shot timer.
- `KeyRepeat` fires on the press, after a delay of 0.25 s and then every 0.05 s by default; it reads keys, not actions.
- `Time::SetTimeScale` slows or freezes the game, and a text that blinks while the game is frozen runs on the unscaled delta.
- A script finds another with `Scene::FindEntityByName(...).GetScript<T>()`, checks for `nullptr`, never keeps the pointer, and gives behaviour at run time with `AddScript<T>()`.

## Check yourself

1. A `Timer` with a period of 0.5 s takes frames of 0.3 s. When does it end the first two times?

   :::answer{tests="use-timers"}
   The periods end at 0.5 s and 1.0 s, and the frames that close at 0.6 s and 1.2 s report them. The timer keeps the first overshoot of 0.1 s, so the second period has 0.4 s left.
   :::

2. The game runs at time scale 0.25 and a frame lasts 0.02 s on the wall clock. What are the delta and the unscaled delta, and which one feeds the fade-out of a menu?

   :::answer{tests="pick-clock slow-pause"}
   The delta is $0.02 \times 0.25 = 0.005$ s and the unscaled delta is 0.02 s. The fade uses the unscaled delta, so that the menu moves at the same speed at any time scale.
   :::

3. You hold a key with the defaults of `KeyRepeat` for 0.4 s at 100 frames per second. How often does `Update` return true?

   :::answer{tests="repeat-key"}
   Five times: at the press, then at 0.25, 0.30, 0.35 and 0.40 s. A frame lasts 0.01 s, so each repeat falls on a frame.
   :::

4. A script keeps a `Scoreboard*` from `OnCreate` and uses it in every `OnUpdate`. Why can this crash, and what does it keep instead?

   :::answer{tests="call-scripts"}
   A hot reload or a destroyed entity leaves the pointer on memory that is gone. The script keeps the `Entity`, checks `IsValid()`, calls `GetScript<Scoreboard>()` when it needs the score, and checks for `nullptr`.
   :::

5. The `Dropper` has a period of 2 s. How many seconds of the wall clock pass between crates at time scale 0.5, and at 0?

   :::answer{tests="use-timers slow-pause"}
   At 0.5 the timer counts game time at half speed, so 4 s. At 0 the delta is 0 and no crate drops.
   :::

## Exercises

1. **Basic.** Show the dash cooldown as a bar at the bottom of the screen that fills with the timer's progress.

   :::answer[Worked solution]{tests="use-timers" solution="tutorials/make/timers-events/exercise-1.tutorial.json"}
   Make an image `DashBar` of the type Filled on the `HUD` canvas. In `Player`, find it in `OnCreate`, and in `OnUpdate` set its fill with `SetProperty("UIImage", "FillAmount", ...)` to `m_Cooldown.GetProgress()` while the timer runs and to 1 when it does not. The bar is full when the dash is ready, and it reaches full 1.5 s after a dash.
   :::

2. **Medium.** Write two timers of 10 s that count down, one on the unscaled delta and one on the scaled delta, started together. What does each do at time scale 0, and at 0.25?

   :::answer{tests="pick-clock slow-pause"}
   Feed one `Timer` with `Time::GetUnscaledDeltaTime()` and the other with `deltaTime`. At 0 the unscaled one ends after 10 s of the wall clock and the scaled one never moves. At 0.25 the unscaled one still ends after 10 s, the scaled one after 40 s.
   :::

## Where it lives in Strata

- `StrataScriptCore/Include/StrataScript/Time.h`: the `Time` class, with every clock of the table.
- `StrataScriptCore/Include/StrataScript/Gameplay.h`: `Timer` and `KeyRepeat`, which run inside the script module.
- `StrataScriptCore/Include/StrataScript/Entity.h`: `GetScript`, `AddScript`, `HasScript` and `RemoveScript`.
- `Strata/src/Strata/Scene/Scene.cpp`: where the scene computes the scaled and the unscaled delta of a frame.
- `Samples/ThirdPerson/Scripts/Coin.cpp`: a coin that finds `CourseState` again when the player collects it.

## Further reading

- [Game Programming Patterns, "Game Loop"](https://gameprogrammingpatterns.com/game-loop.html): how a loop measures time, with the problems of a fixed and a variable step (intermediate).
- [Unity manual, "Time.timeScale"](https://docs.unity3d.com/ScriptReference/Time-timeScale.html): the same idea in another engine, with its scaled and unscaled times (beginner).
