---
id: ui/text
title: "Text and text fields"
description: "How a UI text gets its shaped lines from its rect, and how a player types one line of text into an input field."
kind: internals
size: M
tracks: [E]
needs: [ui/layout, ui/input, gpu/text, input/devices-state]
time: 65
learn:
  - id: rect-to-options
    text: explain how a rect's size, wrap setting and overflow mode become the options of shaping
  - id: scroll-line
    text: compute how far a field's line scrolls to keep the caret in view
  - id: utf8-boundaries
    text: trace how Backspace removes one whole character from UTF-8 text
  - id: key-to-field
    text: trace a key press from the input system to a changed field
  - id: map-while-editing
    text: predict which keys and gamepad actions still act while a field is edited
since: 0.4.0
status: final
---

Every text in a game's interface needs lines: which words stand on which line, how wide each line is, and where the text may not go. The game user interface (UI) module gives every text element those lines from the element's rect. It also lets a player type one line of text into an input field. It never draws a glyph: fonts, shaping and the glyph atlas belong to [the text page](../gpu/text.md) of the :term[graphics processing unit]{id=gpu} (GPU) part. The quads for glyphs, caret and selection belong to [the drawing page](../ui/drawing.md).

## The problem and how engines solve it

A button that fits its label must know the label's width, and a label that wraps must know where its lines break. Layout asks these questions before any picture exists, and often without a window: commands and tests run headless. The answer needs only the advance of each glyph, the distance the pen moves after it. Pixels would only tie layout to the glyph atlas and its budget. [The text page](../gpu/text.md) shows how Strata shapes from metrics and draws later.

An input field adds a second problem: text that the player changes. The engine must remember a place in the text and move it over characters that take several :term[bytes]{id=byte}. It must also show that place when the text is wider than the field. The rest of this page builds both parts, text in a rect and the field, from the smallest idea up.

## The map

`Strata/src/Strata/GameUI/GameUIText.cpp` holds the shaping side. It reads the rect and the text element, and it calls `ShapeText` and `MeasureCaretStops` of `Strata/src/Strata/Renderer/TextLayout.h`. `Strata/src/Strata/GameUI/GameUISystem.cpp` holds the editing side: keys, :term[typed text]{id=typed-text} and clicks. The two meet in the `GameUIScene`, which keeps the editing state of the one field being edited.

```mermaid caption="Who calls whom. Layout and drawing ask the scene for shaped text. The scene shapes from font metrics through the text layout header. The system reads the keyboard and the pointer, changes the field and tells the scene its caret." alt="A flow chart with boxes. Layout and quad building point to the game UI scene. The scene points to the text layout functions, which read font metrics. The game UI system points to the input class for keys and typed text, to the field component, and to the scene with the caret and anchor."
flowchart LR
  Layout["Layout and quads"] --> Scene["GameUIScene: GameUIText.cpp"]
  Scene --> Shape["ShapeText, MeasureCaretStops: TextLayout.h"]
  Shape --> Face["FontFace metrics"]
  System["GameUISystem: editing"] --> Input["Input: keys, typed text"]
  System --> Field["UIInputField component"]
  System --> Scene
```

A text element carries a `UIText` component: the text, a font asset, a size in :term[canvas units]{id=canvas-unit} per :term[em]{id=em}, a color, alignments, a wrap switch, an overflow mode, a line spacing and an outline. A text receives the pointer only when you switch its :term[raycast target]{id=raycast-target} on. An input field carries a `UIInputField` component: the text, the element that shows it, a placeholder element, a limit in characters, the colors of caret and selection. An :term[event target]{id=event-target} also hears the submit.

## The contract

- **Layout never rasterizes a glyph.** Shaping reads a font face's metrics only. Layout runs headless, in commands and tests, and it must not depend on the atlas or on how much of it the frame may fill.
- **A field's text element is a `UIText`, and the field has a mask.** The text element draws the text, the caret and the selection. A line that scrolls would otherwise spill out of the field.
- **A field has a `UISelectable` on its own entity.** Only :term[selectables]{id=selectable} take the focus, and editing starts when the focused selectable also holds a field. A field built by hand without one never takes the keyboard.
- **A change of text is a signalled change.** The system writes a field with `registry.patch`, so layout and drawing see it.

