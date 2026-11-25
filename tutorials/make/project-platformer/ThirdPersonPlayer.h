#pragma once

#include "StrataScript/StrataScript.h"

#include <cstdint>
#include <vector>

// The player, on the "Player" entity (a CharacterController whose child "Robot" is the animated model), driven by the
// project's input actions: it walks where the camera looks, runs while Run is held, jumps with a short coyote time and
// goes back to its last checkpoint when it falls off the islands or when Respawn is pressed.
class ThirdPersonPlayer : public Strata::Script
{
public:
	float WalkSpeed = 3.0f;          // Metres per second
	float RunSpeed = 6.5f;
	float JumpSpeed = 5.5f;          // Metres per second upward: about 1.5 m high
	float CoyoteSeconds = 0.15f;     // A jump still counts this long after walking off a ledge
	float TurnSpeed = 720.0f;        // Degrees per second the body turns toward where it walks
	float FallHeight = -15.0f;       // Below this height the player is back at its last checkpoint
	Strata::Entity Robot;            // The model with the Animator
	Strata::Entity Camera;           // The follow camera whose view the movement follows
	Strata::AssetHandle JumpSound;
	Strata::AssetHandle LandSound;

	// What the player does, to watch in the Inspector
	bool Grounded = false;
	int32_t Checkpoint = 0;          // The last checkpoint reached (0: the start)
	glm::vec3 StartPosition = glm::vec3(0.0f);

	void OnCreate() override;
	void OnReload() override;
	void OnUpdate(float deltaTime) override;

	// Throws the player up at `speed` metres per second (a jump pad).
	void Launch(float speed);
	// Back to the last checkpoint, or to the start.
	void Respawn();
private:
	glm::vec3 GetViewForward() const;
	void UpdateCheckpoints(const glm::vec3& position);
	void StartJump(float speed, const glm::vec3& position, bool withSound);
private:
	float m_Yaw = 0.0f;              // Degrees, 0: facing -Z
	float m_AirSeconds = 0.0f;       // Since the player last stood on the ground
	float m_JumpCooldown = 0.0f;     // Seconds before another jump: the controller leaves the ground a step after Jump
	std::vector<glm::vec3> m_Checkpoints;
};
