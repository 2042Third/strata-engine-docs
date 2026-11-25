// A toy of the package version rule: the project's version, with an optional pre-release suffix.
#include <cstdio>
#include <string>

bool IsSuffixCharacter(char c)
{
	return (c >= '0' && c <= '9') || (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c == '.';
}

// An empty request means the project's version. Otherwise the request is that version, then nothing or "-" and text.
bool ResolvePackageVersion(const std::string& projectVersion, const std::string& requested, std::string& outVersion)
{
	if (requested.empty())
	{
		outVersion = projectVersion;
		return true;
	}
	if (requested.compare(0, projectVersion.size(), projectVersion) != 0)
		return false;
	const std::string rest = requested.substr(projectVersion.size());
	if (!rest.empty())
	{
		if (rest.size() < 2 || rest[0] != '-')
			return false;
		for (size_t index = 1; index < rest.size(); index++)
			if (!IsSuffixCharacter(rest[index]))
				return false;
	}
	outVersion = requested;
	return true;
}

int main()
{
	const std::string project = "0.7.0";
	const char* requests[] = { "", "0.7.0", "0.7.0-rc1", "0.7.0-beta.2", "0.6.0", "0.7.0-", "0.7.01", "0.7.0.1" };
	for (const char* request : requests)
	{
		std::string version;
		if (ResolvePackageVersion(project, request, version))
			std::printf("'%s' -> Strata-%s-linux-x64.tar.gz\n", request, version.c_str());
		else
			std::printf("'%s' -> refused\n", request);
	}
	return 0;
}
