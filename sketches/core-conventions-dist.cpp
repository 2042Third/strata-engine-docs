// The toy's assert in a Dist build: the condition inside it is never evaluated, so a side effect there is lost.
#include <algorithm>
#include <cstdio>
#include <vector>

#define TOY_DIST

#if defined(TOY_DIST)
	#define TOY_ASSERT(condition) ((void)0)
#else
	#define TOY_ASSERT(condition) ((condition) ? (void)0 : (void)std::puts("assertion failed"))
#endif

namespace
{
	// Removes the first element equal to id; returns whether it found one.
	bool Remove(std::vector<int>& ids, int id)
	{
		const auto found = std::find(ids.begin(), ids.end(), id);
		if (found == ids.end())
			return false;
		ids.erase(found);
		return true;
	}
}

int main()
{
	std::vector<int> broken = { 1, 2, 3 };
	TOY_ASSERT(Remove(broken, 2)); // the removal is inside the assert

	std::vector<int> fixed = { 1, 2, 3 };
	[[maybe_unused]] const bool removed = Remove(fixed, 2);
	TOY_ASSERT(removed); // the removal is outside: only the check is optional

	std::printf("broken keeps %zu ids, fixed keeps %zu ids\n", broken.size(), fixed.size());
	return 0;
}
