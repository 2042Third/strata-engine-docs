// A toy crash guard: a call runs under a guard, a signal ends it, and Invoke returns false. The faults are raised by
// std::raise so that every run behaves the same; a real fault arrives the same way, from the processor.

#include <csetjmp>
#include <csignal>
#include <cstdio>
#include <initializer_list>

namespace
{

	struct GuardFrame
	{
		std::jmp_buf JumpBuffer;
		GuardFrame* Previous = nullptr;
		volatile std::sig_atomic_t Signal = 0;
	};

	GuardFrame* s_CurrentFrame = nullptr;

	void SignalHandler(int signal)
	{
		std::signal(signal, SignalHandler); // Windows resets the handler before it runs
		GuardFrame* frame = s_CurrentFrame;
		if (!frame)
		{
			std::signal(signal, SIG_DFL);
			std::raise(signal);
			return;
		}
		frame->Signal = signal;
		s_CurrentFrame = frame->Previous;
		std::longjmp(frame->JumpBuffer, 1);
	}

	struct Noisy
	{
		~Noisy() { std::printf("  destructor ran\n"); }
	};

	void Healthy() { std::printf("  healthy call\n"); }

	void Crashing()
	{
		const Noisy noisy;
		std::raise(SIGSEGV);
		std::printf("  never printed\n");
	}

	void Dividing() { std::raise(SIGFPE); }

	bool Invoke(void (*function)())
	{
		GuardFrame frame;
		frame.Previous = s_CurrentFrame;
		if (setjmp(frame.JumpBuffer) == 0)
		{
			s_CurrentFrame = &frame;
			function();
			s_CurrentFrame = frame.Previous;
			return true;
		}
		std::printf("  contained: %s\n", frame.Signal == SIGSEGV ? "memory fault" : "arithmetic fault");
		return false;
	}

	void Nested()
	{
		const bool inner = Invoke(Dividing);
		std::printf("  outer continues, inner returned %s\n", inner ? "true" : "false");
	}

}

int main()
{
	std::signal(SIGSEGV, SignalHandler);
	std::signal(SIGFPE, SignalHandler);

	for (void (*function)() : { Healthy, Crashing, Crashing, Nested })
		std::printf("returned %s\n", Invoke(function) ? "true" : "false");
	return 0;
}
