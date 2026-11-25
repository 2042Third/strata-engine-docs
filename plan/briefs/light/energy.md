# Brief: `light/energy`

| Field | Value |
| --- | --- |
| Title | Keeping the energy: directional albedo, the BRDF table and the white furnace |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `light/brdf`, `gpu/compute` |
| From | render-indirect ch. 3 (was `indirect/energy`); render-direct concept 9, code #8, #9 (`BRDFLut.comp.slang`); render-indirect concept 7, code #1, #5, #6, rule 2; the furnace tests of `GPUSceneLightingTests.cpp` and the shot `lookdev.furnace`; render-direct figure 4, render-indirect figure 6 |
| Unit | `plan/allocation/light.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `light/energy` — Keeping the energy: directional albedo, the BRDF table and the white furnace

**Covers.** The job: a white surface under a uniform white sky stays white at every roughness. This page carries the
full section on the problem: single-scattering GGX loses light at high roughness, so rough metals look dull and tempt
artists to paint wrong albedos; the approaches are Kulla-Conty 2017, Fdez-Aguera 2019 and Filament's factor 1 + F0 (1 /
E - 1), with their costs. The idea: the directional albedo E, the share of light a lobe reflects for one view direction,
and the BRDF table over (NoV, roughness) that holds the scale and bias of F0; this is the second half of the split sum
(its prefiltered half is `indirect/ibl`'s), which the forward pass reads at SRV t5. The map: the table is computed once
by `BRDFLut.comp` and read by `ShadeLitSurface`, glass and the coat. A toy computes E for one (NoV, roughness) by Monte
Carlo on the CPU. The real code: `BRDFLut.comp` importance-samples GGX with the Hammersley pattern, and the probability
density cancels D; `GetSpecularEnergy` and its use in `ShadeLitSurface`, applied to direct and image light alike;
diffuse keeps 1 - F. The white furnace: a uniform 1-nit sky, where an energy-conserving white surface shows 1
everywhere; the furnace tests (metals, dielectrics by IOR, direct specular, coat over metal) and the look-dev shot
`lookdev.furnace`; the rule that shading changes are checked with the furnace and the debug views, not by eye. Figures:
the plot of E and of the factor 1 / E, and the furnace rows without and with compensation. How it is tested:
`GPU.SceneRenderer.Lighting` (the furnace cases). Changing it safely: AGENTS.md's "light keeps its energy". Exercises:
re-derive the table in C++ for a few points; turn the compensation off locally and measure the loss per roughness; trace
the table from where it is made once to its three readers. Afterwards the reader can derive the BRDF table, explain the
compensation, and test a shading change with the furnace.

**Leaves out.**

- The prefiltered environment, the split sum's other half → `indirect/ibl`
- The look-dev harness itself → `engineering/look-dev`
- Monte Carlo integration from zero → `basics/math-probability`
- The coat's lobe and its compensation → `light/clearcoat-transmission`
- The horizon fade of image light → `indirect/ibl`

**Fit.** `over`: about 4,400 words against M (3,000). The importance-sampling derivation, three excerpts (the furnace
test among them), two figures and three exercises pass M's top; by S2 the page takes L (5,000), whose range holds it.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:58-59` | feature | home | The split-sum BRDF table (scale and bias of F0 by NoV and roughness, the same Smith term) and the multiple-scattering compensation |
| `render-direct:324` | concept | home | The split sum as far as the BRDF table, which also drives the compensation |
| `render-direct:329` | concept | home | Energy conservation and multiple scattering; the mistakes |
| `render-direct:440` | code | home | `Strata/shaders/Include/PBR.slang:59-71`: `GetSpecularEnergy`, with its use at `Strata/shaders/Scene/Forward.frag.slang:211-218` |
| `render-direct:441` | code | home | `Strata/shaders/IBL/BRDFLut.comp.slang:20-49`: importance-sampled GGX, the density that cancels D |
| `render-direct:486` | figure | home | Diagram: E(NoV, roughness) from the table and the factor 1 / E |
| `render-direct:528` | figure | home | The white furnace without and with compensation (`lookdev.furnace`, Tonemapper None) |
| `render-direct:591` | rule | home | Check shading changes with the white furnace and the debug views, not by eye |
| `render-direct:655-656` | hands-on | home | Exercises: re-derive the table in C++; measure the loss with the compensation off |
| `new:34` | hands-on | home | Exercise (trace it yourself): find with a search where the BRDF table is made once (its size, samples and the dispatch of `BRDFLut.comp`) and every reader of `GetSpecularEnergy`: the surface in `ShadeLitSurface`'s setup, the coat's lobe and glass. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:60-61`, `:656-668`; `Strata/shaders/Scene/Forward.frag.slang:218`, `:225`, `:368` |
| `render-direct:683-686` | term | home | BRDF table, directional albedo, energy compensation, white furnace test |
| `render-direct:682` | term | link | The split sum; its home is `indirect/ibl` |
| `render-indirect:59` | feature | home | The BRDF table (128 x 128 RG16F, 512 samples) as render-indirect lists it; the table of `render-direct:58` |
| `render-indirect:72` | feature | home | The compensation as render-indirect lists it (`render-direct:59`) |
| `render-indirect:194-195` | feature | home | The white furnace as tests (`GPU.SceneRenderer.Lighting`) and as the look-dev shot `lookdev.furnace` |
| `render-indirect:259` | concept | home | Energy conservation and the white furnace test; the mistakes |
| `render-indirect:338` | code | home | `Strata/shaders/IBL/BRDFLut.comp.slang:20-49`: the excerpt of `render-direct:441`, shown once |
| `render-indirect:342` | code | home | `Strata/shaders/Include/PBR.slang:59-71`: the excerpt of `render-direct:440`, shown once |
| `render-indirect:343` | code | home | `StrataTests/src/Renderer/GPUSceneLightingTests.cpp:860-914`: the white furnace as a test, copper's expected value from the formula |
| `render-indirect:384`, `render-indirect:427` | figure | home | The energy-loss chart and the furnace pair; with `render-direct:486` and `render-direct:528`, one chart and one pair |
| `render-indirect:467-470` | rule | home | Light keeps its energy, checked with the furnace; diffuse gets what specular leaves |
| `render-indirect:546` | hands-on | home | Exercise: a CPU white furnace, E(NoV, r) plotted and the compensation derived, against `BRDFLut.comp` |
| `render-indirect:587` | term | home | Energy compensation and multiple scattering ("multiple scattering" qualified: `render-direct:749` is the atmosphere's) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The BRDF in code: GGX, Smith, `EvaluateLightWeighted` | `light/brdf` | must |
| Compute shaders and dispatches | `gpu/compute` | must |
| Monte Carlo integration and the Hammersley pattern | `basics/math-probability` | must |
| Integrals over the hemisphere | `basics/math-sphere` | must |
| Writing a GPU test and reading pixels back | `gpu/first-triangle` | must |
| The split sum's prefiltered half | `indirect/ibl` | helps |
| The look-dev harness | `engineering/look-dev` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `brdf-table-lut` | BRDF table (LUT) | BRDF lookup table (LUT) |
| `directional-albedo-e` | Directional albedo (E) | - |
| `energy-compensation` | Energy compensation | - |
| `white-furnace-test` | White furnace test | - |
