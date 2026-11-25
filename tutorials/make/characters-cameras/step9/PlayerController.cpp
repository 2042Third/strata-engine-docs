#include "StrataScript/StrataScript.h"

#include <algorithm>
#include <cmath>

using namespace Strata;

// Walks its character relative to the primary camera, turns the body toward where it walks and jumps.
class PlayerController : public Script
{
public:
	float WalkSpeed = 5.0f;       // Metres per second
	float TurnSharpness = 12.0f;  // How quickly the body turns (1/s)
	float JumpSpeed = 5.0f;       // Upward speed of a jump, metres per second
	float CoyoteSeconds = 0.15f;  // A jump still counts this long after the ground was left
	float FallHeight = -8.0f;     // Below this height the player respawns, in metres
	int GroundStateNumber = 0;    // 0 on ground, 1 on steep ground, 2 not supported, 3 in air (to watch in the Inspector)

	void OnCreate() override
	{
		m_Spawn = GetTransform().GetWorldPosition();
	}

	void OnUpdate(float deltaTime) override
	{
		CharacterController controller = GetEntity().GetCharacterController();
		if (GetTransform().GetWorldPosition().y < FallHeight)
			controller.Teleport(m_Spawn); // Drawn where it lands, with no slide
		const glm::vec3 move = GetMoveDirection();
		controller.Move(move * WalkSpeed);
		if (glm::length(move) > 0.05f)
		{
			const float target = std::atan2(-move.x, -move.z);
			m_Yaw += std::remainder(target - m_Yaw, 6.2831853f) * (1.0f - std::exp(-TurnSharpness * deltaTime));
			GetTransform().SetWorldRotation(glm::angleAxis(m_Yaw, glm::vec3(0.0f, 1.0f, 0.0f)));
		}

		GroundStateNumber = static_cast<int>(controller.GetGroundState());
		m_JumpCooldown = std::max(0.0f, m_JumpCooldown - deltaTime);
		if (controller.IsGrounded() && m_JumpCooldown <= 0.0f)
			m_AirSeconds = 0.0f;
		else
			m_AirSeconds += deltaTime;
		if (Input::IsActionPressed("Gameplay/Jump") && m_AirSeconds <= CoyoteSeconds && m_JumpCooldown <= 0.0f)
		{
			controller.Jump(JumpSpeed);
			m_JumpCooldown = 0.2f; // The jump starts at the next fixed step: until then the ground still counts
			m_AirSeconds = CoyoteSeconds + 1.0f;
		}
	}

private:
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
	glm::vec3 m_Spawn = glm::vec3(0.0f);
	float m_Yaw = 0.0f;
	float m_AirSeconds = 0.0f;
	float m_JumpCooldown = 0.0f;
};

ST_SCRIPT_CLASS(PlayerController)
{
	ST_SCRIPT_FIELD(WalkSpeed);
	ST_SCRIPT_FIELD(TurnSharpness);
	ST_SCRIPT_FIELD(JumpSpeed);
	ST_SCRIPT_FIELD(CoyoteSeconds);
	ST_SCRIPT_FIELD(FallHeight);
	ST_SCRIPT_FIELD(GroundStateNumber);
}
