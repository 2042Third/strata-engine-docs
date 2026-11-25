// Slides a box, a tent and a bell kernel along a spike of height 16: each result keeps the total of 16.
#include <cstdio>
#include <vector>

int main()
{
	const std::vector<double> spike = { 0, 0, 0, 16, 0, 0, 0 };
	const std::vector<double> kernels[3] = { { 1.0 / 3, 1.0 / 3, 1.0 / 3 }, { 0.25, 0.5, 0.25 }, { 0.0625, 0.25, 0.375, 0.25, 0.0625 } };
	for (const std::vector<double>& kernel : kernels)
	{
		const int radius = static_cast<int>(kernel.size()) / 2;
		for (int i = 0; i < 7; i++)
		{
			double sum = 0.0;
			for (int k = -radius; k <= radius; k++)
				if (i + k >= 0 && i + k < 7)
					sum += spike[i + k] * kernel[k + radius];
			std::printf("%.2f%c", sum, i < 6 ? ' ' : '\n');
		}
	}
}
