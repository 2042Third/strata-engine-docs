// A thread_local variable has one copy per thread: each thread counts to 3 and the main thread's copy stays 0.
#include <iostream>
#include <thread>

thread_local int t_Calls = 0;

int CountCall()
{
	t_Calls++;
	return t_Calls;
}

int main()
{
	int lastOfA = 0;
	int lastOfB = 0;
	std::thread a([&]() { for (int i = 0; i < 3; i++) lastOfA = CountCall(); });
	std::thread b([&]() { for (int i = 0; i < 3; i++) lastOfB = CountCall(); });
	a.join();
	b.join();
	std::cout << "A " << lastOfA << ", B " << lastOfB << ", main " << t_Calls << '\n';
}
