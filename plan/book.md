# The book

Working title: **The Strata Engine Book** — *how a game engine works, and how to make games with one*.

This file decides who reads the book, the tracks they read along, the kinds of page, where each concept is taught,
Strata's design decisions, what the book says Strata does not do, the running examples and the parts. The pages
themselves are rows of `plan/outline-1.md` to `outline-4.md`; the reading orders are `plan/tracks.md`; how a page is
written is `plan/style.md`. Every page id in this file is a row of the outline.

## What the owner asked for

Human-facing docs for engine developers and for game developers; complete and detailed to the level of a textbook,
usable as learning material by people who have no idea how to implement an engine or a game; every feature of the
engine, with screenshots (at least of the rendering features); code snippets and whatever else good teaching material
needs; a web project that deploys to the owner's server under `/strata-engine-docs`; a good, easy to understand and
complete textbook on Strata and on engines in general. The owner's server runs nginx, and the book's address is
`https://pdm.pw/strata-engine-docs/` for now; the book is closed source, all rights reserved (`critique/rulings-6.md`,
R20, R23, R24).

## Readers and personas

The book has three personas. Writers write for them, and the provenance reviewer reads each page with their knowledge
lists. The exact lists ("Has" and "Has not", item by item) are in `style.md` §1.1; this table is their summary.

| Persona | Track | Has | Has not | Wants |
| --- | --- | --- | --- | --- |
| **G0, game maker** | G | Installs programs, uses files and folders, school arithmetic and a little algebra | Any programming, any 3D software, a terminal | A finished game |
| **B0, beginner** | B | The same as G0 | The same as G0; B0 also wants every "why" answered on the page or by a page of track B | To understand everything, from zero |
| **E1, engine builder** | E | Has written programs of a few hundred lines in some language; school algebra | C++ beyond the basics, linear algebra, graphics, engines | To understand and change an engine |

- A page is written and reviewed for the least prepared persona of its tracks. From least to most prepared: B0, G0,
  E1. A page on tracks G and B is written for B0.
- A page assumes only what its persona's list holds and what the pages of its Needs closure teach (`style.md` §1.2).
- A Need is always a page of this book, primers included. A page never asks for "some background in X".
- **The fourth reader**, a contributor to the engine or an agent, arrives by search and has no persona. Reference and
  internals pages serve this reader: exact names, the `## Changing it safely` sections, `reference/term-index` and
  `reference/glossary`. The site publishes no separate text for agents: `site.md` does not use `starlight-llms-txt`
  0.12.0, because the book is written for people and is not offered as a corpus. An agent that works on the engine
  has the engine's own guide and skills (`critique/rulings-6.md`, R20).

## Tracks

A track is one reader's way through the book. `plan/tracks.md` writes each track as a numbered list of page ids, and
the site's "next page" and "previous page" links of a track follow that list. Every page shows one badge per track it
is on, with the accessible names "Game maker" (G), "Beginner" (B) and "Engine builder" (E). `plan/check_outline.py`
checks the lists against the outline.

| Track | Persona | Reads | Size |
| --- | --- | --- | --- |
| **G** | G0 | `start` in order (`start/coming-from` is optional); then `make` in order: block A, block B, block C. After `make/first-script` it steps into `basics/programming-1`, `basics/programming-2`, `basics/programming-3` and `basics/debugging`, and comes back at `make/script-loop`. Two side steps: `basics/tools` before `make/first-script`, `basics/math-vectors` before `make/gameplay-math`. | 52 pages and 2 side steps; ends with `make/project-platformer` |
| **B** | B0 | `start` without `start/coming-from`; `make` block A from `make/editor-tour` to `make/lighting`; `basics/computer` and `basics/tools`; `make/first-script`; `basics/programming-1` to `basics/programming-3` and `basics/debugging`; the rest of block A, from `make/script-loop` to `make/project-coin-run`; then the other pages of `basics` in order, from `basics/git` to `basics/threads`. | 53 pages; then the reader continues on track G at `make/gameplay-math` or on track E at `core/map` |
| **E** | E1 | `start` in order; `basics` in order (every primer can be tested out); `core`; `world`; `gpu`; then the later parts in the order of the parts table. Not `make`, `reference` or `appendix`. | 264 pages |

The 29 pages of `reference` and `appendix` are on no track. Readers reach them by links and search.

Rules that hold for every page:

1. Every Need of a page, or one of its alternatives, comes earlier on every track the page is on (checked). Links
   forward in prose are allowed ("the renderer, which part 7 explains"); Needs forward are not.
2. **A game maker never has to read internals.** No page on track G or B is of kind I or R. At this outline, track G
   holds C 6, H 19, P 4 and T 23 pages, and track B holds C 4, H 6, P 30 and T 13.
3. A page on track G or B may link a page that is not on its track, as optional reading ("how it works"). No step,
   question or exercise of the page depends on that page.
4. A side step is offered, never forced. It stands in a Need only as one alternative
   (`` `basics/tools`\|`start/install` ``), and the track's "next page" link passes over it.
5. Track E meets the editor in `start/first-game` and does not read `make`. An E page uses the editor only as far as
   `start/first-game` shows it, or it teaches the step it uses. It may link `make/editor-tour` as optional reading.
6. A track B reader who switches at `make/gameplay-math` or at `core/map` has read every page that the chosen track
   lists before that page, except the optional `start/coming-from` (`plan/tracks.md`).

## Kinds of page

Each page is exactly one kind. The kind is in the front matter and shown as a badge. `style.md` §7 is the full
contract of each shape; this table is its summary.

| Kind | Answers | Shape (body sections in order; every page ends with the bottom strip of `style.md` §6.3) | Pages |
| --- | --- | --- | --- |
| **P primer** | Teach me from zero something that is not Strata's: programming, mathematics, how computers work | A "Test out" box of five questions (a reader who answers all five skips the page) → why you will need this → the idea on the smallest example → worked examples, each with a try-it → common mistakes → practice with answers → where the book uses it | 30 |
| **C concept** | What is the problem, how do engines solve it, what did Strata choose and why | The problem as a reader meets it → the naive answer and where it breaks → the idea → the approaches engines use, with a table of their costs → Strata's choice and its reason → what the choice cannot do and what Strata does not do here → common mistakes | 45 |
| **I internals** | How does Strata's code do it, and how do I change it safely | The job → the problem and how engines solve it (at most a fifth of the prose) → the map of files → the contract → a toy version → the real code walked through → alternatives Strata did not choose → how it is tested → changing it safely → what went wrong before (when the history has a case) | 176 |
| **T tutorial** | Lead me through building one thing | What you will make → what you need → step sections, each step with the result to expect and each section ending in a downloadable checkpoint; runnable as a command script or, when it changes the engine, as a patch (`pipelines.md`) | 34 |
| **H how-to** | I have a goal, give me the steps | The goal and what must be true first → numbered steps → result → variations. No theory: at most two sentences of why, and a link | 24 |
| **R reference** | Give me the exact facts | One paragraph on how to read it → tables generated from the engine, or parsed and checked by a tool → where it lives in Strata | 26 |

Sizes: S about 1,500 words (7 pages), M 3,000 (116), L 5,000 (181), XL 8,000 (31). A size is a budget of prose
words with a range: S 600 to 2,250, M 2,251 to 4,000, L 4,001 to 6,500, XL 6,501 to 10,000 (`critique/rulings-7.md`,
R28). An XL page is split into sections with their own anchors, and past 10,000 words a page splits into pages
(`critique/rulings-4.md`, R7). Pages of kind R have no size check: their size measures the generated volume that their
Fit line states, and their words stay in the book's totals (`critique/rulings-7.md`, R33). Primers and pages of track
B are at most L.

