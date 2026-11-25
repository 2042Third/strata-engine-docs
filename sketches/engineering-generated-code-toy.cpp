// A toy of StrataShaderTool's patch: after every "BuiltIn Position" decoration of a hand-made SPIR-V module,
// insert an "Invariant" decoration. Insertions are collected first and made from the back.
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <utility>
#include <vector>

namespace
{
	using Words = std::vector<uint32_t>;

	constexpr size_t c_HeaderWords = 5;
	constexpr uint32_t c_OpDecorate = 71;
	constexpr uint32_t c_OpMemberDecorate = 72;
	constexpr uint32_t c_BuiltIn = 11;
	constexpr uint32_t c_Position = 0;
	constexpr uint32_t c_Invariant = 18;

	uint32_t Op(uint32_t opcode, uint32_t wordCount)
	{
		return (wordCount << 16) | opcode;
	}

	void Print(const char* title, const Words& words)
	{
		std::printf("%s (%zu words)\n", title, words.size());
		for (size_t offset = c_HeaderWords; offset < words.size(); offset += words[offset] >> 16)
			std::printf("  word %2zu: opcode %2u, %u words\n", offset, words[offset] & 0xFFFFu, words[offset] >> 16);
	}

	void DecoratePositionInvariant(Words& words)
	{
		std::vector<std::pair<size_t, Words>> insertions;
		for (size_t offset = c_HeaderWords; offset < words.size(); offset += words[offset] >> 16)
		{
			const uint32_t opcode = words[offset] & 0xFFFFu;
			const size_t end = offset + (words[offset] >> 16);
			if (opcode == c_OpDecorate && words[offset + 2] == c_BuiltIn && words[offset + 3] == c_Position)
				insertions.push_back({ end, { Op(c_OpDecorate, 3), words[offset + 1], c_Invariant } });
			if (opcode == c_OpMemberDecorate && words[offset + 3] == c_BuiltIn && words[offset + 4] == c_Position)
				insertions.push_back({ end, { Op(c_OpMemberDecorate, 4), words[offset + 1], words[offset + 2], c_Invariant } });
		}
		for (auto it = insertions.rbegin(); it != insertions.rend(); ++it)
			words.insert(words.begin() + static_cast<std::ptrdiff_t>(it->first), it->second.begin(), it->second.end());
	}
}

int main()
{
	Words module = { 0x07230203u, 0x00010500u, 0u, 12u, 0u,   // magic, version 1.5, generator, id bound, schema
		Op(17, 2), 1u,                                          // OpCapability Shader
		Op(c_OpDecorate, 4), 3u, c_BuiltIn, c_Position,         // OpDecorate %3 BuiltIn Position
		Op(c_OpDecorate, 4), 4u, 30u, 0u,                       // OpDecorate %4 Location 0
		Op(c_OpMemberDecorate, 5), 5u, 0u, c_BuiltIn, c_Position, // OpMemberDecorate %5 0 BuiltIn Position
		Op(19, 2), 2u };                                        // OpTypeVoid %2
	Print("before", module);
	DecoratePositionInvariant(module);
	Print("after", module);
	return 0;
}
