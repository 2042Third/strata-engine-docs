// RAII: the constructor opens, the destructor closes, and every way out of the function runs the destructor.
#include <iostream>

struct Guard
{
	Guard() { std::cout << "open\n"; }
	~Guard() { std::cout << "close\n"; }
};

bool Load(bool fail)
{
	Guard file;
	if (fail)
		return false; // an early exit still runs the destructor
	std::cout << "loaded\n";
	return true;
}

int main()
{
	std::cout << "call 1\n";
	Load(false);
	std::cout << "call 2\n";
	Load(true);
}
