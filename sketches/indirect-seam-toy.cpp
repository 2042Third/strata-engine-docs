// A toy of the indirect light's seam on one color channel: one struct of inputs, two gathers and a compose step.
#include <cstdio>

enum class Form
{
	Probes,
	Screen,
	Sky,
	Ambient
};

struct Inputs
{
	Form Kind = Form::Ambient;
	bool Environment = false;
	float ProbeWeight = 0.0f;
	float ProbeIrradiance = 0.0f;
	float ProbeRadiance = 0.0f;
	float ScreenLight = 0.0f; // Premultiplied: the light times the confidence
	float ScreenConfidence = 0.0f;
	float SkyIrradiance = 0.0f;
	float SkyRadiance = 0.0f;
};

constexpr float c_Albedo = 0.5f;
constexpr float c_SpecularColor = 0.1f;
constexpr float c_DiffuseOcclusion = 0.8f;
constexpr float c_SpecularOcclusion = 0.6f;
constexpr float c_ScreenOcclusion = 0.9f;
constexpr float c_Ambient = 0.2f;
constexpr float c_SkyIntensity = 2.0f;

Form ChooseForm(const Inputs& inputs)
{
	if (inputs.ProbeWeight > 0.0f)
		return Form::Probes;
	if (inputs.ScreenConfidence > 0.0f)
		return Form::Screen;
	return inputs.Environment ? Form::Sky : Form::Ambient;
}

float GatherDiffuse(const Inputs& inputs)
{
	const float scatter = c_Albedo * (1.0f - c_SpecularColor);
	const float sky = 1.0f - inputs.ProbeWeight;
	float diffuse = c_Ambient * c_Albedo;
	if (inputs.Kind == Form::Probes)
		diffuse = (inputs.ProbeIrradiance + inputs.SkyIrradiance * c_SkyIntensity * sky) * scatter;
	else if (inputs.Kind == Form::Screen)
		diffuse = inputs.SkyIrradiance * scatter * c_SkyIntensity;
	else if (inputs.Kind == Form::Sky)
		diffuse = inputs.SkyIrradiance * scatter;
	return diffuse * c_DiffuseOcclusion;
}

float GatherSpecular(const Inputs& inputs)
{
	float fallback = inputs.SkyRadiance;
	if (inputs.Kind == Form::Ambient)
		return 0.0f;
	if (inputs.Kind == Form::Probes)
		fallback = inputs.ProbeRadiance + inputs.SkyRadiance * c_SkyIntensity * (1.0f - inputs.ProbeWeight);
	else if (inputs.Kind == Form::Screen)
		fallback = inputs.SkyRadiance * c_SkyIntensity;
	if (inputs.ScreenConfidence > 0.0f)
		return (fallback * c_SpecularOcclusion * (1.0f - inputs.ScreenConfidence) + inputs.ScreenLight * c_ScreenOcclusion) * c_SpecularColor;
	return fallback * c_SpecularColor * c_SpecularOcclusion;
}

float Compose(const Inputs& inputs, float diffuse, float specular)
{
	if (inputs.Kind == Form::Ambient)
		return diffuse;
	if (inputs.Kind == Form::Sky)
		return (diffuse + specular) * c_SkyIntensity;
	return diffuse + specular;
}

void Shade(const char* name, Inputs inputs)
{
	inputs.Kind = ChooseForm(inputs);
	const float diffuse = GatherDiffuse(inputs);
	const float specular = GatherSpecular(inputs);
	std::printf("%-8s form %d: diffuse %.3f specular %.3f total %.3f\n", name, static_cast<int>(inputs.Kind), diffuse, specular,
		Compose(inputs, diffuse, specular));
}

int main()
{
	Inputs probes;
	probes.Environment = true;
	probes.ProbeWeight = 0.75f;
	probes.ProbeIrradiance = 0.6f;
	probes.ProbeRadiance = 0.9f;
	probes.SkyIrradiance = 0.4f;
	probes.SkyRadiance = 0.5f;
	Shade("probes", probes);

	Inputs screen;
	screen.Environment = true;
	screen.ScreenLight = 0.4f;
	screen.ScreenConfidence = 0.5f;
	screen.SkyIrradiance = 0.4f;
	screen.SkyRadiance = 0.5f;
	Shade("screen", screen);

	Inputs sky;
	sky.Environment = true;
	sky.SkyIrradiance = 0.4f;
	sky.SkyRadiance = 0.5f;
	Shade("sky", sky);

	Shade("ambient", Inputs());
}
