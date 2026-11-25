// The chance that two of n random 64-bit identifiers are equal: about n * n / 2^65 while it stays small.
#include <cmath>
#include <cstdio>
#include <initializer_list>

int main()
{
	const double space = 18446744073709551616.0; // 2^64 identifiers
	for (const double count : { 1.0e3, 1.0e6, 1.0e9, 5.06e9 })
	{
		const double chance = -std::expm1(-count * count / (2.0 * space));
		std::printf("%.2e identifiers: chance %.3g, one in %.3g\n", count, chance, 1.0 / chance);
	}
}
