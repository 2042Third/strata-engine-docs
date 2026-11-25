// The capacity a vertex arena has after each growth, for requests that did not fit.
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <initializer_list>

constexpr uint64_t c_MaxBufferBytes = 2ull << 30;
constexpr uint64_t c_AttributeStride = 36;
constexpr uint64_t c_VertexGranularity = 16;

uint64_t Grow(uint64_t capacity, uint64_t requested)
{
	const uint64_t wanted = std::max(capacity * 2, capacity + requested);
	const uint64_t limit = c_MaxBufferBytes / c_AttributeStride;
	return std::min(wanted, limit) / c_VertexGranularity * c_VertexGranularity;
}

int main()
{
	uint64_t capacity = 65536;
	for (const uint64_t requested : { 100000ull, 200000ull, 70000ull, 60000000ull })
	{
		capacity = Grow(capacity, requested);
		std::printf("request %llu: capacity %llu vertices\n", static_cast<unsigned long long>(requested), static_cast<unsigned long long>(capacity));
	}
}
