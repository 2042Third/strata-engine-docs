---
id: draw/index
title: "Drawing a scene"
description: "What the pages of the part on drawing a scene cover, how they build on each other from the render scene to motion vectors, and what you can do after them."
tracks: [E]
status: final
generated: index
---

This part follows a scene from its mesh entities to the draw calls of its passes. It starts with the render scene, a retained copy of every mesh entity, and the culling, requests, batching and levels of detail that turn it into draws. Mirrors, positions relative to the camera and the scene's copy on the graphics card follow. Then culling and draw lists move to the graphics card, and occlusion culling follows. The last pages teach mip streaming, skinned meshes and motion vectors, so that you can predict a frame's draws, uploads and requests and diagnose passes that disagree.
