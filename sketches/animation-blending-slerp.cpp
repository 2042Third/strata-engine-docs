// Three rotations about one axis, blended by a weighted sum and by slerp pair by pair.
#include <cmath>
#include <cstdio>
#include <glm/glm.hpp>
#include <glm/gtc/quaternion.hpp>

float AngleOf(const glm::quat& q)
{
	return glm::degrees(2.0f * std::atan2(q.z, q.w));
}

int main()
{
	const glm::vec3 axis(0.0f, 0.0f, 1.0f);
	const glm::quat rotations[3] = { glm::angleAxis(glm::radians(0.0f), axis), glm::angleAxis(glm::radians(60.0f), axis),
		glm::angleAxis(glm::radians(120.0f), axis) };
	const float weights[3] = { 0.5f, 0.25f, 0.25f };

	// The engine's way: sum the weighted quaternions, then normalize.
	glm::quat sum(0.0f, 0.0f, 0.0f, 0.0f);
	for (int index = 0; index < 3; index++)
	{
		sum.w += rotations[index].w * weights[index];
		sum.x += rotations[index].x * weights[index];
		sum.y += rotations[index].y * weights[index];
		sum.z += rotations[index].z * weights[index];
	}
	sum = glm::normalize(sum);

	// Pair by pair: fold in each rotation with the share it adds to the weight so far.
	glm::quat folded = rotations[0];
	float total = weights[0];
	for (int index = 1; index < 3; index++)
	{
		total += weights[index];
		folded = glm::slerp(folded, rotations[index], weights[index] / total);
	}

	std::printf("weighted sum:  %.2f degrees\n", AngleOf(sum));
	std::printf("slerp by pair: %.2f degrees\n", AngleOf(folded));
	return 0;
}
