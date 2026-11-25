// One axis of a rect: anchors, pivot, position and size, the way the engine states its rect model.
#include <algorithm>
#include <cstdio>

struct AxisRect
{
	float AnchorMin, AnchorMax, Pivot, Position, Size;
};

void Anchored(float parentMin, float parentSize, const AxisRect& rect, float& outMin, float& outSize)
{
	const float anchor0 = parentMin + rect.AnchorMin * parentSize;
	const float anchor1 = parentMin + rect.AnchorMax * parentSize;
	outSize = std::max(anchor1 - anchor0 + rect.Size, 0.0f);
	const float pivotPoint = anchor0 + (anchor1 - anchor0) * rect.Pivot + rect.Position;
	outMin = pivotPoint - outSize * rect.Pivot;
}

int main()
{
	float x = 0.0f, width = 0.0f, y = 0.0f, height = 0.0f;
	Anchored(0.0f, 1920.0f, { 0.0f, 0.0f, 0.0f, 110.0f, 380.0f }, x, width);
	Anchored(0.0f, 1080.0f, { 0.5f, 0.5f, 0.5f, 90.0f, 400.0f }, y, height);
	std::printf("menu x=%.0f y=%.0f w=%.0f h=%.0f\n", x, y, width, height);
}
