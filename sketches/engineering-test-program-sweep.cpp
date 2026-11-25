// A corruption sweep for a small parser: truncation at every selected length and one changed byte at every selected offset.
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <random>
#include <vector>

// The format: one byte holds the number of names; each name is a length byte followed by that many characters.
static bool ParseNames(const std::vector<uint8_t>& bytes, size_t& count)
{
	if (bytes.empty())
		return false;
	size_t position = 1;
	for (uint8_t name = 0; name < bytes[0]; name++)
	{
		if (position >= bytes.size())
			return false;
		const size_t length = bytes[position++];
		if (length > bytes.size() - position)
			return false;
		position += length;
	}
	count = bytes[0];
	return position == bytes.size();
}

// Every offset in a full sweep; else the header, the bytes near the block edges and offsets from a fixed seed.
static std::vector<size_t> SelectOffsets(size_t size, bool full, size_t header, size_t boundary, size_t randomCount)
{
	std::vector<size_t> offsets;
	for (size_t offset = 0; offset < size; offset++)
	{
		const size_t distance = offset % boundary < boundary / 2 ? offset % boundary : boundary - offset % boundary;
		if (full || offset < header || distance <= 2)
			offsets.push_back(offset);
	}
	std::mt19937_64 random(0x5EED ^ size);
	for (size_t index = 0; !full && index < randomCount; index++)
		offsets.push_back(random() % size);
	std::sort(offsets.begin(), offsets.end());
	offsets.erase(std::unique(offsets.begin(), offsets.end()), offsets.end());
	return offsets;
}

int main()
{
	std::vector<uint8_t> good = { 3 };
	for (uint8_t length : { 4, 2, 5 })
	{
		good.push_back(length);
		good.insert(good.end(), length, 'x');
	}
	for (bool full : { false, true })
	{
		const std::vector<size_t> offsets = SelectOffsets(good.size(), full, 2, 8, 6);
		size_t wrongAccepts = 0;
		size_t rejected = 0;
		for (size_t length : offsets)
		{
			size_t count = 0;
			wrongAccepts += ParseNames(std::vector<uint8_t>(good.begin(), good.begin() + static_cast<std::ptrdiff_t>(length)), count) ? 1 : 0;
		}
		for (size_t offset : offsets)
		{
			std::vector<uint8_t> changed = good;
			changed[offset] ^= 0xA5;
			size_t count = 0;
			rejected += ParseNames(changed, count) ? 0 : 1;
		}
		std::printf("%s: %zu of %zu offsets, truncated files accepted %zu, changed bytes rejected %zu\n", full ? "full   " : "sampled", offsets.size(),
			good.size(), wrongAccepts, rejected);
	}
	return 0;
}
