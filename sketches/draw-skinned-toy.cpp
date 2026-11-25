// Blends the palette entries of a vertex's four influences into one matrix, as BlendJoints does in the vertex shader.
#include <array>
#include <cstdio>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>

glm::mat4 BlendJoints(const std::array<glm::mat4, 3>& palette, const glm::uvec4& joints, const glm::vec4& weights)
{
	glm::mat4 blended(0.0f);
	for (int influence = 0; influence < 4; influence++)
		blended += palette[joints[influence]] * weights[influence];
	return blended;
}

void Skin(const std::array<glm::mat4, 3>& palette, const glm::uvec4& joints, const glm::vec4& weights)
{
	const glm::vec4 bindPosition(1.0f, 1.0f, 0.0f, 1.0f);
	const glm::vec4 posed = BlendJoints(palette, joints, weights) * bindPosition;
	std::printf("joints (%u, %u), weights (%.2f, %.2f): vertex (1, 1, 0) goes to (%.2f, %.2f, %.2f)\n", joints[0], joints[1], weights[0], weights[1],
		posed.x, posed.y, posed.z);
}

int main()
{
	// Entry 0 leaves the vertex alone, entry 1 moves it 2 along x, entry 2 moves it 4 along y.
	const std::array<glm::mat4, 3> palette = { glm::mat4(1.0f), glm::translate(glm::mat4(1.0f), glm::vec3(2.0f, 0.0f, 0.0f)),
		glm::translate(glm::mat4(1.0f), glm::vec3(0.0f, 4.0f, 0.0f)) };
	// Unused influences name joint 0 with weight 0: they must still name a real joint, because the shader reads all four.
	Skin(palette, glm::uvec4(0, 1, 0, 0), glm::vec4(0.5f, 0.5f, 0.0f, 0.0f));
	Skin(palette, glm::uvec4(0, 2, 0, 0), glm::vec4(0.75f, 0.25f, 0.0f, 0.0f));
	Skin(palette, glm::uvec4(1, 2, 0, 0), glm::vec4(1.0f, 0.0f, 0.0f, 0.0f));
}
