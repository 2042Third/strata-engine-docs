// A toy mixer: voices summed into one stream that a callback pulls, one period at a time.
#include <algorithm>
#include <atomic>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <numbers>
#include <vector>

struct ToyVoice
{
	float Frequency = 440.0f; // Hz
	float Volume = 0.5f;
	double Phase = 0.0; // 0 to 1 around one cycle
};

class ToyMixer
{
public:
	explicit ToyMixer(uint32_t sampleRate)
		: m_SampleRate(sampleRate)
	{
	}

	void AddVoice(float frequency, float volume) { m_Voices.push_back({ frequency, volume, 0.0 }); }
	// Another thread may call this while the callback runs: the callback reads the value with one atomic load.
	void SetMasterVolume(float volume) { m_MasterVolume.store(std::max(volume, 0.0f), std::memory_order_relaxed); }

	// What the device calls when it needs the next period: the sum of every voice, times the master volume.
	void Pull(float* output, uint32_t frameCount)
	{
		const float master = m_MasterVolume.load(std::memory_order_relaxed);
		for (uint32_t frame = 0; frame < frameCount; frame++)
		{
			float sum = 0.0f;
			for (ToyVoice& voice : m_Voices)
			{
				sum += voice.Volume * static_cast<float>(std::sin(2.0 * std::numbers::pi * voice.Phase));
				voice.Phase += voice.Frequency / static_cast<double>(m_SampleRate);
				if (voice.Phase >= 1.0)
					voice.Phase -= 1.0;
			}
			output[frame] = sum * master;
		}
	}
private:
	uint32_t m_SampleRate;
	std::atomic<float> m_MasterVolume = 1.0f;
	std::vector<ToyVoice> m_Voices;
};

int main()
{
	ToyMixer mixer(48000);
	mixer.AddVoice(440.0f, 0.6f);
	mixer.AddVoice(660.0f, 0.6f);

	std::vector<float> period(480);
	for (float master : { 1.0f, 0.5f })
	{
		mixer.SetMasterVolume(master);
		mixer.Pull(period.data(), 480);
		float peak = 0.0f;
		for (float sample : period)
			peak = std::max(peak, std::abs(sample));
		std::printf("master %.1f: peak %.3f of a possible 1.000\n", master, peak);
	}
	return 0;
}
