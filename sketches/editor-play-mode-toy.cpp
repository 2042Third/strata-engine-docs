#include <cstdio>
#include <optional>
#include <utility>
#include <vector>

struct Light
{
	float Intensity = 3.0f;
};

struct Scene
{
	std::vector<Light> Lights;
};

class ToyEditor
{
public:
	explicit ToyEditor(Scene scene)
		: m_EditScene(std::move(scene))
	{
	}

	bool IsPlaying() const { return m_RuntimeScene.has_value(); }
	size_t GetUndoSteps() const { return m_UndoSteps; }
	float GetMasterVolume() const { return m_MasterVolume; }
	void SetMasterVolume(float volume) { m_MasterVolume = volume; }
	const Scene& GetEditScene() const { return m_EditScene; }

	// The scene that commands act on: the running copy while it exists, else the edited scene.
	Scene& GetActiveScene() { return m_RuntimeScene ? *m_RuntimeScene : m_EditScene; }

	bool Play()
	{
		if (IsPlaying())
			return false;
		m_VolumeBeforePlay = m_MasterVolume;
		m_RuntimeScene = m_EditScene; // The copy: from here on the two scenes share nothing
		return true;
	}

	void Stop()
	{
		m_RuntimeScene.reset(); // Everything the game did to its copy goes with it
		m_MasterVolume = m_VolumeBeforePlay;
	}

	// A command that sets a light's intensity. Edits are recorded for undo; edits of the running copy are not.
	const char* SetIntensity(size_t index, float intensity)
	{
		GetActiveScene().Lights[index].Intensity = intensity;
		if (IsPlaying())
			return "warning: applies to the running copy and is discarded by Stop";
		m_UndoSteps++;
		return "ok";
	}
private:
	Scene m_EditScene;
	std::optional<Scene> m_RuntimeScene;
	size_t m_UndoSteps = 0;
	float m_MasterVolume = 1.0f;
	float m_VolumeBeforePlay = 1.0f;
};

int main()
{
	ToyEditor editor(Scene { { Light {} } });
	std::printf("edit:  %s\n", editor.SetIntensity(0, 5.0f));
	editor.Play();
	editor.SetMasterVolume(0.2f); // The game's own volume setting
	std::printf("play:  %s\n", editor.SetIntensity(0, 20.0f));
	std::printf("running copy %.1f, edited scene %.1f\n", editor.GetActiveScene().Lights[0].Intensity, editor.GetEditScene().Lights[0].Intensity);
	editor.Stop();
	std::printf("stopped: intensity %.1f, undo steps %zu, volume %.1f\n", editor.GetActiveScene().Lights[0].Intensity, editor.GetUndoSteps(),
		editor.GetMasterVolume());
	return 0;
}
