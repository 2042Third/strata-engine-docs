---
id: animation/state-machines
title: "State machines"
description: "How an animation controller chooses which clip plays: parameters, states, transitions, Any State and triggers, from the document to the update that fires."
kind: internals
size: L
tracks: [E]
needs: [animation/clips]
time: 75
learn:
  - id: read-document
    text: name the parameters, states and transitions of a controller document and the limits that validate it
  - id: predict-states
    text: predict, update by update, which state an animator is in
  - id: triggers
    text: explain how a transition consumes a trigger and why a trigger can stay set
  - id: commands
    text: explain what Play, CrossFade, PlayClip and the parameter setters do, also while a controller loads
  - id: trace-update
    text: trace the update in which a transition consumes a trigger
since: 0.3.0
status: final
---

A character does not play one clip for ever: it stands, walks, runs and jumps as the game changes around it. The
**animation controller** is the asset that decides which clip plays and when the animator switches to another. It
holds named values the game sets (the parameters), the states that play clips, and the rules for moving between
states. One `AnimatorInstance` runs a controller for one animator, in plain data without a scene: a test or a preview
can run it too. The controller never draws or moves anything; it only chooses what plays, and the blending of the
result belongs to [Blending](../animation/blending.md).

## The problem and how engines solve it

Take the robot of the third-person sample. While you hold the stick it walks, with a stronger push it runs, and when
you press the jump button it leaves the ground. Which clip plays must follow the game: its speed, whether it stands on
the ground, a button that was pressed. A clip itself knows nothing of this. Something has to look at the game's
numbers every update and pick the clip.

The first answer is a hand-written decision in a game script: an `if` per case that starts a clip. It works for two
clips. With six clips the decisions grow into a tangle: running must not start while the jump plays, the jump may
start from every clip, and each rule needs its own flag. Every new clip touches many old lines, and a designer who
wants to change the order of events must change code.

The second answer is to move the decisions into data. A **state** is a clip with its settings: its speed, whether it
loops, and the events it raises. The animator is in exactly one state at a time, and the clip of that state plays.

A **transition** is a rule for leaving one state for another: it names the two states and the conditions under which it
fires. The game writes numbers into the parameters, and the machine reads them. A game script now says "Speed is 3.2"
and never says which clip plays.

Unity's animation system, Mecanim, uses this model, and Strata's is close to it. Strata's has parameters of three types,
transitions that wait for an exit time, triggers, and a source called Any State. A transition from **Any State** is a
rule that applies whatever state the animator is in: a jump may start from standing, walking or running, and one rule
says so once instead of three. Unreal Engine's animation blueprints, Esoterica and Morpheme put state machines inside
a larger graph: a machine is one node among blend nodes, and its result feeds other nodes. That is more powerful and
much larger to build, to show in an editor and to test.

Strata chooses the smaller model: one flat machine for each animator. The transitions from Any State are tried
first, then the transitions of the current state, and at most one transition fires in an update. The price is that
Strata has no graph: a wave on the upper body while the legs walk has no place in this model, and
[Limits](../animation/limits.md) lists what to do instead. The gain is a model a reader can run by hand, and that is
what this page teaches.

## The map

The data lives in one file and runs in another. `Strata/src/Strata/Animation/AnimationController.h` and its source
hold the asset: the data, the validation and the :term[JSON]{id=json} reader and writer. `Strata/src/Strata/Animation/AnimatorInstance.cpp`
holds the live state of one animator: its parameters, the states that play, and the update that runs the machine. The
Animation scene system in `Strata/src/Strata/Animation/AnimationSystem.cpp` owns one record per animator entity and
calls `Advance` once per update, in a parallel job that writes only that animator's record ([The Animation system](system.md) shows the jobs).
Scripts and editor commands reach the instance through the same system.

```mermaid caption="The asset is validated once and shared; each animator entity has its own instance, which the Animation scene system advances every update." alt="A document file is read into a validated controller asset. The Animation scene system holds one instance per animator and calls its advance function each update. Scripts and commands call the system to set parameters and play states."
flowchart LR
	Doc[".stanimator document"] -->|"DataFromJson, Create"| Ctl["AnimationController (shared, read only)"]
	Ctl --> Inst["AnimatorInstance (one per animator)"]
	Sys["AnimationSystem"] -->|"Advance each update"| Inst
	Scripts["Scripts and commands"] -->|"SetFloat, SetTrigger, Play"| Sys
	Inst --> Pose["Playing entries, then the pose"]
```

The controller is shared and never changes after it is made: many robots can use one controller, each with their own
instance. The instance owns everything that changes: the parameter values, the current state and the fade. That split
is why a reloaded controller can replace the shared object while each instance keeps its values, as you will see in
the section on reloading.

