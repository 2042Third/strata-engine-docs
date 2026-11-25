// Practice 1: the sizes of two vectors after a copy and after a move.
#include <iostream>
#include <utility>
#include <vector>

int main()
{
	std::vector<int> first = { 1, 2, 3, 4, 5 };
	std::vector<int> copied = first;
	std::cout << "after the copy: first " << first.size() << ", copied " << copied.size() << '\n';
	std::vector<int> moved = std::move(first);
	std::cout << "after the move: first " << first.size() << ", moved " << moved.size() << '\n';
	return 0;
}
