// A toy window service: requests wait until the frame's end, the latest of each kind wins, and a request the window
// already meets changes nothing and says nothing.
#include <cstdio>
#include <optional>

struct ToyWindow
{
	int Width = 1280;
	bool VSync = true;
};

class ToyWindowService
{
public:
	explicit ToyWindowService(ToyWindow& window)
		: m_Window(window)
	{
	}

	void SetWidth(int width) { m_PendingWidth = width; }
	void SetVSync(bool enabled) { m_PendingVSync = enabled; }

	void ApplyRequests(int frame)
	{
		bool changed = false;
		if (m_PendingWidth && *m_PendingWidth != m_Window.Width)
		{
			m_Window.Width = *m_PendingWidth;
			changed = true;
		}
		if (m_PendingVSync && *m_PendingVSync != m_Window.VSync)
		{
			m_Window.VSync = *m_PendingVSync;
			changed = true;
		}
		if (changed)
			std::printf("frame %d: window %d wide, vsync %s\n", frame, m_Window.Width, m_Window.VSync ? "on" : "off");
		m_PendingWidth.reset();
		m_PendingVSync.reset();
	}
private:
	ToyWindow& m_Window;
	std::optional<int> m_PendingWidth;
	std::optional<bool> m_PendingVSync;
};

int main()
{
	ToyWindow window;
	ToyWindowService service(window);
	for (int frame = 1; frame <= 4; frame++)
	{
		// A game that asks for its options in every update, and from frame 2 on wants 1600. In frame 2 it also asks for
		// 1920 first: the latest request wins.
		if (frame == 2)
			service.SetWidth(1920);
		service.SetWidth(frame >= 2 ? 1600 : 1280);
		service.SetVSync(true);
		service.ApplyRequests(frame);
	}
	return 0;
}
