---
id: world/interpolation
title: "Drawing between fixed steps"
description: "How Strata draws what its fixed steps move between their last two poses, so motion stays smooth above the step rate and the simulation never reads it."
kind: internals
size: L
tracks: [E]
needs: [world/scene-graph, world/systems, basics/math-interpolation]
time: 95
learn:
  - id: approaches
    text: compare interpolation, extrapolation and a variable step by what each costs
  - id: drawn-time
    text: compute the step alpha and the drawn time of a frame from its accumulator and its steps
  - id: roles
    text: choose the role, Blend, Compose or Exact, that an entity the steps moved gets
  - id: rules
    text: write renderer and game code that reads drawn transforms and never simulates with them
  - id: trace
    text: trace a drawn matrix from the render scene's sync to the code that computes it
since: 0.8.0
status: final
---

A crate that the simulation moves 60 times a second can be shown on a screen that refreshes 144 times a second. Between two steps the simulation has not moved the crate, so a :term[renderer]{id=renderer} that draws the latest pose shows it standing still and then jumping. Interpolation is the part of Strata's `Scene` that draws what the :term[fixed steps]{id=fixed-step} moved between the last two poses, which keeps motion smooth at every :term[frame rate]{id=frame-rate}. It changes only what is drawn: the simulation never reads it, and it never changes a transform or the step count. It does not decide when steps run ([Time](../core/time.md) does), and it draws nothing itself: the renderer reads its results.

## The problem and how engines solve it

### Judder, in numbers

Take a crate that slides at 6 metres per second. The simulation moves it in fixed steps of 16.7 ms (60 steps a second), so every step moves it 0.1 m. A display that refreshes 144 times a second shows a frame every 6.9 ms. A step is due every 2.4 frames: some frames run a step, and most run none.

Count what a renderer shows if it draws the latest pose. Over 11 frames, which last 76 ms, four steps run, on frames 3, 5, 8 and 10. The crate is drawn at 0, 0, 0.1, 0.1, 0.2, 0.2, 0.2, 0.3, 0.3, 0.4 and 0.4 m. It moves on four frames and stands still on seven.

Smooth motion would move the crate 0.042 m on every frame, which is 6 m/s times 6.9 ms. Instead the picture holds still for one or two frames and then jumps 0.1 m, 2.4 times too far. The eye reads this as **judder**: a steady motion that jerks. A camera that follows the crate makes it easier to see.

The step is the reason for the problem, and also the reason it cannot be removed at its source. A fixed step gives the same poses on every machine for the same inputs. So the fix has to live in what is drawn, not in what is simulated.

:::history
Strata 0.7.0 and earlier drew every entity at its latest simulated pose. The audit for 0.8.0 measured the result: the robot of the Third-Person sample, drawn at 702 frames per second on a 4K screen, swung 29.4 pixels peak to peak against a camera that followed it.
:::

### Four ways out

An engine has four usual answers. The table lists what each draws and what it costs.

| Approach | What is drawn | What it costs |
| --- | --- | --- |
| Raise the step rate | The newest pose, more often | More simulation work, and judder whenever the rates differ |
| Step by the frame's time | The simulation at the frame's own time | Different poses on different machines, and unstable long steps |
| Extrapolate | A guess ahead of the newest pose | Overshoot where motion stops or turns, and a snap back |
| Interpolate | A pose between the last two | One step of delay, and work for every entity that moved |

Raising the rate shrinks the jump but cannot match every display: players own 60, 120, 144 and 240 Hz screens, and a rate that suits one differs from the others.

A **variable step** advances the simulation by the time the frame took. The motion is smooth, but the same inputs meet different step lengths on different machines, so results differ, and every tool that counts steps loses its clock.

To **extrapolate** is to draw the entity where its last speed says it should be by now. Nothing lags, but the guess is wrong exactly when it matters.

:::example[A crate that hits a wall]
The crate again, at 6 m/s, with a wall at 0.3 m. Steps run at 0, 16.7, 33.3 and 50 ms, so the poses are 0, 0.1, 0.2 and 0.3 m. The wall then holds the crate at 0.3 m.

A frame comes 8.3 ms after the step at 50 ms, which is half a step. An extrapolating renderer adds the last speed times 8.3 ms, which is 0.05 m, and draws the crate at 0.35 m: 5 cm inside the wall. At 66.7 ms the next step reports 0.3 m and the crate snaps back.

A renderer that draws between poses uses the time of the latest step plus the leftover time minus one step: 50 + 8.3 - 16.7 = 41.7 ms. That time lies halfway between 0.2 m at 33.3 ms and 0.3 m at 50 ms, so the crate is drawn at 0.25 m and never passes the wall. The price is that 0.25 m is where the simulation had the crate 8.3 ms ago.
:::

### What Strata chose

Strata interpolates. **Interpolation** (also called state interpolation) draws each entity that the fixed steps moved between its pose before the latest steps and its pose after them. An entity the steps did not move is drawn where it is.

The matrix an entity is drawn with in one frame is its **drawn transform**. While a game runs on the clock it can differ from the entity's :term[world transform]{id=world-transform} by up to a step of motion. What the simulation reads, `TransformComponent` and `WorldTransformComponent` included, stays what a scene without interpolation holds, bit for bit.

:::why
Extrapolation overshoots at every stop and collision, and a variable step loses identical results on every machine and the step count. Interpolation leaves the simulation alone. Its cost is delay: the drawn time trails the clock by exactly one step, where the latest pose trails it by anywhere from none to one. On average the delay grows by half a step, close to 8 ms at 60 steps a second. A higher `FixedRate` in the project's settings shrinks it.
:::

:::elsewhere
Unity runs physics in fixed steps and lets each rigid body choose interpolation or extrapolation. A well-known article on fixed steps describes the :term[accumulator]{id=accumulator} and the blend between steps that this page builds on.
:::

## The map

The scene graph's world transforms feed everything here. The fixed steps write them, a capture pass records what they changed, and the render scene reads the result. The diagram shows who feeds whom.

```mermaid caption="The fixed steps move entities, a capture pass records the set, and the render scene and scripts read drawn matrices computed from it." alt="Boxes joined by arrows. Fixed steps lead to a capture pass, which fills the interpolated set. The frame computes the step alpha and gives it to the set. The render scene's sync and scripts read drawn matrices from the set."
flowchart LR
  steps["Fixed steps"] --> capture["Capture pass"]
  capture --> set["Interpolated set"]
  frame["Step alpha of the frame"] --> set
  set --> sync["Render scene sync"]
  set --> scripts["Scripts in the late update"]
```

The **interpolated set** is the scene's list of entities that the latest stepping frame moved, with a drawn matrix for each. Every entry has one of three roles:

- **Blend**: the entity's own transform changed in the steps, so it is drawn between its world pose before them and its world pose after them.
- **Compose**: the entity moved only because an ancestor moved, so it is drawn as its parent's drawn matrix times its own current :term[local transform]{id=local-transform}.
- **Exact**: the entity is drawn where it is, with no blend. Causes are a teleport, a move every frame, a new parent, shear (its axes no longer at right angles), or creation without an interpolated parent.

