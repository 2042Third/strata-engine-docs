#include "StrataScript/StrataScript.h"

#include <cmath>

using namespace Strata;

// Turns to face the cursor's place on the ground.
class Turret : public Script
{
public:
	void OnUpdate(float) override
	{
		glm::vec3 origin, direction;
		if (!GetPointerRay(origin, direction) || direction.y > -0.001f)
			return; // No camera, or the ray never reaches the ground
		const float rayLength = -origin.y / direction.y;
		const glm::vec3 hit = origin + direction * rayLength;
		const glm::vec3 position = GetTransform().GetWorldPosition();
		GetTransform().SetWorldRotation(Motion::LookAt(position, glm::vec3(hit.x, position.y, hit.z)));
	}

	// The ray from the camera through the cursor, in the world.
	bool GetPointerRay(glm::vec3& outOrigin, glm::vec3& outDirection) const
	{
		Entity camera = Scene::GetPrimaryCamera();
		const glm::uvec2 window = Game::GetWindowSize();
		const glm::vec2 mouse = Input::GetMousePosition();
		if (!camera || window.x == 0 || window.y == 0)
			return false;
		TransformComponent transform = camera.GetTransform();
		const float fov = glm::radians(camera.GetProperty<float>("Camera", "PerspectiveFOV").value_or(60.0f));
		const float aspect = static_cast<float>(window.x) / static_cast<float>(window.y);
		const float x = (2.0f * mouse.x / static_cast<float>(window.x) - 1.0f) * std::tan(fov * 0.5f) * aspect;
		const float y = (1.0f - 2.0f * mouse.y / static_cast<float>(window.y)) * std::tan(fov * 0.5f);
		outOrigin = transform.GetWorldPosition();
		outDirection = glm::normalize(transform.GetForward() + transform.GetRight() * x + transform.GetUp() * y);
		return true;
	}
};

ST_SCRIPT_CLASS(Turret)
{
}
