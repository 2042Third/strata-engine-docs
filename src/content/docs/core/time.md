---
id: core/time
title: "Time: delta time, the fixed step and time scale"
description: "Why a game measures the time of each frame, how fixed steps keep physics stable and repeatable, and what Strata does when frames run long."
kind: concept
size: L
tracks: [E]
needs: [core/frame-loop, basics/math-change]
time: 70
learn:
  - id: delta-time
    text: explain why a game scales movement by the frame's delta time and why physics needs a fixed step as well
  - id: fixed-steps
    text: predict how many fixed steps a frame runs and what the accumulator keeps
  - id: toy
    text: write the accumulator loop in a toy program and compare it with the engine's
  - id: dilation
    text: explain why Strata drops the backlog of steps and when time dilates
  - id: time-scale
    text: choose scaled or unscaled time for a piece of game logic
since: 0.3.0
status: final
---

Move a ball across the screen by 0.1 m in every frame. On a computer that draws 60 frames a second, the ball moves 6 m each second. On a computer that draws 120 frames a second, the same code moves it 12 m each second. Nobody changed the game, yet the ball runs twice as fast on the faster machine.

The opposite problem is harder to see. A stack of crates is simulated by physics, and each frame advances the simulation by the length of that frame. A frame of 8 ms and a frame of 33 ms then feed the simulation different amounts of time, and the crates tremble or burst apart. A game has to decide what one tick of its clock means. This page builds that decision in steps: the clocks, the fixed step, and what Strata does when frames run long.

