#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>

// Middle gray (0.18, already exposed) under each of Strata's curves, from the formulas of Tonemap.frag.slang: the value
// the curve returns, and its sRGB code. A gray input has equal channels, so one channel stands for all three.
using Vec3 = std::array<float, 3>;
using Mat3 = std::array<Vec3, 3>;

Vec3 Multiply(const Mat3& matrix, const Vec3& v)
{
	Vec3 result{};
	for (int row = 0; row < 3; row++)
		result[row] = matrix[row][0] * v[0] + matrix[row][1] * v[1] + matrix[row][2] * v[2];
	return result;
}

float ACES(float gray)
{
	const Mat3 input = { Vec3{ 0.59719f, 0.35458f, 0.04823f }, Vec3{ 0.07600f, 0.90834f, 0.01566f }, Vec3{ 0.02840f, 0.13383f, 0.83777f } };
	const Mat3 output = { Vec3{ 1.60475f, -0.53108f, -0.07367f }, Vec3{ -0.10208f, 1.10813f, -0.00605f }, Vec3{ -0.00327f, -0.07276f, 1.07602f } };
	Vec3 c = Multiply(input, { gray, gray, gray });
	for (float& v : c)
		v = (v * (v + 0.0245786f) - 0.000090537f) / (v * (0.983729f * v + 0.4329510f) + 0.238081f);
	return Multiply(output, c)[0];
}

float AgX(float gray)
{
	const Mat3 inset = { Vec3{ 0.842479f, 0.078434f, 0.079224f }, Vec3{ 0.042328f, 0.878469f, 0.079166f }, Vec3{ 0.042376f, 0.078434f, 0.879143f } };
	const Mat3 outset = { Vec3{ 1.196879f, -0.098021f, -0.099030f }, Vec3{ -0.052897f, 1.151903f, -0.098961f }, Vec3{ -0.052972f, -0.098043f, 1.151074f } };
	Vec3 c = Multiply(inset, { gray, gray, gray });
	for (float& v : c)
	{
		const float x = std::clamp((std::log2(v) + 12.47393f) / (12.47393f + 4.026069f), 0.0f, 1.0f);
		const float x2 = x * x;
		const float x4 = x2 * x2;
		v = 15.5f * x4 * x2 - 40.14f * x4 * x + 31.96f * x4 - 6.868f * x2 * x + 0.4298f * x2 + 0.1191f * x - 0.00232f;
	}
	return std::pow(std::max(Multiply(outset, c)[1], 0.0f), 2.2f); // the curve's output is gamma 2.2: back to linear
}

float KhronosNeutral(float gray)
{
	const float offset = gray < 0.08f ? gray - 6.25f * gray * gray : 0.04f;
	return gray - offset; // below the compression start (0.76) nothing else changes
}

float Filmic(float gray)
{
	return gray; // the curve returns 0.18 at t = 0 by construction (target T1)
}

float Encode(float linear)
{
	return linear <= 0.0031308f ? 12.92f * linear : 1.055f * std::pow(linear, 1.0f / 2.4f) - 0.055f;
}

int main()
{
	const float gray = 0.18f;
	const float exposed = gray * std::exp2(0.8f);
	const char* names[] = { "None", "Reinhard", "ACES", "ACES +0.8 EV", "AgX", "Khronos Neutral", "Filmic" };
	const float values[] = { gray, gray / (1.0f + gray), ACES(gray), ACES(exposed), AgX(gray), KhronosNeutral(gray), Filmic(gray) };
	for (int index = 0; index < 7; index++)
		std::printf("%-16s %.4f  code %3.0f\n", names[index], values[index], Encode(values[index]) * 255.0f);
	return 0;
}
