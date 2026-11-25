#include <cassert>
#include <cstdio>

int main()
{
	int checks = 0;

	// The expression inside assert runs only in a build that keeps asserts.
	assert(++checks == 1);

	std::printf("checks run: %d\n", checks);
	return 0;
}
