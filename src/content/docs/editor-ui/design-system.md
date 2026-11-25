---
id: editor-ui/design-system
title: "The design system: theme, fonts, icons"
description: "How the editor names its colors, sizes, fonts and icons once, so every panel looks alike and a scan of the source fails a stray color."
kind: internals
size: L
tracks: [E]
needs: [editor-ui/ui-scale, gpu/text]
time: 90
learn:
  - id: tokens-roles
    text: explain how a palette token reaches a widget through a meaning and a role table
  - id: font-chain
    text: explain how merged fonts, excluded ranges and a fallback font decide which face draws a character
  - id: icons-text
    text: write the call that draws an icon as text and say why a color sample is a rectangle
  - id: trust-boundary
    text: explain why the editor's text may skip the engine's font validation
  - id: add-meaning
    text: add a theme meaning and predict how the source scan answers a hex color
since: 0.3.0
status: final
---

The editor looks the same in every panel, and this page explains how that stays true. Every color comes from one short list of names, every piece of text comes from three :term[fonts]{id=font}, and every icon is a character. A test reads the source and fails when a panel breaks one of these rules.

This page covers the colors (the palette and the style that :term[ImGui]{id=dear-imgui} reads), the fonts (the atlas, the icon merge and the fallback for Chinese, Japanese and Korean), the icons, and the window's own icon. It does not cover how the engine draws text in a game, which `gpu/text` teaches, nor the scale that multiplies the sizes, which `editor-ui/ui-scale` teaches.

## The problem and how engines solve it

Picture a tool with sixty panels written over two years by many people and by agents. One writes the color of an error as red `(1, 0, 0)`, another as `(0.9, 0.3, 0.3)`, and a third copies a value from a screenshot. Nobody did wrong, yet the tool now has five reds. Warnings, selected rows and disabled text drift the same way. When someone wants a warmer look, they must find every number.

The usual cure is a **theme**: one place that decides how the whole interface looks. A theme has layers, and each layer removes one kind of drift.

- **A palette of named colors.** A named color is a **token**: a name for one value, so code says `Ochre` and never `0xE08A2E`. The palette is the whole list of tokens. A token says what a color looks like, but not what it is for.
- **Meanings.** A semantic color is a token with a job, such as `Error`, `Warning`, `AxisX` or `Accent`. A panel that draws an error asks for `Error`, which is today a red. If the look changes, one line changes and every error follows. Two jobs may share a color on purpose, and can part later.
- **A type scale.** A **type scale** is a short fixed list of text sizes, such as 12, 14, 17 and 24 pixels, so that text never takes a size in between.
- **An icon set.** All icons come from one family that shares a style, a stroke and a size.
- **Enforcement.** Rules in a style guide are read once and forgotten, so a good design system makes the wrong thing fail. A compile-time check or a test turns "please use the tokens" into "the build is red".

The last layer is the one that tools often skip. Without it, the first :term[hex]{id=hexadecimal} color written "only this once" on a hurried afternoon starts the drift again, and nobody sees it until the tool looks wrong. :term[Dear ImGui]{id=dear-imgui}, which the Strata editor draws with, gives one color to each of its drawing roles in a structure called `ImGuiStyle` and leaves the rest to the tool. A tool built on ImGui must add the other layers itself, and that is what this page shows.

## The map: from tokens to every ImGui color

Strata has one theme, and calls it Bedrock. Its palette has 16 tokens, named after minerals: dark stone surfaces, pale limestone text and an orange accent. The values are in the :term[sRGB]{id=srgb} :term[color space]{id=color-space}, the way ImGui draws them. They fall into four groups.

| Group | Tokens and their hex values | Used for |
| --- | --- | --- |
| Surfaces, darkest first | `Basalt` `0E1013`, `Shale` `15181C`, `Slate` `1D2126`, `Flint` `262B31`, `Seam` `323840` | Chrome bands, panels, raised cards, buttons, borders |
| Text | `Limestone` `E8E4DC`, `Ash` `9BA1A9`, `Dust` `5E656D` | Text, secondary text, disabled marks |
| The accent | `Ochre` `E08A2E`, `Sandstone` `F2B872`, `Rust` `B9562B`, `Umber` `6B3A22` | Selection, hover, pressed, selected backgrounds |
| Meanings | `Malachite` `3DBE8B`, `Azurite` `4C8FE0`, `Sulfur` `E9C34D`, `Cinnabar` `E5534B` | Success, information, warning, error |

The map has three steps. A token goes into a meaning, and a meaning goes into a role of ImGui's style. `ThemeColors` holds the meanings that panels and widgets use: `Accent`, `Success`, `Error`, `Text`, `Panel`, `Border` and more. The function `ApplyTheme` holds the roles: a table that says, for every `ImGuiCol_` slot, which token it takes and with what alpha.

```mermaid caption="Tokens become meanings for panel code and roles for the widgets of ImGui. The three axis colors come from the meanings and appear again in the scene gizmo and in the fields that edit vectors." alt="A diagram in three columns. Sixteen palette tokens lead to the meanings and to the style slots of ImGui. The axis meanings also lead to the scene gizmo and to the vector fields."
flowchart LR
  subgraph T[Palette: 16 tokens]
    S[Surfaces: Basalt Shale Slate Flint Seam]
    X[Text: Limestone Ash Dust]
    A[Accent: Ochre Sandstone Rust Umber]
    M[Meanings: Malachite Azurite Sulfur Cinnabar]
  end
  subgraph C[ThemeColors: meanings]
    AC[Accent and levels]
    AX[AxisX AxisY AxisZ]
    PS[Play states]
    TX[Text and surfaces]
  end
  R[ApplyTheme: role table to every ImGuiCol_]
  G[Scene gizmo]
  V[Vector fields]
  T --> C
  T --> R
  AX --> G
  AX --> V
```

Some meanings share a token. `AxisX` and `Error` are both `Cinnabar`, `AxisY` and `Success` are both `Malachite`, and `AxisZ` and `Info` are both `Azurite`. Code asks for the meaning, so one line can part them later, and the axis colors show why that matters. The :term[gizmo]{id=gizmo-start} in the Scene view draws its handles in `AxisX`, `AxisY` and `AxisZ`, and the fields that edit a vector color the letters X, Y and Z with the same three. A red handle therefore always belongs to the red X field.

The play states are a small group of their own: `Edit` is `Ash`, `Play` is `Malachite`, `Simulate` is `Azurite` and `Paused` is `Sulfur`. The bars around the viewport read them, and no panel decides alone what "playing" looks like.

The editor always applies Bedrock. No command, preference or program option draws its panels in ImGui's own default style, which is blue-gray with rounded windows, so the figure shows Bedrock alone.

::figure{id=default-and-bedrock variant=bedrock}

