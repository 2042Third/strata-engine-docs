// Practice 3: passing a Coin by value slices it; passing it by reference does not.
#include <iostream>

struct Pickup
{
	virtual ~Pickup() = default;
	virtual const char* Name() const { return "pickup"; }
};

struct Coin : Pickup
{
	const char* Name() const override { return "coin"; }
};

void ByValue(Pickup pickup) { std::cout << "value: " << pickup.Name() << "\n"; }
void ByReference(const Pickup& pickup) { std::cout << "reference: " << pickup.Name() << "\n"; }

int main()
{
	ByValue(Coin());
	ByReference(Coin());
}
