---
id: core/jobs
title: "Threads and the job system"
description: "How Strata runs slow work on other threads without making the frame wait, who owns what across threads, and why parallel work gives the same result."
kind: internals
size: L
tracks: [E]
needs: [core/frame-loop, basics/threads]
time: 105
learn:
  - id: choose-pool
    text: choose the pool and the priority for a piece of work, and say which thread runs it
  - id: safe-wait
    text: explain why a thread that waits for a job cannot deadlock the pool, and why it never runs other jobs
  - id: parallel-for
    text: predict how ParallelFor splits a range into batches and who runs each one
  - id: same-result
    text: explain how jobs that write only their own records keep a result the same on any number of threads
  - id: hand-off
    text: trace how a result travels from another thread to the main thread
since: 0.3.0
status: final
---

A frame lasts a few milliseconds, and much of what an engine does takes far longer: reading a big file, compressing a texture, writing a scene to disk. The job system is how Strata runs such work on other threads, so that a frame never waits for what it does not need. It owns three pools of threads, a call that queues a piece of work, a call that waits for it safely, a call that splits a loop across threads, and one hand-off that never waits. It does not decide what work to do, and it leaves the scene to the :term[main thread]{id=main-thread}, which owns it. Strata has no work stealing, no fibers and no task graph of the frame.

