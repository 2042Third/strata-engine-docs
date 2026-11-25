// A toy virtual keyboard for one key: a queue of tool events applied at the frame boundary, merged with the device.
#include <cstdio>
#include <vector>

struct Button
{
	bool Down = false;
	bool Pressed = false;
	bool Released = false;

	void Set(bool down)
	{
		if (down && !Down)
			Pressed = true;
		else if (!down && Down)
			Released = true;
		Down = down;
	}

	void ClearTransitions()
	{
		Pressed = false;
		Released = false;
	}

	bool HeldThroughout() const { return Down && !Pressed && !Released; }
};

// A transition of one source counts only if the other source did not hold the key through the frame.
bool MergedPressed(const Button& device, const Button& tool)
{
	return (device.Pressed && !tool.HeldThroughout()) || (tool.Pressed && !device.HeldThroughout());
}

bool MergedReleased(const Button& device, const Button& tool)
{
	return (device.Released && !tool.HeldThroughout()) || (tool.Released && !device.HeldThroughout());
}

// What happens in one frame: the person's event arrives at once; the tool's is queued for the next frame.
struct Frame
{
	int Person; // 0 nothing, 1 press, 2 release
	int Tool;
};

void Run(const char* title, const std::vector<Frame>& frames)
{
	std::printf("%s\n", title);
	Button device;
	Button tool;
	std::vector<bool> queue;
	for (size_t i = 0; i < frames.size(); i++)
	{
		device.ClearTransitions(); // Input::BeginFrame
		tool.ClearTransitions();
		for (const bool down : queue)
			tool.Set(down);
		queue.clear();
		if (frames[i].Person != 0)
			device.Set(frames[i].Person == 1);
		std::printf("frame %zu: down %d pressed %d released %d\n", i + 1, static_cast<int>(device.Down || tool.Down),
			static_cast<int>(MergedPressed(device, tool)), static_cast<int>(MergedReleased(device, tool)));
		if (frames[i].Tool != 0)
			queue.push_back(frames[i].Tool == 1); // Applied at the next frame's start
	}
}

int main()
{
	Run("A tool taps a key nobody holds", { { 0, 1 }, { 0, 2 }, { 0, 0 }, { 0, 0 } });
	Run("A person holds the key, the tool taps it, the person lets go", { { 1, 0 }, { 0, 1 }, { 0, 2 }, { 2, 0 }, { 0, 0 } });
}
