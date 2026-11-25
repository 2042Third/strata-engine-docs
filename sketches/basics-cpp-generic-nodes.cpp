// Moving one node of a map to the end of the order, without a copy and without a search for the new place.
#include <iostream>
#include <map>
#include <string>
#include <utility>

int main()
{
	std::map<int, std::string> order = { { 1, "tree" }, { 2, "rock" }, { 3, "coin" } };
	auto node = order.extract(2);
	node.key() = 4;
	order.insert(order.end(), std::move(node));
	for (const auto& entry : order)
		std::cout << entry.first << ' ' << entry.second << '\n';
	return 0;
}
