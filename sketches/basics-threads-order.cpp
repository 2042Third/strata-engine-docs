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
