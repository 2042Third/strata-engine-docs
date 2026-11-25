#include <algorithm>
#include <cstdio>

// The horizon, as the cosine of its angle to the view, after six samples along one side of a slice.
float Walk(const float (&samples)[6], float decay)
{
	const float edge = 0.0f; // The horizon of the hemisphere itself: nothing occludes
	float horizon = edge;
	for (float sample : samples)
	{
		if (sample > horizon)
			horizon = sample;
		else
			horizon = std::max(horizon + (sample - horizon) * decay, edge);
	}
	return horizon;
}

int main()
{
	const float pole[6] = { 0.2f, 0.8f, 0.2f, 0.2f, 0.2f, 0.2f };
	const float board[6] = { 0.2f, 0.8f, 0.8f, 0.8f, 0.2f, 0.2f };
	const float decays[2] = { 0.0f, 0.1f };
	for (float decay : decays)
		std::printf("decay %.1f: pole %.3f, board %.3f\n", static_cast<double>(decay), static_cast<double>(Walk(pole, decay)),
			static_cast<double>(Walk(board, decay)));
	return 0;
}
