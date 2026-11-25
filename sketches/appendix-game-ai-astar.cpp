#include <cstdio>
#include <cstdlib>
#include <queue>
const char* c_Map[8] = { "########", "#......#", "#..#..##", "#..#.#.#", "#.##.#.#", "#......#", "#......#", "########" };
void Search(int weight)
{
	const int start = 25, goal = 30; // cell = row * 8 + column
	const auto guess = [&](int c) { return weight * (std::abs(c / 8 - goal / 8) + std::abs(c % 8 - goal % 8)); };
	std::vector<int> cost(64, 99), from(64, -1);
	std::priority_queue<std::pair<int, int>> open; int taken = 0; // largest first: priorities go in negated
	cost[start] = 0; open.push({ -guess(start), start });
	while (!open.empty())
	{
		const int cell = open.top().second; open.pop();
		taken++; if (cell == goal) break;
		for (int n : { cell - 8, cell + 8, cell - 1, cell + 1 })
		{
			if (c_Map[n / 8][n % 8] == '#' || cost[n] <= cost[cell] + 1) continue;
			cost[n] = cost[cell] + 1; from[n] = cell; open.push({ -cost[n] - guess(n), n });
		}
	}
	std::printf("weight %d: length %d, taken %d, path", weight, cost[goal], taken);
	for (int c = goal; c >= 0; c = from[c]) std::printf(" (%d,%d)%s", c % 8 - 1, c / 8 - 1, c == start ? "\n" : "");
}
int main() { Search(1); Search(0); Search(3); }
