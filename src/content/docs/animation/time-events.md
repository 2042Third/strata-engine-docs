---
id: animation/time-events
title: "Time, loops and events"
description: "How one playing state moves its playhead through a clip, across loops and backwards, and which events and exit times the move fires."
kind: internals
size: M
tracks: [E]
needs: [animation/state-machines]
time: 55
learn:
  - id: trace-playhead
    text: trace a playhead through a large backward step and list the events and exit times it fires
  - id: count-loops
    text: explain why Strata counts loops and keeps normalized time instead of keeping only the place in the loop
  - id: predict-exit
    text: predict the update in which an exit time fires on a looping state and on a state that does not loop
  - id: event-rules
    text: name the rules that decide which events fire, and the case where an event never fires
since: 0.3.0
status: final
---

A state machine decides which clip plays. Something must still move time forward inside that clip, and that is the job of `AnimatorInstance::AdvanceEntry`. The function takes one playing entry and the seconds this update adds, and it moves the entry's **playhead**, the position in seconds inside the clip. It wraps the playhead across the loop boundary in both directions and counts each crossing.

The function also keeps the normalized time and collects the events the playhead passed. The state machine then reads the normalized time to test its exit times, the points in the clip at which a transition may leave the state. This page does not dispatch events to listeners and does not blend poses: it only moves one playhead and reports what the move passed.

## The problem and how engines solve it

Take a walk clip that lasts 1 second. At 60 :term[frames per second]{id=frame-rate} each update adds about 0.0167 seconds, so a playhead that starts at 0 reaches 1 after 60 updates. Then it must return to the start. The usual first attempt is `time = fmod(time + seconds, duration)`, where `fmod` is the remainder of a division: it keeps the place in the loop and forgets how many loops passed.

Forgetting the count breaks two things. A transition may say "leave this state after 1.5 loops". Nothing in the place `0.5` tells you whether the clip is in its first loop or its second.

Events break too. A footstep at 0.9 s must sound once in the update that moves the playhead from 0.85 to 0.95. In the update that moves it from 0.95 to 0.05 the playhead jumped backwards in number, so a test of the form "is the event between the old and the new place" fails. The footstep at 0.9 is lost every loop.

A second mistake is to ask whether the playhead equals the event time. Time is a float and the update steps are arbitrary, so the playhead almost never lands exactly on 0.9. A test of `time == eventTime` never fires.

Engines solve this by treating the playhead as a window. The event fires if its time lies inside the stretch the playhead crossed in this update, and the stretch is split at the loop boundary. Strata also keeps a loop counter next to the place. The pair gives **normalized time**, the number of loops completed plus the place divided by the duration. A value of 1.5 means halfway through the second loop.

Engines differ in where an event lives. Unreal Engine stores such markers, which it calls notifies, inside the animation clip. Strata stores them on the controller's states, because glTF, the model format Strata imports, carries no events in its clips. A named moment that a state's clip passes is an **animation event** (also called a notify). The cost: the same clip used in two states needs its events written twice.

## The map

Three pieces take part. The Animation system runs the animators in parallel, in jobs of up to eight animators each. `AnimatorInstance::Advance` scales the update's time and calls `AdvanceEntry` for each playing entry, which is more than one while states fade. Then it tests the transitions of the state machine.

```mermaid caption="The animation system calls an animator's advance step, which calls the playhead walk for each playing entry. Events flow back to the system, which dispatches them after all poses. Normalized time flows to the transition test." alt="Boxes in a row. The animation system leads to the advance step. The advance step leads to the playhead walk, which leads to collected events and to normalized time. The collected events lead back to the Animation system for dispatch. The normalized time leads to the exit time test, which leads to a transition."
flowchart LR
    S[Animation system] --> A[AnimatorInstance::Advance]
    A --> E[AdvanceEntry per entry]
    E --> V[Collected events]
    E --> N[Normalized time]
    V --> D[Dispatched after all poses]
    N --> X[Exit time test] --> T[Transition]
```

## The contract

