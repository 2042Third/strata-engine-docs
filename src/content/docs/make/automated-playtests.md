---
id: make/automated-playtests
title: "Automated play-tests"
description: "Write a command script that plays Tetris by itself, checks an exact score and fails when a change breaks the rule."
kind: how-to
size: L
tracks: [G]
needs: [make/menus, basics/tools|start/install]
time: 60
learn:
  - id: write-script
    text: write a command script that plays Tetris with timed keys and expects an exact score
  - id: run-read
    text: run a command script from a terminal and read its exit code and its failing expect
  - id: exact-play
    text: explain why input counted in fixed steps gives the same game on every computer
  - id: test-ui
    text: build a menu button with commands and check its place and its click without looking
  - id: copy-step
    text: find the Activity panel's Copy as script and say what a replay script is
since: 0.3.0
status: final
---

You will write a play-test that the editor runs by itself. It plays a copy of Tetris with timed key presses, checks the score on the screen and fails when a change breaks a rule of the game. Before you start:

- You can open a terminal and run a program with arguments, as [Install Strata](../start/install.md) shows.
- You have read [Menus](menus.md), and you know how to press Play, pause and step a game ([Play-test and debug](play-test-debug.md)).
- You know that a game runs in fixed steps ([The script loop](script-loop.md)) and that a script has fields ([Your first script](first-script.md)).
- You have a text editor that saves plain text, and a folder where you may copy a sample.

## Why a script plays better than you

You change a rule of your game, say how fast the pieces fall. Then you must check that the game still works, so you play it for a minute. After ten changes you have played it ten times, and you remember less each time.

A script does not tire. It plays the same minute, press for press, after every change. The loop you follow is the one in the diagram: you write the script once, and then you build, play with simulated input, observe and check, again and again.

```mermaid caption="The testing loop: a script is written once, and every change to the game runs the same play and the same checks." alt="A loop of boxes. Change the game leads to build the scripts, then play with simulated keys, then observe values, then check against the expectations. A failed check leads back to change the game; a passed check leads to done."
flowchart LR
    A[Change the game] --> B[Build the scripts]
    B --> C[Play with simulated keys]
    C --> D[Observe values]
    D --> E{Check against the expectations}
    E -- failed --> A
    E -- passed --> F[Done]
```

The loop only helps when the same input gives the same result. A person fails this test. You press **Left** about every third of a second, never exactly, and a piece that falls every 0.8 s has moved or not by the time you press. Two plays then end with two different scores, and a test cannot tell a broken rule from a slow thumb.

Look at the numbers of the Tetris test you will write. It presses 13 keys within 26 fixed steps. Strata runs 60 fixed steps in a second, so the whole play lasts 26 divided by 60, about 0.43 s of game time. No person presses a key every 2 steps, and a script does it every time.

Two things must hold for a test to give the same result every time, and the page builds both. First, the game must not depend on the clock or on luck: Tetris starts from a seed, a number that fixes its random choices, so the pieces come in the same order. Second, the input must arrive at the same game step, whatever the speed of the computer. Strata counts the time of simulated input in fixed steps, never in frames or seconds, and a later section shows why.

:::why
A test that waits by the clock fails on a slow computer, and one that waits for a number of frames fails when the frame rate changes. Strata's own tests wait for a condition or count game steps, and a script of yours does the same. The check then holds on every computer.
:::

## JSON, from zero

A command script is a file written in JSON. JSON is a text format for data: a few kinds of value, written with brackets, quotes and commas. A program reads it without guessing, which is why scripts use it, and you need to write it by hand.

An object holds named values in braces. Each name is a string, which is text in double quotes, followed by a colon and a value. Pairs are separated by commas, and the last pair has no comma after it. Here is an object with four pairs:

```json
{ "name": "Ada", "lives": 3, "alive": true, "items": ["key", "map"] }
```

The value of `"lives"` is a number, written plainly (`3`, `0.25`, `-1`), without quotes. The value of `"alive"` is `true`; the other truth value is `false`, and both are written in small letters without quotes. The value of `"items"` is an array, a list in square brackets whose values are separated by commas.

Values can hold values. An object can hold an array of objects, and that is the shape of a script. A line break inside a string is written `\n`, and a quote inside a string is written `\"`. Single quotes are not JSON: `'Ada'` is an error.

