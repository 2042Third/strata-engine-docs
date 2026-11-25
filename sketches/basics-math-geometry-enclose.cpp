#include <cstdio>
#include <glm/glm.hpp>

struct Box { glm::vec3 Low = glm::vec3(1e30f); glm::vec3 High = glm::vec3(-1e30f); }; // empty: Low is above High

Box Enclose(const glm::vec3 points[], int count)
{
	Box box;
	for (int i = 0; i < count; i++)
	{
		box.Low = glm::min(box.Low, points[i]);
		box.High = glm::max(box.High, points[i]);
	}
	return box;
}

int main()
{
	const glm::vec3 points[3] = { glm::vec3(1.0f, 2.0f, 0.0f), glm::vec3(-1.0f, 5.0f, 2.0f), glm::vec3(0.0f, 3.0f, -4.0f) };
	const Box box = Enclose(points, 3);
	std::printf("low (%g, %g, %g), high (%g, %g, %g)\n", box.Low.x, box.Low.y, box.Low.z, box.High.x, box.High.y, box.High.z);
	std::printf("no points: low.x %g, high.x %g\n", Enclose(points, 0).Low.x, Enclose(points, 0).High.x);
}
