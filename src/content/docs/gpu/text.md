---
id: gpu/text
title: "Text: fonts, shaping and signed distance fields"
description: "How Strata turns a font file and a UTF-8 string into sharp glyphs at any size, without trusting the file and without stalling a frame."
kind: internals
size: L
tracks: [E]
needs: [gpu/debug-drawing, basics/bytes]
time: 70
learn:
  - id: measure-text
    text: explain why Strata measures text from font metrics and never by rasterizing it
  - id: sdf-values
    text: compute the value a distance-field texel stores and the coverage a pixel gets from it
  - id: atlas-budget
    text: trace one glyph from a string through ShapeText and the budget to its atlas cell and its upload
  - id: validate-font
    text: explain why every byte stb_truetype reads is checked first, and extend the checks for a crafted font
since: 0.3.0
status: final
---

Text has to look right at every size, in every language the font covers, and from a file that anyone can hand to the
engine. Strata turns a font file and a :term[UTF-8]{id=utf-8} string into **glyphs**, the shapes that stand for characters. It measures the
string without drawing anything. It draws the shapes from a texture that fills on demand, and it checks the font file before
any library reads a :term[byte]{id=byte} of it. It does not shape complex scripts, and it does not read fonts with cubic outlines.

## The problem and how engines solve it

A **font** is a file that describes the shape of each character, how far to move after drawing it, and a few numbers about
the lines of text it makes. The :term[graphics processing unit]{id=gpu} (GPU) draws triangles and reads textures; it knows nothing about
letters. Somebody has to turn the outline of a letter into pixels, and do it inside a frame of 16.7 ms.

The first idea is to draw each letter into an image at the size you need. You put the images in one texture and draw a
textured rectangle per letter. The result is exact at that size. Ask for twice the size and the letters turn soft, because
the texture holds too few texels; ask for a smaller size and they shimmer. A game with a menu, a sign in the world and a
subtitle needs a texture for each size, and each texture costs memory and :term[rasterizing]{id=rasterization} time.

Three families of answers exist. The first keeps the image atlas and makes one per size, rebuilt when the size changes. The
second stores something richer than coverage in the texture, so that one texture serves many sizes. The third skips textures
and draws the outlines as curves in a :term[shader]{id=shader}. Each has a price, which the table near the end of the page lists.

Strata takes the second answer in its simplest form. A **signed distance field** (SDF) stores, for each texel, the distance
from that texel to the nearest point of the outline, with a sign that tells inside from outside. A shader reads the distance
and decides coverage. The outline then stays where it belongs when the texture is magnified.

Strata keeps one number per texel, a single channel, and rasterizes each glyph once at 32 texels per em.

An **em** is the font's unit of size: text at a font size of 1 is one em tall, and every measurement on this page is a
fraction of it. A label 32 pixels tall then maps one texel to one pixel, and a title 96 pixels tall still has a clean edge.

A text engine must also decide where each glyph goes. That job is **text shaping**: choosing the glyphs for a string and
their positions. Full shaping handles scripts in which a letter changes form beside its neighbours. Strata does only the
simple part, which a later section describes.

The second problem is trust. A font file is a binary format full of offsets, and the library that reads it, stb_truetype,
follows those offsets without checking them. A game loads fonts from projects and from the internet. Strata therefore
checks the file in full before the library sees it, and a section below shows how.

## The map: from bytes to quads

The font pipeline has two halves with a hard wall between them. The left half needs no GPU and no texture: it reads bytes,
checks them and measures text. The right half rasterizes, places glyphs in a texture and draws.

```mermaid caption="The font pipeline. Square boxes are data and round boxes are code. Everything left of the atlas works without a graphics card." alt="A diagram of the font pipeline from left to right. Font bytes pass validation and become a font asset, which makes a face that holds glyph metrics. The face feeds shaping, which turns a string into glyphs and pen positions, and it feeds the atlas, which rasterizes glyphs under a budget into a texture array. The text renderer joins the shaped glyphs and the atlas into quads and draws them with a shader."
flowchart LR
	bytes["Font bytes, not trusted"] --> val(["Validation"])
	val --> font["Font asset"]
	font --> face["Face: metrics, no pixels"]
	face --> shape(["ShapeText: glyphs and pens"])
	text["UTF-8 string"] --> shape
	face --> atlas(["Atlas: rasterize and place"])
	shape --> resolve(["Resolve: quads"])
	atlas --> resolve
	atlas --> tex["Texture array, one layer per page"]
	resolve --> draw(["Text renderer and shader"])
	tex --> draw
```

Each box has one owner.

- `Strata/src/Strata/Renderer/FontValidation.cpp` owns validation.
- `Font` in `Strata/src/Strata/Renderer/Font.h` owns the checked bytes and makes its face on first use.
- `FontFace` owns metrics and caches.
- `ShapeText` in `Strata/src/Strata/Renderer/TextLayout.cpp` owns layout.
- `FontAtlas` owns rasterizing, cells and uploads.
- `FontAtlasCache` owns the atlases of one :term[renderer]{id=renderer}, and `TextRenderer` owns the vertex data and the draw.

