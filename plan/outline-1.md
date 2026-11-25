# Outline 1: Start here, Making games, Foundations, Engine architecture

## How to read the tables

These rules hold for the four outline files (`outline-1.md` to `outline-4.md`). The other three files say "Columns as
in outline-1.md".

Each part starts with its heading ``## Part N — Title (`slug`)``, a line `Tracks: ...` and a line
`Needs of the part: ...`. The `Tracks:` line starts with the tracks of its pages, written as in the Tracks column
(`G, B, E` or `-`); prose may follow after ".", ";", " (" or " —". The `Needs of the part:` line says what a reader of
the whole part needs from other parts. It holds every Need of the part's rows that points to another part, once,
written as in the Needs column; a Need with an alternative inside the part is met inside it and is left out; `-` when
there is none. `check_outline.py` computes both lines and fails when they differ. The part's index page shows the
part's Needs; a part with fewer than eight rows has no index page, and its first page shows them in its top strip
("Before this part", `site.md` "Navigation"). The rows follow in reading order. Every table has these columns:

`| id | Title | Kind | Size | Tracks | Needs | From |`

- **id**: the page's path under the site's base and its file under `src/content/docs/` (`core/time` →
  `core/time.md`). Ids may still change until the first publication, never after.
- **Title**: the page's published title.
- **Kind**: one letter. The shape of each kind is in `style.md`.
  - `C` concept: a problem, the ways engines solve it, and Strata's choice.
  - `I` internals: how Strata's code does it, and how to change it.
  - `T` tutorial: the reader builds something step by step and sees the result of every step.
  - `H` how-to: the steps of one task, without theory.
  - `R` reference: facts to look up.
  - `P` primer: a lesson from zero on something that is not Strata's (programming, mathematics, how computers work).
    Its shape: why you will need this → the idea on the smallest example → worked examples → practice with answers →
    where the book uses it. Every primer opens with a **Test out** box of five questions; a reader who answers all five
    skips the page.
- **Size**: a budget of prose words with a range: `S` about 1,500 words (600 to 2,250), `M` 3,000 (2,251 to 4,000),
  `L` 5,000 (4,001 to 6,500), `XL` about 8,000 (6,501 to 10,000).
  - An XL page is split into sections with their own anchors. Each section of an XL tutorial ends in a state the reader
    can play and download, shown by a "you should now have" picture. Past 10,000 words a page splits into pages
    (rulings 4, R7).
  - A generated reference page may be split by group (`reference/commands` by command group).
  - Primers and pages of track B are at most L.
- **Tracks**: the tracks whose reading order contains the page: letters among `G`, `E`, `B`, separated by ", ". `-`
  marks a page on no track (reference, appendix). The rules of the tracks are below.
- **Needs**: at most five page ids in all, alternatives included, each in backticks, separated by ", ". The reader
  must have read all of them before the page.
  - `` `a`\|`b` `` is one Need with two alternatives: either page teaches what is needed. It is used in three cases:
    where one page teaches how to use a thing and the other how it works; for side steps; and where two tracks reach
    the page from different pages that both teach what it needs (`basics/programming-1` needs
    `make/first-script`\|`start/first-game`: tracks G and B reach it from the first, track E from the second). The
    page may use only what both alternatives teach (`style.md` §1.2). The pipe is escaped (`\|`) so that the table
    keeps its columns.
  - `-` means the page needs nothing but its part's first page. A part's first page with `-` needs nothing. The
    part's first page is not checked as a Need, because a track may enter a part in the middle (track G reads
    `basics/programming-1` without `basics/computer`); where a track holds the first page, the order of the rows puts
    it earlier.
  - A page that an earlier Need of the row already needs may be left out.
  - Links forward are allowed in prose ("the renderer, which part 7 explains"). Needs forward are not.
- **From**: where the page's material comes from.
  - `<inventory> "<chapter>"` names a proposed chapter (section 8) of `plan/inventory/<inventory>.md`; `§1.n`,
    "concept n", "code n", "diagram n", "pitfall n" and "hands-on Gn" or "En" name items of that inventory's other
    sections. A writer reads the inventory's whole file, not only the named chapter.
  - `curricula` is `plan/research/curricula.md`. Engine documents are read at the pin: PackageReadme
    (`Docs/Releases/PackageReadme.md`), `Manual/<Name>` (`Docs/Manual/<Name>.md`), skill `strata-<name>`
    (`.claude/skills/strata-<name>/SKILL.md`), release notes (`Docs/Releases/<version>.md`), and engine files by path.
  - "new; <what and why>" marks a page that no inventory proposed.
  - "home of X" and "use home of X" repeat `book.md`'s one-home table: the page teaches X, and other pages say one
    sentence and link to it.
  - A mark ends the From: ` · W8` or ` · W8r (<section revised>)`.

### Tracks

`plan/tracks.md` writes each track out as an ordered list of page ids; the site's "next page" link of a track follows
it. These rules produce the lists:

- **G, game maker**: the pages of `start` in order (`start/coming-from` is optional); then the pages of `make` in order.
  After `make/first-script` the track steps through `basics/programming-1`, `basics/programming-2`,
  `basics/programming-3` and `basics/debugging`, and comes back to `make/script-loop`. `basics/tools` and
  `basics/math-vectors` are side steps for G: they are offered where a `make` page first needs them, they are not in
  G's order, and they appear in Needs only as alternatives.
- **B, beginner**: the pages of `start` without `start/coming-from`; `make` block A from `make/editor-tour` to
  `make/lighting`; `basics/computer`, `basics/tools`; `make/first-script`; `basics/programming-1`,
  `basics/programming-2`, `basics/programming-3`, `basics/debugging`; the rest of block A, from `make/script-loop` to
  `make/project-coin-run`; then the other pages of `basics` in order, from `basics/git` to `basics/threads`. There
  track B ends, and the reader chooses: track G from `make/gameplay-math` (block B), or track E from `core/map`.
- **E, engine builder**: the pages of every part except `make`, `reference` and `appendix`, in the order of the parts
  in `book.md` (`start`, `basics`, `core`, `world`, `gpu`, then the later parts) and in the order of the rows within a
  part. Every primer can be tested out. A later part is readable once the Needs of its pages are read; its index page
  names them, or its first page when the part has no index page.

### The check

