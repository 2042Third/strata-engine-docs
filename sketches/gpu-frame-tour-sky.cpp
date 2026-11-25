#include <cstdio>
#include <vector>

// One row of eight pixels after the prepass. Reversed-Z: the far plane is depth 0 and the buffer is cleared to it.
int main()
{
	constexpr int c_Width = 8;
	std::vector<float> depth(c_Width, 0.0f);
	for (int x = 2; x < 6; x++)
		depth[x] = 0.5f; // An opaque surface covers columns 2 to 5

	// The sky is a triangle drawn at depth 0, the far plane, after the opaque pass.
	const float skyDepth = 0.0f;
	int shadedGreaterOrEqual = 0;
	int shadedGreater = 0;
	for (int x = 0; x < c_Width; x++)
	{
		if (skyDepth >= depth[x])
			shadedGreaterOrEqual++;
		if (skyDepth > depth[x])
			shadedGreater++;
	}
	std::printf("sky with GreaterOrEqual: %d of %d pixels\n", shadedGreaterOrEqual, c_Width);
	std::printf("sky with Greater:        %d of %d pixels\n", shadedGreater, c_Width);
	return 0;
}
