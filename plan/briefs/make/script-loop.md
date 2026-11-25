# Brief: `make/script-loop`

| Field | Value |
| --- | --- |
| Title | The game loop from a script's side |
| Kind | C |
| Size | M |
| Tracks | G, B |
| Needs | `make/first-script`, `basics/programming-3` |
| From | gamedev "The game loop from a script's side" (concepts 1, 12); scripting "The script lifecycle and the frame"; home of the script lifecycle and its callbacks; use home of the fixed step, frame and fixed updates, time scale and FixedRate; `Time`'s delta and fixed delta; Coin Run's coins bob in `OnUpdate` |
| Unit | `plan/allocation/make-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/script-loop` — The game loop from a script's side

**Covers.** A concept page, home of the script lifecycle and its callbacks and use home of the fixed step. The
problem as the reader meets it: the coins spin at the same speed on a fast and a slow computer because the turn is
multiplied by `deltaTime`; the ball of `make/physics` will need more than that. The naive answer, a constant amount
moved each frame, and where it breaks (twice the frame rate, twice the speed). The idea, in one paragraph and the
frame timeline: a frame of variable length runs `OnUpdate` once; game time advances in fixed steps (1/60 s by default)
that run zero, one or several times per frame, each with physics and `OnFixedUpdate`; then `OnLateUpdate`; an
accumulator holds the time not yet simulated, capped so a long frame does not snowball, and when steps cannot keep up
the game slows (time dilation) instead of freezing. The approaches engines use, each brought in by the flaw of the one
before: a fixed loop tied to the display, a variable delta for everything, a fixed simulation with variable drawing,
in a table of costs with sources. Strata's choice and its reason, with the design decision in a `:::why` aside (game
time counts fixed steps, never frames, home `core/time`): `OnUpdate` per frame, `OnFixedUpdate` per step, the
project's **FixedRate** (Scene, 30, 60, 120 or 240 on the Timing page of Project Settings) over the scene's own fixed
step, time scale as a multiplier of game time (0 pauses it), and `Time`'s delta and fixed delta. The lifecycle: the
base class's comment read whole, then each callback in order (constructed, fields applied, `OnCreate` once all
existing scripts are constructed, the update callbacks, `OnDestroy`; `OnReload` after a hot reload), with the contact
and UI callbacks named with the pages that use them; instances update parents first, then in the order of the
scripts on an entity; inactive entities get no `OnUpdate`, `OnFixedUpdate` or `OnLateUpdate`, and no new contacts or
animation events, while `OnCreate` and `OnDestroy` run anyway and a contact that began still ends with its Exit (the
inventory's slip, `new:22`); a destroyed entity goes at the end of the frame. What Strata does not do here
(`new:21`): no callback when an entity is activated or deactivated (no `OnEnable` or `OnDisable`; `OnCreate` is the
only start). The page's example, with no Coin Run stage: the `Coin` script also bobs, its height from a sine of
`Time::GetElapsedTime()` in `OnUpdate`, with the sine given as a recipe (a value that swings between -1 and 1);
`make/scripting-scene` builds it as its first step. What the choice cannot do: drawing between two steps is the
interpolation that `make/characters-cameras` turns on in code. Common mistakes: constant per-frame moves; putting in
`OnFixedUpdate` what must happen once a frame, since fixed updates run zero, one or several times a frame (the presses
of a key are that case, and `make/physics` shows it); blocking a script or starting threads in it, which stops the
whole frame. At the end the reader can say which callback runs when, why physics needs fixed steps,
and what time scale and FixedRate change.

**Leaves out.**

- The clock, the accumulator and time dilation as the engine runs them → `core/time`
- The fixed step's code in `Scene` → `world/systems`
- The script system's dispatch and order inside → `scripting/script-system`
- Drawing between steps, `GetDrawnPosition` → `make/characters-cameras`, `world/interpolation`
- Timers, unscaled time and the clocks of `Time` → `make/timers-events`
- Pausing a game with a menu at time scale 0 → `make/menus`
- Pausing and stepping in the editor → `make/play-test-debug`
- Sine and cosine as mathematics → `basics/math-vectors`

**Fit.** `over`: about 4,050 words against M (3,000). Five ideas taught from zero at B0's length, the approaches table,
the base class's comment, the bob's code, two figures, three mistakes and the exercise take it over M's top. L (5,000)
by S2: the page is the home of the lifecycle and the use home of the fixed step at once, and neither half can move to
another page of track B.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:361` | code | home | `StrataScriptCore/Include/StrataScript/Script.h:30-47`: the base class's comment, every callback and when it runs, update order and inactive entities |
| `gamedev:70` | feature | use | Scene settings: the fixed timestep and the steps per frame, greyed when the project's FixedRate rules; the item's home, with the Physics section, is `make/physics` |
| `gamedev:126` | feature | home | The 15 lifecycle callbacks; only those a class overrides are called |
| `gamedev:156` | feature | home | Timing: FixedRate; its Interpolation switch named for `make/characters-cameras` |
| `gamedev:158` | feature | home | Time dilation: the game slows instead of spiralling |
| `gamedev:286` | concept | home | What a game is to a computer: a loop of frames and fixed steps; the mistakes (per-frame amounts; what must happen once a frame put in `OnFixedUpdate`, which runs zero to N times a frame). The press half of the second mistake is `make/physics`' with its rule `gamedev:488` |
| `gamedev:321` | concept | home | The script lifecycle and its order: `OnCreate` after construction, parents first, destruction at the end of the frame; inactive entities get no update callbacks, while `OnCreate` and `OnDestroy` run anyway (`new:22`) |
| `gamedev:405` | figure | home | The frame timeline from a script's side, with the accumulator at 30, 60 and 144 Hz |
| `gamedev:412` | figure | home | The script lifecycle as a state machine, with the hot reload branch |
| `gamedev:497` | rule | home | Never block or start threads in a script |
| `gamedev:615` | term | home | Fixed step |
| `gamedev:616` | term | home | Accumulator |
| `gamedev:617` | term | home | Time scale |
| `gamedev:620` | term | home | Time dilation |
| `scripting:289` | concept | home | The script lifecycle: the callbacks, their order and the instance's states; what an inactive entity still gets (`OnCreate`, `OnDestroy`, the Exit of a contact that began) and what it does not (update callbacks, new contacts, animation events) |
| `new:21` | not-done | home | Callbacks when an entity is activated or deactivated: no `OnEnable` or `OnDisable`; `OnCreate` is the only start. Evidence: `StrataScriptCore/Include/StrataScript/Script.h:83-97`, the 15 callbacks; `git grep -n -e OnEnable -e OnDisable 822a7a46 -- StrataScriptCore Strata/src` finds nothing (run at the pin) |
| `new:22` | erratum | home | `plan/inventory/gamedev.md:322` says that inactive entities get nothing. At the pin they get no `OnUpdate`, `OnFixedUpdate` or `OnLateUpdate`, but `OnCreate` and `OnDestroy` run regardless, and a contact that began before the entity was deactivated still ends with its Exit. The page states the code's facts; its brief says that no test covers the `OnCreate` half (the test of inactive entities deactivates them after the start: `StrataTests/src/Scripting/ScriptLifecycleTests.cpp:131-158`). Evidence: `Strata/src/Strata/Scripting/ScriptSystem.cpp:276-280`, `:347-352` (contacts begin for active entities only), `:394` (animation events), `:664-679`; `Strata/src/Strata/Scripting/ScriptSystem.h:55-56`; `StrataScriptCore/Include/StrataScript/Script.h:57-58` (read at the pin) |
| `scripting:570` | term | home | Callback, in the meaning of scripts |
| `scripting:587` | term | home | Fixed update |
| `foundation:184-185` | feature | use | The accumulator and time dilation as Strata runs them, at the maker's level |
| `foundation:187` | feature | use | The project's FixedRate |
| `foundation:228` | concept | use | The fixed timestep, the accumulator and time scale, at the maker's level |
| `foundation:406` | figure | use | The fixed step on a time axis |
| `foundation:539` | hands-on | use | One object moved in `OnUpdate` and one in `OnFixedUpdate`, as an exercise |
| `scene-ecs:112-113` | feature | use | The project's rate over `SceneSettings` |
| `scene-ecs:222` | feature | use | The `Scene.Timing` section on the Timing page |
| `scene-ecs:316` | concept | use | Game loop time, at the maker's level |
| `scripting:92` | feature | use | The 15 class callbacks |
| `scripting:123` | feature | use | The SDK's `Time` |
| `scripting:165` | feature | use | Update order: parents first, then script order |
| `scripting:294` | concept | use | Deferred destruction at the end of the frame |
| `scripting:411` | figure | use | The instance lifecycle state machine |
| `scripting:414` | figure | use | A frame timeline for scripts |
| `scripting:462` | rule | use | The engine calls scripts on one thread; never call it from threads of your own |
| `scripting:479` | rule | use | Never block in a script |
| `scripting:483` | rule | use | The root of the rule: what must happen once a frame goes in `OnUpdate`; the press and release edges themselves are `make/physics`' |
| `editor-ui:187` | feature | use | The scene settings' fixed rate link with nothing selected |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The `Coin` script, `OnUpdate` and `deltaTime`, building and hot reload | `make/first-script` | must |
| Variables, `if`, loops, functions, classes and members | `basics/programming-3` | must |
| The frame map and frame time | `start/what-an-engine-is` | must |
| Project Settings and its pages | `make/project-files` | must |
| Sine as a wave between -1 and 1 | `basics/math-vectors` | helps |
| Breakpoints and the log | `basics/debugging` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `fixed-update` | Fixed update | - |
| `callback` | callback (use) | - |
| `accumulator` | accumulator (use) | - |
| `fixed-step` | fixed step (use) | - |
| `time-dilation` | time dilation (use) | - |
| `time-scale` | Time scale (use) | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-a-13 | should | order | `make/project-coin-run` (steps 1, 2 and 5; `new:48`) | The round needs scripts that talk to each other, and block A never teaches it: `GetScript<T>` is `make/timers-events`', a page of block B on track G only. The HUD's timer (`CoinHud`, from `Time`) and the round's time left (a field of `CoinRunGame`, with a difficulty field) would disagree; "the ball stops" names no means; and `new:48`'s Basic exercise sums the coins' `Points` field in the HUD. | `CoinRunGame` takes over the timer's text and the time bar from `CoinHud`, so one script owns the round's time; the ball stops with `Time::SetTimeScale(0)` (taught on `make/script-loop`; a scene reload starts at 1), or with `RemoveScript("BallControl")` and its velocity set to zero; `new:48`'s Basic exercise counts a second tag (`BigCoin`, worth five) with `FindEntitiesByTag` (about 80 words). The other way is in forPlanner. | `allocation/make-a.md:1079`, `:1519-1520`, `:1806-1813`, `:1845`; `allocation/make-b1.md:89`, `:103-104`; `outline-1.md:77-81`, `:203`; `StrataScriptCore/Include/StrataScript/Entity.h:88`, `:93`; `StrataScriptCore/Include/StrataScript/Time.h:43-53`; `Strata/src/Strata/Scene/Scene.h:463`, `:924` |
| critic-make-a-17 | should | stale-item | `make/script-loop` | "What the choice cannot do" says that drawing between two steps is interpolation that `make/characters-cameras` turns on in code. At the pin it is on by default: the project's Timing page has **Interpolation**, on, so what moves in fixed steps is drawn between its last two steps. `make/characters-cameras` reads the drawn position for a camera and turns the switch off only to compare. | The sentence says that fixed-step motion is drawn between its last two steps (**Timing ▸ Interpolation**, on by default), so a script reads where a body is simulated, not where it is drawn, and a camera that follows it reads the drawn position (`make/characters-cameras`) (about 50 words). | `allocation/make-a.md:965-966`, `:995`; `allocation/make-b1.md:512`, `:514`; `Strata/src/Strata/Scene/ProjectSceneTiming.cpp:65-68`; `Strata/src/Strata/Scene/ProjectSceneTiming.h:11-13`; `StrataScriptCore/Include/StrataScript/Entity.h:204-206` |
