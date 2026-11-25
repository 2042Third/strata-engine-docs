// The stall timer of a launch: it restarts whenever the progress count changes.
#include <cstddef>
#include <iostream>
#include <string>
#include <vector>

static void Run(const std::string& title, const std::vector<int>& counts)
{
	const int pollMilliseconds = 250;
	const int stallMilliseconds = 2000;
	int last = -1;
	int lastChange = 0;
	for (size_t poll = 0; poll < counts.size(); poll++)
	{
		const int now = static_cast<int>(poll) * pollMilliseconds;
		if (counts[poll] != last)
		{
			last = counts[poll];
			lastChange = now;
		}
		if (now - lastChange >= stallMilliseconds)
		{
			std::cout << title << ": stalled at " << now << " ms, last change at " << lastChange << " ms\n";
			return;
		}
	}
	std::cout << title << ": ready\n";
}

int main()
{
	std::vector<int> stuck = { 10, 20, 30 };
	stuck.resize(20, 30);

	std::vector<int> slow;
	for (int poll = 0; poll < 20; poll++)
		slow.push_back(poll / 7);

	Run("stuck", stuck);
	Run("slow", slow);
	return 0;
}
