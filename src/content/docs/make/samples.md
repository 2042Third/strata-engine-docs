---
id: make/samples
title: "Studying the samples"
description: "Learn from three finished games that ship with Strata: play each one, read how it is made and change one thing in it."
kind: how-to
size: M
tracks: [G]
needs: [make/project-coin-run]
time: 90
learn:
  - id: open-copy
    text: create a copy of a sample from the editor and explain why the original stays untouched
  - id: read-readme
    text: find the files that hold a feature of a sample by reading its `README.md` and its credits table
  - id: find-feature
    text: name for each of the three samples the engine features it shows and one thing to try in it
  - id: change-one
    text: change one value of a sample in the Inspector and predict what the sample does with it
since: 0.5.0
status: final
---

You finished Coin Run, a small game with one round. A finished game that is ten or a hundred times larger teaches what a small one cannot. It shows how a pile of bodies stays fast, how a world too big for memory loads in pieces, and how a scene is lit like a photograph. Strata ships three such games, so you can open one, play it, read its parts and change one thing. Before you start:

- You have the editor and have opened a sample before, as [the first game](../start/first-game.md) did with Tetris.
- You know how to read a script and its fields, and what hot reload does ([Your first script](first-script.md)).
- You have about an hour and a half, and about 450 MB of free disk for the three copies once they have built and played.

## What a sample is

A **sample** is a finished game that ships with the editor, with its project, scripts, assets and a `README.md`, so that you can learn from it. Five samples ship. Two of them, Tetris and the Third-Person Adventure, are built as projects in other pages of this block. This page uses the other three: the Physics Playground, the Open World and the High Desert Outpost.

A sample never opens in place. When you open one, the editor copies it into a folder you choose and opens the copy. The copy omits the folder `.strata`, where the editor keeps its own data (the import cache, script builds and window state), so the copy builds everything fresh on your machine. The sample's picture becomes the copy's thumbnail, so the launcher shows the copy with the right picture before you save anything. The originals stay exactly as they shipped, and you can break a copy freely.

:::why
Opening a copy and never the original means that a change you try cannot damage the next reader's start. It costs disk space: the Outpost's copy alone grows to about 360 MB, because the originals hold their :term[source assets]{id=source-file} and the copy adds what the editor imports from them.
:::

## Open a copy and read its `README.md`

:::::steps

1. Open a copy of the Physics Playground.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **File ▸ Open Sample** and choose the Physics Playground in the list (on the launcher, press **Open Sample...** instead). In the **Open Sample** dialog, keep the **Folder** name, keep the **Location** or press **Browse...**, and press **Copy and Open**.
   :::
   :::tab[With a command]

   ```json
   { "command": "project.openSample", "parameters": { "sample": "PhysicsPlayground", "directory": "<a new folder>/PhysicsPlayground" } }
   ```

   The `directory` is a full path to a folder that does not exist yet or is empty.
   :::
   ::::

   **You should see:** the project open with the arena in the Scene view, and its Console free of errors.

   **If you do not see it:** the dialog refuses a **Folder** name that already exists in the **Location**, and says so under the fields. Choose another name.

2. Read the `README.md` of the copy.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open `README.md` from the project folder in any text viewer. The editor shows no such file, so use your system's file browser to find the copy.
   :::
   :::tab[With a command]
   Print the file in a terminal; the path is the folder you chose in step 1.

   ```sh
   cat "<the folder you chose>/README.md"
   ```

   The command prints the whole file, with its tables in plain text.
   :::
   ::::

   **You should see:** a title, a picture, and the sections "What it shows", "Controls", "Open it", "How it was made" and "Credits".

   **If you do not see it:** you opened the folder of the editor's install, not your copy. Open the folder you chose in step 1.

:::::

The Playground's and the Open World's `README.md` have the same sections, and this page reads them the same way. The Outpost's differs, as its section shows. "What it shows" is a table with one row per engine feature and, beside it, the files that hold the feature.

This table is your map. To learn how a game spawns a hundred balls, you do not search the project: you read the row. "Controls" lists the keys. "How it was made" names the editor commands that an artificial intelligence (AI) agent ran to build the game, which is the way you would build it too. The same section names the sample's own regression, a script of commands that plays the game and checks its outcome.

The regression lives in the engine's repository, in the folder `StrataTests/Editor/`, and not in the release archive you installed. The archive holds the programs, the samples, the script kit, the manual and the skills. So this page quotes the one part of a regression you need, below.

