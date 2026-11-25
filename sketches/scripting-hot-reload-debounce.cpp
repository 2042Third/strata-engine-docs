// A debounce: a change is reported only after the file stayed unchanged for a quiet time.
#include <cstdio>
#include <vector>

int main()
{
	const int quietMs = 300;
	const std::vector<int> writes = { 0, 120, 260, 900 }; // Times of linker writes, in milliseconds
	int lastWrite = writes.front();
	for (size_t index = 1; index <= writes.size(); index++)
	{
		const int nextWrite = index < writes.size() ? writes[index] : 1000000;
		if (nextWrite - lastWrite >= quietMs)
			std::printf("reported at %d ms\n", lastWrite + quietMs);
		if (index < writes.size())
			lastWrite = nextWrite;
	}
	return 0;
}
