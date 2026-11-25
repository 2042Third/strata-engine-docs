#include <cstdint>
#include <cstdio>
#include <queue>
#include <string>
#include <vector>

enum class GpuType
{
	Other,
	Integrated,
	Discrete
};

struct Gpu
{
	std::string Name;
	GpuType Type = GpuType::Other;
	uint32_t VulkanMinor = 2;
	bool DynamicRendering = true;
	uint64_t MemoryMiB = 0;
};

// Picks the best GPU that meets the requirements; every rejection is logged with its reason.
int SelectGpu(const std::vector<Gpu>& gpus)
{
	int best = -1;
	int64_t bestScore = -1;
	for (size_t index = 0; index < gpus.size(); index++)
	{
		const Gpu& gpu = gpus[index];
		if (gpu.VulkanMinor < 2)
		{
			std::printf("GPU '%s' skipped: Vulkan 1.%u (1.2 required)\n", gpu.Name.c_str(), static_cast<unsigned>(gpu.VulkanMinor));
			continue;
		}
		if (!gpu.DynamicRendering)
		{
			std::printf("GPU '%s' skipped: no dynamic rendering support\n", gpu.Name.c_str());
			continue;
		}
		int64_t score = static_cast<int64_t>(gpu.MemoryMiB);
		if (gpu.Type == GpuType::Discrete)
			score += 1'000'000;
		else if (gpu.Type == GpuType::Integrated)
			score += 100'000;
		std::printf("GPU '%s' scores %lld\n", gpu.Name.c_str(), static_cast<long long>(score));
		if (score <= bestScore)
			continue;
		bestScore = score;
		best = static_cast<int>(index);
	}
	return best;
}

// One ticket per submitted frame; a frame may begin only while fewer than the limit are still queued.
class FramePacer
{
public:
	explicit FramePacer(size_t maxFramesInFlight)
		: m_MaxFramesInFlight(maxFramesInFlight)
	{
	}

	void BeginFrame(uint32_t frame)
	{
		while (m_InFlight.size() >= m_MaxFramesInFlight)
		{
			std::printf("frame %u waits for frame %u\n", static_cast<unsigned>(frame), static_cast<unsigned>(m_InFlight.front()));
			m_InFlight.pop(); // the real device waits for the GPU's event query here
		}
	}

	void EndFrame(uint32_t frame) { m_InFlight.push(frame); }
private:
	size_t m_MaxFramesInFlight;
	std::queue<uint32_t> m_InFlight;
};

struct Message
{
	bool IsError = false;
	std::string Id;
};

// Errors count, a known false report is traced, everything else is a warning.
int Classify(const Message& message)
{
	if (message.IsError)
		return 2;
	return message.Id == "Loader Message" ? 0 : 1;
}

int main()
{
	const std::vector<Gpu> gpus = {
		{ "Old Card", GpuType::Discrete, 1, true, 4096 },
		{ "Laptop Integrated", GpuType::Integrated, 3, true, 16384 },
		{ "Big Discrete", GpuType::Discrete, 3, true, 8192 },
		{ "No Dynamic", GpuType::Discrete, 2, false, 24576 },
	};
	std::printf("chosen: %d\n", SelectGpu(gpus));

	FramePacer pacer(2);
	for (uint32_t frame = 0; frame < 4; frame++)
	{
		pacer.BeginFrame(frame);
		pacer.EndFrame(frame);
	}

	int errors = 0;
	const Message messages[] = { { true, "VUID-x" }, { false, "Loader Message" }, { false, "mvk-warn" } };
	for (const Message& message : messages)
		errors += Classify(message) == 2 ? 1 : 0;
	std::printf("errors counted: %d\n", errors);
	return 0;
}
