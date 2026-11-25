#include <cstdio>
#include <string>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
// Rounds to three decimals; adding 0.0f turns a negative zero into a plain zero.
static glm::vec4 Tidy(const glm::vec4& v)
{
	return glm::round(v * 1000.0f) / 1000.0f + 0.0f;
}

static void Print(const std::string& label, const glm::mat4& m, const glm::vec4& point)
{
	const glm::vec4 c = Tidy(m[3]);
	const glm::vec4 end = Tidy(m * point);
	std::printf("%s: last column (%g, %g, %g), the point lands at (%g, %g, %g)\n", label.c_str(), c.x, c.y, c.z, end.x, end.y, end.z);
}

int main()
{
	const glm::mat4 turn = glm::rotate(glm::mat4(1.0f), glm::radians(90.0f), glm::vec3(0.0f, 0.0f, 1.0f));
	const glm::mat4 move = glm::translate(glm::mat4(1.0f), glm::vec3(3.0f, 0.0f, 0.0f));
	const glm::vec4 point(1.0f, 0.0f, 0.0f, 1.0f);
	Print("turn, then move", move * turn, point);
	Print("move, then turn", turn * move, point);
}
