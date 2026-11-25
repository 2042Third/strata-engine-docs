// A pretend engine file in the shape of the importers (tools/tests/test_reference.py).
namespace Strata
{

	namespace
	{

		class NativeAssetImporter final : public AssetImporter
		{
		public:
			NativeAssetImporter(AssetType type, std::string_view extension)
				: m_Type(type), m_Extension(extension)
			{
			}

			AssetType GetType() const override { return m_Type; }
			std::vector<std::string> GetExtensions() const override { return { m_Extension }; }
			uint32_t GetVersion() const override { return 1; }
		private:
			AssetType m_Type;
			std::string m_Extension;
		};

		class AudioClipImporter final : public AssetImporter
		{
		public:
			AssetType GetType() const override { return AssetType::AudioClip; }
			std::vector<std::string> GetExtensions() const override { return { ".wav", ".ogg" }; }
			uint32_t GetVersion() const override { return 2; }
		};

	}

	void RegisterAssetPipeline()
	{
		AssetImporterRegistry::Register(CreateScope<NativeAssetImporter>(AssetType::Scene, ".stscene"));
		AssetImporterRegistry::Register(CreateScope<AudioClipImporter>());
		AssetImporterRegistry::Register(CreateScope<TextureImporter>());
	}

}
