// A lambda is a function written where it is used; its capture list chooses what it keeps.
#include <algorithm>
#include <iostream>
#include <vector>

int main()
{
	std::vector<int> v = { 5, 2, 8 };
	std::sort(v.begin(), v.end(), [](int a, int b) { return a > b; });

	int limit = 4;
	auto isBig = [limit](int x) { return x > limit; };
	limit = 6;
	std::cout << "big with the old limit: " << std::count_if(v.begin(), v.end(), isBig) << '\n';

	int total = 0;
	std::for_each(v.begin(), v.end(), [&total](int x) { total += x; });
	std::cout << "sorted first " << v.front() << ", total " << total << '\n';
	return 0;
}
