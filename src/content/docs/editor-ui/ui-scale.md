---
id: editor-ui/ui-scale
title: "Pixels, points and UI scale"
description: "How the editor keeps its interface the same size on every display: the content scale, points and pixels, and the style that Strata rebuilds from unscaled sizes."
kind: internals
size: M
tracks: [E]
needs: [editor-ui/imgui-backends]
time: 60
learn:
  - id: predict-scale
    text: predict the UI scale of a display from its content scale, its window and framebuffer sizes, the person's factor and the override
  - id: rebuild-style
    text: explain why `ApplyStyle` builds the style from unscaled defaults every time
  - id: whole-pixels
    text: explain why the theme's base sizes are even, and which sizes cutting down changes
  - id: font-relative
    text: write a widget size that stays crisp at any UI scale
since: 0.4.0
status: final
---

A person who opens the editor on a small laptop and on a monitor with a very fine grid of dots expects the same user interface (UI): buttons to hit and text to read. The editor does not know in advance how many dots a centimetre of the display holds. This page follows one number, the **UI scale**, from the window system to every padding and border of the interface. It shows how Strata decides that number, applies it, and keeps the result sharp.

The page covers `ImGuiLayer::ToUIScale`, the factor and the override, `ApplyStyle`, the theme's base sizes and the display values that the platform backend sets each frame. It does not cover the theme's colors, type scale and fonts ([the design system](design-system.md)), the Preferences window ([settings windows](settings-windows.md)), every option of the editor's :term[command line]{id=terminal-command}, or the canvas scale of a game's own interface.

## The problem and how engines solve it

Displays differ in density: the number of dots, called **pixels**, that fit in a centimetre. A laptop from ten years ago has about 100 pixels in an inch. A modern phone or a Retina display, Apple's name for a display of twice that density, has about 200 or more. A button drawn 24 pixels high is a comfortable 6 mm on the first display and a tiny 3 mm on the second.

The :term[operating system]{id=operating-system} helps with a number, the :term[content scale]{id=content-scale}. It is the factor by which a window's contents should grow on this display: 1 at the platform's default density, 1.5 on a Windows display set to 150 %, 2 on a Retina display. [Windows, events and layers](../core/windows-events.md) explains how the number reaches a program as an event; this page only uses it.

The systems then disagree about what a window's size means. On Windows and X11 a window of 1600 by 900 has 1600 by 900 pixels, even at a content scale of 1.5. On macOS and Wayland a window of 1600 by 900 is measured in **points**, a unit that is one pixel at scale 1 and grows with the scale. At a content scale of 2 that window holds 3200 by 1800 pixels, and its :term[framebuffer]{id=framebuffer}, the image the program draws into, is twice as large as the window in each direction. The window system has already applied the scale there; a program that scales again draws everything four times too large in area.

Engines and tools solve this in two ways.

- **Scale at draw time.** The program lays out in pixels and multiplies every size by the scale. This is simple, and it is what Strata does for sizes. Its cost is that every size must go through the multiplication, or that size stays too small.
- **Lay out in points, rasterize for the framebuffer.** The program lays out in window units and only the fonts are drawn with more pixels, at the framebuffer's density. Sizes need no multiplication, but the program must know which unit each number is in, and a content scale above the display's density still needs a factor.

Strata combines them. It lays out in window units, which are pixels on Windows and X11 and points on macOS and Wayland. It scales the style of the interface, the table of paddings, spacings, roundings and border widths of the :term[ImGui]{id=dear-imgui} library the editor draws with, by the UI scale. It divides the points factor out of the content scale first, so that a Retina window is not scaled twice. It also tells ImGui the framebuffer density, so that glyphs are drawn with enough pixels.

## The map

Five steps turn the display's numbers into a style. Each step has one owner, and only the last one touches ImGui.

