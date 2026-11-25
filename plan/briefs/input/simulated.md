# Brief: `input/simulated`

| Field | Value |
| --- | --- |
| Title | Simulated input |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `input/mouse-cursor`, `input/gamepads` |
| From | audio-input ch. 13 (the engine half); 1.8 (the virtual devices, the merge rules, release and clear, determinism); holds in fixed steps, `input.sequence` and `input.click` are `editor/stepping`'s |
| Unit | `plan/allocation/audio-input.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `input/simulated` — Simulated input

**Covers.** The job: a virtual keyboard, mouse and gamepads that tools, tests and agents press, merged with the real
devices so that the game sees one state; the editor's holds counted in fixed steps are `editor/stepping`'s. The page's
examples are an agent pressing Space for the Third-Person robot while a person holds W, and the feature test's
`InputFeatures` runner, which presses keys and buttons around its `PressFrame`. In this order: the problem, taught from
zero (tests and agents must play the same way at any frame rate and without the window's focus); the map (the simulated
queue applied at `BeginFrame`, merged with the devices behind the same queries); the contract (simulated events apply at
the next input frame; simulated input reaches the game whatever the enabled flag). The toy version is a queue of events
applied at a frame boundary and merged with a device's state.

The real code: the `Simulate*` functions, queued and applied at the next `BeginFrame`, so every transition lasts a whole
input frame; the merge rules (a button is down while either source holds it; a transition of one source is none when the
other held the button through the frame, so a tool's press over a person's hold changes nothing and restarts no repeat;
the pointer-to-member template) with their truth table; the simulated pointer (once moved, its position replaces the
device's; the first move only sets it); simulated gamepads (connected once used, until cleared; a held axis replaces the
device's value); release and clear (`ReleaseAllSimulated` queues releases and drops queued presses; `ClearSimulated`
forgets without releases when a session ends; `HasQueuedSimulatedInput` and the `IsSimulated*` queries); why durations
count fixed steps, named with a link to `editor/stepping`; the feature test's runner as the part's test of the whole
input path. Then the alternatives (injecting operating-system events, recording raw device streams), the tests of
`InputTests.cpp` and changing it safely. The exercises trace a simulated tap from `input.key` to a script's
`IsKeyPressed`, and change the "held throughout" rule to see which test fails and why. At the end the reader can predict
what a game sees when a tool and a person press the same key, and why a simulated press waits for the next input frame.

**Leaves out.**

- Holds counted in fixed steps, `input.sequence`, `input.click` and the other `input.*` commands → `editor/stepping`
- Simulated actions → `input/actions`
- Play-tests from a game maker's side → `make/automated-playtests`
- Agents that play a game → `automation/agents`

**Fit.** `fits`: about 3,350 words against M (3,000). The merge rules with their excerpt and truth table (about 450
words) and the concept from zero take the most; the two exercises add about 450.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `audio-input:136-140` | feature | home | The virtual keyboard, mouse and gamepads, the merge rules, the simulated pointer, simulated gamepads, release and clear |
| `audio-input:182` | feature | home | `InputFeatures` (`StrataTests/FeatureTest/Scripts/InputFeatures.cpp`), whose runner simulates input around `PressFrame` and checks keys, mouse, scroll, gamepad, cursor, actions, rebinding, saving and capture |
| `audio-input:357` | concept | home | B10: the engine's half (a virtual device, events at the frame boundary, merging, suspension); the editor's holds are `editor/stepping`'s |
| `audio-input:378` | code | home | `Strata/src/Strata/Input/Input.cpp:147-175`: merging two sources and the "held throughout" rule |
| `audio-input:447` | figure | home | Truth table: the device held, pressed or released against the simulated source, and what the game sees |
| `audio-input:519` | rule | home | Simulated events apply at the next input frame |
| `audio-input:595` | hands-on | home | Exercise ("trace it yourself"): a simulated tap from `input.key` through `SimulatedInput::Press`, `Input::SimulateKey` and `BeginFrame` to `IsKeyPressed`, with frame and step numbers |
| `audio-input:688` | term | home | Simulated input, virtual device |
| `editor-core:699` | term | home | Simulated input as the editor's glossary words it (held by commands, timed in fixed steps); one glossary entry with `audio-input:688`, whose definition names the device; the holds in fixed steps stay `editor/stepping`'s |
| `audio-input:179` | feature | use | The `input.*` commands that drive this device (home `editor/stepping`) |
| `audio-input:521` | rule | use | Durations of simulated input count fixed steps (home `editor/stepping`) |
| `audio-input:689` | term | use | Hold (editor) (home `editor/stepping`) |
| `audio-input:464` | figure | link | Simulated holds in fixed steps (home `editor/stepping`) |
| `audio-input:164` | feature | link | Simulated actions (home `input/actions`) |
| `audio-input:483` | figure | use | The `input.state` answer as a text capture (home `audio/testing`) |
| `new:33` | hands-on | home | Exercises (D27): the merge rule changed in a scratch branch so that a simulated press over a key the device holds reports Pressed, then the input tests run to see which case fails and why, predicted first (modify; a patch: done). Evidence: `Strata/src/Strata/Input/Input.cpp:147-175`; `StrataTests/src/Core/InputTests.cpp:209` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| `BeginFrame`, input frames and the merged queries | `input/devices-state` | must |
| Gamepads and their axes | `input/gamepads` | must |
| Templates | `basics/cpp-generic` | must |
| Fixed steps | `core/time` | must |
| Pointers to members (`T C::*`) | `basics/cpp-generic` | helps |
| Same inputs, same game: deterministic results | `core/jobs` | helps |
| Simulated actions | `input/actions` | helps |
| Holds counted in fixed steps, `input.sequence` and `input.click` | `editor/stepping` | helps |
| Editor commands | `editor/commands` | helps |
| The feature test | `engineering/feature-test` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `simulated-input` | Simulated input | virtual device |
