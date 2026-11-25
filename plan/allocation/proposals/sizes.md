# Proposals: sizes

Written by the agent `sizes` of workflow B, step 4 of `../README.md` ("Order of the work"). It applies the planner's
rule S to every page and tries the result on a copy of the outline. Sources: `../coverage.md` §7 (the Fit lines),
`G:/GameEngineAI/.worktrees/docs-work/B/prep/pages.tsv` (the same estimates as a table; its README says it matches
coverage.md), the units' files and `prep/questions/`. Scripts and their outputs: `G:/GameEngineAI/.worktrees/docs-work/B/sizes/`.
The trial outline: `G:/GameEngineAI/.worktrees/docs-work/B/outline/plan/`, its edits in
`G:/GameEngineAI/.worktrees/docs-work/B/outline/CHANGES.md`.

## Summary

Rule S, applied to the 332 pages with each page's estimate from its Fit line, and the linter's ranges (S 600 to 2,250;
M 2,251 to 4,000; L 4,001 to 6,500; XL 6,501 to 10,000):

| Verdict | Pages | Which |
| --- | --- | --- |
| keep | 250 | S1: the estimate is inside the range of the page's size. 86 of them are `over` in coverage.md and 1 is `under` (`draw/occlusion`, 4,100 against L) |
| larger | 51 | S2: one class up; 40 from M to L, 10 from L to XL, 1 from S to M |
| smaller | 2 | S2: `draw/gpu-driven` XL to L, `worlds/export` L to M. Neither is marked W8 or W8r |
| split | 3 | S3: `basics/data-structures`, `basics/bytes`, `basics/math-matrices`. Each is a primer, which is at most L, with an estimate in XL's range |
| move-items | 0 | No split breaks a track's rule, so S3 needed no move of items |
| left out | 26 | Kind R: the 22 pages of `reference` and 4 of `appendix` (`math-cheatsheet` 2,800, `history` 2,850, `further-reading` 2,900, `credits` 1,400). These four are mostly tables written by hand; each estimate, tables included, is inside its own size's range, so S1 would keep them too (For the planner, item 7) |

Before and after, from `check_outline.py --counts --words --waves` on the plan and on the trial:

| Count | Before | After |
| --- | --- | --- |
| Pages | 332 | 335 |
| Pages per part | `basics` 26, every other part as now | `basics` 29; no other part changes |
| Pages per size | S 9, M 161, L 144, XL 18 | S 8, M 124, L 176, XL 27 |
| Pages per kind | P 26, C 45, I 177, T 34, H 24, R 26 | P 29; the others unchanged |
| Pages per track | G 52 and 2 side steps, B 49, E 261, on no track 29 | G 52 and 2 side steps, B 52, E 264, on no track 29 |
| Words at the budgets (S 1,500, M 3,000, L 5,000, XL 8,000) | 1,360,500 | 1,480,000 |
| Words per track | G 205,000, B 186,000, E 1,071,500 | G 212,500, B 224,500, E 1,187,000 |
| Pages per wave | 1: 59, 2: 33, 3: 32, 4: 68, 5: 64, 6: 40, B: 36 | 1: 62; the others unchanged |
| Words per wave | 1: 237,000, 2: 130,000, 3: 130,000, 4: 281,500, 5: 261,000, 6: 170,000, B: 151,000 | 1: 290,500, 2: 137,000, 3: 144,000, 4: 284,500, 5: 274,000, 6: 197,000, B: 153,000 |
| The allocators' estimates, all pages | 1,448,300 | about 1,451,200 (the halves of the three splits add about 2,900) |
| The estimates without kind R, against the budgets without kind R | 1,404,050 against 1,254,500 | about 1,406,950 against 1,374,000 |

Words per part at the budgets, where they change: `start` 17,000 to 20,500; `make` 170,000 to 172,000; `basics` 104,000
to 139,000; `core` 62,000 to 72,000; `world` 54,000 to 59,000; `gpu` 62,000 to 69,000; `assets` 53,000 to 65,000;
`draw` 55,500 to 52,500; `image` 60,000 to 62,000; `indirect` 45,000 to 48,000; `physics` 44,500 to 46,500; `input`
26,000 to 28,000; `ui` 24,000 to 30,000; `editor` 74,000 to 78,000; `editor-ui` 74,000 to 88,000; `automation` 29,000
to 34,000; `engineering` 52,000 to 60,000; `appendix` 23,500 to 25,500. `light`, `animation`, `audio`, `scripting`,
`worlds`, `capstone` and `reference` are unchanged.

The check: on the trial, `python -B check_outline.py --counts --words --waves` exits 0 and prints no problem line. The
trial needed, beside the sizes and the three new rows: 13 Needs of rows, 9 "Needs of the part" lines, the lists of
tracks B and E, every count of `book.md`, `process.md` and `README.md` that the check compares, and 4 one-home rows of
`book.md`. Track G's list and `check_outline.py` are unchanged. The trial also holds copies of `process.md` and `README.md`,
which the check reads beside itself. A second check (`sizes/closure_check.py`, the closure of `check_allocation.py`):
all 130 Assumes rows that name a split page keep their "in closure" answer: the plan's answer for the old teacher
equals the trial's for the teacher the concept moves to. 65 of them get a new teacher (41 `basics/data-formats`, 17
`basics/trees-graphs`, 7 `basics/math-bases`). No other Assumes row changes its answer (`sizes/closure_count.py`).

## Changes