## The contract

Callers of the controller and the instance may rely on these rules, and must respect them.

- Only plain data builds a controller. `AnimationController::Create` validates all of it and returns no controller and
  an error text for bad data, so a document that loads is a document that runs.
- The machine runs after the playhead moved. An update first advances the time of the playing states, then tests
  transitions once. The state tested is the newest one, also during a fade.
- At most one transition fires in an update, and Any State comes first. Two transitions whose conditions both hold do
  not both fire: the first in order wins.
- A transition that fires consumes the triggers it tests. A trigger tested by a transition that did not fire stays
  set.
- Commands arrive between updates on the :term[main thread]{id=main-thread} and never wait for a load; the rule box below gives the reason.

:::rule
Script commands never block on loading. When the controller is still loading, `Play`, `CrossFade` and the commands that
set parameters store the request and succeed; the next update after the load applies them. A script that waited for the load
would stall the frame: read [Loading without stalling](../assets/loading.md).
:::

## The document

A controller is stored as a **`.stanimator`** file: a JSON document that declares the parameters, the states and the
transitions. A file that stores the controller as text is the asset's source, and the handle of the file is the
reference games use ([Handles and meta files](../assets/handles-meta.md)). JSON is the format of nested named values
that [Data formats](../basics/data-formats.md) taught.

The document has two top-level keys. `Strata` names the format and version. `AnimationController` holds
`Parameters`, `States`, `DefaultState` and `Transitions`. A parameter has a `Name`, a `Type` of `Float`, `Bool` or
`Trigger`, and, unless it is a trigger, a `Default` (a trigger starts cleared). A state is named, and may have a clip (a handle, or null for none), a `Speed`, `Loop` and
`Events`.

The robot's controller is the example. This is its Walk state.

```json src="Samples/ThirdPerson/Assets/Animations/Robot.stanimator#L36-L51"
{
	"Clip": "57D5825B3AB8DCFD",
	"Events": [
		{
			"Name": "Footstep",
			"Time": 0.019999999552965164
		},
		{
			"Name": "Footstep",
			"Time": 0.5
		}
	],
	"Loop": true,
	"Name": "Walk",
	"Speed": 1.0
},
```

1. **Line 37:** the clip is named by its handle, the number of the clip asset, never by a path.
2. **Lines 38–47:** both events are kept in time order; `Create` sorts them by time.
3. **Line 48:** a looping state starts again when its clip ends.
4. **Line 50:** the speed multiplies the time of this state only.

Walk plays one clip, at normal speed, looping. Its two `Footstep` events sit at 0.02 and 0.5 seconds into the clip:
a script listens for the name and plays a sound (the events themselves belong to
[Time and events](../animation/time-events.md)). Next come the first two transitions of the robot.

```json src="Samples/ThirdPerson/Assets/Animations/Robot.stanimator#L91-L116"
{
	"AnyState": true,
	"CanTransitionToSelf": true,
	"Conditions": [
		{
			"Mode": "Set",
			"Parameter": "Jump"
		}
	],
	"Duration": 0.10000000149011612,
	"ExitTime": null,
	"To": "Jump"
},
{
	"Conditions": [
		{
			"Mode": "Greater",
			"Parameter": "Speed",
			"Threshold": 0.10000000149011612
		}
	],
	"Duration": 0.15000000596046448,
	"ExitTime": null,
	"From": "Idle",
	"To": "Walk"
},
```

1. **Line 92:** a transition from Any State has this flag and no `From`.
2. **Line 93:** a `Jump` trigger set while the jump plays restarts the jump.
3. **Lines 106–110:** one condition: the float `Speed` must be above the threshold.
4. **Line 112:** the cross-fade lasts 0.15 seconds.
5. **Line 113:** null means no exit time: the transition does not wait.

The first has `AnyState` true and no `From`: it applies in every state. It tests the trigger `Jump` and leads to the
state `Jump` over a 0.1 second cross-fade. `CanTransitionToSelf` is true, so a `Jump` trigger set again while the jump plays
restarts it. The second starts in Idle and fires when `Speed` is above 0.1. Its `ExitTime` is null: it does not wait
for the clip to reach a point, and the fade lasts 0.15 seconds.

The whole robot controller has five parameters: `Speed` (float, default 0), `Grounded` (`Bool`, default true) and the
triggers `Jump`, `Wave` and `Dance`. It has six states and fourteen transitions. The diagram shows them as the
machine sees them.

