// Why the order of publishing matters: the same four root moves, applied in two orders, end at different positions.
#include <array>
#include <cstdio>

int main()
{
	// Each animator's job produced one move; the sizes are chosen so that float rounding shows.
	const std::array<float, 4> moves = { 3.0f, 3.0f, 100000000.0f, -100000000.0f };
	const std::array<int, 4> recordOrder = { 0, 1, 2, 3 };
	const std::array<int, 4> finishOrder = { 2, 0, 3, 1 }; // The order four threads might finish in.

	float byRecord = 0.0f;
	for (const int index : recordOrder)
		byRecord += moves[static_cast<size_t>(index)];
	float byFinish = 0.0f;
	for (const int index : finishOrder)
		byFinish += moves[static_cast<size_t>(index)];

	std::printf("in record order: %.1f\n", static_cast<double>(byRecord));
	std::printf("in finish order: %.1f\n", static_cast<double>(byFinish));
	return 0;
}
