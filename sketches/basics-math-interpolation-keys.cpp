// One segment between two keys, read by step, linear and Hermite interpolation.
#include <cstdio>
#include <glm/glm.hpp>
struct Key
{
	float Time, Value;
	float Slope; // value change per second, read by Hermite only
};
float Hermite(const Key& a, const Key& b, float s) // s: 0 at key a, 1 at key b
{
	const float span = b.Time - a.Time;
	const float s2 = s * s, s3 = s2 * s;
	return (2 * s3 - 3 * s2 + 1) * a.Value + (s3 - 2 * s2 + s) * span * a.Slope + (3 * s2 - 2 * s3) * b.Value + (s3 - s2) * span * b.Slope;
}
int main()
{
	const Key a{0.0f, 0.0f, 1.0f};
	const Key b{2.0f, 1.0f, 0.0f};
	for (const float time : {1.0f, 1.5f})
	{
		const float s = (time - a.Time) / (b.Time - a.Time);
		std::printf("t = %g s: step %g, linear %g, Hermite %g\n", time, a.Value, glm::mix(a.Value, b.Value, s), Hermite(a, b, s));
	}
	return 0;
}
