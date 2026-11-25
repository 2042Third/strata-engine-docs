# Brief: `make/patterns`

| Field | Value |
| --- | --- |
| Title | Patterns for game code: state machines, managers and object pools |
| Kind | C |
| Size | L |
| Tracks | G |
| Needs | `make/timers-events`, `make/script-fields` |
| From | new; curricula 1.13; Nystrom, *Game Programming Patterns* (State, Update Method, Object Pool); state machines, managers, object pools, and showing and hiding instead of creating and destroying; examples from the samples' scripts |
| Unit | `plan/allocation/make-b1.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/patterns` — Patterns for game code: state machines, managers and object pools

**Covers.** A concept page about the shapes game code takes once it grows. The problem as a reader meets it: a script
like Coin Run's, grown for a week, with flags (`isPaused`, `isDead`, `hasWon`) that contradict each other, every coin
looking for the score, and bullets created and destroyed many times a second. The naive answers (more flags, a search
for the scoreboard on every coin, `Instantiate` and `Destroy` for everything) and where each breaks. Then the idea: name
the states, give shared work one owner, and keep objects instead of remaking them. The approaches follow, each from the
flaw of the one before, with a table of what each costs and which engines use them (Nystrom's *Game Programming
Patterns*: State, Update Method, Object Pool; Unity's and Godot's habits for comparison):

1. State machines: flags, then a scoped enum with a `switch` (the page's guard, which patrols, chases and returns, is
   the running example; it is also the answer to "where is the AI": Strata has none, see below), then states that own
   their enter and exit code; the excerpt of the Third-Person pause menu, whose Pause action moves between playing,
   paused and "settings open"; an animation controller is a state machine kept as data, which `make/animation` edits.
2. The update method: the engine already calls every script's `OnUpdate` and `OnFixedUpdate` in a known order; game code
   does not need its own loop.
3. Managers: one script on an entity named "Game" that owns the course's state (the Third-Person sample's
   `CourseState`), found by name by whoever needs it (the coins), against a global variable or a singleton; state that
   must outlive a scene is `make/levels-saves`'.
4. Object pools and showing instead of creating: entities made once in `OnCreate` and switched with `SetActive`; the
   Tetris board's 200 cells, found again in `OnReload` instead of made twice; the board's `Refresh`, which compares what
   it shows with what it should show and touches only what changed (a material set, an entity shown or hidden, a HUD
   text rewritten only when its number changed). An inactive pooled entity gets no `OnUpdate`, `OnFixedUpdate` or
   `OnLateUpdate`, but `OnCreate` and `OnDestroy` still run, and a contact that began before it was deactivated still
   ends with its Exit.

Strata's choice, in a `:::why` aside: no gameplay framework above the script lifecycle. Game code is script classes on
entities, and these patterns are plain C++ in them; the samples use all four. One sentence says that Strata has no game
AI (steering, pathfinding, navigation meshes, behaviour trees), so a guard is a state machine in a script, and links
`appendix/game-ai`, which holds the absence and the general techniques. Common mistakes: a flag for every state, a
pointer to another script kept across frames, destroying and creating what could be hidden, creating the pool again in
`OnReload`. The exercises: the guard's flags turned into a scoped enum with a `switch`; a pool of bullets made once and
switched with `SetActive`, done in a script; a design question on where a score that outlives a scene lives. At the end
the reader can choose a pattern for a growing script and recognize each pattern in the samples.

**Leaves out.**

- Timers, key repeat, and scripts that find each other → `make/timers-events`
- Animation state machines as game makers edit them → `make/animation`
- State that survives a scene switch → `make/levels-saves`
- Recipes built on these patterns (the coin, the grab tool, the sound budget) → `make/recipes`
- Game AI techniques in general → `appendix/game-ai`
- Tetris built whole, with its rules class → `make/project-tetris`
- The script lifecycle and its order → `make/script-loop`
- How the engine dispatches script updates → `scripting/script-system`

