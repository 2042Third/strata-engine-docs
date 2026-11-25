// The toy keyboard with suspended input frames: transitions are cleared only once the game has seen them.
// Ticks 3 and 4 are a paused game. D is pressed in tick 3; the game sees the press in tick 5.
#include <bitset>
#include <cstddef>
#include <cstdio>

constexpr size_t c_KeyCount = 128;
constexpr size_t c_KeyA = 65;
constexpr size_t c_KeyD = 68;

struct Keyboard
{
	std::bitset<c_KeyCount> Down;
	std::bitset<c_KeyCount> Pressed;
	bool Suspended = false;
	bool FrameSeen = true;
	int FrameIndex = 0;

	void Set(size_t key, bool down)
	{
		if (down && !Down.test(key))
			Pressed.set(key);
		Down.set(key, down);
	}

	// The engine's BeginFrame, reduced to its two decisions.
	void BeginFrame()
	{
		if (FrameSeen)
		{
			Pressed.reset();
			FrameSeen = false;
		}
		if (Suspended)
			return;
		FrameIndex++;
		FrameSeen = true;
	}
};

int main()
{
	Keyboard keyboard;
	for (int tick = 1; tick <= 6; tick++)
	{
		keyboard.Suspended = tick == 3 || tick == 4;
		keyboard.BeginFrame();
		if (tick == 1)
			keyboard.Set(c_KeyA, true);
		if (tick == 3)
			keyboard.Set(c_KeyD, true);
		std::printf("tick %d: game updates %d, input frame %d, A pressed %d, D pressed %d\n", tick, static_cast<int>(!keyboard.Suspended),
			keyboard.FrameIndex, static_cast<int>(keyboard.Pressed.test(c_KeyA)), static_cast<int>(keyboard.Pressed.test(c_KeyD)));
	}
}
