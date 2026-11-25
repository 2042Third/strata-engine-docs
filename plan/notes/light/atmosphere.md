# Notes: light/atmosphere

## New terms

None proposed. The sixteen glossary terms homed here are defined in bold (the lookup table as "lookup table (LUT)").

## Requests

- Extra words: illuminance (also asked by light/units-exposure), midpoint, quadrature (the numerical rule the engine's code names).
- Names: Bruneton, Neyret, Hillaire, Preetham, Hosek, Wilkie (authors of the cited methods; Further reading and the alternatives table).
- Hosts for Further reading (cited without links): the host of the Bruneton and Neyret 2008 paper, the host of the Hillaire 2020 paper (EGSR), the host of Preetham 1999 and of Nishita 1993.
- Figures `time-of-day-sweep` (5 variants) and `aerial-perspective-scales` (3 variants), kind scene, OpenWorld sample: the camera is "scene"; the planner picks the framing (the mountains from the shore for the second). The entity name `Sky` for the sky light is assumed, as in the other figures.
- The sweep's `groundIlluminance` per variant is reported by `lighting.applySkyPreset`; a recorded `{stats.*}` value was not asked for (the caption has no number).

## Not verified

- Statements about other methods (Preetham 1999, Hosek and Wilkie 2012, Bruneton 2008 as four-dimensional tables, Nishita 1993, Hillaire 2020 targeting the viewer near the ground) come from memory of the papers.
- That `lighting.applySkyPreset` accepts `preset` "Clear" with `sunElevation` 60, 20, 6, 0 and -6 on the OpenWorld sample, and that the sample's entity is named `Sky`.
- The wording "the real sun's 120,000 lux": taken from the comment in `RendererComponents.h`.
- The 94 % and 67 % transmittance figures of the mountain example are hand arithmetic from the Rayleigh and haze coefficients without ozone.
- The test list in "How it is tested" is read from test names, not run.

## Findings not applied

- The brief lists no open findings.
- The brief's times-of-day sweep with the ground's illuminance printed: the caption carries no numbers (figure lint); the numbers are in the text for 6 degrees only.
- Skybox, `AtmosphereAerial.comp` and the sun's disk are described in prose and short quotes; `SceneRenderer::RenderAerialPerspective` is not quoted.

## Since

0.6.0: Docs/Releases/0.6.0.md line 59 introduces the Atmosphere source and the physical atmosphere.

## Clerk

- Admitted to names.txt: Bruneton, Neyret, Hillaire, Preetham, Hosek, Wilkie.
- Admitted to extra-words.txt: illuminance, midpoint, quadrature.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

- `time-of-day-sweep`: published (round 2). Round 1 (`camera: "scene"` replaced by a camera at (330, 14, 330) on the
  peak, fov 45, `sunAzimuth` -75 so the sun lies to the right outside the frame): the camera stood outside the water
  plane (a pale wedge at the bottom), and the first capture of the editor session drew no terrain (`culledProxies` 97 of
  97, a stale cull on the session's first capture). Round 2: camera at (270, 12, 270), and `aerial-perspective-scales`
  moved first in the manifest, so that its capture takes the empty first frame. Automatic exposure (the preset turns it
  on) keeps every picture equally bright, so the caption says the pictures show the light's color, not its fall; the
  reported ground illuminances (103,100, 82,538, 41,859, 1,770 and 0 lux) are in `shows`. At -6 degrees the peak is lit
  only by the glowing sky (soft red under a violet sky), not dark blue as the old alt said.
- `aerial-perspective-scales`: not published (blocked by the sample's size). Round 1: camera (330, 14, 330) toward the
  peak 420 m away, fov 30: off and scale 6 differ by under 1/255 on average (the peak's pixel 99 to 104 in blue), scale 1
  by less; round 2 (camera (270, 12, 270)): scale 1 and 6 again alike on the peak (115, 112, 108 against 114, 112, 111).
  The island is 768 m across and its water ends near 300 m from the center, so no view sees land beyond about 600 m;
  at scale 6 that is 3.6 km of air, a blue transmittance near 0.9, which the height fog and the tone mapper leave
  invisible. The page's words "at a scale of six they fade toward the sky" need about 1.3 km of real distance at scale
  6. Nearest honest picture: the same camera with scales 1, 6 and 64 (the slider's top; at 400 m that is about 26 km of
  air), which would need the page's variant `scale-6` to become `scale-64` and its sentence to say so, or a sample with
  land several kilometers away.
- `time-of-day-sweep`, words (2026-11-18, after a viewer's report that no picture names its elevation and all five
  share one alt): the pictures stand (60: blue sky, gray rock and green grass lit white; 20: beige rock; 6: golden peak;
  0: orange-red peak under a mauve sky; -6: soft red peak under a violet sky), so nothing was retaken. The site's figure
  plugin draws only the recipe's caption and alt (`src/plugins/figures.mjs`, `caption()` and `imageHast()` read
  `entry.caption` and `entry.alt`, never a variant's), so the manifest cannot give each picture its own words. The
  shared caption now names the elevations and the reported illuminances in the pictures' order, and the shared alt
  describes each elevation in turn. Still needed, in the page's words: write each of lines 231-239 as a container
  `:::figure{id=time-of-day-sweep variant=…}` whose body names its picture ("Sun at 20°: about 82,500 lux at the
  ground."; 60°: 103,100; 6°: 41,900; 0°: 1,770; -6°: 0). A single alt per picture needs the plugin to read a variant's
  `alt` (tools/figures.py already merges variant fields over the recipe's).
- The take's first capture of an editor session culls every terrain tile on the OpenWorld sample; keep a figure in front
  of `time-of-day-sweep` in this manifest and take the page whole: a retake of the sweep alone hits that empty capture
  (check `culledProxies` in its results).
- Pin v0.8.0 (319075e3), 2026-11-23. `time-of-day-sweep`: taken again, `figures.py compare` against the published
  files: 0 of 5 differ; republished unchanged (stamps at the new pin).
- `aerial-perspective-scales`: published (round 2). Round 1 (camera (270, 12, 270) toward (-69, 35, 58), fov 40, the
  height fog's `Density` 0 for all variants): the island fills the view but the land lies within 400 to 700 m; scale 6
  moves the peak only from 70/66/62 to 71/69/71, scale 1 not at all; and the `off`
  variant's two captures differed (the session's empty first capture). Round 2: the sea is large, so the camera stands
  out on it at (900, 20, 900), 1.3 km from the island's center, toward (0, 70, 0), fov 16 (the editor camera's far plane
  is 2,000 m); a warm-up `viewport.capture` with the same camera opens the `off` variant's setup and takes the
  session's empty first frame. Off and scale 1 match (the rock 92/85/77 and 93/86/80); at scale 6 the rock turns
  94/92/94 and the grass 79/93/61 to 82/99/86: a cool gray and a bluer green, visible side by side, though nowhere
  near the sky's color (80/114/142). Caption and alt now say that, and that the height fog is off (it hid the haze
  at this sample's distances). The page's words stand: the example's "a small world shows no haze" at scale 1 and
  "the air's blue replaces it" at scale 6 are what the pictures show.
