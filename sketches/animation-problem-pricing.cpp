// Prices two of the robot's clips: every vertex of every frame, against the keys of its joints.
#include <cstdio>

struct ClipKeys
{
	const char* Name = "";
	int Frames = 0;
	int RotationKeys = 0;
	int TranslationKeys = 0;
};

int main()
{
	const long long positionBytes = 7214 * 12; // 7,214 positions of three 4-byte floats
	const ClipKeys clips[] = { { "Walking", 24, 336, 120 }, { "Idle", 81, 405, 81 } };
	for (const ClipKeys& clip : clips)
	{
		const long long naiveBytes = positionBytes * clip.Frames;
		// A key holds its time (4 bytes) and a value: 4 floats for a rotation, 3 for a translation.
		const long long keyBytes = clip.RotationKeys * (4 + 16) + clip.TranslationKeys * (4 + 12);
		const double ratio = static_cast<double>(naiveBytes) / static_cast<double>(keyBytes);
		std::printf("%s: naive %lld bytes, keys %lld bytes, ratio %.1f\n", clip.Name, naiveBytes, keyBytes, ratio);
	}
	return 0;
}
