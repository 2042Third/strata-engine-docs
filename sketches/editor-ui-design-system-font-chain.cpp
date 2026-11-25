// A toy font chain: each face may be limited to a range of code points, or barred from one.
#include <cstdint>
#include <cstdio>
#include <vector>

namespace Toy
{

	struct Range
	{
		uint32_t First;
		uint32_t Last;
	};

	struct Face
	{
		const char* Name;
		Range Only;           // The code points the face may supply.
		Range Exclude;        // The code points it must not supply (First > Last means none).
		std::vector<uint32_t> Has; // What its file really holds.
	};

	constexpr Range c_Everything = { 0, 0x10FFFF };
	constexpr Range c_Icons = { 0xE000, 0xF8FF };
	constexpr Range c_Nothing = { 1, 0 };

	bool Inside(const Range& range, uint32_t codePoint)
	{
		return codePoint >= range.First && codePoint <= range.Last;
	}

	bool Supplies(const Face& face, uint32_t codePoint)
	{
		if (!Inside(face.Only, codePoint) || Inside(face.Exclude, codePoint))
			return false;
		for (const uint32_t held : face.Has)
		{
			if (held == codePoint)
				return true;
		}
		return false;
	}

	// The first face of the chain that supplies the code point, or the fallback character.
	const char* Find(const std::vector<Face>& chain, uint32_t codePoint)
	{
		for (const Face& face : chain)
		{
			if (Supplies(face, codePoint))
				return face.Name;
		}
		return "fallback glyph";
	}

}

int main()
{
	// The text font even holds a glyph inside the icon range, which its exclusion keeps from shadowing the icon.
	const std::vector<Toy::Face> chain = {
		{ "Inter", Toy::c_Everything, Toy::c_Icons, { 'A', 0xE9, 0xE585 } },
		{ "Lucide", Toy::c_Icons, Toy::c_Nothing, { 0xE585, 0xE038 } },
		{ "CJK font", Toy::c_Everything, Toy::c_Icons, { 0x6575, 0xE585 } }
	};
	const uint32_t probes[] = { 'A', 0xE585, 0x6575, 0x1F600 };
	for (const uint32_t codePoint : probes)
		std::printf("U+%04X -> %s\n", static_cast<unsigned>(codePoint), Toy::Find(chain, codePoint));
	return 0;
}
