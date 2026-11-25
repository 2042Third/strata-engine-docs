# Brief: `indirect/gi-cascades`

| Field | Value |
| --- | --- |
| Title | Global illumination II: radiance cascades and the irradiance field |
| Kind | I |
| Size | XL |
| Tracks | E |
| Needs | `indirect/gi-voxels`, `indirect/ao`, `light/measuring-light`, `basics/math-sphere`, `light/atmosphere` |
| From | render-indirect ch. 10; 1.8 (injection, the cascades, merge, field reduce, the forward gather, multi-bounce and settling, what is experimental); + the GI debug views and their statistics · W8 |
| Unit | `plan/allocation/indirect.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `indirect/gi-cascades` — Global illumination II: radiance cascades and the irradiance field

**Covers.** The job: from the voxels to light on surfaces, every frame and without history. The page holds light
injection, the level downsample, probe validity and relocation, probe weights, the cascade marches and their merge, the
field reduce, multi-bounce by re-injection, the forward gather and the join, and GI's debug views and statistics. The
problem section is one paragraph that links `indirect/problem`; then three ideas are taught from zero. Radiance
cascades: the penumbra condition (near a probe, light needs few directions and many places; far away, the opposite),
cascades with four times the directions and four times the interval length, a child's unabsorbed ray continued in its
parents' merged rays, only the top cascade reading the sky, and the lead-in and overlap rules against leaks and doubled
light at interval borders. Probe fields and visibility: trilinear interpolation, dead probes, relocation, DDGI's
Chebyshev test on depth moments and why Strata weights by a voxel-transmittance guard instead (fence crawl), normal and
view bias, and the error of renormalizing a weight that vanishes. Multi-bounce by re-injection: last frame's field read at
each voxel, a geometric series of albedo, settle frames, still frames identical bit for bit; "uses last frame" is not
temporal accumulation; only High bounces on, and Low bounces once, because Low's coarser field with every bounce makes
the Cornell box's ceiling about 1.8 times as bright as High's. The guarantee these rules buy is taught as its own case:
a sealed room stays dark (the sun lights no voxel inside it, and of two rooms that share a wall the sealed one stays
dark, whether the light's source is on screen or not), the case from which a reader learns why the lead-in, the overlap
and the guard exist.

The map lists the passes in order (`VoxelInject`, `VoxelDownsample`, `ProbeValidity`, `ProbeWeights`, `CascadeMarch`
from the top cascade down to 1, `FieldReduce`) and then the forward pass's `SampleIrradianceField`, with three diagrams
(the cascades, the field gather, re-injection over frames). The contract: captures and the project picture wait for GI
to settle, within bounds; GI's constants live in their own buffer at b3, not in `FrameConstants`, for a reason the
engine's documents leave unexplained (added fields made recompiled GTAO and SSR repeat differently), and the page says
so; while GI is pending a surface keeps today's light; a frame without GI keeps the old expression bit for bit (the
decision's home for GI is `indirect/gi-limits`). A toy version is exercise E11: radiance cascades in 1D, two cascades and
the merge rule against brute force.

The real code: injection (every voxel of every level every frame: albedo times the sun's irradiance times a shadow walk
through the voxels, plus emission, plus last frame's field); the downsample; validity, the move off surfaces and the
relocation of cascade-0 probes (four rings of 26 directions); the weights (eight parents' trilinear weights times
validity times transmittance); the march in `GIMarch.slang` (front to back with transmittance, runs, the lead-in, the
depth moments) and the merge in `CascadeMarch.comp`; the field reduce (cascade 0's 64 directions continued by cascade 1,
summed into an ambient cube of six RGBA16F faces per probe, with depth moments in a 10x10 octahedral tile); multi-bounce
(`BounceGain`, albedo clamped to 0.9, `GetSettleFrames`: exercise E12 derives 12 and 17 frames for albedos 0.58 and
0.73); the forward gather (eight cascade-0 probes around the normal-biased point, trilinear times validity times facing
times the voxel guard, the minimum-visible normalization, the fade at the field's edge, `PushOutOfSolid`); the level
sampling; the join (`ReflectionParams.y` and `.z`: today's diffuse times 1 - w plus the field times w, specular
untouched, `x * 1 + 0` where w is 0). Then the debug views `voxels`, `gi`, `open` and `probes` (a GI view runs GI even
where the scene does not ask or the row is Off, and at Off shows High's layout) and the statistics and readbacks, read
as `light/measuring-light` teaches. Alternatives: DDGI's Chebyshev weighting, an octahedral-tile field and an SH field
(both tried and not landed), voxel cone tracing, screen-space GI (refused by the decision). Tests: the
`GPU.SceneRenderer.GlobalIllumination` suites (`Join`, `Bounce`, `Stitching`, `Room`) and the CPU references, and a
trace of `GlobalIlluminationIntensity` from the Post Process to the join. Figures: GI off and on in the Cornell box in a
slider with the path-traced reference, the four GI views on the Cornell box and the sun room, the sealed room's `gi`
view beside the open sun room's, the sun room at `GlobalIlluminationIntensity` 0, 1 and 2, and one bounce against every
bounce as a diagram. The reader can follow one frame of GI from the voxels to a pixel.

**Leaves out.**

- The voxels, the clipmap, the layout and the voxelizer → `indirect/gi-voxels`
- What GI does not do, and the bit-for-bit decision for GI → `indirect/gi-limits`
- Transmittance and front-to-back marching through a medium, in general → `light/atmosphere`
- The other debug views and how statistics are read → `light/measuring-light`
- Waiting for GI in captures from a client → `editor/camera-viewport`
- Trying GI in a game → `make/gi`

**Fit.** `fits`: about 7,550 words against XL (8,000). Three ideas from zero, eleven stages, five excerpts, the sealed
room and eight figures, four of them diagrams, take the most words. Phase B must look again at: the stages that changed
after the pin (the GI batches still landing, `render-indirect:698`), the bodies the survey did not read
(`ProbeValidity`, `ProbeWeights`, `FieldReduce`, `Include/GIProbes.slang`, `Include/GlobalIllumination.slang`:
`render-indirect:687`), the spec's "Review corrections" (`render-indirect:695`), the list of statistics and the
direction counts (`new:13`), whether Low still bounces once (`render-indirect:175`), the sealed-room tests (`new:27`)
and the GI views' exception (`render-indirect:180`).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-indirect:313` | concept | home | Radiance cascades: the penumbra condition, 4x directions and 4x intervals, the merge, only the top reading the sky; the error of leaks or doubling at interval borders |
| `render-indirect:318` | concept | home | Probe fields and their visibility: trilinear probes, dead probes, relocation, DDGI's Chebyshev test and Strata's voxel guard, normal and view bias; the error of renormalizing a vanishing weight |
| `render-indirect:322` | concept | home | Multi-bounce by re-injection and convergence: the geometric series, settle frames, determinism without temporal blending |
| `render-indirect:169` | feature | home | Light injection (`VoxelInject.comp`) |
| `render-indirect:170` | feature | home | The level downsample (`VoxelDownsample.comp`) |
| `render-indirect:171` | feature | home | Probe validity, move and relocation (`ProbeValidity.comp`) |
| `render-indirect:172` | feature | home | Probe weights (`ProbeWeights.comp`) |
| `render-indirect:173` | feature | home | The cascade march and the merge, top cascade down to 1 |
| `render-indirect:174` | feature | home | The field reduce: ambient cubes and depth moments per cascade-0 probe |
| `render-indirect:175` | feature | home | Multi-bounce by re-injection: `BounceGain`, the clamped albedo, `GetSettleFrames`, `SettleGlobalIllumination`; High bounces on and Low once (`GlobalIlluminationLayout::Bounces`), because Low's coarser field with every bounce makes the Cornell box's ceiling about 1.8 times as bright as High's (165 to 235 nits per albedo against 89 to 142); the test "High bounces on, Low once" (`Strata/src/Strata/Renderer/GlobalIlluminationLayout.h:97-100`, `GlobalIlluminationLayout.cpp:190`; `StrataTests/src/Renderer/GlobalIlluminationLayoutTests.cpp:525`; `Docs/DeveloperGuide.md:5128`, `:5269`) |
| `render-indirect:176` | feature | home | Sampling the field in the forward pass (`SampleIrradianceField`, `ReadAmbientCube`, `GetFieldWeight`, `PushOutOfSolid`) |
| `render-indirect:177` | feature | home | Level sampling: the finest level whose valid box holds the point, blended by the distance from the camera |
| `render-indirect:178` | feature | home | The join: `ReflectionParams.y` and `.z`, today's diffuse times 1 - w plus the field times w, specular untouched, 0.7.0's image when off |
| `render-indirect:179` | feature | home | The field's constants at b3 in their own buffer, not in `FrameConstants` |
| `render-indirect:180` | feature | home | The GI debug views `voxels`, `gi`, `open`, `probes` (`DrawVoxelView`, `DrawProbeView`); a GI view runs GI even where the scene does not ask or the row is Off, and at Off it shows High's layout, the one exception to "nothing is made when off" (`Strata/src/Strata/Renderer/SceneRenderer.cpp:3069-3074`; `Docs/DeveloperGuide.md:4966-4967`) |
| `render-indirect:181` | feature | home | The GI statistics and readbacks |
| `render-indirect:182` | feature | home | Capture waits: `viewport.capture` and the project picture wait for `GlobalIlluminationSettled` |
| `render-indirect:363` | code | home | `Strata/shaders/Include/GIMarch.slang:21-76`: the front-to-back march with transmittance, runs, the lead-in and the depth moments |
| `render-indirect:364` | code | home | `Strata/shaders/GI/CascadeMarch.comp.slang:25-100`: the merge into eight parents' directions; only the top reads the sky |
| `render-indirect:365` | code | home | `Strata/shaders/Include/GIField.slang:181-236`: the forward gather; with `ReadAmbientCube` at lines 41-51 |
| `render-indirect:366` | code | home | `Strata/src/Strata/Renderer/GlobalIlluminationLayout.cpp:405-412`: frames until a bounce adds less than 0.25% |
| `render-indirect:367` | code | home | `Strata/shaders/Include/IndirectLight.slang:109-118`: the field gather; with the join at `Strata/shaders/Scene/Forward.frag.slang:301-321`, `x * 1 + 0` where the field's weight is 0 |
| `render-indirect:411` | figure | home | Diagram: the radiance cascades (probe grids 0.5, 1, 2, 4 m; directions per probe as `new:13` gives them; intervals; lead-in and overlap; the merge to eight parents) |
| `render-indirect:413` | figure | home | Diagram: the field gather (the point, normal and view bias, eight probes, facing, the guard through the voxels, a dead probe) |
| `render-indirect:415` | figure | home | Diagram: re-injection over frames, the first k terms after k frames, the settle curve |
| `render-indirect:455` | figure | home | Off and on: GI in the Cornell box (`lookdev.cornell` with Post Process `GlobalIllumination`, quality High), in a slider with the path-traced reference (`new:2` of `indirect/problem`) |
| `render-indirect:456` | figure | home | The GI views: `lookdev.cornell.view.gi`, and the sun room's `lookdev.sunroom.view.gi`, `lookdev.sunroom.view.open`, `lookdev.sunroom.view.voxels` and `lookdev.sunroom.view.probes` (`Tools/LookDev/Shots.json:132-135`, `:149`); the Cornell box has a shot of its `gi` view only, so its other three views need a recipe |
| `render-indirect:458` | figure | home | Diagram: one bounce against every bounce, the light of each bounce adding up over frames; a diagram because tier 2 has no capture switch for `BounceGain` 0, which only the tests set (R34, D42: one request extends tier 2) |
| `new:27` | concept | home | A sealed room stays dark: the sun lights no voxel inside it, and of two rooms that share a wall the sealed one stays dark, whether the light's source is on screen or not; GI's main guarantee against leaks, the case from which a reader learns why the lead-in, the overlap and the guard exist. Evidence: `StrataTests/src/Renderer/GPUSceneGlobalIlluminationRoomTests.cpp:443` ("Paired rooms: the sealed one stays dark"), `:716` ("The sun lights no voxel inside a sealed room"), `:1169` ("A sealed room stays dark"), in the suite `GPU.SceneRenderer.GlobalIlluminationRoom`; `Docs/Manual/Lighting.md:325` |
| `new:28` | figure | home | The sealed room's `gi` view (`lookdev.sealedroom.view.gi`) beside the open sun room's (`lookdev.sunroom.view.gi`), from the same camera. Evidence: `Tools/LookDev/Shots.json:137`, `:132` |
| `new:29` | figure | home | Sweep of GI's main setting: the sun room at `GlobalIlluminationIntensity` 0, 1 and 2 (the shot `lookdev.sunroom.lit.gi`, whose Setup turns GI on, with the intensity set as well); at 0 the field still replaces today's diffuse light inside its reach, scaled to nothing. Evidence: `Tools/LookDev/Shots.json:141`; `Strata/src/Strata/Renderer/SceneRenderer.cpp:3325-3330` (the intensity clamped to 0 to 4 as `ReflectionParams.z`); `Strata/shaders/Scene/Forward.frag.slang:311-319` |
| `render-indirect:511` | rule | home | GI's constants live in their own buffer at b3; a new frame constant must check the `ao` view's repeats |
| `render-indirect:519` | rule | home | Captures and the project picture wait for GI to settle, within bounds: bounces arrive one frame each |
| `render-indirect:703` | open | home | The cause of the non-repeating GTAO and SSR after new frame constants is unexplained in the engine's own documents; the page states it as open, with the rule it led to |
| `render-indirect:556` | hands-on | home | E11: radiance cascades in 1D, two cascades and the merge rule against brute force (the toy version) |
| `render-indirect:557` | hands-on | home | E12: derive `GetSettleFrames` for albedos 0.58 and 0.73 (12 and 17) |
| `new:30` | hands-on | home | Exercise (trace it yourself, R32, D27): `GlobalIlluminationIntensity` followed from the Post Process to a pixel: the CPU sets `ReflectionParams.y` to 1 and `.z` to the clamped intensity only where the scene asked, the field ran and it is not pending, and the forward pass scales the field's irradiance by `.z` and weighs it by the field's weight; the solution names the lines and says what a pending frame draws. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:3320-3330`; `Strata/shaders/Scene/Forward.frag.slang:303-321` |
| `render-indirect:586` | term | home | Ambient cube |
| `render-indirect:633` | term | home | Light injection |
| `render-indirect:634` | term | home | Probe, cascade, interval and direction tile, four entries |
| `render-indirect:635` | term | home | Radiance cascades |
| `render-indirect:636` | term | home | Merge and miss rule, two entries |
| `render-indirect:637` | term | home | Lead-in and overlap, two entries |
| `render-indirect:638` | term | home | Occupancy, its own entry; transmittance is `render-direct:747`'s entry (participating media) |
| `render-indirect:639` | term | home | Dead probe, validity and relocation, three entries |
| `render-indirect:640` | term | home | Irradiance field |
| `render-indirect:641` | term | home | Depth moments and the Chebyshev test (DDGI), two entries |
| `render-indirect:642` | term | home | Guard (voxel guard) |
| `render-indirect:643` | term | home | Normal bias and view bias, two entries, qualified against the shadows' normal offset (`render-direct:719`) |
| `render-indirect:644` | term | home | Open share |
| `render-indirect:645` | term | home | Re-injection, multi-bounce and bounce gain, three entries; "multi-bounce" qualified against multi-bounce AO (`render-indirect:597`) |
| `render-indirect:646` | term | home | Settled and pending, two entries |
| `render-indirect:647` | term | home | Join |
| `new:13` | erratum | use | The direction counts of the cascades, stated as the code gives them |
| `render-indirect:520` | rule | use | No blocking: GI pending shows today's light; taught on `indirect/probes` |
| `render-indirect:510` | rule | link | A frame without GI keeps the old expression bit for bit; the decision for GI is taught on `indirect/gi-limits` |
| `new:2` | figure | use | The path-traced reference of `indirect/problem`, compared in the slider of `render-indirect:455` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The voxels, their levels, anchors and classes | `indirect/gi-voxels` | must |
| Transmittance and marching front to back through a medium | `light/atmosphere` | must |
| Solid angles, octahedral maps and integrating over directions | `basics/math-sphere` | must |
| Trilinear interpolation | `basics/math-interpolation` | must |
| Powers and logarithms (the settle frames) | `basics/numbers` | must |
| A geometric series and its sum | `basics/math-interpolation` | must |
| Ambient occlusion and the multi-bounce fit the field does without | `indirect/ao` | must |
| The debug views and how their statistics are read | `light/measuring-light` | must |
| Emission in nits | `light/materials` | must |
| Readbacks polled per frame | `gpu/readback-timing` | must |
| The seam's field gather and the forms | `indirect/seam` | must |
| Temporal accumulation, to tell it apart from re-injection | `image/taa` | helps |
| The sun's light and its direction in the frame constants | `light/lights` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `ambient-cube` | Ambient cube | - |
| `cascade-indirect` | cascade (indirect) | - |
| `dead-probe` | Dead probe | - |
| `direction-tile` | direction tile | - |
| `interval` | interval | - |
| `irradiance-field` | Irradiance field | - |
| `join` | Join | - |
| `lead-in` | Lead-in | - |
| `light-injection` | Light injection | - |
| `merge-indirect` | Merge (indirect) | - |
| `miss-rule` | miss rule | - |
| `normal-bias` | Normal bias | - |
| `occupancy` | occupancy | - |
| `open-share` | Open share | - |
| `overlap` | overlap | - |
| `pending` | pending | - |
| `probe` | Probe | - |
| `radiance-cascades` | Radiance cascades | - |
| `relocation` | relocation | - |
| `settled` | Settled | - |
| `transmittance-indirect` | Transmittance (indirect) | - |
| `validity` | validity | - |
| `view-bias-indirect` | view bias (indirect) | - |
| `voxel-guard` | voxel guard | - |