This page needs no download. Its sketches are whole programs for the compiler of [How a C++ program is built](../basics/build.md#open-a-terminal-that-finds-a-compiler). Its two editor exercises use the installed Strata: a project of your own, and a copy of the Physics Playground, which **Open Sample...** on the welcome window makes.

## Scaling by delta time fixes speed but not stability

The first fix is to move the ball by a speed instead of a distance per frame. A frame knows how long it lasted, and its **delta time** is the number of seconds since the frame before it. At 60 frames a second the delta time is 1/60 s, and a ball at 6 m/s moves 6 m/s times 1/60 s, which is 0.1 m. At 120 frames a second the delta time is 1/120 s and the ball moves 0.05 m. Both machines move the ball 6 m in each second.

The rule is the one from [rates and accumulation](../basics/math-change.md): a distance is a rate times a time, and the frame supplies the time. A script receives the frame's delta time as the argument of `OnUpdate`. The :term[pseudocode]{id=pseudocode} below adds one slice of distance per frame, and the slice matches the slice of time the frame lasted.

```pseudocode
OnUpdate(deltaTime):
    position.x = position.x + speed * deltaTime
```

The slices differ in size from frame to frame, but together they add up to the right distance. That fix is correct for things that only move. It fails in three places, and each failure leads to a part of the design below.

### A long frame makes one huge step

Hold the game at a breakpoint for a minute, and the next frame has a delta time of 60 s. The ball moves 6 m/s times 60 s, which is 360 m, in one frame. A character that falls 360 m in one step passes through the floor, because no step ever looked at the space in between. A loading hitch of two seconds does the same at a smaller size.

[Frames and clocks in the loop](frame-loop.md) showed the first defence: the application clamps each frame's time to 0.25 s, so the ball moves 1.5 m. The clamp keeps one frame from being absurd. It does not make a step of 0.25 s small enough for physics, as the next part shows.

### Physics needs small and equal steps

The sketch below steps two physical systems with the frame's delta time, once for each of several :term[frame rates]{id=frame-rate}. The first is a jump that leaves the ground at 5 m/s. The second is a stiff spring that starts one metre from rest. Each step changes the speed first and then moves the position with the new speed, the Euler step of the math chapter. Look at how the answers change with the step.

```cpp sketch="core-time-variable-step.cpp"
// What a variable step changes: how high the same jump goes, and whether a stiff spring stays calm.
// Both use semi-implicit Euler: the speed changes first, then the position moves with the new speed.
#include <algorithm>
#include <cmath>
#include <cstdio>

namespace
{
	// The highest point of a jump that leaves the ground at 5 m/s, stepped with `deltaTime`.
	float JumpPeak(float deltaTime)
	{
		float height = 0.0f;
		float speed = 5.0f; // m/s
		float peak = 0.0f;
		while (speed > 0.0f)
		{
			speed -= 9.81f * deltaTime;
			height += speed * deltaTime;
			peak = std::max(peak, height);
		}
		return peak;
	}

	// The largest distance from rest that a spring (stiffness 3600 per second squared) reaches in one second.
	float SpringReach(float deltaTime)
	{
		float position = 1.0f; // m
		float speed = 0.0f;    // m/s
		float reach = 1.0f;
		const int steps = static_cast<int>(std::lround(1.0f / deltaTime));
		for (int i = 0; i < steps; i++)
		{
			speed -= 3600.0f * position * deltaTime;
			position += speed * deltaTime;
			reach = std::max(reach, std::abs(position));
		}
		return reach;
	}
}

int main()
{
	const float steps[] = { 1.0f / 240.0f, 1.0f / 60.0f, 1.0f / 30.0f, 1.0f / 15.0f };
	for (const float deltaTime : steps)
		std::printf("step %5.1f ms: jump peak %.3f m\n", deltaTime * 1000.0f, JumpPeak(deltaTime));
	for (const float deltaTime : { 1.0f / 60.0f, 1.0f / 40.0f, 1.0f / 20.0f })
		std::printf("step %5.1f ms: spring reach %.1f m\n", deltaTime * 1000.0f, SpringReach(deltaTime));
}
```

```text output-of="core-time-variable-step.cpp"
step   4.2 ms: jump peak 1.264 m
step  16.7 ms: jump peak 1.233 m
step  33.3 ms: jump peak 1.192 m
step  66.7 ms: jump peak 1.113 m
step  16.7 ms: spring reach 1.0 m
step  25.0 ms: spring reach 1.5 m
step  50.0 ms: spring reach 61305834902126592.0 m
```

1. **Lines 17–18:** the Euler step: the speed changes first, then the height moves with the new speed.
2. **Line 30:** the spring runs for one second of game time, however many steps that takes.
3. **Lines 33–34:** the same Euler step, with a pull that grows with the distance from rest.

The exact peak of the jump is 1.274 m: the speed squared, 25, divided by twice the gravity, 19.62. Only the smallest step comes close. The jump rises 1.233 m at 60 frames a second, 1.192 m at 30 and 1.113 m at 15. It is the same jump with a different height on every machine.

The spring shows the worse side. For this spring, a step longer than about 33 ms (2/60 s) makes every step add energy. At 25 ms the spring already swings 50 % too far, and at 50 ms it reaches $6 \times 10^{16}$ m: the simulation has exploded. Physics needs steps that are small, and the same size every time.

### No two runs repeat

Frame lengths come from the machine: the display, the other programs and the system. Two runs of one game never share them. With a variable step, the jump above peaks at one height in one run and at another in the next. A test cannot expect a number, a replay drifts away from the recording, and a bug seen once cannot be repeated.

So the frame's time has to become steps of one size. Before that, the clock itself needs a closer look.

## Clocks must never jump and must stay precise

A game measures a frame by reading a clock twice. The **wall clock** tells the time of day. A person can set it back an hour, the network can correct it, and summer time moves it, so a frame measured with it could last minus 3,600 s. A steady clock only counts forward from a fixed start, and nobody can set it. Strata reads the :term[standard library's]{id=standard-library} `std::chrono::steady_clock` through `Time::GetTime`.

The second choice is the number type. A `float` keeps about seven digits. After three hours (10,800 s), two neighbouring `float` values lie about 1 ms apart, so a clock kept in a `float` advances in jumps that a player can see at 240 frames a second. A `double` keeps about 16 digits and stays precise for years. Strata keeps absolute time in a `double` and short spans, such as `Timestep`, in a `float`.

The third choice is the clamp: `ApplicationSpecification::MaxTimestep` is 0.25 s. These clocks measure the program's time. **Game time** is another thing: it counts the time of the game itself. It stops while the game is paused and runs slowly at a time scale of 0.5, and the simulation can fall behind it when steps are dropped. The program's clock never does any of this, and the rest of the page is about the difference.

## A fixed step turns uneven frames into equal steps

The idea separates two clocks. The frames arrive at the pace of the machine, uneven. The simulation advances at a pace of its own, and always by the same amount: one **fixed step**, a slice of game time of constant length, such as 1/60 s.

Between the two stands a number that holds the time the frames have delivered and no step has used yet. This number is the **accumulator**. The diagram shows the loop that connects them.

```mermaid caption="Each frame adds its time to the accumulator, and the loop pays out whole steps while it can." alt="A flow chart. A frame adds its delta time to the accumulator. A test asks whether at least one step is stored. If yes, one fixed step runs, its length is subtracted and the test repeats. If no, the frame is drawn."
flowchart LR
    A["Frame adds its delta time"] --> B["Accumulator"]
    B --> C{"At least one step stored?"}
    C -- yes --> D["Run one fixed step, subtract its length"]
    D --> C
    C -- no --> E["Draw the frame"]
```

A frame that delivers 35 ms to steps of 10 ms runs three steps and keeps 5 ms for the next frame. The frame can also run no step at all, when it delivers less than the accumulator needs. The pseudocode is short.

```pseudocode
accumulator = accumulator + frameTime
while accumulator >= step:
    simulate(step)
    accumulator = accumulator - step
draw()
```

Every call of `simulate` receives the same `step`. The jump of the sketch above therefore peaks at 1.233 m on every machine, when the step is 1/60 s, and the spring never meets a step beyond its limit. The engine runs its simulation in this way, and [the systems chapter](../world/systems.md) walks through the code.

:::example[Four uneven frames with steps of 10 ms]
Take a step of 10 ms and four frames that last 35, 6, 4 and 16 ms. The table follows the accumulator by hand. Each row adds the frame's time, pays out whole steps and keeps the rest.

| Frame | Lasts | Accumulator before the steps | Steps run | Accumulator after |
| --- | --- | --- | --- | --- |
| 1 | 35 ms | 35 ms | 3 | 5 ms |
| 2 | 6 ms | 11 ms | 1 | 1 ms |
| 3 | 4 ms | 5 ms | 0 | 5 ms |
| 4 | 16 ms | 21 ms | 2 | 1 ms |

Frame 3 runs no step, so the screen shows the game as it was in frame 2. Over the four frames, 61 ms arrive and 6 steps of 10 ms run, which leaves 1 ms. No time is created or lost.

The engine's own test checks the first two rows. A scene with a step of 0.01 s receives a frame of 0.035 s and runs 3 steps, then a frame of 0.006 s, which makes the accumulator 0.011 s, and runs one more.

```cpp src="StrataTests/src/Scene/SceneTests.cpp#L496-L503"
scene.OnUpdateRuntime(0.035f);
CHECK(CountingSystem::Updates == 1);
CHECK(CountingSystem::LateUpdates == 1);
CHECK(CountingSystem::FixedUpdates == 3);
CHECK(CountingSystem::LastFixedTimestep == doctest::Approx(0.01f));

scene.OnUpdateRuntime(0.006f); // Accumulated 0.005 + 0.006 -> one more step
CHECK(CountingSystem::FixedUpdates == 4);
```

The test has no clock: it hands `OnUpdateRuntime` the frame's time directly, so the same numbers come out on every machine.
:::

## A cap stops a long frame from owing too much

A step costs real time to compute. Suppose one step simulates 20 ms of game time but needs 30 ms of work, so the loop falls behind. The next frame lasts longer, so it owes more steps, so it takes longer again. This runaway is the **spiral of death**. With those numbers the frames last 20, 30, 30, 60, 90, 120, 180 and 240 ms, because each frame lasts as long as the work of the frame before it.

The cure is a limit: a frame runs at most a fixed number of steps, the cap. Strata's default cap is 8 steps.

What remains due when the cap stops the loop is the **backlog**. Strata drops the whole steps of the backlog and sets the accumulator to exactly one step, so the next frame moves the game again at once. The figure shows the table above with a fifth frame of 130 ms.

::figure{id=accumulator-timeline}

Frame 5 delivers 130 ms on top of the 1 ms in the accumulator, so 13 steps are due. Eight run, four are dropped, and one stays. The dropped time is gone: the simulation now trails the clock by 41 ms, the four steps and the 1 ms that was left, and never catches up. That is the price of staying responsive. The game slows instead of freezing, and the frame that follows is a normal frame.

The cap and the clamp work together. A hitch of 60 s first becomes 0.25 s at the application, and the cap then bounds what remains. At 60 steps a second, 0.25 s is 15 steps due and 8 run.

## Time dilation slows the game instead of the frame rate

The cap bounds the spiral but lets it grow to the cap first. With the 30 ms steps above, frames reach 240 ms, which is 4 frames a second. **Time dilation** goes further: when the steps of a frame take longer in wall time than the game time they simulate, the loop stops running catch-up steps and drops the rest. The first step that is due always runs, and a fraction of a step stays in the accumulator. The table runs both rules on the same costs.

| Frame | Cap only: frame length | Cap only: steps | Time dilation: frame length | Time dilation: steps |
| --- | --- | --- | --- | --- |
| 1 | 20 ms | 1 | 20 ms | 1 |
| 2 | 30 ms | 1 | 30 ms | 1 |
| 3 | 30 ms | 2 | 30 ms | 1 |
| 4 | 60 ms | 3 | 30 ms | 1 |
| 5 | 90 ms | 4 | 30 ms | 1 |
| 6 | 120 ms | 6 | 30 ms | 1 |
| 7 | 180 ms | 8 | 30 ms | 1 |
| 8 | 240 ms | 8 | 30 ms | 1 |

Both columns simulate about two thirds of real time in the end: 20 ms of game time for each 30 ms of work. The difference is the frame. With the cap alone the player sees 4 frames a second, and with time dilation 33. The sketch in the exercises produces this table.

The engine's test uses a system that sleeps 25 ms in each step, with a step of 1/64 s. With time dilation on, a frame that owes four steps and a quarter runs one step, and three are counted as dropped.

```cpp src="StrataTests/src/Scene/SceneTests.cpp#L545-L552"
// With it, the first step took longer than it simulated: the others due are dropped and the fraction of a step
// stays, so the simulation runs slower than the clock instead of owing ever more steps.
SlowSystem::FixedUpdates = 0;
scene.SetTimeDilation(true);
scene.OnRuntimeStart();
scene.OnUpdateRuntime(4.0f / 64.0f + 1.0f / 256.0f);
CHECK(SlowSystem::FixedUpdates == 1);
CHECK(scene.GetDroppedFixedStepCount() == 3);
```

`Scene::GetDroppedFixedStepCount` reports the total of dropped steps, whether time dilation or the cap dropped them. Time dilation is off in a `Scene` until a program enables it with `Scene::SetTimeDilation`. The editor enables it for interactive sessions, and the :term[runtime]{id=runtime} enables it for games that run on the wall clock. Scripted runs (`--frames`, command scripts) and tests keep it off, because a run that must repeat cannot depend on how fast a machine computes.

## Time scale changes how fast game time passes

The **time scale** is a number that the scene multiplies into each frame's delta time: 1 is real time, 0.5 is slow motion and 0 stops game time. The engine never lets it fall below 0. A game uses it for slow motion, fast forward and freezing the action.

The scale acts before the accumulator, and this matters. At a scale of 0.5 each frame delivers half the time, so steps are paid out half as often and each step still simulates one full fixed step. Physics in slow motion is as accurate as at full speed, and it costs less. At a scale of 4 the steps come four times as often. At 60 frames a second that is 4 steps a frame, and a scale of 10 would owe 10 steps, so the cap of 8 limits the game to about 8 times real speed.

At a scale of 0, `OnUpdate` still runs, with a delta time of 0, but no fixed step runs. A fade or a menu that animates with that delta time would freeze with the game. For these, the scene keeps **unscaled time**, the time that the time scale does not change. Scripts read it as `Time::GetUnscaledDeltaTime` and `Time::GetRealTime`. The rule is short: gameplay uses scaled time, and the interface of a pause menu uses unscaled time.

## Drawing between steps hides the step's rhythm

At 240 frames a second and 60 steps a second, three of every four frames run no step, and the screen would show the same picture four times and then a jump. **Interpolation** fixes this by drawing the state between the last two steps, at the fraction of a step that the accumulator holds. The price is latency, and you can count it in two ways. The picture shows the moment one step before the game's clock, which runs ahead of the newest step by what the accumulator holds. A picture of the newest step would show it at once; the blended picture shows it 0 to one step later, half a step on average, about 8 ms at 60 steps a second.

The other choice is to extrapolate, which guesses where things go from their speed. It has no latency, but the guess is wrong whenever something turns or stops.

Strata draws by interpolation what the fixed steps move, a constant one step behind the game's clock. [Interpolation](../world/interpolation.md) names the entities it covers and how a teleport avoids a glide. The project's `Scene.Timing` section has an `Interpolation` switch, on by default. Scripted runs and tests never use interpolation, so that they draw what they simulate.

## Engines solve it in five ways

Each approach below answers a flaw of the one before. The oldest ties the game to the display: one frame runs one step, and the step is the frame. A slower machine runs the game slowly, and a faster one wastes its speed. A variable step fixes that by using the frame's delta time, and has the three failures above.

A semi-fixed step cuts the frame's delta time into equal pieces up to a maximum, and a last, shorter piece. The pieces are small, but the last one differs from run to run, so runs still do not repeat. The accumulator removes that: every step is the same size, and the leftover waits for the next frame. Its own flaw is the spiral, so a cap bounds it. The cap drops time, and time dilation shapes what the player sees when it does.

| Approach | Cost | Quality | Complexity | Used by |
| --- | --- | --- | --- | --- |
| One step per frame, locked to the display | Lowest | Speed follows the machine | Lowest | Console games locked to a fixed display rate |
| Variable step | Low | Unstable, and runs differ | Low | Small games and prototypes |
| Semi-fixed step | Medium | Stable, and runs differ | Medium | A compromise Glenn Fiedler describes |
| Accumulator with a cap | Medium | Stable, and runs repeat | Medium | Unity's fixed update, Godot's physics process, Strata |
| Time dilation on top | Medium, and a clock read | Smooth frames when work is late | Higher | Strata |

The sources for each row are in the further reading. Unity calls its cap the maximum allowed :term[timestep]{id=time-step}, and Godot calls its cap the maximum physics steps per frame.

## Strata clamps, scales, accumulates and caps

Strata combines these parts in a fixed order. The application reads the steady clock and clamps the wall time since the last frame to 0.25 s. The running scene then handles the frame in this order.

1. The scene multiplies the delta time by the time scale. While the scene is paused and a step was requested, the frame's delta time is exactly one fixed step.
2. Every system's `OnUpdate` runs once with that delta time.
3. The accumulator receives the delta time, and each due step runs `OnFixedUpdate` with the fixed step, up to the cap.
4. If the cap or time dilation stopped the loop, the backlog is dropped.
5. Every system's `OnLateUpdate` runs once with the delta time, after the steps. Cameras that follow a moving body read its final position here.
6. The scene's game time grows by the delta time, and the frame counts.

A script sees the three :term[callbacks]{id=callback} of the same names. `OnUpdate` runs once a frame, `OnFixedUpdate` runs zero or more times a frame, and `OnLateUpdate` runs once a frame after the steps. [Time from a script's side](../make/script-loop.md) covers what they receive.

### The step and the cap come from the project

A scene has its own `SceneSettings`: a step of 1/60 s and a cap of 8 steps. The project can override both with its `Scene.Timing` section, whose `FixedRate` is `Scene` (keep the scene's own), 30, 60, 120 or 240 steps per second. At a project rate, the cap is the number of steps that fit in 2/15 s, rounded up. Other code asks the scene for the step with `Scene::GetFixedTimestep` and for the cap with `Scene::GetMaxFixedSteps`, and leaves `SceneSettings` alone, because the project's rate would be missed.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L244-L251" symbol="Scene::GetMaxFixedSteps"
uint32_t Scene::GetMaxFixedSteps() const
{
	// At the project's rate the scene's own cap, chosen for its own step, does not apply: 8 steps of a 240th would drop
	// time on every frame longer than 33 ms.
	if (m_ProjectFixedRate > 0)
		return ProjectSceneTiming::GetMaxSteps(m_ProjectFixedRate);
	return std::max(1u, m_Settings.MaxFixedStepsPerFrame);
}
```

The comment in the code gives the reason: a cap of 8 steps at 240 steps a second covers only 33 ms, so every longer frame would lose time. The cap in steps follows the rate, so that the longest frame without loss is 2/15 s at any rate.

| `FixedRate` | Step | Cap in steps | Longest frame without loss |
| --- | --- | --- | --- |
| 30 | 33.3 ms | 4 | 133 ms |
| 60 | 16.7 ms | 8 | 133 ms |
| 120 | 8.3 ms | 16 | 133 ms |
| 240 | 4.2 ms | 32 | 133 ms |

The section's validation, and how a scene takes the project's values, belong to [Project settings](../world/projects-settings.md).

### Pausing and stepping

A paused scene runs no fixed steps. `Scene::Step` asks for single steps: each following update then advances exactly one fixed step, whatever the time scale. `Scene::GetFixedStepCount` counts the fixed steps since the scene started, and tools that need exact results count in it. [Stepping a paused game](../editor/stepping.md) covers the editor's side.

:::why[Why does game time count fixed steps and never frames?]
A frame count depends on the machine: two computers run different numbers of frames in one second, and a slow one drops frames under load. A step count depends only on the game, so a tool that waits for 120 steps waits for the same game time everywhere. Strata therefore counts game time in fixed steps (`Scene::GetFixedStepCount`) in its tools, simulated input and tests, and never in frames. The cost is that a tool has no direct way to wait for what is drawn: the picture of a step may lag by a frame. The editor keeps one exception, because a held key also counts frames in which the game is frozen, and [Stepping a paused game](../editor/stepping.md) explains it.
:::

## What Strata's choice cannot do

One step serves the scripts' `OnFixedUpdate`, physics and character controllers together. No system runs at a rate of its own: a game cannot simulate physics at 240 steps a second and its fixed scripts at 30. A high rate costs real time, because 240 steps a second run four times the work of 60. A rate of 30 makes contacts soft, and stacks of crates sag and settle slowly.

Interpolation shows the newest step half a step late on average, about 8 ms at 60 steps a second, while the picture stays one step behind the clock. Strata does not extrapolate. Time dilation makes the game slower than real time under load, and the dropped steps are lost for good, so a game that needs every step of a recording runs with time dilation off. More about the engine's limits is in [what Strata does not do](../appendix/not-in-strata.md).

## Common mistakes

- **Physics forces in `OnUpdate`.** Forces and torques act during the next fixed step only. A force applied each frame at 240 frames a second acts four times for every step of 60, or not at all in a frame without a step. Apply them in `OnFixedUpdate`.
- **Multiplying by the frame's delta in `OnFixedUpdate`.** The callback already receives the fixed step. Multiplying by `Time::GetDeltaTime` moves the object a quarter as far at 240 frames a second and twice as far at 30, because steps do not change with the frame rate.
- **Counting frames in tests and tools.** A test that waits for 60 frames waits for a different game time on each machine. Wait for fixed steps.
- **Using the time of day for game time.** The system clock jumps. Use the steady clock, through `Time::GetTime`.
- **Keeping absolute time in a `float`.** After hours of play the clock moves in steps of 1 ms or more. Keep it in a `double`.
- **Moving a body without breaking interpolation.** A teleport inside `OnFixedUpdate` is drawn as a glide from the old place to the new one. Call `ResetInterpolation` on the transform when the move is a jump.

## Summary

- A frame's delta time turns a speed into a distance per frame, so that motion does not depend on the frame rate. Physics also needs steps that are small and equal, or its results change with the machine.
- A fixed step is a constant slice of game time. The accumulator holds the time that frames delivered and that no step has used, and a frame runs as many steps as the accumulator holds, keeping the rest.
- Written as a loop in a toy program, the accumulator gives the same steps and leftovers as the engine's, which the test of `Scene` confirms.
- The cap stops the spiral of death by dropping the backlog, and time dilation stops catch-up steps once they take longer than they simulate. Both make the game slow instead of the frame.
- The time scale multiplies the delta time before the accumulator. Gameplay uses scaled time, and a pause menu uses unscaled time.

## Check yourself

1. A script adds `speed * deltaTime` to a position in `OnUpdate`, with a speed of 6 m/s. Which statement is true?

   - A. At 120 frames a second the object moves 12 m each second.
   - B. At 120 frames a second it moves 6 m each second, in steps of 0.05 m.
   - C. At 30 frames a second it moves 6 m each second, so physics can use the same code.
   - D. The result equals the result of a fixed step.

   :::answer{tests="delta-time"}
   B is right. The delta time shrinks as the frame rate rises, so the speed stays the same. A describes the version without delta time. C is wrong because motion at the right speed is not stable physics: the jump of the sketch peaks at different heights. D is wrong for the same reason: the steps differ in size.
   :::

2. The step is 10 ms and the cap is 8. Three frames last 23 ms each. How many steps does each frame run, and what is in the accumulator after the third frame?

   :::answer{tests="fixed-steps,toy"}
   Frame 1: 23 ms gives 2 steps and leaves 3 ms. Frame 2: 26 ms gives 2 steps and leaves 6 ms. Frame 3: 29 ms gives 2 steps and leaves 9 ms. In all, 69 ms arrived, 60 ms were simulated, and 9 ms wait for the next frame.
   :::

3. Which statement about the cap and time dilation is right?

   - A. The cap saves the dropped steps and runs them in later frames.
   - B. The cap drops the backlog, so that the game slows instead of falling into a spiral.
   - C. Time dilation is on in the engine's tests.
   - D. Time dilation lets more steps run in a frame.

   :::answer{tests="dilation"}
   B is right. A is wrong because Strata drops the whole steps and keeps only one step in the accumulator. C is wrong because time dilation is off in a scene by default, in scripted runs and in tests, which must repeat. D is wrong because time dilation stops catch-up steps; it never adds any.
   :::

4. A pause menu fades in over 0.5 s while the game's time scale is 0. Which delta time should the fade use, and how many fixed steps run during the fade?

   :::answer{tests="time-scale"}
   The fade uses the unscaled delta time (`Time::GetUnscaledDeltaTime`), because the scaled delta time is 0 and the fade would never move. No fixed step runs, because the accumulator receives nothing. One step can run if a dropped backlog left a step in the accumulator.
   :::

5. A script's `OnFixedUpdate` adds `velocity * Time::GetDeltaTime()` to a position. The game runs at 240 frames a second with 60 steps a second. What goes wrong?

   :::answer{tests="fixed-steps"}
   Each step moves the object by the speed times 1/240 s instead of times 1/60 s, so the object moves four times too slowly. At 30 frames a second it would move twice too fast. The callback's own argument, the fixed delta time, is the right factor, because it is the same in every step.
   :::

## Exercises

1. **Basic.** Write a loop that runs the accumulator with a step of 10 ms and a cap of 8 for frames of 35, 6, 4, 16 and 10,000 ms. Print, for each frame, the steps run, the steps dropped and the time left. Predict the last line before you run the program.

   :::answer[Worked solution]{tests="toy,fixed-steps" solution="sketches/core-time-accumulator.cpp"}
   The program adds the frame to the accumulator, runs steps while it can, and drops the backlog when the cap stops it. The last frame brings 10,001 ms with the 1 ms left over, so 8 steps run and 9,921 ms remain. The code keeps one step and drops the whole steps before it, which is 991.

   ```cpp sketch="core-time-accumulator.cpp"
   // The fixed-step accumulator with the engine's cap: uneven frames in, whole steps out, a backlog dropped.
   // Times are whole milliseconds, so every number is exact. The step is 10 ms and a frame runs at most 8 steps.
   #include <algorithm>
   #include <cstdio>

   int main()
   {
   	constexpr int c_Step = 10;     // ms of game time in one fixed step
   	constexpr int c_MaxSteps = 8;  // the most steps one frame runs
   	const int frames[] = { 35, 6, 4, 16, 10000 }; // ms: how long each frame took

   	int accumulator = 0; // ms of game time that no step has simulated yet
   	for (const int frame : frames)
   	{
   		accumulator += frame;
   		int steps = 0;
   		while (accumulator >= c_Step && steps < c_MaxSteps)
   		{
   			accumulator -= c_Step; // here the engine runs OnFixedUpdate
   			steps++;
   		}
   		int dropped = 0;
   		if (steps == c_MaxSteps && accumulator > c_Step)
   		{
   			dropped = (accumulator - c_Step) / c_Step;
   			accumulator = c_Step;
   		}
   		std::printf("frame %5d ms: %d steps, %3d dropped, %2d ms left\n", frame, steps, dropped, accumulator);
   	}
   }
   ```

   ```text output-of="core-time-accumulator.cpp"
   frame    35 ms: 3 steps,   0 dropped,  5 ms left
   frame     6 ms: 1 steps,   0 dropped,  1 ms left
   frame     4 ms: 0 steps,   0 dropped,  5 ms left
   frame    16 ms: 2 steps,   0 dropped,  1 ms left
   frame 10000 ms: 8 steps, 991 dropped, 10 ms left
   ```

   1. **Lines 17–21:** the loop runs at most `c_MaxSteps` steps and subtracts the step each time.
   2. **Lines 22–27:** when the cap stopped the loop with more than one step left, the backlog is counted as dropped and the accumulator becomes one step.

   The first four lines match the table of the page and the test of `Scene`. The engine does the same with `float` seconds instead of whole milliseconds.
   :::

2. **Medium.** In a project, one object moves 0.1 m in each `OnUpdate`, and a second moves 0.1 m in each `OnFixedUpdate`, with a scene step of 1/60 s. Predict how far each object travels in 5 s at 60 frames a second and at 240. Check it in the editor with a window: in **File ▸ Preferences...**, set **Active frame rate** in the **Frame Rate** section to 60 and then to 240, and play each time. The setting is your own and an editor without a window ignores it, so the check has no command; set it back to **Unlimited**, its default, afterwards.

   :::answer[Worked solution]{tests="delta-time,fixed-steps"}
   The first object moves once a frame: 300 frames at 60 and 1,200 at 240, so it travels 30 m and 120 m. The second moves once a step: 60 steps a second give 300 steps in 5 s at both rates, so it travels 30 m both times. The first object runs four times as fast when the frame rate rises four times, and the second does not. A display that refreshes more slowly than 240 times a second holds the real frame rate down, so count the frames you get. The editor draws with interpolation, so the second object looks smooth at 240, and with it off it would move in jumps every fourth frame.
   :::

3. **Medium.** Open a copy of the Physics Playground sample. Set the project's **Fixed Rate** to 30 and press Play, then set it to 240 and press Play again. Fly to the crate tower with the keys 1 to 6. Predict what differs, using what the setting says about contacts and about cost.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open **File ▸ Project Settings...**, choose the **Physics** category and its **Timing** page, and pick the rate in the **Fixed Rate** list.
   :::
   :::tab[With a command]
   That settings page is the section `Scene.Timing`. **Fixed Rate** is a list of choices, so its value is the text `"30"`, not the number 30. Run these lines in PowerShell in the Strata folder, with the copy open in the editor; [The editor's commands](../editor/commands.md) teaches them. On Linux and macOS, pass the text as the argument in place of `-`.

   ```powershell
   '{"section": "Scene.Timing", "value": {"FixedRate": "30"}}' | .\StrataCLI call project.setSettings -
   .\StrataCLI call scene.info
   ```

   The first answer shows `FixedRate` `"30"`, and `isDefault` false. In the second, `settings.fixedRate` reads `source` `project`, `stepsPerSecond` 30 and `maxFixedSteps` 4; at 240 it reads 32, the caps of the table above. `play.start` and `play.stop` press Play and Stop. With `"reset": true` in place of `value`, the first line restores the scene's own step. The number 30 fails with `'FixedRate' must be one of 'Scene', '30', '60', '120', '240'`.
   :::
   ::::

   :::answer[Worked solution]{tests="fixed-steps"}
   At 30 steps a second contacts are soft: the setting's own description says that stacks sag and settle more slowly, because the physics library's contact stiffness depends on the step rate. At 240 the physics does four times the steps of 60, so each frame costs more, and the cap is 32 steps, so a long frame loses no time. With the interpolation switch on, the motion looks smooth at every rate. The latency that interpolation adds, half a step on average, is about 17 ms at 30 steps a second and 2 ms at 240.
   :::

4. **Hard.** Write a toy that runs the spiral of death, as in the page. Use a step of 20 ms that costs 30 ms of work, a cap of 8, and a frame that lasts as long as the work of the one before. Run it with and without time dilation. Then change the cost to 15 ms and predict what happens before you run it.

   :::answer[Worked solution]{tests="dilation,toy" solution="sketches/core-time-spiral.cpp"}
   The sketch holds the whole simulation, one function with a switch for time dilation. Its output is the table of the page: the frames of the cap-only run grow to 240 ms, and the frames with time dilation stay at 30 ms.

   ```cpp sketch="core-time-spiral.cpp"
   // The spiral of death: a step costs 30 ms of work but simulates only 20 ms, so each frame is longer than the one before.
   // The cap bounds the spiral; time dilation stops the catch-up steps instead. Times are whole milliseconds.
   #include <cstdio>

   namespace
   {
   	constexpr int c_Step = 20;     // ms of game time in one fixed step
   	constexpr int c_StepCost = 30; // ms of work one step takes
   	constexpr int c_MaxSteps = 8;  // the most steps one frame runs

   	void Run(const char* name, bool dilation)
   	{
   		std::printf("%s\n", name);
   		int accumulator = 0;
   		int frame = c_Step; // each frame lasts as long as the work of the frame before it
   		int gameTime = 0;
   		int wallTime = 0;
   		for (int number = 1; number <= 8; number++)
   		{
   			accumulator += frame;
   			int steps = 0;
   			bool dilated = false;
   			while (accumulator >= c_Step && steps < c_MaxSteps)
   			{
   				// The steps so far took longer than the time they simulated: stop catching up.
   				if (dilation && steps > 0 && steps * c_StepCost >= steps * c_Step)
   				{
   					dilated = true;
   					break;
   				}
   				accumulator -= c_Step;
   				steps++;
   			}
   			if (dilated)
   				accumulator %= c_Step; // the steps still due are dropped; a fraction of a step stays
   			else if (steps == c_MaxSteps && accumulator > c_Step)
   				accumulator = c_Step; // the backlog is dropped
   			gameTime += steps * c_Step;
   			wallTime += frame;
   			std::printf("frame %d: %3d ms long, %d steps, game time %3d ms of %3d ms\n", number, frame, steps, gameTime, wallTime);
   			frame = steps * c_StepCost;
   		}
   	}
   }

   int main()
   {
   	Run("cap only", false);
   	Run("time dilation", true);
   }
   ```

   ```text output-of="core-time-spiral.cpp"
   cap only
   frame 1:  20 ms long, 1 steps, game time  20 ms of  20 ms
   frame 2:  30 ms long, 1 steps, game time  40 ms of  50 ms
   frame 3:  30 ms long, 2 steps, game time  80 ms of  80 ms
   frame 4:  60 ms long, 3 steps, game time 140 ms of 140 ms
   frame 5:  90 ms long, 4 steps, game time 220 ms of 230 ms
   frame 6: 120 ms long, 6 steps, game time 340 ms of 350 ms
   frame 7: 180 ms long, 8 steps, game time 500 ms of 530 ms
   frame 8: 240 ms long, 8 steps, game time 660 ms of 770 ms
   time dilation
   frame 1:  20 ms long, 1 steps, game time  20 ms of  20 ms
   frame 2:  30 ms long, 1 steps, game time  40 ms of  50 ms
   frame 3:  30 ms long, 1 steps, game time  60 ms of  80 ms
   frame 4:  30 ms long, 1 steps, game time  80 ms of 110 ms
   frame 5:  30 ms long, 1 steps, game time 100 ms of 140 ms
   frame 6:  30 ms long, 1 steps, game time 120 ms of 170 ms
   frame 7:  30 ms long, 1 steps, game time 140 ms of 200 ms
   frame 8:  30 ms long, 1 steps, game time 160 ms of 230 ms
   ```

   1. **Lines 23–33:** the loop pays out steps; with time dilation it stops after a step whose work lasted at least as long as the time it simulated.
   2. **Lines 34–37:** time dilation drops the steps due and keeps the fraction; the cap alone sets the accumulator to one step.

   With a cost of 15 ms, a step is cheaper than the game time it simulates, so no spiral starts. Frame 1 runs one step, so frame 2 lasts 15 ms, delivers less than a step and runs none. The toy then makes a frame of 0 ms, because its frames cost only their steps, and it stops moving. A real frame also costs drawing, so time keeps arriving and a step runs every frame or two; time dilation never triggers.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Scene/Scene.cpp`: `Scene::OnUpdateRuntime` (the phases, the accumulator, the cap, time dilation and the drawn fraction of a step) and `Scene::GetMaxFixedSteps`.
- `Strata/src/Strata/Scene/Scene.h`: `GetFixedTimestep`, `Step`, `GetFixedStepCount`, `SetTimeScale`, `GetUnscaledDeltaTime`, `SetTimeDilation`, `GetDroppedFixedStepCount`, `GetStepAlpha` and `SceneSettings`.
- `Strata/src/Strata/Scene/ProjectSceneTiming.h`: the `Scene.Timing` section and `GetMaxSteps`.
- `Strata/src/Strata/Core/Application.cpp`: the clamp to `ApplicationSpecification::MaxTimestep`; `Strata/src/Strata/Core/Timer.h`: `Time::GetTime`.
- `StrataScriptCore/Include/StrataScript/Time.h` and `Script.h`: the script side, `Time` and the three callbacks.
- `StrataEditor/src/EditorLayer.cpp` and `StrataRuntime/src/RuntimeApplication.cpp`: where time dilation is enabled.
- In the editor: **File ▸ Project Settings...** (the **Timing** page of the **Physics** category, the section `Scene.Timing`) and **File ▸ Preferences...** (the frame rate section). Commands: `project.setSettings`, `scene.info`, `play.step`.
- Tests: `StrataTests/src/Scene/SceneTests.cpp` (`Runtime update runs systems at the fixed timestep`, `Time dilation drops the fixed steps that cannot keep up with real time`).

## Further reading

- [Glenn Fiedler, "Fix Your Timestep"](https://gafferongames.com/post/fix_your_timestep/): the variable, semi-fixed and fixed step, the accumulator and the spiral of death, with code; intermediate.
- [Robert Nystrom, "Game Loop", in Game Programming Patterns](https://gameprogrammingpatterns.com/game-loop.html): loops locked to the display, variable steps and fixed steps; beginner.
- [Unity manual, "Time and frame rate management"](https://docs.unity3d.com/Manual/TimeFrameManagement.html): fixed update, the fixed update step and the maximum allowed step; beginner.
- [Godot documentation, "Physics introduction"](https://docs.godotengine.org/en/stable/tutorials/physics/physics_introduction.html): the physics process and its ticks per second; beginner.
