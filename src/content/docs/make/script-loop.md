---
id: make/script-loop
title: "The game loop from a script's side"
description: "Why a script's update callbacks run at different moments, how fixed steps keep physics the same on every computer, and what each callback receives."
kind: concept
size: M
tracks: [G, B]
needs: [make/first-script, basics/programming-3]
time: 40
learn:
  - id: delta-time
    text: explain why a script scales a move by the frame's delta time and what goes wrong without it
  - id: step-count
    text: compute how many fixed steps a frame runs from the accumulator, the step and the cap
  - id: callback-order
    text: name which callback of a script runs when in a frame, and what an inactive entity still receives
  - id: time-controls
    text: compare what the time scale and the project's fixed rate change
  - id: loop-mistakes
    text: fix a script that moves by a constant amount per frame or puts once-a-frame work in a fixed update
since: 0.3.0
status: final
---

In [Your first script](first-script.md) a coin turned by `DegreesPerSecond * deltaTime` degrees each frame. Run that
project on an old laptop that draws 30 frames each second and on a new computer that draws 144. The coin turns at the
same speed on both, and a player cannot tell which machine is faster by watching it.

Now remove the multiplication, so that the coin turns 3 degrees each frame. The laptop turns it 90 degrees each
second, the new computer 432 degrees. The same game now plays almost five times faster on the better machine. This
page explains how Strata keeps one game the same on every computer, and which moments of a frame your script code runs at.

## A constant move per frame ties the game to the computer

A **frame** is one pass of the game's loop: read the input, change the world, draw the picture. A frame takes as long as it takes. A scene with
few objects on a fast :term[graphics card]{id=gpu} needs 0.007 s (144 frames each second), a heavy scene on a weak one needs 0.033 s.
So the number of frames in a second is not under your control.

The first repair is the one you already used: measure how long the last frame took, the **delta time**, and move by
speed times delta time. A coin that falls at 2 metres each second moves 0.0139 m in a frame of 0.0069 s and 0.0667 m in a
frame of 0.0333 s. After one second both have moved 2 m.

That repair is enough for a spinning coin. It is not enough for a ball that bounces, because the ball is
moved by **physics**: a simulation that adds up accelerations, speeds and collisions step by step. The size of each step changes the
answer, as this example shows.

:::example[One falling ball, three step sizes]
A ball is dropped from rest and gravity adds 10 m/s to its speed every second. Each step first adds gravity to the
speed, then moves the ball by speed times the step. The exact fall after 1 second is 5 m.

With one step of 0.5 s, the speed is 5 m/s and the ball moves 2.5 m, then the speed is 10 m/s and it moves 5 m more. The
total is 7.5 m. With ten steps of 0.1 s the total is 5.5 m, and with 60 steps of 1/60 s it is 5.08 m.

The same simulation gives three answers, only because the steps differ. A game whose physics step follows
the frame length plays differently on every computer: bounces, jumps and stacks of crates change. Large steps
can also move a fast ball through a thin wall within one step.
:::

## Frames vary, game time moves in fixed steps

The model that engines use for this has two clocks. The picture is drawn once per frame, at whatever moment the computer
is ready. The simulation moves in **fixed steps**: slices of game time of one constant length, 1/60 s by default in Strata, that each run physics and the
fixed update of every script.

A frame does not run a fixed number of steps. It asks how much game time has passed since the last step and
runs as many whole steps as fit. The time left over waits in the **accumulator**, a number that holds the game time not yet simulated and
adds to the next frame's time.

```mermaid caption="One frame from the side of a script: input callbacks, the frame's update, zero or more fixed steps, the late update and the end of the frame." alt="A flow from user interface callbacks to the frame update, to a box of fixed steps repeated zero to several times with physics, to the late update, to the removal of destroyed entities."
flowchart LR
    A["UI callbacks"] --> B["OnUpdate (once)"]
    B --> C["Fixed steps, 0 to N times:<br/>physics, OnFixedUpdate"]
    C --> D["OnLateUpdate (once)"]
    D --> E["Destroyed entities removed"]
```

The diagram shows the order inside one frame. The two rows of work have different rhythms: `OnUpdate` and `OnLateUpdate` run
once for every frame, the middle box runs as often as the accumulator allows.

Here are the numbers for a step of 1/60 s (0.0167 s), starting with an empty accumulator:

