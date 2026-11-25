// A toy WhenVisible animator: time always advances, the pose is computed only for an animator reported seen.
#include <cstdio>

struct Range
{
	float Min;
	float Max;
};

bool Overlaps(const Range& a, const Range& b)
{
	return a.Min <= b.Max && b.Min <= a.Max;
}

constexpr float c_Speed = 10.0f;           // The clip carries the joint 10 units along z each second.
constexpr Range c_Reach { 0.0f, 10.0f };   // Where the clip takes the joint over its whole loop.
constexpr Range c_View { 5.5f, 7.5f };     // The part of z the camera sees.

struct Animator
{
	float Time = 0.0f;
	float PoseZ = 0.0f;
	bool HasPose = false;
	int SeenUpdate = 0;
	bool UseReach = true;
};

void Update(Animator& animator, int updateIndex, float deltaTime)
{
	animator.Time += deltaTime; // Gameplay always sees the time go on.
	const bool seen = animator.SeenUpdate != 0 && animator.SeenUpdate + 1 >= updateIndex;
	if (seen || !animator.HasPose) // The first pose is always computed.
	{
		animator.PoseZ = animator.Time * c_Speed;
		animator.HasPose = true;
	}
}

void Report(Animator& animator, int updateIndex)
{
	Range bounds { animator.PoseZ, animator.PoseZ };
	if (animator.UseReach)
	{
		bounds.Min = c_Reach.Min;
		bounds.Max = c_Reach.Max;
	}
	if (Overlaps(bounds, c_View))
		animator.SeenUpdate = updateIndex;
}

int main()
{
	Animator withReach;
	Animator withoutReach;
	withoutReach.UseReach = false;
	for (int update = 1; update <= 10; update++)
	{
		Update(withReach, update, 0.1f);
		Update(withoutReach, update, 0.1f);
		Report(withReach, update);
		Report(withoutReach, update);
		std::printf("update %2d time %.1f | with reach: pose z %4.1f | own bounds only: pose z %4.1f\n", update, withReach.Time, withReach.PoseZ, withoutReach.PoseZ);
	}
}
