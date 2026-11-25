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