:::rule
**Never block a frame on an asset.** A text that waited for its font would stall the frame. The default font stands in while the font loads, and Strata shapes the text again when the font arrives. [The residency page](../assets/residency.md) teaches how assets load later.
:::

The Input Field preset (**Hierarchy**, the plus button, **UI**, **Input Field**) builds a field that follows all of these rules. It adds the selectable, the mask, a text element and a placeholder element.

## A toy version

The toy keeps one line: the text, a caret as a byte offset and a scroll. It supports typing and `Backspace`. Every character is 10 units wide, the box is 50 units wide and the caret is 2 units wide. It prints the field after each step, so you can predict each line before you run it.

:::question
New to C++? The sketch uses :term[structs]{id=struct}, functions, strings and calls such as `text.insert(`. Read [the third programming page](../basics/programming-3.md) first.
:::

The sketch shows the two ideas of the page: move over :term[UTF-8]{id=utf-8} by whole characters, and scroll so the caret stays in the box. The character "é" takes two bytes in UTF-8, so one `Backspace` must remove both.

```cpp sketch="ui-text-toy.cpp"
#include <cstdint>
#include <cstdio>
#include <string>

constexpr float c_CharacterWidth = 10.0f;
constexpr float c_BoxWidth = 50.0f;
constexpr float c_CaretWidth = 2.0f;

struct ToyField
{
	std::string Text;
	uint32_t Caret = 0; // A byte offset, always on a character boundary
	float Scroll = 0.0f;
};

bool IsContinuationByte(char byte)
{
	return (static_cast<uint8_t>(byte) & 0xC0) == 0x80;
}

uint32_t PreviousBoundary(const std::string& text, uint32_t position)
{
	if (position == 0)
		return 0;
	uint32_t index = position - 1;
	while (index > 0 && IsContinuationByte(text[index]))
		index--;
	return index;
}

// Where the caret stands on the line: every character is the same width here.
float CaretX(const ToyField& field)
{
	float x = 0.0f;
	for (uint32_t index = 0; index < field.Caret; index++)
	{
		if (!IsContinuationByte(field.Text[index]))
			x += c_CharacterWidth;
	}
	return x;
}

void KeepCaretInView(ToyField& field)
{
	const float caret = CaretX(field);
	if (caret < field.Scroll)
		field.Scroll = caret;
	if (caret + c_CaretWidth - c_BoxWidth > field.Scroll)
		field.Scroll = caret + c_CaretWidth - c_BoxWidth;
}

void Insert(ToyField& field, const std::string& typed)
{
	field.Text.insert(field.Caret, typed);
	field.Caret += static_cast<uint32_t>(typed.size());
	KeepCaretInView(field);
}

void Backspace(ToyField& field)
{
	const uint32_t start = PreviousBoundary(field.Text, field.Caret);
	field.Text.erase(start, field.Caret - start);
	field.Caret = start;
	KeepCaretInView(field);
}

void Print(const char* step, const ToyField& field)
{
	std::printf("%-12s text=\"%s\" bytes=%zu caret=%u scroll=%.0f\n", step, field.Text.c_str(), field.Text.size(), field.Caret, field.Scroll);
}

int main()
{
	ToyField field;
	Insert(field, "ab");
	Insert(field, "\xC3\xA9"); // e with an acute accent: two bytes, one character
	Print("type ab, e'", field);
	Backspace(field);
	Print("backspace", field);
	Insert(field, "cdefg");
	Print("type cdefg", field);
	return 0;
}
```

1. **Line 18:** `& 0xC0` keeps only the byte's top two bits, and `0x80` is the pattern `10` followed by zeros: a continuation byte has the bits `10` on top, so it never starts a character.
2. **Line 26:** `PreviousBoundary` steps back one byte, then over every continuation byte, and lands on the first byte of the previous character.
3. **Lines 48–49:** the scroll follows the caret to the right when the caret passes the box's right edge.
4. **Line 62:** `Backspace` erases the bytes between the previous boundary and the caret.

```text output-of="ui-text-toy.cpp"
type ab, e'  text="abé" bytes=4 caret=4 scroll=0
backspace    text="ab" bytes=2 caret=2 scroll=0
type cdefg   text="abcdefg" bytes=7 caret=7 scroll=22
```

Read the output. After `ab` and "é" the text has four bytes and three characters, and the caret is at byte 4. The caret is 30 units along the line, so the box of 50 units needs no scroll. `Backspace` removes two bytes and leaves `ab`. After `cdefg` the caret is 70 units along, and the scroll is 70 + 2 - 50 = 22 units.

