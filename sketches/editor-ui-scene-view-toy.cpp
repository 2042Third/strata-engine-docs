// A toy Scene view: a pick that finishes frames later, and a gizmo drag that leaves one undo step.
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <optional>
#include <vector>

class ToyView
{
public:
	ToyView()
	{
		// The ID buffer of a one-row image, 20 pixels wide: entity index + 1 where a crate is drawn, 0 where nothing is.
		m_IdBuffer.assign(20, 0);
		for (size_t crate = 0; crate < m_Positions.size(); crate++)
			for (int pixel = static_cast<int>(m_Positions[crate]); pixel < static_cast<int>(m_Positions[crate]) + 4; pixel++)
				m_IdBuffer[static_cast<size_t>(pixel)] = static_cast<uint32_t>(crate + 1);
	}

	void RequestPick(int pixel)
	{
		// One pending pick: a newer click replaces it. The answer is ready two frames later, as a GPU readback would be.
		m_Pick = Pick { pixel, m_Frame + 2, m_Frame + 300, m_SceneVersion };
	}

	void ReplaceScene() { m_SceneVersion++; }

	void Update()
	{
		m_Frame++;
		if (!m_Pick || m_Frame < m_Pick->ReadyFrame)
		{
			if (m_Pick && m_Frame > m_Pick->TimeoutFrame)
				m_Pick.reset(); // The readback never finished: give up.
			return;
		}
		const Pick pick = *m_Pick;
		m_Pick.reset();
		if (pick.SceneVersion != m_SceneVersion)
		{
			std::printf("frame %d: the pick belongs to another scene, dropped\n", m_Frame);
			return;
		}
		const uint32_t id = m_IdBuffer[static_cast<size_t>(pick.Pixel)];
		m_Selected = id == 0 ? std::optional<size_t>() : std::optional<size_t>(id - 1);
		std::printf("frame %d: pixel %d selects %s\n", m_Frame, pick.Pixel, id == 0 ? "nothing" : "a crate");
	}

	void BeginDrag() { m_DragStart = m_Positions[*m_Selected]; }

	void UpdateDrag(float offset, float step)
	{
		// Always from the start state, so the result never drifts.
		const float snapped = step > 0.0f ? std::round(offset / step) * step : offset;
		m_Positions[*m_Selected] = *m_DragStart + snapped;
	}

	void EndDrag()
	{
		if (m_Positions[*m_Selected] != *m_DragStart)
			m_Undo.push_back({ *m_DragStart, m_Positions[*m_Selected] });
		m_DragStart.reset();
	}

	void Report() const
	{
		std::printf("position %.2f, undo steps %zu\n", m_Positions[*m_Selected], m_Undo.size());
	}

private:
	struct Pick
	{
		int Pixel = 0;
		int ReadyFrame = 0;
		int TimeoutFrame = 0;
		int SceneVersion = 0;
	};
	struct UndoStep
	{
		float Before = 0.0f;
		float After = 0.0f;
	};

	std::vector<uint32_t> m_IdBuffer;
	std::vector<float> m_Positions = { 2.0f, 10.0f };
	std::optional<Pick> m_Pick;
	std::optional<size_t> m_Selected;
	std::optional<float> m_DragStart;
	std::vector<UndoStep> m_Undo;
	int m_SceneVersion = 1;
	int m_Frame = 0;
};

int main()
{
	ToyView view;
	view.RequestPick(11);
	for (int frame = 0; frame < 3; frame++)
		view.Update();

	view.BeginDrag();
	for (const float offset : { 0.3f, 0.8f, 1.3f })
		view.UpdateDrag(offset, 0.5f);
	view.EndDrag();
	view.Report();

	view.RequestPick(3);
	view.ReplaceScene();
	for (int frame = 0; frame < 3; frame++)
		view.Update();
	return 0;
}
