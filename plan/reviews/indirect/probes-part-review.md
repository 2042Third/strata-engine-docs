# Part review: `indirect/probes`

- wrong: the `ForBake` callout called its local-light shadow atlas "a larger atlas"; at the pin it is 2048, half the side of Medium's 4096 (`c_LocalShadowAtlasSizeRow`), which a bake fills with every shadow view in its first frame; the callout now says so.
- order: the conversion was placed "between ambient occlusion and the opaque pass", leaving out the global illumination pass that `indirect/seam` puts between them; it now says after ambient occlusion and global illumination.
- wrong: exercise 3 named `Panels/ViewportPanel.cpp`, a path that does not start at the engine's root; it is now `StrataEditor/src/Panels/ViewportPanel.cpp`.
