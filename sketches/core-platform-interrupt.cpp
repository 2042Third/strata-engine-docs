// A toy interrupt: the handler only counts, and the loop honours the request after its frame.
#include <atomic>
#include <csignal>
#include <cstdint>
#include <cstdio>

namespace
{
	constexpr int c_InterruptedExitCode = 130;

	// Lock-free, so that a signal handler may touch it.
	std::atomic<uint32_t> s_InterruptRequests = 0;
	static_assert(std::atomic<uint32_t>::is_always_lock_free);

	void OnInterruptSignal(int)
	{
		s_InterruptRequests.fetch_add(1);
	}
}

int main()
{
	std::signal(SIGINT, OnInterruptSignal);

	int exitCode = 0;
	for (int frame = 0; frame < 6; frame++)
	{
		std::printf("frame %d begins\n", frame);
		if (frame == 2)
		{
			std::printf("  Ctrl+C arrives in the middle of frame 2\n");
			std::raise(SIGINT);
		}
		std::printf("frame %d ends\n", frame);

		if (s_InterruptRequests.load() > 0)
		{
			std::printf("Interrupted: closing\n");
			exitCode = c_InterruptedExitCode;
			break;
		}
	}

	std::printf("the layers shut down in order\n");
	std::printf("exit code %d\n", exitCode);
	return 0;
}