The code is in `Strata/src/Strata/Scene/SceneInterpolation.cpp` and `Strata/src/Strata/Scene/TransformInterpolation.h`, with two hooks in `Strata/src/Strata/Scene/Scene.cpp`: the :term[frame loop]{id=game-loop} `OnUpdateRuntime` and the walk of the world transforms. The :term[main thread]{id=main-thread} owns all of it. Sets of more than 1,024 entries are built and blended on the job system, the engine's pool of worker threads, where each job writes only its own entries. Worker threads may call `FindDrawnTransform`, which only reads, while no code changes the scene.

## The contract

The simulation may assume that interpolation changes nothing it can observe. The step count, the accumulator, the world transforms and physics come out exactly as in a scene with interpolation off. The tests run twin scenes and compare them bit for bit.

Callers must follow five rules, each with its reason.

1. **Renderer code draws drawn transforms.** Place what you draw with `Scene::FindDrawnTransform` after `UpdateDrawnTransforms`, or with `GetDrawnTransform` where code runs before the frame's sync. When the entity has no drawn matrix, use its world matrix. Never read the set itself. Reason: its layout belongs to the scene and changes whenever a stepping frame rebuilds it.
2. **Simulation never reads drawn transforms.** A script that moved a body by what it read from the drawn pose would feed a step of delay into its own motion. The scene would then simulate differently with interpolation on and off. Reason: the fixed step exists to prevent that.
3. **A teleport must say so.** After a jump, call `BreakInterpolation`. The physics world's `Teleport` and `TeleportCharacter` do it for you. A script that sets a transform far away in `OnFixedUpdate` calls `ResetInterpolation`. Reason: a blended jump draws a streak across the scene.
4. **Follow moving bodies with their drawn pose.** A follow camera reads `GetDrawnPosition` and `GetDrawnRotation` in `OnLateUpdate`. Reason: the body is drawn behind its world position, so a camera on the world position slides against it. At 6 m/s the offset swings between 0 and 0.1 m every step.
5. **Move carriers in fixed steps.** A platform that others ride moves in `OnFixedUpdate` or as a kinematic body, which scripts move and physics does not push. Reason: a platform that a script moves in `OnUpdate` every frame is drawn where it is, but the riders that the steps move are drawn a step behind it.

:::rule[Drawn transforms]
The engine's guide says that renderers read `Scene::FindDrawnTransform` and that teleports call `BreakInterpolation`, because fixed-step motion is drawn between its last two poses. The reasons are the first and third rules above. The code behind them is in the sections on [drawn matrices](#drawn-matrices) and on [breaks](#breaks-clears-and-the-safety-net).
:::

## A toy version

The toy shows the idea with one body and no engine. The body moves 6 m/s in steps of 1/60 second. Frames come at 144 Hz, except frame 6, which lasts 40 ms and needs two steps. For every frame the program prints the position of a renderer that draws the latest pose and of one that blends.

```cpp sketch="world-interpolation-toy.cpp"
// A toy interpolation: a body steps at 60 Hz, frames come at 144 Hz, and the drawn position is printed both ways.
#include <cstdio>
#include <vector>

int main()
{
	const float step = 1.0f / 60.0f;
	const float speed = 6.0f; // metres per second: 0.1 m a step
	// Mostly 144 Hz frames, with one slow frame of 40 ms in the middle that needs two steps.
	std::vector<float> frames(12, 1.0f / 144.0f);
	frames[6] = 0.040f;

	float accumulator = 0.0f;
	float position = 0.0f; // the simulation's pose, after the latest step
	float from = 0.0f;     // the pose before the latest stepping frame's steps
	float to = 0.0f;       // the pose after them
	int steps = 1;         // how many steps that frame ran
	float lastBlended = 0.0f;
	float lastPlain = 0.0f;

	std::printf("frame steps  alpha  plain(m)  moved(m)  blended(m)  moved(m)\n");
	for (size_t index = 0; index < frames.size(); index++)
	{
		accumulator += frames[index];
		int ran = 0;
		const float before = position;
		while (accumulator >= step)
		{
			position += speed * step;
			accumulator -= step;
			ran++;
		}
		if (ran > 0)
		{
			from = before;
			to = position;
			steps = ran;
		}
		// The drawn time is T + a - h, where T is the end of the latest step and a the accumulator.
		const float alpha = 1.0f - (1.0f - accumulator / step) / static_cast<float>(steps);
		const float blended = from + (to - from) * alpha;
		std::printf("%5zu %5d %6.3f  %8.3f  %8.3f  %10.3f  %8.3f\n", index, ran, alpha, position, position - lastPlain, blended,
			blended - lastBlended);
		lastPlain = position;
		lastBlended = blended;
	}
	return 0;
}
```

```text output-of="world-interpolation-toy.cpp"
frame steps  alpha  plain(m)  moved(m)  blended(m)  moved(m)
    0     0  0.417     0.000     0.000       0.000     0.000
    1     0  0.833     0.000     0.000       0.000     0.000
    2     1  0.250     0.100     0.100       0.025     0.025
    3     0  0.667     0.100     0.000       0.067     0.042
    4     1  0.083     0.200     0.100       0.108     0.042
    5     0  0.500     0.200     0.000       0.150     0.042
    6     2  0.950     0.400     0.200       0.390     0.240
    7     1  0.317     0.500     0.100       0.432     0.042
    8     0  0.733     0.500     0.000       0.473     0.042
    9     1  0.150     0.600     0.100       0.515     0.042
   10     0  0.567     0.600     0.000       0.557     0.042
   11     0  0.983     0.600     0.000       0.598     0.042
```

1. **Lines 14–19:** the simulation's pose, the pose before the latest stepping frame's steps, the pose after them, and how many steps that frame ran.
2. **Lines 24–32:** the accumulator collects :term[frame time]{id=frame-time} and the loop runs a step for every full step in it, as the frame loop does.
3. **Lines 33–38:** the two poses and the step count change only on a frame that ran a step. Other frames keep them.
4. **Lines 39–41:** the alpha and the blend, which the rest of this page explains.

The plain column moves 0.1 m or not at all, except on the slow frame 6, which runs two steps and jumps 0.2 m. The blended column moves 0.042 m on almost every frame, as smooth motion should. The slow frame 6 moves it 0.240 m, which is right: 40 ms at 6 m/s is 0.24 m, so the toy is smooth in time. The first two frames show no motion because no step has run.

The toy omits the hard parts: a hierarchy, writes between steps, teleports, and 100,000 entities. The real code decides which entities to blend, keeps the blend right when scripts write transforms, and does the work fast.

## The real code

### The switch

A scene interpolates only when three things hold. `IsInterpolating` is true when the program's switch is on, when the project's `Scene.Timing` field `Interpolation` is on (the default), and when the scene runs. A bare `Scene` has the switch off, so tests and tools draw what they simulate. `StrataRuntime` enables it when it renders outside runs that end by themselves (`--frames`, `--seconds`), and the editor enables it for Play and Simulate outside scripted runs. [Projects and settings](./projects-settings.md) teaches the project's field.

