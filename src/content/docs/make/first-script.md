---
id: make/first-script
title: "Your first script"
description: "Write a script that makes Coin Run's coins spin, then break it on purpose to read a build error and a crash, and change it while the game plays."
kind: tutorial
size: M
tracks: [G, B]
needs: [make/lighting, basics/tools|start/install]
time: 75
learn:
  - id: create-build
    text: create, write and build a script class that turns the coins of Coin Run
  - id: attach-field
    text: add the script to the coin prefab and change its field for one coin
  - id: read-errors
    text: find a build error and a crash in the Problems panel and fix them
  - id: hot-reload
    text: explain what hot reload keeps and what it starts over
since: 0.3.0
status: final
---

## What you will make

You write your first script, a short piece of C++ that makes every coin of Coin Run spin. Then you break it twice on purpose, so that you know what the editor shows when a build fails and when a script crashes.

::figure{id=result}

## What you need

- Coin Run as [Lighting a scene](lighting.md) left it: lit for play, with five instances of the :term[prefab]{id=prefab-make} `Prefabs/Coin.stprefab`.
- The build tools and a code editor that [Install Strata](../start/install.md) checked.
- About 75 minutes. You import no files: you type every line yourself.

You have never programmed, and that is fine. Every line you see gets a sentence on what it does, at the level of names. [How to read code](../start/how-to-read.md) taught the habit: read a name as an English word and guess. [Programming 1](../basics/programming-1.md) starts next and teaches each idea from zero on this same script.

## Create the script

A game's rules are code. Strata lets you write that code as a **script class**, a class (a named bundle of values and actions) built on the engine's `Script`. The engine creates one instance of it for each entity that carries it.

Your script includes the software development kit (SDK). The **SDK** is the folder of header files `StrataScriptCore/Include/StrataScript/` that tells your code what the engine offers.

All the `.cpp` files of your project's `Scripts` folder are built together into one **script module**, a shared library that the editor loads while the game plays. The scripts never link the engine itself, so the engine can contain a mistake of yours, as you see at the end.

You write the code in a program of your choice. Strata calls it the **external editor**, a code editor that is not part of Strata, and it opens your script files there. The setting is yours, kept with your preferences and not in the project, and Strata starts the program directly and not through a shell. A project that you download can therefore never choose what program runs on your machine.

:::::steps

1. Choose your code editor.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open **File ▸ Preferences...**, then the External Editor page. Click an editor in the list of those found (`VS Code`, `Visual Studio` or `CLion`), then **Apply**.
   :::
   :::tab[With a command]

   ```json
   { "command": "preferences.set", "parameters": { "section": "Editor.ExternalEditor", "value": { "Command": "code -g {file}:{line}:{column}" } } }
   ```

   :::
   ::::

   **You should see:** the page shows which program the command starts.

   **If you do not see it:** when no editor was found, the list holds only examples. Click one or type a command by hand, with `{file}` where the file's name goes. **Apply** refuses a program it cannot find.

   ::figure{id=prefs}

2. Create the script.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open **Scripts ▸ New Script...**. Type `Coin` in the Class name field, over the grey example `PlayerController` it shows, leave the Empty class box clear and click **Create**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.create", "parameters": { "class": "Coin", "open": true } }
   ```

   :::
   ::::

   **You should see:** `Scripts/Coin.cpp` opens in your code editor, and the status bar says "Building" while the scripts build for the first time. The answer of `script.create` names the program under `openedWith`.

   **If you do not see it:** the dialog shows a red line when it refuses the name. It refuses names that are not valid C++ names, names that your scripts already use and names that the SDK uses. If the file opens in another program, your setting names no program: Strata then opens it with the program your system uses for `.cpp` files, and `openedWith` reads `the default application`. Return to step 1. If no program opened at all, the Console says why: open the file from the Content Browser's **Scripts** root.

   ::figure{id=new-script-dialog}

:::::

### Read the template

:::question
Which line is a class, and what is a field? See [Programming 3](../basics/programming-3.md) for classes and [Programming 1](../basics/programming-1.md) for values.
:::

The new file holds the template below, without the four comment lines that start it. Read it once with the next paragraph beside you. The word after `class` is the name you typed.

```pseudocode
#include "StrataScript/StrataScript.h"

