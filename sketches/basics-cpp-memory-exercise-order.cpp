// Exercise 1: four objects, one of them in a nested scope; the log shows the order of makes and drops.
#include <iostream>

struct Noisy
{
	const char* Name;
	explicit Noisy(const char* name)
		: Name(name)
	{
		std::cout << "make " << Name << '\n';
	}
	~Noisy() { std::cout << "drop " << Name << '\n'; }
};

int main()
{
	Noisy x("x");
	Noisy y("y");
	{
		Noisy z("z");
	}
	Noisy w("w");
}