```mermaid caption="The robot's controller. Any State leads to Jump on the Jump trigger; the other arrows leave the state they start at." alt="Six states: Idle, Walk, Run, Jump, Wave and Dance. Idle leads to Walk, Wave and Dance. Walk leads to Run and Idle, Run to Walk. Jump leads to Walk and Idle after an exit time. Wave leads to Walk, Idle and Dance, and Dance to Walk and Wave."
stateDiagram-v2
	[*] --> Idle
	Idle --> Walk: Speed above 0.1
	Idle --> Wave: Wave set
	Idle --> Dance: Dance set
	Walk --> Run: Speed above 4.5
	Walk --> Idle: Speed below 0.1
	Run --> Walk: Speed below 4.5
	Jump --> Walk: exit 0.4, grounded, Speed above 0.1
	Jump --> Idle: exit 0.4, grounded, Speed below 0.1
	Wave --> Walk: Speed above 0.1
	Wave --> Idle: exit 0.92
	Wave --> Dance: Dance set
	Dance --> Walk: Speed above 0.1
	Dance --> Wave: Wave set
```

The picture omits the arrow of Any State (from every state to Jump on the Jump trigger), so that the other arrows
stay clear. The Asset tab of the editor shows the same controller as three tables.

::figure{id=robot-asset-tab}

Read the first table as the parameters, the second as states with their clips, and the third as the transitions with
their conditions, exit times and fades. Game makers edit these tables, and [Animation](../make/animation.md) shows how.

### What the machine checks when it loads

`AnimationController::Create` refuses a controller that breaks a limit or a rule, and says why.

| What | Limit or rule |
| --- | --- |
| Parameters | At most 256, unique names of 1 to 256 characters that can be shown, finite defaults |
| States | At least 1 and at most 1,024, unique names, a speed from -100 to 100, a default state that exists |
| Events | At most 256 per state, named, with a time of 0 seconds or more |
| Transitions | At most 4,096, both ends exist, at most 16 conditions, a fade of 0 to 60 seconds, an exit time of 0 or more |
| Conditions | The parameter exists, its type matches the mode, the threshold is finite |

A condition's mode must fit its parameter: `Greater` and `Less` test floats, `True` and `False` test `Bool` values, and `Set`
tests triggers. `Create` also sorts each state's events by time, and keeps events of the same time in their order, so
the update can walk them in order. A controller that fails any check never reaches an animator: the Animation scene system logs a warning with the reason once, and the animator plays the clip of its component instead. A limit is therefore a property of the file and never a surprise in play.

## How an update picks a state

Before reading the engine's code, run a machine by hand. Use the robot with its default values: `Speed` 0 and
`Grounded` true. The animator starts in Idle. Each row is one update, in which a script has set the values shown.

| Update | Values set before it | State after it | Why |
| --- | --- | --- | --- |
| 1 | none | Idle | Any State: `Jump` is not set. Idle: `Speed` 0 is not above 0.1 |
| 2 | `Speed` 3 | Walk | Idle to Walk fires: 3 is above 0.1 |
| 3 | `Speed` 5 | Run | Walk to Run fires: 5 is above 4.5 |
| 4 | `Jump` set | Jump | Any State comes first, and consumes `Jump` |
| 5 | none | Jump | Jump waits for its exit time: 0.4 of its clip must have played |

Update 3 shows the rule of one transition per update. Suppose a script sets `Speed` to 5 while the robot is still in Idle.
Idle to Walk fires, and the robot is in Walk after that update, not in Run. Walk to Run fires one update later.

The fade that starts at update 2 is still running when update 3 fires. The machine tests the newest state, Walk, and
not the state that fades out.

:::example
A jump in the air with a wave pressed at the same time shows both priority and consumption. The robot walks with
`Speed` 3. In one update a script sets both `Jump` and `Wave`. Any State is tried first: Any State to Jump has the
condition `Jump` set, so it fires and consumes `Jump`. The Walk transitions are never tried in that update, and
`Wave` stays set, because no transition that fired tested it.

The robot lands at update 30 with `Speed` 0 and `Grounded` true. Jump to Idle fires at its exit time. The next
update tries Idle's transitions in document order: Walk, Wave, Dance. The Wave transition sees `Wave` still set and
fires.

The robot waves, although the button was pressed a second ago in the air. A trigger is a request that waits for the
first transition that tests it and can fire. If the game wants a request to expire, it clears the trigger itself.
:::

The robot's scripts use exactly this: `Speed` and `Grounded` are written every frame by `ThirdPersonPlayer`, and the
three triggers are set by key presses and menu logic. The script side is in [Animation](../make/animation.md).

## A toy version

