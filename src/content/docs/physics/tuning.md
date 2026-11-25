---
id: physics/tuning
title: "Tuning and measuring"
description: "Measure a physics scene with Strata's instruments, change one solver setting, and show with numbers what the change did."
kind: how-to
size: M
tracks: [E]
needs: [physics/world-step, core/profiling]
time: 90
learn:
  - id: read-instruments
    text: find the step time, the awake bodies and the recycled share of a running scene in the Streaming panel and in physics.stats
  - id: change-setting
    text: change a field of the Physics Simulation section and measure what it did to the numbers
  - id: ceiling
    text: compute the contact stiffness that box3d really uses from the fixed rate and the setting
  - id: compare-layouts
    text: compare two settings of a chaotic scene by medians over many layouts
  - id: run-sweep
    text: run the physics perf tests and the sweep tool and read their reports
since: 0.7.0
status: final
---

A physics setting is a guess until a number backs it. This page measures one scene, the Physics Playground, changes one tuning setting, and shows with numbers what changed. Before you start:

- You have a copy of the Physics Playground open in the editor (**Open Sample...** on the welcome window), and its scripts are built.
- You know what each field of the section does inside a step: [the page on dynamics](../physics/dynamics.md) teaches it, and [Collision detection](../physics/collision-detection.md) teaches contact recycling.
- For the last section you have the source build in Release from [your first change to the engine](../core/first-change.md), its `StrataTests` program, and Python 3.

## The instruments

You cannot tune what you cannot see, so Strata keeps counters while it steps. Each one has a cost, and the cost decides where you may read it. The table lists them from the cheapest to the dearest.

| Instrument | What it counts | Where you read it |
| --- | --- | --- |
| `IPhysicsDiagnostics` and its `PhysicsStepInfo` | The last step's times, the awake and sleeping bodies, kept as the world steps so that a read takes :term[constant time]{id=constant-time} | The Streaming panel, `editor.status`, the perf log of a running game |
| Settling instruments | The fastest body's speed, the bodies faster than their :term[sleep threshold]{id=sleep-threshold}, and the resting jitter in mm | `physics.stats` under `settling` |
| Box3d's stage profile | The time of box3d's stages (pairs, collide, solve, sensors), summed over the steps of one :term[fixed step]{id=fixed-step} | `physics.stats` under `step` |
| Box3d's counters | Islands, contacts, awake contacts and recycled contacts | `physics.stats` under `contacts`, and the Streaming panel's share |
| Contact storage growth | The peak of contacts and how often box3d's storage grew while playing | `physics.stats` under `contacts` |
| `PhysicsStats` | Everything above, plus counts that need a walk over every :term[body record]{id=body-record} | `physics.stats` only, never every frame |

Two rows need a word. The counters cost about 0.1 ms per step at 70,000 bodies, because box3d counts its memory with them and walks every island. So Strata reads them only while **detailed statistics** are enabled, a switch that makes the world read box3d's counters after every step. Without it `physics.stats` reports them as null, unless you ask with `detail: true` to read them once. The settling speeds are displacements over one fixed step, a proxy: box3d decides sleep with its own measure, so a body counted as settling may still fall asleep.

The settling sums are whole numbers that add up exactly in any order. So they give the same value with one thread or twelve, and a change in them is a change in the scene, never in the thread timing.

## Read the numbers of a running scene

The first list measures the scene as it is, before you change anything. Keep the numbers you read: the later sections compare against them.

:::::steps

1. Press **Play** with the Playground open. Open the **Streaming** panel and find its **Physics** section.

   **You should see:** a bar named Bodies with the used slots against the capacity, a line that says "Never grew" or "Grew 1 time, the last in" some milliseconds, and "reserves" some MB. Below them a line reads "Step 1.42 ms (box3d 0.91)" in the form of your own numbers, then "awake" some number "of" the awake and sleeping bodies together.

   **If you do not see it:** the section shows only while a game with physics runs. Press **Play** again, and if the scene has no bodies the section says so. A copy of a sample may also need its scripts built first: run the command `script.build`.

   **Why:** the line counts the growths of the world's room for bodies. A new world reserves room for twice its scene's bodies rounded up to a power of two, at least 1,024, so the Playground's bodies fit at once and the line says "Never grew". A world grows only when bodies created while it runs pass that room. Strata then remembers what the world needed, so the next play reserves it at once. Contacts have storage of their own, and `physics.stats` counts its growths under `contacts`.

