# Brief: `make/recipes`

| Field | Value |
| --- | --- |
| Title | Building blocks and recipes |
| Kind | H |
| Size | L |
| Tracks | G |
| Needs | `make/patterns`, `make/gameplay-math` |
| From | scripting "Building blocks and recipes": `Random` and seeds, recipes from the samples (Coin, the Tetris board), exercises; `Timer` and `KeyRepeat` are `make/timers-events`', `Motion` is `make/gameplay-math`' |
| Unit | `plan/allocation/make-b1.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/recipes` — Building blocks and recipes

**Covers.** A how-to of recipes taken from the samples. Each recipe says what it does, where its sample has it, the
numbered steps that add it to the reader's project, and what to change to make it one's own. It opens with `Random`:
`Range` for whole numbers (a die) and for decimals, `NextFloat`, `Chance`; a seed in a field gives the same sequence on
every computer, an unseeded generator always gives the same one, and a seed from something that varies (a level number)
gives variety; then a deterministic replay: seed from a field, record the outcomes, play again and get them again. Then
the recipes:

1. The coin (Third-Person `Coin.cpp`): spin and bob, collect once on a trigger tagged "Player", tell the manager, hide;
   `OnReload` calling `OnCreate` to find its model again.
2. The seeded pour (Physics Playground `SpawnBalls`): balls in a loose column, each nudged by `Random` from a seed, so
   the same seed pours the same pile; the call that makes them all at once, `Scene::InstantiateMany`, is given with its
   one line per transform, and `make/performance` teaches it.
3. The grab tool (Physics Playground `UpdateGrab`): a ray through the cursor, `Physics::Raycast` for the body under it,
   then a velocity toward a point in front of the camera, proportional to the distance and capped at 20 m/s, with the
   spin damped.
4. Impact sounds with a budget (Physics Playground `Impact.cpp`): the hit's strength from the bodies' speed along the
   contact's normal, volume and pitch from it, `Audio::PlayOneShotAt` at the contact point, and a token bucket shared by
   every body (at most 8 sounds in a frame and 16 a second on average), so a pour of hundreds of contacts plays a few
   voices. This finishes G12, the exercise of `make/gameplay-math`.

The Open World sample's day and night script (`DayNight.h`, hands-on G16) is a recipe of `make/reflections`, beside the
times of day with baked probes; one sentence names it and links there. The exercises, done in a script: the coin made to
come back after a delay with a `Timer`, and the pour seeded from the level number, so that each level pours its own
pile and the same level the same one. At the end the reader can use seeded randomness for variety and for replays, and
can take a recipe from a sample's script into a game and change it.

**Leaves out.**

- `Timer` and `KeyRepeat` → `make/timers-events`
- `Motion`, `LookAt`, `SmoothDamp` and the pointer ray → `make/gameplay-math`
- Probability, generators and seeds as mathematics → `basics/math-probability`
- Many instances in one call → `make/performance`
- A day and night cycle (`DayNight.h`, G16), and times of day with baked reflection probes → `make/reflections`
- Raycasts, masks and contacts → `make/physics`
- The Tetris board, its rules class and its seeded 7-bag → `make/project-tetris`