- **Time is the update's seconds times two speeds.** The animator's `Speed` and the state's speed multiply the delta time. Validation keeps a state's speed within -100 to 100. A negative speed plays the clip backwards. The reason: slow motion and reverse are properties of the animator and of the state, not of the clip.
- **A looping state wraps and counts.** A state that does not loop clamps at its ends and never counts a loop. Normalized time of such a state stops at 1 at the end, and at 0 at the start.
- **The window is half open.** Forwards the playhead passes events in (from, to]; backwards it passes events in [to, from). An event fires on the update that arrives at it and not again on the update that leaves. The reason: each event fires once per pass, with no gap and no double.
- **An event at time 0 fires at the start and once per loop.** At the start the window includes its own first point. Every wrap restarts a window that includes it again.
- **Only the current state's events fire.** States that fade out play their clips but fire nothing. The reason: two states cannot both claim a footstep.
- **Work per update is bounded.** At most four loops walk step by step; the rest is skipped by arithmetic. The reason: a pause of a minute must not cost a minute of loops.
- **This code only collects.** Events go to a list, and the Animation system dispatches them after all poses, on the :term[main thread]{id=main-thread}. Jobs write only their own animator's record, so the walk stays parallel and :term[deterministic]{id=determinism}.

## A toy version

The toy below has the whole idea in one place: a playhead with a place and a loop count, a window test, and a walk that stops at each boundary. It plays forwards and backwards, and its clip always loops.

:::question
The next fence uses `if`, loops, functions, :term[structs]{id=struct}, calls such as `events.size()`, and `std::vector`. If those are new, read [programming 1](../basics/programming-1.md), [programming 2](../basics/programming-2.md) and [programming 3](../basics/programming-3.md) first.
:::

The program plays four updates on a clip of 1 second with two events, one at 0.25 and one at 0.75. Look at how `Collect` picks the window and how `Advance` restarts the window after each crossing.

```cpp sketch="animation-time-events-toy.cpp"
// A toy playhead: it loops, counts the loops and collects the events it passes, forwards and backwards.
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <vector>

struct ToyEvent
{
	const char* Name = "";
	float Time = 0.0f;
};

struct ToyPlayhead
{
	float Duration = 1.0f;
	float Time = 0.0f;
	int64_t Loops = 0;
	bool Fresh = true; // nothing has played yet, so an event at time 0 is still to fire

	double GetNormalized() const { return static_cast<double>(Loops) + static_cast<double>(Time) / static_cast<double>(Duration); }
};

// Events in (from, to] going forwards and in [to, from) going backwards; includeFrom also takes an event at from.
static void Collect(const std::vector<ToyEvent>& events, float from, float to, bool includeFrom, std::vector<ToyEvent>& out)
{
	if (to >= from)
	{
		for (const ToyEvent& event : events)
			if ((event.Time > from || (includeFrom && event.Time == from)) && event.Time <= to)
				out.push_back(event);
	}
	else
	{
		for (size_t index = events.size(); index > 0; index--)
			if ((events[index - 1].Time < from || (includeFrom && events[index - 1].Time == from)) && events[index - 1].Time >= to)
				out.push_back(events[index - 1]);
	}
}

// One update: walk the playhead to the loop boundary, count the crossing, continue with what is left.
static void Advance(ToyPlayhead& playhead, float seconds, const std::vector<ToyEvent>& events, std::vector<ToyEvent>& out)
{
	float remaining = seconds;
	float position = playhead.Time;
	bool includeFrom = playhead.Fresh;
	while (remaining != 0.0f)
	{
		const float step = remaining > 0.0f ? std::min(remaining, playhead.Duration - position) : std::max(remaining, -position);
		Collect(events, position, position + step, includeFrom, out);
		position += step;
		remaining -= step;
		includeFrom = false;
		if (remaining > 0.0f || position >= playhead.Duration)
		{
			position = 0.0f;
			playhead.Loops++;
			includeFrom = true;
		}
		else if (remaining < 0.0f)
		{
			position = playhead.Duration;
			playhead.Loops--;
			includeFrom = true;
		}
	}
	playhead.Time = position;
	playhead.Fresh = false;
}

int main()
{
	const std::vector<ToyEvent> events = { { "StepLeft", 0.25f }, { "StepRight", 0.75f } };
	ToyPlayhead playhead;
	const float updates[] = { 0.875f, 0.5f, 2.0f, -1.75f };
	for (const float seconds : updates)
	{
		std::vector<ToyEvent> fired;
		Advance(playhead, seconds, events, fired);
		std::printf("advance %6.3f: time %.3f loops %lld normalized %.3f events:", seconds, playhead.Time, static_cast<long long>(playhead.Loops), playhead.GetNormalized());
		for (const ToyEvent& event : fired)
			std::printf(" %s", event.Name);
		std::printf("\n");
	}
	return 0;
}
```

