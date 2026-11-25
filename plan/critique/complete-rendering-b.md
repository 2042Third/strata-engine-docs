# Critique `complete-rendering-b`: completeness of parts 8 and 9 against `render-direct` and `render-indirect`

Lens: completeness of the plan against `plan/inventory/render-direct.md` (842 lines) and `plan/inventory/render-indirect.md`
(710 lines), both read in full, and parts 8 to 10 judged as a rendering textbook. All nine plan files were read in full.
Engine facts were checked in `G:/GameEngineAI` at `main` (822a7a46) and, for wave 8 work not yet merged, in the branches
`agent/wave8-area-lights`, `agent/wave8-local-lights` and `agent/wave8-rc-world` with `git log`/`git diff`/`git show`
only (no worktree touched, nothing built or run).

Line numbers: `book.md`, `outline-*.md`, `process.md`, `pipelines.md` as the files stand. Inventory references are
"RD" (`render-direct.md`) and "RI" (`render-indirect.md`) with their section or item numbers.

Summary of the verdict: parts 8 and 9 cover every *feature* of both inventories somewhere, but the allocation of the
*theory* is broken in four places that a reader on track E hits at once: the BRDF table and energy compensation are
homed in part 9 while part 8's core shader uses them; there is no concept page for reflectance (radiometry, the
reflection equation, microfacets) and the rendering equation first appears after the BRDF; exposure, pre-exposure and
HDR have four claimants; and the signals/noise primer that shadows, AO, TAA, dither and textures all stand on does not
exist. The W8 marks are partly wrong: `light/lights` waits for nothing, while `image/quality-settings`,
`indirect/measuring-light` and parts of three other pages do change in wave 8, and `light/area-lights` rests on a feature
the wave 8 plan does not schedule.

---

## Findings (most severe first)

### F1 (major) The BRDF table and energy compensation are homed in part 9, but part 8's direct shading uses them

- **Where:** `book.md:68` ("BRDF table, split sum | `indirect/ibl`"), `book.md:70` ("Energy conservation, white furnace |
  `indirect/energy`"), `outline-3.md:14` (`light/brdf`), `outline-3.md:34` (`indirect/energy`), `outline-3.md:8` (part 8
  prerequisites).
