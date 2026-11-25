#include <cstdint>
#include <cstdio>

namespace
{
	struct Capture
	{
		bool Active = false;
		uint64_t Id = 0; // The number of the last Begin: it never goes back
	};

	Capture s_Capture;

	uint64_t Begin()
	{
		s_Capture.Id++;
		s_Capture.Active = true;
		return s_Capture.Id;
	}

	// An owner cancels only the capture it began: its number must still be the current one.
	bool CancelIfOwned(uint64_t owned)
	{
		if (owned != s_Capture.Id)
			return false;
		s_Capture.Active = false;
		return true;
	}
}

int main()
{
	const uint64_t page = Begin();
	const uint64_t menu = Begin();
	std::printf("page owns %llu, menu owns %llu\n", static_cast<unsigned long long>(page), static_cast<unsigned long long>(menu));
	// Each cancel runs before its printf reads the state: the order of a call's arguments is not fixed.
	const bool pageCancelled = CancelIfOwned(page);
	std::printf("page cancels: %d, still listening: %d\n", pageCancelled ? 1 : 0, s_Capture.Active ? 1 : 0);
	const bool menuCancelled = CancelIfOwned(menu);
	std::printf("menu cancels: %d, still listening: %d\n", menuCancelled ? 1 : 0, s_Capture.Active ? 1 : 0);
	return 0;
}
