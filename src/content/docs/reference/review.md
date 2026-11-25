---
id: reference/review
title: "Review: reference"
description: "Exercises that use several reference pages together: each asks you to find facts on more than one page and to combine them."
tracks: []
status: final
generated: review
---

## Cumulative exercises

These exercises need more than one page of the part, so try each one before you open its worked solution.

1. **Basic.** Your build server runs Linux and has no graphics card. It runs the unit tests of a Debug build, then starts the editor on the script `check.json` and must stop when the script ends.

   (a) Write the `ctest` command that omits the tests that need a graphics processing unit (GPU).

   (b) Write the editor options for a run with no window and no graphics device, which runs the script and closes after it.

   (c) The third command of the script fails. Which exit code does the editor return?

   (d) A colleague writes `--no-gpus` in place of the option `--no-gpu`. What happens?

   (e) Which two test labels select no tests in a Debug build?

   :::answer[Worked solution]
   (a) The build page gives the form `ctest --preset linux-debug -LE gpu`. The option `-LE` excludes the tests that carry a label, so every test without the label `gpu` runs.

   (b) The options are `--no-gpu --commands check.json --quit-after-commands`. The editor page says `--no-gpu` drops the graphics device and implies a headless run, so `--headless` adds nothing. The option `--quit-after-commands` ends the scripted run when the script has finished.

   (c) The exit code is 1, because the table of exit codes of the editor page lists a script that finished with a failed command.

   (d) An option the table lacks ends the start with exit code 3, and nothing runs. A build server reads the 3 as a mistake in the call, not as a failed test.

   (e) The labels `fuzz` and `perf` exist in Release and Dist builds only, as the table of labels says. A Debug build has no test with either of them.
   :::

2. **Basic.** A game runs on a computer whose graphics device reports 12 GiB of memory available to the program.

   (a) Give the default budgets of the three pools of the asset manager.

   (b) The same game starts as `StrataRuntime --headless`. What are the budgets then?

   (c) A support person asks for `--asset-budget-mb 2048`. Which pool does it limit, and which pools keep their defaults?

   (d) A texture of 64 MiB finishes loading. How many upload steps does it need, and in at least how many frames does it arrive when only the default bytes per frame limit it? Then suppose each step costs 1 ms of main-thread time: how many frames at least with the default time limit of the upload steps?

   (e) You run `StrataRuntime --asset-budget-mb lots`. What happens?

   :::answer[Worked solution]
   (a) The assets page gives GPU textures 50 % of the device budget and GPU buffers 15 %. That is 6 GiB for textures and 1.8 GiB for buffers. The pool for the central processing unit (CPU) is unlimited in every case.

   (b) A headless run has no graphics device, so both GPU pools are unlimited, and the CPU pool stays unlimited.

   (c) The option sets the GPU texture budget of the game's assets, so the texture pool becomes 2048 MB. The buffer pool keeps its 15 % share and the CPU pool stays unlimited, because the option names no other pool.

   (d) One step is 4 MiB (`c_AssetUploadStepBytes`), so 64 / 4 = 16 steps. The default `UploadBytesPerFrame` is 16 MiB, which is 4 steps a frame, so the texture needs at least 16 / 4 = 4 frames. The default `UploadMsPerFrame` is 2 ms. At 1 ms a step only 2 steps fit in a frame, so the texture needs at least 16 / 2 = 8 frames. The time limit binds first.

   (e) A wrong value of an option ends the start with exit code 3, as the table of the runtime's exit codes on the page about worlds and runtime says.
   :::

