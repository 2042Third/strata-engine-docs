#include "Editor/CommandUtils.h"
#include "Editor/EditorCommands.h"
#include "Editor/EditorContext.h"
#include "Editor/SceneEdit.h"

#include <Strata/Physics/PhysicsComponents.h>
#include <Strata/Reflection/ComponentRegistry.h>
#include <Strata/Reflection/PropertyJson.h>
#include <Strata/Scene/Scene.h>

#include <nlohmann/json.hpp>

#include <optional>
#include <string>
#include <string_view>
#include <unordered_set>
#include <vector>

// The wind.* commands: what the scene's wind zones hold, and a change of several of them at once.

namespace Strata
{

	using namespace CommandUtils;

	namespace
	{

		const char* ToString(WindZoneMode mode)
		{
			return mode == WindZoneMode::Spherical ? "Spherical" : "Directional";
		}

		// The wind zone's registered properties: commands check values against them, so that a command accepts what the
		// Inspector accepts and refuses what lies outside a property's range.
		struct WindProperties
		{
			const PropertyInfo* Strength = nullptr;
			const PropertyInfo* Radius = nullptr;
			const PropertyInfo* Mode = nullptr;
		};

		std::optional<WindProperties> FindWindProperties()
		{
			const ComponentInfo* info = ComponentRegistry::Find<WindZoneComponent>();
			if (!info)
				return std::nullopt;
			const WindProperties properties { info->FindProperty("Strength"), info->FindProperty("Radius"), info->FindProperty("Mode") };
			if (!properties.Strength || !properties.Radius || !properties.Mode)
				return std::nullopt;
			return properties;
		}

		// An optional parameter, read through the property it sets. A value of the wrong type, outside the range or not one of
		// an enum's options is recorded as the first problem of the arguments.
		std::optional<PropertyValue> ReadValue(CommandArguments& arguments, const nlohmann::json& parameters, const char* name, const PropertyInfo& property)
		{
			if (!arguments.Has(name))
				return std::nullopt;
			std::string error;
			std::optional<PropertyValue> value = PropertyValueFromJson(property, parameters.at(name), &error);
			if (value && property.Type == PropertyType::Enum && !property.FindEnumValue(std::get<int32_t>(*value)))
			{
				error = "is not one of the options";
				value.reset();
			}
			if (value && !property.IsInRange(*value, &error))
				value.reset();
			if (!value)
				arguments.SetError(fmt::format("Parameter '{}' {}", name, error));
			return value;
		}

	}

	void RegisterWindCommands(EditorCommandRegistry& registry)
	{
		registry.Register({ "wind.list",
			"Lists every entity with a WindZone component, active or not: {zones: [{entity, name, active (the entity's own flag), strength "
			"(newtons), radius (meters), mode (\"Directional\" or \"Spherical\")}]}. Changes nothing; while playing it lists the running copy.",
			ObjectSchema({}),
			[](EditorContext& context, const nlohmann::json&)
			{
				Scene& scene = *context.GetActiveScene();
				nlohmann::json zones = nlohmann::json::array();
				for (const auto [handle, zone] : scene.GetRegistry().view<WindZoneComponent>().each())
				{
					const Entity entity(handle, &scene);
					zones.push_back({ { "entity", UUIDToJson(entity.GetUUID()) }, { "name", entity.GetName() }, { "active", entity.IsActive() },
						{ "strength", zone.Strength }, { "radius", zone.Radius }, { "mode", ToString(zone.Mode) } });
				}
				return EditorCommandResult::Ok({ { "zones", std::move(zones) } });
			}, EditorCommandKind::Query });

		registry.Register({ "wind.set",
			"Sets the strength, radius or mode of the WindZone of one or more entities in one undo step (while playing it changes the "
			"running copy only). Values left out stay as they are; at least one is required. Refuses, changing nothing, an entity without a "
			"WindZone and a value outside its property's range. Returns {entities}.",
			ObjectSchema({
				{ "entities", EntityArraySchema("Entities with a WindZone component") },
				{ "strength", NumberSchema("Force of the wind on a body, in newtons (within the range of the Strength property)") },
				{ "radius", NumberSchema("How far the zones reach from their center, in meters (within the range of the Radius property)") },
				{ "mode", { { "type", "string" }, { "enum", { "Directional", "Spherical" } },
					{ "description", "Directional zones blow one way through their radius, spherical zones outward from their center" } } } },
				{ "entities" }),
			[](EditorContext& context, const nlohmann::json& parameters)
			{
				Scene& scene = *context.GetActiveScene();
				const std::optional<WindProperties> properties = FindWindProperties();
				if (!properties)
					return EditorCommandResult::Fail("The WindZone component is not registered", EditorCommandError::Internal);

				CommandArguments arguments(parameters);
				const std::vector<Entity> entities = arguments.GetEntities(scene, "entities");
				const std::optional<PropertyValue> strength = ReadValue(arguments, parameters, "strength", *properties->Strength);
				const std::optional<PropertyValue> radius = ReadValue(arguments, parameters, "radius", *properties->Radius);
				const std::optional<PropertyValue> mode = ReadValue(arguments, parameters, "mode", *properties->Mode);
				if (!arguments.IsValid())
					return arguments.Fail();
				if (!strength && !radius && !mode)
					return EditorCommandResult::InvalidParameters("Give at least one of 'strength', 'radius' and 'mode'");
				for (const Entity entity : entities)
				{
					if (!entity.HasComponent<WindZoneComponent>())
						return EditorCommandResult::InvalidParameters(fmt::format("Parameter 'entities': '{}' has no WindZone component", entity.GetName()));
				}

				// Everything is checked: from here on the command changes the scene.
				std::vector<UUID> ids;
				std::unordered_set<UUID> seen;
				for (const Entity entity : entities)
				{
					if (seen.insert(entity.GetUUID()).second)
						ids.push_back(entity.GetUUID());
				}
				SceneEditTransaction transaction(scene, ids.size() == 1 ? fmt::format("Set the wind of {}", SceneEdit::QuoteName(entities.front().GetName())) :
					fmt::format("Set the wind of {} entities", ids.size()), ids);
				nlohmann::json changed = nlohmann::json::array();
				for (const UUID id : ids)
				{
					Entity entity = scene.GetEntityByUUID(id);
					WindZoneComponent& zone = entity.GetComponent<WindZoneComponent>();
					if (strength)
						zone.Strength = std::get<float>(*strength);
					if (radius)
						zone.Radius = std::get<float>(*radius);
					if (mode)
						zone.Mode = static_cast<WindZoneMode>(std::get<int32_t>(*mode));
					entity.MarkModified<WindZoneComponent>();
					changed.push_back(UUIDToJson(id));
				}
				return FinishEdit(context, transaction, { { "entities", std::move(changed) } });
			} });
	}

}