The toy keeps the idea and drops the rest: two states, one float parameter, and two transitions that test it. There
are no triggers, no exit times and no fades. An update looks through the transitions that leave the current state, and
the first whose condition holds fires.

```cpp sketch="animation-state-machines-toy.cpp"
// A toy state machine: two states, one float parameter, two transitions. One update checks the current state's
// transitions in order, and the first whose condition holds fires; at most one fires per update.
#include <cstddef>
#include <cstdio>
#include <string>
#include <utility>
#include <vector>

namespace
{

	enum class Mode { Greater, Less };

	struct Transition
	{
		size_t From = 0;
		size_t To = 0;
		Mode Test = Mode::Greater;
		float Threshold = 0.0f;
	};

	class ToyMachine
	{
	public:
		ToyMachine(std::vector<std::string> states, std::vector<Transition> transitions)
			: m_States(std::move(states)), m_Transitions(std::move(transitions))
		{
		}

		void Update(float speed)
		{
			for (const Transition& transition : m_Transitions)
			{
				if (transition.From != m_Current)
					continue;
				const bool holds = transition.Test == Mode::Greater ? speed > transition.Threshold : speed < transition.Threshold;
				if (!holds)
					continue;
				m_Current = transition.To;
				return;
			}
		}

		const std::string& GetCurrentName() const { return m_States[m_Current]; }

	private:
		std::vector<std::string> m_States;
		std::vector<Transition> m_Transitions;
		size_t m_Current = 0;
	};

}

int main()
{
	ToyMachine machine({ "Idle", "Walk" }, { { 0, 1, Mode::Greater, 0.1f }, { 1, 0, Mode::Less, 0.1f } });
	const float speeds[] = { 0.0f, 0.05f, 2.0f, 2.0f, 0.1f, 0.08f };
	int update = 1;
	for (const float speed : speeds)
	{
		machine.Update(speed);
		std::printf("update %d: Speed %.2f -> %s\n", update++, speed, machine.GetCurrentName().c_str());
	}
	return 0;
}
```

```text output-of="animation-state-machines-toy.cpp"
update 1: Speed 0.00 -> Idle
update 2: Speed 0.05 -> Idle
update 3: Speed 2.00 -> Walk
update 4: Speed 2.00 -> Walk
update 5: Speed 0.10 -> Walk
update 6: Speed 0.08 -> Idle
```

1. **Lines 34–35:** transitions that leave other states are skipped.
2. **Line 36:** the strict comparison: a value equal to the threshold does not hold.
3. **Lines 39–40:** the first transition that holds fires, and the update ends.
4. **Line 57:** the speed 0.1 sits exactly on the threshold of both transitions.

Look at update 5: `Speed` is exactly 0.1, and Walk to Idle needs it below 0.1, so the animator stays in Walk. At
update 6 it is 0.08 and Idle returns. The same test with `Greater` and `Less` is in the engine, with the same strict
comparison. Everything below is what a real animator needs on top of this: transitions from any state, a cheap way
to find a state's transitions, triggers, exit times, fades, loading and errors.

## The real code

### Grouping transitions by their source state

A state's transitions must be found fast, in document order, each update. Scanning all 4,096 possible transitions
would waste work. `Create` groups them with a counting sort. The result is a layout known as compressed sparse row: one array of
transition indices ordered by source state, and one array that says where each state's run starts
([Data structures](../basics/data-structures.md) shows prefix sums).

By hand with the robot: its 13 transitions with a source state count 3 for Idle, 2 for Walk, 1 for Run, 2 for Jump,
3 for Wave and 2 for Dance. A running total of those counts gives the starts 0, 3, 5, 6, 8, 11, 13: Walk's two
transitions occupy places 3 and 4 of the order array. The seventh number, 13, is the size of the array. The
transition from Any State goes to a separate list.

```cpp src="Strata/src/Strata/Animation/AnimationController.cpp#L227-L245" from="controller->m_StateTransitionStart.assign(stateCount + 1, 0);" to="return controller;" symbol="AnimationController::Create"
controller->m_StateTransitionStart.assign(stateCount + 1, 0);
for (const AnimationTransition& transition : stored.Transitions)
{
	if (transition.From != AnimationTransition::c_AnyState)
		controller->m_StateTransitionStart[transition.From + 1]++;
}
for (uint32_t state = 0; state < stateCount; state++)
	controller->m_StateTransitionStart[state + 1] += controller->m_StateTransitionStart[state];
controller->m_TransitionOrder.resize(controller->m_StateTransitionStart[stateCount]);
std::vector<uint32_t> fill(controller->m_StateTransitionStart.begin(), controller->m_StateTransitionStart.end() - 1);
for (uint32_t index = 0; index < stored.Transitions.size(); index++)
{
	const uint32_t from = stored.Transitions[index].From;
	if (from == AnimationTransition::c_AnyState)
		controller->m_AnyStateTransitions.push_back(index);
	else
		controller->m_TransitionOrder[fill[from]++] = index;
}
return controller;
```

