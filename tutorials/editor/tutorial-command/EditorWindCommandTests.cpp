#include <doctest/doctest.h>

#include "Editor/CommandTestUtils.h"
#include "Editor/EditorCommands.h"
#include "Editor/EditorContext.h"

#include <Strata/Physics/PhysicsComponents.h>
#include <Strata/Reflection/PropertyJson.h>
#include <Strata/Scene/Entity.h>
#include <Strata/Scene/Scene.h>

#include <nlohmann/json.hpp>

#include <initializer_list>
#include <string_view>

using namespace Strata;

namespace
{

	struct WindHarness
	{
		EditorContext Context;
		EditorCommandRegistry Commands;

		EditorCommandResult Execute(std::string_view name, const nlohmann::json& parameters = nlohmann::json::object())
		{
			return Tests::CompleteCommand(Context, Commands.Execute(Context, name, parameters));
		}

		Scene& GetScene() { return *Context.GetActiveScene(); }

		// A zone made directly in the scene: no undo step records it.
		Entity AddZone(const char* name, float strength, float radius)
		{
			Entity zone = GetScene().CreateEntity(name);
			WindZoneComponent& wind = zone.AddComponent<WindZoneComponent>();
			wind.Strength = strength;
			wind.Radius = radius;
			return zone;
		}

		// A JSON array of entity IDs, as the entities parameter takes them.
		static nlohmann::json Ids(std::initializer_list<UUID> ids)
		{
			nlohmann::json array = nlohmann::json::array();
			for (const UUID id : ids)
				array.push_back(UUIDToJson(id));
			return array;
		}

		const WindZoneComponent& Wind(UUID id)
		{
			return GetScene().GetEntityByUUID(id).GetComponent<WindZoneComponent>();
		}
	};

}

TEST_SUITE("Editor.WindCommands")
{
	TEST_CASE("wind.list answers every zone with its values, and changes nothing")
	{
		WindHarness harness;
		const Entity breeze = harness.AddZone("Breeze", 10.0f, 5.0f);
		harness.AddZone("Gust", 25.0f, 8.5f);
		harness.GetScene().CreateEntity("Rock");

		const EditorCommandResult result = harness.Execute("wind.list");
		REQUIRE(result.Success);
		const nlohmann::json& zones = result.Value["zones"];
		REQUIRE(zones.size() == 2);
		for (const nlohmann::json& zone : zones)
		{
			CAPTURE(zone);
			if (zone["name"] == "Breeze")
			{
				CHECK(zone["entity"] == UUIDToJson(breeze.GetUUID()));
				CHECK(zone["strength"] == 10.0);
				CHECK(zone["mode"] == "Directional");
			}
			else
			{
				CHECK(zone["name"] == "Gust");
				CHECK(zone["radius"] == 8.5);
			}
		}
		CHECK_FALSE(harness.Execute("edit.undo").Success);
	}

	TEST_CASE("wind.set changes several zones in one undo step")
	{
		WindHarness harness;
		const UUID breeze = harness.AddZone("Breeze", 10.0f, 5.0f).GetUUID();
		const UUID gust = harness.AddZone("Gust", 25.0f, 8.5f).GetUUID();

		const EditorCommandResult result = harness.Execute("wind.set", { { "entities", WindHarness::Ids({ breeze, gust }) },
			{ "strength", 40.0 }, { "mode", "Spherical" } });
		REQUIRE(result.Success);
		CHECK(result.Value["entities"].size() == 2);
		for (const UUID id : { breeze, gust })
		{
			CHECK(harness.Wind(id).Strength == doctest::Approx(40.0f));
			CHECK(harness.Wind(id).Mode == WindZoneMode::Spherical);
		}
		CHECK(harness.Wind(breeze).Radius == doctest::Approx(5.0f)); // Left out: unchanged
		CHECK(harness.Wind(gust).Radius == doctest::Approx(8.5f));

		REQUIRE(harness.Execute("edit.undo").Success);
		CHECK(harness.Wind(breeze).Strength == doctest::Approx(10.0f));
		CHECK(harness.Wind(gust).Strength == doctest::Approx(25.0f));
		CHECK(harness.Wind(gust).Mode == WindZoneMode::Directional);
		// One step held both zones: nothing is left to undo.
		CHECK_FALSE(harness.Execute("edit.undo").Success);
	}

	TEST_CASE("wind.set refuses invalid input and changes nothing")
	{
		WindHarness harness;
		const UUID breeze = harness.AddZone("Breeze", 10.0f, 5.0f).GetUUID();
		const UUID rock = harness.GetScene().CreateEntity("Rock").GetUUID();
		const nlohmann::json one = WindHarness::Ids({ breeze });
		const nlohmann::json both = WindHarness::Ids({ breeze, rock });

		const auto refused = [&harness](const nlohmann::json& parameters)
		{
			CAPTURE(parameters);
			const EditorCommandResult result = harness.Execute("wind.set", parameters);
			CHECK_FALSE(result.Success);
			CHECK(result.ErrorKind == EditorCommandError::InvalidParameters);
		};
		refused({ { "entities", one }, { "strength", 5000.0 } });                  // Above the range
		refused({ { "entities", one }, { "strength", 20.0 }, { "radius", 0.0 } });  // The second value is invalid
		refused({ { "entities", one }, { "mode", "Sideways" } });                  // Not an option
		refused({ { "entities", one }, { "strength", "strong" } });                // Not a number
		refused({ { "entities", one } });                                          // No value to set
		refused({ { "entities", both }, { "strength", 20.0 } });                   // One entity has no zone
		refused({ { "strength", 20.0 } });                                         // No entities

		CHECK(harness.Wind(breeze).Strength == doctest::Approx(10.0f));
		CHECK(harness.Wind(breeze).Radius == doctest::Approx(5.0f));
		CHECK_FALSE(harness.Execute("edit.undo").Success);
	}

	TEST_CASE("wind.set while playing changes the running copy and says so")
	{
		WindHarness harness;
		const UUID breeze = harness.AddZone("Breeze", 10.0f, 5.0f).GetUUID();
		REQUIRE(harness.Execute("play.start").Success);

		const EditorCommandResult result = harness.Execute("wind.set", { { "entities", WindHarness::Ids({ breeze }) },
			{ "strength", 40.0 } });
		REQUIRE(result.Success);
		CHECK(result.RunningCopy);
		CHECK(result.Value.contains("warning"));
		CHECK(harness.Wind(breeze).Strength == doctest::Approx(40.0f));

		REQUIRE(harness.Execute("play.stop").Success);
		CHECK(harness.Wind(breeze).Strength == doctest::Approx(10.0f));
	}
}