**Generated pages.** Each of the 17 parts with eight or more rows (`make`, `basics`, `core`, `world`, `gpu`,
`assets`, `draw`, `light`, `image`, `indirect`, `physics`, `animation`, `scripting`, `editor`, `editor-ui`,
`engineering`, `reference`) also gets two pages that are not rows, have no kind and are no page's Need:
`<part>/index` (the part's map, the Needs it has outside the part, what the reader can do afterwards) and
`<part>/review` (questions across the part and cumulative exercises). That makes 34 generated pages. No row id ends in
`index` or `review`. A part with fewer than eight rows has no index page: its first page shows the part's Needs in
its top strip ("Before this part") and the part's notation table (`style.md` §6.2, §7.7).

**The usual set per subsystem**: one *use it* page in `make` (tutorial or how-to), one or more concept pages, several
internals pages, one reference page.

## One home per concept

The tables below list the features and concepts that more than one part could claim; a page is the home of
everything in its own Covers (`plan/allocation/<unit>.md`) that no row here names.

The rules:

1. A concept is taught on one page, its **home**. Every other page that needs it says one sentence and links the home.
2. A concept that a game maker acts on also has a **use home** in `make`. The use home teaches everything a game
   maker does with the concept, in a game maker's words. The home explains the mechanism and links back to the use
   home. Pages on tracks G and B link the use home and never need the home.
3. A row that splits a concept names the part each page owns. Neither page repeats the other's part.
4. Where the outline's From column says "home of X" or "use home of X", it names the same page as this table. A brief
   that moves a home changes this table first.
5. A glossary entry names its home page (`home`) and, where there is one, its use home (`use`, `style.md` §3). The
   site's search test expects a concept's home page among the first results (`site.md`).
6. **Words with several meanings.** A word with several meanings gets one qualified glossary entry per meaning, and
   the unqualified word is never a term of its own; a page's term mark chooses the meaning. "Prefetch", "block",
   "journal", "snapshot", "hot reload" and "batch" are examples. `core/map` separates "module", "layer", "registry" and
   "service" before any other page uses them. The glossary step (step 5 of "Next steps" in `plan/README.md`) takes as
   its candidates the homonym groups of `docs-work/B/duplicates/judge_c.txt` and the critics' lists of such words
   (`plan/allocation/completeness.md`; `critique/rulings-7.md`, R33).

The columns: **Home** is the page that teaches the concept. **Use** is the page of `make` that teaches what a game
maker does with it; "home" when the home is itself on track G; "—" when game makers do not act on it. A page of `start`
in this column is a first use, where track G's reader acts on the concept before part `make`; it is no glossary
`use` (`critique/rulings-9.md`, R40). **Others
link** names the pages that use the concept: they say one sentence and link the home (pages on track G link the use
home).

### Programming, mathematics and how computers work

| Concept | Home | Use | Others link |
| --- | --- | --- | --- |
| Programming from zero: values, variables, expressions, decisions, loops, functions, lists, structs, classes, references, files of code, reading errors; the C++ the SDK's calls need at the use level (names in a namespace such as `Key::Space`, scoped enum values such as `CursorMode::Locked`, static member functions, `std::string` and its conversions to and from numbers, pointers and `nullptr`, `std::optional`, template arguments in angle brackets) | `basics/programming-1`, `basics/programming-2`, `basics/programming-3` (a Strata script is the playground; `->`, `nullptr`, `*` in a type, `std::optional`, `has_value` and `value_or` are `basics/programming-3`'s) | home (tracks G and B read them) | `make/first-script`, `basics/cpp-memory`, `basics/cpp-classes` |
| What is special to script code: the `Script` base class, `override`, `ST_SCRIPT_CLASS`, `ST_SCRIPT_FIELD`, no work in the constructor | `make/first-script` | home | `scripting/abi-sdk` (what the macros do), `make/script-fields` |
| The C++ of the engine | `basics/cpp-memory` (pointers, references, lifetimes, RAII, smart pointers); `basics/cpp-classes` (inheritance, virtual calls, interfaces); `basics/cpp-generic` (templates, lambdas, the standard containers); `basics/cpp-modern` (move semantics, `constexpr`, `optional`, `variant`, `span`, concepts) | — | `core/conventions` (Strata's own rules only). These pages extend `basics/programming-1` to `-3`, which use pointers, `std::optional` and template arguments only as far as a script calls them, and explain those features without repeating the primers |
| The terminal, paths, exit codes and the standard streams, environment variables, a code editor, git | `basics/tools`; git `basics/git` | `start/install` (per OS: open a terminal, change folder, run a program of the current folder with arguments, quote a path, paste a command, `sudo` on Linux; on Windows `.\StrataEditor --version \| Write-Output`; a code editor) | `make/script-builds`, `make/automated-playtests`, `make/commands`, `core/first-change` |
| Finding bugs: a method, the log, breakpoints, stepping, the call stack, a debugger attached to the editor | `basics/debugging` | home; `make/play-test-debug` applies it to scripts (a Coin Run script debugged with that debugger) | `core/debugging` |
| How a computer runs a program: CPU, memory, stack, heap, caches, processes | `basics/computer` | `basics/debugging` (a process, and attaching a debugger to the editor's) | `world/what-a-world-is`, `world/ecs`, `core/platform` (Strata's processes and exit codes) |
| Binary, integers, floating point, precision and rounding | `basics/numbers` | — | `draw/mirrors-camera-relative`, `worlds/why-streaming`, `image/pre-exposure`, `physics/scale-streaming`, `engineering/flags-portability` |
| Powers and logarithms: EV stops, decibels; the exponential function and e | `basics/numbers` | `make/lighting` (exposure in EV stops) | `light/units-exposure`, `image/exposure`, `audio/sound-in-a-computer`, `basics/math-interpolation` (`1 - exp(-k dt)`) |
| FMA contraction and floating-point determinism across compilers | `engineering/flags-portability` | — | `core/math` (`ComposeWorldTransform` and its FMA rule), `physics/world-step` |
| Data structures and what they cost: arrays, linked lists, stacks, queues and ring buffers, hash maps and hash functions; arrays of structs against structs of arrays; sparse sets | `basics/data-structures` | — | `world/ecs` (sparse sets), `core/jobs` (job queues) |
| Trees and ordered maps, heaps and priority queues, spatial trees, graphs and their walks, union-find, sorting | `basics/trees-graphs` | — | `assets/references` (reference graphs), `physics/collision-detection` (bounding volume trees), `appendix/game-ai` (A*'s open set) |
| Topological sort (Kahn) | `core/engine-modules` | — | `basics/trees-graphs` (dependency graphs), `world/systems` (the order of scene systems) |
| How a C++ program is built: compiling, linking, executables, static and shared libraries, CMake | `basics/build` | — | `core/map`, `core/first-change`, `engineering/building`, `engineering/cmake` |
| Bytes: files and numbers as bytes, byte order, binary layouts, text encodings and UTF-8 | `basics/bytes` | — | `core/files`, `world/serialization` |
| JSON, Base64, checksums and cryptographic hashes; UUIDs: the standard's 128 bits, Strata's 64 | `basics/data-formats` | `start/how-to-read` (reading a command's JSON); `make/automated-playtests` (writing JSON: objects, arrays, strings, numbers, quotes and commas) | `world/serialization`, `automation/json-rpc`, `assets/handles-meta` |
| Vectors: length, direction, dot and cross products; angles in degrees and radians, sine, cosine, `atan2` | `basics/math-vectors` | `make/transforms-units` (a position or a direction as (x, y, z), adding and scaling them, degrees and radians); `make/gameplay-math` (length, `normalize`, dot, `atan2`, the camera's ray) | `physics/bodies-colliders`, `audio/spatial` |
| Matrices, transforms, hierarchies and spaces; axes, handedness, units and matrix order | `basics/math-matrices` | `make/transforms-units` | `gpu/coordinates` (Strata's API conventions), `core/math`, `world/scene-graph`, `reference/notation` |
| Bases: orthonormal frames, changing basis and tangent space, the determinant and mirrors, normals through the inverse transpose, decomposing a matrix | `basics/math-bases` | — | `draw/mirrors-camera-relative`, `light/materials` (tangent space), `animation/skinning` (the cofactor) |
| Projection: view and projection matrices, homogeneous coordinates, frustums, depth and reversed Z | the mathematics `basics/math-projection`; Strata's conventions, the infinite far plane and depth precision `gpu/coordinates`; the code (`PerspectiveReverseZ*`, `Ray::FromNDC`) `core/math` | — | `draw/bounds-culling`, `light/shadow-basics` |
| Rotations: Euler angles, axis and angle, quaternions, slerp | `basics/math-rotations` | `make/transforms-units` (rotations at the user level: an axis and an angle, a rotation stored as a quaternion and combined by multiplying) | `make/gameplay-math` (Euler angles; forward, right and up), `animation/blending`, `physics/dynamics` |
| Rays, planes, boxes, frustums and intersection tests | the mathematics `basics/math-geometry`; Strata's frustum and box tests (plane extraction, the positive vertex, `AABB::Transformed`) `draw/bounds-culling` | — | `core/math` (the types only), `physics/collision-detection`, `editor/placement`, `ui/input` |
| Change over time: rates and accumulation, the integral as accumulation, explicit and semi-implicit Euler steps, Newton's laws (force, mass, acceleration, momentum, impulse) | `basics/math-change` | `make/physics` (force, mass, velocity and impulse at the use level) | `core/time`, `physics/dynamics`, `basics/math-probability` (integrals as accumulation) |
| Blending and smoothing: lerp and its weight, inverse lerp and remapping, smoothstep, easing, curves through keys, exponential smoothing | `basics/math-interpolation` | `make/gameplay-math` (frame-rate-independent smoothing, `SmoothDamp`) | `world/interpolation`, `animation/clips`, `basics/signals` |
| Color: linear and sRGB values, the sRGB transfer function, chromaticity, white point, gamut, the working color space (scene-linear Rec. 709), the half-float range | `basics/color` | — | `assets/textures` (sRGB textures), `image/encoding` (quantization, dither), `image/grading`, `image/why-post` |
| Sampling, aliasing, filtering; ordered dither; spatial denoising | `basics/signals` | — | `gpu/how-a-gpu-frame-works` (pixels as samples), `assets/textures`, `image/spatial-aa`, `image/taa`, `image/encoding` (dither), `audio/sound-in-a-computer` |
| Probability, random numbers and seeds, Monte Carlo and importance sampling; noise and sampling patterns (white and blue noise, Hammersley, Vogel, Poisson, interleaved gradient noise) | `basics/math-probability` | `make/recipes` (`Random` and seeds) | `light/reflectance`, `light/sun-shadows-2` (the Vogel disk with fixed blue noise), `indirect/problem` (the path tracer sketch), `indirect/ibl`, `indirect/ao` |
| Solid angles, spherical coordinates, spherical harmonics, octahedral maps | `basics/math-sphere` | — | `light/units-exposure`, `indirect/ibl`, `indirect/gi-cascades` |
| Threads, races, mutexes, atomics and memory order in general | `basics/threads` | — | `core/jobs` (Strata's job system only), `audio/engine` |

### Engines, engine architecture and testing

| Concept | Home | Use | Others link |
| --- | --- | --- | --- |
| What a game engine is; a survey of engines | `start/what-an-engine-is` | home | `start/coming-from`, `core/map` |
| The frame map: one frame, start to finish; frame time; the CPU and the GPU working on different frames | for people `start/what-an-engine-is` (frames in flight as a mechanism are `gpu/how-a-gpu-frame-works`'); the renderer's passes `gpu/frame-tour` | home (`start/what-an-engine-is` is on every track) | `core/frame-loop`, `make/script-loop` |
| Strata's names for other engines' ideas (GameObject and entity, prefab variants and overrides, Blueprints and C++ scripts) | `start/coming-from` | home | `make/scenes-entities`, `make/prefabs` |
| "Module", "layer", "registry" and "service": telling apart the two meanings of each word | `core/map` | — | every page that uses the words |
| Errors, asserts and logging in engine code (`ST_CORE_ASSERT`, `ST_CORE_VERIFY`, errors returned, `ErrorThrottle`) | `core/conventions` | — | `core/debugging` (reading asserts and the log while debugging), every internals page |
| Debugging the engine: debugger setup per OS, asserts while debugging, crash reports, debugging one test | `core/debugging` | — | `gpu/debugging`, `scripting/crash-containment`, `scripting/symbolization` |
| The startup: `main`, `ApplicationLaunch`, `GetProgramRun`, the specification | `core/first-frame` | — | `core/frame-loop`, `core/engine-modules`, `core/platform` (console and interactive runs), `worlds/runtime` |
| The frame loop: `Application::Run`, its stages, `Timestep` and the clamp | `core/frame-loop` | — | `core/time`, `core/jobs`, `core/profiling`, `world/systems`, `gpu/how-a-gpu-frame-works` |
| Windows, events, `Handled` and the layer stack | `core/windows-events` | — | `input/how-input-works`, `editor/program`, `editor-ui/imgui`, `worlds/runtime` (the application's layers) |
| The fixed step, the accumulator, time dilation | the concept `core/time`; the code in `Scene` `world/systems` | `make/script-loop` (frame and fixed updates, `FixedRate`) | `physics/dynamics`, `physics/world-step`, `scripting/script-system`, `animation/system`, `editor/stepping` |
| Time scale; unscaled and real time | `core/time` (time dilation) | `make/script-loop` (what time scale does to the loop); `make/timers-events` (the `Time` clocks for timers and pauses) | `make/menus` (a pause menu at time scale 0), `ui/input` |
| Interpolation of fixed steps | Strata's interpolated set, its roles and drawn transforms `world/interpolation`; the idea (interpolate or extrapolate, one step of latency) is one paragraph of `core/time` | `make/characters-cameras` (`GetDrawnPosition` in `OnLateUpdate`, `ResetInterpolation`, platforms in `OnFixedUpdate`) | `physics/world-step`, `draw/render-scene`, `light/lights` (drawn transforms) |
| Engine services and engine modules | `core/engine-modules` | — | `gpu/vulkan-nvrhi`, `audio/engine`, `scripting/host-api` |
| Scene services (`ISkinningPoses`, `IAnimatorControl`, `IAnimationEventSource`, `IUIEvents` and the others) | `world/systems` | — | `animation/system`, `ui/input`, `audio/scene-system` |
| The composition root, dependency inversion, registries that open and accept; the component and settings registries then freeze | `core/layers-registries` (`world/reflection` covers only `ComponentRegistry`'s builder) | — | `world/reflection`, `assets/importing` (importer and loader registries), `world/systems` |
| The layer table, optional modules (`ST_WITH_*`), no tooling in games | the rules, their reasons and tests `core/layers-registries`; the CMake that enforces them (`strata_add_layer_libraries`, the link closure, the linker map, `LayerLibraries.json`) `engineering/cmake` | — | `scripting/why-scripts`, `worlds/export`, `worlds/runtime` |
| The threading model and the threads of a process | `core/jobs` | — | `audio/engine`, `automation/rpc-server`, `core/platform` (thread priorities) |
| Deterministic parallel work: ordered records, fixed chunks, serial publish | `core/jobs` | `make/play-test-debug` ("same inputs, same game") | `physics/world-step`, `animation/system`, `world/serialization` (the parallel writer's deterministic bytes), `input/simulated` |
| Files you can trust: UTF-8 paths, atomic writes, private files, TOCTOU | `core/files` | — | `assets/importing`, `assets/robustness`, `editor/saving`, `engineering/generated-code`, `automation/security`, `automation/sessions` |
| Talking to the operating system: seams, console and GUI programs, signals, exit codes, sleep precision | `core/platform` | — | `core/first-frame`, `worlds/runtime`, `scripting/crash-containment` |
| Measuring the frame: the method, percentiles, self time, "CPU, GPU or capped", Tracy | `core/profiling` | `make/performance` | `physics/tuning`, `gpu/readback-timing`, `engineering/perf-lab` |
| Benchmarks, noise, perf budgets, the perf lab | `engineering/perf-lab` | — | `reference/performance` (every budget, and the machine they were measured on), `core/profiling`, `capstone/land` |
| Strata's math code: `PerspectiveReverseZ*`, `Ray::FromNDC`, `ComposeWorldTransform` | `core/math` | — | `gpu/coordinates`, `draw/bounds-culling` |
| Shared libraries and binary interfaces | `scripting/shared-libraries` | `make/script-builds` (what a module is) | `core/platform`, `scripting/abi-sdk`, `scripting/loading` |
| Testing: test kinds, determinism and flakiness, regression tests that fail without their fix | the concept `engineering/testing`; the program (`TestMain`, shards, labels, locks, helpers) `engineering/test-program` | `make/automated-playtests` (play-tests of a game) | `core/first-change` (one test case, the minimum), the `## How it is tested` section of every internals page |
| Writing a GPU test: the shared `GPUContext`, the error count, pixel readback | `gpu/first-triangle` | — | `engineering/test-kinds` (the suites), `image/tutorial-post-effect`, `gpu/debugging` |
| Corruption sweeps and fuzzing | `engineering/test-program` | — | `assets/robustness`, `assets/extending` |
| Measuring pictures in tests: the flicker metrics (`StrataTests/src/Renderer/FlickerMetrics.h`) and the look-dev harness | flicker metrics `engineering/test-kinds`; the look-dev harness `engineering/look-dev` | — | `image/taa`, `indirect/ssr`, `light/energy` (the white furnace) |
| The feature test | `engineering/feature-test` | — | `world/tutorial-component` (its minimum), `scripting/tutorial-host-function`, `capstone/land` |
| The shader build | writing and registering a shader, the dialect and its checks `gpu/shaders`; the CMake custom commands, `StrataShaderTool`'s SPIR-V patch and the generated registry `engineering/generated-code`; Slang's pinned download `engineering/third-party`; the CI's shader steps `engineering/ci` | — | each of the four names the others in one sentence |
| Building Strata from source | the short build with tabs per OS, and the term "Dist" (the shipping configuration), `core/first-change`; every preset, configuration and option in full `engineering/building` | — | `engineering/ci`, every tutorial that changes the engine |
| Hot reload of scripts | `scripting/hot-reload` | `make/first-script` | `editor/script-builds` |
| Hot reload of assets | `assets/importing` | `make/assets` | `scripting/hot-reload` (the other meaning) |

### Scenes and assets

| Concept | Home | Use | Others link |
| --- | --- | --- | --- |
| Object models: inheritance, components, ECS | `world/what-a-world-is` | `make/scenes-entities` | `world/ecs` |
| Handles instead of pointers; UUIDs as stable identities | `world/ecs` | `make/assets` (one paragraph) | `assets/handles-meta` (asset handles only) |
| The transform contract and change signals | `world/scene-graph` | — | `ui/contract` (the UI contract mirrors it), `draw/render-scene`, `physics/building-bodies` |
| Reflection: one registration, many uses | `world/reflection` | — | `editor-ui/inspectors`, `editor/commands`, `scripting/abi-sdk`, `world/serialization`, `reference/components` |
| Scene documents: the text form, streams, the cooked form (STSC) and its validation | `world/serialization` | — | `assets/packs-export` (when and why the export cooks documents), `editor/saving` |
| Prefabs | the data model, overrides and propagation (`EntityPrototype`, instantiation, `PrefabInstances`, `PrefabOverrides`) `world/prefabs`; keeping instances exact while editing (`PrefabSync`, `UpdatePrefabOverrides` in `CommitEdit`, baselines, apply and revert as undo steps) `editor/prefab-instances` | `make/prefabs` | `assets/models-gltf` (models as entity templates), `editor-ui/inspectors`, `start/coming-from` |
| Loading scenes: whole, additive and in slices (`SceneLoader` and its states, prepared loads with `PrepareSystems` and `PrepareLoadedScene`, `RequestSceneLoad`, `ReleaseInBackground`, the frame's `SceneWorkBudget`) | `world/sub-scenes` | `make/levels-saves` (additive loads, loading screens, state passed between scenes) | `worlds/physics-scripts` (the World system's prepared start), `editor/projects` (opening scenes in the background), `worlds/runtime` |
| Scene switches: `Game::LoadScene`, `ReloadScene`, quitting | in a shipped game `worlds/runtime` (`GameRuntime`); in the editor's play mode `editor/play-mode` | `make/levels-saves` | `world/sub-scenes`, `make/project-coin-run` (`ReloadScene` in one step) |
| Game flow: levels, win, lose, restart, save files | `make/levels-saves` | home | `make/project-coin-run`, `worlds/game-identity` (saves keyed by the manifest's Name) |
| Projects and settings sections: versions, validation, `IProjectSettings`, the hand-over to scenes | `world/projects-settings` | `make/project-files` | `editor-ui/settings-windows`, `reference/settings`, `physics/collision-layers` |
| The project folder and its files | `make/project-files` | home | `world/projects-settings`, `editor/projects` |
| What an asset is: sources and cooked forms | `assets/what-is-an-asset` | `make/assets` | `world/serialization` |
| Asset handles, `.meta` files and sub-assets | `assets/handles-meta` | `make/assets` | `world/ecs` (handles in general), `worlds/grids` (derived handles) |
| Importing: import records, cache validity, background imports, cancellation | `assets/importing` | `make/assets` | `assets/texture-cooking`, `assets/models-gltf`, `image/grading` |
| Textures for the GPU: mips, color spaces, block compression | the problem and the formats `assets/textures`; Strata's importer, cooker and BC7 encoder, `GetMipByteSize` `assets/texture-cooking` | `make/assets` (import settings, Fast and High); `make/materials` (normal maps and `FlipGreen`) | `light/materials`, `light/sky` (what `HDRSun` does) |
| Models and the glTF importer: the model as an entity template, its sub-assets | `assets/models-gltf` | `make/assets` | `animation/importing`, `animation/problem`, `draw/lod` (levels made at import) |
| Loading without stalling | `assets/loading` | — | `draw/asset-requests`, `animation/clips`, `audio/clips-voices-sources` |
| Residency, pins and eviction | `assets/residency` | `make/scripting-scene` (asking for assets early: `Instantiate` never waits); `make/sound` (request in `OnCreate`); `make/levels-saves` (loading screens) | `draw/asset-requests`, `worlds/streamer`, `ui/drawing`, `scripting/script-system` (asset pins), `animation/system` |
| References, closures, load progress and prefetch | `assets/references` | `make/levels-saves` (loading screens) | `worlds/physics-scripts` (prefetch before a teleport), `editor/trash-references`, `make/large-worlds` |
| Budgeted uploads: what is queued and when | `assets/uploads` (the mechanism is `gpu/upload-queue`'s) | — | `draw/mip-streaming` |
| Untrusted input (validate before use, checksums, bounded sizes) and write-ahead ordering | `assets/robustness` | — | `gpu/text` (font validation), `worlds/game-identity` (the manifest is untrusted), `automation/security`, `engineering/test-program` |
| The export | the pack (format, planning, pruning, `AlwaysInclude`, patches, cooked documents) `assets/packs-export`; the export as a whole (`GameExport`, its state machine, up-front checks, world cooking, what the folder holds) `worlds/export`; the manifest and the game's identity `worlds/game-identity` | `make/export` | `world/projects-settings`, `editor-ui/launcher-dialogs` (the Export dialog), `worlds/runtime` |

### The GPU, drawing and the image

| Concept | Home | Use | Others link |
| --- | --- | --- | --- |
| How a GPU works and draws a frame: waves, occupancy, bandwidth, the pipeline, frames in flight | `gpu/how-a-gpu-frame-works` | — | every page of `draw`, `light`, `image` and `indirect` |
| The graphics API and its wrapper: Vulkan, NVRHI, the graphics device, validation layers and error counting, the swap chain and presentation | `gpu/vulkan-nvrhi` (the term Present is `gpu/how-a-gpu-frame-works`'; the Present stage is `gpu/upload-queue`') | — | `gpu/first-triangle`, `gpu/resources-lifetimes`, `gpu/debugging`, `draw/gpu-driven` (device features and limits), `image/encoding` (the swap chain) |
| Compute shaders: dispatches, thread groups, shared memory, atomics, UAV barriers | `gpu/compute` | — | `gpu/resources-lifetimes` (states and barriers in NVRHI), `draw/gpu-driven`, `light/many-lights`, `image/exposure`, `indirect/ao` |
| The camera (`CameraComponent`, projection, Primary, physical fields) and Strata's clip space, depth conventions and precision, UVs | `gpu/coordinates` (it states the counter-clockwise convention only) | `make/look`, `make/characters-cameras` | `world/scene-graph` (the primary-camera lookup), `image/exposure`, `image/depth-of-field` (the depth-of-field fields), `editor/camera-viewport` |
| Debugging the GPU: running with the validation layer, debug names and markers, frame captures, the error count; the list of debug views and the page that reads each | `gpu/debugging` (what validation layers are and how errors are counted is `gpu/vulkan-nvrhi`'s) | — | `light/measuring-light`, `engineering/test-kinds` |
| Resources, lifetimes, deferred release | `gpu/resources-lifetimes` | — | `gpu/upload-queue`, `assets/residency` |
| Staging and the upload queue (`PlanStep`, `StagingPool`, the transfer queue, `PrepareBackBuffer`) | `gpu/upload-queue` (what assets queue and when is `assets/uploads`') | — | `draw/render-scene-gpu`, `draw/mip-streaming`, `ui/drawing` |
| Pipelines and binding: the `PipelineKey` cache, layouts, registers, bindless | `gpu/binding` | — | `gpu/frame-tour`, `draw/batching`, `light/material-data` |
| Meshes on the GPU and the geometry pool | `gpu/geometry-pool` | — | `draw/batching`, `assets/models-gltf`, `indirect/gi-voxels` |
| Forward, deferred and visibility buffers; the depth prepass, `EQUAL` and invariant positions | `gpu/frame-tour` | — | `light/many-lights` (tiled against clustered), `light/brdf` (the `EQUAL` test), `gpu/shaders`, `draw/lod`, `draw/skinned`, `draw/motion-vectors` |
| Readback and GPU timestamps and stages | `gpu/readback-timing` | `make/performance` | `core/profiling` (shows them), `editor-ui/scene-view` (picking's one-pixel readback), `image/pre-exposure` |
| Overlay passes (`SceneOverlayRegistry`) and debug drawing | `gpu/debug-drawing` | — | `ui/drawing`, `editor-ui/scene-view` |
| Text: fonts, `ShapeText` layout, the glyph atlas, signed distance fields, font validation (`FontValidation`) | `gpu/text` | `make/hud` (`TextComponent`, text without a canvas) | `ui/text` (how rects, sizes and overflow modes drive `ShapeText`), `editor-ui/design-system` (the editor's fonts use ImGui's own atlas), `assets/robustness` |
| CPU and GPU culling paths | the CPU path first `draw/bounds-culling`, then the GPU path `draw/gpu-driven` | — | `light/many-lights`, `light/sun-shadows-1`, `light/local-shadows` |
| The render scene: persistent proxies, records and change logs, the lights' records included | `draw/render-scene` (what a light record holds, `LightData` and the sun's choice are `light/lights`') | — | `draw/render-scene-gpu` (the GPU copy follows the logs), `light/sun-shadows-1`, `light/local-shadows` (shadow caches) |
| The screen fraction (`GetScreenFraction`, "How big does it look?") | `draw/bounds-culling` | — | `draw/lod`, `draw/asset-requests`, `draw/mip-streaming` |
| Batching, the draw list, sort keys, instancing; the transparent pass's back-to-front order | `draw/batching` | — | `light/clearcoat-transmission` |
| Mirrored transforms and camera-relative rendering | `draw/mirrors-camera-relative` | — | `gpu/coordinates`, `worlds/why-streaming`, `make/large-worlds`, `light/material-data` (flipped tangents) |
| Mip streaming: partial loads, range reads, wanted levels, fades, bindless slots resolved every frame | `draw/mip-streaming` | — | `draw/asset-requests`, `assets/residency`, `assets/texture-cooking` |
| Skinned meshes in the renderer (`ST_SKINNED` variants) and posed bounds | `draw/skinned`; how the joint matrices are made `animation/skinning`; reach `animation/culling` | `make/animation` | `draw/motion-vectors` |
| Motion vectors and motion history | `draw/motion-vectors` | — | `image/taa`, `image/motion-blur`, `indirect/ssr` |
| Why images need post-processing; the post chain, `PostSource`, the fullscreen pass | `image/why-post` | `make/look` | `image/tutorial-post-effect`, `image/lens-effects` |
| The HDR target, half-float limits, `SanitizeHDR` | the idea and the half-float range `basics/color`; the HDR target and the chain `image/why-post`; `SanitizeHDR`, which the first pass that writes HDR values calls, `light/brdf` | `make/look` | `image/lens-effects`, `gpu/frame-tour` |
| Camera exposure, EV100, metering, adaptation, the exposure key | `image/exposure` | `make/lighting` (exposure); `make/look` | `light/units-exposure`, `light/measuring-light` |
| Pre-exposure: power-of-two scaling, readbacks, epochs, settling, the TAA rescale | `image/pre-exposure` (one paragraph on why is in `light/units-exposure`) | — | `indirect/probes` (the bake's pre-exposure), `indirect/ssr`, `image/taa` |
| Tone mapping and the Filmic curve | `image/tone-mapping` | `make/look` | `image/grading` |
| White balance, grading and lookup tables | `image/grading` | `make/look` | `basics/color` (white point, chromaticity), `assets/importing` (the `.cube` importer), `image/tutorial-post-effect` (neutral settings) |
| Display encoding, dither and grain | `image/encoding` (dither's idea stays `basics/signals`') | `make/look` | `image/spatial-aa` (the last pass's dither), `basics/color` |
| Lens effects: bloom, vignette, flares, fringes | `image/lens-effects` | `make/look` | — |
| Anti-aliasing in one frame: FXAA and morphological AA | `image/spatial-aa` | `make/quality` (choosing the anti-aliasing) | `image/taa` |
| Temporal anti-aliasing; jitter on the frame's camera copy only | `image/taa` | `make/quality` | `gpu/frame-tour`, `gpu/debug-drawing`, `light/sun-shadows-2`, `draw/motion-vectors` |
| Motion blur | `image/motion-blur` | `make/look` | `draw/motion-vectors`, `image/depth-of-field` (the blur mask) |
| Depth of field | `image/depth-of-field` | `make/look` | `gpu/coordinates` |
| The quality rows of a feature | the feature's own page (its row and its cost) | `make/look` (the quality rows of each effect) | `image/quality-settings` (presets, traits, players' options) |
| Players' graphics options (`IGameGraphics`, the options file, the SDK's `Graphics`); presets and traits | `image/quality-settings` | `make/quality` | `make/menus` (the settings screen), `editor-ui/settings-windows` (the Graphics Quality page), `worlds/runtime` (the graphics service) |

### Light and indirect light

| Concept | Home | Use | Others link |
| --- | --- | --- | --- |
| Light units: radiometric and photometric quantities, conversions, reference values, the sun-to-sky ratio | `light/units-exposure` | `make/lighting` | `image/exposure`, `make/look`, `light/lights`, `light/area-lights` (the units of rectangle lights) |
| Strata's material model: maps, alpha modes, emission in nits, plausible albedos, IOR as a field, normal maps and tangent space | the concept `light/materials`; the GPU record (`MaterialGPU::Build`, `MaterialData`, the texture table, the XY normal decode) `light/material-data` | `make/materials` (the maps, alpha modes, normal maps and `FlipGreen`, emission as a color and a strength); `make/lighting` (emission in nits) | `assets/textures` (BC5), `draw/mirrors-camera-relative` (handedness) |
| How surfaces reflect light: radiance and irradiance in use, the reflection equation, Lambert, microfacets, Fresnel and F0 from IOR | `light/reflectance` | — | `light/brdf` (the code), `indirect/problem` (the full rendering equation), `indirect/ssr` (F0 from IOR) |
| The forward shader's anatomy and shading order; GGX, Smith, Schlick; the derivative rule and specular anti-aliasing | `light/brdf` | — | `indirect/seam`, `image/why-post`, `draw/gpu-driven` (shading independent of draw order) |
| Directional albedo, the BRDF table, energy compensation, the white furnace | `light/energy` (the split sum's prefiltered half is `indirect/ibl`'s) | — | `light/brdf`, `indirect/ibl`, `indirect/seam`, `engineering/look-dev` |
| Measuring light: the lighting, luminance, albedo and indirect views, their statistics, measuring the sun-to-sky ratio in a scene | `light/measuring-light` | `make/lighting` (luminance and albedo); `make/materials` (the albedo audit) | every page of `light`, `image` and `indirect` |
| The other debug views, each read where its subject is | streaming `draw/asset-requests`; lod `draw/lod`; mip `draw/mip-streaming`; motion `draw/motion-vectors`; shadows `light/sun-shadows-1`; ao `indirect/ao`; the GI views, voxels included, `indirect/gi-cascades`; the list and the mechanism `gpu/debugging` | `make/lighting` | `light/measuring-light` |
| Lights: the sun, points and spots, falloff, cones, one sun, preview lighting | `light/lights` | `make/lighting` (the sun, preview lighting); `make/lamps` (points and spots) | `light/many-lights`, `indirect/probes` |
| Many lights: light culling, clusters, tiled against clustered shading | `light/many-lights` | — | `light/area-lights`, `light/local-shadows` |
| Lights with size: sized highlights (lobe widening) and area lights | `light/area-lights` | `make/lamps` | `light/lights`, `indirect/probes` (bakes draw no highlights), `light/local-shadows` (the soft shadows of rectangle lights), `light/clearcoat-transmission` (the coat under rectangle lights) |
| Shadow mapping: comparisons, acne and biases, alpha-masked casters | `light/shadow-basics` | `make/lighting` (sun shadows); `make/lamps` | `light/sun-shadows-1`, `light/local-shadows` |
| Sun shadow casters (`FindShadowCasters`, `CanShadowView`), the cascade cache and its versions, cascade occlusion | `light/sun-shadows-1` | — | `draw/bounds-culling`, `draw/occlusion`, `draw/gpu-driven` |
| Local shadow casters (`FindLocalShadowCasters`), the atlas, view caches and their culling | `light/local-shadows` | `make/lamps` | `draw/gpu-driven`, `light/many-lights` |
| The sky as a light: the three sky sources, the procedural sky, environment maps, Extract and Remove Sun, presets, `HDRSun` | `light/sky` (`assets/texture-cooking` gives the `HDRSun` setting) | `make/lighting` (choosing the sky source and its preset) | `indirect/ibl`, `make/reflections` |
| The default template's lighting | `make/lighting` | home | `editor/projects` (templates) |
| Participating media: extinction, transmittance, phase functions; aerial perspective | `light/atmosphere` | — | `light/fog`, `light/clearcoat-transmission` (Beer's law), `indirect/gi-cascades` (the march) |
| Height fog | `light/fog` | `make/look` | — |
| Transparency, blending and premultiplied alpha; scene-color copies; clear coat and glass | `light/clearcoat-transmission` | `make/materials` (alpha modes, glass) | `draw/batching` (the back-to-front order), `image/taa` (the reactive mask), `indirect/ssr` |
| The indirect-light problem: the rendering equation, the families of techniques, a path-traced reference image | `indirect/problem` | — | `indirect/ao`, `indirect/probes`, `indirect/gi-cascades` (they compare their figures with its reference) |
| Image-based lighting, the split sum, the horizon fade | `indirect/ibl` | `make/reflections` | `light/brdf`, `light/energy` |
| Where indirect light meets the surface: inputs, gathers, the fallback stack | `indirect/seam` | — | `indirect/probes`, `indirect/ssr`, `indirect/gi-cascades` |
| Ambient occlusion | `indirect/ao` | `make/reflections` | `indirect/gi-cascades` |
| Reflection probes and their bakes | `indirect/probes` | `make/reflections` | `indirect/ssr` (probes are its fallback) |
| Screen-space reflections | `indirect/ssr` | `make/reflections` (a wet floor) | `image/taa` (the Checkerboard exception) |
| Global illumination | `indirect/gi-voxels`, `indirect/gi-cascades`; what it does not do `indirect/gi-limits` | `make/gi` | `image/quality-settings` (the GI row) |

### Simulation, gameplay and game UI

| Concept | Home | Use | Others link |
| --- | --- | --- | --- |
| Rigid bodies and colliders | `physics/bodies-colliders` | `make/physics` | `physics/building-bodies` |
| Collision detection: broad and narrow phase | `physics/collision-detection` | — | `physics/world-step`, `physics/queries` |
| Rigid body dynamics: integration, contacts, solvers, sleep, continuous collision | `physics/dynamics` | — | `physics/world-step`, `physics/tuning` |
| Collision layers: the project's table, filter bits, the scene's working copy | `physics/collision-layers` | `make/physics` | `physics/queries`, `editor-ui/settings-windows` |
| Contacts and triggers reaching scripts | `physics/contacts-triggers` | `make/physics` | `scripting/script-system` |
| Physics queries: raycasts, overlaps, masks | `physics/queries` | `make/physics` | `physics/character-controllers` |
| Character controllers | `physics/character-controllers` | `make/characters-cameras` | `animation/root-motion` |
| Physics capacity, the growth limit, `Reserve`, sliced and parallel creation, parking, the 1e5 m limit | `physics/scale-streaming` | — | `worlds/physics-scripts` (what a world reserves, `MaxBodiesInRadius`, the cook, prefetch before a teleport) |
| Tuning physics: `Physics.Simulation`, contact recycling, the sleep threshold, `physics.stats` | the idea of contact recycling (narrow-phase caching between steps) `physics/collision-detection`; the settings (`ContactRecycleDistance` and the others of `Physics.Simulation`) and the solver side `physics/tuning` | `make/physics` (the game maker's half) | `engineering/perf-lab` |
| Animation: skeletons, clips, state machines, blending, events, root motion | `animation/skeletons`, `animation/clips`, `animation/state-machines`, `animation/blending`, `animation/time-events`, `animation/root-motion` | `make/animation` | `physics/character-controllers` (the root-motion hook) |
| Edit-mode poses and previews | `animation/editor` | `make/animation` (the how-to half) | `editor-ui/inspectors` |
| Sound inside a computer: samples, frames, channels, gain and decibels, the pull model | `audio/sound-in-a-computer` | `make/sound` | `audio/engine`, `audio/spatial` |
| Clips, voices and sources; load modes | `audio/clips-voices-sources` | `make/sound` | `audio/scene-system` |
| Sound in space: panning, attenuation, Doppler | `audio/spatial` | `make/sound` | `audio/scene-system` |
| How input reaches a game: events, polling, edges, intents | `input/how-input-works` | `make/input` | `input/devices-state` |
| Input ownership: the enabled flag, typed text, keyboard and pointer capture | the engine's side `input/devices-state`; how `Input::SetViewport` maps coordinates inside `Input` `input/mouse-cursor`; the Game view's call of `SetViewport`, its resolutions, letterboxing, the cursor lock and Shift+F1 `editor-ui/game-view` | `make/menus` (typed text in a text field) | `input/mouse-cursor`, `ui/input`, `ui/text` |
| Input actions; UI actions and menu key repeat | `input/actions` | `make/input` (actions); `make/menus` (UI actions, navigation) | `ui/input` |
| Players' bindings and binding capture | the engine's side (the bindings file, capture in `InputActions`) `input/rebinding` | `make/menus` (binding capture, saving the bindings and the rebinding screen); `make/input` (actions and their default bindings) | `editor-ui/settings-windows` (`BindingCapture`) |
| Simulated input | the virtual devices, the merge rules, release and clear, determinism `input/simulated`; holds counted in fixed steps, `input.sequence` and `input.click` `editor/stepping` | `make/automated-playtests` | `automation/agents`, `make/with-an-agent` |
| Why game code lives outside the engine; how other engines script | `scripting/why-scripts` | `start/welcome` (game logic is C++) | `scripting/shared-libraries` |
| The script ABI and the SDK over it; append-only tables | `scripting/abi-sdk` | — | `scripting/loading`, `scripting/host-api`, `scripting/tutorial-host-function`, `engineering/feature-test`, `worlds/physics-scripts` |
| Loading, calling and validating modules | `scripting/loading` | — | `scripting/crash-containment`, `scripting/script-system`, `scripting/hot-reload` |
| The script lifecycle and its callbacks | `make/script-loop` | home | `scripting/script-system` (the code: it names the callbacks and their order for track E, which does not read `make`) |
| The script system: instances, callbacks dispatched, fields | `scripting/script-system` | `make/script-loop` | `scripting/hot-reload`, `scripting/host-api`, `ui/input`, `editor/play-mode`, `worlds/runtime` |
| Building script modules | from the editor (toolchains, CMake, diagnostics for the Problems panel, building before Play) `editor/script-builds`; outside the editor `make/script-builds` | `make/first-script` (building in the editor); `make/script-builds` | `start/install` (the toolchain check) |
| Crash containment; from an address to a file and line | `scripting/crash-containment`; `scripting/symbolization` | `make/first-script` (the crash toast) | `scripting/script-system`, `scripting/host-api` |
| The host API: engine services behind a C table | `scripting/host-api` | — | `scripting/tutorial-host-function`, `reference/script-api` |
| Patterns for game code: state machines, managers, object pools | `make/patterns` | home | `make/recipes`, `make/project-tetris` |
| Planning a small game: the core loop, scope, prototype, playtest | `make/designing-a-game` | home | `make/project-tetris`, `make/project-platformer` |
| What a game UI must do; retained against immediate UIs | `ui/what-game-ui-does` | `make/hud` | `editor-ui/immediate-mode` (why the editor's UI is immediate), `editor-ui/imgui` |
| Rects, anchors and layout | `ui/layout` | `make/hud` (canvases and anchors) | `ui/contract` |
| The UI contract | `ui/contract` | — | `ui/drawing`, `ui/input` |
| Text and text fields in game UI | `ui/text` | `make/hud`; `make/menus` | `gpu/text` |
| UI input: hit grids, world-space rays, navigation, events | `ui/input` | `make/menus` | `input/actions` |
| Testing game UI through commands (`ui.create`, `ui.layout`, `ui.hitTest`, `input.click`) | `make/automated-playtests` | home | `ui/input` |
| Why levels must stream; the 20 km limit | `worlds/why-streaming` | `make/large-worlds` | `draw/mirrors-camera-relative`, `basics/numbers` |
| Grids, cells and the streamer | `worlds/grids`, `worlds/streamer` | `make/large-worlds` | `editor/worlds`, `worlds/physics-scripts` |
| A game's identity: the manifest, icons, platform files | `worlds/game-identity` | `make/export` | `worlds/runtime` |
| The runtime: `StrataRuntime`, `GameRuntime`, options and exit codes, headless runs | `worlds/runtime` | `make/export` (running the exported game); `make/performance` (`--perf-log`) | `reference/worlds-runtime` |

### The editor and automation

| Concept | Home | Use | Others link |
| --- | --- | --- | --- |
| What an editor is, and why it is not the game | `editor/program` | — | `editor-ui/immediate-mode` |
| The tour of the editor | `make/editor-tour` (its anatomy, for people who change it, is `editor-ui/shell`'s) | home | `editor/program` |
| Commands are the API: three clients, one registry | `editor/commands` | `make/editor-tour` (the command tab of every tutorial) | `automation/agents`, `automation/mcp`, `make/commands`, every tutorial |
| Commands that take frames (`Defer`, `MayDefer`, `WaitsForAssets`) | `editor/deferred-commands` | — | `automation/rpc-server`, `editor/projects` |
| Launcher, templates and samples | the model (templates, samples as copies, recent projects) `editor/projects`; the UI `editor-ui/launcher-dialogs`; project pictures `editor/thumbnails` | `start/first-game`; `make/samples` | `make/lighting` (the default template's lighting) |
| Undo and redo | `editor/undo` | `make/project-files` | every editor command, `editor/tutorial-command` |
| No silent data loss: saves off the main thread, the unsaved-changes guard, `AfterSaves`, `ResetScene` | `editor/saving`; asking the person (modals, the re-ask rule, `DrawDiscardQuestion`) `editor-ui/shell` | `make/project-files` | `editor/recovery` |
| Autosave and crash recovery | `editor/recovery` | `make/project-files` | `editor-ui/launcher-dialogs` (the recovery dialog) |
| The trash, references and undoing asset deletes | `editor/trash-references` | `make/assets` | `assets/references` |
| Play and Simulate: the running copy, the game shell, edits while playing | `editor/play-mode` | `make/play-test-debug` | `world/systems`, `audio/scene-system`, `scripting/script-system`, `editor-ui/game-view` (its drawing) |
| Pausing and stepping a game | `editor/stepping` | `make/play-test-debug` | `core/time` (one sentence), `input/simulated` |
| The activity journal: command origins and kinds, the replay export (`BuildReplayScript`), agent presence | `editor/journal` | `make/with-an-agent` | `editor-ui/instrument-panels` (the Activity panel's drawing), `automation/agents` |
| Command scripts (`expect`, `bind` and `$ref`, `until`) and `editor.batch` | `editor/command-scripts` | `make/automated-playtests` (play-tests, record and replay); `make/commands` (scripts that build content) | `engineering/test-kinds`, `automation/agents` |
| Placing content: `asset.place`, the drop and its ghost | `editor/placement` | `make/prefabs` | `editor-ui/scene-view` |
| Editing a streamed world | `editor/worlds` | `make/large-worlds` | `worlds/streamer` |
| The editor camera, per-scene cameras, viewport settings | `editor/camera-viewport` | — | `editor-ui/scene-view` |
| Picking (the asynchronous entity-ID readback) and gizmos (`TransformDrag`) | `editor-ui/scene-view` | — | `gpu/readback-timing` (the one-pixel readback), `editor/undo` (`TransformDrag` as a merge-key example) |
| Dear ImGui from first principles | `editor-ui/imgui` | — | `editor-ui/immediate-mode` |
| The editor's theme, fonts and icons (ImGui's own atlas, not `FontAtlasCache`) | `editor-ui/design-system` | — | `gpu/text` |
| Lists that scale: `HierarchyView`, `AssetBrowserView`, `ImGuiListClipper`, multi-select | `editor-ui/lists` | — | `editor-ui/instrument-panels` |
| Notifications (`EditorNotifications`, their drawing), the status bar, idle throttling | `editor-ui/status` | `make/performance` (idle throttling, said where the frame time is read) | `editor-ui/instrument-panels` |
| Editor shortcuts and keyboard focus | `editor-ui/game-view` | `make/editor-tour` | `reference/editor` |
| Inspectors from reflection; inactive reasons | inactive reasons (`ComponentRegistry::SetInactiveReason`, its rule and its term) `world/reflection`; inspectors from reflection, and how the Inspector shows an inactive reason, `editor-ui/inspectors` | — | `capstone/build`, `image/why-post`, `image/quality-settings`, `indirect/gi-voxels`, `animation/state-machines`, `ui/layout` |
| Why automate an editor; tools for agents; accountability; determinism for agents | `automation/agents` | `make/with-an-agent` | `automation/mcp` |
| Sockets, framing and JSON-RPC | `automation/json-rpc` | — | `appendix/networking` |
| The editor's RPC server: connections, the network thread, limits | `automation/rpc-server` | — | `automation/security`, `automation/sessions`, `editor-ui/status` (the server's clients) |
| The security model: loopback, the token, the handshake, untrusted session files | `automation/security` | — | `automation/sessions`, `appendix/networking`, `reference/automation` |
| Sessions, discovery and launching | `automation/sessions` | `make/with-an-agent` (starting an editor) | `automation/mcp`, `editor-ui/launcher-dialogs` (the automation options) |
| The MCP server and its toolsets | `automation/mcp` | `make/with-an-agent` (toolsets) | `make/commands` |
| What a subsystem does not do | the subsystem's page named in "What Strata does not do" (`animation/limits`, `indirect/gi-limits`, or a section of the page) | the `make` page that the entry names, where it names one | `appendix/not-in-strata` (it indexes them and gives the general technique) |
| Notation: axes, handedness, units, matrix order, depth and color spaces, the symbols of the rendering parts | each item's home above; `reference/notation` collects them in one place and defines nothing | — | `appendix/math-cheatsheet` |

## Strata's design decisions, taught as decisions

These decisions recur through the book. Each is stated once, with its reason, on its home page (in a `:::why` aside,
`style.md` §12), and named in one sentence wherever it shapes the code. The evidence is at the pin, `822a7a46`.

| Decision, as the book states it | Home | Named again in | Evidence |
| --- | --- | --- | --- |
| Strata never renders below native resolution: no render scale below 1, no dynamic resolution, no temporal upscaling. | `image/quality-settings` | `make/quality` (why there is no render scale), `image/spatial-aa`, `image/taa` | `Docs/Roadmap.md:1642-1643`; `Docs/Releases/0.7.0.md:408-409` |
| Nothing needs history to look right: TAA is one anti-aliasing choice, and every other effect looks right in a single frame. One named exception: Medium's Checkerboard screen-space reflections leave their noise to TAA's history. | `image/taa` | `indirect/ssr` (the exception), `indirect/ao` (a fixed pattern, denoised within the frame), `light/sun-shadows-2` (fixed blue noise) | `Docs/Roadmap.md:951-953, 1642-1643`; `AGENTS.md:402-404, 410-411` |
| Global illumination traces world data, never the screen. | `indirect/problem` | `indirect/gi-voxels`, `indirect/gi-cascades`, `make/gi` | `AGENTS.md:405-406` |
| A feature that is off is invisible bit for bit and costs nothing. Global illumination that is off is invisible bit for bit; what it still costs is measured and stated. | as a rule of the renderer `gpu/frame-tour` (its brief checks that "costs nothing" holds for each switch it names); for global illumination `indirect/gi-limits`, which states the cost when off as measured at the tag | `indirect/seam` (the join keeps the old expression), `image/tutorial-post-effect` (`AddNeutralPostProcess` turns post effects off) | `AGENTS.md:399-401, 405-406`; `Docs/DeveloperGuide.md:4968`; `Docs/Plans/Wave8/ReleaseNotes.md:383-386` (off, global illumination spends 0.010 to 0.014 ms more in `GPU.Opaque`; images are unchanged) |
| Light is measured in real units, and a pre-exposure keeps the HDR values in range. | `light/units-exposure` (the `:::why` aside) | `image/pre-exposure` (the mechanism; one sentence names the decision and links back), `make/lighting`, `image/exposure`, `light/lights` | `Docs/DeveloperGuide.md:4005` |
| Game time counts fixed steps, never frames. | `core/time` | `world/systems`, `make/script-loop`, `editor/stepping`, `physics/world-step` | `AGENTS.md:369-370` |
| Parallel work is deterministic: the result does not depend on the number of threads. | `core/jobs` | `world/serialization` (the parallel writer's bytes), `physics/world-step`, `animation/system`, `make/play-test-debug` | `AGENTS.md:308-309`; `Docs/DeveloperGuide.md:2209-2212` |
| Trade-offs are measured on the reference machine, and the numbers are shown. | `engineering/perf-lab` | `core/profiling` (the method), `reference/performance` (every budget and the machine), `make/performance` | `AGENTS.md:109-111`; `Docs/DeveloperGuide.md:491` |

## What Strata does not do

The rules:

1. Each absence is stated plainly on the page where a reader would look for it (the last column). The page gives one
   paragraph: what Strata does not have, how engines usually do it (with a source in Further reading), and what Strata
   offers instead where it offers something. It links `appendix/not-in-strata`.
2. A part with many absences has its own page (`animation/limits`, `indirect/gi-limits`); elsewhere a section of the
   named page holds them (`style.md` §7.2, item 6).
3. `appendix/not-in-strata` indexes every entry with a link to its page and gives the general technique. It does not
   repeat the page's paragraph. It also reads `Docs/Releases/0.8.0.md`, "Known issues" and "Not in this release".
4. Every entry carries its evidence at the pin: a file and its lines, or a search of the named folders that finds no
   match. A search is written as the exact command where a plain word would also match something else ("trail" in
   "trailing", "destruction" of entities); a match that is not the absent feature is named in the entry. No entry is
   stated from memory. In the tables below, `\|` inside a command stands for `|`. The writer runs the evidence again
   when writing the page, and the page's notes record it.
5. A page states what the engine's documents plan only by quoting them ("the Roadmap lists it under Later"), never with
   a date or a promise (`style.md` §13).
6. At each pin move (to `v0.8.0`, then `v0.8.1`) every entry's evidence runs again at the new pin; an entry whose
   evidence changed is corrected here before its page is re-read. An entry whose page is marked W8 or W8r is also a
   line of that page's `## Movable claims` (`plan/notes/<part>/<chapter>.md`, which `tools/pin.py report` lists,
   `pipelines.md` §10.2). The entries of the last table belong to W8 pages and are checked when those pages are written
   in phase B.
7. An entry whose subsystem has a `make` page names that page too.

The book never says Strata lacks something it has. Three facts that are easy to get wrong: games receive the text that
an input method committed (only composition is missing); the editor's text fields take composed text; and area lights
are not an absence, because 0.8.0 has rectangle lights (`light/area-lights`).

### Assets, core and platform

| Strata does not have | Evidence at `319075e3` | Page that says it |
| --- | --- | --- |
| OBJ and FBX import (models are glTF only) | `Strata/src/Strata/Asset/AssetImporters.cpp:160-178`; `Docs/Releases/0.8.0.md:555` | `make/assets`, `assets/models-gltf` |
| BC6H compression (HDR textures are stored as RGBA16F) | `Docs/Releases/0.8.0.md:543`; `Docs/Roadmap.md:1731` | `assets/texture-cooking` |
| EXR import (the texture importer reads `.png`, `.jpg`, `.jpeg`, `.tga`, `.bmp`, `.psd`, `.gif` and `.hdr`) | `Strata/src/Strata/Asset/TextureImporter.cpp:348`; `Docs/Roadmap.md:960` | `assets/texture-cooking` |
| Mesh streaming, per level of detail included (only textures load in parts) | `Strata/src/Strata/Renderer/RendererRegistration.cpp:93`, the only `RegisterPrefix`; `Docs/Roadmap.md:1708` | `draw/mip-streaming` |
| Virtual texturing and sparse residency | no `sparseBinding` in `Strata/src` | `draw/mip-streaming` |
| Shaders as assets and material graphs (shaders are compiled at build time and embedded) | `Strata/src/Strata/Asset/AssetTypes.h:14-31`, no shader type; `strata_add_shaders` in `Strata/CMakeLists.txt` | `make/materials`, `light/materials` |
| Mobile, console and web targets | `Strata/src/Strata/Core/PlatformDetection.h:5-22`, an `#error` for every other target | `core/platform` |
| Work stealing, fibers and a frame task graph | `Docs/Roadmap.md:1721-1722`; `git grep -ni fiber 319075e3 -- Strata/src` finds nothing | `core/jobs` |
| Engine plugins loaded at run time (modules are chosen at compile time with `ST_WITH_*`; only script modules load at run time) | the compile-time module table `Strata/src/Strata/Engine/BuiltinModules.cpp:62-76`; `git grep -lw DynamicLibrary 319075e3 -- Strata/src` finds it used only for script modules (`Strata/src/Strata/Scripting/ScriptModule.cpp`, `ScriptEngine.cpp`, the module's file name in `Strata/src/Strata/Project/Project.cpp`) and for the Vulkan loader (`Strata/src/Platform/Vulkan/VulkanLoader.cpp`), besides its own files | `core/layers-registries` |
| A build without scripting (physics, audio, animation and the window backend, GLFW, can be left out; a build without GLFW runs headless only) | `Docs/Releases/0.8.0.md:544`; `Docs/DeveloperGuide.md:280-284` | `core/layers-registries` |
| A crash handler or crash dumps for the engine's own crashes (only guarded script calls are contained; a crash in engine code ends the process, and the log keeps every warning and error but loses the info and trace lines still queued) | `git grep -n -e MiniDumpWriteDump -e SetUnhandledExceptionFilter -e set_terminate 319075e3 -- Strata/src StrataEditor/src StrataRuntime/src` finds nothing; `Strata/src/Platform/Posix/PosixCrashGuard.cpp:92-109` (outside a guarded call a signal goes where it would have gone without the guard); `Strata/src/Strata/Core/BackgroundLogSink.h:29-32` | `core/debugging` |
| Raising the streaming budgets of a game for a loading screen (no script function and no settings section sets the upload, finalization and staging budgets; the runtime's `--asset-budget-mb` sets only the GPU texture budget) | `Strata/src/Strata/Asset/AssetResidency.h:56-64` (raise all three for a loading screen); `git grep -ln -e UploadBytesPerFrame -e FinalizeMsPerFrame 319075e3 -- Strata/src StrataEditor/src StrataRuntime/src StrataScriptCore` finds only the asset manager's files and the editor's (`StrataEditor/src/Editor/EditorStreamingCommands.cpp`, `StrataEditor/src/Panels/StreamingPanel.cpp`); `StrataRuntime/src/RuntimeApplication.cpp:56, 94-95` | `assets/uploads`, `make/levels-saves` |

### Scenes, prefabs and editing

| Strata does not have | Evidence at `319075e3` | Page that says it |
| --- | --- | --- |
| Nested prefabs and prefab variants (a prefab made from linked entities stores no inner links) | `Strata/src/Strata/Scene/PrefabInstances.h:129-130` (`StripLinks`); `StrataEditor/src/Editor/EditorAssetCommands.cpp:1216, 1247` | `make/prefabs`, `world/prefabs` |
| A prefab edit mode (a prefab changes through an instance and Apply) | `Docs/Releases/0.8.0.md:521` | `make/prefabs` |
| Drawn (interpolated) poses for world-space game UI, editor gizmos and picking, reflection probes, fog, post-processing, the sky and the sun | `Docs/Roadmap.md:1715-1719` | `world/interpolation` |
| Editing several scenes at once (the editor edits one scene and a world's loaded cells; `scene.loadAdditive` works in play mode only) | `StrataEditor/src/Editor/EditorSceneCommands.cpp:458-460` | `editor/play-mode`, `make/levels-saves` |

### Rendering

| Strata does not have | Evidence at `319075e3` | Page that says it |
| --- | --- | --- |
| Particles, trails and decals | `git grep -niE "particle\|decal" 319075e3 -- Strata/src Strata/shaders` finds nothing; `git grep -niwE "trails?"` there finds only the anti-aliasing tooltips of `Strata/src/Strata/Renderer/RendererComponents.cpp:542, 553, 557`; `Docs/Roadmap.md:1707` | `gpu/frame-tour`, `make/look` |
| Terrain: a terrain system, sculpting and painting (the samples' terrains are meshes made by `Tools/GenerateIslandTerrain.py` and `Tools/GenerateShowcaseTerrain.py`) | "terrain" only in comments of `Strata/src`; `Docs/Roadmap.md:1711` | `make/large-worlds` |
| Water as an engine feature (water is a material with IOR 1.33) | `Strata/src/Strata/Renderer/Material.h:59` | `light/clearcoat-transmission` |
| MSAA and supersampling (a render scale above 1) | `Strata/src/Strata/Renderer/SceneRenderer.cpp:2901` refuses targets with `sampleCount != 1`; `Docs/Roadmap.md:955, 1687, 1689`; `Docs/Releases/0.8.0.md:551-552` | `image/spatial-aa`, `make/quality` |
| Rendering below native resolution, dynamic resolution, temporal upscalers: left out by decision (the first design decision) | `Docs/Roadmap.md:1659-1660` | `image/quality-settings` |
| HDR display output (HDR10, scRGB): the swap chain is sRGB only | `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp:1131-1136` | `image/encoding`, `make/quality` |
| Post-process volumes (the first active `PostProcessComponent` applies, with no shape and no blending) | `Strata/src/Strata/Renderer/SceneRenderer.cpp:1505-1513` | `image/why-post`, `make/look` |
| Non-photorealistic shading (toon, cel, ink outlines on objects): there is one physically based material model; the only outlines are the editor's selection outline and the outlines of text | `git grep -niE "toon\|cel[ -]shad\|hatching" 319075e3 -- Strata/src Strata/shaders` finds nothing; `Strata/shaders/Overlay/Outline.frag.slang:5` is the selection outline over the finished image; the other matches of "outline" in `Strata/shaders` are the selection outline's mask (`Scene/DepthPrepass.frag.slang`) and the outlines of glyphs (`GameUI/UIQuad.frag.slang`, `Include/SDFText.slang`, `Overlay/Text.frag.slang`) | `light/materials` |
| Hardware ray tracing | `git grep -niE "accelerationstructure\|RayQuery<\|ray_query\|raytracing\|TraceRay\|VK_KHR_ray" 319075e3 -- Strata/src Strata/shaders` finds nothing (the word `RayQuery` alone matches only physics, `struct RayQuery` of `Strata/src/Strata/Physics/PhysicsWorld.cpp` and its use in `CharacterControllers.cpp`) | `indirect/problem` |
| Mesh shaders and meshlets | no match in `Strata/src` or `Strata/shaders` | `draw/gpu-driven` |
| A render graph or frame graph (`SceneRenderer::RenderFrame` orders the passes by hand) | no `RenderGraph` or `FrameGraph` in `Strata/src`; `Strata/src/Strata/Renderer/SceneRenderer.cpp:3035` | `gpu/frame-tour` |
| Portals | no match in `Strata/src` | `draw/occlusion` |
| A second shadowed directional light; virtual shadow maps | `Docs/Roadmap.md:960-961, 1687` | `light/sun-shadows-1` |
| Lightmaps and baked global illumination (reflection probes are the only bake) | no `Lightmap` in `Strata/src` or `Strata/shaders` | `indirect/problem` |
| Reflection probes captured while the game runs | `Docs/Roadmap.md:953, 958`; `Docs/Releases/0.8.0.md:552` | `indirect/probes` |
| Reflections of and through transparent surfaces; glass behind glass | `Docs/Roadmap.md:949-952, 958-959` | `indirect/ssr`, `light/clearcoat-transmission` |
| Subsurface scattering, sheen, anisotropy, iridescence, specular maps and thickness maps | no `Subsurface` in `Strata/src` or `Strata/shaders`; `Docs/Roadmap.md:960` | `light/materials` |
| Order-independent transparency (glass shows only what was drawn before it) | no match in `Strata/src` or `Strata/shaders`; `Docs/Roadmap.md:949-950` | `light/clearcoat-transmission` |
| Volumetric fog, light shafts and fog volumes (height fog has no volume) | `Strata/src/Strata/Renderer/RendererComponents.h:163-166`; `Strata/shaders/Include/Scene.slang:13-14` (SRVs 34 and 36 reserved); `Docs/Roadmap.md:959` | `light/fog`, `make/look` |
| Billboards and impostors | no match in `Strata/src` or `Strata/shaders` | `draw/lod` |
| Complex-script text shaping, and fonts with CFF outlines | `Strata/src/Strata/Renderer/FontValidation.cpp:131-132`; render-core inventory, concept 30 | `gpu/text` |
| Compute skinning and dual-quaternion skinning (skinning runs per draw in the vertex shader) | `Docs/Roadmap.md:685`; no "dual quaternion" in `Strata/src` or `Strata/shaders` | `draw/skinned`, `animation/limits` |
| Debug drawing from scripts | no such function in `StrataScriptCore/Include/StrataScript/` | `gpu/debug-drawing`, `make/play-test-debug` |
| A second view: split-screen, picture-in-picture, a camera that renders into a texture for a mirror or a minimap (a game is drawn from one camera, the first active entity whose Camera is Primary) | `Strata/src/Strata/Scene/Scene.cpp:867-879`; `Strata/src/Strata/Runtime/GameRenderer.cpp:114-126`; `git grep -niE "split-?screen\|render-?to-?texture\|picture-in-picture\|RenderTexture" 319075e3 -- Strata/src StrataScriptCore Docs` finds nothing | `gpu/frame-tour`, `make/characters-cameras` |
| Clouds, stars and a moon (the atmosphere's haze is clear aerosol; the Overcast preset is a nearly uniform procedural sky) | `Strata/src/Strata/Renderer/SkyPresets.cpp:35-37`; `git grep -niwE "moon\|stars\|starfield\|clouds?" 319075e3 -- Strata/src Strata/shaders` finds only that comment, a tooltip's full-moon illuminance (`Strata/src/Strata/Renderer/RendererComponents.cpp:289`) and two comments on cloud placeholder files (`Strata/src/Platform/Windows/WindowsFileSecurity.h:28`, `Strata/src/Strata/Core/Platform.h:104`) | `light/sky`, `make/lighting` |
| Light cookies, IES profiles, light linking and lighting channels (every light lights every surface in its range) | `git grep -niE "cookie\|light ?channel\|light ?layer\|light ?mask\|light ?link" 319075e3 -- Strata/src Strata/shaders` finds only the DLL-directory cookie of `Strata/src/Platform/Windows/WindowsDynamicLibrary.cpp:21-36` and the socket notifier's cookie of `Strata/src/Platform/Windows/WindowsSocket.cpp`; `git grep -nw IES 319075e3 -- Strata/src Strata/shaders` finds nothing | `light/lights`, `make/lamps` |
| Material parameters per entity, such as a tint or a hit flash, and material changes from scripts (a loaded material never changes; a game gives `MeshRenderer.Material` another asset) | `Strata/src/Strata/Renderer/Material.h:87-90`; `git grep -ni material 319075e3 -- StrataScriptCore/Include/StrataScript/ScriptABI.h` finds nothing; `Samples/Tetris/Scripts/TetrisBoard.cpp:365` | `light/materials`, `make/materials` |
| A gizmo for reflection probes (the Scene view draws no box for a probe's Extents) | `Strata/src/Strata/Renderer/SceneGizmos.cpp:225-391` draws lights (rect lights included) and cameras; `git grep -n "\.Gizmo(" 319075e3 -- Strata/src StrataEditor/src` finds only the colliders and the character controller (`Strata/src/Strata/Physics/PhysicsComponents.cpp:143-184`) and the call that draws them (`Strata/src/Strata/Renderer/SceneGizmos.cpp:177`) | `make/reflections`, `indirect/probes` |
| Cube-map texture assets (skies and probe captures are equirectangular HDR textures, made into cubes at run time) | `Strata/src/Strata/Asset/AssetTypes.h:14-31`, no cube texture type (its `.cube` files are color lookups); `Docs/Roadmap.md:958` | `indirect/ibl`, `make/reflections` |

### Physics

| Strata does not have | Evidence at `319075e3` | Page that says it |
| --- | --- | --- |
| Joints, ragdolls and vehicles | no `b3Create*Joint` in `Strata/src`; `Docs/Roadmap.md:1733-1735` | `physics/why`, `make/physics` |
| Shape sweeps in the API (queries cast rays; a sweep is used only inside the character controller) | `Strata/src/Strata/Physics/PhysicsWorld.cpp:5413, 5435` (`b3World_CastRay`); `Strata/src/Strata/Physics/CharacterControllers.cpp:373` (`b3World_CastMover`) | `physics/queries` |
| Height-field and cylinder colliders (Box, Sphere, Capsule and Mesh only; the Hierarchy's Cylinder, Cone and Torus get a convex mesh collider of their own mesh, a hull of at most 64 vertices, and the torus's hull fills its hole) | `Strata/src/Strata/Physics/PhysicsComponents.h:44-68`; `StrataEditor/src/Panels/SceneHierarchyPanel.cpp:65-69, 83-88`; `Strata/src/Strata/Physics/PhysicsMeshShapes.h:48-49, 57` | `physics/bodies-colliders`, `make/physics` |
| Cloth, soft bodies, destruction, fluids and buoyancy | `git grep -niE "cloth\|soft ?bod\|fluid\|buoyan\|fractur\|destructible" 319075e3 -- Strata/src` finds nothing (the word "destruction" matches only the destruction of entities and objects) | `physics/why`, `make/physics` |
| Bodies farther than 1e5 m from the origin (they wait) | `Strata/src/Strata/Physics/PhysicsWorld.cpp:73` (`c_MaxBodyCoordinate`) | `physics/scale-streaming` |
| Triggers that see triangle-mesh colliders | `Docs/Releases/0.8.0.md:539`; `Docs/Roadmap.md:1736-1737` | `physics/contacts-triggers` |
| Bodies that move from one world cell to another (a moving body unloads with the cell it loaded with) | `Docs/Releases/0.8.0.md:528` | `worlds/physics-scripts`, `make/large-worlds` |
| Stay events, and the impulse or impact speed of a contact (contacts begin and end; a script that needs a hit's strength reads the bodies' velocities) | `Strata/src/Strata/Scene/SceneServices.h:41-45`; `StrataScriptCore/Include/StrataScript/ScriptABI.h:181-186`; `git grep -n enableHitEvents 319075e3 -- Strata/src` finds nothing; `Samples/PhysicsPlayground/Scripts/Impact.cpp:53-55` | `physics/contacts-triggers`, `make/physics`, `make/sound` |
| Rolling resistance and tangent velocity (conveyor belts) of box3d's surface material (a rolling ball slows only through its damping) | `git grep -n -e rollingResistance -e tangentVelocity 319075e3 -- Strata/src` finds nothing; `Strata/vendor/box3d/include/box3d/types.h:417-431` | `physics/bodies-colliders`, `make/physics` |

### Animation

| Strata does not have | Evidence at `319075e3` | Page that says it |
| --- | --- | --- |
| Blend trees, animation layers, IK, morph targets, clip compression | `git grep -nilE "blend ?tree\|inverse kinematics\|morph\|compress" 319075e3 -- Strata/src/Strata/Animation` finds nothing; `Strata/src/Strata/Asset/GltfImporter.cpp:1031` (weight channels skipped); `Docs/Roadmap.md:1666-1669` | `animation/limits`, `make/animation` |
| Additive clips, sync markers, float curves, inertialization, motion matching | `git grep -nilE "additive\|sync ?marker\|float curve\|inertiali\|motion ?match" 319075e3 -- Strata/src/Strata/Animation` finds nothing; `Docs/Roadmap.md:1664-1668` | `animation/limits` |
| Retargeting beyond matching joint names (clips bind to skeletons by name) | `Strata/src/Strata/Animation/AnimationClip.h:38` | `animation/limits` |
| A skeleton overlay in the viewport | `git grep -nilE "joint" 319075e3 -- StrataEditor/src Strata/src/Strata/Renderer Strata/shaders` finds the Asset tab's joint and channel views, the animation commands, the editor's bounds code, the `AttachToJoint` entity icon and the skinning code, and other words (`JoinTypeNames` in `StrataEditor/src/Editor/EditorUICommands.cpp`, "disjoint" in `Strata/src/Strata/Renderer/GlobalIlluminationLayout.h` and `.cpp`); nothing draws joints in a view | `animation/limits` |

### Audio

| Strata does not have | Evidence at `319075e3` | Page that says it |
| --- | --- | --- |
| Buses, effects, reverb and HRTF (a voice sets only its own output volume) | no `ma_sound_group`, reverb, HRTF or filter node in `Strata/src/Strata/Audio`; `Strata/src/Strata/Audio/AudioVoice.cpp:308` | `audio/engine`, `make/sound` |
| Occlusion and reverb zones | no match in `Strata/src/Strata/Audio` | `audio/spatial`, `make/sound` |
| Virtual voices and voice priorities | no match in `Strata/src/Strata/Audio` | `audio/clips-voices-sources`, `make/sound` |
| Streaming from disk or packs (a streamed clip decodes encoded bytes held in memory) | `Strata/src/Strata/Audio/AudioClip.h:45-52`; `Docs/Roadmap.md:1729` | `audio/clips-voices-sources`, `make/sound` |
| A choice of attenuation model per component (components always use Inverse) | `Strata/src/Strata/Audio/AudioComponents.h:11-22`, no model field | `audio/spatial` |
| Listeners per world | `Docs/Roadmap.md:1724` | `audio/scene-system`, `make/sound` |
| Music systems and ducking | no match in `Strata/src/Strata/Audio` | `make/sound` |

### Input

| Strata does not have | Evidence at `319075e3` | Page that says it |
| --- | --- | --- |
| Touch input | no touch code in `Strata/src/Strata/Input` or `Strata/src/Platform/GLFW` | `input/how-input-works`, `make/input` |
| Input-method composition in game UI: committed text arrives, but the text being composed and the candidate window are not shown. The editor's ImGui text fields take composed text and, on Windows, place the candidate list | `Strata/src/Strata/Input/Input.h:148`; GLFW 3.4 has no preedit API (`Strata/vendor/glfw/include/GLFW/glfw3.h`); `Strata/src/Strata/ImGui/ImGuiPlatform.h:25-26` | `ui/text`, `editor-ui/imgui-backends` |
| Action modifiers, chords, processors and interactions; mouse motion and scroll as action sources (they stay on the raw API) | `Docs/DeveloperGuide.md:1478-1479`; `Docs/Releases/0.8.0.md:496-497, 553`; `Strata/src/Strata/Input/InputActionSet.cpp:102` refuses every binding but `Key/`, `Mouse/<button>`, `Gamepad/`, `1D:` and `2D:` | `input/actions`, `make/input` |
| Force feedback | no rumble, vibration or haptic code in `Strata/src` or `StrataScriptCore` | `input/gamepads`, `make/input` |
| Devices assigned to players for local multiplayer (gamepad bindings read every gamepad) | `Docs/DeveloperGuide.md:1474`; `Docs/Releases/0.8.0.md:553`; `Docs/Roadmap.md:1724` | `input/gamepads`, `make/input` |
| Key names that follow the player's keyboard layout (a game shows a key's name by its US position; only the editor's shortcuts follow the layout) | `Docs/Releases/0.8.0.md:496-498`; `git grep -n GetLayoutKey 319075e3 -- Strata/src StrataScriptCore` finds only the window's own code and the ImGui platform's (`Strata/src/Strata/ImGui/ImGuiPlatform.cpp:180` and a comment of its header) | `input/rebinding`, `make/menus` |
| Controllers missing from GLFW's gamepad database, more than four gamepads, and gamepad mappings that a game adds (an unmapped controller reads as not connected and keeps its slot) | `Strata/src/Platform/GLFW/GLFWWindow.cpp:416-442`; `Strata/src/Strata/Input/GamepadCodes.h:42` (`c_MaxGamepads = 4`); `git grep -n glfwUpdateGamepadMappings 319075e3 -- Strata/src StrataEditor/src StrataRuntime/src` finds nothing | `input/gamepads`, `make/input` |

### Scripting

| Strata does not have | Evidence at `319075e3` | Page that says it |
| --- | --- | --- |
| Visual scripting (game logic is C++ script classes) | no node or graph scripting in `Strata/src` or `StrataEditor/src`; `AGENTS.md`, "Scripting" | `start/welcome`, `scripting/why-scripts` |
| Script languages other than C++ | no `lua_`, `mono_` or CoreCLR code in the engine | `scripting/why-scripts` |
| Calls into scripts from other threads | `StrataScriptCore/Include/StrataScript/ScriptABI.h:25-26` | `scripting/abi-sdk` |
| Script modules linked statically | `Docs/Roadmap.md:1726` | `scripting/loading` |
| Script field types beyond the ten (no `std::vector`, array, enum, `double`, `int64_t` or struct: such a field fails to compile with "Unsupported script field type") | `StrataScriptCore/Include/StrataScript/Script.h:133-137, 785-786` | `make/script-fields` |
| Callbacks when an entity is activated or deactivated (no `OnEnable` or `OnDisable`; `OnCreate` is the only start) | `StrataScriptCore/Include/StrataScript/Script.h:83-97`, the 15 callbacks | `make/script-loop` |
| Coroutines (nothing waits inside a callback; timers and state machines do that work) | `git grep -n -i -e coroutine -e co_await 319075e3 -- Strata/src StrataScriptCore` finds nothing | `make/timers-events` |
| Reading the game's title or version from a script | `Docs/Releases/0.8.0.md:499`; `git grep -niE "title\|gameinfo" 319075e3 -- StrataScriptCore` finds only the graphics options' `Title` (`StrataScriptCore/Include/StrataScript/Graphics.h:46, 125`; `ScriptABI.h:289, 299`) | `worlds/game-identity`, `make/export` |

### Game UI

| Strata does not have | Evidence at `319075e3` | Page that says it |
| --- | --- | --- |
| Scroll views, drop-downs, rich text and multi-line input fields (a mask clips a scrolling list; input fields are one line) | `Strata/src/Strata/GameUI/GameUIComponents.cpp:211-397`; `Strata/src/Strata/GameUI/GameUIComponents.h:255-260, 272-273` | `ui/what-game-ui-does`, `make/menus` |
| Localization and right-to-left text | `Docs/Releases/0.8.0.md:556`; `Docs/Roadmap.md:1730`; no localization code in `Strata/src` | `ui/text`, `make/menus` |
| Lit world-space UI; game clicks on world-space canvases that respect geometry in front | `Docs/Releases/0.8.0.md:530-531` | `ui/drawing`, `ui/input` |

### Editor, export and automation

| Strata does not have | Evidence at `319075e3` | Page that says it |
| --- | --- | --- |
| Panels torn out into windows of their own (one main viewport) | `Strata/src/Strata/ImGui/ImGuiPlatform.h:21`; `Docs/Roadmap.md:1732` | `editor-ui/shell` |
| Editor extensions written by a game project (only the editor registers panels) | `StrataEditor/src/EditorLayer.cpp:506` | `editor-ui/shell` |
| A place in the editor's UI to type and run any command (the Activity panel re-runs only commands the journal recorded) | `EditorLayer::DrawMenuBar`, `StrataEditor/src/EditorLayer.cpp:1734-1912`; `StrataEditor/src/Panels/ActivityPanel.cpp:372-397` | `make/commands` |
| Creating an animation controller from the UI (only the command `animation.createController`) | `StrataEditor/src/Editor/EditorAnimationCommands.cpp:153`; `StrataEditor/src/Panels/ContentBrowserPanel.cpp:566-580` | `make/animation` |
| Setting a player's graphics options by command (only `graphics.resetPlayerOptions`) | `StrataEditor/src/Editor/EditorGraphicsCommands.cpp:16` | `make/quality` |
| Automating an exported game (command scripts, simulated input and expectations run in the editor only) | `Docs/Roadmap.md:1714` | `make/automated-playtests`, `worlds/runtime` |
| Exports for another platform, macOS app bundles, signed exports, crash reports in shipped games (the export copies the runtime next to the editor) | `Docs/Releases/0.8.0.md:552-553`; `StrataEditor/src/Editor/GameExport.h:30`; `Docs/Roadmap.md:1701-1702` | `make/export`, `worlds/export` |
| In-game consoles and console variables | no match in `Strata/src`, `StrataRuntime/src` or `StrataScriptCore` | `make/play-test-debug` |
| MCP resources, prompts and logging, a transport other than the standard streams, and cancellation (the MCP server offers tools only, and nothing cancels a command once it is sent: the editor finishes it, as it does after the CLI's exit code 4) | `StrataCLI/src/CLI/McpServer.cpp:367-372` (every notification but `notifications/initialized` is dropped), `:379-397`, `:420` (the `tools` capability alone); `StrataCLI/src/CLI/CliApplication.cpp:372-373` (standard input and output); `StrataCLI/src/CLI/CliApplication.h:24` (exit code 4: the command may still be running in the editor); `git grep -n -i "notifications/cancel" 319075e3 -- StrataCLI Strata/src/Strata/Network` finds nothing | `automation/mcp`, `make/with-an-agent` |
| Rebinding the editor's shortcuts (the chords are written in the code) | `StrataEditor/src/EditorLayer.cpp:1235-1269`; `StrataEditor/src/Editor/EditorPreferences.cpp:69-74` (three preference sections: the external editor, the interface and the frame rate); `Docs/Roadmap.md:1004` | `editor-ui/game-view`, `make/editor-tour` |
| Editor themes other than the one it has | `StrataEditor/src/Editor/EditorPreferences.cpp:69-74`; `Docs/Roadmap.md:1004` | `editor-ui/design-system` |
| A tool that writes patch packs (the export writes none; a patch is a pack written from code and named in the manifest's `PatchPacks` by hand) | `git grep -n PatchPacks 319075e3 -- StrataEditor StrataCLI Tools` finds nothing; `Strata/src/Strata/Project/GameManifest.h:26, 53` | `assets/packs-export`, `make/export` |
| Worlds beyond 20 km from the origin, HLOD (distant cells are not drawn), origin rebasing | `Docs/Releases/0.8.0.md:527, 554-555`; `Docs/Roadmap.md:1710, 1723` | `worlds/why-streaming`, `make/large-worlds` |

### Gameplay

| Strata does not have | Evidence at `319075e3` | Page that says it |
| --- | --- | --- |
| Gameplay networking (network code exists for editor automation only, in the Tooling layer `Network`, which games never link) | `StrataTests/Architecture/Layers.json:99-102` | `appendix/networking`, `automation/json-rpc` |
| Game AI: steering, pathfinding, navigation meshes, behaviour trees (left to scripts) | no match in `Strata/src` or `StrataScriptCore` | `appendix/game-ai`, `make/patterns` |
| A sequencer or timeline for cutscenes (camera moves and cuts are scripted, as the Showcase's camera tour is) | `Samples/Showcase/Scripts/TourPath.h:3-6`; `git grep -niE "sequencer\|cutscene\|cinematic" 319075e3 -- Strata/src StrataEditor/src StrataScriptCore Docs/Roadmap.md` finds only the editor's input sequences (`IsInputSequenceRunning`, `DescribeSequenceResult`) | `make/characters-cameras` |

### Building, testing and the GPU

| Strata does not have | Evidence at `319075e3` | Page that says it |
| --- | --- | --- |
| Asynchronous compute and wave (subgroup) operations (compute runs on the graphics queue, although the device fetches a compute queue) | `git grep -n "CommandQueue::Compute" 319075e3 -- Strata/src` and `git grep -nE "Wave[A-Z][a-z]*\(" 319075e3 -- Strata/shaders` find nothing; the compute queue is fetched at `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp:939-940` | `gpu/compute` |
| Debug information in shaders (slangc runs without `-g`, so a frame capture shows shaders without their source) | `CMake/StrataShaders.cmake:77-79`; `Docs/Roadmap.md:1101` | `gpu/debugging` |
| A choice of GPU (no program sets the device's adapter index, so the device's score picks: a discrete GPU first, then the most memory; the log names each GPU it skips, with the reason) | `Strata/src/Strata/Renderer/GraphicsDevice.h:29`; `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp:632, 637-640, 744-750`; `git grep -n AdapterIndex 319075e3 -- Strata/src StrataEditor/src StrataRuntime/src StrataTests/src` finds only these two files | `gpu/vulkan-nvrhi` |
| Command lists recorded on several threads (the main thread records and submits every command list; the renderer's jobs do CPU work only) | `Docs/Architecture.md:1383-1384`; `git grep -n -e ParallelFor -e "JobSystem::Submit" 319075e3 -- Strata/src/Strata/Renderer` finds only staging copies (`GPUUploadQueue.cpp:531`), poses (`RenderScene.cpp:1428`), extraction (`SceneRendererExtraction.cpp:117`) and caster queries (`SceneRendererExtraction.cpp:538`, `SceneRendererLocalShadows.cpp:1187`) | `gpu/vulkan-nvrhi` |
| A check at startup for the processor's AVX2 (the release builds compile every engine object for AVX2, so an older processor stops at an illegal instruction without a message) | `CMake/StrataCompilerOptions.cmake:30`, `:50-51`, `:61-62`; the only processor check in `Strata/src` is `Strata/src/Strata/Core/Hash.cpp:109-119` (SSE 4.2, for CRC32) | `engineering/flags-portability`, `make/export` |
| Unity builds (every source compiles as its own translation unit) | `git grep -niE "UNITY_BUILD" 319075e3 -- CMakeLists.txt CMake Strata/CMakeLists.txt StrataTests/CMakeLists.txt StrataEditor/CMakeLists.txt` finds nothing | `engineering/flags-portability` |
| A package manager such as vcpkg or Conan (dependencies are pinned submodules wrapped by one CMake file) | `git ls-tree -r --name-only 319075e3 \| grep -iE "vcpkg\|conanfile"` finds nothing; `Strata/vendor/CMakeLists.txt:3-7` | `engineering/third-party` |
| Measured line coverage (the feature test's coverage by construction stands in its place) | `git grep -niE "\-\-coverage\|llvm-cov\|gcov\|OpenCppCoverage\|fprofile-instr" 319075e3 -- CMakeLists.txt CMake StrataTests/CMakeLists.txt .github Tools` finds nothing | `engineering/testing` |
| A coverage-guided fuzzer such as libFuzzer or AFL (the sweeps test fixed, seeded offsets) | `git grep -niE "libfuzzer\|LLVMFuzzerTestOneInput\|fsanitize=fuzzer" 319075e3 -- Strata/src StrataTests CMake CMakeLists.txt .github` finds nothing | `engineering/test-program` |
| Sanitizer builds (AddressSanitizer, UndefinedBehaviorSanitizer) | `git grep -niE "fsanitize" 319075e3 -- CMakeLists.txt CMake StrataTests/CMakeLists.txt .github CMakePresets.json` finds nothing; `.github/scripts/annotate_failures.py:40` only recognizes the word "Sanitizer" in a log | `engineering/ci` |
| A format check (neither CI nor a test runs clang-format, so `.clang-format` and `.editorconfig` act only in editors that read them) | `git grep -n -i "clang-format" 319075e3 -- . ":!Strata/vendor" ":!Docs/Plans"` finds only `AGENTS.md:144` | `engineering/ci` |
| Signed or notarized release archives, and installers (CPack writes a ZIP on Windows and a TGZ elsewhere) | `git grep -niE "signtool\|codesign\|notari" 319075e3 -- .github CMake CMakeLists.txt` finds nothing; `CMake/StrataPackaging.cmake:95-99` | `engineering/releasing` |

### Checked when the W8 page is written (phase B, at `v0.8.0`)

| Strata does not have (at the pin) | Evidence at `319075e3` | Page that says it |
| --- | --- | --- |
| Disk-shaped area lights (0.8.0 has rectangle lights; the release notes plan disk lights for a later wave) | three light record types, point, spot and rect (`Strata/src/Strata/Renderer/SceneRenderData.h:34-37`); `Docs/Releases/0.8.0.md:549` (disk lights in a later wave) | `light/area-lights` |
| Diffuse light and soft shadows from the size of point and spot lights (a light's size widens only its highlight) | `Docs/Roadmap.md:957-958, 1677`; `AGENTS.md:411-412` | `light/area-lights`, `light/local-shadows` |
| Global illumination from local lights and from moving or skinned objects; specular light from global illumination (the field changes only the diffuse indirect light), the open share in specular occlusion, an Ultra level, textured albedo per voxel, hardware ray queries for global illumination, nested probe-field levels, and denser probes near surfaces | `Docs/Plans/Wave8/specs/radiance-cascades-world.md:896-917` ("Below the cut", items 1 to 6 and 8; item 7, probe relocation, is at the pin: `Docs/DeveloperGuide.md:5608`); `Docs/DeveloperGuide.md:5395-5396, 5768, 5968`; render-indirect inventory §1.8 | `indirect/gi-limits`, `make/gi` |

## Running examples

**Coin Run (track G and B, block A of `make`).** A rolling ball collects coins on the Basic 3D template. Block A
builds it step by step. Each tutorial of block A starts from the checkpoint of the tutorial before it (its tutorial
file starts from that tutorial, `pipelines.md` §6) and ends with a checkpoint of Coin Run. The how-to and concept pages
of block A take Coin Run as their example where they show one. A how-to of block A that changes Coin Run
(`make/assets`, `make/scripting-scene`, `make/play-test-debug`) has a tutorial file too, and its `## Result` ends with
the download of its end state (`style.md` §7.5). The stages the outline names:

| Page | What happens to Coin Run |
| --- | --- |
| `make/editor-tour` | The project is created from the Basic 3D template. |
| `make/scenes-entities` | The level: the ground, the walls, the ball and a first coin as entities. |
| `make/assets` | The coin's model is brought in. |
| `make/materials` | The gold coin and the ball's material. |
| `make/prefabs` | The coin becomes a prefab. |
| `make/lighting` | The level is lit for play. |
| `make/first-script` | The coins spin. |
| `basics/programming-1` | The spin speed in a variable; an `if` spins a gold coin faster (a practice item). |
| `basics/programming-2` | A function and a loop line coins up (a practice item; the lines that request and instantiate the prefab are given). |
| `basics/programming-3` | A `Coin` class with a field, and a `BobbingCoin` derived from it (a practice item). |
| `basics/debugging` | A planted bug in the spin is found with breakpoints (a practice item). |
| `make/script-loop` | No stage: the coins' bob in `OnUpdate` is the page's example, and `make/scripting-scene` builds it. |
| `make/scripting-scene` | The coins bob (the page's first step; its tutorial file starts from `make/first-script`'s end); a script places the coins; a collected coin is hidden or destroyed. |
| `make/input` | The Move action. |
| `make/physics` | The ball rolls by a force in `OnFixedUpdate`; the coins are triggers. |
| `make/sound` | The coin sound. |
| `make/hud` | The coin count and the timer. |
| `make/play-test-debug` | A Coin Run script is debugged with the debugger that `basics/debugging` attached. |
| `make/export` | Coin Run is exported and run. |
| `make/project-coin-run` | Win, lose, restart (`Game::ReloadScene` in one step), polish; the reader owns the exported game and may ship it with the book's code in it, by the permission that `appendix/credits` teaches (`critique/rulings-6.md`, R21). |

The four programming primers are also read on track E, which has no Coin Run: their Coin Run items start from the
download of `make/first-script`'s end checkpoint, so any reader can do them. The primers after `basics/debugging` end
with an optional practice item on Coin Run for track B. Blocks B and C do not continue Coin Run. The pages of block B
share the obstacle course that `make/characters-cameras` builds: `make/animation`, `make/menus` and `make/levels-saves`
start from a downloadable checkpoint of it, named in their briefs, and a page of block B that does not continue the
course has its own small example. Each page of block B has its own downloadable start and needs nothing that it does
not teach. Block C has its projects, Tetris (`Samples/Tetris`) and a third-person platformer (`Samples/ThirdPerson`).

**WindZone (track E, from `world/tutorial-component` to the capstone).** A component that pushes bodies with wind.
Every stage is an engine patch; the chain of patches starts at `world/tutorial-component` (`pipelines.md` §6.6).

| Page | What happens to the WindZone |
| --- | --- |
| `world/tutorial-component` | The component and its system are created; a serialization round trip and the feature test's minimum. |
| `gpu/debug-drawing` | Its exercise gives the WindZone its gizmo, a sphere of its radius; the exercise's solution is a patch of the chain. |
| `scripting/tutorial-host-function` | A scene service through which the host function reaches the zones (the Scripting layer may not include Physics, `StrataTests/Architecture/Layers.json:76-78`); the host function `Wind::GetStrength`, and a callback appended to `StrataScriptClassDesc`. |
| `editor/tutorial-command` | The `wind.*` commands, and the `wind.` prefix in the MCP server's toolsets (`c_PrefixToolsets`, `StrataCLI/src/CLI/McpToolsets.cpp:43-54`), so that no later page starts from a failing test. |
| `capstone/plan` | The WindZone designed as a feature: its layers, its registries and the rules that apply. The design is a spec in the form of the engine's own, which the page's patch adds under `Docs/Plans`. |
| `capstone/build` | Forces on bodies (a Directional zone pushes along its entity's local -Z, Strata's forward), the arrow that the gizmo of `gpu/debug-drawing` gains for a Directional zone, an inactive reason in the inspector, the script API and the command, in one change. |
| `capstone/land` | Unit tests, the feature test, a perf budget, the review checklist and a `ci/<name>` branch. |

**Examples of a part.** A part may have its own small running example, named in its brief: for example the
Third-Person sample's robot in `animation` (`animation/problem`) and the Cornell box of the path tracer sketch in
`indirect` (`indirect/problem`).

## Parts

The order of the parts is the book's order: track E and the site's sidebar follow it. The counts come from
`plan/check_outline.py --counts --words`; when the outline changes, this table is regenerated from that output.

| # | Part | Slug | Tracks | Pages | Words (estimate) | Index and review pages |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | Start here | `start` | G, B, E (`start/coming-from`: G, E) | 6 | 20,500 | no |
| 1 | Making games | `make` | G, B (block A); G only (blocks B and C) | 42 (A 18, B 21, C 3) | 176,000 | yes |
| 2 | Foundations | `basics` | B, E, G (G only for `basics/programming-1` to `-3` and `basics/debugging`; `basics/tools` and `basics/math-vectors` are side steps of G) | 30 | 140,000 | yes |
| 3 | Engine architecture | `core` | E | 16 | 74,000 | yes |
| 4 | Scenes and the ECS | `world` | E | 11 | 59,000 | yes |
| 5 | The GPU and the renderer's core | `gpu` | E | 15 | 73,000 | yes |
| 6 | Assets | `assets` | E | 13 | 70,000 | yes |
| 7 | Drawing a scene | `draw` | E | 13 | 54,000 | yes |
| 8 | Light and materials | `light` | E | 18 | 88,000 | yes |
| 9 | The image | `image` | E | 13 | 62,000 | yes |
| 10 | Indirect light | `indirect` | E | 9 | 48,000 | yes |
| 11 | Physics | `physics` | E | 12 | 46,500 | yes |
| 12 | Animation | `animation` | E | 13 | 44,000 | yes |
| 13 | Audio | `audio` | E | 6 | 22,500 | no |
| 14 | Input | `input` | E | 7 | 28,000 | no |
| 15 | Scripting | `scripting` | E | 10 | 46,000 | yes |
| 16 | Game UI | `ui` | E | 6 | 30,000 | no |
| 17 | Large worlds and shipping | `worlds` | E | 7 | 30,000 | no |
| 18 | The editor's core | `editor` | E | 19 | 80,000 | yes |
| 19 | The editor's interface | `editor-ui` | E | 17 | 90,000 | yes |
| 20 | Automation and AI agents | `automation` | E | 6 | 34,000 | no |
| 21 | Building, testing and releasing the engine | `engineering` | E | 14 | 60,000 | yes |
| 22 | Capstone: one feature through every layer | `capstone` | E | 3 | 15,000 | no |
| 23 | Reference | `reference` | - | 22 | 95,500 | yes |
| 24 | Appendices | `appendix` | - | 7 | 25,500 | no |

**335 pages** in 25 parts, plus 34 generated index and review pages in 17 parts. About 1,511,500 words: track G reads
about 216,500, track B 225,500 and track E 1,214,500. Kinds: P 30, C 45, I 176, T 34, H 24, R 26.

**Pages marked for wave 8** (`outline-1.md`, "Marks"):

- **W8**, written in phase B: `make/lamps`, `make/gi`, `light/area-lights`, `light/local-shadows`,
  `indirect/gi-voxels`, `indirect/gi-cascades`, `indirect/gi-limits`.
- **W8r**, written in phase A with one section revised in phase B: `make/look`, `make/quality`, `make/performance`,
  `gpu/frame-tour`, `light/lights`, `light/many-lights`, `image/quality-settings`.

A page's URL is `<base>/<id>/` at the book's origin, with the base `/strata-engine-docs` and the origin
`https://pdm.pw` written in `site.json` (`DOCS_BASE` and `DOCS_SITE` override them for one build, `site.md`):
`core/time` is `https://pdm.pw/strata-engine-docs/core/time/`. A URL never changes once published, except when the
whole book moves to another address (`critique/rulings-6.md`, R24). A move changes `site.json`; a release is tagged
and deployed at the new place, and the old host answers every path under the old prefix with a 301 to the same path
at the new address. Each page keeps its path `<id>/` under the base; canonical links and the sitemap follow from the
rebuild.
