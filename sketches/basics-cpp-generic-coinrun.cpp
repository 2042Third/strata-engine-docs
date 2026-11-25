// Practice 5: coins sorted by their distance to the ball, and a stored callback when the last coin is taken.
#include <algorithm>
#include <cmath>
#include <functional>
#include <iostream>
#include <vector>

struct Coin { float X; float Z; };

int main()
{
	std::vector<Coin> coins = { { 3.0f, 4.0f }, { 1.0f, 0.0f }, { 0.0f, 2.0f } };
	std::function<void()> onAllTaken = []() { std::cout << "all coins taken\n"; };
	std::sort(coins.begin(), coins.end(), [](const Coin& a, const Coin& b)
	{
		return std::hypot(a.X, a.Z) < std::hypot(b.X, b.Z);
	});
	std::cout << "nearest: " << coins.front().X << ", " << coins.front().Z << '\n';
	while (!coins.empty())
	{
		coins.erase(coins.begin());
		if (coins.empty() && onAllTaken)
			onAllTaken();
	}
}
