// Degrees to radians, the point on the unit circle at an angle, and the angle of a direction back.
#include <cmath>
#include <cstdio>
#include <glm/glm.hpp>

int main()
{
	const float angle = glm::radians(60.0f);
	std::printf("60 degrees is %.4f radians\n", angle);
	std::printf("cos %.4f, sin %.4f\n", std::cos(angle), std::sin(angle));

	const float x[4] = { 1.0f, -1.0f, -1.0f, 1.0f };
	const float y[4] = { 1.0f, 1.0f, -1.0f, -1.0f };
	for (int i = 0; i < 4; i++)
	{
		const float withAtan2 = glm::degrees(std::atan2(y[i], x[i]));
		const float withAtan = glm::degrees(std::atan(y[i] / x[i]));
		std::printf("(%g, %g): atan2 %g, atan %g\n", x[i], y[i], withAtan2, withAtan);
	}
	return 0;
}
