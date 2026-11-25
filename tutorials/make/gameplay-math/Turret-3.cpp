#include "StrataScript/StrataScript.h"

#include <cmath>

using namespace Strata;

// Says whether the ball is ahead of the turret, and how far to its side.
class Turret : public Script
{
public:
	Entity Target; // The ball

	void OnUpdate(float deltaTime) override
	{
		if (!Target)
			return;
		const glm::vec3 position = GetTransform().GetWorldPosition();
		const glm::vec3 targetPosition = Target.GetTransform().GetWorldPosition();
		const glm::vec3 offset = targetPosition - position;
		const float distance = glm::length(offset);
		if (distance < 0.001f) // The ball is on the turret: there is no direction
			return;
		const glm::vec3 direction = glm::normalize(offset);
		const float ahead = glm::dot(direction, GetTransform().GetForward());
		const float side = glm::dot(direction, GetTransform().GetRight());
		m_Countdown -= deltaTime;
		if (m_Countdown > 0.0f)
			return;
		m_Countdown = 1.0f;
		Log::Info("Ahead ", ahead, ", side ", side);
	}
private:
	float m_Countdown = 0.0f;
};

ST_SCRIPT_CLASS(Turret)
{
	ST_SCRIPT_FIELD(Target);
}
