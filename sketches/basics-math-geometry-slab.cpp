#include <algorithm>
#include <cstdio>
#include <glm/glm.hpp>
#include <optional>

std::optional<float> HitBox(const glm::vec2& origin, const glm::vec2& direction, const glm::vec2& low, const glm::vec2& high)
{
	float entry = 0.0f, leave = 1e30f;
	for (int axis = 0; axis < 2; axis++)
	{
		const glm::vec2 t = (glm::vec2(low[axis], high[axis]) - origin[axis]) / direction[axis]; // a zero direction gives infinity
		entry = std::max(entry, std::min(t.x, t.y)); // the latest entry into a slab
		leave = std::min(leave, std::max(t.x, t.y)); // the earliest exit from a slab
	}
	return entry <= leave ? std::optional<float>(entry) : std::nullopt;
}

int main()
{
	const glm::vec2 slant(0.8f, 0.6f), low(2.0f, 1.0f), high(4.0f, 3.0f), zero(0.0f), along(1.0f, 0.0f);
	std::printf("hit %g, ", HitBox(zero, slant, low, high).value_or(-1.0f));
	std::printf("miss %g\n", HitBox(zero, slant, low + glm::vec2(0.0f, 3.0f), high + glm::vec2(0.0f, 3.0f)).value_or(-1.0f));
	std::printf("parallel inside %g, ", HitBox(glm::vec2(0.0f, 2.0f), along, low, high).value_or(-1.0f));
	std::printf("parallel outside %g\n", HitBox(glm::vec2(0.0f, 5.0f), along, low, high).value_or(-1.0f));
}
