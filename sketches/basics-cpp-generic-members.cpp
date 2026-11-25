// A pointer to a member names a field of a class, not of one object: it works on any object of the class.
#include <iostream>

struct Coin
{
	float Speed = 2.0f;
	float Height = 0.5f;
};

float Read(const Coin& coin, float Coin::* field)
{
	return coin.*field;
}

int main()
{
	Coin slow;
	Coin fast;
	fast.Speed = 6.0f;
	float Coin::* field = &Coin::Speed;
	std::cout << "slow " << Read(slow, field) << ", fast " << Read(fast, field) << '\n';
	std::cout << "height " << Read(fast, &Coin::Height) << '\n';
	return 0;
}