3. **Basic.** An entity `Guard` has world scale (2, 3, 1.5). It carries a `RigidBody` of type `Dynamic` with `Mass` 0.0004, a `CapsuleCollider` with `Radius` 0.4 and `HalfHeight` 0.5, and a `CharacterController`.

   (a) How wide is the capsule's radius and how tall is the capsule, in metres?

   (b) Which mass does the simulation use, and where does the components page show the smallest legal value?

   (c) Which of the two, the body or the controller, moves the guard?

   (d) A second body of 2 kg receives an impulse of 6 N·s. By how much does its velocity change?

   :::answer[Worked solution]
   (a) The unit table of the physics page says a capsule radius is multiplied by the larger of the world scale's X and Z. The larger is 2, so the radius is 0.4 × 2 = 0.8 m. The `HalfHeight` is the straight part only and is multiplied by the Y scale: 0.5 × 3 = 1.5 m. The straight part is 3 m long, and each end adds a round cap of 0.8 m, so the capsule is 3 + 2 × 0.8 = 4.6 m tall.

   (b) The row for `Mass` says that values below 0.001 count as 0.001, so the simulation uses 0.001 kg. The `RigidBody` entry of the components page lists the range of `Mass` from 0.0010000000474974513, which is the 32-bit float nearest to 0.001.

   (c) The physics page says an entity with both is simulated as the rigid body, and its controller does nothing. The body moves the guard.

   (d) The page defines the newton-second as the unit of an impulse, and an impulse changes the velocity at once. A newton-second is a kilogram metre per second, so the change is 6 / 2 = 3 m/s.
   :::

4. **Medium.** A team starts an editor with `StrataCLI mcp` and lets agents drive it.

   (a) No client connects for 700 s. What does the editor do, and which option do you give for a quiet hour of 3,600 s? Which values does the option accept?

   (b) Nine agents try to sign in at the same time, and eight have signed in. What does the ninth get?

   (c) An agent sends `rpc.ping` before it has signed in. What happens?

   (d) An agent sends `asset.delete` for a material that a scene uses. Which code returns, where does the agent find who uses it, and how can it delete anyway?

   (e) What does `StrataCLI` return as its exit code for every error the editor sent?

   :::answer[Worked solution]
   (a) The automation page says `mcp` starts editors with an idle timeout of 600 s. After 700 s without a client the editor has closed itself, at 600 s. Give `StrataCLI mcp --idle-timeout 3600`: the client passes the value to the editors it starts, and the editor's own option `--idle-timeout` asks for an hour. The option accepts 0 to a week in seconds, so 604,800 s at most, and 0 means never. A launched editor has 0 unless you give a value.

   (b) The limit of signed-in clients is 8, and the ninth client gets `ServerBusy`, code -32004.

   (c) Before the sign-in ends the server accepts only `rpc.handshake` and `rpc.authenticate`. A request of any other kind closes the connection, and `rpc.ping` is refused.

   (d) The command fails, and a failed command is sent as `OperationFailed`, code -32005. The data of the error holds the users of the asset. The command page of `asset.delete` lists the parameter `force`, which deletes although other assets or the open scene use the asset. The delete is one undo step.

   (e) The exit code is 1 for any error the editor sent, whatever its code.
   :::

5. **Medium.** A project keeps scenes with the default `FixedTimestep` of 1/60 s. A frame comes with a time step of 0.2 s.

   (a) With the `Scene.Timing` field `FixedRate` set to `Scene`, how many steps are due and how many run?

   (b) You set `FixedRate` to `240`. Which step does the game use now, how many steps are due for the same frame, and how many run?

   (c) How many steps may run at the rates 30 and 120, and what is the largest number at any rate?

   (d) The `Physics.Simulation` field `ContactHertz` is 100 at 60 steps per second. What does box3d apply, and which statistic shows it?

   (e) Which call sets `Scene.Timing` to 240 steps per second, and what must it contain?

   :::answer[Worked solution]
   (a) The step is 1/60 s, so 0.2 × 60 = 12 steps are due. The scene's own limit is its default of 8 steps (`MaxFixedStepsPerFrame`), so 8 run.

   (b) The project's rate wins in every scene, so the step is 1/240 s, which is 4.17 ms. Then 0.2 × 240 = 48 steps are due. The limit at a project rate is the number of steps of 2/15 s, which is 2/15 × 240 = 32, and never more than the constant `ProjectSceneTiming::c_MaxStepsLimit`, 64. So 32 run.

   (c) The same rule gives 2/15 × 30 = 4 steps at 30 and 2/15 × 120 = 16 steps at 120. At 60 it gives the 8 of (a). The largest limit at any rate is 64, which no rate reaches, because the rates offered are 30, 60, 120 and 240.

   (d) The settings table says box3d uses at most an eighth of the rate of its inner steps, which is 30 at 60 steps per second, so higher values act as that ceiling. Box3d applies 30, and `settings.effectiveContactHertz` of `physics.stats` shows it. At 120 steps per second the ceiling is 60.

   (e) The call is `project.setSettings` for the section `Scene.Timing`, and it sets the whole value of the section, so it holds `FixedRate` as the text `"240"` and `Interpolation`, which is `true` by default. A value outside the five choices, such as `"90"`, changes nothing and names the field.
   :::