The function that sets the switch clears the set when it is disabled.

```cpp src="Strata/src/Strata/Scene/SceneInterpolation.cpp#L165-L172"
void Scene::SetInterpolation(bool enabled)
{
	if (enabled == m_InterpolationEnabled)
		return;
	m_InterpolationEnabled = enabled;
	if (!enabled)
		ClearInterpolation();
}
```

Every other entry point returns early or draws world matrices while `IsInterpolating` is false. That one condition is why a program that never asks for interpolation pays nothing for it.

### The set

The set is three arrays with one index, called a slot: the entities, their entries and their drawn matrices. A fourth array maps an entity's index to its slot, so a lookup costs one read. `FindInterpolationSlot` compares the whole entity handle, so a destroyed entity whose index came back into use is not mistaken for the old one. Parents come first, so a parent's slot is smaller than its children's.

The :term[header]{id=header} holds the role, the pose and the entry.

```cpp src="Strata/src/Strata/Scene/TransformInterpolation.h#L15-L38"
// How an entity of the interpolated set is drawn.
enum class InterpolationRole : uint8_t
{
	Blend,   // Its own transform changed in the fixed steps: drawn between its world pose before them and after them
	Compose, // Moved only with an ancestor: its parent's drawn transform times its current local transform
	Exact    // Drawn where it is: a teleport, a per-frame move, a reparent, shear, or new without an interpolated parent
};

// A world pose in parts, as the blend reads them.
struct InterpolationPose
{
	glm::vec3 Translation = glm::vec3(0.0f);
	glm::quat Rotation = glm::quat(1.0f, 0.0f, 0.0f, 0.0f);
	glm::vec3 Scale = glm::vec3(1.0f);
};

// An entry of the set besides its entity and drawn matrix (Scene keeps the three in parallel arrays, by slot).
struct InterpolatedEntry
{
	uint32_t ParentSlot = c_NoInterpolationSlot; // Its hierarchy parent's slot when the parent is in the set
	InterpolationRole Role = InterpolationRole::Exact;
	InterpolationPose From; // Blend: the world pose before the stepping frame's steps
	InterpolationPose To;   // Blend: after them; per-frame rotation and scale writes keep it current
};
```

1. **Lines 16–20:** the three roles, each with its rule in the comment beside it.
2. **Lines 24–28:** a pose is a world transform in parts, because a blend needs the parts.
3. **Line 34:** the parent's slot, or no slot when the parent is not in the set.
4. **Line 35:** the role starts as Exact: an entry draws where the entity is until a rule says otherwise.
5. **Lines 36–37:** the pose before the stepping frame's steps and the pose after them, used by Blend entries.

### The capture after the steps

The frame loop needs two updates of the world transforms to learn what the steps changed. While the scene interpolates, it calls `UpdateWorldTransforms` before the fixed steps, so the writes of `OnUpdate` settle first and the steps' writes stand alone. After the steps it calls `CaptureInterpolation`, which runs `UpdateWorldTransforms` in a capture pass. The pass records each matrix before it replaces it. The set then holds bodies, characters, what `OnFixedUpdate` moves, and everything below them.

`CaptureInterpolation` builds the new set in four phases. The first decides each entity's role.

```cpp src="Strata/src/Strata/Scene/SceneInterpolation.cpp#L259-L302"
// The safety net: a step faster than box3d's maximum speed is a teleport.
const float maxDistance = c_MaxInterpolatedSpeed * static_cast<float>(steps) * timestep;

// 1. Fill: each record reads the registry and the old set, and writes only its own new entry (and the old slot it
// keeps, which belongs to its entity alone).
ForSlots(count, [&](uint32_t begin, uint32_t end)
{
	for (uint32_t index = begin; index < end; index++)
	{
		const TransformCapture& capture = m_Captures[index];
		m_NextEntities[index] = capture.Entity;
		InterpolatedEntry& entry = m_NextEntries[index];
		entry = InterpolatedEntry {};
		const uint32_t old = FindInterpolationSlot(capture.Entity);
		if (old != c_NoInterpolationSlot)
			m_KeptSlots[old] = 1;
		if (!capture.HadWorld)
		{
			m_SlotScratch[index] = 1;
			continue;
		}
		if (!capture.OwnChange)
		{
			entry.Role = InterpolationRole::Compose;
			continue;
		}
		const glm::mat4& world = worlds->get(capture.Entity).Matrix;
		if (SameMatrix(world, capture.Previous))
			continue;
		bool exactTo = false;
		entry.To = hierarchy->get(capture.Entity).Parent == entt::null ? GetLocalPose(transforms->get(capture.Entity), exactTo)
			: DecomposePose(world, exactTo);
		bool exactFrom = false;
		// The per-frame rules keep a Blend entry's To equal to its world pose before the steps.
		if (old != c_NoInterpolationSlot && m_InterpolatedEntries[old].Role == InterpolationRole::Blend)
			entry.From = m_InterpolatedEntries[old].To;
		else
			entry.From = DecomposePose(capture.Previous, exactFrom);
		// Both poses in one convention: a root's To keeps its authored signs, a decomposed From folds them into X.
		if (!exactTo && !exactFrom && MatchScaleSigns(entry.From, entry.To.Scale)
			&& glm::length(entry.To.Translation - entry.From.Translation) <= maxDistance)
			entry.Role = InterpolationRole::Blend;
	}
});
```

1. **Lines 259–260:** the safety net: a move longer than the top speed of box3d, the physics library, times the time simulated is a teleport, never a blend.
2. **Lines 275–279:** an entity with no earlier world matrix was created during the steps. Phase three decides it from its parent.
3. **Lines 280–284:** an entity whose own transform did not change moved only with an ancestor: Compose.
4. **Lines 286–287:** a matrix that did not change keeps the default role, Exact.
5. **Lines 293–300:** a Blend needs a starting pose, a finishing pose, matching scale signs and a distance below the net. Otherwise the entry stays Exact.

The second phase handles entities of the old set that the new one omits. They stopped moving, since the capture records only matrices that were computed again, so they are drawn where they are from now on. The capture logs them as transform changes, which tells readers of that log that their drawn matrix jumped to the world matrix. The third and fourth phases settle parents and breaks.

