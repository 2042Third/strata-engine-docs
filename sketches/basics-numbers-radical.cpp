// The digits of 1, 2, 3 and 4 written backwards behind the point, in base 2 and in base 3.
#include <cstdint>
#include <iostream>

float RadicalInverse(uint32_t index, uint32_t base)
{
	float result = 0.0f;
	float scale = 1.0f / static_cast<float>(base);
	for (; index > 0; index /= base)
	{
		result += static_cast<float>(index % base) * scale;
		scale /= static_cast<float>(base);
	}
	return result;
}

int main()
{
	for (uint32_t index = 1; index <= 4; index++)
		std::cout << index << ": " << RadicalInverse(index, 2) << " " << RadicalInverse(index, 3) << '\n';
	return 0;
}