**Fit.** `fits`: about 5,400 words against L (5,000). The four patterns taught from zero for a reader who has written
only block A's scripts, with their three excerpts (about 2,550 words), take the most, then the problem and its naive
answers, the three diagrams (the guard's states, a manager and its callers, a pool's life), the three exercises, the
approaches table and the common mistakes.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:374` | code | home | `Samples/Tetris/Scripts/TetrisBoard.cpp:282-369`: `Refresh` and `ShowCell`, touching only what changed: the cached shown state, `SetActive`, the material by `SetProperty`, HUD texts rewritten only when their numbers changed |
| `new:2` | code | home | `Samples/ThirdPerson/Scripts/CourseState.h:7-39`: a manager, the course's state on its "Game" entity, which the coins call through `AddCoin`. No inventory surveyed the file (`plan/inventory/gamedev.md:694-696`) |
| `new:3` | code | home | `Samples/ThirdPerson/Scripts/PauseMenu.cpp:38-52`: a small state machine: one action moves between playing, paused and "settings open". No inventory surveyed the file (`plan/inventory/gamedev.md:694-696`) |
| `new:4` | not-done | link | No game AI: steering, pathfinding, navigation meshes and behaviour trees are left to scripts; the page says so in one sentence and links `appendix/game-ai`, the home of the absence. Evidence: `git grep -niE -e pathfind -e navmesh -e "nav mesh" -e "navigation mesh" -e "behaviou?r ?tree" -e steering 822a7a46 -- Strata/src StrataScriptCore` finds nothing (the word "navigation" alone matches only the game UI's focus navigation: `Strata/src/Strata/GameUI/`, `Strata/src/Strata/Input/UIActions.h`, `Strata/src/Strata/Scene/SceneServices.h`) |
| `new:17` | erratum | home | `Samples/Tetris/README.md:14` says that the sample's cells are "created and destroyed by a script"; the board creates its cells once and then only shows, hides and recolors them. Evidence: `Samples/Tetris/Scripts/TetrisBoard.cpp:222-247` (`CreateCells`, `CreateCell`), `:355-369` (`ShowCell`); `git grep -n Destroy 822a7a46 -- Samples/Tetris/Scripts` finds nothing |
| `new:18` | erratum | home | The gamedev survey says that inactive entities get nothing (`plan/inventory/gamedev.md:322`); they get no `OnUpdate`, `OnFixedUpdate` or `OnLateUpdate`, but `OnCreate` and `OnDestroy` run regardless, and a contact that began before the entity was deactivated still ends with its Exit. Evidence: `Strata/src/Strata/Scripting/ScriptSystem.cpp:276-280`; `Strata/src/Strata/Scripting/ScriptSystem.h:55-56`; `Strata/src/Strata/Scripting/ScriptSystem.cpp:664-679` (`RunPendingStarts` reads no activity); `StrataScriptCore/Include/StrataScript/Script.h:57-58` |
| `new:19` | hands-on | home | Exercises: the guard's three flags turned into a scoped enum with a `switch` (modify); a pool of 20 bullets made in `OnCreate` and switched with `SetActive`, against `Instantiate` and `Destroy` for every shot, done in a script; where a score that must outlive a scene switch lives (design). Evidence: `StrataScriptCore/Include/StrataScript/Entity.h:51` (`SetActive`), `:59` (`Destroy`); `StrataScriptCore/Include/StrataScript/Scene.h:156-174` (`Instantiate`) |
| `gamedev:373` | code | use | The Tetris board making its cells once and finding them again in `OnReload` (its home is `make/project-tetris`) |
| `gamedev:372` | code | use | The Tetris rules class kept apart from the engine, named as a state kept in plain C++ (its home is `make/project-tetris`) |
| `scripting:385` | code | use | Lines 38-46 of `Coin.cpp`: a caller of the manager (its home is `make/recipes`) |
| `gamedev:321` | concept | use | The lifecycle's order: `OnCreate` after every script exists, updates parents first, destruction at the end of the frame (its home is `make/script-loop`) |
| `animation:283` | concept | link | State machines for animation, named as the data form of the same pattern (`animation/state-machines`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The script lifecycle and its order; destruction at the end of the frame | `make/script-loop` | must |
| Finding, spawning, hiding and destroying entities from a script | `make/scripting-scene` | must |
| Scripts that find each other each time; timers | `make/timers-events` | must |
| Scoped enum values and `switch` | `basics/programming-1` | must |
| `std::vector` and loops | `basics/programming-2` | must |
| Classes and member functions | `basics/programming-3` | must |
| Entity and asset fields set in the Inspector | `make/script-fields` | must |
| Prefabs | `make/prefabs` | must |
| Hot reload and `OnReload` | `make/first-script` | must |
| Contacts and triggers | `make/physics` | must |
| Animation controllers | `make/animation` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-b1-10 | should | order | recipe 4 of `make/recipes`; the managers of `make/patterns` | Recipe 4's token bucket is a variable outside any class, in an unnamed namespace of `Impact.cpp`, shared by the `Impact` script of every body; that sharing is the recipe. The page's Assumes row sends the reader to `make/levels-saves` (helps), which stands five pages later on track G, so no page before has taught it. `make/patterns`, which `make/recipes` needs, already compares a manager with a global variable. | The managers section of `make/patterns` says what such a variable is: one for the whole module, shared by every script, kept while the module stays loaded; and when it fits, such as a sound budget (about 100 words). The Assumes row of `make/recipes` then names `make/patterns` (must). `make/levels-saves` keeps the lifetime (`new:37`) and the use across scenes. | `allocation/make-b1.md:267-269`, `:352-355`, `:409`; `tracks.md:105-111`; `Samples/PhysicsPlayground/Scripts/Impact.cpp:13-36` |
| critic-make-b1-14 | should | stale-item | `new:19` and the object pools of `make/patterns` | The pool is "made once in `OnCreate`", and the exercise makes "a pool of 20 bullets made in `OnCreate`". If the bullets are instances of a prefab, `Scene::Instantiate` returns a null entity while the prefab loads, and it never waits. So a pool filled in `OnCreate` may hold no bullets at all, as at the start of Play, when nothing has asked for the prefab yet. The Tetris board avoids this: it builds its cells with `CreateEntity` and `AddComponent`. | The pool section and `new:19` say: ask for the prefab in `OnCreate` and fill the pool in the first update where `Assets::IsLoaded` is true, or build the pooled entities with `CreateEntity`, as Tetris does (about 60 words). | `allocation/make-b1.md:270-271`, `:282-283`, `:312`; `StrataScriptCore/Include/StrataScript/Scene.h:152-156`; `Samples/Tetris/Scripts/TetrisBoard.cpp:222-247`; `Samples/PhysicsPlayground/Scripts/Playground.cpp:209-212` |
| critic-make-b1-21 | could | duplicate | `new:18` on `make/patterns` | `new:18` corrects the gamedev survey's "inactive entities get nothing". `make/script-loop` (unit `make-a`) homes the same erratum as its `new:22`, with the same evidence. One erratum has two homes, and the check cannot see it, because both are new items. | `make/script-loop`, earlier on track G, keeps the erratum (`critique/rulings-10.md`, R46: the row of the earlier page stays). On `make/patterns` the row `new:18` goes; the pool section keeps its sentence and its `use` row of `gamedev:321`. | `allocation/make-b1.md:273-275`, `:311`, `:316`; `allocation/make-a.md:998`, `:1008`; `critique/rulings-10.md:72-74`; `tracks.md:89`, `:105` |
