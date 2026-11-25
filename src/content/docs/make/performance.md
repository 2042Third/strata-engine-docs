---
id: make/performance
title: "Making your game run fast"
description: "Build a field of 5,000 props, measure its cost with the Stats chip and the Performance panel, make it cheaper step by step and measure the exported game."
kind: tutorial
size: M
tracks: [G]
needs: [make/quality, make/large-worlds, make/animation]
time: 120
learn:
  - id: frame-math
    text: compute a frame's time from its rate and explain why milliseconds measure a cost better than frames per second
  - id: read-bound
    text: name what bounds a frame, the CPU, the GPU or the display's cap, from the Performance panel
  - id: draw-cost
    text: explain what raises the draw-call count of a scene and what leaves it alone
  - id: cut-cost
    text: compare the cost of levels of detail, shadows and streaming with the **Stats** chip and the debug views
  - id: measure-run
    text: measure an exported game with a perf log and compare two quality presets
since: 0.3.0
status: final
---

## What you will make

You build a field of 5,000 rocks that runs badly, learn why with numbers, and make it cheaper one change at a time. At the end you measure the exported game and can say what limits its frames.

::figure{id=result}

## What you need

- A new project from the Basic 3D template, with a rock from the Open World sample. Copy `rock_largeA.glb` from the `Samples/OpenWorld/Assets/Models/Nature/` folder of the release into your project's `Models` folder. The rock is part of Kenney's Nature Kit, in the public domain (:term[CC0]{id=cc0}), and that sample's `CREDITS.md` names it.
- A :term[prefab]{id=prefab-make} of the rock, `Prefabs/Rock.stprefab`: drag the rock into the scene, make the prefab as in [Prefabs](prefabs.md), and delete the copy. Add a hut: a built-in cube at 148, 1.5, -14, scaled to 10, 3, 4. No download starts the page. Build these parts, or take Checkpoint 1 at the end of [Spawn the field](#spawn-the-field-and-read-the-stats-chip), which holds them with the `Field` and its script, and skip that section's first two steps.
- A copy of the Open World sample, which the launcher offers, for the streaming section.
- The exported game of your project for the last section ([Exporting and shipping](export.md) shows how).
- A spreadsheet program for the last section. `LibreOffice Calc` is free, and a spreadsheet in a web browser works as well.
- About two hours.

### Three ideas before you measure

#### Milliseconds, not frames per second

A frame is one picture of the game. At 60 frames per second each frame lasts 1000 / 60 = 16.7 ms, which is the whole budget of a frame (100 %). At 30 frames per second a frame lasts 33.3 ms (200 % of that budget).

Costs add up in time, not in rates. Take a game at 100 frames per second: each frame lasts 10 ms (60 % of a frame at 60 frames per second). A feature that costs 2 ms (12 %) gives 12 ms (72 %), which is 83 frames per second: a drop of 17. The same feature on a game at 30 frames per second gives 35.3 ms (211 %), which is 28.3 frames per second: a drop of 1.7. The feature costs the same, and the rates tell two stories, so this page reads times.

#### What bounds a frame

Each frame needs two kinds of work. The central processing unit (CPU) runs your scripts, the physics and the scene, and prepares the drawing. The :term[graphics processing unit]{id=gpu} (GPU) does the drawing. They work like two people in a row: one prepares, the other draws, and the slower one sets the pace.

A frame is **CPU-bound** when the CPU's time is the longest and **GPU-bound** when the GPU's is. It is **capped** when both finish early and the game waits, because vsync (the display's refresh) or a frame-rate limit sets the pace. The cure depends on the answer. Cutting draw work does nothing for a CPU-bound game, and cutting script work does nothing for a GPU-bound one.

#### An average hides spikes

Say 100 frames run, 90 of them at 10 ms (60 % of a frame at 60 frames per second) and 10 of them at 100 ms (600 %). The average is (90 × 10 + 10 × 100) / 100 = 19 ms (114 %), which looks fine. The player sees ten pauses. Sort the frames by time: the **p95** is the time of the 95th frame in that order, here 100 ms (600 %). The maximum is the longest frame, and the Performance panel shows both next to the average, so a spike cannot hide.

#### Measure, change one thing, measure again

:::why
Strata does not tell you which setting is cheap in general. Every cost depends on your scene and your computer, so the engine shows numbers for the frame you have. Change one thing at a time, measure before and after, and write down the computer and the numbers. A result without a named computer cannot be compared. [Performance lab](../engineering/perf-lab.md) shows how the engine's own budgets follow the same rule.
:::

## Spawn the field and read the **Stats** chip

You start with a field that is too big on purpose. One call spawns every rock, and the **Stats** chip then tells you what the scene costs.

:::question
Which lines are loops, what is `std::vector`, and what do `: public Script` and `override` mean? [Programming 2](../basics/programming-2.md) teaches loops and vectors, [Programming 3](../basics/programming-3.md) classes and calls, and [Classes and inheritance](../basics/cpp-classes.md) teaches inheritance.
:::

The script `FieldSpawner` makes a grid of 100 columns and 50 rows, 5,000 places in all. It builds one transform for each place in `OnCreate`. A transform is the position, turn and size of one copy, and here each is built by one line, `glm::translate(glm::mat4(1.0f), position)`, which moves a copy to a position.

```cpp src="book:tutorials/make/performance/FieldSpawner.cpp#L7-L22"
class FieldSpawner : public Script
{
public:
	float Spacing = 3.0f; // Metres between two props

	void OnCreate() override
	{
		for (int row = 0; row < 50; row++)
		{
			for (int column = 0; column < 100; column++)
			{
				const glm::vec3 position(column * Spacing, 0.0f, row * Spacing);
				m_Transforms.push_back(glm::translate(glm::mat4(1.0f), position));
			}
		}
	}
```

1. **Line 10:** `Spacing` is a field, so you can change the gap between rocks in the Inspector.
2. **Lines 14–21:** two loops visit every row and column; each place becomes one transform in `m_Transforms`.
3. **Line 19:** the given line builds a transform that moves a copy by `position`.

`OnUpdate` makes the copies. `Scene::InstantiateMany` takes the prefab and the whole list and creates every copy in one call, which is far cheaper than 5,000 calls of `Scene::Instantiate`. While the prefab still loads, the call returns nothing and starts the load, so the script asks again.

```cpp src="book:tutorials/make/performance/FieldSpawner.cpp#L24-L31"
void OnUpdate([[maybe_unused]] float deltaTime) override
{
	if (m_Spawned)
		return;
	// The call returns nothing while the prefab still loads, and it starts the load: ask again next frame.
	const std::vector<Entity> roots = Scene::InstantiateMany("Prefabs/Rock.stprefab", m_Transforms);
	m_Spawned = !roots.empty();
}
```

`m_Spawned` keeps the script from spawning the field twice.

:::::steps

1. Copy `FieldSpawner.cpp` into your project's `Scripts` folder and build the scripts.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Copy the file from the `Scripts` folder of Checkpoint 1's project, at the end of this section, then press **Ctrl+B**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   **You should see:** the status bar says the build finished with no error.

   **If you do not see it:** open the Problems panel and read the first error, as [Your first script](first-script.md) shows.

2. Create an empty entity named `Field` and attach the script.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Create an empty entity, rename it `Field`, click **Add Component ▸ Script** in the Inspector and pick `FieldSpawner`.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "Field" } }
   ```

   Then attach the class with `script.add`, giving the new entity and the class `FieldSpawner`.
   :::
   ::::

   **You should see:** the Inspector lists a Script component with the field Spacing of 3.

   **If you do not see it:** the list of classes holds only built ones. Build again, then reopen it.

3. Press **Play** and fly the editor camera over the field.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Play** in the top bar of the editor. Move the camera until the field fills the view.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start" }
   ```

   :::
   ::::

   **You should see:** thousands of rocks appear a moment after the game starts, because the prefab loads first.

   **If you do not see it:** when no rock appears, open the Console. A wrong prefab path shows there.

