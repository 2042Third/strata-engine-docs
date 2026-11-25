// A vertical stack: children at their preferred heights, one spacing apart, inside the padding.
#include <cstdio>

int main()
{
	const float groupX = 140.0f, groupWidth = 320.0f; // The group's box from the anchored pass
	const float groupY = 466.0f;
	const float padding = 8.0f;
	const float spacing = 18.0f;
	const float preferred[] = { 64.0f, 64.0f, 64.0f, 64.0f };

	float y = groupY + padding;
	for (const float height : preferred)
	{
		// Stretched children take the padded width; the others keep their own.
		std::printf("button x=%.0f y=%.0f w=%.0f h=%.0f\n", groupX + padding, y, groupWidth - 2.0f * padding, height);
		y += height + spacing;
	}
	std::printf("block ends at y=%.0f\n", y - spacing);
}
