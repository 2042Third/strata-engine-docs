// A pretend engine file: the editor layer's menu and its own command (tools/tests/test_reference.py).
namespace Strata
{

	void EditorLayer::OnAttach()
	{
		m_Commands.Register({ "editor.showPanel", "Shows a panel.",
			CommandUtils::ObjectSchema({ { "panel", CommandUtils::StringSchema("The panel") } }, { "panel" }),
			[this](EditorContext&, const nlohmann::json&) { return EditorCommandResult::Ok(); }, EditorCommandKind::Session,
			EditorCommandResults::Session });
		if (ImGui::BeginMenu("File"))
			ImGui::EndMenu();
	}

}
