---
id: basics/threads
title: "Threads, atomics and races"
description: "Start threads, see why shared data loses counts, and guard it with mutexes, condition variables, atomics and memory order, or with one owner thread."
kind: primer
size: L
tracks: [B, E]
needs: [basics/computer, basics/cpp-generic]
time: 120
learn:
  - id: race
    text: predict what two threads leave in a number that both change without protection, and name a data race and a race condition
  - id: locks
    text: write code that guards shared data with a mutex and takes two locks without a deadlock
  - id: wait
    text: write a condition variable wait with a predicate that hands one value to another thread
  - id: atomics
    text: choose a mutex, an atomic or one owner thread for a counter, a flag, a claim and the data of a scene
  - id: order
    text: explain what a release store and an acquire load promise, and what a relaxed operation does not
status: final
---

::::test-out

1. Two threads each run `counter = counter + 1` on a shared `int` that holds 5. Both read the 5 before either one writes. What does `counter` hold at the end?

   :::answer{tests="race"}
   The answer is 6. Each thread reads 5, computes 6 and writes 6, so the second write replaces the first and one count is lost. Two additions should give 7.
   :::

2. Write one line that adds 1 to `std::atomic<int> hits` so that no count is lost when eight threads run it.

   :::answer{tests="atomics"}
   `hits.fetch_add(1);` does the read, the addition and the write as one step. The line `hits++` does the same.
   :::

3. Thread A locks `first` and then `second`. Thread B locks `second` and then `first`. What can go wrong, and what is one cure?

   :::answer{tests="locks"}
   Each thread can take its first lock and then wait forever for the other's, a deadlock. A cure is to take the locks in one order everywhere, or to take both at once with `std::scoped_lock both(first, second);`.
   :::

4. A thread must sleep until another thread sets `bool ready`. Which standard tool lets it sleep, and why do you test the flag in a predicate?

   :::answer{tests="wait"}
   A `std::condition_variable`. The predicate is checked before the thread sleeps, so a notice that came early is not lost, and again after each wake-up, so a wake-up with no notice does no harm.
   :::

5. Thread X writes `data = 7` and then `ready.store(true, std::memory_order_relaxed)`. Thread Y sees `ready` true and reads `data`. Can Y read the old value, and what change stops that?

   :::answer{tests="order"}
   Yes: a relaxed store promises nothing about the order of other writes. Store with `std::memory_order_release` and load with `std::memory_order_acquire`, and Y must see 7.
   :::

::::

## Why you will need this

A game plays sound, loads files, answers the network and draws, all in one second. Strata runs several lines of work at once for this, and every line can touch the same memory.

This page teaches the tools: threads, locks, waiting, atomics and memory order. It also shows the cheapest cure: data that only one thread touches. You need them in [Threads and the job system](../core/jobs.md), where Strata's workers run small pieces of work, and in [The audio engine](../audio/engine.md), which hands data to the thread that mixes sound. [The frame loop](../core/frame-loop.md) rests on the same rule: one thread owns the scene.