| Frames each second | Frame length | Steps in the first frames |
| --- | --- | --- |
| 30 | 0.0333 s | 2, 2, 2, 2 |
| 60 | 0.0167 s | 1, 1, 1, 1 |
| 144 | 0.0069 s | 0, 0, 1, 0, 1, 0 |

At 144 frames each second the first frame adds 0.0069 s, which is less than a step, so no step runs. The second frame
holds 0.0139 s, still none. The third holds 0.0208 s: one step runs and 0.0042 s stay behind. Over one second every column
adds up to 60 steps, so the game moves the same distance in game time on every machine.

Two limits keep this safe. The first is the **cap** on the steps of one frame, 8 at the default rate.

Suppose a frame takes 0.2 s because the disk was busy. The accumulator then holds 12 steps. Running all of them takes
longer than the frame did, so the next frame is longer still: engines call that a spiral of death. Strata runs at
most 8 steps and drops the steps beyond one, so the game skips ahead and the delay cannot grow without end.

The second limit handles a computer that cannot even run 8 steps in time. If the steps of a frame take longer than the game
time they simulate, Strata stops the frame's steps early and drops the steps still due. That is **time dilation**: the
game runs slower than the clock, in slow motion, instead of freezing. Games that a person watches
on the clock, such as the editor's Play mode and an exported game, enable it.

The last control is the **time scale**, a number that multiplies how fast game time passes. At 1 the game runs at normal speed, at
0.5 in slow motion and at 0 game time stops: a frame then adds 0 to the accumulator, so no fixed step runs.

## How engines run the loop

Each approach below was invented to repair the flaw of the one before.

The oldest loop runs one update for each picture shown, and the display sets the pace. Old console games did
this, since their display ran at one known rate. The flaw: on a computer with another rate the whole game changes speed, as the coin at the top of this page did.

The first repair is a variable delta time for everything: each frame moves each object by speed times the frame's
length. Movement is right at any frame rate. The flaw is the example above: physics now changes with the frame length.

The second repair keeps the variable delta time for drawing and effects, and runs the simulation in fixed steps, fed by
an accumulator. Physics is the same at every frame rate. The flaws are the spiral of death, which the cap and time
dilation repair, and a visible jerk.

The picture shows the world only at step times, so at 144 frames each second the same
pose appears for two or three frames. Drawing between two steps, called interpolation, repairs that.

| Approach | Cost | Quality | Complexity | Used by |
| --- | --- | --- | --- | --- |
| One update per displayed picture | Lowest | Speed depends on the display | Lowest | Games made for one display rate |
| Variable delta for everything | Low | Physics differs by machine | Low | Simple games without physics |
| Fixed steps, variable drawing | One accumulator and a cap | Same physics everywhere | Medium | Games with physics |
| Fixed steps with interpolation | One more stored pose per body | Same physics, smooth picture | Highest | Games with physics, such as Strata |

The article "Fix Your Timestep" in the further reading describes the third and fourth rows in detail.

## Strata runs updates per frame and fixed updates per step

Strata uses the fourth row. A :term[script class]{id=script-class} can override two update callbacks for these two rhythms, and a third for
the end of the frame. A **callback** is a function of your class that the engine calls at a given moment: you write
the body, and Strata decides when it runs.

- `OnUpdate(deltaTime)` runs once for every frame. Put anything that reads input or follows the frame here.
- `OnFixedUpdate(fixedDeltaTime)` runs once for every fixed step, so zero, one or several times in a frame. This
  callback is the **fixed update**: the part of a script that runs in step with physics.
- `OnLateUpdate(deltaTime)` runs once for every frame, after the fixed steps.

The deltas are the numbers `Time` offers: `Time::GetDeltaTime()` is the frame's length multiplied by the time scale, and
`Time::GetFixedDeltaTime()` the length of one fixed step. `Time::GetElapsedTime()` gives the seconds of game time since
the scene started playing, and it stops when the time scale is 0.

:::why[Why does game time count fixed steps and never frames?]
Anything that counts frames changes with the machine: a timer of 600 frames is 10 seconds at 60 frames each second and 4
seconds at 144. A step is always the same slice of game time, so a test, a scripted run or a recorded input
gives the same result on every computer. Strata's tools therefore count steps. The cost is the machinery of this page,
the accumulator and the cap, and a picture that either jerks or, with interpolation, shows the world a step late. The clock
itself is explained in [Time: delta time, the fixed step and time scale](../core/time.md).
:::

Two project settings change the loop. Open **File ▸ Project Settings...**, category **Physics**, page **Timing**.