`plan/check_outline.py` (later part of the site's build) reads the four outline files, `plan/tracks.md`, and the
counts that `book.md`, `process.md` and `README.md` state, and prints one line per problem. It fails when one of these
does not hold:

- every id is unique, is lowercase segments of `[a-z0-9-]` joined by `/`, starts with its part's slug, and does not
  end in `index` or `review` (the generated part pages);
- every table row stands under a part heading;
- the parts are the 25 of `book.md`, numbered 0 to 24, in the order of rulings 2;
- every row has the seven columns; Kind is one of `C I T H R P`; Size is one of `S M L XL`, and a primer or a page of
  track B is not `XL`; Tracks is `-` or letters among `G`, `B`, `E`;
- every row of `basics` is a primer (P), and no page on track G or B is of kind I or R;
- a mark is a final ` · W8` or ` · W8r (<section>)`, and the marked pages are exactly the W8 and W8r lists of
  rulings 1 (R6, "Marks" below);
- every id in Needs exists, no row's Needs name more than five page ids (alternatives included), and the Needs form no
  cycle;
- each part's `Tracks:` line starts with the tracks of its rows, and its `Needs of the part:` line is the one computed
  from its rows;
- every row's Tracks column is the one rulings 1 (R4) give it: `start` on G, B and E (`start/coming-from` on G and E);
  block A of `make` on G and B, blocks B and C on G; `basics` on B and E, and also on G for `basics/programming-1` to
  `basics/programming-3` and `basics/debugging`; the parts from `core` to `capstone` on E; `reference` and `appendix`
  on no track;
- a page's Tracks column names exactly the tracks whose list in `plan/tracks.md` holds it, and every id listed there
  is a row;
- each track's list is the sequence of the rules above (G, B and E as "Tracks" states them), and only track G has side
  steps, exactly `basics/tools` and `basics/math-vectors`;
- for every track a page is on, each Need (or one of its alternatives) comes earlier in that track's list; a track
  keeps the order of each part's rows; a side step stands directly before the first page of the track that names it,
  and each of the side step's own Needs comes earlier on the track (or is an earlier side step);
- a page on no track has each Need (or one alternative) earlier in the book's order of rows;
- no page of a writing wave needs a page of a later wave (the waves are a table in the script; `process.md` states
  the same table);
- the counts that `book.md` (the Parts, kinds and tracks tables and their sentences), `process.md` (the waves table
  and its sentences) and `README.md` state are the outline's.

`--counts` prints the pages per part, block, kind, size, track and wave, the W8 and W8r pages and the total; `--words`
the estimated words (S 1,500, M 3,000, L 5,000, XL 8,000); `--waves` the pages of every wave.

### Marks

- ` · W8`: the page is written in phase B, after engine release 0.8.0, because wave 8 changes its subject.
- ` · W8r (<section>)`: the page is written in phase A, and the named section is revised in phase B. Its phase A text
  states no preset value in prose; the values come from generated tables.
- There is no other mark. A feature that already landed is described at the pin, and the pin move's diff decides what
  is read again. "New in 0.8.0" for readers is front matter (`since: 0.8.0`), not a mark of the plan.

### Generated pages

A part with eight or more pages also gets two generated pages, which are not rows, have no kind and are no page's
Need: `<part>/index` (the part's map, its prerequisites, and what the reader can do afterwards) and `<part>/review`
(questions across the part, collected from its pages and extended by the part's editor). In this file `make` (42
pages), `basics` (30) and `core` (16) get them; `start` (6) does not. A part without them shows its Needs of the part
and its notation table on its first page (`style.md` §7.7).

## Part 0 — Start here (`start`)

Tracks: G, E, B (`start/coming-from`: G, E).

Needs of the part: -

Doing comes before theory: the reader installs Strata and makes a first game before `start/what-an-engine-is`
explains what happened.

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `start/welcome` | What Strata is and what this book teaches | C | S | G, E, B | - | new; the three doors (make a game, understand an engine, learn from zero); the game maker's door says that game logic is C++ (no visual scripting) and that an AI agent can help; it says which track a beginner continues on, and from which page |
| `start/how-to-read` | How to read this book | H | M | G, E, B | - | new; the tracks, the kinds of page, the strips, the conventions, the engine version; the map of the book (tracks and Needs, generated from the front matter; curricula 5.1.4); "How to read a command" (JSON, and that the command tab is optional on game-maker pages); "How to read code you do not understand yet" |
| `start/install` | Installing Strata and the C++ build tools | H | M | G, E, B | `start/how-to-read` | gamedev "Installing Strata" (§1.1: release archives, requirements, first start, script toolchain discovery, logs); PackageReadme "Requirements", "First start"; Manual/Scripting "Where builds happen"; tabs per OS; the terminal skills it teaches, per OS: open a terminal, change folder (`cd`, `~`), run a program of the current folder with arguments (`./`, `.\`), quote a path, paste a command, and on Linux `sudo`; the commands are those of PackageReadme (on Windows `.\StrataEditor --version \| Write-Output`, because PowerShell waits for a windowed program only when its output is piped; on macOS `xattr -dr com.apple.quarantine <folder>` and `xcode-select --install`; on Linux `sudo apt install g++ cmake ninja-build`); use home of the terminal for game makers; a code editor (VS Code or Visual Studio Community). Building from source is `core/first-change`'s |
| `start/first-game` | Your first game | T | L | G, E, B | `start/install` | gamedev "The launcher and your first project" (§1.2; hands-on G1-G3, G6): the Tetris copy played within five minutes, a Basic 3D project with falling bodies, the generated `Spinner` script attached and built; then one change to it: `DegreesPerSecond` changed in the code editor, the scripts built again with **Ctrl+B**, one `Log::Info` line added and read in the **Console** panel (the playground of `basics/programming-1` on track E); the first build (Play on the Tetris copy) is the toolchain check, or a toast names what to install; "what next" names the tracks and `make/with-an-agent` |
| `start/what-an-engine-is` | What a game engine is: one frame, start to finish | C | L | G, E, B | `start/first-game` | foundation "What an engine is, and how Strata is put together" (first half); gamedev "What it takes to make a game" (concepts 1-2); it explains what the reader just did; home of the frame map for people (the renderer's passes are `gpu/frame-tour`'s), with frame time in milliseconds and the CPU preparing one frame while the GPU draws the one before (the mechanism, frames in flight, is `gpu/how-a-gpu-frame-works`'), and of a survey of engines (curricula 1.0) |
| `start/coming-from` | Coming from Unity, Unreal or Godot | H | M | G, E | `start/what-an-engine-is` | new; curricula 5.2; gamedev concepts 4, 7 (GameObject and entity, prefab variants and Strata's overrides, Blueprints and C++ scripts); optional on both tracks |

## Part 1 — Making games (`make`)

Tracks: G, B (block A); G only (blocks B and C).

Needs of the part: `start/how-to-read`, `start/what-an-engine-is`, `basics/tools`\|`start/install`, `basics/programming-3`, `basics/debugging`

Tracks G and B step into `basics` after `make/first-script` for `basics/programming-1` to `basics/programming-3` and
`basics/debugging`, and come back to `make/script-loop`; `basics/tools` and `basics/math-vectors` are side steps of
track G (`plan/tracks.md`). Block A's tutorials build one game, Coin Run, step by step: each starts from the end state
of the one before and needs it, and the reader owns a finished, exported game at the end of block A. Each row of block
A that changes Coin Run names its stage in its From; `book.md` ("Running examples") lists them. Every page of block B
needs block A (it lists
`make/project-coin-run`, or a page of block B that does) and what its Needs name. Block C's projects need what their
Needs name. No page of block A carries a mark.

**Block A — Your first game**

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `make/editor-tour` | A tour of the editor | T | M | G, B | `start/how-to-read`, `start/what-an-engine-is` | gamedev "A tour of the editor" (§1.3); editor-ui "A tour of the Strata editor"; use home of editor commands (the command tab of every tutorial, read as `start/how-to-read` teaches); Coin Run's project starts here from Basic 3D |
| `make/project-files` | Projects, saving, undo and recovery | H | M | G, B | `make/editor-tour` | gamedev §1.2 (the project file, creation), concept 3, diagram 2, pitfall 1; editor-core "Undo and redo", "Autosave and crash recovery" (use side); editor-ui §1.11 (the recovery dialog); file extensions, hidden files and folders (`.strata/`, `.meta` files) and a path copied as text; a Variation section on opening a project of an older release (gamedev §1.2 "migration", release notes "Upgrading"); use home of the project folder, undo, autosave and recovery |
| `make/scenes-entities` | Scenes, entities and components | T | M | G, B | `make/editor-tour` | gamedev "Scenes, entities and components" (§1.4, concept 4); Coin Run's level: the ground, the walls, the ball and a first coin as entities |
| `make/transforms-units` | Positions, rotations and units | C | L | G, B | `make/scenes-entities` | gamedev "Positions, rotations and units" (concept 5); use home, for makers, of a position or a direction as three numbers (x, y, z), adding and scaling them, degrees and radians (`glm::radians`), a rotation as an axis and an angle, a rotation stored as a quaternion and combined by multiplying (the `Spinner`'s `turn * transform.GetRotation()`, `StrataEditor/src/Editor/ScriptProject.cpp:249-250`), axes, handedness and units (their mathematics is `basics/math-vectors`', `basics/math-matrices`' and `basics/math-rotations`'); every idea is first shown with the Inspector's numbers and the gizmo, because the reader cannot read code yet; the code forms stand in one last section, "The same ideas in code", which says that it is read again from `make/scripting-scene`, the first page that uses them |
| `make/assets` | Bringing in assets | H | M | G, B | `make/transforms-units`, `make/project-files` | gamedev "Bringing in assets" (§1.5, concept 6); assets (use side): import settings, Fast and High, sub-assets, safe moves and deletes; editor-core "Project files as history: the trash and references" (use side: deletes go to the trash and are undone); licenses, CC0 sources (Kenney, Poly Haven, Quaternius, ambientCG) and a `CREDITS.md`; handles in one paragraph; use home of the trash and of undoing asset deletes; Coin Run's coin model |
| `make/materials` | Materials | T | L | G, B | `make/assets` | gamedev "Materials" (§1.6, concept 8); render-direct "Describing surfaces: Strata's material model" (use side); normal maps and their import setting `FlipGreen`; emission as a color and a strength (its value in nits is `make/lighting`'s); the albedo audit with the debug view; Coin Run's gold coin and the ball's material |
| `make/prefabs` | Prefabs | T | M | G, B | `make/materials` | gamedev "Prefabs" (§1.7, concept 7; hands-on G5); editor-core "Using prefabs"; Coin Run's coin becomes a prefab |
| `make/lighting` | Lighting a scene: sun, sky and exposure | T | L | G, B | `make/prefabs` | gamedev "Lighting a scene" (§1.8: units, sky sources and presets, sun shadows, exposure, preview lighting, the luminance and albedo debug views; fog is `make/look`'s); render-direct "Lighting a scene in the editor (tutorial)" (the outdoor half); emission in nits; use home of light units, exposure, the sky as a light and the default template's lighting; Coin Run's level lit for play |
| `make/first-script` | Your first script | T | M | G, B | `make/lighting`, `basics/tools`\|`start/install` | gamedev "Your first script" (§1.9, concepts 11, 13; hands-on G6); scripting "Your first script"; Manual/Scripting "Create a script" to "When a script crashes" (the code editor, IntelliSense, the Problems panel, the crash toast); the C++ special to scripts (the `Script` base class, `override`, `ST_SCRIPT_CLASS`, `ST_SCRIPT_FIELD`, no work in the constructor); `deltaTime` named; `Log::Info`; use home of hot reload; Coin Run's coins spin |
| `make/script-loop` | The game loop from a script's side | C | M | G, B | `make/first-script`, `basics/programming-3` | gamedev "The game loop from a script's side" (concepts 1, 12); scripting "The script lifecycle and the frame"; home of the script lifecycle and its callbacks; use home of the fixed step, frame and fixed updates, time scale and FixedRate; `Time`'s delta and fixed delta; Coin Run's coins bob in `OnUpdate` |
| `make/scripting-scene` | Scripts and the scene: finding, spawning and changing entities | H | L | G, B | `make/script-loop` | scripting "The gameplay API, part 1": `Entity` (name, tag, activity, hierarchy, `Destroy`, components by name, properties), the `Component` proxy, `TransformComponent` (local and world position, rotation and scale), `Scene` (create, find, roots, camera, `Instantiate`; `InstantiateMany` is `make/performance`'s), `Assets` (find, request, release, progress); use home of asking for assets early (`Instantiate` never waits); Coin Run's coins placed by a script, and a collected coin hidden or destroyed |
| `make/input` | Input and input actions | T | L | G, B | `make/scripting-scene` | gamedev "Input and input actions" (§1.10, concept 14); audio-input "Controls players can change" (use side: actions and their bindings); scripting "The gameplay API, part 3": `Input` (keys, mouse, gamepads, sticks and dead zones, cursor mode, input actions); hold and toggle; Coin Run's Move action. Binding capture, saving the bindings and typed text are `make/menus`', where the rebinding screen and text fields are built |
| `make/physics` | Physics for game makers | T | L | G, B | `make/input` | gamedev "Physics for game makers" (§1.11, concept 15); physics (use side) and the use half of physics "Tuning and measuring physics" (`Physics.Simulation`, `physics.stats`, the pile that never sleeps); force, mass, velocity and impulse at the use level (what `AddForce` and an impulse do to the ball); scripting "The gameplay API, part 2": `RigidBody`, `Physics` (raycasts, queries, collision layers), contacts and triggers; Coin Run's ball rolls by a force in `OnFixedUpdate` and its coins are triggers (hands-on G12, balls shot through the cursor, is `make/gameplay-math`'s exercise) |
| `make/sound` | Sound | T | M | G, B | `make/physics` | gamedev "Sound" (§1.13, concept 19); audio-input "Making your game sound good"; scripting "The gameplay API, part 2": `AudioSource`, `Audio`; use home of residency for sounds ("request in `OnCreate`"); Coin Run's coin sound |
| `make/hud` | HUDs: text, score and bars | T | M | G, B | `make/sound` | gameui "Making menus and HUDs in the editor" (the HUD half: canvases, anchors, text, images); render-core "Text: fonts, shaping and signed distance fields" (use side: `TextComponent`, text without a canvas); scripting "The gameplay API, part 3": `UIElement` text, image, color and value; Coin Run's coin count and timer |
| `make/play-test-debug` | Playing, testing and debugging | H | M | G, B | `make/hud`, `basics/debugging` | gamedev "Playing, testing and debugging" (§1.17); a Coin Run script debugged with the debugger that `basics/debugging` attached to the editor (Manual/Scripting "Debugging with a debugger" is that page's); use home of Play and Simulate, pausing and stepping, determinism ("same inputs, same game") and debugging scripts |
| `make/export` | Exporting and shipping | T | M | G, B | `make/project-files`, `make/hud` | gamedev "Exporting and shipping" (§1.18, concept 24); worlds-runtime "Shipping a Game: the Export" (use side; hands-on 7, 9); "Giving your game to players": a credits screen, the notices file, SmartScreen, quarantine, the `.desktop` file in a hidden folder; one sentence that an exported streamed world waits for its ground, which `make/large-worlds` checks; use home of the export; Coin Run exported and run |
| `make/project-coin-run` | Project: Coin Run, a first finished game | T | L | G, B | `make/export`, `make/sound`, `make/play-test-debug` | gamedev "Tutorial: Coin Run" (hands-on G8, as a rolling ball, because block A has no character page); skill `strata-make-a-game` §4-8; finishing it: win, lose, restart (`Game::ReloadScene` in one step; game flow's home is `make/levels-saves`), polish, the exported game; "what next" tells a track B reader that track G is open from `make/gameplay-math` at once, and that the rest of `basics` can come later |

**Block B — The toolbox**

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `make/gameplay-math` | The math of moving things: vectors, directions, angles and smoothing | H | L | G | `make/project-coin-run`, `make/transforms-units`\|`basics/math-vectors` | new; skill `strata-make-a-game` L158-256, `Samples/ThirdPerson/Scripts/FollowCamera.cpp` L43-101, `Samples/PhysicsPlayground/Scripts/Playground.cpp` L183-207; scripting "The gameplay API, part 1": `TransformComponent`'s Euler angles and its forward, right and up directions (-Z forward); the SDK's `Motion` (`LookAt`, `SmoothDamp`); each formula (a vector's length and `normalize`, the dot product, `atan2`, the `tan` of half the field of view, `1 - exp(-k dt)`) is given as a recipe: what it computes, at most two sentences of why, and a link to its primer (`make/transforms-units` gave positions, directions and rotations); use home of vectors (length, normalize, dot), angles (`atan2`) and frame-rate-independent smoothing for makers; closing exercise: hands-on G12 (balls shot through the cursor along a ray built from the camera's field of view, as `Playground::GetPointerRay` builds it) |
| `make/timers-events` | Timers, time scale and events between scripts | H | M | G | `make/project-coin-run` | scripting "Building blocks and recipes" (`Timer`, `KeyRepeat`, cooldowns); scripting "The gameplay API, part 3": `Time` (time scale, unscaled and real time, the frame index); scripting "The gameplay API, part 1": `GetScript<T>`, `AddScript<T>` (scripts that call each other, found again every frame: gamedev concept 12) |
| `make/script-fields` | Tuning scripts from the editor: fields, references and prefabs | H | M | G | `make/project-coin-run` | scripting "Your first script" (fields) and "The gameplay API, part 1" (entity and asset fields, `Instantiate` by handle); Manual/Scripting "Create a script"; the field types (`bool`, `int32_t`, `float`, vectors, quaternions, strings, `Entity`, `AssetHandle`); fields through hot reload and in prefab overrides |
| `make/patterns` | Patterns for game code: state machines, managers and object pools | C | L | G | `make/timers-events`, `make/script-fields` | new; curricula 1.13; Nystrom, *Game Programming Patterns* (State, Update Method, Object Pool); state machines, managers, object pools, and showing and hiding instead of creating and destroying; examples from the samples' scripts |
| `make/recipes` | Building blocks and recipes | H | L | G | `make/patterns`, `make/gameplay-math` | scripting "Building blocks and recipes": `Random` and seeds, recipes from the samples (Coin, the Tetris board), exercises; `Timer` and `KeyRepeat` are `make/timers-events`', `Motion` is `make/gameplay-math`' |
| `make/script-builds` | Building and shipping script modules | H | M | G | `make/project-coin-run`, `basics/tools`\|`start/install` | scripting "Building and shipping script modules" (use side): building outside the editor, other compilers and their warnings, long paths, shared libraries next to the module; what a module is, at the use level; Manual/Scripting "Where builds happen", "IntelliSense and building in the IDE" (the `strata` preset the editor writes into `Scripts/CMakePresets.json`); every command it teaches is given exactly, with what the reader should see after it |
| `make/characters-cameras` | Characters and cameras | T | L | G | `make/gameplay-math`, `make/script-fields` | gamedev "Characters and cameras" (§1.11, concepts 16-17); scripting "The gameplay API, part 2": `CharacterController`, `GroundState`, drawn poses for cameras; `TransformComponent`'s drawn pose and `ResetInterpolation`; Manual/Scripting "Following moving things"; use home of interpolation for game code (`GetDrawnPosition` in `OnLateUpdate`, platforms in `OnFixedUpdate`) |
| `make/animation` | Animation for game makers | T | L | G | `make/characters-cameras` | gamedev "Animation for game makers" (§1.12, concept 18); animation "Tutorial: an animated character from import to footsteps"; the how-to half of animation "Animation in the editor: previews, edit poses and commands" (the Asset tab's tables, the Inspector's live state, the preview chip; the `animation.*` commands in the command tab); no menu or button creates an animation controller at the pin (`StrataEditor/src/Panels/ContentBrowserPanel.cpp:564-580`; only `animation.createController`, `StrataEditor/src/Editor/EditorAnimationCommands.cpp:153`), so the tutorial's starting checkpoint holds a minimal controller and the reader edits it in the Asset tab with **Add Parameter**, **Add State** and **Add Transition** (`StrataEditor/src/UI/AnimationAssetViews.cpp:532, 659, 791`); the page says so in one sentence and names `make/commands`, where the command is run; scripting "The gameplay API, part 2": `Animator`, `JointTransform`, `OnAnimationEvent` |
| `make/menus` | Menus: buttons, navigation, pause and settings screens | T | L | G | `make/timers-events`, `make/script-fields` | gameui "Making UI do things: widgets, events and scripts", "Making menus and HUDs in the editor" (the main menu scene); scripting "The gameplay API, part 3": the UI callbacks (`OnUIClick`, `OnUIValueChanged`, `OnUIFocusChanged`, `OnUISubmit`), `UIElement` interactable, value and focus, `UIAction`, the pointer over UI, `Game`'s window mode, resolution, vsync and window size; scripting "The gameplay API, part 3": `Input`'s binding capture, saving the bindings and typed text; audio-input "Controls players can change" (the rebinding side); hands-on G10, G14: a pause menu at time scale 0, a settings screen (volume, window, vsync), a rebinding screen (binding capture and saving) and a name field (typed text); use home of binding capture and of the rebinding screen |
| `make/levels-saves` | Levels, loading screens and save files | H | L | G | `make/menus` | gamedev "Levels, loading, saves and settings" (§1.15, concept 21); scripting "The gameplay API, part 1" (`SubScene`, `LoadAdditive`) and "The gameplay API, part 3" (`Game`: `Quit`, `LoadScene`, `ReloadScene`, progress, save files); a save file holds one value per line, written and read with the page's exact code (`std::to_string` and `std::stoi` from `basics/programming-2`, the `std::optional` that `Game::ReadSaveText` returns from `basics/programming-3`); use home of additive loads, loading screens and state passed between scenes |
| `make/lamps` | Lamps: point, spot and area lights and their shadows | T | L | G | `make/project-coin-run` | render-direct "Lighting a scene in the editor (tutorial)" (the indoor half); gamedev §1.8 (Source Radius, local shadows; hands-on G7's lantern) · W8 |
| `make/reflections` | Sky light, ambient occlusion and reflections in your game | H | L | G | `make/project-coin-run` | render-indirect "Using sky, AO and probes in your game", "Shiny worlds: a wet-floor tutorial" (the sky's light on surfaces, AO, probes and their bakes, times of day, a wet floor with screen-space reflections; choosing the sky source and its preset is `make/lighting`'s) |
| `make/gi` | Trying global illumination | H | M | G | `make/reflections` | render-indirect "Trying global illumination in a scene" · W8 |
| `make/look` | The camera's image | T | L | G | `make/project-coin-run` | gamedev "The camera's image and graphics quality" (the camera half); render-image "Tutorial: giving a scene a camera look"; Manual/Camera; height fog (moved from `make/lighting`, whose tutorial has no room for it); use home of height fog and of the quality rows of each effect · W8r (the effects' quality presets) |
| `make/quality` | Graphics quality and options for players | H | M | G | `make/look`, `make/menus` | gamedev "The camera's image and graphics quality" (the quality half); Manual/AntiAliasing, Manual/Graphics (presets, costs, the quality chip, `--quality`, players' options, why there is no render scale); scripting "The gameplay API, part 3": `Graphics`, `GraphicsOption`, `QualityPreset`; it adds the Graphics row to the settings screen of `make/menus`; use home of players' graphics options · W8r (the presets table) |
| `make/large-worlds` | Large worlds | T | L | G | `make/levels-saves` | gamedev "Large worlds" (§1.16, concept 22; hands-on G13); worlds-runtime "Building a World in the Editor"; scripting "The gameplay API, part 3": `World`, `WorldCellRequest` (prefetch before a teleport); the Play check in the editor and, for the exported game, "A world that waits for its ground" (kept here, not in `make/export`: `make/export` comes before any world on track G, and `make/export` says it in one sentence with a link here) |
| `make/performance` | Making your game run fast | T | M | G | `make/quality`, `make/large-worlds`, `make/animation` | render-scene "Tutorial: making a big scene draw fast"; worlds-runtime "Measuring Shipped Games" (use side: `--perf-log`); the Performance panel, `renderStats`, the quality costs; scripting "The gameplay API, part 1": `Scene::InstantiateMany` (many instances in one call; each transform is built by one given line, such as `glm::translate(glm::mat4(1.0f), position)`, because track G has no page on matrices); use home of measuring a game · W8r (the `renderStats` keys and the Performance panel's numbers) |
| `make/automated-playtests` | Automated play-tests | H | L | G | `make/menus`, `basics/tools`\|`start/install` | gamedev "Automated play-tests and AI agents" (the play-test half: §1.17, concept 23); editor-core "Scripting the editor: command scripts, batches, record and replay" (use side); audio-input "Letting tools play: simulated input" (use side); JSON as a reader writes it: objects, arrays, strings, numbers, quotes and commas, and the editor's message for a broken file; command scripts with `play.step`, `input.sequence`, `expect`, `until` and `bind`, run with `StrataEditor --commands <file>` (in PowerShell with `\| Write-Output`, so that it waits); what a replay script is, and the Activity panel's **Copy as script**; turning a session into a regression test is `make/with-an-agent`'s (G15); gameui "Testing and automating game UI" (use side: `ui.create`, `ui.layout`, `ui.hitTest`, `input.click`); use home of simulated input, command scripts, record and replay |
| `make/commands` | Driving the editor from outside: the CLI and command scripts | H | M | G | `make/automated-playtests`, `make/animation` | automation "Driving the editor from outside" (use side); skill `strata-make-a-game` §1; StrataCLI against a running editor, finding a command and its schema, parameters from a file (`@file`) or from standard input (`-`) because quoting JSON on a Windows command line is fragile (skill `strata-editor-automation`), steps with no UI (`prefab.instantiate` with many instances, `animation.createController`), command scripts that build content |
| `make/with-an-agent` | Making a game with an AI agent | T | L | G | `make/commands` | automation "Connecting an AI agent (MCP)", "Making a game as an agent"; gamedev §1.19 (hands-on G15); skill `strata-make-a-game`; the launcher's agent card, toolsets, presence, the Activity panel (Copy as script, Re-run, Undo to here), steering an agent safely; Tetris as the model; use home of the activity journal |
| `make/samples` | Studying the samples | H | M | G | `make/project-coin-run` | gamedev "Studying the samples" (§1.20); worlds-runtime "The Launcher, Templates and Samples" (use side) |

**Block C — Projects**

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `make/designing-a-game` | Planning a small game: the core loop, scope, prototype and playtest | C | M | G | `make/project-coin-run` | new; curricula 1.13; gamedev concept 23 (testing); the core loop, scope, a prototype and a playtest, with the samples' READMEs as examples; each project page opens with its one-paragraph design |
| `make/project-tetris` | Project: Tetris | T | XL | G | `make/designing-a-game`, `make/recipes`, `make/automated-playtests` | gamedev "Tutorial: Tetris" (hands-on G9: the rules class, the board script, `KeyRepeat`, HUD, sounds, pause, game over, a command-script regression with an exact score); `Samples/Tetris` |
| `make/project-platformer` | Project: a third-person platformer | T | XL | G | `make/designing-a-game`, `make/animation`, `make/levels-saves`, `make/commands` | gamedev "Tutorial: a third-person platformer" (hands-on G11: a skinned character whose controller `animation.createController` makes, a follow camera with a raycast arm, jump pads, checkpoints, a moving platform in `OnFixedUpdate`, footstep events, menus, a loading scene, a pruned export); `Samples/ThirdPerson` |

## Part 2 — Foundations (`basics`)

Tracks: B, E, G (G only for `basics/programming-1`, `basics/programming-2`, `basics/programming-3` and `basics/debugging`; `basics/tools` and `basics/math-vectors` are side steps of G).

Needs of the part: `start/first-game`, `start/install`, `make/first-script`\|`start/first-game`

Every page is a primer (kind P) and opens with a Test out box. The programming primers use a Strata script as their
playground: output goes to the log and to a moving entity, so no second toolchain is needed. Tracks G and B run them in
the reader's Coin Run project; each of the four ends its practice with one Coin Run checkpoint (named in its row), whose
starting project is the download of `make/first-script`'s end checkpoint, so that a reader of track E can do it too.
Each primer after `basics/debugging` ends its practice with one optional item on the reader's Coin Run project for track
B, started from the download of `make/project-coin-run`'s end state. The part's index page names, for each primer, the
first part whose pages need it, so that a reader of track E knows which Test out boxes can wait.

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `basics/computer` | How a computer runs a program: CPU, memory, caches and processes | P | L | B, E | `start/first-game` | new; the CPU, memory, the stack and the heap as places in memory, caches and why the order of data in memory matters, SIMD in one section; processes: process id, environment, child processes; its exercises are editor tasks (track B reads it before any programming); threads are `basics/threads`' (foundation concept 16), job systems `core/jobs`' (foundation concept 17), allocators and the stack and the heap in code `basics/cpp-memory`', arrays of structs and sparse sets `basics/data-structures`', exit codes and the standard streams `basics/tools`' |
| `basics/tools` | The tools: the terminal, files and a code editor | P | M | B, E | `start/install` | new (curricula 1.0, 1.1); it assumes nothing of `basics/computer`, because it is a side step of track G; the terminal (folders and paths, running a program with arguments, quoting paths, PowerShell's `\| Write-Output`), exit codes and the standard streams, the user data folder, environment variables, a code editor; git is `basics/git`'s |
| `basics/programming-1` | Programming from zero I: values, variables, expressions and decisions | P | L | G, B, E | `make/first-script`\|`start/first-game` | new; curricula 1.1; values and types, variables, expressions, `if` and `switch`, each idea run in a script; names in a namespace such as `Key::Space`, and scoped enum values such as `CursorMode::Locked`; namespaces and `::` (`using namespace Strata;`, `glm::`); learncpp lessons linked per section; Coin Run checkpoint: the coins' spin speed in a variable, and an `if` that spins a gold coin faster |
| `basics/programming-2` | Programming from zero II: loops, functions, lists and structs | P | L | G, B, E | `basics/programming-1` | new; curricula 1.1; loops, functions, parameters and return values, static member functions called as `Input::IsActionDown`, `std::vector` and `std::array`, structs, `std::string` with `std::to_string` and `std::stoi`; Coin Run checkpoint: a function and a loop that line coins up, with the lines that request and instantiate the prefab given |
| `basics/programming-3` | Programming from zero III: classes, references, files of code and reading errors | P | L | G, B, E | `basics/programming-2` | new; gamedev concept 11 (classes, inheritance and `override` at the level a script needs, headers and sources, compile errors and the Problems panel); references at the use level; pointers at the use level (`T*`, a `nullptr` check, `->`: what `GetScript<T>()` returns); `std::optional` with `has_value` and `value_or` (what `Entity::GetProperty` and `Game::ReadSaveText` return); template arguments in angle brackets (`GetProperty<float>`); Coin Run checkpoint: a `Coin` class with a field, and a `BobbingCoin` derived from it |
| `basics/debugging` | Finding bugs: a method, the log and the debugger | P | L | G, B, E | `basics/programming-3` | new (curricula 1.18); a method for finding bugs, the log, breakpoints, stepping, the call stack; a process as a running program (one paragraph, since tracks G and B have not read `basics/computer`'s); a debugger attached to the editor's process, with the setup per OS (Manual/Scripting "Debugging with a debugger": Visual Studio's Attach to Process, VS Code's "Attach" entry; the writer checks what each OS asks before an attach, such as Linux's ptrace setting); use home of attaching a debugger to the editor; debugging the engine itself is `core/debugging`'s; Coin Run checkpoint: a planted bug in the coins' spin, found with breakpoints |
| `basics/git` | Version control with git | P | M | B, E | `basics/tools` | new by split of `basics/tools`: track G's side step and track B's reading before `make/first-script` need no git (curricula 1.0); clone, submodules, branch, diff, commit, merges and conflicts, remotes and pushes, tags, patches, worktrees, and the `.gitignore` a new project gets; after `basics/debugging` because track B reads it after `make/project-coin-run`, which needs no git |
| `basics/numbers` | Numbers in a computer: binary, integers, floating point and precision | P | L | B, E | `basics/computer`, `basics/programming-1` | new (curricula 1.1, 1.2); binary and hexadecimal, two's complement, shifts and masks, packing keys, IEEE 754, spacing that grows with magnitude, rounding and determinism; powers and logarithms (EV stops, decibels), the exponential function and the number e; home of floating point and precision, and of exponentials |
| `basics/data-structures` | Data structures I: arrays, lists, hash maps and their cost | P | L | B, E | `basics/programming-3`, `basics/numbers` | new; arrays, linked lists, stacks, queues and ring buffers, hash maps and their cost (big-O, with the logarithms of `basics/numbers`); binary search, swap-remove and free lists, prefix sums; arrays of structs against structs of arrays; the engine's cases: sparse sets (scene-ecs concept 4; code 4, 5, 13) and hash buckets, job queues; trees, heaps, graphs and sorting are `basics/trees-graphs`' |
| `basics/trees-graphs` | Data structures II: trees, heaps, graphs and sorting | P | M | B, E | `basics/data-structures` | new by split of `basics/data-structures`, which could not hold both lessons at a primer's size; trees and ordered maps whose nodes stay put, depth-first and breadth-first walks, binary heaps as priority queues, spatial trees as halving the space to search, graphs (directed graphs, dependency graphs, walks, cycles; their topological sort is `core/engine-modules`', foundation concept 10), union-find, sorting and radix sort; the engine's cases: dependency graphs, spatial trees, reference graphs, queues of loading work by priority |
| `basics/cpp-memory` | C++ memory: pointers, references, lifetimes, RAII and smart pointers | P | L | B, E | `basics/programming-3`, `basics/computer` | new by split of `basics/cpp`; foundation "C++ for engine code: ownership, errors and logging" (the language half); the "Reader must know first" columns of foundation, scene-ecs and assets; the stack and the heap in code, allocators; `Scope` and `Ref`; undefined behavior |
| `basics/cpp-classes` | C++ classes in depth: inheritance, virtual calls and interfaces | P | M | B, E | `basics/cpp-memory` | new by split of `basics/cpp`; inheritance, `virtual` and `override`, interfaces (one interface with a virtual call), operators; type erasure is `basics/cpp-generic`'s |
| `basics/cpp-generic` | Generic C++: templates, lambdas and the standard containers | P | L | B, E | `basics/cpp-classes`, `basics/trees-graphs` | new by split of `basics/cpp`; templates, lambdas and captures, `std::function`, the standard containers; scene-ecs concept 17 (type erasure with `std::function` and `void*`, CRTP, pointers to members) |
| `basics/cpp-modern` | Modern C++ as Strata uses it: move semantics, constexpr, optional, variant, span and concepts | P | L | B, E | `basics/cpp-generic` | new by split of `basics/cpp`; move semantics, `constexpr`, `std::optional`, `std::variant`, `std::span`, `std::string_view`, `enum class`, `if constexpr`, concepts and `requires`, macros, in the measure Strata's code uses them (scene-ecs concept 17) |
| `basics/build` | How a C++ program is built: from two files by hand to CMake | P | L | B, E | `basics/tools`, `basics/programming-3`, `basics/computer` | build-test "How a C++ program is built"; a two-file program built by hand and then with CMake; executables, static and shared libraries (foundation concept 1, which `core/map` needs) |
| `basics/bytes` | Bytes in files and memory: layouts, byte order and text encodings | P | L | B, E | `basics/numbers`, `basics/tools`, `basics/cpp-generic` | new; foundation concept 23; assets concept 19; build-test excerpt 13; files and numbers as bytes, byte order, binary layouts and lengths that cannot be trusted, structs as bytes (`sizeof`, alignment, `offsetof`, `static_assert`), images as bytes, text encodings (Unicode, UTF-8, UTF-16 and code pages); JSON, Base64, hashes and UUIDs are `basics/data-formats`' |
| `basics/data-formats` | JSON, Base64, hashes and UUIDs | P | L | B, E | `basics/bytes` | new by split of `basics/bytes`, which could not hold both lessons at a primer's size; foundation concept 26; numbers written as text and read back exactly, JSON (objects, arrays, strings, numbers, a format header with a version, reading text into tokens by hand, strict against lenient readers), Base64, stable hashes (FNV-1a in `Hash.h`) against `std::hash`, checksums (CRC-32C), cryptographic hashes (SHA-256; HMAC is `automation/security`'), UUIDs |
| `basics/math-vectors` | Vectors: length, direction, dot and cross products | P | L | B, E | `basics/programming-2` | foundation "The math toolkit" (the mathematics: vectors); angles in degrees and radians, sine, cosine and `atan2` |
| `basics/math-matrices` | Matrices and transforms: TRS, hierarchies, spaces and conventions | P | L | B, E | `basics/math-vectors`, `basics/numbers` | foundation "The math toolkit" (the mathematics: matrices); translation, rotation and scale, hierarchies, spaces, the inverse; home of axes, handedness, units and matrix order; bases, the determinant and normals are `basics/math-bases`' |
| `basics/math-bases` | Bases, determinants and normals: orthonormal frames, tangent space, mirrors and the inverse transpose | P | M | B, E | `basics/math-matrices` | new by split of `basics/math-matrices`, which could not hold both lessons at a primer's size; foundation "The math toolkit" (the mathematics: bases); the transpose and orthonormal bases (`Motion::LookAt`), changing basis and tangent space (`TangentBasis`), the determinant and its sign as a mirror, normals through the inverse transpose and the cofactor matrix, decomposing a matrix into translation, rotation and scale and when it fails |
| `basics/math-projection` | Cameras and projection: perspective, homogeneous coordinates and depth | P | L | B, E | `basics/math-matrices` | foundation "The math toolkit" (the mathematics: projections); view and projection matrices, perspective and orthographic, homogeneous coordinates, frustums, depth and reversed Z as mathematics (Lengyel, *Foundations of Game Engine Development* vol. 2 ch. 6); Strata's conventions are `gpu/coordinates`', the code `core/math`'s |
| `basics/math-rotations` | Rotations and quaternions | P | L | B, E | `basics/math-bases` | animation "Rotations that interpolate: quaternions, slerp and TRS"; foundation "The math toolkit" (rotations); Euler angles, axis and angle, quaternions, slerp; the mathematics behind `make/transforms-units` |
| `basics/math-geometry` | Geometry for engines: rays, planes, boxes and intersection tests | P | L | B, E | `basics/math-matrices`, `basics/math-projection` | new; rays, planes, boxes, frustums, intersection tests and their robustness in floating point (Ericson, *Real-Time Collision Detection*) |
| `basics/math-change` | Change over time: rates, accumulation, Euler steps and Newton's laws | P | L | B, E | `basics/math-vectors` | new; derivatives as rates and integrals as accumulation, both from tables of numbers and graphs before any symbol; explicit and semi-implicit Euler steps, and why the step's size matters; Newton's laws (force, mass, acceleration, momentum and impulse); home of rates, integration over time and Newton's laws; blending and smoothing are `basics/math-interpolation`'s |
| `basics/math-interpolation` | Blending and smoothing: lerp, easing, curves and exponential smoothing | P | L | B, E | `basics/math-change`, `basics/numbers` | new by split of `basics/math-change`, which could not hold both lessons at a primer's size; lerp and its weight, inverse lerp and remapping, smoothstep and easing functions, curves through keys (step, linear, cubic Hermite and Bezier at the use level), exponential smoothing (`1 - exp(-k dt)`) and why a fixed fraction per frame depends on the frame rate; home of interpolation as mathematics and of smoothing (interpolating rotations is `basics/math-rotations`') |
| `basics/color` | Color and light for programmers: linear, sRGB and HDR | P | L | B, E | `basics/numbers`, `basics/math-matrices` | new; linear and sRGB values, chromaticity, white point and gamut, the working color space (scene-linear Rec. 709); home of the sRGB transfer function and of the half-float range |
| `basics/signals` | Sampling, aliasing and filtering | P | L | B, E | `basics/math-interpolation`, `basics/color` | new; curricula 1.2 ("Signals"); sampling and Nyquist, kernels, mip prefiltering, ordered dither, spatial denoising; noise and sampling patterns are `basics/math-probability`'s |
| `basics/math-probability` | Chance: probability, noise, integrals and Monte Carlo | P | L | B, E | `basics/math-change`, `basics/signals` | new by split of `basics/math-light`; curricula 1.2 ("Randomness"); random variables, density, expected value, seeds and generators (the SDK's `Random` is PCG32); white and blue noise, Hammersley, Vogel and Poisson patterns, interleaved gradient noise; integrals as areas, Monte Carlo integration; home of noise and sampling patterns |
| `basics/math-sphere` | Directions on a sphere: solid angles, spherical harmonics and octahedral maps | P | L | B, E | `basics/math-probability` | new by split of `basics/math-light`; solid angle, spherical coordinates, spherical harmonics, octahedral maps; home of the mathematics of spherical harmonics |
| `basics/threads` | Threads, atomics and races | P | L | B, E | `basics/computer`, `basics/cpp-generic` | new; foundation concept 16; home of threads, races, mutexes, atomics and memory order in general (Strata's job system is `core/jobs`') |

## Part 3 — Engine architecture (`core`)

Tracks: E.

Needs of the part: `start/what-an-engine-is`, `basics/git`, `basics/build`, `basics/cpp-classes`, `basics/cpp-modern`,
`basics/trees-graphs`, `basics/threads`, `basics/bytes`, `basics/data-formats`, `basics/debugging`,
`basics/math-change`, `basics/math-rotations`, `basics/math-projection`, `basics/math-geometry`.

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `core/map` | How Strata is put together: programs, libraries, modules and layers | C | M | E | `basics/build`, `start/what-an-engine-is` | foundation "What an engine is, and how Strata is put together" (second half); home of "module", "layer", "registry" and "service" (two meanings each) |
| `core/first-change` | Your first engine change: build from source, change one thing, test it | T | L | E | `core/map`, `basics/cpp-classes`, `basics/git` | new; build-test "Building Strata: CMake, presets and configurations" (the source build in short, with tabs per OS; the full options stay in `engineering`); one change; build-test "Testing an engine: doctest, CTest and Strata's test program" (one test case written and run; testing's home is `engineering`) |
| `core/conventions` | Ownership, errors and logging in Strata | I | L | E | `core/first-change`, `basics/cpp-modern` | foundation "C++ for engine code: ownership, errors and logging" (the Strata half; §1.5: logging, asserts, `ErrorThrottle`); the code style and why |
| `core/reading-code` | Finding your way in a large codebase | H | M | E | `core/first-change`, `core/conventions` | new (curricula gap: reading a big codebase); Strata's own tree, with an example inside `core`: one command-line option followed from `CommandLine` to its effect; following a click to a pixel needs the later parts and is an exercise of `capstone/plan` |
| `core/first-frame` | From main to the first frame | I | L | E | `core/conventions` | foundation "From `main` to the first frame" (§1.1: entry point, launch, `ProgramRun`; §1.2: the specification, startup, `ReportFatalError`, exit codes, `CommandLine`) |
| `core/frame-loop` | The frame loop | I | L | E | `core/first-frame`, `basics/threads` | foundation "The frame loop" (§1.2: `Run`, `RunFrame`, skipping, work time, `SubmitToMainThread`, `FramePacer`, timers, shutdown; §1.6: `SleepUntil`) |
| `core/time` | Time: delta time, the fixed step and time scale | C | L | E | `core/frame-loop`, `basics/math-change` | foundation "Time: delta time, the fixed step and interpolation"; physics "Time in a game: the fixed step"; home of "game time counts fixed steps, never frames", the fixed step and time dilation; interpolation in one paragraph (interpolate or extrapolate, one step of latency; Strata's interpolated set is `world/interpolation`'s) |
| `core/windows-events` | Windows, events and layers | I | L | E | `core/frame-loop` | foundation "Windows, events and layers" (§1.4; `Layer` and `LayerStack` of §1.2) |
| `core/engine-modules` | Engine modules | I | L | E | `core/frame-loop`, `basics/trees-graphs` | foundation "Engine modules" (§1.3; device creation in detail is `gpu/vulkan-nvrhi`'s); home of engine services and of the topological sort (Kahn); the exercise: write a `FrameCounterModule` |
| `core/layers-registries` | Layers, registries and the composition root | I | L | E | `core/engine-modules`, `basics/data-formats` | foundation "Layers, registries and the composition root" (§1.1: the composition root, options, state machine, optional modules; §1.10); home of the layer table's rules, optional modules (`ST_WITH_*`), "no tooling in games", registries that open, accept and freeze, and dependency inversion (the CMake that enforces the layers is `engineering/cmake`'s) |
| `core/jobs` | Threads and the job system | I | L | E | `core/frame-loop`, `basics/threads` | foundation "Threads and the job system" (§1.6); home of the threading model and the threads of a process (foundation figure 12) and of "parallel work is deterministic" (ordered records, fixed chunks, serial publish); threads in general are `basics/threads`' |
| `core/platform` | Talking to the operating system | I | L | E | `core/jobs` | foundation "Talking to the operating system" (§1.7: `Platform`; §1.2: interrupts, the GUI subsystem, power throttling; concepts 19, 21-22): seams and detection, console and GUI programs, signals and exit codes, dialogs, thread priorities, sleep precision; files are `core/files`' |
| `core/files` | Files you can trust | I | L | E | `core/platform`, `basics/bytes` | new by split of `core/platform`; foundation §1.7 (`FileSystem`, `AtomicFileWriter`, `FileReader`, `FileLock`, `FileWatcher`, `BoundedRead`), concepts 23-24: UTF-8 paths, atomic writes, private files and TOCTOU; home of atomic writes and private files |
| `core/profiling` | Measuring the frame: the frame profiler, Tracy and the method | I | L | E | `core/jobs` | foundation "Measuring the frame: the frame profiler and Tracy" (§1.5); home of the measuring method: percentiles (taught here, from the average a reader knows), self time, "CPU, GPU or capped" (the CPU and GPU working on different frames is `start/what-an-engine-is`' frame map; the reference machine and the perf tests are `engineering`'s) |
| `core/debugging` | Debugging the engine: debuggers, asserts, the log and crash reports | I | L | E | `core/first-change`, `core/platform`, `basics/debugging` | new (curricula 1.18); foundation §1.5, §1.7 (`Platform`'s debugger functions, memory); debugger setup per OS, asserts and verifies, the log, crash reports, debugging one test; the general method is `basics/debugging`'s |
| `core/math` | Strata's math toolkit | I | M | E | `basics/math-rotations`, `basics/math-projection`, `basics/math-geometry`, `core/conventions` | foundation "The math toolkit" (the code, §1.8): `PerspectiveReverseZ*`, `Ray::FromNDC`, `ComposeWorldTransform` and its FMA rule; culling is `draw/bounds-culling`'s, the conventions are `gpu/coordinates`' |
