// A toy keyboard: three bitsets and a frame boundary, the whole of polled input state.
// Each frame starts by clearing the transitions, then the window's events arrive, then the game reads.
#include <bitset>
#include <cstddef>
#include <cstdio>
#include <vector>

constexpr size_t c_MaxKeyCode = 512;
constexpr size_t c_KeySpace = 32; // GLFW's value for Space, and the engine's

struct ButtonStates
{
	std::bitset<c_MaxKeyCode> Down;
	std::bitset<c_MaxKeyCode> Pressed;
	std::bitset<c_MaxKeyCode> Released;

	// The one place that records an edge: only a change of state is a transition.
	void Set(size_t key, bool down)
	{
		if (down && !Down.test(key))
			Pressed.set(key);
		else if (!down && Down.test(key))
			Released.set(key);
		Down.set(key, down);
	}

	void ClearTransitions()
	{
		Pressed.reset();
		Released.reset();
	}
};

struct KeyEvent
{
	size_t Key;
	bool Down;
};

int main()
{
	// What the operating system reports between two frames. Frames 1 and 2 hold Space; frame 4 is a tap inside one frame.
	const std::vector<std::vector<KeyEvent>> frames = {
		{ { c_KeySpace, true } },
		{},
		{ { c_KeySpace, false } },
		{ { c_KeySpace, true }, { c_KeySpace, false } },
		{},
	};

	ButtonStates keys;
	for (size_t frame = 0; frame < frames.size(); frame++)
	{
		keys.ClearTransitions(); // Input::BeginFrame
		for (const KeyEvent& event : frames[frame])
			keys.Set(event.Key, event.Down); // The window's callbacks
		std::printf("frame %zu: down %d pressed %d released %d\n", frame + 1, static_cast<int>(keys.Down.test(c_KeySpace)),
			static_cast<int>(keys.Pressed.test(c_KeySpace)), static_cast<int>(keys.Released.test(c_KeySpace)));
	}
}