Strata reads a script with care and tells you what is wrong. A path that does not exist gives `Cannot read 'Playtest.json'`. A file that is not JSON gives `'Playtest.json' is not valid JSON:` and then the parser's reason, usually a missing comma or an extra one. A step with a name Strata does not know, such as `"param"`, gives a message that starts `Step 3: unknown key 'param'` and lists the keys it knows. Strata checks the whole file before it runs the first step, so a spelling mistake costs you no half-played game.

## A command script

In Strata every action of the editor is a **command**: a named operation with parameters that answers with a result. Pressing Play runs `play.start`; creating an entity runs `entity.create`. Commands have names of the form `group.action`, and you read their results as [How to read this book](../start/how-to-read.md) shows.

A **command script** is a JSON array of steps, which the editor runs one after another, and each step is one command. A step is an object with a `command` and, when the command needs them, its `parameters`. The first line of the Tetris test is a step with no parameters:

```json
{ "command": "play.start", "expect": { "/state": { "equals": "Play" } } }
```

The step runs `play.start`, whose answer is an object that includes `state`. The key `expect` is the test: it lists what the answer must hold. Here `"/state"` is a JSON pointer, a path into the answer written with slashes. The pointer `/values/Text` means the key `values`, then the key `Text` inside it. The condition `{ "equals": "Play" }` says the value there must be the string `Play`.

An expectation has one of three forms. `equals` compares with any value and needs an exact match. `min` and `max` compare a number: `{ "min": 1 }` accepts 1 and every larger number, and `{ "max": 62 }` accepts every number up to 62. You can give `min` and `max` together. All of them compare with constants written in the file, so a check such as "moved 3 m" needs a :term[script field]{id=script-field} that computes the distance, and the test reads that field.

When an expectation fails, Strata logs one error line that names the pointer, the value it expected and the value it found. For example, `expected '/values/Text' to be "Score: 210", but it is "Score: 209"`. The script does not stop there: it runs its later steps and, at the end, the editor logs `Command script finished with errors` and exits with code 1. A script with no failure exits with code 0, which is what a build server or a person's `if` reads.

### Naming an entity

Most steps name an entity. The command takes its identifier (ID), a number of up to 16 hexadecimal digits written as a string, such as `"893AE784EA121440"`. In the editor, select the entity and press the copy button next to its ID in the Inspector (its tooltip says it copies the ID as commands and scripts take it). In a script you can also find it by name: `entity.find` with `{ "name": "<the name you gave>" }` answers a list of IDs, and a step can keep one with `"bind": { "board": "/entities/0" }`.

A later step then writes `{ "$ref": "board" }` where the ID belongs. The `bind` names a value of this step's answer, and `$ref` uses it in a later step's parameters. The sample's entities keep their IDs in the copy you make, so the Tetris test can write them out. The IDs stay the same once a scene is saved, so a test that names them keeps working.

### Edits and the scene's changes

Some steps change the scene. The test you build sets two script fields, and `script.setField` in edit mode changes the scene of the copy, so each call is an undo step and the scene counts as modified. When the test ends and the editor closes without asking, the changes you did not save are written as recovery data, and the editor offers them the next time you open the project. A good test therefore ends as the sample's does: it stops play, calls `edit.undo` once for each edit, and checks with `scene.info` that `/modified` is `false`.

## Exact play

A running game is made of fixed steps, 60 in a second by default. In each step the game reads its input, moves its objects and updates its state. A frame is one picture. A fast computer draws many frames in a second and a slow one draws few, but both run 60 steps for each second of game time.

**Simulated input** is input that a command presses for the game, in place of a keyboard, a mouse or a gamepad. The input commands (`input.key`, `input.mouseButton`, `input.mouseMove`, `input.scroll`, `input.click`, `input.type`, `input.gamepadButton`, `input.gamepadAxis` and `input.action`) act like a virtual device. They count how long a key stays down in fixed steps: `input.key` with `{ "key": "Left", "steps": 3 }` holds **Left** for three steps. The command `input.releaseAll` lets go of everything, and `input.state` lists what is held.

