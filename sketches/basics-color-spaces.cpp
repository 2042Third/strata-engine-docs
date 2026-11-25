// A color space as a matrix: built from three primaries and a white, then one change of space.
#include <cstdio>
#include <glm/glm.hpp>

glm::dvec3 ToXYZ(const glm::dvec2& xy)
{
	return glm::dvec3(xy.x / xy.y, 1.0, (1.0 - xy.x - xy.y) / xy.y);
}

glm::dmat3 RGBToXYZ(const glm::dvec2 primaries[3], const glm::dvec2& white)
{
	const glm::dmat3 columns(ToXYZ(primaries[0]), ToXYZ(primaries[1]), ToXYZ(primaries[2]));
	const glm::dvec3 scale = glm::inverse(columns) * ToXYZ(white); // makes (1, 1, 1) the white
	return columns * glm::dmat3(scale.x, 0.0, 0.0, 0.0, scale.y, 0.0, 0.0, 0.0, scale.z);
}

int main()
{
	const glm::dvec2 d65(0.3127, 0.3290);
	const glm::dvec2 rec709[3] = { { 0.64, 0.33 }, { 0.30, 0.60 }, { 0.15, 0.06 } };
	const glm::dvec2 rec2020[3] = { { 0.708, 0.292 }, { 0.170, 0.797 }, { 0.131, 0.046 } };
	const glm::dmat3 change = glm::inverse(RGBToXYZ(rec709, d65)) * RGBToXYZ(rec2020, d65);
	const glm::dvec3 green = change * glm::dvec3(0.0, 1.0, 0.0);
	std::printf("pure Rec. 2020 green in Rec. 709: (%.4f, %.4f, %.4f)\n", green.x, green.y, green.z);
}
