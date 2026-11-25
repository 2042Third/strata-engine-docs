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