| Page | Size now | Estimate | Verdict | Proposal | Tracks and order | Why |
| --- | --- | --- | --- | --- | --- | --- |
| `start/how-to-read` | S | 2,400 | larger | S to M | G, E, B; order unchanged | S2: 2,400 is inside M's range (2,251 to 4,000) |
| `start/first-game` | M | 4,400 | larger | M to L | G, E, B; order unchanged | S2: 4,400 is inside L's range (4,001 to 6,500) |
| `make/reflections` | M | 4,300 | larger | M to L | G; order unchanged | S2: 4,300 is inside L's range (4,001 to 6,500); the split its Fit line offers is not needed |
| `basics/tools` | M | 6,200 | larger | M to L | B, E; order unchanged | S2: 6,200 is inside L's range (4,001 to 6,500); the split its Fit line offers is not needed; I recommend the split instead (For the planner) |
| `basics/debugging` | M | 4,200 | larger | M to L | G, B, E; order unchanged | S2: 4,200 is inside L's range (4,001 to 6,500) |
| `basics/data-structures` | L | 7,100 | split | split into `basics/data-structures` (L, about 5,000) and `basics/trees-graphs` (M, about 3,000) | B, E; `basics/trees-graphs` directly after `basics/data-structures` in the part and on B and E | About 7,100 is in XL's range, and a primer is at most L (S3). Each half answers one question: what the linear structures cost, and how trees, heaps and graphs search and order |
| `basics/cpp-generic` | M | 4,900 | larger | M to L | B, E; order unchanged | S2: 4,900 is inside L's range (4,001 to 6,500) |
| `basics/cpp-modern` | M | 5,900 | larger | M to L | B, E; order unchanged | S2: 5,900 is inside L's range (4,001 to 6,500); the split its Fit line offers is not needed |
| `basics/bytes` | M | 7,400 | split | split into `basics/bytes` (L, about 4,100) and `basics/data-formats` (L, about 4,100) | B, E; `basics/data-formats` directly after `basics/bytes` in the part and on B and E | About 7,400 is two classes up, in XL's range, and a primer is at most L (S3). The halves: bytes and text encodings; formats, hashes and identifiers |
| `basics/math-matrices` | L | 7,200 | split | split into `basics/math-matrices` (L, about 4,900) and `basics/math-bases` (M, about 3,500) | B, E; `basics/math-bases` directly after `basics/math-matrices` in the part and on B and E | About 7,200 is in XL's range, and a primer is at most L (S3). The halves: transforms and spaces; bases, determinants and normals |
| `basics/math-projection` | M | 4,900 | larger | M to L | B, E; order unchanged | S2: 4,900 is inside L's range (4,001 to 6,500) |
| `basics/math-geometry` | M | 5,800 | larger | M to L | B, E; order unchanged | S2: 5,800 is inside L's range (4,001 to 6,500); the split its Fit line offers is not needed |
| `basics/math-interpolation` | M | 5,400 | larger | M to L | B, E; order unchanged | S2: 5,400 is inside L's range (4,001 to 6,500); the split its Fit line offers is not needed |
| `basics/color` | M | 5,700 | larger | M to L | B, E; order unchanged | S2: 5,700 is inside L's range (4,001 to 6,500); the split its Fit line offers is not needed |
| `basics/signals` | M | 5,100 | larger | M to L | B, E; order unchanged | S2: 5,100 is inside L's range (4,001 to 6,500) |
| `basics/math-probability` | M | 6,200 | larger | M to L | B, E; order unchanged | S2: 6,200 is inside L's range (4,001 to 6,500); the split its Fit line offers is not needed |
| `basics/math-sphere` | M | 5,200 | larger | M to L | B, E; order unchanged | S2: 5,200 is inside L's range (4,001 to 6,500) |
| `core/conventions` | M | 4,500 | larger | M to L | E; order unchanged | S2: 4,500 is inside L's range (4,001 to 6,500) |
| `core/windows-events` | M | 4,100 | larger | M to L | E; order unchanged | S2: 4,100 is inside L's range (4,001 to 6,500); the split its Fit line offers is not needed |
| `core/engine-modules` | M | 4,900 | larger | M to L | E; order unchanged | S2: 4,900 is inside L's range (4,001 to 6,500) |
| `core/files` | M | 4,250 | larger | M to L | E; order unchanged | S2: 4,250 is inside L's range (4,001 to 6,500) |
| `core/profiling` | M | 4,300 | larger | M to L | E; order unchanged | S2: 4,300 is inside L's range (4,001 to 6,500) |
| `world/reflection` | L | 7,000 | larger | L to XL | E; order unchanged | S2: 7,000 is inside XL's range (6,501 to 10,000); the split its Fit line offers is not needed |
| `world/projects-settings` | M | 5,000 | larger | M to L | E; order unchanged | S2: 5,000 is inside L's range (4,001 to 6,500) |
| `gpu/vulkan-nvrhi` | L | 6,700 | larger | L to XL | E; order unchanged | S2: 6,700 is inside XL's range (6,501 to 10,000); the split its Fit line offers is not needed |
| `gpu/resources-lifetimes` | M | 4,400 | larger | M to L | E; order unchanged | S2: 4,400 is inside L's range (4,001 to 6,500); the split its Fit line offers is not needed |
| `gpu/readback-timing` | M | 4,300 | larger | M to L | E; order unchanged | S2: 4,300 is inside L's range (4,001 to 6,500); the split its Fit line offers is not needed |
| `assets/loading` | L | 7,300 | larger | L to XL | E; order unchanged | S2: 7,300 is inside XL's range (6,501 to 10,000); the split its Fit line offers is not needed |
| `assets/residency` | L | 7,200 | larger | L to XL | E; order unchanged | S2: 7,200 is inside XL's range (6,501 to 10,000); the split its Fit line offers is not needed |
| `assets/references` | M | 5,400 | larger | M to L | E; order unchanged | S2: 5,400 is inside L's range (4,001 to 6,500) |
| `assets/uploads` | M | 4,700 | larger | M to L | E; order unchanged | S2: 4,700 is inside L's range (4,001 to 6,500) |
| `assets/robustness` | M | 4,500 | larger | M to L | E; order unchanged | S2: 4,500 is inside L's range (4,001 to 6,500) |
| `draw/gpu-driven` | XL | 6,300 | smaller | XL to L | E; order unchanged | S2: 6,300 is inside L's range (4,001 to 6,500); below XL's floor of 6,501, so XL would fail `size`; the merge with `draw/visibility-feedback` is the other way (For the planner) |
| `image/encoding` | M | 4,100 | larger | M to L | E; order unchanged | S2: 4,100 is inside L's range (4,001 to 6,500) |
| `indirect/probes` | L | 7,400 | larger | L to XL | E; order unchanged | S2: 7,400 is inside XL's range (6,501 to 10,000); the split its Fit line offers is not needed |
| `physics/contacts-triggers` | M | 4,100 | larger | M to L | E; order unchanged | S2: 4,100 is inside L's range (4,001 to 6,500) |
| `input/devices-state` | M | 4,700 | larger | M to L | E; order unchanged | S2: 4,700 is inside L's range (4,001 to 6,500) |
| `ui/drawing` | L | 7,400 | larger | L to XL | E; order unchanged | S2: 7,400 is inside XL's range (6,501 to 10,000); the split its Fit line offers is not needed |
| `ui/input` | L | 7,100 | larger | L to XL | E; order unchanged | S2: 7,100 is inside XL's range (6,501 to 10,000); the split its Fit line offers is not needed |
| `worlds/physics-scripts` | M | 5,000 | larger | M to L | E; order unchanged | S2: 5,000 is inside L's range (4,001 to 6,500); the split its Fit line offers is not needed |
| `worlds/export` | L | 3,800 | smaller | L to M | E; order unchanged | S2: 3,800 is inside M's range (2,251 to 4,000); below L's floor of 4,001; taking items from `worlds/game-identity` is the other way (For the planner) |
| `editor/projects` | M | 4,800 | larger | M to L | E; order unchanged | S2: 4,800 is inside L's range (4,001 to 6,500) |
| `editor/script-builds` | M | 6,500 | larger | M to L | E; order unchanged | S2: 6,500 is inside L's range (4,001 to 6,500); the split its Fit line offers is not needed |
| `editor-ui/shell` | L | 7,600 | larger | L to XL | E; order unchanged | S2: 7,600 is inside XL's range (6,501 to 10,000); the split its Fit line offers is not needed |
| `editor-ui/inspectors` | L | 6,600 | larger | L to XL | E; order unchanged | S2: 6,600 is inside XL's range (6,501 to 10,000); the split its Fit line offers is not needed |
| `editor-ui/status` | M | 5,500 | larger | M to L | E; order unchanged | S2: 5,500 is inside L's range (4,001 to 6,500) |
| `editor-ui/launcher-dialogs` | M | 4,800 | larger | M to L | E; order unchanged | S2: 4,800 is inside L's range (4,001 to 6,500) |
| `editor-ui/settings-windows` | M | 4,800 | larger | M to L | E; order unchanged | S2: 4,800 is inside L's range (4,001 to 6,500) |
| `editor-ui/instrument-panels` | M | 5,200 | larger | M to L | E; order unchanged | S2: 5,200 is inside L's range (4,001 to 6,500) |
| `automation/security` | L | 7,200 | larger | L to XL | E; order unchanged | S2: 7,200 is inside XL's range (6,501 to 10,000); the split its Fit line offers is not needed |
| `automation/sessions` | M | 4,400 | larger | M to L | E; order unchanged | S2: 4,400 is inside L's range (4,001 to 6,500) |
| `engineering/flags-portability` | M | 5,300 | larger | M to L | E; order unchanged | S2: 5,300 is inside L's range (4,001 to 6,500); the split its Fit line offers is not needed |
| `engineering/third-party` | M | 4,700 | larger | M to L | E; order unchanged | S2: 4,700 is inside L's range (4,001 to 6,500) |
| `engineering/generated-code` | M | 4,500 | larger | M to L | E; order unchanged | S2: 4,500 is inside L's range (4,001 to 6,500) |
| `engineering/ci` | M | 4,100 | larger | M to L | E; order unchanged | S2: 4,100 is inside L's range (4,001 to 6,500) |
| `appendix/game-ai` | M | 4,400 | larger | M to L | no track; order unchanged | S2: 4,400 is inside L's range (4,001 to 6,500) |