## The real code

The parts below follow the data: first a text in its rect, then the field.

### A text in its rect

A shaped text is a list of positioned lines in em units, the font's own square. Strata shapes a text when the text, its font or the options of its rect change, and keeps the result per element and per layout. A fitted rect is measured with the options that drawing uses, so one shaping serves both.

:::example
**A label in a 300 by 80 rect.** A `UIText` has a font size of 32 canvas units per em, wrap on, the overflow mode Ellipsis and a rect of 300 by 80 units that does not fit its content. The wrap width is 300 / 32 = 9.375 em. The text wraps, so the maximum width is 0. The box height is 80 / 32 = 2.5 em, so lines that do not fit in 2.5 em are omitted and the last line shown ends in three dots.

Now switch wrap off and make the rect 200 units wide. The wrap width becomes 0, so a long line stays whole. The maximum width is 200 / 32 = 6.25 em, and glyphs that cross it are cut.
:::

The two functions below turn a rect into options. Search for the division by the font size and for the three conditions that decide the maximum width and the box height.

```cpp src="Strata/src/Strata/GameUI/GameUIText.cpp#L65-L89"
TextShapeOptions GameUIScene::GetMeasureOptions(const UITextComponent& text, float wrapWidth) const
{
	// The options a fitted rect measures its text with, and the same ones it is drawn with (so it is shaped once): the
	// block placed at the top, wrapped only when the width does not fit the text.
	TextShapeOptions options;
	options.Alignment = text.Alignment;
	options.VerticalAlignment = TextVerticalAlignment::Top;
	options.WrapWidth = wrapWidth;
	options.LineSpacing = std::clamp(text.LineSpacing, 0.5f, 3.0f);
	options.Overflow = ToOverflowMode(text.Overflow);
	return options;
}

TextShapeOptions GameUIScene::GetShapeOptions(const UITextComponent& text, const UIRectComponent* rect, const UIBox& box) const
{
	const float fontSize = std::clamp(text.FontSize, 1.0f, 1024.0f);
	const bool fitsWidth = rect && (rect->FitContent == UIFitContent::Width || rect->FitContent == UIFitContent::Both);
	const bool fitsHeight = rect && (rect->FitContent == UIFitContent::Height || rect->FitContent == UIFitContent::Both);
	const bool cuts = text.Overflow != UITextOverflow::Overflow;
	// A rect that fits the text's width holds it unwrapped; one that fits its height holds every line.
	TextShapeOptions options = GetMeasureOptions(text, text.Wrap && !fitsWidth ? box.Size.x / fontSize : 0.0f);
	options.MaxWidth = cuts && !text.Wrap && !fitsWidth ? box.Size.x / fontSize : 0.0f;
	options.BoxHeight = cuts && !fitsHeight ? box.Size.y / fontSize : 0.0f;
	return options;
}
```

1. **Line 73:** the line spacing stays between 0.5 and 3 times the font's line height, so a bad value cannot collapse or explode a block.
2. **Line 85:** a text wraps at the rect's width in em, unless the rect fits its width and holds the line whole.
3. **Line 86:** with Truncate or Ellipsis and no wrap, a maximum width cuts each line at the rect's width.
4. **Line 87:** with Truncate or Ellipsis, a box height keeps only the lines that fit, unless the rect fits its height.

The **ellipsis** (also called truncate) is the overflow mode where text that does not fit is cut. Ellipsis ends the last line kept with three dots, and Truncate shows no mark. The default mode, Overflow, draws everything, even outside the rect.

::figure{id=text-overflow}

The shape cache comes next. Strata uses a cached shaping while the font and every option stay the same. A text whose font still loads is shaped with the engine's default font, and the cache remembers which font it used. When the real font arrives, the remembered font differs from the current one, so Strata shapes the text again.