using namespace Strata;

class Coin : public Script
{
public:
	float Speed = 1.0f;

	// When the entity starts playing (its fields hold the scene's values by now).
	void OnCreate() override
	{
	}

	// Every frame; deltaTime is the frame's game time in seconds.
	void OnUpdate([[maybe_unused]] float deltaTime) override
	{
	}
};

ST_SCRIPT_CLASS(Coin)
{
	ST_SCRIPT_FIELD(Speed);
}
```

1. **Lines 1–3:** the first line brings in the SDK, and the third says that names from Strata, such as `Script`, need no prefix.
2. **Line 5:** the class `Coin` is built on the SDK's `Script`, so it inherits what every script can do.
3. **Lines 7–8:** `public:` makes what follows usable from outside the class, which the engine needs for fields. `Speed` is a field, a number with a default of `1.0f`.
4. **Lines 10–18:** two functions that the engine calls for you. `override` says that they replace the empty versions in `Script`.
5. **Lines 21–24:** `ST_SCRIPT_CLASS` registers the class with the engine, and `ST_SCRIPT_FIELD` registers the field, so that the Inspector can show it.

`OnCreate` runs once when the entity starts playing. `OnUpdate` runs every frame, and `deltaTime` is the seconds that frame took. The `[[maybe_unused]]` before it tells the compiler that the body may leave the number unused, so that an empty body raises no warning. A frame at 60 frames per second has a `deltaTime` of 0.0167 s.

:::rule
Do the game's setup in `OnCreate`, never in the constructor of the class. The module makes one instance of every class when it loads, to read the defaults of the fields, and that instance has no entity to read. [The script loop](script-loop.md) says when each function runs.
:::

::checkpoint{stage=1}

::figure{id=scripts-root}

## Make the coins spin

A coin turns a little each frame. How little? Take a turn speed of 90 degrees per second. At 60 frames per second a frame lasts 0.0167 s, so the coin turns 90 × 0.0167 = 1.5 degrees per frame, and 60 frames add up to 90 degrees.

On a slower computer at 30 frames per second a frame lasts 0.0333 s, and the coin turns 3 degrees per frame: the same 90 degrees in one second. Multiplying by `deltaTime` makes the speed independent of the frame rate.

A **field** is a named value that belongs to a class.

A **script field** is a field that the script registers with `ST_SCRIPT_FIELD`. The Inspector shows it, each entity keeps its own value, and the value survives a rebuild while the game plays.

:::question
What are a function, inheritance and `override`? See [Programming 2](../basics/programming-2.md) and [C++ classes](../basics/cpp-classes.md).
:::

[Rotations](transforms-units.md) taught the turn itself: an angle around an axis, in radians. The file below replaces the template, and the list after it reads the lines that matter.

```cpp src="book:tutorials/make/first-script/Coin.cpp#L1-L21"
#include "StrataScript/StrataScript.h"

using namespace Strata;

class Coin : public Script
{
public:
	float DegreesPerSecond = 90.0f;

	void OnUpdate(float deltaTime) override
	{
		TransformComponent transform = GetTransform();
		const glm::quat turn = glm::angleAxis(glm::radians(DegreesPerSecond * deltaTime), glm::vec3(0.0f, 1.0f, 0.0f));
		transform.SetRotation(turn * transform.GetRotation());
	}
};