All of it runs on the :term[main thread]{id=main-thread}.

The **glyph atlas** is the texture that holds the rasterized glyphs of one font.

Strata makes it a texture array of single-channel layers, and each layer is a **page**: a square of 512 by 512 texels. One
page holds 262,144 bytes, which is cheap to keep and to upload.

A page is cut into a grid of squares. A **cell** is the fixed slot of a page that one glyph occupies, and a larger glyph
takes a block of cells. Cells are 42 texels wide, so a page holds 12 cells in a row and 144 in all.

A glyph of Latin size fills about 30 texels, so it takes one cell with room to spare. The empty texel between neighbours
keeps texture filtering from mixing them.

A code point is the number Unicode gives a character, and the bytes of a UTF-8 string spell it out; see
[Bytes in files and memory](../basics/bytes.md). A font maps code points to glyph indices through its character map.

Each glyph also has an **advance**: the distance the pen moves to the right after the glyph is drawn. The pen is the point where layout places the
next glyph, as a hand moves along a line of writing.

## The contract

Callers of the text code may assume the following, and must do their part.

- A `Font` exists only if its validation passed. Everything below it reads a font that is well formed in every way the
  rasterizer needs.
- `FontFace` answers every question about size and position without a texture. A caller measures text with `ShapeText` and
  with nothing else.
- Glyphs appear over several frames. A glyph that is not in the atlas yet is pending: it keeps its advance, gets no quad and
  is drawn on a later frame. Callers count the pending glyphs and never wait for them.
- Atlases belong to the renderer's `FontAtlasCache`. A pass that draws glyphs asks the cache for the atlas and lends the
  frame's budget to it, so two passes never rasterize without knowing of each other.
- Every call runs on the main thread.

:::rule[Rule of the engine: font files are not trusted]
`AGENTS.md` says that before code calls another stb_truetype function, `Strata/src/Strata/Renderer/FontValidation.h` gets
the checks for it, with tests that feed crafted fonts. The reason is that the library checks no bounds: one bad offset in a
file becomes a read past the end of memory. The same rule bounds time as well as reads, because a few bytes can describe
millions of points. The guide's section on rendering states it in full.
:::

:::rule[Rule of the engine: measure from metrics and share the cache]
Text is measured with `ShapeText`, never by rasterizing, and every pass that draws glyphs shares the renderer's
`FontAtlasCache`. The reason for the first half is cost: a layout that rasterized would stall the frame that asks, and could
not run in a tool that has no GPU. The reason for the second half is that one budget and one atlas per font serve every pass.
:::

## A toy version

Before the real code, a small program does both jobs the simple way. It builds a distance field from an 8 by 8 grid by trying
every texel, and it shapes the line `AVA` from a table of advances and one kerning pair. A kerning pair is a spacing fix between two letters, which a later paragraph names. The font is invented, so its numbers
are not those of a real font.

:::question
Do you know constants, loops, functions, :term[structs]{id=struct}, classes, calls such as `std::printf`, pointers, maps and `constexpr`? If
not, read [Programming from zero: values and decisions](../basics/programming-1.md), [Programming from zero: loops and functions](../basics/programming-2.md) and
[Programming from zero: classes and references](../basics/programming-3.md), then [C++ memory](../basics/cpp-memory.md), [Generic C++](../basics/cpp-generic.md) and
[Modern C++ as Strata uses it](../basics/cpp-modern.md).
:::

The field asks, for each texel, which texel on the other side of the outline is nearest. The outline lies halfway between the
two texels, so the distance to it is half a texel shorter. The stored value is 128 on the outline plus 32 for each texel
inside, clamped to the range of a byte. Outside, the value falls by 32 per texel. Strata uses the same numbers, with a padding
of 4 texels around the glyph.

```cpp sketch="gpu-text-toy.cpp"
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <map>
#include <string>
#include <utility>

constexpr int c_Size = 8;
constexpr int c_Padding = 4;
constexpr float c_OnEdge = 128.0f;
constexpr float c_PerTexel = c_OnEdge / c_Padding;

// A glyph as a bitmap: '#' is inside the outline.
const char* const c_Letter[c_Size] = { "........", ".##.....", ".##.....", ".##.....", ".##.....", ".#####..", ".#####..", "........" };

bool IsInside(int x, int y)
{
	return x >= 0 && y >= 0 && x < c_Size && y < c_Size && c_Letter[y][x] == '#';
}

// Brute force: search every texel for the nearest one on the other side of the outline.
uint8_t DistanceValue(int x, int y)
{
	const bool inside = IsInside(x, y);
	float nearest = 1000.0f;
	for (int sy = -c_Padding - 1; sy < c_Size + c_Padding + 1; sy++)
	{
		for (int sx = -c_Padding - 1; sx < c_Size + c_Padding + 1; sx++)
		{
			if (IsInside(sx, sy) != inside)
				nearest = std::min(nearest, std::hypot(float(sx - x), float(sy - y)));
		}
	}
	// The outline lies halfway between the two texels, so the distance to it is half a texel shorter.
	const float signedDistance = (inside ? 1.0f : -1.0f) * (nearest - 0.5f);
	return uint8_t(std::clamp(c_OnEdge + c_PerTexel * signedDistance, 0.0f, 255.0f));
}

struct ToyFont
{
	std::map<char, float> Advance = { { 'A', 0.65f }, { 'V', 0.62f } };
	std::map<std::pair<char, char>, float> Kerning = { { { 'A', 'V' }, -0.08f } };
};

// Shapes one line: each pen position is the sum of the earlier advances and kerning pairs, in em.
void ShapeLine(const ToyFont& font, const std::string& text)
{
	float pen = 0.0f;
	for (size_t index = 0; index < text.size(); index++)
	{
		if (index > 0)
		{
			const auto pair = std::make_pair(text[index - 1], text[index]);
			if (font.Kerning.count(pair) > 0)
				pen += font.Kerning.at(pair);
		}
		std::printf("%c at %.2f\n", text[index], pen);
		pen += font.Advance.at(text[index]);
	}
	std::printf("width %.2f em\n", pen);
}

int main()
{
	std::printf("row 3, texels -4 to 11:");
	for (int x = -4; x < c_Size + 4; x++)
		std::printf(" %d", DistanceValue(x, 3));
	std::printf("\n");
	ShapeLine(ToyFont(), "AVA");
	return 0;
}
```

