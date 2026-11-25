// A ray from a pixel through an infinite reversed-Z projection, with glm alone: the depths 1 and 0.5 give two points.
#include <cstdio>
#include <glm/glm.hpp>

namespace
{
	// The matrix of an infinite reversed-Z projection: the depth is near / distance.
	glm::mat4 MakeProjection(float verticalFov, float aspect, float nearClip)
	{
		const float focal = 1.0f / glm::tan(verticalFov * 0.5f);
		glm::mat4 result(0.0f);
		result[0][0] = focal / aspect;
		result[1][1] = focal;
		result[2][3] = -1.0f;
		result[3][2] = nearClip;
		return result;
	}

	glm::vec3 Unproject(const glm::mat4& inverse, const glm::vec2& ndc, float depth)
	{
		const glm::vec4 point = inverse * glm::vec4(ndc, depth, 1.0f);
		return glm::vec3(point) / point.w;
	}
}

int main()
{
	const glm::mat4 projection = MakeProjection(glm::radians(90.0f), 1.0f, 1.0f);

	for (const float distance : { 1.0f, 2.0f, 100.0f, 1.0e6f })
	{
		const glm::vec4 clip = projection * glm::vec4(0.0f, 0.0f, -distance, 1.0f);
		std::printf("distance %9.0f -> depth %.6f\n", distance, clip.z / clip.w);
	}

	const glm::mat4 inverse = glm::inverse(projection);
	const glm::vec2 ndc(0.5f, 0.25f);
	const glm::vec3 origin = Unproject(inverse, ndc, 1.0f);
	const glm::vec3 target = Unproject(inverse, ndc, 0.5f);
	const glm::vec3 direction = glm::normalize(target - origin);
	std::printf("origin    (%.4f, %.4f, %.4f)\n", origin.x, origin.y, origin.z);
	std::printf("target    (%.4f, %.4f, %.4f)\n", target.x, target.y, target.z);
	std::printf("direction (%.4f, %.4f, %.4f)\n", direction.x, direction.y, direction.z);
	std::printf("w at depth 0: %.4f\n", (inverse * glm::vec4(ndc, 0.0f, 1.0f)).w);
}
