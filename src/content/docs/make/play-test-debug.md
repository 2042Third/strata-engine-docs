---
id: make/play-test-debug
title: "Playing, testing and debugging"
description: "Play Coin Run on purpose, freeze it, step it, change it while it runs, read its log and find a bug in one of its scripts."
kind: how-to
size: M
tracks: [G, B]
needs: [make/hud, basics/debugging]
time: 60
learn:
  - id: play-copy
    text: explain why Play runs a copy of the scene and which edits made while playing go at Stop
  - id: pause-step
    text: run a paused game one fixed step at a time
  - id: read-log
    text: find the Console, the editor's log file and the exported game's log
  - id: find-bug
    text: find a bug in a script with the log or a breakpoint and fix it
  - id: same-steps
    text: explain why the same inputs, counted in fixed steps, give the same game
since: 0.3.0
status: final
---

You will play Coin Run on purpose, freeze it at any moment, run it one step at a time, change it while it runs and find
a bug in one of its scripts. At the end the coin count on the screen is right in every frame. Before you start:

- You have Coin Run with its coin count on the screen, as built in [the chapter on text, score and bars](hud.md). Its
  `CoinHud` script writes the count. If you skipped that page, download the checkpoint at the end of its last section,
  [Check every screen and add text in the world](hud.md#check-every-screen-and-add-text-in-the-world). The zip holds a
  folder with `CoinRun.stproj`: open that file with **File ▸ Open Project...**.
- You attached a debugger to the editor, as [Finding bugs: a method, the log and the debugger](../basics/debugging.md)
  showed. Without one, the steps still work with the log.
- You know that destruction happens at the end of the frame, and that the :term[fixed step]{id=fixed-step} is the clock of physics.

## A bug that lasts one frame

A game draws 60 frames each second, so one frame lasts 16.7 ms, which is 100 % of a frame at 60 frames per second. A
number that is wrong for one frame stays on the screen that long: too short for your eyes. You cannot fix what you
cannot look at, so a game maker needs two tools. One stops time, and the other makes the same moment come again.

Strata gives you both. The editor can freeze the game and run it step by step. The game also counts its own time in
fixed steps, so the same steps give the same game. The page uses both to find one planted bug.

## Play works on a copy

**Play** runs a copy of the edited scene, with its scripts, physics and sound. The copy is the **running copy**: the
game changes the copy, never your scene. **Stop** throws the copy away and shows the scene as you left it. For this
reason the coins come back after Stop, even though the ball collected them.

```mermaid caption="Play copies the edited scene into a running copy. Everything the game does happens in the copy. Stop throws the copy away." alt="A flow of three boxes. The edited scene leads by an arrow labelled Play to the running copy. The running copy leads by an arrow labelled Stop to a box that says nothing is left of the copy. The edited scene stays unchanged."
flowchart LR
	edited["Edited scene"] -- "Play copies it" --> copy["Running copy"]
	copy -- "Stop throws it away" --> gone["Nothing is left of the copy"]
```

The copy has a price. You lose anything you change while the game plays, unless it belongs to the project and not to
the scene. Step 4 shows both kinds of change.

## Why the same steps give the same game

The game does not move bodies by the length of each frame. Frames differ: one takes 1/60 s and the next 1/25 s. Strata
adds the :term[frame times]{id=frame-time} up and runs **fixed steps** of the same length, 1/60 s by default, until the time is used. Bodies,
characters and the `OnFixedUpdate` of your scripts move only in those steps.

The sketch below shows what that buys. A ball falls for one second from 3 m, with no floor. The program plays the
fall twice: with 60 frames of 1/60 s, and with 30 frames of 1/30 s. Each play moves once by the frame time and once by
a fixed step. Look at the four heights.

```cpp sketch="make-play-test-debug-fixed-step.cpp"
// A ball falls for one second, in frames of two lengths; the fixed step is 1/60 s.
#include <cstdio>

float Fall(float frameTime, int frames, bool fixedStep)
{
	float height = 3.0f, speed = 0.0f, accumulator = 0.0f;
	const float step = fixedStep ? 1.0f / 60.0f : frameTime;
	for (int frame = 0; frame < frames; frame++)
	{
		accumulator += frameTime;
		while (accumulator >= step)
		{
			speed -= 9.81f * step;
			height += speed * step;
			accumulator -= step;
		}
	}
	return height;
}

int main()
{
	std::printf("60 frames of 1/60 s: variable %.4f m, fixed %.4f m\n", Fall(1.0f / 60.0f, 60, false), Fall(1.0f / 60.0f, 60, true));
	std::printf("30 frames of 1/30 s: variable %.4f m, fixed %.4f m\n", Fall(1.0f / 30.0f, 30, false), Fall(1.0f / 30.0f, 30, true));
}
```

```text output-of="make-play-test-debug-fixed-step.cpp"
60 frames of 1/60 s: variable -1.9867 m, fixed -1.9867 m
30 frames of 1/30 s: variable -2.0685 m, fixed -1.9867 m
```

1. **Line 7:** a fixed step has its own length; without it, the step is the frame time.
2. **Lines 10–11:** the :term[accumulator]{id=accumulator} collects frame time and runs a step for each full step it holds.
3. **Lines 13–14:** one step of physics: the speed changes, then the height.
4. **Lines 23–24:** the same fall with two frame lengths, by frame time and by fixed step.

Moving by the frame time gives two different heights, because the program computes a different path for each frame
length. The fixed step gives one height for both, because both runs make the same 60 steps. Strata chose the fixed step
for this reason: a bug that shows after 200 steps shows again after 200 steps. The price is that a very slow frame runs
several steps at once, and Strata drops the steps it cannot run in time.

Two limits keep the promise honest. The inputs must be the same in each step: a person never presses a key in the same
step twice, but a command script does ([Testing a game with commands](automated-playtests.md)). The physics gives the
same results whatever the number of threads, which the engine's tests check.

## Play, step and debug the game

:::::steps

1. Press **Play** (Ctrl+P), roll the ball into two coins, then press **Stop**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   The status bar says Playing, and the Game view comes forward and takes your keyboard.
   :::
   :::tab[With a command]
   Run `play.start`. It builds changed scripts first and answers `{"state": "Play", "paused": false}`. Run `play.stop`
   to end.
   :::
   ::::

   **You should see:** the two coins vanish while you play. After Stop the scene is as you left it, with no coin in it:
   `CoinPlacer` places all five again in the copy that the next Play makes.

   **If you do not see it:** the button says it is building scripts, so wait for the build. A failed build leaves the
   game stopped; step 6 shows how to read the failure.

2. Press **Simulate** and watch only the physics run. The `CoinPlacer`, `Coin` and `CoinHud` scripts do not run, so no
   coin appears and the count does not change. No sound plays and no animation runs, so a character with a skeleton
   keeps its rest pose. Press **Stop** again.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Simulate**. A ball above the ground falls under gravity.
   :::
   :::tab[With a command]
   Run `play.simulate`, then `play.stop`.
   :::
   ::::

   **You should see:** the status bar says Simulating, a ball above the ground falls without any input, and the level
   has no coins.

   **If you do not see it:** the ball has no :term[rigid body]{id=rigid-body}, or it rests on the ground already. Raise it in the
   **Inspector** first.

3. Press **Play**, then **Pause**. The game freezes and the status bar says Paused. Press **Step** once. The game runs
   one frame with exactly one :term[fixed update]{id=fixed-update} and pauses again.

   Select a coin's root entity, `Coin`, in the Hierarchy, and read its **Rotation** in the **Inspector** before and
   after a step. The root turns; its child `coin-gold` only holds the mesh and keeps a rotation of 0.

   ```mermaid caption="One step while paused: the updates of the scripts, one fixed update where physics and the contact callbacks run, the late updates, then the destruction of the entities that the frame marked." alt="A flow of four boxes in a row: update, one fixed update, late update, destroy the marked entities."
   flowchart LR
   	update["OnUpdate"] --> fixed["One fixed update"] --> late["OnLateUpdate"] --> destroy["Destroy marked entities"]
   ```

   A step advances the game's time by one fixed step, 1/60 s. The `Coin.cpp` of [Physics](physics.md) sets `DegreesPerSecond` to 120.
   A coin then spins 120 degrees per second, so it turns $120 / 60 = 2$ degrees in each step: its rotation reads 2 degrees more after one step
   and 20 more after ten.

   The coins appear only once `CoinPlacer` has loaded their :term[prefab]{id=prefab-make}, so step a few times first.
   The status bar does not count steps. The command `play.step` with `{"steps": 10}` answers `fixedSteps`, the steps
   run since play started.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Pause**, then press **Step** as often as you want. Pressing **Pause** again resumes real time and drops the
   steps not run yet.
   :::
   :::tab[With a command]
   Run `play.start` with `{"paused": true}` and `play.step` with `{"steps": 30}`, so that the coins exist. Then
   `entity.find` with `{"tag": "Coin"}` answers the identifiers (IDs) of the five roots; each Play makes new coins with new IDs, so
   find them again after every **Play**.

   `entity.get` with `{"entity": "<the first ID>", "world": true}` answers `world.rotation.euler` in degrees, as the
   Inspector shows them: 58 on Y after 30 steps. `component.get` of its `Transform` answers the rotation as a
   :term[quaternion]{id=quaternion}, x, y, z and w, where y is the sine of half the angle: 0.4848 for 58 degrees. Run `play.step` with
   `{"steps": 1}` and read it again: 60 degrees. Then `play.step` with `{"steps": 10}`, a read, 80 degrees, and
   `play.state`.
   :::
   ::::

   **You should see:** each press of **Step** moves the coin's rotation by one fixed step's share, and nothing moves
   between presses.

   **If you do not see it:** **Step** is grey while the game runs. Press **Pause** first.

4. Press **Play**, drag the ball in the Scene view, and change a field of a script in the **Inspector**. The Inspector
   says that play discards changes when it stops. Press **Stop**. Then play again, change a value in Project Settings
   and stop: that change stays.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Drag the ball with the :term[gizmo]{id=gizmo-start} while the game plays. Type a new number into the field of a script.
   :::
   :::tab[With a command]
   Run `component.set` for the ball's `Transform` while playing; its answer carries a `warning` that the change goes
   at Stop. `script.setField` changes the live script at once.
   :::
   ::::

   **You should see:** the ball and the field change in the running game, and both are as before after Stop. The
   project setting stays, because it belongs to the project, not to the scene.

   **If you do not see it:** you changed the scene before you pressed **Play**. Edits made while the game does not play
   belong to your scene and stay.

5. While the game plays or pauses, select an entity with a script. The **Inspector** shows the fields of the live
   script, not the stored ones, so a field that the script changes moves on the screen. Pause to read a value that no
   frame moves.

   **You should see:** a field such as a timer or a counter change while you watch it.

   **If you do not see it:** only fields registered with `ST_SCRIPT_FIELD` show. A plain member of the class stays
   hidden, so write it to the log instead.

6. Break `CoinHud.cpp` by deleting the `;` at the end of a line, then press **Play**. A toast tells you the build
   failed, and the status bar shows a red pill, "Build failed", with the count of errors. Click it. The :term[Problems panel]{id=problems-panel}
   lists each error with its file and line.

   The compiler names the place where it noticed the missing `;`: the start of the next statement, often a line or two
   below the one you broke. Repair the line.

   Scripts write to the log with `Log::Info`, `Log::Warn` and `Log::Error`. The **Console** shows each line as the
   time, the source of the line (`Script` for these) and the text, in the color of its level. A red pill with the
   count of errors you have not seen opens it.

   The same lines go to a file. The editor writes `StrataEditor.log` in the `Logs` folder of its data folder. An
   exported game writes `Game.log` in the `Logs` folder of its own folder, named after the game. The data folder is
   `%LOCALAPPDATA%\Strata` on Windows, `~/.local/share/Strata` on Linux and `~/Library/Application Support/Strata` on
   macOS.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Play** with the broken script and click the pill. Read your own `Log` lines in the **Console**.
   :::
   :::tab[With a command]
   A failed `script.build` answers an error, code -32005, whose message holds the compiler's lines, such as
   `CoinHud.cpp(22,3): error C2143: syntax error: missing ';' before 'const'`: the file, then the line and the column.
   `script.status` lists the same errors in `build.last.diagnostics`, each with its `file`, `line`, `column` and
   `message`; with `{"wait": false}` the build answers at once and `script.status` tells when it ends. `log.read` with
   `{"newest": true, "limit": 20}` answers the last 20 lines of the log; without `newest` it starts at the oldest.
   :::
   ::::

   **You should see:** the pill, the toast, and the error with its file and line in **Problems**.

   **If you do not see it:** a run that crashed leaves no lines after you start the editor again. Every start empties
   the program's log file, and every editor of your user writes the same `StrataEditor.log`. Copy the file before you
   start the editor again.

7. Open `Scripts/Coin.cpp` in your debugger and put a :term[breakpoint]{id=breakpoint} on the first line of `OnTriggerEnter`. Press **Play**
   and roll into a coin. The editor freezes and the debugger shows the line. Read the :term[call stack]{id=call-stack}: the top call is your
   `OnTriggerEnter`, and the calls below it belong to the editor.

   Without a debugger, read this step and continue: step 8 finds the bug with the log alone.

   ::::tabs{sync=os}
   :::tab[Windows]
   The script build writes a program database in every configuration, so the breakpoint binds. Attach Visual Studio to
   `StrataEditor.exe` before you press **Play**, as the earlier page showed.
   :::
   :::tab[Linux]
   The editor builds scripts in its own configuration, and GCC or Clang add :term[debug information]{id=debug-information}
   in every one, Release and Dist too. The breakpoint binds. Attach `gdb` to `StrataEditor` before you press **Play**.
   :::
   :::tab[macOS]
   The same holds as on Linux: Clang builds the scripts of every editor with debug information, and the breakpoint
   binds. Attach `lldb` to `StrataEditor` before you press **Play**.
   :::
   ::::

   **You should see:** the debugger stops on the line, and the call stack lists the call that reached it.

   **If you do not see it:** the breakpoint stays hollow when the debugger has no symbols; the earlier page says how to
   fix that. A breakpoint on a line that never runs never stops.

8. Find the planted bug. Plant it first, in `CoinHud.cpp`:

   - Delete the two lines of the count from `OnUpdate`: the line that starts `const int coinsLeft` and the `SetText` of
     `m_CoinText` below it.
   - Add a new function after the line `float TimeLimit = 60.0f;`: `void OnLateUpdate(float) override`, with the body
     below between its braces. It writes the count only when it changes, and logs it with the number of the frame,
     `Time::GetFrameIndex()`.
   - Add the member `size_t m_Shown = SIZE_MAX;` after `Entity m_TimeBar;`, and `#include <cstdint>` after
     `#include <cmath>`: the header defines `SIZE_MAX`.

   ```cpp src="book:tutorials/make/play-test-debug/CoinHud.cpp#L17-L23"
   const size_t left = Scene::FindEntitiesByTag("Coin").size();
   if (left != m_Shown)
   {
   	m_Shown = left;
   	m_CoinText.GetUI().SetText("Coins left: " + std::to_string(left));
   	Log::Info("HUD shows ", left, " coins in frame ", Time::GetFrameIndex());
   }
   ```

   In `Coin.cpp`, add a log line with the frame's number as the first line inside the `if` of `OnTriggerEnter`:

   ```cpp src="book:tutorials/make/play-test-debug/CoinLogged.cpp#L38-L43"
   if (collision.Other.GetName() == "Ball")
   {
   	Log::Info("Coin collected in frame ", Time::GetFrameIndex());
   	Audio::PlayOneShotAt(m_Sound, GetTransform().GetWorldPosition());
   	GetEntity().Destroy();
   }
   ```

   The download at the end of [Result](#result) holds both files whole: `Scripts/CoinHud.cpp` as planted here, and
   `Scripts/Coin.cpp` as the fix below leaves it.

   Build, press **Play**, collect one coin and read the **Console**. It shows `Coin collected in frame 36` and then
   `HUD shows 4 coins in frame 37`: the count is one frame late. Your numbers depend on when you reach the coin, but
   they are always one apart. The commands of step 9 collect the coin in frame 36 every time.

   The count asks the scene for every entity tagged `Coin`. A frame runs every `OnUpdate`, then the fixed updates,
   where `OnTriggerEnter` collects a coin and calls `Destroy`, then every `OnLateUpdate`. Strata destroys entities
   only at the end of the frame, so in that frame the coin still exists and the count includes it. The next frame shows
   the right number, and Pause shows the wrong one as long as you look.

   With a debugger attached (step 7), you can also watch it. Put a second breakpoint on the line `const size_t left`
   and a watch on `left`. Collect a coin, :term[step over]{id=stepping-through-code} `GetEntity().Destroy()` in
   `Coin.cpp`, then continue. The watch shows 5 with 4 coins on the screen.

   To fix it, tell the scene at once that the coin is gone: change its tag before you destroy it, so no later count in
   the frame finds it. In `Coin.cpp`:

   ```cpp pseudocode
   GetEntity().SetTag("Collected"); // The count no longer finds this coin
   GetEntity().Destroy();           // Still happens at the end of the frame
   ```

   Build, press **Play**, collect a coin and read the count and the **Console**.

   **You should see:** `Coin collected in frame 36` and `HUD shows 4 coins in frame 36`, the same number: the count
   changes in the frame of the collection and never shows a coin twice. With your own play the number is yours, but
   both lines carry the same one.

   **If you do not see it:** the build failed (step 6), or the other coins have a tag other than `Coin`.

9. Run `play.start` with `{"paused": true}`, then `input.sequence` with
   `{"events": [{"step": 0, "key": "S", "action": "tap", "steps": 150}], "steps": 180}`: it holds **S** for 150 steps
   and runs 180, enough to collect a coin. Then `play.state`, and `play.stop`. Run the same commands again. A command
   script holds the same keys in the same steps ([Testing a game with commands](automated-playtests.md)), so the game
   reaches the same state each time.

   **You should see:** `fixedSteps` 180 after each run, "Coins left: 4" both times, and the ball in the same place.

   **If you do not see it:** the keys did not arrive in the same steps, or a script reads the real clock.

:::::

## Result

Coin Run counts its coins right in every frame. You can also freeze any moment of a game, step it by fixed steps, read
a script's fields live, follow a failure from its pill to its line and stop a script on a line.

## Variations

- **Other debuggers.** The page used Visual Studio. The earlier page also shows Visual Studio Code with a launch file
  and `lldb` on macOS.

  ::::tabs{sync=os}
  :::tab[Windows]
  Visual Studio Code with the C/C++ extension and `cppvsdbg` reads the same program database.
  :::
  :::tab[Linux]
  Visual Studio Code with `gdb` works for every editor, since scripts carry debug information in every configuration.
  :::
  :::tab[macOS]
  `lldb` works for every editor in the same way.
  :::
  ::::

- **Simulate to tune physics.** Press **Simulate**, watch the ball fall and bounce, and change the physics values of
  the scene until it feels right. No script runs, so nothing else moves.
- **What Strata does not have.** Scripts cannot draw debug lines or shapes, and the game has no in-game console and no
  console variables. The log and the **Inspector** stand in for them. [What Strata does not have](../appendix/not-in-strata.md)
  lists the missing features.

## Summary

- Play runs a copy of the edited scene, and Stop throws it away with every edit made while playing; project settings stay.
- Pause freezes the game, and Step runs one frame with one fixed update, 1/60 s by default.
- The Console, the editor's `StrataEditor.log` and an exported game's `Game.log` hold what scripts log.
- Destruction waits for the end of the frame, so a count taken before it still includes the entity.
- The game counts time in fixed steps, so the same steps give the same game.

## Check yourself

1. You collect three coins, press **Stop** and press **Play** again. How many coins does the level have?

   :::answer{tests="play-copy"}
   All five. Play ran a copy of the edited scene, and Stop threw the copy away with the coins it lost. The next Play
   makes a new copy, and `CoinPlacer` places all five coins in it again.
   :::

2. The game is paused. You press **Step** five times. How much game time passed?

   :::answer{tests="pause-step"}
   Five fixed steps, which is 5/60 s at the default step. Each step runs one frame with one fixed update, whatever the
   real time between your presses.
   :::

3. While the game plays you move the ball, change a :term[script field]{id=script-field} and change a value in Project Settings. After
   **Stop**, which changes remain?

   :::answer{tests="play-copy"}
   Only the change in Project Settings. The ball and the field belonged to the running copy, which Stop threw away.
   :::

4. The editor crashed during a run. You start it again and the log is empty. Why, and what should you have done?

   :::answer{tests="read-log"}
   Every start empties the log file, and every editor of your user writes the same `StrataEditor.log`. You should have
   copied or read the file before you started the editor again.
   :::

5. In `OnTriggerEnter` you call `Destroy()` on a coin and count the entities tagged `Coin` on the next line. Is the
   coin in the count?

   :::answer{tests="find-bug"}
   Yes. Destruction happens at the end of the frame, so the coin stays in the scene until then. Changing its tag first
   removes it from the count at once.
   :::

6. Two plays with the same inputs run at 30 and at 60 frames per second. Why does a fixed step make the games agree?

   :::answer{tests="same-steps"}
   Both runs make the same number of steps of the same length, and each step is computed alone. The frame time only
   decides how many steps run in a frame, never how long a step is.
   :::

## Exercises

1. **Basic.** Press **Simulate** with the ball's centre 3 m above the ground. Predict when it lands, and whether the coins
   appear. Then check in the **Inspector**.

   :::answer[Worked solution]{tests="pause-step,same-steps" solution="tutorials/make/play-test-debug/exercise-1.tutorial.json"}
   The centre falls 2.5 m, because the ball's radius is 0.5 m. The fall takes $\sqrt{2h/g}$, where $h = 2.5$ m is the drop and
   $g = 9.81$ m/s² is gravity. That is 0.71 s, about 43 fixed steps. No coin appears, because Simulate runs physics only and no script, so `CoinPlacer` places none. The
   file runs `play.simulate`, checks the state, waits for the ball to land, finds no coin and stops.
   :::

2. **Medium.** Log the ball's height with `Log::Info` in an `OnFixedUpdate`. Pause, press **Step** ten times and match
   the new lines of the **Console** with the steps you pressed.

   :::answer[Worked solution]{tests="pause-step,read-log"}
   Add `Log::Info("Ball height ", GetTransform().GetTranslation().y);` to `OnFixedUpdate`. Each **Step** runs one fixed
   update, so ten presses add exactly ten lines, whatever the pauses between presses. Resuming drops pending steps.
   :::

3. **Hard.** Extend the sketch so that it plays the fall with an even list of frame times and with an irregular list
   that adds up to the same second. Show that a fixed step gives the same height.

   :::answer[Worked solution]{tests="same-steps" solution="sketches/make-play-test-debug-irregular.cpp"}
   The program below takes the frame times as a list of ticks of 1/120 s. Whole ticks keep the sum exact: a sum of
   rounded times such as 1/60 s can fall a hair short of a step and lose it. Both lists hold 120 ticks, one second, so
   the accumulator makes 60 steps of 1/60 s in each case.

   ```cpp sketch="make-play-test-debug-irregular.cpp"
   #include <cstdio>
   #include <vector>
   float Fall(const std::vector<int>& frames)
   {
   	const float step = 1.0f / 60.0f;
   	float height = 3.0f, speed = 0.0f;
   	int accumulator = 0;
   	for (const int frameTicks : frames)
   	{
   		accumulator += frameTicks;
   		while (accumulator >= 2)
   		{
   			speed -= 9.81f * step;
   			height += speed * step;
   			accumulator -= 2;
   		}
   	}
   	return height;
   }

   int main()
   {
   	std::printf("even frames:      %.4f m\n", Fall(std::vector<int>(60, 2)));
   	std::printf("irregular frames: %.4f m\n", Fall({ 10, 20, 30, 60 }));
   }
   ```

   ```text output-of="make-play-test-debug-irregular.cpp"
   even frames:      -1.9867 m
   irregular frames: -1.9867 m
   ```

   1. **Line 3:** the function takes a list of frame times, in ticks, instead of one length.
   2. **Lines 10–11:** the accumulator collects each frame's ticks and runs a step for every 2 ticks, 1/60 s.
   3. **Lines 23–24:** two lists with the same total give the same height.
   :::

## Where it lives in Strata

- `StrataEditor/src/EditorLayer.cpp`: the buttons **Play**, **Simulate**, **Pause**, **Step** and **Stop**, and the
  status bar's pills.
- `StrataEditor/src/Editor/Commands/PlayCommands.cpp`: the commands `play.start`, `play.stop`, `play.pause`,
  `play.step`, `play.state` and `play.simulate`.
- `Strata/src/Strata/Scene/Scene.cpp`: `Scene::OnUpdateRuntime` runs the frame, the fixed steps and the end-of-frame
  destruction.
- `Strata/src/Strata/Core/Log.cpp`: the log file sink, which empties the file at each start.
- `StrataScriptCore/CMake/StrataScriptModule.cmake`: the debug information of :term[script modules]{id=script-module}.
- `Docs/Manual/GameView.md`: the engine's own guide to playing and testing in the editor.

## Further reading

- Glenn Fiedler, "Fix Your Timestep!" (gafferongames.com): why a game runs physics in fixed steps (intermediate).
- Microsoft, "Debug C++ code in Visual Studio" (learn.microsoft.com): breakpoints, watches and the call stack
  (beginner).
