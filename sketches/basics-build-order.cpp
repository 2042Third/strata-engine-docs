#include <cstdio>

// A global is built before main runs. Within one file, in the order of its definitions.
struct Announcer
{
	explicit Announcer(int number)
	{
		std::printf("building global %d\n", number);
	}
};

Announcer g_First(1);
Announcer g_Second(2);

int main()
{
	std::printf("main starts\n");
	return 0;
}
