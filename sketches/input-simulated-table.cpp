// The merge rule of one button, tried on every pair of states a source can be in during a frame.
#include <cstdio>

struct Button
{
	bool Down = false;
	bool Pressed = false;
	bool Released = false;

	bool HeldThroughout() const { return Down && !Pressed && !Released; }
};

enum class State
{
	Up,
	Pressed,
	Released,
	Held
};

const char* c_Names[] = { "up", "pressed", "released", "held" };

Button MakeButton(State state)
{
	Button button;
	button.Down = state == State::Pressed || state == State::Held;
	button.Pressed = state == State::Pressed;
	button.Released = state == State::Released;
	return button;
}

int main()
{
	for (int d = 0; d < 4; d++)
	{
		for (int s = 0; s < 4; s++)
		{
			const Button device = MakeButton(static_cast<State>(d));
			const Button tool = MakeButton(static_cast<State>(s));
			const bool pressed = (device.Pressed && !tool.HeldThroughout()) || (tool.Pressed && !device.HeldThroughout());
			const bool released = (device.Released && !tool.HeldThroughout()) || (tool.Released && !device.HeldThroughout());
			std::printf("device %-8s tool %-8s down %d pressed %d released %d\n", c_Names[d], c_Names[s],
				static_cast<int>(device.Down || tool.Down), static_cast<int>(pressed), static_cast<int>(released));
		}
	}
}
