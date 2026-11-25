# Brief: `gpu/text`

| Field | Value |
| --- | --- |
| Title | Text: fonts, shaping and signed distance fields |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `gpu/debug-drawing`, `basics/bytes` |
| From | render-core; gameui "Text in the UI" (the rendering half); home of fonts, `ShapeText` layout, the atlas and signed distance fields, and of font validation (`FontValidation`; untrusted input in general is `assets/robustness`') |
| Unit | `plan/allocation/gpu.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `gpu/text` — Text: fonts, shaping and signed distance fields

**Covers.** The job: turn a font file and a UTF-8 string into glyphs that stay sharp at any size, without trusting the
file and without stalling a frame. The problem and the approaches: bitmap atlases per size, SDF and MSDF atlases, vector
rendering, shaping libraries; Strata's choice: single-channel signed distance fields at 32 texels per em, atlases filled
on demand with LRU eviction and raster budgets, simple shaping (advances, kerning, wrapping, ellipsis), and measuring
kept apart from rasterizing. The map is the font pipeline, from bytes to quads. The contract: font files are untrusted
input (extend `FontValidation`, with crafted-font tests, before calling another stb_truetype function; bound time as
well as reads); text is measured with `ShapeText`, never by rasterizing; passes share the renderer's `FontAtlasCache`.
The toy computes a glyph's distance field from a bitmap by brute force, then shapes one line by advances.

The real code: the `Font` asset (TrueType, the first font of a collection, Roboto Medium embedded as the default);
validation (every table stb_truetype reads, outlines and composites bounded, kerning switched off when unbounded, CFF
rejected, the cmap format 4 search corrected); `FontFace` (metrics without rasterizing, caches bounded at 4,096);
`ShapeText`, `LayoutText`, `MeasureCaretStops` and `DecodeUTF8`; `FontAtlas` (512x512 pages of 42-texel cells, up to 8
pages, LRU that never evicts this frame's glyphs, uploads in bands of 64 rows, cheaper resolution for costly glyphs);
`FontAtlasCache`, shared with the game UI; `TextRenderer` (`TextComponent` on the entity's XY plane, depth-tested, or on
the screen over everything; 32 glyphs and 512 Ki of cost a frame); the shader's coverage, a smoothstep over about one
screen pixel from `fwidth`, taken before the discard. Figures: world and screen text, a magnified glyph, an atlas page.
What Strata does not do: complex scripts and CFF fonts. Alternatives, tests (font, atlas, layout and text GPU suites),
changing safely; the exercise crafts a font whose `loca` points past `glyf`, and a second traces one glyph from
`ShapeText` to its atlas cell. Code point is said in one sentence and linked to `basics/bytes`, its home.

**Leaves out.**

- How rects, sizes and overflow modes drive `ShapeText` in game UI, and text fields → `ui/text`
- Drawing the game UI's glyph quads → `ui/drawing`
- `TextComponent` for game makers: signs and HUD text → `make/hud`
- The editor's fonts, which use ImGui's own atlas → `editor-ui/design-system`
- Untrusted input in general: checksums and bounded sizes → `assets/robustness`
- Localization and right-to-left text → `ui/text`

**Fit.** `fits`: about 5,600 words against L (5,000). Eight features with three excerpts, the validation contract and
two exercises take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-core:425` | concept | home | Fonts, shaping, glyph atlases and SDFs; Strata's choices; the mistake of measuring text by rasterizing it |
| `render-core:430` | concept | home | Untrusted input in the renderer: font files and stb_truetype, which checks no bounds |
| `render-core:232-239` | feature | home | `Font`; font validation; `FontFace`; `ShapeText` and its siblings; `FontAtlas`; `FontAtlasCache`; `TextRenderer`; SDF coverage in the shader |
| `new:23` | code | home | `Strata/src/Strata/Renderer/TextLayout.h:50-112`: `TextShapeOptions`, `ShapedText` and `ShapeText`: layout from metrics alone |
| `render-core:474` | code | home | `Strata/src/Strata/Renderer/FontValidation.h:63-72`: what is verified before stb_truetype reads a byte, with the CFF refusal at `Strata/src/Strata/Renderer/FontValidation.cpp:131-132` |
| `render-core:473` | code | home | `Strata/shaders/Include/SDFText.slang:4-15`, with `Strata/shaders/Overlay/Text.frag.slang:17-26`: coverage from `fwidth`, the derivative before the discard |
| `new:24` | not-done | home | No complex-script shaping and no fonts with CFF outlines: shaping is advances, kerning and line breaks. Evidence: `Strata/src/Strata/Renderer/FontValidation.cpp:131-132`; `Strata/src/Strata/Renderer/TextLayout.h:109-112`; render-core inventory, concept 30 |
| `render-core:513` | figure | home | The font pipeline |
| `render-core:536` | figure | home | World and screen text; a magnified SDF glyph; an atlas page from `FontAtlas::GetPagePixels` |
| `render-core:613` | rule | home | Font files are untrusted: extend `FontValidation` first; bound time as well as reads |
| `render-core:615` | rule | home | Measure with `ShapeText`; passes share the `FontAtlasCache` |
| `render-core:651` | hands-on | home | The font validation exercise |
| `new:51` | hands-on | home | Exercise ("trace it yourself"): one glyph from `ShapeText` to its atlas cell on the source build: a sign whose text holds a glyph not yet in the atlas, a breakpoint in `FontAtlas::Rasterize`, the cells allocated and the page it lands in, and the frame its rows upload in. Evidence: `Strata/src/Strata/Renderer/FontAtlas.cpp:81, 103-116, 147, 342`; `Strata/src/Strata/Renderer/TextLayout.h:109-112` |
| `render-core:762-769` | term | home | Font and glyph (code point, which the item also names, is linked to `basics/bytes`, its home: duplicates.md, "Code point"); TrueType, CFF and OTTO; stb_truetype; kerning and GPOS; text shaping; SDF; glyph atlas, page and cell; LRU eviction |
| `render-core:247` | feature | use | `TextComponent`, which the renderer registers |
| `gameui:303` | concept | home | Shaping against rasterizing and distance-field fonts, the same subject as `render-core:425`; `ui/text` and `ui/drawing` use it |
| `gameui:645` | term | home | Glyph, advance, kerning, baseline and em; one entry with `render-core:762` and `render-core:765` |
| `editor-ui:716` | term | home | Font atlas, as the editor's UI words it; one entry with `render-core:768`; the editor's own atlas is ImGui's, which `editor-ui/design-system` says |
| `gameui:115` | feature | link | The game UI shaping its texts from font metrics |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Overlays and their order | `gpu/debug-drawing` | must |
| Bytes, text encodings and UTF-8 | `basics/bytes` | must |
| Derivatives and discard in shaders | `gpu/shaders` | must |
| Texture arrays and binding sets | `gpu/binding` | must |
| Hash maps and caches | `basics/data-structures` | must |
| Budgeted uploads | `gpu/upload-queue` | helps |
| Untrusted input in general | `assets/robustness` | helps |
| Text in game UI | `ui/text` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `advance` | advance | - |
| `baseline-gpu` | baseline (gpu) | - |
| `cell-gpu` | cell (gpu) | - |
| `em` | em | - |
| `font` | Font | - |
| `glyph` | glyph | - |
| `glyph-atlas` | Glyph atlas | Font atlas |
| `gpos` | GPOS | - |
| `kerning` | Kerning | - |
| `lru-eviction` | LRU eviction | - |
| `page` | page | - |
| `signed-distance-field` | Signed distance field | SDF |
| `stb-truetype` | stb_truetype | - |
| `text-shaping` | Text shaping | - |
| `truetype` | TrueType | CFF, OTTO |
