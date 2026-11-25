// A pretend engine file in the shape of the quality rows (tools/tests/test_reference.py).
namespace Strata
{

	namespace
	{

		template<typename T>
		using PresetRow = std::array<T, 4>; // Low, Medium, High, Ultra

		// Sharper shadows cost memory.
		constexpr PresetRow<ShadowMapResolution> c_ShadowResolutionRow = { ShadowMapResolution::Size1024, ShadowMapResolution::Size2048, ShadowMapResolution::Auto, ShadowMapResolution::Size4096 };
		constexpr PresetRow<uint32_t> c_ShadowCascadesRow = { 2, 3, 4, 4 };
		constexpr PresetRow<float> c_LODErrorPixelsRow = { 2.0f, 1.0f, 1.0f, 0.5f };

	}

	SettingsSection MakeQualitySection()
	{
		SettingsSection section;
		section.Fields.push_back(EnumField("Preset", "Preset", "The quality preset.", presets, "High"));
		section.Fields.push_back(EnumField("ShadowResolution", "Shadow resolution", "Texels of a cascade.", resolutions, "Auto"));
		section.Fields.push_back(NumberField("ShadowCascades", "Shadow cascades", "Sun shadow cascades.", SettingsFieldType::Int, 1, 4, 4));
		section.Fields.push_back(NumberField("LODErrorPixels", "Level of detail error", "Pixels of error.", SettingsFieldType::Float, 0.0, 8.0, 1.0));
		return section;
	}

}
