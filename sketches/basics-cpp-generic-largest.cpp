// Practice 1: a function template Largest, called with int and with float.
#include <iostream>

template<typename T>
T Largest(T a, T b)
{
	return a > b ? a : b;
}

int main()
{
	std::cout << "Largest(3, 7) = " << Largest(3, 7) << '\n';
	std::cout << "Largest(2.5f, 1.5f) = " << Largest(2.5f, 1.5f) << '\n';
	return 0;
}