**Fit.** `fits`: about 4,700 words against L (5,000). Four recipes of about 700 to 800 words each (an introduction, an
excerpt, three steps with their results, what to change) and the `Random` section with its replay (about 800) take the
most; the day and night recipe is one sentence that links `make/reflections`.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scripting:385` | code | home | `Samples/ThirdPerson/Scripts/Coin.cpp:1-59`: a complete small game script: fields, `OnCreate` and `OnReload`, spin and bob in `OnUpdate`, `OnTriggerEnter` collecting once and calling `CourseState` |
| `gamedev:383` | code | home | `Samples/PhysicsPlayground/Scripts/Playground.cpp:223-275`: the grab, a velocity toward a target with a speed cap, and the seeded pour with `Random` jitter (its `InstantiateMany` line read as given) |
| `gamedev:384` | code | home | `Samples/PhysicsPlayground/Scripts/Impact.cpp:13-61`: the token bucket shared by every body, and the hit's strength from the velocities along the contact's normal |
| `gamedev:386` | code | link | The day and night script `DayNight.h`, named in one sentence (`make/reflections`) |
| `physics:450` | hands-on | home | The grab tool, built as `UpdateGrab` builds it |
| `gamedev:549` | hands-on | link | G16, the day and night script, named in the same sentence (`make/reflections`) |
| `scripting:527` | hands-on | home | A deterministic replay: `Random` seeded from a field, outcomes recorded and reproduced |
| `gamedev:663` | term | home | Seed |
| `gamedev:664` | term | home | Token bucket |
| `scripting:133` | feature | home | `Random` in the SDK: PCG32, the same on every platform, unbiased whole-number ranges by rejection; `reference/script-api` lists the declarations and links here |
| `scripting:343` | concept | home | Determinism helpers: a seeded generator gives the same sequence on every computer, which the replay builds on; the SDK's helpers (PCG32 with unbiased ranges, timers that keep their overshoot, critically damped smoothing) are compiled into the script module and behave the same everywhere; why they live in the module is `scripting/abi-sdk`'s |
| `new:20` | hands-on | home | Exercises, done in a script: the coin made to come back after a delay with a one-shot `Timer` (shown again with `SetActive`); the pour seeded from the level number, so that each level pours its own pile and the same level the same one. Evidence: `Samples/ThirdPerson/Scripts/Coin.cpp:1-59`; `StrataScriptCore/Include/StrataScript/Gameplay.h:23-110` (`Random`, its seed), `:115-176` (`Timer`); `StrataScriptCore/Include/StrataScript/Entity.h:51` |
| `physics:325` | code | use | The physics survey's excerpt of the same `UpdateGrab` (its home is `physics/queries`) |
| `gamedev:545` | hands-on | use | G12, whose impact sounds with a budget this page finishes (its home is `make/gameplay-math`) |
| `gamedev:387` | code | link | Times of day with baked probes switched with an overlap (`make/reflections`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Raycasts, velocities, triggers, contacts and their normals | `make/physics` | must |
| The pointer ray and the dot product | `make/gameplay-math` | must |
| One-shot sounds at a position, and asking for clips early | `make/sound` | must |
| Managers and state machines | `make/patterns` | must |
| Scripts that find each other each time | `make/timers-events` | must |
| Entity and asset fields set in the Inspector | `make/script-fields` | must |
| Opening a sample as a copy | `start/first-game` | must |
| Finding entities by tag and setting a property by name | `make/scripting-scene` | must |
| Variables outside a class, shared by every instance in the module | `make/levels-saves` | helps |
| Seeds, generators and uniform ranges as mathematics | `basics/math-probability` | helps |

**Starting state.** No checkpoint: each recipe opens its sample as a copy from the launcher (Third-Person for the coin,
Physics Playground for the pour, the grab and the impact sounds) to read the script at work, then adds it to a new
project from the Basic 3D template. The `Random` section starts in that new project.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `token-bucket` | Token bucket | - |
| `seed` | seed (use) | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-b1-3 | should | shape | `make/gameplay-math`, `make/timers-events`, `make/script-fields`, `make/script-builds`, `make/levels-saves` | style.md gives a how-to a `## Variations` section: the same goal under other conditions. The Covers of these five how-tos name no variation, so the writer has nothing to fill it with. The how-tos of `make-a` and `make-b2` name theirs. (`make/recipes` has its "what to change" per recipe.) | Each Covers names two variations (about 250 words a page). From the pin: gameplay-math, aiming with the right stick through the Look action instead of the cursor (`FollowCamera.cpp:57-60`), and a turret that turns at a limited speed (critic-make-b1-16); timers-events, a timer in `OnFixedUpdate` fed with the fixed delta, for gameplay that keeps step with physics, and a held gamepad direction repeated (critic-make-b1-5); script-fields, tuning many spawners at once through their prefab (critic-make-b1-4); script-builds, the plain `cmake -S` and `-B` build as a check that the code compiles on another machine (critic-make-b1-1); levels-saves, three save slots named "Slot 1" to "Slot 3" and listed with `ListSaveFiles`. The five Fit lines count them. | `style.md:535-541`; `allocation/make-b1.md:5-24`, `:91-111`, `:174-193`, `:420-440`, `:922-962`; `allocation/make-a.md:130`, `:424`; `allocation/make-b2.md:393`; `StrataScriptCore/Include/StrataScript/Game.h:104-107`, `:157-158` |
| critic-make-b1-10 | should | order | recipe 4 of `make/recipes`; the managers of `make/patterns` | Recipe 4's token bucket is a variable outside any class, in an unnamed namespace of `Impact.cpp`, shared by the `Impact` script of every body; that sharing is the recipe. The page's Assumes row sends the reader to `make/levels-saves` (helps), which stands five pages later on track G, so no page before has taught it. `make/patterns`, which `make/recipes` needs, already compares a manager with a global variable. | The managers section of `make/patterns` says what such a variable is: one for the whole module, shared by every script, kept while the module stays loaded; and when it fits, such as a sound budget (about 100 words). The Assumes row of `make/recipes` then names `make/patterns` (must). `make/levels-saves` keeps the lifetime (`new:37`) and the use across scenes. | `allocation/make-b1.md:267-269`, `:352-355`, `:409`; `tracks.md:105-111`; `Samples/PhysicsPlayground/Scripts/Impact.cpp:13-36` |
| critic-make-b1-11 | should | missing-item | Starting state and recipes of `make/recipes` | Each recipe "adds it to a new project", but no step says what the reader copies, and the samples' scripts depend on others. `Coin.cpp` includes `CourseState.h`, whose source includes `ThirdPerson.h` and `ThirdPersonPlayer.h`. The grab and the pour are member functions of the large `Playground` class. `Impact.cpp` finds its sounds by path, so they must exist at `Sounds/Impacts/...` in the new project, and a pruned export must list them under Always Include. A reader who copies `Coin.cpp` alone gets compile errors. | The Starting state and each recipe say that the reader writes a script of their own from the excerpt (the coin calls the `Scoreboard` of `make/timers-events` instead of `CourseState`), which sounds to copy with the file browser and import, and one sentence that sounds found by path need Always Include (`make/export`). About 200 words. | `allocation/make-b1.md:337-355`, `:412-414`; `allocation/make-a.md:1752`; `Samples/ThirdPerson/Scripts/Coin.cpp:4`, `:43-44`; `Samples/ThirdPerson/Scripts/CourseState.cpp:3-4`; `Samples/PhysicsPlayground/Scripts/Playground.h:76`, `:79`; `Samples/PhysicsPlayground/Scripts/Impact.cpp:1-4`, `:18`, `:63-77` |
| critic-make-b1-19 | could | missing-item | `make/timers-events`; the replay of `make/recipes` | `Timer`, `KeyRepeat` and `Random` are plain members, not fields, so a hot reload starts them over. A cooldown restarts, and a seeded `Random` begins its sequence again in the middle of a game, which breaks the recorded replay of `make/recipes`. The SDK's header says to make them again in `OnReload` or keep what matters in fields; neither page says it. | One sentence on each page, where `Timer` and the replay are taught (about 40 words each). | `allocation/make-b1.md:93-96`, `:338-341`; `StrataScriptCore/Include/StrataScript/Gameplay.h:12-14`; `Docs/Manual/Scripting.md:177-181` |
| critic-make-b1-22 | could | other | the pointer ray of `make/gameplay-math`; the check "Mouse units on a scaled display" | The pointer ray divides `Input::GetMousePosition` by `Game::GetWindowSize`. critic-audio-input-7 suspects that the two differ on a scaled display in an exported game, and its check names only `input/mouse-cursor`. The recipe, G12 and the grab tool of `make/recipes` rest on the same division, so the check's result would not reach them. | The check's pages include `make/gameplay-math` and `make/recipes`; the pointer-ray recipe holds an item of type `open` ("Check: Mouse units on a scaled display.") until the result is in. | `allocation/README.md:282`; `allocation/completeness.md:101`; `allocation/make-b1.md:17-18`, `:49`; `Samples/PhysicsPlayground/Scripts/Playground.cpp:183-207`; `StrataScriptCore/Include/StrataScript/Input.h:274` |
