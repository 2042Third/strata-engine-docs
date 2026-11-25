// Iterators: a forward walk, a reverse walk, and an erase that hands back the next position.
#include <iostream>
#include <vector>

int main()
{
	std::vector<int> v = { 10, 20, 30, 40 };
	for (std::vector<int>::iterator it = v.begin(); it != v.end(); ++it)
		std::cout << *it << ' ';
	std::cout << '\n';
	for (auto it = v.rbegin(); it != v.rend(); ++it)
		std::cout << *it << ' ';
	std::cout << '\n';
	for (auto it = v.begin(); it != v.end();)
	{
		if (*it == 20 || *it == 30)
			it = v.erase(it);
		else
			++it;
	}
	std::cout << "left: " << v.size() << ", first " << v[0] << ", last " << v[1] << '\n';
	return 0;
}
