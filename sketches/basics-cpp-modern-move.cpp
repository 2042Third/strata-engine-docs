// A copy keeps the source; a move takes its contents and leaves the source valid but empty in practice.
#include <iostream>
#include <string>
#include <utility>

int main()
{
	std::string original(40, 'a');
	std::string copy = original;
	std::string moved = std::move(original);
	std::cout << "copy " << copy.size() << ", moved " << moved.size() << '\n';
	std::cout << "original after the move: " << original.size() << '\n';
	return 0;
}
