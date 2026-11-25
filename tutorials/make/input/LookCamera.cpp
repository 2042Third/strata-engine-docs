#include "StrataScript/StrataScript.h"

using namespace Strata;

// Turns its entity with the mouse while the right button is held, and with the Look action.
class LookCamera : public Script
{
public:
	float DegreesPerPixel = 0.1f;
	float StickDegreesPerSecond = 120.0f;

	void OnCreate() override
	{
		const glm::vec3 angles = GetTransform().GetEulerAngles();
		m_Pitch = angles.x;
		m_Yaw = angles.y;
	}

	void OnUpdate(float deltaTime) override
	{
		const bool looking = Input::IsMouseButtonDown(Mouse::ButtonRight);
		Input::SetCursorMode(looking ? CursorMode::Locked : CursorMode::Normal);

		if (looking)
		{
			const glm::vec2 delta = Input::GetMouseDelta();
			m_Yaw -= glm::radians(delta.x * DegreesPerPixel);   // Mouse right turns right
			m_Pitch -= glm::radians(delta.y * DegreesPerPixel); // Mouse down looks down
		}

		const glm::vec2 look = Input::GetActionValue("Gameplay/Look");
		m_Yaw -= glm::radians(look.x * StickDegreesPerSecond * deltaTime);
		m_Pitch += glm::radians(look.y * StickDegreesPerSecond * deltaTime);
		m_Pitch = glm::clamp(m_Pitch, glm::radians(-89.0f), glm::radians(89.0f));

		GetTransform().SetEulerAngles(glm::vec3(m_Pitch, m_Yaw, 0.0f));
	}

private:
	float m_Pitch = 0.0f;
	float m_Yaw = 0.0f;
};

ST_SCRIPT_CLASS(LookCamera)
{
	ST_SCRIPT_FIELD(DegreesPerPixel);
	ST_SCRIPT_FIELD(StickDegreesPerSecond);
}
