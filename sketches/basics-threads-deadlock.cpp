#include <chrono>
#include <iostream>
#include <latch>
#include <mutex>
#include <thread>

int main()
{
	std::timed_mutex first;
	std::timed_mutex second;
	std::latch bothHold(2);
	bool gotSecond = true;
	bool gotFirst = true;
	auto take = [&](std::timed_mutex& mine, std::timed_mutex& other, bool& got)
	{
		std::scoped_lock lock(mine);
		bothHold.arrive_and_wait();
		got = other.try_lock_for(std::chrono::milliseconds(100));
	};
	std::thread a([&]() { take(first, second, gotSecond); });
	std::thread b([&]() { take(second, first, gotFirst); });
	a.join();
	b.join();
	std::cout << std::boolalpha << "A got the second lock: " << gotSecond << "\nB got the first lock: " << gotFirst << '\n';
}
