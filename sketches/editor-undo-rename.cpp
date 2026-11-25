#include <cstdio>
#include <set>
#include <string>
#include <utility>

using Files = std::set<std::string>;

// A rename of a file that checks, in both directions, that the world still looks as the step expects.
class RenameAction
{
public:
	RenameAction(Files& files, std::string from, std::string to)
		: m_Files(files), m_From(std::move(from)), m_To(std::move(to))
	{
	}

	bool Execute(std::string* error) { return Move(m_From, m_To, error); }
	bool Undo(std::string* error) { return Move(m_To, m_From, error); }
private:
	bool Move(const std::string& source, const std::string& target, std::string* error)
	{
		if (!m_Files.contains(source))
		{
			*error = "'" + source + "' is gone";
			return false;
		}
		if (m_Files.contains(target))
		{
			*error = "'" + target + "' is taken";
			return false;
		}
		m_Files.erase(source);
		m_Files.insert(target);
		return true;
	}
private:
	Files& m_Files;
	std::string m_From;
	std::string m_To;
};

static void Show(const char* label, const bool ok, const std::string& error, const Files& files)
{
	std::printf("%-14s %-4s files:", label, ok ? "ok" : "FAIL");
	for (const std::string& file : files)
		std::printf(" %s", file.c_str());
	std::printf("%s%s\n", ok ? "" : "  reason: ", error.c_str());
}

int main()
{
	Files files = { "a.txt" };
	std::string error;
	RenameAction rename(files, "a.txt", "b.txt");
	Show("rename", rename.Execute(&error), error, files);
	files.insert("a.txt"); // Something else takes the old name in the meantime.
	error.clear();
	Show("undo (blocked)", rename.Undo(&error), error, files);
	files.erase("a.txt");
	error.clear();
	Show("undo (free)", rename.Undo(&error), error, files);
	return 0;
}
