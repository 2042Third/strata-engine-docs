// A pretend engine file: a capture and the asset statistics (tools/tests/test_reference.py).
namespace Strata
{

	void RegisterViewportCommands(EditorCommandRegistry& registry)
	{
		registry.Register(MayDefer({ "viewport.capture", "Renders the scene and returns the picture.",
			ObjectSchema({ { "debugView", EnumSchema("A debug view", c_DebugViews) } }),
			[](EditorContext& context, const nlohmann::json& parameters) { return EditorCommandResult::Ok(); },
			EditorCommandKind::Query, EditorCommandResults::Session }));
		registry.Register({ "asset.stats", "Asset memory and streaming: resident bytes per pool.",
			ObjectSchema({}),
			[](EditorContext& context, const nlohmann::json&) { return EditorCommandResult::Ok(); },
			EditorCommandKind::Query, EditorCommandResults::Session });
		registry.Register({ "asset.setBudget", "Sets a pool's budget.",
			ObjectSchema({ { "pool", StringSchema("The pool") } }, { "pool" }),
			[](EditorContext& context, const nlohmann::json&) { return EditorCommandResult::Ok(); },
			EditorCommandKind::Session });
	}

}
