// Voxelizes a closed box, then fills its inside by counting winding steps along each column of voxels.
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

static bool AxisSeparates(const glm::vec3& axis, const Triangle& triangle, const glm::vec3& halfSize)
{
	const float p0 = glm::dot(triangle.A, axis);
	const float p1 = glm::dot(triangle.B, axis);
	const float p2 = glm::dot(triangle.C, axis);
	const float radius = halfSize.x * std::abs(axis.x) + halfSize.y * std::abs(axis.y) + halfSize.z * std::abs(axis.z);
	return std::max({ p0, p1, p2 }) < -radius || std::min({ p0, p1, p2 }) > radius;
}

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

static float Edge(const glm::vec2& a, const glm::vec2& b, const glm::vec2& p)
{
	return (b.x - a.x) * (p.y - a.y) - (b.y - a.y) * (p.x - a.x);
}

// Adds +1 where the column's line enters the mesh and -1 where it leaves, at the first voxel whose center lies above the crossing.
static void AddWindingSteps(const Triangle& triangle, int steps[9][9][9])
{
	const float facing = glm::cross(triangle.B - triangle.A, triangle.C - triangle.A).y;
	if (std::abs(facing) < 1e-9f)
		return;
	const glm::vec2 a(triangle.A.x, triangle.A.z);
	const glm::vec2 b(triangle.B.x, triangle.B.z);
	const glm::vec2 c(triangle.C.x, triangle.C.z);
	const float sign = Edge(a, b, c) < 0.0f ? -1.0f : 1.0f;
	for (int z = 0; z < 9; z++)
	{
		for (int x = 0; x < 9; x++)
		{
			const glm::vec2 p(float(x) + 0.50137f, float(z) + 0.50291f); // Off the voxel centers, so no mesh edge lies on a line
			const float w0 = sign * Edge(b, c, p);
			const float w1 = sign * Edge(c, a, p);
			const float w2 = sign * Edge(a, b, p);
			if (w0 < 0.0f || w1 < 0.0f || w2 < 0.0f)
				continue;
			const float y = (w0 * triangle.A.y + w1 * triangle.B.y + w2 * triangle.C.y) / (w0 + w1 + w2);
			const int layer = std::max(int(std::floor(y - 0.5f)) + 1, 0);
			if (layer < 9)
				steps[x][layer][z] += facing < 0.0f ? 1 : -1;
		}
	}
}

int main()
{
	const std::vector<Triangle> box = MakeBox(2.4f, 6.6f);
	std::set<std::array<int, 3>> surface;
	int steps[9][9][9] = {};
	for (const Triangle& triangle : box)
	{
		AddWindingSteps(triangle, steps);
		const glm::vec3 low = glm::min(glm::min(triangle.A, triangle.B), triangle.C);
		const glm::vec3 high = glm::max(glm::max(triangle.A, triangle.B), triangle.C);
		for (int z = int(std::floor(low.z)); z <= int(std::floor(high.z)); z++)
		{
			for (int y = int(std::floor(low.y)); y <= int(std::floor(high.y)); y++)
			{
				for (int x = int(std::floor(low.x)); x <= int(std::floor(high.x)); x++)
				{
					if (TriangleBoxOverlap(glm::vec3(x, y, z) + 0.5f, glm::vec3(0.5f), triangle))
						surface.insert({ x, y, z });
				}
			}
		}
	}
	int solid = 0;
	int interior = 0;
	for (int z = 0; z < 9; z++)
	{
		for (int x = 0; x < 9; x++)
		{
			int sum = 0;
			for (int y = 0; y < 9; y++)
			{
				sum += steps[x][y][z];
				if (sum == 0)
					continue;
				solid++;
				interior += surface.count({ x, y, z }) == 0 ? 1 : 0;
			}
		}
	}
	std::printf("surface %zu, solid %d, interior %d\n", surface.size(), solid, interior);
}
