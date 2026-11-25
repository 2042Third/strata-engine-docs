# Part review of `light/brdf`

- wrong: the map said `Forward.frag.slang` compiles into six pixel shaders; at the pin `strata_add_shaders` builds 24, each of the six variants also with `ST_AREA_LIGHTS`, `ST_FORWARD_FIELD` and both, picked by the pipeline key's `AreaLights` and `Field` (`SceneRenderer::GetScenePipeline`); a paragraph after the variant list says so, and the Summary and Check-yourself 5 name the four forms.
- wrong: the stage paragraph said the light culling runs in `GPU.Setup` on the CPU path; at the pin only the cluster pass runs there and the processor picks the lights (`RunGPULightCulling` only when `m_GPULightsFrame`); the sentence, the Mermaid node and the caption now say so.
- wrong: "Some older documents put them in the culling stage alone" named no source and is not supported by the engine's documents; removed.
- contradiction: Changing it safely sent the reader to `light/measuring-light` for the white-furnace test, which that page says it does not teach; the furnace now links `light/energy`, and the debug views keep the measuring-light link.
- gap: the manifest's crop `highlight` of `specular-aa-compare` was taken but placed nowhere (pagecheck failed); both crops now follow the compare with a sentence that introduces them.
- unclear: `time` raised from 70 to 75, the floor of the page's grown prose.
