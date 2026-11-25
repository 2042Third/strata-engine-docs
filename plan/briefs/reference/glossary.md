# Brief: `reference/glossary`

| Field | Value |
| --- | --- |
| Title | Glossary |
| Kind | R |
| Size | XL |
| Tracks | - |
| Needs | - |
| From | all inventories' glossaries (about 1,590 terms before merging); one definition list, without a table of contents |
| Unit | `plan/allocation/reference.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `reference/glossary` — Glossary

**Covers.** The paragraph on top says what the page is and how to read an entry: every term of the book in one
definition list, in alphabetical order and without a table of contents (`../site.md`, "Glossary"), drawn by
`::glossary` from `src/content/glossary.json`. Each entry gives the term, its one-sentence definition, its home page
(the page that teaches it) and, where there is one, its use home in `make`, and its other accepted names. The list
holds the seed of 400 entries of a beginner's vocabulary (homes in `start` and `basics`), the inventories' terms
(about 1,590 until the glossary step counts them) with the homes the allocation gave them, and the new terms the
writers' notes admit (`../pipelines.md` §9). A word with two meanings has two entries, each qualified by a word ("pack
block" and "BC block"; "prefetch", "block", "journal", "snapshot", "hot reload" and "batch", `../book.md`, one-home rule
6), never one entry with two definitions; and an inventory entry that defines several terms is split into one entry per
term at the merge. Pages link entries with `:term[text]{id=…}`; a reader who arrives from a popover lands on the entry.
Hand-written: only the paragraph on top, the note on qualified entries and `## Where it lives in Strata`, which names
the glossary file of the book and, for engine terms, the homes' "Where it lives" sections. The tools are
`tools/pages.py check` and `tools/lint.py` (homes that exist, no duplicate term or alias, every home defines its term).

**Leaves out.**

- A beginner's vocabulary taught from zero, which the seed's entries link → `basics/computer`
- The index of engine identifiers and the pages that quote them → `reference/term-index`
- The symbols of mathematics → `appendix/math-cheatsheet`

**Fit.** `fits`: about 450 words against XL (8,000). The entries give the page its size: about 2,000 after the merge
(the seed's 400 and the inventories' terms), roughly 50,000 words drawn from the glossary file; the spike measured 1,600
terms at 116 KB gzipped (`../spike-report-1.md`), so they stay within the largest-page budget of `../site.md` (row 10,
300 KB) and no split is needed. The prose is the paragraph on top and the note on qualified entries.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `animation:527-589` | term | link | The 63 entries of the animation glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `assets:637-737` | term | link | The 101 entries of the assets glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `audio-input:606-693` | term | link | The 87 entries of the audio-input glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `automation:703-786` | term | link | The 81 entries of the automation glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `build-test:609-698` | term | link | The 84 entries of the build-test glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `editor-core:648-740` | term | link | The 93 entries of the editor-core glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `editor-ui:700-794` | term | link | The 88 entries of the editor-ui glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `foundation:548-645` | term | link | The 94 entries of the foundation glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `gamedev:569-665` | term | link | The 97 entries of the gamedev glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `gameui:617-685` | term | link | The 69 entries of the gameui glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `physics:477-541` | term | link | The 65 entries of the physics glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `render-core:679-775` | term | link | The 89 entries of the render-core glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `render-direct:671-758` | term | link | The 88 entries of the render-direct glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `render-image:634-736` | term | link | The 101 entries of the render-image glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `render-indirect:564-650` | term | link | The 87 entries of the render-indirect glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `render-scene:569-654` | term | link | The 86 entries of the render-scene glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `scene-ecs:611-693` | term | link | The 80 entries of the scene-ecs glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `scripting:557-621` | term | link | The 58 entries of the scripting glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `worlds-runtime:513-568` | term | link | The 56 entries of the worlds-runtime glossary, merged into the one list; an entry that defines several terms becomes one entry per term |

**Assumes.**

none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.