```text output-of="animation-time-events-toy.cpp"
advance  0.875: time 0.875 loops 0 normalized 0.875 events: StepLeft StepRight
advance  0.500: time 0.375 loops 1 normalized 1.375 events: StepLeft
advance  2.000: time 0.375 loops 3 normalized 3.375 events: StepRight StepLeft StepRight StepLeft
advance -1.750: time 0.625 loops 1 normalized 1.625 events: StepLeft StepRight StepLeft StepRight
```

1. **Lines 13-21:** The playhead keeps the place, the loop count and a flag for a fresh start, and computes normalized time from them.
2. **Lines 23-38:** `Collect` is the window: forwards in (from, to], backwards in [to, from), with the start point included only when asked.
3. **Lines 46-65:** The walk stops at each boundary, counts the crossing and restarts the window including its first point.
4. **Lines 70-83:** `main` plays four updates and prints the place, the loop count, normalized time and the events.

The first update starts fresh, so the window takes both events. The second crosses a boundary and passes only the next loop's `StepLeft`. The third spends two whole loops in one update. The fourth runs backwards over three passes through the clip and fires four events in reverse order. Normalized time ends at 1.625, which is one loop plus 0.625 of the next.

## The real code

The real function does what the toy does, with three additions: it clamps clips that do not loop, it skips loops beyond four, and it keeps the normalized time in double precision. The page reads it in three parts. The first part prepares the entry and defines `fire`, the window test. It also handles the cases that have no walk at all.

```cpp src="Strata/src/Strata/Animation/AnimatorInstance.cpp#L458-L503"
const AnimatorClip clip = GetClip(assets, entry.State);
const float duration = clip.Clip ? clip.Clip->GetDuration() : 0.0f;
if (!(duration > 0.0f))
{
	// Nothing to play (no clip, or a single pose): it is done at once.
	entry.Time = 0.0f;
	entry.Loops = 0;
	entry.Normalized = 1.0;
	return 0;
}
const bool loop = IsStateLooping(assets, settings, entry.State);
const float start = entry.Time;
const bool fresh = entry.Normalized == 0.0 && entry.Time == 0.0f;

// Events of the state the animator is in, in the order the playhead passes them (only controller states have events).
const std::vector<AnimationEvent>* events = nullptr;
if (fireEvents && entry.State != c_ClipState && assets.Controller && entry.State < assets.Controller->GetStates().size())
{
	events = &assets.Controller->GetStates()[entry.State].Events;
	if (events->empty())
		events = nullptr;
}
auto fire = [&](float from, float to, bool includeFrom)
{
	// Events in (from, to] forward or [to, from) backward; includeFrom also takes an event at `from` itself.
	if (!events)
		return;
	if (to >= from)
	{
		for (uint32_t index = 0; index < events->size(); index++)
		{
			const float time = (*events)[index].Time;
			if ((time > from || (includeFrom && time == from)) && time <= to)
				outEvents.push_back(AnimatorFiredEvent { entry.State, index, time });
		}
	}
	else
	{
		for (uint32_t index = static_cast<uint32_t>(events->size()); index > 0; index--)
		{
			const float time = (*events)[index - 1].Time;
			if ((time < from || (includeFrom && time == from)) && time >= to)
				outEvents.push_back(AnimatorFiredEvent { entry.State, index - 1, time });
		}
	}
};
```

1. **Lines 459-467:** A clip with no duration is done at once, with normalized time 1; there is nothing to walk.
2. **Lines 468-470:** The state's loop flag, the start place, and `fresh`: nothing has played yet, so an event at time 0 is still to fire.
3. **Lines 473-479:** Only the controller state's events count, and only when the caller asks for them; a plain clip has none.
4. **Lines 480-503:** `fire` is the window test, forwards in time order and backwards in reverse order, with the start of the window included only when asked.

The next part is the cap. A state that loops enters a long step; if the step is longer than four durations, the code skips the first part of it by arithmetic. It counts the whole loops skipped and lands at the right place in the clip. Look at how the events of the skipped part never fire.