One key at a time is not enough for a play. An **input sequence** is a timed list of input events, each with the fixed step at which it happens, that Strata plays in one command. The command `input.sequence` takes `steps`, the length of the whole play, and `events`. It pauses the game, then runs exactly one step per frame with the events of that step, and it resumes the game at the end if the game ran before.

Look at one event of the Tetris test: `{ "step": 6, "key": "Space", "action": "tap" }`. At step 6 the game sees **Space** pressed, and the tap lasts one step. Nothing in it depends on time. A computer at 30 frames per second and one at 240 run step 6 in the same state. The game state moves only when a step runs, and the sequence runs one step per frame.

The design has one reason: a test that sleeps for half a second between keys gets a different game on every computer, and a test that says "at step 6" gets one game everywhere. The seed fixes the pieces, the sequence fixes the moments, and the paused wait fixes the rest. The page [Simulated input](../input/simulated.md) shows how these events merge with a real keyboard, and [Stepping a paused game](../editor/stepping.md) shows how the editor steps.

### Starting paused and stepping

The command `play.start` with `{ "paused": true }` starts the game paused before its first fixed step, so nothing has moved yet. Then `play.step` with `{ "steps": 120 }` runs 120 steps, one per frame, and answers only after the last one ran: its answer has `stepsRun`, which a test can expect to be 120. Frames run as fast as the computer allows, so 600 steps do not take 10 s.

Use this when the game must be at a known state before the test acts. The Tetris test does not start paused. It sets `StartInterval` to 100, which makes a piece fall once in 100 s, so the few steps before the sequence cannot move a piece.

### Waiting for an outcome

Some outcomes take game time: a ball must stop rolling, or a timer must run out. A step with `until` repeats its command until its `expect` holds, and stops when `steps` fixed steps have run or `seconds` of real time have passed, whichever is first. Without `seconds` it waits at most 300 s, and `until` needs an `expect`: without one the script is refused before it starts. When the game is paused, each attempt first runs one fixed step, so the wait counts game time. This step waits for the game over text of Tetris:

```json
{ "command": "component.get", "parameters": { "entity": "3AB0E777DCA23EC4", "component": "UIText" },
  "expect": { "/values/Text": { "equals": "GAME OVER\nPress R or Enter to play again" } }, "until": { "steps": 3000, "seconds": 60 } }
```

The text of the sample has two lines, so the expected string writes the line break as `\n`. The step asks the same question after every step until the text says game over, and fails if it takes more than 3000 steps or 60 s. The Tetris sample's own script instead waits with `editor.wait` for 300 frames. That wait counts frames, so it depends on the computer, and this book never uses it as a model. Your scripts wait with `until`.

## What a test can read

A test is only as good as what it can see. A few commands cover most games:

- `component.get` reads a component's values, such as the `Text` of a `UIText`. `entity.get` reads the whole entity.
- `script.get` reads a script's fields and whether its module is live (`/scripts/0/live`). Fields change while the game runs, so a script that counts its own score makes the best thing to check.
- `editor.status` has `/errors/unread`, the number of errors logged since the last `log.read`. `log.read` with `minLevel` set to `Warn` lists warnings and errors.
- `physics.stats` gives body counts, such as `/sleep/awake`. `audio.state` lists the sounds that play, and `/oneShots/played` counts the :term[one-shot]{id=one-shot} sounds since play started. `input.state` shows what simulated input holds.

When a person must look, a **viewport capture** is a picture of the viewport, saved to a file by a command. The command is `viewport.capture` with `width`, `height` and `path`. With `live`, a `camera` and `atFixedStep`, it returns what the running game showed at that fixed step, at the size of the view, so the picture is the same every time.

The answer of `viewport.capture` says whether the picture is settled. `/complete` is true when the picture lacks nothing; otherwise `/incomplete` lists the fields that say what it lacks, such as `/pendingAssets` for assets still loading or `/screenSpaceReflectionsPending`. Every wait of the command has a limit, and the command succeeds when a limit runs out, so a script that needs a settled picture expects `/complete` to equal `true`.

## Record and replay

You do not have to type every step. Strata records every command the editor runs, including those that your clicks in menus and panels run, in the **activity journal**. Open it with **View ▸ Activity**. Each row is one command, with its parameters and result, and the **Copy as script** button of a selected row copies that command as a step you can paste into a script. A row whose parameters the journal had to shorten cannot be copied, and the button is dim.

