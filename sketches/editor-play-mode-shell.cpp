#include <cstdint>
#include <cstdio>
#include <optional>

// A toy game shell for the window: it records what the game asks for and reports a request once.
class ToyGameWindow
{
public:
	bool SetResolution(uint32_t width, uint32_t height)
	{
		if (m_Width == width && m_Height == height)
			return false; // The same request as the last one: nothing changes, nothing is logged
		m_Width = width;
		m_Height = height;
		std::printf("recorded: resolution %u x %u (the editor's window keeps its size)\n", width, height);
		return true;
	}

	bool SetVSync(bool enabled)
	{
		if (m_VSync == enabled)
			return false;
		m_VSync = enabled;
		std::printf("recorded: vsync %s\n", enabled ? "on" : "off");
		return true;
	}

	// Called when play starts and when it stops: requests belong to one session.
	void Clear()
	{
		m_Width.reset();
		m_Height.reset();
		m_VSync.reset();
	}
private:
	std::optional<uint32_t> m_Width;
	std::optional<uint32_t> m_Height;
	std::optional<bool> m_VSync;
};

int main()
{
	ToyGameWindow window;
	std::printf("session 1\n");
	for (int frame = 0; frame < 3; frame++)
	{
		window.SetResolution(1920, 1080); // A game that applies its options every frame
		window.SetVSync(false);
	}
	window.Clear(); // Stop
	std::printf("session 2\n");
	window.SetResolution(1920, 1080);
	return 0;
}
