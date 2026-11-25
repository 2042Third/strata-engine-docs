#include <algorithm>
#include <bit>
#include <cstdint>
#include <cstdio>

// Staging buffers come in powers of two, from a smallest size on, so buffers of similar uploads are reused.
constexpr uint64_t c_MinBufferBytes = 64ull << 10;

uint64_t GetBufferByteSize(uint64_t bytes)
{
	return std::max(c_MinBufferBytes, std::bit_ceil(bytes));
}

int main()
{
	const uint64_t requests[] = { 1, 65536, 65537, 100000, 4194304, 20000000 };
	for (const uint64_t bytes : requests)
	{
		const uint64_t size = GetBufferByteSize(bytes);
		const double waste = 100.0 * static_cast<double>(size - bytes) / static_cast<double>(size);
		std::printf("%llu bytes -> buffer of %llu bytes, %.1f %% unused\n", static_cast<unsigned long long>(bytes),
			static_cast<unsigned long long>(size), waste);
	}
	return 0;
}