```text output-of="gpu-text-toy.cpp"
row 3, texels -4 to 11: 0 16 48 80 112 144 144 112 80 80 72 53 28 0 0 0
A at 0.00
V at 0.57
A at 1.19
width 1.84 em
```

1. **Lines 11–12:** the value on the outline, 128, and the slope, 128 divided by the padding of 4 texels, so 32 per texel.
2. **Lines 27–33:** the search visits every texel of the padded grid; the cost is the number of texels squared, which is
   fine for a toy and too slow for a font.
3. **Lines 36–37:** the half-texel correction, the sign by side, and the clamp to a byte.
4. **Lines 52–57:** the kerning pair adds to the pen before the glyph, so a pair changes where that glyph starts.

Row 3 of the grid is `.##.....`. The printed row starts four texels left of the grid, so the 0 there says that the texel is
far outside. The two texels of the stem hold 144, which is 16 above the outline value. The texel next to the stem on each
side holds 112, which is 16 below it. To the left the values fall by 32 per texel until they reach 0, and to the right they
fall more slowly, because the foot of the letter lies two rows down.

The shaping half shows **kerning**: an adjustment to the distance between two particular glyphs. The pair A then V adjusts
by minus 0.08 em, so V starts at 0.65 minus 0.08 = 0.57 em, not at 0.65. The final pen position, 1.84 em, is the width of the
line. The program never touched a pixel to learn it.

Each pen position lies on the **baseline**, the line on which the letters stand. A font reports how far glyphs rise above it
and fall below it, and how far one baseline lies from the next.

Everything the real code adds is about trust, speed and memory: real outlines instead of a grid, a texture of limited size, a
budget for the time spent, and checks in front.

## The real code, in the order data flows

### The Font asset and the default font

`Font::Create` takes the bytes of a TrueType file, checks them and keeps a copy, with one correction described below. It
accepts a `.ttf` file, and for a `.ttc` collection it uses the first font.

**TrueType** is the font format whose outlines are straight lines and simple curves that bend once. The other family, OpenType
with outlines in the Compact Font Format (CFF), carries the tag `OTTO`, and Strata refuses it.

A game without a font of its own gets `Font::GetDefault`, Roboto Medium, which `Strata/CMakeLists.txt` embeds in the engine.
Text whose font asset is still loading draws with the default font and switches when the asset arrives.

### Validation

The library is **stb_truetype**, a single-file C library that reads TrueType data and rasterizes distance fields. Its author
omitted every bounds check, which keeps it small and makes a hostile font dangerous. `ValidateTrueTypeFont` checks, before
the library reads anything, every range of bytes that the library can follow.

The first check covers the tables. A font is a set of tables named `head`, `hhea`, `maxp`, `hmtx`, `loca`, `glyf` and
`cmap`, and optionally `kern` and `GPOS`. Each table must lie inside the file and meet its minimum size. The `loca` table
gives the start of each glyph inside `glyf`, so its entries must not decrease and must not point past the end of `glyf`.

The second check covers the character map. The library uses one part of it, in format 0, 4, 6, 12 or 13, and each format has
arrays whose lengths come from the file, and Strata bounds them all. Format 4 also stores three numbers for a :term[binary search]{id=binary-search}, and
the library trusts them. If they disagree with the segment count, Strata computes the right ones and the font keeps a
corrected copy. That is why `Font::GetData` is not always the bytes of the file.

The third check covers every glyph. A simple glyph lists contours, flags and coordinates, and the flag bytes can repeat, so
two bytes can stand for 256 points. The file size therefore does not bound the work. Strata counts the points and rejects a
font whose glyphs total more than `FontLimits::c_MaxOutlinePoints`, which is 16,777,216.

A composite glyph builds a letter from other glyphs, such as an accent on a base letter. Strata checks every index, forbids
cycles, and allows at most `c_MaxCompositeDepth` levels of nesting, which is 8. After expanding, a glyph may have at most
`c_MaxCompositeComponents` components, which is 256. The transforms must keep every coordinate within 16 bits.

