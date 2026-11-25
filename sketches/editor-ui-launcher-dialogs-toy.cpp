// A toy dialog: it runs one command, and asks again when the scene changed after the person answered.
#include <cstdio>
#include <functional>
#include <map>
#include <string>

struct Editor
{
	int SceneVersion = 0;
	std::string ProjectName;
};

class CommandRegistry
{
public:
	using Command = std::function<bool(Editor&, const std::string&)>;

	void Register(const std::string& name, Command command) { m_Commands[name] = command; }

	bool Execute(Editor& editor, const std::string& name, const std::string& argument)
	{
		const auto found = m_Commands.find(name);
		return found != m_Commands.end() && found->second(editor, argument);
	}

private:
	std::map<std::string, Command> m_Commands;
};

class NewProjectDialog
{
public:
	// The person has answered the question about unsaved changes by the time the dialog opens.
	void Open(const Editor& editor) { m_AnsweredVersion = editor.SceneVersion; m_Name = "My Project"; }

	// One frame. Returns false once the dialog is done.
	bool Draw(Editor& editor, CommandRegistry& commands, bool createPressed, bool personAnswered)
	{
		if (personAnswered)
			m_AnsweredVersion = editor.SceneVersion; // the new answer covers the new changes
		else if (!createPressed)
			return true;
		if (editor.SceneVersion != m_AnsweredVersion)
		{
			std::printf("  the scene changed since the answer: asking again\n");
			return true;
		}
		const bool created = commands.Execute(editor, "project.create", m_Name);
		std::printf("  project.create %s\n", created ? "succeeded" : "failed");
		return !created;
	}

private:
	int m_AnsweredVersion = 0;
	std::string m_Name;
};

int main()
{
	Editor editor;
	editor.SceneVersion = 12;
	CommandRegistry commands;
	commands.Register("project.create", [](Editor& target, const std::string& name)
	{
		target.ProjectName = name;
		return true;
	});

	NewProjectDialog dialog;
	dialog.Open(editor);
	std::printf("frame 1: an agent creates an entity\n");
	editor.SceneVersion = 13;
	std::printf("frame 2: Create pressed\n");
	bool open = dialog.Draw(editor, commands, true, false);
	std::printf("frame 3: the person answers\n");
	open = dialog.Draw(editor, commands, false, true);
	std::printf("dialog open: %s, project: %s\n", open ? "yes" : "no", editor.ProjectName.c_str());
	return 0;
}
