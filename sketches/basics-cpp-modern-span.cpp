// A span views a run of numbers it does not own; the last numbers are reached with the reverse iterators.
#include <iostream>
#include <span>
#include <vector>

void PrintBackwards(std::span<const int> values)
{
	for (auto it = values.rbegin(); it != values.rend(); ++it)
		std::cout << *it << ' ';
	std::cout << '\n';
}

int main()
{
	const std::vector<int> scores = { 10, 20, 30, 40, 50 };
	PrintBackwards(scores);
	PrintBackwards(std::span<const int>(scores).first(3));
	std::cout << "size " << std::span<const int>(scores).size() << ", bytes " << std::span<const int>(scores).size_bytes() << '\n';
	return 0;
}
