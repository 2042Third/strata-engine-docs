// Reading an empty optional with value() throws; the throw runs the destructor of every object it leaves.
#include <iostream>
#include <optional>
struct Guard
{
	~Guard() { std::cout << "guard released\n"; }
};
int Work()
{
	Guard guard;
	const std::optional<int> nothing;
	return nothing.value();
}
int main()
{
	try
	{
		std::cout << Work() << '\n';
	}
	catch (const std::bad_optional_access&)
	{
		std::cout << "caught a bad optional access\n";
	}
}
