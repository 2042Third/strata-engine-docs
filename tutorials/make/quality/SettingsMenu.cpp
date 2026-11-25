#include "StrataScript/StrataScript.h"

#include <optional>
#include <string>

using namespace Strata;

// The settings screen: volume, window mode, resolution, vsync and the Graphics row.
class SettingsMenu : public Script
{
public:
	Entity VolumeSlider;
	Entity GraphicsLow;
	Entity GraphicsMedium;
	Entity GraphicsHigh;
	Entity GraphicsUltra;

	void OnCreate() override
	{
		// Values set from code raise no OnUIValueChanged, so showing the volume and the preset sets nothing.
		if (VolumeSlider.IsValid())
			VolumeSlider.GetUI().SetValue(Audio::GetMasterVolume());
		// The preset in effect switches its toggle on; a Custom preset switches none on.
		const std::optional<QualityPreset> preset = Graphics::GetPreset();
		for (const Entity toggle : { GraphicsLow, GraphicsMedium, GraphicsHigh, GraphicsUltra })
		{
			if (toggle.IsValid())
				toggle.GetUI().SetValue(preset && GetGraphicsPreset(toggle) == preset ? 1.0f : 0.0f);
		}
	}

	void OnUIValueChanged(Entity widget, float value) override
	{
		// The Graphics row is one toggle group: act only on the toggle that switched on.
		if (const std::optional<QualityPreset> preset = GetGraphicsPreset(widget))
		{
			if (value == 0.0f)
				return;
			Graphics::SetPreset(*preset);
			if (!Graphics::Save())
				Log::Warn("The graphics options were not saved");
			return;
		}
		const std::string name = widget.GetName();
		if (name == "Volume")
			Audio::SetMasterVolume(value);
		else if (name == "VSync")
			Game::SetVSync(value != 0.0f);
		else if (value != 0.0f)
			ChooseWindowMode(name);
	}

	void OnUIClick(Entity widget) override
	{
		const std::string name = widget.GetName();
		if (name == "Size720")
			Game::SetResolution(1280, 720);
		else if (name == "Size1080")
			Game::SetResolution(1920, 1080);
		else if (name == "Size1440")
			Game::SetResolution(2560, 1440);
	}

private:
	// The preset of a Graphics toggle, or nothing for another widget.
	std::optional<QualityPreset> GetGraphicsPreset(Entity widget) const
	{
		if (!widget.IsValid())
			return std::nullopt;
		if (widget == GraphicsLow)
			return QualityPreset::Low;
		if (widget == GraphicsMedium)
			return QualityPreset::Medium;
		if (widget == GraphicsHigh)
			return QualityPreset::High;
		if (widget == GraphicsUltra)
			return QualityPreset::Ultra;
		return std::nullopt;
	}

	// Called only for a toggle that turned on: its group turned the others off and raised their 0 first.
	void ChooseWindowMode(const std::string& name)
	{
		if (name == "Windowed")
			Game::SetWindowMode(WindowMode::Windowed);
		else if (name == "Borderless")
			Game::SetWindowMode(WindowMode::Borderless);
		else if (name == "Fullscreen")
			Game::SetWindowMode(WindowMode::Fullscreen);
	}
};

ST_SCRIPT_CLASS(SettingsMenu)
{
	ST_SCRIPT_FIELD(VolumeSlider);
	ST_SCRIPT_FIELD(GraphicsLow);
	ST_SCRIPT_FIELD(GraphicsMedium);
	ST_SCRIPT_FIELD(GraphicsHigh);
	ST_SCRIPT_FIELD(GraphicsUltra);
}
