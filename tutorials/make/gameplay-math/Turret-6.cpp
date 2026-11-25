#include "StrataScript/StrataScript.h"

#include <cmath>

using namespace Strata;

// Aims at a point that follows the ball a little late.
class Turret : public Script
{
public:
	Entity Target; // The ball
	float Sharpness = 4.0f; // Higher follows faster

	void OnCreate() override
	{
		if (Target)
			m_Aim = Target.GetTransform().GetWorldPosition();
	}

	void OnUpdate(float deltaTime) override
	{
		if (!Target)
			return;
		const float weight = 1.0f - std::exp(-Sharpness * deltaTime);
		m_Aim = glm::mix(m_Aim, Target.GetTransform().GetWorldPosition(), weight);
		GetTransform().SetWorldRotation(Motion::LookAt(GetTransform().GetWorldPosition(), m_Aim));
	}
private:
	glm::vec3 m_Aim = glm::vec3(0.0f);
};

ST_SCRIPT_CLASS(Turret)
{
	ST_SCRIPT_FIELD(Target);
	ST_SCRIPT_FIELD(Sharpness);
}
