// A toy Game view: fit an aspect ratio in a panel, map a mouse position to the game's pixels, decide who gets the keys.
#include <cmath>
#include <cstdio>
#include <glm/glm.hpp>

struct Frame
{
	glm::vec2 Offset;
	glm::vec2 Size;
};

// The largest rectangle of the aspect ratio inside the area, centered on whole units.
Frame FitAspect(const glm::vec2& area, float aspect)
{
	glm::vec2 size(area.x, area.x / aspect);
	if (size.y > area.y)
		size = glm::vec2(area.y * aspect, area.y);
	size = glm::floor(size);
	return { glm::floor((area - size) * 0.5f), size };
}

// A window position in the game's pixels: out of the panel, out of the bars, then scaled to the resolution.
glm::vec2 ToGamePixel(const glm::vec2& mouse, const glm::vec2& areaMin, const Frame& frame, const glm::vec2& resolution)
{
	return (mouse - areaMin - frame.Offset) * resolution / frame.Size;
}

struct EditorState
{
	bool Modal;
	bool Playing;
	bool GameShown;
	bool GameFocused;
};

bool GameGetsInput(const EditorState& state)
{
	return state.GameShown && state.GameFocused && state.Playing;
}

bool EditShortcutsAllowed(const EditorState& state)
{
	return !state.Modal && !GameGetsInput(state);
}

int main()
{
	const glm::vec2 areaMin(100.0f, 50.0f);
	const Frame frame = FitAspect(glm::vec2(900.0f, 800.0f), 16.0f / 9.0f);
	std::printf("image %.0f x %.0f at offset %.0f, %.0f\n", frame.Size.x, frame.Size.y, frame.Offset.x, frame.Offset.y);

	const glm::vec2 pixel = ToGamePixel(glm::vec2(550.0f, 400.0f), areaMin, frame, glm::vec2(1920.0f, 1080.0f));
	std::printf("mouse (550, 400) is game pixel %.1f, %.1f\n", pixel.x, pixel.y);

	const EditorState editing = { false, false, true, true };
	const EditorState playing = { false, true, true, true };
	const EditorState typing = { false, true, true, false };
	std::printf("editing: game %d, edit keys %d\n", GameGetsInput(editing), EditShortcutsAllowed(editing));
	std::printf("playing: game %d, edit keys %d\n", GameGetsInput(playing), EditShortcutsAllowed(playing));
	std::printf("typing in the Inspector: game %d, edit keys %d\n", GameGetsInput(typing), EditShortcutsAllowed(typing));
	return 0;
}
