#include <cmath>
#include <cstdint>
#include <cstdio>

struct CellKey
{
	uint8_t Layer = 0;
	int32_t X = 0;
	int32_t Z = 0;
};

// Floor, not truncation: -0.0003 cells is cell -1, not cell 0.
int32_t ToCell(double offset, double cellSize)
{
	return static_cast<int32_t>(std::floor(offset / cellSize));
}

CellKey CellAt(uint8_t layer, double cellSize, double originX, double originZ, double x, double z)
{
	return CellKey { layer, ToCell(x - originX, cellSize), ToCell(z - originZ, cellSize) };
}

// The layer goes in the top 8 bits, then X and Z shifted by 2^27 into 28 bits each.
uint64_t Pack(const CellKey& key)
{
	const int64_t offset = int64_t(1) << 27;
	const uint64_t x = static_cast<uint64_t>(key.X + offset);
	const uint64_t z = static_cast<uint64_t>(key.Z + offset);
	return (uint64_t(key.Layer) << 56) | (x << 28) | z;
}

void Print(const char* label, const CellKey& key)
{
	std::printf("%s: layer %d, cell (%d, %d), key 0x%016llx\n", label, key.Layer, key.X, key.Z, static_cast<unsigned long long>(Pack(key)));
}

int main()
{
	// A layer of 32 m cells whose grid starts at (200, -100).
	Print("origin", CellAt(3, 32.0, 200.0, -100.0, 200.0, -100.0));
	Print("just below", CellAt(3, 32.0, 200.0, -100.0, 199.99, -100.01));
	Print("far", CellAt(3, 32.0, 200.0, -100.0, 264.0, -36.0));
}