The field
**Fixed Rate** chooses the steps each second: **Scene**, 30, 60, 120 or 240. **Scene** keeps the scene's own step,
1/60 s by default. Any number overrides it in every scene of the project and of the exported game. The cap
then covers 2/15 s of steps: 4, 8, 16 or 32.

A higher rate makes physics more exact and costs more: 240 runs four times the steps of 60. The scene's own step and cap, in the scene settings of the **Inspector** with nothing selected, are greyed out while a rate is set.
The time scale is a script's own: `Time::SetTimeScale(0.5f)` halves the speed of game time, and a negative
value is rejected and reported. Menus that must animate while the game is paused use the unscaled clocks of
[Timers, events and the clocks](timers-events.md) and [Menus](menus.md).

## What a script receives, in order

A script class lives through a fixed series of moments. Strata first constructs the object, applies the fields set in
the inspector and then calls `OnCreate`, once all scripts that exist at that moment are constructed. After that the
update callbacks run each frame until the entity is destroyed, the script is removed or the scene stops. The class
comment of `Script` in the software development kit (:term[SDK]{id=sdk}) states the rules whole.

```cpp src="StrataScriptCore/Include/StrataScript/Script.h#L30-L47"
// Base class of game scripts. A script class is attached to entities through their Script component; the engine
// creates one instance per entity and calls:
//   OnCreate        once, before the first update (all scripts that exist at that moment are already constructed)
//   OnUpdate        every frame
//   OnFixedUpdate   zero or more times per frame, at the fixed timestep (gameplay physics)
//   OnLateUpdate    every frame, after the fixed updates
//   OnDestroy       when the entity is destroyed, the script is removed or the scene stops playing
//   OnReload        after a hot reload, instead of OnCreate (see below)
//   OnCollisionEnter / OnCollisionExit, OnTriggerEnter / OnTriggerExit
//                   when the entity's physics body starts or stops touching another body (see below)
//   OnAnimationEvent
//                   when the playhead of the entity's animator passes an event of its controller's current state, with
//                   the event's name (after the animators were evaluated, in the order the events happened)
//   OnUIClick / OnUIValueChanged / OnUIFocusChanged / OnUISubmit
//                   when the player clicks a button, changes a slider or toggle, moves the focus, or submits an input
//                   field's text (see below)
// Instances update in entity hierarchy order (parents first), then in the order of the scripts on the entity.
// Inactive entities receive no updates. Overrides may be public, protected or private.
```

1. **Line 34:** zero or more calls per frame, at the fixed step: the reason a key press cannot be read there.
2. **Line 37:** after a :term[hot reload]{id=hot-reload} the old object is deleted and a new one built. `OnReload` runs instead of `OnCreate`.
3. **Lines 46–47:** parents update before their children, then the scripts of one entity in their order.

Initialization belongs in `OnCreate`, never the :term[constructor]{id=constructor}, because the module also builds one object when it loads
only to read the fields' defaults. Only the callbacks a class overrides are called. If a callback throws, Strata disables that instance.

```mermaid caption="The life of a script instance: built, given its field values, created, running, then destroyed; a hot reload replaces the instance and calls the reload callback." alt="A state diagram from constructed to fields applied to created to running, ending in destroyed, with a branch from running through a rebuilt module back to running."
stateDiagram-v2
    [*] --> Constructed
    Constructed --> FieldsApplied
    FieldsApplied --> Running: OnCreate
    Running --> Running: OnUpdate, OnFixedUpdate, OnLateUpdate
    Running --> Reloaded: module rebuilt
    Reloaded --> Running: OnReload
    Running --> Destroyed: OnDestroy
    Destroyed --> [*]
```

The other callbacks answer events instead of time. Contacts are covered in [Physics](physics.md), and the callbacks
of the game's interface in [Menus](menus.md):

| Callback | When it runs |
| --- | --- |
| `OnCollisionEnter`, `OnCollisionExit` | The entity's body starts or stops touching another, after the fixed step that found it |
| `OnTriggerEnter`, `OnTriggerExit` | The same for contacts where either body is a trigger |
| `OnAnimationEvent` | The animator passes an event of its current state |
| `OnUIClick`, `OnUIValueChanged`, `OnUIFocusChanged`, `OnUISubmit` | The player uses a widget, before the frame's `OnUpdate` |

Fifteen callbacks exist in all, and a class overrides only the ones it needs.

