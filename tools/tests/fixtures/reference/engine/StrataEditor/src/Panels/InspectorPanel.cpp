// A pretend engine file: literals of a panel (tools/tests/test_reference.py).
namespace Strata
{

	void InspectorPanel::Draw()
	{
		if (ImGui::Button("Add Component##inspector"))
			OpenPopup();
		ImGui::TextUnformatted("Create "
			"Child");
		ImGui::TextUnformatted(ICON_PLUS " Save ");
		ImGui::TextUnformatted("\xE2\x96\xB8 Next");
	}

}
