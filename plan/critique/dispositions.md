# Dispositions of the critique's findings

This file records what happened to every finding of `summary.md` section 2. The planner's rulings are
`rulings-1.md` to `rulings-3.md` (R1 to R6 are the numbered rulings of `rulings-1.md`), and `rulings-6.md` for the
owner's answers of 2026-11-10. A ruling wins over the summary and over a critic. A finding that no ruling names is
accepted as the summary states it.

Every "Where it landed" cell names the revised plan file and its heading. Each one was opened and checked against the
disposition. A cell says **NOT APPLIED** where the revised file lacks what the disposition says, and names the missing
item.

## Counts

| Group | Findings | Blocker | Major | Minor |
| --- | --- | --- | --- | --- |
| BK (`book.md`) | 11 | 1 | 7 | 3 |
| OL (`outline-1.md` to `outline-4.md`) | 19 | 5 | 10 | 4 |
| ST (`style.md`) | 12 | 0 | 6 | 6 |
| SI (`site.md`) | 25 | 1 | 16 | 8 |
| PI (`pipelines.md`) | 34 | 1 | 15 | 18 |
| PR (`process.md`) | 9 | 0 | 8 | 1 |
| README (RM) | 1 | 0 | 0 | 1 |
| **All** | **111** | **8** | **62** | **41** |

