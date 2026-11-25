#include <algorithm>
#include <cstdio>

#include <glm/glm.hpp>

struct Listener
{
	glm::vec3 Position;
	glm::vec3 Forward;
	glm::vec3 Up;
};

// The inverse model: the distance is clamped first, so the gain is 1 inside the minimum distance.
static float InverseGain(float distance, float minDistance, float maxDistance, float rolloff)
{
	const float clamped = std::clamp(distance, minDistance, maxDistance);
	return minDistance / (minDistance + rolloff * (clamped - minDistance));
}

static void Report(const char* name, const Listener& listener, const glm::vec3& source)
{
	const glm::vec3 right = glm::cross(listener.Forward, listener.Up);
	const glm::vec3 toSource = source - listener.Position;
	const float distance = glm::length(toSource);
	// One dot product: +1 when the source is exactly to the right, -1 exactly to the left, 0 ahead or behind.
	const float side = glm::dot(toSource / distance, right);
	const float gain = InverseGain(distance, 1.0f, 50.0f, 1.0f);
	// Each ear gets (1 + side) / 2 of the gain, but never less than 0.2.
	const float leftEar = gain * std::max((1.0f - side) * 0.5f, 0.2f);
	const float rightEar = gain * std::max((1.0f + side) * 0.5f, 0.2f);
	std::printf("%-12s distance %6.2f  gain %.3f  left %.3f  right %.3f\n", name, distance, gain, leftEar, rightEar);
}

int main()
{
	const Listener facingMinusZ = { glm::vec3(0.0f), glm::vec3(0.0f, 0.0f, -1.0f), glm::vec3(0.0f, 1.0f, 0.0f) };
	const Listener facingPlusZ = { glm::vec3(0.0f), glm::vec3(0.0f, 0.0f, 1.0f), glm::vec3(0.0f, 1.0f, 0.0f) };

	Report("right", facingMinusZ, glm::vec3(5.0f, 0.0f, 0.0f));
	Report("ahead", facingMinusZ, glm::vec3(0.0f, 0.0f, -5.0f));
	Report("behind", facingMinusZ, glm::vec3(0.0f, 0.0f, 5.0f));
	Report("front right", facingMinusZ, glm::vec3(3.0f, 0.0f, -4.0f));
	Report("far right", facingMinusZ, glm::vec3(100.0f, 0.0f, 0.0f));
	Report("turned round", facingPlusZ, glm::vec3(5.0f, 0.0f, 0.0f));
	return 0;
}
