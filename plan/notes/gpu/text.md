# Notes: gpu/text

## New terms

None beyond the glossary's homes: glyph, font, signed distance field, em, text shaping, glyph atlas, page, cell, advance, kerning, baseline, TrueType, stb_truetype, GPOS and LRU eviction are defined in bold on the page.

## Requests

- Extra words: rasterize, rasterized, rasterizes, rasterizing, rasterizer, rasterization (the page's central verb), emoji.
- Names: Roboto, OpenType, FreeType, HarfBuzz, TextMesh, msdfgen, MSDF, Indic.
- Figures not drawn: world and screen text (a sign and the Tetris HUD), a magnified glyph, an atlas page from `FontAtlas::GetPagePixels`. The page has only its Mermaid map.
- Hosts for Further reading: none linked (the entries cite sources without links).

## Since

0.3.0: `TextRenderer`, `Font` and `FontAtlas` are listed in the render-core inventory as 0.3.0.

## Not verified

- The order of the three allocation steps (free cells, new page, evict) rests on the comment of `FontAtlas::Allocate`; only the free-cell search was read.
- The claims about other engines in the alternatives table (Slate, Godot, TextMesh Pro, Slug, browsers) come from general knowledge and the cited papers, not from the pin.
- The sizes of the glyph in the worked example (37 by 40 texels) are invented, and the page says so ("say").

## Findings not applied

The brief lists no open findings.

## Clerk

- Admitted to names.txt: Roboto, OpenType, FreeType, HarfBuzz, TextMesh, msdfgen, MSDF, Indic; to extra-words.txt: emoji. The rasterize words came in as aliases of the term rasterization (gpu/how-a-gpu-frame-works).
- Left for the planner: the figures not drawn.