1. **Line 227:** one start for each state plus one: the last start is the size of the order array.
2. **Lines 228–232:** count the transitions of each source state, one place to the right; Any State is not counted.
3. **Lines 233–234:** a running total turns the counts into starts.
4. **Line 236:** a cursor for each state, copied from the starts, marks where its next transition goes.
5. **Lines 237–244:** one pass in document order: Any State to its own list, the others to their state's run.

Compared with one list per state, this uses two flat arrays and no allocation per state. The order within a state
equals the document's order, so a designer decides priorities by writing transitions in order.

### Conditions and triggers

Every parameter lives as a float in the instance, so one array holds floats, `Bool` values and triggers alike: a `Bool` or a
trigger is 0 or 1. The test of a transition is below.

```cpp src="Strata/src/Strata/Animation/AnimatorInstance.cpp#L426-L444" symbol="AnimatorInstance::ConditionsHold"
bool AnimatorInstance::ConditionsHold(const AnimationTransition& transition) const
{
	for (const AnimationCondition& condition : transition.Conditions)
	{
		const float value = condition.Parameter < m_Parameters.size() ? m_Parameters[condition.Parameter] : 0.0f;
		bool holds = false;
		switch (condition.Mode)
		{
			case AnimationConditionMode::Greater: holds = value > condition.Threshold; break;
			case AnimationConditionMode::Less:    holds = value < condition.Threshold; break;
			case AnimationConditionMode::True:
			case AnimationConditionMode::Set:     holds = value != 0.0f; break;
			case AnimationConditionMode::False:   holds = value == 0.0f; break;
		}
		if (!holds)
			return false;
	}
	return true;
}
```

1. **Line 430:** a parameter index outside the array reads as 0.
2. **Lines 436–437:** `True` and `Set` test the same way: the value is not 0.
3. **Lines 440–441:** one condition that fails stops the test: all must hold.
4. **Line 443:** no conditions means the transition holds at once.

All conditions must hold, and a transition with none holds at once. A trigger tested by `Set` is the same as a `Bool`
tested by `True`: the difference is only the consuming, which `ConsumeTriggers` does after the transition is chosen.
It clears every `Set` parameter the firing transition tests, and no other. A trigger that is not set never fires, and a set
one fires until some transition consumes it.

### The update

The state machine runs at the end of `Advance`, after the playheads moved and the events were collected.

```cpp src="Strata/src/Strata/Animation/AnimatorInstance.cpp#L725-L762" from="// The state machine: transitions from any state first" to="tryTransitions(controller->GetStateTransitions(playing.State));" symbol="AnimatorInstance::Advance"
// The state machine: transitions from any state first, then from the state the animator is in; one fires at most.
const AnimationController* controller = assets.Controller;
if (!controller || !settings.Transitions || m_PlayedClip.IsValid() || m_Count == 0)
	return true;
const Playing& playing = m_Entries[m_Count - 1];
if (playing.State == c_ClipState)
	return true;
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
auto tryTransitions = [&](std::span<const uint32_t> transitions)
{
	for (const uint32_t index : transitions)
	{
		const AnimationTransition& transition = controller->GetTransitions()[index];
		if (transition.From == AnimationTransition::c_AnyState && transition.To == playing.State && !transition.CanTransitionToSelf)
			continue;
		if (!exitReached(transition) || !ConditionsHold(transition))
			continue;
		ConsumeTriggers(transition);
		StartState(transition.To, transition.Duration);
		return true;
	}
	return false;
};
if (!tryTransitions(controller->GetAnyStateTransitions()))
	tryTransitions(controller->GetStateTransitions(playing.State));
```

1. **Line 727:** no controller, transitions disabled, a clip played directly or nothing playing: no machine.
2. **Line 729:** the newest entry is the state the animator is in, also during a fade.
3. **Lines 751–752:** an Any State transition skips its own target unless it allows itself.
4. **Lines 755–756:** the firing transition consumes its triggers, then starts the target with its fade.
5. **Lines 761–762:** Any State first; the current state's list only when Any State gave nothing.