4. Enable the **Stats** chip of the viewport.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click **Stats** in the top bar of the viewport.
   :::
   :::tab[With a command]

   ```json
   { "command": "viewport.setSettings", "parameters": { "stats": true } }
   ```

   :::
   ::::

   **You should see:** lines over the image: :term[frame time]{id=frame-time}, `draw calls (N opaque, N shadow)`, instances, `occluded`, triangles, `shadowed lights`, `visible of N proxies` and `loading`.

   **If you do not see it:** the chip sits in the viewport you look at. The Game view has its own **Stats** chip.

5. Move the camera behind the hut, so the hut stands between you and most of the field.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Hold the right mouse button and fly until the hut hides the field.
   :::
   :::tab[With a command]

   ```json
   { "command": "camera.set", "parameters": { "position": [148, 1.6, -24], "target": [148, 1.2, 60] } }
   ```

   The camera now stands behind the hut. Run `viewport.capture` with `{ "camera": "editor", "width": 640, "height": 360 }` before and after the move, and compare `renderStats.occludedProxies`: one computer read 0 above the field, then 1982 behind the hut. The `renderStats` of `editor.perf` is `null` in an editor without a window.
   :::
   ::::

   **You should see:** the `occluded` count rises and the `visible of` count falls, because the engine skips what the hut hides.

   **If you do not see it:** the hut must hide whole rocks. Step back until it covers a wide part of the field.

