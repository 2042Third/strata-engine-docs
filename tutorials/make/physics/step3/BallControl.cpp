#include "StrataScript/StrataScript.h"

using namespace Strata;

// Rolls the ball with a force, puts it back with R and jumps with an impulse when it stands on something.
class BallControl : public Script
{
public:
	float PushStrength = 12.0f; // Newtons at full push
	float MaxSpeed = 8.0f;      // Metres per second along the ground
	float JumpImpulse = 5.0f;   // Added speed in metres per second for a mass of 1
	float GroundReach = 0.6f;   // How far below its centre the ball looks for ground, in metres

	void OnCreate() override
	{
		m_StartPosition = GetTransform().GetWorldPosition();
	}

	void OnUpdate(float) override
	{
		const glm::vec2 move = Input::GetActionValue("Gameplay/Move");
		m_Push = glm::vec3(move.x, 0.0f, -move.y);

		RigidBody body = GetEntity().GetRigidBody();
		if (Input::IsKeyPressed(Key::R))
		{
			body.Teleport(m_StartPosition);
			body.SetLinearVelocity(glm::vec3(0.0f));
			body.SetAngularVelocity(glm::vec3(0.0f));
		}
		if (Input::IsActionPressed("Gameplay/Jump") && IsOnGround())
			body.AddImpulse(glm::vec3(0.0f, JumpImpulse, 0.0f));
	}

	void OnFixedUpdate(float) override
	{
		RigidBody body = GetEntity().GetRigidBody();
		const glm::vec3 velocity = body.GetLinearVelocity();
		const float groundSpeed = glm::length(glm::vec3(velocity.x, 0.0f, velocity.z));
		if (groundSpeed < MaxSpeed)
			body.AddForce(m_Push * PushStrength);
	}
private:
	bool IsOnGround() const
	{
		const glm::vec3 origin = GetTransform().GetWorldPosition();
		const glm::vec3 down = glm::vec3(0.0f, -1.0f, 0.0f);
		return Physics::Raycast(origin, down, GroundReach, Physics::c_AllLayers, GetEntity()).has_value();
	}

	glm::vec3 m_StartPosition = glm::vec3(0.0f);
	glm::vec3 m_Push = glm::vec3(0.0f);
};

ST_SCRIPT_CLASS(BallControl)
{
	ST_SCRIPT_FIELD(PushStrength);
	ST_SCRIPT_FIELD(MaxSpeed);
	ST_SCRIPT_FIELD(JumpImpulse);
	ST_SCRIPT_FIELD(GroundReach);
}
