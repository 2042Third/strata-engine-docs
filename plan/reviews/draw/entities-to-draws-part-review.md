# Part review: draw/entities-to-draws (group 1 of 2)

- contradiction: the tables sent `RenderSceneGPU::Update` and the uploaded-bytes line to draw/render-scene, but the GPU copy's update is draw/render-scene-gpu's; both now link it, and so does the answer of Check yourself 3.
- contradiction: `ResolveAssets` and the assets-requested line linked draw/render-scene; the resolve cache and request priorities are draw/asset-requests' home, which both rows now link.
- contradiction: the occlusion phases and the occluded line linked draw/gpu-driven; draw/occlusion is their page, linked now in the table and in the sentence below the timeline.
- contradiction: the `FindShadowCasters` row linked only draw/bounds-culling, which says it does not find the sun's casters; light/sun-shadows-1 is linked beside it.
- wrong: "While a scene plays, its playing copy has its own GPU copies, which doubles sceneMirrorMB": the pin (Docs/Architecture.md, the clone's GPU copy) doubles the mirror memory only while both copies live; the sentence says so.
