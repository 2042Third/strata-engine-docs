#include "StrataScript/StrataScript.h"

using namespace Strata;

class PlayerAnimation : public Script
{
public:
	Entity Robot; // The model with the Animator

	void OnUpdate(float) override
	{
		const CharacterController controller = GetEntity().GetCharacterController();
		const glm::vec3 velocity = controller.GetVelocity();
		const bool grounded = controller.IsGrounded();
		Animator animator = Robot.GetAnimator();
		// Set the trigger once, on the update the player leaves the ground going up.
		if (m_WasGrounded && !grounded && velocity.y > 0.5f)
			animator.SetTrigger("Jump");
		m_WasGrounded = grounded;
		animator.SetFloat("Speed", glm::length(glm::vec2(velocity.x, velocity.z)));
		animator.SetBool("Grounded", grounded);
	}
private:
	bool m_WasGrounded = true;
};

ST_SCRIPT_CLASS(PlayerAnimation)
{
	ST_SCRIPT_FIELD(Robot);
}