ImGui has about sixty color slots, such as `ImGuiCol_Text`, `ImGuiCol_Button` and `ImGuiCol_TabSelected`, and the count changes when ImGui is upgraded. Text has its own map, with its own layers: three faces, icons merged into two of them, and a fallback font for the scripts that the faces lack.

```mermaid caption="The atlas holds three faces. Two text faces take the icons by a merge, and every face can take the system's font for Chinese, Japanese and Korean later. The fixed-width face takes no icons." alt="A diagram of three font stacks. The first stack is a regular text face, then an icon font, then a system font for Chinese, Japanese and Korean. The second stack is a heavier text face with the same two behind it. The third is a fixed-width face with only the system font behind it."
flowchart TB
  subgraph Atlas[ImGui font atlas]
    direction TB
    R[Inter Regular, default] --> RI[Lucide icons] --> RC[System CJK font, merged later]
    B[Inter SemiBold] --> BI[Lucide icons] --> BC[System CJK font, merged later]
    Mo[JetBrains Mono] --> MC[System CJK font, merged later]
  end
```

## The contract

Code that uses the design system keeps four rules, and each has a reason.

**Colors come only from tokens or meanings.** Panel code reads `UI::GetThemeColors()` and never writes a color number. The reason is the drift above. A test scans the sources of the user interface (UI) and fails on any color spelled as numbers outside `UI/Theme.cpp`.

:::rule
Colors in editor code come from the theme and sizes follow the font: a color or a size written into one panel cannot follow a theme change or the :term[UI scale]{id=ui-scale}. See [the source scans](../editor-ui/ui-testing.md).
:::

**Text goes only through the editor's fonts.** ImGui can draw with a built-in bitmap font, and the editor never uses it. Text comes from `Inter` in two weights or from `JetBrains Mono`, chosen with `UI::PushFont`. A test fails if the call `AddFontDefault` appears anywhere in the editor's sources. The built-in font has no icons and few characters, so a panel that used it would show boxes where the rest shows icons.

**Icons are text.** An **icon font** is a font whose :term[glyphs]{id=glyph} are pictures: a play triangle, a trash can, a gear. Because an icon is a character, you draw one with a text call, `ImGui::Button(Icons::Play)`, or join it to a label with `fmt::format("{} Play", Icons::Play)`. The icon takes the color, the size and the place on the line of the text around it. A color sample, a box that shows a value, is no glyph: it is a rectangle drawn with the draw list, the shapes ImGui keeps for a window, in a theme color.

**Text is encoded as UTF-8 once.** A :term[source file]{id=source-file} spells a character such as the middle dot `·` as UTF-8 :term[bytes]{id=byte} once. A tool that reads the file as Latin-1 text and saves it again as UTF-8 turns the two bytes of the dot into four, and the editor shows `Â·` in its place. A test finds those four-byte pairs in the sources, so the damage shows on the day it happens. The fix is to write the character's `\x` escapes, as the other texts do.

:::why[Rules that fail the build, not rules to remember]
Strata has many authors, and some are agents that read a rule once per session. A rule that is only written down holds on the days someone remembers it. A rule that fails a build holds every day, and it costs the author a minute instead of the reviewer an hour. The price is a scan that must be exact enough to give no false alarms. It strips comments and text before it looks, so a comment may mention `ImVec4(1, 0, 0, 1)` without a failure.
:::

## A toy version: roles and a font chain

The toy has two parts, and each is small enough to read in one sitting. The first builds a palette, a role table and the compile-time check. The second shows how a chain of fonts decides which face draws a character.

The first program has four tokens, four style slots and a table whose rows point into the palette with a :term[pointer to a member]{id=pointer-to-a-member}. The type `Color Palette::*Token` means "the place of one `Color` inside a `Palette`", so a row names a token and copies no color. Search for the `static_assert` and for the loop that writes the slots.

```cpp sketch="editor-ui-design-system-roles.cpp"
// A toy theme: a palette of tokens, a role table of pointers to members and a check that no slot lacks a role.
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <iterator>

namespace Toy
{

	struct Color
	{
		float R, G, B, A;
	};

	constexpr Color FromRGB(uint32_t rgb)
	{
		return { static_cast<float>((rgb >> 16) & 0xFF) / 255.0f, static_cast<float>((rgb >> 8) & 0xFF) / 255.0f,
			static_cast<float>(rgb & 0xFF) / 255.0f, 1.0f };
	}

	struct Palette
	{
		Color Basalt;
		Color Flint;
		Color Limestone;
		Color Ochre;
	};

	constexpr Palette c_Palette = { FromRGB(0x0E1013), FromRGB(0x262B31), FromRGB(0xE8E4DC), FromRGB(0xE08A2E) };

	// The slots the toy toolkit draws with.
	enum class Slot : size_t
	{
		Text,
		FrameBackground,
		Button,
		CheckMark,
		Count
	};

	struct Role
	{
		Slot Where;
		Color Palette::*Token;
		float Alpha;
	};

	constexpr Role c_Roles[] = {
		{ Slot::Text, &Palette::Limestone, 1.0f },
		{ Slot::FrameBackground, &Palette::Basalt, 1.0f },
		{ Slot::Button, &Palette::Flint, 1.0f },
		{ Slot::CheckMark, &Palette::Ochre, 0.9f }
	};
	// A toolkit upgrade that adds a slot fails the build here until the slot has a role.
	static_assert(std::size(c_Roles) == static_cast<size_t>(Slot::Count), "Give every slot a palette token");

	void Apply(std::array<Color, static_cast<size_t>(Slot::Count)>& colors)
	{
		for (const Role& role : c_Roles)
		{
			const Color& token = c_Palette.*role.Token;
			colors[static_cast<size_t>(role.Where)] = { token.R, token.G, token.B, role.Alpha };
		}
	}

}

int main()
{
	std::array<Toy::Color, static_cast<size_t>(Toy::Slot::Count)> colors = {};
	Toy::Apply(colors);
	const char* names[] = { "Text", "FrameBackground", "Button", "CheckMark" };
	for (size_t index = 0; index < colors.size(); index++)
	{
		const Toy::Color& color = colors[index];
		std::printf("%-16s rgb %3d %3d %3d alpha %.1f\n", names[index], static_cast<int>(color.R * 255.0f + 0.5f),
			static_cast<int>(color.G * 255.0f + 0.5f), static_cast<int>(color.B * 255.0f + 0.5f), color.A);
	}
	return 0;
}
```

```text output-of="editor-ui-design-system-roles.cpp"
Text             rgb 232 228 220 alpha 1.0
FrameBackground  rgb  14  16  19 alpha 1.0
Button           rgb  38  43  49 alpha 1.0
CheckMark        rgb 224 138  46 alpha 0.9
```