```cpp src="Strata/src/Strata/Scene/SceneInterpolation.cpp#L329-L373"
// 3. Parents: the walk recorded parents first, so a parent in the set has a smaller slot. Entities created during the
// steps ride their parent when it is in the set, and are drawn where they are otherwise.
ForSlots(count, [&](uint32_t begin, uint32_t end)
{
	for (uint32_t slot = begin; slot < end; slot++)
	{
		InterpolatedEntry& entry = m_InterpolatedEntries[slot];
		entry.ParentSlot = FindInterpolationSlot(hierarchy->get(m_InterpolatedEntities[slot]).Parent);
		if (m_SlotScratch[slot])
			entry.Role = entry.ParentSlot != c_NoInterpolationSlot ? InterpolationRole::Compose : InterpolationRole::Exact;
		else if (entry.Role == InterpolationRole::Compose && entry.ParentSlot == c_NoInterpolationSlot)
			entry.Role = InterpolationRole::Exact;
	}
});

// 4. Breaks during the steps: the broken entities are drawn where the steps left them, with every Blend entry below.
if (!m_PendingBreaks.empty())
{
	std::fill(m_SlotScratch.begin(), m_SlotScratch.end(), uint8_t(0));
	for (const entt::entity entity : m_PendingBreaks)
	{
		const uint32_t slot = FindInterpolationSlot(entity);
		if (slot == c_NoInterpolationSlot)
			continue;
		m_SlotScratch[slot] = 1;
		m_InterpolatedEntries[slot].Role = InterpolationRole::Exact;
	}
	for (uint32_t slot = 0; slot < count; slot++)
	{
		InterpolatedEntry& entry = m_InterpolatedEntries[slot];
		if (m_SlotScratch[slot] || entry.ParentSlot == c_NoInterpolationSlot || !m_SlotScratch[entry.ParentSlot])
			continue;
		m_SlotScratch[slot] = 1;
		if (entry.Role == InterpolationRole::Blend)
			entry.Role = InterpolationRole::Exact;
	}
	m_PendingBreaks.clear();
}

m_DrawnMatrices.resize(count);
m_InterpolationSteps = std::max(1u, steps);
m_InterpolationTimestep = timestep;
m_DrawnStale = true;
m_DrawnFilled = false;
m_DrawnVersion++;
```

1. **Lines 336–340:** the parent's slot is found now that every slot exists. A new entity composes with an interpolated parent and is drawn where it is otherwise.
2. **Lines 345–355:** teleports requested during the steps make their entities Exact.
3. **Lines 356–364:** every Blend entry below a broken entity becomes Exact too. The parent's slot is smaller, so the loop meets it first.
4. **Lines 368–373:** the drawn array gets its size, the step count and :term[timestep]{id=time-step} are stored for the alpha, and the drawn matrices are marked stale under a new version.

### The step alpha

The set holds two poses, and each frame must say how far between them to draw. That fraction is the **step alpha**: the share of the way from the poses before the latest stepping frame's steps to those after them that this frame draws.

The time line shows one frame. Steps ran at 0, 16.7 and 33.3 ms, so the latest step ended at $T$ = 33.3 ms and the two poses are those at 16.7 and 33.3 ms. The frame happens at 37.5 ms, which leaves 4.2 ms in the accumulator.

::figure{id=step-timeline}

The drawn time trails the clock by one step: 33.3 + 4.2 - 16.7 = 20.8 ms. It lies 4.2 ms after the first pose, a quarter of the 16.7 ms between them, so the alpha is 0.25. The body is drawn at 0.100 m + 0.25 × 0.100 m = 0.125 m. Its child light, a Compose entry, is drawn at its parent's 0.125 m plus its own local offset of 0.5 m. A crate teleported at the second step is Exact and has no blend.

When a frame runs $n$ steps, the two poses are $n$ steps apart, and one formula keeps the drawn time the same:

$$
\alpha = 1 - \frac{1 - a/h}{n}
$$

$\alpha$ is the step alpha, a fraction from 0 to 1. $a$ is the time left in the accumulator and $h$ is the step, both in seconds. $n$ is the number of steps the latest stepping frame ran. Read the fraction as "one minus the result of one minus a over h, divided by n".

:::derivation
The poses are at $T - nh$ and $T$, so they are $nh$ apart. The drawn time is $T + a - h$, which is $a - h + nh$ after the first pose. Divide by $nh$ and the fraction is $1 - (h - a)/(nh)$, which is the formula.
:::

Check the limits. With $n = 1$ the formula reduces to $a/h$: 0 when the frame lands exactly on a step, and nearly 1 right before the next. For a frame that ran two steps and left $a = 5$ ms, $a/h = 0.3$ and $\alpha = 1 - 0.7/2 = 0.65$. The drawn time is $T - 11.7$ ms, and 65 % of 33.3 ms after $T - 33.3$ ms is the same. With no step the poses and $n$ stay and $a$ grows, so the alpha grows too.

The frame loop computes the alpha right after the capture. It uses the step count that built the set, so frames without a step use it again.

```cpp src="Strata/src/Strata/Scene/Scene.cpp#L2313-L2321"
if (interpolating)
{
	if (steps > 0)
		CaptureInterpolation(steps, fixedTimestep);
	// Drawn one step behind the clock: the latest step ended at T, the set holds the poses at T - n h and T, and
	// T + a - h lies 1 - (1 - a / h) / n of the way between them (Docs/DeveloperGuide.md, "Interpolation").
	const float behind = 1.0f - std::min(m_FixedTimeAccumulator / fixedTimestep, 1.0f);
	m_StepAlpha = std::clamp(1.0f - behind / static_cast<float>(m_InterpolationSteps), 0.0f, 1.0f);
}
```

The code writes `behind` for `1 - a / h`, capped so that it never goes below zero, and subtracts `behind / steps` from 1. After a hitch, with :term[time dilation]{id=time-dilation}, or when the game drops steps it fell behind on, the drawn time still never moves backward. At :term[time scale]{id=time-scale} 0 the accumulator freezes and so does the alpha, so slow motion is drawn smoothly. `GetStepAlpha` is final after the frame's steps: `OnLateUpdate` sees this frame's value and `OnUpdate` sees the previous frame's. It is 1 while the scene is paused, stepping, or has interpolation off.

::figure{id=drawn-trace}

The second figure shows the toy's result. Without interpolation the position is a staircase. With it the position climbs in a straight line, one step behind in time, and that delay is the whole cost.

### Writes outside the steps

Scripts and tools write transforms between steps too: a script that moves a body every frame, an edit made while playing, a character that turns to walk. When `UpdateWorldTransforms` computes an entity of the set again, a per-frame rule decides what the write means for its entry.

```cpp src="Strata/src/Strata/Scene/SceneInterpolation.cpp#L196-L238"
void Scene::ApplyPerFrameRule(uint32_t slot, entt::entity handle, const glm::mat4& previous, bool ownChange, bool ancestorMoved)
{
	const entt::registry& registry = m_Registry;
	InterpolatedEntry& entry = m_InterpolatedEntries[slot];
	if (entry.Role == InterpolationRole::Exact)
		return;
	if (entry.Role == InterpolationRole::Compose)
	{
		// It composes from its current local transform every frame; only a reparent leaves its parent slot.
		const entt::entity parent = registry.get<HierarchyComponent>(handle).Parent;
		if (entry.ParentSlot == c_NoInterpolationSlot || m_InterpolatedEntities[entry.ParentSlot] != parent)
			entry.Role = InterpolationRole::Exact;
		return;
	}

	// A Blend entry. Moved with an ancestor: its world poses no longer describe it.
	if (ancestorMoved || !ownChange)
	{
		entry.Role = InterpolationRole::Exact;
		return;
	}
	const glm::mat4& world = registry.get<WorldTransformComponent>(handle).Matrix;
	if (MovedPerFrame(glm::vec3(previous[3]), glm::vec3(world[3])))
	{
		// A per-frame move: it asked to be there.
		entry.Role = InterpolationRole::Exact;
		return;
	}
	// A turn or a scale (the player turning to walk, root motion's turn): drawn as written on every frame, while the
	// translation keeps blending. Blending the turn from the captured rotation would draw it lagging and catching up.
	bool exact = false;
	const InterpolationPose written = GetWorldPose(handle, world, exact);
	if (exact)
	{
		entry.Role = InterpolationRole::Exact;
		return;
	}
	entry.From.Rotation = written.Rotation;
	entry.To.Rotation = written.Rotation;
	entry.From.Scale = written.Scale;
	entry.To.Scale = written.Scale;
	entry.To.Translation = written.Translation;
}
```

