// A base class and a derived class: the order of their constructors and destructors.
#include <iostream>

class Pickup
{
public:
	Pickup() { std::cout << "Pickup built\n"; }
	~Pickup() { std::cout << "Pickup destroyed\n"; }
};

class Coin : public Pickup
{
public:
	Coin() { std::cout << "Coin built\n"; }
	~Coin() { std::cout << "Coin destroyed\n"; }
};

int main()
{
	Coin coin;
	return 0;
}
