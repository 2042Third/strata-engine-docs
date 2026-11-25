# Brief: `make/timers-events`

| Field | Value |
| --- | --- |
| Title | Timers, time scale and events between scripts |
| Kind | H |
| Size | M |
| Tracks | G |
| Needs | `make/project-coin-run` |
| From | scripting "Building blocks and recipes" (`Timer`, `KeyRepeat`, cooldowns); scripting "The gameplay API, part 3": `Time` (time scale, unscaled and real time, the frame index); scripting "The gameplay API, part 1": `GetScript<T>`, `AddScript<T>` (scripts that call each other, found again every frame: gamedev concept 12) |
| Unit | `plan/allocation/make-b1.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/timers-events` — Timers, time scale and events between scripts

**Covers.** A how-to on a small arcade room built from a new Basic 3D project. First the `Time` clocks a script can read:
the frame's delta and the fixed delta, the elapsed time and the frame index, the time scale, and the two clocks that go
on at time scale 0, the unscaled delta and the real time; which one to use for what, in a table. Then `Timer`: a crate
dropped every two seconds by a repeating timer (`for (int32_t i = timer.Update(deltaTime); i > 0; i--)`, and why a
repeating timer keeps its overshoot), a one-shot delay, and a cooldown on a dash key; a timer fed with scaled time stops
while the game is paused, and a duration that is not positive stops it. Then `KeyRepeat`: a selection marker moved along a
row of cubes while an arrow key is held, fired on the press, after a delay and then at an interval; the excerpt of
`Gameplay.h` shows it as a small state machine. One sentence says that `KeyRepeat` is the script's own helper and
differs from the menu key repeat of UI actions, which the engine applies on the UI map (`input/actions` homes it,
`make/menus` uses it). Then time scale as a game uses it: slow motion at 0.25 and a pause at 0,
with a "Paused" text that blinks on unscaled time; the pause menu itself is `make/menus`'. Last, scripts that talk to
each other: a `Scoreboard` script on an entity named "Game", and pickups that find it again each time they need it
(`Scene::FindEntityByName("Game").GetScript<Scoreboard>()`, checked for `nullptr`) and call its `AddPoint`, as the
Third-Person sample's `Coin` calls `CourseState::AddCoin`; the rule that a `GetScript<T>()` pointer is never kept from
one frame to the next, because the script may be destroyed or reloaded, so a script keeps the `Entity` and checks
`IsValid()`; `AddScript<T>()` to give an entity a behaviour while the game runs, and `HasScript` and `RemoveScript` by
class name. What Strata does not do here: coroutines; nothing waits inside a callback, and timers and state machines
do that work. The exercises, done in a script: a dash cooldown shown as a bar that fills with the timer's progress, and
a countdown on unscaled time beside one on scaled time, with what each does while the game is paused. At the end the
reader can time things in game time or in real time, repeat a held key, slow and pause the game, and let scripts call
each other safely.

**Leaves out.**

- Frame and fixed updates, `FixedRate` and what time scale does to the loop → `make/script-loop`
- The fixed step, time dilation and the accumulator as a mechanism → `core/time`
- A pause menu and UI animated on unscaled time → `make/menus`
- The UI's own key repeat on the UI map → `make/menus`
- Smoothing over time → `make/gameplay-math`
- Random numbers and seeds → `make/recipes`
- State machines, managers and object pools → `make/patterns`
- Fields set in the Inspector, entity and asset fields → `make/script-fields`
- Waiting for game time in a play-test, counted in fixed steps → `make/automated-playtests`

