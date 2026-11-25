# Review exercises of the part `draw`

Pages each exercise needs (ids under `draw/`):

1. Basic: render-scene, render-scene-gpu, entities-to-draws (free list, instance bytes, budget frames, `deferredInstanceBytes`, 27-bit limit)
2. Basic: bounds-culling, asset-requests (screen fraction, High and Normal, prefetch, unloaded assets)
3. Medium: lod, batching (halving rule, error rule, sort key, radix passes, fade codes)
4. Medium: mirrors-camera-relative, batching (mirror flag, cofactor normal, winding, draw count, camera-relative precision)
5. Medium: mip-streaming, asset-requests, bounds-culling (mesh priority, wanted level, read order, bindless slot)
6. Hard: occlusion, gpu-driven (pyramid levels, footprint, counting offsets, camera cut, feedback)
7. Hard: motion-vectors, skinned, render-scene-gpu (history size, palette skip, copy list versus whole copy, per-renderer history)
8. Hard: lod, skinned, motion-vectors (the prepass and forward pass agree: transposed dither table, fade steps, thumbnails, the skinned velocity variant)

Numbers checked by script: sort keys and XOR of exercise 3, the pyramid of exercise 6, the disagreeing pixels per step of exercise 8.
