// Root motion of a cross-fade: each playing entry's travel, weighted by its share of the blend.
#include <cstdio>

struct Entry
{
	float Speed = 0.0f;  // Metres per second the clip's root travels
	float Weight = 0.0f; // Share of the blend after the update
};

int main()
{
	const float deltaTime = 0.5f;
	for (int fade = 0; fade <= 4; fade++)
	{
		const float share = static_cast<float>(fade) / 4.0f;
		const Entry entries[2] = { { 2.0f, 1.0f - share }, { 4.0f, share } };
		float travel = 0.0f;
		for (const Entry& entry : entries)
			travel += entry.Speed * deltaTime * entry.Weight;
		std::printf("run share %.2f: the entity moves %.2f m\n", share, travel);
	}
	return 0;
}