2. Check **Count contacts** in the same section.

   **You should see:** after a few steps a second fact joins the step line, "recycled" and a percentage. While the balls still roll, it is lower; once the pit rests it rises to most of the awake contacts. The check box runs the command `physics.setDetailedStats`.

   **If you do not see it:** when no contact is awake, the share has nothing to divide, so the panel hides it. Shoot a ball or fly into the pit to wake some bodies, and the share returns.

:::::

::figure{id=streaming-physics}

The panel shows a summary. The complete answer comes from one command, `physics.stats`, which no menu or button shows. The next step gives the line to paste, and [Editor commands](../editor/commands.md) teaches commands in general.

:::::steps

1. With the editor open, run this in a terminal. The program `StrataCLI` finds the running editor itself and prints the answer.

   ```sh
   StrataCLI call physics.stats
   ```

   **You should see:** one :term[JSON object]{id=json-object}. Its `step` group holds the last step's milliseconds and the stages of box3d's part. The `sleep` group holds awake, sleeping and moving bodies. The `contacts` group holds the totals and `recycledShare`. The `settling` group holds the fastest body's speed, and the `settings` group the tuning that applies now.

   **If you do not see it:** the answer reads `{running: false}` while you edit, so start the game first. Several editors may run: pass `--project <dir>` to pick one.

   **Why:** the answer walks every body record to count them, so a person asks for it and the panel never does.

:::::

The answer of a paused game after 600 fixed steps, reduced to the five groups:

```text capture="physics-stats-answer"
{
  "step": {
    "library": {
      "collide": 0.08590000122785568,
      "constraints": 0.35749998688697815,
      "continuous": 0.0,
      "islands": 0.00019999999494757503,
      "pairs": 0.01810000091791153,
      "refit": 0.00139999995008111,
      "sensors": 0.00860000029206276,
      "solve": 0.4178999960422516,
      "splitIslands": 0.0,
      "transforms": 0.05609999969601631
    },
    "libraryMs": 0.5311999917030334,
    "ms": 0.8112999796867371,
    "parts": {
      "apply": 9.999999747378752e-05,
      "characters": 0.0,
      "checkedPairs": 0.05689999833703041,
      "events": 0.0020000000949949026,
      "instruments": 0.00279999990016222,
      "pairs": 0.1607000082731247,
      "sync": 0.02410000190138817,
      "writeBack": 0.03350000083446503
    },
    "strataMs": 0.2800999879837036,
    "totalLibraryMs": 301.5653997659683,
    "totalMs": 468.24849981069565,
    "workers": 24
  },
  "sleep": {
    "awake": 653,
    "islands": 48,
    "moving": 723,
    "sleeping": 70
  },
  "contacts": {
    "awake": 3575,
    "capacity": 2048,
    "detailed": true,
    "lastGrowthStepMs": 1.44350004196167,
    "peak": 3751,
    "recycled": 3563,
    "recycledShare": 0.9966433566433567,
    "roomGrowths": 1,
    "total": 3682,
    "tracked": 2222
  },
  "settling": {
    "maxSpeed": 1.1975626945495605,
    "restingJitterMm": 0.04501130059361458,
    "settling": 16
  },
  "settings": {
    "contactDampingRatio": 10.0,
    "contactHertz": 30.0,
    "contactPushSpeed": 3.0,
    "contactRecycleDistance": 0.05000000074505806,
    "effectiveContactHertz": 29.999998092651367,
    "sleepThreshold": 0.07999999821186066,
    "source": "defaults"
  }
}
```

