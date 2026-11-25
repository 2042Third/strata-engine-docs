# Rulings 2: the outline, part by part

Read with `summary.md` §3. For a part not named here, or a row not named here, apply the summary's proposed row
(where the summary gives one proposal) and R1's columns. Ids of removed or renamed pages may change freely:
nothing is published yet.

## Order of the parts

| # | Part | Tracks |
| --- | --- | --- |
| 0 | Start here (`start`) | all |
| 1 | Making games (`make`) | G, B |
| 2 | Foundations (`basics`) | B, E (some pages G) |
| 3 | Engine architecture (`core`) | E |
| 4 | Scenes and the ECS (`world`) | E |
| 5 | The GPU and the renderer's core (`gpu`) | E |
| 6 | Assets (`assets`) | E |
| 7 | Drawing a scene (`draw`) | E |
| 8 | Light and materials (`light`) | E |
| 9 | The image (`image`) | E |
| 10 | Indirect light (`indirect`) | E |
| 11 | Physics (`physics`) | E |
| 12 | Animation (`animation`) | E |
| 13 | Audio (`audio`) | E |
| 14 | Input (`input`) | E |
| 15 | Scripting (`scripting`) | E |
| 16 | Game UI (`ui`) | E |
| 17 | Large worlds and shipping (`worlds`) | E |
| 18 | The editor's core (`editor`) | E |
| 19 | The editor's interface (`editor-ui`) | E |
| 20 | Automation and AI agents (`automation`) | E |
| 21 | Building, testing and releasing the engine (`engineering`) | E |
| 22 | Capstone: one feature through every layer (`capstone`) | E |
| 23 | Reference (`reference`) | - |
| 24 | Appendices (`appendix`) | - |

Decided contradictions: `gpu` comes before `assets` (texture cooking and uploads need it); `image` comes before
`indirect` (RB); the editor is two adjacent late parts (CU's split, not its early position); scene documents,
prefabs' data model and sub-scenes stay in `world` (CF); sky, atmosphere and fog stay in `light` (RB).

## Part 0 — `start`

Order: `start/welcome`, `start/how-to-read` (includes the map of the book; no `start/map`), `start/install`
(H/M, "Installing Strata and the C++ build tools": release download, per-OS tabs, the script toolchain, a code
editor, the `script.status` check; OL5), `start/first-game`, `start/what-an-engine-is` (C/L, home of the frame
map; it explains what the reader just did), `start/coming-from` (H/M, "Coming from Unity, Unreal or Godot",
optional on G and E). Doing comes before theory.

`start/first-engine-change` leaves the part and becomes `core/first-change` (below): it needs a source build.

## Part 1 — `make` (OL4)

Three blocks. **Block A's tutorials build one game, Coin Run, step by step** (each starts from the end state of the
one before), so the reader owns a finished, exported game at the end of block A.

**Block A — your first game** (in this order):
`make/editor-tour` (T/M) · `make/project-files` (H/M, "Projects, saving, undo and recovery"; no separate
`make/undo-save-recover`) · `make/scenes-entities` (T/M) · `make/transforms-units` (C/M) · `make/assets` (H/M) ·
`make/materials` (T/L) · `make/prefabs` (T/M) · `make/lighting` (T/M, sun, sky and exposure; no mark) ·
`make/first-script` (T/M) · [track steps through `basics/programming-1..3`, `basics/debugging`] ·
`make/script-loop` (C/M) · `make/scripting-scene` (H/L, "Scripts and the scene: finding, spawning and changing
entities") · `make/input` (T/M) · `make/physics` (T/L) · `make/sound` (T/M) · `make/hud` (T/M, text, score and
bars) · `make/play-test-debug` (H/M) · `make/export` (T/M) · `make/project-coin-run` (T/L, finishing it: win,
lose, restart, polish, the exported game).

