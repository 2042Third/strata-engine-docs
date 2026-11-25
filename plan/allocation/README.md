# The allocation: which page holds what

The allocation gives every page of the outline its content, and every item of the inventories one home page. The
part briefs are written from it (`../process.md`, "Allocation and part briefs"). This file is the contract: the
allocators write to it, `check_allocation.py` checks it, and the planner settles what the check reports.

Two rules stand above the rest:

- **Every item has one home.** An item of an inventory is taught on exactly one page (its `home`), or the allocation
  says why the book leaves it out. Other pages may use it or link to it. This is how the book holds every feature of
  the engine, and how one concept keeps one home (`../book.md`, "One home per concept").
- **Nothing is used before it is taught.** A page lists what it assumes and which page teaches that. The check
  compares the list with the page's Needs.

## Items

An **item** is one thing an inventory lists: a row of a table or a top-level entry of a list, in sections 1 to 7 and 9
of a file of `../inventory/`. Section 8 (proposed chapters) holds no items: the outline has used it.

- The inventories are frozen. They are never edited, so a line number names an item for good.
- An item's id is `<inventory>:<line>`: the file's name without `.md` and the line where the item starts
  (`foundation:112`). `<inventory>:<a>-<b>` names every item that starts on lines a to b.
- An item's type follows from its section:

  | Section | Type |
  | --- | --- |
  | 1. Features | `feature` |
  | 2. Concepts to teach | `concept` |
  | 3. Code worth showing | `code` |
  | 4. Figures | `figure` |
  | 5. Rules and pitfalls | `rule` |
  | 6. Hands-on | `hands-on` |
  | 7. Glossary | `term` |
  | 9. Not determined | `open` |

- `check_allocation.py items` writes the list of all items to `items/<inventory>.tsv` (id, type, a short label).
  Allocators cite ids from these files.
- A **new item** is something a page must hold that no inventory lists: code that no inventory surveyed, an entry of
  "What Strata does not do", an erratum, a concept of a primer, a check before writing (below). Its id is `new:<n>`,
  numbered within its file. Its types are those above and also `not-done` and `erratum`. A new item always states its
  evidence (below).

## Units

One allocator works on one **unit** and writes one file, `<unit>.md`. A unit is a part of the book, with three
exceptions: `make` is four units, `basics` is two, and `audio` and `input` are one (they share an inventory).

| Unit | Pages | Inventory it owns |
| --- | --- | --- |
| `start` | part `start` | - |
| `make-a` | `make` block A | - |
| `make-b1` | `make` block B from `make/gameplay-math` to `make/levels-saves` | - |
| `make-b2` | `make` block B from `make/lamps` to `make/samples` | - |
| `make-c` | `make` block C | - |
| `basics-a` | `basics/computer` to `basics/data-formats`, and `basics/threads` | - |
| `basics-b` | `basics/math-vectors` to `basics/math-sphere` (the mathematics, `basics/color`, `basics/signals`) | - |
| `core` | part `core` | `foundation` |
| `world` | part `world` | `scene-ecs` |
| `gpu` | part `gpu` | `render-core` |
| `assets` | part `assets` | `assets` |
| `draw` | part `draw` | `render-scene` |
| `light` | part `light` | `render-direct` |
| `image` | part `image` | `render-image` |
| `indirect` | part `indirect` | `render-indirect` |
| `physics` | part `physics` | `physics` |
| `animation` | part `animation` | `animation` |
| `audio-input` | parts `audio` and `input` | `audio-input` |
| `scripting` | part `scripting` | `scripting` |
| `ui` | part `ui` | `gameui` |
| `worlds` | part `worlds` | `worlds-runtime` |
| `editor` | part `editor` | `editor-core` |
| `editor-ui` | part `editor-ui` | `editor-ui` |
| `automation` | part `automation` | `automation` |
| `engineering` | part `engineering` | `build-test` |
| `capstone` | part `capstone` | - |
| `reference` | part `reference` | - |
| `appendix` | part `appendix` | - |
| `router-gamedev` | none | `gamedev` |

**The owner of an inventory places every item of it**, each exactly once in the owner's file: as a `home` row on one
of the owner's pages, or as a row of "Passed on" that names the page of another unit which should be its home, or
`nowhere` with the reason. `nowhere` is for what is not content: a surveyor's note about files it did not read, an
item that repeats another item (name that item). A feature of the engine is never `nowhere`.

