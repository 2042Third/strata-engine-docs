#include "StrataScript/StrataScript.h"

#include "Triple.h"

using namespace Strata;

class TripleLog : public Script
{
public:
	int Value = 14;

	void OnCreate() override
	{
		Log::Info("Triple of ", Value, " is ", Triple(Value));
	}
};

ST_SCRIPT_CLASS(TripleLog)
{
	ST_SCRIPT_FIELD(Value);
}