This page needs no project and no download. Its sketches are whole programs for the compiler of [How a C++ program is built](../basics/build.md#open-a-terminal-that-finds-a-compiler). Its test commands and its trace need the source build of [your first engine change](first-change.md#build-the-engine-and-start-the-editor), in `Debug`.

## The problem and how engines solve it

A game at 60 :term[frames per second]{id=frame-rate} has 16.7 ms for each frame. Compressing one 4096 by 4096 texture for the :term[graphics card]{id=gpu} takes seconds. If the main thread did that work, the editor would freeze for those seconds, so the work moves to other threads. The frame must also not wait for it. A job that finishes in the next second is no problem; a frame that stops to ask whether it finished is one.

Starting a new thread for each piece of work costs too much when the pieces number in the thousands. Every engine therefore keeps a **thread pool**: a fixed set of threads that take pieces of work, called jobs, from a queue. The :term[primer]{id=primer} on [threads, atomics and races](../basics/threads.md) shows the smallest pool. A real engine must answer more questions, and each answer has a price.

### What a pool can look like

One shared queue is the simplest form. Every thread takes the next job from the same queue under one lock. The price is a crowd at the lock when many threads take short jobs. **Priorities** add several queues: threads empty the first before they look at the second, so urgent work overtakes work that can wait.

A **task graph** lets each job name the jobs it needs first. The system sees the whole frame as a graph and runs every job whose inputs are done. It can fill the processors well, but every system must describe its dependencies, and the description must stay true as the code changes.

**Work stealing** gives each thread a queue of its own. A thread that runs out of work takes jobs from the end of another thread's queue. Locks become rare and data stays near the thread that made it. The scheme is harder to write and to reason about.

**Fibers** are light stacks that a program switches between by itself, without the :term[operating system]{id=operating-system}. A job on a fiber can wait for another job by switching to a third one, so no thread sits idle. Naughty Dog described an engine built this way in a conference talk of 2015. The price is that every library a job calls must survive the job changing threads.

Reading a file adds a different problem. A thread that reads from a disk sleeps until the data arrives, and a sleeping thread does no work. If every thread of a pool sleeps on a file, the processing behind it waits for nothing. Many engines give blocking reads a pool of their own.

### A worked number: why long work has its own pool

The editor imports a project's textures in the background. Suppose a machine has 24 :term[hardware threads]{id=hardware-thread} and the pool for long work uses all of them, each compressing a texture for seconds. The main thread, the graphics driver's threads and the frame's helpers now share the processors evenly with 24 busy threads. A thread of the frame that wakes up for a little work may wait a whole time slice for a processor. By Strata's own estimate, the editor's frames of about 3 ms would stretch to between 10 and 30 ms while an import ran.

Lowering the priority of the long-work threads helped, but did not fix it. With all 24 processors busy, the driver's thread of normal priority still waited, and frames took between 5 and 27 ms. What fixed it was leaving four hardware threads without long work: those frames took between 2.0 and 2.8 ms. Strata therefore gives long work its own pool, at a lower priority, with fewer threads than processors.

### Who may touch the world

The second question is which thread may change the game's state. One answer lets every system run on its own thread, with locks around the data they share. The other lets one thread own the changing state while the others compute and report. Strata takes the second answer: the main thread owns the scene, the input, the scripts and the submission of drawing. Other threads read what they were given, compute, and return a result through a queue that the main thread polls, or through `Application::SubmitToMainThread`.

The choice costs latency: a result waits until the main thread reaches the queue, up to one frame. It buys a scene that changes only at known points of a frame, with no lock around it and no race that shows once in a thousand runs. At the start of each turn of the :term[frame loop]{id=game-loop}, the main thread runs the queue. [The frame loop](frame-loop.md) shows where.

## The three pools and the threads of the editor

Strata keeps three pools, and the call that submits a job decides which one runs it. The picture shows who submits to which.

```mermaid caption="Three pools with their queues. Work for the frame goes to the workers, blocking reads to the I/O threads, and long work to the background threads." alt="A diagram with three rows. Frame work such as drawing preparation, transform updates and physics tasks goes to the worker pool. Asset reads, saves and searches go to the I/O pool. Imports, exports and scene reads go to the background pool, which runs below normal priority."
flowchart LR
	frame["frame work: extraction, transforms, physics tasks"] -->|"Submit, ParallelFor"| workers["Worker pool: hardware threads minus 1, normal priority"]
	reads["asset reads, saves, searches"] -->|"SubmitIO"| io["I/O pool: 2 threads, normal priority"]
	long["imports, exports, scene reads"] -->|"JobPriority::Background"| background["Background pool: below normal priority"]
	workers -. "work that background jobs start" .-> background
```

The **worker threads** run frame work: the :term[renderer's]{id=renderer} extraction of what to draw, the update of world transforms and the tasks of the physics library box3d. A frame that waits for such work continues only when the worker has the processor again, so workers run at the priority of the main thread. The **I/O threads**, two by default, run jobs that block on files and searches. The **background threads** run long work that no frame waits for, below normal priority.

Each pool has a default size that depends on the hardware threads of the machine. The workers number one fewer than the hardware threads, but at least one. The background pool has the larger of two numbers, half the hardware threads and all but four, and never more than the workers.

| Hardware threads | Workers | Background threads | Hardware threads without background work |
| --- | --- | --- | --- |
| 4 | 3 | 2 | 2 |
| 8 | 7 | 4 | 4 |
| 16 | 15 | 12 | 4 |
| 24 | 23 | 20 | 4 |

The last column is the point: from eight hardware threads on, four stay free for the main thread, the graphics driver and the frame's helpers. The editor uses these defaults, and the tests start pools of chosen sizes. `StrataRuntime`, which plays exported games, starts two background threads, because a game's only long work is releasing a scene.

The editor's process has more threads than the pools. Watcher threads scan folders for changes, a remote :term[function call]{id=function-call} (RPC) server reads the sockets of outside commands, the audio library mixes sound, and one thread writes the log. Each hands its results to the main thread by a queue that the main thread polls.

```mermaid caption="Each other thread of the editor ends in a queue that the main thread reads at a fixed point of its frame." alt="A diagram. Job threads feed a completion queue, file watchers a change queue, the network thread a request queue, and any thread a main-thread queue. The main thread reads all four queues. The audio thread reads one value from the main thread through a sequence lock."
flowchart LR
	jobs["job threads"] --> completions["completion queue of the asset manager"]
	watchers["file watcher threads"] --> changes["change queue"]
	network["RPC network thread"] --> requests["request queue"]
	any["any thread"] --> queue["SubmitToMainThread queue"]
	completions --> main(("main thread"))
	changes --> main
	requests --> main
	queue --> main
	main -- "SequenceLockedValue" --> audio["audio thread"]
```

The audio thread is the exception, and its arrow points the other way. The mixer must never wait for the main thread, so the main thread publishes a value that the audio thread reads without a lock. The real code below shows that hand-off.

## The contract

The rules of the job system are few. Each has a reason, and a change must keep the reasons.

### Putting work on a pool

`JobSystem::Submit(job, priority)` queues a job on the worker pool. A job is any `std::function<void()>`. `JobSystem::SubmitIO(job, priority)` queues it on the I/O pool, or on the workers when the program asked for no I/O threads. Both return a **job handle**: a small object that shares the job's state, so that you can ask whether the job is complete or wait for it. A handle with nothing in it counts as complete.

`JobPriority` has four values: `High`, `Normal`, `Low` and `Background`. Each pool keeps three queues, for the first three values, and a thread takes from the first queue that holds a job. `Background` is different: `Submit` with it sends the job to the background pool, into its normal queue. `SubmitIO` with `Background` only queues the job last, like `Low`.

Work that background work starts stays in the background. If a background job calls `Submit` or `ParallelFor`, the new jobs go to the background pool too. The same holds for a thread that runs a background job it waited for. Without the rule, an import that splits its compression over the workers would take the processors from the frame.

`SubmitBackgroundPart(job)` serves one more case. A thread hands out pieces of work and waits for them, such as the chunks of a big scene file. Queued behind a hundred imports, the pieces would wait while the thread ran them one by one. `SubmitBackgroundPart` puts them in the first queue of the background pool, ahead of imports that have not started.

Two edges remain. Before `JobSystem::Init` and after `JobSystem::Shutdown`, a submit runs the job at once on the calling thread, so engine code never needs a special case for one thread. `Shutdown` stops the I/O pool first, then the background pool, then the workers, and each pool runs the jobs still queued. That order follows who hands work to whom.

### Waiting for a job

The pool's thread and a waiting thread may both want one job, and exactly one must run it. A **claim** is the act of taking a job by setting its flag with an atomic exchange. The thread that reads the old value false owns the job, and every later thread reads true and leaves it alone. The claim is one instruction, with no lock.

`JobSystem::Wait(handle)` first returns if the job is complete. Then it tries to claim the job. If it wins, nobody had started the job, and the waiting thread runs it on the spot. If it loses, a pool thread is running the job, and the waiter sleeps on a :term[condition variable]{id=condition-variable} until the job reports completion. `WaitAll` waits for a list of handles one after another.

Take a pool with one worker, and a job that submits a second job and waits for it. Without the claim, the worker would sleep for a job that only a worker can run, and the pool would :term[deadlock]{id=deadlock}. With it, the waiting job claims the second job and runs it. A job that waits can only wait for a job that is running, which makes progress, or one that nobody started, which the waiter runs.

A waiting thread never runs a different job. Picture a frame that waits for a small job while an import's long compression sits in the queue. If the frame took the long job, it would stop for seconds. The rule keeps a wait from becoming longer than the job waited for.

### Splitting a loop

Many jobs are a loop over many items, such as updating 100,000 transforms. `JobSystem::ParallelFor(count, minBatchSize, function)` serves them. It calls `function(begin, end)` for slices of the range from 0 to `count`. A **batch** is one such slice: the items from `begin` up to, but not including, `end`.

The batch size is `minBatchSize`, or 1 when it is 0, and the number of batches is the count divided by the batch size, rounded up. A call with one batch, or without a pool, runs everything on the calling thread. Otherwise the call queues helper jobs: one per pool thread at most, and at most one fewer than the batches.

**ParallelFor** is this call: it runs one function over a range in batches that the calling thread and its helpers take, and it returns only when every batch is done. An atomic counter hands out the batches. Each thread adds 1 to the counter and takes the batch whose number it got, until the numbers pass the last batch. The caller takes batches too, so a call on a busy pool still makes progress. Once every batch is taken, helpers that have not started are dropped: they complete without running.

:::example[One ParallelFor, with numbers]
Call `ParallelFor(1000, 64, ...)` on a pool of 7 workers. The batch size is 64, and 1000 divided by 64, rounded up, gives 16 batches. The last batch covers the items 960 to 999: 40 items, because the last slice stops at 1000. The call queues min(7, 15) = 7 helpers.

The caller and the helpers now race for the numbers 0 to 15. A thread that is slow, perhaps because another program took its processor, takes fewer batches. Suppose no worker is free. The caller takes all 16 batches, drops the helpers and returns without waiting for them. With a batch size of 1,000, the call would make one batch and run it on the calling thread, with no helper.
:::

### Failures, numbers and one lock-free value

Every job and every batch runs inside a `try` and `catch`. The engine's own code does not throw, but libraries may. A job that throws is logged and still completes, so a thread that waits for it is released.

`JobSystem::GetStats` returns, for each pool, the number of threads, the running and queued jobs, the completed jobs and the busy time of its threads. It does not stop the pool: each thread keeps its counters in a record that another thread can read while the owner writes. Subtract the busy times of two samples and divide by the time between them and by the thread count, and you have how busy the pool was. The editor's Performance panel shows these shares as workers, I/O and background percentages, and the frame profiler records them for every frame.

`SequenceLockedValue<T>` hands one value from one writer thread to one reader thread, and neither ever waits. The audio thread uses it for the listener's up direction.

### The rules that follow

:::rule[The main thread owns the scene; the rest hand results back]
The main thread owns the scene, the input, the scripts and the submission of drawing. Workers return results through `Application::SubmitToMainThread` or queues the main thread polls. A worker that touched the scene would race with the main thread, and no test finds such a race reliably. The rule stands in the engine's `AGENTS.md`, under "Architecture rules".
:::

:::why[Never block a frame on a long job]
A frame never waits for a job that may run long, and a waiting thread never runs other jobs. A frame that waited would take as long as the job; a waiter that ran other jobs would take as long as the longest one queued. The comments of `JobSystem.h` state the rule; `AGENTS.md` does not.
:::

The main thread's frame work also touches no file. A blocking read stalls the frame for as long as the disk takes, and no one controls that time. The engine counts the file operations of each thread (`FileSystem::GetThreadOperationCount`), and a test checks that the asset manager's `Update` adds none on the main thread. Reads go to the I/O pool by `SubmitIO`, and their results return by polling or `SubmitToMainThread`.

:::why[Long work goes to the background]
An import's texture compression and a pack's compression run at `JobPriority::Background`, because no frame needs their result soon. Frame work stays on the normal-priority workers. Long jobs on the workers would take the processors at the frame's priority, and frames of 3 ms would stretch to 10 to 30 ms. The engine's `Docs/Architecture.md` gives these numbers; `AGENTS.md` states no rule for this.
:::

:::why[What a job captures is released where it runs]
A job may hold the last reference to an object, such as a scene that `Scene::ReleaseInBackground` destroys away from the frame. The object must die on the thread that runs the job. A copy of the function left with the submitting thread would destroy it on the main thread, inside the frame. The real code below shows how `Submit` keeps the rule.
:::

## A toy version

The toy is a pool with one queue and a `Wait` that runs the job itself. It has no priorities, no `ParallelFor` and no statistics. Its point is the claim, so read `RunIfFirst` and `Wait` first: everything else feeds them.

```cpp sketch="core-jobs-toy.cpp"
// A toy job system: one queue, a few threads, and a Wait that runs the job itself when no thread has started it.
#include <atomic>
#include <condition_variable>
#include <cstdio>
#include <deque>
#include <functional>
#include <memory>
#include <mutex>
#include <thread>
#include <vector>

namespace
{
	struct Job
	{
		std::function<void()> Function;
		std::atomic<bool> Claimed = false;
		std::atomic<bool> Completed = false;
		std::mutex Mutex;
		std::condition_variable Condition;
	};

	using JobRef = std::shared_ptr<Job>;

	// Runs the job unless another thread claimed it first.
	void RunIfFirst(Job& job)
	{
		if (job.Claimed.exchange(true))
			return;
		job.Function();
		job.Function = nullptr;
		{
			std::scoped_lock lock(job.Mutex);
			job.Completed = true;
		}
		job.Condition.notify_all();
	}

	void Wait(const JobRef& job)
	{
		RunIfFirst(*job); // does nothing when a pool thread has the job
		std::unique_lock lock(job->Mutex);
		job->Condition.wait(lock, [&job]() { return job->Completed.load(); });
	}

	class Pool
	{
	public:
		explicit Pool(unsigned threadCount)
		{
			for (unsigned index = 0; index < threadCount; index++)
				m_Threads.emplace_back([this]() { ThreadMain(); });
		}

		~Pool()
		{
			{
				std::scoped_lock lock(m_Mutex);
				m_Stopping = true;
			}
			m_Condition.notify_all();
			for (std::thread& thread : m_Threads)
				thread.join();
		}

		JobRef Submit(std::function<void()> function)
		{
			auto job = std::make_shared<Job>();
			job->Function = std::move(function);
			{
				std::scoped_lock lock(m_Mutex);
				m_Queue.push_back(job);
			}
			m_Condition.notify_one();
			return job;
		}
	private:
		void ThreadMain()
		{
			while (true)
			{
				JobRef job;
				{
					std::unique_lock lock(m_Mutex);
					m_Condition.wait(lock, [this]() { return m_Stopping || !m_Queue.empty(); });
					if (m_Queue.empty())
						return;
					job = std::move(m_Queue.front());
					m_Queue.pop_front();
				}
				RunIfFirst(*job);
			}
		}
	private:
		std::mutex m_Mutex;
		std::condition_variable m_Condition;
		std::deque<JobRef> m_Queue;
		std::vector<std::thread> m_Threads;
		bool m_Stopping = false;
	};
}

int main()
{
	const std::thread::id mainThread = std::this_thread::get_id();
	Pool pool(1); // one thread: the case where a waiting job would deadlock a pool without the claim

	std::atomic<int> value = 0;
	const JobRef outer = pool.Submit([&]()
	{
		const JobRef inner = pool.Submit([&]() { value = 41; });
		Wait(inner);
		value++;
	});
	Wait(outer);
	std::printf("outer waited for inner: value is %d\n", value.load());

	std::atomic<bool> holding = false;
	std::atomic<bool> release = false;
	pool.Submit([&]()
	{
		holding = true;
		while (!release.load())
			std::this_thread::yield();
	});
	while (!holding.load())
		std::this_thread::yield();

	std::atomic<bool> ranHere = false;
	const JobRef quick = pool.Submit([&]() { ranHere = std::this_thread::get_id() == mainThread; });
	Wait(quick); // the only thread is busy, so the waiting thread runs the job
	std::printf("the job ran on the waiting thread: %s\n", ranHere.load() ? "yes" : "no");
	release = true;
	return 0;
}
```

1. **Line 28:** the claim: one atomic exchange, so exactly one thread runs the job.
2. **Lines 39-44:** `Wait` tries to run the job itself, then sleeps until some thread completed it.
3. **Lines 78-92:** a pool thread takes a job from the one queue and calls `RunIfFirst`, which skips jobs a waiter ran.
4. **Lines 109-115:** the deadlock case with one pool thread: the outer job waits for the inner job.

```text output-of="core-jobs-toy.cpp"
outer waited for inner: value is 42
the job ran on the waiting thread: yes
```

The first line of output shows the deadlock case. The pool has one thread, and the outer job waits for the inner job. The line appears because `Wait` claims the inner job while the only thread is busy with the outer one. The second part holds the only thread in a job that spins, so the waiting thread claims the quick job itself, and the job reports that it ran on the main thread.

## The real code: the claim, the pool, ParallelFor and the hand-off

The toy keeps one queue and one kind of job. The real pool adds three queues by priority, a drain when the pool stops, activity records, a flag for background work and a rule about what a job leaves behind. The code below follows a job from its claim to its end, then the pool's thread, then the loop, and last the :term[lock-free]{id=lock-free} value.

### The claim and the wait

A job is a `JobState` that holds its function, a flag for background work, the atomic flags `Claimed` and `Completed`, and a :term[mutex]{id=mutex} and condition variable for sleeping waiters. Two small functions run it.

```cpp src="Strata/src/Strata/Core/JobSystem.cpp#L33-L68"
void ExecuteJob(Detail::JobState& job)
{
	if (job.Background)
		t_BackgroundJobDepth++;
	try
	{
		job.Function();
	}
	catch (const std::exception& exception)
	{
		ST_CORE_ERROR("JobSystem: job threw an exception: {}", exception.what());
	}
	catch (...)
	{
		ST_CORE_ERROR("JobSystem: job threw an unknown exception");
	}
	if (job.Background)
		t_BackgroundJobDepth--;
	// What the job captured is released before anyone hears that it completed.
	job.Function = nullptr;

	{
		std::scoped_lock<std::mutex> lock(job.Mutex);
		job.Completed.store(true, std::memory_order_release);
	}
	job.Condition.notify_all();
}

// Runs the job unless another thread claimed it first. Returns whether it ran here.
bool TryRunJob(Detail::JobState& job)
{
	if (job.Claimed.exchange(true, std::memory_order_acq_rel))
		return false;
	ExecuteJob(job);
	return true;
}
```

1. **Line 35:** a background job raises a counter of the thread, so that what it submits stays in the background, also on a thread that only runs it while waiting.
2. **Lines 37-48:** the function runs inside `try` and `catch`. A throw is logged, and the code below still marks the job complete.
3. **Line 52:** the function is emptied before anyone hears of the completion, so what it captured is released here, on the thread that ran it.
4. **Lines 54-58:** `Completed` is set under the job's mutex, and then all waiters wake. The mutex closes the gap in which a waiter has checked the flag and not yet gone to sleep.
5. **Line 64:** the claim: one `exchange` that returns the old value. Only the thread that read `false` runs the job.

The wait is short, because the claim does the work.

```cpp src="Strata/src/Strata/Core/JobSystem.cpp#L502-L514"
void JobSystem::Wait(const JobHandle& handle)
{
	if (handle.IsComplete())
		return;

	// Nobody started it yet: run it here, which also keeps a job that waits for another from deadlocking the pool.
	Detail::JobState& state = *handle.m_State;
	if (TryRunJob(state))
		return;

	std::unique_lock<std::mutex> lock(state.Mutex);
	state.Condition.wait(lock, [&state]() { return state.Completed.load(std::memory_order_acquire); });
}
```

1. **Lines 504-505:** a complete job, or an empty handle, needs no wait.
2. **Lines 508-510:** the claim decides: a win means the job ran on this thread and is complete.
3. **Lines 512-513:** a loss means another thread runs the job, so the waiter sleeps until `Completed` is true. The predicate protects it from waking early.

### The pool's thread

A `JobPool` holds three queues, one mutex and one condition variable for all of them. The thread's loop is its heart.

```cpp src="Strata/src/Strata/Core/JobSystem.cpp#L274-L304"
void ThreadMain(ThreadActivity& activity)
{
	while (true)
	{
		JobRef job;
		{
			std::unique_lock<std::mutex> lock(m_Mutex);
			m_Condition.wait(lock, [this]()
			{
				if (m_Stopping)
					return true;
				for (const std::deque<JobRef>& queue : m_Queues)
				{
					if (!queue.empty())
						return true;
				}
				return false;
			});

			// When stopping, keep draining until every queue is empty.
			if (!PopLocked(job))
				return;
		}
		// A job that a waiting thread ran, or a dropped helper, is only taken off the queue.
		if (job->Claimed.exchange(true, std::memory_order_acq_rel))
			continue;
		activity.BeginJob(GetClockNanoseconds(std::chrono::steady_clock::now()));
		ExecuteJob(*job);
		activity.EndJob(GetClockNanoseconds(std::chrono::steady_clock::now()));
	}
}
```

1. **Lines 281-291:** the thread sleeps until the pool stops or some queue holds a job. One condition variable serves all three queues.
2. **Lines 293-295:** while stopping, a thread keeps draining and returns only when every queue is empty. That is the drain of `Shutdown`.
3. **Line 298:** a job that a waiter already claimed, or a dropped helper, is only taken off the queue. The claim makes this check safe without another lock.
4. **Lines 300-302:** the thread notes the job's start and end in its own activity record, for the statistics.

The queues are scanned in order, so a job in the `High` queue always goes before one in `Normal`. The pool has no aging: a steady stream of `High` jobs could starve `Low` ones.

### ParallelFor

The state of one `ParallelFor` is shared. Helpers hold it through a `Ref`, so a helper that starts after the call returned finds no batch left and ends without touching the function.

```cpp src="Strata/src/Strata/Core/JobSystem.cpp#L371-L401"
void RunBatches(ParallelForState& state)
{
	while (true)
	{
		const uint32_t batch = state.NextBatch.fetch_add(1, std::memory_order_relaxed);
		if (batch >= state.BatchCount)
			return;

		const uint32_t begin = batch * state.BatchSize;
		const uint32_t end = std::min(begin + state.BatchSize, state.Count);
		try
		{
			(*state.Function)(begin, end);
		}
		catch (const std::exception& exception)
		{
			ST_CORE_ERROR("JobSystem: a ParallelFor batch threw an exception: {}", exception.what());
		}
		catch (...)
		{
			ST_CORE_ERROR("JobSystem: a ParallelFor batch threw an unknown exception");
		}

		// The function is not touched after the last batch is counted: the call may return from then on.
		if (state.FinishedBatches.fetch_add(1, std::memory_order_acq_rel) + 1 == state.BatchCount)
		{
			std::scoped_lock<std::mutex> lock(state.Mutex);
			state.Condition.notify_all();
		}
	}
}
```

1. **Line 375:** the batch number comes from `fetch_add`. Two threads never get the same number, and `relaxed` is enough because the numbers carry no data.
2. **Lines 379-380:** the range of the batch follows from the number, and the last batch ends at `Count`.
3. **Lines 381-392:** a throw is contained for the batch; the loop continues with the next one.
4. **Lines 395-399:** the thread that counts the last finished batch wakes the caller. After this the call may return, so nobody touches the function again.

The call itself sets the state up, queues helpers, joins in and waits.

```cpp src="Strata/src/Strata/Core/JobSystem.cpp#L522-L566"
void JobSystem::ParallelFor(uint32_t count, uint32_t minBatchSize, const std::function<void(uint32_t begin, uint32_t end)>& function,
	JobPriority helperPriority)
{
	if (count == 0)
		return;

	const uint32_t batchSize = minBatchSize > 0 ? minBatchSize : 1;
	const uint32_t batchCount = (count + batchSize - 1) / batchSize;
	JobSystemData* data = s_Data.load();
	if (!data || batchCount == 1)
	{
		function(0, count);
		return;
	}

	const bool background = helperPriority == JobPriority::Background || IsInBackgroundWork();
	JobPool& pool = background ? data->Background : data->Workers;
	// Helpers of work in progress go before work that has not started.
	const JobPriority queuePriority = background ? JobPriority::High : helperPriority;

	auto state = CreateRef<ParallelForState>();
	state->Function = &function;
	state->Count = count;
	state->BatchSize = batchSize;
	state->BatchCount = batchCount;

	const uint32_t helperCount = std::min(pool.GetThreadCount(), batchCount - 1);
	std::vector<JobRef> helpers;
	helpers.reserve(helperCount);
	for (uint32_t index = 0; index < helperCount; index++)
	{
		JobRef helper = MakeJob([state]() { RunBatches(*state); }, background);
		pool.Push(helper, queuePriority);
		helpers.push_back(std::move(helper));
	}

	RunBatches(*state);

	// Every batch is taken: helpers that have not started would find nothing to do.
	for (const JobRef& helper : helpers)
		DropJob(*helper);

	std::unique_lock<std::mutex> lock(state->Mutex);
	state->Condition.wait(lock, [&state]() { return state->FinishedBatches.load(std::memory_order_acquire) == state->BatchCount; });
}
```

1. **Lines 531-535:** one batch, or no pool, runs inline. A loop of 10 items costs a :term[function call]{id=function-call}, not a hand-off.
2. **Lines 537-540:** background work uses the background pool and its first queue, so helpers of work in progress go before work that has not started.
3. **Lines 548-556:** at most one helper per pool thread and one fewer than the batches, because the caller takes batches too.
4. **Lines 558-562:** the caller runs batches, then drops every helper that has not been claimed. A dropped helper completes without running, and a pool thread that pops it only skips it.
5. **Lines 564-565:** the caller waits until the finished count equals the batch count. Only batches that helpers are running keep it waiting.

### The emptied function

The last rule of the contract has a short implementation and a long reason.

```cpp src="Strata/src/Strata/Core/JobSystem.cpp#L335-L342"
// Empties a std::function that was moved into a job, before the job can run. Moving one need not leave it empty:
// libc++ copies a callable that fits its small buffer. What the job captured must be released where the job runs
// (a job may hold the last reference to a scene it destroys off the frame, Scene::ReleaseInBackground), not by a copy
// that the submitting thread lets go of after the job ran.
void ReleaseMovedFunction(std::function<void()>& function)
{
	function = nullptr;
}
```

The standard does not say that a moved `std::function` is empty. The library `libc++` copies a small function when it moves it, so the parameter of `Submit` may still hold a copy of what the job captured. Here is how `Submit` uses the helper.

```cpp src="Strata/src/Strata/Core/JobSystem.cpp#L460-L474"
JobHandle JobSystem::Submit(std::function<void()> job, JobPriority priority)
{
	JobSystemData* data = s_Data.load();
	if (!data)
		return RunInline(job);

	const bool background = priority == JobPriority::Background || IsInBackgroundWork();
	JobRef state = MakeJob(std::move(job), background);
	ReleaseMovedFunction(job);
	if (background)
		data->Background.Push(state, priority == JobPriority::Background ? JobPriority::Normal : priority);
	else
		data->Workers.Push(state, priority);
	return JobHandle(std::move(state));
}
```

1. **Lines 466-468:** the job is made by moving the function in, and the leftover in the parameter is emptied before the job can run on any thread.
2. **Lines 469-472:** a background job goes to the background pool, in the normal queue; the others go to the workers, in the queue of their priority.

### The sequence lock

Most hand-offs between threads use a queue with a mutex. The audio thread cannot: a mixer that waits for a lock may miss its deadline, and the listener hears a click. A **sequence lock** lets a writer publish a value without ever waiting, and lets a reader take the latest whole value or nothing. A counter that the writer makes odd during a write tells the reader whether what it read belongs together.

```cpp src="Strata/src/Strata/Core/SequenceLock.h#L19-L59"
template<typename T>
class SequenceLockedValue
{
	static_assert(std::is_trivially_copyable_v<T>, "SequenceLockedValue copies values bytewise");
public:
	// Writer thread.
	void Publish(const T& value)
	{
		std::array<uint32_t, c_WordCount> words {};
		std::memcpy(words.data(), &value, sizeof(T));

		const uint64_t sequence = m_Sequence.load(std::memory_order_relaxed);
		m_Sequence.store(sequence + 1, std::memory_order_relaxed);
		// The odd sequence becomes visible before any word of the new value.
		std::atomic_thread_fence(std::memory_order_release);
		for (size_t index = 0; index < c_WordCount; index++)
			m_Words[index].store(words[index], std::memory_order_relaxed);
		m_Sequence.store(sequence + 2, std::memory_order_release);
	}

	// Reader thread: the latest value, if one was published since the last value taken and none is being written.
	bool TakeNew(T& outValue)
	{
		const uint64_t sequence = m_Sequence.load(std::memory_order_acquire);
		if (sequence == m_TakenSequence || (sequence & 1u) != 0)
			return false;

		std::array<uint32_t, c_WordCount> words;
		for (size_t index = 0; index < c_WordCount; index++)
			words[index] = m_Words[index].load(std::memory_order_relaxed);
		// The words are read before the sequence is checked again.
		std::atomic_thread_fence(std::memory_order_acquire);
		if (m_Sequence.load(std::memory_order_relaxed) != sequence)
			return false; // Rewritten meanwhile

		// T is trivially copyable (asserted above), so copying its bytes is valid even when it has default member
		// initializers; the void* tells GCC so (-Wclass-memaccess).
		std::memcpy(static_cast<void*>(&outValue), words.data(), sizeof(T));
		m_TakenSequence = sequence;
		return true;
	}
```

1. **Lines 27-28:** the value is copied into words first, so the time between the two counter changes is only a few stores.
2. **Lines 30-33:** the counter becomes odd, and the fence makes that visible before any new word.
3. **Lines 34-36:** the words are stored, and then the counter becomes even again with a release store, so a reader that sees the even number also sees the words.
4. **Lines 42-44:** the reader returns at once when nothing new was published or the counter is odd. It never waits; it asks again in its next turn.
5. **Lines 46-52:** the reader copies the words, fences, and checks the counter again. A changed counter means a write ran meanwhile, so the copy is thrown away.

The words are atomic and relaxed, so reading them during a write is no :term[data race]{id=data-race} in the sense of the language. The counter tells the truth, not the words. The pool's own `ThreadActivity` record works the same way: each pool thread writes its busy time and job count, and `GetStats` reads them from another thread without stopping anything.

## Parallel work that stays deterministic

Running a loop on several threads brings a new risk: the answer may change with the number of threads. Floating-point addition shows it. A 32-bit float holds :term[integers]{id=integer} exactly up to 16,777,216. Add 1 to 16,777,216 and the result rounds back to 16,777,216. So (16,777,216 + 1) + 1 gives 16,777,216, but 16,777,216 + (1 + 1) gives 16,777,218.

Now sum these three numbers with a parallel loop. One thread adds them from left to right. Two threads may add 1 + 1 first, and then add the result to the big number. The sums differ by 2, and which one you get depends on the number of threads and on when they run. A game that records a replay or compares two builds cannot accept that.

Strata's rule has three parts. Jobs write only their own records: each job reads shared data but writes into a slot that no other job writes. The cut of the work into chunks depends on the data and on fixed constants, never on the number of threads. Everything that merges, orders or changes the scene happens afterwards, on the main thread, in a fixed order. Then the threads change only how fast the answer arrives, not the answer.

Three places keep the rule. The animation system evaluates animators with `ParallelFor` in batches of 8. Each job writes only its animator's record, and the main thread applies root motion, attachments and events animator by animator. The physics world builds the shapes of new bodies in jobs of 512 owners each, when a round has at least 256 owners. The main thread then creates the bodies in record order, so body numbers and the simulation do not depend on the threads.

The scene writer cuts entities into chunks of 4,096 and converts them in parallel. A job of its own writes the chunks in order, so the :term[bytes]{id=byte} of a file never depend on the thread count.

:::why[Why the result must not depend on the threads]
Strata could let jobs combine results as they finish, which is a little faster. It does not, because a result that depends on timing cannot be tested: a failure shows once in a hundred runs, on one machine. With fixed chunks and an ordered publish, a test runs the same work with one, two and eight threads and compares the bytes. The cost is real: the ordered publish runs on one thread, jobs need records of their own, and some results wait for the slowest chunk.
:::

## Alternatives Strata did not choose

The engine's `Docs/Roadmap.md` lists `JobSystem v2 with work stealing and a frame task graph` under later work, so the choices below are open, not forbidden.

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Work stealing, one queue per thread | Intel's Threading Building Blocks library and the Rayon library for Rust | Fewer collisions at the queue with many threads, and data that stays near its thread | Simple priorities: with queues per thread, "all High jobs first" needs more machinery |
| Fibers | The engine of the 2015 Naughty Dog talk | A job could wait without blocking a thread, so the waiter rule would not be needed | Every library a job calls must survive a change of thread, and debuggers show less |
| A task graph of the frame | Unreal Engine's task graph | The engine sees all dependencies and could run a whole frame in parallel | Every system must declare its dependencies, and the main thread's ownership of the scene would change |

## How it is tested

The suite `Core.JobSystem` holds a test for each rule. It starts its own pools with chosen sizes, for example one worker and no I/O threads, so a situation that is rare on a real machine happens every time. One test makes a job wait for another on a single worker. Another holds the only worker, queues a long job and a short one, and checks that the waiter ran the short one itself and never the long one. Others check that `ParallelFor` covers every index exactly once, contains a throwing batch, and runs no other queued job on the calling thread.

More tests check that the background pool leaves hardware threads to the frame, that workers and I/O threads run at normal priority and background threads below it, and that `Shutdown` runs every queued job. The test of the captured reference checks that a job holding the last reference to an object sees a count of 1. `Core.SequenceLock` passes two million samples between two threads and counts the torn ones.

The :term[deterministic]{id=determinism} parts are tested in their own suites, which run the same work with different thread counts and compare the results. Two examples are `Animators evaluate the same with any number of threads` and `The bytes do not depend on the thread count or the chunk size, and are hashed as written`.

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Core.JobSystem
```

The command runs only the tests of the job system, in the folder of your source build.

## Changing it safely

The extension points are the call sites, not the pools: new work picks a pool and a priority, and a new loop picks a batch size. A change inside `JobSystem.cpp` needs more care, because each rule above guards a measured failure.

- Choose the pool by what the work does: frame work on `Submit`, a blocking read or a search on `SubmitIO`, long work that no frame needs soon at `JobPriority::Background`.
- Keep a batch much costlier than the atomic counter, and keep many more batches than threads. The animation system uses 8 items because one animator's evaluation costs a lot.
- Never make `Wait` run a job it was not asked to wait for, and never call it on the main thread for a job that may run long. Keep the handle and poll it in a later frame.
- Never add a :term[callback]{id=callback} that touches engine state from a worker. Add a queue that the main thread polls, or call `SubmitToMainThread`.
- In a parallel job, write only your own record, publish in order, and add a test that compares the results of different thread counts bit for bit.

Run `Core.JobSystem`, `Core.SequenceLock` and the deterministic tests before a commit. A change to the sizes or priorities of the pools also needs the editor open on a project that imports textures, with the frame profiler recording. The failures it guards against appear in :term[frame times]{id=frame-time}, not in unit tests.

## What went wrong before

Three failures shaped the code. The first was the background pool. Below normal priority, a pool as large as the processors still stalled frames. The graphics driver's thread waited for a processor, and the editor's frames took between 5 and 27 ms while an import compressed a texture. The fix was `c_FrameHardwareThreads`, four hardware threads left to the frame, and the test `The background threads leave hardware threads to the frame` holds the table of sizes.

The second was the chunks of a scene read. They queued behind the imports and ran one at a time on the reading thread, so a scene of a million entities took 7 s instead of 1.3 s. `SubmitBackgroundPart` puts such pieces ahead of the imports. The test `Parts of background work in progress run on the background threads before background work that has not started` keeps it.

The third was a copy. A `std::function` moved into a job was not always empty, and its copy kept a reference to a scene until `Submit` returned, so the scene could die in the frame. `ReleaseMovedFunction` empties it. The test `Nothing of a submitted job stays behind in Submit: what it captured is released where it runs` fails without it.

## Summary

- A job goes to the pool its call names: `Submit` to the workers, `SubmitIO` to the I/O threads, `JobPriority::Background` to the background threads. Those run below normal priority and leave four hardware threads to the frame.
- A thread that waits claims the job with an atomic exchange and runs it if no thread has started it; it never runs another job, so waiting inside a job cannot deadlock the pool.
- `ParallelFor` cuts a range into batches that the caller and its helpers take with an atomic counter, and drops helpers that have not started once every batch is taken.
- Jobs write only their own records and the main thread publishes them in order, so a result is the same on any number of threads.
- Results return to the main thread through polled queues or `SubmitToMainThread`; a sequence lock hands one value to the audio thread without waiting.

## Check yourself

1. A machine has 8 hardware threads. How many workers and background threads does the editor start, and how many hardware threads does background work leave to the frame?

   :::answer{tests="choose-pool"}
   There are 7 workers (one fewer than the hardware threads) and 4 background threads (the larger of half of 8 and 8 minus 4). Four hardware threads stay free, so the main thread, the driver and the frame's helpers find processors while imports run.
   :::

2. A job on a pool with one worker submits another job and waits for it. Which statement is right? (a) It deadlocks, because the only worker is busy. (b) It works, because the waiting job claims the second job and runs it. (c) It works, because the waiting job runs the next job of the queue, whichever it is.

   :::answer{tests="safe-wait"}
   Option (b) is right. No thread has started the second job, so the claim by exchange succeeds for the waiter, which runs it. Option (a) describes a pool without the claim. Option (c) is wrong because a waiter never runs another job: that could keep it far longer than the job it waits for.
   :::

3. Call `ParallelFor(5000, 128, ...)` on a pool of 7 workers. How many batches are there, how many items has the last one, and how many helpers are queued?

   :::answer{tests="parallel-for"}
   5000 divided by 128, rounded up, gives 40 batches. The last one starts at 39 times 128 = 4992 and ends at 5000, so it holds 8 items. The call queues min(7, 39) = 7 helpers. Helpers that have not started when the caller has taken the last batch are dropped.
   :::

4. Two threads sum a list of floats, each taking half, and the main thread adds the two halves. Another run uses four threads. Why may the totals differ, and what does Strata do about it?

   :::answer{tests="same-result"}
   Float addition depends on the order, so a different cut of the list gives a different total. Strata cuts work by fixed chunk sizes and not by thread count, lets each job write only its own record, and merges the records in order on the main thread. The total then does not depend on the threads.
   :::

5. A job reads a file and wants the scene to use it. Name the pool it runs on, and say how the result reaches the scene.

   :::answer{tests="hand-off"}
   The read runs by `SubmitIO` on an I/O thread. It must not touch the scene. It puts its result into a polled queue or calls `Application::SubmitToMainThread`, and the main thread applies it at a known point of its frame.
   :::

## Exercises

1. **Basic.** `ParallelFor(10000, size, ...)` runs on a pool of 7 workers. Compute the number of batches, the items of the last batch and the helpers queued for the sizes 1, 64 and 4096. Say which size pays most for the atomic counter and which leaves threads idle.

   :::answer[Worked solution]{tests="parallel-for"}
   Size 1 gives 10,000 batches, a last batch of 1 item and 7 helpers. Size 64 gives 157 batches, a last one of 16 items (10000 minus 156 times 64), and 7 helpers. Size 4096 gives 3 batches, a last one of 1,808 items and 2 helpers, so at most 3 threads work and 5 stay idle. Size 1 pays the counter and a function call 10,000 times.
   :::

2. **Medium.** Trace it yourself. In `StrataTests/src/Core/JobSystemTests.cpp`, find the test in which a job waits for another job. Put breakpoints in `JobSystem::Wait` and `TryRunJob`, run it in a Debug build, and say which thread claims the inner job and why the test cannot hang.

   :::answer[Worked solution]{tests="safe-wait"}
   The test is `Jobs may wait on other jobs without deadlocking`. `JobSystem::Wait` in `Strata/src/Strata/Core/JobSystem.cpp` calls `TryRunJob`, whose `exchange` on `Claimed` returns false for the waiting worker, because no thread started the inner job. The worker runs it in place. The pool has one worker, so no other thread could.
   :::

3. **Medium.** Write a complete program with a `Submit` that stores a function in a job, runs the job on a thread, and joins that thread before it returns. The function captures a `shared_ptr` to an object that records the thread of its :term[destructor]{id=destructor}. Compare a `Submit` that copies the function with one that empties its parameter.

   :::answer[Worked solution]{tests="choose-pool" solution="sketches/core-jobs-last-ref.cpp"}
   The copy stays in the parameter until `Submit` returns, so the job sees 2 references and the main thread releases the last one. After `function = nullptr` the job sees 1 reference and the worker releases it.

   ```cpp sketch="core-jobs-last-ref.cpp"
   // Where is the last reference to what a job captured released? A Submit that keeps a copy of the function lets the
   // submitting thread release it; a Submit that empties the function leaves the release to the thread that ran the job.
   #include <cstdio>
   #include <functional>
   #include <memory>
   #include <thread>

   namespace
   {
   	std::thread::id s_ReleasedOn; // written by Probe's destructor

   	struct Probe
   	{
   		~Probe() { s_ReleasedOn = std::this_thread::get_id(); }
   	};

   	struct Job
   	{
   		std::function<void()> Function;
   	};

   	// Runs the job on a worker thread before it returns, as a free worker does with a short job.
   	void Submit(std::function<void()> function, bool emptyTheParameter)
   	{
   		auto job = std::make_shared<Job>();
   		if (emptyTheParameter)
   		{
   			job->Function = std::move(function);
   			function = nullptr; // a moved std::function need not be empty: say so
   		}
   		else
   			job->Function = function; // a copy stays in the parameter until Submit returns

   		std::thread worker([job]()
   		{
   			job->Function();
   			job->Function = nullptr; // the job lets go of its function when it ran
   		});
   		worker.join();
   	}

   	void Run(const char* name, bool emptyTheParameter)
   	{
   		long seen = 0;
   		Submit([probe = std::make_shared<Probe>(), &seen]() { seen = probe.use_count(); }, emptyTheParameter);
   		const bool onMain = s_ReleasedOn == std::this_thread::get_id();
   		std::printf("%s: the job saw %ld reference(s); the last one went on the %s thread\n", name, seen, onMain ? "submitting" : "worker");
   	}
   }

   int main()
   {
   	Run("copying", false);
   	Run("emptying", true);
   	return 0;
   }
   ```

   ```text output-of="core-jobs-last-ref.cpp"
   copying: the job saw 2 reference(s); the last one went on the submitting thread
   emptying: the job saw 1 reference(s); the last one went on the worker thread
   ```

   1. **Lines 26-32:** the two versions of `Submit`: the first moves and empties, the second leaves a copy in the parameter.
   2. **Line 39:** the join stands for a job that finishes before `Submit` returns, as a free worker finishes a short job.
   3. **Line 45:** the job reads the use count of its own capture.
   :::

4. **Hard.** Write a sequence lock for a :term[struct]{id=struct} of two integers, with one writer thread and one reader thread, and a test that publishes 200,000 samples whose second number is twice the first. Count the samples that break the rule, and print the last sample taken.

   :::answer[Worked solution]{tests="hand-off" solution="sketches/core-jobs-sequence.cpp"}
   The writer makes the counter odd, stores the words and makes it even. The reader returns nothing while the counter is odd, copies the words and checks the counter again. No sample is torn, and the reader takes the last one after the writer finishes.

   ```cpp sketch="core-jobs-sequence.cpp"
   // A sequence lock: one writer thread hands samples to one reader thread, and neither ever waits for the other.
   #include <atomic>
   #include <cstdint>
   #include <cstdio>
   #include <thread>

   namespace
   {
   	struct Sample
   	{
   		uint32_t Index = 0;
   		uint32_t Twice = 0; // always 2 * Index: a sample that mixes two writes breaks this
   	};

   	class Handoff
   	{
   	public:
   		// The writer thread.
   		void Publish(const Sample& value)
   		{
   			const uint64_t sequence = m_Sequence.load(std::memory_order_relaxed);
   			m_Sequence.store(sequence + 1, std::memory_order_relaxed); // odd: a write is running
   			std::atomic_thread_fence(std::memory_order_release);
   			m_Index.store(value.Index, std::memory_order_relaxed);
   			m_Twice.store(value.Twice, std::memory_order_relaxed);
   			m_Sequence.store(sequence + 2, std::memory_order_release); // even: the write is done
   		}

   		// The reader thread: false when nothing new was published or the writer is in the middle of a write.
   		bool TakeNew(Sample& outValue)
   		{
   			const uint64_t sequence = m_Sequence.load(std::memory_order_acquire);
   			if (sequence == m_Taken || (sequence & 1u) != 0)
   				return false;

   			Sample value;
   			value.Index = m_Index.load(std::memory_order_relaxed);
   			value.Twice = m_Twice.load(std::memory_order_relaxed);
   			std::atomic_thread_fence(std::memory_order_acquire);
   			if (m_Sequence.load(std::memory_order_relaxed) != sequence)
   				return false; // rewritten while it was read

   			outValue = value;
   			m_Taken = sequence;
   			return true;
   		}
   	private:
   		std::atomic<uint64_t> m_Sequence = 0;
   		std::atomic<uint32_t> m_Index = 0;
   		std::atomic<uint32_t> m_Twice = 0;
   		uint64_t m_Taken = 0; // the reader thread only
   	};
   }

   int main()
   {
   	constexpr uint32_t c_Count = 200000;
   	Handoff handoff;
   	std::atomic<bool> finished = false;
   	std::thread writer([&]()
   	{
   		for (uint32_t index = 1; index <= c_Count; index++)
   			handoff.Publish({ index, 2 * index });
   		finished = true;
   	});

   	uint32_t torn = 0;
   	uint32_t last = 0;
   	while (true)
   	{
   		const bool wasFinished = finished.load(); // read first: after the last write, one more take finds the last sample
   		Sample sample;
   		if (handoff.TakeNew(sample))
   		{
   			if (sample.Twice != 2 * sample.Index)
   				torn++;
   			last = sample.Index;
   		}
   		else if (wasFinished)
   			break;
   	}
   	writer.join();
   	std::printf("torn samples: %u\n", torn);
   	std::printf("last sample taken: %u\n", last);
   	return 0;
   }
   ```

   ```text output-of="core-jobs-sequence.cpp"
   torn samples: 0
   last sample taken: 200000
   ```

   1. **Lines 21-26:** the writer's odd counter, fence, words and even counter, in the order of the engine's code.
   2. **Lines 32-34:** the reader stops when nothing is new or a write is running.
   3. **Lines 39-40:** the fence and the second look at the counter reject a copy that a write overlapped.
   4. **Lines 71-79:** the reader reads the finished flag first, so that one more take after the last write finds the last sample.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Core/JobSystem.h` and `JobSystem.cpp`: `JobSystem`, `JobHandle`, `JobPriority`, `JobSystemSpecification`, `JobPoolStats`, `JobSystemStats`; in the `.cpp`, `ExecuteJob`, `TryRunJob`, `DropJob`, `ThreadActivity`, `JobPool` and `ParallelForState`.
- `Strata/src/Strata/Core/SequenceLock.h`: `SequenceLockedValue<T>`.
- `Strata/src/Strata/Core/Application.h`: `ApplicationSpecification::Jobs` and `SubmitToMainThread`.
- `Strata/src/Strata/Core/FileSystem.h`: `GetThreadOperationCount`.
- `StrataTests/src/Core/JobSystemTests.cpp` and `SequenceLockTests.cpp`: the suites `Core.JobSystem` and `Core.SequenceLock`.
- `StrataRuntime/src/RuntimeApplication.cpp`: the :term[runtime's]{id=runtime} two background threads.

## Further reading

- Jason Gregory, "Game Engine Architecture", the chapters on concurrency and parallel programming: job systems and thread models of engines; intermediate.
- Christian Gyrling, "Parallelizing the Naughty Dog Engine Using Fibers", GDC 2015: a job system on fibers, and what it costs; advanced.
- The documentation of Intel's oneTBB library, on its task scheduler: work stealing explained for one library; intermediate.
- Anthony Williams, "C++ Concurrency in Action": atomics, memory order and lock-free structures behind a sequence lock; advanced.