:::::

The draw-call line is the one to understand. A draw call is one order from the CPU to the GPU to draw a batch of copies, and a proxy is the :term[renderer's]{id=renderer} record of one object it may draw. Draws follow the mesh, its submesh, its level of detail and the pipeline state: double-sided, alpha-masked, mirrored or skinned. They never follow the material or the number of copies.

You see 5,000 instances in a handful of draw calls, so the common advice to merge materials does not apply here. [Batching](../draw/batching.md) explains why.

::checkpoint{stage=1}

::figure{id=field-stats}

## Read the Performance panel

The **Stats** chip counts what the :term[renderer]{id=renderer} draws. The Performance panel shows where the time goes. Open it while the game plays: an idle editor does not tell you the game's speed.

The editor saves power. While nothing happens, it draws 30 frames per second, and 10 without the focus, so the frame pill shows that rate and not the game's. While the game plays, it draws up to the active frame rate of the Preferences, unlimited by default ([Editor status](../editor-ui/status.md)).

:::::steps

1. Open the panel and read its top line.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **View ▸ Performance** while the game plays.
   :::
   :::tab[With a command]

   ```json
   { "command": "editor.perf" }
   ```

   :::
   ::::

   **You should see:** a line `Frame N ms · p95 N · max N · N FPS`, a graph of the last 600 frames and a table of stages with average, p50, p95 and max columns.

   **If you do not see it:** the panel says no frames were profiled yet when the game has not run a frame. Wait a second.

2. Read what bounds the frame.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Search the lines under the GPU graph for `CPU-bound`, `GPU-bound` or `Capped`.
   :::
   :::tab[With a command]
   Read `gpu` in the result of `editor.perf`, next to `frame` and `interval`.
   :::
   ::::

   **You should see:** one of the three words with the CPU time, the GPU time and the frame interval beside it. A narrow panel cuts the line at the Stage column's edge, so widen the panel to read it.

   **If you do not see it:** the line says unknown until the GPU's times arrive, in an editor without a window, and when the graphics card writes no timestamps. The other numbers still hold.

3. Pause the panel to read a spike.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click **Pause**, or press **Space** with the panel focused. Point at a tall bar of the graph.
   :::
   :::tab[With a command]
   This step needs the panel: **Pause** holds the numbers still while the profiler keeps measuring. Use `editor.perf` for the latest frames.
   :::
   ::::

   **You should see:** a tooltip with the frame's time, and the time of each stage inside it.

   **If you do not see it:** press **Resume**, wait for a spike and pause again.

4. Press **Copy as JSON** and keep the numbers.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Click **Copy as JSON** and paste the text into a note, with the name of your computer.
   :::
   :::tab[With a command]

   ```json
   { "command": "editor.perf" }
   ```

   :::
   ::::

   **You should see:** the pasted text holds the same figures as the panel.

   **If you do not see it:** the copy lasts only until the next copy. Paste before you copy anything else.

:::::

Read the table like this. A CPU-bound field spends its time in `Scene.Transforms` or `Render.Extract`, which prepare 5,000 copies. A GPU-bound field shows the time in the GPU stages. At the display's rate the panel says **Capped**: nothing limits you but the display.

::checkpoint{stage=2}

::figure{id=panel-bound}

## Make the field cheaper

Two changes follow, each measured on its own: levels of detail, then shadows. Write down the numbers of the **Stats** chip and the panel before each one.

:::::steps

1. Show the levels of detail the field draws.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open the debug view menu of the viewport and choose **LOD: level of detail drawn**.
   :::
   :::tab[With a command]

   ```json
   { "command": "viewport.setSettings", "parameters": { "debugView": "lod" } }
   ```

   :::
   ::::

   **You should see:** every rock in one tint, and a legend that counts them all at level 0. The rock has about 80 triangles with sharp edges, too few for the importer to make simpler levels of it, so it keeps one level.

   **If you do not see it:** the rocks keep their own colors. Each viewport has its own debug view, so choose it in the menu of the view you look at.

2. Compare the presets **Low** and **Ultra**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open **Project Settings**, the **Graphics Quality** page, choose **Low**, and read the **Stats** chip. Then choose **Ultra** and read it again.
   :::
   :::tab[With a command]

   ```json
   { "command": "project.setSettings", "parameters": { "section": "Renderer.Quality", "value": { "Preset": "Low" } } }
   ```

   Run it again with `Ultra` and compare the **Stats** chip.
   :::
   ::::

   **You should see:** the same `triangles` line on **Low** and on **Ultra**. Your rock has one level, so no preset has a simpler one to choose. A mesh with simpler levels would swap to them sooner on **Low**, and its `triangles` line would be smaller there.

   **If you do not see it:** the numbers change as the camera moves. Hold the camera still between the two readings.

3. Switch shadows off for the rocks and measure again.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Stop the game. Drag `Rock.stprefab` into the scene, clear **Cast Shadows** on the mesh renderer of its innermost `rock_largeA`, apply the change to the prefab, and delete the copy. Play again.
   :::
   :::tab[With a command]
   Run `play.stop` and `prefab.instantiate` with `Rock.stprefab`. The copy has two entities named `rock_largeA`: ask for the one with the mesh renderer.

   ```json
   { "command": "entity.find", "parameters": { "name": "rock_largeA", "component": "MeshRenderer" } }
   { "command": "component.set", "parameters": { "entity": "<the ID entity.find gave>", "component": "MeshRenderer", "values": { "CastShadows": false } } }
   ```

   Then run `prefab.apply` for the same entity and component, `entity.delete` for the copy and `play.start`.
   :::
   ::::

   **You should see:** while the camera moves, the `shadow` draw calls fall and `GPU.Shadows` shrinks. A still camera keeps the sun's shadow and counts no shadow draws, so a capture reads `shadowDraws` 0 either way.

   **If you do not see it:** edits made while playing change only the running copy. Make the change in edit mode.

:::::

A level of detail is a simpler copy of a mesh that the engine draws when the object is small on screen. The quality row **Level of detail error (pixels)** names how many pixels of error the player may not notice, and each preset sets it: **Low** accepts the most error and **Ultra** the least. The engine draws a shadow once more for every object that casts it, so small rocks whose shadows nobody sees are a bad trade. Shadowed point, spot and rectangle lights draw their casters again, and the chip's `shadowed lights` line counts them. [Levels of detail](../draw/lod.md) and [Presets](quality.md) explain the engine's side.

Your project has no mesh with simpler levels, so the picture below uses a scanned boulder that has them. From where the camera stands, every boulder draws one of its simplest levels, because its finest detail is smaller than a pixel.

::checkpoint{stage=3}

::figure{id=lod-view}

## Watch streaming

A big world does not fit in memory, so Strata loads its cells as the camera needs them ([Large worlds](large-worlds.md)). Streaming costs time as well, and the debug view shows what is loading.

:::::steps

1. Open your copy of the Open World sample and choose the streaming view.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open the copy from the launcher. Choose **Streaming: loading and failed assets** in the debug view menu, and open **View ▸ Streaming**.
   :::
   :::tab[With a command]

   ```json
   { "command": "viewport.setSettings", "parameters": { "debugView": "streaming" } }
   ```

   :::
   ::::

   **You should see:** tinted entities where a mesh, a material or a texture still loads, and in the panel the loads, the queues and the cell map.

   **If you do not see it:** nothing is tinted once everything has loaded. Fly to a place you have not seen.

2. Fly across the island and watch the requests.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Hold the right mouse button and fly fast in a straight line. Read the `assets requested` and `loading` figures of the **Stats** chip while you fly.
   :::
   :::tab[With a command]
   Move the editor camera with `camera.set` and run `world.status` at once and a few seconds later: its `cells` count what is `wanted`, `loading`, `loaded` and `unloading`.
   :::
   ::::

   **You should see:** the requests follow the view: cells in front of you load, and cells behind you leave.

   **If you do not see it:** fly farther. A short flight stays inside cells that are already there.

:::::

::checkpoint{stage=4}

::figure{id=streaming-view}

## Measure the exported game

The editor adds its own cost. To measure the game as a player has it, run the exported game and let it write a log. A **perf log** is a file with one row of times for every frame.

:::::steps

1. Run the exported game for 600 frames and write the log.

   ::::tabs{sync=os}
   :::tab[Windows]

   Run the game from a terminal in its folder.

   ```powershell
   .\MyGame.exe --perf-log run.csv --frames 600 --resolution 1280x720
   ```

   Press **Enter** to run it.
   :::
   :::tab[Linux]

   Run the game from a terminal in its folder.

   ```sh
   ./MyGame --perf-log run.csv --frames 600 --resolution 1280x720
   ```

   Press **Enter** to run it.
   :::
   :::tab[macOS]

   Run the game from a terminal in its folder.

   ```sh
   ./MyGame --perf-log run.csv --frames 600 --resolution 1280x720
   ```

   Press **Enter** to run it.
   :::
   ::::

   **You should see:** the game opens a window of 1280 by 720 pixels, closes after 600 frames and leaves `run.csv` beside it.

   **If you do not see it:** the game refuses the options and says why on the terminal. `--perf-log` needs a file name.

:::::

The log `run.csv` is a table written as text: one row on each line, and a mark between the columns. A spreadsheet program opens it as a table. Open `run.csv`, select the column `WorkMs`, and insert a line chart.

`WorkMs` is the CPU's work time of the frame, `IntervalMs` the time since the frame before, and `GPUBusyMs` the GPU's busy time. Then come the times of every stage and columns of the renderer: `DrawCalls`, `Instances`, `Triangles`, `VisibleProxies`, `OccludedProxies` and `LocalShadowLights`.

:::::steps

1. Run again with the preset **Ultra** and write a second log.

   ::::tabs{sync=os}
   :::tab[Windows]

   Run the game with another log name and `--quality`.

   ```powershell
   .\MyGame.exe --perf-log ultra.csv --frames 600 --resolution 1280x720 --quality ultra
   ```

   Repeat with `--quality low` and the name `low.csv`.
   :::
   :::tab[Linux]

   Run the game with another log name and `--quality`.

   ```sh
   ./MyGame --perf-log ultra.csv --frames 600 --resolution 1280x720 --quality ultra
   ```

   Repeat with `--quality low` and the name `low.csv`.
   :::
   :::tab[macOS]

   Run the game with another log name and `--quality`.

   ```sh
   ./MyGame --perf-log ultra.csv --frames 600 --resolution 1280x720 --quality ultra
   ```

   Repeat with `--quality low` and the name `low.csv`.
   :::
   ::::

   **You should see:** two more files. In the chart, the `GPUBusyMs` column is lower on **Low** than on **Ultra**.

   **If you do not see it:** if the two charts match, the game was CPU-bound or capped, and the preset changes only what the GPU draws.

:::::

The run is a fair test, because `--frames` stops after a fixed number of frames and every :term[fixed step]{id=fixed-step} runs. Never compare two runs whose game time followed the frame rate: they played different games. Name the computer next to every chart.

### Variations

- **Vsync.** In an exported game that offers vsync on its settings screen, run the log with it on and off. With vsync on, the panel and the log show a capped frame: the interval equals the display's rate, and the GPU's busy time is lower than the interval.
- **Streaming columns.** Every log holds columns such as `WorldCellsLoaded`, which matter in a game with a world. Chart them next to `WorkMs` and search for a spike where a cell loads.
- **Many scripts.** 100,000 scripts whose `OnUpdate` does nothing take about 1.9 ms a frame on the reference machine, 11 % of a frame at 60 frames per second, or about 20 ns for each call. A :term[callback]{id=callback} a class does not override costs nothing, so override only the callbacks you use.

::checkpoint{stage=5}

::figure{id=perf-log-chart}

## Summary

- You computed a frame's time from its rate and saw why milliseconds add up where frames per second mislead.
- You read the Performance panel and named what bounds a frame: the CPU, the GPU or the cap.
- You learned that draw calls follow the mesh, its levels of detail and the pipeline state, never the material or the copies.
- You compared levels of detail, shadows and streaming with the **Stats** chip and the debug views.
- You measured the exported game with a perf log and compared two presets.

## Check yourself

1. A feature adds 2 ms (12 % of a frame at 60 frames per second) to a frame. Your game ran at 50 frames per second. What is the new rate?

   :::answer{tests="frame-math"}
   A frame at 50 frames per second lasts 1000 / 50 = 20 ms (120 %). The new frame lasts 22 ms (132 %), which is 1000 / 22 = 45 frames per second.
   :::

2. The panel says Capped and your game runs at 60 frames per second. Will a cheaper scene give more frames per second?

   :::answer{tests="read-bound"}
   No. Both the CPU and the GPU finish early, and vsync or a limit sets the pace. A cheaper scene leaves more idle time, and the rate stays at 60.
   :::

3. You give 5,000 rocks ten different materials. Do the opaque draw calls rise?

   :::answer{tests="draw-cost"}
   The opaque draw calls stay as they were. Draws follow the mesh, its submesh, its level of detail and the pipeline state, so ten materials make no new batch.
   :::

4. The **Stats** chip shows many `occluded` proxies behind the hut. What does that save?

   :::answer{tests="cut-cost"}
   The engine skips drawing what the hut hides, so the draw work and the triangles fall. The hidden rocks still exist and still cost their scripts and transforms.
   :::

5. Two runs of your exported game differ by 30 %. What must you check before you trust it?

   :::answer{tests="measure-run"}
   Check that both ran on the same computer with the same options (`--frames`, `--resolution`, `--quality`), and that game time did not follow the frame rate. Run again to see the spread.
   :::

## Exercises

1. **Basic.** Give the field's rocks ten different materials. Predict the opaque draw calls, then read them on the **Stats** chip before and after.

   :::answer[Worked solution]{tests="draw-cost" solution="tutorials/make/performance/exercise-1.tutorial.json"}
   The opaque draw calls do not change. The engine's own test draws 10,000 materials in at most four draw calls: the material is not part of what makes a batch.
   :::

2. **Medium.** Run the log of the exported game on **Low** and on **Ultra** and compare `GPUBusyMs` and `WorkMs`. Say which preset helps and why.

   :::answer{tests="measure-run"}
   If `GPUBusyMs` falls and `WorkMs` stays, the game was GPU-bound, and the preset helped by cutting draw work. If both stay, the CPU or the cap set the pace.
   :::

3. **Hard.** Spawn 500 animated characters, set their Culling Mode to When Visible, and turn the camera away from them. Predict the change of `Scene.Animation`, then measure it.

   :::answer{tests="cut-cost"}
   The stage shrinks, because characters nobody draws stay still. With the camera on them, the stage is as costly as with Always Animate.
   :::

## Where it lives in Strata

- `StrataEditor/src/Panels/PerformancePanel.cpp`: the summary line, the graphs, the stage table and the bound's wording.
- `StrataEditor/src/Panels/ViewportToolbar.cpp`: the lines over the viewport.
- `Strata/src/Strata/Renderer/SceneDrawKey.h`: what makes a draw, and what does not.
- `Strata/src/Strata/Runtime/FramePerfLog.cpp`: the perf log's columns.
- `StrataEditor/src/Editor/EditorFrameRate.h`: the editor's idle and active frame rates.

## Further reading

- The engine's Graphics manual: the quality rows and their costs (beginner).
- The engine's Worlds manual: streaming and the cell map (intermediate).
