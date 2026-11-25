#include <cmath>
#include <cstdio>

constexpr float c_HighFraction = 0.05f;
constexpr float c_PrefetchDistance = 100.0f;
constexpr float c_Pi = 3.14159265f;

struct Cube
{
	const char* Name;
	float Distance;
	bool InView;
	bool CastsShadow;
};

// The bounding sphere's diameter over the height of the view at that distance.
float GetScreenFraction(float radius, float distance, float verticalFov)
{
	return radius / (distance * std::tan(verticalFov * 0.5f));
}

void Describe(const Cube& cube, float radius, float verticalFov)
{
	if (cube.InView)
	{
		const float fraction = GetScreenFraction(radius, cube.Distance, verticalFov);
		std::printf("%s: fraction %.3f, %s\n", cube.Name, fraction, fraction > c_HighFraction ? "Resolve at High" : "Resolve at Normal");
		return;
	}
	if (cube.Distance <= c_PrefetchDistance)
		std::printf("%s: out of view, within the prefetch distance, Prefetch\n", cube.Name);
	if (cube.CastsShadow)
		std::printf("%s: out of view, casts a shadow, FindResident\n", cube.Name);
}

int main()
{
	// A cube of side 1 has a bounding sphere of radius 0.866; the vertical field of view is 60 degrees.
	const float radius = 0.866f;
	const float verticalFov = c_Pi / 3.0f;
	const Cube cubes[] = {
		{ "A", 7.5f, true, false },
		{ "B", 60.0f, true, false },
		{ "C", 40.0f, false, false },
		{ "D", 150.0f, false, true },
	};
	for (const Cube& cube : cubes)
		Describe(cube, radius, verticalFov);
	return 0;
}
