// A toy MCP server: one JSON message per line in, one per line out. It lists two commands as tools and calls them.
#include <iostream>
#include <string>
#include <vector>

struct Command
{
	std::string Name;
	std::string Description;
};

static const std::vector<Command> s_Commands = {
	{ "entity.create", "Creates an entity. Returns its ID." },
	{ "scene.save", "Writes the open scene to its file." } };

// Characters outside letters, digits, "_" and "-" become "_": entity.create becomes entity_create.
std::string MakeToolName(const std::string& method)
{
	std::string name;
	for (char character : method)
	{
		const bool valid = (character >= 'a' && character <= 'z') || (character >= 'A' && character <= 'Z')
			|| (character >= '0' && character <= '9') || character == '_' || character == '-';
		name.push_back(valid ? character : '_');
	}
	return name;
}

std::string FirstSentence(const std::string& text)
{
	const size_t end = text.find(". ");
	return end == std::string::npos ? text : text.substr(0, end + 1);
}

// The text of a field of one flat message: a quoted string, or a number up to the next "," or "}".
std::string ReadField(const std::string& line, const std::string& key)
{
	const size_t at = line.find("\"" + key + "\":");
	if (at == std::string::npos)
		return {};
	size_t start = at + key.size() + 3;
	const bool quoted = line[start] == '"';
	if (quoted)
		start++;
	const size_t end = line.find_first_of(quoted ? "\"" : ",}", start);
	return line.substr(start, end - start);
}

std::string Reply(const std::string& id, const std::string& result)
{
	return "{\"jsonrpc\":\"2.0\",\"id\":" + id + ",\"result\":" + result + "}";
}

std::string HandleLine(const std::string& line)
{
	const std::string method = ReadField(line, "method");
	const std::string id = ReadField(line, "id");
	if (id.empty())
		return {}; // A notification has no id and gets no answer.
	if (method == "initialize")
		return Reply(id, "{\"protocolVersion\":\"2025-06-18\",\"capabilities\":{\"tools\":{}},\"serverInfo\":{\"name\":\"toy\"}}");
	if (method == "tools/list")
	{
		std::string tools;
		for (const Command& command : s_Commands)
		{
			tools += std::string(tools.empty() ? "" : ",") + "{\"name\":\"" + MakeToolName(command.Name) + "\",\"description\":\""
				+ FirstSentence(command.Description) + "\",\"inputSchema\":{\"type\":\"object\"}}";
		}
		return Reply(id, "{\"tools\":[" + tools + "]}");
	}
	if (method == "tools/call")
	{
		const std::string name = ReadField(line, "name");
		for (const Command& command : s_Commands)
		{
			if (MakeToolName(command.Name) == name)
				return Reply(id, "{\"content\":[{\"type\":\"text\",\"text\":\"ran " + command.Name + "\"}],\"isError\":false}");
		}
		return Reply(id, "{\"content\":[{\"type\":\"text\",\"text\":\"Unknown tool " + name + "\"}],\"isError\":true}");
	}
	return "{\"jsonrpc\":\"2.0\",\"id\":" + id + ",\"error\":{\"code\":-32601,\"message\":\"Method not found\"}}";
}

int main()
{
	const std::vector<std::string> input = {
		R"({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18"}})",
		R"({"jsonrpc":"2.0","method":"notifications/initialized"})",
		R"({"jsonrpc":"2.0","id":2,"method":"tools/list"})",
		R"({"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"entity_create","arguments":{}}})",
		R"({"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"scene_load","arguments":{}}})" };
	for (const std::string& line : input)
	{
		const std::string answer = HandleLine(line);
		if (!answer.empty())
			std::cout << answer << "\n";
	}
	return 0;
}