1. **Line 45:** the token is a pointer to a member of `Palette`, so a role names a color without copying it.
2. **Line 56:** a `static_assert` ties the number of roles to the number of slots, so a new slot stops the build.
3. **Line 62:** the loop reads the token through the pointer and writes the slot with the alpha of its role.

The program prints the four colors in bytes. Remove one row from `c_Roles` and the program does not compile, because the `static_assert` says that every slot needs a token. That is the whole idea of the role table. The real one is larger only because ImGui has more slots.

The second program is the text side. A chain has three faces. Each face may supply some :term[code points]{id=code-point} (`Only`), is barred from others (`Exclude`), and holds a list of glyphs. The lookup walks the chain and returns the first face that supplies the code point, or the fallback glyph when none does. Search for the exclusion of the icon range and for the face that holds a glyph inside it.

```cpp sketch="editor-ui-design-system-font-chain.cpp"
// A toy font chain: each face may be limited to a range of code points, or barred from one.
#include <cstdint>
#include <cstdio>
#include <vector>

namespace Toy
{

	struct Range
	{
		uint32_t First;
		uint32_t Last;
	};

	struct Face
	{
		const char* Name;
		Range Only;           // The code points the face may supply.
		Range Exclude;        // The code points it must not supply (First > Last means none).
		std::vector<uint32_t> Has; // What its file really holds.
	};

	constexpr Range c_Everything = { 0, 0x10FFFF };
	constexpr Range c_Icons = { 0xE000, 0xF8FF };
	constexpr Range c_Nothing = { 1, 0 };

	bool Inside(const Range& range, uint32_t codePoint)
	{
		return codePoint >= range.First && codePoint <= range.Last;
	}

	bool Supplies(const Face& face, uint32_t codePoint)
	{
		if (!Inside(face.Only, codePoint) || Inside(face.Exclude, codePoint))
			return false;
		for (const uint32_t held : face.Has)
		{
			if (held == codePoint)
				return true;
		}
		return false;
	}

	// The first face of the chain that supplies the code point, or the fallback character.
	const char* Find(const std::vector<Face>& chain, uint32_t codePoint)
	{
		for (const Face& face : chain)
		{
			if (Supplies(face, codePoint))
				return face.Name;
		}
		return "fallback glyph";
	}

}

int main()
{
	// The text font even holds a glyph inside the icon range, which its exclusion keeps from shadowing the icon.
	const std::vector<Toy::Face> chain = {
		{ "Inter", Toy::c_Everything, Toy::c_Icons, { 'A', 0xE9, 0xE585 } },
		{ "Lucide", Toy::c_Icons, Toy::c_Nothing, { 0xE585, 0xE038 } },
		{ "CJK font", Toy::c_Everything, Toy::c_Icons, { 0x6575, 0xE585 } }
	};
	const uint32_t probes[] = { 'A', 0xE585, 0x6575, 0x1F600 };
	for (const uint32_t codePoint : probes)
		std::printf("U+%04X -> %s\n", static_cast<unsigned>(codePoint), Toy::Find(chain, codePoint));
	return 0;
}
```

```text output-of="editor-ui-design-system-font-chain.cpp"
U+0041 -> Inter
U+E585 -> Lucide
U+6575 -> CJK font
U+1F600 -> fallback glyph
```

1. **Line 34:** a face supplies a code point only inside its range, outside its exclusion and when its file holds a glyph.
2. **Lines 45–52:** the lookup takes the first face of the chain that supplies the code point, and ends at the fallback glyph.
3. **Lines 61–62:** `Inter` holds a glyph at U+E585, but its exclusion leaves that code point to `Lucide`.

The second line shows the point. U+E585 is held by `Inter`, by `Lucide` and by the font for Chinese, Japanese and Korean, and only `Lucide` may supply it. The exclusion makes the answer the same whatever a text font holds in that range. The last probe, U+1F600, is held by no face, so the chain answers with the fallback glyph.

## The real code

The real code has three parts, and each follows the toy: the role table with its check, the :term[font atlas]{id=glyph-atlas} with its ranges, and the fallback font read off the :term[main thread]{id=main-thread}. Icons and the window's icon follow them.

### The palette, the meanings and the role table

The file `StrataEditor/src/UI/Theme.cpp` holds the only color numbers of the editor. It has a helper `FromRGB` that turns `0xE08A2E` into a color of floats, the palette `c_Bedrock`, the list of names `c_Tokens` for tests, and the meanings `c_Colors`, built from palette members. A `static_assert` on `c_Tokens` compares its size with `sizeof(ThemePalette)`, so a new token without a name fails the build.

The worked example is one slot, the button. The row `{ ImGuiCol_Button, &ThemePalette::Flint, 1.0f }` says that the button is `Flint`, fully opaque. `Flint` is `0x262B31`, which is the bytes 38, 43 and 49. Divided by 255, they are 0.149, 0.169 and 0.192. A hovered button takes `Seam` (`0x323840`, the bytes 50, 56 and 64) and a pressed one takes `Umber`, so the three states climb from dark gray to the brown of the accent.

The first rows of the table show the shape of a row.

```cpp src="StrataEditor/src/UI/Theme.cpp#L93-L124"
struct ColorRole
{
	ImGuiCol Slot;
	ImVec4 ThemePalette::*Token;
	float Alpha;
};

constexpr ColorRole c_ColorRoles[] = {
	{ ImGuiCol_Text, &ThemePalette::Limestone, 1.0f },
	// ImGui draws hints, disabled menu items and TextDisabled() with it: secondary text must stay readable.
	{ ImGuiCol_TextDisabled, &ThemePalette::Ash, 1.0f },
	{ ImGuiCol_WindowBg, &ThemePalette::Shale, 1.0f },
	{ ImGuiCol_ChildBg, &ThemePalette::Shale, 0.0f },
	{ ImGuiCol_PopupBg, &ThemePalette::Slate, 0.98f },
	{ ImGuiCol_Border, &ThemePalette::Seam, 1.0f },
	{ ImGuiCol_BorderShadow, &ThemePalette::Basalt, 0.0f },
	{ ImGuiCol_FrameBg, &ThemePalette::Basalt, 1.0f },
	{ ImGuiCol_FrameBgHovered, &ThemePalette::Slate, 1.0f },
	{ ImGuiCol_FrameBgActive, &ThemePalette::Flint, 1.0f },
	{ ImGuiCol_TitleBg, &ThemePalette::Basalt, 1.0f },
	{ ImGuiCol_TitleBgActive, &ThemePalette::Slate, 1.0f },
	{ ImGuiCol_TitleBgCollapsed, &ThemePalette::Basalt, 0.75f },
	{ ImGuiCol_MenuBarBg, &ThemePalette::Basalt, 1.0f },
	{ ImGuiCol_ScrollbarBg, &ThemePalette::Shale, 0.0f },
	{ ImGuiCol_ScrollbarGrab, &ThemePalette::Seam, 1.0f },
	{ ImGuiCol_ScrollbarGrabHovered, &ThemePalette::Dust, 1.0f },
	{ ImGuiCol_ScrollbarGrabActive, &ThemePalette::Ash, 1.0f },
	{ ImGuiCol_CheckMark, &ThemePalette::Ochre, 1.0f },
	{ ImGuiCol_CheckboxSelectedBg, &ThemePalette::Umber, 1.0f },
	{ ImGuiCol_SliderGrab, &ThemePalette::Ochre, 1.0f },
	{ ImGuiCol_SliderGrabActive, &ThemePalette::Sandstone, 1.0f },
	{ ImGuiCol_Button, &ThemePalette::Flint, 1.0f },
```

