// Four containers that hold the same coin values.
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <unordered_map>
#include <vector>

int main()
{
	std::vector<int> values = { 30, 10, 20, 10 };
	std::map<std::string, int> ordered = { { "gold", 3 }, { "bronze", 1 }, { "silver", 2 } };
	std::unordered_map<std::string, int> hashed(ordered.begin(), ordered.end());
	std::set<int> unique(values.begin(), values.end());

	std::cout << "vector[2] = " << values[2] << ", size " << values.size() << '\n';
	std::cout << "map in order:";
	for (const auto& entry : ordered)
		std::cout << ' ' << entry.first << '=' << entry.second;
	std::cout << "\nunordered_map silver = " << hashed.at("silver") << '\n';
	std::cout << "set holds " << unique.size() << " values, first " << *unique.begin() << '\n';
	return 0;
}
