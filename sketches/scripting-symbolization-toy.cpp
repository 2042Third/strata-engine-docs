// A toy symbolizer: the nearest symbol at or below an offset, valid only inside the symbol's size.
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <string>
#include <vector>

namespace
{
	struct Symbol
	{
		uint64_t Offset = 0; // From the start of the module
		uint64_t Size = 0;
		std::string Name;
	};

	// The table is sorted by offset, as a linker writes it.
	const std::vector<Symbol> s_Table = {
		{ 0x1000, 0x100, "OnCreate" },
		{ 0x1100, 0x100, "Crash" },
		{ 0x1200, 0x100, "Update" },
	};

	std::string Describe(uint64_t offset)
	{
		const auto above = std::upper_bound(s_Table.begin(), s_Table.end(), offset,
			[](uint64_t value, const Symbol& symbol) { return value < symbol.Offset; });
		if (above == s_Table.begin())
			return "unknown";
		const Symbol& symbol = *(above - 1);
		if (offset - symbol.Offset >= symbol.Size)
			return "unknown";
		char text[64];
		std::snprintf(text, sizeof(text), "%s+0x%llx", symbol.Name.c_str(), static_cast<unsigned long long>(offset - symbol.Offset));
		return text;
	}

	void Print(const char* what, uint64_t offset)
	{
		std::printf("%-22s 0x%llx -> %s\n", what, static_cast<unsigned long long>(offset), Describe(offset).c_str());
	}
}

int main()
{
	Print("fault address", 0x1234);
	Print("return address", 0x1200);
	Print("return address minus 1", 0x1200 - 1);
	Print("before the table", 0x0fff);
	Print("after the last symbol", 0x1400);
	return 0;
}
