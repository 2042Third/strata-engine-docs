#pragma once

#include "UI/EditorPanelRegistry.h"

#include <cstdint>
#include <string>
#include <vector>

namespace Strata
{

	class Scene;

	// The selected entities in one glance: how many there are, which components all of them have, and a button that
	// frames them in the Scene view (camera.focus). The lines are rebuilt when the selection, the undo history or the
	// scene changes; an idle frame compares three numbers.
	class SelectionSummaryPanel : public EditorPanel
	{
	public:
		void OnImGuiRender(EditorPanelContext& panelContext) override;

		// What the last drawn frame showed (for tests).
		size_t GetSelectedCount() const { return m_SelectedCount; }
		const std::vector<std::string>& GetSharedComponents() const { return m_SharedComponents; }
	private:
		void Rebuild(EditorContext& context);
		void FrameSelection(EditorPanelContext& panelContext) const;
	private:
		size_t m_SelectedCount = 0;
		std::vector<std::string> m_SharedComponents; // Display names, in registration order

		// What the lines were built from.
		const Scene* m_Scene = nullptr;
		uint64_t m_SelectionVersion = UINT64_MAX;
		uint64_t m_HistoryVersion = UINT64_MAX;
	};

}