The last section, "Credits", points to `CREDITS.md`. It holds one table with the columns Files, Source, Author, License, Attribution and Changes. Every source asset of the sample appears in exactly one row, and every license is Creative Commons Zero (CC0) or Creative Commons Attribution, the rule you met in [Assets](assets.md). The row for the Open World's fox, for example, names three kinds of author, because the model, the rigging and the glTF conversion were made by different people.

## The Physics Playground

The Playground is an arena of six stations with about 600 bodies. It holds a crate tower and pyramid, a run of falling tiles, a pit of 500 balls, a goal that counts, ghost boxes and a ramp into ten pins. Look at its `README.md` table and find these rows.

- **Four materials, one prefab each.** The balls differ in restitution (how much they bounce), friction and mass, so each kind of ball behaves differently when you shoot it. The files are in `Prefabs/` and `Scenes/Main.stscene`.
- **Triggers.** The goal's basket counts balls with `OnTriggerEnter`; the launch pad sends balls down the ramp. The scripts are `GoalBasket.cpp` and `LaunchPad.cpp`.
- **The Ghost layer.** The ghost boxes belong to the layer Ghost, which does not collide with the layer Ball in the project's :term[layer matrix]{id=layer-matrix}. So balls fall through them and rest on the floor under.
- **Shoot and grab.** A left click shoots a ball along the ray through the cursor. Holding **E** grabs the body under the cursor and pulls it by setting its velocity toward a point.
- **A pour.** The tool panel's button pours 100 balls with one call of `Scene::InstantiateMany`, not 100 separate spawns.
- **Sound within a budget.** A pour starts hundreds of contacts in one frame. `Impact.cpp` plays at most 8 sounds in a frame and 16 per second on average, so a few voices play and the rest stay silent.
- **Slow motion and reset.** A toggle sets the :term[time scale]{id=time-scale} to `SlowMotionScale`, which is 0.25. Reset loads the scene again.

::figure{id=pit}

<!-- markdownlint-disable MD029 -->
:::::steps

3. Play the Physics Playground and look at each row you found.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Ctrl+P**. The editor builds the scripts first, so the first start takes longer. Fly with **W**, **A**, **S**, **D** and the right mouse button, press **1** to **6** to fly to a station, and press the tool panel's pour button.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start" }
   ```

   :::
   ::::

   **You should see:** the arena, and after the pour 100 more balls falling into the pit with impact sounds that thin out when many hit at once. The game also plays by itself at the start: at 2 seconds it pushes the falling tiles, at 6 seconds it pours 100 balls, and at 10 seconds it feeds the goal and launches balls. So the count `Bodies: 615` at the top right grows by 100 with each pour, yours and the game's.

   **If you do not see it:** if the scripts fail to build, the Console and the :term[Problems panel]{id=problems-panel} say why. Build again with **Ctrl+B** after the first build finishes.

4. Change one thing: make slow motion slower.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Stop with **Ctrl+P**. Type `Game` in the Hierarchy's search field and select the entity `Game`: it carries the `Playground` script. In the Inspector set the field `SlowMotionScale` from 0.25 to 0.1, and save with **Ctrl+S**. Play again and press the slow-motion toggle.
   :::
   :::tab[With a command]

   The script sits on the entity named `Game`, so `entity.find` gives its identifier (ID) first. Then set the field and save:

   ```json
   { "command": "entity.find", "parameters": { "name": "Game" } }
   { "command": "script.setField", "parameters": { "entity": "<the ID of Game>", "class": "Playground", "field": "SlowMotionScale", "value": 0.1 } }
   { "command": "scene.save", "parameters": {} }
   ```

   :::
   ::::

   **You should see:** the world moving at a tenth of its speed when the toggle is on, instead of a quarter.

   **If you do not see it:** you set the field while playing and then stopped, and the stop restored the value. Set it in edit mode, as this step does. The save matters for the next step: the editor opens another sample only over a saved scene, and otherwise refuses with `has unsaved changes`.

:::::
<!-- markdownlint-enable MD029 -->

The quote below is the part of the Playground's regression that shows how a game is checked without a person. It clicks the start button and then reads the script's field `DominoesDown` until it reaches 60, within 1,200 :term[fixed steps]{id=fixed-step}. Look at the `until` object: the script waits for an outcome, never for a number of frames.

```json src="StrataTests/Editor/PhysicsPlaygroundCommands.json.in#L27-L32"
{ "command": "input.click", "parameters": { "entity": { "$ref": "start" } } },
{ "command": "script.get", "parameters": { "entity": { "$ref": "game" }, "class": "Playground" },
	"expect": { "/scripts/0/fields/DominoesDown": { "min": 60 } }, "until": { "steps": 1200, "seconds": 900 } },
{ "command": "input.click", "parameters": { "entity": { "$ref": "feed" } } },
{ "command": "script.get", "parameters": { "entity": { "$ref": "game" }, "class": "Playground" },
	"expect": { "/scripts/0/fields/Score": { "min": 4 } }, "until": { "steps": 900, "seconds": 900 } },
