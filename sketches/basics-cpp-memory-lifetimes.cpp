// Three lifetimes: automatic (the braces), static (the whole run) and dynamic (new until delete).
#include <iostream>

int s_Total = 0; // a global: built before main starts, kept to the end

int CountCalls()
{
	static int calls = 0; // built the first time this line runs, kept to the end
	calls++;
	return calls;
}

int main()
{
	CountCalls(); CountCalls();
	std::cout << "calls: " << CountCalls() << '\n';
	{
		int inner = 7; // automatic: gone at the closing brace
		s_Total += inner;
	}
	int* onHeap = new int(40); // dynamic: lives until delete
	s_Total += *onHeap;
	delete onHeap;
	std::cout << "total: " << s_Total << '\n';
}
