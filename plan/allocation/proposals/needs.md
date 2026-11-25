# Proposals: Needs and teachers

Written by the agent `needs` of workflow B, step 4 of `../README.md` ("Order of the work"). It applies the planner's
rule N to every Assumes row that the check flags, on the trial outline that the agent `sizes` left
(`G:/GameEngineAI/.worktrees/docs-work/B/outline/plan/`, with the three splits of `sizes.md`). Sources: `../coverage.md`
§6, `G:/GameEngineAI/.worktrees/docs-work/B/prep/assumes.tsv`, the units' files, `prep/questions/`, `from-workflow-a.md`
("final.forPlanner", points 4 and 5). Scripts and their outputs: `G:/GameEngineAI/.worktrees/docs-work/B/needs/`. The
edits to the trial are listed in `G:/GameEngineAI/.worktrees/docs-work/B/outline/CHANGES.md`, section "Needs (agent
`needs`)". Unit files, coverage.md and the plan's own outline are unchanged.

## Summary

On the trial, the closure of `check_allocation.py` (coverage §6) flags the same 114 rows as coverage.md: 85 rows of
depth `must` whose teacher is outside the page's Needs closure, and 29 rows with `?`. The splits change no answer:
rows that name a split page take the half that holds their concept, by the rule of `sizes/closure_check.py`
(`needs/lib.py`, `SPLIT_RULES`), and the 114 are the same rows.

| Verdict | Rows | How |
| --- | --- | --- |
| add-need | 85 | 47 Needs cells change: 29 on the parts' pages, 18 on reference pages. Where a part's chain misses a page, the Need goes on the page where the chain starts, as the units asked (one Need settles up to 8 rows) |
| part-need | 0 | Not a separate edit: `check_outline.py` computes each part's line from its rows (`check_part_lines`, line 459) and fails on any other entry. 4 part lines follow the rows' Needs |
| other-teacher | 19 | Rows with `?` whose concept a page already homes; each names the home row |
| earlier-home | 3 | Regular expressions, on `basics/data-formats` (about 350 words) |
| self-taught | 6 | Reading Python (4 rows), least-squares fitting, mesh simplification. Depth stays `helps` |
| for the planner | 1 | `start/coming-from`: the row names the page's reader, not a concept |

The check on the trial: `python -B plan/check_outline.py --counts --words --waves` exits 0, prints no problem, and
prints exactly what it printed before (no count, size, track or wave changes). Every Need stands before its page on each
of the page's tracks, or earlier in the book's order for pages on no track (coverage §6 "Before": yes for all 85).
After the edits: 0 `must` rows outside a closure; no Assumes row of any depth leaves a closure; 77 `helps` rows enter
one; the only closures that lose a page are 17 reference pages, which lose `reference/script-api`, the part's first
page that their `-` named (`needs/compare.py`).

To apply them, the units change only Assumes cells: the "Taught by" of 28 rows with `?` (the 29th row is deleted), and
the words that the earlier-home and self-taught verdicts add to four pages' Covers. The add-need rows need no change in
a unit's file.

## Needs that change

"Rows this settles": the flagged rows whose teacher this one Need brings into the closure, on the page itself or on
pages that reach it. `editor/camera-viewport`'s row at `editor.md:1286` needs this page's Need and the one on
`editor/commands` together. Each reference page lists its own rows; through the part's line each reference Need also
reaches the other reference pages (For the planner, item 2).

