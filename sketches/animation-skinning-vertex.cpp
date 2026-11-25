// Skins one vertex between two joints, the way a palette and four weighted influences do.
#include <cstdint>
#include <cstdio>

#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>

struct Influence
{
	uint16_t Joint = 0;
	uint16_t Weight = 0; // In 1/65535ths; the weights of a vertex add up to 65535
};

// Blends the palette entries of the influences by weight, then moves the bind-pose vertex with the result.
glm::vec3 SkinVertex(const glm::vec3& position, const Influence (&influences)[2], const glm::mat4* palette)
{
	glm::mat4 blended(0.0f);
	for (const Influence& influence : influences)
		blended += palette[influence.Joint] * (static_cast<float>(influence.Weight) / 65535.0f);
	return glm::vec3(blended * glm::vec4(position, 1.0f));
}

int main()
{
	// Joint 0 is the shoulder at the origin; joint 1 is the elbow, one unit up.
	const glm::mat4 inverseBind[2] = { glm::mat4(1.0f), glm::translate(glm::mat4(1.0f), glm::vec3(0.0f, -1.0f, 0.0f)) };
	// The pose: the shoulder stays, the forearm turns a quarter turn about z at the elbow.
	const glm::mat4 elbowBent = glm::translate(glm::mat4(1.0f), glm::vec3(0.0f, 1.0f, 0.0f)) * glm::rotate(glm::mat4(1.0f), glm::radians(90.0f), glm::vec3(0.0f, 0.0f, 1.0f));
	const glm::mat4 pose[2] = { glm::mat4(1.0f), elbowBent };

	glm::mat4 palette[2];
	for (int joint = 0; joint < 2; joint++)
		palette[joint] = pose[joint] * inverseBind[joint];

	const glm::vec3 vertex(0.2f, 1.1f, 0.0f);
	const Influence influences[2] = { { 0, 16384 }, { 1, 49151 } };
	const glm::vec3 skinned = SkinVertex(vertex, influences, palette);
	const glm::vec3 withShoulder = glm::vec3(palette[0] * glm::vec4(vertex, 1.0f));
	const glm::vec3 withElbow = glm::vec3(palette[1] * glm::vec4(vertex, 1.0f));
	std::printf("shoulder alone: %.3f %.3f %.3f\n", withShoulder.x, withShoulder.y, withShoulder.z);
	std::printf("elbow alone:    %.3f %.3f %.3f\n", withElbow.x, withElbow.y, withElbow.z);
	std::printf("blended:        %.3f %.3f %.3f\n", skinned.x, skinned.y, skinned.z);
	return 0;
}