The fourth check covers kerning. The glyph positioning table (**GPOS**) is OpenType's general table of positioning data, and
kerning may live there. The library reads `GPOS` when the font has it and the older `kern` table otherwise. Strata bounds what
is read, and it bounds time too: the library searches every lookup, and every part of the pair lookups, for each glyph pair it
adjusts.

A font whose search exceeds 512 steps for one pair, or whose kerning takes more than 1,048,576 units of work to check, is not
rejected. It loses its kerning, and `Font::HasUsableKerning` is false. The choice favors a usable font over a perfect one.

The last check covers the format. The file must start with a TrueType signature. A collection leads to its first font, and a
font that carries the `OTTO` tag fails, because the library parses CFF data without bounds and no rule above covers it.

```cpp src="Strata/src/Strata/Renderer/FontValidation.cpp#L127-L134"
	fontStart = U32(12);
	if (!Has(fontStart, 12))
		return Fail("Font collection points outside the file");
}
if (IsTag(fontStart, "OTTO"))
	return Fail("OpenType fonts with CFF outlines (OTTO) are not supported; use TrueType outlines");
if (U32(fontStart) != c_SfntTrueType && !IsTag(fontStart, "true"))
	return Fail("Not a TrueType font");
```

The whole file is also capped at 64 MiB, `FontLimits::c_MaxFontSize`.

### `FontFace`: measuring without pixels

`FontFace` holds what layout needs: the glyph of a code point, its advance, kerning between two glyphs and the font's
vertical metrics. The face reports the ascent above the baseline, the descent below it and the line height, all in em. For
each glyph it also reports the plane bounds, which are the corners of the glyph's quad relative to the pen, and the texel
size of its distance field.

Two caches stay bounded. The map from code points to glyph indices and the map of kerning pairs are cleared when they reach
`FontFace::c_CacheLimit`, 4,096 entries each, so a text in a hundred languages cannot grow them without end. The map of
glyph metrics holds at most the font's glyph count.

The face also decides whether a glyph can be drawn at all. A glyph larger than 192 texels with padding, or costlier to
rasterize than 2,097,152 units, is rasterized at half resolution, then at a quarter, and beyond that not drawn. The cost is
about proportional to time: about 4 ns per unit on an :term[optimized]{id=optimization} desktop build, and a curve point counts three times as much as a point of a straight line. The checks of
the validation record each glyph's shape, so the cost is known before any rasterizing.

### `ShapeText`: layout from metrics alone

`ShapeText` takes a face, a UTF-8 string and options, and fills a `ShapedText`. It holds the glyphs with their pen positions,
the bounds of the block, the width of the widest line, the line count and a flag for cut text. `DecodeUTF8` turns broken bytes
into the replacement character `U+FFFD`, so a bad string cannot stop layout. `MeasureCaretStops` returns the pen position before
each character, which a text field needs.

```cpp src="Strata/src/Strata/Renderer/TextLayout.h#L50-L66"
// How ShapeText lays text out, in em units (font size 1).
struct TextShapeOptions
{
	// Left (value-initialized: the enumerators are in Renderer/RendererComponents.h, which this header leaves out).
	TextAlignment Alignment{};
	TextVerticalAlignment VerticalAlignment = TextVerticalAlignment::Top;
	// Above 0: lines wrap at this width, between words (after spaces, which a break drops, and after hyphens), and inside
	// words longer than a line.
	float WrapWidth = 0.0f;
	// Above 0, with Truncate or Ellipsis: lines are cut at this width (usually the wrap width of unwrapped text).
	float MaxWidth = 0.0f;
	// Above 0: the height of the box vertical alignment places the block in (from y = 0 down), and with Truncate or
	// Ellipsis the height lines must fit in (a line fits when its descent does).
	float BoxHeight = 0.0f;
	float LineSpacing = 1.0f; // Times the font's line height
	TextOverflowMode Overflow = TextOverflowMode::Overflow;
};
```

1. **Line 58:** the wrap width in em; above 0, lines break between words and inside a word longer than a line.
2. **Line 60:** the cut width, used only with `Truncate` or `Ellipsis`.
3. **Line 63:** the box height, for vertical alignment and for how many lines fit.
4. **Line 64:** the line spacing multiplies the font's own line height.
5. **Line 65:** the overflow mode, which says what happens beyond the box.

Wrapping breaks after spaces and after a dash, drops the space at a break, and cuts inside a word that is longer than a
line. A tab advances by four spaces, and other control characters take no room.

The overflow modes decide what happens beyond the box. `Overflow` continues, `Truncate` omits what does not fit, and
`Ellipsis` ends the last kept line with the character U+2026, or with three dots. Everything is in em, so the caller scales
by the font size.

Strata's shaping stops there: it has no joined letter forms, no change of letter order and no right-to-left text.

### `FontAtlas`: a bounded texture filled on demand

`FontAtlas::GetGlyph` returns a `GlyphInfo`. The first call for a glyph describes it from the face, and the glyph is pending
if it has a shape. A pending glyph goes through `Rasterize`, which is where time and memory are spent.

