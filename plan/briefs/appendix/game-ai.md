# Brief: `appendix/game-ai`

| Field | Value |
| --- | --- |
| Title | Game AI in general: steering, pathfinding, navigation meshes and behaviour trees |
| Kind | C |
| Size | L |
| Tracks | - |
| Needs | `basics/trees-graphs`, `basics/math-geometry` |
| From | new; how engines do navigation and behavior, which Strata leaves to scripts (curricula 1.13); the OpenWorld sample's `Wander.cpp` as the one example |
| Unit | `plan/allocation/appendix.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `appendix/game-ai` — Game AI in general: steering, pathfinding, navigation meshes and behaviour trees

**Covers.** The problem as the reader meets it: an animal in a forest should look alive, and a guard should reach the
player around a wall. The naive answers are to move straight at the target, or to pick a new random action every
frame; the first walks into walls and the second jitters. The idea: three layers on top of the senses. Deciding (what
to do now), finding a way (which way to go), and moving (how to get there), with rays and overlap tests as the senses
(can I see the player, is there ground). Deciding: finite state machines and their hierarchical form, behaviour trees
(sequences, selectors, conditions and a tick from the root), utility scoring, and goal-oriented action planning; a
table of their cost per agent, authoring effort, how they are debugged and who uses them, with sources (Red Blob Games
[S28] and the State chapter of Nystrom's *Game Programming Patterns* [S7] in `research/curricula.md`). Moving: steering
behaviours (seek, flee, arrive, wander, separation, and obstacle avoidance with rays), each as a desired velocity.
Finding a way: the level as a graph; breadth-first search, Dijkstra's algorithm and A* with a heuristic, worked by hand
on a grid of six by six cells; navigation meshes built from the walkable geometry, with path smoothing by string
pulling and local avoidance between agents.

Strata's choice: no AI module (the evidence), so game AI is script code. The SDK gives a script what it needs to build
it: `Physics::Raycast`, `RaycastAll`, `OverlapSphere` and `OverlapBox` with layer masks, the character controller's
moves, `Random` with seeds, `Timer`, the animator's `CrossFade`, and entities found by name. The one example is the Open
World sample's fox, `Samples/OpenWorld/Scripts/Wander.cpp`, in two excerpts: `Choose` and `SetState`, a state machine of
three states (Survey, Walk, Run) with a timer each, a seeded random target around the fox's home, and the animator's
state cross-faded to match; and `OnUpdate`, which waits while no ground is under the fox, seeks the target at walking or
running speed, turns the fox to face its way with `atan2`, and stands it on the terrain with a ray down to the Terrain
layer. The fox has no body (its prefab holds an Animator and a Script): it writes its own transform each frame and asks
physics only for the ground. Then how it would grow: arrive instead of a hard stop, a grid A* in a script, rays to step
around rocks. What Strata cannot do here: no navigation mesh to bake, no path queries, no shape sweeps in the API, and
no debug drawing from scripts, so a path cannot be drawn in the view. Common mistakes: deciding every frame, searching
a path every frame for every agent, a heuristic that overestimates (A* then misses the shortest path), and moving a
physics body by writing its transform instead of through its body or controller. The file's first comment says that
the target stays inside the fox's own world cell; the code picks a spot within `Range` of home and tests no cell, and
most foxes stand closer than `Range` to an edge of their cell, so the page says what the code does and does not repeat
the comment (an erratum of the engine). The exercises: A* in a sketch on the page's grid, run with three heuristics, and
a guard written as a state machine and as a behaviour tree. At the end the reader can choose a decision model and a
path search for a game, and write a first one in a script.

**Leaves out.**

- State machines, managers and object pools for game code → `make/patterns`
- The animator's state machine and cross-fades → `animation/state-machines`, `animation/blending`
- Raycasts, overlaps and their layer masks → `physics/queries`, `physics/collision-layers`
- Collide-and-slide movement of characters → `physics/character-controllers`
- Random numbers and seeds → `basics/math-probability`, `make/recipes`
- Graphs, queues and their cost → `basics/trees-graphs`

**Fit.** `fits`: about 4,750 words against L (5,000). The problem, the naive answer and the idea take 650 words, four
decision models with their table 900, path search with a worked A* and navigation meshes 750, the fox's two excerpts
500, steering 400, Strata's choice and what the SDK offers 350, the limits, the erratum of `Wander.cpp`'s first comment
and the mistakes 350, the two exercises 250, and the fixed parts 600; the four figures go with their sections.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:78` | not-done | home | Game AI (steering, pathfinding, navigation meshes, behaviour trees) is left to scripts. Evidence: `git grep -niE "pathfind\|path ?finding\|nav ?mesh\|navigation mesh\|behaviou?r ?tree\|steering\|blackboard\|utility ai\|goap" 822a7a46 -- Strata/src StrataScriptCore` finds nothing; `git grep -niwE "astar\|a-star\|dijkstra" 822a7a46 -- Strata/src StrataScriptCore` finds nothing; the word "navigation" alone matches only the game UI's keyboard and gamepad navigation (`Strata/src/Strata/GameUI/GameUIComponents.cpp`) |
| `new:103` | code | home | `Samples/OpenWorld/Scripts/Wander.cpp:68-87`: `Choose` and `SetState`, a three-state machine (Survey, Walk, Run) with a timer per state, a seeded random target around home, and a cross-fade of the animator per state |
| `new:104` | code | home | `Samples/OpenWorld/Scripts/Wander.cpp:36-66`: `OnUpdate`, waiting for ground, seeking the target, facing it with `atan2` and standing on the terrain by a ray down to the Terrain layer |
| `new:105` | figure | home | The three layers of game AI (decide, find a way, move) over the senses, as a diagram. General knowledge. |
| `new:106` | figure | home | A guard's behaviour as a state machine beside the same behaviour as a behaviour tree. General knowledge. |
| `new:107` | figure | home | A* on a six-by-six grid with a wall, step by step: the open set, the costs and the path found. General knowledge. |
| `new:108` | figure | home | The fox's three states and their timers, drawn from the code. Evidence: `Samples/OpenWorld/Scripts/Wander.cpp:68-87` |
| `new:109` | term | home | Behaviour tree (sequence, selector, condition, tick). General knowledge. |
| `new:110` | term | home | Steering behaviour (seek, flee, arrive, wander, separation). General knowledge. |
| `new:111` | term | home | A* search and its heuristic (admissible heuristic). General knowledge. |
| `new:112` | term | home | Navigation mesh (navmesh). General knowledge. |
| `new:113` | term | home | Utility AI. General knowledge. |
| `new:114` | term | home | Goal-oriented action planning (GOAP). General knowledge. |
| `new:115` | term | home | Line of sight, as an AI's sense. General knowledge. |
| `new:116` | term | home | Local avoidance. General knowledge. |
| `new:187` | erratum | home | The first comment of `Wander.cpp` says that a fox's target stays inside its own world cell, so that it never walks into a cell that is not loaded; `Choose` picks a spot 0.3 to 1 times `Range` (22 m) from the fox's home and tests no cell, and 27 of the 30 foxes stand within 22 m of an edge of their 64 m Wildlife cell. The page states what the code does and does not repeat the comment (process.md's table of errata, kind `engine`). Evidence: `Samples/OpenWorld/Scripts/Wander.cpp:1-2`, `:20`, `:68-77`; `Samples/OpenWorld/Assets/Worlds/Island.stworld:2649` (the Wildlife layer's `CellSize` of 64); the translations of the 30 foxes in `Samples/OpenWorld/Assets/Worlds/Island/Wildlife/*.stscene`, the only scenes that use the script |
| `new:190` | hands-on | home | The page's exercises (D27). Done, a sketch with its output: A* on the page's six-by-six grid with its wall, in a C++ sketch whose open set is a priority queue; it prints the path, its length and the number of cells taken from the open set, and the reader predicts, then runs, the same search with no heuristic (Dijkstra's algorithm) and with one that overestimates, and explains the differences in the counts and the paths. Design: a guard that patrols, chases a player it sees and goes back, written as a state machine and as a behaviour tree; the reader says which a Strata script would hold more simply, and where each would put the fox's timers (about 250 words). General knowledge. |
| `new:37` | not-done | link | No debug drawing from scripts, stated on `gpu/debug-drawing` |
| `physics:114` | feature | use | `Raycast`, `RaycastAll`, `OverlapSphere` and `OverlapBox`: the senses a script's AI uses |
| `physics:116` | feature | link | No shape casts in the public API, so a wide agent cannot sweep its shape |
| `physics:132` | feature | link | Character controllers, for agents that must collide while they move |
| `scripting:125` | feature | use | The SDK's `Physics` and `RaycastHit`, as the fox calls them |
| `scripting:133` | feature | use | The SDK's `Random` with seeds |
| `scripting:134` | feature | use | The SDK's `Timer` |
| `animation:85` | feature | link | The animator's own state machine, which the fox's states drive with `CrossFade` |
| `animation:283` | concept | link | State machines for animation, a sibling of decision state machines |
| `gamedev:257` | feature | use | The Open World sample: foxes with an animation controller in streamed cells |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Graphs, queues and a priority queue, and the cost of their operations (A* keeps its open set in a priority queue) | `basics/trees-graphs` | must |
| Rays, planes and intersection tests | `basics/math-geometry` | must |
| Vectors: length, direction, normalizing, `atan2` | `basics/math-vectors` | must |
| A rotation from an axis and an angle (`glm::angleAxis`) | `basics/math-rotations` | helps |
| Random numbers and seeds | `basics/math-probability` | helps |
| Script classes, their callbacks (`OnCreate`, `OnUpdate`) and fields | `scripting/script-system` | helps |
| Physics queries and their layer masks | `physics/queries` | helps |
| Collision layers | `physics/collision-layers` | helps |
| Character controllers | `physics/character-controllers` | helps |
| Animation state machines and cross-fades | `animation/state-machines` | helps |
| State machines for game code | `make/patterns` | helps |
| World cells that stream in and out | `worlds/why-streaming` | helps |
| The standard containers (`std::priority_queue`, the exercise's sketch) | `basics/cpp-generic` | helps |

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
| critic-appendix-7 | should | shape | `appendix/networking`, `appendix/game-ai` | The concept shape asks for Strata's choice and its reason. Neither Covers gives a reason, and the pin has none: the engine's documents neither plan nor refuse gameplay networking or game AI. Without that sentence a writer may invent a reason or read a plan into the silence. | Each page states it: the engine's documents name no plan and no decision; network code serves automation only, and AI is left to scripts; with the search as evidence (book.md rule 4). About 50 words on each page. | `style.md:486-487`; `allocation/appendix.md:227-234`, `:333`; pin: `git grep -n -i -w -E` for the words multiplayer, netcode, lockstep, replication and matchmaking over `Docs`, `AGENTS.md` and `README.md` finds only local multiplayer (`Docs/Releases/0.6.0.md:415, 490`, `Docs/Releases/0.7.0.md:412`, `Docs/Roadmap.md:988`) and a test's "lockstep" (`Docs/Plans/Wave8/specs/physics-timing.md:836`); `git grep -n -i -E` for nav mesh, navigation mesh, pathfind, behaviour tree, steering and game AI there finds only the input axis "steering" of `Docs/Manual/Settings.md:71` |
| critic-appendix-8 | should | missing-item | new item on `appendix/game-ai` | Strata has no debug drawing from scripts, so a reader cannot draw a path or a state. The page does not say how to see and test an AI's decisions. The fox shows the way: it keeps its state and the distance it moved in script fields (`StateIndex`, `Distance`), which the Inspector shows, and the Open World's regression script finds a fox, reads `StateIndex`, resets `Distance` and waits until the fox has moved 1 m. | Add a feature row (or a short code row of the four lines) after the fox's excerpts: state in fields, read in the Inspector or by `script.get`, and a command-script check with `until`; one sentence on log lines. About 150 words; it links `make/automated-playtests`. | `allocation/appendix.md:333-350`, `:387`; pin `Samples/OpenWorld/Scripts/Wander.cpp:22-23`; `StrataTests/Editor/OpenWorldCommands.json.in:32-35` |
| critic-appendix-9 | should | missing-item | `appendix/game-ai`, `appendix/networking` (Further reading) | Each approach's "who uses it" needs a source. The game-ai page names only Red Blob Games [S28] and *Game Programming Patterns* [S7], which do not cover behaviour trees, utility AI, goal-oriented planning, steering behaviours or navigation meshes. The networking page names Gaffer on Games [S17] and Gambetta [S24], which do not cover rollback. The research holds no other source for them. | The two Covers name the sources the writer must find for these rows (for example Reynolds 1999 on steering, Isla 2005 on behaviour trees in Halo 2, Orkin 2006 on goal-oriented planning in F.E.A.R., Mononen's Recast and Detour, GGPO and the GDC talks on rollback), marked as not yet fetched. `appendix/further-reading` takes them in its second part. About 100 words of further reading lines. | `style.md:484-485`; `allocation/appendix.md:221-222`, `:326-327`, `:572-576`; `research/curricula.md:613-640` |
| critic-appendix-10 | should | other | `new:89`, `new:90`, `new:91` on `appendix/networking`; `new:109` on `appendix/game-ai` | Three term homes of the networking page share a word with another home that has another meaning. "Jitter" is homed on `image/taa` as the sub-pixel offset of the projection. "Latency" is homed on `audio/sound-in-a-computer` with the mixing period. "Tick" is also a word of the behaviour tree's entry on `appendix/game-ai`, where a tick is one evaluation from the root. `new:95` says that "snapshot" is a third meaning; these three rows do not. | Make the entries qualified, as `new:95` is: "jitter (network)", "latency (network)" with one sentence on audio latency, "tick (simulation)" and "tick (behaviour tree)". Each page says in one sentence which meaning it uses and links the other. About 40 words. | `allocation/appendix.md:284-286`, `:290`, `:377`; `allocation/image.md:733`, `:736`; `allocation/audio-input.md:48` |
| critic-appendix-13 | could | duplicate | `appendix/not-in-strata` (the Gameplay group) | The page gives one technique paragraph per area. For the Gameplay area, the techniques of networking and game AI are the whole subject of `appendix/networking` and `appendix/game-ai`, from the same angle. | The Gameplay group gives the technique of cutscene timelines and links the two appendix pages in one sentence each. This saves about 120 words. | `allocation/appendix.md:15-25`, `:50-52`; `book.md:574-580`; `allocation/appendix.md:205-239`, `:320-350` |
| critic-appendix-14 | could | thin-home | `new:103`, `new:104` on `appendix/game-ai` | The two excerpts use `m_Random` and `m_TerrainMask` but do not show where they come from. `OnCreate` sets the home, seeds the generator from the per-fox `Seed` field (each fox in the cells overrides it), and builds the Terrain mask from `Physics::GetLayerIndex` with `c_AllLayers` as the fallback. `OnReload` runs `OnCreate` again. The page's "seeded random target" rests on these lines. | Add a third short code row, `Samples/OpenWorld/Scripts/Wander.cpp:25-34`, or widen `new:104`'s take to name them; one sentence on the prefab override of `Seed`. About 150 words. Assumes gains `make/prefabs` (helps) for the override. | `allocation/appendix.md:335-341`, `:371-372`; pin `Samples/OpenWorld/Scripts/Wander.cpp:25-34`; `Samples/OpenWorld/Assets/Worlds/Island/Wildlife/0_2.stscene:2` (override `Wander.Seed`) |