Each callback treats an **inactive** entity (one switched off, or whose parent is) in its own way. The entity receives no
`OnUpdate`, `OnFixedUpdate` or `OnLateUpdate`, no new contacts and no animation events. But `OnCreate` and
`OnDestroy` run regardless. A contact that began before the entity was switched off still ends with its Exit
callback, so a script that counts contacts stays right. The comment in the kit says only that inactive entities
receive no updates; the rule is narrower than that, and the code is the reference.

A script can destroy its own entity, or another one, but the entity does not go at once. Strata removes it at the end of
the frame, so the callbacks still running that frame stay safe.

## A coin that bobs

The example is the coin of the Coin Run game, which [the scene chapter](scripting-scene.md) builds. Besides turning, it moves up and
down. Its height comes from a **sine**: a function that swings between -1 and 1 as its input grows. You need nothing
more of it than that.

```pseudocode
OnCreate():
    baseHeight = height of my entity

OnUpdate(deltaTime):
    swing = sin(BobSpeed * Time.ElapsedTime)
    height of my entity = baseHeight + BobHeight * swing
```

With `BobHeight` set to 0.2 and `BobSpeed` to 3, larger than the scene chapter's 0.1 and 2, the coin reaches `0.2 * sin(3 * 0.5)`. That is 0.199 m above its base at 0.5 s
of game time, and 0.028 m at 1 s. One swing takes 2.09 s.

The code reads the total game time, not a sum of small moves, so it needs no delta time and cannot drift. When the time scale is 0 the game time stops and the coin freezes in
place, which is what a pause should do. After a hot reload `baseHeight` is gone, because only fields carry over, so
`OnReload` has to read it again.

## What this design cannot do

Between two steps the simulation has no state. A script reads where a body is simulated, which is where the latest step left it.

Strata draws what
moves in fixed steps between its last two steps, so motion is smooth at any frame rate. The switch is **Interpolation** on the same Timing page,
and it is on by default.

The price is that the picture shows the world one step later than the simulation, 0.0167 s at 60 steps each second. A camera that follows a body reads
the drawn position: [Characters and cameras](characters-cameras.md) shows how, and
[Interpolation](../world/interpolation.md) explains the mathematics.

Strata offers no callback when an entity is switched on or off: there is no `OnEnable` or `OnDisable`, and
`OnCreate` is the only start. [What Strata does not do](../appendix/not-in-strata.md) lists the rest. How the engine's own systems are dispatched is the subject of
[The script system](../scripting/script-system.md).

## Common mistakes

- **A constant amount per frame.** The symptom: the game runs faster on a better computer. The fix: multiply a speed by
  the delta time, or read `Time::GetElapsedTime()`.
- **Once-a-frame work in `OnFixedUpdate`.** The symptom: a key press is missed, or acted on twice, because a frame with
  no step skips the callback and a frame with two runs it twice. The fix: read key presses in `OnUpdate`, and keep in
  `OnFixedUpdate` only the work that belongs to physics. [Physics](physics.md) shows the case in full.
- **Blocking or starting threads.** The symptom: the whole game stalls. The engine calls scripts on one thread, and a
  sleep, a long loop or a wait for a file holds up the frame, the picture and every other script. Threads that call the
  engine from outside its callbacks are not allowed at all. The fix: spread the work over frames.
- **Expecting a start when an entity is switched on.** The symptom: setup runs once and never again. The fix: reset state
  from the code that switches the entity on.

## Summary

- A script scales a move by the frame's delta time, or reads the game time, because the number of frames in a second differs between machines.
- A frame adds its time to the accumulator and runs as many whole fixed steps as fit, at most the cap; the rest waits for the next frame.
- `OnUpdate` and `OnLateUpdate` run once a frame, `OnFixedUpdate` once a step, `OnCreate` first and `OnDestroy` last; an inactive entity still gets those two.
- The time scale multiplies game time, and 0 stops it; the project's Fixed Rate sets the steps each second and the cap.
- Once-a-frame work such as key presses belongs in `OnUpdate`, never in `OnFixedUpdate`, and a script never blocks.

## Check yourself

1. A script turns an object by 2 degrees in `OnUpdate`. The player's computer draws 120 frames each second. How fast
   does the object turn, and what is the fix?

   :::answer{tests="delta-time"}
   The object turns 240 degrees each second, twice as fast as at 60 frames each second. The fix is to turn by
   a speed in degrees each second times `deltaTime`.
   :::

