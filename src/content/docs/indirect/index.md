---
id: indirect/index
title: "Indirect light"
description: "The pages of the part on indirect light: what they cover, how they build on each other and what you can do after them."
tracks: [E]
status: final
generated: index
---

This part teaches how Strata lights a surface with light that bounced before it arrived. It starts with the problem and the sky's image light, then one seam in the shader joins every source. Next come ambient occlusion, reflection probes and screen-space reflections, which each fix a fault of the layers below. The turning point is global illumination: a voxel copy of the world, radiance cascades that trace it into a field of probes, and their limits. Afterwards you can predict the light a pixel gets and name the limit that decides whether a method helps.
