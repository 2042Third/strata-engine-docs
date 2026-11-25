# Part review: draw/mip-streaming (group 2 of 2)

- contradiction: contract rule 5 marked "GPU copies" with the term `gpu-copy`, the render scene's GPU copy of `draw/render-scene-gpu`; the texture's level copies are now "copies on the GPU", as are the two later uses in "Dropping and forgetting" that markterms would have marked.
- unclear: the link text "the renderer rules" did not name its target; it now reads "asking for assets at draw time".

Checked and held at the pin: `c_AssetPrefixHeadBytes` 64 KiB, `c_ResidentTailDimension` 32, `c_FadeInSeconds` 0.25, `c_IdleDropSeconds` 30, `c_ForgetFactor` 2, `c_MaxDropsPerFrame` 8, `c_RetryFrames` 60, `CanChangeLevels` (version 2), the ranking test's order, `ForBake` and `ForThumbnails` without fades, the Mip view's four colors.
