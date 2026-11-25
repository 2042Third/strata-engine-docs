// Exercise: which selectable gets the focus when Right is pressed, by the score along + 2 x across.
#include <glm/glm.hpp>

#include <cmath>
#include <cstdio>
#include <limits>
#include <string>
#include <vector>

struct Candidate
{
	std::string Name;
	glm::vec2 Center;
};

// Returns the index of the best candidate, or -1 when none lies ahead.
static int Navigate(glm::vec2 origin, glm::vec2 axis, const std::vector<Candidate>& candidates)
{
	int best = -1;
	float bestScore = std::numeric_limits<float>::max();
	for (size_t index = 0; index < candidates.size(); index++)
	{
		const glm::vec2 offset = candidates[index].Center - origin;
		const float along = glm::dot(offset, axis);
		if (along <= 1e-3f)
			continue;
		const float across = std::abs(offset.x * axis.y - offset.y * axis.x);
		const float score = along + 2.0f * across;
		std::printf("%s: along %.0f, across %.0f, score %.0f\n", candidates[index].Name.c_str(), along, across, score);
		if (score < bestScore)
		{
			bestScore = score;
			best = static_cast<int>(index);
		}
	}
	return best;
}

int main()
{
	const std::vector<Candidate> candidates = { { "B", { 500.0f, 300.0f } }, { "C", { 400.0f, 380.0f } }, { "D", { 350.0f, 200.0f } },
		{ "E", { 100.0f, 300.0f } } };
	const int best = Navigate({ 200.0f, 300.0f }, { 1.0f, 0.0f }, candidates);
	std::printf("Right moves the focus to %s\n", best >= 0 ? candidates[static_cast<size_t>(best)].Name.c_str() : "nothing");
	return 0;
}
