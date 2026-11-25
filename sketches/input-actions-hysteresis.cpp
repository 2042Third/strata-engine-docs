// A half axis holding a Button: pressed beyond 0.5, held until the value falls below 0.35.
#include <cstdio>

int main()
{
	const float c_Press = 0.5f;
	const float c_Release = 0.35f;
	const float samples[] = { 0.0f, 0.4f, 0.6f, 0.45f, 0.36f, 0.3f, 0.4f, 0.55f };
	bool held = false;
	for (const float value : samples)
	{
		const bool wasHeld = held;
		held = held ? value > c_Release : value > c_Press;
		std::printf("value %.2f: down=%d pressed=%d released=%d\n", value, held, held && !wasHeld, !held && wasHeld);
	}
	return 0;
}
