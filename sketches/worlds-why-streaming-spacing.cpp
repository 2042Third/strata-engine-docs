// The gap between a float and the next float above it, at several distances from the origin.
#include <cmath>
#include <iostream>

int main()
{
	const float distances[] = { 1000.0f, 16383.0f, 16384.0f, 20000.0f, 32767.0f, 32768.0f, 100000.0f };
	for (const float distance : distances)
	{
		const float next = std::nextafter(distance, 1.0e9f);
		std::cout << distance << " m: gap " << (next - distance) * 1000.0f << " mm\n";
	}
	return 0;
}
