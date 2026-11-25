// A window set to the largest number: a plain sum wraps round to a small one, a saturating sum stays at the limit.
#include <cstdint>
#include <iostream>

uint64_t SaturatingAdd(uint64_t a, uint64_t b)
{
	return b > UINT64_MAX - a ? UINT64_MAX : a + b;
}

// Whether `bytes` fit beside `held` in a budget.
bool Fits(uint64_t budget, uint64_t held, uint64_t bytes)
{
	return held <= budget && bytes <= budget - held;
}

int main()
{
	const uint64_t budget = 1000;
	const uint64_t resident = 600;
	const uint64_t window = UINT64_MAX; // an in-flight window set to "anything"
	const uint64_t request = 100;

	const uint64_t plainHeld = resident + window;
	const uint64_t saturatedHeld = SaturatingAdd(resident, window);
	std::cout << "plain sum:      held " << plainHeld << ", fits " << Fits(budget, plainHeld, request) << '\n';
	std::cout << "saturating sum: held " << saturatedHeld << ", fits " << Fits(budget, saturatedHeld, request) << '\n';
}
