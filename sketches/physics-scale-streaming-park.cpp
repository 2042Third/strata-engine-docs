#include <algorithm>
#include <cstdint>
#include <cstdio>

constexpr uint64_t c_ParkedSteps = 60;
constexpr uint32_t c_DisablesPerStep = 1024;

int main()
{
	// 2,500 static bodies are parked together at step 10; count what each later step disables.
	const uint64_t parkedAt = 10;
	uint32_t waiting = 2500;
	for (uint64_t step = parkedAt; waiting > 0; step++)
	{
		if (step < parkedAt + c_ParkedSteps)
			continue;
		const uint32_t disabled = std::min(waiting, c_DisablesPerStep);
		waiting -= disabled;
		std::printf("step %llu disables %u, %u left\n", static_cast<unsigned long long>(step), disabled, waiting);
	}
	return 0;
}