```cpp src="Strata/src/Strata/GameUI/GameUIText.cpp#L144-L164"
const ShapedText& GameUIScene::ShapeElementText(Layout& layout, uint32_t element, const UITextComponent& text, std::string_view shown,
	const TextShapeOptions& options)
{
	AssetHandle shapedFont;
	const FontFace* face = GetTextFace(text, shapedFont);
	if (m_Validating)
	{
		// A fresh shaping, so that a text written without a signal shows as a difference.
		ShapeText(*face, shown, options, m_ValidateShaped);
		return m_ValidateShaped;
	}
	ElementText& cached = layout.Texts[element];
	if (cached.Valid && cached.ShapedFont == shapedFont && SameOptions(cached.Options, options))
		return cached.Shaped;
	ShapeText(*face, shown, options, cached.Shaped);
	cached.Valid = true;
	cached.Options = options;
	cached.ShapedFont = shapedFont;
	m_Stats.TextsShaped++;
	return cached.Shaped;
}
```

1. **Line 152:** during validation, Strata always shapes fresh, so a text written without a signal shows as a difference.
2. **Line 156:** the cache hits only when the shaped font and every option are the same.
3. **Line 162:** `TextsShaped` counts each fresh shaping, not the cache hits, so a test can check that a text is shaped once for measuring and drawing.

A text asks for its font at High priority, because players read text first.

### The field's line

A field changes three things in the options. Its text is one line that Strata never wraps or cuts, because `GetElementShapeOptions` shapes it with a wrap width of 0 and the Overflow mode. The text shown is the field's `Text`, not the text element's own. A line wider than the box scrolls.

The **caret** is the place between two characters where typed text goes in, drawn as a thin bar.

The **selection anchor** is the other end of a selection: the selection covers the bytes between the anchor and the caret, and when they are equal nothing is selected. Both are byte offsets into the text.

The **placeholder** is the element that shows a hint such as "Enter text..." while the field's text is empty.

```mermaid caption="A field's text of four bytes: the bytes, the caret and the anchor as offsets between them, and the box that scrolls over the line when the line is wider than the box." alt="A row of cells for the bytes of a, b and the two bytes of an accented e, with offsets zero to four. One arrow marks the anchor at offset one and another marks the caret at offset four. A frame marks the box that scrolls over the line."
flowchart LR
  subgraph Bytes["Text bytes, offsets 0 to 4"]
    B0["a: 0-1"] --- B1["b: 1-2"] --- B2["e acute: 2-4"]
  end
  Anchor["anchor = 1"] -.-> B1
  Caret["caret = 4"] -.-> B2
  Box["box: scroll window over the line"] -.-> Bytes
```

`MeasureCaretStops` gives the places a caret can stand: one before each character and one after the last, each with its byte and its distance along the line in em. `PlaceFieldLine` uses them to place the line. Search for the two cases: the line fits, or it is wider and scrolls.

```cpp src="Strata/src/Strata/GameUI/GameUIText.cpp#L111-L142"
glm::vec2 GameUIScene::PlaceFieldLine(const UITextComponent& text, const ShapedText& shaped, const UIBox& box, float size, FieldRecord* record,
	std::span<const TextCaretStop> stops) const
{
	const float place = text.VerticalAlignment == UITextVerticalAlignment::Top ? 0.0f : (text.VerticalAlignment == UITextVerticalAlignment::Middle ? 0.5f : 1.0f);
	const float top = box.Min.y + (box.Size.y - shaped.Height * size) * place;
	const float width = shaped.Width * size;
	const float caretWidth = GetCaretWidth(size);
	if (width + caretWidth <= box.Size.x)
	{
		// It fits: placed by its alignment, like any text.
		if (record)
			record->Scroll = 0.0f;
		const float origin = text.Alignment == TextAlignment::Left ? box.Min.x : (text.Alignment == TextAlignment::Center ? box.GetCenter().x : box.GetMax().x);
		return glm::vec2(origin + shaped.Min.x * size, top);
	}
	// Wider than the element: from its left edge, scrolled so that the caret stays inside.
	float scroll = record ? record->Scroll : 0.0f;
	if (record)
	{
		float caret = 0.0f;
		for (const TextCaretStop& stop : stops)
		{
			if (stop.Byte == record->State.Caret)
				caret = stop.X * size;
		}
		scroll = std::min(scroll, caret);
		scroll = std::max(scroll, caret + caretWidth - box.Size.x);
		scroll = std::clamp(scroll, 0.0f, width + caretWidth - box.Size.x);
		record->Scroll = scroll;
	}
	return glm::vec2(box.Min.x - scroll, top);
}
```