The exits come before the work: with no controller, with transitions disabled in `AnimatorSettings`, with a clip
played directly or with nothing playing, the function returns before it tests a thing. The newest entry is the state
the animator counts as being in. `tryTransitions` loops over a list in order and fires the first whose exit time was
reached and whose conditions hold. The exit test, for a looping state and for the others, is explained in
[Time and events](../animation/time-events.md). Any State first, and the current state's list only when Any State
gave nothing: that is the whole priority rule, in two lines at the end.

An Any State transition whose target is the current state is skipped unless `CanTransitionToSelf` is true. Without the
flag, a held trigger would restart the state every update. With it, a `Jump` trigger set during the robot's jump restarts the jump clip.

When a transition fires, `StartState` begins the target with the transition's duration. The weights during that fade
are the subject of [Blending](../animation/blending.md); here the point is only that the machine fires and moves on.

:::why
Strata fires at most one transition per update, and tries Any State first, for two reasons. A reader can predict the
result by hand: the rows of the table above need no search for the best path. And the cost of an update stays small: it
looks at the Any State list and one state's run of transitions, never at paths through the machine.

The price is a delay of one update for each further step, and no way to say "of two true transitions, take the one
with the highest score". A designer who needs that order writes the transitions in that order.
:::

## Playing without a controller, and states without clips

An animator without a controller is in **simple mode**: it plays the clip set on the component, looping or not by the
`Loop` setting, and no machine runs. While a controller is set, the Inspector disables the `Clip` property of the Animator component.
It shows the reason, "The controller's states choose the clips (Controller is set)", which comes from the
property's inactive reason ([Reflection](../world/reflection.md)). With a controller the clip of each state plays, and
the component's `Clip` plays nowhere.

A state may have no clip at all. Such a state is over at once (its normalized time, the share of its clip played, is 1) and it shows the :term[rest pose]{id=rest-pose} of
the skeleton. It is a way to say "nothing plays here", and an exit time of 1 or a condition leads out of it.

Two traps follow from the rules above, and each is one sentence. A transition with no condition and no exit time fires
in the first update of its source state, so that state hardly plays. After `PlayClip`, the controller's transitions do
not run until `Play` or `CrossFade` names a state again.

## Commands and parameters

Scripts and the editor drive an animator with a few commands. Each returns whether it worked.

| Command | What it does | Refused when |
| --- | --- | --- |
| `Play` | Jumps to a named state at once, with no fade | The state is unknown, or there is no controller |
| `CrossFade` | Moves to a named state over some seconds; a longer fade is cut to 60 | The state is unknown, there is no controller, or the time is negative or not finite |
| `PlayClip` | Plays one clip directly, without the controller | The handle is none or not a clip |
| `SetFloat` | Writes a float parameter by name | The name is unknown, the type is not float, or the value is not finite |
| `SetBool` | Writes a `Bool` parameter by name | The name is unknown or the type is not `Bool` |
| `SetTrigger` | Sets or clears a trigger by name | The name is unknown or the type is not trigger |

Names are strings, so a wrong name is a refusal and not a crash: a script reads the result and reports it. A float
that is not finite (a not-a-number value from a division by zero) is refused, so no condition ever compares such a
value. `ResetTrigger` is `SetTrigger` with false: it clears a trigger a script no longer wants, which is the cure for
the waiting wave of the example above.

### While the controller loads

A controller arrives later than the scene ([Loading without stalling](../assets/loading.md)). While it loads, `Play`,
`CrossFade` and the parameter commands do not fail: the instance keeps the latest state request and, for each name, the latest
parameter value. The first `Advance` after the load applies them, so the animator starts in the state the script
asked for with the parameters it wrote. A script that sets `Speed` every frame while the controller loads keeps one
entry, not a growing list. If there is no controller and none is loading, the commands are refused.

### When the controller is reloaded

Editing the controller reloads it, and a new object replaces the old one ([Importing](../assets/importing.md)). The
instance then binds again: each parameter takes its default, then the value of the old parameter with the same name
and type, then anything set by name in the meantime. A renamed parameter or one of another type starts over at its
default. If a state the animator plays no longer exists, the instance restarts at the controller's default state with
no fade. Playing the game while you tune a controller therefore keeps the robot's speed and grounded values.

## Settings of the animator

`AnimatorSettings` carries what one update reads from the component. `Speed` scales the time of every state, `Loop`
applies to simple mode and played clips, `ApplyRootMotion` lets the clip's motion move the entity, and `Transitions`
turns the machine off. Previews turn `Transitions` off so that the state you look at stays where it is.

With the game running, the Inspector shows the live state of the robot's animator, and during a fade it shows both
states: Walk, an arrow, then Run.

