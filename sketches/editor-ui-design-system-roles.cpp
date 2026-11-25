// A toy theme: a palette of tokens, a role table of pointers to members and a check that no slot lacks a role.
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <iterator>

namespace Toy
{

	struct Color
	{
		float R, G, B, A;
	};

	constexpr Color FromRGB(uint32_t rgb)
	{
		return { static_cast<float>((rgb >> 16) & 0xFF) / 255.0f, static_cast<float>((rgb >> 8) & 0xFF) / 255.0f,
			static_cast<float>(rgb & 0xFF) / 255.0f, 1.0f };
	}

	struct Palette
	{
		Color Basalt;
		Color Flint;
		Color Limestone;
		Color Ochre;
	};

	constexpr Palette c_Palette = { FromRGB(0x0E1013), FromRGB(0x262B31), FromRGB(0xE8E4DC), FromRGB(0xE08A2E) };

	// The slots the toy toolkit draws with.
	enum class Slot : size_t
	{
		Text,
		FrameBackground,
		Button,
		CheckMark,
		Count
	};

	struct Role
	{
		Slot Where;
		Color Palette::*Token;
		float Alpha;
	};

	constexpr Role c_Roles[] = {
		{ Slot::Text, &Palette::Limestone, 1.0f },
		{ Slot::FrameBackground, &Palette::Basalt, 1.0f },
		{ Slot::Button, &Palette::Flint, 1.0f },
		{ Slot::CheckMark, &Palette::Ochre, 0.9f }
	};
	// A toolkit upgrade that adds a slot fails the build here until the slot has a role.
	static_assert(std::size(c_Roles) == static_cast<size_t>(Slot::Count), "Give every slot a palette token");

	void Apply(std::array<Color, static_cast<size_t>(Slot::Count)>& colors)
	{
		for (const Role& role : c_Roles)
		{
			const Color& token = c_Palette.*role.Token;
			colors[static_cast<size_t>(role.Where)] = { token.R, token.G, token.B, role.Alpha };
		}
	}

}

int main()
{
	std::array<Toy::Color, static_cast<size_t>(Toy::Slot::Count)> colors = {};
	Toy::Apply(colors);
	const char* names[] = { "Text", "FrameBackground", "Button", "CheckMark" };
	for (size_t index = 0; index < colors.size(); index++)
	{
		const Toy::Color& color = colors[index];
		std::printf("%-16s rgb %3d %3d %3d alpha %.1f\n", names[index], static_cast<int>(color.R * 255.0f + 0.5f),
			static_cast<int>(color.G * 255.0f + 0.5f), static_cast<int>(color.B * 255.0f + 0.5f), color.A);
	}
	return 0;
}
