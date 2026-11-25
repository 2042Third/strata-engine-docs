#include "StrataScript/StrataScript.h"

#include <cmath>

using namespace Strata;

// Moves its kinematic body between its start and start + Travel, or, with Loop on, from the start to the far end and back at once.
class MovingPlatform : public Script
{
public:
	glm::vec3 Travel = glm::vec3(6.0f, 0.0f, 0.0f); // Metres from the start to the far end
	float Period = 8.0f;                            // Seconds for a trip there and back (a loop: one way)
	bool Loop = false;                              // Jump back to the start after each trip

	void OnCreate() override
	{
		m_Start = GetTransform().GetWorldPosition();
	}

	void OnFixedUpdate(float fixedDeltaTime) override
	{
		if (Period <= 0.0f)
			return;
		const float before = m_Time;
		m_Time += fixedDeltaTime;
		TransformComponent transform = GetTransform();
		if (Loop)
		{
			transform.SetWorldPosition(m_Start + Travel * (std::fmod(m_Time, Period) / Period));
			if (std::floor(m_Time / Period) > std::floor(before / Period))
				transform.ResetInterpolation(); // It jumped back: do not draw it sliding there
		}
		else
		{
			const float phase = 0.5f - 0.5f * std::cos(6.2831853f * m_Time / Period);
			transform.SetWorldPosition(m_Start + Travel * phase);
		}
	}

private:
	glm::vec3 m_Start = glm::vec3(0.0f);
	float m_Time = 0.0f;
};

ST_SCRIPT_CLASS(MovingPlatform)
{
	ST_SCRIPT_FIELD(Travel);
	ST_SCRIPT_FIELD(Period);
	ST_SCRIPT_FIELD(Loop);
}
