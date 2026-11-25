#include <array>
#include <cstdint>
#include <cstdio>

namespace
{

	constexpr uint32_t c_LayerCount = 32;

	std::array<uint32_t, c_LayerCount> s_Masks;

	void SetCollide(uint32_t a, uint32_t b, bool collide)
	{
		if (collide)
		{
			s_Masks[a] |= 1u << b;
			s_Masks[b] |= 1u << a;
		}
		else
		{
			s_Masks[a] &= ~(1u << b);
			s_Masks[b] &= ~(1u << a);
		}
	}

	bool DoCollide(uint32_t a, uint32_t b)
	{
		return (s_Masks[a] & (1u << b)) != 0 && (s_Masks[b] & (1u << a)) != 0;
	}

	uint32_t CountPartners(uint32_t layer)
	{
		uint32_t count = 0;
		for (uint32_t other = 0; other < c_LayerCount; other++)
		{
			if (DoCollide(layer, other))
				count++;
		}
		return count;
	}

}

int main()
{
	s_Masks.fill(0xFFFFFFFFu);
	std::printf("layer 3 starts with %u partners\n", CountPartners(3));
	SetCollide(3, 4, false);
	std::printf("after parting 3 and 4: %u\n", CountPartners(3));
	SetCollide(3, 3, false);
	std::printf("after parting 3 and 3: %u\n", CountPartners(3));
	s_Masks[5] &= ~(1u << 3);
	std::printf("after a one-sided edit of layer 5: %u\n", CountPartners(3));
	return 0;
}
