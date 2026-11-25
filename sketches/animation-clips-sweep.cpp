// A tiny cooked clip and a loader that bounds every count before it allocates, then a sweep that flips each byte.
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <vector>

namespace
{

	constexpr uint32_t c_Magic = 0x43544E59;
	constexpr uint32_t c_MaxKeys = 1024;

	struct Header
	{
		uint32_t Magic;
		uint32_t KeyCount;
	};

	// The bytes: a header, then the key times, then one value per key.
	std::vector<uint8_t> Cook(const std::vector<float>& times, const std::vector<float>& values)
	{
		const Header header { c_Magic, static_cast<uint32_t>(times.size()) };
		std::vector<uint8_t> bytes(sizeof(Header) + (times.size() + values.size()) * sizeof(float));
		std::memcpy(bytes.data(), &header, sizeof(Header));
		std::memcpy(bytes.data() + sizeof(Header), times.data(), times.size() * sizeof(float));
		std::memcpy(bytes.data() + sizeof(Header) + times.size() * sizeof(float), values.data(), values.size() * sizeof(float));
		return bytes;
	}

	bool Load(const std::vector<uint8_t>& bytes, std::vector<float>& outTimes, std::vector<float>& outValues)
	{
		Header header;
		if (bytes.size() < sizeof(Header))
			return false;
		std::memcpy(&header, bytes.data(), sizeof(Header));
		// Both bounds come before any allocation: the format's limit and the bytes that are left.
		if (header.Magic != c_Magic || header.KeyCount == 0 || header.KeyCount > c_MaxKeys)
			return false;
		if (bytes.size() != sizeof(Header) + 2 * static_cast<size_t>(header.KeyCount) * sizeof(float))
			return false;
		outTimes.resize(header.KeyCount);
		outValues.resize(header.KeyCount);
		std::memcpy(outTimes.data(), bytes.data() + sizeof(Header), header.KeyCount * sizeof(float));
		std::memcpy(outValues.data(), bytes.data() + sizeof(Header) + header.KeyCount * sizeof(float), header.KeyCount * sizeof(float));
		for (uint32_t key = 0; key < header.KeyCount; key++)
		{
			const bool increasing = key == 0 || outTimes[key] > outTimes[key - 1];
			if (!std::isfinite(outTimes[key]) || outTimes[key] < 0.0f || !increasing || !std::isfinite(outValues[key]))
				return false;
		}
		return true;
	}

}

int main()
{
	const std::vector<uint8_t> cooked = Cook({ 0.0f, 1.0f, 3.0f }, { 0.0f, 2.0f, 1.0f });
	int accepted = 0;
	int rejected = 0;
	for (size_t position = 0; position < cooked.size(); position++)
	{
		std::vector<uint8_t> damaged = cooked;
		damaged[position] ^= 0xFF;
		std::vector<float> times;
		std::vector<float> values;
		(Load(damaged, times, values) ? accepted : rejected)++;
	}
	std::printf("%zu bytes flipped one at a time: %d rejected, %d loaded\n", cooked.size(), rejected, accepted);
	return 0;
}
