# Notes: `basics/math-interpolation`

## New terms

- **bilinear interpolation**: a blend of the four corner values of a square, made by lerps along x on two edges and then along y between the results. Home: `basics/math-interpolation`. Aliases: bilinear blend.
- **trilinear interpolation**: a blend of the eight corner values of a cube, made by bilinear interpolation on two squares and a lerp between the results. Home: `basics/math-interpolation`. Aliases: trilinear blend. (The glossary's `render-image:673` entry for the grading's lookup table links here.)
- **exponential decay**: a quantity that loses the same fraction in each equal step of time or distance, `v0 e^(-kt)`. Home: `basics/math-interpolation`. Aliases: decay.
- **time constant**: the time `tau = 1 / k` after which an exponential decay has fallen to 1 / e, 36.8 %, of its start. Home: `basics/math-interpolation`. Aliases: tau.
- **half-life**: the time an exponential decay needs to lose half its value, `ln 2 / k`. Home: `basics/math-interpolation`. Aliases: half-lives.
- **geometric series**: a sum in which each term is the one before it times the same number r, with the sum 1 / (1 - r) for 0 < r < 1. Home: `basics/math-interpolation`. Aliases: none.

The page defines in bold the ten glossary terms of its brief: linear interpolation (lerp), inverse linear interpolation (inverse lerp), remapping, easing function, smoothstep, keyframe (key), cubic Hermite curve, Bezier curve, exponential smoothing and frame-rate independence.

## Requests

- `tools/data/extra-words.txt`: "bilinear" (the proposed term above; its `word-list` finding is left until the term exists).
- `tools/external-hosts.txt`: `www.youtube.com` for Freya Holmér's talk "Lerp smoothing is broken" and `iquilezles.org` for Inigo Quilez's "Useful little functions"; both Further reading entries are cited without a link.
- Figures: five diagram requests in `src/content/figures/basics/math-interpolation.json` (the lerp line, four easing curves, step, linear and Hermite curves through two keys, the four bilinear weights, the decay stepped at 30 and 120 frames per second). None is drawn yet.

## Not verified

- Coin Run's details (practice 7): the name of the ball, how a coin is collected and what the camera looks at. `make/project-coin-run` is not written, so the `CoinPop` and camera scripts are `pseudocode`, not compiled; the answer tells the reader that their own collecting code starts the pop, and that 4 is only a first value for the camera's sharpness. The names `Script`, `OnUpdate(float)`, `OnLateUpdate(float)`, `TransformComponent`, `SetTranslation`, `SetScale`, `SetWorldPosition`, `GetDrawnPosition` and `ST_SCRIPT_FIELD` come from `StrataScriptCore/Include/StrataScript/Entity.h` and `Samples/ThirdPerson/Scripts/FollowCamera.cpp` at the pin.
- The sentences of "Where the book uses it" about `animation/clips`, `image/taa`, `audio/spatial` and `light/fog` follow the brief; those pages are not written. The fog model in the exponential decay section (a layer of fog adding light that crosses the fog in front of it, with the total (1 - e^(-kd)) / k) is general mathematics, not a statement about how Strata draws fog.
- That `std::remainder` returns a value from -180 to 180 for a divisor of 360 is the C++ standard's, not read at the pin; the pin's use is `Samples/ThirdPerson/Scripts/ThirdPersonPlayer.cpp` lines 97 to 100 and `FollowCamera.cpp` line 68.
- Figures are not taken or drawn; the numbers in their requests were computed by the page's sketches and by hand.

## Findings not applied

None: both findings hold at the pin and are applied.

- `critic-basics-b-6`: applied in practice 7. The camera reads `GetDrawnPosition` in `OnLateUpdate`, with two sentences of why and a link to `world/interpolation`; the follow-camera section says the same of `FollowCamera.cpp` (lines 73 to 79 quoted; the SDK comment on `GetDrawnPosition` at `Entity.h` 204 to 206). The `scripting:120` use row is the planner's.
- `critic-basics-b-7`: applied in the section "Angles wrap around, so blend the shortest difference" (`std::remainder`, then the turn-rate limit with `std::clamp`, as `ThirdPersonPlayer.cpp` lines 97 to 100 do) and in the common mistakes.

## Clerk

- Admitted: bilinear interpolation, exponential decay (alias "decay" left out: one everyday word), time constant (alias tau), half-life, geometric series. Refused: trilinear interpolation (homed on `image/grading`; the planner may move it here).
- `external-hosts.txt`: `iquilezles.org` (front page fetched). Left for the planner: `www.youtube.com` (a platform anyone publishes on, not a publisher's or project's own site).

## Track walk E-final-4

Each sketch of the page compiled with `cl /std:c++20 /EHsc` (Visual Studio 2026, 19.50) and with g++ 15 `-std=c++20`, glm from the 0.8.0 package's `StrataScriptCore/ThirdParty/glm`; both printed the same output (`docs-work/walkfix-E4/cl/`, 2026-11-24). The exact Windows line of the page was run in PowerShell in a Visual Studio developer environment (`cmdtest/`).
