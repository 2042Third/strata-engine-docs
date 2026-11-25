// A model of Dear ImGui's ID stack: an ID is a CRC-32C hash of a label, seeded by the top of the stack.
// A "###" in a label restarts the hash, so only it and the text after it count. Strings stand in for PushID's values.
#include <cstdint>
#include <cstdio>
#include <string>
#include <vector>

namespace
{

	uint32_t s_Table[256];

	void BuildTable()
	{
		for (uint32_t index = 0; index < 256; index++)
		{
			uint32_t value = index;
			for (int bit = 0; bit < 8; bit++)
				value = (value & 1) ? (value >> 1) ^ 0x82F63B78u : value >> 1;
			s_Table[index] = value;
		}
	}

	uint32_t HashLabel(const std::string& label, uint32_t seed)
	{
		seed = ~seed;
		uint32_t crc = seed;
		for (size_t position = 0; position < label.size(); position++)
		{
			if (label.compare(position, 3, "###") == 0)
				crc = seed;
			crc = (crc >> 8) ^ s_Table[(crc & 0xFF) ^ static_cast<unsigned char>(label[position])];
		}
		return ~crc;
	}

	struct IdStack
	{
		std::vector<uint32_t> Ids;

		explicit IdStack(const std::string& window)
		{
			Ids.push_back(HashLabel(window, 0));
		}

		uint32_t GetID(const std::string& label) const { return HashLabel(label, Ids.back()); }
		void Push(const std::string& label) { Ids.push_back(GetID(label)); }
		void Pop() { Ids.pop_back(); }
	};

	void Print(const std::string& what, uint32_t id)
	{
		std::printf("%-26s 0x%08X\n", what.c_str(), id);
	}

}

int main()
{
	BuildTable();
	IdStack stack("Scratch");
	Print("Delete", stack.GetID("Delete"));
	Print("Delete (second call)", stack.GetID("Delete"));
	Print("Delete##2", stack.GetID("Delete##2"));
	Print("Delete###Row", stack.GetID("Delete###Row"));
	Print("Remove###Row", stack.GetID("Remove###Row"));
	for (int row = 0; row < 2; row++)
	{
		stack.Push(std::to_string(row));
		Print("row " + std::to_string(row) + ": Delete", stack.GetID("Delete"));
		stack.Pop();
	}
	return 0;
}
