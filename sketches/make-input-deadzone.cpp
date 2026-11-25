#include <cstdio>
#include <glm/glm.hpp>

// A square zone: each axis alone, stretched so that 1 stays 1.
static float Axis(float value, float zone)
{
	const float size = glm::abs(value);
	return size <= zone ? 0.0f : glm::sign(value) * (size - zone) / (1.0f - zone);
}

// A round zone: the length of the whole tilt, so the direction stays.
static glm::vec2 Stick(glm::vec2 value, float zone)
{
	const float length = glm::length(value);
	return length <= zone ? glm::vec2(0.0f) : value / length * (length - zone) / (1.0f - zone);
}
int main()
{
	const glm::vec2 samples[] = { { 0.10f, 0.10f }, { 0.14f, 0.90f }, { 0.60f, 0.00f }, { 0.60f, 0.80f } };
	for (const glm::vec2& s : samples)
	{
		const glm::vec2 r = Stick(s, 0.15f);
		std::printf("stick (%.2f, %.2f): square (%.2f, %.2f), round (%.2f, %.2f)\n", s.x, s.y, Axis(s.x, 0.15f), Axis(s.y, 0.15f), r.x, r.y);
	}
}
