// A toy comparison of two one-row grey images: the absolute difference and the signed one.
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <vector>

struct Difference
{
	int Differing = 0;
	int Largest = 0;
	float Mean = 0.0f;
};

Difference Absolute(const std::vector<int>& before, const std::vector<int>& after)
{
	Difference result;
	int total = 0;
	for (size_t index = 0; index < before.size(); index++)
	{
		int delta = std::abs(after[index] - before[index]);
		if (delta == 0)
			continue;
		result.Differing++;
		result.Largest = std::max(result.Largest, delta);
		total += delta;
	}
	result.Mean = static_cast<float>(total) / static_cast<float>(before.size());
	return result;
}

void Report(const char* name, const std::vector<int>& before, const std::vector<int>& after)
{
	Difference difference = Absolute(before, after);
	std::printf("%s: %d differ, largest %d, mean %.2f, signed:", name, difference.Differing, difference.Largest, difference.Mean);
	for (size_t index = 0; index < before.size(); index++)
		std::printf(" %d", after[index] - before[index]);
	std::printf("\n");
}

int main()
{
	std::vector<int> before = { 100, 100, 100, 100, 100, 100, 100, 100 };
	std::vector<int> brighter = { 100, 100, 106, 106, 106, 106, 100, 100 };
	std::vector<int> darker = { 100, 100, 94, 94, 94, 94, 100, 100 };
	Report("brighter", before, brighter);
	Report("darker", before, darker);
	return 0;
}
