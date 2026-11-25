---
id: core/review
title: "Review: engine architecture"
description: "The questions of every page of the part on the engine's architecture, and exercises that use several of its pages together."
tracks: [E]
status: final
generated: review
---

## Cumulative exercises

These exercises need more than one page of the part, so try each one before you open its worked solution.

1. **Basic.** You add a function `ToTitleCase` to the engine in three new files, which stand beside the header `StringUtils.h` and its tests in `StringUtilsTests.cpp`:

   ```text
   Strata/src/Strata/Core/TitleCase.h
   Strata/src/Strata/Core/TitleCase.cpp
   StrataTests/src/Core/TitleCaseTests.cpp   (suite: Core.TitleCase)
   ```

   Which library holds the source file, and which layers may it include? Does the build need a new configure step? Which program runs only your tests, and with which option? Which two lines open the source file?

   :::answer[Worked solution]
   The folder is `Core`, and no `Exclude` of the table removes this file, so it belongs to the layer `Core` and its library `Strata_Core`. The row of `Core` has an empty `MayInclude`, so the file may include no other engine layer.

   All three files are new, and the build collects its files at the configure step. You run `cmake --preset <preset>` again before you build.

   The tests run in `StrataTests`, started with `--test-suite=Core.TitleCase`, which runs your suite alone. An engine source file starts with `#include "stpch.h"`, and its own header follows: `#include "Strata/Core/TitleCase.h"`.
   :::

2. **Basic.** A person holds a game at a breakpoint for 60 s. The step is 1/60 s and the cap is 8 steps, the defaults, and the accumulator holds nothing. Then the game runs one frame.

   (a) How long is the frame's time step? How many steps are due, how many run and how many are dropped? What stays in the accumulator?

   (b) Answer again with a time scale of 0.5.

   :::answer[Worked solution]
   (a) The application clamps the time step of 60 s to 0.25 s, because `MaxTimestep` is 0.25 s. Then 0.25 / (1/60) = 15 steps are due. The cap lets 8 run, which leaves 7 due. The loop drops the backlog but keeps one step in the accumulator, so 6 steps are dropped and 16.67 ms stay.

   (b) The clamp comes first and the scene multiplies afterwards, so the delta time is 0.25 × 0.5 = 0.125 s. That is 7.5 steps. Seven run, which is below the cap, so nothing is dropped, and half a step, 8.33 ms, stays in the accumulator.
   :::

3. **Basic.** A program lists four engine modules in this order: P, Q, R and S. P starts after R, and Q starts after S. R and S start after nothing. A layer logs `L` in its update.

   (a) Give the start order of the registry, and the order that a queue version of Kahn's algorithm gives.

   (b) List the hooks of one normal frame in the order they run.

   (c) In the next frame, S answers `Skip` from `OnBeginFrame`. Which hooks run, and does the loop count the frame?

   :::answer[Worked solution]
   (a) The waiting counts are P 1, Q 1, R 0 and S 0. The registry scans the listing from the top and takes R, the first ready module. Then P is ready and stands first, so it takes P. Next it takes S, and Q last, so the order is R, P, S, Q.

   A queue holds R and S at the start. It places R and adds P behind S, then places S and adds Q. That gives R, S, P, Q.

   (b) The start order is R, P, S, Q. The frame runs `OnBeginFrame` of the four modules in this order, then the layer's update `L`. Then come `OnUpdate` and `OnRenderUI` of the four, each in the same order. `OnEndFrame` runs in reverse: Q, S, P, R.

   (c) R, P and S get `OnBeginFrame`, and S answers `Skip`. No other hook runs for the frame: Q gets no begin call, the layer does not update and nobody gets `OnEndFrame`. The loop sleeps 16 ms and does not count the frame.
   :::

4. **Medium.** A windowed editor runs on macOS, on a display with a content scale of 2, and its window has 1440 by 900 points. The editor's layer sets `Handled` on the first `WindowClose` it sees, to ask about unsaved changes, and on no other. The person clicks close at frame 300 and again at frame 420.

   How many pixels wide and high is the framebuffer? How many pixels does a panel of 360 points cover? After which frame does the loop end, and with which exit code?

   :::answer[Worked solution]
   On a display counted in points, the framebuffer is the window's size times the scale: 1440 × 2 = 2,880 pixels wide and 900 × 2 = 1,800 high. A panel of 360 points covers 360 × 2 = 720 pixels.

   The first close reaches the layer, which sets `Handled`, so nobody else sees it and the loop continues. The second close finds no layer that handles it, so after the layers the application sets `m_Running` to false.

   A close never stops a frame in the middle: frame 420 runs to its end, and the loop ends after it. The run did not fail and no signal arrived, so the exit code is 0.
   :::

