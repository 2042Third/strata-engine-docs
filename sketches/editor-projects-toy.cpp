#include <algorithm>
#include <cstdio>
#include <string>

struct Scene
{
	std::string Name;
	int Entities = 0;
};

struct SceneLoad
{
	int Id = 0;
	Scene Result;
	int Created = 0;

	bool IsDone() const { return Created >= Result.Entities; }
};

class ToyEditor
{
public:
	void BeginOpenScene(const std::string& name, int entities)
	{
		// A newer request replaces the load under way.
		if (m_Loading)
			std::printf("  request %d cancelled\n", m_Load.Id);
		m_Load = { m_NextId++, { name, entities }, 0 };
		m_Loading = true;
	}

	bool TryEdit() const
	{
		// The scene on screen is read-only while another one is being opened.
		if (m_Loading)
		{
			std::printf("  edit refused: '%s' is being opened (%d%%)\n", m_Load.Result.Name.c_str(),
				m_Load.Created * 100 / m_Load.Result.Entities);
			return false;
		}
		std::printf("  edit applied to '%s'\n", m_Shown.Name.c_str());
		return true;
	}

	// One call per frame, before anything is drawn: the swap happens between two frames.
	void Update(int entitiesPerFrame)
	{
		if (!m_Loading)
			return;
		m_Load.Created = std::min(m_Load.Created + entitiesPerFrame, m_Load.Result.Entities);
		if (!m_Load.IsDone())
			return;
		m_Shown = m_Load.Result;
		m_Loading = false;
		std::printf("  request %d swapped in: '%s', %d entities\n", m_Load.Id, m_Shown.Name.c_str(), m_Shown.Entities);
	}

private:
	Scene m_Shown = { "Blank", 0 };
	SceneLoad m_Load;
	bool m_Loading = false;
	int m_NextId = 1;
};

int main()
{
	ToyEditor editor;
	for (int frame = 0; frame < 5; frame++)
	{
		std::printf("frame %d\n", frame);
		editor.Update(1000);
		if (frame == 0)
			editor.BeginOpenScene("Big", 2500);
		if (frame == 1)
			editor.TryEdit();
		if (frame == 2)
			editor.BeginOpenScene("Small", 1000);
		if (frame == 4)
			editor.TryEdit();
	}
}