::figure{id=robot-inspector-fade}

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Decisions in scripts | Small games, prototypes | No asset format to learn | Tangled code, designers blocked |
| Hierarchical states (machines inside states) | Mecanim sub-state machines, many tools | Fewer arrows when a group shares exits | A second level of priority rules to teach and test |
| State machines as graph nodes | Unreal animation blueprints, Esoterica, Morpheme | Layers, masks and blends in one graph | A graph editor and much more to validate |
| Behaviour trees or utility scoring | Decision making of game characters, some animation switches | Priorities by structure | The result is a choice per update, not a smooth fade |

Sources are in Further reading.

## How it is tested

The suite `Animation.StateMachine` in `StrataTests/src/Animation/AnimatorTests.cpp` runs a small controller for standing, walking and jumping
and checks the rules of this page.

One case checks that conditions choose transitions from the current state and from
any state, with refusals for a wrong type or a value that is not finite. Another checks exit times. The case
"Triggers are consumed by the transition that fires, once" runs a chain of three states, A, B and C, where one trigger moves exactly
one step. Another case, "Commands given while the controller loads apply once it is known", checks the waiting rule
above. The controller cases of the suite `Animation.Assets` check that controllers validate, round trip as documents,
and reject wrong JSON with a reason.

Run them from the build folder (adjust the preset): `StrataTests.exe --test-suite=Animation.StateMachine`, or the
whole set through `ctest --preset windows-debug -j 8`.

## Changing it safely

- A new condition mode or parameter type goes into the enums, the validation of `Create`, `ConditionsHold`, the JSON
  reader and writer, and the tests. A reader that does not know a mode must refuse the document, never guess.
- Keep the order: Any State, then the current state, one transition. A second transition in one update would change
  the meaning of every controller already made.
- Run `Animation.StateMachine`, `Animation.Assets` and the feature test, which must exercise a new field.

## Summary

- A controller document lists parameters (float, `Bool`, trigger), states with clips, and transitions with conditions, exit times and fades; `Create` checks the limits and the types.
- An update advances the playheads, tries Any State transitions, then the current state's, in document order; at most one fires.
- A firing transition consumes the triggers it tests; a trigger that no transition fires on stays set until one does.
- `Play`, `CrossFade` and `PlayClip` choose states or clips; commands given while the controller loads wait, and a reload keeps values of parameters with the same name and type.
- To trace a trigger, break in the loop of `tryTransitions` and watch `ConsumeTriggers`.

## Check yourself

1. The robot is in Walk with `Speed` 5 and `Wave` set. Which state follows the next update?

   :::answer{tests="predict-states"}
   Run. Any State has only the jump rule, and `Jump` is not set. Walk's transitions come in order: Walk to Run holds
   (5 is above 4.5) and fires. Wave is tested only in Idle and Dance, so it stays set.
   :::

2. Which of these is a mistake? (a) A `Bool` parameter tested with `Set`. (b) A float tested with `Greater`. (c) A
   trigger tested with `Set`. (d) A `Bool` tested with `False`.

   :::answer{tests="read-document"}
   (a) is the mistake: `Set` tests triggers, and `Create` refuses a condition whose mode does not fit the type. The
   others fit: floats use `Greater` and `Less`, `Bool` values use `True` and `False`, triggers use `Set`.
   :::

3. A script sets a trigger every frame while a state with no transition on that trigger plays. What happens to the
   trigger?

   :::answer{tests="triggers,trace-update"}
   The trigger stays set, because only a transition that fires and tests it consumes it. The first transition that tests it
   and can fire, perhaps after the state changes, fires on the old request.
   :::

4. A script calls `PlayClip` for a wave and later sets `Speed` to 3. Does Idle to Walk fire?

   :::answer{tests="commands"}
   No. After `PlayClip` the update returns before the state machine, so no transition runs until `Play` or
   `CrossFade` names a state.
   :::

5. A script calls `Play("Walk")` while the controller is loading. What does the call return, and when does Walk play?

   :::answer{tests="commands"}
   The call returns true: the request is stored. Walk starts in the first update after the controller has loaded, instead
   of the default state.
   :::

## Exercises

1. **Basic.** Using the robot's numbers, start in Idle and give `Speed` 0.1 in update 1, 0.2 in update 2 and 5 in
   update 3. Name the state after each update.

   :::answer[Worked solution]{tests="predict-states"}
   Update 1: 0.1 is not above 0.1, so the robot stays in Idle. Update 2: 0.2 is above 0.1, so Idle to Walk fires and
   Walk follows. Update 3: Walk to Run fires, because 5 is above 4.5. The state after each update is Idle, Walk, Run.
   :::

