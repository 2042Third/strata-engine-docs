#include <cmath>
#include <iostream>

class Coin
{
public:
	float Angle = 0.0f;
	virtual void OnUpdate(float deltaTime) { Angle += 90.0f * deltaTime; }
};

class BobbingCoin : public Coin
{
public:
	void OnUpdate(float deltaTime) override
	{
		Coin::OnUpdate(deltaTime);
		std::cout << "angle " << Angle << ", offset " << 0.5f * std::sin(Angle * 0.01745f) << '\n';
	}
};

int main()
{
	BobbingCoin coin;
	coin.OnUpdate(0.5f);
}
