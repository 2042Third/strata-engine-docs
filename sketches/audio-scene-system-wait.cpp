// How long a one-shot waits for its clip: each update adds the frame time, and a clip not ready after the limit is dropped.
#include <cstdio>

namespace
{

	constexpr float c_MaxClipWait = 0.25f;

}

int main()
{
	const float frameTime = 0.04f;
	const int loadFrames[3] = { 3, 6, 9 };
	for (const int load : loadFrames)
	{
		float waited = 0.0f;
		int frame = 0;
		bool started = false;
		while (!started && waited <= c_MaxClipWait)
		{
			frame++;
			waited += frameTime;
			started = frame >= load;
		}
		std::printf("clip ready after %d frames: %s at frame %d, waited %.2f s\n", load, started ? "plays" : "dropped", frame, waited);
	}
	return 0;
}