| Page | Needs now | Needs proposed | Rows this settles |
| --- | --- | --- | --- |
| `make/patterns` | `make/timers-events` | `make/timers-events`, `make/script-fields` | `make/patterns` make-b1.md:300; `make/recipes` make-b1.md:377; `make/project-tetris` make-c.md:186 |
| `make/characters-cameras` | `make/gameplay-math` | `make/gameplay-math`, `make/script-fields` | `make/characters-cameras` make-b1.md:556; `make/animation` make-b1.md:673; `make/project-platformer` make-c.md:342 |
| `make/menus` | `make/timers-events` | `make/timers-events`, `make/script-fields` | `make/menus` make-b1.md:808; `make/levels-saves` make-b1.md:910; `make/project-tetris` make-c.md:186; `make/project-platformer` make-c.md:342 |
| `basics/data-structures` | `basics/programming-2`, `basics/numbers` | `basics/programming-3`, `basics/numbers` | `basics/data-structures` basics-a.md:594 |
| `basics/build` | `basics/tools`, `basics/programming-3` | `basics/tools`, `basics/programming-3`, `basics/computer` | `basics/build` basics-a.md:918 |
| `basics/bytes` | `basics/numbers`, `basics/tools` | `basics/numbers`, `basics/tools`, `basics/cpp-generic` | `basics/bytes` basics-a.md:1012; `basics/bytes` basics-a.md:1013 |
| `basics/math-matrices` | `basics/math-vectors` | `basics/math-vectors`, `basics/numbers` | `basics/math-projection` basics-b.md:234; `basics/math-geometry` basics-b.md:391 |
| `basics/color` | `basics/numbers` | `basics/numbers`, `basics/math-matrices` | `basics/color` basics-b.md:624 |
| `gpu/vulkan-nvrhi` | `basics/cpp-classes`, `basics/numbers`, `core/engine-modules`, `core/layers-registries`, `core/platform` | `basics/cpp-classes`, `basics/numbers`, `gpu/how-a-gpu-frame-works`, `core/layers-registries`, `core/platform` | `gpu/vulkan-nvrhi` gpu.md:161; `gpu/shaders` gpu.md:247; `gpu/compute` gpu.md:311; `gpu/resources-lifetimes` gpu.md:581; `gpu/upload-queue` gpu.md:645; `gpu/binding` gpu.md:728 |
| `gpu/coordinates` | `basics/math-projection`, `basics/numbers`, `core/math`, `world/scene-graph` | `basics/math-projection`, `basics/numbers`, `core/math`, `world/scene-graph`, `gpu/how-a-gpu-frame-works` | `gpu/coordinates` gpu.md:386; `gpu/resources-lifetimes` gpu.md:581; `gpu/upload-queue` gpu.md:645; `gpu/binding` gpu.md:728 |
| `assets/handles-meta` | `core/files` | `core/files`, `assets/what-is-an-asset` | `assets/handles-meta` assets.md:143; `assets/importing` assets.md:242; `assets/loading` assets.md:560 |
| `light/materials` | `assets/textures`, `basics/math-bases` | `assets/textures`, `basics/math-bases`, `light/units-exposure` | `light/materials` light.md:136; `light/reflectance` light.md:266; `light/measuring-light` light.md:495; `light/lights` light.md:570; `light/area-lights` light.md:709; `light/sky` light.md:1071; `light/atmosphere` light.md:1145; `image/exposure` image.md:164 |
| `image/exposure` | `gpu/compute`, `gpu/coordinates`, `light/measuring-light` | `gpu/compute`, `gpu/coordinates`, `light/measuring-light`, `image/why-post` | `image/exposure` image.md:165; `image/pre-exposure` image.md:241; `image/tone-mapping` image.md:317; `image/encoding` image.md:470; `image/taa` image.md:700; `image/tutorial-post-effect` image.md:979 |
| `indirect/probes` | `indirect/seam`, `image/pre-exposure`, `assets/residency`, `basics/math-geometry` | `indirect/seam`, `image/pre-exposure`, `assets/residency`, `basics/math-geometry`, `draw/mip-streaming` | `indirect/probes` indirect.md:519 |
| `indirect/ssr` | `indirect/probes`, `image/taa`, `light/clearcoat-transmission` | `indirect/probes`, `image/taa`, `light/clearcoat-transmission`, `indirect/ao` | `indirect/ssr` indirect.md:654 |
| `indirect/gi-voxels` | `indirect/seam`, `gpu/compute`, `gpu/geometry-pool`, `draw/render-scene` | `indirect/seam`, `gpu/compute`, `gpu/geometry-pool`, `draw/render-scene`, `indirect/problem` | `indirect/gi-voxels` indirect.md:759 |
| `indirect/gi-cascades` | `indirect/gi-voxels`, `indirect/ao`, `light/measuring-light`, `basics/math-sphere` | `indirect/gi-voxels`, `indirect/ao`, `light/measuring-light`, `basics/math-sphere`, `light/atmosphere` | `indirect/gi-cascades` indirect.md:891 |
| `animation/root-motion` | `animation/time-events`, `physics/character-controllers` | `animation/time-events`, `physics/character-controllers`, `animation/blending` | `animation/root-motion` animation.md:599 |
| `animation/editor` | `animation/system` | `animation/system`, `animation/skinning` | `animation/editor` animation.md:859 |
| `audio/engine` | `basics/threads`, `core/frame-loop`, `core/engine-modules` | `basics/threads`, `core/frame-loop`, `core/engine-modules`, `audio/sound-in-a-computer` | `audio/engine` audio-input.md:136; `audio/clips-voices-sources` audio-input.md:221; `audio/spatial` audio-input.md:303 |
| `input/devices-state` | `core/time`, `basics/bytes` | `core/time`, `basics/bytes`, `input/how-input-works` | `input/devices-state` audio-input.md:597; `input/actions` audio-input.md:817 |
| `scripting/shared-libraries` | `basics/build`, `basics/cpp-classes` | `basics/build`, `basics/cpp-classes`, `scripting/why-scripts` | `scripting/shared-libraries` scripting.md:124 |
| `worlds/grids` | `assets/handles-meta`, `world/serialization` | `assets/handles-meta`, `world/serialization`, `worlds/why-streaming` | `worlds/grids` worlds.md:148 |
| `worlds/runtime` | `worlds/game-identity`, `core/engine-modules`, `core/platform`, `scripting/script-system`, `image/quality-settings` | `worlds/game-identity`, `core/engine-modules`, `core/windows-events`, `scripting/script-system`, `image/quality-settings` | `worlds/runtime` worlds.md:648 |
| `editor/commands` | `world/reflection`, `basics/data-formats` | `world/reflection`, `basics/data-formats`, `editor/program` | `editor/commands` editor.md:142; `editor/deferred-commands` editor.md:211 |
| `editor/placement` | `editor/undo`, `basics/math-geometry`, `draw/bounds-culling` | `editor/undo`, `basics/math-geometry`, `draw/bounds-culling`, `editor/deferred-commands` | `editor/placement` editor.md:1160 |
| `editor/camera-viewport` | `gpu/coordinates`, `basics/math-rotations`, `draw/bounds-culling` | `gpu/coordinates`, `basics/math-rotations`, `draw/bounds-culling`, `editor/commands` | `editor/camera-viewport` editor.md:1286; `editor/camera-viewport` editor.md:1287 |
| `automation/json-rpc` | `basics/data-formats`, `basics/threads`, `core/platform` | `basics/data-formats`, `basics/threads`, `core/platform`, `automation/agents` | `automation/sessions` automation.md:447; `automation/mcp` automation.md:541 |
| `capstone/build` | `physics/world-step`, `gpu/debug-drawing`, `editor-ui/inspectors` | `physics/world-step`, `gpu/debug-drawing`, `editor-ui/inspectors`, `capstone/plan` | `capstone/build` capstone.md:270 |
| `reference/script-api` | - | `basics/programming-3` | `reference/script-api` reference.md:79 |
| `reference/commands` | - | `make/commands`, `basics/data-formats` | `reference/commands` reference.md:159; `reference/commands` reference.md:161 |
| `reference/components` | - | `make/scenes-entities` | `reference/components` reference.md:238 |
| `reference/settings` | - | `world/projects-settings` | `reference/settings` reference.md:298; `reference/settings` reference.md:299 |
| `reference/scene` | - | `basics/programming-3` | `reference/scene` reference.md:368 |
| `reference/assets` | - | `assets/handles-meta` | `reference/assets` reference.md:435 |
| `reference/renderer` | - | `gpu/frame-tour` | `reference/renderer` reference.md:525 |
| `reference/physics` | - | `physics/bodies-colliders` | `reference/physics` reference.md:591 |
| `reference/animation` | - | `animation/state-machines` | `reference/animation` reference.md:649 |
| `reference/audio-input` | - | `input/actions` | `reference/audio-input` reference.md:710 |
| `reference/ui` | - | `ui/layout` | `reference/ui` reference.md:762 |
| `reference/worlds-runtime` | - | `worlds/runtime` | `reference/worlds-runtime` reference.md:826; `reference/worlds-runtime` reference.md:828 |
| `reference/editor` | - | `make/editor-tour` | `reference/editor` reference.md:891 |
| `reference/automation` | - | `automation/json-rpc` | `reference/automation` reference.md:956 |
| `reference/core` | - | `basics/programming-3` | `reference/core` reference.md:1012 |
| `reference/build` | - | `basics/build` | `reference/build` reference.md:1064; `reference/build` reference.md:1065 |
| `reference/performance` | - | `engineering/perf-lab` | `reference/performance` reference.md:1114 |
| `reference/game-makers` | - | `make/first-script` | `reference/game-makers` reference.md:1174; `reference/game-makers` reference.md:1175; `reference/game-makers` reference.md:1176 |

