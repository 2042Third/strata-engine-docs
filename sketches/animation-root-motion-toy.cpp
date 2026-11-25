// A toy root motion: a clip's root walks a circle; the entity follows the root's travel, not its place.
#include <cmath>
#include <cstdio>
#include <numbers>

struct Vec
{
	float X = 0.0f;
	float Z = 0.0f;
};

struct RootSample
{
	Vec Position;
	float Yaw = 0.0f;
};

struct Entity
{
	Vec Position;
	float Yaw = 0.0f;
};

constexpr float c_Pi = std::numbers::pi_v<float>;
constexpr float c_Radius = 2.0f;
constexpr float c_Period = 2.0f; // Seconds for one lap: one loop of the clip

// The clip: where the root is, and which way it faces, at a time inside one loop.
RootSample SampleClip(float time)
{
	const float angle = 2.0f * c_Pi * time / c_Period;
	return { { c_Radius * (1.0f - std::cos(angle)), c_Radius * std::sin(angle) }, angle };
}

// The shortest signed angle from a to b.
float AngleDifference(float a, float b)
{
	float difference = std::fmod(b - a, 2.0f * c_Pi);
	if (difference > c_Pi)
		difference -= 2.0f * c_Pi;
	else if (difference < -c_Pi)
		difference += 2.0f * c_Pi;
	return difference;
}

Vec RotateY(const Vec& vector, float angle)
{
	return { std::cos(angle) * vector.X + std::sin(angle) * vector.Z, -std::sin(angle) * vector.X + std::cos(angle) * vector.Z };
}

// The travel of one update, in the frame the root faced when the update began.
struct Travel
{
	Vec Translation;
	float Yaw = 0.0f;

	void Append(const RootSample& from, const RootSample& to)
	{
		const Vec local = RotateY({ to.Position.X - from.Position.X, to.Position.Z - from.Position.Z }, -from.Yaw);
		const Vec turned = RotateY(local, Yaw);
		Translation.X += turned.X;
		Translation.Z += turned.Z;
		Yaw += AngleDifference(from.Yaw, to.Yaw);
	}
};

// The playhead goes from before to after (times since the start); a loop boundary splits the stretch in two.
Travel Advance(float before, float after)
{
	const float loopBefore = std::floor(before / c_Period);
	const float loopAfter = std::floor(after / c_Period);
	const float from = before - loopBefore * c_Period;
	const float to = after - loopAfter * c_Period;
	Travel travel;
	if (loopBefore == loopAfter)
	{
		travel.Append(SampleClip(from), SampleClip(to));
		return travel;
	}
	travel.Append(SampleClip(from), SampleClip(c_Period));
	travel.Append(SampleClip(0.0f), SampleClip(to));
	return travel;
}

int main()
{
	Entity entity;
	entity.Position = { 10.0f, 0.0f };
	entity.Yaw = c_Pi * 0.5f; // Facing +X
	const Vec center = { entity.Position.X + c_Radius * std::cos(entity.Yaw), entity.Position.Z - c_Radius * std::sin(entity.Yaw) };
	const float step = 0.7f;
	for (int update = 1; update <= 6; update++)
	{
		const float before = static_cast<float>(update - 1) * step;
		const Travel travel = Advance(before, before + step);
		const Vec move = RotateY(travel.Translation, entity.Yaw);
		entity.Position = { entity.Position.X + move.X, entity.Position.Z + move.Z };
		entity.Yaw += travel.Yaw;
		const float away = std::hypot(entity.Position.X - center.X, entity.Position.Z - center.Z);
		std::printf("t=%.1f  x=%6.3f  z=%6.3f  yaw=%6.1f  from centre=%.3f\n", before + step, entity.Position.X, entity.Position.Z,
			entity.Yaw * 180.0f / c_Pi, away);
	}
	return 0;
}