A **replay** is a script made from a session's commands, run again to repeat the session. Its later steps refer to the results of earlier ones with `bind` and `$ref`, because an ID that one run created differs in the next. Copying one row gives you a step; the whole session as a replay script, and the test you make from it, is the subject of [Working with an agent](with-an-agent.md).

What Strata does not do here: an exported game runs no command script. The commands, the simulated input and the expectations work in the editor only, and a play-test is a test of the project that you open in the editor.

## Write and run the Tetris test

The steps below build the test in two stages. No menu or button runs a command script: you write a file, then you run a command in a terminal. The real test in the engine's repository, `StrataTests/Editor/TetrisCommands.json.in`, is the model. Its first 24 lines are this excerpt, which the steps rebuild in your file.

```json src="StrataTests/Editor/TetrisCommands.json.in#L1-L24"
[
	{ "command": "play.start", "expect": { "/state": { "equals": "Play" }, "/built/build": { "min": 1 } } },
	{ "command": "script.get", "parameters": { "entity": "72E590A9EEB83AFC", "class": "TetrisBoard" }, "expect": { "/scripts/0/live": { "equals": true } } },
	{ "command": "play.stop", "expect": { "/state": { "equals": "Edit" } } },
	{ "command": "script.setField", "parameters": { "entity": "72E590A9EEB83AFC", "class": "TetrisBoard", "field": "LinesPerLevel", "value": 1 } },
	{ "command": "script.setField", "parameters": { "entity": "72E590A9EEB83AFC", "class": "TetrisBoard", "field": "StartInterval", "value": 100 } },
	{ "command": "ui.layout", "parameters": { "entity": "893AE784EA121440", "screen": [1280, 720] },
		"expect": { "/elements/0/rect": { "equals": [70, 70, 131.677734375, 42.1875] } } },
	{ "command": "ui.layout", "parameters": { "entity": "893AE784EA121440", "screen": [2560, 1440] },
		"expect": { "/elements/0/rect": { "equals": [140, 140, 263.35546875, 84.375] } } },
	{ "command": "play.start", "expect": { "/state": { "equals": "Play" } } },
	{ "command": "component.get", "parameters": { "entity": "893AE784EA121440", "component": "UIText" }, "expect": { "/values/Text": { "equals": "Score: 0" } } },

	{ "command": "input.key", "parameters": { "key": "F" }, "expect": { "/held/keys": { "equals": [] } } },

	{ "command": "input.sequence", "parameters": { "steps": 26, "events": [
		{ "step": 0, "key": "Left", "action": "tap" }, { "step": 2, "key": "Left", "action": "tap" }, { "step": 4, "key": "Left", "action": "tap" }, { "step": 6, "key": "Space", "action": "tap" },
		{ "step": 8, "key": "Up", "action": "tap" }, { "step": 10, "key": "Z", "action": "tap" }, { "step": 12, "key": "Down", "action": "tap" }, { "step": 14, "key": "Space", "action": "tap" },
		{ "step": 16, "key": "Right", "action": "tap" }, { "step": 18, "key": "Right", "action": "tap" }, { "step": 20, "key": "Right", "action": "tap" }, { "step": 22, "key": "Right", "action": "tap" }, { "step": 24, "key": "Space", "action": "tap" }
	] }, "expect": { "/stepsRun": { "equals": 26 } } },

	{ "command": "component.get", "parameters": { "entity": "479A9674867A5955", "component": "UIText" }, "expect": { "/values/Text": { "equals": "Lines: 1" } } },
	{ "command": "component.get", "parameters": { "entity": "893AE784EA121440", "component": "UIText" }, "expect": { "/values/Text": { "equals": "Score: 209" } } },
	{ "command": "component.get", "parameters": { "entity": "25892A97AD67432E", "component": "UIText" }, "expect": { "/values/Text": { "equals": "Level: 2" } } },
```

1. **Line 2:** the test begins in play mode, so this step expects the state `Play` and a script build that ran (`/built/build` at least 1).
2. **Lines 5–6:** `script.setField` runs in edit mode and sets `LinesPerLevel` to 1 and `StartInterval` to 100, so one cleared line raises the level and no gravity moves a piece.
3. **Lines 7–10:** `ui.layout` lists where the score text lies at two screen sizes, without drawing: the 2560 by 1440 rectangle is exactly twice the 1280 by 720 one.
4. **Lines 16–20:** the input sequence taps 13 keys across 26 steps and expects `stepsRun` to be 26.
5. **Lines 22–24:** the three expectations that matter: one line cleared, score 209 and level 2.

