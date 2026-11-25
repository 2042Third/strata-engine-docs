// Adding a component after the components it requires, with a guard against requirements that name each other.
#include <algorithm>
#include <cstdio>
#include <map>
#include <set>
#include <string>
#include <vector>

namespace
{
	const std::map<std::string, std::vector<std::string>> c_Requires = {
		{ "UIRect", {} },
		{ "UIImage", { "UIRect" } },
		{ "Ping", { "Pong" } },
		{ "Pong", { "Ping" } },
	};

	void Add(const std::string& name, std::set<std::string>& entity, std::vector<std::string>& adding)
	{
		if (entity.contains(name))
			return;
		adding.push_back(name);
		for (const std::string& required : c_Requires.at(name))
		{
			if (std::find(adding.begin(), adding.end(), required) == adding.end())
				Add(required, entity, adding);
		}
		adding.pop_back();
		entity.insert(name);
		std::printf("added %s\n", name.c_str());
	}
}

int main()
{
	std::set<std::string> entity;
	std::vector<std::string> adding;
	Add("UIImage", entity, adding);
	Add("UIImage", entity, adding);
	Add("Ping", entity, adding);
	std::printf("the entity has %zu components\n", entity.size());
	return 0;
}
