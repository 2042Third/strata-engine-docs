#include "StrataScript/StrataScript.h"

#include <algorithm>
#include <cmath>
#include <optional>

using namespace Strata;

// Orbits its target with the mouse or the Look action, follows it as drawn, and shortens its arm where a wall is in the way.
class FollowCamera : public Script
{
public:
	Entity Target;                   // The entity to follow, set in the Inspector
	float Distance = 6.5f;           // Metres from the pivot when nothing is in the way
	float Yaw = 0.0f;                // Degrees about +Y, 0 looks along -Z
	float Pitch = -18.0f;            // Degrees, negative looks down
	float MinPitch = -70.0f;
	float MaxPitch = 35.0f;
	float MouseDegreesPerPixel = 0.12f;
	float StickDegreesPerSecond = 160.0f;
	float PivotHeight = 1.5f;        // Metres above the target's feet
	float FollowSharpness = 14.0f;   // How quickly the pivot follows the target (1/s)
	float WallMargin = 0.3f;         // Metres kept between the camera and a wall
	float ArmReturnSharpness = 6.0f; // How quickly the arm grows back (1/s)

	void OnCreate() override
	{
		Input::SetCursorMode(CursorMode::Locked);
		if (Target.IsValid())
			m_Pivot = Target.GetTransform().GetDrawnPosition() + glm::vec3(0.0f, PivotHeight, 0.0f);
		Place(0.0f);
	}

	void OnDestroy() override
	{
		Input::SetCursorMode(CursorMode::Normal);
	}

	void OnLateUpdate(float deltaTime) override
	{
		const glm::vec2 mouse = Input::GetMouseDelta();
		const glm::vec2 look = Input::GetActionValue("Gameplay/Look");
		Yaw -= mouse.x * MouseDegreesPerPixel + look.x * StickDegreesPerSecond * deltaTime;
		Pitch -= mouse.y * MouseDegreesPerPixel - look.y * StickDegreesPerSecond * deltaTime;
		Pitch = std::clamp(Pitch, MinPitch, MaxPitch);

		if (Target.IsValid())
		{
			const glm::vec3 pivot = Target.GetTransform().GetDrawnPosition() + glm::vec3(0.0f, PivotHeight, 0.0f);
			if (glm::length(pivot - m_Pivot) > 8.0f)
				m_Pivot = pivot; // A respawn: no slide across the course
			else
				m_Pivot = glm::mix(m_Pivot, pivot, 1.0f - std::exp(-FollowSharpness * deltaTime));
		}
		Place(deltaTime);
	}

private:
	// deltaTime 0 puts the arm at its free length at once.
	void Place(float deltaTime)
	{
		const glm::quat rotation = glm::angleAxis(glm::radians(Yaw), glm::vec3(0.0f, 1.0f, 0.0f)) * glm::angleAxis(glm::radians(Pitch), glm::vec3(1.0f, 0.0f, 0.0f));
		const glm::vec3 back = rotation * glm::vec3(0.0f, 0.0f, 1.0f);
		float free = Distance;
		if (const std::optional<RaycastHit> hit = Physics::Raycast(m_Pivot, back, Distance + WallMargin, Physics::c_AllLayers, Target))
			free = std::max(0.4f, hit->Distance - WallMargin);
		if (free <= m_ArmLength || deltaTime <= 0.0f)
			m_ArmLength = free; // In at once, so that a wall never hides the player
		else
			m_ArmLength += (free - m_ArmLength) * (1.0f - std::exp(-ArmReturnSharpness * deltaTime));
		TransformComponent transform = GetTransform();
		transform.SetWorldPosition(m_Pivot + back * m_ArmLength);
		transform.SetWorldRotation(rotation);
	}

private:
	glm::vec3 m_Pivot = glm::vec3(0.0f);
	float m_ArmLength = 0.0f;
};

ST_SCRIPT_CLASS(FollowCamera)
{
	ST_SCRIPT_FIELD(Target);
	ST_SCRIPT_FIELD(Distance);
	ST_SCRIPT_FIELD(Yaw);
	ST_SCRIPT_FIELD(Pitch);
	ST_SCRIPT_FIELD(MinPitch);
	ST_SCRIPT_FIELD(MaxPitch);
	ST_SCRIPT_FIELD(MouseDegreesPerPixel);
	ST_SCRIPT_FIELD(StickDegreesPerSecond);
	ST_SCRIPT_FIELD(PivotHeight);
	ST_SCRIPT_FIELD(FollowSharpness);
	ST_SCRIPT_FIELD(WallMargin);
	ST_SCRIPT_FIELD(ArmReturnSharpness);
}
