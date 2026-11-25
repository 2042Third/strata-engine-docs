// A toy irradiance convolution: a tiny cube map of radiance, and the cosine-weighted average of it around a normal.
#include <cmath>
#include <cstdio>

struct Vec3
{
	float X, Y, Z;
};

constexpr int c_Size = 8;
constexpr float c_Pi = 3.14159265f;

// The engine's face convention: +X, -X, +Y, -Y, +Z, -Z, texel row 0 at the top of each face.
Vec3 FaceDirection(float s, float t, int face)
{
	switch (face)
	{
		case 0: return { 1.0f, -t, -s };
		case 1: return { -1.0f, -t, s };
		case 2: return { s, 1.0f, t };
		case 3: return { s, -1.0f, -t };
		case 4: return { s, -t, 1.0f };
		default: return { -s, -t, -1.0f };
	}
}

// The sky: radiance 1 above the horizon, 0 below it.
float SkyRadiance(const Vec3& direction)
{
	return direction.Y > 0.0f ? 1.0f : 0.0f;
}

// The convolution at one normal: sum of radiance * cosine * solid angle, divided by pi.
float Irradiance(const Vec3& normal)
{
	float sum = 0.0f;
	float totalSolidAngle = 0.0f;
	for (int face = 0; face < 6; face++)
		for (int row = 0; row < c_Size; row++)
			for (int column = 0; column < c_Size; column++)
			{
				float s = (static_cast<float>(column) + 0.5f) / c_Size * 2.0f - 1.0f;
				float t = (static_cast<float>(row) + 0.5f) / c_Size * 2.0f - 1.0f;
				Vec3 d = FaceDirection(s, t, face);
				float length = std::sqrt(d.X * d.X + d.Y * d.Y + d.Z * d.Z);
				d = { d.X / length, d.Y / length, d.Z / length };
				// A texel near a face's corner is seen under a smaller angle than one at its center.
				float solidAngle = (2.0f / c_Size) * (2.0f / c_Size) / std::pow(1.0f + s * s + t * t, 1.5f);
				float cosine = d.X * normal.X + d.Y * normal.Y + d.Z * normal.Z;
				totalSolidAngle += solidAngle;
				if (cosine > 0.0f)
					sum += SkyRadiance(d) * cosine * solidAngle;
			}
	std::printf("  solid angles add up to %.4f (4 pi is %.4f)\n", totalSolidAngle, 4.0f * c_Pi);
	return sum / c_Pi;
}

int main()
{
	std::printf("normal up:\n");
	std::printf("  irradiance / pi = %.4f\n", Irradiance({ 0.0f, 1.0f, 0.0f }));
	std::printf("normal sideways:\n");
	std::printf("  irradiance / pi = %.4f\n", Irradiance({ 1.0f, 0.0f, 0.0f }));
	std::printf("normal down:\n");
	std::printf("  irradiance / pi = %.4f\n", Irradiance({ 0.0f, -1.0f, 0.0f }));
	return 0;
}
