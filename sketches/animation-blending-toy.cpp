// A toy cross-fader: up to four entries, kept shares, the faintest dropped, weights that sum to 1.
#include <cstdio>

struct Entry
{
	int State = 0;
	float StartWeight = 1.0f;
	float Weight = 1.0f;
};

class Fader
{
public:
	static constexpr int c_MaxPlaying = 4;

	void Start(int state)
	{
		if (m_Count == 0)
		{
			m_Entries[0] = Entry{ state, 1.0f, 1.0f };
			m_Count = 1;
			return;
		}
		// Every entry keeps the share it has now as the share it fades out from.
		for (int index = 0; index < m_Count; index++)
			m_Entries[index].StartWeight = m_Entries[index].Weight;
		if (m_Count == c_MaxPlaying)
			DropFaintest();
		m_Entries[m_Count] = Entry{ state, 0.0f, 0.0f };
		m_Count++;
	}

	void Update(float progress)
	{
		if (progress >= 1.0f)
		{
			// The fade is over: only the target (the last entry) is left.
			m_Entries[0] = m_Entries[m_Count - 1];
			m_Entries[0].StartWeight = 1.0f;
			m_Entries[0].Weight = 1.0f;
			m_Count = 1;
			return;
		}
		for (int index = 0; index + 1 < m_Count; index++)
			m_Entries[index].Weight = (1.0f - progress) * m_Entries[index].StartWeight;
		m_Entries[m_Count - 1].Weight = progress;
	}

	void Print(const char* label) const
	{
		float sum = 0.0f;
		std::printf("%-14s", label);
		for (int index = 0; index < m_Count; index++)
		{
			std::printf(" S%d=%.4f", m_Entries[index].State, m_Entries[index].Weight);
			sum += m_Entries[index].Weight;
		}
		std::printf("  sum=%.4f\n", sum);
	}

private:
	void DropFaintest()
	{
		int faintest = 0;
		for (int index = 1; index < m_Count; index++)
		{
			if (m_Entries[index].StartWeight < m_Entries[faintest].StartWeight)
				faintest = index;
		}
		const float dropped = m_Entries[faintest].StartWeight;
		for (int index = faintest; index + 1 < m_Count; index++)
			m_Entries[index] = m_Entries[index + 1];
		m_Count--;
		// The others share the dropped weight in the proportions they had.
		for (int index = 0; index < m_Count; index++)
			m_Entries[index].StartWeight /= 1.0f - dropped;
	}

	Entry m_Entries[c_MaxPlaying + 1] = {};
	int m_Count = 0;
};

int main()
{
	Fader fader;
	fader.Start(0);
	fader.Start(1);
	fader.Update(0.4f);
	fader.Print("fade 1 at 0.4");
	fader.Start(2);
	fader.Update(0.5f);
	fader.Print("fade 2 at 0.5");
	fader.Start(3);
	fader.Update(0.5f);
	fader.Print("fade 3 at 0.5");
	fader.Start(4);
	fader.Update(0.25f);
	fader.Print("fade 4 at 0.25");
	fader.Update(1.0f);
	fader.Print("fade 4 done");
	return 0;
}
