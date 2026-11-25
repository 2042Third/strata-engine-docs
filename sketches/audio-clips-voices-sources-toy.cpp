// A toy voice: a cursor over frames that many voices share. The end is reported with the last frames, so a looping
// voice wraps inside one read.
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <memory>
#include <vector>

namespace
{

	struct Clip
	{
		std::vector<float> Frames; // One channel, to keep the numbers small
	};

	struct Voice
	{
		std::shared_ptr<const Clip> Shared;
		uint64_t Cursor = 0;
		bool Looping = false;
		bool Ended = false;

		// Copies up to frameCount frames into out and returns how many it wrote.
		uint64_t Read(float* out, uint64_t frameCount)
		{
			uint64_t written = 0;
			while (written < frameCount && !Ended)
			{
				const uint64_t available = Shared->Frames.size() - Cursor;
				if (available == 0)
				{
					if (Looping)
						Cursor = 0;
					else
						Ended = true;
					continue;
				}
				const uint64_t count = std::min(frameCount - written, available);
				std::copy_n(Shared->Frames.data() + Cursor, count, out + written);
				Cursor += count;
				written += count;
			}
			return written;
		}
	};

	void Print(const char* name, Voice& voice)
	{
		float period[4] = {};
		const uint64_t written = voice.Read(period, 4);
		std::printf("%s:", name);
		for (uint64_t i = 0; i < written; i++)
			std::printf(" %.0f", period[i]);
		std::printf(" | cursor %llu, ended %s\n", static_cast<unsigned long long>(voice.Cursor), voice.Ended ? "yes" : "no");
	}

}

int main()
{
	auto clip = std::make_shared<Clip>();
	for (int i = 0; i < 10; i++)
		clip->Frames.push_back(static_cast<float>(i));

	Voice a { clip, 0, false, false };
	Voice b { clip, 4, false, false };
	Voice c { clip, 7, true, false };
	std::printf("owners of the clip: %ld\n", clip.use_count());

	for (int period = 1; period <= 2; period++)
	{
		std::printf("period %d\n", period);
		Print("a", a);
		Print("b", b);
		Print("c", c);
	}
	return 0;
}
