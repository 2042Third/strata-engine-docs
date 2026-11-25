# Part review of `light/local-shadows`

- gap: the brief assigns the row `MaxShadowedLocalLights` with its values, and the page named the row without them; it now gives the presets' 4, 16, 64 and 256 lights (`c_MaxShadowedLocalLightsRow`, `Strata/src/Strata/Renderer/RendererQuality.cpp:45`), which also shows that Low allows fewer than the Manual's 16.
