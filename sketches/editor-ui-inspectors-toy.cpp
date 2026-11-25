// A toy generic inspector: one list of property descriptions draws and edits every light, with mixed values,
// an inactive reason and one undo step per drag.
#include <cstdio>
#include <functional>
#include <string>
#include <vector>

struct Light
{
	bool CastShadows = true;
	float Intensity = 1.0f;
	float Softness = 0.5f;
};

struct Property
{
	std::string Name;
	std::function<float(const Light&)> Get;
	std::function<void(Light&, float)> Set;
	std::function<std::string(const Light&)> InactiveReason; // empty function: always active
};

struct UndoStep
{
	size_t Property = 0;
	std::vector<float> Before;
	float After = 0.0f;
};

static const std::vector<Property> s_Properties = {
	{ "Cast Shadows", [](const Light& light) { return light.CastShadows ? 1.0f : 0.0f; }, [](Light& light, float value) { light.CastShadows = value != 0.0f; }, {} },
	{ "Intensity", [](const Light& light) { return light.Intensity; }, [](Light& light, float value) { light.Intensity = value; }, {} },
	{ "Softness", [](const Light& light) { return light.Softness; }, [](Light& light, float value) { light.Softness = value; },
		[](const Light& light) { return light.CastShadows ? std::string() : std::string("Cast Shadows is off"); } },
};

static std::vector<UndoStep> s_Undo;
static bool s_MergeOpen = false;

static void DrawRow(const std::vector<Light>& lights, size_t index)
{
	const Property& property = s_Properties[index];
	bool mixed = false;
	std::string reason;
	for (const Light& light : lights)
	{
		mixed = mixed || property.Get(light) != property.Get(lights.front());
		std::string own = property.InactiveReason ? property.InactiveReason(light) : std::string();
		if (own.empty())
			reason.clear(); // active on one entity: the row stays active
		else if (&light == &lights.front() || !reason.empty())
			reason = own;
	}
	std::printf("%-13s %s%s\n", property.Name.c_str(), mixed ? "--" : std::to_string(property.Get(lights.front())).substr(0, 4).c_str(),
		reason.empty() ? "" : ("   (disabled: " + reason + ")").c_str());
}

static void Edit(std::vector<Light>& lights, size_t index, float value)
{
	if (!s_MergeOpen || s_Undo.empty() || s_Undo.back().Property != index)
	{
		UndoStep step;
		step.Property = index;
		for (const Light& light : lights)
			step.Before.push_back(s_Properties[index].Get(light));
		s_Undo.push_back(step);
		s_MergeOpen = true;
	}
	s_Undo.back().After = value; // a merged edit keeps its first "before" and updates its last value
	for (Light& light : lights)
		s_Properties[index].Set(light, value);
}

int main()
{
	std::vector<Light> lights(2);
	lights[1].Softness = 0.9f;
	for (size_t index = 0; index < s_Properties.size(); index++)
		DrawRow(lights, index);
	for (const float value : { 2.0f, 3.0f, 4.0f })
		Edit(lights, 1, value); // three frames of one drag
	s_MergeOpen = false;        // the drag ends: the next edit starts a new step
	std::printf("undo steps after the drag: %zu\n", s_Undo.size());
	Edit(lights, 0, 0.0f);
	for (size_t index = 0; index < s_Properties.size(); index++)
		DrawRow(lights, index);
}