1. **Line 96:** the token is a pointer to a member of `ThemePalette`, so a row names a token and copies no color.
2. **Lines 102–103:** the comment says why secondary text uses `Ash`: ImGui draws disabled items with this slot.
3. **Line 124:** the button row of the worked example: `Flint`, with an alpha of 1.

The other rows follow the same shape, one for every ImGui slot, with a comment where a row needs a reason. Selected rows take the accent: `ImGuiCol_Header` is `Umber` at an alpha of 0.9. A row that is not selected, under the mouse, takes the neutral `Flint`, so a mouse over a row is never mistaken for a selection. `ImGuiCol_TextDisabled` is `Ash` and not `Dust`, because ImGui draws hints and disabled menu items with it, and secondary text must stay clear to read.

The end of the table carries the check that keeps it complete.

```cpp src="StrataEditor/src/UI/Theme.cpp#L166-L171"
	{ ImGuiCol_NavWindowingHighlight, &ThemePalette::Limestone, 0.7f },
	{ ImGuiCol_NavWindowingDimBg, &ThemePalette::Basalt, 0.6f },
	{ ImGuiCol_ModalWindowDimBg, &ThemePalette::Basalt, 0.7f }
};
// An ImGui upgrade that adds colors fails here until they are given a token.
static_assert(std::size(c_ColorRoles) == ImGuiCol_COUNT, "Give every ImGuiCol_ a palette token");
```

1. **Line 168:** the last row of the table, for the dim behind :term[modal]{id=modal} windows.
2. **Lines 170–171:** the comment and the `static_assert` that stops the build when ImGui has more slots than the table has rows.

ImGui lists its slots in an enum that ends with `ImGuiCol_COUNT`. When Strata upgrades ImGui and a new slot appears, the count grows by one and the table does not, so the build fails at this line until a person gives the new slot a token. Without the check, the new slot would keep ImGui's default dark color, and one control would look foreign for months.

The function that uses the table is short. It writes every color, sets the base sizes, scales them and sets a few options of shape.

```cpp src="StrataEditor/src/UI/Theme.cpp#L253-L270"
void ApplyTheme(ImGuiStyle& style, float scale)
{
	for (const ColorRole& role : c_ColorRoles)
		style.Colors[role.Slot] = WithAlpha(c_Bedrock.*role.Token, role.Alpha);

	SetBaseSizes(style);
	style.ScaleAllSizes(scale);
	// A factor, not a size (it also places tooltips): ScaleAllSizes truncates it to whole numbers, 1 at 150%.
	style.MouseCursorScale = scale;

	style.WindowTitleAlign = ImVec2(0.0f, 0.5f);
	// No triangle menu and no close button on dock nodes: every tab has its own close button, and closed panels come
	// back through the View menu.
	style.WindowMenuButtonPosition = ImGuiDir_None;
	style.DockingNodeHasCloseButton = false;
	style.DisabledAlpha = 0.5f;
	style.FontSizeBase = GetTextSize(TextSize::Body);
}
```

1. **Lines 255–256:** every row of the role table becomes one color of the style, with its alpha.
2. **Lines 258–259:** the base sizes are set, then multiplied by the scale.
3. **Line 261:** the cursor scale is a factor, not a size, so it is set after the scaling and is not cut to whole numbers.
4. **Line 269:** the body size of the type scale becomes the base font size of ImGui.

The base sizes are in `SetBaseSizes`, and each is even or zero. The reason is `ScaleAllSizes`, which cuts off the fraction of each result: a base of 8 at a scale of 1.5 gives 12, but a base of 5 would give 7.5 and become 7. Only the thin lines are 1, so they stay one pixel wide below a scale of 2 and become two pixels at 2. The exercises ask you to try this.

The style :term[callback]{id=callback} gives `ApplyTheme` its scale. `ImGuiLayer::ApplyStyle`, in `Strata/src/Strata/ImGui/ImGuiLayer.cpp`, makes a fresh `ImGuiStyle` and fills it with ImGui's dark defaults. It then calls the callback with the style and the scale, and sets `FontScaleDpi` to the scale. It starts from the defaults every time, so scaling twice never compounds. The editor registers `UI::ApplyTheme` once with `SetStyleCallback`, and the layer applies it again whenever the UI scale changes.

:::example[One button, followed from token to pixel]
A panel calls `ImGui::Button("Save")`. ImGui draws the frame with the slot `ImGuiCol_Button`, which holds the color that `ApplyTheme` wrote from the row of the role table: `Flint`. The person then sets a scale of 1.5. The style is rebuilt, the colors come out the same, and the frame padding, which was `(8, 4)`, becomes `(12, 6)`, with both numbers whole because 8 and 4 are even. The panel changed nothing, and it never saw a color or a size.
:::

### The font atlas

Games draw text through the engine's own atlas, `FontAtlasCache`, which `gpu/text` teaches. The editor does not. It draws through the font atlas of ImGui itself, the picture of glyphs that ImGui keeps for its own widgets. ImGui lays out and draws all of its text, and a second text system beside it would draw the menus again, with different results.

The fonts come from four files that the build compiles into the editor with `strata_embed_file`, so the editor reads no font file at run time. The files are `Inter-Regular.ttf`, `Inter-SemiBold.ttf`, `JetBrainsMono-Regular.ttf` and `Lucide.ttf`, and they sit in `StrataEditor/Resources/Fonts`. The same build step embeds `ThirdPartyNotices.md`, which the About window shows. [The page on generated code](../engineering/generated-code.md) explains how `strata_embed_file` works.

:::note[The fonts and their licenses]
`Inter` 4.1 and `JetBrains Mono` 2.304 come under the Open Font License 1.1. `Lucide` 1.47.0 comes under the `ISC` license, and the icons that it took from Feather also come under the MIT license. Each license text sits next to its font, and `ThirdPartyNotices.md` lists them. [The page on third-party code](../engineering/third-party.md) covers licenses in general.
:::

