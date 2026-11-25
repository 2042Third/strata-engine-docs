// A hash map's buckets: eight lists, and the sum of the letter codes as the hash function.
#include <iostream>
#include <string>
#include <vector>

size_t HashName(const std::string& name)
{
	size_t sum = 0;
	for (char letter : name)
		sum += static_cast<unsigned char>(letter);
	return sum;
}
int main()
{
	std::vector<std::vector<std::string>> buckets(8);
	for (const std::string name : { "ant", "bee", "tan", "cat" })
		buckets[HashName(name) % buckets.size()].push_back(name);
	for (size_t index = 0; index < buckets.size(); index++)
	{
		std::cout << "bucket " << index << ":";
		for (const std::string& name : buckets[index])
			std::cout << ' ' << name;
		std::cout << '\n';
	}
}
