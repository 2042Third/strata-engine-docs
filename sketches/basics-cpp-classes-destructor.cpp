// Deleting a Coin through a Pickup pointer: the virtual destructor runs both destructors.
#include <iostream>

struct Pickup
{
	virtual ~Pickup() { std::cout << "Pickup destroyed\n"; }
};

struct Coin : Pickup
{
	~Coin() override { std::cout << "Coin destroyed\n"; }
};

int main()
{
	Pickup* pickup = new Coin();
	delete pickup;
}
