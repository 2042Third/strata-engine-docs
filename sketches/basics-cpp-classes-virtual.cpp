// A call through a base reference: Describe is not virtual, OnCollected is.
#include <iostream>

class Pickup
{
public:
	virtual ~Pickup() = default;
	void Describe() const { std::cout << "a pickup\n"; }
	virtual void OnCollected() const { std::cout << "pickup collected\n"; }
};

class Coin : public Pickup
{
public:
	void Describe() const { std::cout << "a coin\n"; }
	void OnCollected() const override { std::cout << "coin collected\n"; }
};

int main()
{
	Coin coin;
	const Pickup& pickup = coin;
	pickup.Describe();
	pickup.OnCollected();
}
