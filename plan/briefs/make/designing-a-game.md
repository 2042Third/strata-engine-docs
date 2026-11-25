# Brief: `make/designing-a-game`

| Field | Value |
| --- | --- |
| Title | Planning a small game: the core loop, scope, prototype and playtest |
| Kind | C |
| Size | M |
| Tracks | G |
| Needs | `make/project-coin-run` |
| From | new; curricula 1.13; gamedev concept 23 (testing); the core loop, scope, a prototype and a playtest, with the samples' READMEs as examples; each project page opens with its one-paragraph design |
| Unit | `plan/allocation/make-c.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/designing-a-game` — Planning a small game: the core loop, scope, prototype and playtest

**Covers.** The page opens with a problem every reader of block C meets: after Coin Run and the toolbox of block B,
the reader wants to make "a real game", and the first idea is usually far too big. The reader lists what a large
adventure would need and compares the list with the two games block C builds: Tetris is three source files of 829
lines and one scene; Sky Islands is 18 source files of 1,720 lines and three scenes. The naive answer, building
everything at once from a long document, breaks there: nothing is playable for weeks, nobody knows whether it is fun,
and nothing can be cut. The idea follows: the **core loop**, the short cycle the player repeats every few seconds,
shown as a diagram for Tetris (a piece falls, the player moves and turns it, it locks, rows clear, the score rises,
gravity speeds up) and for Sky Islands (run, jump, collect coins, reach a checkpoint, finish faster). Then the
approaches, each brought in by the flaw of the one before: a design document first, a paper prototype, a grey box
built in the editor from built-in meshes, and a vertical slice, ending with a table of what each costs, what it tests
and who uses it. **Scope** is taught as a cut list (must, should, could), with the platformer's own cuts as the example
(lanterns, probes, the Graphics row and the attract mode are "could").

Strata's part is the samples' way of working, stated once in a `:::why` aside: design the code so that tools can check
it, with the rules in a plain class, randomness from a seed field, tuning as fields that change while the game plays,
and one log line per event (`.claude/skills/strata-make-a-game/SKILL.md:53-62`). The **one-paragraph design** that
each project page opens with is taught next, from the samples' READMEs, and the reader writes one as the page's
`:::example`. **Playtests** with people close the page: watch without explaining, note where the player stops, change
one thing, test again; a play-test that a machine runs is a different tool, linked to its page. What the choice cannot
do: a tool can check the rules, never the fun. Common mistakes: scope that grows, polish before the loop works, testing
only by yourself, numbers changed in code instead of in fields. The exercises: the core loop and the cut list of Coin
Run (a design exercise), then a grey box of the reader's own design built in the editor and play-tested with one person
(an editor task). At the end the reader can write a one-paragraph design with a core loop and a cut list for a game of
their own, and knows how to test it with a person.

**Leaves out.**

- State machines, managers and object pools for game code → `make/patterns`
- Play-tests that a command script runs, and regression tests → `make/automated-playtests`
- Finding the same bug twice: same inputs, same game → `make/play-test-debug`
- Game AI: steering, pathfinding and behaviour trees → `appendix/game-ai`
- Planning and building a game with an AI agent → `make/with-an-agent`
- Reading the samples' code and READMEs in depth → `make/samples`
- Asset licenses for a prototype's downloaded assets → `make/assets`
- Building the two designs → `make/project-tetris`, `make/project-platformer`

