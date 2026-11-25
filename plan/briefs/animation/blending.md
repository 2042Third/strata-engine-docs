# Brief: `animation/blending`

| Field | Value |
| --- | --- |
| Title | Blending and cross-fades |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `animation/state-machines` |
| From | animation ch. 8; 1.6 (weights, the four entries, quaternion blending, phase mismatch) |
| Unit | `plan/allocation/animation.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `animation/blending` — Blending and cross-fades

**Covers.** The job: while a cross-fade runs, `AnimatorInstance` plays up to four entries at once and blends their
poses into one; when the fade ends only the target is left. The problem and how engines solve it: a cut from one state
to the next pops; cross-fades with weight schedules (Strata), blend trees and blend spaces (which Strata does not
have), and inertialization, which decays the difference to the previous pose instead of evaluating both (not used);
the writer gives the sources for who uses which. Cross-fades, in the order data flows: `StartState` (the excerpt)
saves each playing entry's share, drops the faintest when a fifth would start and renormalizes the others;
`UpdateWeights` (the excerpt) grows the target's weight linearly with the fade's progress and scales the others by what
is left, so the weights always sum to 1; the timeline of three fades that interrupt each other. Blending poses in
`Evaluate` (the excerpt): one entry samples straight over the rest pose; several entries sum translations and scales
linearly and rotations as a weighted sum on the first entry's hemisphere, then normalize (blending matrices instead of
TRS shears the joints; the sign test is there because q and -q are one rotation); then forward kinematics; the root hold
at the end of `Evaluate` is `animation/root-motion`'s. A cross-fade halfway, captured at fixed steps with `play.step`
(screenshot). Phase mismatch: the robot's walk and run are 27% of a cycle apart in their cross-fade (`Docs/Roadmap.md`
1619-1620), so the feet slide; there are no sync markers. The toy: two poses and a fade, in about 40 lines. The
alternatives not chosen: slerp applied pair by pair, inertialization, sync markers, blend spaces. How it is tested:
"Cross-fade weights add up to 1, also when fades interrupt each other" and "A cross-fade blends the poses by the
weights" (`AnimatorTests.cpp`). Exercises E6 (start the target at the source's normalized phase and measure the robot's
foot sliding), E7 (slerp pair by pair against the weighted sum, for three entries or more) and a trace (a cross-fade
from the system's command to the weights, found with a search). At the end the reader can
compute every entry's weight while fades interrupt each other and explain why rotations are summed on one hemisphere.

**Leaves out.**

- Normalized time, which a phase-matched fade would use → `animation/time-events`
- Where the root's travel is weighted by the same shares → `animation/root-motion`
- Blend trees, layers, additive clips and sync markers as absences → `animation/limits`
- Slerp and the double cover as mathematics → `basics/math-rotations`

**Fit.** `fits`: about 3,750 words against M (3,000). Three excerpts, two figures and the concept take the most; the
three exercises take about 750.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `animation:90-91` | feature | home | Cross-fades (`c_MaxPlaying` = 4, linear growth, kept proportions, the faintest dropped) and pose blending |
| `animation:289` | concept | home | Blending and cross-fades: weighted pose blending, weight schedules, interrupted fades, inertialization, phase mismatch; blending matrices as the mistake |
| `animation:345` | code | home | `Strata/src/Strata/Animation/AnimatorInstance.cpp:247-288`: starting a cross-fade, saved shares, dropping the faintest of four |
| `animation:346` | code | home | `Strata/src/Strata/Animation/AnimatorInstance.cpp:587-609`: the weights of a fade and its end |
| `animation:349` | code | home | `Strata/src/Strata/Animation/AnimatorInstance.cpp:766-848`: evaluating a pose, one clip or several on one hemisphere, then forward kinematics; `animation/root-motion` reads its last part |
| `animation:389` | figure | home | Diagram 7, cross-fade weights over time |
| `animation:426` | figure | home | Screenshot 10, a cross-fade halfway, captured at fixed steps |
| `animation:487` | rule | home | Cross-fading walk to run without phase matching slides the feet |
| `animation:503-504` | hands-on | home | E6 and E7 |
| `new:23` | hands-on | home | Trace it yourself (track E): follow a cross-fade with a search from `AnimationSystem::CrossFade` through `AnimatorInstance::CrossFade` to `StartState` and `UpdateWeights`, and name the line that drops the faintest of four entries and the one that keeps the weights' sum at 1. Evidence: `Strata/src/Strata/Animation/AnimationSystem.cpp:989-993`; `Strata/src/Strata/Animation/AnimatorInstance.cpp:315-346`, `:247-288`, `:587-609` |
| `animation:538` | term | home | Hemisphere (quaternion) |
| `animation:567-570` | term | home | Cross-fade, blend weight, sync markers and phase matching, inertialization |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| State machines, transitions and their fade durations | `animation/state-machines` | must |
| Forward kinematics | `animation/skeletons` | must |
| Quaternions: q and -q, normalization, slerp | `basics/math-rotations` | must |
| Lerp and its weight | `basics/math-interpolation` | must |
| Normalized time (for E6) | `animation/time-events` | helps |
| Pausing and stepping a game (`play.step`) | `editor/stepping` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `blend-weight` | Blend weight | - |
| `cross-fade` | Cross-fade | - |
| `hemisphere-quaternion` | Hemisphere (quaternion) | - |
| `inertialization` | Inertialization | - |
| `sync-markers` | Sync markers | phase matching |
