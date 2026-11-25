// A constexpr function runs at compile time when its arguments are known; if constexpr drops the branch not taken.
#include <iostream>
#include <type_traits>

constexpr int Factorial(int n) { return n <= 1 ? 1 : n * Factorial(n - 1); }
static_assert(Factorial(5) == 120);
struct Tag {};
struct Health { int Points = 100; };

template<typename T>
int SizeOfValue()
{
	if constexpr (std::is_empty_v<T>)
		return 0;
	else
		return static_cast<int>(sizeof(T));
}

int main()
{
	constexpr int c_Slots = Factorial(4);
	int values[c_Slots] = {};
	std::cout << "slots " << c_Slots << ", array " << sizeof(values) / sizeof(values[0]) << '\n';
	std::cout << "tag " << SizeOfValue<Tag>() << ", health " << SizeOfValue<Health>() << '\n';
}
