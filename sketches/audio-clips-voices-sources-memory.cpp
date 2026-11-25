// What one three-minute stereo music file costs at 44,100 Hz in each load mode, for one and for eight voices.
#include <cstdint>
#include <cstdio>
#include <initializer_list>

namespace
{

	constexpr uint64_t c_Seconds = 180;
	constexpr uint64_t c_SampleRate = 44100;
	constexpr uint64_t c_Channels = 2;
	constexpr uint64_t c_EncodedBytes = 4 * 1024 * 1024; // The size of the encoded file in this exercise

	uint64_t DecodedBytes()
	{
		return c_Seconds * c_SampleRate * c_Channels * sizeof(float);
	}

}

int main()
{
	for (uint64_t voices : { 1, 8 })
	{
		std::printf("%llu voice(s)\n", static_cast<unsigned long long>(voices));
		std::printf("  Decompressed: %llu bytes shared, 0 frames decoded per second\n", static_cast<unsigned long long>(DecodedBytes()));
		std::printf("  Streamed: %llu bytes shared, %llu frames decoded per second\n", static_cast<unsigned long long>(c_EncodedBytes), static_cast<unsigned long long>(voices * c_SampleRate));
	}
	return 0;
}
