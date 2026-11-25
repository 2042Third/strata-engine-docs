# For the planner: settling the allocation

Made by `digest` (workflow B, step 4) from the 20 critics' files (all 344 findings, word for word, in
`../completeness.md`), the six proposal files beside this one and `docs-work/B/outline/CHANGES.md`. `critic-<inventory>-<n>`
is a finding; `sizes`, `needs`, `duplicates`, `learner`, `systems`, `tools-render` are proposal files, the last three
answering `<unit>-q<n>`. Nothing is applied; my scripts are in `docs-work/B/digest/`. No agent failed.

## 1. Numbers

Findings: 344 from 20 critics, 26 must, 152 should, 166 could. By kind: missing-item 133, thin-home 61, stale-item
49, duplicate 39, other 32, wrong-home 19, order 11. The 26 musts: stale-item 14, missing-item 8, thin-home 3, other 1.
Every critic file parses (one table, seven cells a row, ids without gaps).

| Proposal | Rows | Classes |
| --- | --- | --- |
| `sizes.md` | 332 pages | keep 250 (86 of them `over` in coverage.md), larger 51 (40 M to L, 10 L to XL, 1 S to M), smaller 2, split 3, kind R left out 26 |
| `needs.md` | 114 Assumes rows | add-need 85 (47 Needs cells, 29 on part pages and 18 on reference pages; 4 part lines follow), other-teacher 19, earlier-home 3, self-taught 6, planner 1 |
| `duplicates.md` | 39 merges | 29 move a term or rule home and change no prose; 9 take an excerpt, rule or concept off a second page (100 to 300 words each); 1 adds about 30 words |
| questions (3 files) | 231 questions | 162 follow from a rule, 69 are the planner's; size 30, need 41, duplicate 31, rule 10, seed 18, outline 11, content 56, check 9, other 25 |

The trial outline (`docs-work/B/outline/plan/`, sizes' and needs' edits): `check_outline.py --counts --words --waves`,
run again by me, exits 0 with no problem. 335 pages (332 now), 29 primers (26); S 8, M 124, L 176, XL 27 (9, 161, 144,
18); track G 52 and 2 side steps, B 52 (49), E 264 (261), no track 29; 1,480,000 words at the budgets (1,360,500), G
212,500, B 224,500, E 1,187,000; wave 1 the largest, 62 pages and 290,500 words. `check_allocation.py check` on the plan:
exit 0. The trial's `process.md` predates commit `cbe2d2d` (10:41: the fox erratum, R25), so its counts go into the
current file. Not in the trial: `basics/git` (tried apart in `sizes/alt-tools/plan`: passes), D2's merge, sizes'
option (b), `make/lamps` at L, the reorders of D5.

The critics' added words against rule S (`crossref.py` attributes each "about N words" to a page; I read every page it
flagged): 7 pages pass the top of their range once the findings are applied, and 4 more reach it.

| Page | Size by sizes.md | Estimate | Added by | After |
| --- | --- | --- | --- | --- |
| `light/sun-shadows-1` | L | 6,500 | critic-render-scene-1, critic-render-direct-2, -9, -20 | about 7,200 |
| `assets/importing` | L | 6,500 | critic-editor-core-8 and critic-worlds-runtime-9 (one content stamp), critic-assets-6, -9 | about 6,800 |
| `worlds/runtime` | L | 6,500 | critic-worlds-runtime-1, -11 | about 6,690 |
| `draw/gpu-driven` | L (from XL) | 6,300 | critic-render-scene-2, -3 | about 6,630, XL's range again |
| `light/material-data` | M | 3,900 | critic-render-direct-10 | about 4,100 |
| `gpu/upload-queue` | M | 4,000 | critic-render-core-5, -9 (the Present stage moves in) | about 4,200 |
| `core/debugging` | M | 3,900 | critic-foundation-5, -6 | about 4,060 |
| `editor/stepping`, `physics/scale-streaming`, `ui/contract`, `editor/camera-viewport` | M | 3,200 to 3,900 | audio-input-3, -4; physics-8; gameui-6, -11, -14; editor-core-1 | 3,900 to 4,000 |

## 2. What follows from the rules

**Sizes (rule S).** 56 changes, listed in `sizes.md` "Changes" and applied in the trial: units `basics-b` 8,
`basics-a` 6, `editor-ui` 6, `core` 5, `assets` 5, `engineering` 4, `gpu` 3, and 1 or 2 in 13 more. Where an agent says
S gives a bad result: 34 pages planned within 5% of their top, 10 exactly at it (sizes item 1; systems item 6);
`basics/tools` (sizes 2); `draw/gpu-driven` shrunk to L at 6,300 (sizes 4), which the critics then push back over;
`make/lamps`, a W8 page at 3,800 that phase B will fill (sizes 5, learner 7); kind R, which cannot be sized by prose
(sizes 7, reference-q1); and section 1's table, since S was applied before the critics added words. The critics' own
size worries were measured against budgets; under S these need nothing: `editor-ui/imgui` 5,650 (L),
`physics/building-bodies` 5,450 (L), `light/atmosphere` 5,320 (L), `indirect/ibl` 5,810 (L), `indirect/probes` 7,600
(XL), `gpu/vulkan-nvrhi` 7,790 (XL), `automation/mcp` 5,880 (L), the assets part. One exception: D4.

