#include <cstdio>
#include <vector>

struct Box { float X0, Y0, X1, Y1; };

bool Overlaps(const Box& a, const Box& b)
{
	return a.X0 <= b.X1 && a.X1 >= b.X0 && a.Y0 <= b.Y1 && a.Y1 >= b.Y0;
}

int main()
{
	std::vector<Box> boxes;
	for (int i = 0; i < 1000; i++)
	{
		const float x = static_cast<float>(i * 37 % 1000) * 0.1f;
		const float y = static_cast<float>(i * 91 % 1000) * 0.1f;
		boxes.push_back({ x, y, x + 1.0f, y + 1.0f });
	}
	const Box view = { 20.0f, 20.0f, 45.0f, 35.0f };
	int found = 0;
	for (const Box& box : boxes)
		found += Overlaps(box, view) ? 1 : 0;
	std::printf("tested %zu boxes, %d overlap the view\n", boxes.size(), found);
}
