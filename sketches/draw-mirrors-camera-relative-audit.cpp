#include <cstdio>
#include <initializer_list>

int main()
{
	// A debug line end 100 km out, 3 mm beyond the camera's position along one axis.
	const double cameraX = 100000.0;
	const double lineX = 100000.003;
	const float floatCamera = static_cast<float>(cameraX);
	const float floatLine = static_cast<float>(lineX);
	const float subtractedInFloat = floatLine - floatCamera;
	const float subtractedInDouble = static_cast<float>(lineX - cameraX);
	std::printf("float minus float:   %.4f m\n", static_cast<double>(subtractedInFloat));
	std::printf("double, then float:  %.4f m\n", static_cast<double>(subtractedInDouble));
	return 0;
}
