// A toy UI harness: one button that decides hovering from the previous frame, and a click over three frames.
#include <cstdio>
#include <map>
#include <string>

struct Rect
{
	float MinX = 0.0f;
	float MinY = 0.0f;
	float MaxX = 0.0f;
	float MaxY = 0.0f;
};

class MiniUI
{
public:
	// Input waits here and applies at the start of the next frame, as in ImGui's queue.
	void SetMouse(float x, float y, bool down)
	{
		m_NextX = x;
		m_NextY = y;
		m_NextDown = down;
	}

	void Frame()
	{
		const bool wasDown = m_Down;
		m_X = m_NextX;
		m_Y = m_NextY;
		m_Down = m_NextDown;
		const Rect button{ 10.0f, 10.0f, 110.0f, 40.0f };
		const bool inside = m_X >= button.MinX && m_X <= button.MaxX && m_Y >= button.MinY && m_Y <= button.MaxY;
		if (m_Down && !wasDown && m_Hovered)
			m_Pressed = true; // A press counts only on a widget hovered in the frame before
		if (!m_Down && wasDown && m_Pressed && inside)
			m_Clicks++; // A button acts on the release
		if (!m_Down)
			m_Pressed = false;
		m_Hovered = inside;
		m_Probe["Save"] = button;
		m_Frames++;
	}

	const Rect* FindItem(const std::string& key) const
	{
		const auto found = m_Probe.find(key);
		return found == m_Probe.end() ? nullptr : &found->second;
	}

	int GetClicks() const { return m_Clicks; }
	int GetFrames() const { return m_Frames; }

private:
	std::map<std::string, Rect> m_Probe;
	float m_NextX = 0.0f, m_NextY = 0.0f, m_X = 0.0f, m_Y = 0.0f;
	bool m_NextDown = false, m_Down = false, m_Hovered = false, m_Pressed = false;
	int m_Clicks = 0;
	int m_Frames = 0;
};

bool ClickItem(MiniUI& ui, const std::string& key)
{
	const Rect* item = ui.FindItem(key);
	if (!item)
		return false;
	const float x = (item->MinX + item->MaxX) * 0.5f;
	const float y = (item->MinY + item->MaxY) * 0.5f;
	ui.SetMouse(x, y, false);
	ui.Frame(); // Hover
	ui.SetMouse(x, y, true);
	ui.Frame(); // Press
	ui.SetMouse(x, y, false);
	ui.Frame(); // Release
	return true;
}

int main()
{
	MiniUI ui;
	ui.Frame();
	std::printf("missing key: %d\n", ClickItem(ui, "Open") ? 1 : 0);
	const bool found = ClickItem(ui, "Save");
	std::printf("Save found: %d, clicks: %d, frames: %d\n", found ? 1 : 0, ui.GetClicks(), ui.GetFrames());

	MiniUI hasty;
	hasty.Frame();
	hasty.SetMouse(60.0f, 25.0f, true); // Move and press together
	hasty.Frame();
	hasty.SetMouse(60.0f, 25.0f, false);
	hasty.Frame();
	std::printf("without a hover frame, clicks: %d\n", hasty.GetClicks());
	return 0;
}