## Splits in detail

Each new page is a primer. Tracks.md asks two things of every primer, which the allocators' Fit lines do not count for
the new halves: a Test out box at the top, and, after `basics/debugging`, an optional practice item on the reader's Coin
Run project. The estimates below include the fixed parts. The `basics` index page names, for each primer, the first
part that needs it; it is generated, so the new primers enter it by themselves.

### `basics/data-structures` into two primers

The rows in the trial outline (`outline-1.md`, part `basics`):

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `basics/data-structures` | Data structures I: arrays, lists, hash maps and their cost | P | L | B, E | `basics/programming-2`, `basics/numbers` | new; arrays, linked lists, stacks, queues and ring buffers, hash maps and their cost (big-O, with the logarithms of `basics/numbers`); binary search, swap-remove and free lists, prefix sums; arrays of structs against structs of arrays; the engine's cases: sparse sets (scene-ecs concept 4; code 4, 5, 13) and hash buckets, job queues; trees, heaps, graphs and sorting are `basics/trees-graphs`' |
| `basics/trees-graphs` | Data structures II: trees, heaps, graphs and sorting | P | M | B, E | `basics/data-structures` | new by split of `basics/data-structures`, which could not hold both lessons at a primer's size; trees and ordered maps whose nodes stay put, depth-first and breadth-first walks, binary heaps as priority queues, spatial trees as halving the space to search, graphs (directed graphs, dependency graphs, walks, cycles; their topological sort is `core/engine-modules`', foundation concept 10), union-find, sorting and radix sort; the engine's cases: dependency graphs, spatial trees, reference graphs, queues of loading work by priority |

