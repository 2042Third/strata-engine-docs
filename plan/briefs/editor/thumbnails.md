# Brief: `editor/thumbnails`

| Field | Value |
| --- | --- |
| Title | Thumbnails |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `editor/projects`, `gpu/frame-tour`, `gpu/readback-timing`, `assets/residency` |
| From | editor-core ch. 15 (caches keyed by content, offscreen rendering, readback without stalls, `ThumbnailCache::c_Version`, project pictures) |
| Unit | `plan/allocation/editor.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor/thumbnails` — Thumbnails

**Covers.** The problem: the Content Browser shows hundreds of assets as pictures; rendering each costs GPU time,
rendering them again at every start or edit wastes it, and a picture that no longer matches its asset misleads. The
idea: a cache keyed by content, whose key hashes the content stamps of the asset and of everything it depends on
together with a version of how the pictures are made; pictures rendered offscreen one at a time; pixels read back
without stalling a frame. The content stamp (`EditorAssetManager::GetContentStamp`) is `assets/importing`'s, and the
page links it: here it is what the key hashes. Strata's code: `ThumbnailCache` (textures from the levels of their mip
tail, read by byte range so that a thumbnail never loads a whole chain; materials on a sphere and meshes, models and
prefabs framed, rendered under the preview lighting by an offscreen `SceneRenderer` and read back with
`TextureReadback`; PNG files in the cache directory named by the key; `c_Version`, bumped when thumbnails would look
different; `Request` every frame for what is on screen only; large previews for the Asset tab, kept in memory);
`DisplayImage`, the RGBA8 textures of display colors the UI draws as they are; and `ProjectThumbnail`, the launcher's
picture taken after each scene save, rendered at three times 480x270 and averaged down once loads, exposure and TAA have
settled. The rule: bump `ThumbnailCache::c_Version` when thumbnails would look different. The example edits and saves a
material, watches its key change and its thumbnail render again, then restarts the editor and sees it read from its
file; the trace exercise stops in `ComputeKey` during that save. Afterwards the reader can add a kind of asset preview
that never stalls a frame and is never stale.

**Leaves out.**

- The content stamp, how it is built and what it lasts across → `assets/importing`
- Thumbnails drawn in the Content Browser's tiles → `editor-ui/lists`
- Readback and GPU timing → `gpu/readback-timing`
- The preview lighting → `light/lights`
- The launcher's cards → `editor-ui/launcher-dialogs`

**Fit.** `over`: about 4,200 words against M (3,000). Counted again from the sections, after the content stamp left for
`assets/importing` and with the trace exercise: one concept, the two cached kinds of picture, three excerpts and the
shape of an internals page pass M's top; the next size is L (5,000) (S2).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:370` | concept | home | Caches keyed by content; a version for how pictures are made; readback without stalls |
| `editor-core:256-257` | feature | home | `ThumbnailCache` and `ProjectThumbnail` |
| `new:41` | feature | home | `DisplayImage`: RGBA8 textures of display colors that the editor's UI draws as they are (thumbnails). Evidence: `StrataEditor/src/Editor/DisplayImage.h:11-20` |
| `new:42` | code | home | `StrataEditor/src/Editor/ThumbnailCache.cpp:1127-1134`: `ComputeKey`, the version and the content stamps of the dependency closure |
| `new:43` | code | home | `StrataEditor/src/Editor/ThumbnailCache.cpp:763-894`: `UpdateSceneJob`, one offscreen picture at a time, read back when ready |
| `new:44` | code | home | `StrataEditor/src/Editor/ProjectThumbnail.h:16-88`: the launcher's picture and what it waits for |
| `editor-core:533` | figure | home | The launcher's project cards and the Content Browser's thumbnails |
| `worlds-runtime:180` | feature | home | Project thumbnails, as the worlds survey lists them |
| `assets:145` | feature | use | The content stamp, homed on `assets/importing`: the thumbnail cache's key hashes the stamps of an asset's dependency closure |
| `assets:216` | feature | home | Thumbnails read a texture's cooked header and mip tail by byte range |
| `editor-core:593` | rule | home | Bump `ThumbnailCache::c_Version` when thumbnails would look different |
| `new:64` | hands-on | home | Trace it yourself (D27): edit and save a material with a breakpoint in `ThumbnailCache::ComputeKey`, see its key change through the content stamp of the material or of a texture it uses, then follow `UpdateSceneJob` as it renders the picture again and reads it back. Evidence: `StrataEditor/src/Editor/ThumbnailCache.cpp:1127-1134`, `:763-894` |
| `editor-core:735` | term | home | Thumbnail cache |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| A frame of the scene renderer | `gpu/frame-tour` | must |
| Readback without stalls | `gpu/readback-timing` | must |
| Residency: requests every frame, reads of a mip tail | `assets/residency` | must |
| Dependency closures | `assets/references` | must |
| Importing, cached imports and the content stamp | `assets/importing` | must |
| The preview lighting | `light/lights` | helps |
| TAA and its settling | `image/taa` | helps |
| Display colors and RGBA8 | `basics/color` | helps |
| Projects and their saves | `editor/projects` | must |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `thumbnail-cache` | Thumbnail cache | - |
