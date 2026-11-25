#include <cstdio>

// One key as the polled state keeps it: held now, and what changed since the frame began.
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

	void BeginFrame()
	{
		Pressed = false;
		Released = false;
	}
};

int main()
{
	// Per frame: 0 nothing happened, 1 a press arrived, 2 a release arrived, 3 a press and a release arrived.
	const int events[6] = { 0, 1, 0, 2, 3, 0 };
	// Per frame: how many fixed steps ran after the frame's update.
	const int steps[6] = { 0, 2, 1, 1, 0, 1 };

	Button space;
	bool lastDown = false;
	int updateJumps = 0;
	int comparedJumps = 0;
	int fixedJumps = 0;
	for (int frame = 1; frame <= 6; frame++)
	{
		space.BeginFrame();
		const int event = events[frame - 1];
		if (event == 1 || event == 3)
			space.Set(true);
		if (event == 2 || event == 3)
			space.Set(false);

		const bool compared = space.Down && !lastDown;
		lastDown = space.Down;
		updateJumps += space.Pressed ? 1 : 0;
		comparedJumps += compared ? 1 : 0;
		fixedJumps += space.Pressed ? steps[frame - 1] : 0;
		std::printf("Frame %d: down=%d pressed=%d released=%d compared=%d steps=%d\n", frame, space.Down, space.Pressed,
			space.Released, compared, steps[frame - 1]);
	}
	std::printf("Jumps: update %d, compared with the last frame %d, fixed update %d\n", updateJumps, comparedJumps, fixedJumps);
	return 0;
}
