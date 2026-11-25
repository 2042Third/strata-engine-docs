# Brief: `editor/stepping`

| Field | Value |
| --- | --- |
| Title | Pausing, stepping and exact tests |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `editor/play-mode`, `input/simulated` |
| From | editor-core ch. 10 "Time in steps" (fixed steps, time dilation, `play.step`); home of holds counted in fixed steps, `input.sequence` and `input.click` (`SimulatedInput`, `InputSequence`, `EditorInputCommands.cpp`); the simulated device and its merge rules are `input/simulated` |
| Unit | `plan/allocation/editor.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor/stepping` — Pausing, stepping and exact tests

**Covers.** The problem: a test or an agent must run a game for exactly 60 fixed steps and then check a position; a test
that waits 60 frames gives another answer on a faster machine. The idea is one paragraph that links `core/time`: game
time counts fixed steps, never frames, and a paused game that runs one fixed step per frame gives the same state
whatever the frame rate. The code, from the scene up: `Scene::SetPaused` stops the running systems and tells them
(`OnPausedChanged`), `Scene::Step(n)` lets the next n updates each run exactly one fixed step, and `GetFixedStepCount`
counts the fixed steps since the start, the clock that tools count in; then the editor's `SetPaused` and `Step(n)` (one
fixed step per frame while paused; resuming drops the steps not run yet; the counters of resumes and of fixed steps at a
resume and at a stop; `UpdateInputSuspension`, which suspends input frames while the game is paused without a step to
run); `play.step {steps, wait}`, a deferred Session command whose poll keeps its own state, stacks after earlier calls
and fails with `stepsRun` when the game is resumed or stopped; the frame cap lifted while stepping; the editor's switch
for time dilation, off in tests and scripted runs; and the editor's simulated input: holds made by commands with their
durations in fixed steps, `input.sequence` (a timeline of events per fixed step, observations sampled every n steps,
holds released at the end unless kept) and `input.click` (the pointer moved to a UI element's center and a tap of n
steps, refused when something covers the element). A paragraph takes the commands that act on the game's input as a
whole: `input.action` holds an input action whatever its bindings (named as scripts name it, its value refused when it
does not fit the action's kind; an action has one value, so a new hold replaces the one before without letting the
action go; it reads as up while its map is disabled or a binding capture listens); `input.state` lists the held actions,
every action as the game reads it, the maps' enables, the players' bindings that replace the project's and whether a
capture listens; `input.type` queues typed text (1 to 1,024 bytes); `input.releaseAll` ends every hold and drops presses
still queued. The rule that tools count game time in fixed steps, never frames, is `core/time`'s, and the page links it;
it keeps the rule's exception for simulated input: holds count `EditorContext::GetInputStepCount`, the fixed steps plus
every frame in which a running game updates at time scale 0 without a step, so that a tap on a pause menu still ends.
The example starts a game paused (`play.start {paused: true}`), runs `play.step {steps: 30}` and reads `fixedSteps`,
then plays an `input.sequence` that presses a key at step 10 and samples the ball's height every 5 steps. The trace
exercise counts the fixed steps each frame runs during a `play.step`. Afterwards the reader can write a check of a game
that gives the same result on every machine.

**Leaves out.**

- The fixed step, the accumulator, time dilation and the rule "fixed steps, never frames" → `core/time`
- The simulated device, its merge rules, release and clear → `input/simulated`
- How a click finds a UI element → `ui/input`
- Files of such checks → `editor/command-scripts`
- Play-tests as a game maker writes them → `make/automated-playtests`

