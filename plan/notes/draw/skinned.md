# Notes: draw/skinned

## Since

0.3.0: skin proxies, skinned variants and `HasSkinProxies` (Docs/Releases/0.3.0.md:63); posed bounds and change-driven palettes 0.4.0.

## New terms

None proposed. The page defines **posed bounds** (glossary home), and in passing **bind pose**, **palette**, **skin proxy**, **dual quaternion** and **union** in bold; the first two are homed on `animation/skinning`, the rest are the planner's to keep or drop.

## Requests

- Figure not drawn: the Third-Person robot mid-dance with a limb outside its bind-pose box, drawn and shadowed (`render-scene:444`, `animation:422`). It needs the Dance state set up and a camera on the swung arm; the page has no figures file.
- Further reading names two sources without links (a textbook and a paper); no hosts requested.

## Not verified

- That the Third-Person robot's Dance animation swings an arm outside its bind-pose box: the page says only that it swings its arms the same way.
- The 5,152 vertices of the speed test's character are from the comment of `AnimationPerfTests.cpp`; the 48 bytes of a joint matrix come from the shader's three rows of four floats.

## Findings not applied

- Brief item `render-scene:491` (every influence names a joint of the skin) is stated once in the contract with a link to `animation/skinning` as the brief asks; its home page owns the explanation.
- The brief's Fit note (over by 4,000 words, make it L by S2) is not applied: the page holds 3,491 words, inside M.

## Clerk

- Nothing to admit: bind pose is homed on animation/skinning; palette and union are common words; skin proxy and dual quaternion stay plain bold, the planner's.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