6. **Medium.** A scene has 3,000 bodies and asks for `MaxBodies` 0. Its world also holds cells that lie 30 km from the origin, and one body there is thrown to a distance of 120 km.

   (a) Compute the room for bodies and for contacts, and the `reservedMB` that `physics.stats` shows.

   (b) Is a cell at 30 km valid? Which tool warns about it, and why?

   (c) What happens to the body at 120 km, and which counter of `physics.stats` can show it?

   :::answer[Worked solution]
   (a) The physics page sizes an automatic room as the bodies doubled and rounded up to a power of two, never fewer than 1,024. Doubling gives 6,000, and the next power of two is 8,192 bodies. The contact room is twice the bodies, 6,000, and the least is 2,048, so 6,000 contacts. The estimate is 32,768 bytes plus 2,120 × 8,192 plus 250 × 6,000, which is 32,768 + 17,367,040 + 1,500,000 = 18,899,808 bytes. Divided by 1,048,576 it gives `reservedMB` 18.02.

   (b) The world page gives `WorldData::c_MaxExtent` as 1,000 km, so the cell is valid and the document loads. The supported extent, `WorldData::c_SupportedExtent`, is 20 km, so `world.cook` warns about it. A 32-bit float has fewer steps far from the origin: at 20 km a position moves only in steps of 2 to 4 mm, and farther away objects visibly jitter.

   (c) The limit `c_MaxBodyCoordinate` is 100,000 m, so a body at 120 km waits until it comes back. It does not wait for room, so `waitingForSlot` stays unchanged. The table of limits says such a body waits like a body with a degenerate transform, so `pendingOther`, the counter of entities that wait for other reasons, counts it.
   :::

7. **Medium.** You run the perf tests on your own computer. The metric `TrivialUpdate100k` of the `Perf.Scripting` suite takes 4.0 ms and the metric `Sort200k` of the `Perf.Harness` suite takes 22 ms.

   (a) Which command runs the tests, and in which builds does it find them?

   (b) Is the 4.0 ms a regression of the script system?

   (c) The metrics `TrivialUpdate100k` and `TrivialUpdate300k` of `Perf.Scripting` measured 1.856 ms and 5.745 ms. Check that their budgets follow the rule. Then give the share of a frame at 60 frames a second that the 300,000 scripts take, at the measurement and at the budget.

   (d) A change makes the metric `Copy1M` of the `Perf.Scene` suite take 60 ms. May the author raise its budget of 54.51 ms?

   (e) What does a metric such as `WakeLatency` of `Perf.Jobs` do, with no measured value?

   :::answer[Worked solution]
   (a) The command is `ctest --preset windows-release -L perf`, from the suites page. The label `perf` selects tests in Release and Dist builds only, as the build page says, so a Debug build runs none.

   (b) No conclusion follows. The budgets come from the reference machine, and the performance page says to compare a result of yours only with a run of the same code on the same machine. The canary `Sort200k` of `Perf.Harness` measured 10.0 ms there and has a budget of 15.0 ms, and your 22 ms is 2.2 times that. Your 4.0 ms is 4.0 / 1.856 = 2.2 times its measurement too, so the whole machine is slower, and the numbers show no regression. Run the test again on the code before the change, on your machine, and compare the two.

   (c) A budget is at most 1.5 times the measurement. For 100,000 scripts, 1.5 × 1.856 = 2.784 ms, which is the budget exactly. For 300,000 scripts, 1.5 × 5.745 = 8.6175 ms, and the budget of 8.617 ms lies below it, so both follow the rule. A frame at 60 frames a second lasts 16.67 ms. The measurement takes 5.745 / 16.67 = 34 % of it, and the budget 8.617 / 16.67 = 52 %.

   (d) No. A budget only goes down, and a cost over its budget is a regression to fix, not a limit to raise. The 60 ms is 10 % over the budget. The author must make the copy cheaper or drop the change.

   (e) A metric with only a unit is provisional. Its test measures once, prints and records the value, and never fails, until the reference machine measures it.
   :::

