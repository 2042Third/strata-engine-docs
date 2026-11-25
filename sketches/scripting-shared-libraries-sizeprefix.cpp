#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstring>

struct InfoV1
{
	uint32_t StructSize;
	uint32_t Id;
};

struct InfoV2
{
	uint32_t StructSize;
	uint32_t Id;
	uint32_t Flags;
};

// Fills the caller's struct: at most as many bytes as the caller's StructSize allows and the filler knows.
void Fill(void* out, const void* known, uint32_t knownSize)
{
	uint32_t capacity = 0;
	std::memcpy(&capacity, out, sizeof(capacity));
	const uint32_t written = capacity < knownSize ? capacity : knownSize;
	std::memcpy(out, known, written);
	std::memcpy(out, &written, sizeof(written));
}

int main()
{
	const InfoV2 newEngine = { sizeof(InfoV2), 7, 99 };
	InfoV1 oldModule = { sizeof(InfoV1), 0 };
	Fill(&oldModule, &newEngine, sizeof(InfoV2));
	std::printf("old module: size %u, Id %u\n", oldModule.StructSize, oldModule.Id);

	const InfoV1 oldEngine = { sizeof(InfoV1), 7 };
	InfoV2 newModule = { sizeof(InfoV2), 0, 0 };
	Fill(&newModule, &oldEngine, sizeof(InfoV1));
	const bool hasFlags = newModule.StructSize >= offsetof(InfoV2, Flags) + sizeof(newModule.Flags);
	std::printf("new module: size %u, Id %u, Flags readable: %s\n", newModule.StructSize, newModule.Id, hasFlags ? "yes" : "no");
	return 0;
}
