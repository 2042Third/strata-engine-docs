# Part review: draw/batching (group 1 of 2)

- gap: the brief asks the measured proof (10,000 materials in one opaque call, 10,000 meshes in 8 draw commands) to be read through the perf keys; both sentences now use `:value` of `perf.PerfGPU.Renderer.Render10kMaterials.OpaqueDrawCalls.Measured` and `perf.PerfGPU.Renderer.Render10kUniqueMeshes.DrawCommands.Measured`.
- wrong: the DrawBuckets callout "Lines 2139-2146" left out the line that grows the bucket; it is 2139 to 2147.
