// A destructor runs at the closing brace, and the objects of a scope go in the reverse order of their making.
#include <iostream>

struct Noisy
{
	const char* Name;
	explicit Noisy(const char* name)
		: Name(name)
	{
		std::cout << "make " << Name << '\n';
	}
	~Noisy() { std::cout << "drop " << Name << '\n'; }
};

int main()
{
	Noisy a("a");
	{
		Noisy b("b");
		Noisy c("c");
	}
	Noisy d("d");
}
