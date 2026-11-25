// Exercise: a section's validation reports the first bad field in the order of its fields.
#include <cstdio>
#include <string>
#include <vector>

struct Field
{
	std::string Name;
	float Min;
	float Max;
	float Value;
};

std::string FindProblem(const std::vector<Field>& fields)
{
	for (const Field& field : fields)
	{
		if (field.Value < field.Min || field.Value > field.Max)
			return field.Name + " must be from " + std::to_string(static_cast<int>(field.Min)) + " to " + std::to_string(static_cast<int>(field.Max));
	}
	return std::string();
}

int main()
{
	std::vector<Field> fields = { { "Rate", 1.0f, 240.0f, 500.0f }, { "Steps", 1.0f, 8.0f, 20.0f }, { "Scale", 0.0f, 1.0f, 0.5f } };
	std::printf("1: %s\n", FindProblem(fields).c_str());
	fields[0].Value = 60.0f;
	std::printf("2: %s\n", FindProblem(fields).c_str());
	fields[1].Value = 4.0f;
	std::printf("3: [%s]\n", FindProblem(fields).c_str());
	return 0;
}
