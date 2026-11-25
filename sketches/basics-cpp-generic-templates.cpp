// A function template and a class template: the compiler writes one version for each argument it meets.
#include <iostream>

template<typename T>
T Square(T value)
{
	return value * value;
}

template<typename T, int Count>
struct Row
{
	T Values[Count] = {};
	int Size() const { return Count; }
};

int main()
{
	std::cout << "Square(4) = " << Square(4) << '\n';
	std::cout << "Square(1.5f) = " << Square(1.5f) << '\n';
	std::cout << "bytes of Row<float, 3>: " << sizeof(Row<float, 3>) << '\n';
	std::cout << "bytes of Row<double, 3>: " << sizeof(Row<double, 3>) << '\n';
	return 0;
}
