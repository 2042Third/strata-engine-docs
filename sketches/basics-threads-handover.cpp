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
