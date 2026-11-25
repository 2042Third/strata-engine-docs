// A pretend engine file in the shape of the MCP toolsets (tools/tests/test_reference.py).
namespace Strata::CLI::McpToolsets
{

	namespace
	{

		constexpr std::string_view c_CoreCommands[] = {
			"editor.commands", "entity.create" };

		constexpr std::pair<std::string_view, std::string_view> c_ExactToolsets[] = {
			{ "asset.list", "streaming" } };

		constexpr std::pair<std::string_view, std::string_view> c_PrefixToolsets[] = {
			{ "scene.", "scene" }, { "entity.", "scene" }, { "asset.", "assets" } };

		constexpr ToolsetInfo c_Toolsets[] = {
			{ "core", "Making and testing a game" },
			{ "scene", "Scenes and entities" },
			{ "assets", "Assets" },
			{ "streaming", "Residency" } };

	}

}
