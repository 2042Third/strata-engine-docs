// A toy of the UI's pointer input: rects in draw order, a hit test from the last drawn, and a gesture.
#include <glm/glm.hpp>

#include <cstdio>
#include <optional>
#include <string>
#include <vector>

struct Rect
{
	std::string Name;
	glm::vec2 Min;
	glm::vec2 Size;
	bool Button;
};

// Half-open: the minimum edges are inside, the maximum edges are not.
static bool Contains(const Rect& rect, glm::vec2 point)
{
	return point.x >= rect.Min.x && point.y >= rect.Min.y && point.x < rect.Min.x + rect.Size.x && point.y < rect.Min.y + rect.Size.y;
}

// The rects are in draw order, so the last one that contains the point is on top.
static std::optional<size_t> HitTest(const std::vector<Rect>& rects, glm::vec2 point)
{
	for (size_t index = rects.size(); index-- > 0;)
	{
		if (Contains(rects[index], point))
			return index;
	}
	return std::nullopt;
}

enum class Gesture { None, UI, Game };

class ToyUI
{
public:
	explicit ToyUI(std::vector<Rect> rects)
		: m_Rects(std::move(rects))
	{
	}

	void Update(glm::vec2 position, bool down)
	{
		const std::optional<size_t> hit = HitTest(m_Rects, position);
		const bool pressed = down && !m_WasDown;
		const bool released = !down && m_WasDown;
		if (pressed && m_Gesture == Gesture::None)
		{
			m_Gesture = hit ? Gesture::UI : Gesture::Game;
			m_Pressed = hit && m_Rects[*hit].Button ? hit : std::nullopt;
		}
		if (released && m_Pressed && m_Pressed == hit)
			std::printf("  click on %s\n", m_Rects[*hit].Name.c_str());
		if (released)
			m_Pressed.reset();
		// The game hides its mouse buttons during a UI gesture, and while the pointer is over the UI between gestures.
		const bool hidden = m_Gesture == Gesture::UI || (m_Gesture == Gesture::None && hit);
		std::printf("(%3.0f,%3.0f) down=%d hit=%-6s game sees the button: %s\n", position.x, position.y, down ? 1 : 0,
			hit ? m_Rects[*hit].Name.c_str() : "none", hidden ? "no" : "yes");
		if (!down)
			m_Gesture = Gesture::None;
		m_WasDown = down;
	}

private:
	std::vector<Rect> m_Rects;
	std::optional<size_t> m_Pressed;
	Gesture m_Gesture = Gesture::None;
	bool m_WasDown = false;
};

int main()
{
	ToyUI ui({ { "Panel", { 0.0f, 0.0f }, { 200.0f, 100.0f }, false }, { "Button", { 20.0f, 20.0f }, { 60.0f, 30.0f }, true } });
	std::printf("Press the button, drag onto the panel, release:\n");
	ui.Update({ 30.0f, 30.0f }, false);
	ui.Update({ 30.0f, 30.0f }, true);
	ui.Update({ 150.0f, 80.0f }, true);
	ui.Update({ 150.0f, 80.0f }, false);
	std::printf("Press and release on the button:\n");
	ui.Update({ 30.0f, 30.0f }, true);
	ui.Update({ 30.0f, 30.0f }, false);
	std::printf("Press in the game, drag over the button, release:\n");
	ui.Update({ 300.0f, 300.0f }, true);
	ui.Update({ 30.0f, 30.0f }, true);
	ui.Update({ 30.0f, 30.0f }, false);
	return 0;
}