```cpp src="Strata/src/Strata/Renderer/FontAtlas.cpp#L105-L116"
if (m_Budget.Glyphs == 0 || m_Budget.Cost == 0)
	return;
const glm::uvec2 cells = (entry.Size + glm::uvec2(c_GlyphGutter + c_CellSize - 1)) / c_CellSize;
CellBlock block;
if (!Allocate(cells, block))
	return;
m_Budget.Glyphs--;
m_Budget.Cost = m_Budget.Cost > entry.Cost ? m_Budget.Cost - entry.Cost : 0;

const uint32_t glyphIndex = entry.Info.GlyphIndex;
const std::vector<uint8_t> distances = m_Face->RasterizeGlyph(glyphIndex);
entry.Info.Pending = false;
```

1. **Line 105:** a spent budget, in glyphs or in cost, leaves the glyph pending for a later frame.
2. **Line 107:** the cell count per axis, with one gutter texel added and rounded up: a field of 41 texels fits one cell.
3. **Lines 109–110:** with no free cells and nothing to free, the glyph stays pending.
4. **Lines 111–112:** the budget pays one glyph and the glyph's cost; the last glyph may cost more than is left, and the budget
   stops at 0.
5. **Lines 115–116:** the face rasterizes the field, and the glyph is no longer pending.

Allocation takes three steps, in this order. The atlas searches for free cells on the pages it has. If none fit and fewer than
`MaxPages` pages exist, it adds a page, up to 8. Only then does it free cells.

**LRU eviction** removes the least recently used entries when a store is full. Here the atlas frees the glyphs that went
longest unused, and never a glyph used in the current frame, because a quad of this frame may already point at it.

Rasterizing calls `stbtt_GetGlyphSDF` through the face. The atlas copies the rows into the page and marks them as changed.
A glyph that lost its cells is rasterized again when the text returns. `FontAtlasStats` counts rasterized glyphs, freed
glyphs and uploaded bytes.

`Upload` creates the `R8_UNORM` texture array. Its layer count grows in powers of two up to the page limit.

When the texture is
created or grows, every page is sent in full. Other uploads send only the changed rows. The graphics library writes whole layers, so the rows
travel through a staging texture of 512 by 64 texels, in bands of 64 rows that start at the first changed row. One band is 32,768 bytes, an eighth of a page.

### `FontAtlasCache` and the frame budget

`FontAtlasCache` keeps one atlas per font for one renderer. `Get` makes the atlas on first use and marks it used. At the
start of each frame, `BeginFrame` drops the atlases that no pass asked for in the previous frame and whose font only the
cache still holds. It never drops the default font's atlas. It also gives the frame its rasterization budget.

A pass lends the budget to an atlas, makes its glyph requests and takes back what is left. The game user interface draws
after the text and spends what the text left.

`TextRenderer::c_FrameRasterBudget` is 32 glyphs and 524,288 units of cost. That allows about 2 ms of rasterizing on a
desktop build: about ten Latin letters, or one emoji. Whichever of the two counts runs out first ends the frame's
rasterizing, so the cost binds for Latin letters, and the 32 glyphs bind only when each glyph costs less than 16,384
units. Glyphs over the budget wait for the next frame, so new text appears in
pieces instead of stalling one frame. A `static_assert` ties the largest cost of one glyph to four times the budget.

### `TextRenderer`

A `TextComponent` holds the string, a font handle, a color, a font size, a screen-space switch, an anchor and an alignment.
For each active component the renderer lays the text out with the atlas, which returns quads for the glyphs that are in the
atlas. For each quad it appends vertex data with a position, a texel position and page, and a packed color.

World-space text lies in the plane of the entity's X and Y axes. The font size is in world units per em, and the depth test
hides the text behind geometry. Screen-space text takes the font size in pixels, an anchor and an offset, and draws over
everything. The glyphs of one atlas form one draw range with one binding.

### The shader

The vertex shader places the quad. The fragment shader reads one atlas texel and turns the distance into coverage.

```slang src="Strata/shaders/Include/SDFText.slang#L4-L15"
// Signed distance field glyphs (FontAtlas): the outline is where the distance crosses the on-edge value, and the value
// rises by 128 / 255 over FontFace::c_DistancePadding (4) texels toward the inside.
static const float c_SDFOnEdgeValue = 128.0 / 255.0;
static const float c_SDFValuePerTexel = 32.0 / 255.0;

// Coverage of a distance sample around an edge value: ramps over about one screen pixel, so text stays sharp and smooth at
// any size. Call in uniform control flow (it takes the distance's screen derivatives).
float SDFCoverage(float distanceValue, float edgeValue)
{
	float width = max(fwidth(distanceValue) * 0.7, 1e-4);
	return smoothstep(edgeValue - width, edgeValue + width, distanceValue);
}
```

1. **Lines 6–7:** the outline value, 128 of 255, and the rise per texel, 32 of 255, written as the shader sees them.
2. **Line 13:** the width of the ramp is 0.7 of the change per pixel, with a floor so that it never reaches 0.
3. **Line 14:** `smoothstep` turns the distance into coverage between an edge value a little below the outline and one a little above.

