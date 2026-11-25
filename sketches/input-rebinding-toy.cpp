#include <array>
#include <cstdio>
#include <optional>
#include <string>

namespace
{
	constexpr int c_KeyCount = 3;
	constexpr int c_Space = 0;
	const char* c_KeyNames[c_KeyCount] = { "Space", "Enter", "Escape" };

	struct Capture
	{
		bool Active = false;
		std::array<bool, c_KeyCount> Held = {}; // The keys that were down when the capture began, then at the last update
		std::optional<std::string> Result;
		int Suppressed = -1;                    // The captured key, until it is released
	};

	std::array<bool, c_KeyCount> s_Raw = {}; // What the keys do now, whatever the game thinks
	Capture s_Capture;

	void Begin()
	{
		s_Capture = Capture();
		s_Capture.Active = true;
		s_Capture.Held = s_Raw; // A key that is already down is not a new press
	}

	void Update()
	{
		if (s_Capture.Active)
		{
			for (int key = 0; key < c_KeyCount; key++)
			{
				const bool wentDown = s_Raw[key] && !s_Capture.Held[key];
				s_Capture.Held[key] = s_Raw[key];
				if (!wentDown)
					continue;
				s_Capture.Active = false;
				s_Capture.Result = c_KeyNames[key];
				s_Capture.Suppressed = key;
				return;
			}
		}
		if (s_Capture.Suppressed >= 0 && !s_Raw[s_Capture.Suppressed])
			s_Capture.Suppressed = -1;
	}

	// The action Jump, bound to Space: up while a capture listens and while its control is suppressed.
	bool IsJumpDown()
	{
		return !s_Capture.Active && s_Capture.Suppressed != c_Space && s_Raw[c_Space];
	}

	void Frame(int number, bool space, bool enter)
	{
		s_Raw[c_Space] = space;
		s_Raw[1] = enter;
		Update();
		std::printf("frame %d: result=%s jump=%d\n", number, s_Capture.Result ? s_Capture.Result->c_str() : "-", IsJumpDown() ? 1 : 0);
	}
}

int main()
{
	s_Raw[1] = true; // Enter is down: it started the capture
	Begin();
	Frame(1, false, true);
	Frame(2, true, false);
	Frame(3, true, false);
	Frame(4, false, false);
	Frame(5, true, false);
	return 0;
}
