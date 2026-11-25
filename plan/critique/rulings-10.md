# Rulings 10: what the packets left open

The packets of the units (`docs-work/C/packets/`, written from the plan at `be1893b`) carry every finding, answer and
ruling to the unit that applies it. Their writers and their reviewer reported the points that no file of the plan
settles. This file settles them. Where it differs from an earlier file or from a packet, this file wins. The planner
made the edits of R48 and the rows of R47 in the same commit; the rest is applied by the units in the second
application, which reads this file beside its packet.

## R44 — The five questions that no ruling named

| Question | What holds |
| --- | --- |
| `start-q9` | As proposed: `start/welcome` keeps every section of the concept shape, one or two paragraphs each, mapped by the part's brief. `start.md` changes nothing; the unit removes the question. |
| `ui-q4` | As recommended, one line. `editor`: the table of command groups on `editor/commands` names `ui/input` for the `ui` group beside `make/automated-playtests`. `ui`: `ui/input` gains a `use` row for one `ui.hitTest` line, which runs the page's own hit test (`StrataEditor/src/Editor/EditorUICommands.cpp:414-470`). The handlers get no code home. Both units remove the question. |
| `reference-q4` | The split stands as `reference` made it: the full rows of components, settings, commands and the SDK are on the four catalogue pages only, and an area page of `reference` links the catalogue's anchor for its module and holds what is its own (units, formats, limits, services, statistics). `physics` and `ui` send "every property with its default and range" to `reference/components`; units stay with `reference/physics`. |
| `editor-ui-q6` | The three new items stand. The screenshot paragraph: next row. |
| `reference-q8`, `automation-q4`, `router-gamedev-q7` | The inventories' notes on how pictures are made instruct the photographer, so they belong to pipelines.md §5.5, not to a page. The second application checks each of the eleven passages that `from-workflow-a.md` lists (verify.paragraphContent) against §5.4 and §5.5 and adds what is missing to §5.5. `reference/figures` keeps its one section for readers. The three units remove the question. |

## R45 — An Assumes row without a teacher in the book

Six rows of depth `helps` have the teacher `?`, and no page of the outline teaches their subject: reading a short
Python function or script (four pages of `engineering`), least-squares fitting with the principal axis of a cloud of
points, and mesh simplification (two pages of `assets`).

An Assumes row names what another page of the book teaches. What no page teaches is not assumed; the page supplies
it. So:

- The four Python rows are deleted. Each of the four pages introduces its first Python fence with the paragraph that
  says what differs from C++ (R40, D7), and its Covers says so in a clause.
- The two rows of `assets` are deleted. Each page's Covers says that the page explains the idea in a paragraph where
  it uses it (what the fit finds; what simplification keeps), and the page's further reading names a source.
- After the second application no Assumes row of the plan has the teacher `?`. A unit that finds another such row
  either names the page that teaches the concept or treats the row this way, and reports which.

## R46 — The round of moves

**R36's judgment comes first.** The ledger's lines 84 to 120 are candidates: items homed on a page of kind R that
may teach. Before the round, `reference` and `appendix` judge each by R36's test. An item that passes stays, and its
line leaves the round. An item that fails gets its teaching page, and its line joins the round with that page's
unit as the receiver. The judgment is a file beside the ledger (`docs-work/C/packets/r36-judgment.tsv`); the units
read it with the ledger.

**One round.** A receiver takes every move the ledger and the judgment give it. Where it judges a move wrong (its
page does not teach the item, or teaches it later than the giver's page), it takes the item all the same and says so
in its report; the planner settles those after the round. Nothing is passed back or on.

**The SDK's classes without a twin** (lines 14 to 22). The mapping that the ledger reads from today's `use` rows
stands: `scripting:118` to `:121` go to `make/scripting-scene`, `:124` to `basics/programming-1`, `:129` to
`make/levels-saves`, `:133` to `make/recipes`, and `:123` and `:134` to `make/timers-events`. R36's "fourteen"
counted classes; the ledger counts items, and a class may have two.

**Decomposition and the cofactor matrix** (lines 124 to 126). The moves stand: the three terms are words of
mathematics, taught from zero on `basics/math-bases`, which is their home by R28; `world/scene-graph` and
`draw/mirrors-camera-relative` hold `use` rows. What the engine's function does (it fails for zero scale and for a
matrix with shear) is a fact about the function and stays in `world/scene-graph`'s Covers. It is no second meaning:
the glossary has one entry, "decomposition (of a transform)", and "normal matrix" joins the cofactor matrix's entry
unless `basics-b` homes it apart.

