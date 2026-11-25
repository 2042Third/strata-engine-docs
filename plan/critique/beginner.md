# Critique of the plan: the complete beginner

Critic key: `beginner`. Lens: a reader who has never programmed, has no idea how an engine or a game is made, and
reads English as a second language. Read: all nine plan files, `research/curricula.md` in full, and the inventories
`gamedev`, `foundation`, `scene-ecs`, `build-test`, `assets`, `physics`, `audio-input`, `render-core` and `scripting`
(the sections named below), plus engine files at `822a7a46` (named where used). Line numbers are those of each plan
file.

## Verdict

As planned, the complete beginner cannot start from zero. The plan names this reader (book.md 19: "Nothing assumed")
and promises that a prerequisite is always a page of the book (book.md 22-23). But the outline has no page that
teaches programming, no first program, no tools, and no school mathematics below vectors. The beginner's track (B)
exists only as a sentence. It has no value in the front matter, no reading order and no reviewer persona. So the
novice review, the one stage that could find these gaps, reviews the primers as a reader who "knows some programming".
Fix these first. Add a programming-from-zero sequence and a first-program tutorial to `basics`. Then make track B and
its persona real, so that the tools and the novice review can check the promise.

## 1. What is assumed but never taught

Each item below is used by pages of the outline. No page of the outline is its home. "Partial" means that a page
touches it, but the page is the wrong kind or size, or comes later than the pages that use it.

