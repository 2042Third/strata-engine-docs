// How two touching materials combine, and the ramp angle at which a box starts to slide.
#include <cmath>
#include <cstdio>
#include <initializer_list>

namespace
{
	constexpr double c_Pi = 3.14159265358979323846;

	// Friction of a contact: the square root of the product of the two materials' friction.
	double MixFriction(double a, double b)
	{
		return std::sqrt(a * b);
	}

	// Restitution of a contact: the larger of the two values.
	double MixRestitution(double a, double b)
	{
		return a > b ? a : b;
	}

	// A box rests on a ramp while tan(angle) stays below the friction coefficient.
	double SlideAngleDegrees(double friction)
	{
		return std::atan(friction) * 180.0 / c_Pi;
	}
}

int main()
{
	std::printf("ice on wood: friction %.3f\n", MixFriction(0.05, 0.5));
	std::printf("rubber on floor: restitution %.2f\n", MixRestitution(0.8, 0.0));

	const double mixed = MixFriction(0.1, 0.9);
	std::printf("box on ramp: friction %.2f, slides above %.1f degrees\n", mixed, SlideAngleDegrees(mixed));
	for (double angle : { 15.0, 20.0 })
	{
		const bool slides = std::tan(angle * c_Pi / 180.0) > mixed;
		std::printf("ramp at %.0f degrees: the box %s\n", angle, slides ? "slides" : "holds");
	}
	return 0;
}
