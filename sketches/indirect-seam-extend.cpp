// Adds a new term to a toy's inputs at the end and checks that every old pixel keeps its exact bits.
#include <cstdio>
#include <cstring>

enum class Form
{
	Probes,
	Sky,
	Ambient
};

struct Inputs
{
	Form Kind = Form::Probes;
	float Diffuse = 0.0f;
	float Specular = 0.0f;
	float Bounce = 0.0f; // The new field, last: what the old code never knew is 0
};

float ComposeBefore(const Inputs& inputs)
{
	if (inputs.Kind == Form::Ambient)
		return inputs.Diffuse;
	if (inputs.Kind == Form::Sky)
		return (inputs.Diffuse + inputs.Specular) * 2.0f;
	return inputs.Diffuse + inputs.Specular;
}

float ComposeAfter(const Inputs& inputs)
{
	return ComposeBefore(inputs) + inputs.Bounce;
}

bool SameBits(float a, float b)
{
	return std::memcmp(&a, &b, sizeof(float)) == 0;
}

int main()
{
	const Form forms[] = { Form::Probes, Form::Sky, Form::Ambient };
	int same = 0;
	for (const Form form : forms)
	{
		Inputs inputs;
		inputs.Kind = form;
		inputs.Diffuse = 0.288f;
		inputs.Specular = 0.069f;
		same += SameBits(ComposeBefore(inputs), ComposeAfter(inputs)) ? 1 : 0;
	}
	std::printf("forms with the same bits while Bounce is 0: %d of 3\n", same);

	Inputs lit;
	lit.Diffuse = 0.288f;
	lit.Specular = 0.069f;
	lit.Bounce = 0.05f;
	std::printf("with Bounce 0.05: %.3f instead of %.3f\n", ComposeAfter(lit), ComposeBefore(lit));
}
