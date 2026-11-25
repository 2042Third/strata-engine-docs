# Rulings 4: the planner's read of the revised plan

The planner read the revised outline (all four files), `README.md`, `process.md`'s order and the rows of
`dispositions.md` §4 and §5. These rulings decide what the revisers left open. Where they differ from
`rulings-2.md` (sizes, the list of `basics`, the order of `editor`), this file wins. The outline now holds
**332 pages**; `check_outline.py` passes.

## R7 — A size is a budget of words, not a limit on content

A page that is too full gets more room, or is split. It never loses content it needs, and it never teaches faster
than its persona can follow. The revisers kept four sizes because a ruling set them; the ruling changes:

| Page | Was | Is | Why |
| --- | --- | --- | --- |
| `make/transforms-units` | C/M | C/L | It is the use home of positions, directions, rotations, hierarchies, spaces and units for a reader who cannot read code yet. Every idea is shown first with the Inspector's numbers and the gizmo. The code forms come in one last section, "The same ideas in code", which `make/scripting-scene` sends the reader back to. |
| `make/lighting` | T/M | T/L | Sun, sky, exposure in EV stops and Coin Run's stage, each step with its result to expect, do not fit 3,000 words. |
| `make/input` | T/M | T/L | Action maps, the script's side, keyboard and gamepad, and Coin Run's stage. |
| `basics/numbers` | P/M | P/L | Binary, integers, floating point and precision, and now also powers, logarithms and the exponential function, from zero. |

`make/gameplay-math` stays H/L: its formulas are recipes (what to type, what it does, when to use it), and the
mathematics is `basics`'.

## R8 — `basics/math-change` is two primers

One primer at M could not teach both rates with integration and interpolation with smoothing from zero. It is split:

| id | Title | Kind | Size | Tracks | Needs |
| --- | --- | --- | --- | --- | --- |
| `basics/math-change` | Change over time: rates, accumulation, Euler steps and Newton's laws | P | L | B, E | `basics/math-vectors` |
| `basics/math-interpolation` | Blending and smoothing: lerp, easing, curves and exponential smoothing | P | M | B, E | `basics/math-change`, `basics/numbers` |

`basics/math-interpolation` follows `basics/math-change` directly, in the part and on tracks B and E. Derivatives
and integrals are taught as rates and accumulation, from tables of numbers and graphs before any symbol.
`basics/signals`, `world/interpolation` and `animation/clips` need the new page; `core/time`, `physics/dynamics`
and `basics/math-probability` keep `basics/math-change`. The one-home table of `book.md` has a row for each.
Interpolating rotations stays `basics/math-rotations`'.

## R9 — The order of `editor`

The order the revisers wrote stands, with one move: `editor/projects` comes after `editor/recovery` and needs
`editor/saving`, `world/projects-settings` and `world/sub-scenes`. Opening or closing a project releases the edited
scene, so the page uses the unsaved-changes guard and `AfterSaves`, whose home is `editor/saving`.

## R10 — The rows of `dispositions.md` §4

Every row is accepted as the plan applies it:

- `reference/term-index` (a row id may not end in `index`).
- `editor` and `scripting` in wave 5.
- The `Graphics` API in `make/quality`, `World` in `make/large-worlds`, `Scene::InstantiateMany` in
  `make/performance`.
- One more build in phase B, the patch runner's `build/docs-patch`.
- "Before" pictures: the baseline sets exist (0.6.0, 0.7.0 and 0.7.0 at Medium, in the planning worktrees of waves
  7 and 8). The planner copies them once, read-only, to `G:/GameEngineAI/.worktrees/docs-baselines/` before phase B
  (`pipelines.md` §5.5).
- Pictures (SI4): committed files carry no hash; the site serves each under a name with the first 10 hex digits of
  its SHA-256; PNG originals stay in the ignored `originals/` folder and go into the release's archive
  (`figures.py archive --tag`).
- OL15 (the exported world's check stays in `make/large-worlds`), OL11 (the rebinding screen is in `make/menus`),
  SI11 and SI23 (the spike's `caption` and `alt`, and its two overrides).
- SI3: the planner adds the banner to `research/framework.md` §5 (done with these rulings).

## R11 — What the later steps must do

- **Briefs may propose a split.** When a brief shows that a page cannot hold its content at its size, the planner
  changes the size or splits the page, with `check_outline.py` passing, before the page is written (R7).
- **Briefs name every checkpoint a page starts from.** In particular: the Coin Run practice item of each
  programming primer starts from `make/first-script`'s downloadable checkpoint; `make/animation` starts from a
  checkpoint that already holds a controller (made by `animation.createController`); `make/menus` carries the
  "name field" example of typed text.
- **A command-only step on track E before parts 18 and 20.** A page that needs a step only a command can do gives
  the complete line to paste, one sentence on what it does, and a link forward to `editor/commands`. It is no Need:
  `start/how-to-read` teaches how to read and run a command.
- **The tool builder** moves the rules that `check_outline.py` holds into `tools/booklib/outline.py` with unit tests
  (`site.md`), including the checks of R7 to R9 that are rules (sizes of primers and track B pages, the order of
  tracks).
- **The site builder** verifies the sparse-checkout patterns of `site.md`'s CI section against the engine
  repository before CI is turned on.
