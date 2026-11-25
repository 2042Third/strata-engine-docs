// Exercise solution: a size limit counted in code points, not in bytes, as Docs.AgentGuide counts.
#include <cstddef>
#include <cstdio>
#include <string>

// A UTF-8 text has one code point for every byte that is not a continuation byte (10xxxxxx).
static size_t CountCodePoints(const std::string& text)
{
	size_t count = 0;
	for (const char byte : text)
	{
		if ((static_cast<unsigned char>(byte) & 0xC0) != 0x80)
			count++;
	}
	return count;
}

int main()
{
	const size_t limit = 40000;
	const size_t current = 38677; // the code points of AGENTS.md before the change
	// A heading with an em dash: the dash is one code point and three bytes.
	const std::string heading = "Strata Engine \xE2\x80\x94 Agent Guide";
	std::printf("heading: %zu bytes, %zu code points\n", heading.size(), CountCodePoints(heading));

	const size_t added[] = { 1300, 1400 };
	for (const size_t count : added)
		std::printf("adding %zu: %zu of %zu, %s\n", count, current + count, limit, current + count <= limit ? "fits" : "over the limit");
	return 0;
}
