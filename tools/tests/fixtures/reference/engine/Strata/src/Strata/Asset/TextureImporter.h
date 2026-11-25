#pragma once
// A pretend engine file: an importer declared in a header (tools/tests/test_reference.py).

namespace Strata
{

	enum class TextureUsage : uint8_t
	{
		Color,
		Normal
	};

	class TextureImporter final : public AssetImporter
	{
	public:
		AssetType GetType() const override { return AssetType::Texture; }
		std::vector<std::string> GetExtensions() const override;
		uint32_t GetVersion() const override { return 5; }
	};

}
