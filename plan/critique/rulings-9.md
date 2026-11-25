# Rulings 9: what the first application of rulings 7 and 8 left open

The first half of the application (R35's steps 1 and 2, with the structure of the split and merged pages and the
seed) is in the plan's files. Its appliers and reviewers reported what they could not settle. This file settles it.
Where it differs from an earlier file, this file wins. The planner made the small edits it names in the same commit;
the rest goes to the units through their packets (R43), or to the builders of the tools and the site (R42).

## R39 — The engine's four checks do not block a brief

R34 said two things about the four checks that the engine's agents run (`PrefabSync` with cells; the pending window
of mesh colliders; mouse units on a scaled display; script breakpoints on Linux and macOS): that a page with a
"Check:" item gets no brief until the result has replaced the item, and that until a result is in such a page states
only what the code at the pin shows and says that it was read, not run. Both cannot hold. Those checks are engine
work after 0.8.0, and pages of the first writing waves hold them. What holds:

- The photographer's four captures, and the reading of miniaudio's source for `audio/engine`, block the brief of the
  pages that hold them. They are cheap, and they need only the pin's programs or the pin's sources.
- The engine's four checks block nothing. Their items stay in the allocation, of type `open`, labelled "Check:". The
  page is briefed and written from the code at the pin, and it says in one sentence that the claim was read, not
  run. Its brief names the item, so the writer knows which sentence that is.
- When a result is in, the planner replaces the item with it, and the page is corrected: before the page is written
  through its brief, afterwards as a fix through review. A result that the pin's code contradicts is an erratum of
  the page and is treated as one.
- `check_allocation.py checks` lists both kinds. The table of `allocation/README.md` says which checks do not block.

## R40 — Small points, settled

| Point | What holds |
| --- | --- |
| The seed's `use` | A use home is a page of part `make` (book.md, "One home per concept", rule 2). `check_seed.py` now refuses a `use` elsewhere. The pages of `start` that start-q5 proposes as use homes are homes or links, never use homes. |
| The warning on a concept homed on a how-to | The parts `start` and `make` are exempt, as rule D names both. The eleven warnings on `start` are gone; the three that remain are judged by their units. |
| R36's last sentence of its fourth bullet | It is about the item: a new item on a page of kind R that is a list of facts is typed `feature`, not `concept`. It says nothing about retyping a page. |
| D39, the end state of a how-to | The reviewer's sentence stands: a how-to of block A of `make` that changes Coin Run ends in `## Result` with a download of its end state. `make/project-files` changes nothing in Coin Run and has none. The sentence about block B stands only in book.md. |
| D7, Python beside C++ | The sentence that says what differs from C++ stands in the paragraph that introduces the page's first Python fence. "Line by line" is a matter for the reviewer of the page; the lint checks only that the fence has its introduction. |
| D30, the count of terms | The plan says "about 1,590 terms" until the glossary step has counted them. No file states an exact count before that. |
| D1, git | The seed's seven git words are homed on `basics/git`. book.md's row with "`basics/tools`; git `basics/git`" and track B's wording stand. style.md's workbench list now gives git to `basics/git`. |
| D32, two meanings | style.md §3, pipelines.md §9 and process.md say that the unqualified word is never a term of its own. |
| `basics/math-bases` | book.md's one-home table has its row. |
| `basics/git`'s From cell | It gives the split's reason: track G's side step and track B's reading before `make/first-script` need no git. |
| The table of errata | A row stays when it is true at the pin, whoever proposed it: an erratum costs a writer one line of reading. The row about `AGENTS.md:204-206` is removed: the document is right and the code breaks it, which is a finding of pipelines.md §11, not an erratum. The row about "151 commands" stays. The table holds 29 rows of kind `engine` and 14 of kind `inventory`. |
| The structure of the split and merged pages | Accepted on the appliers' proofs (no item lost, none homed twice, the order of sections as the outline's) and on the planner's run of the checks. The practices the appliers designed (`new:120`, `new:205` to `new:209`) stand as drafts that the briefs may change. `render-scene:373`'s take joined the home row of `draw/gpu-driven`; the forward sentence about sun casters stands after the buckets sentence. |
| Sizes that the structure step reports | `basics/tools` (about 4,350 words against M) and `basics/math-bases` (about 4,400 against M) are for the second size pass, which takes each to L by S2 unless its unit's new estimate says otherwise. |

## R41 — Forms that the tools need (D38)

| Question | Form |
| --- | --- |
| A tutorial that starts from an exercise's solution | `startsFrom` takes `{"tutorial": "<page id>", "exercise": <n>}`: the runner replays that tutorial and then applies its `exercise-<n>.patch`. `scripting/tutorial-host-function` starts from `gpu/debug-drawing`'s exercise this way, and `gpu/debug-drawing`'s tutorial file starts from `world/tutorial-component`. `tutorials.py check` fails when the exercise has no solution patch. |
| `patch.pictures` and `patch.experiment` | They stand as pipelines.md §6.6 has them. |
| `perf.<name>.Measured` for a budget without a measurement | The key exists only where `Budgets.json` gives the value. A page that names a key that does not exist fails `reference.py check`; the page states the budget and says that it is provisional. |
| A figure of another chapter | `::figure{id=… from=<part>/<chapter>}` shows a picture of that chapter's recipes. It is captured once, by the chapter that owns the recipe. |
| Who runs `reference.py render` after pages change | The integrator, per batch, before the build: the tables of terms and of further reading are built from the pages. CI's `reference.py check` fails when the committed tables are stale. |
| `pages.py check` and `use` | It checks `use` as it checks `home`: the page exists, and it is a page of part `make`. |
| The rows of `tools/data/game-makers.json` | The brief of part `reference` lists them. The writer of `reference/game-makers` writes the file in phase B. |

