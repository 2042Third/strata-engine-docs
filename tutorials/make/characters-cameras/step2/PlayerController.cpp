#include "StrataScript/StrataScript.h"

#include <cmath>

using namespace Strata;

// Walks its character relative to the primary camera and turns the body toward where it walks.
class PlayerController : public Script
{
public:
	float WalkSpeed = 5.0f;      // Metres per second
	float TurnSharpness = 12.0f; // How quickly the body turns (1/s)

	void OnUpdate(float deltaTime) override
	{
		const glm::vec3 move = GetMoveDirection();
		GetEntity().GetCharacterController().Move(move * WalkSpeed);
		if (glm::length(move) > 0.05f)
		{
			// Forward is -Z, so a turn of yaw radians about Y points the body along (-sin, 0, -cos).
			const float target = std::atan2(-move.x, -move.z);
			m_Yaw += std::remainder(target - m_Yaw, 6.2831853f) * (1.0f - std::exp(-TurnSharpness * deltaTime));
			GetTransform().SetWorldRotation(glm::angleAxis(m_Yaw, glm::vec3(0.0f, 1.0f, 0.0f)));
		}
	}

private:
	// The Move action's direction on the ground: its up is the camera's forward, its right the camera's right.
	glm::vec3 GetMoveDirection() const
	{
		const Entity camera = Scene::GetPrimaryCamera();
		if (!camera.IsValid())
			return glm::vec3(0.0f);
		glm::vec3 forward = camera.GetTransform().GetForward();
		forward.y = 0.0f;
		if (glm::length(forward) < 0.001f)
			return glm::vec3(0.0f);
		forward = glm::normalize(forward);
		const glm::vec3 right(-forward.z, 0.0f, forward.x);
		const glm::vec2 input = Input::GetActionValue("Gameplay/Move");
		return right * input.x + forward * input.y;
	}

private:
	float m_Yaw = 0.0f;
};

ST_SCRIPT_CLASS(PlayerController)
{
	ST_SCRIPT_FIELD(WalkSpeed);
	ST_SCRIPT_FIELD(TurnSharpness);
}