Order: `basics/trees-graphs` stands directly after `basics/data-structures` in the part's rows, on track B (entry 32)
and on track E (entry 15). Both pages are on B and E only, as every primer after the programming ones.

Sizes: the Fit line (`basics-a.md:549`) gives about 5,000 and 3,000, and adds the second page's fixed parts (8,000
against 7,100). 5,000 is inside L's range and 3,000 inside M's, so L and M, as the allocator proposed.

What moves (items of `basics-a.md:509-597`):

- Stays on `basics/data-structures`: cost and big-O (`new:101`), arrays (`new:102`), binary search (`new:103`),
  swap-remove and free lists (`new:104`), linked lists (`new:105`), stacks (`new:106`), queues and ring buffers
  (`new:107`), hash maps and sets (`new:108`), prefix sums (`new:109`), arrays of structs and structs of arrays
  (`new:110`), sparse sets (`new:111`), the practice item (`new:118`), the terms `foundation:614` and
  `render-scene:571`, and the use rows `scene-ecs:284`, `scene-ecs:376`, `scene-ecs:385`.
- Moves to `basics/trees-graphs`: trees and ordered maps with their walks (`new:112`), binary heaps (`new:113`),
  spatial trees (`new:114`), graphs (`new:115`), union-find (`new:116`), sorting and radix sort (`new:117`), the use
  row `foundation:332` (radix sort), the link rows `foundation:256`, `assets:297`, `assets:318`, and the Leaves out
  entries for topological sort, reference graphs, bounding volume trees and A*. It needs a practice item of its own;
  the allocation names none.
- Glossary seed (`../../glossary/seed.json`): tree, directed graph and dependency graph move to `basics/trees-graphs`
  (as `basics-a-q12` proposes).

Needs elsewhere (rows that name `basics/data-structures`):

| Page | Its Needs now | In the trial | Why |
| --- | --- | --- | --- |
| `basics/cpp-generic` | `basics/cpp-classes`, `basics/data-structures` | `basics/cpp-classes`, `basics/trees-graphs` | Its must row "Arrays, hash maps, trees and what they cost" uses trees (`std::map`) |
| `core/engine-modules` | `core/frame-loop`, `basics/data-structures` | `core/frame-loop`, `basics/trees-graphs` | "Graphs and dependency graphs" (must) |
| `assets/residency` | `assets/loading`, `gpu/resources-lifetimes`, `basics/data-structures` | the same with `basics/trees-graphs` | "Trees and maps" (must) |
| `physics/collision-detection` | `physics/bodies-colliders`, `basics/math-geometry`, `basics/data-structures` | the same with `basics/trees-graphs` | "Trees, their costs and big-O" (must) |
| `appendix/game-ai` | `basics/data-structures`, `basics/math-geometry` | `basics/trees-graphs`, `basics/math-geometry` | "Graphs, queues and a priority queue" (must) |
| `world/what-a-world-is` | keeps `basics/data-structures` | unchanged | "Arrays, hash maps and what operations cost" (helps) is the first half's |

"Needs of the part" lines: `core`, `assets`, `physics` and `appendix` name `basics/trees-graphs` in place of
`basics/data-structures`; `world` keeps `basics/data-structures`. Since `trees-graphs` needs `data-structures`, no
closure loses a page.

Assumes rows whose teacher becomes `basics/trees-graphs` (all inside their closure in the trial): `basics/cpp-generic`,
`core/engine-modules`, `core/jobs` (priority queues), `world/scene-graph` (trees), `world/systems`, `assets/loading`,
`assets/residency`, `assets/references`, `draw/batching` (sorting), `light/many-lights` (sorting), `light/local-shadows`,
`physics/collision-detection`, `physics/building-bodies` (ordered maps), `ui/layout`, `worlds/streamer` (sorting),
`engineering/cmake` (graphs), `appendix/game-ai`. Where a row names both halves ("Linked lists, trees and hash maps"),
it names `basics/trees-graphs`, whose closure holds the first half.

One-home rows of `book.md` (done in the trial): the row "Data structures and what they cost" becomes two rows, and
the row "Topological sort (Kahn)" links `basics/trees-graphs`.

