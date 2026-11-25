// RMS of a sine of amplitude 0.8 over a whole number of periods, against amplitude / sqrt(2).
#include <cmath>
#include <cstdio>

int main()
{
	constexpr double c_Pi = 3.14159265358979;
	constexpr double c_SampleRate = 48000.0;
	constexpr double c_Amplitude = 0.8;
	constexpr int c_Frames = 4800;

	double sum = 0.0;
	for (int frame = 0; frame < c_Frames; frame++)
	{
		const double sample = c_Amplitude * std::sin(2.0 * c_Pi * 440.0 * frame / c_SampleRate);
		sum += sample * sample;
	}
	std::printf("measured %.4f, expected %.4f\n", std::sqrt(sum / c_Frames), c_Amplitude / std::sqrt(2.0));
	return 0;
}
