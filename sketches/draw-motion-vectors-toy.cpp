// A pixel's motion from two positions and two view-projection matrices: where the point lands on screen now, minus
// where it landed in the previous frame, in UV units (x to the right, y downward).
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>

#include <cstdio>

namespace
{

	glm::vec2 ToUV(const glm::mat4& viewProjection, const glm::vec3& point)
	{
		const glm::vec4 clip = viewProjection * glm::vec4(point, 1.0f);
		const glm::vec2 ndc = glm::vec2(clip) / clip.w;
		return glm::vec2(ndc.x * 0.5f + 0.5f, 0.5f - ndc.y * 0.5f);
	}

	glm::mat4 MakeViewProjection(const glm::vec3& cameraPosition)
	{
		const glm::mat4 view = glm::translate(glm::mat4(1.0f), -cameraPosition);
		const glm::mat4 projection = glm::perspective(glm::radians(90.0f), 1.0f, 0.1f, 100.0f);
		return projection * view;
	}

	glm::vec2 Motion(const glm::mat4& current, const glm::vec3& currentPoint, const glm::mat4& previous, const glm::vec3& previousPoint)
	{
		return ToUV(current, currentPoint) - ToUV(previous, previousPoint);
	}

	void Print(const char* name, const glm::vec2& motion)
	{
		std::printf("%-26s x %+.4f  y %+.4f\n", name, motion.x, motion.y);
	}

}

int main()
{
	const glm::mat4 still = MakeViewProjection(glm::vec3(0.0f));
	const glm::mat4 panned = MakeViewProjection(glm::vec3(0.2f, 0.0f, 0.0f));
	const glm::vec3 before(1.0f, 1.0f, -4.0f);
	const glm::vec3 after(1.4f, 1.4f, -4.0f);

	Print("still point, still camera", Motion(still, before, still, before));
	Print("cube moved, still camera", Motion(still, after, still, before));
	Print("still point, camera pans", Motion(panned, before, still, before));
	Print("both moved", Motion(panned, after, still, before));
	return 0;
}