**Fit.** `fits`: about 3,200 words against M (3,000). The `Timer` section and the scripts that call each other, with
its rule (about 1,000 words), the table of clocks, the `KeyRepeat` excerpt and the two exercises take the most; the
absence of coroutines is one sentence.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:146` | feature | home | `KeyRepeat`: fires on the press, after a delay, then at an interval while the key stays down |
| `audio-input:174` | feature | home | The same helper as the input survey lists it: it runs inside the script module, with a delay of 0.25 s and an interval of 0.05 s by default |
| `gamedev:371` | code | home | `StrataScriptCore/Include/StrataScript/Gameplay.h:178-219`: `KeyRepeat`, a small state machine for a held key (press, delay, interval, a long frame repeating once) |
| `gameui:208` | feature | home | `Time::GetUnscaledDeltaTime`, the clock that goes on at time scale 0, for whatever moves while the game is paused |
| `gamedev:618` | term | home | Unscaled time |
| `gamedev:496` | rule | home | Never keep a `GetScript<T>()` pointer from one frame to the next; keep the `Entity`, check `IsValid()` and ask again |
| `scripting:123` | feature | home | `Time` in the SDK, beside `gameui:208`: delta, fixed delta, elapsed time, frame index, time scale, unscaled delta, real time, and which clock to use for what; `reference/script-api` lists the declarations and links here |
| `scripting:134` | feature | home | `Timer` in the SDK: one-shot and repeating, the overshoot kept so that a repeating timer does not drift, a duration that is not positive stops it; `reference/script-api` lists the declarations and links here |
| `scripting:135` | feature | home | `KeyRepeat` in the SDK, one entry with `gamedev:146` and `audio-input:174`; `reference/script-api` lists the declaration and links here |
| `scripting:343` | concept | use | The determinism helpers' timer: a repeating `Timer` keeps its overshoot, so it does not drift (the concept's home is `make/recipes`) |
| `scripting:118` | feature | use | `Entity`'s `GetScript<T>`, `AddScript<T>`, `HasScript` and `RemoveScript` |
| `scripting:474` | rule | use | The scripting survey's form of the same rule, with its reason |
| `scripting:385` | code | use | Lines 43-44 of `Coin.cpp`: the coin finds `CourseState` again when it is collected (the whole script is `make/recipes`') |
| `gamedev:321` | concept | use | The script lifecycle's mistake of caching `T*` across frames (its home is `make/script-loop`) |
| `new:13` | not-done | home | Coroutines: nothing waits inside a callback; timers and state machines do that work. Evidence: `git grep -n -i -e coroutine -e co_await 822a7a46 -- Strata/src StrataScriptCore` finds nothing; `StrataScriptCore/Include/StrataScript/Script.h:83-97` (the 15 callbacks, plain `void` functions) |
| `new:14` | hands-on | home | Exercises, done in a script: a dash cooldown shown on the HUD as a bar that fills with `Timer::GetProgress`; a countdown on `Time::GetUnscaledDeltaTime` beside one on the scaled delta, and what each does at time scale 0. Evidence: `StrataScriptCore/Include/StrataScript/Gameplay.h:143` (`Update`), `:166-170` (`IsRunning`, `GetRemaining`, `GetProgress`); `StrataScriptCore/Include/StrataScript/Time.h:57` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The script lifecycle: `OnCreate`, `OnUpdate`, `OnFixedUpdate`, and `deltaTime` | `make/script-loop` | must |
| What time scale does to the loop | `make/script-loop` | must |
| Finding entities by name from a script; instantiating a prefab and asking for it early | `make/scripting-scene` | must |
| Prefabs | `make/prefabs` | must |
| Pointers at the use level: `T*`, a `nullptr` check, `->` | `basics/programming-3` | must |
| Classes with member variables and methods | `basics/programming-3` | must |
| Loops and functions | `basics/programming-2` | must |
| Keys and input actions in a script | `make/input` | must |
| Triggers and `OnTriggerEnter` | `make/physics` | must |
| Text on a HUD set from a script | `make/hud` | must |
| The fixed step and time dilation as a mechanism | `core/time` | helps |

**Starting state.** A new project from the Basic 3D template; no checkpoint. The first step makes a crate prefab from a
cube with a dynamic RigidBody, as `make/prefabs` and `make/physics` taught, and a text element for the score, as
`make/hud` taught.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `unscaled-time` | unscaled time (use) | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-b1-3 | should | shape | `make/gameplay-math`, `make/timers-events`, `make/script-fields`, `make/script-builds`, `make/levels-saves` | style.md gives a how-to a `## Variations` section: the same goal under other conditions. The Covers of these five how-tos name no variation, so the writer has nothing to fill it with. The how-tos of `make-a` and `make-b2` name theirs. (`make/recipes` has its "what to change" per recipe.) | Each Covers names two variations (about 250 words a page). From the pin: gameplay-math, aiming with the right stick through the Look action instead of the cursor (`FollowCamera.cpp:57-60`), and a turret that turns at a limited speed (critic-make-b1-16); timers-events, a timer in `OnFixedUpdate` fed with the fixed delta, for gameplay that keeps step with physics, and a held gamepad direction repeated (critic-make-b1-5); script-fields, tuning many spawners at once through their prefab (critic-make-b1-4); script-builds, the plain `cmake -S` and `-B` build as a check that the code compiles on another machine (critic-make-b1-1); levels-saves, three save slots named "Slot 1" to "Slot 3" and listed with `ListSaveFiles`. The five Fit lines count them. | `style.md:535-541`; `allocation/make-b1.md:5-24`, `:91-111`, `:174-193`, `:420-440`, `:922-962`; `allocation/make-a.md:130`, `:424`; `allocation/make-b2.md:393`; `StrataScriptCore/Include/StrataScript/Game.h:104-107`, `:157-158` |
| critic-make-b1-5 | should | missing-item | `gamedev:146`, `scripting:135` on `make/timers-events` | `KeyRepeat` takes a key code and reads that key with `Input::IsKeyDown` and `IsKeyPressed`. It cannot repeat an input action or a gamepad button, so a repeat built on it ignores the player's rebinding and the gamepad. `make/input` teaches that gameplay reads rebindable controls as input actions, and the page never says that `KeyRepeat` steps outside that rule. `make/project-tetris` later writes a repeat for actions, and no page has said why it must. | One paragraph after the `KeyRepeat` step: it reads keys only; for a held action or a gamepad direction, the same logic is written on `Input::IsActionDown` and `IsActionPressed` with a delay and an interval (about 100 words; the sketch can be the page's Variation, critic-make-b1-3). | `allocation/make-b1.md:96-100`, `:133-135`; `StrataScriptCore/Include/StrataScript/Gameplay.h:178-219`; `StrataScriptCore/Include/StrataScript/Input.h:384-393`; `AGENTS.md:287`; `allocation/make-c.md:155` |
| critic-make-b1-6 | should | missing-item | the scripts that call each other on `make/timers-events` | The pickups call `Scoreboard::AddPoint` through `GetScript<Scoreboard>()`. **Scripts > New Script** writes one `.cpp` per class, so the pickup's file cannot see the `Scoreboard` class. The class must move to a header that both files include, as the sample's `CourseState.h` is, while `ST_SCRIPT_CLASS(Scoreboard)` stays in `Scoreboard.cpp`. If the registration goes into the header, the module fails to load with "class 'Scoreboard' is registered twice", and no script runs. The Covers has no step for the split, and the Assumes has no row for header and source files. | Add a step before the pickups: `Scoreboard.h` with the class, `Scoreboard.cpp` with the registration, the pickup's `#include "Scoreboard.h"`, and the message as the step's "If you do not see it" (about 120 words). Add two Assumes rows: "Header and source files, `#include`" taught by `basics/programming-3` (must), and "`ST_SCRIPT_CLASS` once per class, in a `.cpp`" taught by `make/first-script` (must). | `allocation/make-b1.md:102-106`, `:150-164`; `allocation/basics-a.md:321-323`; `allocation/make-a.md:885`; `Docs/Manual/Scripting.md:11`; `StrataScriptCore/Include/StrataScript/Script.h:840-852`; `Strata/src/Strata/Scripting/ScriptModule.cpp:979-983`; `Samples/ThirdPerson/Scripts/CourseState.h:10`; `Samples/ThirdPerson/Scripts/Coin.cpp:4`, `:43-44` |
| critic-make-b1-11 | should | missing-item | Starting state and recipes of `make/recipes` | Each recipe "adds it to a new project", but no step says what the reader copies, and the samples' scripts depend on others. `Coin.cpp` includes `CourseState.h`, whose source includes `ThirdPerson.h` and `ThirdPersonPlayer.h`. The grab and the pour are member functions of the large `Playground` class. `Impact.cpp` finds its sounds by path, so they must exist at `Sounds/Impacts/...` in the new project, and a pruned export must list them under Always Include. A reader who copies `Coin.cpp` alone gets compile errors. | The Starting state and each recipe say that the reader writes a script of their own from the excerpt (the coin calls the `Scoreboard` of `make/timers-events` instead of `CourseState`), which sounds to copy with the file browser and import, and one sentence that sounds found by path need Always Include (`make/export`). About 200 words. | `allocation/make-b1.md:337-355`, `:412-414`; `allocation/make-a.md:1752`; `Samples/ThirdPerson/Scripts/Coin.cpp:4`, `:43-44`; `Samples/ThirdPerson/Scripts/CourseState.cpp:3-4`; `Samples/PhysicsPlayground/Scripts/Playground.h:76`, `:79`; `Samples/PhysicsPlayground/Scripts/Impact.cpp:1-4`, `:18`, `:63-77` |
| critic-make-b1-19 | could | missing-item | `make/timers-events`; the replay of `make/recipes` | `Timer`, `KeyRepeat` and `Random` are plain members, not fields, so a hot reload starts them over. A cooldown restarts, and a seeded `Random` begins its sequence again in the middle of a game, which breaks the recorded replay of `make/recipes`. The SDK's header says to make them again in `OnReload` or keep what matters in fields; neither page says it. | One sentence on each page, where `Timer` and the replay are taught (about 40 words each). | `allocation/make-b1.md:93-96`, `:338-341`; `StrataScriptCore/Include/StrataScript/Gameplay.h:12-14`; `Docs/Manual/Scripting.md:177-181` |