The outline is the value 128 out of 255. The value rises by 32 per texel inward, so four texels of padding fill the whole
range. The function measures how fast the value changes across one screen pixel, with `fwidth`. The ramp spans about 1.4
pixels at any size.

```slang src="Strata/shaders/Overlay/Text.frag.slang#L17-L26"
void st_Main()
{
	float2 pageSize = float2(TextureSize(u_Atlas, 0).xy);
	// Array layers are selected by rounding, so interpolation error in the page coordinate does not matter.
	float distance = u_Atlas.Sample(u_AtlasSampler, float3(v_TexCoord.xy / pageSize, v_TexCoord.z)).r;
	float coverage = SDFCoverage(distance, c_SDFOnEdgeValue);
	if (coverage <= 0.0)
		discard;
	o_Color = float4(v_Color.rgb, v_Color.a * coverage);
}
```

1. **Line 21:** one sample of the page, chosen by the glyph's texel position and the page number.
2. **Line 22:** coverage, computed from the sample before anything leaves the shader.
3. **Lines 23–24:** a pixel with no coverage leaves, so empty parts of the quad write no color and no depth.
4. **Line 25:** the glyph color, with its alpha scaled by the coverage.

The function that uses `fwidth` runs in uniform control flow, because derivatives compare neighbouring pixels. The `discard`
comes after the coverage, so every pixel of a quad takes part in the derivative before any pixel leaves.

## One glyph, from string to pixel

:::example[A letter that is new to the atlas]
A sign shows the word "Gate" at 32 pixels per em. The letter G is not in the atlas. The layout asks the face for the glyph,
which has an advance and a plane quad, and the atlas finds the glyph pending.

Say the glyph's field is 37 texels wide and 40 tall with padding. Its cell block is (37 + 1 + 41) / 42 = 1 across and
(40 + 1 + 41) / 42 = 1 down, so one cell, using whole-number division. A size of 41 would still fit one cell, and 42 would
need two. The budget drops from 32 glyphs to 31 and loses the glyph's cost, and the atlas copies 40 rows into the page.

Those rows lie within one band of 64 rows. Unless the texture has to grow, the frame sends 32,768 bytes, not the 262,144 bytes
of a page.

On screen the quad covers 37 pixels, one texel per pixel. At the outline the value is 128. A pixel center half a pixel inside
reads 128 plus 16 = 144. The `fwidth` of the value is 32 / 255 = 0.1255 per pixel. The ramp runs from 128 minus 0.7 of that
to 128 plus 0.7 of that, which is 0.0878 of the value range on each side, or 1.4 pixels in all.

That pixel lies (0.5 + 0.7) / 1.4 = 0.857 of the way up the ramp, and `smoothstep` turns it into a coverage of about 0.94.
At 128 pixels per em the same glyph covers four pixels per texel. The value then changes by 0.0314 per pixel, the ramp is
still 1.4 pixels wide, and the edge is as sharp as before.
:::

An exercise below asks you to compute these coverages with a program.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Image atlas per size | Engines built on FreeType, such as Unreal's Slate | Exact hinted pixels at the size asked for | One texture per size, soft or shimmering text when scaled, rasterizing again when a size changes |
| Multi-channel distance fields (MSDF) | Godot and the msdfgen tool | Sharp corners at large scales | Three channels per texel, a slower generator and a more complex shader |
| Single-channel SDF at one size | Valve's paper, TextMesh Pro in Unity | Strata's choice: one small texture and one cheap shader | Rounded corners at huge sizes, no hinting at tiny ones |
| Outlines drawn as curves in the shader | The Slug library | No atlas, exact edges at any scale | More shader work per pixel and per glyph, and a larger body of code to check |
| Full shaping with HarfBuzz | Godot, web browsers | Arabic, Indic scripts, joined letters and right-to-left text | A large library reading data that is not trusted, and a layout that needs more than metrics |

The single-channel choice is the cheapest one that keeps text sharp across the sizes a game uses. Its weakness is corners:
the field is a smooth ramp, so a corner of a glyph rounds when the text grows far beyond 32 texels per em.

:::why[Why Strata keeps shaping simple]
A full shaping library would give right-to-left and Indic text. It would also read a second binary format that is not
trusted, with its own bounds to defend, and layout would depend on more than metrics. Strata chose advances, kerning and line
breaking. The cost is that texts in scripts that need shaping show wrong joins and a wrong order.
:::

## How it is tested

The suites sit in `StrataTests/src/Renderer/`. `Renderer.Font` in `FontTests.cpp` feeds crafted fonts to the checks. The
fonts have a missing table, `loca` entries that decrease or point past `glyf`, or bad character maps. Others have outlines
past their ranges, composite cycles, glyphs too costly to rasterize, or kerning that is broken or has no limit.

`Renderer.Font` also truncates a font at every table boundary and expects rejection. `Renderer.Font.Sweep` changes a
few bytes at random and expects rejection or a safe render.