| Disposition | Findings |
| --- | --- |
| Accepted (as stated, or with the option a ruling names) | 110 |
| Rejected | 1 (OL3) |
| Accepted, with an item NOT APPLIED in the revised plan | 1 of the 110 (SI3: the banner on `plan/research/framework.md`, a file the plan's revisers do not edit) |
| Accepted, with an item applied in its nearest workable form | 1 of the 110 (OL15); section 4 lists every such place, rulings included |
| Accepted and fully landed | 108 |

Some accepted findings have one sub-item that a ruling rejects or replaces (BK5, OL14, PR7). Their cells name it.

## 1. Findings

### `book.md`

| Finding | Severity | Disposition | Where it landed |
| --- | --- | --- | --- |
| BK1 | blocker | accepted: R3 and R4. The B order is R4's, neither BG's nor CU's. It is written in `plan/tracks.md`, as BG asked. The personas are R3's. The Test out box has five questions (R2), not three. A page is written and reviewed for the least prepared persona of its tracks (R3), in place of item (d) | `book.md` "Readers and personas", "Tracks"; `tracks.md` "Rules", "Track B: the beginner"; `style.md` §1.1, §1.2, §6.1 (`tracks`), §6.2 (badges), §7.1; `outline-1.md` "Tracks" and the row `start/welcome`; `site.md` "Navigation" |
| BK2 | major | accepted | `book.md` "One home per concept" (rules 1 and 2, the Use column), "Tracks" (rules 1 to 3); `site.md` "Outline rules on the pages" (O4); `check_outline.py` |
| BK3 | major | accepted: §4.1 and §4.2, with the contradictory rows decided as `rulings-3.md` "book.md" says | `book.md` "One home per concept", its seven tables |
| BK4 | major | accepted: the homes of `rulings-3.md` (`image/taa`; `indirect/problem`; `gpu/frame-tour` and `indirect/gi-limits`; `light/units-exposure` and `image/pre-exposure`; `core/time`; `core/jobs`; `engineering/perf-lab`). The TAA decision names Medium's Checkerboard screen-space reflections as its exception | `book.md` "Strata's design decisions, taught as decisions"; the rows `image/taa`, `indirect/ssr`, `indirect/problem`, `indirect/gi-limits` (`outline-3.md`), `gpu/frame-tour` (`outline-2.md`), `engineering/perf-lab` (`outline-4.md`) |
| BK5 | major | accepted: the list corrected from §5 with evidence per entry (`rulings-3.md`). SM's animation wording ("until 0.8.0's animation graph") is not used: the animation entries stay (`rulings-1.md`). Area lights are not an absence: 0.8.0 has rectangle lights (`rulings-1.md`) | `book.md` "What Strata does not do" (rules 1 to 6, thirteen tables, the last "Checked when the W8 page is written"); `outline-4.md` row `appendix/not-in-strata` (its From names `Docs/Releases/0.8.0.md`); `outline-3.md` rows `animation/limits`, `indirect/gi-limits` |
| BK6 | major | accepted: the part order of `rulings-2.md` (CU's order world, gpu, assets, with scene documents, prefab data and sub-scenes kept in `world` as CF asked). Track E meets the editor only in `start/first-game` (R4); CU's proposal that E reads `make/editor-tour` is not adopted | `book.md` "Parts", "Tracks" (rule 5); `tracks.md` "Track E: the engine builder"; `outline-2.md` Parts 4 to 6 |
| BK7 | major | accepted: `rulings-3.md` "Running examples". Coin Run is GM's rolling ball, built in stages through block A (BG); WindZone runs from `world/tutorial-component` to the capstone; the capstone part exists. CU's box "What happens to Coin Run here" in the engine parts is not used, because Coin Run stays in block A | `book.md` "Running examples"; `outline-1.md` Part 1, block A; `outline-4.md` Part 22; `process.md` "Allocation and part briefs" (brief item 3) |
| BK8 | major | accepted: R2 (the primer's shape and a Test out box of five questions) | `book.md` "Kinds of page"; `style.md` §6.3, §7.1; `outline-1.md` "How to read the tables" (Kind) and Part 2 |
| BK9 | minor | accepted | `book.md` "One home per concept" (rule 6 and the row on "module", "layer", "registry" and "service"); `outline-1.md` row `core/map`; `style.md` §3 ("Two meanings"); `pipelines.md` §9 |
| BK10 | minor | accepted: the counts are those `check_outline.py --counts --words` prints, 332 pages after `rulings-4.md` (`rulings-3.md`) | `book.md` "Parts"; `README.md` "Decisions at a glance" (item 3); `process.md` (introduction) |
| BK11 | minor | accepted (the finding asks to consider the package): considered and not used, because the book is written for people and is not offered as a corpus; an agent that works on the engine has the engine's own guide and skills (`rulings-6.md`, R20) | `book.md` "Readers and personas" (the fourth reader); `site.md` "Plugins: package or ours" (last row) |

### `outline-1.md` to `outline-4.md`

| Finding | Severity | Disposition | Where it landed |
| --- | --- | --- | --- |
| OL1 | blocker | accepted: R1 | `outline-1.md` "How to read the tables" (columns, Tracks, Needs), "Tracks", "The check"; the line "Needs of the part" of every part in `outline-1.md` to `outline-4.md`; `check_outline.py` (it passes); `site.md` "Outline rules on the pages" (O1 to O9) |
| OL2 | blocker | accepted: R5. BG's primers are in `basics`; the tracks read them after `make/first-script`, with a Strata script as the playground (GM's placement). There is no `make/cpp-for-scripts`, `make/cpp-1`, `make/cpp-2`, `basics/first-program`, `basics/programming` or `start/terminal`. `basics/cpp` is four primers; `core/debugging` is added | `outline-1.md` Part 2 (rows `basics/tools`, `basics/programming-1` to `-3`, `basics/debugging`, `basics/cpp-memory`, `basics/cpp-classes`, `basics/cpp-generic`, `basics/cpp-modern`, `basics/build`) and Part 3 (row `core/debugging`); `book.md` "One home per concept" (first table); `tracks.md` tracks G and B |
| OL3 | blocker | rejected: `rulings-1.md` "Facts the critics did not have". The animation-graph stream left wave 8 on 2026-11-03, so animation in 0.8.0 is 0.7.0's. No page of `animation` carries a W8 mark; no `animation/graph` or `animation/sync-layers` | `outline-3.md` Part 12 (no mark; `animation/limits` keeps blend trees and layers); `book.md` "What Strata does not do", "Animation"; `process.md` step 11 (the plan expects no animation graph in 0.8.0) |
| OL4 | blocker | accepted: `rulings-2.md` Part 1. GM's three blocks; Coin Run built step by step through block A (BG); `make/gameplay-1` to `-3` dissolved into topic pages (SM F4, GM F3); GM's `make/scripting-scene` (H, L); `make/first-script` before the programming primers (GM); `make/play-test-debug` in block A after `make/hud`; Coin Run as GM's rolling ball. Every API family of the scripting inventory's "Gameplay API" chapters has a home; two families of part 3 have none among the twelve pages `rulings-2.md` lists and went to the nearest page: graphics options (`Graphics`, `GraphicsOption`, `QualityPreset`) to `make/quality`, worlds (`World`, `WorldCellRequest`) to `make/large-worlds`. One function of part 1, `Scene::InstantiateMany`, went from `make/scripting-scene` to `make/performance`, because it takes 4×4 matrices, which no earlier page of track G teaches | `outline-1.md` Part 1 (blocks A, B and C); `book.md` "Running examples"; `tracks.md` "Track G: the game maker" |
| OL5 | blocker | accepted: GM's `start/install` (H, M; the script toolchain; the final check `script.status`). The source build moved to `core/first-change` (`rulings-2.md`). `start/first-game` takes option GM. `start/what-an-engine-is` comes after `start/first-game` (CU, GM) | `outline-1.md` Part 0 and Part 3 (row `core/first-change`); `outline-4.md` row `engineering/building` |
| OL6 | major | accepted: `rulings-2.md` Part 2. `basics/numbers` is its own page; `basics/signals` (pixels as samples stay one sentence of `gpu/how-a-gpu-frame-works`); CU's four pages from `basics/math-vectors`; BG's split of `basics/math-light` into `basics/math-probability` and `basics/math-sphere`; `basics/math-change` and `basics/data-structures` added. `basics/gpu` and `basics/math-numbers` are rejected by `rulings-2.md`: powers and logarithms are in `basics/numbers`, makers' angles in `make/gameplay-math` | `outline-1.md` Part 2 and the row `start/how-to-read` ("How to read a command", JSON); `outline-2.md` row `gpu/how-a-gpu-frame-works`; `book.md` "One home per concept" (first table); `style.md` §10 (the command tab is optional on G pages) |
| OL7 | major | accepted: the part order of `rulings-2.md` and its decided contradictions. (a) `gpu` before `assets`; the upload split stays. (b) The editor is two adjacent late parts, `editor` and `editor-ui`, with ED's moves of the journal and of world editing. (c) RB's order of `light`, with `light/energy` and `light/measuring-light` in it; sky and fog stay in `light`; `draw/motion-vectors` and `draw/skinned` stay; `draw/mip-streaming`; `image` before `indirect`. (d) Testing is in `engineering`, split as CF asked; writing a GPU test is in `gpu/first-triangle`. (e) `physics/scale-streaming` stays, with the Need `world/sub-scenes`. (f) SM's split. (g) By the waves. (h) `gpu/first-triangle` after `gpu/coordinates`, needing `core/first-change` | the part order and the rows of `outline-1.md` to `outline-4.md`; `book.md` "Parts"; `process.md` step 10 |
| OL8 | major | accepted: R6. W8 on seven pages and W8r on seven; no W8L, and "new in 0.8.0" is the `since` front matter; `light/lights` and `light/many-lights` W8r; `light/area-lights` W8; `image/quality-settings` and `make/look` W8r; `make/lighting` and `make/reflections` without a mark; no mark for fog, materials or placement (`rulings-1.md`) | `outline-1.md` "Marks"; the marks of the rows in `outline-1.md` to `outline-3.md`; `book.md` "Parts" (the W8 and W8r lists); `style.md` §13 (`w8r-preset`). The coat under rectangle lights: the rows `light/clearcoat-transmission` and `light/area-lights`. §3.3's note on the units of rectangle lights: one sentence of `light/units-exposure`, a movable claim read again at the pin move (`process.md` step 11), and the units themselves in `light/area-lights` (W8) (`outline-3.md` Part 8) |
| OL9 | major | accepted: the kinds of §3.2 as `rulings-2.md` sets them: `engineering/testing` C and `engineering/test-program` I; `assets/textures` C and `assets/texture-cooking` I; `light/materials` C and `light/material-data` I; `scripting/host-api` I and `scripting/tutorial-host-function` T; `animation/editor` I; `light/measuring-light` I; `make/reflections` and `make/gi`; `make/scripting-scene` H; `make/assets` H; `core/reading-code` H; every primer P; `make/commands`; `assets/robustness` C; `input/how-input-works` (SM's id); `light/reflectance` | the named rows of `outline-1.md` to `outline-4.md` |
| OL10 | major | accepted: primers and pages of track B are at most L (the G projects `make/project-tetris` and `make/project-platformer` stay XL, `rulings-2.md`); every section of an XL tutorial ends playable and downloadable (GM); `reference/commands` may split (SO); ED's sizes and splits win over CU's merges (`rulings-2.md`) | `outline-1.md` "How to read the tables" (Size), "The check"; `outline-4.md` Parts 18 and 19 (`editor/undo` XL, `editor-ui/imgui-backends` L, `editor-ui/lists` L, `editor-ui/game-view` holds the shortcuts, `editor-ui/settings-windows`) |
| OL11 | major | accepted: the moves; GM's `make/commands` (H, M) without `start/terminal` (R5); one page `make/with-an-agent` (T, L; `rulings-2.md`); undo, saving and recovery in `make/project-files` (`rulings-2.md`); `automation` on track E only. The use half of `physics/tuning` stays in `make/physics`. The rebinding screen is built in `make/menus`, with binding capture, saving the bindings and typed text, not in `make/input` as the finding has it: the screen needs buttons and UI events, which `make/menus` teaches and `make/input` (before `make/hud`) cannot use (nearest workable form, section 4) | `outline-1.md` Part 1 (rows `make/animation`, `make/physics`, `make/automated-playtests`, `make/performance`, `make/lighting`, `make/materials`, `make/commands`, `make/with-an-agent`, `make/project-files`, `make/menus`); `outline-3.md` row `input/rebinding`; `outline-4.md` Part 20 |
| OL12 | major | accepted: every row. `start/map` is part of `start/how-to-read` and `engineering/measuring` is the retitled `engineering/perf-lab` (`rulings-2.md`). `reference/index` is `reference/term-index`, because a row id may not end in `index` and the part `reference` has a generated `reference/index` | `outline-1.md` rows `make/designing-a-game`, `make/patterns`, `start/coming-from`, `make/project-files`, `start/how-to-read`, `core/debugging`, `core/files`; `outline-2.md` rows `gpu/compute`, `gpu/debugging`, `assets/texture-cooking`; `outline-3.md` rows `light/reflectance`, `light/material-data`, `light/atmosphere`, `indirect/seam`; `outline-4.md` rows `editor/script-builds`, `editor/projects`, `editor-ui/settings-windows`, `worlds/game-identity`, `engineering/test-program`, `engineering/perf-lab`, `reference/scene`, `reference/performance`, `reference/term-index`, `reference/notation`, `appendix/game-ai`, and Part 22; `book.md` "Kinds of page" (generated pages) |
| OL13 | major | accepted: RA's and RB's wordings together | `outline-3.md` "Figures of parts 8 to 10"; `style.md` §11; `process.md` "Allocation and part briefs" (brief item 5) |
| OL14 | major | accepted, except the W8 mark on `reference/animation`, which `rulings-1.md` rejects. `reference/index` is `reference/term-index` (see OL12) | `outline-4.md` Part 23 (rows `reference/scene`, `reference/performance`, `reference/term-index`, `reference/notation`, `reference/assets`, `reference/renderer`, `reference/editor`, `reference/script-api`, `reference/commands`, `reference/glossary`, `reference/worlds-runtime`); `pipelines.md` §7.1; `process.md` step 12 |
| OL15 | major | accepted with the orders of `rulings-2.md`: `core/conventions` third, after `core/first-change`; `make/script-loop` after `make/first-script` (R5); `editor/camera-viewport` last before `editor/tutorial-command`, because `editor-ui/scene-view` is in the next part | `outline-1.md` Part 3; `outline-4.md` Part 18 (`editor/deferred-commands` third); `outline-3.md` Part 11 (`physics/collision-layers` before `physics/contacts-triggers`) and Part 8 (`light/area-lights` after `light/many-lights`); `outline-2.md` (`world/tutorial-component` last; `gpu/first-triangle` after `gpu/coordinates`). In its nearest workable form: the exported-start check "A world that waits for its ground" stays in `make/large-worlds`, because `make/export` is in block A, before any world on track G (Coin Run has none); `make/export` says it in one sentence and links `make/large-worlds` (`outline-1.md` rows `make/export`, `make/large-worlds`) |
| OL16 | minor | accepted | the From columns of the primers (`outline-1.md` Part 2), `make/hud` (`TextComponent`), `make/project-coin-run` (`outline-1.md`), `automation/agents`, `editor-ui/inspectors`, `reference/editor`, `engineering/generated-code` (`outline-4.md`) |
| OL17 | minor | accepted with the sizes of `rulings-2.md` (`make/input` M, `make/assets` M; `scripting/crash-containment` L split from `scripting/symbolization` M) | `outline-2.md` rows `world/interpolation` (L), `draw/visibility-feedback` (S); `outline-3.md` rows `image/grading` (L), `image/motion-blur` (M), `image/depth-of-field` (L), `animation/clips` (L); `outline-4.md` Part 15 |
| OL18 | minor | accepted | `outline-4.md` rows `ui/text`, `editor/play-mode`, `editor/command-scripts`; `outline-1.md` row `make/levels-saves`; `outline-2.md` rows `gpu/vulkan-nvrhi`, `gpu/binding` |
| OL19 | minor | accepted | `outline-4.md` row `appendix/math-cheatsheet`; `style.md` §4 |

### `style.md`

| Finding | Severity | Disposition | Where it landed |
| --- | --- | --- | --- |
| ST1 | major | accepted: at most a fifth of the prose (RA); one paragraph that links the concept page when one holds it (CU); the table of alternatives (CU) | `style.md` §7.3; `book.md` "Kinds of page" (I); `process.md` "Allocation and part briefs" (brief item 4) and "The stages of a page" (technical review) |
| ST2 | major | accepted | `style.md` §2.1, §2.2 (`sentence-mean`, `sentence-max`, `paragraph-length`, `word-list`, `acronym`, `phrasal-verb`, `pronoun-start`, `noun-stack`, `copied-text`), §2.3, §2.4, §2.5, §3 (`term-section`); `site.md` "Front matter and the teaching checks" ("Language") |
| ST3 | major | accepted | `style.md` §9.1 (`code-intro`, `code-follow`, `callouts`, `long-quote`, `cpp-feature`); `outline-1.md` row `start/how-to-read` |
| ST4 | major | accepted | `style.md` §4 (`math-symbols`, `math-derivation`, `math-g`), §2.2 (`banned-word`), §7.7 (the notation table) |
| ST5 | major | accepted: both exercise rules, GM's for pages before `make/first-script`, BG's for the other pages | `style.md` §8, §12 (`:::simplified`, `:::analogy`, `:::example`), §7.1 and §7.2 (`## Common mistakes`) |
| ST6 | major | accepted | `style.md` §7.4, §10 (`step-parts`; a command-only step needs `make/commands`), §11; `pipelines.md` §6.2 to §6.4 |
| ST7 | minor | accepted | `style.md` §6.1 (the example's title is the title of `core/time` in `outline-1.md`) |
| ST8 | minor | accepted | `style.md` §2.1 (last item) |
| ST9 | minor | accepted | `style.md` §6.1 (`time`), §6.2 (the levels and what they mean), §2.2 (`time`) |
| ST10 | minor | accepted | `style.md` §6.1 (`learn` as `{id, text}`), §6.3 (Summary), §8 (`tests`); `site.md` "Page shape" (P2); `process.md` "The provenance check" ("What it returns": one row per learn id, with the questions that test it and whether the reviewer answered them from the page and its closure) |
| ST11 | minor | accepted as R6 decides: `since` and `:since[0.8.0]`, not a mark | `style.md` §6.1, §6.2, §12, §13; `site.md` "Navigation" |
| ST12 | minor | accepted | `style.md` §13 (`g-frame-share`) |

### `site.md`

| Finding | Severity | Disposition | Where it landed |
| --- | --- | --- | --- |
| SI1 | blocker | accepted: the budget table is pass or fail for the spike (`rulings-3.md`) | `site.md` "Budgets and the spike" (20 rows with machine and remedy), "Framework and versions" ("Fallback": the verdict is final); `README.md` "Decisions at a glance" (item 10) |
| SI2 | major | accepted: the spike's content follows the revised outline (332 rows after `rulings-4.md`) | `site.md` "Budgets and the spike" ("The spike's content follows the book") |
| SI3 | major | accepted | `site.md` "Where this file overrides the research" (its first paragraph says that `research/framework.md` §5 is background only and that `site.md` and `pipelines.md` decide); `README.md` "Files" (row `research/`); `process.md` "What a writer is given" (item 5); `site.md` "Layout of the repository" (`labs/`; no `diagrams/` folder, with the reason). NOT APPLIED: the banner on `plan/research/framework.md` §5 itself, because the plan's revisers and fixer do not edit `plan/research/`; the planner adds it |
| SI4 | major | accepted: `rulings-3.md` "Pictures". PL's `publish: lossy \| lossless` per recipe; SO's one format per picture, no upscaling, crops never resampled and enlarged pixelated in CSS, names with a content hash; PNG originals never committed, archived per book release (at most 1 GB) | `site.md` "Pictures"; `pipelines.md` §5.7; `README.md` "Decisions at a glance" (item 9) |
| SI5 | major | accepted | `site.md` "Math", "The three gates" ((a) item 2), "Diagrams" |
| SI6 | major | accepted (the track links stand in `<template data-book-track>`, the spike's form) | `site.md` "The three gates" ((a), (b), (c)), "Navigation" |
| SI7 | major | accepted | `site.md` "The base path" (rules 1 to 8, "Every way the site can leave the base, and its test"), "Where the site is served: the settings" |
| SI8 | major | accepted | `site.md` "Deployment" ("The deploy folder", "The ten requirements and their tests", "`deploy/README.md`") |
| SI9 | major | accepted: `rulings-3.md` (the design is written; only the reservation is implemented; one version is built) | `site.md` "Versions"; "The base path" (rule 8) |
| SI10 | major | accepted | `site.md` "Deployment" (`deploy/Dockerfile`, `deploy/Dockerfile.build` with its memory need, "What a release holds"), "CI" (`serve-test`, `release`) |
| SI11 | major | accepted with the spike's names: `caption` and `alt` in place of `accTitle` and `accDescr`; the page's Inter in place of an embedded font subset | `site.md` "Diagrams"; `style.md` §11 |
| SI12 | major | accepted | `site.md` "Glossary"; `style.md` §3 |
| SI13 | major | accepted | `site.md` "Plugins: package or ours" (with the two rules) |
| SI14 | major | accepted: SO's path `src/generated/reference/`, which `pipelines.md` uses too | `site.md` "Generated reference"; `pipelines.md` §7.2 |
| SI15 | major | accepted | `site.md` "Search" |
| SI16 | major | accepted | `site.md` "CI" |
| SI17 | major | accepted | `site.md` "Front matter and the teaching checks" (O1 to O9, P1 to P4, "Language"), "Navigation" |
| SI18 | minor | accepted | `site.md` "Navigation" (print views); "Budgets and the spike" (row 19) |
| SI19 | minor | accepted | `site.md` "`deploy/README.md`" (item 7) |
| SI20 | minor | accepted | `site.md` "Checks" (Accessibility); "Budgets and the spike" (rows 14, 15) |
| SI21 | minor | accepted | `site.md` "Pictures" (retakes, repository size), "CI" (`links.yml`) |
| SI22 | minor | accepted | `site.md` "The authoring machine"; `process.md` "Files and who writes them" ("Who commits") |
| SI23 | minor | accepted: the overrides listed are the two the spike uses, `PageTitle` and `Pagination` | `site.md` "What MDX would have given, and the replacements" |
| SI24 | minor | accepted | `site.md` "Astro and Starlight settings the book depends on"; "Budgets and the spike" (confirm item 6) |
| SI25 | minor | accepted | `site.md` "Framework and versions" (the table and "Known risks") |

### `pipelines.md`

| Finding | Severity | Disposition | Where it landed |
| --- | --- | --- | --- |
| PI1 | blocker | accepted: `rulings-3.md` "The engine at the pin". One clone `G:/GameEngineAI/.worktrees/docs-pin`; one Release build per pin by the tool builder, `--parallel 8`, under `Tools/PerfLock.py`; `--engine` and `--build`; `--no-gpu` editors one at a time; the `engineCommit` check; dumps and stamps of tutorials without rendering in phase A. The ruling says that no docs agent builds anything else; the plan has one more build, the patch runner's `build/docs-patch` in the same clone in phase B, which PI9 (accepted) needs for the tutorials that change the engine. It is the nearest form that meets both (section 4) | `pipelines.md` §1.1 to §1.4, §2, §13 ("Phase A"); `process.md` "Roles" (tool builder), step 5, "Not interfering with the engine's work"; `README.md` "Decisions at a glance" (item 7) |
| PI2 | major | accepted. The `engine` field for "before" pictures is the variant `baseline` of owner question 9 | `pipelines.md` §5.2 |
| PI3 | major | accepted | `pipelines.md` §5.3; §11 (tier 1) |
| PI4 | major | accepted | `pipelines.md` §5.4 ("Project copies", "Still figures") |
| PI5 | major | accepted | `pipelines.md` §5.6; §5.4 (live and runtime figures) |
| PI6 | major | accepted: `rulings-3.md`. The spike's names (`src="<path>#L…"`, `mark="L…"`) are kept and the file says so; `symbol` is added; the header comes from the spike's remark plugin | `pipelines.md` §3.1 to §3.5; `site.md` "Code fences" |
| PI7 | major | accepted | `pipelines.md` §3.2, §3.5 (`relocate` step 3) |
| PI8 | major | accepted | `pipelines.md` §6.1 to §6.4; `style.md` §7.4 |
| PI9 | major | accepted | `pipelines.md` §6.6, §6.2 (exercise solutions); `process.md` "The provenance check" (item 7) |
| PI10 | major | accepted: `rulings-3.md`. The names lint and phase B whole-editor pictures; no agent controls the owner's screen; the owner is invited to walk one tutorial, and the book does not wait | `pipelines.md` §6.5, §8, §5.5 (`takenBy: owner`); `process.md` "Track walks" |
| PI11 | major | accepted | `pipelines.md` §7.1 |
| PI12 | major | accepted | `pipelines.md` §7.2; `site.md` "Generated reference" |
| PI13 | major | accepted | `pipelines.md` §8, §13; `process.md` "The stages of a page" |
| PI14 | major | accepted: `rulings-3.md` (owner question 5). Tiers 1 and 2 land on the engine's `main` after 0.8.0 through its CI, not on a `release/0.8` branch; v0.8.1 is the final pin; tier 3 only where no debug view serves | `pipelines.md` §11; `process.md` step 13; `README.md` "Decisions at a glance" (item 8) |
| PI15 | major | accepted, with the W8 and W8r marks of R6 in place of W8L | `pipelines.md` §10.2 (items 4 and 5), §7.1, §7.3; `style.md` §13 |
| PI16 | major | accepted | `pipelines.md` §9; `process.md` step 6; `book.md` "One home per concept" (rule 6) |
| PI17 | minor | accepted | `pipelines.md` §5.1 (`text`, `tool`, "Text instead of a picture"), §5.5 (tool pictures) |
| PI18 | minor | accepted: the spike's `commit` and `release` lines stand for the tag comment | `pipelines.md` §1.1 |
| PI19 | minor | accepted | `pipelines.md` §5.4 (whole-editor figures), §2 |
| PI20 | minor | accepted | `pipelines.md` §5.4 (runtime figures) |
| PI21 | minor | accepted | `pipelines.md` §5.4 (project copies) |
| PI22 | minor | accepted as owner question 9 is decided: the variant `baseline` | `pipelines.md` §5.5 ("Before" pictures) |
| PI23 | minor | accepted | `pipelines.md` §6.4, §6.3 (`check`) |
| PI24 | minor | accepted | `pipelines.md` §10.2 (item 3), §5.7 (`compare`) |
| PI25 | minor | accepted | `pipelines.md` §1.2, §3.2 |
| PI26 | minor | accepted | `pipelines.md` §4 |
| PI27 | minor | accepted | `pipelines.md` §5.5 (Labs) |
| PI28 | minor | accepted | `pipelines.md` §5.5 (Shots), §10.2 (item 3) |
| PI29 | minor | accepted | `pipelines.md` §5.5 (Shots), §5.2 (`camera`) |
| PI30 | minor | accepted | `pipelines.md` §5.5 (Options menus); `book.md` "What Strata does not do" ("Editor, export and automation") |
| PI31 | minor | accepted | `pipelines.md` §2 |
| PI32 | minor | accepted | `pipelines.md` §13 (CI) |
| PI33 | minor | accepted | `pipelines.md` §5.1 (`reference`), §5.5 (Reference figures); `outline-3.md` "Figures of parts 8 to 10" and the row `indirect/problem` |
| PI34 | minor | accepted | `pipelines.md` §5.8 (last paragraph); `outline-4.md` row `reference/figures` |

### `process.md`

| Finding | Severity | Disposition | Where it landed |
| --- | --- | --- | --- |
| PR1 | major | accepted: the waves of `rulings-3.md`, with `editor` and `scripting` moved to wave 5 because the check found seven Needs on later waves; the ruling says to fix the wave list, not the Needs | `process.md` step 10 (the table and the moved Needs); `check_outline.py` (`WAVES`, `--waves`) |
| PR2 | major | accepted: the seven pilot pages of `rulings-3.md` | `process.md` step 9; `pipelines.md` §13 ("Phase A") |
| PR3 | major | accepted | `process.md` "The provenance check", "After the pictures (phase B)", "Roles" |
| PR4 | major | accepted: track G after wave 2 and at the end, track E at the end (`rulings-3.md`) | `process.md` "Track walks", step 16 |
| PR5 | major | accepted | `process.md` "The stages of a page" (exit checks, confirms); `pipelines.md` §13, §3.5 (`list --since`) |
| PR6 | major | accepted: `rulings-3.md` (each page pipeline writes only its own files; only the integrator commits and runs `npm ci`) | `process.md` "Files and who writes them", "Who commits"; `pipelines.md` §12 |
| PR7 | major | accepted, except the rule for a cut of 0.8.0 from landing 1, which `rulings-1.md` makes moot (the animation graph left wave 8) | `process.md` "What a writer is given" (`## Movable claims`), steps 11 and 12, step 10 ("Inside a wave": `editor/placement`, `editor-ui/scene-view`); `pipelines.md` §10.2 (item 4) |
| PR8 | major | accepted | `process.md` "Allocation and part briefs" (the allocation notes, brief items 1 to 8, "Errata known at 822a7a46") |
| PR9 | minor | accepted | `process.md` "Definition of done" |

### `README.md`

| Finding | Severity | Disposition | Where it landed |
| --- | --- | --- | --- |
| RM1 | minor | accepted as `rulings-3.md` "README.md" decides: the README lists the questions still open, those of `rulings-6.md` "For the owner". The license and the site's origin and server were decided by the owner on 2026-11-10 (`rulings-6.md`, R20 to R24); the other questions of §6 are decided (section 2 below) | `README.md` "Open questions for the owner", "Decisions at a glance" (items 10 and 13) |

The unnumbered README edits of summary §2.7 also landed: the W8 list follows R6 (`README.md` "Decisions at a glance",
item 8, without the animation graph, volumetric fog or material layers); the re-pin target is v0.8.1 (item 8); the
reference is "generated, or parsed from the source and checked" (item 6); the spike's pass or fail rule (item 10).

## 2. The owner questions of summary §6

| # | Question | Decided how | Where |
| --- | --- | --- | --- |
| 1 | The book's license | Decided by the owner on 2026-11-10: closed source, all rights reserved, with one permission for the book's code; third-party material keeps its own terms and notices | `rulings-6.md`, R20, R21, R22; `README.md` "Decisions at a glance" (item 13) |
| 2 | Where the site lives: the origin for `DOCS_SITE`, the server, files or a container | Decided by the owner on 2026-11-10: nginx, at `https://pdm.pw/strata-engine-docs/` for now, an address written once, in `site.json`. Both copied files and the container are tested, and copied files are recommended; which of the two, and what `nginx -V` prints on the host, are asked in `README.md` "Open questions for the owner" | `rulings-6.md`, R23, R24; `README.md` "Decisions at a glance" (item 10), "Open questions for the owner"; `site.md` "Where the site is served: the settings", "Deployment" |
| 3 | Picture storage | Decided (`rulings-3.md`, SI4): the docs repository commits the published files and the recipes; PNG originals go into one archive per book release (at most 1 GB); no LFS, no media repository | `site.md` "Pictures"; `README.md` "Decisions at a glance" (item 9) |
| 4 | 0.8.0's scope | Decided (`rulings-1.md`): the animation graph left wave 8; area lights are in 0.8.0 (rectangle lights; disk lights if stage 5 lands); volumetric fog, new showcase materials and new placement tools are not planned. The pin move's diff at `v0.8.0` is the check | `outline-1.md` "Marks"; `outline-3.md` Parts 8 and 12; `book.md` "What Strata does not do"; `process.md` step 11 |
| 5 | Engine additions for captures | Decided (`rulings-3.md`, PI14): tiers 1 and 2 land on the engine's `main` after 0.8.0 through its CI and ship as v0.8.1 (not from a `release/0.8` branch); the book's final pin is v0.8.1 | `pipelines.md` §11; `process.md` step 13 |
| 6 | The engine on the owner's machine in phase A | Decided (`rulings-3.md`, PI1): one separate clone, one Release build with limited parallelism at a time the planner chooses, `--no-gpu` editors one at a time under `Tools/PerfLock.py` | `pipelines.md` §1, §2; `process.md` "Not interfering with the engine's work" |
| 7 | Real beginners | Decided (`rulings-3.md`): personas check the book; the owner is invited to give it to a real beginner; nothing waits for that | `process.md` "Track walks" ("People"); `README.md` "Decisions at a glance" (item 12) |
| 8 | The UI walk | Decided (`rulings-3.md`): the names lint, and whole-editor pictures in phase B; no agent controls the owner's screen; the owner is invited to walk one tutorial; the book does not wait | `pipelines.md` §6.5; `process.md` "Track walks" |
| 9 | "Before" pictures | Decided (`rulings-3.md`): the engine's look-dev baselines at older tags, named with their tag. The ruling says "committed", but the baseline sets are not committed in the engine repository (`Docs/DeveloperGuide.md:769-773` at 822a7a46), so the plan takes them from read-only copies in `G:/GameEngineAI/.worktrees/docs-baselines/`, which the planner makes after confirming that the source folders still exist (section 4) | `pipelines.md` §5.5; `process.md` step 14; `README.md` "Decisions at a glance" (item 9) |

## 3. Contradictions and the option that won

"No ruling" marks a contradiction that no ruling decides; the revised plan chose the option named.

| Where in the summary | Question | Options | Won | Decided by |
| --- | --- | --- | --- | --- |
| BK1 | Track B's order | BG §6.12; CU §7 | Neither: R4's order (start; block A to `make/lighting`; `basics/computer`, `basics/tools`; `make/first-script`; the programming primers and `basics/debugging`; the rest of block A; the rest of `basics`) | R4 |
| BK1 (b) | Where the B order is written | BG: `plan/tracks.md`; CU: `book.md` | BG | R4 |
| BK6; OL7 a | World, assets and the GPU | CF: keep the order, add Needs; CU: world, gpu, assets, with scene documents in `assets`; RA: `basics/gpu` and one upload page; BG: gpu to the upload queue in wave 3 | CU's order; scene documents, prefab data and sub-scenes stay in `world` (CF); the upload split stays (CF) | `rulings-2.md` "Order of the parts", "Parts 4 to 7" |
| BK8 | The primers' kind | BG: P; CU: C | BG | R2 |
| BK7; OL4 | Coin Run's design | GM F11: a rolling ball on Basic 3D; CU: a first-person `CharacterController` | GM | No ruling; it follows from block A of `rulings-2.md`, which has no character page |
| OL2 | The form of programming from zero | BG: pages in `basics`; CU: one XL `basics/programming`; GM: `make/cpp-1`, `make/cpp-2` | BG's pages in `basics`, read after `make/first-script` with a script as the playground (GM's placement) | R5 |
| OL4 | `make/gameplay-2` and `-3` | SM, GM: dissolve; CU: keep as tutorials; SM's fallback | Dissolve | `rulings-2.md` Part 1 |
| OL4 | `make/gameplay-1` | GM: `make/scripting-scene` (H, L); CU: `make/scripting-the-world` (T, L) | GM | `rulings-2.md` Part 1 |
| OL4 | The order of `make` | GM: three blocks; CU: one order; BG: Coin Run in stages | GM's blocks, with Coin Run built in stages through block A (BG) | `rulings-2.md` Part 1 |
| OL4 | First script and C++ | GM: `make/first-script` first; BG: primers first; CU: `make/cpp-for-scripts` first | GM | R4, R5, `rulings-2.md` Part 1 |
| OL4 | `make/play-test-debug` | GM: after the scene-scripting page; CU: after Tetris | In block A after `make/hud` (nearer GM) | `rulings-2.md` Part 1 |
| OL5 | `start/first-game` | GM: the Tetris copy, Basic 3D, the generated `Spinner`; BG: no code, no samples | GM | No ruling |
| OL5 | The place of `start/what-an-engine-is` | BG: second; CU, GM: after `start/first-game` | CU, GM | `rulings-2.md` Part 0 |
| OL5 | `start/first-engine-change` | GM, CU: in `start`, track E; BG: `engineering/first-change` | Neither: `core/first-change` | `rulings-2.md` Parts 0 and 3 |
| OL6 | Floating point | Its own page (CU, ED, an RA option); inside `basics/bytes` (BG, an RA option) | Its own page, `basics/numbers` | `rulings-2.md` Part 2 |
| OL6 | Sampling and aliasing | `basics/signals` (RB, CU); `basics/sampling` (BG); `gpu/how-a-gpu-frame-works` (RA m4) | `basics/signals`; pixels as samples stay one sentence of `gpu/how-a-gpu-frame-works` | `rulings-2.md` Part 2 |
| OL6 | School algebra, powers, logarithms | BG: `basics/math-numbers`; GM: `make/gameplay-math` | GM's page; powers and logarithms in `basics/numbers` | `rulings-2.md` Parts 1 and 2 |
| OL6 | Splitting `basics/math-vectors` | CU: four pages; BG: two | CU | `rulings-2.md` Part 2 |
| OL6 | `basics/math-light` | BG: split; CU: keep | BG | `rulings-2.md` Part 2 |
| §3.2 | `basics/bytes` | BG: numbers inside, L; CU, ED: bytes, files, text and hashes, M | CU, ED (JSON in the title) | `rulings-2.md` Part 2 |
| §3.2 | `basics/reading-code` | CU: `core/reading-code`; BG: keep in `basics` | CU | `rulings-2.md` Parts 2 and 3 |
| OL7 b | The editor parts | CU: an early `editor` and a late `editor-ui`; ED: one part, pages moved into it; SM: pages to wave 6 | CU's split as two adjacent late parts, with ED's moves | `rulings-2.md` "Order of the parts", "Parts 18 to 24" |
| OL7 c | The measuring page | After `light/energy` (RB); after `light/units-exposure` (CU) | RB | `rulings-2.md` "Parts 8 to 10" |
| §3.2 | `light/energy`'s scope | RB: the BRDF table and the furnace; CU: with specular anti-aliasing | RB (specular anti-aliasing in `light/brdf`) | `rulings-2.md` "Parts 8 to 10" |
| OL7 c; §4.1 | The sky and fog | In `light`, split (RB); `indirect/sky`, `indirect/fog` (CU) | RB | `rulings-2.md`; `rulings-3.md` |
| OL7 c; §4.1 | Motion vectors | `image/motion-vectors` (CU); `draw/motion-vectors` (RB) | RB | `rulings-2.md` "Parts 4 to 7" |
| OL7 c; §4.1 | Skinned meshes in the renderer | `animation/skinned-rendering` (CU); `draw/skinned` with Needs on animation (RA M9) | `draw/skinned`, with no Need on animation and a forward link | `rulings-2.md` "Parts 4 to 7" |
| OL7 c | Mip streaming | CF; RA; CU | CU: `draw/mip-streaming` after `draw/visibility-feedback` | `rulings-2.md`; `rulings-3.md` |
| OL7 d | Testing | CU: `core/testing`; CF: split in `engineering`; RA: GPU test in `gpu/first-triangle` | CF's split; the GPU test in `gpu/first-triangle` (RA); `core/first-change` teaches one test | `rulings-2.md` Part 3 and "Parts 18 to 24"; `rulings-3.md` |
| OL7 e | `physics/scale-streaming` | SM, ED: keep, Need `world/sub-scenes`; CU: `physics/capacity` | SM, ED | No ruling |
| OL7 f; §4.1 | Simulated input | SM: devices in `input/simulated`, holds and `input.sequence` in `editor/stepping`; CU: `input.sequence` in `input/simulated` | SM | No ruling |
| OL8 | `light/lights` | No mark (RB); a split into `light/sun` and `light/local-lights` (CU) | Neither: W8r | R6 |
| OL8 | `light/area-lights` | A W8 section with a fallback (RB); out (SM); unchanged (CU) | W8 with 0.8.0's rectangle lights (nearest CU) | `rulings-1.md`; R6 |
| OL8 | `light/many-lights` | Phase A with a section revised (RB); W8 (CU) | RB: W8r | R6 |
| OL8 | `image/quality-settings` | W8r (RA); W8, or no preset value in prose (RB) | W8r, and no preset value in prose | R6 |
| §3.3 | `make/look` | W8r (RA); its quality section W8 (RB) | RA | R6 |
| §3.3 | `editor/placement` | W8? (CU); no mark, written last and re-read (ED) | ED | `rulings-1.md`; `process.md` step 10 |
| OL3; §3.3 | The animation pages' marks | SM: 12 pages; CF: 3; ED: 4; CU: 9 | None | `rulings-1.md` |
| OL8; §3.3 | Wave 8 work that has landed | W8L (CF); no mark, a "new in 0.8.0" label (SM, ED) | SM, ED | R6 |
| OL9 | The input concept page | SM: `input/how-input-works`; CU: `input/devices-to-intents` | SM | `rulings-2.md` "Parts 11 to 17" |
| §3.2 | `audio` sizes | SM F15 option a (two L pages); option b (a split) | Option a | `rulings-2.md` "Parts 11 to 17" |
| §3.2 | `scripting/host-api` and its tutorial: titles | SM; CU | SM | No ruling |
| OL10 | Editor sizes and merges | CU: three merges; ED: sizes, splits, shortcuts with the Game view | ED | `rulings-2.md` "Parts 18 to 24" |
| OL11 | The page moved from `automation` | ED: `make/command-line` (T, M); GM: `make/commands` (H, M) and `start/terminal`; CU: `make/editor-from-outside` (T, M) | GM's `make/commands`, without `start/terminal` | `rulings-2.md` Part 1; R5 |
| OL11; §4.1 | AI-agent pages, and the journal's use home | ED: `make/ai-agent` and `make/agent-game`; GM: one page `make/with-an-agent`; CU: none | One page `make/with-an-agent` (T, L) | `rulings-2.md` Part 1 |
| OL11 | Undo, saving and recovery for game makers | ED: `make/undo-save-recover`; GM: `make/editor-tour` | Neither: `make/project-files` | `rulings-2.md` Part 1 |
| §3.2 | Lamps, look and quality pages of `make` | GM: `make/lamps`, `make/look`, `make/quality`; CU: `make/local-lights`, one `make/look` | GM | `rulings-2.md` Part 1 |
| §3.2 | Game UI pages of `make` | SM, CU: `make/ui` and a widgets page; GM: `make/hud` and `make/menus` | GM | `rulings-2.md` Part 1 |
| §3.2 | The design page | GM, BG: `make/designing-a-game`; CU: `make/game-design` | GM, BG | `rulings-2.md` Part 1 |
| §3.2 | `make/recipes` and `make/reflections` sizes | Recipes M (GM) or L (CU); reflections L (RB) or M (CU) | Recipes L; reflections M | `rulings-2.md` Part 1 |
| OL12 | Compute shaders | RA: `gpu/compute`; CU: retitle `gpu/shaders` | RA | `rulings-2.md` "Parts 4 to 7" |
| OL12 | Debugging the GPU | CU: `gpu/debugging`; RA: a section of `gpu/frame-tour` | CU (the frame-capture check of `gpu/frame-tour` stays, phase B) | `rulings-2.md` "Parts 4 to 7" |
| OL15 | `core/conventions` | Second (CF); ninth (CU) | Neither: third, after `core/first-change` | `rulings-2.md` Part 3 |
| OL15 | `physics/collision-layers` | Before contacts (SM); after queries (CU) | SM | `rulings-2.md` "Parts 11 to 17" |
| §3.2 | `worlds/editing` | ED: `editor/worlds`; CU: keep in `worlds` | ED | `rulings-2.md` "Parts 11 to 17" |
| SI4 | Picture details | SO: one format per picture, served 1920 plus 960; PL: PNG originals committed, `publish` per recipe | Both in part: PL's `publish`; SO's formats, sizes and hashes; PNG originals archived per release, not committed | `rulings-3.md` "site.md" |
| SI14 | Where generated reference lands | SO: `src/generated/reference/`; PL: `reference/_generated/` | SO | No ruling (the summary notes that SO's point applies) |
| PI6 | Fence attribute names | SO: `lines="L…" marks="L…"`; PL: `src="engine:…" lines="…" highlight="…"` | The spike's names (`src="<path>#L…"`, `mark="L…"`) plus `symbol` | `rulings-3.md` "pipelines.md" |
| PR1 | Fixing the waves | SM: swap waves 4 and 5; CU: layers of a sort of the Needs | CU, then `editor` and `scripting` moved to wave 5 by the check | `rulings-3.md` "process.md" |
| PR2 | The pilot | BG; GM; PL; CF and CU | `start/install` and `basics/programming-1` (BG); `basics/math-vectors` (CU's id); `make/first-script` stamped with the pin build (GM, PL); `core/time` kept; `world/ecs`; `image/tone-mapping` with the offline `figures.py check` (PL). GM's `make/project-coin-run` is not in it | `rulings-3.md` "process.md" |
| §4.1 | Prefabs' data model | `world/prefabs` (CF); `assets/prefabs` (CU) | CF | `rulings-2.md`; `rulings-3.md` |
| §4.1 | Sub-scenes and the frame's budget | `world/sub-scenes` (CF); `assets/sub-scenes` (CU) | CF | `rulings-2.md`; `rulings-3.md` |
| §4.1 | The upload queue | One page `assets/uploads` (RA); `gpu/upload-queue` and `assets/uploads` (CF) | CF | `rulings-2.md` "Parts 4 to 7" |
| §4.1 | Light records | `light/many-lights` (RA M5); `draw/render-scene` with what a record holds in `light/lights` (RB F16) | RB | No ruling |
| §4.1 | Debug views and measuring light | RB F11; RA m3; CU | RB's split | `rulings-3.md` "book.md" |
| §3.2; §4 | Camera exposure and EV100 | CU, RA: `light/units-exposure`; RB: `image/exposure` | RB | No ruling |
| §4.3 | "Nothing needs history to look right" | `image/taa` (RA); `light/sun-shadows-2` (RB); `gpu/frame-tour` (CU) | `image/taa`, with the Checkerboard exception | `rulings-3.md` "book.md" |
| §4.3 | "GI traces world data" | `indirect/problem` (RA, CU); `indirect/gi-voxels` (RB) | RA, CU | `rulings-3.md` "book.md" |
| §4.3 | "Off is invisible bit for bit" | `gpu/frame-tour` (RA, CU); `indirect/seam` (RB) | `gpu/frame-tour` as a rule of the renderer, `indirect/gi-limits` for GI | `rulings-3.md` "book.md" |
| §4.3 | "Light in real units" | `light/units-exposure` (RA, CU); RB's split | RB: units in `light/units-exposure`, the mechanism in `image/pre-exposure` | `rulings-3.md` "book.md" |
| §4.3 | "Measured on the reference machine" | `engineering/perf-lab` (RA); `engineering/measuring` (CF); `core/profiling` (CU) | `engineering/perf-lab`, retitled to cover budgets; the method in `core/profiling` | `rulings-2.md` "Parts 18 to 24"; `rulings-3.md` |

## 4. Where the plan applies a ruling or a finding in its nearest workable form

Each row is a place where the ruling or the finding, applied as written, contradicts a fact or another accepted
decision. The plan does the nearest thing that works, and says so where it lands.

| Ruling or finding | As written | What the plan does, and why | Where |
| --- | --- | --- | --- |
| `rulings-2.md` "Parts 18 to 24" (`reference`) | add `reference/index` | `reference/term-index`: a row id may not end in `index` (R2), and the 22-page part `reference` has a generated `reference/index` | `outline-4.md` Part 23 |
| `rulings-3.md` "process.md" (PR1) | `editor` in wave 3, `scripting` in wave 4 | both in wave 5: the check found seven Needs on later waves, and the ruling says to fix the wave list, not the Needs | `process.md` step 10; `check_outline.py` (`WAVES`) |
| `rulings-2.md` Part 1 | every Gameplay API family to one of twelve pages | graphics options to `make/quality`, worlds to `make/large-worlds`, `Scene::InstantiateMany` to `make/performance` | row OL4 |
| `rulings-3.md` "pipelines.md" (PI1) | no docs agent builds anything else | one more build, the patch runner's `build/docs-patch` in phase B, which PI9 needs | row PI1; `pipelines.md` §6.6; `process.md` "Not interfering with the engine's work" |
| `rulings-3.md` "pipelines.md", owner question 9 | "before" pictures from the committed baselines | the sets are not committed at the pin; the planner copies them to `docs-baselines` after confirming their folders exist | `pipelines.md` §5.5; `process.md` step 14; `README.md` item 9 |
| `rulings-3.md` "site.md" (SI4) | published files have content-hash names | the committed files carry no hash (the spike's names); the site serves each under a name with the first 10 hex digits of its SHA-256 (the spike's `src/lib/images.mjs`), as the ruling on the spike's names allows | `site.md` "Pictures"; `pipelines.md` §5.7 |
| OL15 | the exported world's check moves to `make/export` | it stays in `make/large-worlds`; `make/export` names it in one sentence | row OL15 |
| OL11 | the rebinding menu stays in `make/input` | the rebinding screen is in `make/menus` | row OL11 |
| SI11, SI23 | `accTitle` and `accDescr`; four overrides | the spike's `caption` and `alt`, and its two overrides | rows SI11, SI23 |
| SI3 | a banner on `research/framework.md` §5 | the revisers did not add it (`plan/research/` is not theirs to edit); the planner added it with `rulings-4.md`; the same statement stands in `site.md`, `README.md` and `process.md` | row SI3; `research/framework.md` §5 |

## 5. The checks of the revised plan (2026-11-10)

Three checkers and this file's writer read the revised plan against the rulings and the summary. What changed:

- **The outline check** (`check_outline.py`) now checks what the plan states as fixed: each track's list against the
  sequences of R4, computed from the rows; every row's Tracks column; the part order of `rulings-2.md`; no kind I or R
  on tracks G and B; every `basics` row a primer; the W8 and W8r lists of R6; at most five page ids in a row's Needs,
  alternatives included; the Needs of pages on no track in the book's order; the own Needs of side steps; table rows
  outside a part; the `Tracks:` line as a leading list of letters; and the counts that `book.md`, `process.md` and
  `README.md` state.
- **Learner path**, within the rulings' kinds and sizes: block A's Needs follow the Coin Run chain (`make/lighting`
  needs `make/prefabs`, `make/first-script` needs `make/lighting`, `make/hud` needs `make/sound`,
  `make/play-test-debug` needs `make/hud`); `make/editor-tour` needs `start/how-to-read` and
  `start/what-an-engine-is`; `core/conventions` needs `core/first-change`, so every later page of `core` and `world`
  has the source build in its closure; `world/ecs` needs `world/what-a-world-is`; `core/frame-loop` needs
  `basics/threads`; `basics/data-structures` needs `basics/numbers`; `basics/math-vectors` needs only
  `basics/programming-2` and `basics/tools` needs `start/install`, so both side steps of track G can be read where they
  are offered; `basics/computer` needs `start/first-game` and lost what belongs to other primers; the programming
  primers teach the C++ that the SDK's calls need; `make/transforms-units` is the use home of positions, directions
  and rotations; `start/install` teaches the terminal per OS; JSON has use homes on track G; the G12 exercise moved to
  `make/gameplay-math`; `make/animation` starts from a checkpoint that holds a controller; Coin Run has a stage in
  every tutorial of block A and a practice item in each programming primer; height fog's use home is `make/look`;
  binding capture and typed text moved to `make/menus`; noise and sampling patterns moved to
  `basics/math-probability`.
- **Not changed by the revisers, because a ruling set it:** the sizes of `make/transforms-units` (C/M),
  `make/lighting` (T/M), `basics/numbers` (M) and `basics/math-change` (M), and the kind of `make/gameplay-math` (H).
  Where a checker found one of them too full, the plan moved content (fog to `make/look`) or gave formulas as recipes
  (`make/gameplay-math`). The use half of physics tuning stays in `make/physics` (OL11). **The planner then changed
  the ruling** (`rulings-4.md`, R7 and R8): the first three pages and `make/input` are L, and `basics/math-change`
  is split into `basics/math-change` (L) and `basics/math-interpolation` (M). `make/gameplay-math` stays H/L.
- **Pictures**: `site.md` "Pictures" and `pipelines.md` §5.7 now give one set of names: `scripts/encode-figures.mjs`,
  committed names without a hash, served names with 10 hex digits, the ignored `originals/` folder, and
  `figures.py archive --tag <tag>` writing a `.tar`.

## 6. After the planner's read (`rulings-4.md`)

The planner read the revised plan and ruled on what §4 and §5 left open. What changed in the plan's files:

- **Sizes (R7)**: `make/transforms-units` C/L, `make/lighting` T/L, `make/input` T/L, `basics/numbers` P/L.
- **The split (R8)**: `basics/math-interpolation` is new, after `basics/math-change` in the part and on tracks B
  and E; `basics/signals`, `world/interpolation` and `animation/clips` need it; `book.md`'s one-home table has a
  row for each of the two primers.
- **`editor` (R9)**: `editor/projects` comes after `editor/recovery` and needs `editor/saving`.
- **§4's rows (R10)**: all accepted; the SI3 banner is added.
- **Counts**: 332 pages (26 primers); about 1,360,500 words; wave 1 holds 59 pages and wave 2 about 130,000
  words. `book.md`, `README.md`, `process.md` and `tracks.md` state them, and `check_outline.py` passes.
