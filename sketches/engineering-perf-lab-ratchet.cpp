#include <algorithm>
#include <cstddef>
#include <cstdio>
#include <string>
#include <vector>

struct Entry
{
	double Measured = 0.0;
	double Budget = 0.0;
};

// The class of a metric after several runs, in the order of the lab's tool: too few runs, over budget, unstable,
// then the median against the measurement on the reference machine.
std::string Classify(const Entry& entry, std::vector<double> values)
{
	const size_t count = values.size();
	if (count < 3)
		return "not recorded";
	std::sort(values.begin(), values.end());
	const double median = count % 2 == 1 ? values[count / 2] : (values[count / 2 - 1] + values[count / 2]) * 0.5;
	if (values.back() > entry.Budget)
		return "over budget";
	if ((values.back() - values.front()) / median > 0.25)
		return "unstable";
	if (median < 0.9 * entry.Measured)
		return "cheaper";
	if (median > 1.1 * entry.Measured)
		return "dearer within";
	return "same";
}

int main()
{
	const Entry entry = { 10.0, 15.0 };
	const std::vector<std::vector<double>> runs = {
		{ 10.1, 9.8 },
		{ 10.2, 9.9, 10.4, 10.0 },
		{ 8.1, 8.3, 8.2 },
		{ 11.6, 11.4, 11.9, 11.5 },
		{ 10.0, 13.9, 9.9, 10.1 },
		{ 10.0, 10.1, 15.5 },
	};
	for (const std::vector<double>& values : runs)
		std::printf("%zu values: %s\n", values.size(), Classify(entry, values).c_str());
	return 0;
}
