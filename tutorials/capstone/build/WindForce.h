#pragma once

#include "Strata/Physics/PhysicsComponents.h"

#include <entt/entt.hpp>
#include <glm/glm.hpp>

#include <span>
#include <vector>

namespace Strata
{

	class Scene;

	// One wind zone as the wind code reads it: the component's values and where the zone stands in the world.
	struct WindZoneSample
	{
		entt::entity Handle = entt::null;
		glm::vec3 Position = { 0.0f, 0.0f, 0.0f }; // The zone's center in world space
		glm::mat4 World = glm::mat4(1.0f);         // The zone's world transform: its rotation turns a directional zone's wind
		float Strength = 0.0f;                     // Newtons
		float Radius = 0.0f;                       // Meters, never scaled by the entity's scale
		WindZoneMode Mode = WindZoneMode::Directional;
	};

	// The scene's zones that are active in the hierarchy, in the order of the registry. Reads the world transforms the scene
	// caches: call Scene::UpdateWorldTransforms first when the scene was edited.
	std::vector<WindZoneSample> GatherWindZones(Scene& scene);

	// The force, in newtons, that one zone applies at a world position.
	// Directional: Strength along the zone's local -Z (Strata's forward) turned by its world rotation, everywhere.
	// Spherical: Strength away from the center within Radius of it, and nothing at the center itself or outside.
	// A zone whose transform has no direction, a zone without strength and a position that is not finite give no force.
	glm::vec3 GetWindForce(const WindZoneSample& zone, const glm::vec3& position);

	// The sum of the forces of the zones at a world position.
	glm::vec3 GetWindForceAt(std::span<const WindZoneSample> zones, const glm::vec3& position);

	// The same sum over the active zones of a scene, read now: it works while the scene is edited, when no system runs.
	glm::vec3 GetWindForceAt(Scene& scene, const glm::vec3& position);

}
