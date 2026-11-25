# Brief: `basics/math-interpolation`

| Field | Value |
| --- | --- |
| Title | Blending and smoothing: lerp, easing, curves and exponential smoothing |
| Kind | P |
| Size | L |
| Tracks | B, E |
| Needs | `basics/math-change`, `basics/numbers` |
| From | new by split of `basics/math-change`, which could not hold both lessons at a primer's size; lerp and its weight, inverse lerp and remapping, smoothstep and easing functions, curves through keys (step, linear, cubic Hermite and Bezier at the use level), exponential smoothing (`1 - exp(-k dt)`) and why a fixed fraction per frame depends on the frame rate; home of interpolation as mathematics and of smoothing (interpolating rotations is `basics/math-rotations`') |
| Unit | `plan/allocation/basics-b.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/math-interpolation` — Blending and smoothing: lerp, easing, curves and exponential smoothing

**Covers.** In order: (1) lerp: a + (b - a) × t, its weight t from 0 to 1, the same as a weighted average whose weights
add to 1, for numbers, positions and colors (`glm::mix`); blending two values; (2) inverse lerp, remapping a value from
one range to another, and clamping; (3) smoothstep and easing functions: curves that start or end slowly, their graphs,
and which motion wants which; (4) curves through keys: a keyframe as a time and a value, step and linear interpolation
between keys, and finding the two keys around a time; (5) cubic Hermite curves, shaped by the keys' values and slopes,
and Bezier curves at the use level (control points that pull the curve); (6) bilinear and trilinear interpolation: lerps
along x, then y, then z, between the corners of a square or a cube, as a texture read or a 3D grid of values uses them;
(7) exponential decay: a quantity that loses the same fraction each second or each metre, its curve e^(-kt) with the e
of `basics/numbers`, the half-life and the time constant τ, and the total it adds up to over a distance d,
(1 - e^(-kd)) / k, as light through fog does (exponentials and their integrals); (8) exponential smoothing: moving a
fixed fraction of the remaining way toward a target in each step, why a fixed fraction per frame depends on the frame
rate, and `1 - exp(-k * dt)` (written `1 - exp(-dt / tau)` with the time constant) as the weight that does not, read in
`FollowCamera`'s smoothing line; the SDK's `Motion::SmoothDamp` named as a spring that also keeps a velocity; (9)
geometric series: after n steps that each keep a fraction r of the gap, the gap left is rⁿ, the sum 1 + r + r² + ...
is 1 / (1 - r), and how many frames a smoothed value needs to settle.

Figures: the lerp line, smoothstep with two easing curves, keys joined by step, linear and Hermite curves, bilinear
weights between four corners, decay curves stepped at 30 and at 120 frames per second against the exact curve. The
common mistakes: t outside 0 to 1 without a clamp, a fixed fraction per frame, a Hermite slope not scaled by the time
between its keys, angles lerped across 360°. Practice (three to eight exercises, `style.md` §8) ends with the optional
Coin Run item: a collected coin that rises and shrinks over half a second, its time remapped to 0 to 1 and eased with
smoothstep, and a camera that follows the ball with `1 - exp(-k * deltaTime)`, checked by a loop that simulates one
second at 30 and at 120 steps and logs both results. "Where the book uses it" names `world/interpolation`,
`animation/clips`, `image/taa`, `audio/spatial` and `light/fog`.

**Leaves out.**

- Interpolating rotations: slerp and nlerp → `basics/math-rotations`
- The exponential function and the number e → `basics/numbers`
- Strata's transforms drawn between fixed steps → `world/interpolation`
- glTF's samplers, tangents scaled by the key span, and key reduction → `animation/clips`
- Texture reads as sampling and filtering → `basics/signals`
- Smoothing recipes for a game maker's camera → `make/gameplay-math`
- Fog and how Strata draws it → `light/fog`
- The TAA history blend → `image/taa`
- Color lookup tables read with trilinear interpolation → `image/grading`

