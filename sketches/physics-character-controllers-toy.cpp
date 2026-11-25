#include <array>
#include <cstdio>
#include <span>

#include <glm/glm.hpp>

// A wall or floor in two dimensions: the points where dot(Normal, point) equals Offset. The normal points to the free side.
struct Plane
{
	glm::vec2 Normal;
	float Offset;
};

// Moves a circle by `displacement`, stopping at the planes and sliding along them: each pass pushes the target out of the
// planes it would sink into, and several passes settle a corner where one push undoes another.
glm::vec2 CollideAndSlide(glm::vec2 position, glm::vec2 displacement, float radius, std::span<const Plane> planes)
{
	glm::vec2 target = position + displacement;
	for (int pass = 0; pass < 4; pass++)
	{
		for (const Plane& plane : planes)
		{
			const float gap = glm::dot(plane.Normal, target) - plane.Offset - radius;
			if (gap < 0.0f)
				target -= plane.Normal * gap;
		}
	}
	return target;
}

int main()
{
	const float radius = 0.5f;
	const Plane floor { { 0.0f, 1.0f }, 0.0f };
	const Plane wall { { -1.0f, 0.0f }, -3.0f }; // a wall at x = 3
	const Plane ramp { glm::normalize(glm::vec2(-1.0f, 1.0f)), -0.7071f }; // rises at 45 degrees from x = 1
	const std::array<Plane, 2> room = { floor, wall };
	const std::array<Plane, 2> slope = { floor, ramp };

	const glm::vec2 free = CollideAndSlide({ 0.0f, 0.5f }, { 0.5f, 0.0f }, radius, room);
	std::printf("free walk: x %.3f y %.3f\n", free.x, free.y);

	const glm::vec2 blocked = CollideAndSlide({ 2.0f, 0.5f }, { 2.0f, -0.2f }, radius, room);
	std::printf("into the wall at x = 3: x %.3f y %.3f\n", blocked.x, blocked.y);

	const glm::vec2 climbed = CollideAndSlide({ 0.5f, 0.5f }, { 1.0f, 0.0f }, radius, slope);
	std::printf("onto the ramp: x %.3f y %.3f\n", climbed.x, climbed.y);
	return 0;
}
