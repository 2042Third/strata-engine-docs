#include <cstdint>
#include <cstdio>
#include <initializer_list>

constexpr uint32_t c_HighResolutionRows = 1440;

// The side of one cascade for a row set to AutoFine: it follows the output's rows.
uint32_t ResolveAutoFine(uint32_t outputRows)
{
	return outputRows >= c_HighResolutionRows ? 8192 : 4096;
}

int main()
{
	const uint64_t cascades = 5;
	for (const uint32_t rows : { 1080u, 1439u, 1440u, 2160u })
	{
		const uint64_t side = ResolveAutoFine(rows);
		const uint64_t bytes = cascades * side * side * 4; // One 32-bit depth value per texel
		std::printf("%u rows: side %llu, %llu MiB\n", rows, static_cast<unsigned long long>(side),
			static_cast<unsigned long long>(bytes / (1024 * 1024)));
	}
}
