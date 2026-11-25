// A local variable is made again, with its first value, at every call.
#include <iostream>

void Count()
{
	int hits = 0;
	hits = hits + 1;
	std::cout << "hits: " << hits << '\n';
}

int main()
{
	Count();
	Count();
	return 0;
}
