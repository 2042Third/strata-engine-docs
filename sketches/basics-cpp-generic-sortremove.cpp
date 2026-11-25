// Practice 2: sort with a lambda, then remove with remove_if and erase.
#include <algorithm>
#include <iostream>
#include <vector>

int main()
{
	std::vector<int> v = { 4, 9, 1, 7, 3 };
	std::sort(v.begin(), v.end(), [](int a, int b) { return a > b; });
	v.erase(std::remove_if(v.begin(), v.end(), [](int x) { return x < 4; }), v.end());
	for (int value : v)
		std::cout << value << '\n';
	return 0;
}
