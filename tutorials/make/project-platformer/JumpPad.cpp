// A jump pad, on a static box trigger: the player walking onto it is thrown up (ThirdPersonPlayer::Launch).

#include "ThirdPersonPlayer.h"

using namespace Strata;

class JumpPad : public Script
{
public:
	float LaunchSpeed = 12.0f; // Metres per second upward: about 7 m high
	AssetHandle BounceSound;

	void OnCreate() override
	{
		Assets::RequestLoad(BounceSound);
	}

	void OnTriggerEnter(const Collision& collision) override
	{
		if (!collision.Other.IsValid() || collision.Other.GetTag() != "Player")
			return;
		ThirdPersonPlayer* player = collision.Other.GetScript<ThirdPersonPlayer>();
		if (!player)
			return;
		player->Launch(LaunchSpeed);
		if (BounceSound.IsValid())
			Audio::PlayOneShotAt(BounceSound, GetTransform().GetWorldPosition(), 0.8f);
	}
};

ST_SCRIPT_CLASS(JumpPad)
{
	ST_SCRIPT_FIELD(LaunchSpeed);
	ST_SCRIPT_FIELD(BounceSound);
}
