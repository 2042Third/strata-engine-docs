// A toast's lifetime by level, and what hovering does to it.
#include <algorithm>
#include <cstdio>

enum class Level
{
	Info,
	Warning,
	Error
};

double GetLifetime(Level level)
{
	switch (level)
	{
		case Level::Info: return 5.0;
		case Level::Warning: return 8.0;
		case Level::Error: return 12.0;
	}
	return 5.0;
}

struct Toast
{
	Level Kind = Level::Info;
	double Expires = 0.0;
};

// The person hovers the toast: it stays at least `extra` seconds from now, and never loses time it already had.
void KeepAlive(Toast& toast, double now, double extra)
{
	toast.Expires = std::max(toast.Expires, now + extra);
}

int main()
{
	Toast toast { Level::Error, 0.0 };
	toast.Expires = 0.0 + GetLifetime(toast.Kind);
	std::printf("posted at 0 s, expires at %.1f s\n", toast.Expires);
	KeepAlive(toast, 5.0, 2.0);
	std::printf("hover at 5 s: expires at %.1f s\n", toast.Expires);
	KeepAlive(toast, 11.0, 2.0);
	std::printf("hover at 11 s: expires at %.1f s\n", toast.Expires);
	for (const double now : { 12.5, 13.0 })
		std::printf("at %.1f s the toast is %s\n", now, toast.Expires <= now ? "gone" : "shown");
	return 0;
}
