#include <glm/glm.hpp>

#include <algorithm>
#include <cmath>
#include <cstdio>

constexpr float c_Pi = 3.14159265f;
constexpr float c_MinRoughness = 0.045f;

struct Surface
{
	glm::vec3 Normal = glm::vec3(0.0f, 0.0f, 1.0f);
	glm::vec3 View = glm::vec3(0.0f, 0.0f, 1.0f);
	glm::vec3 Albedo = glm::vec3(0.8f);
	float Metallic = 0.0f;
	float Roughness = 0.5f;
	glm::vec3 F0 = glm::vec3(0.04f);
};

float DistributionGGX(float NoH, float alpha)
{
	const float alpha2 = alpha * alpha;
	const float f = (NoH * alpha2 - NoH) * NoH + 1.0f;
	return alpha2 / (c_Pi * f * f);
}

float VisibilitySmithGGXCorrelated(float NoV, float NoL, float alpha)
{
	const float alpha2 = alpha * alpha;
	const float lambdaV = NoL * std::sqrt((NoV - NoV * alpha2) * NoV + alpha2);
	const float lambdaL = NoV * std::sqrt((NoL - NoL * alpha2) * NoL + alpha2);
	return 0.5f / std::max(lambdaV + lambdaL, 1e-5f);
}

glm::vec3 FresnelSchlick(const glm::vec3& f0, float VoH)
{
	const float f = std::pow(1.0f - VoH, 5.0f);
	return glm::vec3(f) + f0 * (1.0f - f);
}

// The shader's EvaluateLightWeighted for a point light, with both weights 1 and a specular energy of 1.
glm::vec3 EvaluateLight(const Surface& surface, const glm::vec3& lightDirection, const glm::vec3& radiance)
{
	const glm::vec3 H = glm::normalize(surface.View + lightDirection);
	const float NoL = glm::clamp(glm::dot(surface.Normal, lightDirection), 0.0f, 1.0f);
	if (NoL <= 0.0f)
		return glm::vec3(0.0f);
	const float NoV = std::max(glm::dot(surface.Normal, surface.View), 1e-4f);
	const float NoH = glm::clamp(glm::dot(surface.Normal, H), 0.0f, 1.0f);
	const float VoH = glm::clamp(glm::dot(surface.View, H), 0.0f, 1.0f);

	const float roughness = std::max(surface.Roughness, c_MinRoughness);
	const float alpha = roughness * roughness;
	const glm::vec3 F = FresnelSchlick(surface.F0, VoH);
	const glm::vec3 specular = DistributionGGX(NoH, alpha) * VisibilitySmithGGXCorrelated(NoV, NoL, alpha) * F;
	const glm::vec3 diffuse = (glm::vec3(1.0f) - F) * (1.0f - surface.Metallic) * surface.Albedo / c_Pi;
	return (diffuse + specular) * radiance * NoL;
}

void Print(const char* name, const glm::vec3& light)
{
	std::printf("%-22s %.4f %.4f %.4f\n", name, light.x, light.y, light.z);
}

int main()
{
	const glm::vec3 radiance(1.0f);
	Surface plastic;
	Print("plastic, head-on", EvaluateLight(plastic, glm::vec3(0.0f, 0.0f, 1.0f), radiance));

	const glm::vec3 slanted = glm::normalize(glm::vec3(1.0f, 0.0f, 1.0f));
	Print("plastic, light at 45", EvaluateLight(plastic, slanted, radiance));

	Surface gold;
	gold.Albedo = glm::vec3(1.0f, 0.77f, 0.34f);
	gold.Metallic = 1.0f;
	gold.F0 = gold.Albedo;
	Print("gold, light at 45", EvaluateLight(gold, slanted, radiance));

	Surface mirror = plastic;
	mirror.Roughness = 0.0f;
	Print("roughness 0 reads 0.045", EvaluateLight(mirror, glm::vec3(0.0f, 0.0f, 1.0f), radiance));
	return 0;
}