2. The step is 1/60 s. Three frames of 0.04 s follow each other, starting with an empty accumulator. How many steps
   does each frame run?

   :::answer{tests="step-count"}
   The first adds 0.04 s, so 2 steps run (0.0333 s) and 0.0067 s stay. The second holds 0.0467 s: 2 steps again, 0.0133 s stay.
   The third holds 0.0533 s: 3 steps, 0.0033 s stay. The answer is 2, 2 and 3.
   :::

3. A script must react when the player presses the jump key. Where does it read the key, and why?
   A: in `OnFixedUpdate`, because jumping is physics. B: in `OnUpdate`. C: in `OnLateUpdate`, so that all else is done.

   :::answer{tests="callback-order, loop-mistakes"}
   B is right. A frame with no step never calls `OnFixedUpdate`, so the press is missed, and a frame with two steps
   calls it twice. A is wrong for that reason. C runs once a frame, so it would see the press, but it runs after the fixed
   steps of that frame, so the jump would start a step late.
   :::

4. The time scale is 0. Which of `OnUpdate`, `OnFixedUpdate` and `Time::GetElapsedTime()` still change?

   :::answer{tests="time-controls"}
   `OnUpdate` still runs each frame, but its delta time is 0. No fixed step runs, because the accumulator gains nothing,
   and the game time stays where it was.
   :::

5. A script is attached to an entity that a switch disables. Which of `OnCreate`, `OnUpdate` and `OnDestroy` can
   still run?

   :::answer{tests="callback-order"}
   `OnCreate` and `OnDestroy` run regardless of the entity's activity. `OnUpdate` does not run while the entity is
   inactive.
   :::

## Exercises