1. **Lines 200–209:** an Exact entry stays Exact. A Compose entry composes from its current local transform every frame, so only a new parent makes it Exact.
2. **Lines 211–216:** a Blend entry whose ancestor moved, or whose own transform did not change, no longer matches its two poses and becomes Exact.
3. **Lines 217–223:** a translation larger than a tiny share of the entity's distance from the origin (1e-5, with a floor of 1 m) means the writer asked the entity to be there. The entity is drawn there until the next step.
4. **Lines 224–237:** a turn or a scale leaves the translation blending, and the written rotation and scale replace the stored ones, so the turn is drawn as written on every frame.

The last rule matters for characters. A player who turns to walk writes a rotation each frame. Blending that turn from the captured rotation would draw it late and then catching up at every step.

### The pose blend

`BlendPose` turns two poses and an alpha into a matrix.

```cpp src="Strata/src/Strata/Scene/SceneInterpolation.cpp#L104-L116"
// The pose `alpha` of the way from the entry's From to its To. The translation as From + (To - From) * alpha, not
// glm::mix: monotonic and exact at both ends far from the origin. The rotation by a normalized lerp along the shorter
// arc: within 0.03 degrees of a slerp at 30 degrees a step, 0.9 at 90.
glm::mat4 BlendPose(const InterpolatedEntry& entry, float alpha)
{
	const InterpolationPose& from = entry.From;
	const InterpolationPose& to = entry.To;
	const glm::vec3 translation = from.Translation + (to.Translation - from.Translation) * alpha;
	const glm::quat target = glm::dot(from.Rotation, to.Rotation) < 0.0f ? -to.Rotation : to.Rotation;
	const glm::quat rotation = glm::normalize(from.Rotation * (1.0f - alpha) + target * alpha);
	const glm::vec3 scale = from.Scale + (to.Scale - from.Scale) * alpha;
	return Math::ComposeTransform(translation, rotation, scale);
}
```

1. **Line 111:** the translation is the start plus the difference times the alpha, a :term[lerp]{id=linear-interpolation}.
2. **Line 112:** when the :term[dot product]{id=dot-product} of the two :term[quaternions]{id=quaternion} is negative, one flips its sign, so the blend takes the shorter arc.
3. **Line 113:** a :term[normalized]{id=normalization} lerp, :term[nlerp]{id=nlerp}: the weighted sum of the four numbers, divided by its length.
4. **Line 114:** the scale is a lerp too.
5. **Line 115:** the three parts become a matrix.

The translation is written as the start plus a scaled difference, not with `glm::mix`. A mix multiplies both large positions by weights and adds the products, so each rounds at the size of the position. Far from the origin that rounding can make the result step backwards between two nearby alphas. The code rounds once, at the end, and the difference of two nearby poses is small. The result never goes backwards and is exact at both ends.

The rotation uses an nlerp, not a :term[slerp]{id=slerp}. The comment states the price in accuracy: within 0.03 degrees of a slerp for a turn of 30 degrees in a step, and 0.9 degrees at 90. Exercise 2 measures those numbers. A step turns an entity by a small angle, so the nlerp's uneven speed does not show, and it spares the sines and :term[cosines]{id=cosine} of every blend. [Rotations](../basics/math-rotations.md) teaches both blends.

### Drawn matrices

Nothing needs a drawn matrix until something draws. `UpdateDrawnTransforms` computes them when asked, and `RenderScene::Sync` calls it first.

```cpp src="Strata/src/Strata/Scene/SceneInterpolation.cpp#L410-L455"
void Scene::UpdateDrawnTransforms()
{
	UpdateWorldTransforms();
	if (m_InterpolatedEntities.empty() || !IsInterpolating())
		return;
	if (m_DrawnFilled && !m_DrawnStale && m_DrawnAlpha == m_StepAlpha)
		return;
	// Part of keeping what UpdateWorldTransforms keeps, timed with it.
	ST_PROFILE_STAGE("Scene.Transforms");

	const entt::registry& registry = m_Registry;
	const uint32_t count = static_cast<uint32_t>(m_InterpolatedEntities.size());
	const float alpha = m_StepAlpha;
	// 1. Blend and Exact entries: each reads the registry and its own entry and writes its own drawn matrix.
	ForSlots(count, [&](uint32_t begin, uint32_t end)
	{
		for (uint32_t slot = begin; slot < end; slot++)
		{
			const entt::entity entity = m_InterpolatedEntities[slot];
			const InterpolatedEntry& entry = m_InterpolatedEntries[slot];
			if (entry.Role == InterpolationRole::Compose || !registry.valid(entity))
				continue;
			const glm::mat4& world = registry.get<WorldTransformComponent>(entity).Matrix;
			// At alpha 1 the world matrix itself, bit for bit, whatever the decomposition.
			m_DrawnMatrices[slot] = entry.Role == InterpolationRole::Exact || alpha >= 1.0f ? world : BlendPose(entry, alpha);
		}
	});
	// 2. Compose entries, parents first, with the association UpdateWorldTransforms uses: under a parent drawn where it is,
	// a Compose entry equals its world matrix bit for bit.
	for (uint32_t slot = 0; slot < count; slot++)
	{
		const InterpolatedEntry& entry = m_InterpolatedEntries[slot];
		const entt::entity entity = m_InterpolatedEntities[slot];
		if (entry.Role != InterpolationRole::Compose || !registry.valid(entity))
			continue;
		if (entry.ParentSlot == c_NoInterpolationSlot || !registry.valid(m_InterpolatedEntities[entry.ParentSlot]))
			m_DrawnMatrices[slot] = registry.get<WorldTransformComponent>(entity).Matrix;
		else
			m_DrawnMatrices[slot] = Math::ComposeWorldTransform(m_DrawnMatrices[entry.ParentSlot],
				registry.get<TransformComponent>(entity).GetTransform());
	}
	m_DrawnAlpha = alpha;
	m_DrawnStale = false;
	m_DrawnFilled = true;
	m_DrawnVersion++;
}
```

1. **Lines 412–416:** it brings the world transforms up to date, then returns when there is no set or nothing changed: the same alpha and no write since. A run that draws nothing never blends.
2. **Lines 424–436:** Blend and Exact entries each read their own entry and write their own matrix, in parallel above 1,024 entries. At an alpha of 1 the matrix is the world matrix, bit for bit.
3. **Lines 439–450:** Compose entries follow in slot order, so a parent's drawn matrix is ready before its children's.
4. **Lines 451–454:** the alpha is remembered, the cache is marked current, and the version changes so readers know to look again.

