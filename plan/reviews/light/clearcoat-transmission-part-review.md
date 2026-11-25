# Part review of `light/clearcoat-transmission`

- wrong: the coat's image light was placed at lines 324 to 334 of `Strata/shaders/Scene/Forward.frag.slang`; at the pin that code (the prefiltered Fresnel, the indirect light and the emission under the coat) is lines 454 to 467.