**Order slips** (critic-animation-9, critic-render-image-3, critic-scene-ecs-3). R29's sentence holds as the packets
read it: an order slip gets a `helps` row on the earlier page, and the moves that the three proposals ask for are not
made.

**Game view and Scene view** (line 28). The move stands: `editor-ui:763` goes to `editor/play-mode`, and
`editor-ui/scene-view` keeps a `use` row. The item names three terms. The glossary step splits it: "Game view" is one
entry with `editor-core:694`, homed on `editor/play-mode`; "Scene view" and "viewport" are homed on
`editor-ui/scene-view`, whose `use` row says so now.

**Hysteresis** (line 24). The move stands: the term goes to `input/gamepads`, the earlier page that teaches it;
`worlds/streamer` keeps its concept of the load and keep radii and says what hysteresis is in a sentence with a
link.

**An erratum whose Briefs cell names a whole part.** The packets' rule stands: the unit whose page would repeat the
mistake places it. Where two units place the same erratum, the check finds the second home, and the planner keeps
the row of the page that comes first in the outline.

## R47 — "What Strata does not do": two rows, and evidence

R34 asked for a row where a reader would expect otherwise. Both cases qualify, and book.md has the rows with this
file:

- A failure exit code after an exception leaves the frame loop (the program logs a critical line, ends in order and
  exits with 0): `core/frame-loop`. `core` adds the `not-done` item beside the sentence that critic-foundation-7 asks
  for.
- A check at startup for the processor's AVX2 (the release builds are compiled for it): `engineering/flags-portability`
  and, by rule 7, `make/export`. `engineering` and `make-a` add the `not-done` items beside what critic-build-test-5
  asks for.

Both stay on the engine's list for v0.8.1 (pipelines.md §11). When a fix ships at the book's pin, rule 6 removes the
row.

The two rows of the animation table cited "animation inventory §1.16", which is no evidence at the pin
(critic-book-24). They now cite the searches, run at `822a7a46`. The row about work stealing cites the Roadmap's
lines and the search for "fiber" (core-q2).

## R48 — Small edits made with this file

| Where | What |
| --- | --- |
| README.md (step 5), pipelines.md §9, process.md (step 7), site.md | "about 1,590 terms" in place of the exact counts (R40, D30). |
| pipelines.md §6, the `startsFrom` row | The form `{"tutorial": "<page id>", "exercise": <n>}` of R41. |
| book.md's running examples and outline-1.md, `basics/programming-2` | "the lines that request and instantiate the prefab are given" (basics-a-q4): `Scene::Instantiate` returns a null entity until the prefab is loaded, so the practice needs the request, the check and the call. |
| book.md, "Placing content" | The Use cell is `make/prefabs` (router-gamedev-q3). |
| book.md, the row of probability | It names importance sampling (indirect-q3). The glossary step splits `render-indirect:583`: "importance sampling" on `basics/math-probability`, "filtered importance sampling" on `indirect/ibl`. |
| book.md, the columns of the one-home table | A page of `start` in the Use column is a first use: the place where track G's reader acts on the concept before part `make`. It is no glossary `use` (R40). |

`start.md` calls two pages of `start` "the use home" (`start/how-to-read` for a command's JSON, `start/install` for
the terminal). The unit writes "the first use", as book.md's columns now say.

Added to R42's list for the builders of the tools: the table of the CPU's stages that critic-foundation-3 asks for is
a generated table (`tools/reference.py`), like the renderer's.

## R49 — Outcomes, and how the second application reads the packets

- critic-book-14 to -21: `declined: the page's own Covers is its home (book.md, "One home per concept", first
  paragraph); D36 gave rows to critic-book-6 to -11`. critic-book-24: `applied` (R47, with the evidence cells that the
  first application corrected).
- The Outcome column of `completeness.md` is filled after the second application, from the units' reports and from
  this list, and the planner checks it: every row ends in one of R29's forms.
- The packets cite lines of the plan at `be1893b`. The edits of this file change no file of `allocation/`. In book.md
  the lines after the columns' paragraph of "One home per concept" move by two, and by one more after each of the two
  rows added to "What Strata does not do"; the other files keep their line numbers. A unit reads a row before it
  changes it and goes by the row's words, not by its number.
- Still later, as the packets say: the inbox is empty only after the round; the completeness critics of the ten units
  without an inventory run in the second application (R35, step 4); book.md's column of rule 7 and pipelines.md §7.1
  are corrected from the units' reports; the second size pass, the glossary and the briefs follow.