`gamedev.md` is the game maker's view of the whole engine, and its pages are spread over five units. So one agent, the
**router**, reads it whole and passes every item on to a page of `start` or `make` (or elsewhere, or `nowhere`). Its
file `router-gamedev.md` holds only "Passed on".

**A unit takes what is passed to its pages.** For each item passed to one of its pages, the unit adds a `home` row (on
that page or on a better one of its own), or a row of "Not taken" with the reason and the page it thinks better. An
item that nobody takes goes to the planner.

A unit never writes `home` for an item of an inventory it does not own, unless the item was passed to it. A unit that
thinks one of its pages is the true home of such an item writes `use` and a line under "Questions for the planner".

## The file of a unit

````markdown
# Allocation: <unit>

## `<page id>` — <title>

**Covers.** What the page teaches, in the order it teaches it. One or two paragraphs.

**Leaves out.**

- <what a reader might expect here> → `<page id>`

**Fit.** `fits`: about 4,600 words against L (5,000). <One or two sentences.>

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:112-118` | feature | home | The clock and the three kinds of time |
| `foundation:344` | code | home | `Strata/src/Strata/Core/Application.cpp:412-448`: the fixed-step loop |
| `scene-ecs:301` | concept | use | Fixed steps, as the scene's systems see them |
| `new:1` | not-done | home | No variable physics rate per scene. Evidence: `Docs/Roadmap.md:1701` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| A rate of change, and adding small steps | `basics/math-change` | must |
| What a thread is | `basics/threads` | helps |

**Starting state.** <Tutorials, how-tos with steps, and primers with a checkpoint only: the project or checkpoint the
page starts from, and what it already holds.>

**Command-only steps.** <Tutorials and how-tos with steps only: `none`, or each step that only a command can do.>

## Passed on

| Item | Type | To | Why |
| --- | --- | --- | --- |
| `foundation:150` | feature | `engineering/profiling` | The profiler's setup is taught with measuring |
| `foundation:690` | open | `nowhere` | A note about files the survey did not read |

## Not taken

| Item | Passed by | Why not | Better page |
| --- | --- | --- | --- |

## Questions for the planner

- <a question, or `none`>
````

The rules of the format, which the check enforces:

1. A unit's file has one `## ` section for each of its pages, in the outline's order, and no section for another
   page. The heading starts with the page's id in backquotes. The generated pages (`<part>/index`, `<part>/review`)
   have no section.
2. Every page section has **Covers**, **Leaves out**, **Fit**, **Items** and **Assumes**, in this order, each starting
   a line in bold with its full stop inside the bold. Pages of kind T, and of kind H where the page has numbered
   steps, also have **Starting state** and **Command-only steps**. A page of kind P may have **Starting state**, never
   **Command-only steps**: every checkpoint of a primer stands in its Starting state, and Covers keeps what the page
   teaches (`../critique/rulings-7.md`, R33; `../critique/rulings-8.md`, R38). A list or table that is empty holds
   the one word `none` in place of the list or table.
3. **Items**: the Item cell holds one or more ids in backquotes, separated by commas. Every id names an item that
   exists; the Type is the item's type. Role is `home`, `use` or `link`:
   - `home`: this page teaches it. The reader learns it here.
   - `use`: the page uses it or teaches how to use it; the home is elsewhere. The use pages of `make` are of this
     role for the engine's inventories, and of role `home` for the items of `gamedev` passed to them.
   - `link`: the page names it and links to its home.
4. A `home` row of type `code` names one item (no range), and its last cell starts with the excerpt's place at the
   pin as `` `<path from the repository's root>:<first line>-<last line>` ``. The allocator has opened that file in
   the pin clone and seen that the lines hold what the row says. The inventories often shorten a path
   (`Skeleton.cpp` 178-187): the row gives it whole.
5. A row of a new item states its evidence at the pin in its last cell, after the word `Evidence:`: a file and lines,
   or the exact search that finds nothing (`../book.md`, "What Strata does not do", rule 4). A new item that says
   nothing about Strata (a concept of a primer, such as binary numbers) has no place in the engine: its last cell
   ends with `General knowledge.` and may name where the plan asks for it. A new item that holds a check before
   writing (below) is of type `open`, and its last cell starts with `Check: <the check's name>.`; a last cell that
   starts with `Check:` belongs to such an item.
