#include <iostream>
struct Glow
{
	Glow() { std::cout << "Glow built\n"; }
	~Glow() { std::cout << "Glow destroyed\n"; }
};

struct Item
{
	Item() { std::cout << "Item built\n"; }
	~Item() { std::cout << "Item destroyed\n"; }
};

struct Gem : Item
{
	Glow Light;
	Gem() { std::cout << "Gem built\n"; }
	~Gem() { std::cout << "Gem destroyed\n"; }
};

int main()
{
	Gem gem;
}
