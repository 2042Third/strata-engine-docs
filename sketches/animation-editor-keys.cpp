#include <cstdio>
#include <map>
#include <utility>
#include <vector>

// An animator names its skeleton and the clip it plays on start (0: none).
struct Animator
{
	int Skeleton = 0;
	int Clip = 0;
};

int main()
{
	const std::vector<Animator> animators = { { 1, 0 }, { 1, 0 }, { 1, 5 }, { 1, 5 }, { 1, 5 }, { 2, 5 } };

	// The rest pose depends on the skeleton alone.
	std::map<int, int> restPoses;
	for (const Animator& animator : animators)
		restPoses[animator.Skeleton]++;

	// The clip-start pose depends on the skeleton and the clip.
	std::map<std::pair<int, int>, int> clipStartPoses;
	for (const Animator& animator : animators)
		clipStartPoses[{ animator.Skeleton, animator.Clip }]++;

	std::printf("rest: %zu poses for %zu animators\n", restPoses.size(), animators.size());
	std::printf("clip start: %zu poses for %zu animators\n", clipStartPoses.size(), animators.size());
	return 0;
}
