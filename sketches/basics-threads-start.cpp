// A thread starts from a lambda and runs beside the main thread; join waits until it is done.
#include <iostream>
#include <thread>

int main()
{
	const std::thread::id mainId = std::this_thread::get_id();
	int result = 0;
	std::thread worker([&result, mainId]()
	{
		result = 6 * 7;
		std::cout << std::boolalpha << "worker is the main thread: " << (std::this_thread::get_id() == mainId) << '\n';
	});
	worker.join();
	std::cout << "result = " << result << '\n';
	std::cout << "main is the main thread: " << (std::this_thread::get_id() == mainId) << '\n';
	return 0;
}
