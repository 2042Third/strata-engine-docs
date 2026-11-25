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
		Animator animator = Robot.GetAnimator();
		animator.SetFloat("Speed", glm::length(glm::vec2(velocity.x, velocity.z)));
		animator.SetBool("Grounded", controller.IsGrounded());
	}
};

ST_SCRIPT_CLASS(PlayerAnimation)
{
	ST_SCRIPT_FIELD(Robot);
}