## R42 — What goes to the builders of the tools and the site

The fixer of the site and tools reads this list with rulings 6 to 8:

- `tools/data/cpp-features.json` still homes pointers on `basics/cpp-memory` with a pattern that the outline's new
  pages do not fit, and `std::optional` on `basics/cpp-modern` with a pattern that also matches `std::nullopt` (D24).
- R41's forms: `startsFrom` with `exercise`, `::figure` with `from`, `pages.py check` on `use`, the missing `perf`
  keys.
- site.md's download of a how-to's end state is drawn from the page's tutorial file (R40, D39).
- `check_seed.py` has no tests. When the seed moves to `src/content/glossary.json`, its rules move into
  `tools/pages.py check` with tests, and `check_seed.py` goes.

## R43 — What the units apply with their packets

The packets of the units carry these points beside the findings, answers and rulings of their unit. Each is applied
by the unit whose file it names.

**"What Strata does not do" and rule 7.** Rule 7 of book.md stands as cut: an entry whose subsystem has a `make`
page names that page too. The units of `make` report, for every entry of the table, whether one of their pages
states it; the planner then corrects the table's column. Older rows that break the rule today (BC6H and EXR, disk
area lights, mesh streaming) are corrected the same way. A `make` page that the table names needs a `not-done` item
from its unit. Entries on pages marked W8 or W8r go into the lists of phase B.

**Rows that the first application left.**

- `light.md`: delete the row "GPU-driven culling of casters → `draw/gpu-driven`" from `light/sun-shadows-1`'s Leaves
  out, and add the casters section of about 450 words that D3 gives the page.
- `basics-a.md`: `new:188` becomes a `use` row and `new:108` on `basics/data-structures` keeps the home of hash
  functions (D30); `basics/numbers` drops the geometric series (`new:96`) and links (R31, D7); the stale teacher cells
  outside the six sections (cpp-generic's Assumes "trees" and Leaves out, programming-2's Leaves out); the file's
  "Questions for the planner", which still proposes what was decided.
- `basics-b.md`: the Assumes rows of `basics/math-rotations` (the transpose) and `basics/math-sphere` that now belong
  to `basics/math-bases`; the checkpoints of the other nine primers move to Starting state (R38); the file's
  "Questions for the planner".
- Teacher cells in other units' files that name an old page: the lists are
  `G:/GameEngineAI/.worktrees/docs-work/C/basics-a/teacher-cells.tsv` and `…/C/basics-b/teacher-cells.tsv`. Among
  them: git given to `basics/tools` (core.md, capstone.md, engineering.md, assets.md, editor-ui.md, scripting.md,
  appendix.md, make-a.md), `draw/mirrors-camera-relative`'s row that mixes the determinant with transforms,
  `animation/skinning`'s cofactor, `appendix/math-cheatsheet`'s missing group for `basics/math-bases`, and the Leaves
  out of `core/math` and `world/scene-graph` that send decomposing a matrix to `basics/math-matrices` alone.
- Four rows with teacher `?` that are settled: regular expressions (editor-ui.md, two rows of engineering.md) are
  taught by `basics/data-formats`; git worktrees (engineering.md) by `basics/git`.
- `make-a.md`: `make/project-files` is on tracks G and B and leaves git to a page that track G does not read. The
  page says what its reader needs in a sentence and links `basics/git` as a side step.
- Rows that still name `draw/visibility-feedback` (draw.md, animation.md, assets.md) name `draw/gpu-driven`.
- Rows that still give XL as "8,000 or more" (world.md, make-c.md) follow R37's ranges.
- Section titles that differ from the outline's (basics-a.md, editor.md, automation.md) take the outline's.
- `start.md`: `start/coming-from`'s Assumes row with teacher `?` (D10).
- `indirect.md`: the `:::why` about GI near line 917; `gpu.md`: the terms about the validation layer that still stand
  on `gpu/debugging`.
- `reference.md`: "about 400 entries" near line 1246 becomes the plan's wording (R40); "asset settings sections",
  which pipelines.md §7.1 names, do not exist at the pin: the unit says what the pin has, and the planner corrects
  §7.1 from its report.
- Glossary homes for step 5, recorded now: decomposition and the cofactor matrix are taught from zero on
  `basics/math-bases`, so by R28 that page is their home, and `world/scene-graph` and
  `draw/mirrors-camera-relative` hold use rows.
- The three concepts homed on pages of kind R (`appendix.md`: `new:140`, `new:141`, `new:146`) are judged by R36's
  test.
- critic-book-22's Outcome: probe relocation is at the pin (`Docs/DeveloperGuide.md:5090`), so the finding is
  applied with that correction, not as proposed.
- process.md's item 6 of a brief names track G alone. It stays: a step that only a command can do matters where the
  reader has no terminal habit. Pages of other tracks state such steps as any other step.

**Seed.** Seventeen entries are used on their own home page before the sentence that defines them. They stand until
the glossary step, which orders a page's terms with its brief.