An icon font needs code points to live at, and it must not take any that a text font uses. :term[Unicode]{id=unicode} keeps a block for private agreements, the **Private Use Area** (PUA): the code points from U+E000 to U+F8FF, to which no standard gives a meaning. `Lucide` puts its icons there, so `Icons::Play` is a character in a range that no language owns.

To use two fonts as one, ImGui has **merge mode**: it adds the second font to the font before it. A lookup for a character then asks the first font and each merged one in order. The code merges `Lucide` into each `Inter` face.

```cpp src="StrataEditor/src/UI/EditorFonts.cpp#L77-L97"
// A text font at the body size, optionally with the icons merged in.
ImFont* AddTextFont(ImFontAtlas& atlas, std::span<const uint8_t> data, const char* name, bool icons)
{
	const float size = GetTextSize(TextSize::Body);
	ImFontConfig textConfig;
	textConfig.GlyphExcludeRanges = c_IconRanges;
	ImFont* font = AddFont(atlas, data, name, textConfig, size);
	if (!font || !icons)
		return font;

	ImFontConfig iconConfig;
	iconConfig.MergeMode = true;
	iconConfig.GlyphRanges = c_IconRanges;
	// Icons advance by a whole text size, so rows of icons line up like a grid.
	iconConfig.GlyphMinAdvanceX = size;
	iconConfig.GlyphOffset = ImVec2(0.0f, c_IconOffsetY);
	iconConfig.PixelSnapH = true;
	if (!AddFont(atlas, EmbeddedFiles::GetLucideFont(), "Lucide", iconConfig, size * c_IconScale))
		return nullptr;
	return font;
}
```

1. **Line 82:** the text font excludes the icon range.
2. **Lines 88–89:** `Lucide` joins in merge mode and may supply only the icon range.
3. **Lines 91–92:** the minimum advance is the body size, and the offset moves the icons down by 2 pixels.
4. **Line 94:** icons are drawn at 0.9 of the text size, and a failure returns null so that the caller reports it.

The text font is added with `GlyphExcludeRanges` set to the icon range, so a text font with glyphs in that range can never shadow an icon, as the toy showed. `Lucide` is added with `MergeMode` and with `GlyphRanges` set to the same range, so it supplies only icons. It also has a size, an offset and a minimum advance.

The glyphs of `Lucide` fill their whole square, which sits higher than the text of `Inter`. At the body size of 14 pixels the code draws the icons at 0.9 of it, 12.6 pixels, and moves them down by 2 pixels at the base size. The comment in the file says that the offset scales with the size. The result is an icon as tall as the capitals of `Inter`, centered on the text line, also inside a button next to a label. The minimum advance is the body size, 14, so every icon advances by 14 pixels and a column of icons lines up like a grid, whatever the shape of each.

The editor adds three faces. `Inter Regular` with the icons is the default, `Inter SemiBold` with the icons serves :term[headers]{id=header} and titles, and `JetBrains Mono` without icons serves the console, identifiers and numbers. A test checks that exactly three fonts exist and that none is the built-in one. `EditorFonts::Load` returns false, with a log line, if ImGui cannot read a font. The editor then reports that its fonts are unavailable and runs with the default font of ImGui, which is the one failure path where the built-in font appears.

### The fallback font for other scripts

`Inter` has no Chinese, Japanese or Korean characters, and the three scripts together are called **CJK** (Chinese, Japanese and Korean). A project may be named in them, and so may a folder or a log line. Strata compiles no font for them into the editor, because such fonts weigh tens of MB. It takes them from the system, where they are already installed.

The list of files comes from `Platform::FindFallbackFontFiles`. On Windows it takes the first existing file of `msyh.ttc`, `msjh.ttc`, `YuGothM.ttc`, `meiryo.ttc` and `simsun.ttc` in the system's fonts folder, for Chinese characters and the Japanese syllable scripts. It then takes the first of `malgun.ttf` and `gulim.ttc`, for Korean letters. On macOS it searches for `PingFang.ttc` and two older files, then for `AppleSDGothicNeo.ttc`, and on Linux in the folders where distributions install the `Noto Sans CJK`, `WenQuanYi` and `Droid Sans Fallback` fonts. A system with none of them gives an empty list, and the editor logs a warning.

Reading a file of tens of MB on the main thread would stop a frame, so the editor reads on a job. Two functions work together. The first starts the read.

```cpp src="StrataEditor/src/UI/EditorFonts.cpp#L131-L152"
void EditorFonts::BeginLoadingFallback()
{
	if (!ImGui::GetCurrentContext() || !Get(EditorFont::Regular))
		return;
	s_FallbackRequestedAtlas = ImGui::GetIO().Fonts;
	// Read once per process: later atlases (UI tests) merge the same bytes.
	if (s_Fallback || s_FallbackRead)
		return;
	Ref<FallbackFonts> read = CreateRef<FallbackFonts>();
	s_FallbackRead = read;
	s_FallbackJob = JobSystem::SubmitIO([read]()
	{
		for (const std::filesystem::path& file : Platform::FindFallbackFontFiles())
		{
			std::optional<std::vector<uint8_t>> bytes = FileSystem::ReadBytes(file);
			if (!bytes || bytes->empty())
				continue;
			read->Data.push_back(std::move(*bytes));
			read->Names.push_back(FileSystem::ToUTF8(file.filename()));
		}
	}, JobPriority::Low);
}
```

1. **Line 135:** the atlas that asked is remembered, so the merge goes into that one.
2. **Lines 137–138:** the files are read once per process.
3. **Lines 141–151:** the I/O job reads each file at low priority and keeps its bytes and its name.

