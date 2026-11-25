# Brief: `assets/texture-cooking`

| Field | Value |
| --- | --- |
| Title | Cooking textures: Strata's importer, mips and BC7 encoder |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `assets/importing`, `assets/textures`, `basics/numbers` |
| From | assets §1.8 (the texture importer, defaults from name tokens, `ChooseFormat`, the Mitchell cooker, `BC7Encoder.cpp`, the `HDRSun` setting, STTX v2, `GetMipByteSize`, the BC decode fallback), excerpts 12-15, rules 4, 14, 15; new by split from `assets/textures` (the importer, the cooker and the encoder are internals); what `HDRSun` does is `light/sky`'s |
| Unit | `plan/allocation/assets.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `assets/texture-cooking` — Cooking textures: Strata's importer, mips and BC7 encoder

**Covers.** The job: turn an image file into an `STTX` cooked texture that the GPU samples and the streamer reads by
byte range, as fast as a background job allows and exactly as the settings say. The problem takes one paragraph that
links `assets/textures`. The map: `TextureImporter` (settings, defaults, `Decode`, `ChooseFormat`), `TextureCooker`
(mips), `BC7Encoder`, `HDRSun` (behind the RemoveSun setting), `CookedTexture` (`STTX`), `TextureFormat`
(`GetMipByteSize`) and `BlockCompression` (decoding for devices without BC). The contract: ten settings, four of which
grey out with an inactive reason (Compression and Quality for HDR textures, which stay 16-bit float; Quality also when
the texture is uncompressed or not color, since it only chooses how block compression encodes color; FlipGreen except on
normal maps; RemoveSun except on HDR maps); defaults guessed from tokens of the file name (`_nor`, `_rough`; a `dx`
token turns `FlipGreen` on); the image limits (a longest side of at most 16,384 texels, a larger image scaled down with
its aspect ratio kept and `MaxSize` 0 meaning that limit, at most 15 levels; only Radiance HDR files keep more than 8
bits a channel, so a 16-bit PNG is decoded to 8; a GIF gives its first frame); one format per usage; levels written
smallest first, each 16-byte aligned; sizes only from `GetMipByteSize`; cooked bytes read only through
`ParseCookedTexture`. A change of output bumps the version of `TextureImporter` and of `GltfImporter`, which cooks a
model's images the same way (the rule's box is `assets/importing`'s). A toy of about 50 lines builds a box-filtered mip
chain and a size calculator; the real code then shows where Strata differs.

The real code, in the order data flows: the settings and their defaults (version 5); `ChooseFormat`, with its comment
on why data channels need BC7; `CookLevels`, which encodes a level and then filters the next, holding two levels at a
time (a Mitchell filter, sRGB in linear space, alpha weighting, edges by wrap mode, normal maps renormalized), and the
HDR path (a box filter, values clamped to the half-float range, NaN and negative values dropped); the BC7 encoder (a
block's modes, partitions, endpoints, p-bits and indices; endpoints along the colors' principal axis, least-squares
refits, mode screening; High searches every mode, Fast modes 6 and 5; the page explains the fit itself where the
encoder uses it, in a `:::derivation` box of about 200 words: the mean of the block's colors, their spread along a
direction, the direction of the greatest spread, found by power iterations, as the line the colors are fitted to, and
least squares as the endpoints that bring the indexed colors closest to the texels; the further reading names a source
on least squares and eigenvectors, such as Strang's *Introduction to Linear Algebra*); the RemoveSun setting of HDR
skies (what `HDRSun` finds and paints out is `light/sky`'s); the `STTX` v2 layout (figure 476: header, mip table, name,
then the levels smallest first, so the mip tail is one range after the header; version 1 is still read) and
`ComputeCookedTextureLayout`; `GetMipByteSize` (a 2x2 BC7 level takes one whole 16-byte block); `ParseCookedTexture`;
the decoding of BC data on the loading worker for devices that cannot sample it; and the warning when a texture's usage
disagrees with its material slot. What Strata does not do here: BC6H, and EXR import. Then the alternatives, the tests
(`Asset.TextureImport`, `Asset.HDRSun`, the encoder's tests), and changing it safely (the version bump of two
importers). Exercises: a cooked-texture inspector; Fast against High on a large albedo; trace it yourself: a search
finds where the file name's tokens choose the defaults, then a DirectX normal map is fixed by its name; BC7's PSNR at
High and at Fast.

**Leaves out.**

- The general problem and the families of formats → `assets/textures`
- What `HDRSun` finds in a sky, and Extract Sun → `light/sky`
- How the shader reads normal maps and the grayscale bit → `light/material-data`
- The resident mip tail and the reads of finer levels → `draw/mip-streaming`
- Uploading the levels to the GPU in steps → `assets/uploads`
- The textures inside a glTF model → `assets/models-gltf`

**Fit.** `fits`: about 6,315 words against L (5,000). The BC7 encoder with its derivation box, the stored form with
figure 476, four excerpts and four exercises take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `assets:281` | concept | home | File layout for streaming: the smallest level first, so the tail is one read |
| `assets:153-156` | feature | home | The texture importer (settings, name tokens, version 5), the format choice, the cooker, the BC7 encoder |
| `assets:162-164` | feature | home | `STTX` v2, block sizes, the BC decode fallback |
| `render-core:109` | feature | home | The device's block-compression flag, which sends loaders to the decode fallback |
| `assets:166` | feature | home | Usage warnings with their `asset.setImportSettings` fix |
| `assets:398` | code | home | `Strata/src/Strata/Asset/TextureImporter.cpp:641-666`: `ChooseFormat`, with the comment on data channels |
| `assets:400` | code | home | `Strata/src/Strata/Asset/TextureCooker.cpp:275-309`: `CookLevels`, encode then filter, two levels held |
| `assets:402` | code | home | `Strata/src/Strata/Renderer/TextureFormat.cpp:53-65`: `GetMipByteSize` and `GetBlockRowByteSize`, rounding to whole blocks |
| `assets:404` | code | home | `Strata/src/Strata/Renderer/CookedTexture.cpp:339-360`: `ComputeCookedTextureLayout`, with the format comment of `CookedTexture.h:17-31` |
| `assets:476` | figure | home | The cooked texture layout: header, table, name, levels smallest first, the tail as the first read |
| `assets:547` | rule | home | Texture sizes come from `GetMipByteSize`, never bytes per pixel |
| `assets:550` | rule | home | Read cooked textures through `ParseCookedTexture` |
| `assets:582` | hands-on | home | A cooked-texture inspector: format, levels, offsets, the smallest-first layout |
| `assets:608` | hands-on | home | BC7's PSNR at High and at Fast, in the encoder's tests |
| `assets:615` | hands-on | home | Trace it yourself (D27): a search finds where the file name's tokens choose the defaults (`GetNameTokens`, `GetDefaults`); then a normal map is fixed by its name: tokens, `FlipGreen`, the usage warning |
| `assets:617` | hands-on | home | Fast against High: look, stored size, import time |
| `assets:711` | term | home | Endpoints, indices, partitions, p-bits and modes (BC7) |
| `assets:716-718` | term | home | Mitchell and box filters, alpha weighting, `STTX` |
| `new:2` | not-done | home | No BC6H: HDR textures are stored as RGBA16F. Evidence: `Docs/Releases/0.7.0.md:403`; `Docs/Roadmap.md:1714` |
| `new:3` | not-done | home | No EXR import: the importer reads `.png`, `.jpg`, `.jpeg`, `.tga`, `.bmp`, `.psd`, `.gif` and `.hdr`. Evidence: `Strata/src/Strata/Asset/TextureImporter.cpp:348`; `Docs/Roadmap.md:949` |
| `new:28` | feature | home | The image limits, about 80 words: the longest side is at most 16,384 texels, a larger image is scaled down with its aspect ratio kept, `MaxSize` 0 means this limit, and a cooked texture has at most 15 levels; only Radiance HDR files keep more than 8 bits a channel (a 16-bit PNG is decoded to 8 bits); a GIF imports its first frame. Evidence: `Strata/src/Strata/Asset/TextureImporter.h:59`, `:80`, `:84`; `Strata/src/Strata/Asset/TextureImporter.cpp:111-120`, `:529`, `:575`; `Strata/src/Strata/Renderer/CookedTexture.h:35-36` |
| `assets:526` | rule | use | The version bump of `TextureImporter` and `GltfImporter`, which both cook textures (the rule's box is `assets/importing`'s) |
| `assets:157` | feature | use | What `HDRSun` does, in one sentence (taught in `light/sky`) |
| `assets:165` | feature | use | The grayscale bit and the XY normal decode, named (taught in `light/material-data`) |
| `render-direct:160` | feature | use | Extract Sun and Remove Sun, the lighting side |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Mips, color spaces, block compression and the BC formats | `assets/textures` | must |
| Importers, settings, inactive reasons and versions | `assets/importing` | must |
| Filters and kernels for resampling | `basics/signals` | must |
| The sRGB transfer function; the half-float range | `basics/color` | must |
| Shifts and masks; integer division that rounds up; logarithms | `basics/numbers` | must |
| Vectors, dot products, normalizing | `basics/math-vectors` | must |
| `ParallelFor` and the job system | `core/jobs` | must |
| An HDR sky, and its sun as a light | `light/sky` | helps |
| The resident mip tail, and finer levels read by range | `draw/mip-streaming` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `sttx` | `STTX` | - |
| `alpha-weighting` | Alpha weighting | - |
| `endpoints` | Endpoints | p-bits, modes (BC7) |
| `mitchell-filter` | Mitchell filter | box filter |