Only exercise 2 uses a project. Your Coin Run works, or the project at the last checkpoint of [Your first script](first-script.md#change-the-code-while-playing-then-crash-it), whose box offers it as a download. Exercise 3 runs a sketch, which needs a C++ compiler: [Installing Strata and the C++ build tools](../start/install.md) gives you one, and [How a C++ program is built](../basics/build.md) shows how to compile one file. Without them, work the steps out by hand and check them against the printed output.

1. **Basic.** A coin has `BobHeight` 0.2 and `BobSpeed` 3. Its game time is 1.5 s and the sine of 4.5 is
   -0.98. Where is the coin relative to its base, and what changes at 144 frames each second?

   :::answer[Worked solution]{tests="delta-time, loop-mistakes"}
   The height is 0.2 times -0.98, which is -0.196 m: almost the lowest point of the bob. At 144 frames each second
   nothing changes in the formula: it reads game time, so the coin is at the same place at the same time. Only
   how many frames show the coin on the way differs.
   :::

2. **Medium.** In an open project raise the project's fixed rate to 120. How long is one step, and how many steps does a
   frame of 0.04 s run with an empty accumulator?

   :::answer[Worked solution]{tests="step-count, time-controls" solution="tutorials/make/script-loop/exercise-2.tutorial.json"}
   Open **File ▸ Project Settings...**, category **Physics**, page **Timing**, and choose 120 for **Fixed Rate**. One step is
   1/120 s, 0.0083 s. A frame of 0.04 s holds 4.8 steps: 4 run and 0.0067 s stay, well below the cap of 16 for this rate.
   The file sets the section `Scene.Timing` with `project.setSettings`, then checks with `scene.info` that the scene
   runs the project's step: 120 steps each second and a cap of 16.

   The rate stays in the project until you change it. Afterwards choose **Scene** for **Fixed Rate** again, so that the
   later pages run at 60 steps each second. The file does the same with `project.setSettings` and
   `{ "section": "Scene.Timing", "reset": true }`, and `scene.info` then names the scene's own step again.
   :::

3. **Hard.** The sketch below runs the accumulator with the cap for a list of frames. Change it to the project rate of
   120 steps each second with a cap of 16, and the last frame to 0.02 s. Predict the steps of each frame, then run it.

   ```cpp sketch="make-script-loop-accumulator.cpp"
   // How many fixed steps each frame runs, for a list of frame times.
   #include <cstdio>
   #include <vector>

   int main()
   {
   	const float step = 1.0f / 60.0f;
   	const int maxSteps = 8;
   	const std::vector<float> frames = { 0.0167f, 0.0340f, 0.0069f, 0.0069f, 0.0069f, 0.2000f, 0.0167f };
   	float accumulator = 0.0f;
   	for (const float frame : frames)
   	{
   		accumulator += frame;
   		int steps = 0;
   		while (accumulator >= step && steps < maxSteps)
   		{
   			accumulator -= step;
   			steps++;
   		}
   		if (steps == maxSteps && accumulator > step)
   			accumulator = step; // Too far behind: drop the rest of the backlog.
   		std::printf("frame %.4f s: %d steps, %.4f s left\n", frame, steps, accumulator);
   	}
   	return 0;
   }
   ```

   ```text output-of="make-script-loop-accumulator.cpp"
   frame 0.0167 s: 1 steps, 0.0000 s left
   frame 0.0340 s: 2 steps, 0.0007 s left
   frame 0.0069 s: 0 steps, 0.0076 s left
   frame 0.0069 s: 0 steps, 0.0145 s left
   frame 0.0069 s: 1 steps, 0.0047 s left
   frame 0.2000 s: 8 steps, 0.0167 s left
   frame 0.0167 s: 2 steps, 0.0000 s left
   ```

   1. **Line 7:** the length of one fixed step, here 1/60 s.
   2. **Line 15:** a frame runs a step while one whole step fits in the accumulator and the cap allows another.
   3. **Lines 20–21:** past the cap, the steps still due are dropped and one stays, as in the engine.

   :::answer[Worked solution]{tests="step-count" solution="sketches/make-script-loop-rate.cpp"}
   Only three values change: `step` is `1.0f / 120.0f`, `maxSteps` is 16 and the last frame is 0.0200. Predict first: the
   first frame of 0.0167 s is 2 steps, the second 4, and the frame of 0.2 s hits the cap of 16 steps. Strata drops the rest of the steps due and keeps one.

   ```cpp sketch="make-script-loop-rate.cpp"
   // The same accumulator at the project rate of 120 steps each second, with a cap of 16.
   #include <cstdio>
   #include <vector>

   int main()
   {
   	const float step = 1.0f / 120.0f;
   	const int maxSteps = 16;
   	const std::vector<float> frames = { 0.0167f, 0.0340f, 0.0069f, 0.0069f, 0.0069f, 0.2000f, 0.0200f };
   	float accumulator = 0.0f;
   	for (const float frame : frames)
   	{
   		accumulator += frame;
   		int steps = 0;
   		while (accumulator >= step && steps < maxSteps)
   		{
   			accumulator -= step;
   			steps++;
   		}
   		if (steps == maxSteps && accumulator > step)
   			accumulator = step; // Too far behind: drop the rest of the backlog.
   		std::printf("frame %.4f s: %d steps, %.4f s left\n", frame, steps, accumulator);
   	}
   	return 0;
   }
   ```

   ```text output-of="make-script-loop-rate.cpp"
   frame 0.0167 s: 2 steps, 0.0000 s left
   frame 0.0340 s: 4 steps, 0.0007 s left
   frame 0.0069 s: 0 steps, 0.0076 s left
   frame 0.0069 s: 1 steps, 0.0062 s left
   frame 0.0069 s: 1 steps, 0.0047 s left
   frame 0.2000 s: 16 steps, 0.0083 s left
   frame 0.0200 s: 3 steps, 0.0033 s left
   ```

   1. **Line 7:** the length of one fixed step, here 1/120 s.
   2. **Line 15:** a frame runs a step while one whole step fits in the accumulator and the cap allows another.
   3. **Lines 20–21:** past the cap, the steps still due are dropped and one stays, as in the engine.

   The output confirms it. The smaller step runs about twice the steps of the first sketch in the same frames, and the cap
   covers the same 2/15 s.
   :::

## Where it lives in Strata

- **Project Settings ▸ Physics ▸ Timing**: the fields **Fixed Rate** and **Interpolation** of the section `Scene.Timing`.
- **Inspector** with nothing selected: the scene's own step and its cap, **Max Steps per Frame**.
- The commands `project.settings` and `project.setSettings` read and set the section; `scene.setSettings` the scene's own values.
- `StrataScriptCore/Include/StrataScript/Script.h`: the :term[base class]{id=base-class} and its callbacks.
- `StrataScriptCore/Include/StrataScript/Time.h`: the `Time` functions of a script.
- `Strata/src/Strata/Scene/ProjectSceneTiming.h`: the project's fixed rate, its cap and the Interpolation switch.

## Further reading

- Glenn Fiedler, "Fix Your Timestep" (gafferongames.com): the accumulator, fixed steps and interpolation (intermediate).
- Robert Nystrom, "Game Loop" in Game Programming Patterns (gameprogrammingpatterns.com): the approaches of this page, with code (beginner).
