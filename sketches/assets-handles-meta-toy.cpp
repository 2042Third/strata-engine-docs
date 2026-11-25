#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <map>
#include <string>
#include <string_view>

namespace
{

	constexpr uint64_t c_MaxBuiltin = 0xFF;

	uint64_t Fnv1a(std::string_view text)
	{
		uint64_t hash = 14695981039346656037ull;
		for (char character : text)
		{
			hash ^= static_cast<uint8_t>(character);
			hash *= 1099511628211ull;
		}
		return hash;
	}

	uint64_t Combine(uint64_t seed, uint64_t value)
	{
		value *= 0xff51afd7ed558ccdull;
		value ^= value >> 33;
		return seed ^ (value + 0x9e3779b97f4a7c15ull + (seed << 6) + (seed >> 2));
	}

	// The same handle on every machine: only the parent's handle and the key go in.
	uint64_t DeriveChild(uint64_t parent, std::string_view key)
	{
		uint64_t value = Combine(Fnv1a(key), parent);
		if (value <= c_MaxBuiltin)
			value += c_MaxBuiltin + 1;
		return value;
	}

	// A sidecar is one line, "Handle: <16 hex digits>". Zero means invalid: report it, never overwrite it.
	uint64_t ReadSidecar(const std::string& text)
	{
		if (text.rfind("Handle: ", 0) != 0)
			return 0;
		char* end = nullptr;
		const uint64_t handle = std::strtoull(text.c_str() + 8, &end, 16);
		return *end == '\0' ? handle : 0;
	}

}

int main()
{
	std::map<std::string, std::string> files = {
		{ "Rock.png", "Handle: 1A2B3C4D5E6F7081" },
		{ "Notes.png", "<<<<<<< HEAD" },
	};
	std::map<std::string, uint64_t> handleOf;
	for (const auto& [path, sidecar] : files)
	{
		const uint64_t handle = ReadSidecar(sidecar);
		if (handle == 0)
			std::printf("%s: invalid sidecar, file ignored\n", path.c_str());
		else
			handleOf[path] = handle;
	}

	// A rename that carries the sidecar keeps the handle.
	files["Stone.png"] = files["Rock.png"];
	files.erase("Rock.png");
	handleOf.clear();
	for (const auto& [path, sidecar] : files)
		if (const uint64_t handle = ReadSidecar(sidecar); handle != 0)
			handleOf[path] = handle;
	for (const auto& [path, handle] : handleOf)
		std::printf("%s -> %016llX\n", path.c_str(), static_cast<unsigned long long>(handle));

	const uint64_t model = 0x1A2B3C4D5E6F7081ull;
	for (std::string_view key : { "Mesh/0", "Material/0", "Skeleton" })
		std::printf("%.*s -> %016llX\n", static_cast<int>(key.size()), key.data(),
			static_cast<unsigned long long>(DeriveChild(model, key)));
	return 0;
}