1. **Line 118:** the line must leave room for the caret as well as the text.
2. **Line 122:** when everything fits, the scroll is 0 and the alignment places the line like any text.
3. **Line 136:** the scroll never exceeds the caret's position, so the caret cannot hide at the left.
4. **Line 137:** the scroll is at least the caret's position plus the caret's width minus the box width, so the caret cannot hide at the right.
5. **Line 138:** the scroll stops at the end of the line, so no empty space shows after the last character.

:::example
**A scrolled name field.** The preset's field is 360 units wide with 12 units of padding per side. The text element's box is 336 units wide. The font size is 24, so the caret is max(1, 24 × 0.06) = 1.44 units wide.

A name of 400 units with the caret at its end puts the caret at 400. The scroll is at least 400 + 1.44 - 336 = 65.44 units, and the last rule allows no more. The caret then stands at the right edge.
:::

The scroll lives in a record next to the editing state, so a frame that does not move the caret keeps its scroll. Once the line scrolls, it starts at the left edge, so the field's own alignment matters only while the text fits.

### The editing state

Editing starts in `GameUISystem::Focus`. It ends any earlier editing, and when the new focus holds a field, it begins editing. `BeginEditing` puts the caret and the anchor at the end of the text and switches :term[keyboard capture]{id=pointer-capture} on. The keyboard then belongs to the field, so typing a name never moves the player. Escape or a lost focus ends editing and gives the keyboard back.

The scene holds the state that drawing needs: the caret, the anchor and whether the caret shows this frame. The system updates it every frame through `ShowFieldState`. The caret blinks every 0.53 s: it shows for 0.53 s and hides for 0.53 s. Any change of the text, the caret or the selection restarts the blink with the caret shown.

### Moving over UTF-8

UTF-8 stores a character as one to four bytes. The first byte tells how long the character is, and the other bytes, the continuation bytes, all have the bits `10` on top. A caret inside a character would split it, so every move stops on a boundary. Moving by one byte is the mistake this page warns about: `Backspace` after "é" would leave one stray byte, which is no valid text.

```cpp src="Strata/src/Strata/GameUI/GameUISystem.cpp#L68-L94"
bool IsContinuationByte(char byte)
{
	return (static_cast<uint8_t>(byte) & 0xC0) == 0x80;
}

// Character boundaries of UTF-8 text around a byte.
uint32_t PreviousBoundary(const std::string& text, uint32_t position)
{
	uint32_t index = std::min(position, static_cast<uint32_t>(text.size()));
	if (index == 0)
		return 0;
	index--;
	while (index > 0 && IsContinuationByte(text[index]))
		index--;
	return index;
}

uint32_t NextBoundary(const std::string& text, uint32_t position)
{
	const uint32_t size = static_cast<uint32_t>(text.size());
	if (position >= size)
		return size;
	uint32_t index = position + 1;
	while (index < size && IsContinuationByte(text[index]))
		index++;
	return index;
}
```

1. **Line 70:** a byte is a continuation byte when its top two bits are `10`.
2. **Line 80:** stepping backwards, the loop skips continuation bytes until it reaches the first byte of the character.
3. **Line 91:** going forward, the loop skips the continuation bytes of the character the caret stands before.

The character limit counts the same way. `CountCharacters` counts the bytes that are not continuation bytes, so the limit counts :term[code points]{id=code-point}, not bytes. A limit of 10 holds ten letters and also ten accented letters.

### A key to a changed field

`UpdateEditing` runs once per update while a field is edited. It reads six keys, `Backspace`, `Delete`, `Left`, `Right`, `Home` and `End`, with the repeat timing of the :term[UI actions]{id=ui-map}: on the press, again after 0.4 s held, then every 0.1 s. It reads **Shift** and **Ctrl** (or the Command key on macOS) from the key states. It edits a copy of the text and writes the copy back once. The quote shows the end of the function: typed text, the patch and the two keys that end it.

