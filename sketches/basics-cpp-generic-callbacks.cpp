// A list of std::function callbacks, run in the order they were added.
#include <functional>
#include <iostream>
#include <vector>

int main()
{
	std::vector<std::function<void()>> callbacks;
	int coins = 0;
	callbacks.push_back([&coins]() { coins++; });
	callbacks.push_back([&coins]() { coins += 10; });
	callbacks.push_back([]() { std::cout << "all callbacks ran\n"; });
	for (const auto& callback : callbacks)
		callback();
	std::cout << "coins: " << coins << '\n';
	return 0;
}
