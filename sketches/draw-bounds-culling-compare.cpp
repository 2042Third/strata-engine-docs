#include <algorithm>
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
	std::vector<Box> boxes;
	std::map<std::pair<int, int>, std::vector<int>> cells; // Ids of the boxes in each 10 by 10 cell
	for (int i = 0; i < 100000; i++)
	{
		const float x = static_cast<float>(i * 7919 % 100000) * 0.01f;
		const float y = static_cast<float>(i * 6007 % 100000) * 0.01f;
		boxes.push_back({ x, y, x + 1.0f, y + 1.0f });
		cells[{ static_cast<int>(x / 10.0f), static_cast<int>(y / 10.0f) }].push_back(i);
	}
	const Box view = { 200.0f, 200.0f, 450.0f, 350.0f };
	std::vector<int> brute;
	std::vector<int> grid;
	int tested = 0;
	for (int i = 0; i < 100000; i++)
	{
		if (Overlaps(boxes[i], view))
			brute.push_back(i);
	}
	for (const auto& [cell, ids] : cells)
	{
		const float x = static_cast<float>(cell.first) * 10.0f;
		const float y = static_cast<float>(cell.second) * 10.0f;
		if (!Overlaps({ x, y, x + 11.0f, y + 11.0f }, view))
			continue;
		for (const int id : ids)
		{
			tested++;
			if (Overlaps(boxes[id], view))
				grid.push_back(id);
		}
	}
	std::sort(grid.begin(), grid.end());
	std::printf("same ids: %s, brute tested 100000, grid tested %d\n", grid == brute ? "yes" : "no", tested);
}
