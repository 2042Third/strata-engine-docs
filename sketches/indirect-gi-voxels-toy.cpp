// Voxelizes a box's twelve triangles on a grid of unit voxels with Akenine-Moller's triangle-box test.
#include <glm/glm.hpp>

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <set>
#include <vector>

struct Triangle
{
	glm::vec3 A;
	glm::vec3 B;
	glm::vec3 C;
};

// True when the axis puts the triangle's shadow and the box's shadow apart. The box is centered on the origin.
static bool AxisSeparates(const glm::vec3& axis, const Triangle& triangle, const glm::vec3& halfSize)
{
	const float p0 = glm::dot(triangle.A, axis);
	const float p1 = glm::dot(triangle.B, axis);
	const float p2 = glm::dot(triangle.C, axis);
	const float radius = halfSize.x * std::abs(axis.x) + halfSize.y * std::abs(axis.y) + halfSize.z * std::abs(axis.z);
	return std::max({ p0, p1, p2 }) < -radius || std::min({ p0, p1, p2 }) > radius;
}

// Touching counts as overlap. Thirteen axes decide: nine edge crossings, three box faces and the triangle's plane.
static bool TriangleBoxOverlap(const glm::vec3& center, const glm::vec3& halfSize, Triangle triangle)
{
	triangle.A -= center;
	triangle.B -= center;
	triangle.C -= center;
	const std::array<glm::vec3, 3> edges = { triangle.B - triangle.A, triangle.C - triangle.B, triangle.A - triangle.C };
	const std::array<glm::vec3, 3> axes = { glm::vec3(1, 0, 0), glm::vec3(0, 1, 0), glm::vec3(0, 0, 1) };
	for (const glm::vec3& axis : axes)
	{
		for (const glm::vec3& edge : edges)
		{
			if (AxisSeparates(glm::cross(axis, edge), triangle, halfSize))
				return false;
		}
		if (AxisSeparates(axis, triangle, halfSize))
			return false;
	}
	return !AxisSeparates(glm::cross(edges[0], edges[1]), triangle, halfSize);
}

// A face with its normal along cross(u, v) is two triangles.
static void AddFace(std::vector<Triangle>& triangles, const glm::vec3& origin, const glm::vec3& u, const glm::vec3& v)
{
	triangles.push_back({ origin, origin + u, origin + u + v });
	triangles.push_back({ origin, origin + u + v, origin + v });
}

static std::vector<Triangle> MakeBox(float low, float high)
{
	const float s = high - low;
	const glm::vec3 o(low);
	std::vector<Triangle> triangles;
	AddFace(triangles, o, glm::vec3(0, 0, s), glm::vec3(0, s, 0));
	AddFace(triangles, { high, low, low }, glm::vec3(0, s, 0), glm::vec3(0, 0, s));
	AddFace(triangles, o, glm::vec3(s, 0, 0), glm::vec3(0, 0, s));
	AddFace(triangles, { low, high, low }, glm::vec3(0, 0, s), glm::vec3(s, 0, 0));
	AddFace(triangles, o, glm::vec3(0, s, 0), glm::vec3(s, 0, 0));
	AddFace(triangles, { low, low, high }, glm::vec3(s, 0, 0), glm::vec3(0, s, 0));
	return triangles;
}

int main()
{
	std::set<std::array<int, 3>> voxels;
	for (const Triangle& triangle : MakeBox(2.4f, 6.6f))
	{
		const glm::vec3 low = glm::min(glm::min(triangle.A, triangle.B), triangle.C);
		const glm::vec3 high = glm::max(glm::max(triangle.A, triangle.B), triangle.C);
		for (int z = int(std::floor(low.z)); z <= int(std::floor(high.z)); z++)
		{
			for (int y = int(std::floor(low.y)); y <= int(std::floor(high.y)); y++)
			{
				for (int x = int(std::floor(low.x)); x <= int(std::floor(high.x)); x++)
				{
					if (TriangleBoxOverlap(glm::vec3(x, y, z) + 0.5f, glm::vec3(0.5f), triangle))
						voxels.insert({ x, y, z });
				}
			}
		}
	}
	std::printf("voxels touched by the box's surface: %zu\n", voxels.size());
	for (int z = 0; z < 9; z++)
	{
		for (int x = 0; x < 9; x++)
			std::printf("%c ", voxels.count({ x, 4, z }) ? '#' : '.');
		std::printf("\n");
	}
}
