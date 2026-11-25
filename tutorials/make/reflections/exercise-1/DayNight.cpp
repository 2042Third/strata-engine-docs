#include "StrataScript/StrataScript.h"

#include <algorithm>
#include <cmath>

using namespace Strata;

// Turns the sun (the entity this script is on, with a DirectionalLight) through a day of DayLengthSeconds, in steps of at
// most StepDegrees. At night the same light is the moon, across the sky from the sun. Entities tagged "Campfire" with a
// PointLight burn from dusk to dawn.
class DayNight : public Script
{
public:
	float DayLengthSeconds = 600.0f; // A whole day
	float TimeOfDay = 9.0f;          // Hours, 0 to 24 (6 sunrise, 18 sunset)
	float StepDegrees = 0.25f;       // The sun turns in steps of at most this much
	float Azimuth = 35.0f;           // Degrees: where the sun crosses the sky
	float SunIntensity = 120000.0f;  // Lux above the atmosphere, which dims it on its way down
	float CampfireIntensity = 100.0f; // Candela
	bool CampfiresLit = false;

	void OnCreate() override { Apply(true); }
	void OnReload() override { Apply(true); }

	void OnUpdate(float deltaTime) override
	{
		TimeOfDay = std::fmod(TimeOfDay + deltaTime * 24.0f / std::max(DayLengthSeconds, 1.0f), 24.0f);
		Apply(false);
	}

private:
	static constexpr float c_MoonIntensity = 0.2f; // Lux: the light at night

	void Apply(bool force)
	{
		const float angle = (TimeOfDay - 6.0f) / 12.0f * 180.0f; // -90 at midnight, 90 at noon
		if (!force && std::abs(angle - m_AppliedAngle) < StepDegrees)
			return;
		m_AppliedAngle = angle;

		const bool night = std::sin(glm::radians(angle)) < 0.0f;
		const float lightAngle = night ? std::fmod(angle + 180.0f, 360.0f) : angle;
		const glm::quat rotation = glm::angleAxis(glm::radians(Azimuth), glm::vec3(0.0f, 1.0f, 0.0f))
			* glm::angleAxis(glm::radians(-std::clamp(lightAngle, 2.0f, 178.0f)), glm::vec3(1.0f, 0.0f, 0.0f));
		GetTransform().SetRotation(rotation);
		const float fade = std::clamp(std::sin(glm::radians(lightAngle)) / 0.035f, 0.0f, 1.0f);
		GetEntity().SetProperty("DirectionalLight", "Intensity", (night ? c_MoonIntensity : SunIntensity) * fade);

		const bool lit = std::sin(glm::radians(angle)) < 0.1f;
		if (lit != CampfiresLit || force)
		{
			CampfiresLit = lit;
			for (Entity fire : Scene::FindEntitiesByTag("Campfire"))
				fire.SetProperty("PointLight", "Intensity", lit ? CampfireIntensity : 0.0f);
		}
	}

	float m_AppliedAngle = -1000.0f;
};

ST_SCRIPT_CLASS(DayNight)
{
	ST_SCRIPT_FIELD(DayLengthSeconds);
	ST_SCRIPT_FIELD(TimeOfDay);
	ST_SCRIPT_FIELD(StepDegrees);
	ST_SCRIPT_FIELD(Azimuth);
	ST_SCRIPT_FIELD(SunIntensity);
	ST_SCRIPT_FIELD(CampfireIntensity);
	ST_SCRIPT_FIELD(CampfiresLit);
}
