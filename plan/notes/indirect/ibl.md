# Notes: indirect/ibl

## Since

- Image light from HDR maps and the procedural sky: 0.3.0 (`git grep ProceduralSky v0.3.0` finds `Strata/shaders/IBL/ProceduralSky.comp`).
- The atmosphere's cube: 0.6.0 (`AtmospherePass.glsl` first at `v0.6.0`).
- `EnvironmentResolution` and 512 texel prefiltering: 0.7.0 (`RendererQuality.cpp` at `v0.7.0` holds the row, at `v0.6.0` it does not).
- The horizon fade: 0.7.0 (settled in the brief).

## New terms

None. The page defines in bold only the eight terms the glossary homes on it: image-based lighting, equirectangular, cube map, cube array, split-sum approximation, prefiltered environment, filtered importance sampling, horizon fade.

## Requests

- Figure `sky-source-spheres` (and `sky-source-spheres-indirect`, `mirror-roughness-sweep`) need the Basic 3D template (and, for the mirror ball, the Showcase sample) to hold a sky light entity named `Sky`; the recipes set `SkyLight.Source` through `component.set` and, for the "no sky light" variant, call `entity.delete` on `Sky`.
- No editor layout and no new host.

## Not verified

- That the Basic 3D template names its sky light entity `Sky` (the recipes rely on it; `light/sky`'s recipes name it for the Showcase sample).
- The material property names `Metallic` and `Roughness` in the `material.create` recipes (taken from the shader's `SurfaceData`).
- The `entity.delete` call that removes the sky light in the figure's "ambient" variant.
- That the hardware filters across cube seams (stated in general terms in the problem section).
- The alternatives table's "who uses it" column is general knowledge, not read at the pin.

## Findings not applied

- The brief's Medium exercise (a patch against the pin that drops the comparison in `UpdateEnvironment` and a prediction of the failing check) is replaced by a sketch exercise, `sketches/indirect-ibl-budget.cpp`, because the tutorial patch tooling was not used on this page. The Basic exercise (trace it yourself) is as the brief says.
- `appendix/not-in-strata` is linked for the missing cube-map texture asset; its page did not exist in this worktree when the page was written.
- The brief's open finding `render-direct:824` (the horizon fade shipped in 0.7.0) is applied in the `:::history` block.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

The page's recipes changed project: neither the Basic 3D template nor the Showcase's `Outpost` holds an environment map
(both skies are `Atmosphere` with no map), and a figure setup cannot import an engine file. All three recipes now open
the ThirdPerson sample (its start scene `MainMenu` names `Sun` and `Sky` once each), replace the scene with
`scene.new {template: basic3d, force: true}`, and set the sun and the sky to ThirdPerson's own balance (sun 4.433 lux,
sky `Intensity` 1, the map `Environment/kloofendal_48d_partly_cloudy_puresky_1k.hdr`, handle `A76F8BB1E806ACFF`,
imported with `RemoveSun`, and `Course`'s procedural colours). Under Basic 3D's 120,000 lux sun a map or procedural sky
at `Intensity` 1 would not show at all. Every variant creates its own materials (`material.create` refuses a path a
previous variant of the same project copy made), the "no sky light" variant uses `component.remove SkyLight`
(`entity.delete` takes IDs, not `entityName`), and `material.set` takes `material`, not `path`.

- `sky-source-spheres` (published, round 2): map, procedural, atmosphere, none. The map's clouds show sharply on the
  smooth metal; the procedural sky gives a pale gradient, the atmosphere a deep blue over a brown ground. With no sky
  light the background is black and the metals are black but for the sun, which a constant ambient cannot reflect. The
  caption and alt now say this (the old caption's "the constant ambient lights only the white sphere" did not fit: the
  sun still lights all three).
- `sky-source-spheres-indirect` (published, round 2): the Indirect view under the procedural sky. The white sphere is an
  even pale blue rather than "lit from above"; caption and alt rewritten to what shows.
- `mirror-roughness-sweep` (waits, three rounds): round 1, with the sun, was deterministic but from roughness 0.4 on the
  sun's highlight and terminator dominate the ball, so it showed the sun's lobe, not the sky's prefiltered levels. Rounds
  2 and 3 remove the sun (`component.remove DirectionalLight`), and the picture is right: the clouds sharp at 0, blurred
  at 0.2, gone at 0.4, then ever smoother blue-gray gradients to 1.0. But the variants r04, r06, r08 and r1 were
  nondeterministic twice: 28 to 50 channel values off by 1 between the two captures, scattered over the frame (r0 and
  r02 pass). The captures are in `docs-work/photo/indirect-ibl/nondeterministic/indirect.ibl.mirror-roughness-sweep.*/`.
  The recipe left in the manifest is the sunless one. Nearest honest picture: the same recipe once the take allows
  off-by-one differences, or a fourth round trying manual exposure (the sky-only scene probably leaves auto exposure
  dithering by one step); the caption as written fits the sunless picture.

Retake at v0.8.0 (pin 319075e3, one hold, one round): `sky-source-spheres` (four variants) and
`sky-source-spheres-indirect` came out pixel-identical to their published files (`figures.py compare`: 5 of 5 equal),
so publish left them as they were, stamped at 822a7a46. `mirror-roughness-sweep` is published (round 1 at the new pin,
the sunless recipe unchanged): the take passed its pair check now, and the picture shows what the caption says: the
clouds sharp at 0, blurred at 0.2, a bright patch over a dark lower half at 0.4, then ever smoother blue-gray gradients
to 1.0.
