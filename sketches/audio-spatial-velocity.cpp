#include <cmath>
#include <cstdio>

int main()
{
	const float stepTime = 1.0f / 60.0f;
	const float frameTime = 1.0f / 144.0f;
	const float smoothingTime = 0.1f;

	float stepClock = 0.0f;
	float position = 0.0f;      // Moves 0.5 units on every fixed step: 30 units per second.
	float lastFramePosition = 0.0f;
	float lastMovePosition = 0.0f;
	float sinceMove = 0.0f;
	float smoothed = 0.0f;

	for (int frame = 1; frame <= 12; frame++)
	{
		stepClock += frameTime;
		while (stepClock >= stepTime)
		{
			stepClock -= stepTime;
			position += 0.5f;
		}

		const float naive = (position - lastFramePosition) / frameTime;
		lastFramePosition = position;

		sinceMove += frameTime;
		if (position != lastMovePosition)
		{
			const float measured = (position - lastMovePosition) / sinceMove;
			smoothed += (measured - smoothed) * (1.0f - std::exp(-sinceMove / smoothingTime));
			lastMovePosition = position;
			sinceMove = 0.0f;
		}
		std::printf("frame %2d  position %.1f  naive %5.1f  smoothed %5.1f\n", frame, position, naive, smoothed);
	}
	return 0;
}
