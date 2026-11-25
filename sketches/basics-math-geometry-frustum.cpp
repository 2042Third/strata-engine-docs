#include <cstdio>
#include <glm/glm.hpp>

// A toy frustum of two planes, x >= 1 and y >= 1: inward-facing, so a point inside has a distance of 0 or more.
bool SphereVisible(const glm::vec3& center, float radius, const glm::vec4 planes[2])
{
	for (int i = 0; i < 2; i++)
	{
		if (glm::dot(glm::vec3(planes[i]), center) + planes[i].w < -radius)
			return false; // wholly on the outer side of this plane
	}
	return true; // not proven outside: kept
}

int main()
{
	const glm::vec4 planes[2] = { glm::vec4(1.0f, 0.0f, 0.0f, -1.0f), glm::vec4(0.0f, 1.0f, 0.0f, -1.0f) };
	std::printf("inside %d\n", SphereVisible(glm::vec3(3.0f, 3.0f, 0.0f), 0.5f, planes));
	std::printf("across %d\n", SphereVisible(glm::vec3(0.8f, 3.0f, 0.0f), 0.5f, planes));
	std::printf("outside %d\n", SphereVisible(glm::vec3(0.0f, 3.0f, 0.0f), 0.5f, planes));
	std::printf("near the corner %d\n", SphereVisible(glm::vec3(0.6f, 0.6f, 0.0f), 0.5f, planes));
}
