---
id: make/commands
title: "Driving the editor from outside: the CLI and command scripts"
description: "Run any editor command from a terminal, scatter 200 coins, make a controller, capture a picture and repeat the work as a script."
kind: how-to
size: M
tracks: [G]
needs: [make/automated-playtests, make/animation]
time: 100
learn:
  - id: call-command
    text: run an editor command from a terminal with its parameters from a file or from standard input
  - id: read-failure
    text: fix a failed call from its exit code and the error's list of parameters
  - id: command-only
    text: run commands that no menu or button has, such as the 200-coin scatter and a store-page capture
  - id: batch-script
    text: build an atomic editor.batch and run the same steps as a command script
since: 0.3.0
status: final
---

You drive the running editor from a terminal: you send it any command, also the ones no menu or button has, and you write a script that builds content for you. Before you start:

- You have a terminal, as the [install page](../start/install.md) shows, and you know where the Strata folder is.
- You can write a command script by hand, as [Automated play-tests](automated-playtests.md) taught: a list of steps, each with a `command` and its `parameters`.
- The editor runs with Coin Run open: your own, or Checkpoint 4 at the end of [Ship the finished game](project-coin-run.md#ship-the-finished-game), the end of the Coin Run project. Later steps name the project they need and where its download is.

## The idea in one paragraph

Every menu item and every button of the editor runs a **command**: a named action with parameters, such as `entity.create`. [Commands in the editor](../editor/commands.md) explains how the editor checks them. The editor also listens on your computer for a program that asks it to run a command. That program is `StrataCLI`, the **command-line client** that sends one command and prints the answer. So you can do from a terminal everything the interface does, and a few things it does not.

:::why
Strata has one list of commands and no second path for agents. A command that exists is at once a button, a script step and a terminal call. The price is that a command is a name with JSON parameters, which reads worse than a menu.
:::

:::note
No place in the editor's window takes a typed command and runs it. The **Activity** panel only re-runs a command the editor recorded in its journal. The terminal is where you type commands.
:::

:::caution
A command that replaces the open scene, such as `scene.open`, fails while the scene has changes you have not saved. The parameter `force` discards them. A script never passes `force` for a person's work: save first, or stop and ask.
:::

## Connect, call and read an error

The first steps teach the tool. You use them for every later step.

:::::steps

1. Find the running editor.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Look at the right end of the status bar. The pill there reads `port 51234 · no agent`, with the port your editor picked. A port is the number a program uses to reach another on your computer.
   :::
   :::tab[With a command]
   Run `StrataCLI status`. It prints whether an editor answers and lists the editor sessions it knows. To start an editor yourself, run `StrataCLI launch --project <dir> --headless`, where `<dir>` is the project's folder. Add `--no-gpu` for a run with no graphics device at all.
   :::
   ::::

   **You should see:** the pill with a port, and `status` naming your editor.

   **If you do not see it:** no editor runs, or you opened a terminal in the wrong folder. `StrataCLI` is a program in the Strata folder, not a command of your terminal, so run it from there. `launch` waits until the project has opened, and prints its progress.

2. List the commands.

   ::::tabs{sync=how}
   :::tab[In the editor]
   No menu or button does this whole step: use the other tab.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command. `StrataCLI list` prints one line for each command: its name, then its description. `StrataCLI list --json` prints the same with the JSON Schema of each command's parameters, which says which names are required and which types they take.
   :::
   ::::

   **You should see:** a line for each of the :value{key="commands.count"} commands, `entity.create` and `prefab.instantiate` among them, and a few more lines at the top for the connection itself, whose names start with `rpc.`.

   **If you do not see it:** the list is long, so save it with `StrataCLI list --json > commands.json` and search that file in your code editor. The list prints every command at once. You cannot ask `list` for one.

3. Call a command that needs no parameters.

   ::::tabs{sync=os}
   :::tab[Windows]
   In PowerShell, run the program from the Strata folder with a leading `.\`.

   ```powershell
   .\StrataCLI call editor.status
   ```

   The program prints the editor's state as JSON. Every run also ends with an exit code, a number that says how it went: type `$LASTEXITCODE` and press **Enter** to see it.

   :::
   :::tab[Linux]
   In a shell, run the program from the Strata folder.

   ```sh
   ./StrataCLI call editor.status
   ```

   The program prints the editor's state as JSON. Every run also ends with an exit code, a number that says how it went: type `echo $?` and press **Enter** to see it.

   :::
   :::tab[macOS]
   In a shell, run the program from the Strata folder.

   ```sh
   ./StrataCLI call editor.status
   ```

   The program prints the editor's state as JSON. Every run also ends with an exit code, a number that says how it went: type `echo $?` and press **Enter** to see it.

   :::
   ::::

   **You should see:** a JSON answer with `engineVersion`, `project` with its name, `scene` with its `entityCount`, and `undo` with the names of the next undo and redo steps.

   **If you do not see it:** the exit code is 2 (no editor) when the editor is closed. Start it, or run `launch` as in step 1.

4. Pass parameters from a file, then from standard input. Save the text below as `find.json` in UTF-8, the format every code editor writes by default.

   ```json
   { "tag": "Coin" }
   ```

   The command `entity.find` returns the identifiers (IDs) of the entities that match every filter you give. Standard input is the text that another program sends into this one through the pipe sign `|`.

   ::::tabs{sync=os}
   :::tab[Windows]
   Quote the file argument. A bare `@find.json` stops PowerShell with an error, because it reads `@` as an operator. The second line sends the parameters through the pipe.

   ```powershell
   .\StrataCLI call entity.find '@find.json'
   '{ "tag": "Coin" }' | .\StrataCLI call entity.find -
   ```

   Both lines send the same parameters, so both print the same answer.

   :::
   :::tab[Linux]
   The `-` at the end tells the program to read the parameters from standard input.

   ```sh
   ./StrataCLI call entity.find @find.json
   echo '{ "tag": "Coin" }' | ./StrataCLI call entity.find -
   ```

   Both lines send the same parameters, so both print the same answer.

   :::
   :::tab[macOS]
   The `-` at the end tells the program to read the parameters from standard input.

   ```sh
   ./StrataCLI call entity.find @find.json
   echo '{ "tag": "Coin" }' | ./StrataCLI call entity.find -
   ```

   Both lines send the same parameters, so both print the same answer.

   :::
   ::::

   **You should see:** both lines print the same JSON, with an `entities` list. The list is empty when the scene holds no coin yet.

   **If you do not see it:** the message `is UTF-16 text; write it as UTF-8` means your file has the wrong encoding. PowerShell 5 writes UTF-16 with `>`, so save the file from the code editor. Typing the JSON in the command line itself also works on Linux and macOS, but quotes inside JSON break on Windows: that is why files and `-` exist.

5. Read an error. Call `component.set` with a parameter that does not exist, `value` instead of `values`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   No menu or button does this whole step: use the other tab.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command. Save `bad.json` with `{ "entity": "1", "component": "Transform", "value": { "Scale": [2, 2, 2] } }` and call `component.set` with `'@bad.json'` as in step 4.
   :::
   ::::

   **You should see:** the exit code 1 and, on the error stream (a second output that your terminal shows like the first), a JSON error with `code`, `message` and `data`. The message starts `Unknown parameter 'value' for component.set`. The `data` holds the command and the `parameters`: the schema of what the command takes.

   **If you do not see it:** the exit code tells the class of failure. Read the list in the next paragraph, then change `value` to `values` and call again.

:::::

The exit codes of `StrataCLI` are small numbers, and a script reads them:

| Code | Meaning |
| --- | --- |
| 0 | The command succeeded. |
| 1 | The editor answered with an error: read the JSON on the error stream. |
| 2 | No editor answers, or the connection was lost. |
| 3 | The command line itself is wrong, for example a missing method name. |
| 4 | No answer came within `--timeout` (30000 ms unless you set it). |
| 5 | The answer arrived, but `--save-image` could not save the picture. |

Code 4 is no failure. The command may still run in the editor, for example a long import. Check with `status` and wait; never start a second editor on the same project, because two editors would write the same files.

## Do what no menu can

Each step below runs one command. They need `StrataCLI call <command> '<file>'` as in step 4, written for your system. The parameters are the JSON shown. Where a step needs another project, the line before it says so.

:::::steps

1. Scatter 200 coins with one command. Start from the Coin Run checkpoint. Take `scatter.json` from the download of the Hard exercise's worked solution, at the end of [Exercises](#exercises): it places `Prefabs/Coin.stprefab` 200 times, in 10 rows of 20 coins 2 m apart. Put it in the folder where you run `StrataCLI`.

   The two first entries show its shape. Each instance gives its own Transform, so the first coin stands at x = -19, y = 0.8, z = -9 and the second 2 m further along x:

   ```json
   { "prefab": "Prefabs/Coin.stprefab", "instances": [
   	{ "components": { "Transform": { "Translation": [-19, 0.8, -9] } } },
   	{ "components": { "Transform": { "Translation": [-17, 0.8, -9] } } }
   ] }
   ```

   Run `call prefab.instantiate '@scatter.json'`. The last coin stands at x = 19, z = 9, because 20 columns of 2 m span 38 m.

   ::::tabs{sync=how}
   :::tab[In the editor]
   No menu or button does this whole step: use the other tab.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command. The editor would need 200 drops by hand. The command makes all of them as one undo step, and the answer lists the new entity IDs in the order you gave.
   :::
   ::::

   **You should see:** the Hierarchy fills with 200 coins, and the Scene view shows a field of gold. A coin whose name another coin has gets a number, so the first coin of the list is `Coin (1)`, the second `Coin (2)`, and only the last keeps the plain name `Coin`. **Undo** (**Ctrl+Z**) removes all 200 at once.

   **If you do not see it:** exit code 1 with `Instance 12: unknown key` names the entry with a spelling error. A single `instances` call takes 1 to 100,000 entries, and it refuses `parent` or `components` beside it.

2. Make an :term[animation controller]{id=animation-controller}. Open the project with the robot: Checkpoint 9 at the end of [Animate only what is seen](animation.md#animate-only-what-is-seen). First list the model's clips with `animation.info`, parameters `{ "asset": "Models/Robot/RobotExpressive.glb" }`. Each clip has an `asset` of 16 hexadecimal digits: its handle.

   Save `controller.json`, with the handles of the `Idle` and `Walking` clips in place of the two words in capitals:

   ```json
   { "path": "Animations/Scratch.stanimator",
   	"parameters": [ { "Name": "Speed", "Type": "Float", "Default": 0 } ],
   	"states": [ { "Name": "Idle", "Clip": "IDLE_HANDLE" }, { "Name": "Walk", "Clip": "WALK_HANDLE" } ],
   	"transitions": [ { "From": "Idle", "To": "Walk", "Duration": 0.15,
   		"Conditions": [ { "Parameter": "Speed", "Mode": "Greater", "Threshold": 0.1 } ] } ] }
   ```

   The file names one parameter, two states that each play a clip, and one transition. The transition fires when `Speed` rises above 0.1 and fades over 0.15 s.

   ::::tabs{sync=how}
   :::tab[In the editor]
   No menu or button does this whole step: use the other tab.
   :::
   :::tab[With a command]
   This step has no menu or button for a whole controller: run `call animation.createController '@controller.json'`. It writes the file `Animations/Scratch.stanimator`, which an :term[Animator]{id=animator} component can play through its **Controller** field.
   :::
   ::::

   **You should see:** the controller in the Content Browser under `Animations`, and an answer that lists its states and the clips each plays.

   **If you do not see it:** `is not an animation clip` means a handle belongs to another asset: copy it from the `clips` list again.

3. Preview a pose. Find the robot's ID with `entity.find` and `{ "name": "Robot" }`, then call `animation.preview` with its ID. The text below shows the shape, with the ID in capitals:

   ```json
   { "entity": "ROBOT_ID", "state": "Walk", "time": 0.4 }
   ```

   The call poses one entity at one time of one state.

   ::::tabs{sync=how}
   :::tab[In the editor]
   No menu or button does this whole step: use the other tab.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command. The viewport shows the robot posed 0.4 s into its `Walk` state, and the scene itself does not change.
   :::
   ::::

   **You should see:** a chip in the viewport reading `Previewing 'Walk' at 0.40 s` with the entity's name. Clicking the chip stops the preview. The command stops it too, with `{ "stop": true }`.

   **If you do not see it:** the message `The scene plays` means Play mode is on; press **Stop**. A preview poses only the edited scene.

4. Change a world's layers. Open the world of Checkpoint 7 at the end of [Export the world](large-worlds.md#export-the-world), and its scene `Worlds/Meadow`. The command replaces the whole list. A name alone keeps that layer's settings, and an object adds or changes one:

   ```json
   { "world": "Worlds/Meadow.stworld",
   	"layers": [ "Terrain", "Buildings", "Props", "Gameplay", { "name": "Decals", "cellSize": 32 } ] }
   ```

   The four names keep their layers as they are, and the object adds a fifth. The world is named by its file, with the `.stworld` at the end: `Worlds/Meadow` alone names no asset, and the command fails with `Parameter 'world': no asset 'Worlds/Meadow'`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   No menu or button does this whole step: use the other tab.
   :::
   :::tab[With a command]
   This step has no menu or button for a whole list: run `call world.setLayers '@layers.json'`. It is one undo step.
   :::
   ::::

   **You should see:** five layers in the world's asset panel, the new one with 32 m cells. The answer lists them too, and `Decals` streams 128 m, four of its cells. One **Undo** takes the fifth layer back.

   **If you do not see it:** removing a layer that already has cells, or changing a layer's cell size, is refused. Pass `"deleteCells": true` to move those cells to the trash, and only when you want them gone.

5. Capture a picture for a store page. Return to the Coin Run checkpoint. Save `shot.json` with the camera of the scene, a size and a quality preset, and the editor overlays off:

   ```json
   { "camera": "scene", "width": 1920, "height": 1080, "quality": "high", "overlays": false }
   ```

   The scene camera sees the game as a player does, so no grid or outline shows.

   ::::tabs{sync=how}
   :::tab[In the editor]
   No menu or button does this whole step: use the other tab.
   :::
   :::tab[With a command]
   This step has no menu or button for a file of a chosen size: run `call viewport.capture '@shot.json' --save-image store.png`. The program writes the PNG into the folder of your terminal and prints its path, not the picture's data.
   :::
   ::::

   **You should see:** `store.png` of 1920 by 1080 pixels, and an answer with `width`, `height` and `renderStats`, what the frame drew.

   **If you do not see it:** exit code 5 means the file could not be saved: check the folder. A capture needs a graphics device, so it fails in an editor started with `--no-gpu`.

6. Bake the probes and look at the global illumination. Open the courtyard of [Reflections](reflections.md), the download at the end of its [Result](reflections.md#result). That download holds the courtyard as the page starts it, with no probe yet, so first add the room's probe as that page's step 6 does. Save `probe.json` with the parameters below and call `entity.create '@probe.json'`.

   ```json
   { "name": "Room Probe", "components": { "Transform": { "Translation": [0, 1.5, 0] }, "ReflectionProbe": {} } }
   ```

   Then call `lighting.bakeProbes` with `{}` to bake every active probe. For the second call open the room of [Global illumination](gi.md) with the feature on, the download at the end of its [Result](gi.md#result). Save `gi.json` with `{ "debugView": "gi" }` and capture it with `--save-image gi.png`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   No menu or button does this whole step: use the other tab.
   :::
   :::tab[With a command]
   This step has no menu or button for the whole bake: run both calls. The first answers when the new textures are imported and lists each probe with its capture's path and whether it is `complete`.
   :::
   ::::

   **You should see:** a texture for each probe under `Assets/Lighting/`, here `Lighting/Main/` and the probe's ID with `.hdr`, and a picture of the indirect light in `gi.png`.

   **If you do not see it:** the message `The scene has no active reflection probe` means the probe is missing: add it first. The message `Stop playing first` means Play mode is on. Both commands need a graphics device.

:::::

## Build with a script

A call is one command. A script is a list of them that you can run again and again.

:::::steps

1. Run several commands as one. Return to the Coin Run checkpoint. The command `editor.batch` takes a list of `steps`, written as in a command script. A step can `bind` a value of its result to a name, and a later step reads it as `{ "$ref": "name" }`.

   The batch below places a coin and then makes it twice as large and 3 m up. The third step has a spelling error on purpose:

   ```json
   { "steps": [
   	{ "command": "prefab.instantiate", "parameters": { "prefab": "Prefabs/Coin.stprefab" }, "bind": { "coin": "/id" } },
   	{ "command": "component.set", "parameters": { "entity": { "$ref": "coin" }, "component": "Transform", "values": { "Scale": [2, 2, 2], "Translation": [0, 3, 0] } } },
   	{ "command": "component.set", "parameters": { "entity": { "$ref": "coin" }, "component": "Transfrom", "values": { "Scale": [1, 1, 1] } } }
   ] }
   ```

   Step 0 places the coin and binds its ID to `coin`. Step 1 reads the binding, and step 2 does the same with a wrong component name.

   ::::tabs{sync=how}
   :::tab[In the editor]
   No menu or button does this whole step: use the other tab.
   :::
   :::tab[With a command]
   This step has no menu or button: run `call editor.batch '@batch.json'`. The batch is **atomic** by default: when one step fails, the steps before it are undone and the batch records no undo step.
   :::
   ::::

   **You should see:** exit code 1 and an error that names the failing step by its number, 2, counted from 0. No new coin stands in the scene.

   **If you do not see it:** a step that waits for frames, such as a capture or a save, is refused before anything runs. Run those outside the batch.

2. Fix the third step, by changing `Transfrom` to `Transform`, or delete it, and run the batch again.

   ::::tabs{sync=how}
   :::tab[In the editor]
   No menu or button does this whole step: use the other tab.
   :::
   :::tab[With a command]
   Call `editor.batch` with the repaired file. The answer lists each step's result and the `bindings`.
   :::
   ::::

   **You should see:** one new coin at x = 0, y = 3, z = 0 with the scale 2. One **Undo** removes it.

   **If you do not see it:** `"atomic": false` runs every step and keeps what worked. Leave it at the default for a script that must not leave half its work.

3. Run the same steps as a command script. Save the list of `steps` alone, from its `[` to its `]`, as `bigcoin.json`. A script file starts an editor of its own, so end your editor first: call `editor.quit`, which refuses while a scene has changes you have not saved and needs `scene.save` before it. In the lines below, replace the path of `StrataEditor` with the one in your Strata folder.

   ::::tabs{sync=os}
   :::tab[Windows]
   Piping to `Write-Output` makes PowerShell wait for the program.

   ```powershell
   & "C:\Strata\StrataEditor.exe" --project . --commands bigcoin.json --quit-after-commands --no-gpu | Write-Output
   ```

   The editor opens the project, runs the script, closes and returns its exit code.

   :::
   :::tab[Linux]
   Run it from the project's folder.

   ```sh
   /opt/strata/StrataEditor --project . --commands bigcoin.json --quit-after-commands --no-gpu
   ```

   The editor opens the project, runs the script, closes and returns its exit code.

   :::
   :::tab[macOS]
   Run it from the project's folder.

   ```sh
   /Applications/Strata/StrataEditor --project . --commands bigcoin.json --quit-after-commands --no-gpu
   ```

   :::
   ::::

   **You should see:** the exit code 0 when every step worked, and 1 when one failed, with the error above the end line.

   **If you do not see it:** the script changed the scene in memory and `--quit-after-commands` closed the editor without saving it. Add a `scene.save` step at the end of the script to keep the coin.

:::::

## Result

You changed a scene from the terminal: 200 coins in one undo step, a controller file, a world's layers and a picture file, none from a menu. You also hold a script, `bigcoin.json`, that repeats a small build in a fresh editor and reports success by its exit code. Run it on a project before a change and after it, and the two exit codes tell you whether the change broke the build.

## Variations

- A long command. Wrap the call in a short script of your shell that sets `--timeout 120000`, runs the call, and treats the exit code 4 as "wait and check `status`", not as an error. The default wait is 30 s, so a long import needs the longer one.
- An editor with no window. `StrataCLI launch --project . --headless` starts one with no window that still renders, so captures work. Add `--no-gpu` for a run with no graphics device: it suits scripts that only change data, and every capture fails in it. The editor ends with `editor.quit`, or after `--idle-timeout` seconds without a client.

## Summary

- A terminal call runs any editor command: `StrataCLI call <command>` with the parameters from `'@file'` on Windows PowerShell, `@file` elsewhere, or `-` for standard input, in UTF-8.
- Exit code 1 carries the error's JSON, with the schema of the command's parameters in `data`; code 4 is no failure, and a second editor is never started.
- Commands with no menu, such as `prefab.instantiate` with `instances`, `animation.createController`, `world.setLayers` and `viewport.capture --save-image`, run from the terminal.
- `editor.batch` runs steps with `bind` and `$ref` as one atomic undo step, and the same steps run as a `--commands` script.

## Check yourself

1. Why does `StrataCLI call entity.find @find.json` fail in PowerShell, and what is the fix?

   :::answer{tests="call-command"}
   PowerShell reads a bare `@` as an operator and stops with an error. Quote the argument: `'@find.json'`. Standard input with `-` avoids files altogether.
   :::

2. A call ends with exit code 4 after 30 s. What do you do?

   :::answer{tests="read-failure"}
   Nothing is lost: the command may still run. Check `StrataCLI status` and the editor, wait, and call again with a longer `--timeout`. Never start a second editor.
   :::

3. A call fails with `Unknown parameter 'entites'`. Where do you find the right name?

   :::answer{tests="read-failure"}
   The error's `data.parameters` is the schema, and the message lists the names the command takes. `StrataCLI list --json` holds the schema of every command.
   :::

4. Why is `prefab.instantiate` with 200 `instances` better than 200 calls?

   :::answer{tests="command-only"}
   One call makes them all, and the editor makes instances that give only a Transform together, which is the fastest way. The 200 coins are one undo step, so one **Ctrl+Z** takes all of them back.
   :::

5. In a batch of five steps the fourth fails. What does the scene hold afterwards?

   :::answer{tests="batch-script"}
   The scene is as before step 1. The batch is atomic, so it undoes steps 1 to 3 and records no undo step. With `"atomic": false` the first three would stay.
   :::

## Exercises

1. **Basic.** Run `StrataCLI call editor.status` and read `undo` in the answer. Then scatter the coins of step 1 and read it again. What changed?

   :::answer[Worked solution]{tests="call-command"}
   Before the scatter `undo` is the name of your last edit. After it, `undo` names the scatter's step, one entry for 200 coins, and `redo` is empty.
   :::

2. **Medium.** Write the exit code of each call: an editor that is closed, a file `@missing.json`, and a parameter with a wrong name.

   :::answer[Worked solution]{tests="read-failure"}
   A closed editor gives 2. A missing parameter file gives 3, a wrong command line, with `cannot read the params file` on the error stream. A wrong parameter name gives 1.
   :::

3. **Hard.** Undo the scatter of 200 coins from the terminal, check that no coin is left, and bring all 200 back.

   :::answer[Worked solution]{tests="command-only batch-script" solution="tutorials/make/commands/exercise-1.tutorial.json"}
   Call `edit.undo`, then `entity.find` with `{ "tag": "Coin" }`: the `entities` list is empty. Call `edit.redo` and `entity.find` again: it lists 200 IDs. The undo and the redo each take one call, because the scatter was one step. The download of this solution holds `scatter.json`, the parameters of step 1, beside its commands.
   :::

## Where it lives in Strata

- `StrataCLI/src/CLI/CliApplication.cpp`: the commands `call`, `list`, `status`, `launch`, the reading of `@file` and `-`, and the exit codes.
- `StrataCLI/src/CLI/EditorLauncher.cpp`: how `launch` starts an editor and waits for the project.
- `StrataEditor/src/Editor/EditorCommands.cpp`: the check that makes the error for an unknown parameter.
- `StrataEditor/src/Editor/EditorPrefabCommands.cpp`, `StrataEditor/src/Editor/EditorAnimationCommands.cpp`, `StrataEditor/src/Editor/EditorWorldCommands.cpp`, `StrataEditor/src/Editor/EditorViewportCommands.cpp` and `StrataEditor/src/Editor/EditorLightingCommands.cpp`: the commands of the steps.
- `StrataEditor/src/Editor/Commands/BatchCommands.cpp`: `editor.batch`.
- `StrataEditor/src/Panels/ViewportPanel.cpp`: the preview chip.

## Further reading

- The JSON Schema site, "Understanding JSON Schema": how a schema states required names and types (beginner).
- The manual of your shell, on quoting and redirection: why quotes in JSON break on Windows (intermediate).
