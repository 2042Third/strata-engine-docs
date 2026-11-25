// A toy validator: a module's description is data from outside, so every count and name is checked before it is used.
#include <cstdint>
#include <cstdio>
#include <set>
#include <string>
#include <vector>

namespace
{

	constexpr std::uint32_t c_MaxClasses = 65536;
	constexpr std::uint32_t c_MaxFields = 4096;
	constexpr std::size_t c_MaxNameSize = 1024;

	struct ClassDescription
	{
		std::string Name;
		std::uint32_t FieldCount = 0;
	};

	// Returns an empty string when the description is valid, else the reason it is refused.
	std::string Validate(std::uint32_t classCount, const std::vector<ClassDescription>& classes)
	{
		if (classCount > c_MaxClasses || classCount != classes.size())
			return "invalid class list";

		std::set<std::string> names;
		for (const ClassDescription& description : classes)
		{
			if (description.Name.empty() || description.Name.size() > c_MaxNameSize)
				return "a class has an invalid name";
			if (!names.insert(description.Name).second)
				return "class '" + description.Name + "' is registered twice";
			if (description.FieldCount > c_MaxFields)
				return "class '" + description.Name + "' has an invalid field list";
		}
		return {};
	}

	void Report(const char* label, const std::string& error)
	{
		std::printf("%s: %s\n", label, error.empty() ? "valid" : error.c_str());
	}

}

int main()
{
	Report("one class", Validate(1, { { "Spinner", 1 } }));
	Report("same name twice", Validate(2, { { "Spinner", 1 }, { "Spinner", 0 } }));
	Report("5000 fields", Validate(1, { { "Spinner", 5000 } }));
	Report("empty name", Validate(1, { { "", 0 } }));
	Report("count too large", Validate(70000, {}));
	return 0;
}
