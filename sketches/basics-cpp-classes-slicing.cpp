// Slicing: copying a Coin into a Pickup value keeps only the Pickup part.
#include <iostream>

struct Pickup
{
	int Points = 1;
	virtual ~Pickup() = default;
	virtual void OnCollected() const { std::cout << "pickup: " << Points << "\n"; }
};

struct Coin : Pickup
{
	int Bonus = 5;
	void OnCollected() const override { std::cout << "coin: " << Points + Bonus << "\n"; }
};

int main()
{
	Coin coin;
	const Pickup& reference = coin;
	const Pickup copy = coin;
	reference.OnCollected();
	copy.OnCollected();
}
