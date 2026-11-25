// How the estimate of the cost per entity follows four chunks that measure 6,000, 1,500, 1,500 and 1,500 ns.
#include <algorithm>
#include <cstdio>

// A dearer chunk raises the estimate at once; a cheaper one lowers it halfway.
static double Record(double estimateNs, double measuredNs)
{
	return std::max(measuredNs, 0.5 * (estimateNs + measuredNs));
}

int main()
{
	const double measured[] = { 6000.0, 1500.0, 1500.0, 1500.0 };
	double estimateNs = 2000.0;
	for (const double chunkNs : measured)
	{
		estimateNs = Record(estimateNs, chunkNs);
		std::printf("measured %.0f ns, estimate %.1f ns\n", chunkNs, estimateNs);
	}
	return 0;
}
