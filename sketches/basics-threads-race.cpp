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