`Renderer.FontAtlas` checks the budget, least recently used eviction through thousands of glyphs, the rule that this frame's
glyphs stay, the kerning cache and reduced resolution. `Renderer.FontAtlasCache` checks sharing and the budget that passes
share. `Renderer.Text` checks UTF-8 decoding, atlas growth and alignment.

The GPU suites `GPU.Renderer.FontAtlas` and `GPU.SceneRenderer.Text` read the texture back. They check that uploads send only
changed rows and keep the GPU pages equal to the pages in main memory. They also check that text lands where its anchor puts
it, and that text with many new glyphs completes over frames within the budget.

To run a group, use `build/windows/bin/Debug/StrataTests.exe --test-suite=Renderer.Font*`. The GPU suites carry the label
`gpu`.

## Changing it safely

To add a call to stb_truetype, extend `FontValidation.h` first. Write down which bytes the call reads, make the checks bound
every one of them, and add a test in `Renderer.Font` that crafts a font violating each bound. Bound time as well: count the
steps the call takes for the worst input, and put a limit beside `FontLimits`. Run the new test without the change in the
checks, and see it fail.

To add a layout feature, put it in `ShapeText`, which works from the face alone. A feature that needs pixels belongs in the
atlas or the renderer. The game user interface shapes its text from the same face, so a layout change reaches every label.
Keep the pen positions the same when the options have their default values.

To change how a glyph looks, change what the face rasterizes, and check the GPU suites. Passes that draw glyphs ask the
shared cache for an atlas and never build one.

## Summary

- Strata measures text from font metrics with `ShapeText`, because rasterizing to measure would cost time and need a GPU.
- A distance-field texel stores 128 on the outline and 32 more per texel inside, and the shader turns it into coverage over
  about 1.4 pixels at any size.
- A glyph passes from `ShapeText` to a pending state, then to a cell of a 512 by 512 page when the frame's budget allows, and
  uploads in bands of 64 rows.
- Strata checks every byte that stb_truetype can read, with limits on size and on work, and refuses fonts with CFF outlines.

## Check yourself

1. Which of these measures the width of a label correctly in Strata? (a) Rasterize every glyph and add the widths of the
   images. (b) Call `ShapeText` with the font's face and read `Width`. (c) Draw the text and read the pixels back.

   :::answer{tests="measure-text"}
   (b). It uses advances and kerning from the face, with no texture. (a) is wrong because rasterizing spends the frame's
   budget on a number the metrics already hold, and the images include padding. (c) is wrong because it needs a GPU and a
   frame, and the answer arrives frames later.
   :::

2. A distance field stores 128 on the outline and 32 per texel inward. What does a texel store that lies 1.5 texels outside
   the outline, and what does one store that lies 3 texels inside?

   :::answer{tests="sdf-values"}
   Outside, 128 minus 1.5 × 32 = 80. Inside, 128 plus 3 × 32 = 224. At 4 texels inside the value would reach 256, and the
   byte holds 255.
   :::

3. A glyph's field is 42 texels wide and 20 tall. How many cells does it take? (a) One. (b) Two. (c) Four.

   :::answer{tests="atlas-budget"}
   (b). The count is (42 + 1 + 41) / 42 = 2 across and (20 + 1 + 41) / 42 = 1 down, a block of 2 by 1. (a) forgets the gutter
   texel that keeps neighbours apart. (c) would hold for a field 42 tall as well.
   :::

4. A font file of 20 MiB has simple glyphs with 12,000,000 points in all and a valid kerning table whose search takes 700
   steps for one pair. What does `Font::Create` do?

   :::answer{tests="validate-font"}
   `Font::Create` accepts the font without kerning. The points are under the limit of 16,777,216, and the file is under 64 MiB. The
   kerning search is over the limit of 512, so kerning is switched off, but the font is still created.
   :::

5. Why must the coverage be computed before the `discard` in the fragment shader?

   :::answer{tests="sdf-values"}
   `fwidth` compares a pixel with its neighbours. If neighbours had already left the shader, the derivative would read
   undefined values at the border of the glyph. Computing it first keeps every pixel of the quad in step.
   :::

## Exercises

1. **Basic.** Compute how many single-cell glyphs fit in the eight pages of one atlas, and how many bytes the pages hold.

   :::answer[Worked solution]{tests="atlas-budget"}
   A page has 512 / 42 = 12 cells per row, since 12 × 42 = 504, so 12 × 12 = 144 cells. Eight pages give 1,152 cells. Each
   page is 512 × 512 = 262,144 bytes, so eight pages are 2,097,152 bytes, or 2 MiB. A glyph of 192 texels takes
   (192 + 1 + 41) / 42 = 5 cells across and 5 down, which is 25 cells.
   :::

2. **Basic.** Trace it yourself: follow one glyph from `ShapeText` to its atlas cell. Use a build of the engine from source, a
   project with a sign whose text holds a glyph the atlas has not seen, and a debugger.

   :::answer[Worked solution]{tests="atlas-budget"}
   Set a breakpoint in `FontAtlas::Rasterize` in `Strata/src/Strata/Renderer/FontAtlas.cpp`. When it stops, step over
   `Allocate` and read `block` for the page and the cell, and `entry.Size` for the size of the field. Step on to see
   `MarkDirty` record the rows. The rows travel in `FontAtlas::Upload`, in the same frame, in bands of 64 rows. The layout
   came earlier, from `ShapeText` in `Strata/src/Strata/Renderer/TextLayout.cpp`, which only reads the face.
   :::

