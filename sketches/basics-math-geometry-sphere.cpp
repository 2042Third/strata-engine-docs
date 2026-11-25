#include <cstdio>
#include <glm/glm.hpp>
#include <optional>

std::optional<float> HitSphere(const glm::vec3& origin, const glm::vec3& direction, const glm::vec3& center, float radius)
{
	const glm::vec3 toOrigin = origin - center; // the direction has length 1, so the quadratic has a = 1
	const float b = glm::dot(toOrigin, direction);
	const float c = glm::dot(toOrigin, toOrigin) - radius * radius;
	const float discriminant = b * b - c;
	if (discriminant < 0.0f)
		return std::nullopt; // the line misses the sphere
	const float root = glm::sqrt(discriminant);
	if (-b + root < 0.0f)
		return std::nullopt; // the sphere lies behind the origin
	return -b - root >= 0.0f ? -b - root : -b + root; // inside the sphere: the way out
}

int main()
{
	const glm::vec3 center(0.0f, 0.0f, 5.0f), zero(0.0f), along(0.0f, 0.0f, 1.0f), up(0.0f, 1.0f, 0.0f);
	std::printf("hit %g, miss %g, ", HitSphere(zero, along, center, 1.0f).value_or(-1.0f), HitSphere(zero, up, center, 1.0f).value_or(-1.0f));
	std::printf("inside %g, ", HitSphere(center, along, center, 1.0f).value_or(-1.0f));
	std::printf("behind %g\n", HitSphere(zero, -along, center, 1.0f).value_or(-1.0f));
}
