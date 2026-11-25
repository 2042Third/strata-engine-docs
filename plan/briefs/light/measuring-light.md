# Brief: `light/measuring-light`

| Field | Value |
| --- | --- |
| Title | Measuring light: the debug views and their statistics |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `light/brdf`, `gpu/readback-timing`, `gpu/debug-drawing` |
| From | render-direct ch. 14, 1.10 and render-indirect ch. 12, 1.9 (was `indirect/measuring-light`, a how-to): the lighting, luminance, albedo and indirect views, their statistics, the sun-to-sky ratio; the shadows view is `light/sun-shadows-1`'s, the AO view `indirect/ao`'s, the GI views `indirect/gi-cascades`' |
| Unit | `plan/allocation/light.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `light/measuring-light` — Measuring light: the debug views and their statistics

**Covers.** The job: show light as numbers, so that a scene is judged by measurement and not by eye on one monitor. The
problem and its approaches in one section: false-color luminance, albedo validation, furnace tests, texel-density views.
The map: a view is chosen per renderer (`SceneLightingView`, through `MaterialParams.y`), the forward pass branches on
it, an overlay draws the legend's colors, and a compute pass counts every pixel into histograms that come back through a
ring of readbacks, never waited for. The views: Lighting (every lit surface white, through the scene's exposure),
AmbientOcclusion and Indirect (one sentence each says what ambient occlusion and indirect light are and links
`indirect/problem`), Luminance (EV100 bands, log2 of nits plus 3, from 5 to 17) and Albedo (values outside 0.03 to 0.85
marked); the value views are written without pre-exposure, because 2^-19 would make an albedo of 0.03 subnormal. The
statistics: quarter-EV histograms of surfaces and background, value bins, percentiles, and the illuminance of the sun
and of the sky on flat ground with their ratio (the sky's is pi times the irradiance map at +Y; one sentence on the sky
as a light links `light/sky`). Access: the Scene view's debug view chip, `viewport.capture {debugView}` and
`viewport.setSettings`, whose result holds `debugView.lighting`; each command is a complete line with one sentence and a
link forward to `editor/commands`. The code: the enum of views, the stats shader's group-shared histograms, and what
comes back (`LightingViewStats`). A toy counts EV100 over an image on the CPU. Figures: the Lighting, Indirect,
Luminance and Albedo views of one scene; the luminance view of a sunlit street and an interior; the Albedo view marking
a black and a white cube. How it is tested: `GPU.SceneRenderer.LightingViews`. Changing it safely: a new view keeps the
enum in the order of `Scene.slang`'s constants, and value views stay unexposed. The exercises make a material set (rough
copper, polished gold, wet asphalt) and audit it in the Albedo view, add a lighting view end to end (the enum, the
forward branch, the overlay, the editor's names, a test), and trace one frame's statistics from the stats pass to a
command's result. The word "debug view" is said in one sentence and links its glossary entry on `gpu/debugging`. The
shadows view is `light/sun-shadows-1`'s, the AO view `indirect/ao`'s, the GI views `indirect/gi-cascades`'. Afterwards
the reader can use every lighting view and read its statistics from the editor and from a command.

**Leaves out.**

- The shadows view → `light/sun-shadows-1`
- The ambient occlusion view → `indirect/ao`
- The GI views (voxels, gi, open, probes) → `indirect/gi-cascades`
- The list of every debug view and how views work → `gpu/debugging`
- EV100, metering and exposure → `image/exposure`
- The white furnace → `light/energy`
- The look-dev harness → `engineering/look-dev`
- The legends as the Scene view draws them → `editor-ui/scene-view`

**Fit.** `over`: about 4,450 words against M (3,000). Five views, their statistics, the agent's access, three excerpts
and three exercises pass M's top; by S2 the page takes L (5,000), whose range holds it.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:422` | concept | home | Measuring lighting instead of eyeballing it; the mistake of tuning exposure to fix wrong albedo |
| `render-direct:161` | feature | home | The sun-to-sky ratio as the lighting views report it (`LightingViewStats`) |
| `render-direct:178-180` | feature | home | The five lighting views, their statistics through a ring of readbacks, editor and agent access |
| `render-direct:540-541` | figure | home | The Luminance view of a sunlit street and an interior; the Albedo view marking out-of-range albedos |
| `render-direct:580` | rule | home | Value views are written without pre-exposure |
| `render-direct:641` | hands-on | home | Exercise: a material set audited in the Albedo view |
| `new:35` | hands-on | home | Exercise (trace it yourself): follow one frame's statistics with a search or a debugger from `LightingViewStats.comp`'s buffer through the ring of readbacks (`ResolveLightingViewStats`) to the `debugView.lighting` result of `viewport.setSettings`, and count the frames they come back after. Evidence: `Strata/src/Strata/Renderer/SceneRendererLightingView.cpp:18-19`, `:223`, `:257`; `StrataEditor/src/Editor/EditorViewportCommands.cpp:277` |
| `render-direct:757` | term | link | Debug view: said in one sentence; its one glossary entry is on `gpu/debugging`, beside `render-scene:182`, which lists every view |
| `new:4` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.h:322-336`: `SceneLightingView`, what each view shows |
| `new:5` | code | home | `Strata/shaders/Effects/LightingViewStats.comp.slang:25-87`: every pixel counted in group-shared histograms, then added to the buffer; the sky's light on a horizontal surface |
| `new:6` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.h:364-387`: `LightingViewStats`, the percentiles and the sun and sky illuminance that come back frames later |
| `render-direct:177` | feature | link | The shadows view; its home is `light/sun-shadows-1` |
| `render-indirect:189-193` | feature | home | The lighting views, value views without pre-exposure, statistics, history and exposure under a view, editor and agent access, as render-indirect lists them |
| `render-indirect:417`, `render-indirect:461` | figure | home | Diagram: the statistics pipeline (histogram pass, ring of readbacks, percentiles); the Lighting, Indirect, Luminance and Albedo views of one scene |
| `render-image:101` | feature | home | The Luminance view for judging exposure |
| `render-indirect:326` | concept | home | Measuring light by numbers as render-indirect lists it (with `render-direct:422`) |
| `render-indirect:548` | hands-on | home | Exercise: a new lighting view end to end (the enum, `ST_LIGHTING_VIEW_*`, the forward branch, the overlay, the editor's names, a test) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Luminance in nits and illuminance in lux | `light/units-exposure` | must |
| The forward shader and its value branches | `light/brdf` | must |
| Plausible albedos | `light/materials` | must |
| Readbacks that never wait | `gpu/readback-timing` | must |
| Overlay passes | `gpu/debug-drawing` | must |
| Group-shared memory and atomics | `gpu/compute` | must |
| Percentiles | `core/profiling` | helps |
| EV100 | `image/exposure` | helps |
| The pre-exposure | `image/pre-exposure` | helps |
| Debug views and the `debugView` parameter | `gpu/debugging` | helps |
| Running an editor command | `editor/commands` | helps |
| The sky as a light | `light/sky` | helps |
| Indirect light and ambient occlusion | `indirect/problem` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.
