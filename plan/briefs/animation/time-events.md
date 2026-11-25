# Brief: `animation/time-events`

| Field | Value |
| --- | --- |
| Title | Time, loops and events |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `animation/state-machines` |
| From | animation ch. 9; 1.6 (`AdvanceEntry`, normalized time, exit times, events) |
| Unit | `plan/allocation/animation.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `animation/time-events` — Time, loops and events

**Covers.** The job: `AdvanceEntry` moves one playing entry's playhead by the update's time, wraps it across the loop
boundary in both directions, counts the crossings, keeps the normalized time and collects the events the playhead
passed; the state machine reads the normalized time for its exit times. The problem and how engines solve it: `fmod`
keeps the place in the loop and loses the count of loops, so exit times and events at the boundary fail; events as
notifies stored in clips (Unreal) against events on controller states (Strata, because glTF carries none); comparing
`time == eventTime` never fires. Time: the state's speed times the animator's (negative speeds play backwards), and
clips that do not loop stop at their ends. Loop accounting (the excerpt, read in three parts): the event window
(from, to] forwards and [to, from) backwards, with an event at time 0 firing at the start and once per loop; the walk
across the boundary; steps of more than four loops skipped arithmetically, so the work per update stays bounded.
Normalized time is loops plus time over duration (1.5 is halfway through the second loop): the playhead-across-loops
diagram. Exit times (the exit test of the state machine's excerpt, read again): on a looping state, an exit time below
1 lets the transition fire at that point of every loop (0.4, 1.4, 2.4: the second diagram); otherwise it fires once the
normalized time reaches it. Only the current state's events fire, never those of states fading out; this page only
collects them, and the Animation system dispatches them after all poses. An event whose time is past its clip's
duration never fires, and nothing warns: validation checks only that the time is not negative, and the playhead stops
or wraps at the duration. The toy: a playhead with loops and events, in
about 50 lines. How it is tested: "Looping clips wrap and other clips stop at their end", "Events fire once each when
the playhead passes them, in order, also across a loop boundary", "An event at the start of a looping clip fires when it
starts and once per loop" and "Exit times fire in the update that reaches them, at every loop of a looping state"
(`AnimatorTests.cpp`). Exercise E5: a test matrix of exit times on states that do not loop, each firing frame
predicted before the run; and a trace in the debugger of the event windows of one test. At the end the reader can
trace a playhead through a large backward step and list the events and exit times it fires.

**Leaves out.**

- Dispatching events to listeners and scripts → `animation/system`
- Reacting to an event in a script (footstep sounds) → `make/animation`
- Typed clip events and sync markers, as absences → `animation/limits`
- Frame time and the fixed step in general → `core/time`

**Fit.** `fits`: about 3,690 words against M (3,000). The long excerpt quoted in three parts, two timelines and the two
concepts take the most; the dispatch of events is left to `animation/system`.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `animation:88` | feature | home | Exit times: normalized time with loops; once per loop below 1 on a looping state |
| `animation:96-97` | feature | home | Loop accounting (`Playing::Loops`, at most `c_MaxEventLoops` = 4 loops of events per update) and events |
| `animation:293` | concept | home | Time, loops and normalized time; speeds below zero; large steps; the `fmod` mistake |
| `animation:296` | concept | home | Animation events (notifies): clip notifies against state events, firing across loops and backwards; the mistakes |
| `animation:347` | code | home | `Strata/src/Strata/Animation/AnimatorInstance.cpp:455-585`: advancing a playhead with loops both ways, event windows, loop counts, bounded work |
| `animation:391` | figure | home | Diagram 8, the playhead across loops |
| `animation:393` | figure | home | Diagram 9, an exit time on a looping state |
| `animation:502` | hands-on | home | E5 |
| `new:24` | rule | home | An event whose time is past its clip's duration never fires, and nothing warns (one sentence). Evidence: `Strata/src/Strata/Animation/AnimationController.cpp:187-188` (validation refuses only a negative or non-finite time); `Strata/src/Strata/Animation/AnimatorInstance.cpp:505-511` (a clip that does not loop stops at its duration), `:524-536` (a looping one wraps there) |
| `new:25` | hands-on | home | Trace it yourself (track E): with a breakpoint in `AdvanceEntry`'s `fire`, run "Events fire once each when the playhead passes them, in order, also across a loop boundary" in the engine's source build, and write down each update's window and the events it fires. Evidence: `Strata/src/Strata/Animation/AnimatorInstance.cpp:455-585` (`fire` at line 480); `StrataTests/src/Animation/AnimatorTests.cpp:363-394` |
| `animation:564-566` | term | home | Exit time, normalized time, playhead |
| `animation:571` | term | home | Animation event (notify) |
| `animation:348` | code | use | The exit test (`AnimatorInstance.cpp` 734-745), read again |
| `animation:127` | feature | link | Event dispatch, taught on `animation/system` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| State machines: states, transitions, an exit time as a field | `animation/state-machines` | must |
| Clips: duration, holding outside the keys | `animation/clips` | must |
| Floating point, rounding and precision (normalized time in double) | `basics/numbers` | must |
| Delta time | `core/time` | must |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `animation-event-notify` | Animation event (notify) | - |
| `exit-time` | Exit time | - |
| `normalized-time` | Normalized time | - |
| `playhead` | Playhead | - |
