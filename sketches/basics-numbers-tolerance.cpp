// Practice 4: ten additions of 0.1f against 1.0f, with every digit, without and with a tolerance.
#include <cmath>
#include <iomanip>
#include <iostream>

int main()
{
	float sum = 0.0f;
	for (int count = 0; count < 10; count++)
		sum += 0.1f;
	std::cout << std::setprecision(9) << std::boolalpha;
	std::cout << "sum: " << sum << '\n';
	std::cout << "equal to 1: " << (sum == 1.0f) << '\n';
	std::cout << "within 1e-6: " << (std::abs(sum - 1.0f) < 1e-6f) << '\n';
	return 0;
}
