// A static_assert inside a template checks the argument while the program builds.
#include <iostream>
#include <type_traits>

template<typename T>
T Half(T value)
{
	static_assert(std::is_floating_point_v<T>, "Half needs a float or a double");
	return value / 2;
}

int main()
{
	std::cout << "Half(5.0f) = " << Half(5.0f) << '\n';
	// Half(5) does not build: T is int, and the message above appears in the build output.
	return 0;
}
