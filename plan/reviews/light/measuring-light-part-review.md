# Part review of `light/measuring-light`

Checked against the engine at the pin (v0.8.0, 319075e3) and against `light/many-lights`, `light/energy`,
`indirect/gi-cascades` and `indirect/gi-voxels`. Every quote's line notes, the toy's and the audit's outputs, the
worked numbers and the capture's keys hold.

- wrong: the contract named occlusion, albedo and the open share as the views that are not light; at the pin
  `IsLightingValueView` (C++ and `Forward.frag.slang`) and the counting shader's `IsValueView` also hold `Clusters`.
  The contract and the note on the counting shader's value branch now name the cluster's count of lights.
- wrong: the test scene's ratio was written $2.46 / 1.01 = 2.43$; that is 2.44, which the page now says (the test,
  `GPUSceneLightingViewTests.cpp:369`, expects 2.43 within 3 %, which 2.44 meets).
- wrong: an albedo of 0.03 at a pre-exposure of $2^{-19}$ ($5.7 \times 10^{-8}$) was called subnormal; it lies below
  even the smallest subnormal half-float ($6.0 \times 10^{-8}$) and rounds to it, as 0.02 does. The section and Check
  yourself 3 say so.
- wrong: Changing it safely and Exercise 3 said a value view goes into the functions named `IsLightingValueView` and
  "the value branch of the counting shader"; the counting shader's own function is `IsValueView`
  (`LightingViewStats.comp.slang:20`), now named in both.
- unclear: "so a marked bright surface is never taken for a bright one" now reads "so the mark cannot pass for a red
  surface". The resolve's fifth line note repeated the paragraph on the sky's lux and went, to keep size M.
