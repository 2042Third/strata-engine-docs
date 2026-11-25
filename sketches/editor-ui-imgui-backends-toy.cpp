#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <vector>

// A toy renderer backend: the steps of a UI renderer, with a printout in place of a GPU.
struct Vertex
{
	float X;
	float Y;
	float U;
	float V;
	uint32_t Color;
};

struct Command
{
	float ClipMinX;
	float ClipMinY;
	float ClipMaxX;
	float ClipMaxY;
	uint32_t ElemCount;
	uint32_t IdxOffset;
	uint32_t VtxOffset;
};

struct DrawList
{
	std::vector<Vertex> Vertices;
	std::vector<uint16_t> Indices;
	std::vector<Command> Commands;
};

struct DrawData
{
	float DisplayWidth;
	float DisplayHeight;
	float Scale; // Framebuffer pixels per display unit
	std::vector<DrawList> Lists;
};

static void Render(const DrawData& data)
{
	const float width = data.DisplayWidth * data.Scale;
	const float height = data.DisplayHeight * data.Scale;

	// One vertex buffer and one index buffer for every list, so each list starts after the one before it.
	std::vector<Vertex> vertices;
	std::vector<uint16_t> indices;
	for (const DrawList& list : data.Lists)
	{
		vertices.insert(vertices.end(), list.Vertices.begin(), list.Vertices.end());
		indices.insert(indices.end(), list.Indices.begin(), list.Indices.end());
	}

	// Pixels with y down to NDC with y up: x * scale + translate.
	const float scaleX = 2.0f / data.DisplayWidth;
	const float scaleY = -2.0f / data.DisplayHeight;
	std::printf("scale (%.7f, %.7f) translate (-1, 1), %zu vertices, %zu indices\n", scaleX, scaleY, vertices.size(), indices.size());

	uint32_t globalVertex = 0;
	uint32_t globalIndex = 0;
	for (const DrawList& list : data.Lists)
	{
		for (const Command& command : list.Commands)
		{
			const float minX = std::max(command.ClipMinX * data.Scale, 0.0f);
			const float minY = std::max(command.ClipMinY * data.Scale, 0.0f);
			const float maxX = std::min(command.ClipMaxX * data.Scale, width);
			const float maxY = std::min(command.ClipMaxY * data.Scale, height);
			if (maxX <= minX || maxY <= minY)
				continue;
			std::printf("draw %u indices from index %u, vertex %u, scissor x %.0f to %.0f, y %.0f to %.0f\n", command.ElemCount,
				command.IdxOffset + globalIndex, command.VtxOffset + globalVertex, minX, maxX, minY, maxY);
		}
		globalVertex += static_cast<uint32_t>(list.Vertices.size());
		globalIndex += static_cast<uint32_t>(list.Indices.size());
	}
}

int main()
{
	DrawList panel;
	panel.Vertices.assign(400, Vertex { 0.0f, 0.0f, 0.0f, 0.0f, 0xFFFFFFFFu });
	panel.Indices.assign(600, 0);
	panel.Commands = { Command { 10.0f, 20.0f, 210.0f, 120.0f, 600, 0, 0 } };

	DrawList popup;
	popup.Vertices.assign(120, Vertex { 0.0f, 0.0f, 0.0f, 0.0f, 0xFFFFFFFFu });
	popup.Indices.assign(180, 0);
	popup.Commands = { Command { 1500.0f, 800.0f, 1700.0f, 1000.0f, 180, 0, 0 }, Command { 5.0f, 5.0f, 5.0f, 90.0f, 3, 0, 0 } };

	Render(DrawData { 1600.0f, 900.0f, 1.0f, { panel, popup } });
	Render(DrawData { 800.0f, 450.0f, 2.0f, { panel, popup } });
	return 0;
}
