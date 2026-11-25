#include "ThirdPersonPlayer.h"

#include <algorithm>
#include <cmath>

using namespace Strata;

namespace
{

	const glm::vec3 c_Up(0.0f, 1.0f, 0.0f);

}

void ThirdPersonPlayer::OnCreate()
{
	StartPosition = GetTransform().GetWorldPosition();
	Assets::RequestLoad(JumpSound);
	Assets::RequestLoad(LandSound);
}

void ThirdPersonPlayer::OnReload()
{
}

void ThirdPersonPlayer::OnUpdate(float deltaTime)
{
	if (deltaTime <= 0.0f)
		return; // Paused: the pause menu sets the time scale to 0

	TransformComponent transform = GetTransform();
	CharacterController controller = GetEntity().GetCharacterController();
	const glm::vec3 position = transform.GetWorldPosition();
	Grounded = controller.IsGrounded();

	m_JumpCooldown = std::max(0.0f, m_JumpCooldown - deltaTime);
	if (Grounded && m_JumpCooldown <= 0.0f)
	{
		if (m_AirSeconds > 0.3f && LandSound.IsValid())
			Audio::PlayOneShotAt(LandSound, position, 0.7f);
		m_AirSeconds = 0.0f;
	}
	else
	{
		m_AirSeconds += deltaTime;
	}

	// The Move action: +Y walks forward, and its length is at most 1, a diagonal of keys too.
	const glm::vec2 input = Input::GetActionValue("Gameplay/Move");
	const glm::vec3 forward = GetViewForward();
	const glm::vec3 right = glm::normalize(glm::cross(forward, c_Up));
	const glm::vec3 move = forward * input.y + right * input.x;
	const float speed = Input::IsActionDown("Gameplay/Run") ? RunSpeed : WalkSpeed;
	controller.Move(move * speed);
	if (glm::length(move) > 0.05f)
	{
		// The controller moves the position; the script turns the body toward where it walks.
		const float target = glm::degrees(std::atan2(-move.x, -move.z));
		const float difference = std::remainder(target - m_Yaw, 360.0f);
		const float maxTurn = TurnSpeed * deltaTime;
		m_Yaw += std::clamp(difference, -maxTurn, maxTurn);
		transform.SetWorldRotation(glm::angleAxis(glm::radians(m_Yaw), c_Up));
	}

	if (Input::IsActionPressed("Gameplay/Jump") && m_JumpCooldown <= 0.0f && m_AirSeconds <= CoyoteSeconds)
		StartJump(JumpSpeed, position, true);
	if (Input::IsActionPressed("Gameplay/Respawn"))
		Respawn();

	if (position.y < FallHeight)
		Respawn();
}

void ThirdPersonPlayer::Launch(float speed)
{
	StartJump(speed, GetTransform().GetWorldPosition(), false);
}

void ThirdPersonPlayer::Respawn()
{
	const bool atCheckpoint = Checkpoint > 0 && Checkpoint <= static_cast<int32_t>(m_Checkpoints.size());
	const glm::vec3 target = atCheckpoint ? m_Checkpoints[static_cast<size_t>(Checkpoint - 1)] : StartPosition;
	GetEntity().GetCharacterController().Teleport(target + glm::vec3(0.0f, 0.05f, 0.0f));
	m_AirSeconds = 0.0f;
	Log::Info("Platformer: back to checkpoint ", Checkpoint);
}

glm::vec3 ThirdPersonPlayer::GetViewForward() const
{
	const Entity camera = Camera.IsValid() ? Camera : Scene::GetPrimaryCamera();
	if (!camera.IsValid())
		return glm::vec3(0.0f, 0.0f, -1.0f);
	const glm::vec3 forward = camera.GetTransform().GetForward();
	const glm::vec2 flat(forward.x, forward.z);
	if (glm::length(flat) < 0.001f)
		return glm::vec3(0.0f, 0.0f, -1.0f);
	const glm::vec2 direction = glm::normalize(flat);
	return glm::vec3(direction.x, 0.0f, direction.y);
}

void ThirdPersonPlayer::StartJump(float speed, const glm::vec3& position, bool withSound)
{
	GetEntity().GetCharacterController().Jump(speed);
	if (withSound && JumpSound.IsValid())
		Audio::PlayOneShotAt(JumpSound, position, 0.6f);
	m_JumpCooldown = 0.2f;                  // The jump starts at the next fixed step: until then the ground still counts
	m_AirSeconds = CoyoteSeconds + 1.0f;
}

ST_SCRIPT_CLASS(ThirdPersonPlayer)
{
	ST_SCRIPT_FIELD(WalkSpeed);
	ST_SCRIPT_FIELD(RunSpeed);
	ST_SCRIPT_FIELD(JumpSpeed);
	ST_SCRIPT_FIELD(CoyoteSeconds);
	ST_SCRIPT_FIELD(TurnSpeed);
	ST_SCRIPT_FIELD(FallHeight);
	ST_SCRIPT_FIELD(Robot);
	ST_SCRIPT_FIELD(Camera);
	ST_SCRIPT_FIELD(JumpSound);
	ST_SCRIPT_FIELD(LandSound);
	ST_SCRIPT_FIELD(Grounded);
	ST_SCRIPT_FIELD(Checkpoint);
	ST_SCRIPT_FIELD(StartPosition);
}
