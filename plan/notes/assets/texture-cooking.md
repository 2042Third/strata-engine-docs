# Notes: `assets/texture-cooking`

## New terms

None proposed. The page defines the four terms the glossary homes here (`STTX`, Mitchell filter, alpha weighting, endpoints) in bold. P-bits and modes (aliases of endpoints) are explained in plain words in the paragraphs after the definition; "box filter" (an alias of Mitchell filter) is plain text in the HDR section.

## Requests

- Extra words for `tools/data/extra-words.txt`: `encoder` (18 uses: the BC7 encoder is the page's subject, and the page title carries it), `PSNR` (peak signal-to-noise ratio, expanded at its first use) and `DirectX` (a product name for `names.txt`). Their `word-list` findings are left until the words exist.
- Figure `sttx-layout` (`src/content/figures/assets/texture-cooking.json`, kind diagram): a row of boxes: header (40 bytes), mip table (24 bytes a level, largest first), name, padding, then the levels smallest first, each at a multiple of 16 bytes, with a bracket over the header and the smallest levels marking the first read. No layout file needed.
- External hosts: none linked. Further reading names the Khronos Data Format Specification, the ISPC Texture Compressor, bc7enc, Compressonator, the NVIDIA Texture Tools, Basis Universal, KTX 2 and Strang's book without links.

## Since

`since: 0.3.0`. `Strata/src/Strata/Asset/BC7Encoder.cpp` was added by `aca98838` ("Encode BC7 with Strata's own encoder") and the `STTX` version 2 layout with the cooker by `a5999d7f` ("Cook textures to BC formats with a mip-tail-first layout"); the tag `v0.3.0` contains both. `RemoveSun` (0.6.0) and `FlipGreen` (importer version 5) came later but are details of the page's subject.

## Not verified

- The Further reading entries (Khronos specification, the encoder projects, Basis Universal, KTX 2, NVIDIA Texture Tools, Mitchell and Netravali) and the alternatives table's "who uses it" column are general knowledge; no source was opened. The table's column names no product.
- Exercise 4 predicts that `Fast` finishes sooner and may show banding; the page says "expect" and "may" and gives no measured time.
- "Strata cooks once, in the editor" follows from the cooked form living in the import cache and packs (`CookedTexture.h` header comment); the call path of the editor's background import was not traced.
- The line numbers of callouts follow the quotes as `excerpts fill` wrote them at the pin.

## Findings not applied

The brief lists no open findings. Items of the brief not carried: the usage-warning message's exact text is not quoted (the page names `FindTextureUsageMismatches` and the fix command); the render-core flag's source lines (`Renderer.cpp:165`) were replaced by `Texture::IsBlockCompressionSupported` in `Texture.cpp`, which the loader in `RendererRegistration.cpp` calls.

## Clerk

- Admitted to extra-words.txt: PSNR (expanded at its first use). DirectX entered names.txt; encoder was already in extra-words.txt.
- Left for the planner: figure `sttx-layout`.
- Page fix: the :::derivation lost its label, which the build's rules refuse.
