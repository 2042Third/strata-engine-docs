# Notes: `world/interpolation`

## New terms

- judder: a steady motion that looks jerky because it is drawn in unequal jumps; defined in bold in the section on the problem; home `world/interpolation`; no aliases.
- variable step: a simulation step as long as the frame that needed it; home `world/interpolation`; no aliases.
- extrapolation: drawing an entity where its last speed says it should be now, ahead of the newest simulated pose; home `world/interpolation`; aliases extrapolate, extrapolating.
- interpolated set: the scene's list of entities that the latest stepping frame moved, with an entry and a drawn matrix for each; home `world/interpolation`; no aliases.
- Compose and Exact: the other two roles of an interpolated entry besides Blend (the glossary homes only Blend); defined in bold in the map, one sentence each; home `world/interpolation`.

## Requests

- Words for `tools/data/extra-words.txt`: `judder` and `extrapolate` (with `extrapolating`, `extrapolation`), `overshoot` (`overshoots`), and the forms of the glossary term: `interpolate`, `interpolates`, `interpolated`. The page's last nine `word-list` failures are these words.
- Figures: `step-timeline` and `drawn-trace` are diagrams with SVGs drawn for this page (`src/assets/figures/world/interpolation/`); `drawn-trace` plots the toy sketch's output. The brief's plotted trace of a real sample at a high frame rate (item `scene-ecs:759`, choose `Samples/ThirdPerson` or `Samples/PhysicsPlayground`) is not requested: `core/time` already carries a capture of the Third-Person robot with interpolation off and on.
- Link hosts: none beyond `gafferongames.com`, which is on the list. The Unity entry in Further reading names its host, `docs.unity3d.com`, without a link because its exact address was not checked.

## Since

`since: 0.8.0`: the engine's guide marks interpolation as wave 8 work, and the Roadmap's Status records that `physics-timing` landed in landing 1 for 0.8.0 (`Docs/Roadmap.md` at the pin, the `physics-timing` bullet); `Docs/DeveloperGuide.md`, "Interpolation", says the same, and the Third-Person robot's numbers come from the 0.8.0 audit. 0.7.0 and earlier drew every entity at its latest pose.

## Not verified

- The `Spinner` system and its `SpinComponent` belong to `world/systems`, not yet written at this page's writing; exercise 4 assumes the entity rotates in `OnFixedUpdate`. Its expected counts (Entities 2, Blended 1, Composed 1, Exact 0) come from reading `CaptureInterpolation`, not from running a test.
- Which code reads the drawn transform for lights, the scene camera and world-space text: the page repeats the developer guide's list; only mesh proxies (`RenderScene.cpp` 428-437 at v0.8.0) and skinned palettes (`RenderScene.cpp` 1299) were traced.
- That the editor enables interpolation for Play and Simulate outside scripted runs (the guide's words; `EditorContext.h` 120-123 and `RuntimeApplication.cpp` 91 were read for the runtime only).
- The measurements 29.4 px (702 frames per second), the 2.1 ratio against 1.5, and half a step more latency (about 8 ms) are the developer guide's and the Roadmap's numbers, not measured here.
- The rounding explanation for why `from + (to - from) * alpha` beats `glm::mix` far from the origin is the page's own reasoning; the code comment says only "monotonic and exact at both ends".
- The Unity sentence (a rigid body chooses interpolation or extrapolation) repeats `core/time`'s; the article in Further reading was not read.
- The names of the commands `play.state`, `physics.stats` and `project.setSettings` come from the developer guide and `core/time`'s figure file, not from their code.

## Findings not applied

The brief lists no open findings. Left out of the page on purpose: the 330 bytes per entity and the 33 MB at 100,000 bodies of the developer guide (not checked against the structs), and the guide's editor measurements (2,000 balls at 356 and 501 frames per second).

## Clerk

- Admitted: judder, extrapolation (aliases extrapolate, extrapolates, extrapolated, extrapolating), interpolated set, Compose, Exact; Blend takes the page's wording; interpolation takes the aliases interpolate, interpolates, interpolated, interpolating.
- `extra-words.txt`: overshoot, overshoots. The other asked words are now glossary words (R54).
- Not admitted, because the page check would then fail and the page is the writer's: variable-step (the section "The problem and how engines solve it" would define 5 terms (term-section)). The part's reviewer splits the paragraph or section; the next clerk admits it then (the entries are in the wave-1b clerk's apply.py).

## Pin move to v0.8.0

- Read again at the move (process step 11). The absence list still holds: `Docs/Releases/0.8.0.md`, Known issues, Rendering, "Motion drawn between physics steps", lists world-space game UI, gizmos, picking, probes, fog, post-process volumes, the sky and the sun, and attachments outside their animator's hierarchy on simulated poses; `Docs/Roadmap.md`, "Interpolation, the rest", keeps them as later work with the 2.1 to 1.5 ratio. The page now cites the release notes and their 5.5 ms against 2.6 ms.
- Exercise 3's line numbers rechecked at the pin: `RenderScene.cpp` 331 (was 321), `RenderLights.cpp` 201 (was 161), `RenderScene::GetDrawnTransform` 428 (was 418); the others hold.

## Track walk E-final-8

WK3: the Medium nlerp exercise now says where `glm` is (`StrataScriptCore/ThirdParty/glm` of the Strata folder) and
gives the compile lines of `basics/math-interpolation`, linked. `sketches/world-interpolation-nlerp.cpp` compiled with
`cl /std:c++20 /EHsc /I <package>\StrataScriptCore\ThirdParty\glm` (Visual Studio 2026) and printed the page's output
(`docs-work/walkfix-E-final-8/nlerp/`, 2026-11-24); the walker's g++ build printed the same.
