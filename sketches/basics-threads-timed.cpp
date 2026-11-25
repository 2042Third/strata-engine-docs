#include <atomic>
#include <chrono>
#include <iostream>
#include <mutex>
#include <thread>
template<typename Add>
std::chrono::steady_clock::duration Time(Add add)
{
	const auto start = std::chrono::steady_clock::now();
	std::thread a([&]() { for (int i = 0; i < 1000000; i++) add(); });
	std::thread b([&]() { for (int i = 0; i < 1000000; i++) add(); });
	a.join();
	b.join();
	return std::chrono::steady_clock::now() - start;
}
int main()
{
	std::mutex mutex;
	int guarded = 0;
	std::atomic<int> single = 0;
	const auto withMutex = Time([&]() { std::scoped_lock lock(mutex); guarded++; });
	const auto withAtomic = Time([&]() { single.fetch_add(1); });
	std::cout << std::boolalpha << "totals: " << guarded << ' ' << single.load() << '\n';
	std::cout << "the mutex took longer: " << (withMutex > withAtomic) << '\n';
}
