# Brief: `assets/textures`

| Field | Value |
| --- | --- |
| Title | Textures for the GPU: mips, color spaces, block compression |
| Kind | C |
| Size | M |
| Tracks | E |
| Needs | `basics/color`, `basics/signals`, `gpu/how-a-gpu-frame-works` |
| From | assets ch. 4 (the general problem and the formats); L→M |
| Unit | `plan/allocation/assets.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `assets/textures` — Textures for the GPU: mips, color spaces, block compression

**Covers.** The problem as the reader meets it: one 4096 by 4096 photo stored as RGBA8 holds 64 MiB, its mips add a
third, and a scene has hundreds of textures; far away the texture shimmers; a normal map imported as a color looks
wrong. The naive answer, RGBA8 at full size sampled at level 0, breaks on memory, on bandwidth and on aliasing. The idea
comes in three short parts, because `basics/signals` and `basics/color` teach the mathematics: mips as prefiltered
levels for a third more memory; color spaces in textures (sRGB color, filtered in linear space; linear data such as
roughness; HDR values above 1, in RGBA16F); and block compression, which stores 4x4 texels in 8 or 16 bytes at a fixed
rate, so the GPU can read any block directly. The approaches follow: uncompressed, the BC family on desktops, ASTC and
ETC on phones, and transcoding at load time (Basis Universal), with a table of bits per texel, quality, encoding cost
and who uses each.

A BC1 block is opened up (figure 478): two endpoints and a 2-bit index per texel, so the colors of one block lie on one
line through RGB space. That is why data with independent channels needs BC7, and why normal maps use BC5 (X and Y in
two channels, Z rebuilt from them). BC7's own parts are named here and taught with the encoder. Strata's choice is one
table: color BC7 (BC1 for opaque color at Fast), normal maps BC5, one-channel data BC4, other data BC7, HDR RGBA16F,
and uncompressed formats when asked; the code is `assets/texture-cooking`'s. What the choice cannot do: there is no
BC6H, so an HDR texture takes 8 bytes a texel, and there are no phone formats, because Strata runs on desktops only.
Common mistakes: sizes computed from bytes per pixel, a normal map imported as Color, the green channel of DirectX
normal maps against OpenGL ones. Figure 498 shows one texture as Color, NormalMap and Data, and at High against Fast.
Exercises: the stored size of a 4096 by 4096 texture with its mips worked out by hand as RGBA8, BC1, BC7 and RGBA16F,
then compared with the cache files that imports at those settings write; one normal map imported as Color and as
NormalMap and compared in the Scene view; four colors of one block that do not lie on a line, and what BC1 gives up for
them. At the end the reader can choose the usage and quality of any texture and say what each choice costs.

**Leaves out.**

- How Strata's importer chooses formats, cooks mips and encodes BC7 → `assets/texture-cooking`
- Sampling, aliasing and prefiltering as mathematics → `basics/signals`
- The sRGB transfer function and the half-float range → `basics/color`
- Normal maps in tangent space, and how the shader reads them → `light/materials`, `light/material-data`
- Loading only some of a texture's levels → `draw/mip-streaming`
- Import settings as a game maker uses them → `make/assets`, `make/materials`

**Fit.** `fits`: about 3,800 words against M (3,000). The idea in three short parts, the BC1 block of figure 478 and the
table of formats take the most words, then the three exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `assets:273` | concept | home | Texture data for GPUs: mips, color spaces, block compression; the BC family; why data needs BC7 |
| `assets:478` | figure | home | BC block anatomy: a 4x4 block, BC1's endpoints and indices, why data channels fail in BC1 |
| `assets:498` | figure | home | One texture at Usage Color, NormalMap and Data, and at High against Fast, zoomed |
| `assets:702` | term | home | Mip, mip level, mip chain |
| `assets:710` | term | home | Block compression (BC1-BC7) |
| `assets:713-715` | term | home | Linear data, normal map, HDR (RGBA16F) |
| `render-image:682` | term | home | Mip chain and pyramid (the bloom's pyramid links here) |
| `new:27` | hands-on | home | Exercises (D27): the stored size of a 4096 by 4096 texture with its mips worked out by hand as RGBA8, BC1, BC7 and RGBA16F, then compared with the cache files that imports at those settings write (done); one normal map imported as Color and as NormalMap and compared in the Scene view (editor task); four colors of one block that do not lie on a line, and what BC1 gives up for them (design). Evidence: `Strata/src/Strata/Renderer/TextureFormat.cpp:53-65` (`GetMipByteSize`); `Strata/src/Strata/Asset/EditorAssetManager.cpp:707` (the cache file `<handle>.bin`) |
| `assets:154` | feature | use | Strata's format per usage, as a table (the code is `assets/texture-cooking`'s) |
| `assets:165` | feature | use | Normal maps read as X and Y with Z rebuilt, in one sentence (taught in `light/material-data`) |
| `assets:547` | rule | use | Sizes come from `GetMipByteSize` (the box is `assets/texture-cooking`'s) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Sampling, aliasing and mip prefiltering | `basics/signals` | must |
| Linear and sRGB values, the sRGB transfer function, the half-float range | `basics/color` | must |
| Textures, texels, sampling and filtering on a GPU; memory bandwidth | `gpu/how-a-gpu-frame-works` | must |
| Bits, bytes, and numbers packed into bits | `basics/numbers` | must |
| Vectors: length and normalizing | `basics/math-vectors` | must |
| What an asset and a stored form are | `assets/what-is-an-asset` | helps |
| Normal maps as directions in tangent space | `light/materials` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `block-compression-bc1-bc7` | Block compression (BC1-BC7) | - |
| `hdr-rgba16f` | HDR (RGBA16F) | - |
| `linear-data` | Linear data | - |
| `mip` | Mip | mip level |
| `mip-chain` | Mip chain | - |
| `normal-map` | Normal map | - |
