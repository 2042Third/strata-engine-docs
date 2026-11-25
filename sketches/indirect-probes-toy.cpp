#include <cmath>
#include <cstdio>

// A box centered at the origin with half sizes `extents`; `local` is a position inside it, `reflected` a unit direction.
// Returns where the reflected ray leaves the box: the point to look up in the capture, seen from the center.
void GetBoxLookup(const float extents[3], const float local[3], const float reflected[3], float lookup[3])
{
	float exitDistance = 1.0e30f;
	for (int axis = 0; axis < 3; axis++)
	{
		// A ray that does not move along an axis never reaches that axis's faces.
		if (std::fabs(reflected[axis]) < 1.0e-6f)
			continue;
		const float face = reflected[axis] > 0.0f ? extents[axis] : -extents[axis];
		exitDistance = std::fmin(exitDistance, (face - local[axis]) / reflected[axis]);
	}
	exitDistance = std::fmax(exitDistance, 0.0f);
	std::printf("exit distance %.4f m\n", exitDistance);
	for (int axis = 0; axis < 3; axis++)
		lookup[axis] = local[axis] + reflected[axis] * exitDistance;
}

// 1 deeper than `blend` meters inside the box, falling to 0 at its faces.
float GetWeight(const float extents[3], const float local[3], float blend)
{
	float depth = extents[0] - std::fabs(local[0]);
	for (int axis = 1; axis < 3; axis++)
		depth = std::fmin(depth, extents[axis] - std::fabs(local[axis]));
	if (depth <= 0.0f)
		return 0.0f;
	return blend > 0.0f ? std::fmin(depth / blend, 1.0f) : 1.0f;
}

int main()
{
	const float extents[3] = { 4.0f, 2.0f, 3.0f };
	const float local[3] = { 2.0f, -1.5f, 0.0f };
	const float reflected[3] = { 0.6f, 0.8f, 0.0f };

	float lookup[3] = {};
	GetBoxLookup(extents, local, reflected, lookup);
	std::printf("lookup direction (%.4f, %.4f, %.4f)\n", lookup[0], lookup[1], lookup[2]);
	const float rise = std::atan2(lookup[1], std::hypot(lookup[0], lookup[2])) * 57.29578f;
	std::printf("rises %.1f degrees; the plain reflection rises %.1f\n", rise, std::asin(0.8f) * 57.29578f);

	// Two probes at this position: the stronger one's weight, then the weaker one's weight of what is left.
	const float strong = GetWeight(extents, local, 1.0f);
	const float weak = 0.8f * (1.0f - strong);
	std::printf("weights %.2f and %.2f; the sky fills %.2f\n", strong, weak, 1.0f - strong - weak);
	return 0;
}
