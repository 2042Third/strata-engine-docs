#include <cmath>
#include <cstdio>

constexpr double c_Pi = 3.14159265358979323846;

struct Vec3
{
	double X = 0.0;
	double Y = 0.0;
	double Z = 0.0;
};

// An orbit camera: a target, a distance and two angles in degrees. Nothing else is stored.
struct OrbitCamera
{
	Vec3 Target;
	double Distance = 10.0;
	double Yaw = 45.0;
	double Pitch = -30.0;
	double FOV = 60.0;
};

double ToRadians(double degrees)
{
	return degrees * c_Pi / 180.0;
}

// Yaw 0 looks along -Z; a positive pitch looks up.
Vec3 GetForward(const OrbitCamera& camera)
{
	const double yaw = ToRadians(camera.Yaw);
	const double pitch = ToRadians(camera.Pitch);
	return { -std::sin(yaw) * std::cos(pitch), std::sin(pitch), -std::cos(yaw) * std::cos(pitch) };
}

// The position is the target minus the forward direction times the distance.
Vec3 GetPosition(const OrbitCamera& camera)
{
	const Vec3 forward = GetForward(camera);
	return { camera.Target.X - forward.X * camera.Distance, camera.Target.Y - forward.Y * camera.Distance,
		camera.Target.Z - forward.Z * camera.Distance };
}

// World units one pixel covers at the target's depth.
double GetUnitsPerPixel(const OrbitCamera& camera, double viewportHeight)
{
	return 2.0 * camera.Distance * std::tan(ToRadians(camera.FOV) * 0.5) / viewportHeight;
}

// Each wheel step toward the target keeps 85 percent of the distance.
void Dolly(OrbitCamera& camera, double steps)
{
	camera.Distance *= std::pow(0.85, steps);
}

// The distance at which the bounding sphere of radius `radius` fits the narrower half field of view, with 10 percent room.
double GetFocusDistance(const OrbitCamera& camera, double radius, double aspectRatio)
{
	const double halfVertical = ToRadians(camera.FOV) * 0.5;
	const double halfHorizontal = std::atan(std::tan(halfVertical) * aspectRatio);
	return radius * 1.1 / std::sin(std::fmin(halfVertical, halfHorizontal));
}

int main()
{
	OrbitCamera camera;
	const Vec3 position = GetPosition(camera);
	std::printf("position: %.3f %.3f %.3f\n", position.X, position.Y, position.Z);
	std::printf("units per pixel at 720 pixels: %.4f\n", GetUnitsPerPixel(camera, 720.0));
	Dolly(camera, 5.0);
	std::printf("distance after 5 wheel steps: %.3f\n", camera.Distance);
	const double radius = std::sqrt(3.0);
	std::printf("focus distance, 16:9 view: %.3f\n", GetFocusDistance(camera, radius, 16.0 / 9.0));
	std::printf("focus distance, 1:2 view: %.3f\n", GetFocusDistance(camera, radius, 0.5));
	return 0;
}
