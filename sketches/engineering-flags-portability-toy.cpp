// Two ways to compute a * b + c in float: rounded twice (multiply, then add), and fused (rounded once).
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>

static std::uint32_t Bits(float value)
{
	std::uint32_t bits = 0;
	std::memcpy(&bits, &value, sizeof(bits));
	return bits;
}

// The volatile product is stored and read back, so the compiler cannot fuse it with the addition.
static float Separate(float a, float b, float c)
{
	volatile float product = a * b;
	return product + c;
}

static void Show(float a, float b, float c)
{
	const float separate = Separate(a, b, c);
	const float fused = std::fma(a, b, c);
	std::printf("%g * %g + %g\n", a, b, c);
	std::printf("  two roundings: %.9g (bits %08x)\n", separate, static_cast<unsigned>(Bits(separate)));
	std::printf("  one rounding:  %.9g (bits %08x)\n", fused, static_cast<unsigned>(Bits(fused)));
	std::printf("  same bits: %s\n", Bits(separate) == Bits(fused) ? "yes" : "no");
}

int main()
{
	Show(1.1f, 1.5f, 0.1f);
	Show(3.3f, 1.1f, -3.63f);
	Show(1.5f, 2.0f, 0.25f);
	return 0;
}
