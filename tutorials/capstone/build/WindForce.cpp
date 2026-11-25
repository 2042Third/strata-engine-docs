#include "stpch.h"
#include "Strata/Physics/WindForce.h"

#include "Strata/Scene/Entity.h"
#include "Strata/Scene/Scene.h"

#include <cmath>

namespace Strata
{

	namespace
	{

		// Below this length a world transform's Z axis has no direction (a scale of nearly zero).
		constexpr float c_MinAxisLength = 1.0e-6f;

		bool IsFinite(const glm::vec3& value)
		{
			return std::isfinite(value.x) && std::isfinite(value.y) && std::isfinite(value.z);
		}

	}

	std::vector<WindZoneSample> GatherWindZones(Scene& scene)
	{
		std::vector<WindZoneSample> zones;
		for (const auto [handle, zone] : scene.GetRegistry().view<WindZoneComponent>().each())
		{
			const Entity entity(handle, &scene);
			if (!scene.IsActiveInHierarchy(entity))
				continue;

			// Reading the world transform changes nothing, so the transform contract asks for no signal.
			const glm::mat4 world = scene.GetWorldTransform(entity);
			zones.push_back({ handle, glm::vec3(world[3]), world, zone.Strength, zone.Radius, zone.Mode });
		}
		return zones;
	}

	glm::vec3 GetWindForce(const WindZoneSample& zone, const glm::vec3& position)
	{
		if (!(zone.Strength > 0.0f) || !std::isfinite(zone.Strength) || !IsFinite(position))
			return glm::vec3(0.0f);

		if (zone.Mode == WindZoneMode::Directional)
		{
			// -Z is forward. Dividing by the axis' length keeps the scale of the entity out of the strength.
			const glm::vec3 axis = -glm::vec3(zone.World[2]);
			const float length = glm::length(axis);
			if (!IsFinite(axis) || !(length > c_MinAxisLength))
				return glm::vec3(0.0f);
			return axis / length * zone.Strength;
		}

		const glm::vec3 offset = position - zone.Position;
		const float distance = glm::length(offset);
		if (!(distance > 0.0f) || !(distance <= zone.Radius) || !std::isfinite(distance))
			return glm::vec3(0.0f);
		return offset / distance * zone.Strength;
	}

	glm::vec3 GetWindForceAt(std::span<const WindZoneSample> zones, const glm::vec3& position)
	{
		glm::vec3 force(0.0f);
		for (const WindZoneSample& zone : zones)
			force += GetWindForce(zone, position);
		return force;
	}

	glm::vec3 GetWindForceAt(Scene& scene, const glm::vec3& position)
	{
		return GetWindForceAt(GatherWindZones(scene), position);
	}

}