**Fit.** `over`: about 4,100 words against M (3,000). Counted again from the sections: the problem and the naive
answer (about 400 words), the core loop with its diagram (470), the approaches with their table (500), scope (350),
the one-paragraph design with its example (400), playtests (350), Strata's aside, what the choice cannot do and four
common mistakes (530), the two exercises (500) and the fixed parts (600), with no code excerpt. Over M's top of
4,000, the page takes L by S2 (4,001 to 6,500 words), which the second size pass decides.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:1` | concept | home | The core loop: the short cycle a player repeats, found by asking what the player does every few seconds; Tetris's loop and Sky Islands' loop as the examples. Evidence: `Samples/Tetris/README.md:3-5`; `Samples/ThirdPerson/README.md:3-7` |
| `new:2` | concept | home | Scope as a cut list of must, should and could, with the samples' sizes as a yardstick: Tetris has three source files of 829 lines and one scene, Sky Islands 18 source files of 1,720 lines and three scenes. Evidence: `Samples/Tetris/Scripts/TetrisGame.h:108`, `TetrisGame.cpp:269` and `TetrisBoard.cpp:452` (the last lines); `git ls-tree -r --name-only 822a7a46 -- Samples/ThirdPerson/Scripts` lists 18 `.cpp` and `.h` files besides `CMakeLists.txt` and `.gitignore`, 1,720 lines in all; `Samples/ThirdPerson/Assets/Scenes/` holds `MainMenu`, `Course` and `Loading` |
| `new:3` | concept | home | The approaches to planning a game: a design document first, a paper prototype, a grey box in the engine, a vertical slice; a table of their cost, what each tests (the loop, the feel, the content) and who uses them, with sources in Further reading. General knowledge. |
| `new:4` | concept | home | Playtests with people: watch without explaining, note where the player stops or is lost, change one thing, test again; how this differs from a play-test a machine runs. General knowledge. |
| `new:5` | concept | home | The one-paragraph design that each project page of block C opens with: what the player does, the core loop, how the game is won and lost, the controls, and what is left out. Evidence: `Samples/Tetris/README.md:3-5`; `Samples/ThirdPerson/README.md:3-7`; `Samples/PhysicsPlayground/README.md:3-6` |
| `new:6` | concept | home | Strata's way of working, in a `:::why` aside: design the code so that tools can check it (rules in a plain class, randomness from a seed field, tuning as fields, one log line per event). Evidence: `.claude/skills/strata-make-a-game/SKILL.md:53-62` |
| `new:7` | figure | home | Diagram: the core loops of Tetris and of Sky Islands as two cycles side by side. Evidence: `Samples/Tetris/README.md:3-5`; `Samples/ThirdPerson/README.md:3-7` |
| `gamedev:254-255` | feature | use | The two samples that block C follows, as the examples of a core loop, a scope and a one-paragraph design |
| `gamedev:256-258` | feature | link | The other three samples, named as further examples of a small scope |
| `gamedev:346` | concept | use | Testing a game: determinism and observability, named as the reason for designing the code for tools; the automated play-test is linked; the page uses it for play-tests by people |
| `new:25` | hands-on | home | Exercise (Basic, design): the core loop of Coin Run written as a cycle, and its features sorted into must, should and could; the answer discusses good cut lists. General knowledge. |
| `new:26` | hands-on | home | Exercise (Medium, editor task): the core loop of the reader's own one-paragraph design built as a grey box from the built-in meshes of the Hierarchy's "+" menu in a project from the Basic 3D template, played by one person without explaining, one change, played again; the worked solution is a command script that builds a small grey box. Evidence: `StrataEditor/src/Panels/SceneHierarchyPanel.cpp:72-89` |
| `gamedev:516` | rule | link | Deterministic play-tests need seeds and fixed steps: one sentence in the aside |
| `gamedev:663` | term | link | Seed, used in the aside |
| `automation:224` | feature | link | The `strata-make-a-game` skill, the playbook the samples were made by |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Game flow: levels, win, lose, restart | `make/project-coin-run` | must |
| The finished Coin Run, which the page compares with the projects | `make/project-coin-run` | must |
| One frame, start to finish; frame time | `start/what-an-engine-is` | helps |
| Built-in meshes from the Hierarchy's "+" menu, for a grey box | `make/scenes-entities` | helps |
| Fields changed in the Inspector while the game plays; hot reload | `make/first-script` | helps |
| `Log::Info` and the Console panel | `make/first-script` | helps |
| Same inputs, same game | `make/play-test-debug` | helps |
| Opening a copy of a sample | `start/first-game` | helps |
| `Random` and seeds | `make/recipes` | helps |
| Play-tests of a game that a command script runs | `make/automated-playtests` | helps |
| Exercises: a new project from the Basic 3D template | `make/project-files` | helps |

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
| critic-make-c-8 | should | shape | `new:26` on `make/designing-a-game` | In the Medium exercise, the reader builds a grey box of their own design from built-in meshes in a new Basic 3D project, and one person plays it. Built-in meshes get colliders and nothing else: there is no player, no control and no rule to play. The page's Needs closure gives the reader only Coin Run's ball to play with. As written, the exercise has nothing to rest on. | The exercise starts from a copy of the reader's finished Coin Run: the folder is copied in the file browser and opened (`make/project-files`). It keeps the ball, the Move action, the coin prefab and the HUD. The reader grey-boxes a new level of their core loop from built-in meshes and changes one rule in a field; the worked solution does the same. The Assumes row on line 81 becomes "copying and opening a project". About 60 words. | `allocation/make-c.md:26-27`, `:62`, `:81`; `allocation/make-a.md:1800-1867` (Coin Run's end state); pin: `StrataEditor/src/Panels/SceneHierarchyPanel.cpp:70-89` (the presets: a mesh and a collider each) |
| critic-make-c-9 | should | missing-item | new item on `make/designing-a-game` | Section 6 of a concept page states what Strata does not do here. A reader who has grey-boxed in another engine expects block-out tools, and Strata has none: no brushes, no CSG and no mesh editing. In Strata a grey box is made of the seven built-in meshes, scaled and placed, or of imported models. The page has no `not-done` item, and `book.md`'s table has no such row. | Add a `not-done` item on the page (about 50 words), and a row in `book.md`'s "What Strata does not do" (the planner's). | `allocation/make-c.md:13-15`, `:24`; `style.md:488`; pin: `StrataEditor/src/Panels/SceneHierarchyPanel.cpp:70-89`; a case-insensitive git grep at 822a7a46 for CSG, blockout, greybox, graybox and ProBuilder in Strata/src, StrataEditor/src, StrataScriptCore and Docs/Manual finds nothing (in Docs, "graybox" names only the Showcase's stage in the wave 8 plans) |
| critic-make-c-10 | should | missing-item | new items on `make/designing-a-game` | The page homes its ideas as concepts but as no term. Core loop, scope, prototype, grey box, vertical slice and playtest get no glossary entry. The seed's "scope" means the part of the code where a name can be used, and is homed on `basics/programming-1`. A term mark of "scope" on this page would link that meaning. Rule 6 asks for one qualified entry per meaning. A playtest with people and the play-test that a command script runs also need to be told apart. | Add new items of type `term` on the page: "scope (of a game)" beside the seed's entry (which becomes qualified by rule 6), core loop, prototype, grey box, vertical slice and playtest. The glossary step adds "scope" to its homonym candidates. No words are added to the page. | `allocation/make-c.md:49-65`; `glossary/seed.json:697-703`; `book.md:119-124`; `allocation/make-b2.md:668` |
| critic-make-c-15 | could | stale-item | `gamedev:256-258` on `make/designing-a-game` | The link row names Physics Playground, Open World and High Desert Outpost as further examples of a small scope. Open World is a streamed 768 m island with 20,000 props. The Showcase is the graphics reference scene, with three baked times of day. Neither has a small scope, and the Showcase has no core loop. | The row names Physics Playground as a small toy with a loop. It names Open World and the Showcase as what a scope grows into, or as demos without a core loop. No words change. | `allocation/make-c.md:59`; `inventory/gamedev.md:256-258`; pin: `Samples/Samples.json:7-37` |
| critic-make-c-16 | could | missing-item | new item on `make/designing-a-game` | The page teaches playtests with people, and a reader may expect to record a session and replay it later. Strata records editor commands, not a player's keys, mouse and gamepad: a replay repeats Edit commands only, and simulated input comes from commands. | Add a `not-done` item beside the playtest section (about 40 words), and a row in `book.md`'s table (the planner's). | `allocation/make-c.md:22-24`, `:54`; pin: `StrataEditor/src/Editor/CommandJournal.h:24-30`; a case-insensitive git grep at 822a7a46 for InputRecorder, "input record" and "record the player" in Strata/src, StrataEditor/src, Docs/Roadmap.md and Docs/Manual finds nothing |