| Knowledge | Used by (examples) | Taught where |
| --- | --- | --- |
| Programming itself: values, variables, types, expressions, `if`, loops, functions, parameters, return values | `make/first-script`, every `basics/*` exercise, every internals page | **Nowhere.** `basics/cpp` is "The C++ you need to *read* Strata" (outline-1 72). `make/cpp-for-scripts` is one L page of kind *concept* (outline-1 38) |
| A first program: write a source file, compile it, run it, see output, read one compile error | style.md 23 ("a tiny program whose output surprises"), style.md 52-53 (an exercise that "changes or runs real code"), every sketch | **Nowhere.** `basics/build` is a concept page (outline-1 73) |
| The terminal: what it is, a working folder, running a program with arguments | `start/install` (macOS `xattr`, Linux `apt`; PackageReadme "First start"), `make/automated-playtests` (StrataCLI, `claude mcp add`), `make/export` (`--headless`), all of `engineering` | **Nowhere** |
| The operating system: files, folders, paths, the user data folder, environment variables, executables and libraries, processes | `start/install` (logs under `%LOCALAPPDATA%`), `core/platform`, `scripting/shared-libraries` | **Nowhere.** `basics/computer` covers CPU, memory, stack, heap and caches only (outline-1 71) |
| git: clone, submodules, branch, diff, commit | `start/first-engine-change`, `engineering/building` (AGENTS.md "Building": `git submodule update`), `engineering/contributing`; new projects get a `.gitignore` (gamedev 1.2, "Project creation") | **Nowhere** (curricula 1.1: "[gap]") |
| A code editor or IDE: open the scripts, IntelliSense | `make/first-script` (the file "opens in your code editor", Manual/Scripting) | Partial: `make/script-builds` (H, after first-script) |
| Reading compiler and linker errors | `make/first-script` (Problems panel), `basics/build` | Partial: `basics/build` (concept, track E/B only) |
| The debugger: breakpoints, stepping, the call stack, attaching to a process | `make/play-test-debug` (gamedev 1.9 "Debugger attach"), the "trace it yourself" exercises (curricula 3.2 item 10) | **Nowhere** (curricula 1.18: "[gap]"). `make/play-test-debug` is a how-to |
| School algebra: equations, functions and graphs, powers, roots, logarithms, exponentials, summation (Σ) | `basics/math-vectors`; its source inventory says "Prerequisites: high-school algebra" (foundation §8 ch. 12); EV stops (`light/units-exposure`, `make/look`); decibels (`audio/sound-in-a-computer`); `1 - exp(-k dt)` smoothing (gamedev concept 17) | **Nowhere** |
| Trigonometry: angles, degrees and radians, sin, cos, tan, atan2 | `make/first-script` (`glm::radians`), `make/characters-cameras` (27 lines of `std::exp/atan2/sin/cos/remainder/sqrt` in `Samples/*/Scripts`), `Playground.cpp` 183-207 "trigonometry (tan)" (gamedev code 24), `basics/math-light` (spherical coordinates) | **Nowhere** |
| Floating point: representation, precision, epsilon, precision far from the origin | `physics/*` (tolerances), `worlds/*` (20 km limit), `draw/mirrors-camera-relative`, `core/time` (double vs float time, foundation concept 4) | **Nowhere** (curricula 1.1, 1.2: "[gap]") |
| Interpolation: lerp, smoothstep, easing, exponential smoothing | `animation/clips`, `animation/blending`, `make/characters-cameras`, BC block decoding in `assets/textures` | **Nowhere** as a home |
| Change over time: derivative as a rate, integral as accumulation, explicit and semi-implicit Euler | `physics/how-simulation-works`, `core/time`, `basics/math-light` (integrals) | **Nowhere** (curricula 1.2) |
| Newtonian mechanics: force, mass, acceleration, momentum, impulse, torque, inertia | `physics/how-simulation-works`; the physics inventory lists only "vectors, quaternions" as prerequisites (physics §8 ch. 4) | **Nowhere** |
| Signals: sampling, aliasing, Nyquist, filtering | `assets/textures` (mips), `image/spatial-aa`, `image/taa`, `light/shadow-basics` (PCF), `audio/sound-in-a-computer` (Nyquist, audio-input A1) | **Nowhere.** Curricula 1.2: "taught five times, badly, or not at all" |
| Probability and random numbers: distributions, expected value, seeds, PRNGs | `basics/math-light` (Monte Carlo), `indirect/ao`, SDK `Random` (`make/recipes`), seeds (gamedev glossary "Seed") | Partial: a quarter of `basics/math-light` (L, four topics) |
| Data structures and their cost: arrays, linked lists, hash maps, queues, trees, graphs, big-O | `world/ecs` (sparse sets, O(1), linked lists, hash buckets: scene-ecs code 4, 5, 13), `core/engine-modules` (Kahn's sort, foundation concept 10), `core/jobs` (queues), `draw/bounds-culling` (spatial index), physics broad phase (BVH), `assets/references` (graphs, closures) | **Nowhere** |
| JSON | the command tab of every tutorial from `start/first-game` (style.md 65), `make/automated-playtests`, `automation/*` | **Nowhere** as a home (not named in `basics/bytes`) |
| What a pixel, a frame, a frame rate and a GPU are (for the game maker) | `make/materials`, `make/look` (quality presets cost "GPU ms"), `start/install` ("Vulkan 1.2 GPU") | Partial: `gpu/how-a-gpu-frame-works` (part 6, track E) |
| How to design a game: core loop, scope, prototyping, game feel, playtesting | the owner's "no idea how to implement a … game"; curricula 1.13 marks it "[gap]" | **Nowhere.** No inventory covers it: there are no matches for "game design", "core loop" or "game feel" in `inventory/` |

## 2. The primers: are they the right ones, big enough, in order? Is a first program taught?

**A first program is taught nowhere.** On track G the first code is `make/first-script`, page 11 of part `make`
(outline-1 39). The editor's build compiles it, so the reader never sees a compiler, `main` or console output. That is
acceptable for G. But it needs the C++ toolchain from `start/install`. On tracks B and E there is no hello-world at
all: `basics/cpp` (XL) comes before `basics/build` (outline-1 72-73), and neither is a tutorial. Every exercise of
`basics` that should "change or run real code" (style.md 52-53) has nowhere to run.

**Missing primers.** Programming from zero, school algebra and trigonometry, change and motion, sampling, floating
point, data structures, and tools (terminal, OS, git, editor, debugger). See section 1.

**Too small.** `basics/cpp` is one XL page (8,000+ words). It cannot hold both programming and the C++ the engine
uses. In `Strata/src`, `StrataEditor/src` and `StrataScriptCore` there are 2,245 lines with `std::optional`, 1,702
with `std::move`, 1,490 with `std::string_view`, 731 with `std::span`, about 635 with lambda captures, 265 with
`memory_order`, 257 with `template <`, 56 with `if constexpr` and 48 with `requires`. At about 400 words for each
feature with one worked example, twenty features fill 8,000 words. That leaves nothing for variables, loops, functions,
classes or pointers. `make/cpp-for-scripts` (L, about 5,000 words) has the same problem for the game maker. The sample
scripts the projects use (5,344 lines in `Samples/*/Scripts`) use `std::optional` (25 lines), `std::array` (20),
`static_cast` (87), `constexpr` (45), references and pointers. And the gamedev inventory's concept 11 needs classes,
inheritance, virtual functions, headers and sources, macros, CMake, shared libraries and compile errors.
`basics/math-light` (L) holds integrals, Monte Carlo, spherical harmonics and octahedral maps. For a reader without
calculus or probability, each of these needs a page of its own.

**Wrong order.** `basics/computer` (stack frames) comes before any page teaches what a function is. `basics/cpp`
comes before `basics/build`, so C++ is taught before the reader can run code. `basics/bytes` (integer sizes, hex)
comes after `basics/cpp`, whose types (`int32_t`, `uint8_t`, `float`) need it.

**Wrong kind.** All primers are kind C, so they get the concept shape (style.md 58-59): "the naive answer → the
approaches engines use → Strata's choice". That shape does not fit a lesson on vectors or on C++ classes. process.md 71
already calls `basics/math-vectors` a "(primer)". That kind is not defined in book.md or style.md.

**The beginner's door goes to hardware.** "Learn from zero" (outline-1 18) leads to *Foundations* in order, and its
first page is 5,000 words on the CPU, memory and caches. Curricula 5.3 recommends an on-ramp: "Programming you need",
"The math you need for your first game" and "What is in a frame", then the game-maker track. The plan dropped this
on-ramp.

### Proposed `basics` (replaces outline-1 69-80)

Kind `P` is a new kind, *primer*, defined in finding 7. Pages marked † are also on track G.

| id | Title | Kind | Size |
| --- | --- | --- | --- |
| `basics/first-program` † | Your first program: write it, build it, run it, break it | T | M |
| `basics/programming-1` † | Values, variables, decisions and loops | P | M |
| `basics/programming-2` † | Functions, parameters and the call stack | P | M |
| `basics/programming-3` † | Grouping data: arrays, strings, structs and classes | P | M |
| `basics/tools` | Your workbench: the terminal, folders and paths, git, a code editor | T | M |
| `basics/debugging` † | Finding bugs: compiler errors, logs and the debugger | T | M |
| `basics/computer` | How a computer runs a program: CPU, memory, stack, heap and caches | P | L |
| `basics/bytes` | Bytes, integers, floating point, text, JSON and hashes | P | L |
| `basics/cpp-memory` | Pointers, references and who owns what (RAII, `Scope`, `Ref`, move) | P | M |
| `basics/cpp-classes` | Classes in depth: inheritance, `virtual`, `override`, operators | P | M |
| `basics/cpp-generic` | Templates, lambdas and the standard library's containers | P | M |
| `basics/cpp-modern` | The modern C++ Strata uses: `optional`, `span`, `string_view`, `constexpr`, `enum class`, `if constexpr`, `requires`, macros | P | M |
| `basics/build` | How a C++ program is built | P | M |
| `basics/data-structures` | Data structures and what they cost | P | L |
| `basics/math-numbers` † | Numbers, functions, powers, logarithms and angles | P | L |
| `basics/math-vectors` † | Vectors | P | M |
| `basics/math-matrices` | Matrices and transforms | P | L |
| `basics/math-rotations` | Rotations and quaternions | P | L |
| `basics/math-change` † | Change over time: rates, accumulation, motion and interpolation | P | L |
| `basics/color` | Color and light for programmers: linear, sRGB, HDR | P | M |
| `basics/sampling` | Sampling, aliasing and filtering | P | L |
| `basics/math-probability` | Chance: random numbers, probability and Monte Carlo | P | M |
| `basics/math-sphere` | Directions on a sphere: solid angle, spherical harmonics, octahedral maps | P | M |
| `basics/threads` | Threads, atomics and races | P | L |
| `basics/reading-code` | Reading a big codebase | H | M |

This adds 15 pages. `make/cpp-for-scripts` then becomes a bridge page ("C++ in a Strata script", M), with
`basics/programming-1..3` as its prerequisites. If the planner will not add pages, the honest alternative is to change
book.md 19 and 22-23: name the entry knowledge exactly ("you can write a small program in any language; school
algebra"). That would no longer meet the owner's "people who have no idea".

## 3. Ten pages traced

For each page: what it needs, and the page that teaches it. ✗ means no page teaches it. "Later" means that the home
comes after the page in its track, or in a later wave of writing.

### `start/install` (part 0, H, S)

| Needs | Taught at |
| --- | --- |
| Unzip, folders, where to keep a program | ✗ |
| Unblock and SmartScreen (Windows), `xattr` in a terminal (macOS), `sudo apt install` (Linux) | ✗ (terminal, package manager) |
| What a GPU driver and Vulkan are, and how to update a driver | later (`gpu/how-a-gpu-frame-works`, part 6, track E) |
| Installing Visual Studio's "Desktop development with C++" workload or Build Tools, and CMake 3.25. Even Playing a sample needs them: "Press Play in a sample: it builds the sample's scripts first" (PackageReadme "Make a game") | ✗ for track G (what a compiler is: `basics/build`, track B/E) |
| Where logs are (`%LOCALAPPDATA%`, `~/.local/share`) | ✗ |
| Building from source ("build-test short form"): git, submodules (19 of them), CMake presets | ✗ (git); later (`engineering/building`) |

All of this is planned at about 1,500 words for three operating systems.

### `make/first-script` (part 1, T, M)

| Needs | Taught at |
| --- | --- |
| What source code and a programming language are | partial: `make/cpp-for-scripts` (L, concept shape) |
| `class Spinner : public Script`, `public:`, `override`, member initializers, the `90.0f` literal, `#include`, `using namespace`, `glm::` scopes, `[[maybe_unused]]` (the New Script template in Manual/Scripting), the `ST_SCRIPT_CLASS(X) { … }` macro form | partial: `make/cpp-for-scripts` |
| Quaternion turn `turn * transform.GetRotation()`, `glm::angleAxis`, degrees and radians | `make/transforms-units` (also claimed by `basics/math-rotations`; not in book.md's one-home table) |
| `deltaTime` and frame-rate independence | later: `make/script-loop` comes after it (outline-1 39-40) |
| A code editor that opens the file | later: `make/script-builds` (H) |
| Reading a compile error in the Problems panel | ✗ |
| An installed toolchain | `start/install` (too small, see above) |

### `basics/math-light` (part 2, C, L)

| Needs | Taught at |
| --- | --- |
| Functions, graphs, Σ notation | ✗ |
| Integrals (and derivatives before them) | the page itself, with no calculus before it |
| Random variable, probability density, expected value | the page itself (a quarter of an L page) |
| sin, cos, radians, spherical coordinates | ✗ |
| Projection onto a basis (spherical harmonic coefficients) | partial: `basics/math-vectors` (vector projection) |
| Cube maps | later: `indirect/ibl` |
| Pseudo-random and low-discrepancy sequences | ✗ |

### `core/jobs` (part 3, I, XL)

| Needs | Taught at |
| --- | --- |
| Threads, mutexes, atomics, memory order, deadlock | `basics/threads` ✓ |
| Lambdas and captures, `std::function`, move | `basics/cpp` (only if one XL page reaches that depth) |
| Queues, work stealing | ✗ (no data-structures page) |
| OS scheduling, thread priorities, P-cores and E-cores, power throttling (foundation concept 19) | ✗ as a primer; must be taught on the page (not allocated) |
| Frame time in ms, stalls | `core/frame-loop` ✓; how to measure: later (`core/profiling` comes after `core/jobs`) |

### `world/ecs` (part 4, I, L)

| Needs | Taught at |
| --- | --- |
| Templates, perfect forwarding, `decltype(auto)`, `static_assert` (scene-ecs code 2: `Entity.h` 12-114) | `basics/cpp` (doubtful at XL) |
| Arrays against sparse sets, O(1), linked lists, hash buckets (scene-ecs code 4, 5, 13; concept 4) | ✗ |
| A 32-bit handle split into a 20-bit index and a version (scene-ecs diagram 3) | `basics/bytes`, but it is not in part `world`'s prerequisites (outline-2 7) |
| Cache lines, cache-friendly iteration | `basics/computer` ✓ |
| UUIDs | `basics/bytes` (hashes; UUIDs not named) |

### `assets/textures` (part 5, C, L)

| Needs | Taught at |
| --- | --- |
| Texture sampling on the GPU. The assets inventory asks for "basic graphics (texture sampling) from the rendering primer" (assets §8 ch. 4) | later: part `gpu` is part 6, written in wave 5; part `assets` is wave 3 (process.md 77, 79) |
| Why mips exist: aliasing, minification, filtering | ✗ (no sampling primer) |
| Bytes per pixel, formats | `basics/bytes` ✓ |
| sRGB against linear | `basics/color` ✓ |
| lerp between block endpoints (block compression) | ✗ (no interpolation home) |
| Powers of two, log2 for the number of mips | ✗ |

The same applies to `assets/uploads`: the inventory asks for "GPU command submission basics (rendering primer)"
(assets §8 ch. 9), and its home `gpu/upload-queue` is later.

### `gpu/first-triangle` (part 6, T, L)

| Needs | Taught at |
| --- | --- |
| Building the engine, running `StrataTests` with a test filter, writing a doctest case (render-core §8 ch. 3, hands-on 1) | `start/first-engine-change` (part 0, no prerequisites); later: `engineering/building`, `engineering/test-kinds` (part 20, wave 6) |
| Shaders, Slang, `strata_add_shaders`, re-configuring | later: `gpu/shaders` comes after it (outline-2 51-52) |
| NDC, clip space | later: `gpu/coordinates` (outline-2 53) |
| Pipeline, command list | `gpu/vulkan-nvrhi` ✓ |
| A runner that checks the tutorial still works | ✗ (pipelines.md 106-116 runs only editor command scripts) |

### `physics/how-simulation-works` (part 11, C, XL)

| Needs | Taught at |
| --- | --- |
| Force, mass, acceleration, momentum, impulse | ✗ |
| Derivatives and integration, the Euler methods | ✗ |
| Cross product; 3×3 matrices | `basics/math-vectors` ✓ |
| Torque, the inertia tensor | ✗ |
| Quaternion update from angular velocity | partial: `basics/math-rotations` |
| AABB, bounding-volume trees (broad phase) | AABB: `draw/bounds-culling` (part 7, not a listed prerequisite, outline-3 64); trees: ✗ |
| Tolerances, epsilon, floating-point error | ✗ |

### `audio/sound-in-a-computer` (part 13, C, M)

| Needs | Taught at |
| --- | --- |
| Waves, frequency (Hz) | the page itself |
| Sampling, Nyquist (audio-input A1) | ✗ (no sampling primer; otherwise taught again in parts 5, 8 and 10) |
| Logarithms and decibels ("perceived loudness is logarithmic", A1) | ✗ |
| 16-bit integers against 32-bit floats | `basics/bytes` (floats are not named in its title) |
| The audio thread, lock-free hand-off | `basics/threads` ✓ |

### `automation/json-rpc` (part 19, C, L)

| Needs | Taught at |
| --- | --- |
| JSON syntax | ✗ (used since `start/first-game`, with no home) |
| TCP, ports, loopback, sockets, client and server | the page itself ✓ |
| Byte streams, framing | `basics/bytes` ✓ |
| Hashes, tokens | `basics/bytes` ✓; `automation/security` |
| A terminal to run `StrataCLI` | ✗ |

In the ten pages, 30 needed items have no page anywhere (✗). Thirteen more are taught later than the page that needs
them, or only by an unsuitable page.

## 4. style.md as the writers' contract

What is too vague to produce pages a beginner can follow:

- Line 8: "Short sentences in plain words." There is no number, so no writer and no linter can check it.
  Curricula 4.2 gives numbers: sentences of 15-20 words on average, rarely over 30; paragraphs of 2-5 sentences.
- Line 10: a term is defined "in one sentence". There is no limit on new terms per section. Curricula 4.3 item 7
  says at most three or four. There is no rule for acronyms (curricula 4.3 item 6: spell out on first use per page).
- Line 3: "may read English as a second language". This is the only line about it. Missing: a target level (CEFR B1
  is a reasonable one); a controlled vocabulary (a common word list plus the glossary plus code names); no phrasal
  verbs where a single verb exists; no pronoun whose noun is far away; no noun stacks ("scene system descriptor
  order"). Writers read inventories written in the dense style of AGENTS.md, and they will copy it unless told not to.
- Lines 25-26: "Math is derived step by step, each symbol named in words, with a number worked through." This is
  good, but it misses what an anxious reader needs. See finding 18.
- Line 27: "Code. The smallest code that does it: first a sketch, then Strata's real code." For a reader who cannot
  read C++ yet, there is no stage in plain words or pseudocode first. There are no line-by-line callouts and no rule
  for C++ features that appear before they are taught. Line 73 allows 60-line quotes; curricula 4.6 says usually
  5-25, with at most five callouts. See finding 17.
- Lines 51-53: "Check yourself (three to six questions…)", "Exercises (one to four…)". No kinds of exercise are
  given. Missing: worked examples before practice, faded examples, Parsons problems, predict-then-run, and wrong
  answers that each match a known misconception (curricula 4.7; Teaching Tech Together, curricula 735-739).
- Line 52: "at least one changes or runs real code". This cannot be met on `start/welcome`, on how-to pages, or on
  game-maker pages that need no code. There is also no environment where a beginner could run code (section 2).
- Lines 56-66: there is no primer shape, and the concept shape is forced on lessons (section 2). The tutorial shape
  puts "when it does not work" once at the end; curricula 3.3 wants "If you don't" after every step, plus a project
  checkpoint after each section.
- Lines 83-91 (Figures): screenshots are about rendering features only. Nothing asks for a picture after each
  tutorial step that changes the screen, with the control to click marked. For a beginner in the editor, that is the
  most important picture.
- Asides (lines 95-98): there is no `:::simplified` (curricula 4.8: say what is left out and where the full story
  is) and no rule for analogies (curricula 4.4: say where the analogy stops being true).
- Line 17: "No mention … of agents" conflicts with part `automation` and `make/automated-playtests`, which are about
  AI agents. It should say "of the agents that wrote the book".
- Missing everywhere: reading time on the top strip (curricula 3.0), a length limit per section, a "common
  misconceptions" section (curricula 3.1 item 8; every inventory lists "Newcomer error" items), and an exemplar
  paragraph or page that shows the voice.

## 5. The novice review (process.md)

What it must catch: knowledge used but not taught; English too hard for the reader; code the reader cannot read yet;
math steps that were skipped; tutorial steps that do not match the editor; exercises that need tools the reader does
not have. Will it?

- **The persona is wrong for the pages that matter most.** The persona is chosen "of the page's track and level"
  (process.md 46). Tracks are only `game | engine` (style.md 41; book.md 34). The primers are track E and level 1, so
  their reviewer is the engine builder who "knows some programming" (book.md 18). No persona is written down anywhere
  in the plan (the word "persona" appears only at process.md 46).
- **"Lost" is a feeling, and the reviewer is an expert.** An Opus reviewer knows C++, calculus and the engine. It
  will not feel lost where a beginner would (curricula 735-739: "experts are blind to what novices need, so test
  material on learners"). It reports "every term used before its definition", but the terms come from a glossary that
  has none of the basic words (finding 24). Skills and operations used but not taught (log2, atan2, a for loop) are
  not in its brief at all.
- **No reading-level check.** Nothing measures sentence length or rare words. The style linter (site.md 100) checks
  banned words, undefined terms and long quotes only.
- **It reviews without pictures.** Pictures are taken in phase B step 8 (process.md 87-88). The novice review runs in
  phase A, so it judges tutorials and "Show" beats without what they show. No novice pass runs after the pictures.
- **It cannot do the exercises it is told to do.** It is given "no code" and no engine, and no docs agent may build
  anything in phase A (process.md 97-99). "Does the exercises" (process.md 11) means answering on paper. Nothing in
  pipelines.md checks exercise solutions.
- **Its findings are closed by the wrong people.** The fixer may reject a "lost here" finding (process.md 12). The
  confirm step is done by the technical reviewer (process.md 50-51), not by a novice. A fix written for an expert can
  close a novice finding.
- **No real reader ever.** The plan has no step where a human beginner reads anything.

## 6. Findings

Ranked, most severe first. "Where" names the plan file and line.

1. **Blocker.** book.md 17-19 and 22-23; outline-1 38, 67-80. *Problem:* no page teaches programming, and no
   first program exists. The plan promises "Nothing assumed" (beginner) and "maybe no programming" (game maker), and
   that every prerequisite is a page of the book. `basics/cpp` is one XL page about *reading* engine C++, after
   `basics/computer` and before `basics/build`. `make/cpp-for-scripts` is one L page of kind concept. Evidence: the
   engine's feature counts and the sample scripts' C++ (section 2); gamedev concept 11; curricula 5.3. *Proposal:*
   replace outline-1 69-80 with the table in section 2. At least add `basics/first-program` (T, M),
   `basics/programming-1..3` (M each), split `basics/cpp` into four M pages, and make `make/cpp-for-scripts` a bridge
   page whose prerequisites are `basics/programming-1..3`. Add a one-home row: "Programming basics: home
   `basics/programming-*`; `make/cpp-for-scripts` links".
2. **Blocker.** book.md 31-34; style.md 41; site.md 80-81; process.md 46. *Problem:* track B exists only in prose.
   The front matter has no `beginner` value. The B sequence ("interleaved with the first chapters of track G") is
   never written. Track navigation has no data for it. The novice persona follows the track, so the primers get the
   engine-builder persona. No persona is defined. *Proposal:* (a) add `beginner` to `tracks` in style.md 41 and B
   badges in book.md 34; (b) add `plan/tracks.md` with the exact page order of each track (a B sequence is sketched in
   finding 12); (c) define three personas in style.md, each with an explicit list of what it knows. Example for B:
   "has used a PC for games and school; has never programmed or opened a terminal; school math up to linear equations,
   no trigonometry; reads English at CEFR B1; Windows 11, a mid-range GPU". (d) In process.md 46, give pages in
   `start` and `basics`, and all level-1 pages, the B persona whatever their track.
3. **Major.** outline-1 75-78. *Problem:* the math primers start at vectors. There is no algebra, no powers,
   logarithms or exponentials, and no trigonometry. Yet EV stops, decibels, `atan2`, radians and `1 - exp(-k dt)` are
   used from part `make` on. The source of `basics/math-vectors` assumed "high-school algebra" (foundation §8
   ch. 12). *Proposal:* add `basics/math-numbers` (P, L) "Numbers, functions, powers, logarithms and angles" before
   `basics/math-vectors`, put it on tracks B, E and G, and add rows to the one-home table for "logarithms and EV
   stops" and "degrees and radians".
4. **Major.** outline-1 69-80; outline-3 64 and 70. *Problem:* primers that many parts need are missing. These are
   change and motion (calculus and Newton for `physics/how-simulation-works`), sampling and aliasing (`assets/textures`,
   `image/spatial-aa`, `image/taa`, `light/shadow-basics`, `audio/sound-in-a-computer`), floating point, and
   interpolation. `basics/math-light` (L) crams four topics. Evidence: physics §8 ch. 4 lists only "vectors,
   quaternions"; audio-input A1 (Nyquist, decibels); curricula 1.2 marks these as gaps. *Proposal:* add
   `basics/math-change` (P, L), `basics/sampling` (P, L), floating point inside `basics/bytes` (raise it to L, and name
   it in the title), split `basics/math-light` into `basics/math-probability` (M) and `basics/math-sphere` (M), and
   add these pages to the prerequisites of parts `physics`, `animation`, `image`, `audio` and `indirect`.
5. **Major.** outline-1 69-80. *Problem:* there is no primer on data structures and their cost. Engine pages
   rely on sparse sets, linked lists, hash buckets (scene-ecs code 4, 5, 13), Kahn's topological sort (foundation
   concept 10), queues (`core/jobs`), spatial trees (`draw/bounds-culling`, physics broad phase) and reference graphs
   (`assets/references`). *Proposal:* add `basics/data-structures` (P, L) "Data structures and what they cost: arrays,
   lists, hash maps, queues, trees, graphs, big-O". Add it to the prerequisites of parts `world`, `core`, `assets` and
   `draw`.
6. **Major.** outline-1 18-23 and 69-80. *Problem:* tools and operating-system ideas are never taught: the
   terminal, folders and paths, git, a code editor, the debugger, reading compiler errors. Yet `start/install`,
   `start/first-engine-change`, `make/automated-playtests`, `make/export` and part `engineering` use them. There is
   also no place where a reader can run a sketch or an exercise. Curricula 1.0, 1.1 and 1.18 mark these as gaps.
   *Proposal:* add `basics/tools` (T, M) and `basics/debugging` (T, M). Make `basics/first-program` the page that sets
   up the reader's workbench (compiler, terminal, editor, the `sketches/` folder) on each OS. Every primer exercise
   then runs there.
7. **Major.** book.md 38-46; style.md 56-68; process.md 71. *Problem:* there is no *primer* kind. The ten
   primers (and `make/cpp-for-scripts`) are kind C and get the concept shape, "approaches engines use → Strata's
   choice", which does not fit a lesson. process.md 71 already uses "primer" as if it were a kind. *Proposal:* add the
   kind `primer` to book.md's table and to style.md's shapes. Shape: what you can do after this page → what you
   already know (links) → small steps, each a worked example and then a try-it → common mistakes → a practice set with
   worked solutions → summary. Use it for every `basics/*` page except `reading-code`, and for `make/cpp-for-scripts`.
8. **Major.** outline-1 8, 72, 75. *Problem:* XL is "never split into several pages". So `basics/cpp` and
   `basics/math-vectors` are single pages of 8,000 or more words. For a beginner who reads English as a second
   language, that is more than an hour of dense text with no stop. Curricula 735-739 says to chunk. *Proposal:* in
   outline-1 8, add: "Pages of tracks B and G, and all primers, are at most L. A larger subject becomes several
   pages." Split `basics/math-vectors` into `basics/math-vectors` (M) and `basics/math-matrices` (L).
9. **Major.** outline-1 20-23. *Problem:* part `start` does not work for a beginner. (a) `start/install` (S) must
   cover three operating systems, unsigned executables, GPU drivers and the Visual Studio C++ workload with CMake.
   Even Playing a sample builds its scripts (PackageReadme "Make a game"). It also carries a source-build "short form".
   (b) `start/first-game` comes from the AI-agent skill (CLI, scripts, export), not from a UI walkthrough.
   (c) `start/first-engine-change` needs git, CMake, a terminal, C++ and doctest, with no prerequisites, in part 0.
   (d) `start/what-an-engine-is` comes after it. *Proposal:* raise `start/install` to M, release download only, with
   tabs for each OS and a separate "Install the C++ tools (needed to build scripts)" section that says how large the
   download is. Move the source build to `engineering/building`. Make `start/first-game` free of code (gamedev
   hands-on G2-G3, Basic 3D, no samples) and base it on gamedev, not on the skill. Move `start/first-engine-change` to
   `engineering/first-change`, with prerequisites `basics/tools`, `basics/build` and `basics/cpp-classes` (or keep it
   in `start` marked track E only and not linked from the "learn from zero" door). Put `start/what-an-engine-is`
   second, after `start/welcome`.
10. **Major.** outline-1 31, 38, 41-44, 48; book.md 27-28. *Problem:* the game maker's own math and programming
    homes are not decided. `make/transforms-units` and `basics/math-rotations` both teach rotations. `make/cpp-for-scripts`
    and `basics/cpp` both teach C++. `make/characters-cameras` needs normalize, dot, cross, `atan2`, `exp` and
    `std::remainder` (gamedev code 19-20). Track G does not include `basics`. The gameplay API pages are how-tos
    ("no theory", style.md 67), although the scripting inventory proposed them as "reference + tutorial". *Proposal:*
    put `basics/programming-1..3`, `basics/debugging`, `basics/math-numbers`, `basics/math-vectors` and
    `basics/math-change` on track G (the † pages). Add one-home rows: "Vectors for game makers: `basics/math-vectors`;
    `make/transforms-units` links" and "Rotations at the user level: `make/transforms-units`; the math:
    `basics/math-rotations`". Change `make/gameplay-1..3` to kind T.
11. **Major.** book.md 27-28 and 58; style.md 43. *Problem:* the "why" links of part `make` lead to E pages
    whose prerequisites are internals pages. The style example itself gives `core/time` the prerequisite
    `core/frame-loop` (an internals page). A game maker who follows the one-home rule from `make/script-loop` reaches
    pages that need an XL math primer and an internals chapter. *Proposal:* add the rule "a concept page that a `make`
    page links for 'why' has only prerequisites in `start`, `make` or track-G primers". The strips plugin (site.md 72)
    enforces it, and it also checks that every prerequisite comes earlier in every track sequence of
    `plan/tracks.md` (curricula 3.0, "Before you start").
12. **Major.** outline-1 39-40; outline-2 25, 51-53; outline-4 22; process.md 73-74. *Problem:* the trace finds
    prerequisites that come later. `make/first-script` uses `deltaTime` before `make/script-loop`. Part `assets` needs
    GPU texture sampling and command submission, by its own inventory (assets §8 ch. 4 and ch. 9), but part `gpu` is
    part 6 and wave 5, against wave 3. `gpu/first-triangle` comes before `gpu/shaders` and `gpu/coordinates`, and it
    needs building and testing from part 20. Part `ui` (wave 4) lists `gpu/text` (wave 5). process.md 73-74 claims the
    waves respect prerequisites. *Proposal:* swap `make/script-loop` before `make/first-script`, or teach `deltaTime`
    in `make/cpp-for-scripts`. Add `gpu/how-a-gpu-frame-works` and `gpu/upload-queue` to part `assets`'s
    prerequisites, and write `gpu` up to `gpu/upload-queue` in wave 3. Move `gpu/first-triangle` after
    `gpu/coordinates`, with `engineering/first-change` as a prerequisite. Move part `ui` to wave 5, or `gpu/text` to
    wave 4. A sketch of the B sequence: `start/welcome` → `start/what-an-engine-is` → `start/how-to-read` →
    `start/install` → `start/first-game` → `make/editor-tour` → `make/scenes-entities` → `basics/math-numbers` →
    `basics/math-vectors` → `make/transforms-units` → `basics/first-program` → `basics/programming-1..3` →
    `basics/debugging` → `make/cpp-for-scripts` → `make/script-loop` → `make/first-script` → `basics/math-change` →
    the rest of track G; then, for engine builders, `basics/tools` → `basics/computer` → … in the order of section 2.
13. **Major.** outline-1 58-60. *Problem:* all three project chapters sit at the end of part `make`. The first
    finished game (Coin Run) is page 30 of 33, after about 120,000 words. Curricula 5.2 Part II and the Rust book
    pattern (curricula 664-670) say to interleave project chapters. *Proposal:* make Coin Run the running example of
    part `make`, built in stages. Each stage closes an enabling page: spinning coins after `make/first-script`;
    collecting coins after `make/input` and `make/physics`; the HUD and the win screen after `make/ui` and
    `make/sound`; shipping after `make/export`. Each stage has a checkpoint project. `make/project-coin-run` then
    becomes the short page that assembles and polishes it. Tetris follows `make/recipes`.
14. **Major.** outline-1 25-61; book.md 93-99. *Problem:* there is nothing on how to design or structure a
    game: core loop, scope, prototyping, game feel, playtesting, game state and win or lose conditions. The owner asks
    for people with "no idea how to implement a … game". Curricula 1.13 marks it "[gap]", and no inventory covers it.
    Game AI and navigation are not in the list of what Strata does not do. *Proposal:* add `make/designing-a-game`
    (C, M) before the first project, from curricula 1.13 and GPP's State, Update Method and Object Pool. Add "game AI,
    pathfinding and navigation meshes" to book.md 96-99 and to `appendix/not-in-strata`.
15. **Major.** pipelines.md 106-116; process.md 97-99; style.md 52-53. *Problem:* eight tutorials change the
    engine, and no runner checks them: `start/first-engine-change`, `world/tutorial-component`, `gpu/first-triangle`,
    `assets/extending`, `image/tutorial-post-effect`, `scripting/host-api`, `editor/tutorial-command`,
    `editor/tutorial-panel`. The tutorial tool runs only editor command scripts. Exercises that "change or run real
    code" have no check either. An untested step is where a beginner gets stuck with no way out. *Proposal:* add to
    pipelines.md "Engine tutorials are patches": `tutorials/<part>/<chapter>.patch`, applied to the pin, built and
    tested by `tools/tutorials.py` in phase B (curricula 3.3 item 9). Add "Exercise solutions": sketches with expected
    output, editor exercises as command scripts, engine exercises as patches, each stamped like tutorials.
16. **Major.** style.md 64-66 and 83-91; pipelines.md 106-116. *Problem:* what a beginner follows is the UI tab
    (**Menu ▸ Item**, drag here), and nothing verifies it. The tutorial tool runs commands, not clicks. Drags and the
    placement ghost cannot be simulated or captured (captures.md §5 item 7). The inventory's UI labels "come from source
    strings, not from seeing the editor" (gamedev §9). style.md asks for no screenshot per step, and gives no
    checkpoints. *Proposal:* (a) in style.md's tutorial shape, require for each step the action, "you should see"
    with a whole-editor picture where the screen changes, and "if you don't"; (b) add a checkpoint project after each
    section, produced by the tutorial runner and downloadable from the page; (c) in phase B, a UI walk: an agent or a
    person does each tutorial through the UI in a windowed editor and takes the step pictures. Until then, a check
    finds every **Menu ▸ Item** path in the menu strings of `EditorLayer.cpp` at the pin.
17. **Major.** style.md 27 and 72-81; pipelines.md 33. *Problem:* the code rules assume a reader who reads
    C++. Quotes may be 60 lines. There are no callouts, no plain-language stage, and no rule for a C++ feature that
    appears before it is taught. *Proposal:* on level-1 pages and on track B and G pages, quotes are at most 25 lines.
    Each quote is preceded by its idea in plain words (or `Pseudocode`) and followed by at most five numbered callouts
    that say why. The first time a page uses a C++ feature not yet taught, it adds a `:::question` "What is
    `std::optional`?" (two lines plus a link to its `basics/cpp-*` home), as curricula 4.6 and Catlike Coding do.
    `start/how-to-read` gets a section "How to read code you do not understand yet".
18. **Major.** style.md 25-26 and 30-31. *Problem:* nothing handles fear of mathematics. *Proposal:* add a
    section "Math for readers who fear it". The order is: the idea in words and a picture → one example with small
    numbers, worked by hand → the formula, with each symbol read aloud ("Σ is read 'the sum of'") and its units → the
    code → a check at the limits (curricula 4.5). Long derivations go in a collapsible "Where this comes from" box
    marked "you can skip this". Each part has a notation table on its first page. G pages state results in words and
    keep formulas in boxes. Never write "it follows", "clearly" or "it is easy to see" (add them to the banned words
    of site.md 100).
19. **Major.** style.md 13, 19-28, 51-53 and 95-98. *Problem:* teaching devices from the curricula study are
    missing: worked examples and faded examples, Parsons problems, predict-then-run, misconception distractors,
    analogies with their limits, a "simplified" box, and a misconceptions section. The rule "an exercise changes or
    runs real code" does not fit G and how-to pages. *Proposal:* add from curricula 4.4, 4.7 and 4.8 the kinds of
    exercise; a rule "at least one worked example before the first exercise"; check questions whose wrong answers come
    from the inventory's "Newcomer error" items; `:::simplified` and `:::analogy` (with "where it breaks") asides; and a
    "Common mistakes" section in the concept and primer shapes. Change style.md 52-53 to "at least one exercise is done
    in the editor (G) or runs code on the reader's workbench (B, E)".
20. **Major.** style.md 3 and 8-13; site.md 100. *Problem:* the language rules cannot be measured. There is no
    target for a reader of English as a second language, and nothing stops writers copying the dense prose of the
    inventories. *Proposal:* add to style.md: sentences of 20 words or fewer on average, none over 35; paragraphs of at
    most five sentences; at most four new terms per section; every acronym spelled out at its first use on the page; a
    word list (a common English list of about 3,000 words, plus the glossary, plus code names), with words outside it
    defined; no noun stacks of more than two nouns; "never copy sentences from the inventories, AGENTS.md or the
    Developer Guide". Give five good and bad sentence pairs. The style linter (site.md 100) measures sentence length,
    paragraph length, terms per section and words outside the list.
21. **Major.** process.md 11 and 46-49. *Problem:* the novice review rests on a feeling of being "lost", and the
    reviewer is an expert model. It checks terms only, not skills or operations. *Proposal:* make it a provenance
    check. The reviewer gets the persona's knowledge list, plus the `learn` lines, the summaries and the glossary terms
    of the page's prerequisite closure. For each section, it lists every idea, term, symbol, C++ feature and UI action
    the section uses, and names the sentence that taught it (on this page or in a prerequisite). Anything without a
    source is a finding "used but not taught". It also runs the reading metrics of finding 20. "No code" in process.md
    46 should read "no access to the engine's source".
22. **Major.** process.md 12, 50-51, 87-88 and 117. *Problem:* novice findings are closed without a novice. The
    fixer may reject "lost here". The confirmation is technical. Pictures arrive after the novice review. No human
    beginner reads anything. *Proposal:* (a) a fresh novice reviewer (a new agent, since the first has learned the
    page) confirms every fix of a novice finding; (b) the fixer may not reject a "used but not taught" finding, only
    move the teaching to a prerequisite and say where; (c) after phase B's pictures, a second novice pass for
    tutorials and level-1 pages; (d) add an open question to README.md: before phase B, can the owner have two or three
    real beginners do `start/install` → `start/first-game` → `make/first-script`, and note where they stopped?
23. **Major.** process.md 69-72. *Problem:* the pilot has no page where the beginner promise is most likely to
    fail: no programming page, no `start` page. `basics/math-vectors` is a primer, but for a reader who already has
    algebra. *Proposal:* replace `core/time` with `make/cpp-for-scripts` (or `basics/programming-1`), and add
    `start/install`. Review both with the B persona, using the provenance check of finding 21.
24. **Major.** pipelines.md 137-142; site.md 71 and 100. *Problem:* the glossary is merged from the inventories'
    1,592 engine terms. Those have no entry for variable, function, terminal, git, source code, integer, floating
    point, array, vector, integral, probability, debugger, operating system, folder, path or byte (searched in the
    `inventory/*.md` glossaries). So the linter's "undefined terms" check can never flag the basic words a beginner
    lacks. *Proposal:* before writing starts, seed the glossary with a beginner base vocabulary of about 300 terms,
    each homed in a `start` or `basics` page. Add to process.md step 3: "the base vocabulary is merged first".
25. **Minor.** style.md 65; outline-1 19. *Problem:* every tutorial's second tab shows JSON commands from
    `start/first-game` on, and JSON has no home until `basics/bytes` (track B/E). *Proposal:* give JSON a short home in
    `start/how-to-read` ("How to read a command"), name it in `basics/bytes`'s title, and say on G pages that the
    command tab is optional.

## 7. Further minor findings (file only)

- style.md 42: `level` is about dependencies, not difficulty. A beginner cannot tell how hard a page is or how long it
  takes. Add `time:` (reading or doing minutes) to the front matter and the top strip (curricula 3.0), and say on the
  strip what level 1, 2 and 3 mean.
- style.md 51: "Summary (five lines at most)" is not tied to the `learn` lines. Make each `learn` line get one
  summary sentence and at least one check question (curricula 3.0, bottom strip).
- appendix/math-cheatsheet (outline-4 157): also give a "how to read the symbols" table (Σ, ∫, ‖v‖, ·, ×, θ) with the
  page that teaches each.
- book.md 19: "then either track". After `basics` the beginner meets parts that are tagged E only. Say on
  `start/welcome` which track a beginner continues on, and how far along the B sequence they must be to start it.
- outline-1 21: "Your first game in 30 minutes". If it keeps a sample or a script, the toolchain download alone can
  exceed 30 minutes. Either keep it free of code (finding 9) or drop the time from the title.
- outline-1 59-60: `make/project-tetris` and `make/project-platformer` are XL tutorials on one page each. With
  checkpoints (finding 16) this can stay, but give each section its own "you should now have" picture.
- pipelines.md 34-35: sketches are checked with "`-fsyntax-only` at least". A sketch shown as a "tiny program whose
  output surprises" (style.md 23) must run, and its shown output must be compared. Make that the rule for every
  sketch shown with output.
- style.md 15: numbers measured on an RTX 5090 mean little to a beginner on a mid-range GPU. On G pages, add one
  sentence on what the number means for a typical player's machine, or state it as a share of the frame.
