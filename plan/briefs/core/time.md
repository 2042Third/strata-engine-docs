# Brief: `core/time`

| Field | Value |
| --- | --- |
| Title | Time: delta time, the fixed step and time scale |
| Kind | C |
| Size | L |
| Tracks | E |
| Needs | `core/frame-loop`, `basics/math-change` |
| From | foundation "Time: delta time, the fixed step and interpolation"; physics "Time in a game: the fixed step"; home of "game time counts fixed steps, never frames", the fixed step and time dilation; interpolation in one paragraph (interpolate or extrapolate, one step of latency; Strata's interpolated set is `world/interpolation`'s) |
| Unit | `plan/allocation/core.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `core/time` — Time: delta time, the fixed step and time scale

**Covers.** The problem as the reader meets it: a ball moved by a fixed distance each frame crosses the screen twice as
fast on a computer twice as fast, and a physics step that changes with the frame's length makes bodies jitter or fly
apart. The naive answer, multiplying by the frame's delta time, and where it breaks: a breakpoint or a loading hitch
makes one huge step, physics needs equal steps to stay stable, and no run repeats another. Clocks first: the wall clock,
which jumps, against the monotonic clock; double for absolute time and float for short steps; the clamp against long
frames. The idea: simulate in fixed steps that an accumulator pays out of the frames' time; the spiral of death when
steps cost more than they simulate; time scale and unscaled time; interpolation in one paragraph (draw between the last
two steps at one step of latency, or extrapolate; Strata's interpolated set is `world/interpolation`'s). The approaches,
with a table of their costs: a fixed frame rate in lockstep, a variable step, a semi-fixed step, the accumulator with a
cap, and time dilation. Strata's choice: a variable step clamped to 0.25 s for the frame's work; the scene's
accumulator, capped by `GetMaxFixedSteps` (steps of 2/15 s at the project's rate) with the backlog dropped; time
dilation in programs that run on the wall clock, and never in runs that must repeat; the project's `Scene.Timing`
`FixedRate` (30, 60, 120 or 240 steps per second) over every scene's own step; `OnUpdate`, the steps' `OnFixedUpdate`,
then `OnLateUpdate`; time scale and unscaled time; pausing and `Step`. The design decision as a `:::why`: game time
counts fixed steps (`Scene::GetFixedStepCount`), never frames, and so do the tools (the rule's home; the editor's
exception, input holds that also count frozen frames, is `editor/stepping`'s). The accumulator's code is
`world/systems`' walk-through; this page shows its behaviour as numbers, in a table of uneven frames as `SceneTests.cpp`
checks it. What the choice cannot do: one step serves scripts, physics and animation together, and no system runs at a
rate of its own. The common mistakes: physics in `OnUpdate`, multiplying by the frame's delta in `OnFixedUpdate`,
counting frames in tests, `system_clock` for game time, float absolute time after hours, a teleport that does not break
the interpolation. The exercises: the accumulator written in a toy loop and compared with the engine's; the Physics
Playground at `FixedRate` 30 and 240, with its steps in the editor written out; one object moved in `OnUpdate` and one
in `OnFixedUpdate` at two frame caps. At the end the reader can predict how many fixed steps a frame runs, why the
backlog is dropped and when time dilates.

**Leaves out.**

- The accumulator's code in `Scene` → `world/systems`
- Interpolation: the interpolated set, its roles and drawn transforms → `world/interpolation`
- Pausing and stepping in the editor, and holds counted in fixed steps → `editor/stepping`
- The `Scene.Timing` section's validation and its hand-over to scenes → `world/projects-settings`
- Integrating bodies inside a step → `physics/dynamics`
- Time from a script's side: the callbacks and `Time`'s clocks → `make/script-loop`
- The runtime's `--frames` and `--seconds` → `worlds/runtime`

**Fit.** `fits`: about 4,650 words against L (5,000). The two concepts with the approaches table take the most, then
Strata's choice with the design decision's `:::why`, which now also holds the rule that tools count fixed steps; three
exercises follow.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:224` | concept | home | Time: the wall clock and the monotonic clock, double and float, the clamp, frames against game time |
| `foundation:228` | concept | home | The fixed step, the accumulator, the spiral of death, time scale, interpolation in one paragraph; the approaches and their costs |
| `foundation:183` | feature | home | The variable step: the wall time since the previous frame, clamped to 0.25 s (`MaxTimestep`) |
| `foundation:184` | feature | home | The accumulator as Strata runs it: `OnUpdate`, the due `OnFixedUpdate` steps up to `GetMaxFixedSteps`, the backlog dropped, `OnLateUpdate`; time scale and unscaled time; its code is `world/systems`' |
| `foundation:185` | feature | home | Time dilation: catch-up steps stop once they take longer in wall time than they simulate |
| `foundation:187` | feature | home | The project's `Scene.Timing` `FixedRate` over the scenes' own steps, and the cap of `ceil(rate * 2 / 15)` steps; the section's mechanism is `world/projects-settings`' |
| `foundation:406` | figure | home | The fixed step on a time axis: uneven frames filling the accumulator, steps falling out, the cap dropping the backlog, the interpolation's alpha one step behind |
| `foundation:489` | rule | home | Steps are clamped (0.25 s) and fixed-step backlogs dropped |
| `foundation:491` | rule | home | Read the step through `Scene::GetFixedTimestep` and `GetMaxFixedSteps`; count game time in fixed steps, never frames (the design decision's `:::why`) |
| `foundation:524` | hands-on | home | The accumulator written in a toy loop (uneven frames, the cap, the dropped backlog, the alpha), then compared with the engine's |
| `foundation:538` | hands-on | home | The Physics Playground at `FixedRate` 30 and 240: what changes in contacts and smoothness |
| `foundation:539` | hands-on | home | One object moved in `OnUpdate` and one in `OnFixedUpdate`, played at two frame caps |
| `foundation:571` | term | home | Two entries: timestep and delta time |
| `foundation:572` | term | home | Fixed timestep |
| `foundation:573` | term | home | Accumulator |
| `foundation:574` | term | home | Spiral of death |
| `foundation:575` | term | home | Time dilation |
| `foundation:577` | term | home | Two entries: time scale and unscaled time |
| `scene-ecs:316` | concept | home | Game loop time from the scene's side, the same concept as `foundation:228`: the accumulator, the cap, the dropped backlog, time scale, pausing and single steps, `GetFixedStepCount` as the tools' time base |
| `scene-ecs:436` | figure | home | The accumulator's timeline, the same figure as `foundation:406`, with the case of time dilation drawn in |
| `scene-ecs:541` | rule | home | Tools count game time in fixed steps, never frames: the design decision's `:::why`, with `foundation:491` |
| `editor-core:580` | rule | home | Tools count game time in fixed steps, never frames, as the editor's guide states it (frames differ per machine; steps make tests exact): one rule box with `scene-ecs:541` and `foundation:491`, passed by `editor` (R31, "Fixed steps, never frames"); `editor/stepping` keeps the exception (input holds also count frozen frames) and links |
| `scene-ecs:637-641` | term | home | Fixed timestep, accumulator, spiral of death, time dilation, and time scale with unscaled time: the same entries as this page's own |
| `audio-input:690`, `editor-core:691`, `worlds-runtime:564` | term | home | Fixed step, the same entry as `foundation:572` |
| `editor-core:692`, `worlds-runtime:563` | term | home | Time dilation, the same entry as `foundation:575` |
| `scripting:617` | term | home | Time scale, the same entry as `foundation:577` |
| `foundation:186` | feature | use | Pausing, `Step` and `GetFixedStepCount` as the clock tools count by; the mechanism is `editor/stepping`'s |
| `foundation:188` | feature | link | Interpolation of drawn transforms, named in its one paragraph |
| `foundation:576` | term | link | Interpolation (render), whose entry is `world/interpolation`'s |
| `foundation:369` | code | use | The accumulator's excerpt, placed with `scene-ecs:388` and linked, not quoted |
| `scene-ecs:107` | feature | use | `OnUpdateRuntime`'s order of phases, as the scene runs them |
| `scene-ecs:111` | feature | use | Time dilation and `GetDroppedFixedStepCount` |
| `scene-ecs:113` | feature | use | `SceneSettings`' fixed step and maximum steps, which the project's rate overrides |
| `scene-ecs:222` | feature | use | The `Scene.Timing` section |
| `scene-ecs:388` | code | use | The accumulator's code, linked to its walk-through on `world/systems` |
| `scene-ecs:389` | code | use | The accumulator's behaviour as numbers: the source of the page's table of uneven frames |
| `scene-ecs:539` | rule | use | Read the step through `Scene`, from the scene's side |
| `physics:156`, `physics:158` | feature | use | The accumulator and `Scene.Timing` from physics' side |
| `physics:241` | concept | use | Why physics needs a fixed step: stability, determinism and repeatable runs |
| `physics:396`, `physics:398` | rule | use | Read the step through `Scene`; tools count fixed steps |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The frame loop, `Timestep` and the clamp in `Run` | `core/frame-loop` | must |
| Rates, accumulation and Euler steps | `basics/math-change` | must |
| Floating-point precision | `basics/numbers` | must |
| A script's `OnUpdate` and its delta time | `start/first-game` | helps |
| Opening a sample from the launcher | `start/first-game` | helps |
| Lerp | `basics/math-interpolation` | helps |
| A scene and its systems | `world/systems` | helps |
| Rigid bodies and their integration | `physics/dynamics` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `accumulator` | accumulator | - |
| `delta-time` | delta time | - |
| `fixed-step` | fixed step | - |
| `spiral-of-death` | Spiral of death | - |
| `time-dilation` | time dilation | - |
| `time-scale` | Time scale | - |
| `unscaled-time` | unscaled time | - |