```cpp src="Strata/src/Strata/Animation/AnimatorInstance.cpp#L505-L540"
if (!loop)
{
	const float end = std::clamp(start + seconds, 0.0f, duration);
	fire(start, end, fresh);
	entry.Time = end;
	entry.Normalized = end / duration;
	return 0;
}

// The passes through the clip this update makes, the earliest skipped beyond c_MaxEventLoops loops. Every crossing of
// the loop boundary is counted where the playhead makes it.
int64_t crossings = 0;
float remaining = seconds;
float position = start;
bool includeFrom = fresh;
const float maxSpan = duration * static_cast<float>(c_MaxEventLoops);
if (std::abs(remaining) > maxSpan)
{
	const float skipped = std::abs(remaining) - maxSpan;
	const float skippedInClip = std::fmod(skipped, duration);
	// The whole loops in what is skipped (what fmod leaves out is a whole number of durations, up to rounding), then the
	// part of a loop.
	const int64_t wholeLoops = static_cast<int64_t>(std::round((skipped - skippedInClip) / duration));
	if (remaining > 0.0f)
	{
		crossings += wholeLoops + (position + skippedInClip >= duration ? 1 : 0);
		position = std::fmod(position + skippedInClip, duration);
	}
	else
	{
		crossings -= wholeLoops + (position - skippedInClip < 0.0f ? 1 : 0);
		position = std::fmod(position - skippedInClip + duration, duration);
	}
	remaining = remaining > 0.0f ? maxSpan : -maxSpan;
	includeFrom = false;
}
```

1. **Lines 505-512:** A state that does not loop clamps at both ends, fires its window once and counts no loop.
2. **Lines 516-520:** The crossing counter, the seconds left, the place, and the cap of four durations.
3. **Lines 521-538:** A longer step first skips whole loops by arithmetic, counts them, moves the place by the remainder, and leaves four durations to walk.
4. **Lines 539-540:** The skipped part fires nothing, and the walk does not include its start point.

The last part is the walk and the result. Look at how the two directions end differently when a step lands exactly on a boundary.

```cpp src="Strata/src/Strata/Animation/AnimatorInstance.cpp#L541-L584"
while (remaining != 0.0f)
{
	if (remaining > 0.0f)
	{
		const float step = std::min(remaining, duration - position);
		fire(position, position + step, includeFrom);
		position += step;
		remaining -= step;
		if (remaining > 0.0f || position >= duration)
		{
			// Back to the start: an event at time 0 fires again.
			position = 0.0f;
			includeFrom = true;
			crossings++;
			if (remaining <= 0.0f)
				break;
			continue;
		}
	}
	else
	{
		const float step = std::max(remaining, -position);
		fire(position, position + step, includeFrom);
		position += step;
		remaining -= step;
		if (remaining < 0.0f || position <= 0.0f)
		{
			position = duration;
			includeFrom = true;
			// Ending exactly at the start is no crossing (the playhead stays there); going on past it is.
			if (remaining >= 0.0f)
				break;
			crossings--;
			continue;
		}
	}
	includeFrom = false;
}
// Ending exactly on a loop boundary leaves the playhead at the start.
entry.Time = position >= duration ? 0.0f : position;
entry.Loops += crossings;
// Normalized time counts loops forward; playing backwards before the first loop keeps it at the start.
entry.Normalized = std::max(0.0, static_cast<double>(entry.Loops) + static_cast<double>(entry.Time) / static_cast<double>(duration));
return crossings;
```

1. **Lines 543-558:** Forwards, the step stops at the boundary, `fire` runs, and a wrap counts a crossing and includes the start point again.
2. **Lines 560-575:** Backwards the same, but ending exactly at the start counts no crossing and leaves the loop.
3. **Line 577:** A step that stopped inside the clip does not include its start point.
4. **Lines 580-583:** The place, the loop count and normalized time in double, never below 0.

Three differences from the toy matter. The real code works on one entry at a time, and the caller passes `fireEvents` true only for the current entry. A clip with no duration is done at once, with normalized time 1.

The result is `Loops` plus the place over the duration, in double, and it never goes below 0. As in the toy, a forward step that ends exactly on the boundary counts a crossing, while a backward step that ends exactly at the start does not.

