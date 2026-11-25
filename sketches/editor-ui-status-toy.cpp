// A toy of the page's three ideas: compact pills with a margin, a toast queue that merges, and an idle cap.
#include <cstddef>
#include <cstdio>
#include <string>
#include <vector>

struct Toast
{
	std::string Title;
	int Count = 1;
};

class ToastQueue
{
public:
	static constexpr std::size_t c_MaxActive = 4;

	void Post(const std::string& title)
	{
		for (Toast& toast : m_Active)
		{
			if (toast.Title == title)
			{
				toast.Count++; // The same news again: one toast with a count
				return;
			}
		}
		m_Active.push_back({ title, 1 });
		if (m_Active.size() > c_MaxActive)
			m_Active.erase(m_Active.begin()); // Too many: the oldest goes
	}

	void Print() const
	{
		for (const Toast& toast : m_Active)
			std::printf("  %s x%d\n", toast.Title.c_str(), toast.Count);
	}

private:
	std::vector<Toast> m_Active;
};

// Compact once the full texts overflow; full again only with a margin of two font sizes to spare.
bool DecideCompact(bool compact, float fullWidth, float available, float fontSize)
{
	if (fullWidth > available)
		return true;
	if (fullWidth <= available - fontSize * 2.0f)
		return false;
	return compact;
}

// 0 means unlimited. Work someone waits for by frames is never capped.
int ChooseCap(bool uncapped, bool busy, bool focused)
{
	if (uncapped || busy)
		return 0;
	return focused ? 30 : 10;
}

int main()
{
	const float fullWidth = 700.0f;
	bool compact = false;
	for (const float available : { 800.0f, 690.0f, 720.0f, 740.0f })
	{
		compact = DecideCompact(compact, fullWidth, available, 16.0f);
		std::printf("available %.0f: %s\n", available, compact ? "compact" : "full");
	}

	ToastQueue queue;
	for (const char* title : { "a failed", "a failed", "b failed", "c failed", "d failed", "e failed" })
		queue.Post(title);
	std::printf("toasts:\n");
	queue.Print();

	std::printf("cap idle focused: %d\n", ChooseCap(false, false, true));
	std::printf("cap idle unfocused: %d\n", ChooseCap(false, false, false));
	std::printf("cap while stepping: %d\n", ChooseCap(true, false, true));
	return 0;
}
