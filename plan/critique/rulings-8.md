# Rulings 8: four points of rulings 7, made exact

Preparing the application of rulings 7 showed four places where its words would be applied wrongly, or in two ways.
This file says what holds there. Where it differs from rulings 7 or from an earlier file, this file wins. Everything
else of rulings 7 stands, and R35's order stands.

## R36 — What a page of kind R may be the home of

Rulings 7 (R31, the row of D26) said that no item is homed on a page of kind R. That is too wide. Forty home rows
stand on pages of kind R today, and most of them belong there: a small helper that only the reference lists
(`Base64`, `Prefetch`), the fields of the renderer's statistics, the releases and their dates on `appendix/history`,
the credits. R32 itself (the row of D18) puts new items on `appendix/credits`. What holds:

- An item is homed where the book states it in full. A page of kind R explains nothing: it lists facts. So it is the
  home only of **catalogue items**: facts to look up that no teaching page explains further. A helper's declaration,
  a field of the statistics, the slot of a binding, a release and its date, a credit, and an erratum about a number
  that the page's table states right are catalogue items.
- The test: when a reader needs more than the row of a table to use the thing or to understand it, a teaching page is
  its home, and the page of kind R holds a `link` row. Every item of type `concept` fails the test. So do the
  fourteen SDK classes of critic-scripting-4, which move as rulings 7 says.
- The four pages of kind R in `appendix` are written by hand. The rule is the same for them.
- `check_allocation.py` warns on an item of type `concept` homed on a page of kind R. A warning does not fail the
  check. A new item of type `concept` on such a page that is a list of facts takes the type `feature`.
- The units `reference` and `appendix` judge every home row on their pages of kind R by the test, and move what
  fails it to the teaching page, with the teaching page's unit (a cross-unit move, R31).

## R37 — The Fit line under rule S

R28 gave the ranges and S5, and did not say what the three states of a Fit line mean under them. Rule 6 of
`allocation/README.md` measured them against the budget. From now on they are measured against the range of the
page's size:

| State | The estimate | The line says |
| --- | --- | --- |
| `fits` | inside the range and below its top | what takes the most words, in one or two sentences |
| `over` | at or over the top of the range | the next size, or the split with the titles of the pages (S2, S3, S5) |
| `under` | below the bottom of the range | what the page could take from a neighbour; on a page marked W8 or W8r, what phase B adds; or the smaller size (S2) |

The tops are 2,250 (S), 4,000 (M), 6,500 (L) and 10,000 (XL); the bottoms are 600, 2,251, 4,001 and 6,501. The
form of the line stays: the state, "about N words against <size> (<the size's budget>)", then the sentences.

- A page of kind R has no size check (R33, the row of D22). Its state is always `fits`, its number is the prose it
  holds, and its sentence states the generated volume that gives the page its size. The check compares nothing for
  it, and `coverage.md` never lists it among the pages over or under.
- An estimate that equals the size's budget to the word gets a warning from the check: it is counted again from the
  page's sections (S5).
- `check_allocation.py` enforces the table, with tests. `coverage.md` lists the pages `over` and `under`: that list is
  what the second size pass reads (R30).
- The outline's sizes change in step 2 of R35's order, and the Fit lines follow in step 5, when every unit estimates
  again. Between the two steps `check_allocation.py check` reports Fit lines whose size or state no longer matches.
  The sections that step 2 writes or merges (the splits' pages, `draw/gpu-driven`) have Fit lines that pass at once.

## R38 — Three sentences of rulings 7, said exactly

- **Starting state on primers** (R33, the row of D21). The primers' units move every checkpoint that stands in a
  primer's Covers into the primer's Starting state. Covers keeps what the page teaches.
- **The seed's three words** (R33, the row of D29). The seed already holds `log`, `build` and `debug information`.
  They get the definitions and the homes that "For the planner" 1 to 3 of `proposals/questions-learner.md` recommend:
  `log` on `start/install`, `build` on `start/first-game`, `debug information` on `basics/debugging`. No entry is
  added, and the seed keeps 400 entries. Of the nine definitions that R33 corrects (the row of D34), those that are
  entries of the seed are corrected in the seed; the others are terms of the inventories, and their units correct
  the rows that hold them.
- **The units of `basics`** (R35, step 2). With the splits' pages, `basics-a` holds `basics/computer` to
  `basics/data-formats`, and `basics/threads`; `basics-b` holds `basics/math-vectors` to `basics/math-sphere`. So
  `basics-a` writes the sections of `basics/git`, `basics/trees-graphs` and `basics/data-formats`, and `basics-b` the
  section of `basics/math-bases`.
