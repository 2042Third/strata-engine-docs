#include <glm/glm.hpp>

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <optional>
#include <vector>

struct Ball
{
	int Id = 0;
	glm::vec3 Center = glm::vec3(0.0f);
	float Radius = 1.0f;
};

struct Hit
{
	int Id = 0;
	float Distance = 0.0f;
};

// Where a ray along a unit direction enters a ball. A ray that starts inside it has no entry and hits nothing.
static std::optional<float> Enter(const glm::vec3& origin, const glm::vec3& direction, const Ball& ball)
{
	const glm::vec3 toCenter = ball.Center - origin;
	const float along = glm::dot(toCenter, direction);
	const float gap = ball.Radius * ball.Radius - (glm::dot(toCenter, toCenter) - along * along);
	if (gap < 0.0f)
		return std::nullopt;
	const float entry = along - std::sqrt(gap);
	if (!(entry > 0.0f))
		return std::nullopt;
	return entry;
}

// The balls come in any order, as a tree would give them. The limit shrinks to each closer hit.
static std::optional<Hit> Raycast(const glm::vec3& origin, const glm::vec3& direction, float maxDistance, const std::vector<Ball>& balls)
{
	std::optional<Hit> closest;
	float limit = maxDistance;
	for (const Ball& ball : balls)
	{
		const std::optional<float> entry = Enter(origin, direction, ball);
		if (!entry || *entry > limit)
			continue;
		closest = Hit { ball.Id, *entry };
		limit = *entry;
	}
	return closest;
}

// Every ball in reach, sorted so that the answer does not depend on the order the balls came in.
static std::vector<Hit> RaycastAll(const glm::vec3& origin, const glm::vec3& direction, float maxDistance, const std::vector<Ball>& balls)
{
	std::vector<Hit> hits;
	for (const Ball& ball : balls)
	{
		const std::optional<float> entry = Enter(origin, direction, ball);
		if (entry && *entry <= maxDistance)
			hits.push_back(Hit { ball.Id, *entry });
	}
	std::sort(hits.begin(), hits.end(), [](const Hit& a, const Hit& b)
	{
		return a.Distance != b.Distance ? a.Distance < b.Distance : a.Id < b.Id;
	});
	return hits;
}

static void Print(const char* label, const std::vector<Hit>& hits)
{
	std::printf("%s:", label);
	for (const Hit& hit : hits)
		std::printf(" ball %d at %.1f", hit.Id, hit.Distance);
	std::printf("\n");
}

int main()
{
	const std::vector<Ball> balls = { { 3, glm::vec3(9.0f, 0.0f, 0.0f), 1.0f }, { 1, glm::vec3(3.0f, 0.0f, 0.0f), 1.0f }, { 2, glm::vec3(6.0f, 0.0f, 0.0f), 1.0f } };
	const glm::vec3 along(1.0f, 0.0f, 0.0f);

	const std::optional<Hit> closest = Raycast(glm::vec3(0.0f), along, 20.0f, balls);
	Print("closest from 0", { *closest });
	Print("all from 0", RaycastAll(glm::vec3(0.0f), along, 20.0f, balls));
	Print("all within 6 m", RaycastAll(glm::vec3(0.0f), along, 6.0f, balls));
	const std::optional<Hit> inside = Raycast(glm::vec3(6.0f, 0.0f, 0.0f), along, 20.0f, balls);
	Print("closest from inside ball 2", { *inside });
	return 0;
}
