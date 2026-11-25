// The window width, in screen coordinates, that gives a wanted framebuffer width: the window's size is scaled by the
// ratio of the window to its framebuffer, the way a windowed window's resolution is set.
#include <algorithm>
#include <cmath>
#include <cstdio>

struct Display
{
	const char* Name;
	int WindowWidth;      // screen coordinates
	int FramebufferWidth; // pixels
};

static int WindowWidthFor(int wantedPixels, const Display& display)
{
	if (display.WindowWidth <= 0 || display.FramebufferWidth <= 0)
		return wantedPixels;
	const double ratio = static_cast<double>(display.WindowWidth) / display.FramebufferWidth;
	return std::max(1, static_cast<int>(std::lround(wantedPixels * ratio)));
}

int main()
{
	const Display displays[] = {
		{ "pixels", 1600, 1600 },
		{ "points", 1600, 3200 },
		{ "odd", 1280, 1920 },
	};
	for (const Display& display : displays)
	{
		std::printf("%s: window %d, framebuffer %d: ask for %d\n", display.Name, display.WindowWidth,
			display.FramebufferWidth, WindowWidthFor(1920, display));
	}
	return 0;
}
