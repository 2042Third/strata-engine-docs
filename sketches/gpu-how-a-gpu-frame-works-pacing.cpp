#include <cstddef>
#include <cstdio>
#include <queue>

int main()
{
	const std::size_t maxFramesInFlight = 2;
	std::queue<int> outstanding;

	for (int frame = 0; frame < 5; frame++)
	{
		// The GPU finishes frames in order, so waiting frees the oldest one.
		while (outstanding.size() >= maxFramesInFlight)
		{
			std::printf("frame %d: waits for frame %d\n", frame, outstanding.front());
			outstanding.pop();
		}
		std::printf("frame %d: the CPU records it\n", frame);
		outstanding.push(frame);
	}
	return 0;
}