**Needs (rule N).** The 85 must rows become 47 Needs cells (`needs.md` "Needs that change", applied in the trial): 0
must rows stay outside a closure, no row loses its teacher, 77 helps rows enter one. 28 Assumes cells in 9 units get a
new teacher and `start`'s row goes (`needs.md` "Rows without a teacher"). Bad results named: reference pages (D9);
`start/coming-from`'s row (D10). N2 and N3 also settle, without a decision, the critics' helps rows for order slips
(critic-assets-14, critic-render-direct-17, critic-render-scene-5, critic-scene-ecs-12, critic-physics-16,
critic-render-image-14) and wrong teachers (critic-editor-ui-12, critic-editor-core-14, critic-scene-ecs-13,
critic-scripting-13; world-q7, world-q8, basics-a-q11, basics-b-q4, -q5).

**One home (rule D).** `duplicates.md` lists 39 merges; 12 of its groups are named by critics too (headless, sequence
lock, origin rebasing, `AssetPin`, CRC-32C, apply and revert, content stamp, backpressure, hysteresis, Game view,
raycast, volatile constant buffer). Bad results named: 12 merges whose teacher stands after the page that keeps a link
(duplicates item 4); term homes on which agents disagree (D33). Rule D lets a make page and an E page both hold home
rows on one feature (scripting-q2, make-a-q6); the glossary still gives each term one home (D31).

**Findings that only need applying.** Stale items are reworded in the rows that repeat them; missing items become new
items with the evidence the finding gives at the pin; thin homes widen a row's take; order slips get helps rows. Of the
26 musts, 15 need no decision: critic-audio-input-1 and -2, critic-build-test-2 and -3, critic-editor-core-2,
critic-editor-ui-1 (5,650 stays inside L), critic-gameui-1, critic-physics-1, critic-render-core-1 (7,790 inside XL),
critic-render-direct-1, critic-scene-ecs-1 (its "basics/math-matrices `new:22`" is `basics/math-bases` after the
split), critic-scripting-1, -2, -3, critic-worlds-runtime-1. The other 11 are in D3, D13 to D18, D23 and D34. The
162 questions answered by a rule are taken as their rows say, unless a decision below changes them.

## 3. Decisions

**D1. Split `basics/git` off `basics/tools`** (sizes item 2; basics-a-q1). S2 gives L at 6,200, but about 2,900 words
are git, which neither track G's side step nor track B's reading before `make/first-script` needs. Options: L whole; or
`basics/tools` (M, about 3,300) and `basics/git` (M, about 2,900) placed after `basics/debugging`, with
`core/first-change` and core's part line needing `basics/git` (tried: check passes, 336 pages, B 53, E 265).
Recommend the split: both tracks read less before their first program, nothing is cut. Touches outline-1.md, tracks.md,
`basics-a`, `core`, needs.md:143's teacher (git worktrees) and every count.

**D2. Merge `draw/visibility-feedback` into `draw/gpu-driven`** (sizes item 4; draw-q5; critic-render-scene-2, -3).
Sizes makes gpu-driven L (6,300) and keeps visibility-feedback S at its top (2,250); the critics then add about 330
words to the first and a sentence and a test to the second. Options: (a) one XL page of about 8,300 words, the Needs of
`draw/mip-streaming`, `animation/culling` and animation's part line naming gpu-driven; (b) two pages, gpu-driven XL
again by S2 and visibility-feedback M. draw-q5 opposes a merge only because of those Needs, which (a) renames.
Recommend (a): the counting pass writes the feedback, so one page holds both with room. Touches `draw`, `animation`.

**D3. The sun's casters and `light/sun-shadows-1`** (critic-render-scene-1, must; critic-render-direct-2, -9, -20;
light-q2). No page teaches how casters are culled and drawn into the cascades on either path: draw.md:657 and
light.md:802 send it to each other. The page is at L's top before this. Options: (a) XL by S2, with a casters section
(about 450 words); (b) the split its Fit line offers (light.md:806-808): "Sun shadows I: stable cascades" (L) and "Sun
shadow casters and caches" (M); (c) a home on `draw/gpu-driven`, which comes before cascades: no. Recommend (a): S2
gives it and no page is added. Either way light.md:802's Leaves out line goes and gpu-driven keeps one forward sentence.