Two functions read the result. `FindDrawnTransform` returns the cached matrix of an entry, or null for an entity outside the set; renderers use it. `GetDrawnTransform` serves code that cannot wait for a sync.

```cpp src="Strata/src/Strata/Scene/SceneInterpolation.cpp#L457-L477"
const glm::mat4* Scene::FindDrawnTransform(entt::entity handle) const
{
	if (!m_DrawnFilled)
		return nullptr;
	const uint32_t slot = FindInterpolationSlot(handle);
	return slot != c_NoInterpolationSlot ? &m_DrawnMatrices[slot] : nullptr;
}

glm::mat4 Scene::GetDrawnTransform(Entity entity) const
{
	if (!entity.IsValid())
		return glm::mat4(1.0f);
	if (entity.GetScene() != this)
		return entity.GetScene()->GetDrawnTransform(entity);
	const uint32_t slot = IsInterpolating() ? FindInterpolationSlot(entity.GetHandle()) : c_NoInterpolationSlot;
	if (slot == c_NoInterpolationSlot)
		return GetWorldTransform(entity);
	if (m_DrawnFilled && !m_DrawnStale && m_DrawnAlpha == m_StepAlpha && m_DirtyTransforms.empty())
		return m_DrawnMatrices[slot];
	return ComputeDrawnTransform(slot);
}
```

1. **Lines 459–462:** the cache is trusted only after a fill, and the pointer is null for an entity outside the set.
2. **Lines 471–476:** a script that reads the drawn transform in `OnLateUpdate` gets the cache when it is current. Otherwise it gets a matrix computed from the set the way the next update will.

That second path is `ComputeDrawnTransform`, and it makes `GetDrawnTransform` exact at any time.

```cpp src="Strata/src/Strata/Scene/SceneInterpolation.cpp#L479-L496"
glm::mat4 Scene::ComputeDrawnTransform(uint32_t slot) const
{
	const entt::registry& registry = m_Registry;
	const entt::entity handle = m_InterpolatedEntities[slot];
	const Entity entity(handle, const_cast<Scene*>(this));
	const InterpolatedEntry& entry = m_InterpolatedEntries[slot];
	const float alpha = m_StepAlpha;
	if (entry.Role == InterpolationRole::Exact)
		return GetWorldTransform(entity);
	const HierarchyComponent& node = registry.get<HierarchyComponent>(handle);
	if (entry.Role == InterpolationRole::Compose)
	{
		// The next update makes a reparented entry Exact.
		if (entry.ParentSlot == c_NoInterpolationSlot || m_InterpolatedEntities[entry.ParentSlot] != node.Parent)
			return GetWorldTransform(entity);
		return Math::ComposeWorldTransform(ComputeDrawnTransform(entry.ParentSlot),
			registry.get<TransformComponent>(handle).GetTransform());
	}
```

1. **Lines 486–487:** an Exact entry is its world transform.
2. **Lines 489–495:** a Compose entry is its parent's drawn transform, computed the same way, times its own local transform, unless it was given a new parent since.

The code walks up the hierarchy for every ancestor, so a call costs the entity's depth. Reading one body's pose costs little; a loop over all entities should read the cache.

### Breaks, clears and the safety net

A **teleport** is a jump that no motion explains: a character moved to a checkpoint, a body placed across the level. A blend would draw it as a streak, so a teleport must break the interpolation.

```cpp src="Strata/src/Strata/Scene/SceneInterpolation.cpp#L527-L549"
void Scene::BreakInterpolation(Entity entity)
{
	if (!entity.IsValid())
		return;
	if (entity.GetScene() != this)
	{
		entity.GetScene()->BreakInterpolation(entity);
		return;
	}
	if (!IsInterpolating())
		return;
	const uint32_t slot = FindInterpolationSlot(entity.GetHandle());
	if (m_InFixedSteps)
	{
		// The capture after the steps applies it to the poses they leave.
		m_PendingBreaks.push_back(entity.GetHandle());
		if (slot != c_NoInterpolationSlot)
			m_InterpolatedEntries[slot].Role = InterpolationRole::Exact;
		return;
	}
	if (slot != c_NoInterpolationSlot)
		BreakSlot(slot);
}
```

1. **Lines 536–537:** a scene that does not interpolate has nothing to break.
2. **Lines 539–545:** during the steps the break is queued, and the capture after them applies it to the poses they leave.
3. **Lines 547–548:** outside the steps the break takes effect at once, including for what blends below.

The entity and every Blend entry below it are drawn where they are until the next step moves them again. The jump is logged as a transform change.

Some events empty the whole set and log every entity in it, so everything is drawn where it is. Pausing is one, so that :term[gizmos]{id=gizmo-start}, picking and captures match the picture. The others are stepped frames, a change of the fixed step, the project turning `Interpolation` off, `SetInterpolation(false)`, and starting or stopping the scene. After a pause no extra work is needed, because the next stepping frame starts from the poses the pause left.

The safety net catches a teleport that nobody announced. A step whose distance exceeds 400 m/s times the simulated time, 6.7 m for one step of 1/60 s, counts as a teleport. `Scene::c_MaxInterpolatedSpeed` has that value because it is box3d's maximum speed, so no body moves faster. A wrong Exact costs at most a step of judder, while a wrong blend draws a streak, so the code chooses Exact when in doubt.

Two functions inspect the set. `GetInterpolationStats` counts its entities by role for commands and tests, and walks the set to do it. `ValidateInterpolation` checks that the arrays agree, the slot map maps back, parents come first, Compose entries name their parent and poses are finite. Debug builds run it in the paced check of the scene's caches after updates, which [the scene graph](./scene-graph.md) describes.

## What it does not do yet

