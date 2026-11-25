#include <cmath>
#include <cstdio>

namespace
{

	constexpr float c_Pi = 3.14159265f;

	// Candela for a spot light of the given lumens whose light fills a cone of the given half angle evenly.
	float SpotCandelaFromLumens(float lumens, float halfAngleDegrees)
	{
		const float solidAngle = 2.0f * c_Pi * (1.0f - std::cos(halfAngleDegrees * c_Pi / 180.0f));
		return lumens / solidAngle;
	}

	int s_Failures = 0;

	void Expect(const char* name, float actual, float expected, float tolerance)
	{
		const bool ok = std::fabs(actual - expected) <= tolerance;
		std::printf("%s: %.2f cd (expected %.2f) %s\n", name, actual, expected, ok ? "ok" : "FAILED");
		if (!ok)
			s_Failures++;
	}

}

int main()
{
	// A half angle of 90 degrees is a hemisphere: 2 pi steradians.
	Expect("hemisphere", SpotCandelaFromLumens(628.3185f, 90.0f), 100.0f, 0.01f);
	// 800 lumens in a cone of 30 degrees half angle.
	Expect("narrow cone", SpotCandelaFromLumens(800.0f, 30.0f), 950.3f, 0.5f);
	// Halving the half angle of a narrow cone roughly quadruples the candela.
	Expect("ratio", SpotCandelaFromLumens(800.0f, 15.0f) / SpotCandelaFromLumens(800.0f, 30.0f), 3.93f, 0.01f);
	return s_Failures;
}