3. **Medium.** Write a program that prints the coverage of a pixel whose center lies 1 or 0.5 pixel outside an
   edge, on it, or 0.5 or 1 pixel inside. Use the formulas of the shader, and text of 8, 32 and 128 pixels per em.

   :::answer[Worked solution]{tests="sdf-values" solution="sketches/gpu-text-coverage.cpp"}
   The sketch moves the sample by the change per pixel, which is what `fwidth` reports for an edge parallel to an axis.
   The change and the ramp width both scale with the texels per pixel, so the three sizes agree.

   ```cpp sketch="gpu-text-coverage.cpp"
   #include <algorithm>
   #include <cstdio>

   constexpr float c_OnEdge = 128.0f / 255.0f;
   constexpr float c_PerTexel = 32.0f / 255.0f;
   constexpr float c_TexelsPerEm = 32.0f;

   float Smoothstep(float low, float high, float value)
   {
   	const float t = std::clamp((value - low) / (high - low), 0.0f, 1.0f);
   	return t * t * (3.0f - 2.0f * t);
   }

   // Coverage of a pixel whose centre lies offsetPixels inside an axis-aligned edge, for text of the given size in pixels per em.
   float Coverage(float pixelsPerEm, float offsetPixels)
   {
   	const float texelsPerPixel = c_TexelsPerEm / pixelsPerEm;
   	const float change = c_PerTexel * texelsPerPixel; // What fwidth reports: the distance value's change per pixel
   	const float width = std::max(change * 0.7f, 1e-4f);
   	return Smoothstep(c_OnEdge - width, c_OnEdge + width, c_OnEdge + change * offsetPixels);
   }

   int main()
   {
   	const float sizes[] = { 8.0f, 32.0f, 128.0f };
   	for (const float size : sizes)
   	{
   		std::printf("%5.0f px per em:", size);
   		for (float offset = -1.0f; offset <= 1.01f; offset += 0.5f)
   			std::printf(" %.2f", Coverage(size, offset));
   		std::printf("\n");
   	}
   	return 0;
   }
   ```

   ```text output-of="gpu-text-coverage.cpp"
       8 px per em: 0.00 0.06 0.50 0.94 1.00
      32 px per em: 0.00 0.06 0.50 0.94 1.00
     128 px per em: 0.00 0.06 0.50 0.94 1.00
   ```

   1. **Lines 17–18:** the value changes by 32 / 255 per texel, and a pixel covers `texelsPerPixel` texels.
   2. **Line 19:** the ramp width, as in the shader, with the same floor.
   3. **Line 20:** the sample sits `offsetPixels` pixels inside the edge, which moves the value by `change` per pixel.

   The three rows are identical. The ramp is 1.4 pixels wide at any size, which is why the edge looks the same everywhere.
   :::

4. **Hard.** Craft a font with a `loca` entry that points past `glyf`, and show that `Font::Create` rejects it with a reason.

   :::answer[Worked solution]{tests="validate-font"}
   Start from a font file in a test, and patch it with the `FontPatcher` class of `StrataTests/src/Renderer/FontTests.cpp`. Find the
   `loca` table with `font.Table("loca")`, and write 0xFFFF with `SetU16` into the entry after the last glyph, as the test in
   `FontTests.cpp` does. Pass the bytes to `Font::Create`. It returns null, and the error says that a glyph lies outside the
   font's `glyf` table.

   The check is in `ValidateTrueTypeFont`, in the loop over the `loca` entries. Remove that check in a scratch copy and
   run the test: it fails, which shows that the check carries the test.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/Font.h`, `FontValidation.h`, `FontFace.h`, `TextLayout.h`, `FontAtlas.h`, `FontAtlasCache.h` and
  `TextRenderer.h`, with their sources.
- `Strata/shaders/Include/SDFText.slang` and `Strata/shaders/Overlay/Text.frag.slang`.
- `TextComponent` in `Strata/src/Strata/Renderer/RendererComponents.h`.
- Tests: `Renderer.Font`, `Renderer.Font.Sweep`, `Renderer.FontAtlas`, `Renderer.FontAtlasCache`, `Renderer.Text`,
  `GPU.Renderer.FontAtlas` and `GPU.SceneRenderer.Text`.

## Further reading

- Chris Green, "Improved Alpha-Tested Magnification for Vector Textures and Special Effects", Valve, 2007: the paper behind
  distance-field text. Intermediate.
- msdfgen by Viktor Chlumsky: multi-channel distance fields and their limits. Advanced.
- The FreeType documentation: how glyphs are rasterized and hinted. Intermediate.
- The HarfBuzz manual: what shaping does for complex scripts. Intermediate.
- Eric Lengyel, "GPU-Centered Font Rendering Directly from Glyph Outlines", 2017: the approach of the Slug library. Advanced.