```cpp src="Strata/src/Strata/GameUI/GameUISystem.cpp#L708-L747"
	// Typed characters replace the selection, as many as the character limit leaves room for.
	const std::string typed = FilterTypedText(Input::GetUncapturedTypedText());
	if (!typed.empty())
	{
		edited = eraseSelection() || edited;
		std::string_view inserted = typed;
		if (field->CharacterLimit > 0)
		{
			const size_t count = CountCharacters(text);
			inserted = TakeCharacters(inserted, count < field->CharacterLimit ? field->CharacterLimit - count : 0);
		}
		if (!inserted.empty())
		{
			text.insert(state.Caret, inserted);
			state.Caret += static_cast<uint32_t>(inserted.size());
			state.Anchor = state.Caret;
			edited = true;
		}
	}

	const entt::entity editedField = m_Editing;
	if (edited && text != field->Text)
		registry.patch<UIInputFieldComponent>(editedField, [&text](UIInputFieldComponent& value) { value.Text = text; });
	// The caret blinks, and shows at once where it moved to.
	if (!(state == before) || edited)
		m_CaretBlink = 0.0f;
	else
		m_CaretBlink += deltaTime;
	state.CaretVisible = std::fmod(m_CaretBlink, 2.0f * c_CaretBlinkInterval) < c_CaretBlinkInterval;
	ShowFieldState();

	// Enter submits, Escape stops editing.
	if (Input::GetKeyState(Key::Enter).Pressed || Input::GetKeyState(Key::KPEnter).Pressed)
		QueueEvent(UIEventType::Submit, editedField);
	if (Input::GetKeyState(Key::Escape).Pressed)
	{
		m_KeepCaptureThisFrame = true;
		Focus(entt::null);
	}
}
```

1. **Line 709:** typed text arrives through `Input::GetUncapturedTypedText`, which reads characters while capture is on, and `FilterTypedText` drops control characters.
2. **Line 712:** typing first erases the selection, so typed text replaces it.
3. **Line 717:** the limit takes whole characters only.
4. **Line 730:** `registry.patch` signals the change, so layout shapes the text again and drawing rebuilds the quads.
5. **Line 742:** Escape sets a flag that keeps the capture to the end of the frame, then removes the focus.

Earlier in the function, **Ctrl+A** or **Cmd+A** moves the anchor to 0 and the caret to the end. `Backspace` and `Delete` remove the selection, or else one character. The arrows move one character, and a selection collapses to the side moved to; `Home` and `End` move to the ends. **Shift** keeps the anchor in place, so the move extends the selection. **Enter** queues a submit event.

A click on the field focuses it and moves the caret to the nearest stop: `FindInputFieldCaret` places the line, then takes the stop whose distance to the pointer is smallest. On a world-space canvas, the camera's ray gives the pointer's place on the canvas, so the same click works on a sign in the world.

### The map while a field is edited

Keyboard capture makes `Input::IsKeyDown` report nothing, and the :term[input actions]{id=input-action} read exactly that. The keyboard bindings of the UI map go quiet: **Space** types a space and presses no button, and the field reads Enter, Escape, Left, Right, Home and End itself. The keyboard's Up and Down do nothing. A gamepad does not go through the keyboard, so it still works: its Submit submits, its Cancel ends editing, its Left and Right move the caret, and its Up and Down navigate away. `UpdateNavigation` holds these special cases.

| While a field is edited | Keyboard | Gamepad |
| --- | --- | --- |
| Submit | Enter, read by the field | Submit action submits |
| Cancel | Escape, read by the field | Cancel action ends editing |
| Left and right | Arrows, read by the field | Move the caret |
| Up and down | Nothing | Navigate away |

::figure{id=field-states}

## What Strata does not do

Strata does not translate text and does not lay out right-to-left text: lines run from left to right. Strata's list of later work, `Docs/Roadmap.md`, names string tables and font fallback chains, but the release has neither. The game UI also shows no text that an input method is still composing, and no candidate window. Committed text arrives, so a player who types with an input method gets the finished characters.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Measure text by :term[rasterizing]{id=rasterization} it | Simple engines | One code path for measuring and drawing | Layout would need a GPU and the atlas, and could not run in tests |
| Edit by bytes | Quick prototypes | A simpler loop | Split characters and invalid text after one `Backspace` |
| Wrap and cut a field's line | Multi-line editors | Long values stay whole | A second layout for a field that is one line by contract |
| Show composed text | Desktop libraries | Better input for languages that compose | A platform layer for the input method of every :term[operating system]{id=operating-system} |

## How it is tested

