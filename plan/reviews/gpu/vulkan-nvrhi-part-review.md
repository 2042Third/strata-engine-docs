# Part review: gpu/vulkan-nvrhi (group 1 of 2)

- unclear: the opening sentence joined "open a GPU" and "keep it busy" with a comma alone; now "open ... and keep it busy".

Checked and held: the clamp of MaxFramesInFlight to 1-4 (VulkanGraphicsDevice.cpp:272), AdapterIndex only in GraphicsDevice.h and VulkanGraphicsDevice.cpp, the reject lines and their order (644-732, info level), the score, the queue families, portability subset and memory budget, the NVRHI callback, RendererData's declaration order, four samplers and eight fallbacks (the area light table is a ninth texture, constant data, not a fallback), the editor and runtime module lists, OnEndFrame in reverse module order, RegisterRendererModule, commit 1e0fa713 and GPU.SceneRenderer.Materials.