### `basics/bytes` into two primers

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `basics/bytes` | Bytes in files and memory: layouts, byte order and text encodings | P | L | B, E | `basics/numbers`, `basics/tools` | new; foundation concept 23; assets concept 19; build-test excerpt 13; files and numbers as bytes, byte order, binary layouts and lengths that cannot be trusted, structs as bytes (`sizeof`, alignment, `offsetof`, `static_assert`), images as bytes, text encodings (Unicode, UTF-8, UTF-16 and code pages); JSON, Base64, hashes and UUIDs are `basics/data-formats`' |
| `basics/data-formats` | JSON, Base64, hashes and UUIDs | P | L | B, E | `basics/bytes` | new by split of `basics/bytes`, which could not hold both lessons at a primer's size; foundation concept 26; numbers written as text and read back exactly, JSON (objects, arrays, strings, numbers, a format header with a version, reading text into tokens by hand, strict against lenient readers), Base64, stable hashes (FNV-1a in `Hash.h`) against `std::hash`, checksums (CRC-32C), cryptographic hashes (SHA-256; HMAC is `automation/security`'), UUIDs |

Order: `basics/data-formats` directly after `basics/bytes`, before `basics/math-vectors`; track B entry 39, track E
entry 22.

Sizes: the Fit line (`basics-a.md:961`) gives "about 3,700 words" each and asks L for both. Its two halves add up to
the whole page's 7,400, so they do not count the second page's fixed parts; the other two splits add 900 and 1,200
words for them. With about 700 added, each half is about 4,100 words: inside L's range, and above M's top. So L for
both, as the allocator asked, but for this reason. `basics/bytes` itself goes from M to L.

What moves (items of `basics-a.md:922-1015`):

- Stays on `basics/bytes`: files, numbers and images as bytes, byte order, binary layouts and lengths that cannot be
  trusted, structs as bytes (`sizeof`, alignment, `offsetof`, `static_assert`), text, Unicode, ASCII, UTF-8 down to
  continuation bytes and U+FFFD, UTF-16 and code pages; the terms `audio-input:666`, `audio-input:667`,
  `gameui:678`, `foundation:627`; the link rows `foundation:317`, `assets:351`, `build-test:390`. It needs a practice
  item of its own.
- Moves to `basics/data-formats`: numbers written as text and read back, JSON with the Tetris project file (`new:185`),
  reading text into tokens by hand, strict and lenient readers, Base64, FNV-1a (`new:189`), CRC-32C (`new:190`),
  SHA-256 and the link to HMAC, UUIDs (`new:192`), the practice item on Coin Run's `.stproj` (`new:193`), the terms
  `automation:728`, `automation:745`, `foundation:643`, the concept `foundation:332` (its binary layouts and untrusted
  lengths are used by `basics/bytes`), and the link rows `foundation:154`, `foundation:155`, `foundation:156`,
  `scene-ecs:342`. The Assumes row "Hash maps, which use hash functions" (helps) goes with it.
- Elsewhere in `basics-a.md`: `basics/data-structures` leaves "Stable hashes, checksums and cryptographic hashes" to
  `basics/data-formats`; `foundation:332`'s cell names `basics/trees-graphs` for the radix sort.
- Glossary seed: JSON, JSON object, JSON array, checksum, cryptographic hash, Base64 and UUID move to
  `basics/data-formats` (as `basics-a-q12` proposes); file format, endianness, serialization and the text words stay.

Needs elsewhere (rows that name `basics/bytes`):

| Page | Its Needs now | In the trial | Why |
| --- | --- | --- | --- |
| `world/reflection` | `world/ecs`, `basics/cpp-modern`, `basics/bytes`, `core/layers-registries` | `basics/data-formats` in place of `basics/bytes` | "JSON, UTF-8, and numbers written as text" (must) |
| `assets/what-is-an-asset` | `basics/bytes`, `core/layers-registries`, `world/ecs` | `basics/data-formats` in place of `basics/bytes` | "Files, bytes and JSON" (must) |
| `worlds/game-identity` | `worlds/export`, `basics/bytes`, `basics/color`, `assets/robustness` | `basics/data-formats` in place of `basics/bytes` | "JSON; UTF-8, code points and other encodings" (must) |
| `editor/commands` | `world/reflection`, `basics/bytes` | `world/reflection`, `basics/data-formats` | "JSON: objects, arrays, strings, numbers" (must) |
| `automation/json-rpc` | `basics/bytes`, `basics/threads`, `core/platform` | `basics/data-formats` in place of `basics/bytes` | "Bytes, UTF-8 text and JSON" (must) |
| `core/layers-registries` | `core/engine-modules` | `core/engine-modules`, `basics/data-formats` | "JSON" (must): the first page of `core` that must have JSON, so every later part has it in its closure |
| `core/files`, `gpu/text`, `input/devices-state` | keep `basics/bytes` | unchanged | Their rows ask for UTF-8 and text encodings, the first half's |

"Needs of the part" lines: `core` adds `basics/data-formats` and keeps `basics/bytes`; `world`, `assets`, `worlds`,
`editor` and `automation` name `basics/data-formats` in place of `basics/bytes`; `gpu` and `input` keep `basics/bytes`.

