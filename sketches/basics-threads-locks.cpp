#include <iostream>
#include <map>
#include <mutex>
#include <shared_mutex>
#include <thread>
#include <vector>
std::shared_mutex s_Mutex;
std::map<int, int> s_Values;

int main()
{
	{
		std::unique_lock lock(s_Mutex);
		for (int key = 0; key < 100; key++)
			s_Values[key] = key * 2;
	}
	std::vector<int> sums(4, 0);
	std::vector<std::thread> readers;
	for (int r = 0; r < 4; r++)
		readers.emplace_back([&sums, r]() { std::shared_lock lock(s_Mutex); for (int key = 0; key < 100; key++) sums[r] += s_Values.at(key); });
	for (std::thread& reader : readers)
		reader.join();
	std::cout << "sums: " << sums[0] << ' ' << sums[1] << ' ' << sums[2] << ' ' << sums[3] << '\n';
}
