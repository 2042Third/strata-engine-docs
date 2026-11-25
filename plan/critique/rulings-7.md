# Rulings 7: the allocation's settlement

The allocation gave every item of the inventories a home page (`allocation/README.md`: 6,733 items, 29 units). Then
twenty critics read it for what is missing, thin, stale or in the wrong place, six agents proposed sizes, Needs and
merges under three working rules and answered the units' 231 questions, and one agent wrote the digest,
`allocation/proposals/for-planner.md`. The digest counts 344 findings (`allocation/completeness.md`) and asks the
planner for 43 decisions, D1 to D43.

This file gives them. It is read with the digest: a ruling names the decision and says what holds; the digest holds
the matter, the options and the ids of the findings and questions behind it. "As recommended" means the digest's
recommendation, word for word.

Where this file differs from an earlier ruling, from `book.md`, `style.md`, `pipelines.md`, `process.md`, `site.md`,
`README.md`, the outline or `allocation/README.md` as committed before it, or from a proposal file, this file wins;
those files are changed with it (R35). Earlier rulings stay as records, and so do the proposal files and the critics'
files: nobody edits them.

## R28 — The working rules are rules of the plan

The proposals were made under three working rules that stood only in the run's instructions. They hold from now on,
for the application of this file and for every later change of a size, a Need or a home. `allocation/README.md` gets a
section that states them.

**Rule S, sizes.** The budgets of prose words are S 1,500, M 3,000, L 5,000, XL 8,000. The ranges are S 600 to 2,250,
M 2,251 to 4,000, L 4,001 to 6,500, XL 6,501 to 10,000.

- **S1.** A page whose estimate is inside the range of its own size keeps its size, whatever its Fit line says.
- **S2.** An estimate inside the range of the next size up or down changes the size by one class, when
  `check_outline.py` allows that class for the page's kind and tracks. A page marked W8 or W8r is never made smaller.
- **S3.** Otherwise the page splits. Each new page answers one question a reader would ask and can be read in its
  place on its tracks, and the tracks' rules hold. Primers and pages of track B split where another page would take
  XL. Where a split would break a track's rule, named items move to a page with room, where a reader would look for
  them.
- **S4.** A page never loses content it needs, and never teaches faster than its persona can follow (R7). Nothing is
  cut and no depth is lowered to make a page fit.
- **S5 (new).** An estimate is made again whenever a page's items change. A page whose new estimate is **at or over
  the top** of its range takes the next class by S2, or splits by S3: a page planned at its top has no room, and the
  estimates are rough. An estimate that equals the page's budget to the word is counted again from the page's
  sections before it is believed.

**Rule N, Needs.**

- **N1.** An Assumes row of depth `must` whose teacher is outside the page's Needs closure makes the teacher a Need of
  the page, when the teacher stands before the page on the page's tracks and the check passes. Where many pages of one
  part miss the same page, the part's "Needs of the part" takes it.
- **N2.** Where the teacher cannot become a Need: another page inside the closure that teaches the concept is named
  (with its home row); or the concept moves to an earlier page; or the page teaches the little it needs itself, and
  the depth is `helps`.
- **N3.** A row whose teacher is `?` names the page with the concept's home row, or the best page to take the concept.

**Rule D, one home.** A concept is taught once from one angle. A how-to page of `start` or `make` and an internals
page may both hold home rows about one feature when they take different things from it (how to use it; how it
works). The same angle twice is a duplicate: one page teaches, the other links.

