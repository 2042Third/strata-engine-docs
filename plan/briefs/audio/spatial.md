# Brief: `audio/spatial`

| Field | Value |
| --- | --- |
| Title | Sound in space |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `audio/clips-voices-sources`, `basics/math-vectors` |
| From | audio-input ch. 4; concepts A7-A8 (panning, attenuation models, minimum and maximum distance, rolloff, Doppler and velocity estimation) |
| Unit | `plan/allocation/audio-input.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `audio/spatial` — Sound in space

**Covers.** The job: how a sound comes from where its source is (the listener, panning and distance attenuation) and how
its pitch follows motion (the Doppler effect), with the velocities Strata derives for it. The page's example is the
Physics Playground's impact sound heard from where two bodies hit, and a rolling ball that passes the listener. In this
order: the listener (position, forward, up and velocity; right = forward × up; the engine's frame, right-handed with +Y up
and -Z forward; zero vectors and NaNs refused at the boundary) and the listener-frame diagram; panning by the source's
angle (pan laws for stereo; HRTF for headphones and surround named); attenuation from the physical 1/r: the four models,
minimum and maximum distance, rolloff, OpenAL's "clamped" models, and the plot of the curves; the toy version (an inverse
gain and a pan from one dot product); the real code of `SetAttenuation` (`NoAttenuation` mapped to inverse with rolloff
0 because miniaudio's "none" also turns off panning and Doppler; the minimum distance kept above 0.01; a maximum below
the minimum treated as the minimum; the name `NoAttenuation`, because X11 defines `None`).

Then the Doppler effect from zero: the shift from the relative velocity along the line between source and listener,
the speed of sound, why it grows without bound near that speed, and why a velocity is per second, never per frame. The
two ways to get a velocity (from physics, or from moves over time) and Strata's derivation: the body's velocity limited
to 150 units/s; otherwise the move over the time since the last move, smoothed with `1 - exp(-t / 0.1)`; a teleport
gives no velocity; still for two fixed steps means stopped. A timeline shows fixed steps at 60 Hz against frames at
144 Hz. The vendored miniaudio decides the pan law, the gain smoothing, the Doppler factor and the speed of sound: the
writer reads them in `Strata/vendor/miniaudio` before stating them. Then what Strata does not do (occlusion and reverb
zones; a model chosen per component), the alternatives, the tests and changing it safely. At the end the reader can
predict the gain of a source at a distance under each model, and explain why a velocity measured per frame jitters when
fixed steps and frames run at different rates.

**Leaves out.**

- The records that place sources every frame and choose the listener → `audio/scene-system`
- The sequence lock that carries the up vector → `audio/engine`
- Vectors, dot and cross products → `basics/math-vectors`
- Exponential smoothing as mathematics → `basics/math-interpolation`
- Rigid bodies and their velocities → `physics/bodies-colliders`
- The RMS test method → `audio/testing`

**Fit.** `over`: about 4,500 words against M (3,000). Two concepts from zero (the listener, panning and attenuation;
the Doppler effect: about 1,050 words), two excerpts, three figures, three rules, two absences and two exercises go past
M's top. Proposed: L (5,000) by S2, whose range holds the estimate.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `audio-input:33` | feature | home | The listener: position, forward, up and velocity; non-finite and zero vectors refused; right-handed, +Y up, -Z forward, which are miniaudio's own defaults |
| `audio-input:62` | feature | home | The four attenuation models clamped to [Min, Max]; `NoAttenuation` as inverse with rolloff 0; the minimum distance above 0.01 |
| `audio-input:79` | feature | home | Doppler velocity from the simulating body or an ancestor's (`IBodyMotionQuery::GetPointVelocity`), else from moves; the limit, the smoothing, teleports and stops |
| `audio-input:261` | concept | home | A7: the listener, panning and attenuation curves; MaxDistance below MinDistance; non-spatial sounds have no position |
| `audio-input:270` | concept | home | A8: the Doppler effect and how to get velocities without jitter |
| `audio-input:400` | code | home | `Strata/src/Strata/Audio/AudioVoice.cpp:338-361`: the models and the mapping of `NoAttenuation`; with the enum, `Strata/src/Strata/Audio/AudioSource.h:15-24` |
| `audio-input:401` | code | home | `Strata/src/Strata/Audio/AudioSystem.cpp:664-700`: the velocity over the time since the last move, smoothing, teleports and stops; with `ComputeVelocity` and `LimitSpeed`, `:45-65` |
| `audio-input:432` | figure | home | Plot: gain against distance for the four models with Min 1, Max 50 and Rolloff 1 and 2, the clamped regions shaded |
| `audio-input:434` | figure | home | Diagram (top view): forward -Z, up +Y, right +X; a source at +X louder on the right; facing +Z flips it; a rolled listener |
| `audio-input:436` | figure | home | Timeline: fixed steps at 60 Hz against frames at 144 Hz; the naive velocity against Strata's; the teleport cut-off |
| `audio-input:507-511` | rule | home | Limit Doppler speeds and treat jumps as teleports; derive velocity over the time since the last move; refuse zero vectors and NaNs |
| `audio-input:579` | hands-on | home | Exercise: add an attenuation-model field to `AudioSourceComponent` (property, `ApplyComponent`, the feature test, `AudioSystemTests`) |
| `audio-input:639-646` | term | home | Listener, spatialization, panning, HRTF, attenuation and attenuation model, minimum and maximum distance, rolloff, Doppler effect |
| `audio-input:648` | term | home | Teleport (audio) |
| `audio-input:746` | open | home | The pan law, the gain smoothing, the Doppler factor and the speed of sound are miniaudio's defaults (Strata sets no Doppler factor): the writer verifies them in the vendored source before stating them |
| `audio-input:539` | rule | use | Why the enum value is `NoAttenuation` (home `core/conventions`) |
| `audio-input:649` | term | use | Exponential smoothing (home `basics/math-interpolation`) |
| `audio-input:406` | code | use | The panning test, named in "How it is tested" |
| `new:6` | not-done | home | Occlusion and reverb zones: walls do not muffle a source and rooms add no reverb; how engines trace or tag them. Evidence: `git grep -niE "occlu\|reverb" 822a7a46 -- Strata/src/Strata/Audio` finds nothing |
| `new:7` | not-done | home | A choice of attenuation model per component: `AudioSourceComponent` has no model field, so components always use Inverse (the exercise adds one). Evidence: `Strata/src/Strata/Audio/AudioComponents.h:11-22` |
| `new:24` | hands-on | home | Trace it yourself (D27): a breakpoint in `AudioSystem::UpdateMotion` on a scene with one looping spatial Audio Source on a rigid body and another on an entity that a script moves shows which velocity each gets: the body's, limited (`GetBodyVelocity`, `LimitSpeed`), or the move over the time since the last move, smoothed, and zero after a teleport or two still fixed steps. Evidence: `Strata/src/Strata/Audio/AudioSystem.cpp:664-700`, `:702-715`, `:45-65` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Vectors: length, dot and cross products, normalizing | `basics/math-vectors` | must |
| Axes and handedness: right-handed, +Y up, -Z forward | `basics/math-matrices` | must |
| The exponential function | `basics/numbers` | must |
| Exponential smoothing, `1 - exp(-t / tau)` | `basics/math-interpolation` | must |
| Velocity as a rate of change | `basics/math-change` | must |
| Fixed steps against frames | `core/time` | must |
| Gain and decibels | `audio/sound-in-a-computer` | must |
| Sources, their settings and their voices | `audio/clips-voices-sources` | must |
| An entity's world transform | `world/scene-graph` | must |
| Rigid bodies and their velocity | `physics/bodies-colliders` | helps |
| The Audio scene system, whose records call this code | `audio/scene-system` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `attenuation` | Attenuation | - |
| `attenuation-model` | attenuation model | - |
| `doppler-effect` | Doppler effect | - |
| `hrtf` | HRTF | - |
| `listener-audio` | Listener (audio) | - |
| `max-distance` | max distance | - |
| `min-distance` | Min distance | - |
| `panning` | Panning | - |
| `rolloff` | Rolloff | - |
| `spatialization` | Spatialization | - |
| `teleport-audio` | Teleport (audio) | - |
