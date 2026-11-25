// A toy of placement: one ramp, one ray, and a box that rests on what the ray hits.
#include <glm/glm.hpp>

#include <cstdio>
#include <optional>

struct Ray
{
	glm::vec3 Origin;
	glm::vec3 Direction;
};

struct Box
{
	glm::vec3 Min;
	glm::vec3 Max;
};

// The ramp is an endless plane through the origin that rises 30 degrees along +X.
constexpr glm::vec3 c_RampNormal(-0.5f, 0.8660254f, 0.0f);
constexpr float c_FallbackDistance = 10.0f;

// The distance along the ray to the ramp, or nothing when the ray looks away from its face.
std::optional<float> HitRamp(const Ray& ray)
{
	const float facing = glm::dot(c_RampNormal, ray.Direction);
	if (facing >= 0.0f)
		return std::nullopt;
	return -glm::dot(c_RampNormal, ray.Origin) / facing;
}

// The translation that puts the box's side facing the surface on the point.
glm::vec3 RestOn(const glm::vec3& point, const glm::vec3& normal, const Box& box)
{
	const glm::vec3 center = (box.Min + box.Max) * 0.5f;
	const glm::vec3 extents = (box.Max - box.Min) * 0.5f;
	const float behind = glm::dot(glm::abs(normal), extents) - glm::dot(normal, center);
	return point + normal * behind;
}

void Place(const char* label, const Ray& ray, const Box& box)
{
	glm::vec3 translation;
	const char* source;
	if (const std::optional<float> distance = HitRamp(ray))
	{
		source = "surface";
		translation = RestOn(ray.Origin + ray.Direction * *distance, c_RampNormal, box);
	}
	else
	{
		source = "inFront";
		translation = ray.Origin + ray.Direction * c_FallbackDistance - (box.Min + box.Max) * 0.5f;
	}
	std::printf("%s: %s, translation (%.3f, %.3f, %.3f)\n", label, source, translation.x, translation.y, translation.z);
}

int main()
{
	const Box crate { glm::vec3(-0.5f), glm::vec3(0.5f) };
	Place("ray down at x = 2", Ray { glm::vec3(2.0f, 5.0f, 0.0f), glm::vec3(0.0f, -1.0f, 0.0f) }, crate);
	Place("ray into the sky", Ray { glm::vec3(0.0f, 5.0f, 10.0f), glm::vec3(0.0f, 0.6f, -0.8f) }, crate);
	return 0;
}