```mermaid caption="The path of the UI scale, from the display's numbers to the style and the font scale." alt="A flow from left to right with four boxes. The display's content scale and sizes enter the first, which divides out the points factor. The next multiplies by the person's factor or uses the override, the third clamps to 0.5 to 4, and the last builds the style and the font scale."
flowchart LR
    E["Content scale event"] --> T["ToUIScale: divide out the points factor"]
    S["Window and framebuffer sizes"] --> T
    T --> F["Times the person's factor, or the override"]
    F --> C["Clamp to 0.5 to 4"]
    C --> A["ApplyStyle"]
    A --> D["Unscaled defaults, theme callback, FontScaleDpi"]
```

The `ImGuiLayer` in `Strata/src/Strata/ImGui/ImGuiLayer.cpp` runs the whole path. It calculates the display's scale again when the layer attaches, when a `WindowContentScaleEvent` arrives and at the start of every frame, because on a points display the framebuffer size may change after the event. The person's factor comes from the editor's Interface preference (**Preferences ▸ Interface**, described in [settings windows](settings-windows.md)); the editor application gives it to the layer through `EditorHost::SetUIScaleFactor`. The `--ui-scale` option of the editor gives the override.

## The contract

What callers may assume, and what they must do:

- **The UI scale is always in [0.5, 4].** A value outside the range is clamped. A content scale, factor or override of less than zero, or one that is not a finite number, is ignored with a warning, and the old value stays. A content scale or factor of zero is ignored too.
- **The override wins.** A non-zero override replaces the content scale and the factor together. Zero returns to the display's scale.
- **The style is a function of the scale alone.** Any code that asks for a rebuild gets the same style for the same scale, whatever the style was before.
- **Sizes are multiples of the font size, or pass through the scaled style.** A size written as a number of pixels does not grow with the scale.

