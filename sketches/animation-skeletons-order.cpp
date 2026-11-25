#include <cstdint>
#include <cstdio>
#include <string>
#include <vector>

constexpr uint16_t c_NoJoint = 0xFFFF;

// An empty string when every parent comes before its child, else the first error.
std::string CheckOrder(const std::vector<std::string>& names, const std::vector<uint16_t>& parents)
{
	for (size_t joint = 0; joint < names.size(); joint++)
	{
		if (parents[joint] != c_NoJoint && parents[joint] >= joint)
			return "Joint '" + names[joint] + "' comes before its parent";
	}
	return "";
}

int main()
{
	const std::string good = CheckOrder({ "Shoulder", "Elbow", "Wrist" }, { c_NoJoint, 0, 1 });
	const std::string bad = CheckOrder({ "Wrist", "Elbow", "Shoulder" }, { 1, 2, c_NoJoint });
	std::printf("Arm: '%s'\n", good.c_str());
	std::printf("Reversed arm: '%s'\n", bad.c_str());
	return 0;
}
