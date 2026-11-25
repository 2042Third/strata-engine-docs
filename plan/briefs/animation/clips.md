# Brief: `animation/clips`

| Field | Value |
| --- | --- |
| Title | Clips: sampling motion |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `animation/skeletons`, `assets/loading`, `basics/math-interpolation` |
| From | animation ch. 4; 1.3 (sampling with the three glTF interpolations, keyframe reduction, shared key times, the STAC cooked format, safe loading) |
| Unit | `plan/allocation/animation.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `animation/clips` — Clips: sampling motion

**Covers.** The job: an `AnimationClip` holds keys for the joints it moves and answers "what is this joint's local
pose at time t"; it knows joints by name only, until it is bound to a skeleton. The problem and how engines solve it:
the cost of finding keys and of storing them; keyframe reduction (Strata), quantization and curve fitting, and uniform
sampling with compression, each with its cost; Strata reduces only, and compression waits until it is measured to help
(the absence itself is `animation/limits`'). Clips and channels: one channel per joint and path (translation,
rotation, scale), Step, Linear and CubicSpline keys, the duration as the last key, the first and last values held
outside the keys; the clip-storage diagram (one shared array of times, one array of values, cubic triplets of
in-tangent, value and out-tangent). Sampling, in the order data flows: `FindKey`'s binary search with `upper_bound`;
glTF's three samplers in `SampleChannel`; slerp along the shorter arc with an nlerp fallback when the arc is short;
glTF's cubic Hermite with tangents scaled by the key span (the forgotten scale is the classic mistake); the
interpolation-curves figure; `Sample` and `SampleRootMotionJoint`. Binding by name, once per clip and skeleton
(`AnimationClipBinding`: missing targets skipped, root motion channels recorded), so a clip plays on any skeleton with
the same joint names and on no other; the three ways engines bind a clip (by index, fast and fragile; by name, as
Strata does; through retargeting tables, as Unreal and Unity's humanoid rigs do) and the mistake of looking joints up
by name every frame; the rule of unique joint names. Building a clip: `Create` shares identical
key-time arrays (an FNV-1a hash, then an exact compare); `ReduceKeys` drops the keys that interpolation reproduces
(tolerance 1e-5, 1e-4 of quaternion distance for rotations, a window of 256 keys, a cancel check every 256 keys,
cubic splines untouched). The cooked form STAC v1 and its loader, which applies the skeleton page's rule: every count
bounded before allocation, channels outside the data, invalid times and duplicate channels rejected. The toy: a
linear-only sampler in about 50 lines. How it is tested: `Animation.Sampling` ("Step, linear and cubic spline channels
interpolate as glTF defines"; "Rotations interpolate along the shorter arc and stay normalized"; the two reduction
cases) and the clip cases of `Animation.Assets`. Exercises E2 (sample by hand, from `AnimationAssetTests.cpp` 317),
E3 (corrupt a cooked clip byte by byte, in the style of `AnimationAssetTests.cpp` 161) and a trace (find with a search
every place a clip is bound to a skeleton). At the end the reader can
sample a channel by hand for each interpolation and say what reduction and shared times save.

**Leaves out.**

- Interpolation as mathematics: lerp, curves through keys, Hermite curves → `basics/math-interpolation`
- Where the importer reads glTF samplers and calls the reduction → `animation/importing`
- Blending several sampled poses → `animation/blending`
- Clip compression and retargeting beyond names, as absences → `animation/limits`

**Fit.** `fits`: about 5,270 words against L (5,000). Five excerpts and three concepts (the three ways to bind a clip
among them) take the most; the three exercises take about 750.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `animation:36` | feature | home | `AnimationMath::Slerp`: the shorter arc, the nlerp fallback above cos 0.9995 |
| `animation:46-51` | feature | home | The clip asset, STAC v1, shared key times, `ReduceKeys`, binding by name, sampling |
| `animation:258` | concept | home | Interpolation as glTF's three samplers: step, linear (lerp, slerp against nlerp), cubic Hermite with span-scaled tangents |
| `animation:267` | concept | home | Clips and channels: keys per joint and path, holding outside the keys, binding by name and what it cannot retarget; the three ways to bind a clip (by index, fast and fragile; by name, Strata's; through retargeting tables, Unreal's and Unity's humanoid rigs) and the mistake of looking joints up by name every frame (about 120 words) |
| `animation:271` | concept | home | Sampling cost and storage: binary search, reduction, quantization and curve fitting, compression deferred |
| `animation:335` | code | home | `Strata/src/Strata/Animation/AnimationTypes.h:43-58`: slerp with the shorter-arc flip and the nlerp fallback |
| `animation:340` | code | home | `Strata/src/Strata/Animation/AnimationClip.cpp:459-536`: the key search and the three interpolations |
| `animation:341` | code | home | `Strata/src/Strata/Animation/AnimationClip.cpp:438-457`: binding by name once, recording the root motion channels |
| `animation:342` | code | home | `Strata/src/Strata/Animation/AnimationClip.cpp:206-222`: sharing identical key-time arrays |
| `animation:343` | code | home | `Strata/src/Strata/Animation/AnimationClip.cpp:231-315`: keyframe reduction with its window and cancellation |
| `animation:383` | figure | home | Diagram 4, the clip's storage |
| `animation:386` | figure | home | Diagram 5, step, linear and cubic curves through the same keys; slerp against lerp |
| `animation:467` | rule | home | Joint names are unique and clips bind by name |
| `animation:499-500` | hands-on | home | E2 and E3 |
| `new:17` | hands-on | home | Trace it yourself (track E): starting from `AnimationClip::Bind`, find with a search every place that binds a clip to a skeleton (once per clip of an asset set, once for a clip played directly), and say why no joint is looked up by name while the clip plays. Evidence: `Strata/src/Strata/Animation/AnimationClip.cpp:438-457`; `Strata/src/Strata/Animation/AnimationSystem.cpp:485`, `:529` |
| `animation:539-540` | term | home | Clip, channel and path |
| `animation:542-547` | term | home | Step, linear and cubic spline; tangent (in and out); keyframe reduction; clip compression; binding; retargeting |
| `animation:465` | rule | use | The skeleton page's rule, applied to the STAC loader (`AnimationClip.cpp` 357-361) |
| `animation:420` | figure | use | The clip half of screenshot 6 |
| `animation:52` | feature | link | No clip compression, stated on `animation/limits` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Skeletons, joint names and local poses | `animation/skeletons` | must |
| Curves through keys: step, linear, cubic Hermite; lerp and its weight | `basics/math-interpolation` | must |
| Quaternions, slerp, q and -q | `basics/math-rotations` | must |
| Loading without stalling: loaders and cancellation | `assets/loading` | must |
| Hashes | `basics/data-formats` | must |
| Binary search and what it costs | `basics/data-structures` | must |
| `std::function` (the cancel check) | `basics/cpp-generic` | helps |
| Untrusted input | `assets/robustness` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `binding-clip-to-skeleton` | Binding (clip to skeleton) | - |
| `channel-animation` | Channel (animation) | - |
| `clip-animation` | Clip (animation) | - |
| `clip-compression` | Clip compression | - |
| `keyframe-reduction` | Keyframe reduction | - |
| `retargeting` | Retargeting | - |
| `tangent` | Tangent | - |