The score 209 comes from the rules of the sample. A line cleared at level 1 gives 100 points. A soft drop of one row gives 1 point and a hard drop gives 2 for each row, so the drops of this play give the other 109. The level is read before the line count rises, so the line is scored at level 1, and then the level becomes 1 + 1 / 1 = 2 with `LinesPerLevel` at 1.

The excerpt ends at line 24 because the sample's script then waits with frames, which the page does not copy. The excerpt also edits the scene, so the real script ends with these lines:

```json src="StrataTests/Editor/TetrisCommands.json.in#L36-L41"
{ "command": "component.get", "parameters": { "entity": "479A9674867A5955", "component": "UIText" }, "expect": { "/values/Text": { "equals": "Lines: 0" } } },

{ "command": "play.stop", "expect": { "/state": { "equals": "Edit" } } },
{ "command": "edit.undo" },
{ "command": "edit.undo" },
{ "command": "scene.info", "expect": { "/modified": { "equals": false } } },
```

1. **Lines 39–40:** one `edit.undo` for each of the two `script.setField` edits.
2. **Line 41:** `scene.info` must answer `/modified` as `false`: the test left nothing behind.

:::::steps

1. Make a copy of Tetris, then close the editor.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **File ▸ Open Sample ▸ Tetris**, pick an empty folder for the copy, and wait until the project opens. Then close the editor: the test starts its own editor, and it should be the only one that works on the folder.
   :::
   :::tab[With a command]
   Any running editor takes the call, one with a project open or one that shows only its launcher, as `StrataCLI launch` starts it. Run `project.openSample` with `{ "sample": "Tetris", "directory": "<an absolute path of an empty folder>" }`. Then close the editor with `editor.quit`, which takes no parameters.
   :::
   ::::

   **You should see:** the folder holds `Tetris.stproj`, an `Assets` folder and a `Scripts` folder.

   **If you do not see it:** the copy needs an empty folder, or one that does not exist yet. Choose another, and keep its path: it is the project's folder in the next steps.

2. Create the smallest test: a file `Playtest.json` in the project's folder (beside `Tetris.stproj`), written with your text editor. The script starts play, reads the text of the score label, expects `Score: 0` and stops play.

   ```json
   [
   	{ "command": "play.start", "expect": { "/state": { "equals": "Play" } } },
   	{ "command": "component.get", "parameters": { "entity": "893AE784EA121440", "component": "UIText" },
   		"expect": { "/values/Text": { "equals": "Score: 0" } } },
   	{ "command": "play.stop", "expect": { "/state": { "equals": "Edit" } } }
   ]
   ```

   **You should see:** a file of 6 lines in the folder. Tabs or spaces do not matter: JSON ignores them.

   **If you do not see it:** some editors add `.txt`, giving `Playtest.json.txt`. Rename the file so that its name ends in `.json`.

3. Run the script with a terminal that stands in the project's folder. The first run builds the scripts of the copy, so it takes longer.

   ::::tabs{sync=os}
   :::tab[Windows]
   Run the command with the full path of the editor in quotes, and pipe it into `Write-Output` so that PowerShell waits for the editor to end, as the install page taught:

   ```powershell
   & "C:\Strata\StrataEditor.exe" --project . --commands Playtest.json --quit-after-commands --no-gpu | Write-Output
   $LASTEXITCODE
   ```

   The first line runs the editor on the folder `.` (the current one); the second prints its exit code.
   :::
   :::tab[Linux]
   Run the editor with its full path, then print the exit code:

   ```sh
   /opt/strata/StrataEditor --project . --commands Playtest.json --quit-after-commands --no-gpu
   echo $?
   ```

   The first line runs the editor on the folder `.` (the current one); the second prints its exit code.
   :::
   :::tab[macOS]
   Run the editor with its full path, then print the exit code:

   ```sh
   /Applications/Strata/StrataEditor --project . --commands Playtest.json --quit-after-commands --no-gpu
   echo $?
   ```

   :::
   ::::

   Replace the path with the one of your release folder. On macOS too the first line runs the editor on the folder `.` and the second prints its exit code. The option `--no-gpu` runs the editor without a graphics device and without a window.

   **You should see:** log lines for each command, then `Command script finished (3 commands)`, and the exit code `0`. The first run also logs a warning that the scripts of `Tetris` are not built yet, then the build's lines and `Script build 1 finished in` a few seconds; later runs skip them.

   **If you do not see it:** `Cannot read 'Playtest.json'` means the terminal is not in the project's folder or the name differs. A line with `unknown key` names the step with the spelling mistake. On Windows, a prompt that returns at once and prints nothing means you omitted `| Write-Output`. What you have not saved in an open editor is not tested: the test reads the project from disk.