**Whose home, when two pages claim one term or concept** (D33's principle): `book.md`'s one-home row decides. Where
it has none, the home is the page that teaches the matter from zero; where two do, the earlier one in the outline's
order. A page outside the home's Needs closure that uses the word says what it means in one sentence and links.

## R29 — What follows from the rules is applied

Section 2 of the digest stands as written:

- the 56 size changes and three splits of `proposals/sizes.md` (R30 adds to them);
- the 47 Needs cells and the 28 teacher cells of `proposals/needs.md`, and `start/coming-from`'s row (D10);
- the 39 merges of `proposals/duplicates.md`, with the homes of R31 where R31 names another;
- the 162 answers that follow from a rule, as their rows in the three question files say, unless a ruling below
  changes them; and the 69 answers marked for the planner, as the rulings below decide them. Where a ruling says "as
  recommended", the answer's row holds;
- the findings that only need applying. A stale item is reworded in every row that repeats it. A missing item
  becomes a new item with the evidence the finding gives, read again at the pin. A thin home widens its row's take.
  An order slip gets a `helps` row. The 15 findings of severity `must` that need no decision are applied as the
  digest lists them.

Every one of the 344 findings gets an Outcome in `allocation/completeness.md`: `applied`; `applied: <what differs
from the proposal>`; `rejected: <the reason>`; or `waits: <the check of R34>`. No finding stays `open`. A finding that
names pages of several units gets one Outcome.

Where a proposal names a page that a split divides, read the half that `sizes.md` ("Splits in detail") gives the
item: `basics/data-formats` for CRC-32C (`foundation:643`), HMAC, UUID, regular expressions and reading text into
tokens; `basics/math-bases` for decomposition (`new:22`).

## R30 — The outline

The outline starts from the trial (`docs-work/B/outline/plan/`: the changes of `sizes.md` and `needs.md`, which
passes the check) and takes these changes. `docs-work/B/outline/CHANGES.md` lists what the trial changed.

**D1, split.** `basics/tools` becomes two primers: `basics/tools`, "The tools: the terminal, files and a code
editor" (M), in its place; and `basics/git`, "Version control with git" (M), after `basics/debugging`, on tracks B
and E. `core/first-change` and the "Needs of the part" of `core` name `basics/git`. Track G keeps its two side steps.
The copy `docs-work/B/sizes/alt-tools/plan/` shows the rows.

**D2, merge.** `draw/visibility-feedback` becomes the last section of `draw/gpu-driven` (XL, about 8,300 words): the
counting pass writes the feedback. The Needs of `draw/mip-streaming` and `animation/culling` and the "Needs of the
part" of `animation` name `draw/gpu-driven`.

**D3.** `light/sun-shadows-1` takes a section on how the sun's casters are culled and drawn into the cascades on
both paths (about 450 words) and is XL. A page splits only past 10,000 words (R7). The Leaves out line of
`allocation/light.md` that sends the casters to `draw` goes; `draw/gpu-driven` keeps one sentence that points forward.

**D4, sizes with the findings in.** By S5:

| Page | In the trial | Now | Why |
| --- | --- | --- | --- |
| `light/sun-shadows-1` | L | XL | D3; about 7,200 words |
| `assets/importing` | L | XL | at L's top, and the content stamp and two findings come in; about 6,800 |
| `worlds/runtime` | L | XL | at L's top, and two findings come in; about 6,690 |
| `draw/gpu-driven` | L | XL | D2's merged page |
| `gpu/upload-queue` | M | L | at M's top, and the Present stage comes in (R31); about 4,200 |
| `core/debugging` | M | L | about 4,060 |
| `light/material-data` | M | L | about 4,100 |
| `editor/camera-viewport` | M | L | D16's section; about 4,600 |
| `scripting/tutorial-host-function` | M | L | D38's scene service; about 4,400 |
| `make/automated-playtests`, `gpu/debug-drawing`, `assets/handles-meta`, `editor-ui/ui-testing` | M | L | exactly at M's top |
| `make/lamps` | M | L | a W8 page at 3,800: phase B adds the rectangle lights |

`editor/script-builds` keeps L: it stands at L's top, and D12 and the one addition on a script's crash during play
(R31) take about 250 words off it. The other pages near a top keep their sizes for now. After the units have applied
their findings they estimate every page they touched again (S5) and report the pages at or over a top; a **second
size pass** then changes the outline once, with the check. Units never edit the outline.

**D5, orders inside parts.**

1. `ui`: layout, contract, input, text, drawing; `ui/input` is a Need of `ui/text`.
2. `editor/command-scripts` comes before `editor/journal`, as rulings-2 listed them; `editor/command-scripts` needs
   `editor/stepping`, `editor/journal` needs `editor/undo` and `editor/command-scripts`, and `automation/agents`
   needs `editor/journal`.
3. `light/reflectance` comes before `light/material-data`, so F0 is taught before the rule of 0.04. If the check
   refuses the order, it stays as it is, and rule 586 with the half of excerpt 435 that explains it moves to
   `light/reflectance`; S5 then sizes `light/material-data` again.
4. `draw/render-scene-gpu` and `draw/batching` keep their order; the two `helps` rows of critic-render-scene-5 say
   what the earlier page uses from the later one.
5. The WindZone chain reads in one line: `editor/tutorial-command` needs `scripting/tutorial-host-function` and
   starts from its end state.

**D6, titles and cells.** `automation/mcp` is titled "StrataCLI and its MCP server". `editor/projects` is titled
"Opening projects and scenes: templates, background loads and migration". The row of `appendix/credits` says what
R20 to R22 put there (D18). From cells: `start/install` drops the `script.status` check, and `start/first-game`
says that the first build (Play on the Tetris copy) is the toolchain's check, or a toast names what to install;
`make/automated-playtests`, `basics/programming-1` (with `book.md`'s line on `Key::Space`), `image/why-post` and
`indirect/seam` change as their answers say (make-b2-q4, basics-a-q3, image-q2, indirect-q2).

**D9, the reference pages keep the trial's Needs**, with `editor/commands`, `world/what-a-world-is` and
`editor-ui/shell` in place of `make/commands`, `make/scenes-entities` and `make/editor-tour`: the reference is
written for the persona of track E. The site shows no "Before this part" on `reference/index` (site.md). The lint
rule `term-source` exempts kind R only if a reference page still fails it after this.

**D10, Needs that rule N does not ask for.** `start/install` gains `start/how-to-read`; `editor-ui/imgui` gains
`editor-ui/immediate-mode`; `basics/math-geometry` gains `basics/math-projection`, and its row's depth becomes
`must`; `make/commands` and `make/performance` gain `make/animation` (D40). The trial's two choices stand:
`basics/numbers` is a Need of `basics/math-matrices`, and `editor/camera-viewport` gains `editor/commands`.
`start/coming-from`'s row with the teacher `?` is deleted: what it names is the page's reader, and the fact goes into
the page's "what must be true first".

**The counts.** The outline then holds 335 pages (332, three splits, `basics/git`, less one merge) and 30 primers.
Every other count, the words and the waves come from `check_outline.py --counts --words --waves` and go into
`book.md`, `README.md` and `process.md` in the same edit; the trial's `process.md` is older than the current file,
so its numbers are written into the current one. Where the check refuses a change of this section, the change is
left out and reported with the rule that refused it, and the planner rules. The check itself changes only as R35
says.

**Waves.** The six waves stay as `process.md` has them; wave 1 is not cut in two. A wave may be written in several
batches (process.md says so in one sentence).

## R31 — Homes, teachers and Needs

| Decision | Ruling |
| --- | --- |
| D7 | Static initialization `basics/build`; structs as bytes `basics/bytes`; `std::filesystem::path` `basics/cpp-modern`; calling a C library `basics/cpp-generic`. The geometric series and its sum: `basics/math-interpolation` (`basics/numbers` drops its row and links). Regular expressions: `basics/data-formats`, about 350 words, as `needs.md` describes. Reading Python has no home page: every Python fence is followed by its explanation line by line (`code-follow`), and the first Python fence of a page says in one or two sentences what differs from C++ in it (style.md); the rows stay `helps`. No `appendix/reading-python-regex`. |
| D8 | `make/lamps`, `make/reflections`, `make/gi` and `make/look` each link forward to `make/quality` for the one preset fact they use. The presets are taught once. |
| D11 | The row of inactive reasons splits. `SetInactiveReason`, its rule and its term (`scene-ecs:198`, `:531`, `:654`) are homed on `world/reflection` (about 300 words); how the Inspector shows a reason stays on `editor-ui/inspectors`. `book.md`'s row follows, and the five forward links go. |
| D12 | `Process` is homed on `core/platform` (about 250 words). `editor/script-builds` uses it and links. |
| D24 | `->`, `nullptr`, `*` in a type, `std::optional`, `has_value` and `value_or` are homed on `basics/programming-3` (`cpp-features.json`, style.md). |
| D25 | Validation layers (`render-core:304`) move to `gpu/vulkan-nvrhi` (about 250 words). `check_allocation.py` warns on a concept item homed on a page of kind H outside part `make`. `physics/tuning` and `engineering/contributing` move theirs to a concept or internals page, or their Fit line says why the how-to is where a reader learns it. |
| D26 | A generated page teaches nothing, so no item is homed on a page of kind R. The seven SDK classes with a twin move to the twin's teaching page; the seven without go to the pages critic-scripting-4 names. `reference/script-api` lists them (a `link` row). |
| D33 | By R28's principle: backpressure `assets/loading`; hysteresis `input/gamepads`; content stamp `assets/importing` (with `assets:145`); Game view `editor/play-mode`; Dist `core/first-change`; draw list `draw/batching` (feature and term); content scale `core/windows-events`; infinite far plane `gpu/coordinates`. |
| D40 | `animation:190` to `make/commands`; `animation:520` to `make/performance`; `render-core:668` to `nowhere`, as a repeat of `render-scene:559`; the day and night scripts (`gamedev:386`, `:549`) to `make/reflections`, beside `render-direct:645`; the absences of networking and game AI are homed on the appendix pages, and `automation/json-rpc` and `make/patterns` link. With these, no inventory item is without a home or `nowhere`. |

The collisions of the digest's section 4 that no decision settles:

- **Raycast.** One entry, homed on `physics/queries`. `editor/placement` teaches the editor's ray against the scene
  as its own mechanism, under its own name, and links to the entry. A second entry is made only if step 5 finds the
  word used for a second meaning (R33, D32).
- **The sequence lock.** `core/jobs` keeps the excerpt of `SequenceLock.h` (`book.md`'s row); `audio` quotes its use.
- **Present.** The term is homed on `gpu/how-a-gpu-frame-works`. The stage (`render-core:214`) is homed on
  `gpu/upload-queue`. `core/profiling` keeps its list of stages with one sentence that points forward.
  `gpu/readback-timing` links, and says that Present is no GPU stage.
- **Fixed steps, never frames.** The rule is homed on `core/time`. `editor/stepping` keeps the exception (input
  holds also count frozen frames) and links.
- **Action maps on track G.** One addition of about 200 words on `make/input`.
- **A script's crash during play.** One addition of about 150 words on `editor/play-mode`, counted once.
- **Frame timelines.** One figure, `world/systems`' timeline, with an overlay for physics and one for worlds (D42).

Cross-unit moves happen in one round: the owner's row goes to "Passed on" and the receiver writes its home row.
Afterwards `check_allocation.py inbox` is empty for every unit.

## R32 — What pages hold

| Decision | Ruling |
| --- | --- |
| D13 | `make/animation` keeps the sample's layout (the robot under the player), so that readers can compare with `Samples/ThirdPerson`, and teaches what follows from it: step 8 on the model's root that carries the controller, the drift as an "If you do not see it", Footsteps on the robot, step 9 on a second robot. About 300 words. |
| D14 | As recommended, in this order: first one capture of Simulate in the pin's editor (R34); then the sentence on `animation/editor`, `animation/system` and `make/play-test-debug`, and screenshot 2 made in Simulate. Until the capture, the three pages hold the check as an item (R34). The engine hears of it (R34). |
| D15 | A new feature item on `core/first-change`: what a source build needs (the Linux development packages of GLFW and nfd, the compilers' minimum versions, CMake 3.25, Slang's first download, the Vulkan SDK as optional), in the Linux tab, about 150 words; `build-test` passes it to `core`. The minimums also stand in "What must be true first" of `engineering/building` (about 80). |
| D16 | `editor/camera-viewport` takes the section "Captures" (how `viewport.capture` works, about 700 words, code row `EditorViewportCommands.cpp:808-845`) and is L (R30). |
| D17 | As recommended: `book.md`'s row reads "registries that open and accept; the component and settings registries then freeze"; `core/layers-registries` teaches the two kinds; figure `scene-ecs:447` is labelled as the component registry's; an erratum row; the three Assumes rows are reworded. |
| D18 | One pass, as recommended. `appendix/credits` takes the statement of R20, R21's permission and the fox's full credit as new items; `start/how-to-read` one sentence; `make/project-coin-run`, step 8, a link; screenshot 11 of `animation/culling` and every figure of the Open World sample that shows a fox, a caption with the credit. "The Showcase fox" goes: the fox is the Open World sample's. This closes item 15 of R26. |
| D27 | The exercises are added now, so that sizes count them: the four `world` pages and the five internals pages get the exercises critic-scene-ecs-6 names. Every other unit checks its own pages for the exercises style.md asks of the page's kind, and adds what is missing (about 250 words each). |
| D28 | The rule: an entry of "What Strata does not do" whose subsystem has a `make` page names that page too. The 15 entries of critic-book-4 and -5 are added (about 40 to 50 words each); `make/sound` says that a Streamed clip holds its encoded bytes in memory. |
| D35 | All rows the digest lists become entries of "What Strata does not do". Each entry's evidence (the search that finds nothing, or the line that says no) is run again at the pin by the unit that writes it. |
| D36 | As recommended: `book.md`'s one-home table gets rows for the areas of critic-book-6 to -11 and one sentence that says what the table lists (features and concepts that more than one part could claim; a page is the home of everything in its own Covers without a row); the UUID row (64 bits); the `:::why` of decision 5 on `light/units-exposure`; the evidence cells. |
| D38 | The WindZone chain as recommended, every point. |
| D39 | As recommended: the coins' bob is the first step of `make/scripting-scene`; a how-to of block A ends in `## Result` with a download of its end state (one sentence in style.md §7.5); the pages of block B share the obstacle course, each with its own downloadable start. |
| D43 | As the agents propose. Idle throttling is said on `make/performance`, where the frame time is read. |

## R33 — Rules that disagreed, and the glossary

| Decision | Ruling |
| --- | --- |
| D19 | R11 holds on track E: a page before `editor/commands` that needs a step only a command can do gives the complete line to paste, one sentence on what it does, and a link forward to `editor/commands`. On a page of track G or B, the page that teaches running a command is in the Needs closure, or the step moves to a later page or into the starting checkpoint, as style.md §10 says. A page on track E and on G or B follows the rule for G and B. style.md §10, process.md's line on such steps and the lint's strips rule say this. |
| D20 | For tracks G and B, `make/automated-playtests` teaches running a command script (the editor's `--commands`), and `make/commands` teaches StrataCLI. A command-only step that runs a script needs the first; one that calls a command needs the second. |
| D21 | Starting state is allowed on pages of kind P: every checkpoint of a primer stands there, not in Covers. `check_allocation.py` accepts it, with tests; the primers' units move what they wrote into Covers. |
| D22 | No size check for pages of kind R, the four of `appendix` included: their size is the measure of generated volume that their Fit line states, and their words stay in the book's totals. The lint's `size` says "A page that does not fit asks the planner for the next size; nothing is cut to fit (R7)". `book.md` and `outline-1.md` say: XL is about 8,000 words (6,501 to 10,000); an XL page is split into sections with their own anchors; past 10,000 words a page splits into pages (R7). |
| D23 | process.md's table of errata holds both kinds, and a column says which: the engine's documents and comments that are wrong at the pin, and slips of the inventories. The rows the answers and findings propose are added (about 25), each read again at the pin. The first kind also goes to the engine (R34). The 49 stale-item findings correct the allocation's rows themselves. |
| D29 | New seed entries: log on `start/install`, build on `start/first-game`, debug information on `basics/debugging`, worded as `proposals/questions-learner.md` words them. Moves: editor to `start/welcome`; scene, entity and component to `start/first-game`. |
| D30 | As recommended: the four homes stay where the allocation moved them, the lines of `book.md` and `pipelines.md` follow, and the counts are corrected wherever they stand (1,587 terms in 1,567 entries; the seed has 400 entries). The splits move the seed words that `sizes.md` names; `check_seed.py` passes afterwards. |
| D31 | The seed's format gains an optional `use` (pipelines.md §9, `check_seed.py`). README's step 5 is written down: one entry per term; the seed's entry wins; a `make` page is the `use` of its twin's entry; otherwise the home is `book.md`'s row, or by R28's principle the page in the Needs closure of every page that marks the term. |
| D32 | `book.md`'s rule 6 states the principle: a word with several meanings gets one qualified entry per meaning, and the unqualified word is never a term of its own. Its six words stay as examples. Step 5 takes the homonym groups of `docs-work/B/duplicates/judge_c.txt` and the critics' lists as its candidates. |
| D34 | All nine definitions are corrected before step 5, as the findings say. |

## R34 — Findings for the engine, checks before writing, generated tables

**D37, what the allocation found in the engine.** The book states the behaviour of the pin; it never states what
the code ought to do. The findings go to the engine's work after 0.8.0, in one list that pipelines.md §11 names
beside the additions:

| Finding | From |
| --- | --- |
| After an exception leaves the frame loop the program exits with code 0 | critic-foundation-7 |
| Release builds need AVX2 and nothing checks for it at startup | critic-build-test-5 |
| Nothing runs the format check that the engine's guide calls enforced | critic-build-test-15 |
| `PrefabSync` catches instances up once per prefab and scene; cells that load later may stay behind | critic-worlds-runtime-4 |
| The SDK comment of `IsLoadedAround` promises collision while mesh colliders may still be pending | critic-worlds-runtime-10 |
| Simulate shows skinned meshes in their bind pose | critic-animation-2 |
| Mouse units on scaled displays: an exported game reports mouse positions in screen coordinates and its window size in framebuffer pixels | critic-audio-input-7 |
| `AnimationSystem` and `AudioSystem` use `AssetManager`'s static functions, which the engine's guide forbids | animation-q7, critic-audio-input-8 |
| The Tetris sample's README says its rules are tested on their own; no test builds the rules class | critic-gamedev-6 |
| Script modules built with GCC or Clang carry no debug information (`-g`) | basics-a-q5 |
| The engine's documents and comments that D23 lists | D23 |

The fix of the exit code and `-g` are asked for v0.8.1, with the tier 1 additions. Until a fix ships at the book's
pin, the page says what the pin does, and where a reader would expect otherwise, "What Strata does not do" has the
row.

**D41, checks before writing.** Nothing in the allocation was run. A claim that rests on code alone and that a run
can settle is held as a new item of type `open` on the page that will state it, labelled "Check:" with the check's
name. A page's brief is written only when the page has no such item left: the check's result replaces it.

| Check | Who | Pages that wait |
| --- | --- | --- |
| Simulate and skinned meshes | the figure agent, with the pin's editor | `animation/editor`, `animation/system`, `make/play-test-debug` |
| A capture of the Game view without a camera (the UI over black) | the figure agent | the figures of ui-q6 |
| A capture step that opens the launcher's card | the figure agent | the figures of automation-q4 |
| The recipe that sets WhenVisible on every fox (animation-q8) | the figure agent | `animation/culling` (screenshot 11) |
| `PrefabSync` with cells; the pending window of mesh colliders; mouse units on a scaled display; script breakpoints on Linux and macOS | the engine's agents, as tests or runs (the list above) | the pages the findings name; until a result is in, the page states only what the code at the pin shows, and says that it was read, not run |
| What miniaudio does when a device is lost | the writer of `audio/engine`, from miniaudio's source at the pin | `audio/engine` |

The figure agent's captures run once the pin's programs exist, under the performance lock.

**D42, generated tables and figures.** As recommended: pipelines.md §7.1 gets rows for terms, further reading, the
CPU stages and a `perf.<name>` key per budget, and §7.2 gets `game-makers.json`; a figure planned twice is captured
once; physics and worlds reuse `world/systems`' frame timeline; figure rows name the look-dev shots they use;
switches that tier 2 lacks are shown as diagrams, and one request extends tier 2.

**What nobody checked** (the digest's section 6) is checked in the application:

- The ten units without an inventory (`start`, the four `make` units, both `basics` units, `capstone`, `reference`,
  `appendix`) had no completeness critic. Each gets one now, with the critics' contract, reading from the side of the
  page's persona: what does the page need that it does not list, against style.md's shape for its kind and against
  the samples and the SDK at the pin. Their findings are settled by this file's rules; what needs a decision comes
  to the planner.
- `check_allocation.py code --engine` runs over every unit, so the critics' new code rows are read at the pin.
- For every Assumes row of depth `must`, a verifier reads whether the teacher's section holds a home row for the
  concept.
- `check_seed.py` runs on the seed after the splits' moves and D29's entries.

## R35 — What changes, who changes it, and in what order

**The plan's files.**

| File | Change |
| --- | --- |
| `book.md` | D6 (`Key::Space`), D11, D17, D22, D28, D30, D32, D35, D36, D38, D39, D43; the counts |
| `style.md` | D7 (the first Python fence), D19, D20, D22, D24, D39 |
| `process.md` | D19, D23, R30's sentence on batches, the counts, the seed's numbers |
| `pipelines.md` | D30, D31, D37's list in §11, D38, D42 |
| `site.md` | D9's rule for `reference/index`; D30's numbers |
| `README.md` | D21, D30, D31 (step 5), the counts |
| `outline-1.md` to `outline-4.md`, `tracks.md` | R30 |
| `allocation/README.md` | R28's rules; Starting state on kind P (D21); no home on kind R (D26); the "Check:" item (R34) |
| `allocation/<unit>.md` | everything else, by the unit |
| `allocation/completeness.md` | the Outcome column |

**The check scripts.** `check_allocation.py` accepts Starting state on kind P and warns on a concept item homed on a
page of kind H outside part `make`, each with tests. `check_outline.py` reads `book.md`'s new sentence on sizes.
`check_seed.py` takes the optional `use`. The lint (the tool builder's) skips `size` on kind R, its strips rule
follows D19 and D20, and `tools/booklib/outline.py` follows `check_outline.py`: the planner tells the tool builder in
the handover, and what the chain has already built is the fixer's work.

**The order.**

1. The planner's files and the check scripts (the two tables above).
2. The outline (R30), with the check passing and the counts in the same edit. In the same edit, because the check
   wants a section per page in the outline's order: `basics-a` and `basics-b` write the new pages' sections and
   move their items, `draw` merges two sections, and `ui`, `editor` and `light` put theirs in the new order.
3. The cross-unit moves, in one round (R31).
4. The completeness critics of the ten units without an inventory (R34).
5. Every unit applies its findings and answers: new items with evidence, widened takes, reworded rows, teacher
   cells, `helps` rows, errata, exercises (D27), "Check:" items (R34); then it estimates its touched pages again
   and rewrites their Fit lines (S5).
6. `check_allocation.py check`, `inbox` and `demands` for every unit, `code --engine`, and `coverage`; the Outcome
   column; the second size pass (R30); verifiers who try to refute what the units report.
7. README's step 5, the glossary (after D29 to D34). Then the part briefs.

**Earlier texts this file replaces.**

| Earlier text | Now |
| --- | --- |
| rulings-2, part 0: `start/install` ends with the `script.status` check | the first build on `start/first-game` is the check (D6) |
| The outline's order `editor/journal` before `editor/command-scripts` | command scripts first, as rulings-2 listed them (D5) |
| style.md §10 and process.md: a command-only step before `editor/commands` moves to a later page | R11 holds on track E (D19) |
| outline-1.md: XL is "8,000 or more", an XL page is never several pages | XL is 6,501 to 10,000 words; past 10,000 a page splits (D22) |
| style.md, `size`: a page that does not fit "is cut" | it asks for the next size (D22) |
| pipelines.md §9 "the seed wins" against README's step 5 | D31's order of precedence |
| `book.md`, rule 6: a list of six words | a principle, with the six as examples (D32) |
| R26, item 15: left for this settlement | D18 |

## For the owner

Nothing in this file waits for the owner. The four questions of rulings-6 ("For the owner") are still open, and none
of them holds the work back.
