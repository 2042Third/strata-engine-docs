#include <cstdio>
#include <glm/glm.hpp>

struct Box { glm::vec3 Low; glm::vec3 High; };

bool Overlaps(const Box& a, const Box& b) { return glm::all(glm::lessThanEqual(a.Low, b.High)) && glm::all(glm::greaterThanEqual(a.High, b.Low)); }

Box Grow(const Box& box, const glm::vec3& point) { return { glm::min(box.Low, point), glm::max(box.High, point) }; }

bool SphereTouches(const glm::vec3& center, float radius, const Box& box)
{
	const glm::vec3 gap = center - glm::clamp(center, box.Low, box.High); // from the center to the box's closest point
	return glm::dot(gap, gap) <= radius * radius;
}

int main()
{
	const Box a = { glm::vec3(0.0f), glm::vec3(2.0f) };
	const Box grown = Grow(a, glm::vec3(3.0f, -1.0f, 1.0f));
	std::printf("overlap %d, ", Overlaps(a, Box{ glm::vec3(1.0f), glm::vec3(3.0f) }));
	std::printf("apart %d\n", Overlaps(a, Box{ glm::vec3(3.0f, 0.0f, 0.0f), glm::vec3(4.0f, 2.0f, 2.0f) }));
	std::printf("grown low (%g, %g, %g) high (%g, %g, %g)\n", grown.Low.x, grown.Low.y, grown.Low.z, grown.High.x, grown.High.y, grown.High.z);
	std::printf("sphere %d, ", SphereTouches(glm::vec3(2.5f, 1.0f, 1.0f), 0.6f, a));
	std::printf("corner %d\n", SphereTouches(glm::vec3(2.5f, 2.5f, 1.0f), 0.6f, a));
}
