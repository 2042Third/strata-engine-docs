// A toy frame loop: the order of one frame, a skipped frame, the work time, the clamp and a frame-rate cap.
// The clock is simulated in whole milliseconds, so the output is the same on every machine.
#include <algorithm>
#include <cstdio>
#include <functional>
#include <mutex>
#include <thread>
#include <vector>

namespace
{
	long long s_Now = 0; // the simulated clock, in milliseconds

	std::mutex s_QueueMutex;
	std::vector<std::function<void()>> s_Queue;

	void SubmitToMainThread(std::function<void()> function)
	{
		std::scoped_lock lock(s_QueueMutex);
		s_Queue.push_back(std::move(function));
	}

	void DrainQueue()
	{
		std::vector<std::function<void()>> queue;
		{
			std::scoped_lock lock(s_QueueMutex);
			queue.swap(s_Queue);
		}
		for (std::function<void()>& function : queue)
			function();
	}
}

int main()
{
	constexpr long long c_Period = 20;   // the frame-rate cap: 50 frames per second
	constexpr long long c_MaxStep = 250; // the clamp of the step
	constexpr int c_MaxFrames = 6;

	std::thread worker([] { SubmitToMainThread([] { std::printf("         queue: a worker's result runs on the main thread\n"); }); });
	worker.join(); // here the worker posts before the first frame, so the output never changes

	int framesRun = 0;
	long long lastTurn = s_Now;
	long long nextSlot = 0;
	bool scheduled = false;
	for (int turn = 1; framesRun < c_MaxFrames; turn++)
	{
		const long long turnStart = s_Now;
		const long long step = std::min(turnStart - lastTurn, c_MaxStep);
		lastTurn = turnStart;
		DrainQueue();
		if (turn == 3) // the input stage learns that the window is minimized
		{
			s_Now += 16;
			std::printf("turn %d at %3lld ms: minimized, slept 16 ms, not counted\n", turn, turnStart);
		}
		else
		{
			const long long wait = 3;               // begin: wait for the GPU's earlier frame
			const long long work = turn == 4 ? 30 : 5; // update and UI (turn 4 is a slow frame)
			s_Now += wait + work;
			const long long workTime = s_Now - turnStart - wait;
			s_Now += 1;                             // end: present the image
			if (turn == 6)
				s_Now += 400; // a breakpoint holds the program
			framesRun++;
			std::printf("turn %d at %3lld ms: step %3lld ms, work %2lld ms, frame %d\n", turn, turnStart, step, workTime, framesRun);
		}
		if (framesRun == c_MaxFrames)
			break;
		// The pacer: the next slot is one period after the last one, or now when that slot has passed.
		nextSlot = scheduled ? std::max(nextSlot + c_Period, s_Now) : s_Now + c_Period;
		scheduled = true;
		s_Now = std::max(s_Now, nextSlot);
	}
	return 0;
}
