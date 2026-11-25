// A small SPIR-V inspector: refuses a module whose framing is wrong, lists the opcodes of one that is right.
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <string>
#include <vector>

namespace
{
	using Words = std::vector<uint32_t>;

	constexpr size_t c_HeaderWords = 5;
	constexpr uint32_t c_MagicNumber = 0x07230203u;

	uint32_t Op(uint32_t opcode, uint32_t wordCount)
	{
		return (wordCount << 16) | opcode;
	}

	// The first problem with the module's framing, or an empty string when there is none.
	std::string Check(const Words& words)
	{
		if (words.empty() || words[0] != c_MagicNumber)
			return "word 0 is not the magic number";
		if (words.size() < c_HeaderWords)
			return "the module ends inside its header";
		for (size_t offset = c_HeaderWords; offset < words.size(); offset += words[offset] >> 16)
		{
			const size_t count = words[offset] >> 16;
			if (count == 0)
				return "word count 0 at word " + std::to_string(offset);
			if (count > words.size() - offset)
				return "the instruction at word " + std::to_string(offset) + " runs past the end";
		}
		return "";
	}

	void Inspect(const char* title, const Words& words)
	{
		const std::string problem = Check(words);
		if (!problem.empty())
		{
			std::printf("%s: refused, %s\n", title, problem.c_str());
			return;
		}
		std::printf("%s: accepted\n", title);
		for (size_t offset = c_HeaderWords; offset < words.size(); offset += words[offset] >> 16)
		{
			const uint32_t opcode = words[offset] & 0xFFFFu;
			const bool builtIn = opcode == 71 && words[offset + 2] == 11;
			std::printf("  word %zu: opcode %u%s\n", offset, opcode, builtIn ? " (decorates a built-in)" : "");
		}
	}
}

int main()
{
	const Words good = { c_MagicNumber, 0x00010500u, 0u, 8u, 0u, Op(17, 2), 1u, Op(71, 4), 3u, 11u, 0u };
	Words wrongMagic = good;
	wrongMagic[0] = 0x03022307u;
	Words zeroCount = good;
	zeroCount[5] = Op(17, 0);
	Words pastTheEnd = good;
	pastTheEnd[7] = Op(71, 9);
	Inspect("good", good);
	Inspect("wrong magic", wrongMagic);
	Inspect("zero count", zeroCount);
	Inspect("past the end", pastTheEnd);
	return 0;
}
