# Brief: `draw/mip-streaming`

| Field | Value |
| --- | --- |
| Title | Mip streaming |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `draw/asset-requests`, `draw/gpu-driven`, `assets/texture-cooking`, `assets/uploads`, `gpu/binding` |
| From | assets "Mip streaming"; moved from `assets/mip-streaming` (it reads the views the render scene reports); home of mip streaming: partial loads, range reads, wanted levels, raising and dropping, fades, bindless slots resolved every frame, the mip view |
| Unit | `plan/allocation/draw.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `draw/mip-streaming` — Mip streaming

**Covers.** The job: keep resident only the mip levels the screen needs, raise them before they are missed and drop
them when nothing needs them, without a frame ever waiting. The problem section teaches the approaches: whole-texture
residency by recency, virtual texturing and sparse residency in tiles, and mip streaming as Unreal and Unity do it.
Strata's choice in the order data flows: a first load reads only a prefix (the header and the resident tail of levels
up to 32x32); views report the textures they drew with their size on screen and UV pixels (published by
`draw/asset-requests`, and by the GPU's port of the measure, `draw/gpu-driven`); the wanted level from texel
density, `floor(log2(size * tiling / UVPixels))`; the least needed give levels to the most needed, reads ranked by
missing levels times coverage; then camera cuts, views that need every level, and the streamer's limits: a view that
jumped (more than 10 units or 45 degrees) has its reads ranked Normal, ahead of what older views asked for; a view
without streaming (the probe bake's `ForBake`, exact-pixel tests) needs every level, keeps it under memory pressure and
counts the texture as pending until it is whole; a texture nobody needed for 60 s is forgotten, at most 8 textures drop
levels per frame, a failed read is tried again after 60 frames, and a texture in view always keeps its tail; range reads
of the loaded asset through the same queue and in-flight budget; raising and dropping levels by a new GPU texture with
the resident levels copied on the GPU, the new ones uploaded and a new bindless slot; the fade-in over 0.25 s, and the
mistake of comparing pixels while fades run (captures and thumbnails turn `FadeTextureLevels` off; tests turn it off or
wait until `TextureTable::GetFadeCount()` is 0); the drop after
30 s unneeded or under budget pressure; memory accounting that follows a texture without replacing it; the switch that
turns partial loads off for tests and baselines. Because a texture's bindless slot changes when its levels change, every
frame resolves the slot and materials keep the stable table index. The mip debug view shows the shortfall in levels
(0, 1, 2, 3 or more) while the reader flies through the Showcase, and a surface at its texture's resident tail beside
the same surface at level 0 shows what a first load holds. What Strata does not do here: mesh streaming, and
virtual texturing with sparse residency. The exercise computes wanted levels by hand, and a "trace it yourself"
follows one texture's raise from `ReportView` to its new bindless slot. At the end the reader can compute
the level a texture wants and say why a cached bindless slot is a bug.

**Leaves out.**

- Mips, color spaces and block compression → `assets/textures`
- The cooked texture's layout, smallest level first → `assets/texture-cooking`
- Budgets, eviction and pins → `assets/residency`
- What is uploaded per frame and when → `assets/uploads`
- Bindless slots and the texture table → `gpu/binding`
- The streaming view and the requests of meshes → `draw/asset-requests`

**Fit.** `fits`: about 4,350 words against L (5,000). The streamer's features in the order data flows take the most,
the camera cuts and limits among them, then four figures and two excerpts.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:6` | not-done | home | No mesh streaming, per level of detail included: only textures load in parts. Evidence: `Strata/src/Strata/Renderer/RendererRegistration.cpp:93`, the only call of `RegisterPrefix` (`git grep -n "RegisterPrefix" 822a7a46 -- Strata/src` finds besides it only its declaration and definition in `Strata/src/Strata/Asset/AssetManager.h:207` and `AssetManager.cpp:127`, and a comment that names it at `AssetManager.h:402`); `Docs/Roadmap.md:1691` |
| `new:7` | not-done | home | No virtual texturing and no sparse residency. Evidence: `git grep -niE "sparseBinding\|sparseResidency" 822a7a46 -- Strata/src` finds nothing |
| `assets:339` | concept | home | Partial residency and mip streaming: whole-texture recency, virtual texturing and sparse tiles, mip streaming; the cached-slot mistake, and the second mistake, comparing pixels while fades run: captures and thumbnails turn `SceneRendererSpecification::FadeTextureLevels` off, tests turn it off or wait until `TextureTable::GetFadeCount()` is 0 (`Strata/src/Strata/Renderer/SceneRenderer.h:200-203`) |
| `assets:187-188` | feature | home | Prefix loads (the 64 KiB head, then the header and the resident tail of levels up to 32x32); range reads of the loaded asset through the same queue and in-flight budget, which fail when the asset changed |
| `assets:190-191` | feature | home | The texture streamer (`ReportView`, the wanted level, raising at once, the drop after 30 s or under pressure, the least needed giving to the most needed, the 0.25 s fade-in, `Hold`, `RequestLevel`); raising and dropping levels by a new GPU texture, resident levels copied on the GPU and a new bindless slot |
| `assets:193` | feature | home | The switch `SetPartialLoads(false)`: whole-texture residency for tests and baselines |
| `assets:206` | feature | home | Bindless slots resolved every frame; material data keeps the stable table index |
| `assets:434` | code | home | `Strata/src/Strata/Asset/AssetManager.cpp:1665-1697`: `ReadPrefix`, the head and what the prefix function asks beyond it, with `GetMipTailByteRange` (`Strata/src/Strata/Renderer/CookedTexture.cpp:230-257`): partial loads |
| `assets:436` | code | home | `Strata/src/Strata/Renderer/TextureStreamer.cpp:28-41`: `ComputeWantedLevel`, with `GetUVPixels` at lines 65-80: the mathematics of mip selection on the CPU |
| `assets:487` | figure | home | The mip streaming loop: reports, wanted level, rank, range read, new texture, copy, upload, slot, fade-in; the drop path |
| `assets:500` | figure | home | The mip debug view of the Showcase while flying, then settled |
| `assets:506` | figure | home | A mip fade-in over two frames |
| `assets:509` | figure | home | A surface at its texture's resident tail (32x32) beside the same surface at level 0 |
| `assets:556` | rule | home | Resolve bindless slots every frame; never cache them |
| `assets:604` | hands-on | home | Wanted levels by hand for a 2048 texture tiled 4 times, checked against `TextureStreamerTests` |
| `new:19` | hands-on | home | Exercise ("trace it yourself"): one texture of the Showcase followed with breakpoints as the camera nears it, from `ReportView` (its wanted level and need) through the range read polled in `OnUpdate` to `Texture::RaiseLevels`, and the frame its bindless slot changes (`Texture::GetBindlessSlot`); the solution names each function and the levels before and after. Evidence: `Strata/src/Strata/Renderer/TextureStreamer.cpp:222-233`, `:523-545`; `Strata/src/Strata/Renderer/Texture.cpp:738`; `Strata/src/Strata/Renderer/Texture.h:134` |
| `new:22` | feature | home | Camera cuts, views that need every level, and the streamer's limits: a view that jumped (more than 10 units or 45 degrees) has its reads ranked Normal, ahead of older views'; a view without streaming (`SceneRendererSpecification::ForBake`, exact-pixel tests) needs every level, keeps it under memory pressure and counts the texture as pending until it is whole; a texture nobody needed for twice the idle drop time (60 s) is forgotten; at most 8 textures drop levels per frame; a failed read is tried again after 60 frames; a texture in view keeps its tail. Evidence: `Strata/src/Strata/Renderer/TextureStreamer.h:30-35`, `:44-48`, `:77-97`, `:102`, `:176`, `:182`, `:188`; `Strata/src/Strata/Renderer/SceneRenderer.h:195-199`; `Strata/src/Strata/Renderer/SceneRenderer.cpp:262-269`; `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp:694-696` |
| `assets:703-709` | term | home | Mip tail; mip streaming; partial load; range read; wanted level; texel density; fade-in |
| `assets:189` | feature | use | Memory accounting that follows a texture without replacing it (homed on `assets/residency`) |
| `assets:192` | feature | use | The first-load estimate, which counts only the head while loads read prefixes (homed on `assets/references`) |
| `assets:214` | feature | use | The mip debug view (the streaming view is `draw/asset-requests`') |
| `render-scene:72` | feature | use | The visible materials and textures each frame publishes |
| `render-scene:151` | feature | use | The GPU's port of the texture streaming measure |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Mip chains and texture formats | `assets/textures` | must |
| The cooked texture's layout and `GetMipByteSize` | `assets/texture-cooking` | must |
| Budgets, eviction and pins | `assets/residency` | must |
| Budgeted uploads and `Texture::UploadLevels` | `assets/uploads` | must |
| Bindless slots and the texture table | `gpu/binding` | must |
| What renderers publish each frame | `draw/asset-requests` | must |
| Visibility feedback | `draw/gpu-driven` | must |
| Logarithms in base 2 | `basics/numbers` | must |
| Loading without stalling: the streaming queue | `assets/loading` | must |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `fade-in` | Fade-in | - |
| `mip-streaming` | Mip streaming | - |
| `mip-tail` | Mip tail | - |
| `partial-load` | Partial load | prefix |
| `range-read` | Range read | - |
| `texel-density-draw` | Texel density (draw) | `UVPixels` |
| `wanted-level` | Wanted level | - |
