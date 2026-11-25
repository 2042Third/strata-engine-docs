// A pretend engine file in the shape of the engine's command registrations (tools/tests/test_reference.py).
#include "Editor/EditorCommands.h"

namespace Strata
{

	EditorCommandRegistry::EditorCommandRegistry()
	{
		RegisterSceneCommands(*this);

		Register({ "editor.commands",
			"Every editor command with its description and the schema of its parameters.",
			CommandUtils::ObjectSchema({}),
			[this](EditorContext&, const nlohmann::json&)
			{
				return EditorCommandResult::Ok({ { "commands", nlohmann::json::array() } });
			}, EditorCommandKind::Query });
	}

	void RegisterEntityCommands(EditorCommandRegistry& registry)
	{
		registry.Register({ "entity.create", "Creates an entity. "
			"Returns its ID.",
			ObjectSchema({ { "name", StringSchema("Entity name") } }),
			[](EditorContext& context, const nlohmann::json& parameters)
			{
				return EditorCommandResult::Ok({ { "id", "1" } });
			} });

		registry.Register({ "asset.list", "The assets of the project.",
			ObjectSchema({}),
			[](EditorContext& context, const nlohmann::json&) { return EditorCommandResult::Ok(); },
			EditorCommandKind::Query, EditorCommandResults::Content, true });

		// Not a command: a settings section registry.
		registry.Register(ExternalEditor::MakeSettingsSection());
	}

}