**Block B — the toolbox** (each page needs block A only, plus what its Needs name):
`make/gameplay-math` (H/L) · `make/timers-events` (H/M) · `make/script-fields` (H/M, "Tuning scripts from the
editor: fields, references and prefabs") · `make/patterns` (C/L, state machines, managers, pooling) ·
`make/recipes` (H/L) · `make/script-builds` (H/M) · `make/characters-cameras` (T/L) · `make/animation` (T/L) ·
`make/menus` (T/L, buttons, navigation, pause and settings screens) · `make/levels-saves` (H/L) · `make/lamps`
(T/M, W8: point, spot and area lights and their shadows) · `make/reflections` (H/M) · `make/gi` (H/M, W8) ·
`make/look` (T/L, W8r) · `make/quality` (H/M, W8r, "Graphics quality and options for players") ·
`make/large-worlds` (T/L) · `make/performance` (T/M, W8r, "Making your game run fast") ·
`make/automated-playtests` (H/M) · `make/commands` (H/M, "Driving the editor from outside: the CLI and command
scripts"; moved from `automation/outside`) · `make/with-an-agent` (T/L, one page; no `make/ai-agent` +
`make/agent-game`) · `make/samples` (H/M).

**Block C — projects**: `make/designing-a-game` (C/M) · `make/project-tetris` (T/XL) ·
`make/project-platformer` (T/XL).

`make/gameplay-1..3` are dissolved into the topic pages above (SM, GM). The applier assigns every API family of
the scripting inventory's "Gameplay API 1/2/3" chapters to one of `make/scripting-scene`, `make/gameplay-math`,
`make/timers-events`, `make/script-fields`, `make/physics`, `make/input`, `make/sound`, `make/hud`, `make/menus`,
`make/levels-saves`, `make/characters-cameras`, `make/animation`, and reports a family with no home.
`make/reflections-gi`, `make/ui`, `make/big-scenes-fast`, `make/cpp-for-scripts` no longer exist.

## Part 2 — `basics`

All pages are kind P. Order:
`basics/computer` (L) · `basics/tools` (M) · `basics/programming-1`, `-2`, `-3` (L) · `basics/debugging` (M) ·
`basics/numbers` (M, binary, integers, floating point and precision) · `basics/data-structures` (L, arrays, hash
maps, trees, cost of operations) · `basics/cpp-memory` (L) · `basics/cpp-classes` (M) · `basics/cpp-generic` (M) ·
`basics/cpp-modern` (M) · `basics/build` (L) · `basics/bytes` (M) · `basics/math-vectors` (L, vectors, dot and
cross products) · `basics/math-matrices` (L, matrices, transforms and spaces) · `basics/math-projection` (M,
cameras, perspective, homogeneous coordinates, depth) · `basics/math-rotations` (L) · `basics/math-geometry` (M,
rays, planes, boxes and intersection tests) · `basics/math-change` (M, rates, integration over time,
interpolation, curves and smoothing) · `basics/color` (M) · `basics/signals` (M, sampling, aliasing and
filtering) · `basics/math-probability` (M, probability, integrals and Monte Carlo) · `basics/math-sphere` (M,
solid angles, spherical harmonics, octahedral maps) · `basics/threads` (L).

Rejected: `basics/gpu` (its content is `gpu/how-a-gpu-frame-works`), `basics/math-numbers` (it is
`basics/numbers`), `basics/math-light` (split into the last two math pages). `basics/reading-code` moves to
`core/reading-code`.

## Part 3 — `core`

Order: `core/map` · `core/first-change` (T/L, "Your first engine change: build from source, change one thing,
test it"; the source build with per-OS tabs; full options stay in `engineering`) · `core/conventions` ·
`core/reading-code` (H/M) · `core/first-frame` · `core/frame-loop` · `core/time` · `core/windows-events` ·
`core/engine-modules` · `core/layers-registries` · `core/jobs` (L) · `core/platform` (L) · `core/files` (I/M) ·
`core/profiling` · `core/debugging` (I/M) · `core/math`.

Rejected: `core/testing` (testing's home is `engineering`; `core/first-change` teaches the minimum).

## Parts 4 to 7

- `world`: CF's retitles; `world/tutorial-component` is last and creates the WindZone component the capstone
  completes.
- `gpu`: add `gpu/compute` (C/M) and `gpu/debugging` (H/M, validation, RenderDoc, the error count, debug views);
  `gpu/first-triangle` comes after `gpu/coordinates`; `gpu/binding` retitled to name pipelines.
- `assets`: `assets/textures` (C/M) + `assets/texture-cooking` (I/L); `assets/uploads` stays its own page (what is
  queued and when; the mechanism is `gpu/upload-queue`); `assets/robustness` becomes C; mip streaming moves to
  `draw/mip-streaming`.
- `draw`: `draw/skinned` and `draw/motion-vectors` stay; `draw/skinned` takes "a list of joint matrices per
  mesh" as given and links forward to `animation/skinning` (no Need on it).

## Parts 8 to 10

- `light`: RB's eighteen pages in RB's order. Marks per R6.
- `image`: `image/why-post` M; `image/motion-blur` and `image/depth-of-field` are two pages;
  `image/tutorial-post-effect` last.
- `indirect`: RB's order (problem, ibl, seam, ao, probes, ssr, gi-voxels, gi-cascades, gi-limits).
  `light/energy` and `light/measuring-light` are in `light` (RB): the one-home table follows.

## Parts 11 to 17

- `physics`: `physics/collision-detection` (C/L) and `physics/dynamics` (C/L) replace
  `physics/how-simulation-works`; `physics/building-bodies` and `physics/world-step` as SM proposes; layers
  before contacts.
- `animation`: no W8 marks, no new graph pages (see rulings 1).
- `audio`: SM's sizes. `input`: new first page `input/how-input-works` (C/M); `input/rebinding` retitled.
- `scripting`: `scripting/host-api` becomes I, `scripting/tutorial-host-function` (T/M) is added;
  `scripting/symbolization` (I/M) is split from crash containment.
- `ui`: `ui/text` is "Text and text fields".
- `worlds`: add `worlds/game-identity`; `worlds/templates` moves to `editor/projects`; `worlds/editing` moves to
  `editor/worlds`.

## Parts 18 to 24

- `editor` (core, no UI): the context and commands, `editor/deferred-commands` third, undo (XL), documents and
  saves, prefab instances, placement, projects, script builds, stepping, command scripts, `editor/journal`
  (moved from `automation`), worlds. `editor-ui`: the program and shell, panels, views, inspectors, the widget
  kit and theme, shortcuts, settings windows, launcher and dialogs. The applier sorts every existing editor row
  into one of the two by whether its code is in `StrataEditorCore` or `StrataEditorUI`, applies ED's merges and
  additions, and reports rows it could not place.
- `automation`: track E only; its maker-facing pages are in `make`.
- `engineering`: add `engineering/test-program`; perf tests and budgets are `engineering/measuring` only if no
  existing row already covers them (then retitle that row instead).
- `capstone` (new): `capstone/plan`, `capstone/build`, `capstone/land` (T/L each): WindZone from component to
  system, editor command, script API, feature test, docs and a reviewed commit.
- `reference`: add `reference/scene`, `reference/performance`, `reference/index`, `reference/notation`.
- `appendix`: add `appendix/game-ai` (C/M: how engines do navigation and behavior, which Strata leaves to
  scripts).