The four "Needs of the part" lines that follow (computed as the check computes them): `gpu` drops
`core/engine-modules` (still in every gpu closure through `core/layers-registries`); `indirect` adds
`draw/mip-streaming` and `light/atmosphere`; `worlds` adds `core/windows-events` and drops `core/platform` (still in
every worlds closure, through `assets/residency` and through `core/files`); `reference` goes from `-` to the 17 pages
the reference rows name.

Where a Need replaces one, the old Need stays in the closure: `core/engine-modules` through `core/layers-registries`
(`gpu/vulkan-nvrhi`); `core/platform` through `worlds/game-identity`, `worlds/export` and `core/files`
(`worlds/runtime`); `basics/programming-2` through `basics/programming-3` (`basics/data-structures`). The row may leave
them out (`../../outline-1.md:51`).

## Rows with another verdict

None. Each of the 85 `must` rows whose teacher is a page became add-need, and the check passes with all of them. Two
groups give a weaker result than the rule intends; they stay add-need here and are For the planner, items 2 and 3.

## Rows without a teacher

| Page | Concept | Verdict | Proposal | Why |
| --- | --- | --- | --- | --- |
| `start/coming-from` | Having made something in Unity, Unreal or Godot (must) | for the planner | Delete the row (start.md:471) | It names the page's reader, not a concept: G0 has used no engine (`../../style.md:71`), and `../../tracks.md:10-11` already makes the page optional for whoever has. No page can teach it, and no Need can meet it |
| `make/lamps` | The Graphics Quality presets (Low draws the shadows of four lamps) | other-teacher | Taught by `make/quality` (home rows `gamedev:117` and the term `gamedev:602`, make-b2.md:385 and 393); one sentence inside a link names the preset (forward mention, `../../style.md:296`) | `make/quality` comes after the four pages on track G and needs `make/menus`; each page uses one fact of one preset at depth `helps`, and shows the quality chip as its own step |
| `make/reflections` | The Graphics Quality presets and TAA as an anti-aliasing | other-teacher | Taught by `make/quality` (`gamedev:117` and `gamedev:116`, make-b2.md:385 and 384), as a forward link | As for `make/lamps`; the anti-aliasing kinds are also `make/quality`'s home |
| `make/gi` | The Graphics Quality presets | other-teacher | Taught by `make/quality` (`gamedev:117`, make-b2.md:385), as a forward link | As for `make/lamps`; the page's starting project is already at High (make-b2.md:249) |
| `make/look` | The Graphics Quality presets | other-teacher | Taught by `make/quality` (`gamedev:117`, make-b2.md:385), as a forward link | As for `make/lamps` |
| `core/windows-events` | C callbacks: function pointers and a user pointer | other-teacher | Taught by `basics/cpp-generic` (`new:147`, basics-a.md:763) | Homed there with the C form of callbacks (basics-a.md:729-730); inside the closure through core's "Needs of the part" (`basics/cpp-modern` needs it) |
| `core/layers-registries` | Function pointers | other-teacher | Taught by `basics/cpp-generic` (`new:147`, basics-a.md:763) | The same home row; inside the closure |
| `core/layers-registries` | Static initialization and its order | other-teacher | Taught by `basics/build` (`new:168`, basics-a.md:896) | One of the six concepts (For the planner, item 1); inside the closure |
| `core/files` | `std::filesystem::path` | other-teacher | Taught by `basics/cpp-modern` (`new:161`, basics-a.md:832) | One of the six; inside the closure |
| `world/serialization` | Union-find (disjoint sets) | other-teacher | Taught by `basics/trees-graphs` (`new:116`, basics-a.md:576, which the split moves there: sizes.md:146) | Both basics units named this home (basics-a-q10, basics-b-q13); inside the closure through core's line |
| `assets/texture-cooking` | Least-squares fitting, and the principal axis of a cloud of points | self-taught | A `:::derivation` box of about 200 words: the mean of the block's colors, their spread along a direction, the direction of the greatest spread as the line the colors are fitted to | basics-b-q12 and basics-a-q10 both leave it to the page: covariance and eigenvectors exceed a primer that only this page uses. G0 has the average (`../../style.md:51-52`); `basics/math-probability` is before the page on E but not in its closure, so a link only. 5,900 + 200 stays L |
| `assets/models-gltf` | Mesh simplification | self-taught | A paragraph of about 150 words: `MeshUtils::GenerateLODs` calls meshoptimizer's `meshopt_simplifyWithAttributes`, which removes edges while the error stays under `c_MaxLODError` (0.02 of the mesh's extent), and records each level's error | At the pin: `Strata/src/Strata/Renderer/Mesh.cpp:691-703`, `Mesh.h:207`. `draw/lod` leaves the generation to this page (draw.md:421) and comes after it on E. 4,800 + 150 stays L |
| `assets/packs-export` | Structs as bytes: sizes, alignment and `static_assert` | other-teacher | Taught by `basics/bytes` (`new:178`, basics-a.md:974; it stays on `basics/bytes` after the split, sizes.md:196-198) | One of the six; inside the closure (assets' line has `basics/data-formats`, which needs `basics/bytes`) |
| `indirect/gi-cascades` | A geometric series and its sum (must) | other-teacher | Taught by `basics/math-interpolation` (`new:74`, basics-b.md:523) | One of the six; inside the closure (the row "Trilinear interpolation" already names that page); `basics/numbers`, the other candidate, is inside it too |
| `audio/engine` | Calling a C library from C++: C structs, configuration structs and result codes | other-teacher | Taught by `basics/cpp-generic` (`new:147`, basics-a.md:763) | One of the six; inside the closure |
| `audio/clips-voices-sources` | Standard-layout types and `offsetof` | other-teacher | Taught by `basics/bytes` (`new:178`, basics-a.md:974) | One of the six; inside the closure through core's line |
| `input/actions` | Writing a parser by hand | other-teacher | Taught by `basics/data-formats` (`new:186`, basics-a.md:982, which the split moves there: sizes.md:201-203) | Both basics units named `basics/bytes`, whose half with reading text into tokens is now `basics/data-formats`; inside the closure through world's line |
| `input/simulated` | Pointers to members (`T C::*`) | other-teacher | Taught by `basics/cpp-generic` (`new:148`, basics-a.md:764) | Both basics units named this home; inside the closure |
| `worlds/game-identity` | The save service of a game (`IGameSaves`) as scripts use it | other-teacher | Taught by `scripting/host-api` (`foundation:130`, scripting.md:706; the save functions as its example, scripting.md:666) | worlds-q4 says no track E page teaches it, but `scripting/host-api` homes the service and comes before the page on E (a link: not in the closure). The game maker's side is `make/levels-saves` (`gamedev:203`, make-b1.md:881), which E does not read |
| `worlds/runtime` | The save service of a game (`IGameSaves`) as scripts use it | other-teacher | Taught by `scripting/host-api` (`foundation:130`, scripting.md:706) | As for `worlds/game-identity` |
| `editor-ui/ui-testing` | Regular expressions and scanning source text | earlier-home | `basics/data-formats` takes regular expressions: literal characters, `.`, `*`, `+`, `?`, classes such as `[a-z]`, the anchors, groups and escaping; a glob turned into a pattern; why JSON needs a parser and not a pattern (about 350 words) | One of the six. The page is M at 4,000, the top of M, so it cannot take the lesson itself; `basics/data-formats` is in its closure and in that of every later page |
| `engineering/cmake` | Regular expressions | earlier-home | The same words on `basics/data-formats` | One of the six; the page's glob-to-regex code (engineering.md:119) is the worked example's case |
| `engineering/generated-code` | Regular expressions | earlier-home | The same words on `basics/data-formats` | One of the six; `CMake/StrataEmbeddedFiles.cmake:8-46` holds two patterns (engineering.md:449) |
| `engineering/flags-portability` | Reading a short Python function | self-taught | No home; each quoted function is explained after its fence, as every fence must be (`code-follow`, `../../style.md:622`) | One of the six. The page is on track E only, and E1 has programmed in one language, Python among those named (`../../style.md:80`); running a Python tool is `basics/tools`' (`new:26`, basics-a.md:139) |
| `engineering/generated-code` | Reading a short Python script | self-taught | As for `engineering/flags-portability` | One of the six |
| `engineering/perf-lab` | Reading a short Python function | self-taught | As for `engineering/flags-portability` | One of the six |
| `engineering/look-dev` | Reading a short Python function | self-taught | As for `engineering/flags-portability` | One of the six |
| `engineering/ci` | Shell scripts in bash | other-teacher | Taught by `basics/tools` (`new:26`, basics-a.md:139) | Both basics units named this home; inside the closure |
| `engineering/contributing` | git worktrees | other-teacher | Taught by `basics/tools` (`new:33`, basics-a.md:146); `basics/git` if the planner takes that split (sizes.md, For the planner, item 2) | Both basics units named this home; inside the closure |

"Inside the closure" was checked on the trial with these edits (`needs/teachers.py`).

## For the planner

1. **The six concepts with two proposed teachers.** basics-a homed each on one of its own pages, with a home row;
   basics-b named other pages in a question (basics-b-q13, basics-b.md:962-968) and gave reasons only for the geometric
   series. So basics-a's choices need no move, and basics-b's would move a home row.

   | Concept | basics-a | basics-b | Recommended | Why |
   | --- | --- | --- | --- | --- |
   | Static initialization and its order | `basics/build` (`new:168`, basics-a.md:896): what runs before `main`, with the object a linker drops (basics-a.md:857-862) | `basics/cpp-modern` | `basics/build` | Its user, `core/layers-registries`, argues against self-registration with two facts together, the undefined order and the dropped object of a static library (core.md:685-686); the second is about linking, which `basics/build` teaches and the page already needs (core.md:783) |
   | Structs as bytes, standard layout and `offsetof` | `basics/bytes` (`new:178`, basics-a.md:974), "as the GPU's data and the packs need them" (basics-a.md:928-930) | `basics/cpp-memory` | `basics/bytes` | Its users (`assets/packs-export`, `audio/clips-voices-sources`) need a struct's bytes as a layout, beside byte order and file headers; `basics/cpp-memory` is about lifetimes and ownership. The split keeps it on `basics/bytes` |
   | `std::filesystem::path` | `basics/cpp-modern` (`new:161`, basics-a.md:832): joining and the extension; the encoding is `core/files`' (basics-a.md:793-794) | `basics/bytes` | `basics/cpp-modern` | The type is standard C++, taught beside `std::optional` and `std::string_view`, which `core/files` also uses; the narrow-string trap is `core/files`' own contract (core.md:1004-1006), and the code pages it rests on stay on `basics/bytes`. Two angles, two pages, no repeat |
   | Calling a C library | `basics/cpp-generic` (`new:147`, basics-a.md:763), with function pointers and the user pointer (basics-a.md:729-730) | `basics/build` | `basics/cpp-generic` | GLFW and miniaudio are called the same way: configuration structs, result codes, and a callback through a function pointer with a user pointer; `core/windows-events` and `audio/engine` ask for those halves of one lesson. Neither row asks about linking |
   | Python and regular expressions | A new page on no track, `appendix/reading-python-regex` (H, S), linked by the six pages (basics-a-q9, basics-a.md:1139-1143) | Python on `basics/tools`, regular expressions on `basics/bytes` | Regular expressions on `basics/data-formats`; Python on no page | `basics/tools` comes before any programming on tracks G and B (`../../tracks.md`, rules) and stands at 6,200 of L's 6,500. A new page adds a page and a count for six `helps` rows. Every Python row is on track E, whose E1 has programmed (`../../style.md:80`), and every fence is explained (`code-follow`). Regular expressions are new to E1 and are used three times: `basics/data-formats`, the half of `basics/bytes` that reads text into tokens, holds them in about 350 words at L (about 4,450 of 6,500) |
   | A geometric series and its sum | `basics/numbers` (`new:96`, basics-a.md:490), among the powers (basics-a.md:444) | `basics/math-interpolation` (`new:74`, basics-b.md:523), idea 9 after exponential smoothing (basics-b.md:479-481) | `basics/math-interpolation` | `indirect/gi-cascades` uses it for settle frames and for re-injected bounces (indirect.md:784), the angle of idea 9: the gap left after n steps, 1 / (1 - r), the frames to settle. Both pages are in the closure. Two homes now (rule D): `basics/numbers` drops `new:96` and links; it stands at 6,400 of L's 6,500, so the drop also gives it room |

2. **Rule N1 on reference pages gives a weak result.** The 24 rows are add-need (every teacher is earlier in the book's
   order, and the check passes). But the check computes the part's line from the rows, so `reference`'s line goes
   from `-` to 17 pages, and every reference page's closure becomes the union of them: the one Need of
   `reference/performance` alone would have settled 14 of the 24 rows (`needs/attribute.py`). The part's index page
   would list 17 pages under "Before this part". The edits also fix a defect: with `-`, each reference page's strip
   shows its part's first page, `reference/script-api`, under "Before you start" (`../../style.md:420`), which no
   reference page needs. The alternative is reference-q2's: exempt kind R from coverage §6 and keep the Assumes as the
   links the page gives; then the 18 Needs go, and the strip of a reference page still needs a rule of its own. I
   recommend the Needs, with a site rule that the reference index shows no "Before this part".

3. **Four reference Needs are track G pages.** `make/commands`, `make/scenes-entities`, `make/editor-tour` and
   `make/first-script` are the teachers the reference unit named; pages on no track are written for E1
   (`../../style.md:117-120`), who never reads `make`. For `reference/game-makers` (a cheat sheet for game makers) the
   Need is right. For `reference/commands`, `reference/components` and `reference/editor`, the homes that track E
   reads are `editor/commands` (`../../book.md:324`), `world/what-a-world-is` (`../../book.md:190`) and
   `editor-ui/shell` (the editor's anatomy, `../../book.md:323`). An alternative (`make/commands` or
   `editor/commands`) would show both, but the closure keeps only what both teach, so those rows would be flagged
   again unless their concept is named in words both pages teach. Recommendation: keep the make Needs on
   `reference/game-makers`; give the other three the E page as their Need and as the row's teacher.

4. **Part-need is never its own edit.** `check_part_lines` (`check_outline.py:459`) fails on an entry that no row
   needs. Where many pages of a part miss the part's first page (gpu, assets, light, image, audio, input, automation:
   point 4 of "final.forPlanner"), one Need on the page where the part's chain starts settles them all; the units'
   questions proposed exactly those pages (gpu-q1, assets-q1, light-q1, image-q1, audio-input-q1, automation-q2). The
   first page of a part is in no closure unless a Need names it (`../../outline-1.md:48`, and the closure's definition
   in `check_allocation.py`), and readers of track E may take parts in another order, so the Need is the right fix,
   not a change of the closure.

