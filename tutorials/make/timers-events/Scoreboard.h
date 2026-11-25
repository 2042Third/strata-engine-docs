#pragma once

#include "StrataScript/StrataScript.h"

#include <cstdint>

// The score, on the entity "Game". Other scripts include this header to call AddPoint.
class Scoreboard : public Strata::Script
{
public:
	int32_t Score = 0;

	void AddPoint();
};