1. **Lines 3-15:** the library's stages and their sum `libraryMs`; the stages nest, so `constraints`, `transforms` and the others run inside `solve` and the list does not add up to the sum.
2. **Lines 17-27:** Strata's own `parts` of the step and `strataMs`.
3. **Line 45:** `recycledShare`, present because the detailed counting was on.
4. **Lines 55-63:** the `settings` group names the five values the world runs with and `effectiveContactHertz`, which a later section explains.

## Change one setting

You tune a setting by one change and one comparison. The five fields of the `Physics.Simulation` section belong to the project, and they apply to the running game at its next fixed step. Each has a range: the settings page and `project.setSettings` refuse a value outside it and change nothing. A world that gets a value from code moves it to the nearest end, and a value that is not a number becomes the default.

| Field | Default | Range | What it changes |
| --- | --- | --- | --- |
| `ContactRecycleDistance` | 0.05 m | 0 to 1 | How far touching bodies may move before box3d computes again their contact; 0 disables recycling |
| `SleepThreshold` | 0.08 m/s | 0 to 1 | The speed under which a body, with every body it touches, may fall asleep; 0 keeps all awake |
| `ContactHertz` | 30 | 1 to 240 | How stiffly contacts push overlapping bodies apart |
| `ContactDampingRatio` | 10 | 0 to 100 | How strongly contacts damp the bounce of that push |
| `ContactPushSpeed` | 3 m/s | 0.01 to 100 | The fastest speed with which overlaps are pushed apart |

Why each does what it does belongs to [the page on dynamics](../physics/dynamics.md): its sleep section for the threshold, its soft contact section for the other three. Here the question is only what you can read. Stop the game before the next list and read the numbers of the previous one again: they are your baseline.

:::::steps

1. Open the **Project Settings** panel, choose the **Physics** category and its **Simulation** page, and change **Sleep threshold (m/s)** to `0`. Press **Play**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Edit the field of the page; its tooltip names the default, and **Reset to Defaults** restores all five.
   :::
   :::tab[With a command]
   Run the command with the section and its new value. The value replaces the whole section, so fields you omit return to their defaults.

   ```sh
   StrataCLI call project.setSettings '{"section": "Physics.Simulation", "value": {"SleepThreshold": 0}}'
   ```

   :::
   ::::

   **You should see:** the Streaming panel's "awake" never falls: the first number stays equal to the second, and the step time stays at its busy value. In `physics.stats` the `sleep` group shows no sleeping bodies, and `settings.sleepThreshold` reads 0.

   **If you do not see it:** the command changes the project, not the scene: check that the answer's `isDefault` is false. The editor also writes the project file in the background.

   **Why:** a threshold of 0 means no body is ever slow enough, so every body costs its full step. The default 0.08 m/s is higher than box3d's own 0.05 m/s because at 0.05 the pits of balls took about a third longer to fall asleep.

2. Run the command with `reset` to return to the defaults.

   ```sh
   StrataCLI call project.setSettings '{"section": "Physics.Simulation", "reset": true}'
   ```

   **You should see:** the answer holds `isDefault` true, and after a few seconds of play the bodies of the pit sleep again.

   **If you do not see it:** a game that runs reads the change at its next fixed step, so wait one step. The change also stays after you stop play, so a forgotten test value stays in the project.

:::::

The drawing shows the Simulation page as the editor's code lays it out:

::figure{id=simulation-page}

### The stiffness ceiling

