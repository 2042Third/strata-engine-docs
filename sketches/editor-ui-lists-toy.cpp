// A clipped list: only the rows in view are drawn, plus rows that must be drawn whatever the scroll.
#include <algorithm>
#include <cstdio>
#include <vector>

namespace
{

	constexpr int c_RowCount = 100000;
	constexpr float c_RowHeight = 20.0f;
	constexpr float c_WindowHeight = 600.0f;

	struct RowRange
	{
		int Start = 0;
		int End = 0; // One past the last row
	};

	// Which rows the window shows when it is scrolled down by scrollY pixels.
	RowRange GetVisibleRows(float scrollY)
	{
		const int first = std::max(0, static_cast<int>(scrollY / c_RowHeight));
		const int end = std::min(c_RowCount, static_cast<int>((scrollY + c_WindowHeight) / c_RowHeight) + 1);
		return { first, end };
	}

}

int main()
{
	const float scrollY = 1000000.0f;
	const RowRange visible = GetVisibleRows(scrollY);

	// A row that must stay alive (a rename field, a selection anchor) is added to what the loop draws.
	std::vector<int> drawn;
	const int pinned = 3;
	drawn.push_back(pinned);
	for (int row = visible.Start; row < visible.End; row++)
		drawn.push_back(row);

	std::printf("rows in the list: %d\n", c_RowCount);
	std::printf("visible: rows %d to %d\n", visible.Start, visible.End - 1);
	std::printf("drawn with the clip: %zu\n", drawn.size());
	std::printf("drawn without it: %d\n", c_RowCount);
	return 0;
}
