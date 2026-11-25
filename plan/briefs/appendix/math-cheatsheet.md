# Brief: `appendix/math-cheatsheet`

| Field | Value |
| --- | --- |
| Title | Math cheat sheet |
| Kind | R |
| Size | M |
| Tracks | - |
| Needs | - |
| From | the basics pages; a "how to read the symbols" table (Σ, ∫, ‖v‖, ·, ×, θ) that names the page teaching each symbol |
| Unit | `plan/allocation/appendix.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `appendix/math-cheatsheet` — Math cheat sheet

**Covers.** One paragraph on how to read the page: it teaches nothing; each line names the primer that teaches it, and
a reader who meets a symbol here for the first time follows that link. Then two tables. The first is how to read the
symbols: each symbol that a page of the book uses (Σ, ∫, ∂, ∇, ·, ×, ‖v‖, |x|, θ and φ, ω, π, e and exp, log, √, ∈, ≈,
≤, ∞, the hat of a unit vector, the transpose and the inverse of a matrix, the conjugate of a quaternion, and big-O), with
how it is read aloud, what it does, one example with small numbers, and the page that teaches it. The second holds the
formulas, grouped by primer in the order of `basics`: numbers (powers and logarithms, EV stops and decibels, e and the
exponential, the spacing of floating-point numbers), data structures (the costs in big-O), vectors (length, normalizing,
the dot product and the angle, the cross product, `atan2`), matrices (TRS, composing transforms, the inverse of a rigid
transform), bases (the transpose of an orthonormal basis as its inverse, changing basis, the determinant and its sign as
a mirror, normals through the inverse transpose, decomposing a matrix into translation, rotation and scale), projection
(the perspective divide, reversed depth), rotations (axis and angle to a quaternion, rotating a vector, slerp),
geometry (a ray against a plane, a sphere and a box; the distance of a point to a plane), change (the explicit and the
semi-implicit Euler step, F = m a, impulse), interpolation (lerp, inverse lerp and remapping, smoothstep, exponential
smoothing with 1 - exp(-k dt)), color (the sRGB transfer function, luminance), signals (the Nyquist rate, box and tent
filters), probability (expected value, the Monte Carlo estimate with a density), and the sphere (the solid angle of a
sphere, spherical coordinates, the first bands of spherical harmonics, the octahedral map). Each formula has one line
of meaning, its units, and the page that derives it; no derivation is repeated.
Strata's own conventions (axes, handedness, units, matrix order, depth and color spaces) and the rendering parts'
symbols are `reference/notation`'s: the page links it once. The symbol table is checked against the notation tables
of the parts (`style.md` §4), so every symbol a page introduces is listed here with its teacher.

**Leaves out.**

- Teaching each symbol and formula → `basics/numbers`, `basics/math-vectors`, `basics/math-matrices`, `basics/math-bases`, `basics/math-change`, `basics/math-probability`
- Strata's conventions and the rendering parts' symbols → `reference/notation`
- Strata's math types and functions (`AABB`, `Frustum`, `Ray`, the projections) → `core/math`

**Fit.** `fits`: about 430 words against M (3,000). That is the prose: the paragraph on how to read the page and one
line for each of the 14 groups; the page's size comes from its two tables, written by hand (R36): about 30 symbols (700
words) and about 65 formulas in 14 groups (1,850).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:117` | concept | link | How to read the symbols: each operator symbol with how it is read, what it does and the page that teaches it (`style.md` §4 asks for this table). General knowledge. |
| `new:118` | concept | link | Numbers: powers, logarithms, EV stops, decibels, e and the exponential, the spacing of floats; taught on `basics/numbers`. General knowledge. |
| `new:119` | concept | link | The costs of data structures in big-O; taught on `basics/data-structures`. General knowledge. |
| `new:120` | concept | link | Vectors: length, normalizing, dot and cross products, `atan2`; taught on `basics/math-vectors`. General knowledge. |
| `new:121` | concept | link | Matrices: TRS, composing transforms, the inverse of a rigid transform; taught on `basics/math-matrices`. General knowledge. |
| `new:186` | concept | link | Bases: the transpose and orthonormal bases, changing basis and tangent space, the determinant and its sign as a mirror, normals through the inverse transpose and the cofactor matrix, decomposing a matrix into translation, rotation and scale; taught on `basics/math-bases`. General knowledge. |
| `new:122` | concept | link | Projection: the perspective divide, homogeneous coordinates, reversed depth; taught on `basics/math-projection`. General knowledge. |
| `new:123` | concept | link | Rotations: axis and angle, quaternions, rotating a vector, slerp; taught on `basics/math-rotations`. General knowledge. |
| `new:124` | concept | link | Geometry: rays against planes, spheres and boxes, point-plane distance; taught on `basics/math-geometry`. General knowledge. |
| `new:125` | concept | link | Change: rates, accumulation, Euler steps, Newton's second law and impulse; taught on `basics/math-change`. General knowledge. |
| `new:126` | concept | link | Interpolation: lerp, inverse lerp, remap, smoothstep, exponential smoothing; taught on `basics/math-interpolation`. General knowledge. |
| `new:127` | concept | link | Color: the sRGB transfer function, luminance; taught on `basics/color`. General knowledge. |
| `new:128` | concept | link | Signals: sampling, the Nyquist rate, filters; taught on `basics/signals`. General knowledge. |
| `new:129` | concept | link | Probability: expected value, densities, the Monte Carlo estimate; taught on `basics/math-probability`. General knowledge. |
| `new:130` | concept | link | The sphere: solid angle, spherical coordinates, spherical harmonics, octahedral maps; taught on `basics/math-sphere`. General knowledge. |
| `foundation:325` | concept | link | Math for engines as Strata chose it (glTF's axes, reversed Z with an infinite far plane), homed on `core/math` |
| `foundation:139` | feature | link | The conventions comment of `Math.h`, which `reference/notation` collects |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Binary, integers, floating point; powers, logarithms and the exponential function | `basics/numbers` | helps |
| Data structures and what they cost | `basics/data-structures` | helps |
| Vectors: length, direction, dot and cross products; angles in degrees and radians | `basics/math-vectors` | helps |
| Matrices, transforms, hierarchies and spaces | `basics/math-matrices` | helps |
| Bases, the determinant and normals: orthonormal frames, tangent space, mirrors and the inverse transpose | `basics/math-bases` | helps |
| Projection: view and projection matrices, homogeneous coordinates, depth | `basics/math-projection` | helps |
| Rotations: Euler angles, axis and angle, quaternions, slerp | `basics/math-rotations` | helps |
| Rays, planes, boxes and intersection tests | `basics/math-geometry` | helps |
| Change over time: rates, accumulation, Euler steps, Newton's laws | `basics/math-change` | helps |
| Blending and smoothing: lerp, easing, exponential smoothing | `basics/math-interpolation` | helps |
| Color: linear and sRGB values | `basics/color` | helps |
| Sampling, aliasing and filtering | `basics/signals` | helps |
| Probability, random numbers, integrals and Monte Carlo | `basics/math-probability` | helps |
| Solid angles, spherical coordinates, spherical harmonics, octahedral maps | `basics/math-sphere` | helps |

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
| critic-appendix-17 | could | thin-home | `appendix/math-cheatsheet` | The symbol list leaves out symbols that the primers teach and many pages use: Δ (Δt, a step of time), σ and σ² (the standard deviation and the variance) and E[X]. The formula groups leave out the variance and the standard deviation (taught on `basics/math-probability`), binary and hexadecimal place values, the range of an n-bit integer, shifts and bit masks (`basics/numbers`), and the costs of trees, heaps and sorting (`basics/trees-graphs`; `new:119` names only `basics/data-structures`). | Add these symbols and formulas with their teachers; `new:119` names both pages. About 120 words of table rows. | `allocation/appendix.md:419-433`, `:455`; `allocation/basics-b.md:494`, `:562`, `:807`, `:859`; `allocation/basics-a.md:514-521`, `:680-685`, `:712`; `style.md:336-337` |
