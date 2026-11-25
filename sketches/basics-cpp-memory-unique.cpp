// One owner: make_unique builds the object, the unique pointer deletes it, and ownership moves but never copies.
#include <iostream>
#include <memory>
#include <utility>

struct Enemy
{
	int Health = 0;
	~Enemy() { std::cout << "enemy deleted\n"; }
};

std::unique_ptr<Enemy> MakeEnemy(int health)
{
	std::unique_ptr<Enemy> enemy = std::make_unique<Enemy>();
	enemy->Health = health;
	return enemy; // ownership leaves with the returned value
}

int main()
{
	std::unique_ptr<Enemy> first = MakeEnemy(30);
	std::unique_ptr<Enemy> second = std::move(first); // hand the object over
	std::cout << "first empty: " << std::boolalpha << (first == nullptr) << ", health " << second->Health << '\n';
}