The drawn transform reaches mesh proxies (the renderer's copies of meshes) and skinned palettes (the joint matrices of animated meshes). It also reaches point and spot lights with their shadow views, the scene camera and its focus, and world-space text. Other readers still use the simulated pose, which can differ from the drawn pose by a step of motion while a game runs:

- world-space game user interface (UI), editor gizmos and picking rays;
- reflection probes, fog, post-process volumes, the sky and the sun's direction;
- attachments placed outside their animator's hierarchy;
- audio and world streaming, which follow the simulation on purpose.

The first three groups are known issues of the 0.8.0 release, listed in `Docs/Releases/0.8.0.md` and as later work in `Docs/Roadmap.md`, and there is no cap on interpolated bodies. The capture also costs time: a frame that runs a step with 100,000 moving roots takes 5.5 ms against 2.6 ms without interpolation, 2.1 times as long, against a target of 1.5. That number is a measurement recorded in the release notes and in the ratio of the metric `InterpolatedStepFrame100k` in the `Perf.Scene` suite, and it can change.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Draw the latest pose | Strata 0.7.0 and earlier | No delay, no work | Judder above the step rate |
| Extrapolate | Unity offers it for a rigid body | No added delay | Overshoot at stops, then a snap back |
| A variable step | Described and argued against in a well-known article on fixed steps | Smooth motion with no set | The same result on every machine, and the step count |
| A higher fixed rate | Strata's `Scene.Timing` offers it | Half the delay at 120 Hz | Simulation time, and judder when the display differs |
| Blend descendants' world poses | No engine named here | One rule for every entity | Per-frame local writes lag a full step: 10.8 cm at 6.5 m/s |
| Blend every entity | No engine named here | No set, no capture | Work and memory for entities that did not move |

## How it is tested

The `Scene.Timing` suite in `StrataTests/src/Scene/SceneInterpolationTests.cpp` checks the behaviour as numbers. One test draws a mover at 1,024 frames per second and requires every frame to move the same distance. It then shows that without interpolation frames either stand still or jump a whole step. `The alpha draws one step behind the clock` compares `GetStepAlpha` with the formula for six frame lengths and a hitch. Other tests cover roles, per-frame writes, entities created during the steps, leaving the set, pause and time scale, breaks, mirrored roots, and the default of off.

`Scene.Timing.Sweep` runs random frames, edits, steps, pauses, spawns and breaks on twin scenes. It requires that the simulation equals the scene without interpolation and that every drawn transform stays consistent. `Physics.Interpolation` in `StrataTests/src/Physics/PhysicsInterpolationTests.cpp` checks that a character walking at 6.5 m/s is drawn within a pixel of its path at every frame rate a following camera sees. It also checks that interpolation changes no simulated pose and that teleports draw no streak.

Run one suite directly, or all tests with the preset:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Scene.Timing*
ctest --preset windows-debug -j 8
```

The cost has perf tests for Release and :term[Dist]{id=dist} builds: the metrics `InterpolatedStepFrame100k`, its `Ratio` and `InterpolatedFrame100k` of the `Perf.Scene` suite. Run them with `ctest --preset windows-release -L perf`.

## Changing it safely

New code that draws something at an entity's place reads `FindDrawnTransform`, with the world matrix as the fallback. Code that moves what the steps move writes in `OnFixedUpdate` or through physics, because a per-frame move is drawn where it is. Code that jumps an entity calls `BreakInterpolation`.

A change to the set has four checks to pass. The `Scene.Timing` and `Physics.Interpolation` suites stay green, and `Scene.Timing.Sweep` keeps the simulation equal to the scene without interpolation. `ValidateInterpolation` holds in a Debug build after every update. Perf budgets only go down, and a change to the capture's cost states its measured values.

A new reader of drawn matrices compares `GetDrawnTransformsVersion` to know when to look again.

Two engine rules apply. Engine code that sets transform fields itself must tell the scene, as the [scene graph](./scene-graph.md) teaches, because the capture relies on the dirty flags. A new script function goes at the end of the host table, as `GetStepAlpha` and `ResetInterpolation` did.

## What went wrong before

An early version blended a mirrored root, such as one with scale (1, 1, -1), between poses with different sign conventions. A root's pose keeps its authored signs, while a pose taken from a matrix folds the reflection into X: scale (-1, 1, 1) turned half around Y. The first segment after such a root began to move blended between the two. The scale passed through zero and the body turned by up to 90 degrees on every frame between steps.

The fix rewrites the starting pose with the finishing pose's signs, which describes the same matrix, and draws Exact when an odd number of signs differ. `ValidateInterpolation` now rejects a Blend whose poses have different signs. The regression test is in `Scene.Timing`: `Mirrored roots are drawn mirrored and turning between their steps, also in their first segment`.

## Summary

- Interpolation costs a step of delay and some work, extrapolation overshoots at stops, and a variable step gives different results on different machines.
- The drawn time is $T + a - h$, and the step alpha $1 - (1 - a/h)/n$ places it between the poses before and after the latest stepping frame's steps.
- An entity the steps moved is Blend, one that only follows its parent is Compose, and everything uncertain is Exact.
- Renderers read drawn transforms, simulation never does, teleports break, and followers read drawn poses in `OnLateUpdate`.
- `RenderScene::Sync` calls `UpdateDrawnTransforms` to make the matrices, and `GetDrawnTransform` computes the same matrix on demand.

## Check yourself

1. A crate stops against a wall at 0.3 m. Which technique can draw it at 0.35 m, and why?

   - a) Interpolation, because it blends the last two poses.
   - b) Extrapolation, because it adds the last speed to the newest pose.
   - c) A variable step, because the simulation then runs ahead of the frame.

   :::answer{tests="approaches"}
   Answer b. Extrapolation adds the last speed times the leftover time, 0.05 m, to the newest pose. Interpolation (a) never leaves the range of the two poses, so it draws at most 0.3 m. A variable step (c) changes how long the simulation steps, not how a pose is drawn.
   :::

2. A frame runs 2 steps of 16.7 ms and leaves 10 ms in the accumulator. What are the step alpha and the drawn time, relative to the end $T$ of the latest step?

   :::answer{tests="drawn-time"}
   $a/h = 10 / 16.7 = 0.6$, so $\alpha = 1 - (1 - 0.6)/2 = 0.8$. The drawn time is $T + 10 - 16.7 = T - 6.7$ ms. Check: the poses are 33.3 ms apart, and 80 % of 33.3 ms is 26.7 ms after $T - 33.3$ ms, which is 6.7 ms short of $T$.
   :::

3. A lamp is a child of a crate that a physics body moves. The crate is teleported in the steps. What roles do the crate and the lamp get?

   - a) Both Blend, because both moved.
   - b) The crate Exact and the lamp Compose.
   - c) The crate Blend and the lamp Exact.

   :::answer{tests="roles"}
   Answer b. The teleport breaks the crate to Exact. The lamp's own transform did not change, so it is Compose and follows its parent's drawn matrix. Option a ignores the break and the lamp's unchanged transform. Option c reverses both roles: only a Blend entry below a broken parent becomes Exact, and the lamp has no change of its own to blend.
   :::

4. A follow camera script runs in `OnUpdate` and reads `GetWorldPosition` of a player who moves in fixed steps. The game runs at 240 frames per second. What do players see, and what is the fix?

   :::answer{tests="rules"}
   The world position moves in whole steps while the player is drawn smoothly, so the player slides against the camera, by up to 0.1 m at 6 m/s. The fix is to read `GetDrawnPosition` and `GetDrawnRotation` in `OnLateUpdate`, where the step alpha is final.
   :::

5. Which function does the render scene's sync call first, and what does it do when nothing has changed?

   :::answer{tests="trace"}
   `Scene::UpdateDrawnTransforms`. It updates the world transforms and then returns at once when there is no set, or when the alpha is the same and no entry was written since.
   :::

## Exercises

1. **Basic.** At 60 steps a second a frame runs 3 steps and leaves 4 ms. Find the alpha and the drawn time.

   :::answer[Worked solution]{tests="drawn-time"}
   $h = 16.7$ ms, so $a/h = 4 / 16.7 = 0.24$. Then $\alpha = 1 - (1 - 0.24)/3 = 0.747$. The drawn time is $T + 4 - 16.7 = T - 12.7$ ms. The poses are 50 ms apart, and 0.747 × 50 = 37.4 ms after $T - 50$ ms is $T - 12.6$ ms, which agrees within rounding.
   :::

2. **Medium.** The comment of `BlendPose` says that nlerp strays 0.03 degrees from slerp for a turn of 30 degrees a step, and 0.9 at 90. Write a program that measures the largest gap for a few turns.

   Use the quaternions of `glm`, whose headers are in your Strata folder, and compile as for the sketches of [Blending and smoothing](../basics/math-interpolation.md#why-you-will-need-this). On Windows, run `cl /std:c++20 /EHsc /I "<Strata folder>\StrataScriptCore\ThirdParty\glm" sketch.cpp` and then `.\sketch.exe`. On Linux and macOS, run `c++ -std=c++20 -I "<Strata folder>/StrataScriptCore/ThirdParty/glm" sketch.cpp -o sketch` and then `./sketch`.

   :::answer[Worked solution]{solution="sketches/world-interpolation-nlerp.cpp" tests="roles"}
   The program compares `glm::slerp` with the code's normalized lerp for every alpha from 0 to 1 in steps of 0.01, measures the angle between the two results and keeps the largest. It uses doubles: in float, the inverse cosine of a number near 1 loses so much precision that a gap of 0.03 degrees hides in the noise.

   ```cpp sketch="world-interpolation-nlerp.cpp"
   // How far a normalized lerp strays from a slerp: the largest gap over every weight, for a few turns per step.
   #include <glm/glm.hpp>
   #include <glm/gtc/quaternion.hpp>

   #include <algorithm>
   #include <cmath>
   #include <cstdio>

   double AngleBetween(const glm::dquat& a, const glm::dquat& b)
   {
   	const double cosine = std::min(std::abs(glm::dot(a, b)), 1.0);
   	return glm::degrees(2.0 * std::acos(cosine));
   }

   int main()
   {
   	const glm::dvec3 axis(0.0, 1.0, 0.0);
   	for (const double degrees : { 10.0, 30.0, 90.0, 170.0 })
   	{
   		const glm::dquat from(1.0, 0.0, 0.0, 0.0);
   		const glm::dquat to = glm::angleAxis(glm::radians(degrees), axis);
   		double worst = 0.0;
   		for (int index = 0; index <= 100; index++)
   		{
   			const double alpha = static_cast<double>(index) / 100.0;
   			const glm::dquat exact = glm::slerp(from, to, alpha);
   			const glm::dquat cheap = glm::normalize(from * (1.0 - alpha) + to * alpha);
   			worst = std::max(worst, AngleBetween(exact, cheap));
   		}
   		std::printf("a turn of %5.1f degrees: nlerp strays at most %.3f degrees from slerp\n", degrees, worst);
   	}
   	return 0;
   }
   ```

   ```text output-of="world-interpolation-nlerp.cpp"
   a turn of  10.0 degrees: nlerp strays at most 0.001 degrees from slerp
   a turn of  30.0 degrees: nlerp strays at most 0.033 degrees from slerp
   a turn of  90.0 degrees: nlerp strays at most 0.919 degrees from slerp
   a turn of 170.0 degrees: nlerp strays at most 6.755 degrees from slerp
   ```

   1. **Lines 9–13:** the angle between two rotations is twice the inverse cosine of the absolute dot product, which also handles the shorter arc.
   2. **Lines 26–27:** the exact blend and the cheap one for the same alpha.
   3. **Line 28:** the largest gap so far.

   The gap grows with the turn: 0.033 degrees at 30, 0.919 at 90, as the comment says, and 6.8 at 170. A step turns an entity by far less, so the cheap blend is safe.
   :::

3. **Medium.** Trace it yourself. Start at `RenderScene::Sync` and follow the drawn matrix of a child light under a moving body to the code that computes it.

   :::answer[Worked solution]{tests="trace"}
   `RenderScene::Sync` in `Strata/src/Strata/Renderer/RenderScene.cpp` calls `Scene::UpdateDrawnTransforms` at line 331. That function starts at line 410 of `Strata/src/Strata/Scene/SceneInterpolation.cpp`, and its second loop, lines 439–450, handles Compose entries. For the light it stores `Math::ComposeWorldTransform` of the parent's drawn matrix and the light's local transform in `m_DrawnMatrices`. The light's record then reads that matrix through `Scene::FindDrawnTransform` (line 457 of the scene file), called at line 201 of `Strata/src/Strata/Renderer/RenderLights.cpp`, as a mesh proxy does through `RenderScene::GetDrawnTransform` at line 428. A script's `GetDrawnTransform` call reaches the same arithmetic in `ComputeDrawnTransform`, whose Compose case is at lines 489–495.
   :::

4. **Hard.** Your `Spinner` system rotates entities with a `SpinComponent` in `OnFixedUpdate`. Give one entity a child light. Describe a test that proves the `Spinner` entity is Blend and the light Compose, and say what it must do before its first check.

   :::answer[Worked solution]{tests="roles"}
   Create the entity and its child light before the scene starts, so both have world matrices. Call `SetInterpolation(true)`, then `OnRuntimeStart`. Run one frame longer than a step, for example `OnUpdateRuntime(Timestep(0.02f))`, because only a frame that runs a step builds the set. Then `GetInterpolationStats()` should report `Entities` 2, `Blended` 1, `Composed` 1 and `Exact` 0.

   The entity changed its own rotation, which makes it Blend. The light's own transform did not change, which makes it Compose. Confirm that the test fails when `SetInterpolation(true)` is removed.
   :::

## Where it lives in Strata

- Files: `Strata/src/Strata/Scene/SceneInterpolation.cpp`, `Strata/src/Strata/Scene/TransformInterpolation.h`, the hooks in `Strata/src/Strata/Scene/Scene.cpp` and `Strata/src/Strata/Scene/Scene.h`, and the reader `Strata/src/Strata/Renderer/RenderScene.cpp`.
- Functions: `Scene::SetInterpolation`, `IsInterpolating`, `GetStepAlpha`, `GetDrawnTransform`, `FindDrawnTransform`, `BreakInterpolation`, `GetInterpolationStats`, `ValidateInterpolation`, and the constant `Scene::c_MaxInterpolatedSpeed`.
- Script interface: `GetDrawnPosition`, `GetDrawnRotation`, `ResetInterpolation` and `Time::GetStepAlpha`.
- Tests: the suites `Scene.Timing`, `Scene.Timing.Sweep` and `Physics.Interpolation`, and the metric `InterpolatedStepFrame100k` of the `Perf.Scene` suite.
- Settings and commands: the `Interpolation` field of the `Scene.Timing` section, set with `project.setSettings`; `play.state` and `physics.stats` report whether it is in effect.

## Further reading

- Glenn Fiedler, "Fix Your Timestep!", [gafferongames.com](https://gafferongames.com/post/fix_your_timestep/): the accumulator, the variable step and the blend between states (intermediate).
- Unity's manual page on the interpolation setting of a rigid body, docs.unity3d.com: the same choice in another engine (beginner).
- Strata's `Docs/DeveloperGuide.md`, section "Interpolation": the rules in the engine's own words, with measurements (advanced).
