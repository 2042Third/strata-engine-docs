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