Assumes rows whose teacher becomes `basics/data-formats` (all inside their closure in the trial, except the reference
pages, which were outside before): every row about JSON, hashes, checksums, Base64 or UUIDs, 41 rows (6 of them on
reference pages), from
`core/conventions` to `engineering/releasing` (the list: `sizes/closure_check.py`'s output). The two `must` rows of
`reference/commands` and `reference/settings` stay outside, as coverage.md §6 already lists them.

One-home rows of `book.md` (done in the trial): the row "Bytes, text encodings and UTF-8, JSON, hashes, Base64, UUIDs"
becomes two rows; the JSON row keeps the Use column (`start/how-to-read`, `make/automated-playtests`).

### `basics/math-matrices` into two primers

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `basics/math-matrices` | Matrices and transforms: TRS, hierarchies, spaces and conventions | P | L | B, E | `basics/math-vectors` | foundation "The math toolkit" (the mathematics: matrices); translation, rotation and scale, hierarchies, spaces, the inverse; home of axes, handedness, units and matrix order; bases, the determinant and normals are `basics/math-bases`' |
| `basics/math-bases` | Bases, determinants and normals: orthonormal frames, tangent space, mirrors and the inverse transpose | P | M | B, E | `basics/math-matrices` | new by split of `basics/math-matrices`, which could not hold both lessons at a primer's size; foundation "The math toolkit" (the mathematics: bases); the transpose and orthonormal bases (`Motion::LookAt`), changing basis and tangent space (`TangentBasis`), the determinant and its sign as a mirror, normals through the inverse transpose and the cofactor matrix, decomposing a matrix into translation, rotation and scale and when it fails |

Order: `basics/math-bases` directly after `basics/math-matrices`, before `basics/math-projection`; track B entry 42,
track E entry 25.

Sizes: the Fit line (`basics-b.md:123`) gives about 4,900 and 3,500, with the second page's fixed parts (8,400 against
7,200). It proposes L for both; 3,500 is inside M's range and below L's floor of 4,001, so an L page of that length
would fail `size`. So L and M.

What moves (items of `basics-b.md:77-168`):

- Stays on `basics/math-matrices`: ideas 1 to 7 and 13 (`new:11` to `new:17`, `new:23`), the Coin Run item
  (`new:25`), the terms `scene-ecs:628`, `scene-ecs:629`, `foundation:640`, `animation:535`, the use row
  `foundation:139`; the figures of the axes, the two orders, the parent and child and the right hand; the mistakes of
  the reversed order and rows read as columns.
- Moves to `basics/math-bases`: ideas 8 to 12 (`new:18` to `new:22`), the `TangentBasis` excerpt (`new:24`), the use
  row `scripting:136` (`Motion::LookAt`), the figure of the bent normal, the mistakes of normals under a non-uniform
  scale and of inverting a matrix whose determinant is zero, and the Leaves out entry for mirrored instances. It needs
  a Test out box and a practice item of its own.
- Glossary seed: none of the 18 seed words of the page belongs to the second half (basis vector is idea 2).

Needs elsewhere (rows that name `basics/math-matrices`):

| Page | Its Needs now | In the trial | Why |
| --- | --- | --- | --- |
| `basics/math-rotations` | `basics/math-matrices` | `basics/math-bases` | Its must row asks for "the transpose" (idea 8). Through `core`'s "Needs of the part", every page after `core` then has `basics/math-bases` in its closure |
| `light/materials` | `assets/textures`, `basics/math-matrices` | `assets/textures`, `basics/math-bases` | "Bases and changes of space (tangent space)" (must) |
| `basics/math-projection`, `basics/math-geometry` | keep `basics/math-matrices` | unchanged | Inverses, 4×4 matrices and spaces are the first half's |

"Needs of the part": `light` names `basics/math-bases` in place of `basics/math-matrices`.

Assumes rows whose teacher becomes `basics/math-bases`: `basics/math-rotations`, `basics/math-sphere` (helps; outside
its closure before and after), `draw/render-scene` (helps), `draw/mirrors-camera-relative`, `light/materials`,
`light/shadow-basics` (helps), `physics/building-bodies`, and `animation/skinning` for the cofactor, which its row now
gives to `basics/math-vectors` (`basics-b-q5`). All `must` rows are inside their closure in the trial.

One-home rows of `book.md` (done in the trial): a new row for bases, tangent space, the determinant, the inverse
transpose and decomposing, on `basics/math-bases`.

## Estimates I do not believe

The model: least squares over the 306 pages not of kind R, words = c0 + the sum over item types of a weight times the
page's count of home rows of that type. A pure sum without c0 fits badly (R² -0.27; with c0 fixed at the 600 words of
fixed parts of `../README.md`, R² 0.03), so c0 is fitted too. Weights that came out negative (feature, open, not-done)
were dropped and the fit repeated: words = 2,779 + 183 a concept + 271 a code + 142 a figure + 23 a rule + 159 a
hands-on + 46 a term + 157 an erratum. R² 0.52, root-mean-square error 958 words. Its weights for code and figures are
close to the README's guide (200 to 300, 100 to 150). It cannot see what is no home row: tutorial steps, `use` and
`link` rows (the weight of `make`), and its constant alone is above S's budget. 20 pages differ from it by more than 40
percent. I read each page's section:

