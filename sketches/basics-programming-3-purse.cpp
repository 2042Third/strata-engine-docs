// A class that keeps its coin count private and offers two member functions.
#include <iostream>

class Purse
{
public:
	void Add(int coins) { m_Coins += coins; }
	int GetCoins() const { return m_Coins; }
private:
	int m_Coins = 10;
};

int main()
{
	Purse first;
	Purse second;
	first.Add(5);
	std::cout << "first has " << first.GetCoins() << '\n';
	std::cout << "second has " << second.GetCoins() << '\n';
	return 0;
}
