// Bilinear interpolation between four corners, and trilinear between two squares.
#include <cstdio>
#include <glm/glm.hpp>

float Bilinear(float c00, float c10, float c01, float c11, float u, float v)
{
	const float bottom = glm::mix(c00, c10, u); // along x on the bottom edge
	const float top = glm::mix(c01, c11, u);    // along x on the top edge
	return glm::mix(bottom, top, v);            // then along y between them
}

int main()
{
	const float u = 0.25f;
	const float v = 0.5f;
	std::printf("weights: %g %g %g %g\n", (1 - u) * (1 - v), u * (1 - v), (1 - u) * v, u * v);
	const float front = Bilinear(0.0f, 4.0f, 2.0f, 6.0f, u, v);
	const float back = Bilinear(10.0f, 14.0f, 12.0f, 16.0f, u, v);
	std::printf("bilinear %g and %g, trilinear at w = 0.5: %g\n", front, back, glm::mix(front, back, 0.5f));
	return 0;
}
