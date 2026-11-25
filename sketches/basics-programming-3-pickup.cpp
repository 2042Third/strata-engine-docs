#include <iostream>

class Pickup
{
public:
	int Points = 10;
	virtual void OnCollect() { std::cout << "collected " << Points << " points\n"; }
};

class BonusPickup : public Pickup
{
public:
	void OnCollect() override { Pickup::OnCollect(); std::cout << "plus a bonus of 5\n"; }
};

int main()
{
	BonusPickup pickup;
	pickup.Points = 20;
	pickup.OnCollect();
	return 0;
}