Only the Practice needs a project, which it names. Each sketch is a whole program: save it as `sketch.cpp` and compile it with C++20 in the terminal of [How a C++ program is built](build.md#open-a-terminal-that-finds-a-compiler). On Windows, run `cl /std:c++20 /EHsc sketch.cpp` and then `.\sketch.exe`. On Linux and macOS, run `c++ -std=c++20 sketch.cpp -o sketch` and then `./sketch`. Without a compiler, read each output and its notes.

## A thread is a line of work that shares memory

Picture a game that streams music while it draws. If one list of instructions did both, the music would pause whenever a frame took long. Two lists that run at the same time remove the problem.

A **thread** is one line of work inside a process: its own list of instructions and its own stack, with the same memory as every other thread of the process. The :term[operating system]{id=operating-system} gives each thread time on a core, as [How a computer runs a program](../basics/computer.md) describes.

Your program starts with one thread, the **main thread**, which runs `main`. Every other thread exists because code started it.

In C++ you start a thread with `std::thread` and a function, usually a :term[lambda]{id=lambda}. The next sketch starts one, lets it set a number, and waits for it.

```cpp sketch="basics-threads-start.cpp"
// A thread starts from a lambda and runs beside the main thread; join waits until it is done.
#include <iostream>
#include <thread>

int main()
{
	const std::thread::id mainId = std::this_thread::get_id();
	int result = 0;
	std::thread worker([&result, mainId]()
	{
		result = 6 * 7;
		std::cout << std::boolalpha << "worker is the main thread: " << (std::this_thread::get_id() == mainId) << '\n';
	});
	worker.join();
	std::cout << "result = " << result << '\n';
	std::cout << "main is the main thread: " << (std::this_thread::get_id() == mainId) << '\n';
	return 0;
}
```

```text output-of="basics-threads-start.cpp"
worker is the main thread: false
result = 42
main is the main thread: true
```

1. **Lines 9–13:** the thread starts to run as soon as it is built. The :term[lambda captures]{id=lambda-capture} `result` by reference, so both threads use one variable.
2. **Line 14:** `join` makes the main thread wait until the worker has finished. A running thread that is destroyed without `join` ends the whole program.
3. **Lines 12–16:** the two thread ids differ, so the lambda really ran on another thread.

**Parallelism** means several threads run at the same instant, each on its own core. Threads that share one core, each in its turn, are concurrent but not parallel. With 8 cores of one :term[hardware thread]{id=hardware-thread} each, 8 threads can run in parallel, and a ninth waits for a turn. The :term[central processing unit]{id=processor} (CPU) and the :term[graphics processing unit]{id=gpu} (GPU) are a larger case of the same idea: two processors with two lines of work. [How a GPU works and draws a frame](../gpu/how-a-gpu-frame-works.md) shows the second one.

Threads cost something: each needs a stack, and the system needs time to start it. A thread for a tiny piece of work costs more than the work, so the last section ends with pools.

## Two threads that add to one number lose counts

Shared memory makes threads cheap to connect, and it makes them dangerous. Take a counter that holds 5, and let two threads each add 1. You expect 7.

The line `counter = counter + 1` is three steps for the processor: read the number, add 1, write the result. The system may switch between threads after any step. The sketch below plays one such order by hand, in a single thread, so that its output never changes.

```cpp sketch="basics-threads-schedule.cpp"
// One order in which two threads can run "counter = counter + 1": each thread's line is three steps.
#include <iostream>

int main()
{
	int counter = 5;
	int registerA = counter;   // thread A reads 5
	int registerB = counter;   // thread B reads 5, before A has written
	registerA = registerA + 1; // thread A computes 6
	registerB = registerB + 1; // thread B computes 6
	counter = registerA;       // thread A writes 6
	counter = registerB;       // thread B writes 6 over it
	std::cout << "counter = " << counter << " after two increments of 5\n";
	return 0;
}
```

```text output-of="basics-threads-schedule.cpp"
counter = 6 after two increments of 5
```

1. **Lines 7–8:** both threads read 5 before either has written.
2. **Lines 11–12:** the second write replaces the first, so the count of thread A is lost and the counter holds 6.

```mermaid caption="Thread A and thread B both read 5 from the counter. Each writes 6, and the second write replaces the first." alt="A time line with three columns: thread A, the counter in memory and thread B. Both threads read 5, then A writes 6 and B writes 6."
sequenceDiagram
    participant A as Thread A
    participant M as Counter in memory
    participant B as Thread B
    A->>M: read 5
    B->>M: read 5
    A->>M: write 6
    B->>M: write 6
```

Real threads do this in earnest. The next program makes two threads add 1,000,000 times each, three ways: with an atomic that is read and written in two steps, with an atomic that adds in one step, and with a lock. Do not worry about the lock yet; the next section explains it.

```cpp sketch="basics-threads-race.cpp"
// Two threads add 1,000,000 times each: only a step that is one atomic operation, or a lock, loses nothing.
#include <atomic>
#include <iostream>
#include <mutex>
#include <thread>
template<typename Add>
void RunTwoThreads(Add add)
{
	std::thread a([&]() { for (int i = 0; i < 1000000; i++) add(); });
	std::thread b([&]() { for (int i = 0; i < 1000000; i++) add(); });
	a.join();
	b.join();
}

int main()
{
	std::atomic<int> split = 0, single = 0;
	std::mutex mutex;
	int guarded = 0;
	RunTwoThreads([&]() { split.store(split.load() + 1); });
	RunTwoThreads([&]() { single.fetch_add(1); });
	RunTwoThreads([&]() { std::scoped_lock lock(mutex); guarded++; });
	std::cout << std::boolalpha << "load then store lost counts: " << (split.load() < 2000000) << '\n';
	std::cout << "fetch_add: " << single.load() << "\nmutex: " << guarded << '\n';
}
```

```text output-of="basics-threads-race.cpp"
load then store lost counts: true
fetch_add: 2000000
mutex: 2000000
```

1. **Lines 6–13:** `RunTwoThreads` starts two threads that each call `add` 1,000,000 times, and then joins both.
2. **Line 20:** each addition reads and writes in two separate steps, so another thread can write in between and its count is lost.
3. **Lines 21–22:** `fetch_add` is one step, and the lock makes the whole addition one step for other threads that use the same lock. Both reach 2,000,000.

Now the two terms. A **data race** happens when two threads use the same memory at the same time, at least one of them writes, and nothing orders them. In C++ a data race is :term[undefined behavior]{id=undefined-behavior}: the language promises nothing, and the compiler may assume it never happens.

A **race condition** is the wider bug in which the result depends on which thread is first. The load and store version above has no data race, because every access is atomic, but it is a race condition, and it loses counts.

The plain `int` version is the dangerous one. On one test computer, two threads that added to a plain `int` 1,000,000 times each left about 1.1 million when built with `-O0`, which changes little in your code. Built with `-O2`, which works to make code fast, the same program printed exactly 2,000,000 every time, in a fraction of a millisecond. That is too fast for two million additions to memory, so the compiler most likely replaced the loop with one addition. The code was still wrong, and it only looked right.

:::note[Tests that pass]
A test that passes 1,000 times proves little. A race needs two threads to meet in a few nanoseconds, and a faster computer, another compiler or a busy machine changes the odds. Rely on rules that make races impossible, not on runs.
:::

## A mutex lets one thread at a time into a piece of code

The cure for a lost update is to make the three steps one step for everyone else. A **mutex**, short for mutual exclusion, is an object that only one thread can own at a time.

A **lock** is that ownership: a thread locks the mutex before it touches the shared data and unlocks it afterward. A thread that asks for a mutex that another thread owns waits until the owner unlocks.

:::analogy[A mutex is the key to a small room]
One key hangs by the door of a room. Whoever takes the key may use the room, and everyone else waits outside until the key is back.

**Where it breaks:** a person who keeps the key by mistake locks others out once, but code that forgets to unlock locks them out every time, so a :term[destructor]{id=destructor} hands the key back.
:::

Unlocking by hand is a step you can forget, especially on an early `return`. C++ uses resource acquisition is initialization (RAII), from [C++ memory](../basics/cpp-memory.md), here: a lock object locks in its :term[constructor]{id=constructor} and unlocks in its destructor. `std::lock_guard` guards one mutex, and `std::scoped_lock` guards one or several. The line `std::scoped_lock lock(mutex);` in the race sketch above is the whole pattern: the lock ends where its scope ends, on every path.

What does a lock cost? When no other thread holds the mutex, a lock and unlock take a few nanoseconds. On the test computer, a loop of 10 million locks took about 9 ns per round, against about 3.5 ns for an atomic addition. When another thread holds the mutex, the waiting thread sleeps and the system wakes it later, which takes microseconds. Two threads that add 1,000,000 times each took about 50 ms with a mutex and about 18 ms with `fetch_add`.

Keep the locked part short. While you hold a mutex, every other thread that needs it waits, so never read a file, wait for a network answer or sleep while you hold one.

Many threads that only read do not need to exclude one another. A `std::shared_mutex` has two kinds of lock. A shared lock (`std::shared_lock`) lets any number of readers in together, and an exclusive lock (`std::unique_lock`) admits one writer and no reader. The sketch fills a table under an exclusive lock and then reads it from four threads at once under shared locks.

```cpp sketch="basics-threads-locks.cpp"
#include <iostream>
#include <map>
#include <mutex>
#include <shared_mutex>
#include <thread>
#include <vector>
std::shared_mutex s_Mutex;
std::map<int, int> s_Values;

int main()
{
	{
		std::unique_lock lock(s_Mutex);
		for (int key = 0; key < 100; key++)
			s_Values[key] = key * 2;
	}
	std::vector<int> sums(4, 0);
	std::vector<std::thread> readers;
	for (int r = 0; r < 4; r++)
		readers.emplace_back([&sums, r]() { std::shared_lock lock(s_Mutex); for (int key = 0; key < 100; key++) sums[r] += s_Values.at(key); });
	for (std::thread& reader : readers)
		reader.join();
	std::cout << "sums: " << sums[0] << ' ' << sums[1] << ' ' << sums[2] << ' ' << sums[3] << '\n';
}
```

```text output-of="basics-threads-locks.cpp"
sums: 9900 9900 9900 9900
```

1. **Lines 12–16:** the writer holds the exclusive lock while it changes the map, so no reader sees half of the change.
2. **Line 20:** each of the four readers takes a shared lock, so all four read the map at the same time. Each sum is 9900, the total of the doubled keys 0 to 99.

A shared mutex pays off when reads are many and writes are rare.

## Two locks taken in two orders can deadlock

A mutex solves races and creates a new problem. Suppose thread A holds `first` and wants `second`, while thread B holds `second` and wants `first`. Neither can continue, because each waits for something that the other will never give back. A **deadlock** is this state: threads that wait for each other forever.

```mermaid caption="Thread A holds the first lock and waits for the second. Thread B holds the second lock and waits for the first. Neither can continue." alt="A time line with two threads. Thread A locks the first lock and thread B locks the second lock. Then A asks for the second and B asks for the first, and both wait."
sequenceDiagram
    participant A as Thread A
    participant B as Thread B
    A->>A: lock first
    B->>B: lock second
    A-->>B: wants second, waits
    B-->>A: wants first, waits
```

A deadlock hides on most runs and strikes on a bad one, so the next sketch forces it. A barrier makes both threads hold their first lock before either asks for the second. Instead of waiting forever, each thread then tries the other lock with a limit of 100 ms, so the program can report the deadlock and end.

```cpp sketch="basics-threads-deadlock.cpp"
#include <barrier>
#include <chrono>
#include <iostream>
#include <mutex>
#include <thread>

int main()
{
	std::timed_mutex first;
	std::timed_mutex second;
	std::barrier meet(2);
	bool gotSecond = true, gotFirst = true;
	auto take = [&](std::timed_mutex& mine, std::timed_mutex& other, bool& got)
	{
		std::scoped_lock lock(mine);
		meet.arrive_and_wait(); // both threads hold their own lock
		got = other.try_lock_for(std::chrono::milliseconds(100));
		meet.arrive_and_wait(); // neither lets go of its own lock before both have tried
	};
	std::thread a([&]() { take(first, second, gotSecond); });
	std::thread b([&]() { take(second, first, gotFirst); });
	a.join();
	b.join();
	std::cout << std::boolalpha << "A got the second lock: " << gotSecond << "\nB got the first lock: " << gotFirst << '\n';
}
```

```text output-of="basics-threads-deadlock.cpp"
A got the second lock: false
B got the first lock: false
```

1. **Lines 13–19:** each thread locks its own mutex, waits at the barrier until both threads hold one, and then tries the other mutex for at most 100 ms. It keeps its own until both have tried, so the run never depends on timing.
2. **Lines 20–21:** the two calls name the mutexes in opposite orders. That is the whole bug.

There are two reliable cures. The first is to hold one lock at a time: finish with the first mutex before you take the second, so no thread ever holds one lock while it waits for another. When you need two at once, the second cure is one order: every thread takes the locks in the same order, say always `first` before `second`. Then a thread that holds `second` has no reason to wait for `first`, because nobody holds `first` and waits for `second`.

C++ also offers `std::scoped_lock both(first, second);`, which takes several mutexes together in a way that cannot deadlock, whichever order the names have. A timeout, as in the sketch, does not cure anything. It only turns a hang into a report.

:::example[Find the order]
Three mutexes, `a`, `b` and `c`, guard three tables. Thread P needs `a` and `c`, thread Q needs `c` and `b`, and thread R needs `b` and `a`. Each one locks its first name before its second as written. Can they deadlock, and what order prevents it?

Work it by hand. P holds `a` and waits for `c`, Q holds `c` and waits for `b`, R holds `b` and waits for `a`. That is a circle, so yes. Order the mutexes `a`, `b`, `c` and let everyone lock the lower one first: P still takes `a` then `c`, Q takes `b` then `c`, and R takes `a` then `b`. A circle needs someone to hold a higher lock and wait for a lower one, and nobody does.
:::

Try it: thread S needs `c` and `a`. In which order does it lock them?

:::answer
First `a`, then `c`: the lower mutex in the order `a`, `b`, `c` comes first.
:::

## A condition variable lets a thread sleep until told

Often a thread has nothing to do until another thread produces something: a loaded file, a finished sum, a message. The thread could ask again and again in a loop, but that keeps a core busy for nothing. A **condition variable** lets a thread sleep until another thread tells it that something changed.

A condition variable always works with a mutex and with data that the mutex guards. The waiting thread locks the mutex and calls `wait`, which gives the mutex back while the thread sleeps and takes it again on waking. The other thread changes the data under the mutex and then calls `notify_one`, which wakes one waiter, or `notify_all`, which wakes every waiter.

```cpp sketch="basics-threads-condition.cpp"
#include <condition_variable>
#include <iostream>
#include <mutex>
#include <thread>

int main()
{
	std::mutex mutex;
	std::condition_variable ready;
	bool hasValue = false;
	int value = 0;
	std::thread worker([&]()
	{
		std::scoped_lock lock(mutex);
		value = 42;
		hasValue = true;
		ready.notify_one();
	});
	std::unique_lock lock(mutex);
	ready.wait(lock, [&]() { return hasValue; });
	std::cout << "received " << value << '\n';
	lock.unlock();
	worker.join();
}
```

```text output-of="basics-threads-condition.cpp"
received 42
```

1. **Lines 12–18:** the worker sets the value and the flag while it holds the mutex, and then notifies.
2. **Line 20:** `wait` takes a predicate, a lambda that says whether the thread may continue. It checks the predicate first, so a notice that came before the wait started is not lost, and it sleeps only while the predicate is false.
3. **Line 22:** the main thread gives the mutex back before it joins the worker.

The predicate matters for a second reason. The system may wake a waiting thread with no notice at all. Without a predicate the thread would continue with no value. With one, the thread checks the flag again, finds it false and sleeps again. Treat a wake-up as a hint to look, never as proof that the data changed.

Sometimes a thread must not wait forever. `wait_until` takes a time and `wait_for` takes a length of time. Both return the predicate's value when they end, so false means that the time ran out.

```cpp sketch="basics-threads-until.cpp"
// wait_until gives up at a time: nobody sets the flag, so the wait ends after 50 milliseconds with false.
#include <chrono>
#include <condition_variable>
#include <iostream>
#include <mutex>

int main()
{
	std::mutex mutex;
	std::condition_variable ready;
	bool hasValue = false;
	std::unique_lock lock(mutex);
	const auto deadline = std::chrono::steady_clock::now() + std::chrono::milliseconds(50);
	const bool arrived = ready.wait_until(lock, deadline, [&]() { return hasValue; });
	std::cout << std::boolalpha << "value arrived before the deadline: " << arrived << '\n';
}
```

```text output-of="basics-threads-until.cpp"
value arrived before the deadline: false
```

1. **Lines 13–14:** `std::chrono::steady_clock::now()` reads a clock that never jumps, and adding 50 ms gives the deadline. Nobody sets `hasValue`, so the wait ends at the deadline and returns false.

## An atomic operation cannot be seen half done

A mutex is a heavy tool for one number. An **atomic operation** is a step that other threads see either not started or finished, never half done. The type `std::atomic<T>` makes every operation on its value atomic: `load` reads, `store` writes, `fetch_add` adds and returns the old value, and `exchange` writes a value and returns the old one in one step.

Two jobs fit atomics well. The first is a counter, as in the race sketch. The second is a flag that tells a thread to stop, which the next sketch shows. The main thread sets the flag and then joins, so the worker has surely ended before the program continues.

```cpp sketch="basics-threads-stop.cpp"
// An atomic flag tells a worker to stop; the main thread sets it, then joins the worker.
#include <atomic>
#include <chrono>
#include <iostream>
#include <thread>

int main()
{
	std::atomic<bool> stop = false;
	std::atomic<long> rounds = 0;
	std::thread worker([&]()
	{
		while (!stop.load())
			rounds.fetch_add(1);
	});
	std::this_thread::sleep_for(std::chrono::milliseconds(20));
	stop.store(true);
	worker.join();
	std::cout << std::boolalpha << "worker did work: " << (rounds.load() > 0) << '\n';
	std::cout << "worker has stopped: " << !worker.joinable() << '\n';
}
```

```text output-of="basics-threads-stop.cpp"
worker did work: true
worker has stopped: true
```

1. **Lines 11–15:** the worker loops until it sees the flag, and counts its rounds.
2. **Lines 17–18:** the main thread sets the flag and joins. A flag only asks the thread to stop; `join` waits until it has.

A plain `bool` would be a data race here. The atomic flag is not, and the loop sees the change soon.

The most useful trick is `exchange`: it tells you what was there before. Strata uses it for the claim on a job. Several threads may want to run the same job, and exactly one may. The next quote is the whole function.

```cpp src="Strata/src/Strata/Core/JobSystem.cpp#L61-L68"
// Runs the job unless another thread claimed it first. Returns whether it ran here.
bool TryRunJob(Detail::JobState& job)
{
	if (job.Claimed.exchange(true, std::memory_order_acq_rel))
		return false;
	ExecuteJob(job);
	return true;
}
```

1. **Line 64:** `exchange(true, ...)` writes true and returns the old value. Only the first caller sees false, so only one thread runs the job, and the others return at line 65. The second argument is a memory order, which a later section explains.

A second tool is compare-exchange: write a new value only if the variable still holds the value you expected. If another thread changed it, the call fails and gives you the current value, so you try again. The sketch uses `compare_exchange_weak` in a loop to keep the highest of four numbers, and `exchange` to elect one winner.

```cpp sketch="basics-threads-claim.cpp"
#include <atomic>
#include <iostream>
#include <thread>
#include <vector>

int main()
{
	std::atomic<bool> claimed = false;
	std::atomic<int> winners = 0;
	std::atomic<int> highest = 0;
	std::vector<std::thread> threads;
	for (int id = 1; id <= 4; id++)
		threads.emplace_back([&, id]()
		{
			if (!claimed.exchange(true))
				winners.fetch_add(1);
			int seen = highest.load();
			while (seen < id * 10 && !highest.compare_exchange_weak(seen, id * 10))
			{
			}
		});
	for (std::thread& thread : threads)
		thread.join();
	std::cout << "winners: " << winners.load() << "\nhighest: " << highest.load() << '\n';
}
```

```text output-of="basics-threads-claim.cpp"
winners: 1
highest: 40
```

1. **Line 15:** four threads run `exchange` on the same flag, and exactly one gets false back, so `winners` is 1.
2. **Lines 17–20:** the loop proposes `id * 10` as the new highest value, but only while it is larger than what is stored. When another thread got in first, the call fails, reloads `seen` and the loop checks again. The weak form may also fail now and then with no change at all, and the loop covers that too.

An atomic covers one variable. Two atomics are each safe alone, and a program that reads both can still see one old and one new. When several values must change together, use a mutex.

:::example[Choose the tool]
Take three jobs. (a) Count the frames that were drawn, read now and then by a display. (b) Tell a worker to stop. (c) Move 10 coins from one player's balance to another's, where the two balances must always add up. Which tool fits each?

Work it by hand. For (a) and (b) one value changes alone, so an atomic is enough. For (c) two values change together and no thread may see a state in between, so a mutex around both changes is right.
:::

Try it: a thread must read a whole `std::string` that another thread replaces now and then. Atomic or mutex?

:::answer
A mutex. A string is not a single value that the processor changes in one step, so no atomic fits.
:::

## Memory order says what one thread sees of another's writes

Locks and atomics have a hidden part. Threads are not told to see each other's writes at once, and not in one order. Each core keeps recent writes in its own buffers and caches, as [How a computer runs a program](../basics/computer.md) explains, and the compiler may change the order of instructions that do not depend on each other. Thread X writes `data` and then `ready`, yet thread Y can see `ready` as true while `data` still looks old.

**Memory order** is the set of rules that says which writes of one thread another thread must see, and in what order. Every atomic operation takes an argument for it. Three choices matter.

- `std::memory_order_relaxed` makes the operation atomic and promises nothing about other memory. A plain counter that nobody uses to publish other data can be relaxed.
- `std::memory_order_release` on a store, paired with `std::memory_order_acquire` on a load, hands data over. When the load sees the value that the store wrote, it also sees every write that the storing thread made before the store.
- The default order is sequentially consistent: all threads agree on one order of all such operations. It is the simplest to reason about, and the others exist to save cost where the proof is clear.

The sketch is the hand-over of the test-out question. The sender writes a plain number and then publishes a flag with release. The receiver loops with acquire, and when it sees the flag, it must see 42.

```cpp sketch="basics-threads-order.cpp"
// Hands a plain value from one thread to another: the release store publishes it, the acquire load that sees the flag receives it.
#include <atomic>
#include <iostream>
#include <thread>

int main()
{
	int message = 0;
	std::atomic<bool> ready = false;
	std::thread sender([&]()
	{
		message = 42;
		ready.store(true, std::memory_order_release);
	});
	while (!ready.load(std::memory_order_acquire))
		std::this_thread::yield();
	std::cout << "received " << message << '\n';
	sender.join();
}
```

```text output-of="basics-threads-order.cpp"
received 42
```

1. **Lines 12–13:** the plain write to `message` comes before the release store, so it is published with the flag.
2. **Line 15:** the acquire load pairs with that store. Once it returns true, the receiver sees 42; with relaxed order on both, the result would be undefined.

Release and acquire name a direction: nothing written before a release moves after it, and nothing read after an acquire moves before it. A **fence**, `std::atomic_thread_fence`, gives the same direction without an operation on a variable. Strata uses fences in a sequence lock, a scheme in which one thread publishes a value and another reads it without either one waiting. The writer makes a counter odd while it writes and even afterward, and the reader keeps a read only if the counter was even and unchanged. The next two quotes are the writer and the reader of `SequenceLockedValue`, which Strata uses to hand the audio listener's up direction to the mixing thread.

```cpp src="Strata/src/Strata/Core/SequenceLock.h#L25-L37"
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
```

1. **Line 31:** the sequence becomes odd, which tells readers that a write has begun.
2. **Line 33:** the release fence keeps that odd number from becoming visible after any word of the new value.
3. **Line 36:** the sequence becomes even again with a release store, which publishes the words that came before it.

The value is stored in relaxed atomic words, so a reader that meets a half-written value breaks no rule; it only notices and tries later.

```cpp src="Strata/src/Strata/Core/SequenceLock.h#L40-L59"
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

1. **Line 42:** the reader loads the sequence with acquire, so the words that follow are at least as new as that number.
2. **Line 43:** an even number equal to the last value taken means nothing is new, and an odd number means a write is in progress. Either way the reader leaves with false.
3. **Line 50:** the acquire fence keeps the word reads before the second look at the sequence.
4. **Lines 51–52:** if the sequence moved, a write happened during the reads, so the reader throws the copy away.

:::why[Why Strata uses a sequence lock for one value]
The sound library reads the listener's up direction while it mixes, without atomics, so only the mixing thread may write it, after each mixing period. That thread must never wait for a lock, because a late buffer of sound can be heard as a click. The sequence lock never blocks either side, and the cost is that the reader may miss one value and then takes the next. That is acceptable for a listener's direction, which changes slowly. See [The audio engine](../audio/engine.md) for the mixing thread.
:::

:::simplified[Memory order]
This page omits `memory_order_consume`, the hardware models behind the rules and the proofs that C++ gives. Write a plain lock or a sequentially consistent atomic first. Read the [cppreference page on memory order](https://en.cppreference.com/w/cpp/atomic/memory_order) before you use a weaker order.
:::

:::example[Can the reader see old data]
Thread X runs `a = 1; b = 2; flag.store(true, std::memory_order_release);`. Thread Y runs `if (flag.load(std::memory_order_acquire)) { use(a, b); }`. If Y sees the flag true, what do `a` and `b` hold for Y? Then change both operations to relaxed.

Work it by hand. With release and acquire, Y sees `a` as 1 and `b` as 2, because both writes came before the store. With relaxed, Y may see true and still read 0 for either variable, since nothing ties those writes to the flag.
:::

Try it: if the store is release and the load is relaxed, may Y still read an old `a`?

:::answer
Yes. The promise needs both halves: the release store and an acquire load. A relaxed load does not pair with it.
:::

## Thread-local variables give each thread its own copy

Sometimes data should not be shared at all. A variable declared `thread_local` is **thread-local**: every thread has its own copy, created for that thread. No thread can race with another on it, so it needs no lock. Strata's code writes such names with the prefix `t_`.

```cpp sketch="basics-threads-local.cpp"
// A thread_local variable has one copy per thread: each thread counts to 3 and the main thread's copy stays 0.
#include <iostream>
#include <thread>

thread_local int t_Calls = 0;

int CountCall()
{
	t_Calls++;
	return t_Calls;
}

int main()
{
	int lastOfA = 0;
	int lastOfB = 0;
	std::thread a([&]() { for (int i = 0; i < 3; i++) lastOfA = CountCall(); });
	std::thread b([&]() { for (int i = 0; i < 3; i++) lastOfB = CountCall(); });
	a.join();
	b.join();
	std::cout << "A " << lastOfA << ", B " << lastOfB << ", main " << t_Calls << '\n';
}
```

```text output-of="basics-threads-local.cpp"
A 3, B 3, main 0
```

1. **Line 5:** one declaration, one copy for each thread.
2. **Lines 17–18:** each thread counts to 3 in its own copy, so neither reaches 6.
3. **Line 21:** the main thread's copy was never touched and is still 0.

The job system of `Strata/src/Strata/Core/JobSystem.cpp` keeps three such variables: which pool the thread belongs to, whether it is a pool thread, and how deep the background jobs it runs are nested. Each thread can ask about itself without a lock. See [Threads and the job system](../core/jobs.md) for what they decide.

## Pools, jobs and one owner thread

Starting a thread for each small task wastes time, and a thousand threads on 8 cores spend their time in switching. A **thread pool** is a fixed set of threads that start once and then wait for work.

A **job** is a small piece of work, usually a function, that you give to the pool. Jobs wait in a queue, as [Data structures I](../basics/data-structures.md) describes queues, and each worker takes the next one. The queue itself is shared, so it is guarded by a mutex and a condition variable.

```cpp pseudocode
worker loop:
    repeat:
        lock the queue's mutex
        wait until the queue holds a job or the pool is closing
        if the queue is empty: return        # closing, and nothing is left
        take the first job out of the queue
        unlock the mutex
        run the job                          # outside the lock
```

The shape is a condition variable with a predicate (the wait), a mutex around the queue, and a job that runs after the unlock. A job that ran under the lock would block every other worker. Strata's job system adds the claim you saw above, so that a thread that waits for a job can run it itself instead of sleeping. Its details are in [Threads and the job system](../core/jobs.md).

Locks cost time, and some programs avoid them. **Lock-free** means that sharing is built from atomics so that no thread ever waits for another thread's lock. The sequence lock is an example. Lock-free code is hard to get right, and a mistake is invisible until it hurts, so use it only where a lock cannot be used, as with the audio thread.

The cheapest cure is the one named at the start of this page: data that only one thread touches needs no lock. This is the design of Strata's engine. One thread, the main thread, owns the scene, the input, the scripts and the submission of drawing work. Other threads do their work on their own data and send the result back.

:::why[Why one thread owns the scene]
A scene has thousands of entities, components and caches that depend on each other. Guarding each with a lock would cost time on every access, and a lock order across all of them would be hard to keep. One owner needs no lock for any of it. The cost is that everything that touches the scene queues up on one thread, and results of other threads arrive later: `Application::SubmitToMainThread` runs a function at the start of the next frame. Strata cuts the cost by giving heavy work, such as loading files, to the job system.
:::

:::rule[Threading]
One thread, the main thread, owns the scene, the input, the scripts and the work of submitting drawing. Other threads return results through `Application::SubmitToMainThread` or polled queues, and never run :term[callbacks]{id=callback} that touch engine state. The reason: one owner needs no locks. [Threads and the job system](../core/jobs.md) shows the hand-offs.
:::

Game scripts follow the same rule. The engine calls every script callback on the main thread, so scripts share data without a lock. A script that starts a thread of its own gets no help from the engine. The thread check of `ResolveContext` fails any engine call from another thread, and only `Log` works there; Practice 5 shows what you see.

## Common mistakes

- **Starting a thread and never joining it.** Symptom: the program ends with no message when the `std::thread` is destroyed while it runs. Fix: join every thread before its object goes.
- **Reading shared data without a lock because "it only reads".** Symptom: odd values now and then, never in tests. Fix: lock for reads too, with a shared lock if many threads read, or use an atomic.
- **Trusting a passing test.** Symptom: a race that fails once a week. Fix: reason with the rules of this page, and build with a thread checker, for example `-fsanitize=thread`.
- **Taking two locks in two orders.** Symptom: the program hangs and no thread uses the processor. Fix: one lock at a time, one order, or `std::scoped_lock` with both mutexes.
- **Waiting on a condition variable with no predicate.** Symptom: a thread sleeps forever after an early notice, or continues with no data after a wake-up. Fix: always `wait(lock, predicate)`.
- **Holding a lock during slow work.** Symptom: all threads that need the mutex pause. Fix: copy what you need under the lock and work after it.
- **Using relaxed order to publish data.** Symptom: a reader sees the flag and old data, on some computers only. Fix: release on the store, acquire on the load, or leave the order at its default.
- **Letting an exception leave a thread's function.** Symptom: the whole program ends. Fix: catch every exception inside the function that the thread runs.
- **Starting threads in a script.** A thread that a script started is not guarded by the script crash containment of [Crash containment](../scripting/crash-containment.md), which watches only the thread on which the engine calls the script. A fault in it, an exception that leaves its function, or a `std::thread` destroyed before `join` ends the editor with the work you have not saved. A deadlock that the callback joins freezes the editor. Fix: save first, join every thread before the callback returns, and catch exceptions inside the thread's function.

## Summary

- A thread is a line of work that shares the process's memory. Two threads that change one value without protection are a data race, and a program that depends on who is first has a race condition; both can pass a thousand tests.
- A mutex admits one thread at a time, and a lock object releases it on every path. Take one lock at a time or all locks in one order, and a deadlock cannot form.
- A condition variable sleeps until another thread notifies, always with a predicate that guards against an early notice and a wake-up with no notice.
- An atomic makes each operation on one variable a single step: counters, stop flags, claims with `exchange` and loops that try again with compare-exchange. For several values, use a mutex; for data of one thread, use no tool at all.
- Release and acquire carry a thread's earlier writes with a flag, relaxed carries nothing, and the default order is the safe one.

## Check yourself

1. Two threads each run `counter.store(counter.load() + 1)` 1,000 times on a `std::atomic<int>` that starts at 0. What is true? A: it always ends at 2,000; B: it is undefined behavior and may crash; C: it may end below 2,000, and it is not a data race; D: it always ends at 1,000.

   :::answer{tests="race"}
   C. Each load and each store is atomic, so no access is a data race, but another thread can write between them, and counts are lost. A would be true for `fetch_add`. B would hold for a plain `int`. D has no basis.
   :::

2. A function locks a mutex, checks an error and returns early when it finds one. Which code releases the mutex on every path? A: `mutex.lock();` at the top and `mutex.unlock();` at the end; B: `std::scoped_lock lock(mutex);` at the top; C: `mutex.unlock();` before each `return`, and nothing else; D: no unlock, since the next call unlocks it.

   :::answer{tests="locks"}
   B. The destructor of the lock runs at every `return`. A skips the unlock on the early return. C breaks as soon as someone adds another path, or an exception comes. D is wrong: a locked mutex stays locked.
   :::

3. A thread calls `ready.wait(lock)` with no predicate, and the worker calls `notify_one()` before the thread reaches `wait`. What happens? A: the thread continues, since the notice is stored. B: the thread may sleep forever, and `wait(lock, predicate)` with a flag set under the mutex is the fix. C: the program is undefined.

   :::answer{tests="wait"}
   B. A notice is not stored for a thread that is not yet waiting. A flag under the mutex, tested in a predicate, is true when the thread arrives, so it never sleeps.
   :::

4. Which one needs a mutex, not an atomic? A: a flag that asks a worker to stop. B: a count of dropped frames. C: a list of the enemies that a worker adds to while others read it. D: the name of the thread that claimed a job, as a number.

   :::answer{tests="atomics"}
   C. A list changes in several steps and several memory words. A, B and D are one value that changes alone, so an atomic is enough.
   :::

5. Which statement about `std::memory_order_relaxed` is true? A: it makes the operation not atomic; B: the operation is atomic but orders no other memory; C: it is the same as release; D: it is the default for `std::atomic`.

   :::answer{tests="order"}
   B. Relaxed keeps the operation one step, which is enough for a counter. It gives no order for other data. The default is sequentially consistent, which is the strongest.
   :::

## Practice

Run exercises 1 to 4 in `Playground`, the script that [Programming from zero I](../basics/programming-1.md#the-playground-is-a-script-of-your-own) puts on an empty entity of your Coin Run, or of the project at the last checkpoint of [Your first script](../make/first-script.md#change-the-code-while-playing-then-crash-it). Stop the game before each build. Exercise 5 is optional and works on the same project.

Three rules keep the editor safe, because a thread of a script runs inside the editor's process. Save your work first. Join every thread before the callback returns. Catch exceptions inside the function that the thread runs. In the script, write `Log::Info` where the sketches write `std::cout`.

1. **Basic.** In the script, make two `std::thread` objects that each add 1 to a shared plain `int` a million times, join both, and log the total. Write down the number you expect. Then change the counter to a `std::atomic<int>` that you update with `counter.store(counter.load() + 1)` and predict again before you run it.

   :::answer[Worked solution]{tests="race"}
   Both versions are broken. The plain `int` is a data race, and what it prints depends on the build. The installed Strata builds scripts in its `Dist` configuration, which optimizes as Release does: on Windows, five runs left 1.13 to 1.43 million. A program of its own left about 1.1 million built with `-O0` and exactly 2,000,000 built with `-O2`, so the printed number cannot tell you whether the code is right.

   The atomic version has no data race, but it is a race condition: it left 1.10 to 1.19 million in the script, and 1.2 to 1.8 million in the program. The race sketch above prints `load then store lost counts: true`, and your totals differ from run to run.
   :::

2. **Medium.** Make both versions correct, once with a `std::mutex` and `std::scoped_lock`, and once with `fetch_add` on a `std::atomic<int>`. Time each with `std::chrono::steady_clock` and log both times in milliseconds.

   :::answer[Worked solution]{tests="locks,atomics" solution="sketches/basics-threads-timed.cpp"}
   Both totals are 2,000,000. The sketch times each version with a steady clock and prints only whether the mutex took longer, because the times change on each run.

   ```cpp sketch="basics-threads-timed.cpp"
   #include <atomic>
   #include <chrono>
   #include <iostream>
   #include <mutex>
   #include <thread>
   template<typename Add>
   std::chrono::steady_clock::duration Time(Add add)
   {
   	const auto start = std::chrono::steady_clock::now();
   	std::thread a([&]() { for (int i = 0; i < 1000000; i++) add(); });
   	std::thread b([&]() { for (int i = 0; i < 1000000; i++) add(); });
   	a.join();
   	b.join();
   	return std::chrono::steady_clock::now() - start;
   }
   int main()
   {
   	std::mutex mutex;
   	int guarded = 0;
   	std::atomic<int> single = 0;
   	const auto withMutex = Time([&]() { std::scoped_lock lock(mutex); guarded++; });
   	const auto withAtomic = Time([&]() { single.fetch_add(1); });
   	std::cout << std::boolalpha << "totals: " << guarded << ' ' << single.load() << '\n';
   	std::cout << "the mutex took longer: " << (withMutex > withAtomic) << '\n';
   }
   ```

   ```text output-of="basics-threads-timed.cpp"
   totals: 2000000 2000000
   the mutex took longer: true
   ```

   1. **Lines 6–15:** `Time` starts the clock, runs two threads that add 1,000,000 times each, joins them and returns the time that passed.
   2. **Lines 21–22:** the first call uses the lock and the second uses `fetch_add`. On the test computer the mutex took about 50 ms and the atomic about 18 ms, and in the script about 24 ms and 16 ms.
   :::

3. **Medium.** Draw two threads that take two locks in two orders as a time line, show where they stop, and name a cure. Then write the cure.

   :::answer[Worked solution]{tests="locks" solution="sketches/basics-threads-cure.cpp"}
   Thread A holds `first` and waits for `second`; thread B holds `second` and waits for `first`, as in the diagram of the deadlock section. Do not write a real deadlock in a script: a callback that joins it freezes the editor. The cure is `std::scoped_lock`, which takes both mutexes together.

   ```cpp sketch="basics-threads-cure.cpp"
   // The cure: scoped_lock takes both locks together, whatever order the names are written in, so no thread holds one and waits.
   #include <functional>
   #include <iostream>
   #include <mutex>
   #include <thread>

   int main()
   {
   	std::mutex first;
   	std::mutex second;
   	int finished = 0;
   	auto work = [&](std::mutex& one, std::mutex& other)
   	{
   		for (int i = 0; i < 100000; i++)
   		{
   			std::scoped_lock both(one, other);
   			finished++;
   		}
   	};
   	std::thread a(work, std::ref(first), std::ref(second));
   	std::thread b(work, std::ref(second), std::ref(first));
   	a.join();
   	b.join();
   	std::cout << "finished " << finished << " rounds without a deadlock\n";
   }
   ```

   ```text output-of="basics-threads-cure.cpp"
   finished 200000 rounds without a deadlock
   ```

   1. **Lines 20–21:** the two threads name the mutexes in opposite orders, yet the program never hangs, because `scoped_lock` at line 16 takes both or neither.
   :::

4. **Hard.** Start a worker thread that adds the numbers 1 to 100 and hands the sum to the callback with a `std::condition_variable` and a predicate. The callback waits at most 2 seconds, logs the sum and joins the worker.

   :::answer[Worked solution]{tests="wait" solution="sketches/basics-threads-handover.cpp"}
   The worker sets the sum and a flag under the mutex, and notifies. The waiting side uses `wait_for` with the predicate, so a late start or a wake-up with no notice changes nothing, and the time limit keeps the callback from hanging if the worker never answers.

   ```cpp sketch="basics-threads-handover.cpp"
   #include <chrono>
   #include <condition_variable>
   #include <iostream>
   #include <mutex>
   #include <thread>
   int main()
   {
   	std::mutex mutex;
   	std::condition_variable ready;
   	bool hasSum = false;
   	int sum = 0;
   	std::thread worker([&]()
   	{
   		std::scoped_lock lock(mutex);
   		for (int i = 1; i <= 100; i++)
   			sum += i;
   		hasSum = true;
   		ready.notify_one();
   	});
   	std::unique_lock lock(mutex);
   	if (ready.wait_for(lock, std::chrono::seconds(2), [&]() { return hasSum; }))
   		std::cout << "the sum is " << sum << '\n';
   	lock.unlock();
   	worker.join();
   }
   ```

   ```text output-of="basics-threads-handover.cpp"
   the sum is 5050
   ```

   1. **Lines 14–18:** the worker adds the numbers and publishes the sum under the lock before it notifies.
   2. **Line 21:** `wait_for` returns true only when the predicate is true, so the log line runs only when a sum arrived.
   :::

5. **Hard.** Optional. All script callbacks of Coin Run run on the main thread, so its scripts share data without a lock. Explain why. Then predict what would break if a script started a thread that moved the ball.

   :::answer[Worked solution]{tests="atomics"}
   The engine calls every callback on the main thread, one after another, so two scripts never run at the same time and never meet in the same data. That is one owner thread, which needs no lock.

   A script thread that moves the ball would fail. Engine calls check their thread, so the move does nothing, and the engine logs an error that scripts can only use the engine from the main thread. Only `Log` works from another thread. If the script's own data is shared with that thread, that data is a data race.
   :::

## Where the book uses it

- [Threads and the job system](../core/jobs.md) builds the worker pool, the claim of a job and the waiting of a thread on the tools of this page.
- [The audio engine](../audio/engine.md) hands the listener's data to the mixing thread with a sequence lock.
- [The frame loop](../core/frame-loop.md) uses the rule that one thread owns the scene.
- [How a GPU works and draws a frame](../gpu/how-a-gpu-frame-works.md) compares the CPU thread that prepares a frame with the GPU that draws the one before.
- [Loading assets](../assets/loading.md) waits for jobs that read files without blocking a frame.

## Further reading

- [cppreference: thread support library](https://en.cppreference.com/w/cpp/thread): every thread, mutex, lock and condition variable type, with their rules; intermediate.
- [cppreference: atomic operations library](https://en.cppreference.com/w/cpp/atomic): `std::atomic`, fences and the memory order table; advanced.
- Learn C++ (learncpp.com): the chapters on `std::thread` and on smart pointers that make lifetimes clear; beginner.
- Anthony Williams, C++ Concurrency in Action: threads, locks, atomics and lock-free design in depth; intermediate to advanced.
- Jeff Preshing, "Preshing on Programming" (preshing.com): lock-free programming and the acquire and release rules, with pictures; intermediate.
