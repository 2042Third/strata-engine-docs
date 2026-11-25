# Notes: assets/textures

## New terms

None proposed. The page defines the six glossary terms (block compression, HDR (RGBA16F), linear data, mip, mip chain, normal map). It also defines in bold, without proposing them: Usage, endpoint, mode, partition, p-bit, Quality, Compression.

## Since

0.3.0: textures have been a stored GPU form since the first tag's asset pipeline; the block formats came with texture cooking v2 (inventory assets:154, "cook v2 wave 2"). Evidence not checked against the first tag.

## Requests

- Words for `tools/data/extra-words.txt`: bandwidth (memory bandwidth), encoder, endpoint (of a block's color line).
- Name for `tools/data/names.txt`: DirectX.
- Host for `tools/external-hosts.txt`: registry.khronos.org (Khronos Data Format Specification, Further reading, not linked).
- Figure `usage-compare` (kind scene, variants normal-map and color, Showcase sample): the asset path `Assets/Generated/Props/WeatheredSteel_nor_gl.png` and a camera on a surface that uses it are a guess; the planner must choose the shot (a material that uses that normal map). The High against Fast zoom of brief item assets:498 is not drawn.
- No layout needed.

## Figures

- `usage-compare` (published, both variants). Round 1: the setup's asset path `Assets/Generated/...` was refused (paths
  are relative to `Assets/`); fixed to `Generated/Props/WeatheredSteel_nor_gl.png`. The shot is the Showcase's oil tank
  (`OilTank` at 2.7, 0.09, 17.2, radius 4 m; its shell uses WeatheredSteel, the only material with this normal map),
  seen from +X with the Golden sun raking across it. Round 2: auto exposure brightened the Color variant by about a stop
  (sky and sand washed out), so the pair differed outside the tank; exposure is now fixed at -13.8 (the auto value of
  the NormalMap variant, ev100 13.28). Two captures then differed in 2 to 3 pixels at a ground disc by the tank's right
  edge (nondeterministic); round 3 framed closer and turned toward the lit side, excluding it, and both took cleanly.
  What it shows: NormalMap gives a broad, wave-broken sun sheen on the left half; Color loses the sheen, the left half
  turns dull brown and the half turned from the sun nearly black. Caption, alt and shows rewritten to say so (the
  writer's "one tilted slope without the bumps" was not what the engine draws: the fine relief stays visible as color).
  Mend (viewer's report): in the NormalMap shot the right half's rust is as bright as the left's, so that half is lit,
  not turned from the sun; the caption now says the sheen left of centre is gone, the rust turns dull brown and the
  right half goes almost black. The pictures stand (no retake). The caption and alt now say which picture is which
  ("in the first picture as a normal map (Usage NormalMap), in the second as color (Usage Color)") and name the Usage
  values, since they come before the page defines Usage. Left for the writer (page text): the two
  `::figure{id=usage-compare variant=…}` lines repeat one caption under each picture and carry no label of their own
  (the plugin reads only the recipe's caption and alt); `::compare{id=usage-compare}` would label the sides, and moving
  the figures below the Usage paragraph (line 89) would let the reader know the word first.
- `usage-compare` at v0.8.0 (319075e3), round 1: taken again with the recipe unchanged; both variants complete, and
  `figures.py compare` finds no pixel that differs from the published originals (0 of 2 differ). Looked at both: the
  NormalMap shot shows the broad sheen left of centre and bright orange rust over the whole tank; the Color shot loses
  the sheen, the rust is dull brown and the right half nearly black, as the caption says. The PNGs have the stamps'
  SHA-256, so publish left the pictures and `taken.json` as they were (stamp pin 822a7a46, pixels the same at 319075e3).

## Not verified

- That the cache file `.bin` holds the cooked texture without extra compression (only its name and the header layout were read).
- The BC7 mode details (partitions, p-bits, separate channel) are stated at the level of `Strata/src/Strata/Renderer/BC7Format.h`'s fields, not decoded further.
- Claims about ASTC (128-bit blocks, 4x4 to 12x12), ETC2 (4 or 8 bits) and Basis Universal are general knowledge of those formats, not Strata facts; sources named in Further reading without links.
- The editor panel names for changing a texture's usage: the page names the command `asset.setImportSettings` only.

## Findings not applied

None: the brief lists no open findings.

## Clerk

- Added the alias endpoint to the term endpoints, homed on assets/texture-cooking (its definition kept). Admitted to names.txt: DirectX. bandwidth is already a term (gpu/how-a-gpu-frame-works), encoder already in extra-words.txt, registry.khronos.org already a host.
- Left for the planner: the shot of figure `usage-compare`.
