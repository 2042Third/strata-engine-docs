// Places new instances into a placed update order by binary search and counts the comparisons.
#include <algorithm>
#include <cstdio>
#include <vector>

struct Entry
{
	int Position; // Hierarchy position of the entity: smaller runs first
	const char* Name;
};

int main()
{
	std::vector<Entry> order = { { 10, "A" }, { 20, "B" }, { 30, "C" }, { 40, "D" }, { 50, "E" }, { 60, "F" }, { 70, "G" }, { 80, "H" } };
	const std::vector<Entry> arrivals = { { 35, "X" }, { 5, "Y" }, { 75, "Z" } };

	for (const Entry& arrival : arrivals)
	{
		int comparisons = 0;
		// The first entry whose position comes after the arrival's: the arrival goes right before it.
		const auto after = std::upper_bound(order.begin(), order.end(), arrival.Position, [&comparisons](int position, const Entry& entry)
		{
			comparisons++;
			return position < entry.Position;
		});
		const size_t index = static_cast<size_t>(after - order.begin());
		order.insert(after, arrival);
		std::printf("%s goes to index %zu after %d comparisons\n", arrival.Name, index, comparisons);
	}

	for (const Entry& entry : order)
		std::printf("%s ", entry.Name);
	std::printf("\n");
	return 0;
}
