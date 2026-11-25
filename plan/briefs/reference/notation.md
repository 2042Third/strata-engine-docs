# Brief: `reference/notation`

| Field | Value |
| --- | --- |
| Title | Conventions and notation |
| Kind | R |
| Size | M |
| Tracks | - |
| Needs | - |
| From | new; axes, handedness, units, matrix order, depth and color spaces and the symbols of the rendering parts in one place, checked against `gpu/coordinates` and `basics/math-matrices` |
| Unit | `plan/allocation/reference.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `reference/notation` — Conventions and notation

**Covers.** The paragraph on top says what the page is: every convention and symbol the book uses, in one place, each
row linking the page that teaches it; the page defines nothing (`../book.md`, one-home table). The tables, in this
order. (1) Strata's conventions, hand-checked against the pin, each with its evidence and its home: right-handed, +Y
up, -Z forward (`Math.h`), glTF models facing +Z; D3D-style clip space through NVRHI (framebuffer origin top-left, NDC
+Y up, depth from 0 to 1); reversed Z (near is 1, far is 0, depth cleared to 0, `GreaterOrEqual`); the fullscreen UVs
`uv = (ndc.x * 0.5 + 0.5, 0.5 - ndc.y * 0.5)`; front faces counter-clockwise, mirrored instances clockwise;
column-major matrices with `mul(M, v)` and matrix constructors that take rows in shaders; quaternions stored x, y, z, w
across the ABI; Euler angles in degrees in the Inspector and commands, radians in code; camera-relative positions in
scene shaders. (2) Units: SI for space, mass and time; the photometric units of light (lux for the sun, candela for
points and spots, nits for the sky, ambient and emission) and exposure in EV, with the reference values table's
light levels; bytes as KiB and MiB. (3) Color spaces: linear scene values, pre-exposed HDR targets, sRGB encoding at
the end, textures marked sRGB or linear, normal maps as X and Y with Z rebuilt. (4) The symbols of the parts, collected
by the build from the notation tables of the part index pages (and of the first pages of parts without one): symbol,
how it is read, meaning, unit, the page that introduces it. Hand-written: the paragraph on top, the three hand-checked
tables, one note that a page using another convention says so and links here (`../style.md` §4), and `## Where it
lives in Strata` (`Strata/src/Strata/Math/Math.h`, `Strata/shaders/Include/Common.slang`, `CMake/StrataShaders.cmake`,
`AGENTS.md` "Renderer conventions"). It is checked against `gpu/coordinates` and `basics/math-matrices`.

**Leaves out.**

- Matrices, transforms and spaces, taught → `basics/math-matrices`
- Strata's API conventions and the camera, taught → `gpu/coordinates`
- Light units and exposure, taught → `light/units-exposure`
- Color, linear and sRGB, taught → `basics/color`
- Every symbol with the page that teaches it, for mathematics → `appendix/math-cheatsheet`
- Positions, rotations and units for game makers → `make/transforms-units`

**Fit.** `fits`: about 1,300 words against M (3,000). The symbol tables that the build collects from the part index
pages give the page its size, about 1,500 words written on those pages. The prose is the paragraph on top, the
conventions table (about 15 rows), the units and color tables (about 15 rows), one note and the strip.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:139` | feature | link | The conventions comment of `Math.h` |
| `render-core:137-143` | feature | link | Clip space, reversed Z, fullscreen UVs, front faces, handedness, camera-relative space and column-major matrices |
| `scripting:47` | feature | link | The ABI's transform: quaternions as x, y, z, w |
| `scripting:120` | feature | link | `TransformComponent`'s forward, right and up (-Z forward) |
| `gamedev:71` | feature | link | The conventions a maker must know |
| `render-direct:101` | feature | link | The photometric units on one scale |
| `render-direct:105` | feature | link | The reference values table of light levels |
| `render-image:130` | feature | link | The sRGB encoding at the end of the chain |
| `render-image:27` | feature | link | The HDR scene color target |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Matrices and transforms | `basics/math-matrices` | helps |
| Coordinate systems and the camera | `gpu/coordinates` | helps |
| Rotations and quaternions | `basics/math-rotations` | helps |
| Color: linear, sRGB and HDR | `basics/color` | helps |
| Light units | `light/units-exposure` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-reference-13 | should | duplicate | `reference/game-makers`, sections (1), (4) and (7) | `tools/data/game-makers.json` chooses rows only of commands, components, SDK names and runtime options, so the cheat sheet's editor section (panels, shortcuts, chips), its conventions and its project folder can only be typed by hand. They copy facts that `reference/editor` (panels, shortcuts, chips) and `reference/notation` (conventions) hold as tables, and two hand-kept copies drift at each pin move. | The cheat sheet takes those rows from the tables that hold them: `game-makers.json` gains lists for panels, shortcuts and conventions, which `render` reads from data files that also make the tables of `reference/editor` and `reference/notation`; or the three sections become links to those tables with one line of use each. `../pipelines.md` §7.2 says which. No words added. | `allocation/reference.md:1153-1170`, `:861-866`, `:1219-1224`; `../pipelines.md:1145-1147` |
