#include <algorithm>
#include <cstdio>

#include <glm/glm.hpp>

// Where the game's picture lies inside the window, and how many pixels the game renders into it.
struct Viewport
{
	glm::vec2 Origin;     // Window pixels of the picture's top-left corner
	glm::vec2 Size;       // The picture's size in window pixels
	glm::vec2 Resolution; // The game's own pixels
};

glm::vec2 ToGamePixels(const glm::vec2& windowPoint, const Viewport& viewport)
{
	const glm::vec2 scale = viewport.Resolution / viewport.Size;
	return (windowPoint - viewport.Origin) * scale;
}

glm::vec2 ToGameDelta(const glm::vec2& windowDelta, const Viewport& viewport)
{
	// A movement has no origin: only the scale applies.
	return windowDelta * (viewport.Resolution / viewport.Size);
}

// A visible cursor cannot leave the window: its position stops at the last pixel.
float MoveVisible(float x, float dx, float windowWidth)
{
	return std::clamp(x + dx, 0.0f, windowWidth - 1.0f);
}

int main()
{
	const Viewport viewport = { { 40.0f, 30.0f }, { 960.0f, 540.0f }, { 1920.0f, 1080.0f } };

	const glm::vec2 point = ToGamePixels({ 520.0f, 300.0f }, viewport);
	std::printf("window (520, 300) is game pixel (%.0f, %.0f)\n", point.x, point.y);

	const glm::vec2 delta = ToGameDelta({ 10.0f, -5.0f }, viewport);
	std::printf("a move of (10, -5) is (%.0f, %.0f) game pixels\n", delta.x, delta.y);

	// The player pushes the mouse right by 20 pixels, three frames in a row, near the edge of an 800 pixel window.
	float visible = 790.0f;
	float virtualPosition = 790.0f;
	for (int frame = 1; frame <= 3; ++frame)
	{
		const float next = MoveVisible(visible, 20.0f, 800.0f);
		const float seenDelta = next - visible;
		visible = next;
		virtualPosition += 20.0f; // A locked cursor has no edge
		std::printf("frame %d: visible position %.0f, its delta %.0f; locked position %.0f, its delta 20\n", frame, visible, seenDelta, virtualPosition);
	}
	return 0;
}
