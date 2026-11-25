#include <iostream>
#include <map>
#include <string>
#include <vector>

// A toy project: files with handles, who uses each handle, and a trash. It follows the page's rules:
// a delete asks the users first, a trashed file keeps its handle, and an undo checks the path.
struct Trashed
{
	std::string Path;
	int Handle = 0;
};

class Project
{
public:
	void Create(const std::string& path, int handle) { m_Files[path] = handle; }
	void Use(int handle, const std::string& user) { m_Users[handle].push_back(user); }

	bool Delete(const std::string& path, bool force, Trashed& outTrashed, std::string& outError)
	{
		const auto file = m_Files.find(path);
		if (file == m_Files.end())
		{
			outError = "no such file";
			return false;
		}
		const std::vector<std::string>& users = m_Users[file->second];
		if (!users.empty() && !force)
		{
			outError = "'" + path + "' is used by " + users.front();
			return false;
		}
		outTrashed = { path, file->second };
		m_Files.erase(file); // The real engine moves the file to the trash folder instead
		return true;
	}

	bool Restore(const Trashed& trashed, std::string& outError)
	{
		if (m_Files.contains(trashed.Path))
		{
			outError = "Something else is at '" + trashed.Path + "'";
			return false;
		}
		m_Files[trashed.Path] = trashed.Handle; // The same handle comes back
		return true;
	}

	int Find(const std::string& path) const
	{
		const auto file = m_Files.find(path);
		return file == m_Files.end() ? 0 : file->second;
	}
private:
	std::map<std::string, int> m_Files;
	std::map<int, std::vector<std::string>> m_Users;
};

int main()
{
	Project project;
	project.Create("Materials/Stone.stmat", 1);
	project.Create("Textures/Rust.png", 2);
	project.Use(1, "Scenes/Main.stscene");

	Trashed trashed;
	std::string error;
	if (!project.Delete("Materials/Stone.stmat", false, trashed, error))
		std::cout << "refused: " << error << "\n";

	if (project.Delete("Textures/Rust.png", false, trashed, error))
		std::cout << "deleted Rust, handle " << trashed.Handle << "\n";
	if (project.Restore(trashed, error))
		std::cout << "undo: Rust is back with handle " << project.Find("Textures/Rust.png") << "\n";

	project.Delete("Textures/Rust.png", false, trashed, error);
	project.Create("Textures/Rust.png", 3); // A new file takes the path
	if (!project.Restore(trashed, error))
		std::cout << "undo failed: " << error << "\n";
	return 0;
}