**Fit.** `over`: about 4,900 words against M (3,000). Counted again from the sections, with the paragraph on
`input.action`, `input.state`, `input.type` and `input.releaseAll`, the exception of simulated holds and the trace
exercise: the scene's and the editor's pause and step, the `input.*` commands, three excerpts and four figures pass M's
top; the next size is L (5,000) (S2).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:352` | concept | home | Fixed steps, pausing and stepping; why tests count steps |
| `editor-core:221-222` | feature | home | The editor's time dilation switch; pause and step with their counters |
| `foundation:186` | feature | home | The scene's pause and `Step`, one fixed step per update while paused, and `GetFixedStepCount` as the tools' clock (`Strata/src/Strata/Scene/Scene.h:427-438`); `core/time` uses the count |
| `editor-core:224-226` | feature | home | `play.step {steps, wait}`, the frame cap lifted while stepping, the editor's simulated input with `input.sequence` and `input.click` |
| `editor-core:438` | code | home | `StrataEditor/src/Editor/Commands/PlayCommands.cpp:191-256`: `play.step`, a deferred Session command with a stateful poll |
| `new:34` | code | home | `StrataEditor/src/Editor/EditorContext.cpp:1560-1624`: `SetPaused` and `Step`, one step per frame and the counters |
| `audio-input:178` | feature | home | `UpdateInputSuspension`: the editor suspends input frames while a paused game has no step to run, inside the excerpt of `new:34`; as passed by `audio-input`, whose `input/devices-state` keeps `Input::SetSuspended` |
| `new:35` | code | home | `StrataEditor/src/Editor/EditorInputCommands.cpp:679-760`: `input.sequence`, events per fixed step and observations |
| `editor-core:496` | figure | home | Fixed steps against frames: catch-up, time dilation, one step per frame while stepping, a tap of n steps |
| `editor-core:530` | figure | home | A paused game after `play.step {steps: 30}` |
| `editor-core:580` | rule | link | Tools count game time in fixed steps, never frames: homed in `core/time`'s rule box; the page links it and keeps the input tools' exception (`audio-input:521`) |
| `new:60` | hands-on | home | Trace it yourself (D27): start a game paused, run `play.step {steps: 3}` with breakpoints in `EditorContext::Step` and in `play.step`'s poll, and count the fixed steps each frame runs until `stepsRun` is 3. Evidence: `StrataEditor/src/Editor/EditorContext.cpp:1577-1582`; `StrataEditor/src/Editor/Commands/PlayCommands.cpp:191-256` |
| `editor-core:693` | term | home | Stepping |
| `editor-core:700` | term | home | Input sequence |
| `audio-input:357` | concept | use | Simulated input, determinism and fixed steps, as the input survey states it |
| `audio-input:179` | feature | home | The `input.*` commands: holds, `input.sequence` and `input.click`; and a paragraph (about 300 words) on `input.action` (an action held whatever its bindings; a new hold replaces the old one's single value; refused when the value does not fit the kind; up while its map is disabled or a capture listens), `input.state` (held actions, every action as read, map enables, players' bindings, the capture), `input.type` and `input.releaseAll`. At the pin: `Docs/DeveloperGuide.md:3746-3768`, `:3806-3807`; `StrataEditor/src/Editor/EditorInputCommands.cpp:761-824`, `:1035-1059`, `:1060-1139`, `:1343-1361` |
| `gameui:220` | feature | home | `input.click` on game UI, world canvases projected, refused when the element is covered |
| `audio-input:464` | figure | home | Simulated holds in fixed steps, as a timeline |
| `audio-input:480` | figure | home | The status bar's pill of simulated holds |
| `audio-input:521` | rule | home | Durations of simulated input count fixed steps, never frames, with the exception the page keeps: `EditorContext::GetInputStepCount` adds every frame in which a running game updates at time scale 0 without a step, so that a tap on a pause menu ends; the rule itself is `core/time`'s (`editor-core:580`). At the pin: `StrataEditor/src/Editor/EditorContext.h:349-352`; `StrataEditor/src/Editor/EditorContext.cpp:2763-2765`, `:2797` |
| `audio-input:689` | term | home | Hold (editor) |
| `scene-ecs:642` | term | home | Stepping |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Fixed steps, the accumulator and time dilation | `core/time` | must |
| Simulated devices and their merge rules | `input/simulated` | must |
| Input actions, their maps and kinds, and the players' bindings | `input/actions` | helps |
| The running copy and `play.start` | `editor/play-mode` | must |
| Deferred commands and polls that keep state | `editor/deferred-commands` | must |
| Game UI rects and hit tests | `ui/input` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `hold-editor` | Hold (editor) | - |
| `input-sequence` | Input sequence | - |
| `stepping` | Stepping | - |
