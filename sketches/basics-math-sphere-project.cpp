// Projects a light that is 1 above the horizon and 0 below onto the nine spherical harmonics.
#include <array>
#include <cmath>
#include <cstdio>
#include <glm/glm.hpp>

std::array<float, 9> Basis(const glm::vec3& n) { return { 0.282095f, 0.488603f * n.y, 0.488603f * n.z, 0.488603f * n.x, 1.092548f * n.x * n.y, 1.092548f * n.y * n.z, 0.315392f * (3.0f * n.z * n.z - 1.0f), 1.092548f * n.x * n.z, 0.546274f * (n.x * n.x - n.y * n.y) }; }

int main()
{
	const float pi = 3.14159265f;
	std::array<float, 9> c = {};
	for (int cell = 0; cell < 128 * 256; cell++) // 128 rows of polar angle, 256 columns of azimuth
	{
		const float polar = (static_cast<float>(cell / 256) + 0.5f) / 128.0f * pi, azimuth = (static_cast<float>(cell % 256) + 0.5f) / 256.0f * 2.0f * pi;
		const glm::vec3 n(std::sin(polar) * std::cos(azimuth), std::cos(polar), std::sin(polar) * std::sin(azimuth));
		const float weight = (n.y > 0.0f ? 1.0f : 0.0f) * std::sin(polar) * (pi / 128.0f) * (2.0f * pi / 256.0f); // light times solid angle
		for (int i = 0; i < 9; i++)
			c[i] += weight * Basis(n)[i];
	}
	for (int i = 0; i < 9; i++)
		std::printf("c%d = %.4f\n", i, c[i]);
}
