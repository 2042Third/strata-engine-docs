#include <iostream>
#include <set>
#include <string>
#include <vector>

// A property that names another entity by number; 0 means "no reference".
struct EntityReference
{
	std::string Property;
	int Target = 0;
};

int CheckReferences(const std::set<int>& entities, const std::vector<EntityReference>& references)
{
	int failures = 0;
	for (const EntityReference& reference : references)
	{
		if (reference.Target == 0)
			continue;
		if (!entities.contains(reference.Target))
		{
			std::cout << "FAIL " << reference.Property << ": entity " << reference.Target << " does not exist\n";
			failures++;
		}
	}
	return failures;
}

int main()
{
	const std::set<int> entities = { 1, 2, 3 };
	const std::vector<EntityReference> references = { { "Follow.Target", 2 }, { "Door.Opener", 7 }, { "Light.Parent", 0 } };
	std::cout << CheckReferences(entities, references) << " failures\n";
	return 0;
}
