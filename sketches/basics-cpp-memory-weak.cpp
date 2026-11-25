// A weak pointer watches an object it does not own; lock() gives a shared pointer while the object lives.
#include <iostream>
#include <memory>

int main()
{
	std::shared_ptr<int> owner = std::make_shared<int>(42);
	std::weak_ptr<int> watcher = owner;
	std::cout << "count " << owner.use_count() << '\n';
	if (std::shared_ptr<int> alive = watcher.lock())
		std::cout << "alive: " << *alive << ", count " << owner.use_count() << '\n';
	owner.reset();
	std::cout << "expired: " << std::boolalpha << watcher.expired() << '\n';
	std::cout << "lock gives null: " << (watcher.lock() == nullptr) << '\n';
}
