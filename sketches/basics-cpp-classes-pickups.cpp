#include <iostream>
struct Pickup
{
	virtual ~Pickup() = default;
	virtual void OnCollected() const = 0;
};

struct Star : Pickup
{
	void OnCollected() const override { std::cout << "star collected\n"; }
};

struct SpeedBoost : Pickup
{
	void OnCollected() const override { std::cout << "speed boost collected\n"; }
};

int main()
{
	const Star star;
	const SpeedBoost boost;
	const Pickup* pickups[2] = { &star, &boost };
	for (const Pickup* pickup : pickups)
		pickup->OnCollected();
}
