// A toy of ImGui's popup levels: opening a popup at a level closes every popup at that level and deeper.
#include <cstdio>
#include <string>
#include <vector>

class PopupStack
{
public:
	void Open(const std::string& name, size_t level)
	{
		if (m_Open.size() > level)
			m_Open.resize(level);
		m_Open.push_back(name);
	}

	void Print(const char* what) const
	{
		std::printf("%s:", what);
		for (const std::string& name : m_Open)
			std::printf(" [%s]", name.c_str());
		std::printf("\n");
	}

private:
	std::vector<std::string> m_Open;
};

int main()
{
	// The Recovery dialog is a modal opened over the whole window: level 0.
	PopupStack wrong;
	wrong.Open("Recovery", 0);
	wrong.Open("Unsaved Changes", 0);
	wrong.Print("question over the window");

	// Drawn between the dialog's Begin and End, the question is one level deeper.
	PopupStack right;
	right.Open("Recovery", 0);
	right.Open("Unsaved Changes", 1);
	right.Print("question inside the dialog");
	return 0;
}