| Page | Size | Estimate | Model | I believe | Why |
| --- | --- | --- | --- | --- | --- |
| `start/welcome` | S | 1,500 | 3,149 | the estimate | Four short sections of about 900 words and the fixed parts (`start.md:31`); the model's constant cannot go below 2,779 |
| `start/how-to-read` | S | 2,400 | 4,243 | neither: about 3,000 | By the README's own values: 7 steps on the site at 150 (1,050), JSON and reading code from zero at 400 to 500 each, the conventions with an example each, 600 fixed (`start.md:54-119`). M either way |
| `make/transforms-units` | L | 5,000 | 3,559 | the estimate | Nine ideas from zero at B0's length (`make-a.md:337`); most are `use` rows of other inventories |
| `make/materials` | L | 5,000 | 3,354 | the estimate | Ten steps, three ideas from zero, five pictures (`make-a.md:524`); steps are no items |
| `make/scripting-scene` | L | 4,600 | 2,960 | the estimate | Eight steps with two or three calls each and four excerpts (`make-a.md:1038`) |
| `make/project-coin-run` | L | 5,000 | 2,938 | the estimate | Eight steps in four sections with checkpoints (`make-a.md:1695`); one hands-on row holds the whole project |
| `make/look` | L | 4,700 | 2,824 | the estimate, or a little more | About 22 steps at 150 and four short ideas come to about 5,000 (`make-b2.md:293`); inside L either way |
| `make/project-tetris` | XL | 8,700 | 5,285 | the estimate | Eight stages of about six steps with results (`make-c.md:122`) |
| `make/project-platformer` | XL | 9,800 | 4,963 | the estimate | Nine stages of five or six steps (`make-c.md:271`); 200 words under XL's top (For the planner) |
| `world/scene-graph` | XL | 8,900 | 6,307 | the estimate | Eleven code rows (about 2,750 words by the README) plus the full problem section and the internals shape (`world.md:185`) |
| `world/reflection` | L | 7,000 | 4,841 | the estimate | Nine numbered sections, each a mechanism (`world.md:429-457`), after a problem section with a table of four approaches; XL |
| `gpu/frame-tour` | XL | 7,900 | 4,133 | the estimate | Twenty-four passes walked at about 80 words each are no items (`gpu.md:853`) |
| `light/sun-shadows-2` | XL | 7,900 | 4,837 | the estimate | Six anchored sections, four diagrams, five figures, a long excerpt (`light.md:859-938`) |
| `physics/why` | S | 1,550 | 3,103 | the estimate | A concept page at S (`physics.md:28`); the model's constant |
| `animation/problem` | S | 1,500 | 3,149 | the estimate | Same (`animation.md:28`) |
| `animation/limits` | S | 1,500 | 2,938 | the estimate | Six not-done paragraphs of one paragraph each (`animation.md:892`) |
| `audio/testing` | S | 2,000 | 3,579 | the estimate | The content its Covers lists fits about 2,000 (`audio-input.md:400-454`); its Fit asks M to add test cases, which is new content, not room the page needs. S1 keeps S |
| `editor-ui/imgui` | L | 5,200 | 3,144 | the estimate | Twelve terms taught from zero sit in six home rows (`editor-ui.md:88`) |
| `editor-ui/tutorial-panel` | L | 4,500 | 2,938 | the estimate | Five step sections with a patch excerpt each (`editor-ui.md:1229`) |
| `appendix/not-in-strata` | L | 5,000 | 2,779 | the estimate | 81 link rows of not-done entries, which the model does not count (`appendix.md:45`) |

None of these changes a verdict. Two more numbers I do not believe, outside the model's list:

- The halves of `basics/bytes` (`basics-a.md:961`): 3,700 and 3,700 leave out the second page's fixed parts. I use
  about 4,100 each (Splits in detail), which makes both L.
- 57 of the 306 pages state an estimate exactly equal to their budget (12 of them in `make-a`, 6 in `image`, 5 in
  `basics-a`, 5 in `animation`). Some will be measured counts, but an estimate equal to the budget may be the budget
  written down. S1 keeps all of them; their briefs should count their sections.

## For the planner

1. **Pages at the top of their range.** Rule S keeps a page whose estimate is anywhere inside its range, so 34 pages are
   planned within 5 percent of their range's top, and 10 exactly at it: `make/automated-playtests`, `gpu/upload-queue`,
   `gpu/debug-drawing`, `assets/handles-meta`, `editor-ui/ui-testing` (4,000, M), `assets/importing`,
   `light/sun-shadows-1`, `worlds/runtime`, `editor/script-builds` (6,500, L) and `draw/visibility-feedback` (2,250, S).
   The estimates are rough (the model's error is about 960 words). A page that runs over its top must be cut, which S4
   forbids, or comes back under R11. A page that runs under the floor of the next class needs more examples or
   exercises, which costs the reader nothing. Options: (a) rule S as it is, and the briefs of the 34 count their
   sections first; (b) move the 10 at the exact top one class up now (5 M to L, 4 L to XL, 1 S to M; about 23,500 more
   words at the budgets); (c) a margin in S1, keeping a page only up to its budget plus three quarters of the way to
   its top (S 2,063, M 3,750, L 6,125, XL 9,500), which changes 29 more pages (27 one class up; `basics/numbers` and
   `make/project-platformer` would need splits). I recommend (b) with (a) for the other 24: the ten have no room at
   all, and the next class is open to each (none is a primer or on track B at XL). With item 4's merge,
   `draw/visibility-feedback` leaves the list. The trial does not hold (b).
2. **`basics/tools`: larger, or split.** S2 gives L (6,200, `basics-a.md:119`), 300 words under L's top. The page is
   track G's first side step and track B's reading before `make/first-script`, and git is about 2,900 of its words,
   which neither needs then. The allocator's split (`basics/tools` "The tools: the terminal, files and a code editor",
   M; `basics/git` "Version control with git", M) works if `basics/git` stands after `basics/debugging` in the rows:
   track B then reads it after `make/project-coin-run`, before `basics/numbers`, and track E after `basics/debugging`;
   `core/first-change` needs `basics/git` (its row asks for clone and submodules), and `core`'s "Needs of the part"
   names it. Placed directly after `basics/tools`, it would break the rule that a track keeps a part's row order
   (track B reads `basics/tools` before `make/first-script` and the rest of `basics` after `make/project-coin-run`). I
   tried this on a second copy (`G:/GameEngineAI/.worktrees/docs-work/B/sizes/alt-tools/plan/`, made by
   `sizes/alt_tools.py` on top of the trial): the check passes, with 336 pages, 30 primers, track B 53 and track E 265.
   The halves are near M's top (the terminal about 3,300 and git about 2,900, plus fixed parts that the Fit line may
   not count). I recommend the split.
