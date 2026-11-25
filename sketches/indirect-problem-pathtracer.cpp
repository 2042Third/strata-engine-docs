// Path traces a Cornell box: random bounces, a fixed seed, and more samples per pixel for less noise.
#include <glm/glm.hpp>

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <vector>

struct Random
{
	uint64_t State = 12345;

	float Next() // A number in [0, 1)
	{
		State = State * 6364136223846793005ULL + 1442695040888963407ULL;
		return float(State >> 40) / 16777216.0f;
	}
};

struct Wall
{
	int Axis = 0;
	float Position = 0.0f;
	glm::vec3 Albedo = glm::vec3(0.0f);
};

// The box is 2 wide, 2 deep and 2 high with its front open. The last wall is the ceiling, with a light patch in it.
const Wall c_Walls[5] = { { 0, -1.0f, { 0.63f, 0.065f, 0.05f } }, { 0, 1.0f, { 0.14f, 0.45f, 0.09f } },
	{ 2, -1.0f, { 0.7f, 0.7f, 0.7f } }, { 1, 0.0f, { 0.7f, 0.7f, 0.7f } }, { 1, 2.0f, { 0.7f, 0.7f, 0.7f } } };
const float c_LightRadiance = 18.0f;
const float c_LightHalfSize = 0.3f;

bool InsideBox(const glm::vec3& point)
{
	return std::abs(point.x) <= 1.001f && point.y >= -0.001f && point.y <= 2.001f && std::abs(point.z) <= 1.001f;
}

// The light that arrives along a ray, after at most maxBounces scatterings.
glm::vec3 Radiance(glm::vec3 origin, glm::vec3 direction, int maxBounces, Random& random)
{
	glm::vec3 throughput(1.0f);
	for (int bounce = 0; bounce <= maxBounces; bounce++)
	{
		float nearest = 1e30f;
		int hit = -1;
		for (int i = 0; i < 5; i++)
		{
			const float along = direction[c_Walls[i].Axis];
			if (std::abs(along) < 1e-6f)
				continue;
			const float t = (c_Walls[i].Position - origin[c_Walls[i].Axis]) / along;
			if (t > 1e-4f && t < nearest && InsideBox(origin + direction * t))
			{
				nearest = t;
				hit = i;
			}
		}
		if (hit < 0)
			return glm::vec3(0.0f); // The ray left through the open front
		origin += direction * nearest;
		if (hit == 4 && std::abs(origin.x) < c_LightHalfSize && std::abs(origin.z) < c_LightHalfSize)
			return throughput * c_LightRadiance; // The light patch emits and absorbs
		// A rough surface scatters toward a random direction, favoring those near its normal.
		const int axis = c_Walls[hit].Axis;
		const float side = direction[axis] > 0.0f ? -1.0f : 1.0f;
		const float angle = 6.2831853f * random.Next();
		const float radius = std::sqrt(random.Next());
		direction[(axis + 1) % 3] = radius * std::cos(angle);
		direction[(axis + 2) % 3] = radius * std::sin(angle);
		direction[axis] = side * std::sqrt(1.0f - radius * radius);
		throughput *= c_Walls[hit].Albedo; // The cosine and the sampling density cancel
	}
	return glm::vec3(0.0f);
}

std::vector<glm::vec3> Render(int size, int samples, int maxBounces, uint64_t seed)
{
	Random random;
	random.State = seed;
	std::vector<glm::vec3> image(size * size, glm::vec3(0.0f));
	for (int y = 0; y < size; y++)
	{
		for (int x = 0; x < size; x++)
		{
			glm::vec3 sum(0.0f);
			for (int s = 0; s < samples; s++)
			{
				const float u = ((x + random.Next()) / size * 2.0f - 1.0f) * 0.45f;
				const float v = (1.0f - (y + random.Next()) / size * 2.0f) * 0.45f;
				sum += Radiance(glm::vec3(0.0f, 1.0f, 3.4f), glm::normalize(glm::vec3(u, v, -1.0f)), maxBounces, random);
			}
			image[y * size + x] = sum / float(samples);
		}
	}
	return image;
}

float RootMeanSquareError(const std::vector<glm::vec3>& image, const std::vector<glm::vec3>& reference)
{
	double sum = 0.0;
	for (size_t i = 0; i < image.size(); i++)
	{
		const glm::vec3 difference = image[i] - reference[i];
		sum += glm::dot(difference, difference);
	}
	return float(std::sqrt(sum / (3.0 * image.size())));
}

// The picture for the page's figure: gamma-encoded bytes in the PPM format, written when the program gets any argument.
void WritePicture(const std::vector<glm::vec3>& image, int size)
{
	std::printf("P6\n%d %d\n255\n", size, size);
	for (const glm::vec3& color : image)
	{
		for (int channel = 0; channel < 3; channel++)
			std::putchar(int(255.0f * std::pow(glm::clamp(color[channel], 0.0f, 1.0f), 1.0f / 2.2f) + 0.5f));
	}
}

int main(int argc, char**)
{
	if (argc > 1)
	{
		WritePicture(Render(320, 4096, 8, 4), 320);
		return 0;
	}
	const int size = 24;
	const std::vector<glm::vec3> reference = Render(size, 4096, 8, 1);
	for (int samples : { 4, 64, 1024 })
		std::printf("%4d samples: error %.3f\n", samples, RootMeanSquareError(Render(size, samples, 8, 2), reference));

	// One floor pixel near the red wall, lit directly only and then with every bounce.
	const glm::vec3 direct = Render(size, 4096, 1, 3)[20 * size + 6];
	const glm::vec3 full = reference[20 * size + 6];
	std::printf("direct only: red %.3f green %.3f\n", direct.r, direct.g);
	std::printf("all bounces: red %.3f green %.3f\n", full.r, full.g);
	return 0;
}