The function remembers which atlas asked, then starts a job on the I/O pool at low priority, once per process, because a second atlas (a test's) merges the same bytes. The job reads each file with `FileSystem::ReadBytes` and keeps its bytes and its name. The main thread touches the result only after the job is complete, which is the rule of `core/jobs`.

The second function merges the result between frames.

```cpp src="StrataEditor/src/UI/EditorFonts.cpp#L154-L197"
bool EditorFonts::UpdateFallback()
{
	if (s_FallbackRead && s_FallbackJob.IsComplete())
	{
		s_Fallback = std::move(*s_FallbackRead);
		s_FallbackRead = nullptr;
		s_FallbackJob = JobHandle();
		if (s_Fallback->Data.empty())
			ST_WARN("No system font for Chinese, Japanese and Korean text was found: such text shows as '?'");
	}
	if (!s_Fallback || s_Fallback->Data.empty() || !ImGui::GetCurrentContext())
		return false;
	ImFontAtlas& atlas = *ImGui::GetIO().Fonts;
	if (&atlas != s_FallbackRequestedAtlas || &atlas == s_FallbackAtlas)
		return false;

	// Behind the font's own glyphs and its icons: only what they lack comes from these, never the icons' range.
	bool merged = false;
	for (const EditorFont font : { EditorFont::Regular, EditorFont::SemiBold, EditorFont::Mono })
	{
		ImFont* destination = Get(font);
		if (!destination)
			continue;
		for (size_t index = 0; index < s_Fallback->Data.size(); index++)
		{
			ImFontConfig config;
			config.MergeMode = true;
			config.DstFont = destination;
			config.GlyphExcludeRanges = c_IconRanges;
			std::vector<uint8_t>& data = s_Fallback->Data[index];
			if (AddFont(atlas, data, s_Fallback->Names[index].c_str(), config, GetTextSize(TextSize::Body)))
				merged = true;
			else
				ST_WARN("The system font '{}' could not be used for text in other scripts", s_Fallback->Names[index]);
		}
	}
	// Asked once per atlas, whether or not a font could be used.
	s_FallbackRequestedAtlas = nullptr;
	if (!merged)
		return false;
	s_FallbackAtlas = &atlas;
	s_GlyphGeneration++;
	return true;
}
```

1. **Lines 156–162:** a completed job hands over its result, with one warning when it read nothing.
2. **Lines 167–168:** an atlas that did not ask, or has the fonts already, is skipped.
3. **Lines 180–182:** the fallback joins each face in merge mode with the icon range excluded.
4. **Line 195:** the glyph generation grows when a merge succeeded.

`EditorLayer` calls `UpdateFallback` between frames, unless the editor runs headless. When the job is complete, the function takes the result and warns once if no file was read, because such text then shows as `?`. Otherwise it adds each file to each of the three faces in merge mode with the icon range excluded, so the fallback supplies only what the editor's own glyphs lack, and never the icons. ImGui does not own the bytes of the files, so they stay in memory until the process ends. A file that ImGui cannot use gets a warning, and the other files still merge.

The font costs memory but little time, because ImGui :term[rasterizes]{id=rasterization} a glyph into the atlas only when text first needs it. Until the merge, and on a system without such fonts, the text shows ImGui's question mark. This is the **fallback glyph**: the character that a chain of fonts draws for a code point that no face holds. The word glyph, and the engine's own use of the idea, belong to the page `gpu/text`.

::figure{id=cjk-name}

Merging changes how wide text is. A name that showed as four question marks becomes four wide characters. `EditorFonts` therefore keeps a counter, `GetGlyphGeneration`, that grows when the fonts load and when a merge succeeds. Its comment in the header says that widths measured before, and kept, must be measured again when the counter changes. At the pin no other file of the editor reads it, so it is a contract ready for any cache of measured widths: such a cache must compare it.

:::why[Why the fonts load once and merge between frames]
A read in the first frame would hold the window dark for as long as the disk needs, and a read on the main thread at any time would drop frames. A read on a job costs the main thread nothing, and a merge between frames is quick because ImGui adds a font and defers the rasterizing. The editor is usable at once, and the first frames show a question mark for text in those scripts that becomes the right glyph a moment later. The cost is a visible change after the start, and the counter that tells caches about it.
:::

### The trust boundary

The engine validates every font file that a project gives it, as `gpu/text` teaches, because a font file is untrusted data and its rasterizer does not check what it reads. The editor's atlas skips that check, and the reason is where its fonts come from. The only call of `AddFontFromMemoryTTF` in `StrataEditor/src` is in `AddFont`, in `EditorFonts.cpp`. It reads the four compiled-in fonts and the fallback fonts that the :term[operating system's]{id=operating-system} vendor installed. It never reads a font file of a project.

So the atlas may read without the engine's `FontValidation` because every file it reads is one that the editor ships or the system owns. A change that lets the atlas load a file from a project would break this reason, and would need the validation first. A project's font is drawn by the engine's text in the game, never by ImGui.

### The type scale and the icons

The editor's type scale has four sizes, in unscaled pixels. Caption is 12 for the status bar and dense tables, Body is 14 for most text, Title is 17 for section and dialog titles, and Display is 24 for large headings such as the launcher's. A static array holds them, with a `static_assert` that it has one entry for each `TextSize`. The UI scale multiplies them through `FontScaleDpi`, and `ApplyTheme` sets `FontSizeBase` to the body size.

You do not call `ImGui::PushFont` with a number. You call `UI::PushFont(EditorFont::Mono, TextSize::Caption)`, which finds the face in the current atlas, gives ImGui the size of that step, and pairs with `ImGui::PopFont()`. The names come from the scale, so a panel never says 13.

The header `StrataEditor/src/UI/Icons.h` holds every icon as a UTF-8 string constant, in more than four thousand lines that a person never edits. The program `StrataEditor/Tools/GenerateIconHeader.py` reads the code-point map of `Lucide` and the font itself. It turns each name in `kebab-case` into `PascalCase`, so `mouse-pointer-2` becomes `Icons::MousePointer2`, and it writes one line per icon with its code point in a comment. A name that the map lists but the font no longer holds is omitted and reported. A test checks that every icon of the header has a glyph in the editor's faces.

Two tables use the icons. `UI/EntityIcons.cpp` maps a registered component name to an icon, such as `Camera` to a video camera and `DirectionalLight` to a sun, and a component of a game or a module gets the generic icon. `GetAssetTypeIcon` in `PropertyWidgets.cpp` maps an asset type to its icon, and `GetAssetTypeDisplayName` gives its label.

```cpp src="StrataEditor/src/UI/PropertyWidgets.cpp#L1142-L1162"
const char* GetAssetTypeIcon(AssetType type)
{
	switch (type)
	{
		case AssetType::Scene:     return Icons::Clapperboard;
		case AssetType::Prefab:    return Icons::Package;
		case AssetType::Model:     return Icons::Shapes;
		case AssetType::Mesh:      return Icons::Box;
		case AssetType::Material:  return Icons::Palette;
		case AssetType::Texture:   return Icons::Image;
		case AssetType::AudioClip: return Icons::AudioLines;
		case AssetType::Font:      return Icons::Type;
		case AssetType::Skeleton:  return Icons::Bone;
		case AssetType::AnimationClip: return Icons::Film;
		case AssetType::AnimationController: return Icons::Network;
		case AssetType::World:     return Icons::Earth;
		case AssetType::ColorLookup: return Icons::Blend;
		case AssetType::None:      break;
	}
	return Icons::File;
}
```

1. **Line 1144:** the `switch` has no `default`, so the :term[compiler]{id=compiler} warns about a new asset type.
2. **Line 1159:** `None` leaves the `switch`.
3. **Line 1161:** the generic file icon.

The `switch` has no `default`, so the :term[compiler]{id=compiler} warns when a new `AssetType` is added and this function is not extended. The last line returns the generic file icon for `None`. This is the idea of the role table again: the shape of the code makes a gap loud.

### The brand mark and the window's icon