5. **Medium.** A game is capped at 60 frames a second. In one frame the queue takes 0.4 ms, the input 0.6 ms, the layers 3.0 ms, the modules' update 1.0 ms and `OnRenderUI` 2.0 ms. The graphics module also waits 5.0 ms in `OnBeginFrame` and reports it, and presenting takes 1.5 ms.

   (a) What is the frame's work time?

   (b) Ten intervals between frames, in milliseconds, are 16.7 eight times, then 33.4 and 50.1. Give the mean, P50 and P95.

   (c) The medians are an interval of 16.7 ms, the work time of (a) and a busy time of the graphics processing unit (GPU) of 6 ms. What limits the frame? What changes if the GPU is busy for 16 ms?

   (d) You add an outer stage of 2.5 ms inclusive that wraps an inner stage of 1.5 ms, and no other stage is open around them. What does each record? By how many milliseconds does the row for the rest of the frame shrink, compared with the frame before you added them?

   :::answer[Worked solution]
   (a) The work time counts the work up to the last `OnRenderUI`. It omits the reported wait and the present, so it is 0.4 + 0.6 + 3.0 + 1.0 + 2.0 = 7.0 ms.

   (b) The sum is 8 × 16.7 + 33.4 + 50.1 = 217.1 ms, so the mean is 21.71 ms. By nearest rank, P50 takes the sample at rank ⌈0.5 × 10⌉ = 5, which is 16.7 ms. P95 takes rank ⌈0.95 × 10⌉ = 10, the largest sample, 50.1 ms. The mean hides the hitch, and P95 shows it.

   (c) A frame is CPU-bound from 90 % of the interval, which is 15.0 ms. The work time of 7.0 ms and the GPU time of 6 ms are both below it, so nothing works at its limit and the frame is capped: the cap sets its pace. With 16 ms of GPU busy time, the GPU is above 15.0 ms and above the work time of 7.0 ms, so the frame is GPU-bound.

   (d) A stage records its self time. The inner stage records 1.5 ms, and the outer stage records 2.5 − 1.5 = 1.0 ms. The two self times add up to 2.5 ms, so the row for the rest of the frame shrinks by 2.5 ms, not by 4.0 ms.
   :::

6. **Medium.** On Linux you start `StrataEditor --headless --frames 600` in a terminal.

   (a) What kind of run is it, and how long does it last with no interruption?

   (b) You press **Ctrl+C** after 4 s. About which frame is the loop in, and when does the loop end? What exit code does the shell see?

   (c) You press **Ctrl+C** again 0.1 s later, while the editor closes. What happens?

   (d) A request arrives during frame 600, the last one. What is the exit code?

   :::answer[Worked solution]
   (a) The option `--headless` makes it a Console run. The editor sets `MaxFrameRate` to 60 for a headless run, so 600 frames last about 600 / 60 = 10 s.

   (b) At 60 frames a second, 4 s is about frame 240. The handler only counts the request. The loop honours it after the frame in progress, logs a warning, sets the exit code 130 and ends. The shell sees 130.

   (c) The second request finds the counter above 0, restores the default action of the signal and raises it again. The system ends the process in the middle of its closing, and the log lines not yet written are lost. The shell still reports 130, which is 128 plus the signal number 2.

   (d) A request in the frame where `--frames` ends the run changes nothing, because the run was over already. The exit code stays 0.
   :::

7. **Medium.** The job system's file `Strata/src/Strata/Core/JobSystem.cpp` must read the memory budget of the graphics device, to choose how many background imports run. A colleague adds an include of a header of the graphics module.

   (a) What does `Architecture.Layering` say, and why?

   (b) Name two fixes that the rules forbid and one that they allow, with its steps.

   (c) The editor starts with `--no-gpu`. What does the file get, and what must it do?

   (d) May the file ask in the constructor of `JobSystem`, or only when it chooses the work?

   :::answer[Worked solution]
   (a) The file lies in the layer `Core`, whose row has an empty `MayInclude`, so it may include no other layer. The test reports the file, the line and both layers, and fails.

   (b) Adding the graphics layer to `MayInclude` and adding a line to the allowlist are both forbidden.

   The allowed fix inverts the dependency. The layer `Core` defines an interface, such as a budget with one function. The renderer implements it, and its registration in the composition root registers it with `EngineServices::Register`, as it does for `IAssetGraphics`. The job system calls `EngineServices::Get<T>()` for that interface. The file cannot use `Find<T>()` of the module registry, because that needs the module's header.

   (c) The composition root runs for every start, so the renderer's registration ran and `Get` returns the implementation. But `--no-gpu` drops the Graphics module, so no device exists, and the implementation has no budget to report; the pin's `IAssetGraphics` answers 0 then. The file must handle a budget of 0, and a null `Get` in a program that registered nothing: it chooses a default number of imports.

   (d) The service exists before the application, but the device does not. The job system starts first in the constructor of the application, before the window and the modules, and the Graphics module makes the device in its `OnInit`, later. A question in the constructor would always find no budget, so the file asks when it chooses the work.
   :::