ST_SCRIPT_CLASS(Coin)
{
	ST_SCRIPT_FIELD(DegreesPerSecond);
}
```

1. **Line 8:** the field, turning 90 degrees each second by default.
2. **Line 12:** a copy of this entity's transform, its place, turn and size.
3. **Line 13:** `turn` is a small turn around the up axis, $(0, 1, 0)$, by the degrees of this frame converted to radians.
4. **Line 14:** the new rotation is the small turn followed by the old rotation, which is set back on the entity.
5. **Lines 18–21:** the registration lists the one field.

:::rule
Write `ST_SCRIPT_CLASS` once for each class, in a `.cpp` file and never in a header. Several files include a header, so each of them would register the class. Only the registered members are fields; a later page of this part, [Script fields](script-fields.md), shows the other types.
:::

:::::steps

1. Replace the template with the file above. Save the file.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select all of `Scripts/Coin.cpp` in your code editor and type the new text. The comment lines are optional.
   :::
   :::tab[With a command]
   Edit the file in any text editor. No command writes code for you: `script.create` writes only the template.
   :::
   ::::

   **You should see:** a file of 21 lines that ends with the registration.

   **If you do not see it:** compare your file with the listing line by line. A missing `;` or brace fails the build in the next step.

2. Build the scripts.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+B** in the editor, or open **Scripts ▸ Build Scripts**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** the status bar shows "Building", then the pill goes away. The Problems panel stays empty. The first build also configures CMake and takes longest; later ones are quick.

   **If you do not see it:** the pill reads "Build failed". Open **Scripts ▸ Show Problems**: the next section teaches how to read it.

3. Attach the script to one coin, then to the prefab.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select the root `Coin` in the Hierarchy, not its child. In the Inspector click **Add Component ▸ Script**, open **Add Script...** and pick `Coin`. Then open the menu of the Script component and choose **Apply to Prefab**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.add", "parameters": { "entity": "<coin id>", "class": "Coin" } }
   { "command": "prefab.apply", "parameters": { "entity": "<coin id>" } }
   ```

   `<coin id>` is the identifier (ID) that `entity.find` returns for the name `Coin`. The answer of `script.add` lists under `fields` only the values you gave, none here; `script.get` reads the 90. The answer of `prefab.apply` counts the four other coins under `updatedInstances`.
   :::
   ::::

   **You should see:** the Script component shows `Coin` and a field Degrees Per Second of 90. After the apply, the other four coins show the same component.

   **If you do not see it:** the list holds only built classes. Build again with **Ctrl+B**, then reopen it.

4. Give one coin its own speed. Change Degrees Per Second to 180 for the selected coin only.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Type `180` into the field and press **Enter**. The value shows as changed from the prefab.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.setField", "parameters": { "entity": "<coin id>", "class": "Coin", "field": "DegreesPerSecond", "value": 180 } }
   ```

   :::
   ::::

   **You should see:** this coin's value marked as differing from the prefab, and the others at 90.

   **If you do not see it:** the field edits the selected entities. Select one coin only.

5. Play.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Play** or **Ctrl+P**. Play builds changed sources first and the status bar says "Building to play".
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start" }
   ```

   :::
   ::::

   **You should see:** all five coins spin, one of them twice as fast.

   **If you do not see it:** the Console names the problem. A message that starts with "Script crash" is the subject of the last section.

:::::

::checkpoint{stage=2}

::figure{id=inspector-coin}

## Log a line and read a build error

The Console shows what the game says. The SDK's `Log::Info` writes a line there, and a script calls it with a list of values to print in one line. You bring `OnCreate` back with that one line in it, so each coin says its speed when play starts.

```cpp src="book:tutorials/make/first-script/CoinLog.cpp#L8-L13"
float DegreesPerSecond = 90.0f;

void OnCreate() override
{
	Log::Info("Coin starts with ", DegreesPerSecond, " degrees per second");
}
```

1. **Lines 10–13:** the function `OnCreate`, as the template had it. Your 21-line file has none, so you type all four lines, below the field and before `OnUpdate`.
2. **Line 12:** `Log::Info` joins a piece of text, the field's value and more text.

A **Problems panel** is the editor's list of what went wrong in the last script build and in the last script crash, each with its file and line. You use it now, because a build error is the most common event in a script's life.

:::::steps

1. Type lines 10 to 13 of the listing below the field, build and play. Then stop.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Edit `Scripts/Coin.cpp`, press **Ctrl+P** to play and again to stop. Open the **Console** panel.
   :::
   :::tab[With a command]
   Edit the file in a text editor, then run `script.build` as before.
   :::
   ::::

   **You should see:** five lines, "Coin starts with 90 degrees per second" four times and "180" once.

   **If you do not see it:** a Console filter may hide information lines. Clear the filter.

