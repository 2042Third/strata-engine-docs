// A function that returns a function, and a function that takes one.
#include <functional>
#include <iostream>

std::function<int(int)> MakeAdder(int amount)
{
	return [amount](int x) { return x + amount; };
}

int Twice(const std::function<int(int)>& function, int x)
{
	return function(function(x));
}

int main()
{
	auto addTwo = MakeAdder(2);
	std::cout << "addTwo(5) = " << addTwo(5) << '\n';
	std::cout << "Twice(addTwo, 5) = " << Twice(addTwo, 5) << '\n';
	return 0;
}
