// A toy chip strip: the widths measured while chips draw decide, when the strip ends, what the next frame draws as icons.
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <vector>

struct ChipSize
{
	float Labeled = 0.0f;
	float Icon = 0.0f;
};

struct StripState
{
	std::vector<ChipSize> Sizes;
	size_t FirstIcon = SIZE_MAX;
};

class Strip
{
public:
	Strip(StripState& state, float available)
		: m_State(state), m_Available(available)
	{
	}

	~Strip()
	{
		m_State.Sizes.resize(m_Count);
		float width = m_Count > 0 ? c_Spacing * static_cast<float>(m_Count - 1) : 0.0f;
		for (const ChipSize& size : m_State.Sizes)
			width += size.Labeled;
		size_t firstIcon = m_Count;
		while (firstIcon > 0 && width > m_Available)
		{
			firstIcon--;
			width -= m_State.Sizes[firstIcon].Labeled - m_State.Sizes[firstIcon].Icon;
		}
		m_State.FirstIcon = firstIcon < m_Count ? firstIcon : SIZE_MAX;
	}

	bool NextIsIcon(float labeled, float icon)
	{
		const size_t index = m_Count++;
		if (m_State.Sizes.size() < m_Count)
			m_State.Sizes.resize(m_Count);
		m_State.Sizes[index] = { labeled, icon };
		return index >= m_State.FirstIcon;
	}

private:
	static constexpr float c_Spacing = 8.0f;

	StripState& m_State;
	float m_Available;
	size_t m_Count = 0;
};

void DrawFrame(StripState& state, int frame, float available)
{
	const char* names[] = { "Grid", "Outline", "Gizmos", "Preview lighting", "Game UI" };
	const ChipSize sizes[] = { { 90.0f, 36.0f }, { 110.0f, 36.0f }, { 104.0f, 36.0f }, { 170.0f, 36.0f }, { 110.0f, 36.0f } };
	std::printf("frame %d, %3.0f wide:", frame, available);
	{
		Strip strip(state, available);
		for (size_t index = 0; index < 5; index++)
			std::printf(" %s", strip.NextIsIcon(sizes[index].Labeled, sizes[index].Icon) ? "[]" : names[index]);
	}
	std::printf("\n");
}

int main()
{
	StripState state;
	const float widths[] = { 700.0f, 700.0f, 480.0f, 480.0f, 480.0f, 200.0f, 200.0f };
	for (int frame = 1; frame <= 7; frame++)
		DrawFrame(state, frame, widths[frame - 1]);
	return 0;
}
