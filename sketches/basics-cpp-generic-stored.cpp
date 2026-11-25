// Practice 4: stored callbacks run in order; a position kept as an index survives the vector growing.
#include <functional>
#include <iostream>
#include <vector>

int main()
{
	std::vector<std::function<void()>> callbacks;
	callbacks.push_back([]() { std::cout << "first\n"; });
	callbacks.push_back([]() { std::cout << "second\n"; });
	size_t next = 1; // an iterator such as callbacks.begin() + 1 would be invalid after the next push_back
	callbacks.push_back([]() { std::cout << "third\n"; });
	for (const auto& callback : callbacks)
		callback();
	callbacks[next]();
	return 0;
}
