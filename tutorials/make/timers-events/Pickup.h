#pragma once

#include "Scoreboard.h"

// A crate that scores a point when the Player is next to it. Dropper adds it to each crate it makes.
class Pickup : public Strata::Script
{
public:
	float Reach = 1.2f;

	void OnUpdate(float deltaTime) override;
};