3. **`basics/math-vectors` and track G's side steps** (`basics-b-q2`, `from-workflow-a.md` item 2): settled by S1.
   About 5,500 words is inside L's range (`basics-b.md:44`), so the page keeps L and no `basics/math-angles` is made;
   track G keeps its two side steps. Should a brief measure it above 6,500, S3 cannot put a page before it on track G
   without a third side step (`tracks.md`, "It has two side steps"; `G_SIDE_STEPS` in `check_outline.py`). The way then
   is a page after it, on tracks B and E only, which takes what `make/gameplay-math` does not use (that page uses
   length, `normalize`, the dot product, `atan2` and the camera's ray: `book.md`'s one-home row of vectors), so angles
   stay on `basics/math-vectors`.
4. **The two smaller pages.** `draw/gpu-driven` XL to L (6,300, `draw.md:663`) and `draw/visibility-feedback` kept at S
   (2,250, `draw.md:812`) are both at or near the top of their ranges. The allocators' other way is one page:
   `draw/visibility-feedback` merged into `draw/gpu-driven` as its last section, about 7,950 words at XL (the merged
   page saves one set of fixed parts). The Needs that name `draw/visibility-feedback` (`draw/mip-streaming`,
   `animation/culling` and `animation`'s "Needs of the part") would then name `draw/gpu-driven`. That gives one page with room in place of two without, and
   keeps one home for each concept; the allocator's reason is that the counting pass writes the feedback
   (`draw.md:663`). I recommend the merge; the trial holds rule S's
   result and does not try the merge. `worlds/export` L to M (3,800, `worlds.md:397`) has the other way of taking the
   game icon and the version resources from `worlds/game-identity` (`worlds.md:489`); that would split the game's
   identity over two pages, against `book.md`'s one-home row for the export ("the manifest and the game's identity
   `worlds/game-identity`"). I recommend rule S's M.
5. **W8 pages near their top before phase B adds.** `make/lamps` keeps M at 3,800 (`make-b2.md:35`), and phase B adds
   0.8.0's rectangle lights (component, units, Inspector, script surface, soft shadows): it will not stay under 4,000.
   A W8 page is never made smaller, so giving it L now is safe. I recommend L for `make/lamps` now. `light/local-shadows`
   (5,400, L), `indirect/gi-voxels` (5,800, L) and `gpu/frame-tour` (7,900, XL, W8r) also keep their sizes with phase B
   still to add; for them I recommend leaving the decision to phase B under R11, since their room is 1,100, 700 and
   2,100 words.
6. **XL as a cap** (`make-c-q2`). Rule S uses the linter's range, so XL ends at 10,000 words and both projects stay one
   page: `make/project-tetris` 8,700 and `make/project-platformer` 9,800 (200 under the top). The allocator's split of
   the platformer after stage 5 would give two pages of about 5,400 and 5,200 words, inside L's range (not XL, as its
   Fit line says), and would move the end of track G, which `tracks.md` and `book.md` name. I recommend one page, as
   rule S gives, and a count of its stages in the brief.
7. **Reference pages** (`reference-q1`). Rule S leaves kind R out, but the linter's `size` counts prose, and 21 of the
   22 reference pages are below the floor of their size. Sizing them by prose cannot work for all: `reference/glossary`
   (about 450 words, `reference.md:1262`) and `reference/term-index` (about 350, `reference.md:1315`) are below S's floor
   of 600. I recommend exempting kind R from `size` in `style.md` and keeping their sizes as the measure of generated
   volume that each Fit line states. Their 95,500 words at the budgets stay in the book's totals, which then count
   tables as well as prose. The four appendix pages of kind R are the same case: their estimates count tables written
   by hand, and by prose alone `appendix/history` is under 1,500 words against M and `appendix/credits` about 600
   against S (`appendix.md:433-505`, `appendix.md:545-598`).
8. **Pages that keep their size although their Fit line asks for a split.** Among them `make/physics` (5,800, L; the
   proposal in `make-a-q1` of a new block B page), `make/menus` (6,300), `basics/numbers` (6,400), `basics/math-vectors`
   (5,500), `basics/math-rotations` (5,400), `world/scene-graph` (8,900), `core/jobs` (5,900), `light/sun-shadows-1`
   (6,500) and `editor-ui/imgui-backends` (6,400). Rule S needs none of these splits; items 1 and 2 above cover the ones
   with no room.
9. **Wave 1 grows most.** The three new primers and eleven larger `basics` pages make wave 1 the largest wave at the
   budgets: 290,500 words, against 284,500 for wave 4. Wave 6 grows by 27,000. `process.md`'s table (in the trial) has
   the numbers; whether wave 1 should be cut in two is for the planner.
