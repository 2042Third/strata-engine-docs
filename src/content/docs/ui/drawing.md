---
id: ui/drawing
title: "Drawing the UI"
description: "How Strata turns laid-out UI elements into 64-byte quads and draws every canvas of a scene in about one call, on the screen and in the world."
kind: internals
size: XL
tracks: [E]
needs: [ui/contract, ui/text, gpu/binding, gpu/debug-drawing, draw/mirrors-camera-relative]
time: 110
learn:
  - id: trace-button
    text: trace one button from its components to its pixels
  - id: one-draw
    text: explain why a canvas is one draw call and what splits it into more
  - id: upload-edit
    text: name the buffer that an edit uploads and the number of bytes it costs
  - id: slice-cut
    text: compute the quads of a nine-slice image and of a filled image
  - id: clip-shader
    text: explain why masks clip in the shader and why the one discard comes last
since: 0.4.0
status: final
---

A game's user interface (UI) is a handful of panels, pictures and words. A player expects them to appear sharp, in the right place, at any window size and at no cost to the frame. This page follows the second half of that work: what happens after the layout has placed every element. The engine turns each laid-out element into small records called quads and copies only the records that changed to the :term[graphics processing unit]{id=gpu} (GPU). It then draws all the elements of a canvas in about one call.

Screen canvases draw as an :term[overlay]{id=overlay-core} on the finished image, like the :term[gizmos]{id=gizmo-start} of the Scene view, and canvases placed in the world draw inside the scene, hidden behind nearer objects.

The page does not teach how the boxes are laid out; [Rects, anchors and layout](../ui/layout.md) does. Shaping and drawing glyphs belong to [Text and text fields](../ui/text.md) and [Text on the GPU](../gpu/text.md), and the registration of overlay passes in general to [Overlays, debug drawing and gizmos](../gpu/debug-drawing.md). At the end you can follow one button from its components to its pixels, and say which buffer an edit uploads.

## The problem and how engines solve it

Start with a menu that has a title, a panel, three buttons and a label on each button. That is eight elements. The title has 5 letters and each of the three labels has about 6, so the words hold roughly 23 glyphs. A glyph is one letter drawn from a picture of a :term[font]{id=font}, and each one needs a rectangle of its own. The menu is therefore about 8 images and 23 glyph rectangles, 31 rectangles in all, and a real game screen has several hundred.

The simplest way to draw them is one draw call per rectangle. The program tells the graphics card "draw this rectangle with this color and this picture", 31 times. Each call costs the processor a fixed amount of work, whatever the rectangle is.

The work is small, but a screen with 600 rectangles at 60 :term[frames per second]{id=frame-rate} means 36,000 calls every second for pictures that barely change. The graphics card also sits idle between small calls. So engines search for ways to send many rectangles at once.

The first idea is the **quad**: a rectangle drawn as two triangles, described by a small record of data (its corners, color, :term[texture coordinates]{id=texture-coordinates} and so on). If every rectangle of a canvas is a record in one array, the whole canvas can be one call. The array is in draw order, so a later rectangle covers an earlier one, exactly as the layout intends. The hard part is what a single call cannot vary: the program, the blending and the bound resources stay the same for the whole call. Every difference between rectangles must therefore live inside the record or in tables that the :term[shader]{id=shader} reads.

The second idea is how to give the card its geometry. The classic way writes four corner vertices per rectangle into a vertex buffer every frame. **Instancing** draws one small shape many times in one call, and the shader receives the number of the copy it draws.

With that number the shader reads the rectangle's record from a buffer itself, a method also called vertex pulling. The shape is the same six vertices for every quad, so no vertex buffer exists at all. Strata uses this: six vertices per quad, one instance per quad.

The third idea is clipping. A scrolling list or a credits text must not draw outside its box. There are three well-known ways, and each has a cost.

- A **scissor rectangle** is a rectangle the card applies to a draw call: pixels outside it are dropped. It is cheap, but one call has one scissor, so every change of clip rectangle splits the batch into a new call.
- A **stencil mask** draws the mask's shape into an extra buffer, and later draws test against it. It handles odd shapes, but it adds draws, needs the extra buffer and also breaks batches when masks change.
- **Clipping in the shader** gives each quad the number of its clip rectangle, and the fragment shader (the program that colors each pixel) compares the pixel with the rectangle. Batches never split, and edges can fade softly. The cost is a little work per pixel, and only rectangles can clip.

The last choice is how long the data lives. A UI could rebuild every quad and copy the whole array to the card every frame. That is simple, but a static menu would copy the same :term[bytes]{id=byte} 60 times each second. The other choice keeps the buffers on the card and sends only what changed. That needs careful accounting: the engine must know which quads changed, and a record must stay valid when the engine moves a texture or a glyph underneath it.

:::example[One menu, two ways]
Take the 31 rectangles above. One call each is 31 calls. As quads in an array with one instanced call, the whole menu is 1 call. Now the player moves the pointer onto a button, and its color starts to fade. Only the button's image changes, which is one quad of 64 bytes.

A system that rewrites every quad copies 31 × 64 = 1,984 bytes per frame, and a system that sends only the changed quad copies 64. After the fade ends, the second system copies nothing.
:::

Strata chooses all of the above together: quads in one array per canvas, instanced without a vertex buffer, clipping in the shader, and buffers that stay on the card and receive only changed ranges. The rest of the page shows how each piece works and what the choice costs.

## The map: from component to pixel

The data flows in one direction, from components to pixels. Everything on the central processing unit (CPU) side runs on the :term[main thread]{id=main-thread}, which owns the scene and the rendering submission. The diagram shows the stages, and the table after it lists the buffers that the draw reads.

```mermaid caption="From components to pixels. The scene's UI state builds quads and shaped texts. The pass uploads changed ranges into five buffers, splits them into draw runs and draws through the two shaders." alt="A flow diagram from left to right. UI components feed the game UI scene, which holds elements, shaped texts and the quad array. The overlay pass reads the quads, uploads them to buffers for quads, texture slots, glyphs, clip rectangles and transforms, and builds draw runs. The runs are drawn with the vertex shader and the fragment shader into the finished image."
flowchart LR
    C["Components: image, text, canvas"] --> S["Game UI scene: elements, shaped texts"]
    S --> Q["Quad array in slots, with a change journal"]
    Q --> P["Overlay pass: Prepare"]
    P --> B["Buffers: quads, texture slots, glyphs, clips, transforms"]
    P --> R["Draw runs"]
    B --> V["Vertex shader"]
    R --> V
    V --> F["Fragment shader"]
    F --> I["Finished image"]
```

