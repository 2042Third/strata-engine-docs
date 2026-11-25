#include "StrataScript/StrataScript.h"

using namespace Strata;

// Rolls the ball by pushing it: the Move action sets the direction, a force does the pushing.
class BallControl : public Script
{
public:
	float PushStrength = 12.0f; // Newtons at full push
	float MaxSpeed = 8.0f;      // Metres per second along the ground

	void OnUpdate(float) override
	{
		const glm::vec2 move = Input::GetActionValue("Gameplay/Move");
		m_Push = glm::vec3(move.x, 0.0f, -move.y);
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
	glm::vec3 m_Push = glm::vec3(0.0f);
};

ST_SCRIPT_CLASS(BallControl)
{
	ST_SCRIPT_FIELD(PushStrength);
	ST_SCRIPT_FIELD(MaxSpeed);
}