The `GameUI.Text` suite in `StrataTests/src/GameUI/GameUITextTests.cpp` tests shaping: alignments, wrapping between words, at a `-` and inside long words, cutting and the ellipsis, caret stops, and that shaping rasterizes no glyph. The `GameUI.InputField` suite in `StrataTests/src/GameUI/GameUIInputTests.cpp` tests editing: typed text at the caret, the keys and Shift, the limit, Enter and Escape, a held key repeating, a click placing the caret, the blink and the placeholder. The suites of `GameUIComponentTests.cpp` round-trip every UI component. Run the two text suites like this:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=GameUI.Text,GameUI.InputField
```

The command runs the shaping tests and the editing tests in one process, and it needs no GPU.

## Changing it safely

- Never rasterize in layout. A shaping that needs the atlas breaks headless runs.
- Write a field only with `registry.patch` or `MarkModified`. A write without a signal shows as a difference in validation.
- Move the caret only to character boundaries, and count the limit in characters.
- A change to what typed text accepts belongs to [the input state page](../input/devices-state.md), because that page holds the limit of bytes per frame.

## Summary

- A rect becomes shaping options by dividing its width and height by the font size, and shaping reads font metrics only, so layout runs headless.
- A field's line scrolls only as far as needed to keep the caret inside the box, and never beyond the end of the line.
- `Backspace` steps back over continuation bytes, so one press removes one whole character.
- A key goes from `Input` through `UpdateEditing`, which edits a copy and writes it with `registry.patch`.
- While a field is edited, the keyboard bindings of the UI map go quiet and the gamepad still works.

## Check yourself

1. A text of font size 20 has wrap on, Truncate and a rect of 300 by 60 units that does not fit its content. What are the wrap width and the box height?

   - A. 15 em and 3 em
   - B. 300 em and 60 em
   - C. 15 em and 0

   :::answer{tests="rect-to-options"}
   A. Both are the rect's size divided by 20. B forgets the division. C forgets that Truncate gives a box height.
   :::

2. Why does layout use font metrics and never the glyph atlas?

   - A. The atlas is too small.
   - B. Layout runs headless, in commands and tests, and must not depend on the atlas or its budget.
   - C. Glyphs have no size.

   :::answer{tests="rect-to-options"}
   B. A and C are wrong: the atlas is big enough, and glyphs do have size. Metrics give advances without any pixels.
   :::

3. A field's text element is 100 units wide, the line is 250 units, and the caret is 3 units wide and stands at the end. How far does the line scroll?

   :::answer{tests="scroll-line"}
   250 + 3 - 100 = 153 units. The same number is the largest scroll the clamp allows, so 153 is the only value.
   :::

4. The text is "né" (`n`, then the two bytes of "é") and the caret is at byte 3. Where is the caret after `Backspace`?

   - A. 2
   - B. 1
   - C. 0

   :::answer{tests="utf8-boundaries"}
   B. `PreviousBoundary` starts at byte 2, a continuation byte, steps to byte 1, the first byte of "é", and stops. Both bytes go. A would split the character. C would also remove the `n`.
   :::

5. A field is edited. The player presses Space on the keyboard, then Submit on a gamepad. What happens?

   :::answer{tests="map-while-editing,key-to-field"}
   The space enters the text through `UpdateEditing` and `registry.patch`. The keyboard's Space does not reach the UI map, because capture silences `Input::IsKeyDown`. The gamepad's Submit queues a submit event for the field.
   :::

## Exercises

1. **Basic.** A text has the font size 24, wrap off, Ellipsis and a rect 360 units wide that does not fit its content. Give the wrap width and the maximum width.

   :::answer[Worked solution]{tests="rect-to-options"}
   The text does not wrap, so the wrap width is 0. With Ellipsis, no wrap and no fit, the maximum width is 360 / 24 = 15 em.
   :::

2. **Medium.** Trace it yourself: find where the character "é" enters a field when a player types it, and what keeps the caret from landing between its two bytes.

   :::answer[Worked solution]{tests="key-to-field,utf8-boundaries"}
   Make a field with the Input Field preset, play, and set a breakpoint in `GameUISystem::UpdateEditing` in `Strata/src/Strata/GameUI/GameUISystem.cpp`. Type "é": the typed string has two bytes, `text.insert` puts both at the caret, and the caret grows by 2. Press `Backspace`: `PreviousBoundary` steps back over both bytes, and `registry.patch` signals the new text.
   :::

3. **Hard.** Add word-wise moves for **Ctrl+Left** and **Ctrl+Right**: a word is a run of characters that are not spaces, and every step must stop on a character boundary. Test them on the text `héllo wörld`.

   :::answer[Worked solution]{tests="utf8-boundaries" solution="sketches/ui-text-words.cpp"}
   Build both moves from `PreviousBoundary` and `NextBoundary`. `PreviousWord` skips spaces backwards, then the characters of a word. `NextWord` skips the characters of a word forwards, then spaces. The text has 13 bytes, so the caret starts at 13. The engine's `MoveCaret` moves one character or to an end and never by words, so a real version also keeps the anchor in place for **Shift**.

   ```cpp sketch="ui-text-words.cpp"
   #include <cstdint>
   #include <cstdio>
   #include <string>

   bool IsContinuationByte(char byte)
   {
   	return (static_cast<uint8_t>(byte) & 0xC0) == 0x80;
   }

   uint32_t PreviousBoundary(const std::string& text, uint32_t position)
   {
   	if (position == 0)
   		return 0;
   	uint32_t index = position - 1;
   	while (index > 0 && IsContinuationByte(text[index]))
   		index--;
   	return index;
   }

   uint32_t NextBoundary(const std::string& text, uint32_t position)
   {
   	const uint32_t size = static_cast<uint32_t>(text.size());
   	if (position >= size)
   		return size;
   	uint32_t index = position + 1;
   	while (index < size && IsContinuationByte(text[index]))
   		index++;
   	return index;
   }

   // Spaces are the only word breaks here; every step is a whole character.
   uint32_t PreviousWord(const std::string& text, uint32_t position)
   {
   	while (position > 0 && text[PreviousBoundary(text, position)] == ' ')
   		position = PreviousBoundary(text, position);
   	while (position > 0 && text[PreviousBoundary(text, position)] != ' ')
   		position = PreviousBoundary(text, position);
   	return position;
   }

   uint32_t NextWord(const std::string& text, uint32_t position)
   {
   	const uint32_t size = static_cast<uint32_t>(text.size());
   	while (position < size && text[position] != ' ')
   		position = NextBoundary(text, position);
   	while (position < size && text[position] == ' ')
   		position = NextBoundary(text, position);
   	return position;
   }

   int main()
   {
   	const std::string text = "h\xC3\xA9llo w\xC3\xB6rld"; // "héllo wörld": 13 bytes, 11 characters
   	uint32_t caret = static_cast<uint32_t>(text.size());
   	for (int step = 0; step < 3; step++)
   	{
   		caret = PreviousWord(text, caret);
   		std::printf("Ctrl+Left  -> caret %u\n", caret);
   	}
   	for (int step = 0; step < 3; step++)
   	{
   		caret = NextWord(text, caret);
   		std::printf("Ctrl+Right -> caret %u\n", caret);
   	}
   	return 0;
   }
   ```

   ```text output-of="ui-text-words.cpp"
   Ctrl+Left  -> caret 7
   Ctrl+Left  -> caret 0
   Ctrl+Left  -> caret 0
   Ctrl+Right -> caret 7
   Ctrl+Right -> caret 13
   Ctrl+Right -> caret 13
   ```

   1. **Line 34:** the first loop steps back over spaces.
   2. **Line 36:** the second loop steps back over a word, one whole character at a time.
   3. **Line 44:** `NextWord` runs forwards over a word, then over the spaces after it.
   4. **Line 53:** the text has 13 bytes but 11 characters, so the caret starts at 13 and the stops fall on bytes 7, 0 and 13.
   :::

## Where it lives in Strata

- `Strata/src/Strata/GameUI/GameUIText.cpp`: `GetMeasureOptions`, `GetShapeOptions`, `PlaceFieldLine`, `ShapeElementText`.
- `Strata/src/Strata/GameUI/GameUISystem.cpp`: `UpdateEditing`, `MoveCaret`, `PreviousBoundary`, `NextBoundary`, `UpdateNavigation`.
- `Strata/src/Strata/GameUI/GameUIComponents.h`: `UITextComponent`, `UIInputFieldComponent`.
- `Strata/src/Strata/Renderer/TextLayout.h`: `ShapeText`, `MeasureCaretStops`.
- `StrataEditor/src/Editor/GameUIPresets.cpp`: the Input Field preset.
- Tests: `GameUI.Text` and `GameUI.InputField`.

## Further reading

- Unicode Standard, chapter 3, on UTF-8 (advanced): the exact rules for the bytes of a character.
- "Game Engine Architecture" by Jason Gregory, the chapter on UI (intermediate): text in game interfaces.