**Fit.** `fits`: about 5,400 words against L (5,000). The nine ideas at 400 to 600 words take the most (4,200); the
camera's smoothing line (100) and the fixed parts with the Test out box, Practice and the Coin Run item (1,100) take the
rest.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:66` | concept | home | Linear interpolation and its weight; a weighted average whose weights add to 1; blending numbers, positions and colors (`glm::mix`). Figure: the lerp line. General knowledge. |
| `new:67` | concept | home | Inverse linear interpolation, remapping and clamping. General knowledge. |
| `new:68` | concept | home | Smoothstep and easing functions. Figure: smoothstep and two easing curves. General knowledge. |
| `new:69` | concept | home | Keyframes, and step and linear interpolation between them; finding the two keys around a time. General knowledge. |
| `new:70` | concept | home | Cubic Hermite curves from values and slopes; Bezier curves at the use level. Figure: step, linear and Hermite curves through the same keys. General knowledge. |
| `new:71` | concept | home | Bilinear and trilinear interpolation between the corners of a square and a cube. Figure: the four bilinear weights. General knowledge. |
| `new:72` | concept | home | Exponential decay: the same fraction lost per second or per metre, e^(-kt), the half-life, the time constant, and its total over a distance, (1 - e^(-kd)) / k. General knowledge. |
| `new:73` | concept | home | Exponential smoothing, and frame-rate independence with `1 - exp(-k * dt)`. Figure: decay stepped at 30 and 120 frames per second. General knowledge. |
| `new:74` | concept | home | Geometric series: the gap left after n steps, the sum 1 / (1 - r), the frames a smoothed value needs to settle. General knowledge. |
| `new:75` | hands-on | home | Coin Run practice, from `make/project-coin-run`'s end state: a collected coin that rises and shrinks over half a second (inverse lerp, smoothstep, lerp), a follow camera with `1 - exp(-k * deltaTime)`, and one second simulated at 30 and at 120 steps. Evidence: `StrataScriptCore/Include/StrataScript/Entity.h:177-198` (`SetTranslation`, `SetScale`), `Samples/ThirdPerson/Scripts/FollowCamera.cpp:79` (the smoothing weight) |
| `animation:541` | term | home | Key and keyframe, a time and the value of a channel; one glossary entry with the seed's |
| `audio-input:649` | term | home | Exponential smoothing by `1 - exp(-dt / tau)`; one glossary entry with the seed's |
| `gamedev:378` | code | use | Line 79 of `Samples/ThirdPerson/Scripts/FollowCamera.cpp`, the weight `1 - exp(-FollowSharpness * deltaTime)`; the whole camera is `make/characters-cameras`' |
| `scripting:136` | feature | use | `Motion::SmoothDamp`, a critically damped spring that keeps its velocity between calls |
| `render-image:673` | term | link | Trilinear interpolation as the grading's lookup table reads it, on `image/grading`; the general entry, trilinear interpolation, is this page's at the glossary step (basics-b-q8) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The exponential function and the number e | `basics/numbers` | must |
| Powers and fractions | `basics/numbers` | must |
| Rates, accumulation and the area under a graph | `basics/math-change` | must |
| Vectors: adding and scaling them | `basics/math-vectors` | must |
| A script of the playground: `OnUpdate`, `deltaTime` and `Log::Info` | `basics/programming-1` | must |
| Loops and functions | `basics/programming-2` | must |
| Moving an entity from a script (`SetTranslation`) | `basics/math-vectors` | must |

**Starting state.** The optional Coin Run item of Practice starts from the download of `make/project-coin-run`'s end
state, as the outline's introduction of part `basics` says for every primer after `basics/debugging`: Coin Run as
`make/project-coin-run` finishes it, with the rolling ball, the spinning coins, the HUD, the sounds, winning, losing and
the restart. The page's other examples and exercises run in the playground (`style.md` §8), which is no checkpoint.

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `bezier-curve` | Bezier curve | Bézier curve |
| `cubic-hermite-curve` | cubic Hermite curve | Hermite curve |
| `easing-function` | easing function | easing |
| `exponential-smoothing` | exponential smoothing | - |
| `frame-rate-independence` | frame-rate independence | - |
| `inverse-linear-interpolation` | inverse linear interpolation | inverse lerp |
| `keyframe` | keyframe | - |
| `linear-interpolation` | linear interpolation | lerp |
| `remapping` | remapping | - |
| `smoothstep` | smoothstep | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-b-6 | should | missing-item | `new:75` on `basics/math-interpolation` | The Coin Run item builds a camera that follows the ball. The ball is a body that moves in fixed steps, and the interactive editor draws it between its last two steps. A camera that reads `GetWorldPosition` in `OnUpdate` follows the simulated pose, which runs ahead of the drawn ball and moves in steps, so the view judders. The SDK says that cameras read `GetDrawnPosition` in `OnLateUpdate`, and `FollowCamera` does so. Track B meets neither: `make/script-loop` leaves them to block B. | The item's camera reads `GetDrawnPosition` in `OnLateUpdate`, with two sentences of why and a link to `world/interpolation` (about 60 words); the `use` row of `scripting:120` for it. | `allocation/basics-b.md:571-573`, `:605`; `allocation/make-a.md:979`; `StrataScriptCore/Include/StrataScript/Entity.h:204-206`; `Samples/ThirdPerson/Scripts/FollowCamera.cpp:4`, `:43`, `:74`, `:79`; `StrataEditor/src/EditorLayer.cpp:108-109`; `Strata/src/Strata/Scene/Scene.h:477-482` |
| critic-basics-b-7 | should | missing-item | new item on `basics/math-interpolation`, for the mistake "angles lerped across 360°" | The page lists the mistake, but no row holds its fix: the shortest signed difference of two angles, wrapped into -180° to 180°. The samples turn bodies and cameras with it, `std::remainder(target - yaw, 360)` and then a clamp to a turn rate. The only page that shows it is `make/project-platformer`, on track G. | A concept row: the shortest difference of two angles with `std::remainder`, then lerped, or limited to a turn rate (`std::clamp` by the speed times `deltaTime`), as the fix of the mistake (about 120 words). | `allocation/basics-b.md:570`, `:596-604`; `allocation/make-c.md:251`; `Samples/ThirdPerson/Scripts/ThirdPersonPlayer.cpp:97-100`; `Samples/ThirdPerson/Scripts/FollowCamera.cpp:68` |
