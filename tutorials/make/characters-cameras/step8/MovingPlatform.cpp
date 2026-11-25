#include "StrataScript/StrataScript.h"

#include <cmath>

using namespace Strata;

// Moves its kinematic body between its start and start + Travel, in the fixed steps, so that it and its rider are drawn together.
class MovingPlatform : public Script
{
public:
	glm::vec3 Travel = glm::vec3(6.0f, 0.0f, 0.0f); // Metres from the start to the far end
	float Period = 8.0f;                            // Seconds for a trip there and back

	void OnCreate() override
	{
		m_Start = GetTransform().GetWorldPosition();
	}

	void OnFixedUpdate(float fixedDeltaTime) override
	{
		if (Period <= 0.0f)
			return;
		m_Time += fixedDeltaTime; // Counting steps, never frames
		const float phase = 0.5f - 0.5f * std::cos(6.2831853f * m_Time / Period); // 0 to 1 and back
		GetTransform().SetWorldPosition(m_Start + Travel * phase);
	}

private:
	glm::vec3 m_Start = glm::vec3(0.0f);
	float m_Time = 0.0f;
};

ST_SCRIPT_CLASS(MovingPlatform)
{
	ST_SCRIPT_FIELD(Travel);
	ST_SCRIPT_FIELD(Period);
}
