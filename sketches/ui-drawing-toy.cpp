#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <vector>

// A toy of the UI's batching: elements write quads into slots with room to spare, and the quad array splits into runs.
struct Element
{
	int Glyphs = 0; // 0: an image element, else a text of this many glyphs
	uint32_t Font = 0;
};

struct Quad
{
	bool Hidden = true;
	bool Glyph = false;
	uint32_t Font = 0;
};

struct Slot
{
	uint32_t First = 0;
	uint32_t Capacity = 0;
};

uint32_t GetCapacity(int glyphs)
{
	return glyphs == 0 ? 1u : static_cast<uint32_t>(glyphs) + std::max(4u, (static_cast<uint32_t>(glyphs) + 3u) / 4u);
}

void Write(std::vector<Quad>& quads, const Slot& slot, const Element& element)
{
	const uint32_t used = element.Glyphs == 0 ? 1u : static_cast<uint32_t>(element.Glyphs);
	for (uint32_t index = 0; index < slot.Capacity; index++)
		quads[slot.First + index] = Quad { index >= used, element.Glyphs > 0, element.Font };
}

int main()
{
	std::vector<Element> elements = { { 0, 0 }, { 5, 0 }, { 4, 1 }, { 7, 2 }, { 4, 3 }, { 6, 4 } };
	std::vector<Slot> slots;
	std::vector<Quad> quads;
	for (const Element& element : elements)
	{
		slots.push_back({ static_cast<uint32_t>(quads.size()), GetCapacity(element.Glyphs) });
		quads.resize(quads.size() + slots.back().Capacity);
		Write(quads, slots.back(), element);
	}
	std::printf("quads in the array: %zu\n", quads.size());

	// An edit rewrites its slot alone, unless the text outgrew the room: then the array would be rebuilt.
	for (const int glyphs : { 8, 9 })
	{
		const bool fits = static_cast<uint32_t>(glyphs) <= slots[2].Capacity;
		std::printf("a label of %d glyphs: %s\n", glyphs, fits ? "rewrite the slot" : "rebuild");
		if (fits)
			Write(quads, slots[2], Element { glyphs, 1 });
	}

	// Runs: one draw while at most four fonts are in use; a glyph of a fifth font starts a new run.
	std::vector<uint32_t> bound;
	uint32_t runStart = 0;
	for (uint32_t index = 0; index < quads.size(); index++)
	{
		if (!quads[index].Glyph)
			continue;
		if (std::find(bound.begin(), bound.end(), quads[index].Font) != bound.end())
			continue;
		if (bound.size() == 4)
		{
			std::printf("run: quads %u to %u\n", runStart, index - 1);
			bound.clear();
			runStart = index;
		}
		bound.push_back(quads[index].Font);
	}
	std::printf("run: quads %u to %zu\n", runStart, quads.size() - 1);
	return 0;
}
