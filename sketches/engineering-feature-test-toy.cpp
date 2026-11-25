#include <iostream>
#include <string>
#include <vector>

struct Property
{
	std::string Name;
	int Default = 0;
};

struct Component
{
	std::string Name;
	std::vector<Property> Properties;
};

// One property value of one entity of the feature scene.
struct SceneValue
{
	std::string Component;
	std::string Property;
	int Value = 0;
};

int CheckCoverage(const std::vector<Component>& registry, const std::vector<SceneValue>& scene)
{
	int failures = 0;
	for (const Component& component : registry)
	{
		bool present = false;
		for (const SceneValue& value : scene)
			present |= value.Component == component.Name;
		if (!present)
		{
			std::cout << "FAIL " << component.Name << ": no entity has it\n";
			failures++;
			continue;
		}
		for (const Property& property : component.Properties)
		{
			bool nonDefault = false;
			for (const SceneValue& value : scene)
				nonDefault |= value.Component == component.Name && value.Property == property.Name && value.Value != property.Default;
			if (!nonDefault)
			{
				std::cout << "FAIL " << component.Name << "." << property.Name << ": default on every entity\n";
				failures++;
			}
		}
	}
	return failures;
}

int main()
{
	const std::vector<Component> registry = { { "Light", { { "Intensity", 1 }, { "Range", 10 } } }, { "Camera", { { "Fov", 60 } } } };
	std::vector<SceneValue> scene = { { "Light", "Intensity", 5 }, { "Light", "Range", 10 } };

	std::cout << "Run 1: " << CheckCoverage(registry, scene) << " failures\n";
	scene = { { "Light", "Intensity", 5 }, { "Light", "Range", 25 }, { "Camera", "Fov", 90 } };
	std::cout << "Run 2: " << CheckCoverage(registry, scene) << " failures\n";
	return 0;
}
