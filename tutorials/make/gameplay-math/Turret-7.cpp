#include "StrataScript/StrataScript.h"

#include <cmath>

using namespace Strata;

// Aims at a point that the spring of SmoothDamp pulls after the ball.
class Turret : public Script
{
public:
	Entity Target; // The ball
	float SmoothTime = 0.4f; // Seconds to arrive

	void OnCreate() override
	{
		if (Target)
			m_Aim = Target.GetTransform().GetWorldPosition();
	}

	void OnUpdate(float deltaTime) override
	{
		if (!Target)
			return;
		m_Aim = Motion::SmoothDamp(m_Aim, Target.GetTransform().GetWorldPosition(), m_AimVelocity, SmoothTime, deltaTime);
		GetTransform().SetWorldRotation(Motion::LookAt(GetTransform().GetWorldPosition(), m_Aim));
	}
private:
	glm::vec3 m_Aim = glm::vec3(0.0f);
	glm::vec3 m_AimVelocity = glm::vec3(0.0f); // Kept between frames
};

ST_SCRIPT_CLASS(Turret)
{
	ST_SCRIPT_FIELD(Target);
	ST_SCRIPT_FIELD(SmoothTime);
}
