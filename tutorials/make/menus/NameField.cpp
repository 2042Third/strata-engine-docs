#include "StrataScript/StrataScript.h"

#include <string>

using namespace Strata;

// The name field: Enter shows the name on the HUD.
class NameField : public Script
{
public:
	Entity NameLabel;

	void OnUISubmit(Entity widget) override
	{
		const std::string name = widget.GetUI().GetText();
		if (name.empty())
			return;
		NameLabel.GetUI().SetText("Player: " + name);
		UI::ClearFocus();
	}
};

ST_SCRIPT_CLASS(NameField)
{
	ST_SCRIPT_FIELD(NameLabel);
}
