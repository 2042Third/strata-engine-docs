#include <doctest/doctest.h>

#include "Editor/CommandJournal.h"
#include "Editor/EditorContext.h"
#include "Editor/HarnessEditor.h"
#include "Panels/SelectionSummaryPanel.h"

#include <Strata/Reflection/PropertyJson.h>
#include <Strata/Scene/Scene.h>

#include <nlohmann/json.hpp>

#include <algorithm>
#include <initializer_list>
#include <string>
#include <string_view>
#include <vector>

// The Selection Summary panel: what it counts and lists, its button, and its place in the default layout.

using namespace Strata;
using namespace Strata::Tests;

namespace
{

	// Entities for the summary: two lamps (a Point Light each, the first also tagged) and a tagged crate.
	void MakeEntities(HarnessEditor& editor)
	{
		editor.Run("entity.create", { { "name", "SummaryLamp" }, { "components", { { "PointLight", nlohmann::json::object() }, { "Tag", { { "Tag", "Prop" } } } } } });
		editor.Run("entity.create", { { "name", "SummaryTorch" }, { "components", { { "PointLight", nlohmann::json::object() } } } });
		editor.Run("entity.create", { { "name", "SummaryCrate" }, { "components", { { "Tag", { { "Tag", "Prop" } } } } } });
	}

	// Selects entities by name and draws the panel with them.
	void Select(HarnessEditor& editor, std::initializer_list<const char*> names)
	{
		nlohmann::json ids = nlohmann::json::array();
		for (const char* name : names)
		{
			const Entity entity = editor.Context().GetActiveScene()->FindEntityByName(name);
			REQUIRE(entity);
			ids.push_back(UUIDToJson(entity.GetUUID()));
		}
		editor.Run("selection.set", { { "entities", std::move(ids) } });
		editor.Frames(2);
	}

	bool Has(const std::vector<std::string>& names, std::string_view name)
	{
		return std::find(names.begin(), names.end(), name) != names.end();
	}

	// imgui.ini text as an editor saved it before this panel: no window and no open state of it, and layout version 5.
	std::string WithoutSummaryPanel(const std::string& settings)
	{
		std::string result;
		std::string section;
		size_t start = 0;
		while (start < settings.size())
		{
			const size_t end = settings.find('\n', start);
			const std::string line = settings.substr(start, end == std::string::npos ? std::string::npos : end - start);
			start = end == std::string::npos ? settings.size() : end + 1;
			if (line.starts_with("["))
				section = line;
			if (section == "[Window][SelectionSummary]" || (section == "[StrataPanels][Open]" && line.starts_with("SelectionSummary=")))
				continue;
			result += (section == "[StrataPanels][Layout]" && line.starts_with("Version=") ? "Version=5" : line) + "\n";
		}
		return result;
	}

}

TEST_SUITE("Editor.UI.SelectionSummary")
{
	TEST_CASE("The summary counts the selection and lists the components all of it has")
	{
		HarnessEditor editor({}, WithFeatureProject("SelectionSummary"));
		editor.Frames(2);
		REQUIRE(editor.Context().HasProject());
		MakeEntities(editor);
		editor.Run("editor.showPanel", { { "panel", "SelectionSummary" } });
		editor.Frames(2);
		const SelectionSummaryPanel* panel = editor.Layer->GetPanels().Get<SelectionSummaryPanel>(EditorPanels::c_SelectionSummary);
		REQUIRE(panel);

		editor.Run("selection.set", { { "entities", nlohmann::json::array() } });
		editor.Frames(2);
		CHECK(panel->GetSelectedCount() == 0);

		Select(editor, { "SummaryLamp", "SummaryTorch" });
		CHECK(panel->GetSelectedCount() == 2);
		CHECK(Has(panel->GetSharedComponents(), "Transform"));
		CHECK(Has(panel->GetSharedComponents(), "Point Light"));
		CHECK_FALSE(Has(panel->GetSharedComponents(), "Tag"));

		Select(editor, { "SummaryLamp", "SummaryCrate" });
		CHECK(panel->GetSelectedCount() == 2);
		CHECK(Has(panel->GetSharedComponents(), "Tag"));
		CHECK_FALSE(Has(panel->GetSharedComponents(), "Point Light"));

		// A component added through a command changes the undo history, so the lines follow it.
		editor.Run("component.add", { { "entity", UUIDToJson(editor.Context().GetActiveScene()->FindEntityByName("SummaryCrate").GetUUID()) }, { "component", "PointLight" } });
		editor.Frames(2);
		CHECK(Has(panel->GetSharedComponents(), "Point Light"));
	}

	TEST_CASE("The Frame button runs camera.focus as the person")
	{
		HarnessEditor editor({}, WithFeatureProject("SelectionSummaryButton"));
		editor.Frames(2);
		MakeEntities(editor);
		editor.Run("editor.showPanel", { { "panel", "SelectionSummary" } });
		Select(editor, { "SummaryLamp", "SummaryTorch" });

		const CommandJournal& journal = editor.Context().GetJournal();
		const uint64_t before = journal.GetLatestId();
		REQUIRE(editor.Click("SelectionSummary.Frame"));
		editor.Frames(1);

		const auto entry = std::find_if(journal.GetEntries().begin(), journal.GetEntries().end(),
			[before](const CommandJournalEntry& candidate) { return candidate.Id > before && candidate.Command == "camera.focus"; });
		REQUIRE(entry != journal.GetEntries().end());
		CHECK(entry->Source == CommandSource::UI);
		CHECK(entry->Parameters["entities"].size() == 2);
	}

	TEST_CASE("A layout saved before the panel gives way to the default layout, which docks it beside the Inspector")
	{
		std::string settings;
		{
			HarnessEditor editor({}, WithFeatureProject("SelectionSummaryLayout"));
			editor.Frames(3);
			size_t size = 0;
			settings = ImGui::SaveIniSettingsToMemory(&size);
		}
		REQUIRE(settings.find("[Window][SelectionSummary]") != std::string::npos);
		const std::string older = WithoutSummaryPanel(settings);
		REQUIRE(older.find("[Window][SelectionSummary]") == std::string::npos);
		REQUIRE(older.find("SelectionSummary=") == std::string::npos);
		REQUIRE(older.find("[StrataPanels][Layout]\nVersion=5\n") != std::string::npos);

		HarnessEditor editor({}, WithFeatureProject("SelectionSummaryLayoutReopened"), older);
		editor.Frames(3);
		ImGuiWindow* summary = editor.FindPanelWindow(EditorPanels::c_SelectionSummary);
		ImGuiWindow* inspector = editor.FindPanelWindow(EditorPanels::c_Inspector);
		REQUIRE(summary);
		REQUIRE(inspector);
		REQUIRE(inspector->DockNode);
		CHECK(editor.Layer->GetPanels().IsOpen(EditorPanels::c_SelectionSummary));
		CHECK(summary->DockNode == inspector->DockNode);
		// The current version is saved, so the default layout is built once.
		size_t size = 0;
		const std::string saved = ImGui::SaveIniSettingsToMemory(&size);
		CHECK(saved.find("[StrataPanels][Layout]\nVersion=" + std::to_string(EditorLayer::c_LayoutVersion)) != std::string::npos);
	}
}