Read the diagram left to right. A component such as `UIImageComponent` holds what a game maker sets. `GameUIScene` (the scene's UI state, from [The UI contract](../ui/contract.md)) keeps the laid-out elements and the shaped texts, and turns them into the quad array. The pass, `GameUIRenderer`, runs in `Prepare` before the frame draws: it asks the scene for the quads, copies the changed ones, and works out what to draw. `DrawWorld` and `Draw` then record the calls.

Five buffers feed the shaders. The :term[binding set]{id=binding-set} of `GameUIRenderer` numbers them as shader resource slots, and the other resources of the draw sit beside them.

| Slot | Content | Elements | Changes when |
| --- | --- | --- | --- |
| 0 | Quads (`UIQuad`) | 64 bytes each | an element changes |
| 1 | Texture slots | one 32-bit number per UI texture | a texture loads or its :term[bindless slot]{id=bindless} moves |
| 2 | Glyph table | two 32-bit numbers per glyph of each font | a glyph reaches the atlas |
| 3 to 6 | :term[Glyph atlases]{id=glyph-atlas} | up to four pictures | an atlas grows |
| 7 | Clip rectangles (`UIClipRect`) | 32 bytes each | a mask changes |
| 8 | Transforms | one 4 by 4 matrix per world canvas | the camera or the canvas moves |

The pass also sends a small block of numbers with every draw, the :term[push constants]{id=push-constants} `UIDrawParameters`. They hold the :term[viewport]{id=viewport-input} size, the canvas's origin and scale, flags, where the canvas's quads start in the buffer, and which fonts sit in the four atlas slots. Push constants and bindless textures are taught in [Binding resources](../gpu/binding.md).

Two words name the units of the draw. A canvas has one array of quads, and a **draw run** is a stretch of that array drawn by one call. A canvas is one run unless it uses more fonts than one call can bind.

The shaders color in **display values**, the numbers an :term[sRGB]{id=srgb} screen shows, not linear light. The pass draws after tone mapping, so blending happens in those display numbers, and [Tone mapping](../image/tone-mapping.md) explains what the image holds before that.

## The contract

The rules below keep the module fast and its layers separate. Each has a reason, and breaking one costs something you can name.

:::rule[The renderer never includes the game UI]
The renderer reaches the UI only through `SceneOverlayRegistry`. `RegisterGameUIRenderer` adds a factory under the name `GameUI`, and each `SceneRenderer` makes one pass per factory when it is constructed. The reason is the :term[layer table]{id=layer-table}: the renderer sits below the game UI, so a direct include would make a low layer depend on a high one. With the registry, the renderer builds and works when the module is absent. The registry and the overlay passes in general are taught in [Overlays, debug drawing and gizmos](../gpu/debug-drawing.md).
:::

:::rule[Quads name UI texture and font indices, never slots or atlas places]
A quad holds the index of a texture in the scene's own list of UI textures, and the index of a font in the scene's list of fonts. It never holds a bindless slot or a position in an atlas. Mip streaming changes a texture's bindless slot while the game runs, and the atlas packs a glyph wherever there is room. If quads held those numbers, every move would force the scene to rebuild its quads. With indices, the pass fixes the tables (slots, glyph placements) and the quads stay still.
:::

:::rule[Masks clip in the shader, never by splitting draws]
Every quad carries the number of its clip rectangle, and the shaders apply it. A canvas with ten scrolling lists is still one draw. Splitting at each mask would turn a canvas into many calls and bring back the cost that quads avoid.
:::

:::rule[`UIQuad` and the shader's structs change together]
`UIQuad`, `UIClipRect` and `UIDrawParameters` are written in C++ in `GameUIRenderData.h` and again in `UIQuad.slang`. The `static_assert` on `UIQuad` guards only its size. A field moved in one file and not in the other keeps the size and still reads wrong bytes, with no error. Change both files in the same commit, and run the `GPU.GameUI` tests.
:::

:::rule[The pass asks for each texture and font once per frame]
`UpdateTextures` and `UpdateGlyphs` loop over the distinct textures and fonts of the scene, not over the elements, and request each at High priority. The reason is the cost of a request, which grows with its number, and a screen with 300 quads of one font needs one request for that font. For glyphs, asking also keeps them from :term[eviction]{id=eviction} while they are on screen.
:::

Two limits belong to the contract as well. World-space canvases are drawn after post-processing and without lighting, so no light or shadow touches them. And the game's clicks on a world canvas ignore geometry in front of it: the picture hides behind a wall, but a click through the wall still reaches the canvas ([UI input](../ui/input.md)). Strata does not light world-space UI, and the page does not pretend otherwise.

## A toy version

Before the real code, a small program does the three jobs that matter. It writes elements into slots with room to spare, rewrites one slot when its element changes, and splits the array into runs. The toy has six elements: a panel image, and five texts, each in its own font. It uses no engine code.

```cpp sketch="ui-drawing-toy.cpp"
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <vector>

// A toy of the UI's batching: elements write quads into slots with room to spare, and the quad array splits into runs.
struct Element
{
	int Glyphs = 0; // 0: an image element, else a text of this many glyphs
	uint32_t Font = 0;
};

struct Quad
{
	bool Hidden = true;
	bool Glyph = false;
	uint32_t Font = 0;
};

struct Slot
{
	uint32_t First = 0;
	uint32_t Capacity = 0;
};

uint32_t GetCapacity(int glyphs)
{
	return glyphs == 0 ? 1u : static_cast<uint32_t>(glyphs) + std::max(4u, (static_cast<uint32_t>(glyphs) + 3u) / 4u);
}

void Write(std::vector<Quad>& quads, const Slot& slot, const Element& element)
{
	const uint32_t used = element.Glyphs == 0 ? 1u : static_cast<uint32_t>(element.Glyphs);
	for (uint32_t index = 0; index < slot.Capacity; index++)
		quads[slot.First + index] = Quad { index >= used, element.Glyphs > 0, element.Font };
}

int main()
{
	std::vector<Element> elements = { { 0, 0 }, { 5, 0 }, { 4, 1 }, { 7, 2 }, { 4, 3 }, { 6, 4 } };
	std::vector<Slot> slots;
	std::vector<Quad> quads;
	for (const Element& element : elements)
	{
		slots.push_back({ static_cast<uint32_t>(quads.size()), GetCapacity(element.Glyphs) });
		quads.resize(quads.size() + slots.back().Capacity);
		Write(quads, slots.back(), element);
	}
	std::printf("quads in the array: %zu\n", quads.size());

	// An edit rewrites its slot alone, unless the text outgrew the room: then the array would be rebuilt.
	for (const int glyphs : { 8, 9 })
	{
		const bool fits = static_cast<uint32_t>(glyphs) <= slots[2].Capacity;
		std::printf("a label of %d glyphs: %s\n", glyphs, fits ? "rewrite the slot" : "rebuild");
		if (fits)
			Write(quads, slots[2], Element { glyphs, 1 });
	}

	// Runs: one draw while at most four fonts are in use; a glyph of a fifth font starts a new run.
	std::vector<uint32_t> bound;
	uint32_t runStart = 0;
	for (uint32_t index = 0; index < quads.size(); index++)
	{
		if (!quads[index].Glyph)
			continue;
		if (std::find(bound.begin(), bound.end(), quads[index].Font) != bound.end())
			continue;
		if (bound.size() == 4)
		{
			std::printf("run: quads %u to %u\n", runStart, index - 1);
			bound.clear();
			runStart = index;
		}
		bound.push_back(quads[index].Font);
	}
	std::printf("run: quads %u to %zu\n", runStart, quads.size() - 1);
	return 0;
}
```

```text output-of="ui-drawing-toy.cpp"
quads in the array: 47
a label of 8 glyphs: rewrite the slot
a label of 9 glyphs: rebuild
run: quads 0 to 36
run: quads 37 to 46
```

1. **Line 28:** The capacity of a text slot is its glyphs plus a quarter, at least four, so a label that grows a little keeps its slot.
2. **Line 54:** An edit fits when the new glyph count is no larger than the slot's capacity. Otherwise the whole array is rebuilt, which the toy only reports.
3. **Line 69:** A run holds quads of at most four fonts. The glyph of a fifth font ends the run, and the next run starts at that quad.

The output shows the three effects. The array holds 47 quads for six elements, because every text carries spare quads. A label that grows from 4 to 8 glyphs rewrites its slot, but 9 glyphs do not fit, so the toy reports a rebuild. And five fonts need two runs: the first covers quads 0 to 36, and the second starts at the first glyph of the fifth font. The toy omits what makes the real thing correct and fast: the journal of changed ranges, the lookup tables, clipping, the sizes of images, and the shaders.

## The real code

The real code follows the data through the pass, in the order the frame meets it. The examples use the main menu of the Third-Person sample, which has a title, a Play button and a credits panel.

### The quad

Every rectangle the UI draws is one `UIQuad`.

```cpp src="Strata/src/Strata/GameUI/GameUIRenderData.h#L32-L45"
struct UIQuad
{
	glm::vec4 Rect = glm::vec4(0.0f); // x0, y0, x1, y1
	glm::vec4 UV = glm::vec4(0.0f);   // u0, v0, u1, v1
	uint32_t Color = 0;               // RGBA8, display color
	uint32_t Resource = 0;
	uint32_t Flags = c_UIQuadHidden;
	uint32_t BorderColor = 0;         // RGBA8, display color
	float CornerRadius = 0.0f;        // Canvas units
	float BorderWidth = 0.0f;         // Canvas units (images), em (glyph outlines)
	uint32_t Clip = 0;                // 1 + the canvas's clip rect (UIClipRect) the quad is clipped to; 0 clips nothing
	uint32_t Padding = 0;
};
static_assert(sizeof(UIQuad) == 64);
```

1. **Line 34:** `Rect` is the quad's corners in :term[canvas units]{id=canvas-unit}, with +Y pointing down as in the layout.
2. **Line 35:** `UV` holds texture coordinates for an image. For a glyph, `UV.xy` holds the pen position on the baseline, which the vertex shader needs for pixel snapping.
3. **Lines 36–39:** Colors are 4 bytes each, in display values. `Resource` is a texture index plus one (0 means a solid color) for an image, and a glyph index for a glyph. `Flags` carries the kind in bits 0 and 1 (hidden, image, glyph) and, for a glyph, the font's index in bits 8 to 15.
4. **Lines 40–41:** Corner radius and border width are in canvas units for an image. For a glyph, the border width is the outline, in :term[em]{id=em}.
5. **Lines 42–45:** `Clip` is 1 plus the index of the clip rectangle, and 0 means no clip. The `static_assert` fixes the size at 64 bytes, a number the shader's :term[struct]{id=struct} must match.

The fields make sixteen 4-byte values, exactly 64 bytes, and `Padding` fills the last four. The kind sits in two bits and the font in eight, so a scene's UI can hold up to 256 fonts at once. That limit has a consequence, taught below.

### Quads in slots, and the journal

`GameUIScene::BuildQuads` writes the quads of a canvas. Each element owns a slot of the array in element order, so draw order is array order. A text gets room for a quarter more glyphs than it has, at least four more, and an input field's text gets two more quads for its selection and its :term[caret]{id=caret}. Unused quads are hidden quads, and the vertex shader draws nothing for them.

```cpp src="Strata/src/Strata/GameUI/GameUIQuads.cpp#L196-L227"
if (!layout.QuadsRepack && layout.QuadFirst.size() == count)
{
	if (layout.QuadsDirty.empty())
		return;
	ST_PROFILE_FUNCTION();
	// Each changed element rewrites its slot; one that outgrew it rebuilds the array.
	for (const uint32_t element : layout.QuadsDirty)
	{
		layout.QuadsDirtyMarks[element] = 0;
		if (layout.QuadsRepack)
			continue;
		scratch.clear();
		const uint32_t written = WriteElementQuads(canvas, layout, element, scratch);
		if (written > layout.QuadCapacity[element])
		{
			layout.QuadsRepack = true;
			continue;
		}
		RenderData::UIQuad* slot = layout.Quads.data() + layout.QuadFirst[element];
		for (uint32_t index = 0; index < layout.QuadCapacity[element]; index++)
		{
			RenderData::UIQuad& quad = slot[index];
			CountQuadUses(layout, quad, -1);
			quad = index < written ? scratch[index] : HiddenQuad();
			CountQuadUses(layout, quad, 1);
		}
		m_Stats.QuadsBuilt += written;
		RecordQuadChange(layout, layout.QuadFirst[element], layout.QuadCapacity[element]);
	}
	layout.QuadsDirty.clear();
	if (!layout.QuadsRepack)
		return;
```

1. **Line 196:** The quick path applies when the array is not marked for a rebuild and has one slot per element.
2. **Line 202:** Only the elements that the layout marked dirty are visited.
3. **Lines 208–212:** The element writes its quads into scratch space. If they exceed the slot's capacity, the array is marked for a rebuild and the loop skips the rest.
4. **Lines 215–221:** The slot is rewritten whole, including its hidden quads, and the use counts of textures and glyphs are corrected for what left and what arrived.
5. **Line 223:** The changed range goes into the journal.

The **journal** is the list of ranges that changed, each with a version number (`RecordQuadChange`). Neighbouring ranges of one update merge, and the journal keeps at most 256 entries. When the oldest entries fall off, the pass can no longer know what changed since its last upload, so `GetQuadChanges` reports that the history is gone and the pass uploads the canvas whole. A rebuild gives the array a new `QuadArrayId`, which has the same effect: the pass sees a different array and copies all of it.

:::example[A button's tint fades]
The pointer moves onto the Play button. The button's image is a nine-slice picture (taught below), so it writes 9 quads into a slot of capacity 9, since images get no spare room. Each frame of the fade, the layout marks the element dirty, `BuildQuads` rewrites that one slot, and the journal gains one range of 9 quads. The pass later copies it: 9 × 64 = 576 bytes.

A label whose text goes from 4 to 5 glyphs has capacity 4 + 4 = 8, so it also stays in its slot. When the same label, still in its slot of 8, grows to 9 glyphs, it overflows, the array is rebuilt, and the next upload copies the whole canvas once.
:::

### Image quads

An image element writes one quad, or nine. Its tint comes from the :term[selectable]{id=selectable} that controls it: a color tint multiplies the color, an image swap picks another texture for the hover, pressed, focused or disabled state. A quad is written only when its color is visible or it has a border. A texture index of 0 plus the color alone makes a solid rectangle, which needs no texture at all.

Three more options change the quad's rectangle. **Preserve aspect** fits the rectangle to the texture's shape. Take a texture of 64 by 32 texels, an aspect of 2, in a rect of 100 by 100. The rect is not wider than 100 × 2, so the fitted height is 100 / 2 = 50. The picture is 100 by 50, centered, with 25 units free above and below.

A **filled image** shows only a fraction of its rect, cut along a direction, the way a health bar shrinks. The code cuts the rectangle and the texture coordinates (UV) by the same fraction. Take a bar 200 units wide that starts at x = 10 and is filled to 0.3 from left to right. It ends at x = 10 + 200 × 0.3 = 70, and its UV right edge is 0.3 instead of 1. The picture is cut, not squeezed.

A **nine-slice** image cuts a picture into a grid of three rows and three columns. The four corners keep their size, the four edges stretch in one direction, and the center stretches in both. A panel with rounded decoration then grows to any size without distorting its corners.

```cpp src="Strata/src/Strata/GameUI/GameUIQuads.cpp#L327-L344"
const glm::vec2 size = box.Size;
const float horizontal = units.x + units.z;
const float vertical = units.y + units.w;
if (horizontal > size.x && horizontal > 0.0f)
{
	units.x *= size.x / horizontal;
	units.z *= size.x / horizontal;
}
if (vertical > size.y && vertical > 0.0f)
{
	units.y *= size.y / vertical;
	units.w *= size.y / vertical;
}
const float xs[4] = { min.x, min.x + units.x, max.x - units.z, max.x };
const float ys[4] = { min.y, min.y + units.y, max.y - units.w, max.y };
const glm::vec2 uvSize(uv.z - uv.x, uv.w - uv.y);
const float us[4] = { uv.x, uv.x + borders.x / textureSize.x * glm::sign(uvSize.x), uv.z - borders.z / textureSize.x * glm::sign(uvSize.x), uv.z };
const float vs[4] = { uv.y, uv.y + borders.y / textureSize.y * glm::sign(uvSize.y), uv.w - borders.w / textureSize.y * glm::sign(uvSize.y), uv.w };
```

1. **Lines 328–329:** The left and right borders together, and the top and bottom borders together, are the sums the rect must hold.
2. **Lines 330–339:** If the left and right borders together are wider than the rect, both shrink by the same factor. The top and bottom do the same.
3. **Lines 340–341:** Four x positions and four y positions cut the rect into the grid.
4. **Lines 343–344:** The texture coordinates are cut by the borders divided by the texture's size, so a border of 12 texels in a 48-texel picture takes 0.25 of the picture. The `sign` keeps flipped UV rectangles flipped.

:::example[A nine-slice shrinks]
Take a texture of 48 by 48 texels, borders of 12 on every side, `SliceScale` 1. In a rect 200 wide and 40 high, the borders are 12 canvas units, and 24 is less than both 200 and 40. The x positions are 0, 12, 188 and 200, the y positions 0, 12, 28 and 40, and the picture's cuts are at 0, 0.25, 0.75 and 1. That is 9 quads.

In a rect 20 wide, the borders 12 + 12 = 24 exceed 20, so each shrinks by 20 / 24 to 10. The x positions become 0, 10, 10 and 20. The middle column has no width, the code skips it (an empty piece is dropped), and the panel is 6 quads.
:::

The nine-slice is the reason the slice borders are measured in texels of the picture and not in canvas units. A border in canvas units would cut the wrong part of the picture whenever the texture's size changed. The texture's size is read once the texture has loaded. A nine-slice whose texture is still loading falls back to one quad, and the scene rebuilds the quads when the texture arrives, because it watches the texture.

### Glyph quads

A text element writes one quad per glyph. The shaped text (from [Text and text fields](../ui/text.md)) gives each glyph's pen position and index, and the font gives its metrics.

```cpp src="Strata/src/Strata/GameUI/GameUIQuads.cpp#L469-L482"
RenderData::UIQuad quad;
quad.Flags = RenderData::c_UIQuadGlyph | (font << RenderData::c_UIQuadFontShift);
quad.Color = PackColor(text->Color);
quad.BorderColor = PackColor(text->OutlineColor);
quad.BorderWidth = outline ? std::clamp(text->OutlineWidth, 0.0f, 0.1f) : 0.0f;
for (const ShapedGlyph& glyph : shaped.Glyphs)
{
	const FontGlyphMetrics& metrics = face->GetGlyphMetrics(glyph.GlyphIndex);
	const glm::vec2 pen(originX + penOffset + glyph.Pen.x * size, top - glyph.Pen.y * size);
	quad.Rect = glm::vec4(pen.x + metrics.PlaneMin.x * size, pen.y - metrics.PlaneMax.y * size, pen.x + metrics.PlaneMax.x * size,
		pen.y - metrics.PlaneMin.y * size);
	quad.UV = glm::vec4(pen, 0.0f, 0.0f);
	quad.Resource = glyph.GlyphIndex;
	out.push_back(quad);
```

1. **Line 470:** The flags carry the kind (glyph) and the font's index shifted into bits 8 to 15.
2. **Line 473:** The outline width is clamped to between 0 and 0.1 em, and is 0 when the outline is off.
3. **Line 477:** The pen is the element's origin plus the glyph's pen times the font size, with y flipped because the layout's +Y points down.
4. **Lines 478–479:** The rect is the glyph's box relative to the pen, from the font's metrics.
5. **Line 480:** `UV.xy` keeps the pen, so the vertex shader can move the whole glyph by its baseline's rounding.

An input field adds its extras around this loop. The selection is a solid quad that comes before the glyphs, so the text draws over it, and the caret is a solid quad after them. Every quad of an element gets the element's clip index at the end of `WriteElementQuads`.

### Lookup tables instead of slots

A quad that holds a bindless slot would break whenever mip streaming moves it. Strata therefore puts two lists in the scene: textures and fonts. `GetTextureIndex` and `GetFontIndex` give each distinct asset the next free number. Image quads hold the texture's number plus one, and glyph quads hold the font's number in the flags and the glyph's index in `Resource`.

```mermaid caption="Two steps between a quad and what it draws. The quad's number selects an entry in a table that the pass fills each frame, and that entry names the bindless texture or the place in the atlas." alt="Two chains. The first goes from a quad to a UI texture index, then the texture slot table, then the bindless texture array. The second goes from a quad to a font index and glyph index, then the font's glyph table, then an atlas page and its texels."
flowchart LR
    Q1["Image quad"] --> T1["UI texture index"] --> T2["Texture slot table"] --> T3["Bindless array"]
    Q2["Glyph quad"] --> G1["Font index + glyph index"] --> G2["Glyph table of the font"] --> G3["Atlas page and texels"]
```

The pass fills the tables every frame, from the current state of the assets. For textures it writes one 32-bit number per index: the bindless slot in the low 24 bits, a bit that marks a gray texture (one channel), and a bit that marks an sRGB texture. For glyphs it writes two 32-bit numbers per glyph: where it sits in its atlas page, and how large it is. A width of 0 means the glyph is not in the atlas yet, and its quad draws nothing for now.

```cpp src="Strata/src/Strata/GameUI/GameUIQuads.cpp#L58-L71"
uint32_t GameUIScene::GetFontIndex(AssetHandle font)
{
	auto it = m_FontIndices.find(font);
	if (it != m_FontIndices.end())
		return it->second;
	if (m_Fonts.size() >= RenderData::c_MaxUIFonts)
		return RenderData::c_MaxUIFonts; // No room: the caller draws the text with nothing
	const uint32_t index = static_cast<uint32_t>(m_Fonts.size());
	m_Fonts.push_back(font);
	m_FontIndices.emplace(font, index);
	m_FontGlyphUses.emplace_back();
	m_ResourceVersion++;
	return index;
}
```

1. **Line 60:** A font already in the list returns its index, so the same font is one entry however many texts use it.
2. **Lines 63–64:** When 256 fonts are in the list, the function returns the invalid number 256. The caller draws that text with nothing.
3. **Lines 65–69:** A new font takes the next index, and the resource version changes so the pass looks at the lists again.

No code in `Strata/src/Strata/GameUI` ever removes a font from this list. A scene's UI gives each distinct font an index that lives as long as the scene's UI state, and index 0 is the default font. Once the default and 255 others hold the 256 places, a text in any further font draws nothing, and no log line says so. Real games use a handful of fonts, so the limit is far away, but a game that creates fonts at run time, one per player name for example, would meet it. This is a known limit, and the cost of cheap lookup tables.

### The pass: what happens before drawing

`GameUIRenderer::Prepare` is the pass's long step. It runs once per frame and view, and it does the following in order.

1. The pass drops binding sets that the last frame did not use, and releases all buffers when the scene has no canvases, so a scene without UI holds nothing of the UI's.
2. The pass counts the screen-space canvases as hidden and returns when the view hides the screen UI (an editor view without the Game UI shown, or a thumbnail) and no world canvas can draw. Hidden canvases are counted, not laid out.
3. The pass asks the scene for the layout at the screen's size and scale. That layout includes the :term[screen view]{id=screen-view} that the editor's canvas mode uses to zoom and pan (taught in [the Scene view](../editor-ui/scene-view.md)).
4. The pass uploads the quads, the clip rectangles and the transforms.
5. The pass updates the texture slots and then the glyph table, and builds the runs.
6. The pass adds what it did to `SceneOverlayStats`.

Step 2 has a counterpart for games. A scene without a camera, such as a main menu, has no image to draw over. `HasScreenContent` tells the game's renderer that the scene has screen canvases, and the renderer then shows the UI over black instead of an error message about the missing camera.

The upload is the heart of step 4.

```cpp src="Strata/src/Strata/GameUI/GameUIRenderer.cpp#L304-L325"
bool whole = previous.QuadArrayId != ui.GetQuadArrayId(view) || previous.Offset != offset || previous.Count != count;
if (!whole && ui.GetQuadVersion(view) != previous.QuadVersion)
{
	m_RangeScratch.clear();
	whole = !ui.GetQuadChanges(view, previous.QuadVersion, m_RangeScratch);
	if (!whole)
	{
		std::sort(m_RangeScratch.begin(), m_RangeScratch.end(), [](const UIQuadRange& a, const UIQuadRange& b) { return a.First < b.First; });
		size_t merged = 0;
		for (const UIQuadRange& range : m_RangeScratch)
		{
			if (merged > 0 && range.First <= m_RangeScratch[merged - 1].First + m_RangeScratch[merged - 1].Count + c_RangeMergeGap)
			{
				UIQuadRange& last = m_RangeScratch[merged - 1];
				last.Count = std::max(last.First + last.Count, range.First + range.Count) - last.First;
			}
			else
			{
				m_RangeScratch[merged++] = range;
			}
		}
		m_RangeScratch.resize(merged);
```

1. **Line 304:** A canvas is uploaded whole when it is a different array (a rebuild), sits at another offset in the buffer, or has another size.
2. **Line 308:** Otherwise the pass asks the journal for the ranges changed since its last upload. If the journal has dropped them, the answer is "whole".
3. **Line 311:** The ranges are sorted by their start.
4. **Lines 315–318:** A range that starts within 16 quads of the previous one's end merges with it, because one larger copy is cheaper than two small ones.
5. **Line 325:** The merged list is cut to its length, and each range is then written into the buffer with `writeBuffer`.

All canvases of a view share one quad buffer, one after another, so a canvas's quads start at its offset in it. The buffer doubles when it is too small. A new buffer has no content, so the pass copies everything into it. The test in `GPUGameUITests.cpp` checks the result: an idle frame uploads nothing, and a frame where one label's color changes uploads at most 16 quads.

The clip rectangles follow the same rule, keyed by the layout's identity and a clip version. The transforms of world canvases are computed every frame and uploaded only when they differ from the last upload.

### Textures and glyphs

The pass resolves what the quads name. For textures, it loops over the scene's list, skips the textures with no users, and requests each used texture once.

```cpp src="Strata/src/Strata/GameUI/GameUIRenderer.cpp#L465-L474"
uint32_t entry = BindlessTextureTable::c_WhiteSlot;
const Ref<Texture> texture = assets ? assets->GetAsset<Texture>(textures[index], AssetPriority::High) : nullptr;
if (texture && texture->GetBindlessSlot() != BindlessTextureTable::c_InvalidSlot)
{
	const TextureSpecification& specification = texture->GetSpecification();
	entry = texture->GetBindlessSlot() & 0xFFFFFFu;
	if (specification.Grayscale)
		entry |= RenderData::c_UITextureGrayscale;
	if (GetTextureFormatInfo(specification.Format).IsSRGB)
		entry |= RenderData::c_UITextureSRGB;
```

1. **Line 466:** The request is at High priority, because UI is what players read first.
2. **Line 470:** The bindless slot is masked into the low 24 bits.
3. **Lines 471–474:** A gray texture and an sRGB texture each get their bit, so the shader samples them as the texture needs.

A texture that has not loaded draws as white (the white slot is the table's default), and the pass counts it in `PendingAssets`. For mip streaming, the pass reports each drawn texture with how many pixels one texture-coordinate unit spans: the largest canvas-unit span of any quad that uses the texture, times the canvases' scale on the screen. The page [Mip streaming](../draw/mip-streaming.md) explains how streaming uses that number.

Glyphs work the same way. `UpdateGlyphs` loops over each font and over each distinct glyph the scene's quads use, never over quads. It asks the renderer's shared `FontAtlasCache` for the font's atlas. Asking :term[rasterizes]{id=rasterization} a missing glyph within the frame's budget, so a screen with many new glyphs completes over a few frames, and the glyphs still waiting are counted in `PendingGlyphs`. The glyph table is a buffer with one region per font: the pass writes a glyph's placement into its region and uploads only the span that changed.

### Draw runs

A canvas binds up to four atlases per call, a limit of `c_MaxBoundAtlases`. `BuildRuns` first asks the scene which fonts the canvas uses. If four or fewer, the whole canvas is one run.

```cpp src="Strata/src/Strata/GameUI/GameUIRenderer.cpp#L669-L687"
for (uint32_t quadIndex = 0; quadIndex < quads.size(); quadIndex++)
{
	const RenderData::UIQuad& quad = quads[quadIndex];
	if ((quad.Flags & RenderData::c_UIQuadKindMask) != RenderData::c_UIQuadGlyph)
		continue;
	const uint32_t font = (quad.Flags >> RenderData::c_UIQuadFontShift) & RenderData::c_UIQuadFontMask;
	if (bind(run, bound, font))
		continue;
	run.FirstQuad = uploaded.Offset + runStart;
	run.QuadCount = quadIndex - runStart;
	m_Runs.push_back(run);
	run = empty;
	bound = 0;
	runStart = quadIndex;
	bind(run, bound, font);
}
run.FirstQuad = uploaded.Offset + runStart;
run.QuadCount = uploaded.Count - runStart;
m_Runs.push_back(run);
```

1. **Lines 671–673:** Only glyph quads matter here, since only they name a font.
2. **Lines 674–676:** A font that the run can bind, or that is already bound, continues the run.
3. **Lines 677–682:** A font that does not fit ends the run at the quad before it and starts a new one at this quad.
4. **Lines 685–687:** The last run takes the rest of the array.

The split is rare: a canvas with five fonts splits in two, and the toy showed it. Draw order stays right, because runs are consecutive stretches of the array and are drawn in order. A font that has no atlas yet needs no slot, and its glyph quads draw nothing.

### Pipelines, binding sets and the draw

The pass makes one pipeline for the screen and one for the world, and the world one has a second variant for scenes whose depth was jittered by temporal anti-aliasing.

```cpp src="Strata/src/Strata/GameUI/GameUIRenderer.cpp#L712-L717"
desc.renderState.rasterState.setCullNone();
desc.renderState.blendState.setRenderTarget(0, blend);
// A canvas in the scene hides behind what is in front of it (reversed-Z), like world text; it never writes depth.
desc.renderState.depthStencilState.setDepthTestEnable(world).setDepthWriteEnable(false).setDepthFunc(nvrhi::ComparisonFunc::GreaterOrEqual);
if (world && jitteredDepth)
	SetJitteredDepthBias(desc.renderState.rasterState);
```

1. **Line 712:** No culling: a quad is drawn from both sides, which matters for a world canvas seen from behind.
2. **Line 713:** Blending is the usual source-alpha blend, in display values over the image.
3. **Line 715:** The depth test is on only for world canvases, passes with greater-or-equal (the depth is reversed), and never writes depth.
4. **Lines 716–717:** With a jittered depth, the world pipeline adds a bias toward the camera, so a canvas on a wall does not flicker against it.

Binding sets are keyed by the four atlas textures, and one that no draw used in a frame is released. A buffer that grows is replaced, and :term[command lists]{id=command-list} :term[in flight]{id=in-flight} still hold the old one. The draw itself is short.

```cpp src="Strata/src/Strata/GameUI/GameUIRenderer.cpp#L788-L799"
RenderData::UIDrawParameters parameters;
parameters.ViewportSize = m_ViewportSize;
parameters.Origin = m_ScreenOrigin;
parameters.Scale = run.Scale;
parameters.Flags = (run.PixelSnap ? RenderData::c_UIDrawPixelSnap : 0u)
	| (run.World ? RenderData::c_UIDrawWorld | (run.Transform << RenderData::c_UIDrawTransformShift) : 0u);
parameters.FirstQuad = run.FirstQuad;
parameters.FirstClip = run.FirstClip;
parameters.Fonts = run.Fonts;
parameters.GlyphBases = run.GlyphBases;
commandList->setPushConstants(&parameters, sizeof(parameters));
commandList->draw(nvrhi::DrawArguments().setVertexCount(6).setInstanceCount(run.QuadCount).setStartInstanceLocation(run.FirstQuad));
```

1. **Line 789:** The viewport and the canvas's origin and scale tell the shader how canvas units become pixels.
2. **Lines 792–793:** Flags enable pixel snapping, mark a world canvas, and carry the index of its transform in the upper bits.
3. **Lines 794–797:** The run's first quad, the canvas's first clip rectangle, and which fonts sit in which atlas slots.
4. **Line 799:** Six vertices, one instance per quad, and the :term[first instance]{id=first-instance} is the run's first quad. There is no vertex buffer.

The calls run inside a GPU stage called GPU.UI and a CPU stage called Render.UI, so the frame profiler shows the UI's cost on its own.

### What the pass reports

`SceneOverlayStats`, in `SceneRendererStats::Overlays`, holds what the pass did in a frame. The fields are canvases drawn and hidden, elements, quads (empty slots included), draw calls, glyphs still waiting for the frame's glyph budget, assets still loading, and bytes uploaded. It sits beside the `GameUISceneStats` of [The UI contract](../ui/contract.md), which count the scene's work. The GPU tests read it to show one draw call per canvas and an idle frame that uploads nothing. The editor command `viewport.capture` returns some of it as `ui` and waits while UI glyphs are pending, so a capture does not show half-drawn text.

### The vertex shader

The vertex shader runs six times per quad. It finds its quad by the instance number and the corner by the remainder of its vertex number divided by 6.

```slang src="Strata/shaders/GameUI/UIQuad.vert.slang#L43-L57"
UIQuad quad = u_Quads[st_InstanceIndex];
uint kind = quad.Flags & UI_QUAD_KIND_MASK;
if (kind == UI_QUAD_HIDDEN)
{
	Hide();
	return;
}
float2 corner = c_Corners[st_VertexIndex % 6];
// A world-space canvas stays in canvas units (its transform places it) and never snaps.
bool world = (u_Draw.Flags & UI_DRAW_WORLD) != 0u;
bool snap = !world && (u_Draw.Flags & UI_DRAW_PIXEL_SNAP) != 0u;
float scale = world ? 1.0 : u_Draw.Scale;
float2 origin = world ? float2(0.0) : u_Draw.Origin;
float2 minimum = quad.Rect.xy * scale + origin;
float2 maximum = quad.Rect.zw * scale + origin;
```

1. **Line 43:** The quad is read from the buffer by instance index, the method called vertex pulling.
2. **Lines 45–49:** A hidden quad moves all its vertices to one point, a degenerate triangle that rasterizes nothing.
3. **Line 50:** Six fixed corners make two triangles.
4. **Lines 52–57:** A world canvas stays in canvas units and never snaps. A screen canvas multiplies by its scale and adds its origin to get pixels.

The next fragment shows the part that makes text crisp. An image's edges are rounded to whole pixels, and a glyph moves with its baseline.

```slang src="Strata/shaders/GameUI/UIQuad.vert.slang#L84-L91"
if (snap)
{
	// The whole glyph moves with its baseline onto a whole pixel, so glyphs keep their shapes.
	float baseline = quad.UV.y * scale + origin.y;
	float offset = round(baseline) - baseline;
	minimum.y += offset;
	maximum.y += offset;
}
```

**Pixel snapping** moves a rect's edges and a glyph's baseline onto whole pixels before drawing. With the scale 1.3, a rect from x = 11 to x = 21 canvas units covers 14.3 to 27.3 pixels. Without snapping, the first and last pixel columns blend and the rect looks soft. Snapped, its edges are 14 and 27, so the rect is exactly 13 pixels wide with sharp edges. A glyph keeps its shape: snapping moves the whole glyph by the rounding of its baseline, never one edge alone.

The vertex shader then applies the clip rectangle. It finds the quad's clip in the clip buffer, converts it to pixels (snapped like the rects), and hides the quad when it lies wholly outside. For a quad that is only partly inside, it passes the rectangle and the softness to the fragment shader.

```slang src="Strata/shaders/GameUI/UIQuad.vert.slang#L138-L142"
v_World = world ? 1u : 0u;
if (world)
	st_Position = mul(u_Transforms[u_Draw.Flags >> UI_DRAW_TRANSFORM_SHIFT], float4(position, 0.0, 1.0));
else
	st_Position = float4(UVToNDC(position / u_Draw.ViewportSize), 0.5, 1.0);
```

1. **Lines 139–140:** A world canvas multiplies the position by its transform from the transform buffer, which gives :term[clip space]{id=clip-space} directly.
2. **Line 142:** A screen canvas converts the pixel position to :term[normalized device coordinates]{id=normalized-device-coordinates}, with the depth fixed at 0.5.

### The fragment shader

The fragment shader colors each pixel. It handles two kinds: an image and a glyph. An image's corners come from a :term[signed distance]{id=signed-distance}: the distance from the pixel to the edge of a rounded rectangle, negative inside.

```slang src="Strata/shaders/GameUI/UIQuad.frag.slang#L93-L97"
float unitsPerPixel = v_World != 0u ? max(max(fwidth(v_Local.x), fwidth(v_Local.y)), 1e-6) : 1.0;
float radius = min(v_Parameters.x, min(v_HalfSize.x, v_HalfSize.y));
float2 q = abs(v_Local) - (v_HalfSize - radius);
float distanceToEdge = (length(max(q, float2(0.0))) + min(max(q.x, q.y), 0.0) - radius) / unitsPerPixel;
float coverage = clamp(0.5 - distanceToEdge, 0.0, 1.0);
```

1. **Line 93:** A screen canvas measures in pixels already. A world canvas measures in canvas units, and `fwidth` (how much the value changes across one pixel) tells how many units one pixel spans.
2. **Line 94:** The radius cannot exceed half the rect's shorter side.
3. **Line 95:** `q` is the pixel's distance past the straight part of the edge, measured in each axis.
4. **Line 96:** The distance to the rounded edge, divided by units per pixel.
5. **Line 97:** Coverage ramps from 1 to 0 over one pixel around the edge.

A worked check: a pixel whose center is 0.5 pixel inside the edge has a distance of -0.5, so its coverage is 0.5 - (-0.5) = 1. At the edge the distance is 0 and the coverage 0.5. A pixel 0.5 outside has coverage 0. That one-pixel ramp smooths the edge, and no texture is needed.

A border works the same way: the distance plus the border width gives a second ramp, and the color mixes from the border color to the fill inside it. With a border of 2 pixels, a pixel whose center is 1 pixel inside the edge has `inner = clamp(0.5 - (-1 + 2), 0, 1) = 0`, so it is pure border color.

For a texture, the shader reads the slot table by the quad's texture index and samples the bindless texture. A gray texture reads as (r, r, r, 1). The card decodes an sRGB texture when sampling, so the shader receives linear values. The shader converts them back to display values with `LinearToSRGB`, so the blend happens in the numbers the screen shows. A UI blended in linear :term[high dynamic range]{id=high-dynamic-range} (HDR) instead would not match the colors a designer picked in a paint program.

A glyph reads the distance from the atlas, and `SDFCoverage` turns it into coverage. An outline is a second threshold, lower than the edge's value by `OutlineWidth`: the outer shape's coverage selects the outline color, and the fill's coverage selects the glyph color over it. The code clamps the outline width to 0.1 em, because the field holds distances only a short way past the edge.

Masks come last. The shader computes how much of the pixel the clip rectangle leaves.

```slang src="Strata/shaders/GameUI/UIQuad.frag.slang#L49-L58"
float ClipCoverage()
{
	if (v_ClipRect.z < v_ClipRect.x)
		return 1.0;
	// On the screen the pixel's center, in the scene the point of the canvas the pixel shows.
	float2 pixel = v_World != 0u ? v_Position : st_FragCoord.xy;
	float inside = min(min(pixel.x - v_ClipRect.x, v_ClipRect.z - pixel.x), min(pixel.y - v_ClipRect.y, v_ClipRect.w - pixel.y));
	if (v_ClipSoftness > 0.0)
		return clamp(inside / v_ClipSoftness, 0.0, 1.0);
	return inside > 0.0 ? 1.0 : 0.0;
```

1. **Line 51:** A quad with no clip has a rectangle whose right edge lies left of its left edge, which the shader reads as "no clip".
2. **Line 54:** On the screen, the pixel's center decides. In the world, the point of the canvas the pixel shows decides.
3. **Line 55:** `inside` is the distance from that point to the nearest clip edge, positive inside.
4. **Lines 56–57:** With **softness**, the distance in canvas units over which a clip edge fades, coverage ramps from 0 at the edge to 1 at one softness inside.
5. **Line 58:** With no softness, a pixel is in or out.

With a softness of 20 units at scale 1, a pixel 5 units inside the clip's edge has coverage 5 / 20 = 0.25, and a pixel 20 or more inside has 1. The credits of the Third-Person sample scroll in a mask, and a softness above 0 lets the lines fade at the top and bottom instead of being cut.

The last lines of the shader are the ones to read slowly.

```slang src="Strata/shaders/GameUI/UIQuad.frag.slang#L114-L119"
float clipCoverage = ClipCoverage();
float4 shaded = uint(v_Parameters.z + 0.5) == UI_QUAD_GLYPH ? ShadeGlyph() : ShadeImage();
float alpha = shaded.a * clipCoverage;
if (alpha <= 0.0)
	discard;
o_Color = float4(shaded.rgb, alpha);
```

1. **Line 114:** The clip coverage is computed first and stored, with no early exit.
2. **Line 115:** Both shading paths run in uniform control flow, since the kind is the same for the whole quad.
3. **Line 116:** The clip multiplies the alpha.
4. **Lines 117–118:** The one discard comes last and drops pixels with no alpha.

Why multiply and not discard early? The card shades pixels in groups of 2 by 2, and derivatives (such as `fwidth` and the texture's level of detail) compare a pixel with its neighbours in the group. A discard that differs inside a group leaves the derivatives of the other pixels undefined. A soft mask edge could then break the texture's mip level or the glyph's smoothness. Computing everything first, then multiplying, keeps every pixel's neighbours alive, at the cost of a few wasted operations for pixels that are discarded.

### World-space canvases on the GPU

A world-space canvas is a plane in the scene. `GetCanvasWorldMatrix` builds its matrix in four steps. It moves the canvas's :term[pivot]{id=pivot-ui} to the origin and scales by the canvas's world units per unit, 0.01 by default, so 100 canvas units are one meter. It then flips +Y, so that canvas-down becomes world-down, and applies the entity's :term[world transform]{id=world-transform}. A canvas of 400 by 200 units is a sign of 4 by 2 meters.

The renderer draws these canvases in the scene's camera-relative space, the idea of [Camera-relative rendering](../draw/mirrors-camera-relative.md): the scene's depth was drawn with positions relative to the camera, so the canvas must be too.

```cpp src="Strata/src/Strata/GameUI/GameUIRenderer.cpp#L374-L378"
m_ViewTransforms[index] = static_cast<uint32_t>(m_Transforms.size());
// Relative to the camera (the subtraction in double), as the scene's depth the canvas is tested against was drawn.
glm::mat4 relative = ui.GetCanvasWorldMatrix(views[index]);
relative[3] = glm::vec4(glm::vec3(glm::dvec3(glm::vec3(relative[3])) - glm::dvec3(frame.CameraPosition)), relative[3].w);
m_Transforms.push_back(frame.ViewProjection * relative);
```

The matrix's translation (its fourth column) is converted to double, the camera's position is subtracted, and the result is converted back. The subtraction in double keeps a canvas that is 100 km from the origin as precise as one at the origin, and the `GPU.GameUI` suite has a test for exactly that distance. The view-projection matrix times this relative matrix is what the shader's transform buffer holds.

Four more properties follow. The fragment shader finds how many units a pixel spans with `fwidth`, so rounded corners and borders keep smooth edges in perspective, where one canvas unit covers different pixel counts at different places. Mip streaming gets its pixel count from `GetProjectedUnitPixels`, which projects a point and its neighbours one unit right and down and measures the distances. The depth test uses the scene's depth read-only, so a canvas hides behind nearer geometry and writes nothing itself. With temporal anti-aliasing the pipeline adds a depth bias, as shown above, so the canvas is stable in every jitter phase, which a test checks.

World canvases are drawn after post-processing, so no light, bloom or tone mapping changes them. The scene's world transform places them, which is the last :term[fixed step's]{id=fixed-step} pose, not the drawn one. A name tag on an interpolated body therefore moves in fixed steps against it ([Interpolation](../world/interpolation.md)). No sample has a world canvas; the tests have two, and the feature scene's has 0.005 meters per unit.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| A draw call per element | Simple immediate tools | No quad array, no journal and no tables | Calls grow with the element count; text of hundreds of glyphs costs hundreds of calls |
| Vertex buffer rewritten every frame | Many immediate-mode libraries, such as Dear ImGui | Simple accounting, no journal or lookup tables | Every frame copies the whole UI, even a static menu |
| Scissor rectangles per mask | Dear ImGui and many engines for rectangular clips | Hardware clipping, no per-pixel clip work | One draw per distinct clip, so a list with many masks splits the canvas; no soft edges |
| `Stencil` masks | Unity's Mask component, Unreal's Slate for rotated clips | Clips of any shape | Extra draws and an extra buffer, and batches split when masks change |
| One mesh per canvas on the processor | Unity's canvas batching | A normal vertex buffer, no shader changes | Meshes rebuilt on change; no pulling of data from tables |
| Lit world-space UI | Engines that render UI as scene meshes | Shadows and light on world canvases | Cost per light, and the UI loses its crisp display-value look |

The sources are in Further reading. What Strata loses in each row is what it gains elsewhere: a rectangle-only clip, a limit of 256 fonts and four atlases per call, and a world canvas without light.

## How it is tested

The `GPU.GameUI` suite in `StrataTests/src/Renderer/GPUGameUITests.cpp` renders canvases on the shared test device and reads pixels back. It covers the placement of rects at the same fraction of every screen, with edges on whole pixels. It covers images drawn solid, filled, rounded with borders and nine-sliced, in exact display colors, and text with an outline. Another test shows that an idle frame uploads nothing and that a canvas of up to four fonts is one draw call.

Further tests check the GPU.UI stage, hidden screen canvases and the UI shown over black, masks with soft edges, and an edited input field. Others draw a world canvas in perspective behind nearer geometry, and the same canvas 100 km from the origin. One checks that a canvas on a wall under temporal anti-aliasing covers the same pixels in every jitter phase. The last tests cover the screen view, mip streaming for screen and world canvases, the Tetris heads-up display (HUD) at two resolutions, and the release of buffers and atlases when frames stop drawing UI.

Every test ends by checking that the device reported no new error, as the GPU suites do. Run the suite with the GPU tests of a build, for example `build/windows/bin/Debug/StrataTests.exe --test-suite=GPU.GameUI` on a machine with a GPU. A change to the sample's look needs the feature test, which loads a scene with a world canvas.

## Changing it safely

The extension points are few. A new kind of drawn thing is a new quad kind in `c_UIQuadKindMask`'s two bits (one value is left), a new flag bit, or a new field in the 4 padding bytes. A new image option is a field of `UIImageComponent`, handled in `WriteElementQuads` and, if it changes pixels, in `ShadeImage`.

Follow these rules, each with its reason.

- Keep `UIQuad` at 64 bytes and change the C++ and the shader structs in one commit. The `static_assert` guards the size only, so a difference between the two files passes the build and fails on screen.
- Never put a bindless slot or an atlas position into a quad. Both move while the game runs.
- Keep clipping in the shader. A split draw per mask is the cost the design avoids.
- Never discard before the last line of the fragment shader. Derivatives of the rest of the group go undefined.
- Request assets per distinct texture or font, never per element, and never block on a load.
- Write component fields with `MarkModified` or `registry.patch`, so the layout and the journal see the change (the rule of [The UI contract](../ui/contract.md)).
- Add a shader entry to `strata_add_shaders` in `Strata/CMakeLists.txt`, and run the :term[configure step]{id=configure-step} again.
- A change of the look must keep `GPU.GameUI` passing, and a new component field must appear in the feature test.

The checks to pass are the `GPU.GameUI` suite, the `Architecture.Layering` test (the renderer must not include the module), and the feature test.

## Summary

- A button's components become quads in `GameUIScene`, the pass uploads the changed quads, and the vertex and fragment shaders draw them, over the image or in the world.
- A canvas is one instanced call of six vertices per quad with no vertex buffer; every canvas is its own run, and only more than four fonts split a canvas into more runs.
- An edit rewrites its slot in the quad buffer, the journal records the range, and the pass uploads that range of 64-byte quads; an idle frame uploads nothing.
- A nine-slice has up to nine quads whose borders shrink together when the rect is small, and a filled image cuts the rect and its UVs by the same fraction.
- Masks clip in the shader through a clip index on each quad, and the single discard comes last so derivatives stay defined.

## Check yourself

1. A label has 8 glyphs. How many quads does its slot hold, and what happens when the text becomes 11 glyphs?
   - A. 8 quads; the 11 glyphs are drawn from a second slot.
   - B. 12 quads (8 + 4); 11 glyphs fit, so only the slot is rewritten.
   - C. 10 quads (8 + 2); 11 glyphs do not fit, so the array is rebuilt.

   :::answer{tests="upload-edit"}
   B. The capacity is the glyphs plus a quarter of them, at least four more: 8 + max(4, 2) = 12. The text of 11 glyphs fits, so only the slot is rewritten, and its 12 quads (768 bytes) are the changed range. A is wrong, because an element has one slot. C uses a quarter alone and forgets the minimum of four.
   :::

2. The Play button's tint fades for 0.1 seconds. A frame of the fade changes its image. Which buffer does the frame upload, and about how many bytes?

   :::answer{tests="upload-edit,trace-button"}
   The quad buffer, one range of the button's slot: its nine-slice image is 9 quads, so 9 × 64 = 576 bytes. The test in `GPUGameUITests.cpp` allows 16 quads for one label's color change, so the fade stays below that. The journal records the range, the pass merges it and calls `writeBuffer`. The slot tables and the glyph table do not change.
   :::

3. A canvas uses fonts A, B, C, D and E in that order of first appearance. How many draw runs does it have, and where does the second begin?
   - A. One, because a canvas is one draw.
   - B. Two, beginning at the first glyph of E.
   - C. Five, one per font.

   :::answer{tests="one-draw"}
   B. A run binds at most four atlases. The first glyph whose font cannot be bound (E) ends the run, and a second run starts there. A is wrong for five fonts, and C is wrong because a run holds up to four fonts.
   :::

4. A nine-slice texture is 32 by 32 texels with borders of 8, and `SliceScale` is 2. How many quads and what x positions does a rect of 100 units wide at x = 0 produce, if it is tall enough?

   :::answer{tests="slice-cut"}
   The borders are 8 × 2 = 16 units, and 32 is below 100, so nothing shrinks. The x positions are 0, 16, 84 and 100. With three rows the panel has 9 quads. The texture coordinates are cut at 8 / 32 = 0.25 and 0.75.
   :::

5. A health bar, 150 units wide at x = 20, is filled to 0.4 from right to left. What are its rect's left edge and its UV's left edge, for a UV rectangle of (0, 0, 1, 1)?

   :::answer{tests="slice-cut"}
   The right edge stays at 170. The left edge moves to 170 - 150 × 0.4 = 110, and the UV's left edge to 1 - 1 × 0.4 = 0.6. Only the right 40 % of the picture shows, at its own size.
   :::

6. A masked list scrolls, and a fragment shader author moves the clip test to the top, with `discard` as soon as the pixel lies outside. What goes wrong?

   :::answer{tests="clip-shader"}
   Pixels in the same 2 by 2 group may disagree about the discard, and the derivatives that the texture sampling, the glyph coverage and `fwidth` use then become undefined for the rest. Pixels at the mask's edge would show wrong mip levels or ragged text. The shader multiplies the clip into the alpha and discards once at the end for that reason.
   :::

## Exercises

1. **Basic.** Trace it yourself: with a source build, find the code that decides which part of the quad buffer one frame of the Play button's fade uploads.

   :::answer[Worked solution]{tests="trace-button,upload-edit"}
   Put a breakpoint in `GameUIRenderer::UploadQuads` in `Strata/src/Strata/GameUI/GameUIRenderer.cpp`, and move the pointer onto the Play button of the Third-Person main menu. In the loop over the views, `GetQuadChanges` returns the journal's ranges since the last upload, the sort and merge leave one or two ranges, and `writeBuffer` copies each one. The value that `stats.UploadedBytes` then holds is 64 bytes per changed quad, 576 for the button's 9 nine-slice quads. After the fade ends, the version equals the uploaded one, no range is written and the bytes are 0.
   :::

2. **Medium.** Write a function that gives the coverage of the pixels on a rounded rectangle's diagonal, as the fragment shader does. Use a 20 by 20 pixel rect with the radius 6, and print the distance and the coverage of the first four pixel centers from the corner.

   :::answer[Worked solution]{tests="slice-cut,clip-shader" solution="sketches/ui-drawing-coverage.cpp"}
   The function copies the shader's lines: clamp the radius, take the distance past the straight edge on each axis, add the length of the positive parts and the inner distance, and subtract the radius. Coverage is 0.5 minus the distance, clamped to 0 to 1.

   ```cpp sketch="ui-drawing-coverage.cpp"
   #include <algorithm>
   #include <cmath>
   #include <cstdio>

   // The fragment shader's rounded rect: the signed distance of a pixel center to the edge, and the coverage it gives.
   float GetDistance(float localX, float localY, float halfX, float halfY, float radius)
   {
   	radius = std::min(radius, std::min(halfX, halfY));
   	const float qx = std::fabs(localX) - (halfX - radius);
   	const float qy = std::fabs(localY) - (halfY - radius);
   	const float outside = std::sqrt(std::max(qx, 0.0f) * std::max(qx, 0.0f) + std::max(qy, 0.0f) * std::max(qy, 0.0f));
   	return outside + std::min(std::max(qx, qy), 0.0f) - radius;
   }

   float GetCoverage(float distance)
   {
   	return std::clamp(0.5f - distance, 0.0f, 1.0f);
   }

   int main()
   {
   	// A 20 by 20 pixel rect with corner radius 6: the pixel centers on its diagonal, from the corner inward.
   	for (int pixel = 0; pixel < 4; pixel++)
   	{
   		const float local = -10.0f + static_cast<float>(pixel) + 0.5f;
   		const float distance = GetDistance(local, local, 10.0f, 10.0f, 6.0f);
   		std::printf("pixel %d: distance %.3f, coverage %.3f\n", pixel, distance, GetCoverage(distance));
   	}
   	return 0;
   }
   ```

   ```text output-of="ui-drawing-coverage.cpp"
   pixel 0: distance 1.778, coverage 0.000
   pixel 1: distance 0.364, coverage 0.136
   pixel 2: distance -1.050, coverage 1.000
   pixel 3: distance -2.464, coverage 1.000
   ```

   1. **Lines 6–12:** The distance copies the shader: the radius is clamped, `qx` and `qy` are the distances past the straight part of the edge, and the rounded corner adds their length.
   2. **Line 17:** Coverage is 0.5 minus the distance, clamped to the range 0 to 1.
   3. **Lines 23–26:** The loop visits the pixel centers on the diagonal, from the corner inward.

   The first pixel lies outside the curve and has coverage 0. The second is at 0.364 outside the edge, so it is a fraction of a pixel, and the third, 1.05 inside, is fully covered. The ramp around the edge smooths it.
   :::

3. **Hard.** Add a fill direction `Radial360` that shows a pie, clockwise from the top, with `UIQuad` kept at 64 bytes. Describe the data, the shader path and the tests.

   :::answer[Worked solution]{tests="one-draw,clip-shader"}
   Add the value to `UIFillDirection` and handle it in the image part of `WriteElementQuads`. The cut of the rectangle does not apply, so the quad keeps the whole rect and carries the fill amount itself. `UIQuad` has no free float, but the 4 bytes of `Padding` and the unused bits of `Flags` are free. Store the fill as a number of steps in 16 bits of `Padding`, and mark the quad with a new flag bit above the font bits.

   Add the same field and bit to `UIQuad.slang`, and read them in `ShadeImage`. Compute the angle of `v_Local` from the top, clockwise, and multiply the coverage by 0 where the angle exceeds the fill times a full turn. Add an :term[inactive reason]{id=inactive-reason} on the fill amount for other types, a unit test of the quads, a pixel test in `GPU.GameUI` for 0.25 and 0.75, and a use in the feature test.
   :::

## Where it lives in Strata

- Quads and slots: `Strata/src/Strata/GameUI/GameUIRenderData.h`, `GameUIQuads.cpp`, `GameUIScene.h`.
- The pass: `Strata/src/Strata/GameUI/GameUIRenderer.cpp` and its :term[header]{id=header}; the registry in `Strata/src/Strata/Renderer/SceneOverlay.h`.
- Shaders: `Strata/shaders/GameUI/UIQuad.vert.slang`, `UIQuad.frag.slang`, `UIQuad.slang`, registered in `Strata/CMakeLists.txt`.
- Tests: the `GPU.GameUI` suite in `StrataTests/src/Renderer/GPUGameUITests.cpp`.
- Commands: `viewport.capture` returns the pass's `ui` counts.

## Further reading

- Dear ImGui documentation and source comments: how a draw list holds vertices, indices and clip rectangles per command (intermediate).
- Unity manual, "Canvas" and "Mask" and "RectMask2D": batching of canvas meshes and the three kinds of clipping (beginner).
- Unreal Engine documentation, "Slate" rendering and clipping: how a widget tree is batched and clipped (intermediate).
- "Real-Time Rendering" (Akenine-Möller and others), the chapters on blending and alpha: coverage and why edges need it (advanced).
- Valve, "Improved Alpha-Tested Magnification for Vector Textures and Special Effects": the distance-field text that the glyphs use (advanced).
