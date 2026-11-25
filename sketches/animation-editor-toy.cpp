#include <cstdint>
#include <cstdio>
#include <unordered_map>
#include <vector>

// A skeleton is a chain: each joint sits on its parent, offset by its rest height.
struct Skeleton
{
	std::vector<int> Parents;
	std::vector<float> RestHeights;
	uint64_t Revision = 1; // Grows when the file is imported again
};

struct CachedPose
{
	std::vector<float> Heights; // Height of every joint in the animator's space
	uint64_t Revision = 0;      // The skeleton's revision it was computed from
};

class RestPoseProvider
{
public:
	// Every animator on the same skeleton gets the same pose: computed once, again only after an import.
	const std::vector<float>& GetPose(int skeletonId, const Skeleton& skeleton)
	{
		CachedPose& cached = m_Cache[skeletonId];
		if (cached.Revision != skeleton.Revision)
		{
			cached.Heights.assign(skeleton.Parents.size(), 0.0f);
			for (size_t joint = 0; joint < skeleton.Parents.size(); joint++)
			{
				const int parent = skeleton.Parents[joint];
				const float base = parent < 0 ? 0.0f : cached.Heights[static_cast<size_t>(parent)];
				cached.Heights[joint] = base + skeleton.RestHeights[joint];
			}
			cached.Revision = skeleton.Revision;
			m_Computed++;
		}
		return cached.Heights;
	}

	int GetComputed() const { return m_Computed; }

private:
	std::unordered_map<int, CachedPose> m_Cache;
	int m_Computed = 0;
};

int main()
{
	Skeleton robot;
	robot.Parents = { -1, 0, 1 };
	robot.RestHeights = { 0.5f, 0.5f, 0.75f };

	RestPoseProvider provider;
	for (int animator = 0; animator < 500; animator++)
		provider.GetPose(7, robot);
	std::printf("500 animators, %d pose computed, head at %.2f\n", provider.GetComputed(), provider.GetPose(7, robot)[2]);

	robot.RestHeights[2] = 1.0f;
	robot.Revision++;
	provider.GetPose(7, robot);
	provider.GetPose(7, robot);
	std::printf("after an import, %d poses computed, head at %.2f\n", provider.GetComputed(), provider.GetPose(7, robot)[2]);
	return 0;
}
