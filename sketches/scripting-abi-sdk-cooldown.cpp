// A Cooldown helper of the kind a script module can carry: plain C++ with no engine types, default constructible.
#include <cstdio>

class Cooldown
{
public:
	explicit Cooldown(float duration = 1.0f)
		: m_Duration(duration)
	{
	}

	void Start() { m_Remaining = m_Duration; }

	void Tick(float deltaTime)
	{
		m_Remaining -= deltaTime;
		if (m_Remaining < 0.0f)
			m_Remaining = 0.0f;
	}

	bool IsReady() const { return m_Remaining <= 0.0f; }
	float GetRemaining() const { return m_Remaining; }
private:
	float m_Duration;
	float m_Remaining = 0.0f;
};

int main()
{
	Cooldown shot(0.5f);
	std::printf("ready before the first shot: %s\n", shot.IsReady() ? "yes" : "no");
	shot.Start();
	for (int frame = 1; frame <= 3; frame++)
	{
		shot.Tick(0.2f);
		std::printf("after %.1f s: %.2f s left, ready %s\n", 0.2f * static_cast<float>(frame), shot.GetRemaining(), shot.IsReady() ? "yes" : "no");
	}
	return 0;
}