:::rule
Build the style from unscaled defaults every time. Scaling an already scaled style compounds: at 1.5 twice, an 8-pixel padding becomes 18 pixels, not 12. The rule comes from `AGENTS.md`; the reasons and tests are under [Changing it safely](#changing-it-safely).
:::

:::rule
Sizes are relative to the font; no fixed pixel size above 16. The scale multiplies the font size, so a size that follows the font follows the scale, and a fixed size does not.
:::

## A toy version

Before the real code, a toy that computes the same number. It has the display's three numbers, a two-field style and the same cut to whole pixels as ImGui. Read the three prints for the displays, then the three prints for the style.

:::question
The toy uses functions, :term[structs]{id=struct}, `std::clamp` and calls such as `std::printf(`. Read [functions and structs](../basics/programming-2.md) and [classes and calls](../basics/programming-3.md) first if they are new.
:::

The program below follows the real order: points factor out, factor in, clamp, then scale every size and cut it to whole pixels. It is about sixty lines, and it never touches a window.

```cpp sketch="editor-ui-ui-scale-toy.cpp"
// A toy of the editor's UI scale: the display's numbers in, a whole-pixel style out.
#include <algorithm>
#include <cmath>
#include <cstdio>

struct Display
{
	float ContentScale = 1.0f;
	int WindowWidth = 0;
	int FramebufferWidth = 0;
};

struct Style
{
	float Padding = 0.0f;
	float Border = 0.0f;
};

float ToUIScale(const Display& display)
{
	if (display.WindowWidth == 0 || display.FramebufferWidth == 0)
		return display.ContentScale;
	const float pixelsPerUnit = static_cast<float>(display.FramebufferWidth) / static_cast<float>(display.WindowWidth);
	if (pixelsPerUnit <= 1.0f)
		return display.ContentScale;
	return display.ContentScale / pixelsPerUnit;
}

float GetUIScale(const Display& display, float factor, float overrideScale)
{
	if (overrideScale > 0.0f)
		return std::clamp(overrideScale, 0.5f, 4.0f);
	return std::clamp(ToUIScale(display) * factor, 0.5f, 4.0f);
}

// Like ImGuiStyle::ScaleAllSizes: every size is scaled, then cut to whole pixels.
void ScaleAllSizes(Style& style, float scale)
{
	style.Padding = std::trunc(style.Padding * scale);
	style.Border = std::trunc(style.Border * scale);
}

int main()
{
	const Display windows{ 1.5f, 1600, 1600 };
	const Display retina{ 2.0f, 1440, 2880 };
	std::printf("Windows 150%%, factor 1.25: %.3f\n", GetUIScale(windows, 1.25f, 0.0f));
	std::printf("Retina, factor 1: %.3f\n", GetUIScale(retina, 1.0f, 0.0f));
	std::printf("Override 5: %.3f\n", GetUIScale(windows, 1.25f, 5.0f));

	Style fresh{ 8.0f, 1.0f };
	ScaleAllSizes(fresh, 1.5f);
	std::printf("Fresh style at 1.5: padding %.0f, border %.0f\n", fresh.Padding, fresh.Border);

	Style twice{ 8.0f, 1.0f };
	ScaleAllSizes(twice, 1.5f);
	ScaleAllSizes(twice, 1.5f);
	std::printf("Scaled twice: padding %.0f, border %.0f\n", twice.Padding, twice.Border);

	Style odd{ 5.0f, 1.0f };
	ScaleAllSizes(odd, 1.5f);
	std::printf("Odd base 5 at 1.5: padding %.0f\n", odd.Padding);
}
```

```text output-of="editor-ui-ui-scale-toy.cpp"
Windows 150%, factor 1.25: 1.875
Retina, factor 1: 1.000
Override 5: 4.000
Fresh style at 1.5: padding 12, border 1
Scaled twice: padding 18, border 1
Odd base 5 at 1.5: padding 7
```

1. **Line 24:** a ratio of 1 or less means the window system applied no scale, so the content scale stays.
2. **Line 26:** on a points display the ratio is divided out, so the window is not scaled twice.
3. **Line 33:** the person's factor multiplies the display's scale, and the clamp limits the product.
4. **Line 39:** every size is cut down to whole pixels, as `ImGuiStyle::ScaleAllSizes` does.

The Windows display at 150 % has one pixel per window unit, so the display's scale is 1.5, and the factor of 1.25 gives 1.875. The Retina display has a ratio of 2, so its content scale of 2 is divided out and the UI scale is 1: the window system has scaled the window already. The override of 5 is cut to 4. A padding of 8 scaled once is 12 and scaled twice is 18. A padding of 5, an odd base size, loses half a pixel when it is cut to whole pixels.

## The real code

### From the display to the scale

The first function is the points rule. It takes the content scale and the two widths; the height tells nothing more. It returns the scale the window system has not applied already.

```cpp src="Strata/src/Strata/ImGui/ImGuiLayer.cpp#L171-L176" from="if (windowSize.x == 0" to="return contentScale / pixelsPerUnit;" symbol="ImGuiLayer::ToUIScale"
if (windowSize.x == 0 || framebufferSize.x == 0)
	return contentScale;
const float pixelsPerUnit = static_cast<float>(framebufferSize.x) / static_cast<float>(windowSize.x);
if (!std::isfinite(pixelsPerUnit) || pixelsPerUnit <= 1.0f)
	return contentScale;
return contentScale / pixelsPerUnit;
```

The first test covers a minimized window, which has no size: the content scale passes through unchanged. The ratio of framebuffer width to window width is the number of pixels per window unit, 1 on Windows and X11 and 2 on a Retina display. A ratio of 1 or less, or one that is not finite, leaves the content scale alone; otherwise the ratio is divided out. The `ImGui.Layer` suite checks a content scale of 3 on a window of 1600 points with 3200 pixels. The answer is 1.5: the display has a larger text setting than its density, and that remainder stays.

### The factor, the override and the clamp

`GetUIScale` is the second step. It returns the override when one is set, and otherwise the display's scale times the person's factor, clamped.

```cpp src="Strata/src/Strata/ImGui/ImGuiLayer.cpp#L210-L215" symbol="ImGuiLayer::GetUIScale"
float ImGuiLayer::GetUIScale() const
{
	if (m_ContentScaleOverride > 0.0f)
		return m_ContentScaleOverride;
	return std::clamp(m_ContentScale * m_ContentScaleFactor, c_MinScale, c_MaxScale);
}
```

The override is clamped when it is set, in `SetContentScaleOverride`, which runs the same validation as the content scale, so the early return needs no second clamp. The product of scale and factor needs one: 4 is the limit, so a content scale of 3 with a factor of 2 gives 4, not 6. A second function, `GetDisplayUIScale`, returns the override or the content scale without the factor. The next section uses it.

### Building the style

`ApplyStyle` runs whenever the content scale, the override or the factor changes.

```cpp src="Strata/src/Strata/ImGui/ImGuiLayer.cpp#L223-L230" from="const float scale = GetUIScale();" to="style.FontScaleDpi = scale;" symbol="ImGuiLayer::ApplyStyle"
const float scale = GetUIScale();
ImGuiStyle style;
ImGui::StyleColorsDark(&style);
if (m_StyleCallback)
	m_StyleCallback(style, scale);
else
	style.ScaleAllSizes(scale);
style.FontScaleDpi = scale;
```

The local `style` is a new `ImGuiStyle` that `ImGui::StyleColorsDark` fills with ImGui's own defaults, which are unscaled. The theme's :term[callback]{id=callback}, `ApplyTheme` in the editor, receives it and the scale and does the scaling itself; without a callback, `ScaleAllSizes` scales the defaults. The last line sets **FontScaleDpi**, the global factor that ImGui multiplies into the font size. It makes text grow with the scale, so a fully scaled style still has small text if this line is missing. The result replaces ImGui's current style, and nothing of the old style survives, so nothing compounds.

### The theme's base sizes

`ApplyTheme` sets the base sizes, calls `ScaleAllSizes(scale)` and then sets `MouseCursorScale` by hand, because it is a factor and not a size: it sizes the mouse cursor that ImGui draws and the offset of tooltips. The base sizes are the second half of the story.

```cpp src="StrataEditor/src/UI/Theme.cpp#L178-L184" from="style.WindowPadding = ImVec2(8.0f, 8.0f);" to="style.CellPadding = ImVec2(6.0f, 4.0f);" symbol="SetBaseSizes"
style.WindowPadding = ImVec2(8.0f, 8.0f);
style.WindowMinSize = ImVec2(32.0f, 32.0f);
style.WindowBorderHoverPadding = 4.0f;
style.FramePadding = ImVec2(8.0f, 4.0f);
style.ItemSpacing = ImVec2(8.0f, 6.0f);
style.ItemInnerSpacing = ImVec2(6.0f, 4.0f);
style.CellPadding = ImVec2(6.0f, 4.0f);
```

Every number here is even. `ScaleAllSizes` multiplies each size and cuts it down to a whole number, so a size of 5 at 1.5 becomes 7 where the exact answer is 7.5. An even size gives an exact whole pixel at 1.5 (8 gives 12, 6 gives 9) and at 2 (8 gives 16). The thin one-pixel lines stay at 1 pixel at 1.5 and grow to 2 at a scale of 2. The `Editor.Theme` suite checks that the sizes are exact multiples at 1, 1.5 and 2, and that each thin line equals the scale rounded down.

### The platform backend

Last, the backend that feeds ImGui each frame. It reports the window's size in window units and the framebuffer scale, so that fonts and images are drawn with enough pixels.

```cpp src="Strata/src/Strata/ImGui/ImGuiPlatform.cpp#L192-L197" from="io.DisplaySize = ImVec2(width, height);" to="io.DisplayFramebufferScale = ImVec2(static_cast<float>(framebuffer.x) / width, static_cast<float>(framebuffer.y) / height);" symbol="ImGuiPlatform::NewFrame"
io.DisplaySize = ImVec2(width, height);
// Pixels per window unit: 1 where windows are measured in pixels (Windows), 2 on a Retina display (macOS).
if (width > 0.0f && height > 0.0f)
{
	const glm::uvec2 framebuffer = m_Window->GetFramebufferSize();
	io.DisplayFramebufferScale = ImVec2(static_cast<float>(framebuffer.x) / width, static_cast<float>(framebuffer.y) / height);
```

`DisplaySize` is in window units, the unit of every size in the style. `DisplayFramebufferScale` is the ratio of pixels to window units: 1 on Windows, 2 on a Retina display. ImGui draws glyphs with that density, and so a Retina interface has a UI scale of 1 yet sharp text. The guard on width and height keeps a minimized window from dividing by zero. The same function sets the :term[delta time]{id=delta-time} from the clock, with a first frame of 1/60 of a second and a minimum step of one microsecond afterwards.

### Play mode

In play mode the editor runs a game inside its **Game** view, and the game also has a content scale. `EditorLayer` hands the game `GetDisplayUIScale`, the override or the display's scale without the person's factor. The factor sizes the editor's own interface; a player has no such factor, so a game canvas in the Game view keeps the size a player's display gives it.

:::example
Three displays, by hand. Display A is a Windows laptop with a content scale of 1.5, a window of 1600 by 900 with the same framebuffer, and Interface at 125 %. Display B is a Retina laptop with a content scale of 2, a window of 1440 by 900 points, a framebuffer of 2880 by 1800 and Interface at Automatic. Display C is display A with `--ui-scale 5`.

For A the ratio of framebuffer to window is 1600 / 1600 = 1, so `ToUIScale` returns 1.5. Times the factor 1.25 gives 1.875, inside [0.5, 4]. The theme's frame padding, base (8, 4), is multiplied and cut down: 8 × 1.875 = 15 and 4 × 1.875 = 7.5, which becomes 7. The padding is (15, 7), and the text grows by 1.875.

For B the ratio is 2880 / 1440 = 2, so `ToUIScale` returns 2 / 2 = 1. The factor is 1, so the UI scale is 1 and the padding stays (8, 4) in points, which is (16, 8) pixels on the panel. `DisplayFramebufferScale` is 2, so the glyphs are drawn with twice the pixels.

For C the override of 5 is clamped to 4 when it is set, and it replaces the 1.875. The padding is (32, 16). In play mode the game gets 4 in C and 1.5 in A, because the factor of A is omitted.
:::

The drawing shows the effect of the number on one panel of the editor, drawn to scale from the theme's sizes.

::figure{id=scale-rows}

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Scale the whole frame: draw at one size, then enlarge the image | Programs with a fixed canvas | One code path and no scale in the style | Soft text, and borders that grow with the image |
| Rely on ImGui's own automatic scaling of fonts by monitor | Programs that enable ImGui's experimental font scaling by display density | No `ApplyStyle` of our own | The experimental option scales fonts but not sizes, paddings or borders |
| Lay out in points everywhere, with the framebuffer scale only for fonts | Programs that use points only | No division of the points factor | A different rule per platform in every panel, and no person's factor |
| Scale the existing style in place | Programs that patch the style at each change | A shorter function | Sizes that compound at every change of display |
| Odd base sizes and rounding | Themes with free sizes | Freer sizes | Half pixels at 150 %, so uneven borders and padding |

## How it is tested

Three suites check the rules, and all three run without a :term[graphics card]{id=gpu}.

- `ImGui.Layer` (`StrataTests/src/ImGui/ImGuiLayerTests.cpp`) calls `ImGuiLayer::ToUIScale` for the Windows, Retina, larger text and minimized cases, and checks the layer's styling.
- `Editor.Preferences` (`StrataTests/src/Editor/EditorPreferencesTests.cpp`) checks the factor, the override and `GetDisplayUIScale`, including factors of zero or less.
- `Editor.Theme` (`StrataTests/src/Editor/EditorThemeTests.cpp`) checks the exact multiples at 1, 1.5 and 2, and that a style scaled before gets the same sizes as a fresh one after `ApplyTheme`.
- `Editor.UI.Source` has the case `Sizes scale with the font`, which scans the editor's UI sources for calls such as `Button`, `SetNextItemWidth` and `SameLine` with a fixed size above 16.

To run one suite directly, name it as a doctest filter: `build/windows/bin/Debug/StrataTests.exe --test-suite=ImGui.Layer`. The source scan reports each fixed pixel size with its file and call.

## Changing it safely

- **Add a size to the theme as an even number.** Put it in `SetBaseSizes`, and `ScaleAllSizes` scales it. Run `Editor.Theme`.
- **Never keep a scaled style.** Whatever you add must be set again in the callback, or it compounds. The test with `reused` catches a size that the theme does not set.
- **A new widget takes its size from the font.** Write `ImGui::GetFontSize() * 8.0f` or the style's spacing, not `200.0f`. The scan `Sizes scale with the font` fails otherwise, and so does your display at 200 %.
- **A new place that converts units asks `ImGuiLayer`.** Never divide by the content scale in a panel; the layer knows which platform measures in points.
- **A factor that is not a size is set by hand.** `MouseCursorScale` is an example: `ScaleAllSizes` cuts it to a whole number, which is 1 at 150 %.

## Summary

- The UI scale is the content scale divided by the framebuffer-to-window ratio when that ratio is above 1, times the person's factor, or the override, clamped to [0.5, 4].
- `ApplyStyle` builds the style from ImGui's unscaled defaults every time, because scaling a scaled style compounds.
- The theme's base sizes are even or zero, and thin lines are 1 pixel, so cutting down gives whole pixels at 1.5 and 2.
- A size relative to the font follows the UI scale; a fixed pixel size above 16 does not.

## Check yourself

1. A Windows display has a content scale of 1.25, a window of 1920 by 1080 pixels and a framebuffer of the same size. Interface is at 150 %. What is the UI scale?

   - A. 1.25
   - B. 1.875
   - C. 3.75

   :::answer{tests="predict-scale"}
   B. The ratio is 1, so `ToUIScale` returns 1.25; the factor 1.5 gives 1.875. A omits the factor. C divides when it should multiply.
   :::

2. A Retina laptop has a content scale of 2, a window of 1280 by 800 points and a framebuffer of 2560 by 1600. Interface is Automatic. What is the UI scale, and what is `DisplayFramebufferScale`?

   :::answer{tests="predict-scale"}
   The ratio is 2, so the UI scale is 2 / 2 = 1, and `DisplayFramebufferScale` is 2. The window system has scaled the window already, and ImGui draws fonts with twice the pixels.
   :::

3. A developer calls `style.ScaleAllSizes(1.5f)` on `ImGui::GetStyle()` each time the content scale event arrives. The display moves from scale 1.5 to 1.5 again. What goes wrong, and which line of `ApplyStyle` prevents it?

   :::answer{tests="rebuild-style"}
   Each call multiplies the sizes already scaled: an 8-pixel padding is 12, then 18. `ApplyStyle` declares a new `ImGuiStyle` and fills it with `ImGui::StyleColorsDark`, so no old size survives. Setting `FontScaleDpi` replaces a value and compounds nothing.
   :::

4. Why is a base size of 5 a poor choice, and a base size of 6 a good one?

   :::answer{tests="whole-pixels"}
   At 1.5 a size of 5 gives 7.5, and `ScaleAllSizes` cuts it down to 7, so the edge is half a pixel too small and uneven beside its neighbours. A size of 6 gives exactly 9, and 6 at 2 gives 12.
   :::

5. A new panel draws `ImGui::Button("Run", ImVec2(200.0f, 0.0f))`. What does the editor do at a UI scale of 2, and how do you fix it?

   :::answer{tests="font-relative"}
   The button stays 200 pixels while the text doubles, so the label crowds it, and the source scan fails. Use a width that follows the font, such as `ImGui::GetFontSize() * 12.0f`.
   :::

## Exercises

1. **Basic.** Predict the UI scale of three displays. First, Windows at a content scale of 1.5 and Interface at 125 %. Second, a Retina laptop at 2 and Interface at Automatic. Third, any display with `--ui-scale 5`.

   :::answer[Worked solution]{tests="predict-scale"}
   The first: the ratio is 1, so 1.5 × 1.25 = 1.875. The second: 2 / 2 = 1, times 1 is 1. The third: the override replaces the display's scale and the factor, and 5 is clamped to 4.
   :::

2. **Medium.** Trace it yourself: find where the editor learns that the window moved to a display of another density, and which two sizes it reads then.

   :::answer[Worked solution]{tests="predict-scale"}
   Set a breakpoint in `ImGuiLayer::ToUIScale` in `Strata/src/Strata/ImGui/ImGuiLayer.cpp`, then drag the window to the other display. It is called from the handler of `WindowContentScaleEvent` and from `ImGuiLayer::Begin`. The sizes it reads are the window size from `Window::GetWidth` and `Window::GetHeight`, and the framebuffer size from `Window::GetFramebufferSize`. On a Retina display the second is twice the first.
   :::

3. **Hard.** Add to the toy a function `ScaledWidth(float fontSize, float scale)` that returns a button width of eight font heights, cut to whole pixels, and print it at scales 1, 1.5 and 2 for a font size of 16. Say why this width needs no fixed pixels.

   :::answer[Worked solution]{tests="font-relative" solution="sketches/editor-ui-ui-scale-width.cpp"}
   The width is eight times the font size, and the font size is the base size times the scale, so the width follows the scale by itself. The sketch below multiplies the three and cuts the result to whole pixels.

   ```cpp sketch="editor-ui-ui-scale-width.cpp"
   // A button width of eight font heights, cut to whole pixels, at three UI scales.
   #include <cmath>
   #include <cstdio>
   #include <initializer_list>

   float ScaledWidth(float fontSize, float scale)
   {
   	return std::trunc(8.0f * fontSize * scale);
   }

   int main()
   {
   	for (const float scale : { 1.0f, 1.5f, 2.0f })
   		std::printf("Scale %.1f: width %.0f\n", scale, ScaledWidth(16.0f, scale));
   }
   ```

   ```text output-of="editor-ui-ui-scale-width.cpp"
   Scale 1.0: width 128
   Scale 1.5: width 192
   Scale 2.0: width 256
   ```

   1. **Line 8:** the width is eight font heights times the scale, cut to whole pixels.
   2. **Line 13:** the loop tries the three scales of the exercise.

   The widths are 128, 192 and 256 pixels, so the button keeps its share of the text at every scale.
   :::

## Where it lives in Strata

- `Strata/src/Strata/ImGui/ImGuiLayer.cpp`: `ToUIScale`, `GetUIScale`, `SetContentScaleFactor`, `SetContentScaleOverride` and `ApplyStyle`; the limits are `c_MinScale` and `c_MaxScale` in `ImGuiLayer.h`.
- `Strata/src/Strata/ImGui/ImGuiPlatform.cpp`: `NewFrame` sets the display size and the framebuffer scale.
- `StrataEditor/src/UI/Theme.cpp`: `ApplyTheme` and `SetBaseSizes`.
- `StrataEditor/src/EditorLayer.cpp`: gives the factor to the host and the display's scale to the game.
- Option `--ui-scale <factor>` of `StrataEditor`; the preference **Preferences ▸ Interface ▸ Scale** with the steps Automatic, 75 %, 90 %, 110 %, 125 %, 150 %, 175 % and 200 %.
- Tests: `ImGui.Layer`, `Editor.Preferences`, `Editor.Theme` and `Editor.UI.Source`.

## Further reading

- Dear ImGui's FAQ and its documents on scaling and display density: what `FontScaleDpi`, `ScaleAllSizes` and `DisplayFramebufferScale` mean (intermediate).
- Apple's documentation on points and pixels on Retina displays (beginner).
- The Wayland protocol documents on output scale (advanced).
