#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <vector>

constexpr uint16_t c_NoJoint = 0xFFFF;

struct ToyJoint
{
	const char* Name;
	uint16_t Parent;
	glm::vec3 Translation;
	float AngleDegrees; // About the Z axis
};

// Translation, then rotation: the joint turns about its own origin.
glm::mat4 ToMatrix(const ToyJoint& joint)
{
	const glm::mat4 moved = glm::translate(glm::mat4(1.0f), joint.Translation);
	return glm::rotate(moved, glm::radians(joint.AngleDegrees), glm::vec3(0.0f, 0.0f, 1.0f));
}

// One pass: every parent comes before its children, so its matrix is ready.
std::vector<glm::mat4> ComputeModelTransforms(const std::vector<ToyJoint>& joints)
{
	std::vector<glm::mat4> model(joints.size());
	for (size_t joint = 0; joint < joints.size(); joint++)
	{
		const glm::mat4 local = ToMatrix(joints[joint]);
		const uint16_t parent = joints[joint].Parent;
		model[joint] = parent == c_NoJoint ? local : model[parent] * local;
	}
	return model;
}

float Clean(float value)
{
	return std::round(value * 10.0f) / 10.0f + 0.0f; // + 0.0f turns -0.0 into 0.0
}

void Print(const char* title, const std::vector<ToyJoint>& joints)
{
	std::printf("%s\n", title);
	const std::vector<glm::mat4> model = ComputeModelTransforms(joints);
	for (size_t joint = 0; joint < joints.size(); joint++)
		std::printf("  %-8s (%.1f, %.1f, %.1f)\n", joints[joint].Name, Clean(model[joint][3].x), Clean(model[joint][3].y), Clean(model[joint][3].z));
}

int main()
{
	std::vector<ToyJoint> arm = {
		{ "Shoulder", c_NoJoint, glm::vec3(0.0f), 0.0f },
		{ "Elbow", 0, glm::vec3(0.0f, 1.0f, 0.0f), 0.0f },
		{ "Wrist", 1, glm::vec3(0.0f, 1.0f, 0.0f), 0.0f },
	};
	Print("Rest pose", arm);
	arm[1].AngleDegrees = 90.0f;
	Print("Elbow turned 90 degrees", arm);
	arm[0].AngleDegrees = 90.0f;
	Print("Shoulder and elbow turned 90 degrees", arm);

	// The wrong order, rotation before translation, swings the elbow about the world origin.
	const glm::mat4 wrong = glm::translate(glm::rotate(glm::mat4(1.0f), glm::radians(90.0f), glm::vec3(0.0f, 0.0f, 1.0f)), glm::vec3(0.0f, 1.0f, 0.0f));
	std::printf("Elbow with the wrong order (%.1f, %.1f, %.1f)\n", Clean(wrong[3].x), Clean(wrong[3].y), Clean(wrong[3].z));
	return 0;
}
