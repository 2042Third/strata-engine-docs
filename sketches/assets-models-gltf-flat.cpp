// Flat normal of a triangle and the fallback tangent used when a model has no texture coordinates.
#include <cmath>
#include <cstdio>
#include <glm/glm.hpp>

struct Frame
{
	glm::vec3 Normal;
	glm::vec3 Tangent;
};

static Frame MakeFrame(const glm::vec3& a, const glm::vec3& b, const glm::vec3& c)
{
	const glm::vec3 faceNormal = glm::cross(b - a, c - a);
	const float length = glm::length(faceNormal);
	Frame frame;
	frame.Normal = length > 1e-12f ? faceNormal / length : glm::vec3(0.0f, 1.0f, 0.0f);
	// Any direction that is not nearly parallel to the normal gives a perpendicular tangent through a cross product.
	const glm::vec3 reference = std::abs(frame.Normal.y) < 0.99f ? glm::vec3(0.0f, 1.0f, 0.0f) : glm::vec3(1.0f, 0.0f, 0.0f);
	frame.Tangent = glm::normalize(glm::cross(reference, frame.Normal));
	return frame;
}

int main()
{
	const Frame wall = MakeFrame({ 0.0f, 0.0f, 0.0f }, { 1.0f, 0.0f, 0.0f }, { 0.0f, 1.0f, 0.0f });
	std::printf("wall:  normal (%g, %g, %g) tangent (%g, %g, %g)\n", wall.Normal.x, wall.Normal.y, wall.Normal.z, wall.Tangent.x, wall.Tangent.y, wall.Tangent.z);
	const Frame floor = MakeFrame({ 0.0f, 0.0f, 0.0f }, { 0.0f, 0.0f, 1.0f }, { 1.0f, 0.0f, 0.0f });
	std::printf("floor: normal (%g, %g, %g) tangent (%g, %g, %g)\n", floor.Normal.x, floor.Normal.y, floor.Normal.z, floor.Tangent.x, floor.Tangent.y, floor.Tangent.z);
	return 0;
}
