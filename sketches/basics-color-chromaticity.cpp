// Chromaticity: linear Rec. 709 color to XYZ with the matrix of its primaries, then x and y.
#include <cstdio>
#include <glm/glm.hpp>

void Print(const char* name, const glm::dvec3& rgb)
{
	// glm builds a matrix column by column: these are the columns for red, green and blue.
	const glm::dmat3 toXYZ(0.4124, 0.2126, 0.0193, 0.3576, 0.7152, 0.1192, 0.1805, 0.0722, 0.9505);
	const glm::dvec3 xyz = toXYZ * rgb;
	const double sum = xyz.x + xyz.y + xyz.z;
	std::printf("%-6s Y %.4f  x %.4f  y %.4f\n", name, xyz.y, xyz.x / sum, xyz.y / sum);
}

int main()
{
	Print("red", glm::dvec3(1.0, 0.0, 0.0));
	Print("green", glm::dvec3(0.0, 1.0, 0.0));
	Print("blue", glm::dvec3(0.0, 0.0, 1.0));
	Print("white", glm::dvec3(1.0, 1.0, 1.0));
	Print("white2", glm::dvec3(2.0, 2.0, 2.0));
	return 0;
}
