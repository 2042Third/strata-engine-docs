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
