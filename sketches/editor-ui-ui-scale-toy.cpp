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