6. **Fit** starts with one of `fits`, `under`, `over` in backquotes, a colon and "about N words against <size>
   (<the size's budget>)", then one or two sentences. The budgets and the ranges of the sizes are those of rule S
   (below, "Sizes, Needs and homes"). The state is measured against the range of the page's size
   (`../critique/rulings-8.md`, R37):

   | State | The estimate | The line says |
   | --- | --- | --- |
   | `fits` | inside the range and below its top | what takes the most words, in one or two sentences |
   | `over` | at or over the top of the range | the next size, or the split with the titles of the pages (S2, S3, S5) |
   | `under` | below the bottom of the range | what the page could take from a neighbour; on a page marked W8 or W8r, what phase B adds; or the smaller size (S2) |

   A page of kind R has no size check (`../critique/rulings-7.md`, R33): its state is always `fits`, its number is
   the prose it holds, and its sentence states the generated volume that gives the page its size. The check compares
   nothing for it, and `coverage.md` never lists it among the pages over or under. An estimate that equals the size's
   budget to the word gets a warning: it is counted again from the page's sections (S5).
7. **Assumes** lists what the page uses and does not teach, as far as the page's least prepared persona does not
   bring it (`../book.md`, "Readers and personas"; a page on tracks G and B is written for B0, who has never
   programmed). "Taught by" is a page id in backquotes, or `?` when the allocator finds no page of the outline that
   teaches it. Depth is `must` (the page cannot be followed without it) or `helps` (a link is enough). Name a concept
   in the words of the one-home table of `../book.md` or of the glossary where they have it.
8. **Leaves out**, "Passed on" and "Not taken" name pages by id in backquotes; every id is a row of the outline.
   "To" may also be `nowhere`.
9. An agent writes only its own unit's file. It runs no git command that writes, and it edits no other file of
   `plan/`. What it would change elsewhere (the outline, a Need, a size, `book.md`) it asks under "Questions for the
   planner".

To estimate a page's words: the fixed parts of a page (strips, summary, questions with answers, further reading) take
about 600 words; a concept taught from zero 300 to 500; a code excerpt with what to look for and what it showed 200 to
300; a figure with its paragraph 100 to 150; a step of a tutorial with its "You should see" and "If you do not see
it" 100 to 150; a rule with its why 80 to 120. Pages for B0 take the upper values.

## Sizes, Needs and homes

These rules hold for every change of a size, a Need or a home (`../critique/rulings-7.md`, R28).

**Rule S, sizes.** The budgets of prose words are S 1,500, M 3,000, L 5,000 and XL 8,000. The ranges are S 600 to
2,250, M 2,251 to 4,000, L 4,001 to 6,500 and XL 6,501 to 10,000.

- **S1.** A page whose estimate is inside the range of its own size keeps its size, whatever its Fit line says.
- **S2.** An estimate inside the range of the next size up or down changes the size by one class, when
  `../check_outline.py` allows that class for the page's kind and tracks. A page marked W8 or W8r is never made
  smaller.
- **S3.** Otherwise the page splits. Each new page answers one question a reader would ask and can be read in its
  place on its tracks, and the tracks' rules hold. Primers and pages of track B split where another page would take
  XL. Where a split would break a track's rule, named items move to a page with room, where a reader would look for
  them.
- **S4.** A page never loses content it needs, and never teaches faster than its least prepared persona can follow
  (`../critique/rulings-4.md`, R7). Nothing is cut and no depth is lowered to make a page fit.
- **S5.** An estimate is made again whenever a page's items change. A page whose new estimate is at or over the top
  of its range takes the next class by S2, or splits by S3: a page planned at its top has no room, and the estimates
  are rough. An estimate that equals the page's budget to the word is counted again from the page's sections before
  it is believed.

**Rule N, Needs.**

- **N1.** An Assumes row of depth `must` whose teacher is outside the page's Needs closure makes the teacher a Need of
  the page, when the teacher stands before the page on the page's tracks and `../check_outline.py` passes. Where many
  pages of one part miss the same page, the part's "Needs of the part" takes it.
- **N2.** Where the teacher cannot become a Need: another page inside the closure that teaches the concept is named
  (with its home row); or the concept moves to an earlier page; or the page teaches the little it needs itself, and
  the depth is `helps`.
- **N3.** A row whose teacher is `?` names the page with the concept's home row, or the best page to take the concept.

**Rule D, one home.** A concept is taught once, from one angle. A how-to page of `start` or `make` and an internals
page may both hold home rows about one feature when they take different things from it (how to use it; how it
works). The same angle twice is a duplicate: one page teaches, the other links.

**Whose home, when two pages claim one term or concept.** The row of `../book.md`'s one-home table decides. Where the
table has no row, the home is the page that teaches the matter from zero; where two pages do, the earlier one in the
outline's order. A page that uses the word, and whose Needs closure does not hold the home, says what it means in one
sentence and links the home.

**What a page of kind R is the home of** (`../critique/rulings-8.md`, R36). An item is homed where the book states
it in full. A page of kind R explains nothing: it lists facts. So it is the home only of **catalogue items**: facts to
look up that no teaching page explains further. A helper's declaration, a field of the renderer's statistics, the
slot of a binding, a release and its date, a credit, and an erratum about a number that the page's table states right
are catalogue items. The test: when a reader needs more than the row of a table to use the thing or to understand it,
a teaching page is its home, and the page of kind R holds a `link` row. Every item of type `concept` fails the test.
A new item on a page of kind R whose content is a list of facts takes the type `feature`, not `concept`. The four
pages of kind R in `appendix` are written by hand, and the rule is the same for them. `check` warns on a home row of
type `concept` on a page of kind R.

**Concepts on how-to pages** (`../critique/rulings-7.md`, R31). A how-to says why in at most two sentences and links
the concept page (`../style.md` §7.5). `check` warns on a home row of type `concept` on a page of kind H outside the parts
`start` and `make`: the unit moves the item to a concept or internals page, or the page's Fit line says why the how-to is where a
reader learns it.

## Checks before writing

The allocation reads code; it runs nothing. A claim that rests on code alone and that a run can settle is held as a
new item of type `open` on the page that will state it (`../critique/rulings-7.md`, R34). Its last cell starts with
`Check: <the check's name>.`, with the name as the table below gives it, then states the claim and its evidence at
the pin (rule 5). A page that holds such an item gets no brief until the check's result has replaced the item,
unless the engine's agents run the check: those four checks wait for the engine's work after 0.8.0, so their pages
are briefed and written from the code at the pin, say that the claim was read, not run, and are corrected when the
result is in (`../critique/rulings-9.md`, R39). `check_allocation.py checks` lists these items by check, with page
and unit.

| Check | Who runs it | Pages that hold the item |
| --- | --- | --- |
| Simulate and skinned meshes | the photographer, with the pin's editor | `animation/editor`, `animation/system`, `make/play-test-debug` |
| A capture of the Game view without a camera | the photographer | the pages that hold the figures of ui-q6 (the UI over black) |
| A capture step that opens the launcher's card | the photographer | the pages that hold the figures of automation-q4 |
| The recipe that sets WhenVisible on every fox | the photographer | `animation/culling` (screenshot 11; animation-q8) |
| `PrefabSync` with cells | the engine's agents, as a test or a run; does not block the brief | the pages that critic-worlds-runtime-4 names |
| The pending window of mesh colliders | the engine's agents, as a test or a run; does not block the brief | the pages that critic-worlds-runtime-10 names |
| Mouse units on a scaled display | the engine's agents, as a test or a run; does not block the brief | the pages that critic-audio-input-7 names |
| Script breakpoints on Linux and macOS | the engine's agents, as a test or a run; does not block the brief | the pages that basics-a-q5 names |
| What miniaudio does when a device is lost | the writer of `audio/engine`, from miniaudio's source at the pin | `audio/engine` |

## What an allocator reads

1. `../README.md`, `../book.md` (the personas, "One home per concept", the design decisions, "What Strata does not
   do", the running examples), the legend of `../outline-1.md` and the outline file with the unit's pages,
   `../tracks.md`, `../style.md` §1, §7, §10 and §11, `../process.md` ("Allocation and part briefs" with its table of
   errata) and `../critique/rulings-4.md`.
2. The inventory the unit owns, whole. Of other inventories: every item that the From column of the unit's pages
   names, found through `items/<inventory>.tsv`, and the section around it.
3. The engine at the pin, whenever it checks a place or looks for what no inventory surveyed: the clone
   `G:/GameEngineAI/.worktrees/docs-pin`, read only. Never the repository `G:/GameEngineAI` itself, whose files are
   not at the pin, and never a build.

Besides placing items, an allocator:

- places every entry of "What Strata does not do" of `../book.md` whose "Page that says it" is one of its pages, as a
  new item of type `not-done` on that page, with the table's evidence, run again at the pin;
- places every erratum of `../process.md`'s table that names its part, as a new item of type `erratum` on the page
  that would otherwise repeat the mistake, and adds the errata it finds itself;
- applies the notes of the critique that `../process.md` lists under "Allocation";
- lists, in **Command-only steps**, every step that only a command can do, and places it by the rule for such steps
  (`../critique/rulings-7.md`, R33):
  - On track E, a page before `editor/commands` that needs such a step gives the complete line to paste, one sentence
    on what it does, and a link forward to `editor/commands` (R11). That is no Need: `start/how-to-read` teaches how
    to read and run a command.
  - On a page of track G or B, the page that teaches running a command is in the page's Needs closure, or the step
    moves to a later page or into the starting checkpoint (`../style.md` §10). `make/automated-playtests` teaches
    running a command script (the editor's `--commands`), and `make/commands` teaches StrataCLI: a step that runs a
    script needs the first, and a step that calls a command needs the second.
  - A page on track E and on track G or B follows the rule for G and B.
- names, in **Starting state**, every checkpoint a page starts from, a primer's included (R11;
  `../critique/rulings-8.md`, R38);
- holds every claim that rests on code alone and that a run can settle as a check before writing (above);
- gives each page of `light`, `image` and `indirect` its figures by the rule of `../process.md`, item 5 of the brief:
  off and on, the debug view, a sweep, a crop.

Pages marked W8 or W8r are allocated like the others, from the inventories as they stand at the pin. Their **Fit**
line ends with what phase B must look at again.

## The check

```text
python plan/allocation/check_allocation.py items                 write items/<inventory>.tsv
python plan/allocation/check_allocation.py check [--unit <unit>] the format and every id, and that an owner places
                                                                 each item of its inventory once; exit 1 on a problem;
                                                                 then the warnings, which never change the exit code
python plan/allocation/check_allocation.py inbox <unit>          the items passed to the unit's pages that it has
                                                                 neither taken nor refused
python plan/allocation/check_allocation.py demands <unit>        the Assumes rows of other units that name a page
                                                                 of the unit, and every row with `?`
python plan/allocation/check_allocation.py code --engine <clone> [--unit <unit>]
                                                                 check the place of every `home` row of type code
python plan/allocation/check_allocation.py checks                the items that hold a check before writing, by
                                                                 check, with page and unit; nothing when there are none
python plan/allocation/check_allocation.py coverage              write coverage.md
```

`check` prints its warnings after the problems, under their own heading. A warning never fails the check: it names a
row that the unit or the planner looks at again. The check warns on a Fit estimate that equals its size's budget to
the word (S5; never on a page of kind R), on a home row of type `concept` on a page of kind R, and on a home row of
type `concept` on a page of kind H outside the parts `start` and `make` ("Sizes, Needs and homes").

`coverage.md` is written by the script alone and lists what the planner must settle:

- items with no home and no `nowhere`; items with two homes; items passed on that nobody took;
- Assumes rows of depth `must` whose teacher is not in the page's Needs closure (the page's Needs, their Needs, and
  the part's "Needs of the part"), and rows with `?`;
- pages that are `over` or `under`, never a page of kind R, with the count of their `home` rows per type: this
  list is what the second size pass reads (`../critique/rulings-8.md`, R37);
- every line of "Questions for the planner".

## Order of the work

1. The check script with its tests, the router's file, and the glossary seed (`../glossary/seed.json`,
   `../pipelines.md` §9).
2. Every unit except the two of `basics`, side by side. The units of `start` and `make` begin with their inbox.
3. The two units of `basics`, which begin with their demands: what the other units assume from their pages, and what
   has no teacher. They also correct the seed's homes. Beside them, every other unit takes its inbox.
4. `coverage`, then the completeness critics: one per inventory reads the inventory against the files (is each home
   the page where a reader would look? is anything of the area missing from the inventory itself?), one reads
   `../book.md`'s tables against the files, and one per unit without an inventory reads its pages from the side of
   the page's persona (`../critique/rulings-7.md`, R34). The planner settles their findings and `coverage.md`; the units apply the
   decisions; the check runs again. `completeness.md` records each finding and its Outcome: `applied`,
   `applied: <what differs from the proposal>`, `rejected: <the reason>`, or `waits: <the check>` with the name of a
   check before writing (above). No finding stays `open`, and a finding that names pages of several units has one
   Outcome (`../critique/rulings-7.md`, R29).
5. The terms of the inventories enter the glossary. Each entry's home is chosen in the order of `../pipelines.md`
   §9: the seed's entry, then a `make` page's twin, then `../book.md`'s one-home row or the page in the Needs
   closure of every page that marks the term (`../critique/rulings-7.md`, R33).
