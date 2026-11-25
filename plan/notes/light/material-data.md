# Notes: light/material-data

## New terms

None. No term is bold-defined on the page.

## Requests

- A figure, not drawn: the flat-normal crop of the normal-map figure (render-direct:531) for "What went wrong before". The page uses no figure; its one diagram is Mermaid.
- Words not on the lists, avoided in prose (kept as code or replaced): grayscale, emissive, dielectric, transmissive, unlit, refraction.

## Not verified

- The Inspector draws its fields from the same property list (brief and inventory only; the editor code was not read).
- The default material stands in for a material that is not loaded (read in `RenderSceneGPU::BuildMaterial`); the claim that this keeps every surface present is an inference.
- "Who uses it" cells of the alternatives table are general statements, without a cited source.
- The 10 m wall and 8 cm figures of the flat-normal bug come from a comment in `Renderer.cpp`, not a measurement.

## Findings not applied

- The brief lists no open findings.
- `render-direct:531` (flat-normal crop figure) is not used: see Requests.
- Exercise "modify the engine and watch the test fail" is a reasoning exercise (exercise 3), not a patch: no tutorial files exist for it.

## Since

Material asset and its GPU record: 0.3.0 (inventory: alpha modes 0.3.0); 144-byte record since 0.6.0; flat normal fix 0.8.0.

## Clerk

- Nothing asked.