4. Replace the content of `Playtest.json` with the whole test. It sets the two fields, plays the 26 steps and checks the three texts, then it cleans up. The two `script.setField` steps come before `play.start`: they run in edit mode, and the copy of the scene that plays then holds the new values.

   ```json
   [
   	{ "command": "script.setField", "parameters": { "entity": "72E590A9EEB83AFC", "class": "TetrisBoard", "field": "LinesPerLevel", "value": 1 } },
   	{ "command": "script.setField", "parameters": { "entity": "72E590A9EEB83AFC", "class": "TetrisBoard", "field": "StartInterval", "value": 100 } },
   	{ "command": "play.start", "expect": { "/state": { "equals": "Play" } } },
   	{ "command": "input.sequence", "parameters": { "steps": 26, "events": [
   		{ "step": 0, "key": "Left", "action": "tap" }, { "step": 2, "key": "Left", "action": "tap" }, { "step": 4, "key": "Left", "action": "tap" }, { "step": 6, "key": "Space", "action": "tap" },
   		{ "step": 8, "key": "Up", "action": "tap" }, { "step": 10, "key": "Z", "action": "tap" }, { "step": 12, "key": "Down", "action": "tap" }, { "step": 14, "key": "Space", "action": "tap" },
   		{ "step": 16, "key": "Right", "action": "tap" }, { "step": 18, "key": "Right", "action": "tap" }, { "step": 20, "key": "Right", "action": "tap" }, { "step": 22, "key": "Right", "action": "tap" }, { "step": 24, "key": "Space", "action": "tap" }
   	] }, "expect": { "/stepsRun": { "equals": 26 } } },
   	{ "command": "component.get", "parameters": { "entity": "479A9674867A5955", "component": "UIText" }, "expect": { "/values/Text": { "equals": "Lines: 1" } } },
   	{ "command": "component.get", "parameters": { "entity": "893AE784EA121440", "component": "UIText" }, "expect": { "/values/Text": { "equals": "Score: 209" } } },
   	{ "command": "component.get", "parameters": { "entity": "25892A97AD67432E", "component": "UIText" }, "expect": { "/values/Text": { "equals": "Level: 2" } } },
   	{ "command": "play.stop", "expect": { "/state": { "equals": "Edit" } } },
   	{ "command": "edit.undo" },
   	{ "command": "edit.undo" },
   	{ "command": "scene.info", "expect": { "/modified": { "equals": false } } }
   ]
   ```

   1. **Lines 2–3:** the two edits, one undo step each.
   2. **Lines 5–9:** the 13 timed events, a key for every second step, and the length of the play.
   3. **Lines 10–12:** what the screen must show after the sequence.
   4. **Lines 13–16:** stop, undo twice and check that the scene has no changes.

   **You should see:** nothing yet, until you run it in the next step. The file has 17 lines.

   **If you do not see it:** a JSON error names a position. A missing comma after a step is the usual cause, and `Step 4: unknown key` points at a wrongly spelled name.

5. Run the same command as in step 3.

   **You should see:** a log line from the game, `Tetris: cleared 1 line; score 209, lines 1, level 2`, then `Command script finished (11 commands)` and the exit code `0`.

   **If you do not see it:** `Command script finished with errors` and the exit code `1` mean an expectation failed. Read the line above it: it names the step and the two values. A score other than 209 means a step of the sequence moved, so compare your events with the excerpt line for line.

