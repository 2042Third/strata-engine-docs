// Orders moved body numbers with a bitmap, visiting only the words that got a bit.
#include <algorithm>
#include <bit>
#include <cstdint>
#include <cstdio>
#include <utility>
#include <vector>

int main()
{
	std::vector<uint64_t> bits(3, 0);
	std::vector<uint32_t> words;
	const uint32_t moved[] = { 130, 3, 71, 70 };
	for (const uint32_t body : moved)
	{
		uint64_t& word = bits[body / 64];
		if (word == 0)
			words.push_back(body / 64);
		word |= uint64_t(1) << (body % 64);
	}

	std::sort(words.begin(), words.end());
	for (const uint32_t index : words)
	{
		for (uint64_t rest = std::exchange(bits[index], 0); rest != 0; rest &= rest - 1)
			std::printf("%u ", index * 64 + static_cast<uint32_t>(std::countr_zero(rest)));
	}
	std::printf("\n");
}
