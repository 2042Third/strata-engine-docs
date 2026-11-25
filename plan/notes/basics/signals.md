# Notes: `basics/signals`

## New terms

- **moiré**: false, wide stripes that appear when a fine regular pattern is sampled too coarsely. Home:
  `basics/signals`. Aliases: moire.

The page also defines the glossary's entries of its brief in bold: signal, signal sample, frequency, sampling, sample
rate, Nyquist limit, aliasing, filtering, filter kernel, convolution, dithering, ordered dither, prefiltering (as
"Prefiltering" in its section's first paragraph), denoising and spatial denoising. Bilinear filtering is bold too, as
the interpolation page's term. Mip, the Mitchell filter and the nearest and linear reads are plain text.

## Requests

- `tools/data/names.txt`: "Gaussian" (the bell-shaped kernel; the brief names it). Its word-list finding is left until
  then.
- Figures: four diagram requests in `src/content/figures/basics/signals.json` (a sine sampled above and below the
  limit; one spike under three kernels; a floor with and without mips; a gradient quantized, dithered with noise and
  dithered with the Bayer table). None is drawn yet. The Bayer table itself stands as a table on the page.
- Further reading cites three sources without a link: Mitchell and Netravali (SIGGRAPH 1988), "Physically Based
  Rendering" (its host is not on `tools/external-hosts.txt`), and Julius O. Smith's online book (host `ccrma.stanford.edu`).
- Passive and noun-stack warnings (21) are left: most are adjectives of the form "is sampled" or the names of the
  quantities ("relative depth difference").

## Not verified

- The Mitchell filter's reach (two output pixels each side) and its small negative lobes are general knowledge of the
  filter, not read in the vendored `stb_image_resize2` code.
- That `STBIR_TYPE_UINT8_SRGB` averages in linear values is taken from the importer's header comment
  (`Strata/src/Strata/Asset/TextureImporter.h`) and the name; the vendor code was not read.
- That the graphics card picks the mip level from the texels one pixel spans is general behavior; Strata's sampler
  settings were not checked (they belong to `assets/textures`).
- That Coin Run's coin script resembles the engine's `Spinner` (`StrataEditor/src/Editor/ScriptProject.cpp`): the Coin
  Run end state is not at the pin, so Practice 6 says only "find the script that turns the coins".
- The 16-rotation remark about the ambient occlusion denoiser comes from the shader's own comment
  (`Strata/shaders/Effects/AODenoise.comp.slang`), not from running it.
- That the two passes of the fade draw the same pixels is the comment of `IsLODFadeDrawn` in
  `Strata/shaders/Include/Scene.slang`; the passes were not read.
- Hearing up to about 20,000 Hz and the 24 pictures a second of film are general knowledge.

## Findings not applied

- critic-basics-b-4: applied. The first shader quote (the Bayer table) is introduced by the Slang types and operators that
  differ from C++ (`uint`, `uint2`, the `u` suffix, `& 3u`), and the second (the occlusion denoiser) by `float4`,
  `int2` and `exp`; each is followed by numbered line-by-line callouts. The page has no `float3x3`, `mul`, swizzle,
  `frac`, `select` or `reversebits`, so it does not explain them.
- The brief's item `render-image:677` (TPDF dither) is only linked to `image/encoding`: the page teaches dither's idea,
  not the triangular noise.
- The brief's figure "the Bayer table itself" is a table in the text, not a figure.

## Clerk

- Admitted: moiré (alias moire). `names.txt`: "Gaussian". `external-hosts.txt`: `ccrma.stanford.edu`, `pbr-book.org` (front pages fetched).

## Track walk E-final-4

Each sketch of the page compiled with `cl /std:c++20 /EHsc` (Visual Studio 2026, 19.50) and with g++ 15 `-std=c++20`, glm from the 0.8.0 package's `StrataScriptCore/ThirdParty/glm`; both printed the same output (`docs-work/walkfix-E4/cl/`, 2026-11-24). The exact Windows line of the page was run in PowerShell in a Visual Studio developer environment (`cmdtest/`).

In Checkpoint 4 of `make/project-coin-run` the coins turn with `Coin` (`Scripts/Coin.cpp`).
