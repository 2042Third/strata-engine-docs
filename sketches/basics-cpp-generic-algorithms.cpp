// Sort with a comparator function, find the first match, and remove with the erase idiom.
#include <algorithm>
#include <iostream>
#include <vector>

bool Higher(int a, int b) { return a > b; }
bool IsEven(int value) { return value % 2 == 0; }

int main()
{
	std::vector<int> v = { 5, 2, 8, 1, 9, 3 };
	std::sort(v.begin(), v.end(), Higher);
	std::cout << "first: " << v.front() << '\n';
	auto found = std::find_if(v.begin(), v.end(), IsEven);
	std::cout << "first even: " << *found << '\n';
	auto newEnd = std::remove_if(v.begin(), v.end(), IsEven);
	std::cout << "size before erase: " << v.size() << '\n';
	v.erase(newEnd, v.end());
	std::cout << "size after erase: " << v.size() << '\n';
	return 0;
}
