// The C form of a callback: a function pointer, a user pointer and a result code.
#include <iostream>

enum Result { Success = 0, InvalidArgument = 1 };

Result RunTicks(int count, void (*function)(void* userData, int tick), void* userData)
{
	if (!function || count < 0)
		return InvalidArgument;
	for (int tick = 1; tick <= count; tick++)
		function(userData, tick);
	return Success;
}

void AddTick(void* userData, int tick)
{
	*static_cast<int*>(userData) += tick;
}

int main()
{
	int sum = 0;
	Result result = RunTicks(4, AddTick, &sum);
	std::cout << "result " << result << ", sum " << sum << '\n';
}
