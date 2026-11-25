// The depth that a standard and a reversed projection store for the same distances.
#include <cstdio>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>

float DepthAt(const glm::mat4& projection, float distance)
{
	const glm::vec4 clip = projection * glm::vec4(0.0f, 0.0f, -distance, 1.0f);
	return clip.z / clip.w;
}

int main()
{
	const float fov = glm::radians(60.0f);
	const glm::mat4 standard = glm::perspectiveRH_ZO(fov, 1.0f, 1.0f, 100.0f);
	const glm::mat4 reversed = glm::perspectiveRH_ZO(fov, 1.0f, 100.0f, 1.0f);

	const float distances[] = { 1.0f, 2.0f, 5.0f, 10.0f, 50.0f, 100.0f };
	for (const float distance : distances)
		std::printf("distance %5.1f: standard %.4f, reversed %.4f\n", distance, DepthAt(standard, distance),
			DepthAt(reversed, distance));
	return 0;
}
