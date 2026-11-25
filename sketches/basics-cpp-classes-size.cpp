// The cost of the hidden pointer: the size of an object with and without a virtual function.
#include <iostream>

struct Plain
{
	int Value = 0;
};

struct WithVirtual
{
	int Value = 0;
	virtual ~WithVirtual() = default;
};

int main()
{
	std::cout << "Plain: " << sizeof(Plain) << " bytes\n";
	std::cout << "WithVirtual: " << sizeof(WithVirtual) << " bytes\n";
	return 0;
}