2. **Medium.** Extend the toy: add a state Jump with an Any State transition on a trigger, no self transition, and
   a Jump to Idle transition without a condition. Press the trigger in updates 2 and 3. What is the state after
   each update, and in which update is each press consumed?

   :::answer[Worked solution]{tests="triggers,predict-states" solution="sketches/animation-state-machines-trigger.cpp"}
   The sketch keeps the trigger as a `Bool`. Update 2 consumes the first press. Update 3 presses again in Jump, which
   skips its own target, so the trigger waits; Jump to Idle fires. Update 4 consumes it, and the robot jumps again.

   ```cpp sketch="animation-state-machines-trigger.cpp"
   // The toy with a Jump state, a transition from Any State on a trigger, and a transition without a condition.
   // Any State is tried first and consumes the trigger when it fires; it skips its own target (no self transition).
   #include <cstdio>

   namespace
   {

   	enum class State { Idle, Walk, Jump };

   	const char* GetName(State state)
   	{
   		switch (state)
   		{
   			case State::Idle: return "Idle";
   			case State::Walk: return "Walk";
   			case State::Jump: return "Jump";
   		}
   		return "?";
   	}

   	struct ToyMachine
   	{
   		State Current = State::Idle;
   		float Speed = 0.0f;
   		bool JumpTrigger = false;

   		void Update()
   		{
   			if (JumpTrigger && Current != State::Jump)
   			{
   				JumpTrigger = false; // Consumed by the transition that fires
   				Current = State::Jump;
   				return;
   			}
   			if (Current == State::Idle && Speed > 0.1f)
   				Current = State::Walk;
   			else if (Current == State::Walk && Speed < 0.1f)
   				Current = State::Idle;
   			else if (Current == State::Jump)
   				Current = State::Idle; // No condition, no exit time: fires in the first update
   		}
   	};

   }

   int main()
   {
   	ToyMachine machine;
   	const bool presses[] = { false, true, true, false, false };
   	int update = 1;
   	for (const bool press : presses)
   	{
   		machine.JumpTrigger = machine.JumpTrigger || press;
   		machine.Update();
   		std::printf("update %d: pressed %d -> %s, trigger still set: %d\n", update++, press ? 1 : 0, GetName(machine.Current), machine.JumpTrigger ? 1 : 0);
   	}
   	return 0;
   }
   ```

   ```text output-of="animation-state-machines-trigger.cpp"
   update 1: pressed 0 -> Idle, trigger still set: 0
   update 2: pressed 1 -> Jump, trigger still set: 0
   update 3: pressed 1 -> Idle, trigger still set: 1
   update 4: pressed 0 -> Jump, trigger still set: 0
   update 5: pressed 0 -> Idle, trigger still set: 0
   ```

   1. **Lines 29–34:** Any State is tried first, and it skips the state Jump itself.
   2. **Line 31:** the firing transition consumes the trigger.
   3. **Lines 39–40:** no condition and no exit time: Jump lasts one update.
   4. **Line 53:** a press while the trigger is set changes nothing: it waits.
   :::

3. **Hard.** Trace it yourself. In the engine's source build, put a breakpoint in the loop of `tryTransitions`, then
   run the test "Triggers are consumed by the transition that fires, once". In which update is the trigger consumed,
   by which transition, and why does the next transition not fire on it?

   :::answer[Worked solution]{tests="trace-update"}
   The function is `AnimatorInstance::Advance` in `Strata/src/Strata/Animation/AnimatorInstance.cpp`. In the update after
   `SetTrigger`, the loop finds the transition A to B with `Set` holding, and `ConsumeTriggers` clears `Next`. The
   next transition, B to C, is not tried in that update, because one transition fires at most, and later the trigger
   is clear.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Animation/AnimationController.h` and `AnimationController.cpp`: the data, `Create`, the reader and writer.
- `Strata/src/Strata/Animation/AnimatorInstance.cpp`: parameters, commands and the update.
- `Strata/src/Strata/Animation/AnimationSystem.cpp`: one instance per animator, the calls into it.
- `Strata/src/Strata/Animation/AnimationComponents.cpp`: the Animator component and the reason `Clip` is off.
- `Samples/ThirdPerson/Assets/Animations/Robot.stanimator`: the example controller.
- `StrataTests/src/Animation/AnimatorTests.cpp`: the suite `Animation.StateMachine`.

## Further reading

- Unity manual, the Animator Controller and the Animation State Machine pages: parameters, Any State, exit times and triggers in Mecanim (beginner to intermediate).
- Unreal Engine documentation, State Machines in animation blueprints: a machine as a graph node (intermediate).
- Jason Gregory, Game Engine Architecture, the chapter on animation systems: state machines and blend trees in production engines (advanced).
