// A toy of the release workflow's version gate: a tag, the project's version and whether the release is published.
#include <cstdio>
#include <string>

enum class Verdict
{
	Publish,
	DryRun,
	Refused
};

bool IsNumber(const std::string& text)
{
	if (text.empty())
		return false;
	for (char c : text)
		if (c < '0' || c > '9')
			return false;
	return true;
}

// A tag is "v", three numbers split by dots, then nothing or "-" and a suffix.
Verdict CheckTag(const std::string& tag, const std::string& projectVersion)
{
	if (tag.size() < 6 || tag[0] != 'v')
		return Verdict::Refused;
	const size_t dash = tag.find('-');
	const std::string base = tag.substr(1, dash == std::string::npos ? std::string::npos : dash - 1);
	const size_t firstDot = base.find('.');
	const size_t secondDot = firstDot == std::string::npos ? std::string::npos : base.find('.', firstDot + 1);
	if (secondDot == std::string::npos)
		return Verdict::Refused;
	if (!IsNumber(base.substr(0, firstDot)) || !IsNumber(base.substr(firstDot + 1, secondDot - firstDot - 1)) || !IsNumber(base.substr(secondDot + 1)))
		return Verdict::Refused;
	if (base != projectVersion)
		return Verdict::Refused;
	return dash == std::string::npos ? Verdict::Publish : Verdict::DryRun;
}

int main()
{
	const char* names[] = { "publish", "dry run", "refused" };
	const char* tags[] = { "v0.7.0", "v0.7.0-rc1", "v0.8.0", "0.7.0", "v0.7" };
	for (const char* tag : tags)
		std::printf("%-12s %s\n", tag, names[static_cast<int>(CheckTag(tag, "0.7.0"))]);
	return 0;
}
