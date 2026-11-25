#include <cstdio>
#include <string>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
// Prints the last column rounded to three decimals; adding 0.0f turns a negative zero into a plain zero.
static void Print(const std::string& label, const glm::mat4& m)
{
	const glm::vec4 c = glm::round(m[3] * 1000.0f) / 1000.0f + 0.0f;
	std::printf("%s: translation (%g, %g, %g)\n", label.c_str(), c.x, c.y, c.z);
}

int main()
{
	const glm::mat4 identity(1.0f);
	const glm::mat4 parentWorld = glm::translate(identity, glm::vec3(0.0f, 1.0f, 0.0f))
		* glm::rotate(identity, glm::radians(90.0f), glm::vec3(0.0f, 1.0f, 0.0f));
	const glm::mat4 childLocal = glm::translate(identity, glm::vec3(3.0f, 0.0f, 0.0f));
	const glm::mat4 childWorld = parentWorld * childLocal;
	Print("child world", childWorld);
	Print("inverse(parent) * child world", glm::inverse(parentWorld) * childWorld);
	Print("inverse(parent * local)", glm::inverse(childWorld));
	Print("inverse(local) * inverse(parent)", glm::inverse(childLocal) * glm::inverse(parentWorld));
}
