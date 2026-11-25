# Rulings 1: the rules of the book (planner's decisions on the critique)

These rulings decide the critique (`summary.md`). Where the summary gives options or marks a contradiction, the
ruling here wins. A finding not named in any rulings file is **accepted as the summary states it**. Finding ids
(BK1, OL4, SI8...) are the summary's.

## Facts the critics did not have

The critics read the engine's `Docs/Plans/Wave8/plan.md`. The orchestrator's later decisions replace it:

- **Animation in 0.8.0 is 0.7.0's animation.** The animation-graph stream left wave 8 (2026-11-03). OL3 is
  refuted: no page of `animation` carries a W8 mark, no `animation/graph` or `animation/sync-layers` page is
  added, and "blend trees, animation layers" stay in "What Strata does not do".
- **Area lights are in 0.8.0** (rectangle lights with LTC shading, soft shadows, light surfaces, editor and script
  support; disk lights if stage 5 lands). `light/area-lights` stays W8. The fallbacks proposed for "no area-light
  stream" are not applied.
- **Volumetric fog, new showcase materials and new placement tools are not planned for 0.8.0.** No conditional
  W8 marks for them. The pin tool's diff at `v0.8.0` is the check.

## R1 — Columns of the outline (OL1)

`| id | Title | Kind | Size | Tracks | Needs | From |`

- **Tracks**: the tracks whose reading order contains the page: any of `G`, `E`, `B`. A page on no track (reference,
  appendix) has `-`.
- **Needs**: at most five page ids the reader must have read. All are required. `a|b` means either page teaches
  what is needed (the same idea has a home for makers and another for engine builders only when the two pages
  teach different things: one how to use it, one how it works). `-` when the page needs nothing but its part's
  first page.
- **The check** (`plan/check_outline.py`, later part of the site's build): every id is unique; every Needs id
  exists; for every track a page is on, each Need (or one of its alternatives) comes earlier in that track's
  order (`plan/tracks.md`); no page has more than five Needs; every page of a track is reachable.
- Links forward are allowed in prose ("the renderer, which part 7 explains"). Needs forward are not.

## R2 — Kinds (BK, OL)

Six kinds: C concept, I internals, T tutorial, H how-to, R reference, and **P primer**: a lesson from zero on
something that is not Strata's (programming, mathematics, how computers work). A primer's shape: why you will
need this → the idea on the smallest example → worked examples → practice with answers → where the book uses it.
Every primer opens with a **"Test out"** box: five questions; a reader who answers them skips the page.

Parts with eight or more pages also get two generated pages that are not rows of the outline and carry no kind:
`<part>/index` (the part's map, its prerequisites, what the reader can do afterwards) and `<part>/review`
(questions across the part, collected from the pages and extended by the part's editor).

## R3 — Readers and personas (BK1)

Three personas, used by writers and by the novice review; a page is reviewed with the least prepared persona of
its tracks.

| Persona | Has | Has not |
| --- | --- | --- |
| **G0, game maker** | Installs programs, uses files and folders, school arithmetic and a little algebra | Any programming, any 3D software, a terminal |
| **B0, beginner** | The same as G0, and wants to understand everything | The same as G0 |
| **E1, engine builder** | Has written programs of a few hundred lines in some language, school algebra | C++ beyond the basics, linear algebra, graphics, engines |

The fourth reader (contributor or agent) arrives by search and has no persona: reference and internals pages serve
them by exact names and by the "changing it" sections.

## R4 — Tracks, stated exactly (BK1, OL1)

`plan/tracks.md` lists each track as an ordered list of page ids; the site's "next page" link of a track follows
it. Rules that produce the lists:

- **G**: `start` (in order), then `make` in order; where `make` reaches programming, the track steps through
  `basics/programming-1..3` and `basics/debugging` and comes back. `basics/tools` and `basics/math-vectors` are
  offered as side steps where a `make` page first needs them (they are Needs alternatives there, never forced).
- **B**: `start`; `make` block A up to `make/first-script`, with `basics/computer` and `basics/tools` before the
  first script; the programming primers; the rest of block A to the exported Coin Run; then the remaining
  `basics` in order; then the reader chooses: track G from block B, or track E from `core/map`.
- **E**: `start`; `basics` in order (every page can be tested out); `core`; `world`; `gpu`; then the subsystem
  parts in the book's order. A subsystem part is readable once the Needs of its pages are read; the part's index
  page names them.

## R5 — Programming from zero (OL2)

One home, read by tracks G and B, tested out by E. The primers use **a Strata script as the playground** (the
reader already ran one in `make/first-script`; output goes to the log and to a moving entity), so no second
toolchain is needed and a game maker sees every idea move something.

| id | Title | Kind | Size | Tracks |
| --- | --- | --- | --- | --- |
| `basics/programming-1` | Programming from zero I: values, variables, expressions and decisions | P | L | G, B, E |
| `basics/programming-2` | Programming from zero II: loops, functions, lists and structs | P | L | G, B, E |
| `basics/programming-3` | Programming from zero III: classes, references, files of code and reading errors | P | L | G, B, E |
| `basics/debugging` | Finding bugs: a method, the log and the debugger | P | M | G, B, E |
| `basics/tools` | The tools: the terminal, files, a code editor and git | P | M | B, E (side step for G) |

Consequences: `make/cpp-for-scripts` is removed (what is special about script code moves to `make/first-script`
and `make/script-loop`); no `make/cpp-1`, `make/cpp-2`, `basics/first-program`, `basics/programming` (XL) or
`start/terminal`. `basics/cpp` (XL) is split into four primers for tracks B and E: `basics/cpp-memory` (L:
pointers, references, lifetimes, RAII, smart pointers), `basics/cpp-classes` (M: inheritance, virtual calls,
interfaces), `basics/cpp-generic` (M: templates, lambdas, the standard containers), `basics/cpp-modern` (M: move
semantics, `constexpr`, `optional`, `variant`, `span`, concepts as Strata uses them). `basics/build` becomes P/L
and builds a two-file program by hand and then with CMake. `core/debugging` (I/M) is added for debugging Strata
itself (debugger setup per OS, asserts and verifies, the log, crash reports, debugging one test).

## R6 — Marks for wave 8 (OL3, §3.3)

- **W8**: written in phase B. `light/local-shadows`, `light/area-lights`, `indirect/gi-voxels`,
  `indirect/gi-cascades`, `indirect/gi-limits`, `make/lamps`, `make/gi`.
- **W8r**: written in phase A with the named section revised in phase B: `light/lights`, `light/many-lights`,
  `gpu/frame-tour`, `image/quality-settings`, `make/look`, `make/quality`, `make/performance`. Their phase A text
  states no preset value in prose (values come from generated tables).
- No third mark. A feature that already landed is described at the pin; the pin move's diff decides what is
  re-read. "New in 0.8.0" for readers is front matter (`since: 0.8.0`), not a mark of the plan.