2. Delete the `;` at the end of the `Log::Info` line, save and build.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+B**. When the failure message appears at the bottom right, click **Show Problems**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build", "parameters": { "wait": false } }
   { "command": "script.status" }
   ```

   `script.build` alone fails with the first error. With `wait: false` it answers at once, and `script.status` lists every error under `build.last.diagnostics` once `build.running` is false.

   :::
   ::::

   **You should see:** a toast, a small message at the bottom right, with the title "Script build failed". The pill reads "Build failed · 1 error", and the Problems panel holds one error row with `Coin.cpp` and a line number. The compiler often reports the line after the real mistake, because it notices the gap only when the next token arrives.

   **If you do not see it:** open **Scripts ▸ Show Problems**. The Console also holds the whole build output, and a line that names a file and a line opens it when you click.

   ::figure{id=problems-error}

3. Double-click the error row, add the `;` and build again.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Double-click the row: your code editor opens `Coin.cpp` at that line. Fix it and press **Ctrl+B**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.open", "parameters": { "file": "Scripts/Coin.cpp", "line": 12 } }
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** the error row disappears, and the pill goes away.

   **If you do not see it:** the file opened in another program, the one your system uses for `.cpp` files: your setting names no program, and the answer's `openedWith` reads `the default application`. Fix the line there, or return to the first section.

:::::

::checkpoint{stage=3}

::figure{id=console-log}

## Change the code while playing, then crash it

**Hot reload** is the rebuild of the script module while the game runs, with the new code taking over without a stop. Each instance of a script is deleted and made again from the new class, its fields keep their values, and `OnReload` runs instead of `OnCreate`. Anything that is not a field starts over.

:::rule
Only members registered with `ST_SCRIPT_FIELD` survive a hot reload. A plain member such as `int m_Turns = 0;` starts again from its default, because the instance that held it is gone. Keep what must survive in a field.
:::

Step 3 below puts these two lines at the top of `OnUpdate`. The first makes a pointer that points at address 0, where no data lives. The second writes the number 42 to that address.

```pseudocode
volatile int* pointer = nullptr;
*pointer = 42;
```

No program may write to address 0, so the processor stops the write. The lines show what a stop looks like in the editor and nothing else.

:::::steps

1. Play. While the coins spin, change `glm::vec3(0.0f, 1.0f, 0.0f)` in `Coin.cpp` to `glm::vec3(1.0f, 0.0f, 0.0f)`, save and build.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+P**, edit the file, then press **Ctrl+B** while the game plays.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start" }
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** the coins tumble around the other axis without the game stopping, the Console shows no new "Coin starts with" lines because `OnCreate` did not run, and the faster coin is still faster.

   **If you do not see it:** nothing changes when the build failed. Read the Problems panel.

2. Stop, then change the axis back to `glm::vec3(0.0f, 1.0f, 0.0f)` and build.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+P**, edit, press **Ctrl+B**.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.stop" }
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** no problems.

   **If you do not see it:** check the line against the listing.

3. Crash it on purpose. Put the two lines of the listing above at the top of `OnUpdate`, build and play.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Edit, press **Ctrl+B**, then **Ctrl+P**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   { "command": "play.start" }
   ```

   `script.status` then holds the crash under `lastFault`, with its class, method and stack.

   :::
   ::::

   **You should see:** play stops at once, and a toast "Script crash: play mode stopped" appears with **Show Problems**. The Problems panel lists the crash with its function, file and line, and the Console names `Coin::OnUpdate`. The editor continues.

   **If you do not see it:** if Play never started, an earlier build failed: read the Problems panel. If the game plays and nothing stops, the build missed your edit. On some drives a file saved within two seconds after the last build looks built already, and the build output in the Console names no `Coin.cpp`. Stop, save the file again, build and play.

   ::figure{id=crash-toast}