8. **Hard.** The editor runs on a computer with 8 hardware threads. In one frame the main thread calls `ParallelFor(10000, 256, ...)` over the records of 10,000 transforms.

   (a) How many batches are there, how many items has the last one and how many helpers does the call queue?

   (b) Every worker is busy with other jobs. Who runs the batches, and what happens to the helpers?

   (c) Why is the result the same with 1 thread and with 7 threads?

   (d) Another job reads a file of 4 MB and finishes while the frame is in its layers. Which pool should it run on, and when does the main thread use its result?

   :::answer[Worked solution]
   (a) The batch size is 256, and 10,000 / 256 = 39.06, which rounds up to 40 batches. The last batch starts at 39 × 256 = 9,984 and ends at 10,000, so it has 16 items. A machine with 8 hardware threads has 7 workers. The call queues at most one helper for each pool thread and at most one fewer than the batches: min(7, 39) = 7.

   (b) The caller takes batches too, so a busy pool still makes progress. The caller takes all 40 through the atomic counter, drops the helpers that have not started, and returns without waiting for them.

   (c) Each job writes only the records of its own items, and the main thread publishes the records in order afterwards. No result depends on which thread ran a batch or in what order the batches ended.

   (d) Reading a file waits for the disk, so the job goes to the I/O threads with `SubmitIO`. It hands its result in through `SubmitToMainThread`, and never touches the scene. The main thread runs the function at the start of the next frame, in the main-thread queue. If the program ends first, the queue runs once more after the last frame.
   :::

9. **Hard.** A tool reads a 4×4 matrix from a project file and writes `ST_CORE_ASSERT(DecomposeTransform(matrix, translation, rotation, scale), "bad matrix");`. Then it uses the three results. The tool works in `Debug` and shows garbage in Dist.

   (a) Explain the fault.

   (b) Say which of assert, verify or returned error fits, with the reason, and write the right code.

   (c) For a matrix that mirrors Y only, with no rotation, what does the function return?

   (d) A camera has the near distance 0.1 and an infinite reversed-Z projection. What depth does a point 25 units away get? At which distances lie the two points that `Ray::FromNDC` takes, with the depths 1 and 0.5?

   :::answer[Worked solution]
   (a) A Dist build compiles `ST_CORE_ASSERT` out, and the condition goes with it. The call never runs, so the three outputs keep whatever they held, and the tool uses them. In `Debug` the call ran, so the tool worked. A condition with a side effect makes the two builds two different programs.

   (b) The file can hold a broken matrix, a failure that the world causes. That is a returned error and one log line. An assert and a verify are for a programmer's mistake.

   The code keeps the result in a variable: `const bool decomposed = DecomposeTransform(matrix, translation, rotation, scale);`. Then `if (!decomposed)` it logs once and returns the failure to its caller. The function leaves its outputs untouched when it fails, so the caller keeps its old values.

   (c) It returns `true`. A mirror has no rotation that reproduces it, so the function folds the mirror into X: the scale is (−1, 1, 1) and the rotation is a half turn about Z. The matrix rebuilt from these parts is the same, but the parts differ from the scale (1, −1, 1) that was put in.

   (d) The depth is near / d = 0.1 / 25 = 0.004. Solve d = near / depth for the two points: the depth 1 gives d = 0.1, and the depth 0.5 gives d = 0.2. Both are finite and lie on one ray. The depth 0 lies at an infinite distance, which a ray cannot pass through.
   :::

10. **Hard.** The editor saves a document of 100 MB with `AtomicFileWriter`. Shortly before, it logged one warning and then 30 `Info` lines. After 60 MB are written, an access violation kills the process.

    (a) What does the document's folder hold afterwards, and what is the name of the extra file?

    (b) Which of the logged lines can the log file lack?

    (c) You start the editor again at once to read the log. What do you find, and what should you have done first?

    (d) Why does the document never show half a save?

    :::answer[Worked solution]
    (a) The writer gathers bytes into `<path>.tmp<n>` and renames that file over the document only in `Commit`. The crash came before the commit, so the folder holds the old document whole, and a temporary file with 60 MB or less. A failed write removes its temporary file, but a crash runs no code, so the file stays.

    (b) A warning is on disk when its call returns, because the call waits for the writer to flush, and the writer writes in order. The warning is in the file. The 30 `Info` lines may sit in the queue of the writer thread, and the crash can lose them, all 30 in the worst case.

    (c) The file `StrataEditor.log` is emptied at every start, so the log of the crashed run is gone. You should have copied the file before the new start. If a second editor is open, it shares the same file, so its start empties it as well.

    (d) The rename is one step: a reader sees either the old document or the new one, never a mix. Until `Commit`, the new bytes live only in the temporary file.
    :::
