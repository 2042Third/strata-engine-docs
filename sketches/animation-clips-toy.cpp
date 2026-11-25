// A linear-only clip sampler for one channel of single floats: binary search for the key, hold outside the keys.
#include <algorithm>
#include <cstddef>
#include <cstdio>
#include <vector>

namespace
{

	struct Channel
	{
		std::vector<float> Times;
		std::vector<float> Values;
	};

	// The last key whose time is not after `time`.
	size_t FindKey(const Channel& channel, float time)
	{
		auto next = std::upper_bound(channel.Times.begin(), channel.Times.end(), time);
		size_t index = static_cast<size_t>(next - channel.Times.begin());
		return index == 0 ? 0 : index - 1;
	}

	float Sample(const Channel& channel, float time, size_t& outKey)
	{
		const size_t last = channel.Times.size() - 1;
		if (!(time > channel.Times[0]) || last == 0)
		{
			outKey = 0;
			return channel.Values[0];
		}
		if (time >= channel.Times[last])
		{
			outKey = last;
			return channel.Values[last];
		}
		const size_t key = std::min(FindKey(channel, time), last - 1);
		const float span = channel.Times[key + 1] - channel.Times[key];
		const float s = (time - channel.Times[key]) / span;
		outKey = key;
		return channel.Values[key] + (channel.Values[key + 1] - channel.Values[key]) * s;
	}

}

int main()
{
	const Channel channel { { 0.0f, 1.0f, 3.0f }, { 0.0f, 2.0f, 1.0f } };
	for (float time : { -1.0f, 0.0f, 0.5f, 1.0f, 2.0f, 3.0f, 5.0f })
	{
		size_t key = 0;
		const float value = Sample(channel, time, key);
		std::printf("t = %4.1f  key %zu  value %.2f\n", static_cast<double>(time), key, static_cast<double>(value));
	}
	return 0;
}