4. Remove the two lines and build.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Delete the lines and press **Ctrl+B**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** a clean build, and Play works again.

   **If you do not see it:** the module stays off until a build or reload replaces it.

:::::

What you saw is **crash containment**: the engine catches that stop at the border of the script module, switches the module off, and ends play. The editor keeps running with all the work you have not saved. A division by zero would not do the job here, because on `ARM64`, the Apple silicon of Strata's macOS releases, an integer division by zero gives 0. An exception thrown in a script disables only that instance and logs it.

:::danger
On Linux and macOS, `abort()`, a failed `assert()` or `std::terminate` in a script ends the whole editor with the work you have not saved. Windows contains them in the modules that the editor builds. A script that finds a broken state reports it with `Log::Error` and returns.
:::

You can now write, build, attach and change a script, read a build error and a crash, and use hot reload. The next pages teach programming from zero on this script, and you return to Coin Run with the coins spinning.

::checkpoint{stage=4}

::figure{id=coins-reloaded}

## Summary

- You created a script class with **Scripts ▸ New Script...**, read the template line by line, wrote the spin with a field, and built it with **Ctrl+B**.
- You attached `Coin` to a coin, applied it to the prefab, and changed the field for one coin in the Inspector.
- You read a build error in the Problems panel, opened its line, and read where a crash stopped, then fixed both.
- You learned that hot reload keeps registered fields and starts every other member over, and that `OnReload` replaces `OnCreate`.

## Check yourself

1. Why does the turn multiply by `deltaTime`?

   :::answer{tests="create-build"}
   A frame lasts a different time on each computer. Multiplying the speed in degrees per second by the seconds of the frame gives the same turn for each second at any frame rate.
   :::

2. You attach `Coin` to one coin and the other four do not spin. What did you forget?

   :::answer{tests="attach-field"}
   You did not choose **Apply to Prefab**, so the other instances still follow the old prefab. Apply the Script component, and they follow.
   :::

3. The build fails, and the line that the Problems panel names looks right. Where is the mistake likely to be?

   :::answer{tests="read-errors"}
   One line earlier. The compiler notices a missing `;` only when it reads the next token.
   :::

4. After a hot reload, a coin keeps its speed of 180, but a counter you declared without `ST_SCRIPT_FIELD` is 0 again. Why?

   :::answer{tests="hot-reload"}
   The field is registered, so the engine copies its value into the new instance. The plain member lived in the old instance, which is deleted, and the new one starts from its default.
   :::

## Exercises

1. **Basic.** Change the default of `DegreesPerSecond` to `-180.0f`. Predict the direction and the time of one turn, then build and play.

   :::answer[Worked solution]{tests="create-build" solution="tutorials/make/first-script/exercise-1.tutorial.json"}
   The coins turn the other way, and one turn takes 360 / 180 = 2 s. Coins you gave their own value in the Inspector keep it, because that value differs from the default.
   :::

2. **Medium.** Add `void OnReload() override` with one `Log::Info` line. Predict when the line appears, then build while playing.

   :::answer{tests="hot-reload"}
   The line appears once for each coin after each rebuild during play, never on a normal start, because `OnReload` runs in place of `OnCreate`.
   :::

3. **Hard.** Replace the two crash lines with `throw 1;`. Predict whether play stops, then try it.

   :::answer{tests="read-errors"}
   Play continues. An exception disables only that coin's script and the Console says so, while a crash switches off the module. All five coins stop in the same frame, each with its own Console line.
   :::

## Where it lives in Strata

- `StrataEditor/src/Editor/ScriptProject.cpp`: writes the template and checks the class name.
- `StrataEditor/src/UI/ScriptDialogs.cpp`: the New Script dialog and the External Editor page.
- `StrataScriptCore/Include/StrataScript/Script.h`: the `Script` base class and its callbacks.
- `Strata/src/Strata/Scripting/ScriptEngine.h`: what crash containment catches on each platform.

## Further reading

- cppreference.com, "Attribute specifier sequence": what `[[maybe_unused]]` does (intermediate).
- The engine's own guide for people writing scripts, the "Writing scripts" manual (beginner).
