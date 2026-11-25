# Brief: `light/clearcoat-transmission`

| Field | Value |
| --- | --- |
| Title | Transparency, clear coat and glass |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `light/energy`, `draw/batching` |
| From | render-direct ch. 12; 1.1 (clear coat, glass, the scene-color copy); home of transparency, blending and premultiplied alpha, and of the scene-color copies; the coat under rectangle lights is `light/area-lights`' |
| Unit | `plan/allocation/light.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `light/clearcoat-transmission` — Transparency, clear coat and glass

**Covers.** The job: surfaces that are layered or let light through. The problem: car paint and varnish, glass that
bends what lies behind it, and surfaces that are only partly there; the approaches are layered BRDFs (Weidlich-Wilkie),
screen-space refraction from a copy of the image, and ray-traced refraction, with a table. First the home of
transparency: blending and premultiplied alpha from zero, why the order of transparent surfaces matters (the
back-to-front order is `draw/batching`'s), and why Blend surfaces are shaded after the opaque ones; one sentence gives
the HDR target's alpha convention (glass, unblended, writes alpha 1 as opaque writers do, and blended surfaces multiply
it by 1 - a; the why is `image/taa`'s). The clear coat in code: a dielectric layer of IOR 1.5 with its own strength,
roughness and normal map; the light it reflects no longer reaches the base (1 - F); image light on the coat by its
prefiltered Fresnel. Glass: `Transmission`, `IOR`, `Thickness` along the normal and the attenuation color and distance;
refraction (Snell's law and `refract`) to an exit point at the thickness scaled by the instance, a mip of the copy
chosen by roughness, Beer's absorption (linked to `light/atmosphere`), the surface's reflectance taken out (the glass
diagram and `TransmitLight`). How it is drawn: first in the transparent pass, unblended, writing depth, entity ids and
motion. The scene-color copy: half resolution, six levels, B10G11R11 or RGBA16F without extended storage formats, made
after the sky and read at SRV 19. The rule: glass is not in the prepass, so it gets no AO, casts no shadow, and the copy
holds no glass behind it. "What Strata does not do": water as an engine feature (water is a material with IOR 1.33),
reflections of and through transparent surfaces and glass behind glass, order-independent transparency. A toy blends two
layers. Figures: the Physics Playground's balls with coat roughness 0 against 0.5 and a coat normal map; its ball-pit
walls with IOR 1.0 against 1.5, `Thickness` 0 against 0.1 and an attenuation color. How it is tested: the
coat-over-metal furnace case, `GPU.SceneRenderer.Materials`, `PerfGPU.Renderer.Transmission`. The exercises make a glass
case with a colored liquid on a varnished base, and trace a material whose `Transmission` turns above 0 into the glass
draws and `TransmitLight`. The coat under rectangle lights is `light/area-lights`'. Afterwards the reader can author
coats and glass, and explain what transparency in Strata can and cannot show.

**Leaves out.**

- The transparent pass's back-to-front order → `draw/batching`
- Beer's law and transmittance → `light/atmosphere`
- Reflections on screen and their limits → `indirect/ssr`
- The coat under rectangle lights → `light/area-lights`
- The TAA's reactive mask for transparent surfaces → `image/taa`
- The sun's shadow on transparent surfaces → `light/sun-shadows-2`
- Glass and alpha modes in a game → `make/materials`

**Fit.** `fits`: about 4,800 words against L (5,000). Blending from zero, four excerpts and three entries of "What
Strata does not do" take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:46-48` | feature | home | Clear coat, glass (transmission) and the scene-color copy |
| `render-direct:416` | concept | home | Layered materials and transmission; the limits and the mistakes |
| `render-direct:469` | code | home | `Strata/shaders/Scene/Forward.frag.slang:354-371`: `TransmitLight`, refraction to the exit point, the mip by roughness, Beer's law |
| `render-direct:516` | figure | home | Diagram: the refracted ray to the exit point, sampling the half-resolution copy at a roughness level |
| `render-direct:562-563` | figure | home | Sweeps: coat roughness and the coat normal map; glass IOR, thickness and attenuation color |
| `render-direct:622` | rule | home | Glass is not in the prepass |
| `render-direct:647` | hands-on | home | Exercise: a glass case with a colored liquid and a varnished wooden base |
| `new:55` | hands-on | home | Exercise (trace it yourself): a material whose `Transmission` turns above 0 followed with a search: `IsTransmissive` and the flags that make it transparent and transmissive, the extraction's glass batches drawn first in the transparent pass, unblended, and `TransmitLight` in the glass variant. Evidence: `Strata/src/Strata/Renderer/MaterialData.cpp:14-22`, `:35-38`; `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:58`; `Strata/src/Strata/Renderer/SceneRenderer.cpp:2711-2725`; `Strata/shaders/Scene/Forward.frag.slang:354-371` |
| `render-direct:690-691` | term | home | Clear coat, transmission |
| `render-direct:693-694` | term | home | Attenuation color and distance, scene-color copy |
| `render-indirect:617` | term | home | Premultiplied alpha |
| `new:20` | not-done | home | Water as an engine feature: water is a material with IOR 1.33. Evidence: `Strata/src/Strata/Renderer/Material.h:59` |
| `new:21` | not-done | home | Reflections of and through transparent surfaces; glass behind glass. Evidence: `Docs/Roadmap.md:939-942, 947-948` |
| `new:22` | not-done | home | Order-independent transparency: glass shows only what was drawn before it. Evidence: `git grep -niE "order[- ]independent" 822a7a46 -- Strata/src Strata/shaders` finds nothing; `Docs/Roadmap.md:939-940` |
| `new:23` | code | home | `Strata/shaders/Include/PBR.slang:157-192`: the coat's data, its Fresnel and `EvaluateClearcoat` with the base's weight |
| `new:24` | code | home | `Strata/src/Strata/Renderer/SceneRendererGlass.cpp:107-129`: the scene-color copy, level 0 from the HDR target and each level from the one above |
| `new:25` | code | home | `Strata/src/Strata/Renderer/SceneRenderer.cpp:2711-2725`: glass drawn first in the transparent pass, unblended, into its own attachments |
| `render-direct:435` | code | use | `GetAbsorption`, Beer's absorption from the attenuation color; the excerpt's home is `light/material-data` |
| `render-direct:692` | term | link | The Beer-Lambert law; its home is `light/atmosphere` |
| `render-image:35` | feature | use | The HDR alpha convention, one sentence where glass and Blend surfaces are drawn: glass, unblended, writes alpha 1 as opaque writers do, and blended surfaces multiply it by 1 - a; the why is `image/taa`'s (`Strata/shaders/Scene/Forward.frag.slang:458-465`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Energy compensation and the BRDF table | `light/energy` | must |
| Batching and the back-to-front order | `draw/batching` | must |
| The material model's coat and transmission fields | `light/materials` | must |
| Compute shaders | `gpu/compute` | must |
| Mip chains | `assets/textures` | must |
| The Beer-Lambert law | `light/atmosphere` | helps |
| The sun's shadow on transparent surfaces | `light/sun-shadows-2` | helps |
| Screen-space reflections | `indirect/ssr` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `attenuation-color` | Attenuation color | - |
| `clear-coat` | Clear coat | - |
| `premultiplied-alpha` | Premultiplied alpha | - |
| `scene-color-copy` | Scene-color copy | - |
| `transmission` | Transmission | - |
