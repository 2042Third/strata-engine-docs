#include <glm/glm.hpp>

#include <cstdio>

namespace
{
	// Linear sRGB to XYZ, and CAT02's matrix from XYZ to cone responses (rows as published; glm is column-major).
	const glm::dmat3 c_SRGBToXYZ = glm::transpose(glm::dmat3(0.4124564, 0.3575761, 0.1804375, 0.2126729, 0.7151522, 0.0721750, 0.0193339, 0.1191920, 0.9503041));
	const glm::dmat3 c_CAT02 = glm::transpose(glm::dmat3(0.7328, 0.4296, -0.1624, -0.7036, 1.6975, 0.0061, 0.0030, 0.0136, 0.9834));
	const glm::dvec2 c_D65 = { 0.3127, 0.3290 };

	glm::dvec3 XYToXYZ(const glm::dvec2& xy)
	{
		return glm::dvec3(xy.x / xy.y, 1.0, (1.0 - xy.x - xy.y) / xy.y);
	}

	// Von Kries: scale each cone response by (response of the target white) / (response of the light), then return to RGB.
	glm::dmat3 MakeAdaptation(const glm::dvec2& lightXY)
	{
		const glm::dvec3 gains = (c_CAT02 * XYToXYZ(c_D65)) / (c_CAT02 * XYToXYZ(lightXY));
		const glm::dmat3 scale(gains.x, 0.0, 0.0, 0.0, gains.y, 0.0, 0.0, 0.0, gains.z);
		return glm::inverse(c_SRGBToXYZ) * glm::inverse(c_CAT02) * scale * c_CAT02 * c_SRGBToXYZ;
	}

	// The shortcut: divide each RGB channel by the light's own RGB. The sRGB primaries stand in for cones.
	glm::dvec3 ScaleRGB(const glm::dvec2& lightXY, const glm::dvec3& color)
	{
		return color / (glm::inverse(c_SRGBToXYZ) * XYToXYZ(lightXY));
	}

	// The ASC CDL around middle gray: the offset is in fractions of middle gray, as in Strata.
	glm::dvec3 ApplyCDL(const glm::dvec3& color, const glm::dvec3& slope, const glm::dvec3& offset, const glm::dvec3& power)
	{
		const glm::dvec3 shifted = glm::max(color * slope + offset * 0.18, glm::dvec3(0.0));
		return 0.18 * glm::pow(shifted / 0.18, power);
	}

	void Print(const char* label, const glm::dvec3& color)
	{
		std::printf("%-26s %.4f %.4f %.4f\n", label, color.x, color.y, color.z);
	}
}

int main()
{
	const glm::dvec2 tungsten(0.4234, 0.3990); // The light of a 3200 K lamp, on the Planckian locus.
	const glm::dmat3 adaptation = MakeAdaptation(tungsten);
	const glm::dvec3 lamp = glm::inverse(c_SRGBToXYZ) * XYToXYZ(tungsten);
	const glm::dvec3 orange(0.8, 0.3, 0.05);
	Print("lamp white", lamp);
	Print("lamp white, adapted", adaptation * lamp);
	Print("gray 0.18, adapted", adaptation * glm::dvec3(0.18));
	Print("orange, von Kries", adaptation * orange);
	Print("orange, RGB scaling", ScaleRGB(tungsten, orange));
	Print("CDL slope 2", ApplyCDL(glm::dvec3(0.18, 0.36, 0.72), glm::dvec3(2.0), glm::dvec3(0.0), glm::dvec3(1.0)));
	Print("CDL offset 0.05", ApplyCDL(glm::dvec3(0.0, 0.18, 0.72), glm::dvec3(1.0), glm::dvec3(0.05), glm::dvec3(1.0)));
	Print("CDL power 1.2", ApplyCDL(glm::dvec3(0.045, 0.18, 0.72), glm::dvec3(1.0), glm::dvec3(0.0), glm::dvec3(1.2)));
	return 0;
}
