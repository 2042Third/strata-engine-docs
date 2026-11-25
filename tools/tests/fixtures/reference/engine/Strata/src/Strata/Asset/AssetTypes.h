#pragma once
// A pretend engine file in the shape of the asset types (tools/tests/test_reference.py).

namespace Strata
{

	enum class AssetType : uint16_t
	{
		None = 0,
		Scene,
		Texture, // Images
		// Added later (append only)
		AudioClip = 7
	};

}