```

The first and the third commands click a button of the tool panel. The second and the fourth read the script's fields: `expect` states the outcome, and `until` sets how long to wait for it. The second waits for the falling tiles, the fourth for the goal's score.

## The Open World

The Open World is a 768 m island with about 20,000 trees, rocks and flowers, five camps and 30 foxes. Nothing in it loads whole. Its world has three layers of 64 m cells, each with its own streaming distance: Vegetation at 192 m, Wildlife at 128 m and Landmarks at 320 m. The persistent scene holds the player, the sun, the sky and 97 terrain tiles, which have static mesh :term[colliders]{id=collider} on the Terrain layer. [Large worlds](large-worlds.md) taught these words; here you see them at full size.

Find these rows in the `README.md` table.

- **Props drawn by the graphics card.** The 20,000 props are instances of 26 one-entity :term[prefabs]{id=prefab-make} in `Prefabs/Nature/`. The graphics processing unit (GPU) decides what is in view and draws it in a few indirect draws.
- **A source on the player.** The player entity carries the streaming source, so cells follow it.
- **A safe teleport.** The keys **1** to **5** teleport to a camp. `Scripts/Explorer.cpp` asks for the cells around the target, waits until they are loaded and casts a ray down to find ground. The player never falls through a gap.
- **Foxes.** They live in the Wildlife cells and walk by a script, `Wander.cpp`, with an animation controller that switches between Survey, Walk and Run.
- **Day and night.** `Scripts/DayNight.h` turns the sun in steps of 0.25 degrees, so the shadow cascades are drawn again only when the sun moved. At dusk it lights the camp fires.
- **A loading scene.** The exported game shows `Scenes/Loading.stscene` with a progress bar while the first cells stream in.

The game starts with a tour of 24 seconds, in which the camera flies over eight points. The `README.md` also says what the game lacks: it has no sound, because no CC0 sound that fit was found.

::figure{id=tour}

A picture that shows a fox needs its authors in its caption. The fox has three kinds of author, for the model, for the rigging and animation, and for the glTF conversion, and `CREDITS.md` names them all. The tour's first seconds show no fox.

<!-- markdownlint-disable MD029 -->
:::::steps

5. Open a copy of the Open World and play it.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **File ▸ Open Sample**, choose the Open World and press **Copy and Open**. Then press **Ctrl+P**. Let the tour run, take over with any key, press **Tab** to walk on the ground and press **3** to teleport to a camp.
   :::
   :::tab[With a command]

   ```json
   { "command": "project.openSample", "parameters": { "sample": "OpenWorld", "directory": "<a new folder>/OpenWorld" } }
   ```

   :::
   ::::

   **You should see:** the island from the air, then after **3** a short fade and the player standing on the ground at the third camp.

   **If you do not see it:** the copy of this sample is about 20 MB, so the copy takes a while. It grows to about 40 MB once its scripts are built and it has played. Wait for the progress to finish before you press play.

6. Change one thing: start flying at once.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Stop playing. Select the entity `Player`, and in the Inspector, in its `Explorer` script, clear the check box `TourOnStart`. Save with **Ctrl+S**, then play again.
   :::
   :::tab[With a command]

   Find the ID with `entity.find` and `{ "name": "Player" }`, then:

   ```json
   { "command": "script.setField", "parameters": { "entity": "<the ID of Player>", "class": "Explorer", "field": "TourOnStart", "value": false } }
   { "command": "scene.save", "parameters": {} }
   ```

   :::
   ::::

   **You should see:** the game starting at the player's place with no tour.

   **If you do not see it:** you edited the field of another entity. Select the one named `Player`. Without the save, the next step's `project.openSample` refuses: the scene `Island` has unsaved changes.

:::::
<!-- markdownlint-enable MD029 -->

## The High Desert Outpost

The Outpost is Strata's graphics showcase: an abandoned fuel stop in a rocky valley after rain, lit by a low sun. Its job is to be the scene that every change to the :term[renderer]{id=renderer} is judged on, so it holds the most detailed assets of the three. It is made from twelve scanned models and ten texture sets by Poly Haven, plus a terrain and props that two scripts in the engine's repository generate. This makes it the largest of the samples, about 80 MB as it ships, and its copy grows to about 360 MB once the editor has imported its textures.

Its `README.md` has no "What it shows" table: a table "What it holds" lists its folders, and the paragraphs under it describe the game. Find these features there.

- **Three times of day.** Dawn, golden hour and dusk are stations. Each has two baked reflection probes, one for the yard and one for the hut. A switch keeps the old probes on for 1 second (`ProbeHoldSeconds`), so a reflection never falls back to the sky.
- **A camera tour.** Six shots of about 80 seconds in all, over marker entities. The tour loops.
- **Walk and flight.** **Tab** switches. The walk follows the ground by rays and stays within 140 m of the origin.
- **A photo mode.** **P** opens a panel to set the hour (6:30 to 19:00), the exposure, the field of view, the focus, the f-number, and the players' quality preset and anti-aliasing. The lighting follows the hour, but reflections snap to the nearest of the three baked times.
- **Flicker.** `Flicker.cpp` animates the fire's and the lanterns' flames.

::figure{id=outpost}

<!-- markdownlint-disable MD029 -->
:::::steps

7. Open a copy of the Outpost and take its photo mode.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **File ▸ Open Sample**, choose the High Desert Outpost and press **Copy and Open**. Press **Ctrl+P**, press **Tab** to take over from the tour, and press **P**. Move the hour slider and the f-number slider.
   :::
   :::tab[With a command]

   ```json
   { "command": "project.openSample", "parameters": { "sample": "Showcase", "directory": "<a new folder>/Showcase" } }
   ```

   :::
   ::::

   **You should see:** a panel over the scene, with the light and the shadows changing as the hour moves, and a blurred background when the f-number is small.

   **If you do not see it:** the game's interface may be hidden. Press **H** to show it again.

:::::
<!-- markdownlint-enable MD029 -->

## Result

You can now say, for each of the three games, which engine features it shows and in which files they live. Keep this table: it is the map you made.

| Sample | Feature | Where to read it |
| --- | --- | --- |
| Physics Playground | Many bodies, four materials | `Prefabs/`, `Scenes/Main.stscene` |
| Physics Playground | Triggers, the Ghost layer, impact sounds | `GoalBasket.cpp`, `LaunchPad.cpp`, `Impact.cpp` |
| Physics Playground | Shoot, grab, pour, slow motion | `Playground.cpp` |
| Open World | A world of three layers, 97 terrain tiles | `Worlds/Island.stworld`, the persistent scene |
| Open World | Teleport with prefetch | `Explorer.cpp` |
| Open World | Day, night and camp fires | `DayNight.h` |
| High Desert Outpost | Stations with baked probes, tour, walk | `Outpost.cpp`, `Stations.h`, `TourPath.h` |
| High Desert Outpost | Photo mode, flicker | `OutpostPhoto.cpp`, `Flicker.cpp` |

## The samples' rules, for your game

The samples follow rules that keep a game clear and ready to share, and your game can follow them too. Each sample has a `README.md` with the feature table, the controls, how it was made and its credits. A `CREDITS.md` table credits every source asset once.

Each sample has a picture of 480 by 270 pixels, the size of a project's thumbnail, which becomes the copy's thumbnail, and at most three screenshots of 3 MB together. The showcase may show six, in 8 MB. A game also has a title, a version and an icon as its identity.

Source assets stay within a size: 25 MB per sample and 80 MB for the showcase. Every asset is CC0 or Creative Commons Attribution, with the attribution it asks for, and a file with an unclear license stays out.

:::why
The limits exist because every sample grows the release archive. A rule that a person can check, such as a table of credits that the engine's tests compare with the files, keeps a hundred files from becoming a legal doubt.
:::

## Variations

- **Read a regression.** The quote above is one command of the Playground's regression. In the engine's repository, `StrataTests/Editor/OpenWorldCommands.json.in` does the same for the Open World: it checks a camp fire's light, then teleports with a key and waits with `until` for the player to stand on the ground. If you have a clone of the repository, read it beside the `README.md`'s "How it was made" paragraph.
- **Change a script and reload it.** Edit a value in a sample's script, such as `c_SoundsPerSecond` in the Playground's `Impact.cpp`. Build with **Ctrl+B** while the game plays, and listen. The fields keep their values, as in the first script, but a `constexpr` constant is no field, so only a rebuild changes it.

## Summary

- A sample opens as a copy without the folder `.strata`, and its picture becomes the copy's thumbnail, so the original stays as it shipped.
- A `README.md` maps each engine feature to the files that hold it, and `CREDITS.md` credits every source asset once.
- The Playground shows many bodies, triggers, the Ghost layer and a budget of sounds. The Open World shows a streamed world, a safe teleport and a day and night. The Outpost shows baked probes at three times of day and a photo mode.
- You change a sample by setting one field in the Inspector in edit mode, and by predicting what the field does before you play.

## Check yourself

1. You edit a script of the Playground's copy. Does the original in the release change?

   :::answer{tests="open-copy"}
   No. A sample always opens as a copy in a folder you chose, and the copy omits the folder `.strata`. The original stays as it shipped.
   :::

2. You want to know how the Open World avoids a fall during a teleport. Which part of the `README.md` do you read, and which file does it lead to?

   :::answer{tests="read-readme"}
   The table "What it shows", the row on prefetching before a teleport. It names `Scripts/Explorer.cpp`, which asks for the cells, waits for them and then casts a ray to the ground.
   :::

3. Why do the Playground's balls fall through the ghost boxes, and why does a pour of 100 balls not play 100 sounds?

   :::answer{tests="find-feature"}
   The Ghost layer does not collide with the Ball layer in the layer matrix. The impact script takes a token from a budget for each sound: at most 8 a frame and 16 a second on average.
   :::

4. You set `DayLengthSeconds` of the Open World's sun from 600 to 60. How fast does the clock of the game run, in hours of the day for each second?

   :::answer{tests="change-one"}
   A day of 24 hours takes 60 seconds, so 24 / 60 = 0.4 hours a second. Before, it was 24 / 600 = 0.04 hours a second.
   :::

## Exercises

1. **Basic.** Open `CREDITS.md` of the Open World copy and find the row of the fox. Name its license and the three kinds of work it credits.

   :::answer[Worked solution]{tests="read-readme"}
   The license is CC-BY-4.0, with the attribution text in the Attribution column. It credits the model, the rigging and animation, and the glTF conversion, each with its own author.
   :::

2. **Medium.** In the Open World copy, build the scripts with **Ctrl+B**: until they are built, the Inspector shows no :term[script fields]{id=script-field}. Set the sun's `DayLengthSeconds` to 60 and `TimeOfDay` to 17 in the Inspector, then play. The camp fires light at dusk, and the Console says so. Before you play, compute at what hour they light and how many seconds you wait.

   :::answer[Worked solution]{tests="change-one,find-feature" solution="tutorials/make/samples/exercise-1.tutorial.json"}
   The script lights the fires when the sun's height is below 0.1. The height is the sine of the elevation, and the elevation is 15 times the hour minus 6, in degrees. The sine is 0.1 at 174.26 degrees, which is the hour 17.62. From 17 the clock needs 0.62 hours at 0.4 hours a second, so 1.55 seconds. The Console shows `OpenWorld: campfires lit at 17:00`, because the script prints the whole hour only.
   :::

3. **Hard.** Say how the Outpost's copy can be the largest sample and still obey the rules above, and what you would check before you add a seventh sample.

   :::answer[Worked solution]{tests="read-readme"}
   Its entry in the index carries the budget `Showcase`, which allows 80 MB of source assets instead of 25 MB and counts its files apart from the other samples. Before you add a sample, check that it has a `README.md`, a `CREDITS.md` that credits each source file once, a picture, at most three screenshots and only CC0 or Creative Commons Attribution assets.
   :::

## Where it lives in Strata

- `Samples/Samples.json`: the index of the samples (folder, name, description, picture, optional budget).
- `StrataEditor/src/Editor/ProjectSamples.h`: how a sample is listed and copied without `.strata`.
- `Samples/PhysicsPlayground/Scripts/Playground.cpp`, `Samples/OpenWorld/Scripts/DayNight.h` and `Samples/Showcase/Scripts/Outpost.cpp`: the scripts this page reads.
- `StrataTests/src/Samples/SampleContentTests.cpp`: the checks of the rules.

## Further reading

- The `README.md` and `CREDITS.md` of each sample, in its folder (beginner).
- The manual's chapters on worlds and scripting, in the release's `Docs/Manual/` (intermediate).
