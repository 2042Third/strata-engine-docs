// Practice 2: a function that returns an optional, and a caller that supplies a fallback with value_or.
#include <iostream>
#include <optional>
#include <vector>

std::optional<int> FirstEven(const std::vector<int>& numbers)
{
	for (int number : numbers)
		if (number % 2 == 0)
			return number;
	return std::nullopt;
}

int main()
{
	std::cout << "first: " << FirstEven({ 3, 5, 8, 10 }).value_or(-1) << '\n';
	std::cout << "second: " << FirstEven({ 3, 5, 7 }).value_or(-1) << '\n';
	return 0;
}
