// The time bar's color from green to red: blended on sRGB values, then in linear light.
#include <cstdio>
#include <glm/glm.hpp>

glm::vec3 Decode(const glm::vec3& encoded)
{
	return glm::mix(encoded / 12.92f, glm::pow((encoded + 0.055f) / 1.055f, glm::vec3(2.4f)), glm::greaterThan(encoded, glm::vec3(0.04045f)));
}

glm::vec3 Encode(const glm::vec3& linear)
{
	return glm::mix(linear * 12.92f, 1.055f * glm::pow(linear, glm::vec3(1.0f / 2.4f)) - 0.055f, glm::greaterThan(linear, glm::vec3(0.0031308f)));
}

int main()
{
	const glm::vec3 green(0.0f, 1.0f, 0.0f);
	const glm::vec3 red(1.0f, 0.0f, 0.0f);
	const glm::vec3 weights(0.2126f, 0.7152f, 0.0722f);
	const glm::vec3 onSRGB = glm::mix(green, red, 0.5f);
	const glm::vec3 inLinear = Encode(glm::mix(Decode(green), Decode(red), 0.5f));
	std::printf("sRGB blend (%.4f, %.4f, %.4f): luminance %.4f\n", onSRGB.r, onSRGB.g, onSRGB.b, glm::dot(Decode(onSRGB), weights));
	std::printf("linear blend (%.4f, %.4f, %.4f): luminance %.4f\n", inLinear.r, inLinear.g, inLinear.b, glm::dot(Decode(inLinear), weights));
	return 0;
}
