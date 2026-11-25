// A pretend engine file: commands that answer later (tools/tests/test_reference.py).
namespace Strata
{

	void RegisterSceneCommands(EditorCommandRegistry& registry)
	{
		registry.Register(MayDefer({ "scene.open",
			"Opens a scene asset for editing.",
			ObjectSchema({ { "scene", StringSchema("The scene") }, { "force", BoolSchema("Discard changes") } }),
			AfterSaves([](EditorContext& context, const nlohmann::json& parameters)
			{
				return EditorCommandResult::Ok({ { "opened", true } });
			}), EditorCommandKind::Session }));
	}

}
