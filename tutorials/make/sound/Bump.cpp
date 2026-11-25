// A bump sound for the rolling ball: plays a soft thud where the ball hits something, louder the harder it hits.

#include "StrataScript/StrataScript.h"

#include <algorithm>

using namespace Strata;

class Bump : public Script
{
public:
	float MinSpeed = 1.5f;        // Meters per second of impact below which nothing sounds
	float FullVolumeSpeed = 10.0f; // Meters per second of impact that plays at full volume

	void OnCreate() override { FindSound(); }
	void OnReload() override { FindSound(); }

	void OnCollisionEnter(const Collision& collision) override
	{
		const glm::vec3 own = GetEntity().GetRigidBody().GetLinearVelocity();
		const glm::vec3 other = collision.Other.IsValid() ? collision.Other.GetRigidBody().GetLinearVelocity() : glm::vec3(0.0f);
		const float separating = std::abs(glm::dot(own - other, collision.Normal));
		const float speed = separating + 0.5f * std::max(glm::length(own), glm::length(other));
		if (speed < MinSpeed || !m_Sound.IsValid())
			return;
		const float volume = std::clamp(speed / FullVolumeSpeed, 0.1f, 1.0f);
		Audio::PlayOneShotAt(m_Sound, collision.Point, volume, 0.9f + 0.2f * std::min(1.0f, speed / FullVolumeSpeed));
	}
private:
	void FindSound()
	{
		m_Sound = Assets::Find("Sounds/Impacts/Soft.ogg");
		if (m_Sound.IsValid())
			Assets::RequestLoad(m_Sound);
		else
			Log::Warn("Bump: there is no asset at Sounds/Impacts/Soft.ogg");
	}
private:
	AssetHandle m_Sound;
};

ST_SCRIPT_CLASS(Bump)
{
	ST_SCRIPT_FIELD(MinSpeed);
	ST_SCRIPT_FIELD(FullVolumeSpeed);
}
