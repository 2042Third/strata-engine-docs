---
id: gpu/index
title: "The GPU and the renderer's core"
description: "The pages of the part on the graphics card and the renderer's core: how they build on each other and what you can do after them."
tracks: [E]
status: final
generated: index
---

This part explains how a graphics card draws and how Strata's renderer works with it. It starts with how a card runs a frame
and what Vulkan and NVRHI add. Then it teaches shaders, compute, the coordinate conventions and the debugging tools, with a
triangle you draw yourself. The turning point is the renderer's shared machinery: lifetimes, uploads, binding and the
geometry pool, which a tour of a frame joins. Readback, timing, overlays and text come last, and then you can trace and time
a frame pass by pass and predict what the engine does with a resource.