6. Make the test fail on purpose. Change `"Score: 209"` to `"Score: 210"` in your file, run it again, then read the output.

   **You should see:** `component.get: expected '/values/Text' to be "Score: 210", but it is "Score: 209"`, then `Command script finished with errors` and the exit code `1`. The later steps still ran.

   **If you do not see it:** if the exit code is `0`, you saved the file in another folder. Change the value back to 209 when you are done.

:::::

## Result

You have a test file that fails when the score rule changes. It sets two fields, plays 26 fixed steps of Tetris with 13 key taps, reads three texts from the screen, and leaves the project as it found it. The same file gives the same result on a slow laptop and on a fast desktop, and its exit code says passed (0) or failed (1).

Run it after every change to the game. A test that runs only when you remember it does not protect you.

## Variations

**Test a menu without looking.** You test a game's user interface (UI) with commands too. The command `ui.create` builds an element in one undo step, and `ui.layout` gives the rectangle of every element at any screen size without drawing. The command `ui.hitTest` names what lies under a point, and `input.click` presses a button in a running game.

The script below builds a button and checks that something you can press lies at the center of two screen sizes. Then it clicks the button in play and cleans up. The script works on your copy of Tetris. With the name of your own button it works on the end of [Menus](menus.md).

```json
[
	{ "command": "ui.create", "parameters": { "type": "button", "name": "Play Button", "text": "Play", "anchor": "middleCenter", "size": [200, 60] }, "bind": { "button": "/entity" } },
	{ "command": "ui.hitTest", "parameters": { "position": [640, 360], "screen": [1280, 720] }, "expect": { "/interactable": { "equals": true } } },
	{ "command": "ui.hitTest", "parameters": { "position": [1280, 720], "screen": [2560, 1440] }, "expect": { "/interactable": { "equals": true } } },
	{ "command": "play.start" },
	{ "command": "input.click", "parameters": { "entity": { "$ref": "button" } }, "expect": { "/clicked": { "equals": true } } },
	{ "command": "play.stop" },
	{ "command": "edit.undo" },
	{ "command": "scene.info", "expect": { "/modified": { "equals": false } } }
]
```

1. **Line 2:** no parent is named, so Strata makes a canvas for the button, and `bind` keeps the button's ID as `button`.
2. **Lines 3–4:** the same question at two screen sizes: the button is anchored at the middle, so the middle of each screen must hit something that can be pressed.
3. **Line 6:** `input.click` moves the pointer to the button's center and taps there. It fails, changing nothing, when something else covers the center.
4. **Lines 7–9:** stop, undo the one edit and check that the scene has no changes.

**A smoke test of your own game.** A smoke test is the shortest play that proves the game starts. Start paused, run 120 steps and check that no error was logged:

```json
[
	{ "command": "play.start", "parameters": { "paused": true }, "expect": { "/state": { "equals": "Play" } } },
	{ "command": "play.step", "parameters": { "steps": 120 }, "expect": { "/stepsRun": { "equals": 120 } } },
	{ "command": "editor.status", "expect": { "/errors/unread": { "equals": 0 } } },
	{ "command": "play.stop" }
]
```

The engine's own smoke script, `SmokeCommands.json.in`, works the same way on a new project. It lives in the engine's repository, not in the release archive, which holds the programs, the samples, the script library, the manual and the skills.

**A physics play-test.** A physics game settles over many steps, and how many depends on the scene. Pause, then wait with `until`, as the Physics Playground's test does. One of its steps looks like this one, which waits until at most 62 bodies are awake:

```json
{ "command": "physics.stats", "expect": { "/sleep/awake": { "max": 62 } }, "until": { "steps": 1200, "seconds": 600 } }
```

**A sound test.** Add one step after the sequence of step 4: `{ "command": "audio.state", "expect": { "/oneShots/played": { "min": 1 } } }`. It passes when the game played a one-shot sound since play started, and it works without a sound device.

## Summary

