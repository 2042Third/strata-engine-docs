// A path joins parts with the slash operator and answers questions about its pieces.
#include <filesystem>
#include <iostream>

int main()
{
	const std::filesystem::path root = "Assets";
	const std::filesystem::path texture = root / "Textures" / "Brick.png";
	std::cout << texture.generic_string() << '\n';
	std::cout << "file " << texture.filename().generic_string() << ", name " << texture.stem().generic_string() << ", extension " << texture.extension().generic_string() << '\n';
	std::cout << "folder " << texture.parent_path().generic_string() << '\n';
	return 0;
}
