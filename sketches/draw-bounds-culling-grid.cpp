#include <cstdio>
#include <map>
#include <utility>
#include <vector>

struct Box { float X0, Y0, X1, Y1; };

bool Overlaps(const Box& a, const Box& b)
{
	return a.X0 <= b.X1 && a.X1 >= b.X0 && a.Y0 <= b.Y1 && a.Y1 >= b.Y0;
}

int main()
{
	std::map<std::pair<int, int>, std::vector<Box>> cells; // Cells of 10 by 10 units, keyed by the box's corner
	for (int i = 0; i < 1000; i++)
	{
		const float x = static_cast<float>(i * 37 % 1000) * 0.1f;
		const float y = static_cast<float>(i * 91 % 1000) * 0.1f;
		cells[{ static_cast<int>(x / 10.0f), static_cast<int>(y / 10.0f) }].push_back({ x, y, x + 1.0f, y + 1.0f });
	}
	const Box view = { 20.0f, 20.0f, 45.0f, 35.0f };
	int found = 0;
	int tested = 0;
	for (const auto& [cell, boxes] : cells)
	{
		const float x = static_cast<float>(cell.first) * 10.0f;
		const float y = static_cast<float>(cell.second) * 10.0f;
		if (!Overlaps({ x, y, x + 11.0f, y + 11.0f }, view)) // The cell's area, grown by a box's size
			continue;
		for (const Box& box : boxes)
		{
			tested++;
			found += Overlaps(box, view) ? 1 : 0;
		}
	}
	std::printf("tested %d boxes, %d overlap the view\n", tested, found);
}
