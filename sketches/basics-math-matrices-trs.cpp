#include <cstdio>
#include <string>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
// Prints a vector rounded to three decimals; adding 0.0f turns a negative zero into a plain zero.
static void Print(const std::string& label, const glm::vec4& v)
{
	const glm::vec4 r = glm::round(v * 1000.0f) / 1000.0f + 0.0f;
	std::printf("%s = (%g, %g, %g, %g)\n", label.c_str(), r.x, r.y, r.z, r.w);
}

int main()
{
	const glm::mat4 identity(1.0f);
	const glm::vec3 position(4.0f, 0.0f, 0.0f);
	const glm::vec3 size(2.0f, 1.0f, 1.0f);
	const float angle = glm::radians(90.0f);
	const glm::vec3 axis(0.0f, 0.0f, 1.0f);
	// Each builder multiplies the matrix it is given on the right, so the chain reads inside out.
	const glm::mat4 chained = glm::scale(glm::rotate(glm::translate(identity, position), angle, axis), size);
	const glm::mat4 product = glm::translate(identity, position) * glm::rotate(identity, angle, axis) * glm::scale(identity, size);
	Print("chained * position", chained * glm::vec4(1.0f, 0.0f, 0.0f, 1.0f));
	Print("product * position", product * glm::vec4(1.0f, 0.0f, 0.0f, 1.0f));
	Print("product * direction", product * glm::vec4(1.0f, 0.0f, 0.0f, 0.0f));
}