**D4. Sizes once the findings are in, and pages at their top** (sizes items 1 and 5; systems item 6; learner 7;
critic-editor-core-1). Apply S2 to the estimates with the accepted additions: `assets/importing` and `worlds/runtime` L
to XL; `gpu/upload-queue` (its own Fit asks L), `core/debugging`, `light/material-data` (unless D5's third reorder) and
`editor/camera-viewport` (critic-editor-core-1 asks L at 3,900) M to L; `scripting/tutorial-host-function` M to L if
D38 adds the scene service (about 4,400). For the 10 pages exactly at a top, sizes recommends option (b), one class up
now (about 23,500 words), and `make/lamps` L now. Recommend all of these, and that the briefs of the other 24 near-top
pages count their sections first. Counts and waves then come from `check_outline.py --counts --words`.

**D5. Orders inside parts.** (1) ui: layout, contract, input, text, drawing, with `ui/input` a Need of `ui/text`
(ui-q2; critic-gameui-3's new item needs focus first); (2) `editor/command-scripts` before `editor/journal`, as
rulings-2.md:150-152 had it, and `automation/agents` needing `editor/journal` (editor-q2); (3) `light/reflectance`
before `light/material-data`, so F0 comes before the 0.04 rule (critic-render-direct-16; or move rule 586 and half of
excerpt 435); (4) `draw/render-scene-gpu` after `draw/batching` (critic-render-scene-5; or two helps rows); (5) the
WindZone chain in one line: `editor/tutorial-command` needs and starts from `scripting/tutorial-host-function`
(editor-q7, capstone-q1). (1), (2) and (5) passed check_outline on the agents' copies; (3) and (4) were not tried.
Recommend 1, 2, 3, 5 and the helps rows for 4 (the critic's own first choice).

**D6. Titles and outline cells.** Retitle `automation/mcp` "StrataCLI and its MCP server" (critic-automation-3,
outline-4.md:140) and `editor/projects` to name scenes opening (critic-editor-core-15, outline-4.md:81); the row of
`appendix/credits` for R20 to R22 (rulings-6.md:339-340); From cells: `start/install` drops the `script.status` check
(start-q1, replacing rulings-2.md:45), `make/automated-playtests` (make-b2-q4), `basics/programming-1` and book.md:125
for `Key::Space` (basics-a-q3), `image/why-post` (image-q2), `indirect/seam` (indirect-q2). Recommend all: no page moves.

**D7. The concepts with two teachers** (needs item 1; basics-a-q9, -q10; basics-b-q12, -q13; engineering-q4;
indirect-q6). Agreed: static initialization `basics/build`, structs as bytes `basics/bytes`, `std::filesystem::path`
`basics/cpp-modern`, calling a C library `basics/cpp-generic`. Open: the geometric series on `basics/math-interpolation`
(needs, tools-render 12, critic-render-direct-7's new row) or `basics/numbers` (learner 11); regular expressions on
`basics/data-formats` (needs, about 350 words), the text half of `basics/bytes` (learner, which the split makes
data-formats) or `core/reading-code` (tools-render 11); reading Python taught where it is quoted (needs, learner) or on
`core/reading-code` (tools-render). Recommend math-interpolation (its users' angle; numbers at 6,400 gets room),
regular expressions on data-formats (in every later closure), Python where quoted.

**D8. The Graphics Quality presets before `make/quality`** (needs item 5; make-b2-q2; light-q6). `make/lamps`,
`make/reflections`, `make/gi` and `make/look` each use one preset fact (helps). Options: a forward link to
`make/quality`; or about 250 words on presets and the quality chip on `make/lighting` (learner). Recommend the links:
the presets are taught once, and the light pages do the same (light-q6).

**D9. Reference pages and their Needs** (needs items 2 and 3; reference-q2; tools-render 6). The trial gives 18
reference pages a Need each, so the part line lists 17 pages, and three Needs are make pages for pages written for E1.
Options: (a) keep them, with `editor/commands`, `world/what-a-world-is` and `editor-ui/shell` in place of
`make/commands`, `make/scenes-entities` and `make/editor-tour`, and a site rule that `reference/index` shows no "Before
this part"; (b) exempt pages on no track whose Needs are `-` from coverage §6 and from `term-source`, and drop the 18.
Recommend (a): it is applied and checked and also fixes the strip that shows `reference/script-api` as "Before you
start"; add (b)'s term-source exemption for kind R only if a reference page still fails it.

**D10. Needs rule N does not ask for** (start-q3, editor-ui-q2, basics-b-q3, make-b1-q5, make-b2-q3, editor-q1).
Each passes the check: `start/install` gains `start/how-to-read`; `editor-ui/imgui` gains `editor-ui/immediate-mode`;
`basics/math-geometry` gains `basics/math-projection` (its row raised to must); `make/commands` and `make/performance`
gain `make/animation` (with D40). Two disagreements: `basics/numbers` on `basics/math-matrices` (needs, in the trial)
or on the two pages that ask (learner); `editor/camera-viewport` gains `editor/commands` (needs) or `editor/play-mode`
(editor-q1). Recommend the four additions and the trial's two choices. `start/coming-from`'s must row with `?` names
its reader: recommend deleting it and putting the fact in the page's "what must be true first" (needs, basics-a-q10).

**D11. Inactive reasons' home** (world-q2; critic-scene-ecs-17). book.md:344 homes them on `editor-ui/inspectors`
(part 19); five earlier E pages link forward, and the home assumes them from `world/reflection` at must. Options: split
the row, `SetInactiveReason` with its rule and term (`scene-ecs:198`, `531`, `654`) on `world/reflection` (about 300
words, XL by sizes) and the display on the inspectors page; or name `editor-ui/inspectors` in the two Assumes rows.
Recommend the split: five forward links go. Touches book.md:344, `world`, `editor-ui`, `image`, `indirect`, `ui`.

**D12. Where `Process` is taught** (critic-foundation-4). It is homed on `editor/script-builds` (6,500, L's top) but
serves the CLI's launcher, the external editor and the tests' helpers, and `automation/sessions` assumes it from
`core/platform` at must. Options: home on `core/platform` (about 250 words, 5,050 inside L, room freed on script-builds);
or name `editor/script-builds` at automation.md:449. Recommend the move (`editor` passes, `core` takes).

**D13. `make/animation`'s layout** (critic-animation-1, must; -7; -11). Root motion drives a CharacterController only
when the Animator is on the controller's entity; the tutorial, like the sample, puts the robot under the player; events
reach only scripts on the animator's entity; step 9's WhenVisible cannot show anything on the followed player.
Options: keep the sample's layout and teach the consequences (step 8 on the model's root carrying the controller, the
drift as "If you do not see it", Footsteps on the robot, step 9 on a second robot); or one entity. Recommend the
sample's layout (readers compare with `Samples/ThirdPerson`): about 300 words, 6,340 inside L.

**D14. Simulate shows skinned meshes in their bind pose** (critic-animation-2, must, read from code only). The
Animation system does not run in Simulate and the preview serves the edited scene; `animation/editor` plans "the editor
always installs a preview". Recommend one Simulate capture in the pin's editor first (figure agent), then one sentence
each on `animation/editor`, `animation/system` and `make/play-test-debug`, and screenshot 2 made in Simulate; optionally
tell the engine's agents that the Simulate copy gets no pose provider.

**D15. What a source build needs** (critic-build-test-1, must; -17). No page names the Linux development packages
GLFW and nfd need, the minimum compilers, CMake 3.25, Slang's first download or the Vulkan SDK as optional, so a Linux
reader's first configure on `core/first-change` fails. Recommend a new feature item on `core/first-change` (Linux tab,
about 150 words; `build-test` passes it to `core`) and the minimums in `engineering/building`'s "What must be true
first" (about 80). The other place, `start/install`, serves readers who build no engine.

**D16. How `viewport.capture` works** (critic-editor-core-1, must). The book's figures come from it, three units
assume `editor/camera-viewport` teaches it, and no inventory surveyed it. Recommend the critic's section "Captures"
(about 700 words, code row `EditorViewportCommands.cpp:808-845`) on that page, sized L (D4). No agent proposed a page.

**D17. Registries that never freeze** (critic-foundation-1, must; core-q4). Only the component and settings
registries freeze; six more stay open. The page's Covers, rule and term, book.md:166 and three Assumes rows
(`assets/what-is-an-asset`, `world/systems`, `worlds/grids`) say all freeze. Recommend book.md:166 "registries that
open and accept; the component and settings registries then freeze", the two kinds taught on `core/layers-registries`,
figure `scene-ecs:447` labelled as the component registry's, an erratum row, and the three rows reworded.

**D18. The license and the fox, left to this settlement** (critic-book-1, -2, must; critic-animation-3, must;
rulings-6.md R20 to R22, its item 15 and lines 339-340; tools-render 17). No page holds the fox's full credit
(process.md:104), R21's permission (`appendix/credits` still calls the license open) or `start/how-to-read`'s sentence,
and `animation/problem` names a Showcase fox that does not exist. Recommend one pass: `appendix/credits` takes the
statement, the permission and the fox's credit as new items; `start/how-to-read` one sentence; `make/project-coin-run`
step 8 a link; screenshot 11 of `animation/culling` and every Open World figure with a fox a caption; "the Showcase fox"
goes. Touches outline-4.md, `appendix`, `start`, `make-a`, `animation`, `make-b2`, `worlds`.

**D19. Command-only steps on track E** (assets-q3, physics-q2, tools-render 1). R11 (rulings-4.md:71-73) against
process.md:58-59, style.md:691-695 and the strips check (style.md:789), all from one commit. Both agents recommend R11
on track E (E1 has read `start/how-to-read`), steps still moved on G and B. Recommend R11 and the three places amended.

**D20. `make/automated-playtests` before `make/commands`** (make-b2-q1, learner 9, tools-render 2). Both recommend
that style.md §10 accept `make/automated-playtests` as track G's teacher of running a command script (only
`--commands` runs one), `make/commands` staying StrataCLI's. The swap also passes the check but moves JSON's use home.
Recommend the rule's change; the strips check follows.

**D21. Starting state on primers** (tools-render 3; basics-b-q14). R11 and README:212 put every checkpoint in
Starting state; README rule 2 and check_allocation.py:1045-1047 allow it on T and H only, so the primers wrote it in
Covers. Options: the check accepts Starting state on kind P; or the contract says Covers for primers (learner). Recommend
the check change: one place per page for the briefs and the list of checkpoint downloads.

**D22. Size rules that disagree** (sizes 7; reference-q1; make-c-q2; gpu-q8; systems item 6). style.md:186 measures
prose, which fails 21 of 22 reference pages (glossary and term-index fall below S's floor); it lets a writer over the
range "cut", against R7; outline-1.md:32-33 calls XL "8,000 or more, never several pages". Recommend no size check for
kind R (the 4 appendix R pages too), "ask for the next size" in place of "cut", and outline-1.md:32 and book.md:85 "XL
about 8,000 (6,501 to 10,000); past 10,000 a page splits by R7"; check_outline.py:712 reads that sentence.

**D23. Errata in process.md's table** (assets-q5 says no; gpu-q6, automation-q6, light-q4, indirect-q5, image-q6,
appendix-q6, make-a-q9, make-c-q5, capstone-q8, critic-render-image-1, critic-assets-9, critic-scripting's forPlanner
2 say yes). About 25 proposed rows: the engine's own docs and comments wrong at the pin (e.g. DeveloperGuide.md:4031 on
the players' AntiAliasing row, the skill's "no `--help`", `TetrisCommands.json.in:28`, `Wander.cpp`'s comment), and
inventory slips (`gamedev:322`, scripting's concept 16, `ImportRecordStore.h:85-163`). The table already holds one
inventory slip (`gameui.md:44`). Recommend both kinds in the one table, since writers read the inventories as background
(process.md:117-119); the 49 stale-item findings also correct the rows themselves.

**D24. cpp-features homes** (basics-a-q15). style.md:645 and :648 home pointers and `std::optional` on cpp-memory and
cpp-modern, but programming-3 teaches both for use (book.md:125), so the lint would ask G pages for asides. Recommend
`->`, `nullptr`, `*` in a type, `std::optional`, `has_value` and `value_or` on programming-3 (cpp-features.json, style.md).

**D25. Concepts homed on how-to pages** (critic-render-core-2). style.md §7.5 gives a how-to two sentences of why and a
link; `render-core:304` (validation layers) is homed on `gpu/debugging` with no concept page to link. Recommend its move
to `gpu/vulkan-nvrhi` (about 250 words) and a check warning for concept items homed on kind H. Today 10 concept items
are homed on 8 H pages (prep's `where/*.tsv`): one each on `gpu/debugging`, `physics/tuning` and
`engineering/contributing` (track E), the other 7 on make pages.

**D26. SDK classes and generated pages as homes** (critic-scripting-4 and its forPlanner 1; scripting-q1;
reference-q9). Seven SDK classes are homed on `reference/script-api` while their twins are homed on teaching pages;
seven more have no twin. Options: rule D allows both (systems: the reference lists facts); or each home moves to the
teaching page with the reference as a link (critic). Recommend the move: a generated page has no prose and teaches
nothing; the seven without twins go to the pages the critic names (`make/scripting-scene`, `basics/programming-1`,
`make/levels-saves`, `make/recipes`, `make/timers-events`).

**D27. Exercises of world pages** (critic-scene-ecs-6). Four world pages list no exercise and five internals pages no
trace exercise, which style.md requires. Options: the allocation adds them now (about 250 words each, one example per
page in the finding) or the briefs do. Recommend now, so the sizes count them. No agent checked other parts for this.

**D28. Not-done entries a game maker meets** (critic-book-4, -5; book.md:348). Most rows name no make page, and tracks
G and B never read I and C pages. Recommend the rule "an entry whose subsystem has a make page names it too", and the 15
entries the findings list (`make/look`, `make/quality`, `make/input`, `make/menus`, `make/physics`, `make/sound`, about
40 to 50 words each), with `make/sound`'s Streamed clip said to hold its encoded bytes in memory.

**D29. Seed: log, build, debug information** (learner 1 to 3; from-workflow-a final.forPlanner 6). New definitions
pass check_seed (scratch `seed-three.json`): log on `start/install` (or `start/first-game`), build on
`start/first-game`, debug information on `basics/debugging`. Recommend these, worded as questions-learner.md:126-141,
and start-q5's moves (editor to `start/welcome`; scene, entity, component to `start/first-game`; `seed-all.json` passes).

**D30. Seed homes already moved, and the counts** (learner 4, 5; sizes, splits). Keep hash, hash-function,
compile-time and integral where workflow A moved them; fix book.md:134, :137, :143, :147 and pipelines.md:1102;
basics-a `new:188` and basics-b `new:100` become use. Terms: 1,587 in 1,567 entries, not 1,592 (outline-4.md:211,
pipelines.md:1106, process.md:483, site.md:820); the seed has 400 entries, not about 300 (README.md:94,
pipelines.md:1099, process.md:478, site.md:820). The splits move seed words (sizes.md:151, :209). Recommend all.

**D31. The glossary's format and merge** (learner 6; tools-render 10; critic-scene-ecs-7; critic-gamedev-11;
critic-audio-input-18; basics-b-q8). The seed lacks the `use` field book.md:110 and style.md:290 need;
pipelines.md:1107 (seed wins) and README step 5 (allocation's homes) disagree for entity, component, scene, project,
UUID and sparse set; 70 gamedev terms have a twin homed on another page (172 pairs). Recommend an optional `use` in
pipelines.md §9 and check_seed.py; step 5 written down: one entry per term, the seed's entry wins, a make page is the
use of its twin's entry (book.md rule 5), else the home is book.md's row or the page in the closure of every page that
marks it. Lists: `docs-work/B/critic-gamedev/term-twins.txt`, `docs-work/B/duplicates/judge_c.txt`.

**D32. Words with several meanings** (critic-editor-core-13, critic-gamedev-11, critic-scene-ecs-8,
critic-worlds-runtime-19, critic-render-core-16, duplicates' 72 groups, basics-a-q13, basics-b-q9, automation-q3).
book.md rule 6 lists six words; the agents name about 40 more (batch six meanings, trigger and snapshot three, token,
instance, transform, interpolation, sample, frame, layer, pin, cook, raycast, constant buffer, stack, heap, thread).
Recommend that rule 6 states the principle, one qualified entry per meaning, with its list as examples, and that step 5
takes judge_c.txt's homonym groups and the critics' lists.

**D33. Ten homes in dispute** (duplicates' choice first; section 4). Backpressure `automation/rpc-server` or
`assets/loading`; hysteresis `worlds/streamer` or `input/gamepads`; content stamp `editor/thumbnails` or
`assets/importing` with `assets:145`; Game view `editor-ui/scene-view` or `editor/play-mode`; Dist `engineering/building`
or `core/first-change`; draw list `draw/batching` or `gpu/geometry-pool`; content scale `editor-ui/ui-scale` or
`core/windows-events`; infinite far plane `gpu/coordinates` or `core/math`; raycast one entry or two; the sequence lock's
excerpt. Recommend one principle: book.md's row, else the page that teaches it from zero, the earlier where two do. It
gives the second side for all but draw list (`draw/batching`), the far plane (`gpu/coordinates`) and the sequence lock
(duplicates', book.md row 168); a page outside the home's closure says the word in one sentence.

**D34. Definitions to correct before step 5.** kinematic body (critic-physics-10), headless and no-gpu
(critic-editor-core-3), content stamp (critic-worlds-runtime-9), faulted module (critic-scripting-20), watchdog
(critic-scripting-7), decomposition (`scene-ecs:630`, critic-scene-ecs-1), registry (critic-foundation-1), constant
buffer as two entries (critic-render-core-16), entity naming both classes (critic-scene-ecs-2). Recommend all.

**D35. Rows of "What Strata does not do"** (about 40, all critic ids without the prefix). MCP tools only (automation-2);
key names ignore the layout, unmapped pads (audio-input-6, -5); shortcuts, one theme (editor-ui-7); one view, no
sequencer, devices per player on `make/input` (gamedev-2, -5, -4); stay events, rolling resistance (physics-7, -14);
clouds, cookies and IES, per-entity materials (render-direct-11, -12, -13); field types, OnEnable, coroutines
(scripting-14, -15); patch packs (worlds-runtime-15); loading-screen budgets (assets-5); a format check (build-test-15);
crash dumps (foundation-6); GPU choice, main-thread recording (render-core-10, -12); probe gizmo, cube maps
(render-indirect-6, -10); script breakpoints (basics-a-q5); appendix-q2's two; book-3's eight; widened rows (book-22,
-23; physics-9). Recommend all, each with its evidence run again at the pin.

**D36. The one-home table's scope** (critic-book-6 to -11, -14 to -21, its forPlanner 2; critic-book-12, -13, -24,
-26). About 25 feature areas, and pages that 6 to 19 Assumes rows name as teachers, have no row: the frame loop,
windows and layers, startup, the graphics device, the script ABI, system and loading, the RPC server and security,
the image effects, the glTF importer. Recommend rows for book-6 to -11 at least and one sentence in book.md that says
what the table lists; plus the UUID row (64 bits), decision 5's `:::why` on `light/units-exposure`, the evidence cells.

**D37. Findings for the engine's work** (critic-foundation-7; critic-audio-input-7, -8; critic-worlds-runtime-4,
-10; animation-q7; basics-a-q5; appendix-q6; critic-gamedev-6; critic-build-test-5, -15). Exit code 0 after an
unhandled exception (an engine fix of one line and a test, recommended by the critic); mouse units on scaled displays;
`PrefabSync` and cells; `IsLoadedAround` and mesh colliders; static `AssetManager` uses against AGENTS.md; `-g` for
GCC and Clang scripts. Recommend: report each as pipelines.md:607 does; pages state the pin's behaviour; the owner
decides the exit-code fix and `-g` (tier 1 of v0.8.1, with a not-done row until it ships).

**D38. The WindZone chain** (scripting-q5, world-q6, assets-q4, capstone-q3 to -q7, world-q5, critic-book-27).
Recommend: a scene service on `scripting/tutorial-host-function` (Scripting may not include Physics,
Layers.json:76-78); `assets/extending` keeps the text asset; the spec as a patch under `Docs/Plans`; a Directional zone
pushes along its local -Z; suite `Physics.WindZone` (pipelines.md:939, scripting.md:818); `editor/tutorial-command`
adds the `wind.` prefix to `c_PrefixToolsets`; the patch runner builds `StrataEditor` for pictures; the gizmo built once
(`gpu/debug-drawing`'s exercise becomes the chain's, book.md:578); the layering experiment needs a run that expects failure.

**D39. Coin Run and block B's course** (make-a-q2, -q3, make-b1-q3). Recommend: the coins' bob becomes the first step
of `make/scripting-scene` (book.md:556); block A how-tos end `## Result` with their end state's download (one sentence
in style.md §7.5); block B shares the obstacle course, each page with its own downloadable start (book.md:568-570).

**D40. Items nobody took, and moves in block B** (systems 13 to 15; learner 12; make-b2-q5; appendix-q8). Recommend:
`animation:190` to `make/commands`, `animation:520` to `make/performance`, `render-core:668` nowhere as a repeat of
`render-scene:559`; the day and night scripts (`gamedev:386`, `:549`) to `make/reflections` beside `render-direct:645`;
networking and game-AI absences homed on the appendix pages, with `automation/json-rpc` and `make/patterns` linking.

**D41. Checks to run before writing** (critic-animation-2, critic-audio-input-7, -16, critic-worlds-runtime-4, -10,
ui-q6, automation-q4, animation-q8, basics-a-q5). Nothing in this run was run. Recommend: the figure agent captures
Simulate, the Game view without a camera, the launcher card and the foxes' WhenVisible recipe; an engine agent tests
`PrefabSync` with cells, the pending window of mesh colliders, mouse units on a scaled display and breakpoints on Linux
and macOS; the writer of `audio/engine` reads miniaudio's device loss. Each page's wording waits for its check.

**D42. Generated tables and figures** (tools-render 7 to 9; reference-q3, -q6, -q7; appendix-q7; critic-foundation-3;
critic-render-scene-3 and its forPlanner 2; critic-animation-12; critic-worlds-runtime-17, -18; critic-physics-17, -18;
critic-render-indirect-7, -15; critic-render-image-16, -17; critic-gameui-2). Recommend pipelines.md §7.1 rows for terms,
further reading, the CPU stages and a `perf.<name>` key per budget, §7.2's `game-makers.json`; one capture per figure
planned twice; `world/systems`' frame timeline reused by physics and worlds; the look-dev shots named in figure rows;
diagrams for switches tier 2 lacks, and one request to extend it.

**D43. Smaller choices.** Letterbox for the post-effect tutorial (image-q8); quote only Roadmap 1645-1653 on
`animation/limits` (animation-q6); `StringUtils::ToUpper` for `core/first-change` (core-q6); book.md:361 "invisible bit
for bit" for GI (appendix-q3); book.md:289, :296 split by rule 3 (physics-q1, audio-input-q4); core.md:1274 drops
`AABB.cpp` (draw-q3); pipelines.md:1195 and process.md:573 name `gpu/debugging` (gpu-q7); idle throttling on
`make/editor-tour` or `make/performance` (section 4); whether wave 1 (290,500 words) is cut in two (sizes 9).
Recommend as the agents propose; for idle throttling, `make/performance`, where the frame time is read.

## 4. Proposals that collide

Found by `crossref.py` (items and pages that two or more files name: 72 items, then read) and by reading. Collisions
whose two sides a decision already names: visibility feedback (D2), the geometric series, regular expressions and
Python (D7), presets before `make/quality` (D8), reference pages (D9), the Needs of `basics/numbers` and
`editor/camera-viewport` (D10), inactive reasons (D11), Starting state on primers (D21), inventory errata (D23), SDK
classes (D26), the ten homes of D33 (backpressure, Game view, infinite far plane and raycast among them), idle
throttling on track G (D43). The others:

| Matter | One side | Other side | Note |
| --- | --- | --- | --- |
| Hysteresis | duplicates: `worlds/streamer` | critic-worlds-runtime-19: `input/gamepads` | neither page is in the other's closure, so the other says it in one sentence |
| Content stamp | duplicates: `editor/thumbnails` | critic-editor-core-8, critic-worlds-runtime-9: `assets/importing` | the critics' home is at L's top already (D4) |
| Dist | duplicates: `engineering/building` | engineering-q2: `core/first-change` | with the first, term-source fails pages of parts 3 to 20 |
| Draw list | duplicates: `draw/batching`, with the feature rows | editor-ui-q4, draw-q6: the term on `gpu/geometry-pool` | D33 keeps both feature and term on `draw/batching` |
| Content scale | duplicates: `editor-ui/ui-scale` | tools-render 10: `core/windows-events` | editor-ui.md:198 and :260 already assume it from `core/windows-events` |
| Sequence lock excerpt | duplicates: `core/jobs` keeps `SequenceLock.h`, audio quotes its use | critic-audio-input-11: `core/jobs` shows `ThreadActivity`, audio keeps the lock | opposite moves of one excerpt |
| CRC-32C, HMAC, UUID | duplicates, critic-scene-ecs-7, basics-a-q7, automation-q5: `basics/bytes` | sizes: `foundation:643` and UUID go to `basics/data-formats` | written for the page before the split; read data-formats |
| Regular expressions | learner: the text half of `basics/bytes` | sizes: reading text into tokens moves to `basics/data-formats` | one page once the split lands |
| Decomposition | critic-scene-ecs-1: `basics/math-matrices` keeps `new:22` | sizes: `new:22` moves to `basics/math-bases` | read math-bases |
| `draw/gpu-driven` | sizes: XL to L at 6,300 | critic-render-scene-2, -3: about 330 words more | the shrink is undone (D2) |
| Action maps on track G | critic-audio-input-10: a step on `make/input` or `make/menus` | critic-gamedev-4: a paragraph on `make/input` | one addition of about 200 words on `make/input` (5,390, L) |
| Script crash and play | critic-editor-core-6: about 100 words | critic-scripting-6: about 150 words | one addition to `editor/play-mode`, counted once |
| Fixed steps, never frames | duplicates: the rule moves to `core/time` | critic-audio-input-3: input holds also count frozen frames | `editor/stepping` keeps the exception with its link |
| Present | critic-render-core-9: the stage's home to `gpu/upload-queue` (its forPlanner: `core/profiling`) | duplicates: the term on `gpu/how-a-gpu-frame-works` | three places; choose the stage's and the term's homes together |
| Frame timelines | critic-physics-17 | critic-worlds-runtime-17 | both reuse `world/systems`' timeline: one figure, two overlays |

Moves onto pages at their top (sizes item 1): `assets/importing` (critic-assets-6, -9, critic-editor-core-8, -10,
critic-worlds-runtime-9), `light/sun-shadows-1` (D3), `worlds/runtime` (critic-worlds-runtime-1, -11),
`gpu/upload-queue` (critic-render-core-5, -9), `draw/visibility-feedback` (critic-render-scene-2), `gpu/debug-drawing`
(critic-gameui-18, no words; critic-book-27), `make/automated-playtests` (critic-scripting-18, critic-audio-input-3).
Off one: critic-foundation-4 and critic-scripting-6 take words off `editor/script-builds`.

## 5. Work for the appliers

Per unit: findings that name a page of the unit (m/s/c; a finding naming pages of several units counts in each, and 8
name no page), sizes' changes (larger, smaller, split), duplicates' merges, and needs' teacher cells (`units.tsv`).

| Unit | m/s/c | Sizes | Merges | Teachers | Unit | m/s/c | Sizes | Merges | Teachers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `start` | 1/0/1 | 2 | 0 | 1 row goes | `physics` | 1/9/11 | 1 | 2 | 0 |
| `make-a` | 6/17/16 | 0 | 0 | 0 | `animation` | 4/6/9 | 0 | 0 | 0 |
| `make-b1` | 3/21/7 | 0 | 1 | 0 | `audio-input` | 1/6/12 | 1 | 3 | 4 |
| `make-b2` | 1/17/7 | 1 | 0 | 4 | `scripting` | 3/10/5 | 0 | 1 | 0 |
| `make-c` | 0/0/1 | 0 | 1 | 0 | `ui` | 1/8/6 | 2 | 2 | 0 |
| `basics-a` | 1/1/0 | 4, 0, 2 | 2 | 0 | `worlds` | 1/9/9 | 1, 1, 0 | 4 | 2 |
| `basics-b` | 1/2/0 | 7, 0, 1 | 3 | 0 | `editor` | 3/16/11 | 2 | 10 | 0 |
| `core` | 4/10/8 | 5 | 9 | 4 | `editor-ui` | 1/2/14 | 6 | 8 | 1 |
| `world` | 1/10/14 | 2 | 7 | 1 | `automation` | 0/5/11 | 2 | 2 | 0 |
| `gpu` | 1/15/14 | 3 | 12 | 0 | `engineering` | 3/9/11 | 4 | 3 | 8 |
| `assets` | 0/11/10 | 5 | 2 | 3 | `capstone` | 0/0/1 | 0 | 0 | 0 |
| `draw` | 1/9/10 | 0, 1, 0 | 4 | 0 | `reference` | 0/3/3 | kind R | 0 | 0 |
| `light` | 2/14/13 | 0 | 2 | 0 | `appendix` | 2/2/1 | 1 | 0 | 0 |
| `image` | 1/12/9 | 1 | 1 | 0 | `indirect` | 0/6/11 | 1 | 0 | 1 |

Order:

1. The planner settles section 3 and edits its files: book.md (D6, D11, D17, D22, D28, D30, D35, D36, D38, D39, D43,
   the counts), style.md (D19 to D22, D24, D39), process.md (D23, the counts, into the current file), pipelines.md
   (D30, D31, D38, D42), README.md (D21, D30), and a ruling for what replaces rulings-2.md:45 and the others it changes.
2. The outline from the trial, with D1, D2, D4, D5, D6 and D10, then `check_outline.py --counts --words --waves`. In
   the same commit, since the check wants a section per page in the outline's order: `basics-a` and `basics-b` write
   the new pages' sections and move their items (sizes.md "Splits in detail"); `draw` merges two sections (D2); `ui`,
   `editor` and `light` reorder theirs (D5).
3. Owners move homes across units, the owner's row to "Passed on" and the receiver's home row in one round
   (duplicates' merges, wrong-home findings, D11, D12, D25, D26, D33, D40); then every unit's `inbox` is empty.
4. Every unit applies its findings and answers (new items with evidence, widened takes, reworded rows, the 28 teacher
   cells and the deleted row, helps rows, D23's errata) and rewrites its Fit lines with the new estimates and sizes.
5. `check`, `inbox` and `demands` for every unit, and `code --engine`; the planner runs `coverage` and fills the
   Outcome column of completeness.md. Then the README's step 5, the glossary, after D29 to D34.

What the check scripts must learn: `check_allocation.py` accepts **Starting state** on kind P (D21, with its tests) and
warns on a concept item homed on kind H (D25); `check_outline.py:712` reads book.md's new XL sentence (D22);
`check_seed.py` takes an optional `use` (D31); the linter skips `size` on kind R (D22), its strips rule accepts R11 on
track E and `make/automated-playtests` on track G (D19, D20), and `term-source` exempts kind R only if D9 needs it.
Nothing in `check_outline.py` blocks the splits or the merge (`G_SIDE_STEPS`, the W8 lists and the waves hold).

## 6. What nobody checked

- Nothing was run (no editor, game, build or test). Claims that rest on code alone: critic-animation-2, -11,
  critic-audio-input-7, -16, critic-scripting-3, -9, critic-worlds-runtime-4, -10, critic-gameui-3, ui-q6, basics-a-q5.
- The units without an inventory (`start`, the four `make` units, both `basics` units, `capstone`, `reference`,
  `appendix`) had no completeness critic: critic-gamedev read the make pages through its items, critic-book read
  book.md's tables, the questions agents only questions. Nobody read the primers' new items, the capstone's steps or the
  reference and appendix Covers for what is missing.
- No agent re-estimated a page (57 estimates equal their budget, sizes); the critics' added words are their guesses,
  and `crossref.py`'s attribution was checked by reading only for the pages of section 1.
- `check_allocation.py code` was not run, so the critics' new code rows are unchecked. The questions agents' closure
  scripts take the union of a Need's alternatives, the check their intersection. Not compared: the 1,051 helps rows'
  closure (prep); whether the 85 must rows' teachers teach the concept (needs).
- Glossary: most critics did not read their terms' definitions; check_seed was not run on the splits' seed moves; the
  homonym groups were judged from labels. book.md's not-done evidence: about 25 of 81 rows were read again; D35's rows
  were run once, by their critics. duplicates misses pairs worded differently, pairs inside one inventory and home rows
  without a place.
- Test bodies and engine files read only in part: each critic's "Not checked" lists them (5 to 8 items a file).
- The trial's `process.md` predates `cbe2d2d`; sizes remapped the split pages' teachers by keyword; D1, D2, D4 (b),
  `make/lamps` at L and the reorders are not in it. Lines of book.md, pipelines.md and process.md may have moved.
- My own: I did not check the critics' evidence at the pin, and sections 4 and 5 see only what shares an item or a page.
