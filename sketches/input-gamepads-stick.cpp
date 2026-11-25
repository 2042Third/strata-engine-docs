// An axial and a radial dead zone side by side, with the default dead zone of 0.15.
#include <algorithm>
#include <cmath>
#include <cstdio>

#include <glm/glm.hpp>

namespace
{
	constexpr float c_DeadZone = 0.15f;

	float Rescale(float magnitude)
	{
		return (magnitude - c_DeadZone) / (1.0f - c_DeadZone);
	}

	glm::vec2 Axial(const glm::vec2& stick)
	{
		glm::vec2 result(0.0f);
		for (int index = 0; index < 2; index++)
		{
			const float magnitude = std::fabs(stick[index]);
			if (magnitude > c_DeadZone)
				result[index] = std::copysign(Rescale(magnitude), stick[index]);
		}
		return result;
	}

	glm::vec2 Radial(const glm::vec2& stick)
	{
		const float length = glm::length(stick);
		if (!(length > c_DeadZone))
			return glm::vec2(0.0f);
		return stick / length * std::min(Rescale(length), 1.0f);
	}
}

int main()
{
	const glm::vec2 sticks[] = { glm::vec2(0.1f, 0.1f), glm::vec2(0.2f, 0.0f), glm::vec2(0.6f, 0.6f) };
	for (const glm::vec2& stick : sticks)
	{
		const glm::vec2 axial = Axial(stick);
		const glm::vec2 radial = Radial(stick);
		std::printf("stick (%.2f, %.2f): axial (%.4f, %.4f), radial (%.4f, %.4f)\n", stick.x, stick.y, axial.x, axial.y, radial.x, radial.y);
	}
	return 0;
}
