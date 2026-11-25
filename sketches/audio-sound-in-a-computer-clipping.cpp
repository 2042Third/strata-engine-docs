#include <cmath>
#include <cstdio>

int main()
{
	const float sampleRate = 48000.0f;
	const float twoPi = 6.2831853f;
	for (int pass = 0; pass < 2; pass++)
	{
		const float gain = pass == 0 ? 1.0f : 0.5011872f; // 0 dB, then -6 dB
		float peak = 0.0f;
		int outside = 0;
		for (int i = 0; i < 48000; i++)
		{
			const float time = i / sampleRate;
			const float first = gain * 0.6f * std::sin(twoPi * 440.0f * time);
			const float second = gain * 0.6f * std::sin(twoPi * 660.0f * time);
			const float sum = first + second;
			peak = std::fmax(peak, std::fabs(sum));
			if (sum > 1.0f || sum < -1.0f)
				outside++;
		}
		std::printf("gain %.4f: peak %.3f, samples outside: %d\n", gain, peak, outside);
	}
}
