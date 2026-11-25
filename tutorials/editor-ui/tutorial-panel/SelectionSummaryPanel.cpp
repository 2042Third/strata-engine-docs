#include "Panels/SelectionSummaryPanel.h"

#include "Editor/EditorContext.h"
#include "Editor/UndoStack.h"
#include "UI/EditorActions.h"
#include "UI/Icons.h"
#include "UI/Theme.h"
#include "UI/Widgets.h"

#include <Strata/Reflection/ComponentRegistry.h>
#include <Strata/Reflection/PropertyJson.h>
#include <Strata/Scene/Entity.h>
#include <Strata/Scene/Scene.h>

#include <imgui.h>
#include <nlohmann/json.hpp>
#include <spdlog/fmt/fmt.h>

#include <algorithm>
#include <utility>

namespace Strata
{

	void SelectionSummaryPanel::Rebuild(EditorContext& context)
	{
		m_SelectedCount = 0;
		m_SharedComponents.clear();
		const Ref<Scene>& scene = context.GetActiveScene();
		if (!scene)
			return;

		// Selected entities that no longer exist (deleted since) do not count.
		std::vector<Entity> entities;
		entities.reserve(context.GetSelection().size());
		for (const UUID id : context.GetSelection())
		{
			if (Entity entity = scene->GetEntityByUUID(id))
				entities.push_back(entity);
		}
		m_SelectedCount = entities.size();
		if (entities.empty())
			return;

		const entt::registry& registry = scene->GetRegistry();
		for (const ComponentInfo* info : ComponentRegistry::GetAll())
		{
			if (info->IsHidden())
				continue;
			const bool onAll = std::all_of(entities.begin(), entities.end(),
				[&](const Entity& entity) { return info->Has(registry, entity.GetHandle()); });
			if (onAll)
				m_SharedComponents.push_back(info->DisplayName);
		}
	}

	void SelectionSummaryPanel::FrameSelection(EditorPanelContext& panelContext) const
	{
		nlohmann::json entities = nlohmann::json::array();
		for (const UUID id : panelContext.Context.GetSelection())
			entities.push_back(UUIDToJson(id));
		// RunEditorCommand runs the command as the person's: the activity journal records the UI as its source.
		RunEditorCommand(panelContext.Context, panelContext.Commands, "camera.focus", { { "entities", std::move(entities) } });
	}

	void SelectionSummaryPanel::OnImGuiRender(EditorPanelContext& panelContext)
	{
		EditorContext& context = panelContext.Context;
		const UI::ThemeColors& colors = UI::GetThemeColors();

		const Scene* scene = context.GetActiveScene().get();
		const uint64_t selectionVersion = context.GetSelectionVersion();
		const uint64_t historyVersion = context.GetUndoStack().GetVersion();
		if (scene != m_Scene || selectionVersion != m_SelectionVersion || historyVersion != m_HistoryVersion)
		{
			Rebuild(context);
			m_Scene = scene;
			m_SelectionVersion = selectionVersion;
			m_HistoryVersion = historyVersion;
		}

		if (m_SelectedCount == 0)
		{
			UI::CenteredText("SelectionSummary.Empty", "Select entities in the Hierarchy or the Scene view to summarize them.", colors.TextSecondary);
			return;
		}

		ImGui::TextUnformatted(fmt::format("{} {} selected", m_SelectedCount, m_SelectedCount == 1 ? "entity" : "entities").c_str());
		ImGui::TextColored(colors.TextSecondary, "Components all of them have");
		for (const std::string& name : m_SharedComponents)
			ImGui::BulletText("%s", name.c_str());

		ImGui::Spacing();
		UI::ButtonStyle style;
		style.Primary = true;
		if (UI::ActionButton("SelectionSummary.Frame", Icons::Focus, "Frame selection", "Point the Scene view at the selected entities", style))
			FrameSelection(panelContext);
	}

}
