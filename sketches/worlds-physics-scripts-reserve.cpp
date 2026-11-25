// What the streamer reserves before it starts loads: the persistent scene, held cells and the cells about to start.
#include <cstdint>
#include <cstdio>
#include <vector>

struct Cell
{
	const char* Name = "";
	uint64_t Bodies = 0;
	bool Failed = false;
};

int main()
{
	const uint64_t persistent = 30;
	const std::vector<Cell> held = { { "A", 40, false }, { "B", 5, false }, { "D", 20, true } };
	const std::vector<Cell> starting = { { "C", 60, false }, { "E", 10, false } };
	uint64_t bodies = persistent;
	for (const Cell& cell : held)
		if (!cell.Failed) // a failed cell holds no bodies
			bodies += cell.Bodies;
	for (const Cell& cell : starting)
		bodies += cell.Bodies;
	std::printf("reserve %llu bodies\n", static_cast<unsigned long long>(bodies));
	return 0;
}