One field has a limit that only its tooltip names. Raise **Contact stiffness (Hz)** from 30 to 60, run the game, and read `physics.stats`: `settings.contactHertz` says 60, but `settings.effectiveContactHertz` still says 29.999998, which is 30 up to the rounding of a float. The value does nothing, because box3d solves each fixed step in 4 inner steps and caps the stiffness at an eighth of their rate per second. Strata computes the same cap so that you can read it.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L5658-L5666" symbol="PhysicsWorld::GetEffectiveContactHertz"
float PhysicsWorld::GetEffectiveContactHertz(float timestep) const
{
	const PhysicsSettings& settings = m_Data->Settings;
	if (!(timestep > 0.0f) || !std::isfinite(timestep))
		return settings.ContactHertz;
	// As b3World_Step computes it: its substep rate is the solver's substeps over each box3d step's time.
	const float subStepRate = static_cast<float>(c_SolverSubSteps) * static_cast<float>(settings.CollisionSteps) / timestep;
	return std::min(settings.ContactHertz, 0.125f * subStepRate);
}
```

The function reads the setting, finds the inner-step rate, and returns the smaller of the setting and one eighth of the rate. Look at how `c_SolverSubSteps` (4) and `CollisionSteps` multiply the rate before the division by the step's time.

A worked example with real numbers. Each fixed step runs 4 inner steps. At 60 fixed steps per second, one fixed step lasts 1/60 s, so the rate is 4 × 1 / (1/60) = 240 inner steps per second. The ceiling is 240 / 8 = 30 Hz. The default setting 30 sits exactly on it, and any value above it does nothing.

Two more rates show the rule. At 120 steps per second the ceiling is 60 Hz, so 60 then acts. At 30 steps per second it is 15 Hz, and the default 30 is already above it. A value below the ceiling does act: at 20 a tower of 20 crates leaned 88 mm instead of 9 mm, as the field's own description records.

Raising `CollisionSteps` also raises the ceiling: two steps per fixed step at 60 fixed steps gives 480 / 8 = 60 Hz. No project setting holds it, and only code sets it: the field `CollisionSteps` of `PhysicsSettings` in `Strata/src/Strata/Physics/PhysicsTypes.h`, which Strata clamps to 1 to 64 in `Strata/src/Strata/Physics/PhysicsWorld.cpp`. Its documented use is very fast bodies, not stiffness.

## Measure with the test tools

The panel and the answer measure one play of one scene on your machine. The engine's own tools measure many scenes in processes that do not share anything.

First, the perf tests. They run in Release and :term[Dist]{id=dist} only, against budgets that live in one file, `StrataTests/Perf/Budgets.json`, never in the test code. A metric that exceeds its budget gets up to three tries, and the test fails only when all three exceed it. [The perf lab](../engineering/perf-lab.md) teaches the method of the budgets and the reference machine.

:::::steps

1. Run the physics perf tests from the folder of the source build in Release. The first command runs only the physics suite, the second runs every perf test.

   ```sh
   build/windows/bin/Release/StrataTests --test-suite=Perf.Physics --no-intro=true
   ctest --preset windows-release -L perf
   ```

   **You should see:** each metric printed with its attempts, for example `Perf.Physics.Boxes70k.StrataStepTime`, and a final count of passed test cases. A metric with a `Provisional` entry is printed and recorded, and never fails.

   **If you do not see it:** a Debug build refuses perf tests, so build and run the Release configuration. Other work on the machine adds to every time, so close it. Replace `windows` by `linux` or `macos` for your preset.

:::::

Second, the sweep. A **settle scene** is a test scene of the engine in which bodies come to rest. Examples are a pit of 500 or 2,000 balls, a tower of 20 crates or a row of falling tiles. The tool `Tools/PhysicsSweep.py` runs a settle scene once per point, in a fresh process of the `StrataTests` helper `physics-settle` with one setting changed.

The command `report` turns the results into tables. Its results stay in a folder outside the :term[repository]{id=repository}: you give it one.

The commands name their goals. `distances` varies the contact recycle distance. `knobs` varies the other settings one at a time at one distance. `workers` varies box3d's worker threads. `pits` plays the ball pits in many layouts, and `playground` plays the Physics Playground through an editor without a window.

:::::steps

1. Sweep one knob on the settle scenes and write the results to a folder of your own.

   ```sh
   python Tools/PhysicsSweep.py knobs --tests build/windows/bin/Release/StrataTests --output sweep --distance 0.05
   python Tools/PhysicsSweep.py report --output sweep
   ```

   **You should see:** the first command runs one fresh process per point and ends without an error (:term[exit code]{id=exit-code} 0). The second prints a table and writes it to `sweep/report.md`: one row per scene and setting, with when 99 % and all bodies slept, the milliseconds of the steps, and the recycled share.

   **If you do not see it:** the tool holds the perf lock so that it never measures beside another measurement: pass `--no-lock` on a machine that you use alone. An interrupted sweep continues where it stopped, because it skips points whose result file exists.

:::::

The tool measures in two ways. Times on the processor repeat three times, with the points interleaved, so that the machine's noise falls on every point alike. The probe scenes, whose results are fixed by the physics, run once. A third kind is different, and the next section explains it.

## Compare chaotic scenes over many layouts

A pile of balls is a **chaotic** system: a difference in the last bit of one ball's start changes the time the pile needs to fall asleep by seconds. So one run ranks nothing. Strata's answer is the layouts: the `pits` command plays each pit in nine arrangements of the same grid, with the balls' fixed offsets shifted, per recycle distance and sleep threshold. The report gives each point's median, lowest and highest time to 99 % asleep over the layouts, and how many slept. Its measure is simulated seconds, so it runs without the perf lock and several runs at a time (`--jobs`).

Here is the reason in numbers. The sketch holds two invented times per layout, for the thresholds 0.08 and 0.05 m/s: invented, because only the real tool can measure yours.

```cpp sketch="physics-tuning-layouts.cpp"
// Ranks two settings by the median, lowest and highest time over nine layouts, as one run cannot.
#include <algorithm>
#include <cstdio>
#include <vector>