:::example
**A backward step across three passes.** A state loops, its clip lasts 1 s, and it has events at 0.25 and 0.75. The playhead stands at 0.375 in the fourth pass, so `Loops` is 3. An update adds -1.75 s.

1. From 0.375 down to 0: the window [0, 0.375) holds 0.25. The playhead wraps to 1 and `Loops` is 2.
2. From 1 down to 0: the window [0, 1] holds 0.75 and then 0.25, in that order. The playhead wraps to 1 and `Loops` is 1.
3. From 1 down to 0.625, which uses the last 0.375 s: the window [0.625, 1] holds 0.75.

The update fires 0.25, 0.75, 0.25, 0.75 and ends at 0.625 with `Loops` 1, so normalized time is 1.625. Check it: 3.375 - 1.75 = 1.625.
:::

```mermaid caption="The three passes of the backward step. Each pass lists the window it covers and the events inside it, and the loop count falls from 3 to 1." alt="Four boxes in a row from left to right. The first reads start at 0.375, loops 3. The second reads window 0 to 0.375, event 0.25, loops 2. The third reads window 0 to 1, events 0.75 then 0.25, loops 1. The fourth reads window 0.625 to 1, event 0.75, end at loops 1."
flowchart LR
    A["start 0.375, loops 3"] --> B["[0, 0.375): 0.25, loops 2"]
    B --> C["[0, 1]: 0.75, 0.25, loops 1"]
    C --> D["[0.625, 1]: 0.75, end, loops 1"]
```

:::example
**A step of ten loops.** The clip lasts 1 s and the playhead stands at 0. An update adds 10.25 s. The cap is 4 s, so 6.25 s are skipped. That holds 6 whole loops and 0.25 s of a seventh, so `Loops` becomes 6 and the playhead moves to 0.25.

The walk then covers 4 s from 0.25 to 4.25: four crossings, `Loops` 10, place 0.25. Only the last 4 s fire events. With the two events above that is eight events, where a full walk would fire twenty-one.
:::

### Exit times

The state machine reads normalized time once per update, after all playheads moved. This is the test again, in the code that calls `AdvanceEntry`.

```cpp src="Strata/src/Strata/Animation/AnimatorInstance.cpp#L732-L745"
const bool looping = IsStateLooping(assets, settings, playing.State);
const double normalized = playing.Normalized;
auto exitReached = [&](const AnimationTransition& transition)
{
	if (!transition.ExitTime)
		return true;
	const double exitTime = *transition.ExitTime;
	if (looping && exitTime < 1.0)
	{
		// Every loop at that point: the update passed exitTime + k for some whole k.
		return std::floor(normalized - exitTime) > std::floor(previousNormalized - exitTime) || (previousNormalized == 0.0 && normalized >= exitTime && exitTime == 0.0);
	}
	return normalized >= exitTime;
};
```

1. **Lines 736-737:** A transition without an exit time is always ready.
2. **Lines 739-742:** A looping state with an exit time below 1 is ready when the whole number of `normalized - exitTime` rose in this update.
3. **Line 744:** Any other state is ready once the normalized time reaches the exit time.

An **exit time** is the normalized time a transition waits for before it may fire. On a state that does not loop, or with an exit time of 1 or more, the test is plain: the normalized time has reached it. On a looping state with an exit time below 1, the transition fires at that point of every loop: the test asks whether the update crossed `exitTime + k` for some whole `k`.

Take exit time 0.4. The test fires in the update that carries the normalized time across 0.4, then across 1.4, then across 2.4. The code also lets an exit time of exactly 0 fire in the first update.

```mermaid caption="Normalized time from 0 to 3 with exit time 0.4. On a looping state the transition may fire at 0.4, 1.4 and 2.4, once per loop. Loop boundaries stand at 1, 2 and 3." alt="A line of points from left to right. Zero leads to exit at 0.4, then boundary 1, exit at 1.4, boundary 2, exit at 2.4, boundary 3."
flowchart LR
    Z[0] --> E1[exit 0.4] --> B1[boundary 1] --> E2[exit 1.4] --> B2[boundary 2] --> E3[exit 2.4] --> B3[boundary 3]
```

