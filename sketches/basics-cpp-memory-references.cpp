// A reference is a second name for an object; a const reference passes a large value without a copy.
#include <iostream>

struct Level { float Heights[1000]; }; // 4,000 bytes

void Raise(int& value) { value += 1; }
float Peek(const Level& level) { return level.Heights[7]; } // reads the caller's level: no copy

int main()
{
	int coins = 3;
	int& alias = coins; // a second name for coins
	alias = 4;
	Raise(coins);
	Level level{};
	level.Heights[7] = 2.5f;
	std::cout << "coins: " << coins << ", alias: " << alias << '\n';
	std::cout << "peek: " << Peek(level) << ", level is " << sizeof(Level) << " bytes\n";
}
