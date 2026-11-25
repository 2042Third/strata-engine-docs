// Scales base sizes by a UI scale and truncates, as ImGui's ScaleAllSizes does, then shows what was lost.
#include <cstdio>

int main()
{
	const float baseSizes[] = { 4.0f, 5.0f, 6.0f, 8.0f, 10.0f, 20.0f };
	const float scales[] = { 1.25f, 1.5f, 2.0f };
	for (const float scale : scales)
	{
		std::printf("scale %.2f:", scale);
		for (const float base : baseSizes)
		{
			const float exact = base * scale;
			const int whole = static_cast<int>(exact);
			std::printf("  %g->%d%s", base, whole, exact == static_cast<float>(whole) ? "" : "*");
		}
		std::printf("\n");
	}
	return 0;
}
