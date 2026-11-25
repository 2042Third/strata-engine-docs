# Part review: draw/render-scene-gpu (group 2 of 2)

- unclear: the worked example's "The loader first builds the proxies" marked the asset-loader term for the scene's preparation; it now names `PrepareLoadedScene`, which builds the proxies in chunks of 2,048 (`RenderScene::c_PrepareChunk`).

Checked and held at the pin: seven buffers of `BufferSet` (`GetGrowingBuffers`), the 64-byte `GPUProxy`, `NewInstanceBytesPerFrame` 16 MiB, `c_PrepareUploadBytes` 16 MiB, `c_UnusedFrames` 300, `c_RecycleBytes` 1 MiB, the staging-failure path, `PrepareExtraction`'s clone rule, the budget test (300 proxies, 4 frames).
