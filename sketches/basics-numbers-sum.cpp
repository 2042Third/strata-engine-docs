// Why 0.1 + 0.2 is not 0.3: every digit of the sum, and a comparison with a tolerance.
#include <cmath>
#include <iomanip>
#include <iostream>

int main()
{
	const double sum = 0.1 + 0.2;
	std::cout << std::setprecision(17) << std::boolalpha;
	std::cout << "0.1 + 0.2 = " << sum << '\n';
	std::cout << "equal to 0.3: " << (sum == 0.3) << '\n';
	std::cout << "difference: " << std::abs(sum - 0.3) << '\n';
	std::cout << "within 1e-9: " << (std::abs(sum - 0.3) < 1e-9) << '\n';
	return 0;
}
