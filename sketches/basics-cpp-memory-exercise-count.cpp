// Exercise 3: the count of a shared pointer as copies come and go, and a weak pointer that expires.
#include <iostream>
#include <memory>

int main()
{
	std::shared_ptr<int> a = std::make_shared<int>(1);
	std::weak_ptr<int> w = a;
	std::shared_ptr<int> b = a;
	std::shared_ptr<int> c = b;
	std::cout << "count " << a.use_count() << '\n';
	b.reset();
	std::cout << "count " << a.use_count() << '\n';
	a.reset();
	c.reset();
	std::cout << "expired " << std::boolalpha << w.expired() << '\n';
}