5. **Choices among equal fixes**, each checked:
   - `editor/camera-viewport` takes `editor/commands`, not editor-q1's `editor/play-mode`: the two `must` rows ask for
     the editor core and commands, and `editor/play-mode` is only a `helps` row. With `editor/commands` needing
     `editor/program`, both are in the closure.
   - `indirect/gi-voxels` takes `indirect/problem` itself (N1 as written). `indirect/ibl` (four Needs) would give the
     whole part its first page, but no other indirect row asks for it.
   - `image/exposure` takes only `image/why-post`, not also `light/units-exposure` as image-q1 asked: the units reach it
     through `light/measuring-light`, `light/brdf`, `light/reflectance` and `light/materials`. One Need fewer, the
     same closure.
   - Six rows now name five Needs: `gpu/coordinates`, `indirect/probes`, `indirect/gi-voxels` and
     `indirect/gi-cascades` reach five; `gpu/vulkan-nvrhi` and `worlds/runtime` had five and keep them by
     replacement. `gpu/coordinates`' `basics/numbers` is now redundant (`basics/math-projection` reaches it through
     `basics/math-matrices`) and may be left out, to keep room.

6. **Sizes.** No verdict changes a size class. Words added: `basics/data-formats` about 350 (about 4,100 to 4,450,
   L); `assets/texture-cooking` about 200 (5,900 to 6,100, L, 400 under its top); `assets/models-gltf` about 150
   (4,800 to 4,950, L). Words removed: `basics/numbers` about 100 to 150 if it drops the geometric series (6,400, L).
   The Needs change no count of `book.md`, `process.md` or `README.md`.

7. **Questions about Needs or teachers that rule N does not reach**, because their rows are `helps` or already
   inside the closure: start-q3, core-q7, editor-ui-q2, ui-q3, basics-b-q3's frustum row, basics-b-q6 and appendix-q5.
   None is settled here. Two teacher changes the questions ask keep their rows inside the closure on the trial:
   `light/fog`'s exponentials to `basics/math-interpolation` (basics-b-q4; through `basics/signals`), and
   `editor/play-mode` and `editor/saving` naming `world/systems` for `Scene::Copy` (world-q7).

8. **Not done here.** No unit file is changed; the Assumes cells of the 28 rows with a new teacher, the deleted row
   and the words of the earlier-home and self-taught verdicts are for the agents that apply the decisions. coverage.md
   was not written again ("coverage" writes files); the closures were computed by `needs/lib.py`, which repeats
   `check_allocation.py`'s definition, on the trial.
