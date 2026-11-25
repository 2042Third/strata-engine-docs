// A standalone copy of the fade state machine, driven by a target level that changes at frame 5 and back at frame 9.
#include <cstdint>
#include <cstdio>

constexpr uint32_t c_Frames = 16;

struct Fade
{
	uint32_t Lod = 0;
	uint32_t From = 0;
	uint32_t Step = c_Frames;
	bool Started = false;
};

// Returns the draw entry's code: 0 draws every pixel, 1 to 15 is the step of a fade under way.
uint32_t Update(Fade& fade, uint32_t target)
{
	if (!fade.Started)
	{
		fade = { target, target, c_Frames, true };
		return 0;
	}
	if (target != fade.Lod)
	{
		if (fade.Step < c_Frames && target == fade.From)
		{
			fade.From = fade.Lod;
			fade.Step = c_Frames - fade.Step;
		}
		else
		{
			fade.From = fade.Step < c_Frames && 2 * fade.Step < c_Frames ? fade.From : fade.Lod;
			fade.Step = 1;
		}
		fade.Lod = target;
	}
	else if (fade.Step < c_Frames)
	{
		fade.Step++;
	}
	if (fade.From == fade.Lod)
		fade.Step = c_Frames;
	return fade.Step < c_Frames ? fade.Step : 0;
}

int main()
{
	Fade fade;
	for (uint32_t frame = 0; frame < 15; frame++)
	{
		const uint32_t target = frame >= 5 && frame < 9 ? 1 : 0;
		const uint32_t code = Update(fade, target);
		std::printf("frame %2u: target %u, code %2u, fading out level %u\n", frame, target, code, fade.From);
	}
	return 0;
}