// Prints the median, lowest and highest of a list of times in seconds.
static void Report(const char* name, std::vector<double> times)
{
	std::sort(times.begin(), times.end());
	std::printf("%s: median %.1f s, lowest %.1f s, highest %.1f s\n", name, times[times.size() / 2], times.front(), times.back());
}

int main()
{
	// Invented seconds to 99 % asleep, one entry per layout of the same pit.
	const std::vector<double> threshold008 = { 14.2, 19.8, 12.9, 16.1, 25.3, 13.7, 18.4, 15.0, 17.6 };
	const std::vector<double> threshold005 = { 17.0, 21.5, 16.8, 22.9, 19.4, 24.1, 18.8, 20.2, 26.6 };
	Report("threshold 0.08", threshold008);
	Report("threshold 0.05", threshold005);
	return 0;
}
```

```text output-of="physics-tuning-layouts.cpp"
threshold 0.08: median 16.1 s, lowest 12.9 s, highest 25.3 s
threshold 0.05: median 20.2 s, lowest 16.8 s, highest 26.6 s
```

1. **Line 7:** `Report` takes the list by value, so sorting it leaves the caller's list unchanged.
2. **Line 10:** the median is the middle entry of the sorted list, here the fifth of nine; the first and last entries are the lowest and the highest.
3. **Lines 16–17:** the nine times, one per layout of the same pit.

Compare the lists layout by layout: the lower threshold wins one single run of nine, the layout with 25.3 s against 19.4 s, so a person who ran only that layout would pick it. The medians show 0.08 about a quarter faster. The engine's test of the pit follows the same rule. Its bound is 1.25 times the slowest time that any layout showed, also with contact values a few bits off the defaults. Towers and pyramids moved by less than 0.1 mm under those changes, so their bounds are 1.25 times one measure.

## Result

You can read a scene's step, its awake bodies and its recycled share. You changed a project setting and measured it against a baseline. You computed the stiffness that box3d really applies. You know which tool answers which question: the panel for one play, `physics.stats` for the full picture, the perf tests for budgets, and the sweep for a default.

## Variations

The same goal under other conditions.

- **A ball pit that never sleeps.** With `SleepThreshold` 0, or a pit of balls that keep bumping, the awake count never falls. Read `settling.maxSpeed` and `restingJitterMm`: a pit with a jitter above zero mm is still moving, and the fix is a larger threshold or a damper contact, not a change of the pit. [Physics for game makers](../make/physics.md) shows the game maker's side of it.
- **A `ContactHertz` above its ceiling.** Read `effectiveContactHertz` before you believe a value acted. If it did not move, the ceiling cut it: change the fixed rate (the project's `Scene.Timing` section, pictured on [Projects and settings](../world/projects-settings.md)) or `CollisionSteps` in code.
- **Contact recycling for a kinematic platform.** Strata creates kinematic and character presence bodies with recycling off, whatever `ContactRecycleDistance` says. A recycled contact keeps its old points, so riders on a platform that turns crept 0.70 m in 4 s, against 17 mm without recycling. The test `Physics.Settling` guards this: see exercise 3.
- **Process defaults for tests and tools.** No project setting holds the capacities of a test world. `PhysicsSystem::SetDefaultSettings` in `Strata/src/Strata/Physics/PhysicsSystem.h` sets what physics systems created afterwards copy, and the project's `Physics.Simulation` section overrides the tuning of it.
- **Very fast bodies.** `CollisionSteps` is clamped to 1 to 64 and raises the cost of every step: use it only when the bodies tunnel through thin walls.

## Summary

- The Streaming panel's Physics row and `physics.stats` give the step time, the awake bodies and, with **Count contacts**, the recycled share.
- A field of `Physics.Simulation` is checked against its range, applies at the next fixed step, and you measure it against a baseline you read before the change.
- The contact stiffness that applies is the smaller of `ContactHertz` and one eighth of the inner-step rate: 30 Hz at 60 fixed steps per second.
- A chaotic pile is compared by the medians, the lowest and the highest over many layouts, never by one run.
- The perf tests check metrics against `StrataTests/Perf/Budgets.json`, and `Tools/PhysicsSweep.py` sweeps settings over the settle scenes and reports.

## Check yourself

1. The Physics row reads "Step 1.42 ms (box3d 0.91) - awake 1,204 of 9,876" and shows no recycled share. How much of the step is Strata's own work, and what must you do to see the share?

   :::answer{tests="read-instruments"}
   Strata's part is the rest: 1.42 minus 0.91 is 0.51 ms. The share appears only while detailed statistics count box3d's contacts, so check **Count contacts**, which runs `physics.setDetailedStats`, and wait for a few steps with awake contacts.
   :::

2. A game steps at 30 fixed steps per second and keeps `ContactHertz` at 30. Which stiffness does box3d use?

   :::answer{tests="ceiling"}
   The inner-step rate is 4 × 30 = 120 per second, and one eighth of it is 15 Hz. The setting 30 is above the cap, so box3d uses 15 Hz, and `effectiveContactHertz` shows it.
   :::

3. You set `SleepThreshold` to 0 and the Playground's step time stays high. Why, and how do you confirm it in `physics.stats`?

   :::answer{tests="change-setting"}
   No body is ever slow enough to sleep, so every moving body stays in the step. The `sleep` group then shows no sleeping bodies, and `settings.sleepThreshold` reads 0.
   :::

4. One run of a ball pit at threshold 0.05 slept 2 s before the run at 0.08. Can you call 0.05 better?

   :::answer{tests="compare-layouts"}
   No. A pit's time to sleep is chaotic, so one pair of runs ranks nothing. Compare the medians, lowest and highest over nine layouts with the `pits` command.
   :::

5. Which sweep command runs without the perf lock, and why?

   :::answer{tests="run-sweep"}
   The `pits` command: its measure is simulated seconds, not wall time, so other work on the machine cannot change it, and it may run several points at a time.
   :::

## Exercises

1. **Basic.** Change the sketch so that it prints how many of the nine single runs the lower threshold wins.

   :::answer[Worked solution]{tests="compare-layouts" solution="sketches/physics-tuning-medians.cpp"}
   Count the layouts in which the second list holds the smaller time, and print the count before the medians. The count is 1 of 9, yet the medians rank the settings the other way: the count alone would mislead.

   ```cpp sketch="physics-tuning-medians.cpp"
   // Ranks two settings by the median, lowest and highest time over nine layouts, as one run cannot.
   #include <algorithm>
   #include <cstdio>
   #include <vector>

   // Prints the median, lowest and highest of a list of times in seconds.
   static void Report(const char* name, std::vector<double> times)
   {
   	std::sort(times.begin(), times.end());
   	std::printf("%s: median %.1f s, lowest %.1f s, highest %.1f s\n", name, times[times.size() / 2], times.front(), times.back());
   }

   int main()
   {
   	// Invented seconds to 99 % asleep, one entry per layout of the same pit.
   	const std::vector<double> threshold008 = { 14.2, 19.8, 12.9, 16.1, 25.3, 13.7, 18.4, 15.0, 17.6 };
   	const std::vector<double> threshold005 = { 17.0, 21.5, 16.8, 22.9, 19.4, 24.1, 18.8, 20.2, 26.6 };
   	int lowerWins = 0;
   	for (int layout = 0; layout < 9; layout++)
   		lowerWins += threshold005[layout] < threshold008[layout] ? 1 : 0;
   	std::printf("threshold 0.05 wins %d of 9 single runs\n", lowerWins);
   	Report("threshold 0.08", threshold008);
   	Report("threshold 0.05", threshold005);
   	return 0;
   }
   ```

   ```text output-of="physics-tuning-medians.cpp"
   threshold 0.05 wins 1 of 9 single runs
   threshold 0.08: median 16.1 s, lowest 12.9 s, highest 25.3 s
   threshold 0.05: median 20.2 s, lowest 16.8 s, highest 26.6 s
   ```

   1. **Line 7:** `Report` takes the list by value, so sorting it leaves the caller's list unchanged.
   2. **Line 10:** the median is the middle entry of the sorted list, here the fifth of nine; the first and last entries are the lowest and the highest.
   3. **Lines 16–17:** the nine times, one per layout of the same pit.
   4. **Lines 19–20:** the loop counts the layouts in which the lower threshold ran faster.
   :::

2. **Medium.** Run the knobs sweep at distance 0.05 and find from `report.md` the row where a changed `--contact-damping` has the longest time to 99 % asleep.

   :::answer[Worked solution]{tests="run-sweep"}
   Run `python Tools/PhysicsSweep.py knobs --tests <StrataTests> --output sweep --distance 0.05`, then `report`. In the table, compare the rows of the damping ratio. The field's own description records that at 5 the 2,000-ball pit did not sleep within 30 s.
   :::

3. **Hard.** Make the test `Physics.Settling` "Boxes ride a moving and turning kinematic platform" fail by letting :term[kinematic bodies]{id=kinematic-body} recycle contacts again.

   :::answer[Worked solution]{tests="change-setting"}
   In `Strata/src/Strata/Physics/PhysicsWorld.cpp`, in `MakeBodySetup`, remove the line `setup.Body.enableContactRecycling = false;` of the kinematic branch. Rebuild and run `StrataTests --test-suite=Physics.Settling`. The riders then creep about 696 mm, and the check of at most 21 mm in `StrataTests/src/Physics/PhysicsSettlingTests.cpp` fails. Restore the line.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Physics/PhysicsSimulationSettings.cpp`: the section, its fields, their labels and ranges.
- `Strata/src/Strata/Physics/PhysicsTypes.h`: `PhysicsSettings`, the defaults, `PhysicsStats`, the library profile and counters.
- `Strata/src/Strata/Physics/PhysicsWorld.cpp`: clamping, `GetEffectiveContactHertz`, `SetDetailedStats`, kinematic bodies without recycling.
- `StrataEditor/src/Panels/StreamingPanel.cpp`: the Physics row; `StrataEditor/src/Editor/EditorWorldCommands.cpp`: `physics.stats` and `physics.setDetailedStats`.
- `StrataTests/src/Physics/PhysicsScenes.cpp`, `Tools/PhysicsSweep.py`, `StrataTests/Perf/Budgets.json`: the settle scenes, the sweep and the budgets.

## Further reading

- Erin Catto, the Box2D and box3d documentation and blog: how soft contacts and sleeping work in the library Strata uses (intermediate).
- Glenn Fiedler, "Fix Your Timestep": why the fixed rate matters for physics results (beginner).
