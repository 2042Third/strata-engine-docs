// A toy mixer pulled by the caller, with gain smoothing, and the RMS measurement of a test.
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <vector>

constexpr float c_SampleRate = 48000.0f;
constexpr float c_Pi = 3.14159265f;
constexpr float c_Amplitude = 0.5f;
constexpr uint64_t c_SettleFrames = 2400;

class ToyMixer
{
public:
	// The source's wanted gains; the mix moves toward them a little every frame.
	void SetTarget(float left, float right)
	{
		m_TargetLeft = left;
		m_TargetRight = right;
	}

	// Pulls frameCount stereo frames, interleaved, like AudioEngine::ReadFrames.
	std::vector<float> Render(uint64_t frameCount)
	{
		std::vector<float> output;
		for (uint64_t frame = 0; frame < frameCount; frame++)
		{
			const float sample = c_Amplitude * std::sin(2.0f * c_Pi * 440.0f * static_cast<float>(m_Frame++) / c_SampleRate);
			m_GainLeft += (m_TargetLeft - m_GainLeft) * 0.002f;
			m_GainRight += (m_TargetRight - m_GainRight) * 0.002f;
			output.push_back(sample * m_GainLeft);
			output.push_back(sample * m_GainRight);
		}
		return output;
	}

private:
	uint64_t m_Frame = 0;
	float m_GainLeft = 0.5f;
	float m_GainRight = 0.5f;
	float m_TargetLeft = 0.5f;
	float m_TargetRight = 0.5f;
};

float ComputeRms(const std::vector<float>& samples, size_t channel)
{
	double sum = 0.0;
	size_t count = 0;
	for (size_t index = channel; index < samples.size(); index += 2)
	{
		sum += static_cast<double>(samples[index]) * samples[index];
		count++;
	}
	return count > 0 ? static_cast<float>(std::sqrt(sum / static_cast<double>(count))) : 0.0f;
}

int main()
{
	ToyMixer early;
	early.SetTarget(0.2f, 0.8f);
	const std::vector<float> tooSoon = early.Render(4800);
	std::printf("too soon: left %.4f right %.4f ratio %.3f\n", ComputeRms(tooSoon, 0), ComputeRms(tooSoon, 1), ComputeRms(tooSoon, 1) / ComputeRms(tooSoon, 0));

	ToyMixer settled;
	settled.SetTarget(0.2f, 0.8f);
	settled.Render(c_SettleFrames);
	const std::vector<float> steady = settled.Render(4800);
	std::printf("settled:  left %.4f right %.4f ratio %.3f\n", ComputeRms(steady, 0), ComputeRms(steady, 1), ComputeRms(steady, 1) / ComputeRms(steady, 0));
	std::printf("sine RMS: %.4f\n", c_Amplitude / std::sqrt(2.0f));
	return 0;
}
