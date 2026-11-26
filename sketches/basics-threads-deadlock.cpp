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
