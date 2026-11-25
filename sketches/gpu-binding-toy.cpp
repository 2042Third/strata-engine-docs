#include <cstdint>
#include <cstdio>
#include <vector>

enum class RegisterClass
{
	Texture,
	Sampler,
	ConstantBuffer,
	ReadWrite
};

// The shift the build adds to each register class on Vulkan: t + 0, s + 128, b + 256, u + 384.
constexpr uint32_t GetVulkanBinding(RegisterClass registerClass, uint32_t slot)
{
	constexpr uint32_t c_Shifts[] = { 0, 128, 256, 384 };
	return c_Shifts[static_cast<size_t>(registerClass)] + slot;
}

struct Item
{
	RegisterClass Class;
	uint32_t Slot;
	const char* Resource; // Only the binding set names a resource.
};

using BindingLayout = std::vector<Item>; // The shape the pipeline expects
using BindingSet = std::vector<Item>;    // The resources that fill that shape

// A draw succeeds only when the set fills every slot of the layout.
bool Draw(const char* name, const BindingLayout& layout, const BindingSet& set)
{
	for (const Item& wanted : layout)
	{
		bool found = false;
		for (const Item& given : set)
			found = found || (given.Class == wanted.Class && given.Slot == wanted.Slot);
		if (!found)
		{
			std::printf("%s: no resource for binding %u\n", name, GetVulkanBinding(wanted.Class, wanted.Slot));
			return false;
		}
	}
	for (const Item& given : set)
		std::printf("%s: binding %u <- %s\n", name, GetVulkanBinding(given.Class, given.Slot), given.Resource);
	return true;
}

int main()
{
	const BindingLayout layout = { { RegisterClass::ConstantBuffer, 0, nullptr }, { RegisterClass::Texture, 0, nullptr },
		{ RegisterClass::Sampler, 0, nullptr } };
	const BindingSet complete = { { RegisterClass::ConstantBuffer, 0, "Frame" }, { RegisterClass::Texture, 0, "Albedo" },
		{ RegisterClass::Sampler, 0, "Linear" } };
	const BindingSet missing = { { RegisterClass::ConstantBuffer, 0, "Frame" }, { RegisterClass::Texture, 0, "Albedo" } };
	Draw("complete", layout, complete);
	Draw("missing", layout, missing);
	return 0;
}
