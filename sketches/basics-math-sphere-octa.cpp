// The octahedral encoding of a unit vector into two numbers, and the way back: the shader's functions in C++.
#include <cstdio>
#include <glm/glm.hpp>

glm::vec2 Encode(glm::vec3 n)
{
	n /= glm::abs(n.x) + glm::abs(n.y) + glm::abs(n.z); // onto the octahedron |x| + |y| + |z| = 1
	return n.z >= 0.0f ? glm::vec2(n) : (1.0f - glm::abs(glm::vec2(n.y, n.x))) * glm::vec2(n.x >= 0.0f ? 1.0f : -1.0f, n.y >= 0.0f ? 1.0f : -1.0f);
}

glm::vec3 Decode(glm::vec2 e)
{
	glm::vec3 n(e.x, e.y, 1.0f - glm::abs(e.x) - glm::abs(e.y));
	const float t = glm::max(-n.z, 0.0f); // how far a point of the lower half was folded out
	n.x += n.x >= 0.0f ? -t : t;
	n.y += n.y >= 0.0f ? -t : t;
	return glm::normalize(n);
}

int main()
{
	const glm::vec2 e = Encode({ -0.2f, 0.4f, -0.8944f });
	const glm::vec3 n = Decode(e);
	std::printf("(%.4f, %.4f) -> (%.4f, %.4f, %.4f)\n", e.x, e.y, n.x, n.y, n.z);
}
