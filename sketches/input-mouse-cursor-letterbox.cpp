#include <algorithm>
#include <cstdio>

#include <glm/glm.hpp>

int main()
{
	// A panel of 1000 x 600 window pixels at (100, 50) shows a 1920 x 1080 game.
	const glm::vec2 panelOrigin = { 100.0f, 50.0f };
	const glm::vec2 panelSize = { 1000.0f, 600.0f };
	const glm::vec2 resolution = { 1920.0f, 1080.0f };

	// Assumption of this exercise: the picture is centered, at the largest size that keeps the game's shape.
	const float fit = std::min(panelSize.x / resolution.x, panelSize.y / resolution.y);
	const glm::vec2 size = resolution * fit;
	const glm::vec2 origin = panelOrigin + (panelSize - size) * 0.5f;
	std::printf("picture origin (%.2f, %.2f), size (%.2f, %.2f)\n", origin.x, origin.y, size.x, size.y);

	const glm::vec2 clicks[] = { { 350.0f, 200.0f }, { 350.0f, 60.0f } };
	for (const glm::vec2& click : clicks)
	{
		const glm::vec2 game = (click - origin) * (resolution / size);
		std::printf("window (%.0f, %.0f) is game pixel (%.2f, %.2f)\n", click.x, click.y, game.x, game.y);
	}
	return 0;
}