The strata mark is four staggered bands, graded from `Sandstone` at the top through `Ochre` and `Rust` to `Umber`, on a `Basalt` rounded square. Inside the editor, `UI::BrandMark(size, tile)` draws it as vectors with the draw list, so it stays sharp at any scale. Below 24 pixels it keeps three bands, so they stay apart.

The window's icon is different, because the system shows it at fixed sizes and a smaller image stretched up looks soft. The mark is therefore drawn at nine sizes: 16, 20, 24, 28, 32, 40, 48, 56 and 64 pixels. They are the small icon (title bar) and the large icon (task bar and Alt+Tab) of Windows at 100, 125, 150, 175 and 200 percent of display scaling. Those sizes are 16 and 32 pixels times the scale. The system picks the image whose area is nearest to what it needs, so with an exact one it never stretches.

`Tools/GenerateBrandAssets.py` draws each size from :term[signed distances]{id=signed-distance}, so no size is a scaled copy of another, and writes raw `RGBA8` files that the build embeds. A 256-pixel PNG, decoded at start, serves the macOS Dock. `SetEditorWindowIcon` in `EditorApplication.cpp` gives the window all ten images, and logs an error if the PNG does not decode.

### One theme only

The editor has one palette, installed by one style callback, and no preference chooses a theme. The preferences hold three sections (the external editor, the interface and the :term[frame rate]{id=frame-rate}), and none is a theme. `Docs/Roadmap.md` lists theme variants among the work left for later. Strata offers no editor theme other than Bedrock.

The design keeps a door open. Every color already reaches the style through a palette and a role table, so a second theme would be a second `ThemePalette` and a choice of which one `ApplyTheme` reads. The token names would need a second thought, because a token such as `Basalt` names a dark stone, and a light theme would not use it as its darkest surface.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Colors in a data file, loaded at start | Tools whose users choose their own look | Themes that people share and switch without a build | The compile-time check of the role table, and one place where a scan sees every color |
| Icons as images in an atlas | Many ImGui tools | Full-color icons of any shape | Icons that take the text's color and size, and one generator that lists every icon |
| The built-in font of ImGui only | Quick ImGui tools | No font files and no merge code | Clear text, the icons and every script beyond a small set |
| A font for those scripts compiled in | Tools that must not depend on the system | The same look on every machine | An :term[executable]{id=executable} that weighs tens of MB more |
| A fallback font read on the main thread | Simple tools | Less code and no counter | A stall of the first frames |

## How it is tested

The suite `Editor.UI.Source` in `StrataTests/src/Editor/EditorUISourceTests.cpp` holds the scans that enforce this page. The test "Colors come only from the theme" reads every UI source file, strips comments and strings, and fails on a color spelled as numbers. It finds a color type built from numbers, the packed color :term[macros]{id=macro} of ImGui and packed hex values such as `0xFF2020E0`. Only `UI/Theme.cpp` is exempt.

The test "The editor never uses ImGui's built-in font" searches for the call `AddFontDefault`. The test "Text is encoded as UTF-8 once" searches for the byte pair that a double encoding makes. The scans have tests of their own: "The color rule finds colors however they are written" feeds the rule samples and counts findings, and checks that `0xE000` inside a glyph range is no color. "The encoding rule finds characters encoded twice, and only those" does the same for the encoding.

The suite `Editor.UI` in `EditorUITests.cpp` holds the test `The editor's fonts: Inter by default, SemiBold and Mono, with every icon`. It checks the three faces and their names, that no font is the built-in one, and that `UI::PushFont` switches face and size. It also checks that every icon of `UI/Icons.h` has a glyph in the `Inter` faces, and that the face for code lacks the first icon. Another test, `A content scale event restyles the UI and scales its fonts`, sets a scale of 2 and checks that the paddings double while the check mark keeps the accent color.

Run a suite with `StrataTests.exe --test-suite=Editor.UI.Source`, for example. [The page on UI tests](../editor-ui/ui-testing.md) covers the scans in depth.

## Changing it safely

- **Add a meaning, not a color.** A new use of color gets a field in `ThemeColors` and a line in `c_Colors`, built from a token. A new token needs a field in `ThemePalette` and a row in `c_Tokens`, or the `static_assert` fails.
- **Give every ImGui upgrade its roles.** When the `static_assert` over `ImGuiCol_COUNT` fails after an upgrade, add a row for the new slot, with a token and an alpha. Do not widen the table or silence the check.
- **Keep the base sizes even.** A new size in `SetBaseSizes` is even, or zero, or 1 for a thin line, so it stays whole at 1.5 and 2.
- **Never merge a font from a project.** The trust boundary holds only while the atlas reads compiled-in and system files.
- **Compare the glyph generation.** A new cache of measured text widths keeps the value of `GetGlyphGeneration` and measures again when it changes.
- **Regenerate with the font.** A new `Lucide` release replaces `Lucide.ttf` and its code-point map, runs `GenerateIconHeader.py` and commits the header with them. Update `ThirdPartyNotices.md` in the same change.
- **Draw color samples as rectangles.** A shape that shows a value is never an icon glyph.

Before a commit, run `Editor.UI.Source` and `Editor.UI`.

## Summary

- A palette token reaches a widget through a meaning in `ThemeColors` or a row of the role table, and a `static_assert` over `ImGuiCol_COUNT` fails the build when ImGui adds a slot.
- The three faces are `Inter Regular`, `Inter SemiBold` and `JetBrains Mono`, with `Lucide` merged into the `Inter` faces in the Private Use Area, so a text font never shadows an icon. The system's font for Chinese, Japanese and Korean joins them between frames.
- Icons are text: `Icons::Play` is drawn like a word, and a color sample is a rectangle.
- The editor's atlas reads only compiled-in and system fonts, never a project's, so it may skip the engine's font validation.
- A new meaning is one field and one line, and a hex color in a panel fails `Editor.UI.Source`.

## Check yourself

1. A panel needs a color for search matches, and no meaning fits. Which is right? (a) `ImVec4(0.95, 0.72, 0.45, 1)`; (b) a new field `Highlight` in `ThemeColors`, set from `Sandstone`; (c) `0xF2B872`.
   :::answer{tests="add-meaning,tokens-roles"}
   Choice (b). The first and the third spell the color as numbers, which the scan of the sources finds and fails, whatever the value. A meaning keeps the color in one place, so a change of look is one line.
   :::
2. After an upgrade, ImGui has one more `ImGuiCol_` than `c_ColorRoles` has rows. What happens, and what do you do?
   :::answer{tests="tokens-roles"}
   The build fails at the `static_assert` over `ImGuiCol_COUNT`, with the message that every slot needs a token. You add a row with a token and an alpha for the new slot. You keep the check, because it is the only thing that tells you that one control would otherwise keep the default color of ImGui.
   :::
