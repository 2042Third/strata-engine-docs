#include "StrataScript/StrataScript.h"

#include <cmath>

using namespace Strata;

// Follows its target from behind and above. This first version reads the target's world position.
class FollowCamera : public Script
{
public:
	Entity Target;                 // The entity to follow, set in the Inspector
	float Distance = 7.0f;         // Metres behind the pivot
	float Pitch = -20.0f;          // Degrees, negative looks down
	float PivotHeight = 1.5f;      // Metres above the target's feet
	float FollowSharpness = 14.0f; // How quickly the pivot follows the target (1/s)

	void OnCreate() override
	{
		if (Target.IsValid())
			m_Pivot = Target.GetTransform().GetWorldPosition() + glm::vec3(0.0f, PivotHeight, 0.0f);
		Place();
	}

	void OnLateUpdate(float deltaTime) override
	{
		if (!Target.IsValid())
			return;
		const glm::vec3 pivot = Target.GetTransform().GetWorldPosition() + glm::vec3(0.0f, PivotHeight, 0.0f);
		m_Pivot = glm::mix(m_Pivot, pivot, 1.0f - std::exp(-FollowSharpness * deltaTime));
		Place();
	}

private:
	void Place()
	{
		const glm::quat rotation = glm::angleAxis(glm::radians(Pitch), glm::vec3(1.0f, 0.0f, 0.0f));
		TransformComponent transform = GetTransform();
		transform.SetWorldPosition(m_Pivot + rotation * glm::vec3(0.0f, 0.0f, Distance));
		transform.SetWorldRotation(rotation);
	}

private:
	glm::vec3 m_Pivot = glm::vec3(0.0f);
};

ST_SCRIPT_CLASS(FollowCamera)
{
	ST_SCRIPT_FIELD(Target);
	ST_SCRIPT_FIELD(Distance);
	ST_SCRIPT_FIELD(Pitch);
	ST_SCRIPT_FIELD(PivotHeight);
	ST_SCRIPT_FIELD(FollowSharpness);
}
