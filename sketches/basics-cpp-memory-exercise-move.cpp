// Exercise 2: the copy does not compile; the move does, and leaves the first pointer empty.
#include <iostream>
#include <memory>
#include <utility>

int main()
{
	std::unique_ptr<int> a = std::make_unique<int>(5);
	std::unique_ptr<int> b = std::move(a);
	std::cout << "b holds " << *b << ", a is empty: " << std::boolalpha << (a == nullptr) << '\n';
}