- A command script is a JSON array of steps. A step's `expect` checks its answer with `equals`, `min` or `max` at a JSON pointer, so a script can play Tetris with timed keys and expect an exact score.
- Run it with `StrataEditor --project . --commands Playtest.json --quit-after-commands` from the project's folder: exit code 0 means it passed, and 1 means a step or an expectation failed, with the error line above the end line.
- Simulated input counts in fixed steps, `input.sequence` plays timed events one step per frame, and a seed fixes the random choices, so the same test gives the same game on every computer.
- `ui.create`, `ui.layout`, `ui.hitTest` and `input.click` test a menu without looking, and the test undoes its edits so that the scene keeps no changes.
- The Activity panel records every command, and **Copy as script** turns a row into a step; a replay script is a session's commands, with later steps using earlier results through `bind` and `$ref`.

## Check yourself

1. Why does the Tetris test set `StartInterval` to 100 before it plays?

   :::answer{tests="write-script exact-play"}
   A piece then falls once in 100 s, so gravity cannot move a piece between the few steps that run before the sequence and the sequence itself. Only the tapped keys move pieces, so the score is exact.
   :::

2. The test exits with code 1 and the last log line is `Command script finished with errors`. Where do you look next?

   :::answer{tests="run-read"}
   At the log lines above it. A failed step has a line of the form `expected '<pointer>' to be <value>, but it is <value>`, which follows the step's command. The script ran all its steps, so several such lines can be there.
   :::

3. A friend runs the same script on a computer that draws 30 frames per second, and you run it at 144. Do the scores differ?

   :::answer{tests="exact-play"}
   No. The command `input.sequence` pauses the game and runs one step per frame, with the events of that step. The game state moves only when a step runs, so the frame rate changes how long the test takes and nothing else.
   :::

4. What does `ui.hitTest` give you that `ui.layout` does not?

   :::answer{tests="test-ui"}
   The command `ui.layout` lists every rectangle at a screen size. The command `ui.hitTest` takes one point and names the element a player would hit there, with the button that a click would press. Together they check where elements are and what a click reaches.
   :::

5. You select a row of the Activity panel and **Copy as script** is dim. Why?

   :::answer{tests="copy-step"}
   The journal shortened that command's parameters, because they were large, so it cannot write them back as a step.
   :::

## Exercises

1. **Basic.** Make the Tetris test fail with one changed field: set `LinesPerLevel` to 2 in the test, leave the expectations as they are and run it. Read the output and say which `expect` failed and why.

   :::answer[Worked solution]{tests="run-read write-script" solution="tutorials/make/automated-playtests/exercise-1.tutorial.json"}
   Only the level fails: `expected '/values/Text' to be "Level: 2", but it is "Level: 1"`. The level is the start level 1 plus the lines divided by `LinesPerLevel`, and 1 line divided by 2 is 0 when the game rounds down. The score stays 209, because the line was scored at level 1 in both runs. The exit code is 1.
   :::

2. **Medium.** Add to the test, before its clean-up, a check that the game ends. Set `MinInterval` and `StartInterval` to 0.01 and wait with `until`, without frames.

   :::answer[Worked solution]{tests="exact-play write-script"}
   After the `Level: 2` check, add two `script.setField` steps. Then add a step like the one in the section on waiting, with the whole game over text of entity `3AB0E777DCA23EC4` and an `until` of 3000 steps and 60 s. The game runs during these edits, so they change only the running copy, and `play.stop` throws them away: add no `edit.undo`, and keep `scene.info` last. The wait counts steps and seconds, so a slow computer fails it only when the game needs more than 60 s.
   :::

## Where it lives in Strata

- `StrataEditor/src/Editor/EditorCommandRunner.cpp`: the command script's loading, its `expect`, `bind`, `$ref` and `until`, and the failure messages.
- `StrataEditor/src/EditorLayer.cpp`: `--commands`, the exit code 1 of a failed script and `--quit-after-commands`.
- `StrataEditor/src/Editor/EditorInputCommands.cpp`: the `input.*` commands, `input.sequence` and `input.click`.
- `StrataEditor/src/Editor/EditorUICommands.cpp`: `ui.create`, `ui.layout` and `ui.hitTest`.
- `StrataEditor/src/Panels/ActivityPanel.cpp`: the Activity panel and **Copy as script**.
- `StrataTests/Editor/TetrisCommands.json.in`: the Tetris sample's test, which the engine's tests run.

## Further reading

- The JSON data format, described at json.org: the whole grammar on one page, for beginners.
- Martin Fowler, "Eradicating Non-Determinism in Tests": why a test that depends on time or luck cannot be trusted, for intermediate readers.
