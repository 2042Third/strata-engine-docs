# Brief: `indirect/seam`

| Field | Value |
| --- | --- |
| Title | Where indirect light meets the surface: inputs, gathers and fallbacks |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `indirect/ibl` |
| From | new; the indirect light's join in the forward shader had no page: render-indirect 1.3 (`IndirectInputs`, the four forms, the gathers, compose, the coat's image light), code #8-#10, #30, concept 15 (the fallback stack) |
| Unit | `plan/allocation/indirect.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `indirect/seam` — Where indirect light meets the surface: inputs, gathers and fallbacks

**Covers.** The job: the one place in the forward pass where every kind of indirect light meets the surface. One struct
of inputs is filled once per pixel, two gathers read it (diffuse and specular), and a compose step adds them. How each
input is made is the job of the later pages of the part; this page is their common map. The problem section is one
paragraph that links `indirect/problem`.

The map starts with the frame. On the CPU, `PrepareGlobalIllumination` and `GatherReflectionProbes` run first; on the
GPU the prepass, the screen shadows, then `GPU.AO`, `GPU.RadianceCascades` and `GPU.Reflections` (probe conversions,
then the SSR trace) all run before `GPU.Opaque`, which reads their results: ambient occlusion at SRV 11, the probes at
SRV 9 and 10, the reflections at SRV 18, the GI field at b3 and SRVs 35 to 40 and 54. The fallback-stack diagram then
shows one pixel: screen-space reflections (confidence a) over the probes (weight w, two blended) over the sky (1 - w)
over the constant ambient, in a diffuse and a specular column, with the places where occlusion, specular occlusion and
the multi-bounce fit multiply and where the GI field replaces the diffuse part.

The contract: `IndirectInputs` is filled once; new streams add their fields at the end; Strata 0.7.0's four forms
(`ST_INDIRECT_PROBES`, `SCREEN`, `SKY`, `AMBIENT`) keep their branch order and their expressions bit for bit; a feature
that is off costs nothing and changes no bit, because its input is a dummy (a black cube array without probes, a black
reflection texture, the GI's dummy views). That rule of the renderer has its home on `gpu/frame-tour`; this page shows
it at work. Global illumination that is off changes no bit either, but its gather is compiled in and still costs a
little, which `indirect/gi-limits` states as measured. A toy version of the stack follows in about 40 lines. The real
code is walked in data order: `IndirectLight.slang` in three pieces (the struct and the forms; the diffuse and specular
gathers; compose, with the field gather shown as structure only), `GetIndirectInputs` (the split-sum reflectance with
its energy compensation, the probes' evaluation, the SSR sample, the sky reads, the form chosen in 0.7.0's order, and
Lagarde's specular occlusion, named here and taught on `indirect/ao`), and the end of `ShadeLitSurface`, where ambient
occlusion and the multi-bounce enter, the field joins (one sentence, linking `indirect/gi-cascades`) and the clear coat
takes its own image light with its own occlusion and horizon fade, from the probes, the sky or the ambient only: the
coat gets no screen-space reflections. The fallback hierarchy is taught as an idea of its own: each layer replaces the
next by a weight, premultiplied, so a texel that found nothing adds no black.

Alternatives Strata did not choose: a separate deferred ambient pass, one target per term composed later, a branch per
feature. How it is tested: `GPU.SceneRenderer.Lighting` and `GPU.SceneRenderer.ReflectionProbes` keep the default image
bit for bit. Changing it safely: the required exercise adds a field to `IndirectInputs` and keeps the default image bit
for bit, and a trace exercise finds which form a pixel takes and where the CPU sets what the choice reads. The reader
can then trace any indirect term of a pixel back to the pass that made it.

**Leaves out.**

- How the sky's maps are made → `indirect/ibl`
- GTAO, the multi-bounce fit and Lagarde's specular occlusion as a model → `indirect/ao`
- How probes are gathered, converted and blended, and why a bake drops the lights' highlights → `indirect/probes`
- How screen-space reflections are traced and resolved → `indirect/ssr`
- The field gather's weights and the join's bit-for-bit form → `indirect/gi-cascades`, `indirect/gi-limits`
- "A feature that is off is invisible bit for bit" as a rule of the whole renderer → `gpu/frame-tour`
- The clear coat as a material, and premultiplied alpha → `light/clearcoat-transmission`

**Fit.** `over`: about 4,350 words against M (3,000). One 131-line shader in three pieces, three more excerpts, the
frame's order, the fallback stack and two exercises (E13 with its worked solution, and the trace) pass M's top; by S2
the page takes the next size, L (5,000).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-indirect:82` | feature | home | `IndirectInputs`: the per-pixel struct both gathers read, filled by `GetIndirectInputs` |
| `render-indirect:83` | feature | home | The four forms and 0.7.0's branch order, kept bit for bit |
| `render-indirect:84` | feature | home | The diffuse gather: probes' SH irradiance plus the sky's share, or the sky, or the ambient; times the occlusion color |
| `render-indirect:85` | feature | home | The specular gather: probes' radiance plus the sky's share; SSR mixed premultiplied; specular occlusion only on the fallback |
| `render-indirect:86` | feature | home | The field gather as one of the gathers: field irradiance on the diffuse albedo under the diffuse occlusion, without the multi-bounce fit; its weight and the join are `indirect/gi-cascades`' |
| `render-indirect:87` | feature | home | Compose: each form's scale where 0.7.0 applied it |
| `render-indirect:88` | feature | home | The clear coat's image light: `SampleSpecularLight` with its own Lagarde occlusion and horizon fade; the probes', the sky's or the ambient's light only, so the coat gets no screen-space reflections (`Strata/shaders/Scene/Forward.frag.slang:323-333`; `Docs/Roadmap.md:941-942`) |
| `render-indirect:201` | feature | home | The frame placement of the area: the CPU gathers, `GPU.AO`, `GPU.RadianceCascades`, `GPU.Reflections` before `GPU.Opaque`, and the bindings the forward pass reads |
| `render-indirect:300` | concept | home | The fallback hierarchy SSR, probes, sky, constant ambient, each layer replacing the next by a weight (premultiplied, no black edges); the error of mixing unpremultiplied colors |
| `render-indirect:345` | code | home | `Strata/shaders/Include/IndirectLight.slang:1-131`: the struct and the forms (9-39), the gathers (52-107), the field gather and compose (109-129), shown in three pieces |
| `render-indirect:346` | code | home | `Strata/shaders/Scene/Forward.frag.slang:118-171`: `GetIndirectInputs`, from the split-sum reflectance to Lagarde's specular occlusion |
| `render-indirect:347` | code | home | `Strata/shaders/Scene/Forward.frag.slang:280-338`: the end of `ShadeLitSurface`, where AO, the multi-bounce, the GI join and the clear coat meet |
| `render-indirect:360` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:3453-3490`: AO, GI and reflections before the opaque pass, each in a GPU stage, and what a failed GI frame does to the field's constants |
| `render-indirect:375` | figure | home | Diagram: the indirect-light fallback stack, per pixel, diffuse and specular columns, with the multipliers and the field |
| `render-indirect:506` | rule | home | Features cost nothing when off and the image stays bit for bit: the dummy black cube array, black SSR texture and GI dummy views, checked by tests; named as the renderer's rule from `gpu/frame-tour`; GI off keeps the image bit for bit while its compiled-in gather still costs a little, stated on `indirect/gi-limits` (book.md's design decision) |
| `new:20` | hands-on | home | Exercise (trace it yourself, R32, D27): for one pixel, find which of the four forms `GetIndirectInputs` chooses and where the CPU sets each value the choice reads (the probes' weight, `ReflectionParams.x` for screen-space reflections, `EnvironmentParams.w` for the sky's maps); the solution names the files and functions. Evidence: `Strata/shaders/Scene/Forward.frag.slang:157-159`; `Strata/shaders/Include/IndirectLight.slang:9-12`; `Strata/src/Strata/Renderer/SceneRenderer.cpp:1029`, `:3118` |
| `render-indirect:558` | hands-on | home | Required exercise E13: add a field to `IndirectInputs` for a new term and keep the default image bit for bit (`GPU.SceneRenderer.Lighting`, `GPU.SceneRenderer.ReflectionProbes`) |
| `render-indirect:329` | concept | link | "Bit for bit when off" as a rule of the whole renderer, taught on `gpu/frame-tour` |
| `render-indirect:470` | rule | use | Diffuse gets what specular leaves (`1 - SpecularColor`), visible in the gathers; taught on `light/energy` |
| `render-indirect:110` | feature | use | Lagarde's specular occlusion in `GetIndirectInputs`, named and linked to `indirect/ao` |
| `render-indirect:367` | code | link | The join's `x * 1 + 0` form, quoted on `indirect/gi-cascades` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The irradiance and prefiltered maps and the split sum | `indirect/ibl` | must |
| The forward shader's anatomy, `ShadeLitSurface` and the variants | `light/brdf` | must |
| Energy compensation (`SurfaceData::SpecularEnergy`) and the BRDF table | `light/energy` | must |
| Clear coat and its Fresnel | `light/clearcoat-transmission` | must |
| Premultiplied alpha | `light/clearcoat-transmission` | must |
| Registers, constant buffers and SRVs of the scene layout | `gpu/binding` | must |
| The frame's passes in order, and the rule that an off feature changes no bit | `gpu/frame-tour` | must |
| GPU stages and markers | `gpu/readback-timing` | helps |
| Shader variants made by preprocessor defines | `gpu/shaders` | helps |
| The debug views, as the tool to check a change | `light/measuring-light` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.