3. `Inter` holds a glyph at U+E585, and `Lucide` holds an icon there. Which one is drawn, and why?
   :::answer{tests="font-chain"}
   The icon. The text font is added with the icon range excluded, and `Lucide` is merged with only that range allowed, so a lookup in that range can reach only `Lucide`. The exclusion is why a text font can never shadow an icon.
   :::
4. A project name in Japanese shows as `?` during the first seconds after the editor starts, and then as the right characters. Why, and which counter changes?
   :::answer{tests="font-chain"}
   The system's font is read on an I/O job, which may take longer than the first frames. Until `UpdateFallback` merges it, the lookup ends at the fallback glyph. The merge raises `GetGlyphGeneration`, so any cache of text widths knows to measure again.
   :::
5. You want a small filled square before each list row, in the color of the row's level. Is that an icon?
   :::answer{tests="icons-text"}
   No. An icon is text and takes the color of the text around it, so it cannot show a color that a value chooses. A color sample is a rectangle drawn with the draw list, in a color from the theme.
   :::
6. Why may the editor's ImGui atlas read a font without the engine's validation?
   :::answer{tests="trust-boundary"}
   The atlas reads only the fonts compiled into the editor and the system's fallback fonts, never a project's file. The engine's validation protects against crafted files, and the editor's atlas never meets one.
   :::

## Exercises

1. **Basic.** The token `Seam` is `0x323840`. Write its three bytes in decimal, and its three floats to three decimals.
   :::answer[Worked solution]{tests="tokens-roles"}
   `0x32` is 3 times 16 plus 2, which is 50. `0x38` is 56, and `0x40` is 64. Divided by 255 they are 0.196, 0.220 and 0.251. The helper `FromRGB` does the same with a shift and a mask for each byte.
   :::
2. **Medium.** Add a meaning `Highlight`, from `Sandstone`. Say which two places change, and what a hex color written in a panel does.
   :::answer[Worked solution]{tests="add-meaning"}
   In `StrataEditor/src/UI/Theme.h` add `ImVec4 Highlight;` to `ThemeColors`, with a comment. In `UI/Theme.cpp` add `.Highlight = c_Bedrock.Sandstone,` to `c_Colors`, at the place of the field, because a list of named initial values must follow the order of the fields. A panel then calls `UI::GetThemeColors().Highlight`. If the panel wrote `ImVec4(0.95, 0.72, 0.45, 1)` instead, `Editor.UI.Source` would report `A color literal outside UI/Theme.cpp (use the theme's tokens)` with the file and line, and the test would fail.
   :::
3. **Medium.** Run the program below, which scales base sizes by 1.25, 1.5 and 2 and truncates them. Predict which sizes lose a fraction, then explain why `SetBaseSizes` keeps its sizes even.
   :::answer[Worked solution]{tests="tokens-roles" solution="sketches/editor-ui-design-system-scale.cpp"}
   The program scales each base size by each scale and prints it cut to whole pixels.

   ```cpp sketch="editor-ui-design-system-scale.cpp"
   // Scales base sizes by a UI scale and truncates, as ImGui's ScaleAllSizes does, then shows what was lost.
   #include <cstdio>

   int main()
   {
   	const float baseSizes[] = { 4.0f, 5.0f, 6.0f, 8.0f, 10.0f, 20.0f };
   	const float scales[] = { 1.25f, 1.5f, 2.0f };
   	for (const float scale : scales)
   	{
   		std::printf("scale %.2f:", scale);
   		for (const float base : baseSizes)
   		{
   			const float exact = base * scale;
   			const int whole = static_cast<int>(exact);
   			std::printf("  %g->%d%s", base, whole, exact == static_cast<float>(whole) ? "" : "*");
   		}
   		std::printf("\n");
   	}
   	return 0;
   }
   ```

   ```text output-of="editor-ui-design-system-scale.cpp"
   scale 1.25:  4->5  5->6*  6->7*  8->10  10->12*  20->25
   scale 1.50:  4->6  5->7*  6->9  8->12  10->15  20->30
   scale 2.00:  4->8  5->10  6->12  8->16  10->20  20->40
   ```

   1. **Line 14:** the cast to `int` cuts the fraction, as the scaling of ImGui does.
   2. **Line 15:** a star marks a size that lost a fraction.

   At 1.25 only 4, 8 and 20 stay exact, and at 1.5 the base 5 gives 7.5, which becomes 7. At 2 every size stays exact. The editor offers eight scales, from 75 % to 200 %, and even bases are exact at 1.5 and 2, the two `SetBaseSizes` aims at. Elsewhere some sizes lose a fraction.
   :::
4. **Hard.** Trace it yourself: find which token the color of `ImGuiCol_Button` comes from, and where the call is made again when the UI scale changes.
   :::answer[Worked solution]{tests="tokens-roles"}
   Search `Theme.cpp` for `ImGuiCol_Button`. The row `{ ImGuiCol_Button, &ThemePalette::Flint, 1.0f }` in `c_ColorRoles` names `Flint`. A breakpoint in `ApplyTheme` shows the loop that writes `style.Colors[role.Slot]` from the palette, and the call stack above it shows `ImGuiLayer::ApplyStyle`, which calls the callback again after every change of the UI scale.
   :::

## Where it lives in Strata

- `StrataEditor/src/UI/Theme.h`, `Theme.cpp`: `ThemePalette`, `ThemeColors`, `c_ColorRoles`, `ApplyTheme`, `GetThemePaletteTokens`.
- `StrataEditor/src/UI/EditorFonts.h`, `EditorFonts.cpp`: `EditorFonts::Load`, the fallback functions, `GetGlyphGeneration`, `UI::PushFont`, `TextSize`.
- `StrataEditor/src/UI/Icons.h` and `StrataEditor/Tools/GenerateIconHeader.py`: the generated icons.
- `StrataEditor/src/UI/EntityIcons.cpp`, `PropertyWidgets.cpp`: component and asset-type icons.
- `StrataEditor/src/EditorIcon.h`, `EditorApplication.cpp`, `Tools/GenerateBrandAssets.py`: the window's icon.
- `StrataEditor/Resources/Fonts`, `StrataEditor/CMakeLists.txt`, `ThirdPartyNotices.md`: fonts, embedding and licenses.
- `Strata/src/Strata/ImGui/ImGuiLayer.cpp`: `ImGuiLayer::ApplyStyle`.
- `StrataTests/src/Editor/EditorUISourceTests.cpp`, `EditorUITests.cpp`: the scans and the font test.

## Further reading

- Dear ImGui, the font documentation in `docs/FONTS.md` of its repository (guide; intermediate): merge mode, ranges and atlases.
- Brad Frost, "Atomic Design" (book, free online; beginner): design systems, tokens and how teams keep a look.
- The Unicode Standard, the chapter on private-use characters (specification; advanced): what the Private Use Area promises.
- Google, "Material Design" guides on color roles (documentation; beginner): the idea of meanings over raw colors.
