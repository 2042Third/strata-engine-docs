// Writing only the axes an edit changed: three entities share one Position row.
#include <array>
#include <cstdio>
#include <vector>

using Vec3 = std::array<float, 3>;

static void Write(std::vector<Vec3>& positions, const Vec3 shown, const Vec3& edited)
{
	for (Vec3& position : positions)
	{
		for (size_t axis = 0; axis < 3; axis++)
		{
			if (shown[axis] != edited[axis])
				position[axis] = edited[axis]; // only an axis the edit changed
		}
	}
}

static void Print(const std::vector<Vec3>& positions)
{
	for (const Vec3& position : positions)
		std::printf("(%g, %g, %g)\n", position[0], position[1], position[2]);
}

int main()
{
	std::vector<Vec3> positions = { { 1.0f, 5.0f, 0.0f }, { 2.0f, 5.0f, 0.0f }, { 3.0f, 7.0f, 0.0f } };
	// The row shows the first entity's value; Y and X differ among the three, Z does not.
	const Vec3 shown = positions.front();
	Write(positions, shown, { 4.0f, 5.0f, 0.0f }); // the person types 4 in X
	Print(positions);
	std::printf("--\n");
	Write(positions, positions.front(), { 4.0f, 9.0f, 0.0f }); // then types 9 in Y
	Print(positions);
}
