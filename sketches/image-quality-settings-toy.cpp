#include <array>
#include <cstddef>
#include <cstdio>
#include <optional>

enum class Preset { Low, Medium, High, Ultra, Custom };

struct Quality
{
	Preset Level = Preset::High;
	int ShadowSize = 0;
	int Cascades = 0;
	bool Reflections = false;
	bool MotionBlur = true; // A players' row: shown (true) or turned off (false)
};

// One row per setting, with one value for each of Low, Medium, High and Ultra.
constexpr std::array<int, 4> c_ShadowSizeRow = { 1024, 2048, 4096, 8192 };
constexpr std::array<int, 4> c_CascadesRow = { 3, 4, 5, 5 };
constexpr std::array<bool, 4> c_ReflectionsRow = { false, true, true, true };

Quality GetPreset(Preset level)
{
	const size_t index = static_cast<size_t>(level);
	return { level, c_ShadowSizeRow[index], c_CascadesRow[index], c_ReflectionsRow[index], true };
}

struct Player
{
	std::optional<Preset> Level; // Nothing: the project's preset applies
	Quality Custom;              // The rows' values while the level is Custom
	bool BlurOff = false;        // Kept under every preset
};

Quality InEffect(Preset project, const Player& player)
{
	Quality result = player.Level == Preset::Custom ? player.Custom : GetPreset(player.Level.value_or(project));
	if (player.BlurOff)
		result.MotionBlur = false;
	return result;
}

void SetCascades(Player& player, Preset project, int cascades)
{
	if (player.Level != Preset::Custom)
	{
		player.Custom = InEffect(project, player); // Custom starts from the look in effect
		player.Level = Preset::Custom;
	}
	player.Custom.Cascades = cascades;
}

void Print(const char* step, const Quality& quality)
{
	constexpr std::array<const char*, 5> names = { "Low", "Medium", "High", "Ultra", "Custom" };
	std::printf("%-22s %-6s shadows %4d, cascades %d, reflections %d, blur %d\n", step, names[static_cast<size_t>(quality.Level)],
		quality.ShadowSize, quality.Cascades, quality.Reflections, quality.MotionBlur);
}

int main()
{
	Player player;
	Print("project High", InEffect(Preset::High, player));
	player.BlurOff = true;
	Print("blur off", InEffect(Preset::High, player));
	SetCascades(player, Preset::High, 3);
	Print("cascades 3", InEffect(Preset::High, player));
	Print("project turns Ultra", InEffect(Preset::Ultra, player));
	player.Level = Preset::Low;
	Print("player chooses Low", InEffect(Preset::Ultra, player));
}
