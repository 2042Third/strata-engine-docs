#include "StrataScript/StrataScript.h"

#include <cmath>
#include <glm/gtc/constants.hpp>

using namespace Strata;

// Smooths the yaw, taking the short way round.
class Turret : public Script
{
public:
	Entity Target; // The ball
	float Sharpness = 4.0f; // Higher turns faster

	void OnUpdate(float deltaTime) override
	{
		if (!Target)
			return;
		const glm::vec3 offset = Target.GetTransform().GetWorldPosition() - GetTransform().GetWorldPosition();
		if (glm::length(offset) < 0.001f)
			return;
		const float wanted = std::atan2(-offset.x, -offset.z);
		const float weight = 1.0f - std::exp(-Sharpness * deltaTime);
		m_Yaw += std::remainder(wanted - m_Yaw, 2.0f * glm::pi<float>()) * weight;
		GetTransform().SetEulerAngles(glm::vec3(0.0f, m_Yaw, 0.0f));
	}
private:
	float m_Yaw = 0.0f; // Radians
};

ST_SCRIPT_CLASS(Turret)
{
	ST_SCRIPT_FIELD(Target);
	ST_SCRIPT_FIELD(Sharpness);
}
