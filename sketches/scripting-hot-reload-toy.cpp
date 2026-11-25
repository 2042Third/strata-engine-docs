// A toy hot reload: a "module" is a table of fields and a step size; an instance keeps its values in fields.
#include <cstdio>
#include <optional>
#include <string>
#include <vector>

struct Field
{
	std::string Name;
	float Value = 0.0f;
};

struct Module
{
	int Version = 0;
	std::vector<Field> Defaults;
	float Step = 1.0f; // Stands for the code of OnUpdate
};

struct Instance
{
	std::vector<Field> Fields;
	float Time = 0.0f; // A plain member: not a field, so a reload loses it
};

// Stands for loading a library: a broken build returns nothing and the old module keeps running.
std::optional<Module> LoadModule(int version, bool broken)
{
	if (broken)
		return std::nullopt;
	if (version == 1)
		return Module { 1, { { "Count", 0.0f }, { "Speed", 5.0f } }, 1.0f };
	return Module { version, { { "Count", 0.0f }, { "Speed", 1.0f }, { "Boost", 2.0f } }, 10.0f };
}

Instance Create(const Module& module)
{
	return Instance { module.Defaults, 0.0f };
}

void Update(Instance& instance, const Module& module)
{
	instance.Fields[0].Value += module.Step;
	instance.Time += 1.0f;
}

void Print(const char* label, const Instance& instance)
{
	std::printf("%s:", label);
	for (const Field& field : instance.Fields)
		std::printf(" %s=%g", field.Name.c_str(), field.Value);
	std::printf(" Time=%g\n", instance.Time);
}

// The reload: snapshot the fields, drop the instance, load the new module, restore by name.
bool Reload(Module& module, Instance& instance, int version, bool broken)
{
	std::optional<Module> next = LoadModule(version, broken);
	if (!next)
	{
		std::printf("load failed, module %d keeps running\n", module.Version);
		return false;
	}
	const std::vector<Field> snapshot = instance.Fields;
	module = *next;
	instance = Create(module); // No OnDestroy for the old instance, no OnCreate for the new one
	for (const Field& saved : snapshot)
		for (Field& field : instance.Fields)
			if (field.Name == saved.Name)
				field.Value = saved.Value;
	std::printf("OnReload runs\n");
	return true;
}

int main()
{
	Module module = *LoadModule(1, false);
	Instance instance = Create(module);
	for (int frame = 0; frame < 3; frame++)
		Update(instance, module);
	instance.Fields[1].Value = 8.0f; // The person edits Speed in the Inspector
	Print("before", instance);

	Reload(module, instance, 2, true);
	Reload(module, instance, 2, false);
	Print("after", instance);
	Update(instance, module);
	Print("next frame", instance);
	return 0;
}
