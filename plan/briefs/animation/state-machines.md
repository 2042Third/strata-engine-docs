# Brief: `animation/state-machines`

| Field | Value |
| --- | --- |
| Title | State machines |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `animation/clips` |
| From | animation ch. 7; 1.3 (the controller asset), 1.6 (parameters, states and transitions) |
| Unit | `plan/allocation/animation.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `animation/state-machines` — State machines

**Covers.** The job: the `AnimationController` asset (a `.stanimator` JSON document) declares parameters, states and
transitions, and `AnimatorInstance` runs it for one animator without a scene. The problem and how engines solve it:
what plays must follow the game (speed, ground, a jump); hand-written switches in scripts, flat state machines with
parameters (Unity's Mecanim, whose model Strata's is close to: parameters, Any State, exit times, triggers), and state
machines inside graphs (Unreal's animation blueprints, Esoterica, Morpheme); Strata: one flat state machine,
transitions from any state first, at most one transition per update. The document, on the robot's controller (the
excerpt: the Walk state with its Footstep events, the Jump transition from any state with `CanTransitionToSelf`, Idle
to Walk on Speed > 0.1), its state-machine diagram, and the same controller as the Asset tab's tables (screenshot).
Validation in `Create`: the limits (256 parameters, 1,024 states, 4,096 transitions, 16 conditions, 256 events per
state, speeds up to 100, fades up to 60 s), names, a condition's mode against its parameter's type, events
stable-sorted by time. Transitions grouped by source state with a counting sort (a CSR layout, the excerpt). Playback
without a scene: simple mode (no controller: the component's clip plays, and the Inspector greys `Clip` while a
controller is set); the state machine (the excerpt): after each advance, the transitions from any state, then the
current state's, and the first whose conditions hold and whose exit time was reached fires (the exit-time test itself
is `animation/time-events`'); the conditions Greater, Less, True, False and Set, all of which must hold; triggers
consumed by the transition that fires, and the pitfall of a trigger that stays set; `CanTransitionToSelf`; a state
without a clip is over at once and shows the rest pose; a transition with no condition and no exit time fires in the
first update of its state, so that state hardly plays. Commands and parameters: `Play`, `CrossFade` and `PlayClip`
(after `PlayClip` the controller's transitions do not run until `Play` or `CrossFade` names a state);
`SetFloat`, `SetBool` and `SetTrigger` by name, refused for a wrong type or a value that is not finite; commands given
while the controller loads wait for it (the rule that script commands never block on loading); a reloaded controller
keeps the values of parameters with the same name and type; a controller that lost a state restarts its entries at the
default state. `AnimatorSettings` (Speed, Loop, ApplyRootMotion, and Transitions, off for previews). The Inspector of
the playing robot shows the live state, `Walk -> Run` during a fade (screenshot). The toy: a state machine with two
states and one float condition, in about 60 lines. How it is tested: `Animation.StateMachine` in `AnimatorTests.cpp`
(conditions, triggers, commands while the controller loads) and the controller cases of `Animation.Assets`. The
exercise is a trace in the debugger: the update in which a trigger is consumed. At the end the reader can read a
`.stanimator` document and predict, update by update, which state the robot is in.

**Leaves out.**

- Weights and blended poses during a transition's cross-fade → `animation/blending`
- Exit times on looping states, normalized time and events → `animation/time-events`
- Editing a controller in the Asset tab and driving it from a script → `make/animation`
- The animation graph and blend trees, which Strata does not have → `animation/limits`

**Fit.** `fits`: about 4,355 words against L (5,000). Three excerpts, three figures, the concept and four rules take the
most; the two behaviours that trap game makers take one sentence each.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `animation:53-55` | feature | home | The controller asset and its document, its validation, transitions grouped by source |
| `animation:75` | feature | home | The `Clip` inactive reason while a controller is set |
| `animation:84-87` | feature | home | Simple mode, the state machine, conditions, triggers consumed |
| `animation:89` | feature | home | `CanTransitionToSelf` |
| `animation:92-95` | feature | home | Commands; waiting for the controller; a reload keeps parameter values; a controller changed under the animator |
| `animation:99-100` | feature | home | A state without a clip; `AnimatorSettings` |
| `animation:283` | concept | home | State machines for animation: states, transitions, conditions, consumed triggers, any-state priority; Mecanim, graphs; the mistakes |
| `animation:344` | code | home | `Strata/src/Strata/Animation/AnimationController.cpp:223-245`: a counting sort groups transitions by source state |
| `animation:348` | code | home | `Strata/src/Strata/Animation/AnimatorInstance.cpp:725-763`: any state first, the exit test, conditions, consuming triggers |
| `animation:365` | code | home | `Samples/ThirdPerson/Assets/Animations/Robot.stanimator:36-51` with lines 91-115: the Walk state and its Footstep events, the Jump transition from any state, Idle to Walk. The JSON reader and writer are `AnimationController.cpp` 248-553, which the survey only outlined |
| `animation:387` | figure | home | Diagram 6, the robot's controller as a state machine, drawn once with the Footstep event times; the one file of this figure, which `make/animation` uses (gamedev figure 14, `gamedev:422`, is the same figure; R34, D42) |
| `animation:416` | figure | home | Screenshot 4: the Inspector of the playing robot, its live state during a fade |
| `animation:418` | figure | home | Screenshot 5: the Asset tab with `Robot.stanimator`: parameters, states, transitions; captured once, and `make/animation` uses the same file (gamedev screenshot 20, `gamedev:458`, is the same picture; R34, D42) |
| `animation:471` | rule | home | Script commands never block on loading |
| `animation:485` | rule | home | Triggers stay set until consumed (`ResetTrigger`) |
| `new:20` | rule | home | A transition with no condition and no exit time fires in the first update of its source state, so that state hardly plays (one sentence). Evidence: `Strata/src/Strata/Animation/AnimationController.h:77-80` ("None: it fires as soon as they hold"); `Strata/src/Strata/Animation/AnimatorInstance.cpp:426-444` (no condition is all conditions holding), `:734-737` (no exit time counts as reached) |
| `new:21` | rule | home | After `PlayClip` the controller's transitions do not run until `Play` or `CrossFade` names a state (one sentence). Evidence: `Strata/src/Strata/Animation/AnimatorInstance.h:144-146`; `Strata/src/Strata/Animation/AnimatorInstance.cpp:727` (a played clip returns before the state machine), `:306` and `:333` (`Play` and `CrossFade` clear it), `:348-350` (`PlayClip` sets it) |
| `new:22` | hands-on | home | Trace it yourself (done, track E): with a breakpoint in the state machine's loop, run "Triggers are consumed by the transition that fires, once" in the engine's source build, and note in which update the trigger is consumed, by which transition, and why the next transition does not fire on it. Evidence: `Strata/src/Strata/Animation/AnimatorInstance.cpp:725-763`; `StrataTests/src/Animation/AnimatorTests.cpp:188-222` |
| `animation:557-563` | term | home | Animation controller, state, transition, Any State, condition, parameter, trigger |
| `animation:587` | term | home | `.stanimator` |
| `animation:212` | feature | use | The robot's controller and the scripts that set its parameters |
| `animation:88` | feature | link | Exit times, taught on `animation/time-events` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Clips, sampling and binding | `animation/clips` | must |
| JSON documents | `basics/data-formats` | must |
| Asset handles | `assets/handles-meta` | must |
| Loading without stalling (a controller arrives later) | `assets/loading` | must |
| Prefix sums and arrays of indices | `basics/data-structures` | helps |
| Hot reload of assets (a reloaded controller) | `assets/importing` | helps |
| The editor's Inspector and Asset tab, as far as the first game shows them | `start/first-game` | helps |
| Inactive reasons (`ComponentRegistry::SetInactiveReason`) and the properties they turn off | `world/reflection` | helps |
| Play mode: the running copy | `editor/play-mode` | helps |
| Normalized time and exit times | `animation/time-events` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `stanimator` | `.stanimator` | - |
| `animation-controller-state-machine` | Animation controller (state machine) | - |
| `any-state` | Any State | - |
| `state` | State | - |
| `transition-animation` | Transition (animation) | - |