The transition also needs its conditions. A looping state whose condition turns true at 0.7 misses the exit at 0.4 and waits for 1.4. A state that does not loop fires in the first update after the condition holds, because its test is "reached", and it stays reached.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Events stored in clips | Unreal Engine (notifies) | Events travel with the clip into every state | A clip format with events: glTF has none, so the :term[importer]{id=importer} would invent one |
| Only the place in the loop (`fmod`) | Simple first attempts, as shown above | One number and no counter | Exit times above 1 and events at the boundary |
| Step through every loop | The toy | No arithmetic skip | Work that grows with the update's length |
| Fire events of fading states too | No engine is named here | Footsteps from both walks | Doubled events during every blend |
| Event times counted in frames | No engine is named here | A simple test | Events that depend on the frame rate |

## How it is tested

Four tests of `StrataTests/src/Animation/AnimatorTests.cpp` check this page, in the suites `Animation.Sampling` and `Animation.StateMachine`. Run one with `StrataTests.exe --test-case="Events fire once*"`, or all animation tests with `StrataTests.exe --test-suite="Animation*"`.

- `Looping clips wrap and other clips stop at their end`: 2.25 s on a 1 s clip gives place 0.25 and normalized time 2.25; a clip that does not loop stops at 1.0, and backwards at 0.
- `Events fire once each when the playhead passes them, in order, also across a loop boundary`: two loops in one update fire four events in the order passed, landing on an event fires it once, and backwards the order reverses.
- `An event at the start of a looping clip fires when it starts and once per loop`: the event at 0 fires at the start, at the wrap, and a fading state fires none.
- `Exit times fire in the update that reaches them, at every loop of a looping state`: it holds the cases of waiting for a condition, a missed exit time that waits one loop, a state that does not loop, and an exit time of 2.

## Changing it safely

- **Keep the windows half open.** A closed window fires twice at a boundary. The four tests above fail when you change one end.
- **Keep every crossing counted where the playhead makes it.** Root motion reads the same crossing count to split its travel across loops. A wrong count moves characters.
- **Keep normalized time in double.** After many loops a float loses the fraction, and an exit time would fire late. The numbers are in [numbers](../basics/numbers.md).
- **Add events through the controller.** Validation refuses a name that is not valid, a time that is negative or not finite, and more than 256 events per state. It also sorts events by time, so `fire` can rely on the order.
- **Change both directions together.** A fix of the forward walk needs a mirror in the backward walk, with a test for each.

An event whose time lies beyond its clip's duration never fires, and nothing warns: validation checks only that the time is not negative. A clip that does not loop stops at its duration, and a looping one wraps there, so the window never reaches the event.

## Summary

- A playhead is the position in seconds inside a clip; one update moves it by the delta time times the animator's speed times the state's speed.
- Strata counts loops and keeps normalized time because the place in the loop alone loses exit times above 1 and events at the boundary.
- On a looping state an exit time below 1 fires at that point of every loop; otherwise it fires once the normalized time reaches it.
- Events fire in the window (from, to] forwards and [to, from) backwards, only for the current state, at most four loops per update; an event past the duration never fires.

## Check yourself

1. A clip lasts 2 s and has an event at 1.5 s. The playhead moves from 1.25 s to 1.75 s. Does the event fire?

   :::answer{tests="event-rules"}
   Yes. The window (1.25, 1.75] holds 1.5. A test of `time == 1.5` would not fire, because the playhead never lands on it.
   :::

2. A looping state lasts 1 s and the exit time is 0.4. The normalized time moves from 0.9 to 1.5 in one update. Does the transition fire when its conditions hold?

   :::answer{tests="predict-exit"}
   Yes. The update crossed 1.4, so `floor(1.5 - 0.4)` is 1 and `floor(0.9 - 0.4)` is 0.
   :::

3. Why does Strata keep `Loops` next to the place instead of calling `fmod`?

   :::answer{tests="count-loops"}
   The place alone cannot tell the first loop from the second, so an exit time of 1.5 and events at the boundary would fail. The count gives normalized time.
   :::

4. A state has events at 0.25 and 0.75 on a 1 s clip. The playhead at 0.5 moves back by 0.5 s. Which events fire, in which order?

   :::answer{tests="trace-playhead"}
   The window [0, 0.5) holds only 0.25, so the update fires 0.25. Then the playhead stands exactly at the start, which is no crossing.
   :::

## Exercises

