// A grid of turned boxes against a camera with an infinite reversed-Z projection. Each box gets a world box by Arvo's
// method; a world box is rejected only when its eight corners all lie outside one clip plane.
#include <cstdio>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>

namespace
{
	struct Box
	{
		glm::vec3 Min, Max;
	};

	Box Transformed(const Box& box, const glm::mat4& transform)
	{
		const glm::vec3 center = (box.Min + box.Max) * 0.5f;
		const glm::vec3 extents = (box.Max - box.Min) * 0.5f;
		const glm::vec3 newCenter = glm::vec3(transform * glm::vec4(center, 1.0f));
		glm::vec3 newExtents(0.0f);
		for (int axis = 0; axis < 3; axis++)
		{
			newExtents[axis] = glm::abs(transform[0][axis]) * extents.x + glm::abs(transform[1][axis]) * extents.y
				+ glm::abs(transform[2][axis]) * extents.z;
		}
		return { newCenter - newExtents, newCenter + newExtents };
	}

	bool IsVisible(const Box& box, const glm::mat4& viewProjection)
	{
		// One bit per clip plane. Depth runs from 0 to w, so the planes are x and y against w, z above w (nearer than
		// the near plane) and z below 0 (beyond the far plane, which an infinite far plane never reaches).
		int outsideAll = 0b111111;
		for (int corner = 0; corner < 8; corner++)
		{
			const glm::vec3 point((corner & 1) ? box.Max.x : box.Min.x, (corner & 2) ? box.Max.y : box.Min.y,
				(corner & 4) ? box.Max.z : box.Min.z);
			const glm::vec4 clip = viewProjection * glm::vec4(point, 1.0f);
			int outside = 0;
			if (clip.x > clip.w) outside |= 1;
			if (clip.x < -clip.w) outside |= 2;
			if (clip.y > clip.w) outside |= 4;
			if (clip.y < -clip.w) outside |= 8;
			if (clip.z > clip.w) outside |= 16;
			if (clip.z < 0.0f) outside |= 32;
			outsideAll &= outside;
		}
		return outsideAll == 0;
	}
}

int main()
{
	const glm::mat4 view = glm::lookAtRH(glm::vec3(0.0f, 0.0f, 10.0f), glm::vec3(0.0f), glm::vec3(0.0f, 1.0f, 0.0f));
	const float focal = 1.0f / glm::tan(glm::radians(60.0f) * 0.5f);
	glm::mat4 projection(0.0f);
	projection[0][0] = focal;
	projection[1][1] = focal;
	projection[2][3] = -1.0f;
	projection[3][2] = 0.1f;

	const Box unitBox { glm::vec3(-1.0f), glm::vec3(1.0f) };
	for (const float z : { 20.0f, 0.0f, -50.0f, -1.0e5f })
	{
		std::printf("z = %9.0f:", z);
		for (const float x : { -20.0f, -10.0f, 0.0f, 10.0f, 20.0f })
		{
			const glm::mat4 model = glm::rotate(glm::translate(glm::mat4(1.0f), glm::vec3(x, 0.0f, z)), glm::radians(45.0f), glm::vec3(0.0f, 1.0f, 0.0f));
			std::printf(" %c", IsVisible(Transformed(unitBox, model), projection * view) ? 'X' : '.');
		}
		std::printf("\n");
	}
}