- **Problem:** The forward shader computes the BRDF table lookup and `SpecularEnergy` at the head of `ShadeLitSurface`
  for *direct* light: `Strata/shaders/Scene/Forward.frag.slang:211-218` ("The split sum's BRDF table at the surface: its
  specular reflectance of image light and the compensation of its lobe for multiple scattering, which direct light takes
  too"), and the coat does the same (220-226). RD 1.2 "Multiple-scattering energy compensation ... applied to direct and
  image light, coat and glass"; RD 2 concept 8 says the table is "needed here because the BRDF table also drives energy
  compensation"; RD 1.14 lists `GPUSceneLightingTests.cpp:958` "direct specular compensated". With the plan's homes, the
  page that walks the direct BRDF (`light/brdf`, part 8) must quote code whose two inputs are explained only in part 9,
  whose prerequisites in turn include `light/brdf` (`outline-3.md:28`). A reader of part 8 meets `dfg` and
  `SpecularEnergy` unexplained in the most important function of the renderer.
- **Proposal:** Move `indirect/energy` into part 8 as `light/energy` ("Keeping the energy: directional albedo, the BRDF
  table and the white furnace", I, M), placed right after `light/brdf`. Its allocation: RD concept 9, RI concept 7, RD
  code #8 and #9 (`BRDFLut.comp.slang:20-49` derived as the table of directional albedo E by importance sampling), RI code
  #1, #5, #6, the white furnace (tests `GPUSceneLightingTests.cpp:860-1010` and shot `lookdev.furnace`), the "diffuse gets
  what specular leaves" rule (RI rule 2), RD figure 4, RI figure 6, exercises RI E1 and RD "Disable energy compensation".
  `indirect/ibl` keeps the split sum and *reuses* the table as its second factor. Change `book.md:68` into two rows:
  "BRDF table (directional albedo, its derivation) | `light/energy` | indirect" and "Split sum (prefiltered radiance times
  the table) | `indirect/ibl` | light"; change `book.md:70` to `light/energy`. Add `basics/math-light` to part 8's
  prerequisites (`outline-3.md:8`): the table's derivation is Monte Carlo importance sampling (RD code #9 "Reader must
  know first: Monte Carlo basics"). The freed slot in part 9 goes to F12's `indirect/seam`.

### F2 (major) `light/lights` is marked W8 but nothing in wave 8 changes it, and the mark breaks the writing order

- **Where:** `outline-3.md:15` (`light/lights` "· W8"), `process.md:79` (phase A writes the pages of `light` not marked W8),
  `process.md:73-74` ("an order where prerequisites are written before the pages that need them").
- **Problem:** The streams that move lights in wave 8 do not touch this page's subject. `git diff --stat
  main...agent/wave8-local-lights` changes `SceneRendererLocalShadows.cpp`, `ShadowAtlasAllocator.*`,
  `LocalShadows.slang`, five lines of the cluster loop in `Forward.frag.slang` and the quality rows, and no file of the
  light components (`RendererComponents.h`) or the light records (`RenderLights.*`). `agent/wave8-area-lights` adds only
  `AreaLights.{h,cpp}`, `LTCTable.inl`, a tool and tests (8 files), no change to points, spots or the sun.
  `physics-timing` (drawn transforms of lights, RD 1.3) is already on main. Meanwhile `light/shadow-basics`,
  `light/sun-shadows-1/2`, `light/sky` and `light/fog` (not W8, written in phase A) all need the sun's component and light
  space from `light/lights`: phase A would write them before their prerequisite exists.
- **Proposal:** Remove "· W8" from `outline-3.md:15`. `light/lights` covers RD 1.3 (components, falloff, cone, one sun,
  records, `LightData`, spot bounds, drawn transforms, preview lighting) and links to `light/area-lights` for lights with
  size. Keep W8 on `light/local-shadows`; make `light/many-lights` "phase A, with its light-loop section revised at 0.8.0"
  (the only wave 8 change there is local-lights' skip of lights behind the surface, `Forward.frag.slang` 265-283 on the
  branch, and area lights' entry into clusters, which no branch has yet).

### F3 (major) `light/area-lights` describes a feature the wave 8 plan does not schedule

- **Where:** `outline-3.md:16` ("Area lights | I | L | new · W8 (wave 8, stages 1 to 3)"), `README.md` decision 5,
  `process.md:86`.
- **Problem:** `Docs/Plans/Wave8/plan.md` section 4 lists nine streams (showcase, reflections, physics-timing,
  radiance-cascades, animation-graph, local-lights, editor-ux, volumetric, showcase-engine); none is area lights, and no
  spec under `Docs/Plans/Wave8/specs/` describes them, so "stages 1 to 3" has no source in the engine. The branch
  `agent/wave8-area-lights` (11 commits, last 2026-11-09) holds the LTC tables and CPU shading math with tests
  (`AreaLights.h`: `AreaLightUnits { Nits, Lumens }`, rect lights, two-sided faces, the coat's lobe), and no component,
  shader, light record, cluster or shadow integration. RD 1.13 and RD 9 confirm main has none. If 0.8.0 ships without rect
  lights, phase B would write an L internals page about code that does not exist, against `style.md:16` ("Never promise
  what the engine does not do"). Meanwhile what main *does* have for sized lights, lobe widening by `SourceRadius` and the
  sun's Angular Diameter (RD 1.2 "Highlights of sized sources", RD concept 12, code #11, RD rule 12, RI rule 5), has no
  clear home (see F4).
- **Proposal:** Retitle the row to "`light/area-lights` | Lights with size: sized highlights and area lights | I | L |
  render-direct concept 12, 1.13; W8 section: rect lights". Make it the home of lobe widening (`GetSourceLobeAlpha2`,
  `GetLobeAlpha`, `RenderData::GetSunLobeAlpha2`, `PBR.slang:12-31, 119-124`), written in phase A; its rect-light section
  (LTC, Heitz 2016; units in nits or lumens; coat) waits for 0.8.0. State the fallback in the row: if 0.8.0 has no rect
  lights, the section becomes "how engines shade area lights" with a diagram and a link to `appendix/not-in-strata`, and
  the page shrinks to M. Move the row after `light/many-lights` (rect lights would be culled and clustered like the
  others) and replace "stages 1 to 3" with the branch name as the source.

### F4 (major) Specular AA, the derivative rule, sized highlights, F0 from IOR and the horizon fade have two or three homes

- **Where:** `outline-3.md:14` (`light/brdf`, from RD ch. 3: "GGX, Smith, Schlick, Lambert, the BRDF table, energy
  compensation, specular AA, sized-source lobes, the horizon fade"), `outline-3.md:34` (`indirect/energy`, titled
  "...and specular anti-aliasing", from RI ch. 3: "energy compensation, F0 from IOR, sized highlights, horizon fade"),
  `outline-3.md:13` (`light/materials`: IOR field), `book.md:56-83` (none of these concepts is in the table).
- **Problem:** Both inventories propose a chapter that owns these five items (RD 8 ch. 3; RI 8 ch. 3) and the plan keeps
  both pages. Writers allocated from the "From" column will both teach `WidenRoughness`, `GetHorizonFade`,
  `GetDielectricF0` and `GetSourceLobeAlpha2`.
- **Proposal:** Add to the one-home table: "Specular anti-aliasing, the derivative rule | `light/brdf` | indirect,
  `draw/gpu-driven`"; "Fresnel, F0 from IOR | `light/reflectance` (the physics; F1/F5), the IOR field in `light/materials`
  | indirect"; "Sized sources (lobe widening) | `light/area-lights` (retitled, F3) | `light/lights`, `indirect/probes`
  (bakes draw no highlights)"; "Horizon fade | `indirect/ibl` (it fades image light only: `PBR.slang:98`, RD 1.2) |
  `light/brdf`". Drop "and specular anti-aliasing" from the energy page's title.

### F5 (major) No concept page teaches reflectance; the rendering equation comes after the BRDF

- **Where:** `outline-3.md:12-14` (part 8 opens with units (C), materials (C), then `light/brdf` (I) "The BRDF in code"),
  `outline-3.md:32` (`indirect/problem`: "the rendering equation").
- **Problem:** The BRDF is defined from radiance and irradiance and lives inside the reflection equation (RD concept 6
  "The rendering equation for a single light, and the BRDF"; RI concept 2 "Radiance, irradiance, solid angle, cosine
  weighting"). The plan gives this theory to an *internals* page, whose shape (`book.md:43`, `style.md:60-63`: job, map,
  contract, toy, code walk, tests, changing it) has no place for a derivation: Lambert's 1/pi, the normalization of D, the
  Jacobian 1/(4 V.H) of the half vector, Smith masking-shadowing and height correlation, Schlick's approximation, metal vs
  dielectric. The rendering equation is introduced in `indirect/problem`, after the reader has read the BRDF. Every
  textbook the plan surveyed puts this first (curricula 1.9.3: "radiometry (flux, irradiance, radiance), photometry ...,
  the rendering equation, BRDFs. RTR ch. 8-9, [S3] ch. 4"; "From Lambert and Phong to physically based shading:
  microfacets, GGX, Fresnel and F0 from IOR, Smith visibility").
- **Proposal:** Add before `light/brdf`: "`light/reflectance` | How surfaces reflect light: the reflection equation and
  microfacets | C | L | new; render-direct concepts 6-7; render-indirect concepts 2-3". It is the home of radiance and
  irradiance in use (the quantities themselves are named in `light/units-exposure`), the reflection equation for one light,
  the BRDF's definition and properties, Lambert, microfacet theory (D, G/V, F) with each term derived, Fresnel and F0
  from IOR. Retitle `light/brdf` "The forward shader and the BRDF in code" (F11). `indirect/problem` then extends the
  reflection equation to the recursive rendering equation. One-home row: "Radiometry in use, the reflection equation,
  microfacet theory | `light/reflectance` | indirect/problem (the full equation)".

### F6 (major) Units, exposure, pre-exposure and HDR are claimed by four or five pages

- **Where:** `outline-1.md:77` (`basics/color`: "linear, sRGB, HDR"), `outline-3.md:12` (`light/units-exposure`: "units,
  HDR and exposure", L), `outline-3.md:49-51` (`image/why-post`, `image/exposure`, `image/pre-exposure`), `book.md:56-83`
  (no row).
- **Problem:** RD concepts 1-3 (units; linear color, HDR targets and half-float range with `SanitizeHDR`; exposure, EV100
  and pre-exposure, code #36 `ChoosePreExposure`) duplicate render-image concepts 2-4 (`render-image.md:318-327`: half
  floats and `SanitizeHDR`, photometric units and the camera exposure model with the EV100 table, pre-exposure; code #3
  and #4 the same lines `Common.slang:49-57` and `SceneRenderer.cpp:1531-1598`). RD says this area owns "the units and the
  pre-exposure ... and must hand over cleanly to 'Exposure' there" (RD boundaries), render-image proposes a whole
  pre-exposure chapter. With no row in the table, three writers will each explain EV100 and the power-of-two scale.
- **Proposal:** Add rows: "Photometric units, conversions, reference values | `light/units-exposure` | image";
  "Camera exposure, EV100, metering, the key | `image/exposure` | light"; "Pre-exposure (why: one paragraph in
  `light/units-exposure`; the mechanism: readbacks, epochs, settling, TAA rescale) | `image/pre-exposure` | light,
  indirect/probes, indirect/ssr"; "Half-float range and subnormals | `basics/color` | light, image"; "`SanitizeHDR` |
  `light/brdf` (the forward shader is the first HDR writer) | image/why-post, image/lens-effects". Retitle
  `light/units-exposure` "Light by the numbers: radiometric and photometric units" (it keeps L with radiometry, the
  lumen/candela/lux/nit conversions, the spot rule, the sun-to-sky ratio and the reference table).

### F7 (major) The signals and noise primer is missing, although parts 5, 8, 9, 10 and 13 stand on it

- **Where:** `outline-1.md:69-80` (part 2), `outline-3.md:20` (`light/sun-shadows-2`), `outline-3.md:35`
  (`indirect/ao`), `outline-3.md:54-57` (`image/encoding`, `image/spatial-aa`, `image/taa`).
- **Problem:** The plan's own curricula study flags this as a gap: "Signals: sampling, aliasing, Nyquist, reconstruction
  filters, convolution, mip filtering. [gap] This is the shared theory under texture filtering, anti-aliasing, TAA,
  shadow filtering and audio. Usually it is taught five times, badly, or not at all" and "Randomness: ... blue noise. [S]
  (`BlueNoise.h` ...)" (`research/curricula.md`, 1.2). In the outline it would be taught five times: specular aliasing (RD
  concept 10), PCF/PCSS with a Vogel disk turned by a fixed 64x64 blue-noise tile and Poisson taps rotated by interleaved
  gradient noise (RD 1.6, 1.7, concept 16, figure 12), the 4x4 ordered-dither pattern weighed by a tent kernel (RI concepts
  10, RI figure 8), TPDF dither and blue noise as its contrast (`render-image.md:140-145, 282-284`), Vogel gathers in depth
  of field (`render-image.md:182`), and "sampling theory light" in `image/spatial-aa` (render-image ch. 8), which comes
  last. `basics/math-light` (`outline-1.md:78`) covers integrals, Monte Carlo, SH and octahedral maps, not sampling theory
  or noise.
- **Proposal:** Add "`basics/signals` | Sampling, aliasing, filtering and noise | C | L | new; curricula 1.2 'Signals' and
  'Randomness'; needed by textures, specular AA, shadow filters, AO, TAA, dither, audio", after `basics/math-light`. It
  is the home of sampling and aliasing, convolution and reconstruction kernels (box, tent, Gaussian, Catmull-Rom), mip
  filtering as prefiltering, white vs blue noise, low-discrepancy sets (Hammersley, Vogel/golden angle, Poisson disk),
  interleaved gradient noise and ordered dither, and denoising by spatial filters. Add one-home row "Sampling patterns
  and noise (blue noise, Vogel, Poisson, IGN, ordered dither) | `basics/signals` | light, indirect, image, audio". Add it
  to the prerequisites of parts 8, 9 and 10 and of `assets/textures` and `audio/sound-in-a-computer`.

### F8 (major) Part prerequisites miss what the inventories require, and the part order forces forward references

- **Where:** `outline-3.md:8` (part 8: `gpu/frame-tour`, `basics/color`, `basics/math-vectors`), `outline-3.md:28`
  (part 9: `light` up to `light/brdf`, `basics/math-light`), `outline-3.md:45` (part 10), `book.md:113-115` (part order).
- **Problem:**
  - Part 8: light records are "kept from EnTT signals and transform changes, with a change log for the GPU mirror"
    (RD 1.3), the GPU light path culls the mirror's records (RD 1.4, figure 6), the CPU path frustum-culls by bounding
    sphere (code #15): `draw/render-scene`, `draw/render-scene-gpu`, `draw/bounds-culling`. RD ch. 5's prerequisites name
    "compute shaders, GPU-driven path basics" and the caster search and local shadow views run in `Cull.comp`'s shadow
    phases (RD 9 "the GPU-driven shadow culling"; AGENTS.md "change both" for the CPU path and `Cull.comp`):
    `draw/gpu-driven`. The material pages need `gpu/binding` (texture table, `render-core.md:100-102`) and
    `assets/textures` (sRGB vs data, BC5; RD concept 5). The BRDF table needs `basics/math-light` (F1).
  - Part 9: `indirect/ibl` filters the three sky sources (RI 1.1) that are explained in `light/sky`, but part 9 lists
    only "up to `light/brdf`". The bake chooses a power-of-two pre-exposure and SSR divides by it (RI 1.6 "Probe bake";
    RD rule 4), whose home is in part 10 (F6). Checkerboard SSR "reads the TAA history along the hit's motion" (RI 1.7;
    RI ch. 7 prerequisites "motion vectors and TAA (other area)"), and `image/taa` is in part 10. The GI voxelizes
    "static-arena indexed submeshes" of the geometry pool (RI 1.8; RI ch. 9 prerequisites "geometry pool and render scene
    (other area); compute atomics"): `gpu/geometry-pool`, `draw/render-scene`.
  - Cycles: `draw/motion-vectors` lists "TAA concept (post area)" (render-scene ch. 13) and `image/taa` lists "motion
    vectors" (render-image ch. 9); `draw/occlusion` lists "shadow cascades (shadows area)" (render-scene ch. 10) while the
    sun-shadow pages need the GPU-driven path. The strips plugin fails on cycles (`site.md:72`, plugin "strips").
- **Proposal:** Part 8 prerequisites: `gpu/frame-tour`, `gpu/binding`, `basics/color`, `basics/math-vectors`,
  `basics/math-light`, `basics/signals`, `assets/textures`, part `draw` up to `draw/render-scene-gpu`; shadow pages add
  `draw/gpu-driven`. Swap parts 9 and 10 in `book.md:113-115` (light, then image, then indirect): part 10 needs only
  `gpu/frame-tour` and `light/units-exposure` (`outline-3.md:45`), and part 9 then has `image/pre-exposure` and
  `image/taa` before it; `image/quality-settings` links forward to the AO, reflection and GI rows as "see" links, not
  prerequisites. Part 9 prerequisites: `light/brdf`, `light/energy`, `light/sky`, `image/pre-exposure`,
  `basics/math-light`; `indirect/ssr` adds `draw/motion-vectors` and `image/taa`; `indirect/gi-voxels` adds
  `gpu/geometry-pool` and `draw/render-scene`. Break the cycles in the allocation: `draw/motion-vectors` says what motion
  vectors are for in one sentence without TAA as a prerequisite; the cascades' occlusion and cascade cache are allocated
  to `light/sun-shadows-1`, and `draw/occlusion` links forward to it.

### F9 (major) The forward shader as a whole has no home; "forward vs deferred" has two

- **Where:** `outline-3.md:14` (`light/brdf`), `outline-3.md:17` (`light/many-lights`), `outline-2.md:58`
  (`gpu/frame-tour`), `book.md:56-83`.
- **Problem:** `Forward.frag.slang` is the shader every lit pixel runs, and both inventories quote its structure: RD 1.2
  "Forward shader variants" (one source, six variants, `Strata/CMakeLists.txt:174-178`), "Opaque forward with EQUAL depth
  test", "Derivative rule" (sample everything before any discard), RD code #18 and #19 (`ShadeLitSurface`, the main), RD
  figure 20 "Shading order within one pixel" (material sample to `SanitizeHDR`), RI code #9 and #10. No page is the home
  of this anatomy: `light/brdf` is "the BRDF in code" (`PBR.slang`), `gpu/frame-tour` lists passes. Separately,
  "forward, forward+, deferred, visibility buffer" is a concept of both render-core (concept 26, `render-core.md:409-412`,
  for `gpu/frame-tour`) and RD concept 13 (for `light/many-lights`).
- **Proposal:** Retitle `light/brdf` "The forward shader and the BRDF in code" and allocate to it: RD 1.2 (variants,
  EQUAL test, `[earlydepthstencil]`, the derivative rule, minimum roughness, `SanitizeHDR`), RD code #6, #7, #10, #19, RD
  figure 20, RD rules 6, 10, 29. Add one-home rows: "Forward vs deferred, the prepass and the EQUAL test | `gpu/frame-tour`
  | light/many-lights" and "The forward shader's anatomy and shading order | `light/brdf` | indirect, image";
  `light/many-lights` keeps only tiled vs clustered and Strata's culling (RD concept 13 minus its first sentence). RD 9
  notes the engine's documents do not say why forward was chosen: the row's note should repeat that the page presents it
  as a trade-off.

### F10 (major) The indirect light's seam has no internals home

- **Where:** `outline-3.md:32-41` (part 9), `book.md:89` (design decision "a feature that is off is bit-for-bit
  invisible").
- **Problem:** RI 1.3 (seven rows: `IndirectInputs`, the four forms `ST_INDIRECT_PROBES/SCREEN/SKY/AMBIENT`, the two
  gathers, the field gather, compose, the coat's image light, the probe-capture mode), RI code #8 ("`IndirectLight.slang:
  1-131` (whole): the seam ... how features add without changing the default image"), #9, #30, RI concepts 15 (fallback
  hierarchy, premultiplied weights) and 22 ("bit for bit when off"), RI figure 1, RI rules 16, 22, 24, exercise E13. The
  only candidate, `indirect/problem`, is a concept page; `indirect/ibl` is about the filter chain. The design decision
  "off is bit-for-bit" has no named home anywhere.
- **Proposal:** Add "`indirect/seam` | Where indirect light meets the surface: inputs, gathers and fallbacks | I | M |
  render-indirect 1.3, code #8-#10, #30" after `indirect/ibl` (the slot freed by F1). One-home rows: "The indirect seam,
  the fallback stack | `indirect/seam` | probes, ssr, gi"; "Design decision: a feature that is off is bit-for-bit
  invisible | `indirect/seam` (the `x * 1 + 0` join, dummy SRVs) | every rendering page".

### F11 (major) `indirect/measuring-light` is the wrong kind, in the wrong place, and conflicts with four homes

- **Where:** `outline-3.md:41` ("Measuring light: debug views, the furnace and the meter | H | M"), `book.md:71`.
- **Problem:** Kind H is "No theory; links to the concept page" (`style.md:67`), but its allocation is internals: RD 1.10
  (`SceneLightingView`, `LightingView.frag`, the statistics' quarter-EV histograms and ring of readbacks), RD rule 5 and
  RI 1.9 "Value views without pre-exposure" (subnormals at P = 2^-19), RI figure 26 (statistics pipeline), RI E3 (add a
  view: enum, define, forward branch, overlay, editor enum, test). It sits last in part 9, yet `outline-3.md:3` makes the
  debug view a figure of *every* page of parts 8 to 10, and RD ch. 7 has the reader "read the shadows view". "The
  furnace" in its title collides with `book.md:70`; the GI views (`voxels`, `gi`, `open`, `probes`, RI 1.8) change with GI
  batch 2 (`agent/wave8-rc-world`: `ProbeView.frag`, `GIField.slang`), so the page is W8 without the mark.
- **Proposal:** Move it to part 8 as "`light/measuring-light` | Measuring light: the debug views and their statistics |
  I | M | render-direct 1.10, render-indirect 1.9" after `light/energy` (F1). Split the homes in `book.md:71`: lighting,
  luminance, albedo and indirect views and their statistics, the sun-to-sky ratio: `light/measuring-light`; the shadows
  view (RD 1.10 first row, figure 13): `light/sun-shadows-1`; the AO view: `indirect/ao`; the GI views and stats:
  `indirect/gi-cascades` (W8); the furnace: `light/energy`; the flicker meter (`Tests::MeasureFlicker`, RI 1.9):
  `engineering/test-kinds`; the look-dev harness: `engineering/look-dev`. The use of the views in the editor goes into
  `make/lighting` and `make/materials` (RI G9 "Albedo audit").

### F12 (major) `light/sky` carries two chapters; aerial perspective sits on the wrong page

- **Where:** `outline-3.md:22` ("The sky and the atmosphere | I | L"), `outline-3.md:23` ("Aerial perspective and height
  fog | I | M").
- **Problem:** `light/sky` is allocated RD 1.8 (nine rows), RD concepts 19 and 20, code #31-#33, figures 16-17,
  screenshots 22-24 and 29, rules 3 and 24: the three sky sources, procedural sky, environment maps, Extract and Remove
  Sun, presets with `groundIlluminance`, the sun-to-sky ratio, *and* a full physical atmosphere (participating media
  theory: extinction, scattering, optical depth, Rayleigh, Mie and ozone, phase functions, single vs multiple scattering;
  Hillaire's four tables; the CPU transmittance in double; the 2^14 storage scale; the 14-step double-buffered refresh).
  The atmosphere alone is the size of a textbook chapter (Hillaire 2020, Bruneton 2008). Aerial perspective is the same
  atmosphere integrated into a froxel volume (`AtmosphereAerial.comp.slang`, RD 1.9; RD figure 16 lists it among the
  atmosphere's four tables), but the plan puts it with height fog. Participating media is also needed by height fog, by
  glass (Beer-Lambert, RD 1.1) and by the GI march's transmittance (RI code #26), and has no row in `book.md`.
- **Proposal:** Split into "`light/sky` | The sky as a light: sources, sun extraction and presets | I | M" and
  "`light/atmosphere` | Earth's atmosphere and aerial perspective | I | L | render-direct 1.8 (atmosphere rows), 1.9 (aerial
  perspective), concept 20". Retitle `light/fog` "Height fog" (M: the closed-form integral, its lighting, the sky at
  infinity, `c_MinHeightFalloff`, what a non-volumetric fog cannot do). One-home row: "Participating media: extinction,
  transmittance, phase functions | `light/atmosphere` | fog, `light/clearcoat-transmission` (Beer's law),
  `indirect/gi-cascades` (the march)".

### F13 (major) `light/materials` is a concept page loaded with internals; tangent space has no home

- **Where:** `outline-3.md:13` ("Strata's material model | C | L"), `book.md:56-83`.
- **Problem:** RD ch. 2 asked for "concept + reference" that also says "how a `.stmat` reaches the GPU". Its material is
  internals: `MaterialGPU::Build` (code #4), the 144-byte `MaterialData` with its flags and the memory layout diagram
  (RD 1.1, figure 5), the texture table indirection (24-bit slot, 7-bit sampler, grayscale bit), neutral fallbacks, the
  exactly flat normal in half floats (RD rule 8), the literal 0.04 at IOR 1.5 (code #3, rule 9), the XY normal decode and
  back-face flip (`MaterialTextures.slang:47-72`, code #5, rule 7), immutability through `ReplaceLoadedAsset`, the
  hand-mirrored layouts (rule 14). Normal mapping and tangent space (RD concept 5; curricula 1.9.3 "Normal maps and
  tangent space, reconstructing Z, mirrored instances and flipped tangents [gap]") are split between `assets/textures`
  (BC5), `draw/mirrors-camera-relative` (handedness) and this page, with no row.
- **Proposal:** Keep `light/materials` (C, L) for the model, the maps, alpha modes, emission in nits, plausible albedos,
  IOR as a field, and normal maps and tangent space as a concept. Add "`light/material-data` | From a material file to
  the shader: the material record and its textures | I | M | render-direct 1.1 (GPU rows), code #2-#5, figure 5, rules
  7-9 and 14" after it. One-home row: "Normal maps and tangent space | `light/materials` (concept), `light/material-data`
  (decode) | `assets/textures` (BC5), `draw/mirrors-camera-relative` (handedness)".

### F14 (major) `make/reflections-gi` merges three tutorials into one how-to and makes all of it wait for GI

- **Where:** `outline-1.md:36` ("Sky light, reflections and global illumination in your game | H | L | ... · W8").
- **Problem:** RI 8 proposed three tutorials for game makers: ch. 6 "Using sky, AO and probes in your game" (T, M), ch. 8
  "Shiny worlds: a wet-floor tutorial" (T, S), ch. 11 "Trying global illumination in a scene" (T, S). As a how-to the page
  has "No theory" and steps only (`style.md:67`), and it is not run by the tutorial tool (`pipelines.md`, "Tutorials that
  are run": tutorials only), so the probe bake (`lighting.bakeProbes`, deterministic, one undo step) and the wet floor
  are never checked against the engine. The whole page waits for 0.8.0 because of GI, though sky, AO, probes, bakes and
  SSR do not change in wave 8 (reflections R1/R2 are on main, RI 1.7). The hardest game-maker exercise, times of day with
  two probe sets switched by `SetActive` and preloaded captures (RI 1.6 "Times of day pattern", RI G6, ML 219), is at risk
  of being cut from a merged page.
- **Proposal:** Split into "`make/reflections` | Sky light, ambient occlusion and reflections in your game | T | L |
  render-indirect ch. 6 and 8 (sky sources, AO, probes and bakes, times of day, a wet floor with SSR)" written in phase A,
  and "`make/global-illumination` | Trying global illumination | T | S | render-indirect ch. 11 · W8".

### F15 (major) W8 marks miss pages that wave 8 does change

- **Where:** `outline-3.md:59` (`image/quality-settings`, no mark), `outline-1.md:37` (`make/look`), `outline-3.md:41`
  (F11), `outline-3.md:12, 24` (`light/units-exposure`, `light/clearcoat-transmission`), `outline-3.md:20`
  (`light/sun-shadows-2`), `pipelines.md:13-16` (the pin move).
- **Problem:** `agent/wave8-local-lights` adds a quality row `LocalShadowViewsPerFrame` (12, 12, 24, 48), changes
  `MaxShadowedLocalLights` from {4, 16, 16, 16} to {4, 16, 64, 256}, raises `Renderer.Quality`'s section version to 7 and
  removes `SceneRendererSpecification::LocalShadowViewsPerFrame` (`RendererQuality.cpp` and `.h` diff; branch
  `ReleaseNotes.md` "Upgrading from 0.7.0"); `agent/wave8-rc-world` changes the GI row's memory (`RendererQuality.cpp`,
  "State the GI row's memory as the layouts count it"). RD 1.11's table of quality rows, which the quality page will
  teach, is thus wrong at 0.8.0. The area-light branch gives rect lights units in nits or lumens (`AreaLightUnits`) and a
  coat path ("Pin the coat's least lobe in the shaded sum"). RD rule 18 says "Local lights still turn with TAA on main";
  the local-lights branch fixes their noise (`LocalShadows.slang`), so a sentence of `light/sun-shadows-2` turns false.
  The pin tool reports only quotes whose text changed (`pipelines.md:13-16`), not prose claims and numbers.
- **Proposal:** Mark `image/quality-settings` W8 (or require that its prose names no preset values and the rows table is
  only the generated `reference/renderer`); mark `make/look`'s Graphics Quality section W8. Note "rect-light units if
  area lights land" on `light/units-exposure` and "coat under rect lights" on `light/clearcoat-transmission`. Add to
  `process.md` "What a writer is given"/notes: every non-W8 page of parts 8 to 10 lists its claims that wave 8 can move
  (numbers of shadowed lights, views per frame, noise, quality values, GI views) in its notes, and phase B step 6
  (`process.md:85`) re-reviews that list along with the pin tool's output.

### F16 (major) The light-records row of the one-home table is not one home and not about shadows

- **Where:** `book.md:67` ("Shadow casters, light records | `light/*` shadow chapters | draw").
- **Problem:** "`light/*`" names four pages, and light records are not a shadow topic: they are the render scene's
  96-byte `RenderData::LightRecord` per light component, kept from EnTT signals with a change log for the GPU mirror (RD
  1.3, `R/RenderLights.h:16-129`; RD figure 6; RD rule 13). The render-scene inventory claims them too
  (`render-scene.md:49` "Point and spot light records ... their own change log and GPU buffer"). Sun casters and local
  casters are found by different code (`FindShadowCasters` per cascade, RD 1.6; `FindLocalShadowCasters` and the
  `LocalShadowViewKey` cache, RD 1.7).
- **Proposal:** Replace the row with: "Render-scene records and change logs (the mechanism, lights included) |
  `draw/render-scene` | light"; "What a light record holds, the sun's choice, `LightData` | `light/lights` | draw";
  "Sun shadow casters, the cascade cache | `light/sun-shadows-1` | `draw/occlusion`, `draw/gpu-driven`"; "Local shadow
  casters and view caches | `light/local-shadows` | `draw/gpu-driven`".

### F17 (major) "What Strata does not do" lacks most rendering absences; the ones it lists are confirmed

- **Where:** `book.md:93-99`.
- **Problem:** The list's rendering items are correct: no file of `Strata/src` or `Strata/shaders` mentions particles or
  decals; there is no terrain system (only comments in `SpatialIndex.h`, `RenderScene.h`, `Mesh.cpp`, `WorldAsset.h`; the
  samples' terrains come from `Tools/Generate*Terrain.py`); water exists only as a material value (`Material.h:59`, IOR
  1.33) and the showcase's stand-in. But readers of parts 8 to 10 will look for these, which the engine does not have:
  - volumetric fog, light shafts and fog volumes (`RendererComponents.h:126-129` "no volume: no light shafts or local
    lights in the fog"; `Scene.slang:13-14` reserves SRV 34 and 36 for a `volumetric` stream "below its cut"; the
    stream is tranche 3, "wave 9 unless usage remains", `Docs/Plans/Wave8/plan.md` section 4, and has no branch);
  - area lights (RD 1.13; see F3), and soft light and soft shadows from sized point and spot lights (`Docs/Roadmap.md:
    946-947`);
  - lightmaps and baked GI (no `Lightmap` in the engine; probes are the only bake), hardware ray tracing (no ray query in
    the renderer; RI 1.8: "hardware ray queries" below the GI spec's cut);
  - subsurface scattering (the owner's item 7, `Docs/Plans/Wave8/owner_feedback.md`, not in wave 8; no `Subsurface` in the
    engine), sheen, anisotropy, iridescence, specular and thickness maps, EXR import (`Docs/Roadmap.md:949`);
  - MSAA (`Docs/Roadmap.md:944-945` "Left for later"), temporal upscaling and rendering below native resolution (ruled
    out by the owner's direction, same lines: a decision, not a gap);
  - HDR display output (no HDR10, PQ, scRGB or Rec. 2020 output path in `Strata/src` or `Strata/shaders`);
  - reflection probes captured at run time (probes are baked; "a moving sun does not relight them", `Docs/Roadmap.md:943,
    947`), SSR on transparent surfaces and glass behind glass (`Docs/Roadmap.md:940-942, 948`; RD rule 27);
  - a second shadowed directional light (`Docs/Roadmap.md:949-950`; one sun shines, RD 1.3 `CollectLights`), virtual
    shadow maps (`Docs/Roadmap.md:1670`);
  - GI from local lights and from moving or skinned objects (RI 1.8, spec D18 below the cut).
- **Proposal:** Replace "particles, terrain tools, water and decals as engine features" in `book.md:98-99` with:
  "particles, terrain tools, water and decals as engine features; in rendering: volumetric fog and light shafts, area
  lights (unless 0.8.0 ships rect lights) and soft light from sized lamps, lightmaps, hardware ray tracing, subsurface
  scattering, sheen, anisotropy and iridescence, MSAA, upscaling (by decision), HDR display output, run-time probe
  capture, reflections of and through transparent surfaces, a second shadowed sun, global illumination from lamps and
  moving objects". Each gets its paragraph on the page a reader would search (`light/fog`, `light/area-lights`,
  `indirect/problem`, `indirect/probes`, `indirect/ssr`, `light/materials`, `image/quality-settings`,
  `image/encoding`, `indirect/gi-limits`).

### F18 (minor) Transparency and compositing are taught nowhere as a concept

- **Where:** `outline-3.md:24` (`light/clearcoat-transmission`), `outline-2.md` (`draw/batching`).
- **Problem:** Alpha modes are in `light/materials` (RD 1.1), back-to-front sorting in `draw/batching`
  (`render-scene.md:85`), premultiplied weights in SSR and the fallback stack (RI rules 15-16, concept 15), glass's limits
  in RD rule 27. The over operator, premultiplied alpha, why blended surfaces skip the prepass, AO and SSR, and
  order-independent transparency as what Strata does not do (curricula 1.9.3 "transparency, alpha testing and sorting,
  order-independent transparency") have no home.
- **Proposal:** Retitle `light/clearcoat-transmission` "Transparency, clear coat and glass" (I, L) and make it the home
  of "Transparency, blending and premultiplied alpha | `light/clearcoat-transmission` | draw/batching (sorting),
  indirect/ssr".

### F19 (minor) Design decisions have no named homes

- **Where:** `book.md:85-91`.
- **Problem:** The paragraph says each decision is "stated once, with its reason, on its home page", but names none. The
  rendering ones are used in several parts: "nothing may need history" by sun shadows (fixed blue noise, RD rule 18), AO
  (RI rule 7), SSR Spatial and local shadows (wave 8), "GI traces world data" by RI rule 23.
- **Proposal:** Name them in the paragraph: no history: `light/sun-shadows-2` (first use; `indirect/ao`, `image/taa`
  link); never below native resolution: `image/quality-settings`; GI traces world data: `indirect/gi-voxels`; off is
  bit-for-bit: `indirect/seam` (F10); real units with pre-exposure: `light/units-exposure` (units) and
  `image/pre-exposure` (mechanism).

### F20 (minor) No reference renderer to judge the approximations against

- **Where:** `outline-3.md:32` (`indirect/problem`).
- **Problem:** Part 9 teaches six approximations of the rendering equation (sky IBL, AO, probes, SSR, voxels, cascades)
  and a reader never sees the answer they approximate. The curricula study lists "Reference renders and validation:
  white-furnace tests, comparing to a path tracer [gap]" (1.9.5). The plan has the means: compiled sketches
  (`pipelines.md`, `sketches/`) and the look-dev Cornell box (`lookdev.cornell`, RI 1.9).
- **Proposal:** Allocate to `indirect/problem` a Sketch: a small Monte Carlo path tracer of the Cornell box (C++,
  standard library, image out), and have `indirect/ao`, `indirect/probes`, `indirect/gi-cascades` compare their figures
  with its image. Add the sketch to the figure manifests as a "reference" kind.

### F21 (minor) The blanket figure rule of parts 8 to 10 cannot hold

- **Where:** `outline-3.md:3-4` ("Every page of parts 8 to 10 has figures rendered by the engine: the effect off and on,
  its debug view, and a sweep of its main setting").
- **Problem:** Several pages have no switch, no debug view, or a switch only code can set: `light/reflectance` and
  `light/brdf` (the BRDF cannot be off), `light/units-exposure`, `indirect/problem`; specular AA
  (`SceneRendererSpecification::SpecularAntiAliasing`, RD screenshot 5), the horizon fade (RI screenshot 5), GI's
  `BounceGain` (RI screenshot 30), "before" states of 0.6.0/0.7.0 (RD screenshot 2, RI 9) — `pipelines.md:93-100` itself
  lists such switches. A writer told to produce three figure kinds per page will invent impossible recipes.
- **Proposal:** Replace the sentence with: "Every page of parts 8 to 10 takes its figures from its inventory's
  'Screenshots' and 'Diagrams' lists (RD 4, RI 4, render-image 4); a feature with a switch gets off and on, its debug
  view and a sweep; one without gets a diagram or a lab."

### F22 (minor) Conditional W8 for the tranche-3 streams is not recorded

- **Where:** `outline-3.md:13, 23` (`light/materials`, `light/fog`), `outline-1.md:33` (`make/materials`).
- **Problem:** `volumetric` (owns `Fog.glsl`, `HeightFogComponent`, adds `FogVolumeComponent`) and `showcase-engine`
  (owns `Asset/Material*`, `MaterialTextures`, changes `MaterialData`'s 144 bytes) are tranche 3, "wave 9 unless usage
  remains" (`Docs/Plans/Wave8/plan.md` section 4 table; RD 9). No branch exists for either today, but if one joins landing
  2, `light/fog`, `light/materials`, `light/material-data` and `make/materials` change.
- **Proposal:** Add to those rows "(W8 if `volumetric` / `showcase-engine` land in 0.8.0)" and a line to `process.md`
  phase B step 6: check both streams in the 0.8.0 release notes before re-reviewing.

### F23 (minor) Small allocations both inventories make, with no home given

- **Where:** `book.md:56-83`.
- **Problem:** Each of these is in both inventories or in one inventory and another area, and the plan does not decide:
  preview lighting (RD 1.3, RI 1.1), Extract and Remove Sun and sky presets (RD 1.8, RI 1.1), the scene-color copies
  (glass's half-resolution copy and SSR's full-resolution previous-frame copy from the same `SceneColorCopy.comp`, RD
  1.1, RI 1.7), spherical harmonics (`basics/math-light`, `indirect/ibl`, `indirect/probes`, GI batch 2 moves the GI field
  to SH too), the balanced default template (RD 1.5: 120,000 lux, sun-to-shade ratio checked by `GPU.Editor.Lighting`).
- **Proposal:** Rows: "Preview lighting | `light/lights` (code), `make/lighting` (use) | indirect"; "Sky presets, Extract
  and Remove Sun | `light/sky` | `make/lighting`, `indirect/ibl`"; "Scene-color copies | `light/clearcoat-transmission` |
  `indirect/ssr`"; "Spherical harmonics (the math) | `basics/math-light` | indirect"; the default template's lighting goes
  to `make/lighting` with `worlds/templates` linking.

### F24 (minor) Order of pages inside part 8

- **Where:** `outline-3.md:12-24`.
- **Problem:** Area lights come before many lights and before shadows, though rect lights would enter the clusters; with
  F1, F5, F11, F12, F13 the part needs a stated order.
- **Proposal:** units-exposure, materials, material-data, reflectance, brdf, energy, measuring-light, lights,
  many-lights, area-lights, shadow-basics, sun-shadows-1, sun-shadows-2, local-shadows, sky, atmosphere, fog,
  clearcoat-transmission (18 pages); part 9: problem, ibl, seam, ao, probes, ssr, gi-voxels, gi-cascades, gi-limits (9
  pages). With F7 and F14 the book has 288 pages instead of 282.

---

## Appendix A: where each inventory item goes (render-direct)

"OK" means the outline has a plausible, single home. Items marked with a finding number are the problems above.

### Features (RD 1)

| Group | Items | Home | Status |
| --- | --- | --- | --- |
| 1.1 Material model | PBR model, alpha modes, emission, nine maps, glTF extensions, material commands | `light/materials`; commands in `make/materials` | OK |
| 1.1 GPU side | GPU record 144 B, fallbacks, exact flat normal, texture table, XY normals, IOR to F0, immutability | none of kind I | F13 |
| 1.1 Clear coat, glass, scene-color copy | | `light/clearcoat-transmission` | OK (F18, F23) |
| 1.2 BRDF | GGX/Smith/Schlick/Lambert, minimum roughness | `light/brdf` | OK (F5) |
| 1.2 Split-sum table, energy compensation | | `indirect/ibl`, `indirect/energy` | F1 |
| 1.2 Specular AA, sized highlights, horizon fade | | `light/brdf` and `indirect/energy` | F4 |
| 1.2 Forward variants, EQUAL test, derivative rule, `SanitizeHDR` | | none | F9, F6 |
| 1.2 Probe-capture mode | | `indirect/probes` | OK |
| 1.2 Mirrored instances | | `draw/mirrors-camera-relative` | OK |
| 1.3 Light types, falloff, cone, one sun, LightData, spot bounds, drawn transforms | | `light/lights` | OK (F2) |
| 1.3 Light records | | `book.md:67` "light/*" | F16 |
| 1.3 Preview lighting | | not decided | F23 |
| 1.4 Many lights | CPU and GPU paths, clusters, overflow bisection, forward loop, stats | `light/many-lights` | OK |
| 1.5 Units, reference values | | `light/units-exposure` | OK |
| 1.5 Exposure model, pre-exposure, settled pre-exposure | | three claimants | F6 |
| 1.5 Balanced default template | | not decided | F23 |
| 1.6 Sun shadows | 18 rows | `light/sun-shadows-1` (map, layout, fifth cascade, depth fit, sub-texel casters, caster search, containment, blend, cache, stats); `light/shadow-basics` (pancaking, biases, alpha-masked casters); `light/sun-shadows-2` (PCSS, ranges, mask, stair blur, contact, transparent receivers) | OK |
| 1.7 Local shadows | 9 rows | `light/local-shadows` (W8) | OK |
| 1.8 Sky | 10 rows | `light/sky` | F12 |
| 1.9 Fog and aerial perspective | 5 rows | `light/fog` | F12, F22 |
| 1.10 Debug views | shadows view, lighting views, statistics, editor access, look-dev | `indirect/measuring-light`, `engineering/look-dev` | F11 |
| 1.11 Quality rows | | `image/quality-settings`, `reference/renderer` | F15 |
| 1.12 GPU stages and bindings | | `gpu/frame-tour`, `reference/renderer` | OK |
| 1.13 Area lights | | `light/area-lights` | F3 |
| 1.14 Tests | | each page's "how it is tested" | OK |

### Concepts (RD 2)

| # | Concept | Home | Status |
| --- | --- | --- | --- |
| 1 | Light as a quantity, units | `light/units-exposure` | OK (F6 retitle) |
| 2 | Linear color, HDR targets, half floats | `basics/color`, `light/units-exposure`, `image/why-post` | F6 |
| 3 | Exposure, EV100, pre-exposure | `light/units-exposure`, `image/exposure`, `image/pre-exposure` | F6 |
| 4 | Metallic-roughness | `light/materials` | OK |
| 5 | Textures as inputs, normal maps, tangent space | split three ways | F13 |
| 6 | Reflection equation and BRDF | `light/brdf` (internals) | F5 |
| 7 | Fresnel, F0, IOR | three claimants | F4 |
| 8 | Split sum | `indirect/ibl` | OK |
| 9 | Energy, multiple scattering | `indirect/energy` (part 9) | F1 |
| 10 | Specular aliasing | two claimants | F4, F7 |
| 11 | Light sources, attenuation | `light/lights` | OK |
| 12 | Sized sources | ambiguous | F3, F4 |
| 13 | Forward, deferred, tiled, clustered | `light/many-lights` and `gpu/frame-tour` | F9 |
| 14-17 | Shadow mapping, cascades, soft shadows, screen-space shadows | shadow pages | OK; noise needs F7 |
| 18 | Local shadows | `light/local-shadows` | OK |
| 19 | Sky as a light source | `light/sky` | OK |
| 20 | Participating media | `light/sky` (overloaded) | F12 |
| 21 | Fog | `light/fog` | OK |
| 22 | Layered materials, transmission | `light/clearcoat-transmission` | OK (F18) |
| 23 | Measuring lighting | `indirect/measuring-light` | F11 |

### Rules and pitfalls (RD 5)

All 30 have a page once the findings are applied: 1-2 `light/units-exposure`; 3, 24 `light/atmosphere`; 4 `image/pre-exposure`
with one line in `light/units-exposure`; 5 `light/measuring-light`; 6, 10, 29 `light/brdf`; 7-9, 14 `light/material-data`;
11 `light/energy`; 12 `light/area-lights`; 13, 23 `light/lights`; 15-17 `light/sun-shadows-1`; 18-19, 21 `light/sun-shadows-2`;
20 `light/sun-shadows-1` and `light/local-shadows`; 22 `light/local-shadows` and `make/lighting`; 25-26 `light/fog`; 27
`light/clearcoat-transmission`; 28 `image/exposure`; 30 is writer notes (the code wins, `style.md:102-104`).

### Proposed chapters (RD 8)

| RD chapter | Plan | Lost or changed |
| --- | --- | --- |
| 1 Units, HDR, exposure (M) | `light/units-exposure` (L) | overlaps image (F6) |
| 2 Material model (C + reference) | `light/materials` (C) | the GPU path (F13) |
| 3 BRDF in code | `light/brdf` | energy and table moved to part 9 (F1); theory without a concept page (F5) |
| 4 Lights | `light/lights` | wrongly W8 (F2) |
| 5 Many lights | `light/many-lights` | OK |
| 6-9 Shadows | four pages | OK |
| 10 Sky (L) | `light/sky` (L) | overloaded (F12) |
| 11 Air and fog | `light/fog` | aerial perspective belongs to the atmosphere (F12) |
| 12 Layers and glass | `light/clearcoat-transmission` | OK (F18) |
| 13 Lighting tutorial | `make/lighting` | OK |
| 14 Measuring light (reference + tutorial) | `indirect/measuring-light` (H) | kind and place (F11) |
| 15 Reference | `reference/renderer`, `reference/components` | OK |
| Area-light placeholder | `light/area-lights` | F3 |

## Appendix B: where each inventory item goes (render-indirect)

### Features (RI 1)

| Group | Home | Status |
| --- | --- | --- |
| 1.1 IBL (sky component, procedural cube, equirect, filter chain, FIS, budget, shared environments, constant ambient, atmosphere cube) | `indirect/ibl`; component and sources `light/sky` | OK |
| 1.1 BRDF LUT | `indirect/ibl` | F1 |
| 1.1 Preview lighting, Extract Sun, presets | `light/sky`, `light/lights` | F23 |
| 1.2 Shading recap (GGX, energy, specular AA, F0, sized highlights, horizon fade) | `light/*` and `indirect/energy` | F1, F4 |
| 1.3 The seam (7 rows) | none | F10 |
| 1.4 AO (10 rows), 1.5 specular occlusion | `indirect/ao` | OK |
| 1.6 Probes (14 rows incl. bake and times of day) | `indirect/probes`; times of day `make/reflections` | OK (F14) |
| 1.7 SSR (13 rows) | `indirect/ssr` | OK (prerequisites F8) |
| 1.8 GI (22 rows) | `indirect/gi-voxels`, `gi-cascades`, `gi-limits` (W8) | OK; GI views F11 |
| 1.9 Views, stats, furnace, look-dev, flicker meter | `indirect/measuring-light` | F11 |
| 1.10 Frame placement | `gpu/frame-tour` | OK |

### Concepts (RI 2)

1 `indirect/problem`; 2-3 `light/reflectance` (F5); 4-6 `indirect/ibl`; 7 `light/energy` (F1); 8 `light/brdf` (F4); 9, 11, 12
`indirect/ao`; 10 `basics/signals` for the theory (F7), `indirect/ao` for its use; 13 `indirect/probes`; 14 `indirect/ssr`; 15,
22 `indirect/seam` (F10); 16 `indirect/problem` (families) with Strata's choice in `indirect/gi-voxels`; 17 `gi-voxels`; 18-20
`gi-cascades`; 21 `light/measuring-light` (F11).

### Proposed chapters (RI 8)

| RI chapter | Plan | Lost or changed |
| --- | --- | --- |
| 1 Indirect-light problem (S) | `indirect/problem` (M) | OK; add the reference sketch (F20) |
| 2 IBL | `indirect/ibl` | OK |
| 3 Energy, furnace, specular AA | `indirect/energy` | F1, F4 |
| 4 AO | `indirect/ao` | OK |
| 5 Probes | `indirect/probes` | OK |
| 6 Sky, AO, probes in your game (T) | merged into `make/reflections-gi` (H) | F14 |
| 7 SSR | `indirect/ssr` | OK |
| 8 Wet-floor tutorial (T) | merged into `make/reflections-gi` | F14 |
| 9-10 GI I and II | `gi-voxels`, `gi-cascades` | OK |
| 11 Trying GI (T) | merged into `make/reflections-gi` | F14 |
| 12 Measuring light | `indirect/measuring-light` (H) | F11 |
| 13 Reference | `reference/renderer` | OK |

### Rules (RI 5)

1-2 `light/energy`; 3 `light/brdf`; 4 `light/material-data`; 5 `light/area-lights`; 6-9 `indirect/ao`; 10-16 `indirect/ssr`
(16 also `indirect/seam`); 17-21 `indirect/probes`; 22, 24 `indirect/seam`; 23, 26-28 `indirect/gi-voxels`; 25, 29
`indirect/gi-cascades`; 30 `indirect/seam`.

## Appendix C: wave 8 status of the pages of these areas

| Page | Plan | Evidence | Verdict |
| --- | --- | --- | --- |
| `light/lights` | W8 | no wave 8 branch touches light components or records | not W8 (F2) |
| `light/area-lights` | W8 | no stream in the wave 8 plan; branch has CPU math only | W8 section only, with a fallback (F3) |
| `light/many-lights` | W8 | local-lights' 5-line skip in the light loop | phase A, one section revised (F2) |
| `light/local-shadows` | W8 | local-lights rewrites it (971 lines of `SceneRendererLocalShadows.cpp`) | W8, correct |
| `light/sun-shadows-1/2` | — | stable cascades, fifth cascade, stair blur on main | not W8; rule 18's sentence changes (F15) |
| `light/units-exposure`, `light/clearcoat-transmission` | — | area-light units and coat | note "if area lights land" (F15) |
| `light/fog`, `light/materials`, `make/materials` | — | tranche 3 streams, likely wave 9 | conditional (F22) |
| `indirect/ibl`, `ao`, `probes`, `ssr` | — | reflections R1/R2 on main; rc-world touches no seam, AO or SSR file | not W8, correct |
| `indirect/gi-*` | W8 | rc-world batch 2 (SH probes, voxel centering, thin gaps) | W8, correct |
| `indirect/measuring-light` | — | GI views change on rc-world | W8 for its GI part (F11) |
| `image/quality-settings`, `make/look` | — | new row, new preset values, section version 7, GI memory | W8 (F15) |
| `make/lighting` | W8 | local lights' new presets, area lights | W8, but draft in phase A |
| `make/reflections-gi` | W8 | only its GI part changes | split (F14) |

## Appendix D: parts 8 to 10 as a rendering textbook

What a rendering engineer would expect, and where the plan stands after the findings:

| Expected | Status |
| --- | --- |
| Radiometry and photometry, solid angle | `light/units-exposure` + `basics/math-light` (F6) |
| Reflection and rendering equations, BRDF properties, microfacet derivation | missing as a concept (F5) |
| Sampling theory, aliasing, reconstruction, noise | missing primer (F7) |
| Monte Carlo, importance sampling, low-discrepancy sets | `basics/math-light`; patterns in `basics/signals` (F7) |
| Normal mapping, tangent space | no home (F13) |
| Forward, deferred, clustered architectures | two homes (F9) |
| Transparency, compositing, OIT | no home (F18) |
| Participating media, Beer-Lambert, phase functions | no home (F12) |
| Shadow mapping theory, filtering families (PCF, PCSS, VSM/ESM/MSM) | `light/shadow-basics`, `light/sun-shadows-2` (OK) |
| Cube maps, SH, split sum, prefiltering | `indirect/ibl`, `basics/math-light` (OK) |
| GI families compared, a reference to compare with | families in `indirect/problem` (OK); reference missing (F20) |
| Color science, tone mapping, exposure | `basics/color`, part 10 (outside this lens; OK as planned) |
| Working color space of the renderer | `basics/color` should state it: scene-linear sRGB (Rec. 709) primaries (`PostProcessMath.h:62` "scene-linear sRGB light"); a sentence, not a finding |

## Not checked

- The render-image, render-core and render-scene inventories were read only where they overlap these two areas (their
  proposed chapters and the overlapping concepts); their own completeness is other critics' work.
- The bodies of the wave 8 branches beyond diff stats, the area-light header and the local-lights shader, quality and
  release-note diffs; `agent/wave8-rc-world`'s effect on the GI pages' content.
- Whether `viewport.capture` can set the specification switches the figure recipes need (RD 9 leaves it open).