1. **Basic.** Predict, before you run it, the six lines that `animation-time-events-exit.cpp` prints for exit time 0.5 and a step of 0.375. Then run it.

   :::answer[Worked solution]{tests="predict-exit" solution="sketches/animation-time-events-exit.cpp"}
   Normalized time grows 0.375, 0.75, 1.125, 1.5, 1.875, 2.25. A looping state fires when `floor(current - 0.5)` rises: at update 2 (from -1 to 0) and at update 4 (from 0 to 1). A state that does not loop shows 1 from update 2 on, because the test is "reached".

   ```cpp sketch="animation-time-events-exit.cpp"
   // The exit test alone: does the update that moved the normalized time from previous to current reach the exit time?
   #include <cmath>
   #include <cstdio>

   static bool ExitReached(bool looping, double exitTime, double previous, double current)
   {
   	if (looping && exitTime < 1.0)
   		return std::floor(current - exitTime) > std::floor(previous - exitTime);
   	return current >= exitTime;
   }

   int main()
   {
   	const double exitTime = 0.5;
   	const double step = 0.375; // a binary fraction, so the sums are exact
   	double previous = 0.0;
   	for (int update = 1; update <= 6; update++)
   	{
   		const double current = previous + step;
   		std::printf("update %d: normalized %.3f looping %d not looping %d\n", update, current, ExitReached(true, exitTime, previous, current) ? 1 : 0,
   			ExitReached(false, exitTime, previous, current) ? 1 : 0);
   		previous = current;
   	}
   	return 0;
   }
   ```

   ```text output-of="animation-time-events-exit.cpp"
   update 1: normalized 0.375 looping 0 not looping 0
   update 2: normalized 0.750 looping 1 not looping 1
   update 3: normalized 1.125 looping 0 not looping 1
   update 4: normalized 1.500 looping 1 not looping 1
   update 5: normalized 1.875 looping 0 not looping 1
   update 6: normalized 2.250 looping 0 not looping 1
   ```

   1. **Lines 5-10:** The exit test: a looping state with an exit time below 1 asks whether the whole number rose; any other state asks whether the time reached it.
   2. **Line 15:** A step of 0.375 is a binary fraction, so each sum is exact.
   3. **Lines 19-21:** Each update prints both answers for the same move of the normalized time.
   :::

2. **Medium.** The toy clip lasts 1 s with events at 0.25 and 0.75, and the playhead stands at 0.5 with `Loops` 0. Trace an update of -0.75 s in the real engine. Give the events, the place and the normalized time.

   :::answer[Worked solution]{tests="trace-playhead"}
   Window [0, 0.5): 0.25 fires and the playhead reaches the start with 0.25 s left. It wraps to 1 and the loop count falls to -1. Window [0.75, 1] fires 0.75. The place is 0.75. The sum is -0.25, so the real engine's normalized time is 0, because it never goes below 0.
   :::

3. **Hard.** Trace it yourself: build the engine from source, set a breakpoint on the line in `AdvanceEntry` that appends to `outEvents`, and run `Events fire once each when the playhead passes them, in order, also across a loop boundary`. Write down each update's window and events.

   :::answer[Worked solution]{tests="trace-playhead,event-rules"}
   The function is `AnimatorInstance::AdvanceEntry` in `Strata/src/Strata/Animation/AnimatorInstance.cpp`, and the :term[lambda]{id=lambda} is `fire`. The test advances 0.125 (no event), 0.75 (0.25 and 0.75), 0.5 (0.25), 2.0 (0.75, 0.25, 0.75, 0.25), 0.375 (0.75), 0.125 (none), and then -0.75 backwards (0.75, 0.25).
   :::

## Where it lives in Strata

- `Strata/src/Strata/Animation/AnimatorInstance.cpp`: `AdvanceEntry` and `Advance`, with the exit test.
- `Strata/src/Strata/Animation/AnimatorInstance.h`: `c_MaxEventLoops`.
- `Strata/src/Strata/Animation/AnimationController.cpp`: the validation of events.
- `StrataTests/src/Animation/AnimatorTests.cpp`: the four tests.

## Further reading

- Unreal Engine documentation, "Animation Notifies" (intermediate): how another engine stores events in clips.
- Jason Gregory, "Game Engine Architecture", the chapter on animation systems (advanced): time scaling and events in clip playback.
