# Notes: draw/mip-streaming

## New terms

None proposed. The page defines the seven glossary terms of its brief in bold: mip streaming, mip tail, texel density, partial load, range read, wanted level, fade-in.

## Since

0.3.0: partial loads, range reads and the texture streamer landed in wave 3 (inventory assets lines 187 to 193, "wave 3, 0.3.0"); the 30 s idle drop came in 0.4.0.

## Requests

- Figures waiting for a later edition (stand-ins placed at this pin, see Figures): `mip-view-flying` (tier 3, a moving camera), `mip-view-settled` (Mip debug view, Showcase), `tail-and-level-zero` (tier 2: renderer switches; needs a way to hold a texture at its tail and to show it whole), `fade-in-frames` (tier 3).
- Host for Further reading: the Unreal Engine documentation, the Unity manual, Sean Barrett's talk and the DirectX 12 specifications are cited without links.

## Figures

- `mip-view-settled`: published (round 1, scene camera, Mip view). All 140 drawn entities are at shortfall 0 (`entitiesPerMipShortfall` [140, 0, 0, 0]): bus, tank and ground green. The bus's underside and wheel hubs stay brown because the view does not tint entities without textures; the alt says so.
- `mip-view-settled` at v0.8.0 (pin 319075e3): taken again and compared with the published file (1 pixel off by 1 level); the published picture stays, checked at the new pin. All drawn entities green, 140 tinted, 0 short of levels.
- `tail-and-level-zero`: v0.8.0 has the renderer switches, so the old `waitsFor` went; the recipe now frames the fire pit from 2.6 m (camera at (-13.4, 1.5, -12.4) toward (-15, 0.25, -14), fov 30, FXAA), where the stones and the cracked ground show the 1k textures' detail plainly. Round 1: the tail variant with `waitForAssets` false and `expectAlso /texturesBelowWanted min 1` came back complete with `texturesBelowWanted` 0 after 2 waited frames: the streamer raised the levels within the capture, so the picture showed level 0, the same as the level-zero variant. The switch `TextureStreaming` false only makes everything whole (the level-zero side), and figures.py passes no `renderer` to the capture anyway. Nothing in the pin holds a near texture at its tail, so the figure waits for a tier 3 addition (a capture that draws textures from their resident tails); not published. The level-zero side is ready (complete, the fire pit sharp). Nearest honest picture meanwhile: a diagram of a level chain with the resident tail marked beside level 0.
- `mip-view-flying` (tier 3, a camera in motion) and `fade-in-frames` (tier 3, a running fade): wait for those engine additions; not taken. Nearest honest picture for the page meanwhile: the settled view alone.
- Final pin (v0.8.0), last round: no take can make the three waiting figures. The capture's renderer switches (dumped schema of 319075e3) hold no texture at its tail (`TextureStreaming` false makes every texture whole), and no capture shows a moving camera or a running fade. Their `waitsFor` stays as the request for a later edition.
  - `tail-and-level-zero`: stand-in `tail-levels`, a drawing of a 2048 texture's 12 levels with levels 0 to 5 as the streamed ones, levels 6 to 11 as the mip tail and level 6 marked as what a first load draws from (`Texture::c_ResidentTailDimension` 32). The sentence before it now introduces the chain.
  - `fade-in-frames`: stand-in `fade-in-lod`, a graph of the finest level sampled during a raise from level 4 to level 2: the fade starts at the levels gained and falls linearly with the clock over 0.25 s (`TextureTable::SetFadeIn`, `UpdateFades`). The old caption said the surface sharpens "in steps"; the pin's fade is linear, so the waiting entry's caption now says it sharpens a little in each frame.
  - `mip-view-flying`: no stand-in (`noStandIn`): the paragraph names the tints of a flight, and the settled picture that follows shows the view itself; its lead-in now introduces the settled picture.

## Not verified

- The order of steps inside `Texture::ContinueLevelChange` (new GPU texture, GPU copy, upload, slot swap) is taken from the comments of `TextureStreamer.h`, not read in `Texture.cpp`.
- That `TextureTableTests.cpp` and `GPUTextureStreamingTests.cpp` run only on a machine with the shared device is taken from the AGENTS label rules, not from the CMake files.
- That Unreal and Unity stream mips by screen size and a pool is general knowledge, cited by Further reading only.
- The exercise's one byte per texel is an assumption stated in the exercise, not Strata's format.

## Findings not applied

The brief lists no open findings.

## Clerk

- Nothing to admit; no host was asked with a front page.
