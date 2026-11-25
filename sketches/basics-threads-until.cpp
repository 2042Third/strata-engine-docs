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