8. **Hard.** A game's project sets `Renderer.Quality` rows by `project.setSettings`. On a weak test card the Performance panel shows too much time in `GPU.Shadows` and in `GPU.RadianceCascades`.

   (a) Name every quality row whose cost shows in each of the two stages.

   (b) You must free GPU memory and leave every shadow row alone. Which cost rows count memory, and which of the five players' rows counts memory too?

   (c) A designer sets `FilmGrain` and `ChromaticAberration` to `Off`, and sees `GPU.Post` unchanged. What can explain it?

   (d) A tester wants one run at the Low preset, with nothing saved and without the players' saved options over the preset. Which command and option do that?

   (e) The designer writes `ContactShadows` 3 into Custom. How many steps does the game march?

   :::answer[Worked solution]
   (a) The table of quality rows names the stage of each row. In `GPU.Shadows` are `ShadowResolution`, `ShadowCascades`, `LocalShadowAtlasSize`, `LocalShadowMaxTile` and `MaxShadowedLocalLights`. In `GPU.RadianceCascades` is `GlobalIllumination` alone.

   (b) The rows with a memory entry that are not shadow rows are `EnvironmentResolution` (the sky's map), `Reflections` (the traced targets), `MotionBlurQuality` (the blur's targets), `ReflectionProbeResolution` (the probes' cubes) and `GlobalIllumination` (the field and voxels). Of the players' rows only `MotionBlur` counts memory, and it is counted with the samples of `MotionBlurQuality`.

   (c) The two rows are players' rows, and their value `Scene` shows each effect only where the game uses it. A players' row may disable what a scene uses, never enable more, so in a scene with no film grain and no color fringes `Off` removes nothing. The table also lists `GPU.Post` for the row `AntiAliasing`, whose stage is the chosen method's own: `GPU.TAA` or `GPU.Post`. A method that runs in `GPU.Post` keeps the stage busy, so check the scene's effects and the method before you judge the change.

   (d) The runtime option `--quality low` draws with the Low preset for this run, instead of the project's preset with the players' saved options over it, and it saves nothing. The editor has no such option, as its table shows.

   (e) The Custom column says `ContactShadows` accepts 0, or 4 to 32 steps, and counts 1 to 3 as 4. So 3 counts as 4 steps.
   :::

9. **Hard.** A game's interface draws a canvas of 2,000 elements under `ScaleWithScreen`. A player drags the window through five different shapes in turn. The canvas uses six fonts.

   (a) Under which condition does a change of window size leave `ElementsLaidOut` at 0, and when does it count a `FullRebuilds`?

   (b) The five shapes repeat in the same order. Show how many layouts the canvas keeps, and why each change of shape rebuilds.

   (c) Suppose the cost of a full layout grows in proportion to the elements, and use the measurement of the 10,000-element suite. How long does one rebuild of this canvas take, and is that a reason to worry?

   (d) At least how many draw calls does the canvas need for text, and which stages would you read to check its cost?

   :::answer[Worked solution]
   (a) The page says a window that keeps the same size in canvas units is served by the kept layout, so `ElementsLaidOut` stays 0: 1920 by 1080 to 1280 by 720 is such a change. A window that changes its shape needs a new layout, and `FullRebuilds` counts it.

   (b) The limit `c_MaxLayoutsPerCanvas` is 4, one for each canvas size in units, and a fifth size replaces the layout used longest ago. Shapes A, B, C and D fill the four places. E arrives and replaces A. When A comes next, it replaces B, then B replaces C, and so on.

   In a cycle of five, each shape finds its layout gone, so every change rebuilds. `FullRebuilds` then grows every frame that changes the shape.

   (c) The metric `Layout10k` of the `Perf.GameUI` suite measured 0.4059 ms for 10,000 elements. For 2,000 elements the proportion gives 0.4059 × 2,000 / 10,000 = 0.081 ms. In a frame of 16.67 ms that is 0.5 %, so the rebuilds cost little, and the counter only tells you where they come from. The budget of 0.6088 ms for 10,000 elements gives 0.12 ms at most.

   (d) The limit `c_MaxBoundAtlases` is 4, so a canvas with up to four fonts is one draw call. Six fonts need at least two draws: four atlases in one and two in the next. The page lists the CPU stage `Render.UI` and the GPU stage `GPU.UI` for the work of the pass. The font limit of one scene is 256, far above six.
   :::
