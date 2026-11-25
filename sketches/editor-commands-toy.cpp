#include <algorithm>
#include <charconv>
#include <cstdio>
#include <functional>
#include <map>
#include <optional>
#include <string>
#include <utility>
#include <vector>

namespace Toy
{

	using Parameters = std::map<std::string, std::string>;

	enum class ErrorKind { None, UnknownCommand, InvalidParameters, Failed };

	struct Result
	{
		bool Success = true;
		std::string Value;
		std::string Error;
		ErrorKind Kind = ErrorKind::None;

		static Result Ok(std::string value) { return { true, std::move(value), {}, ErrorKind::None }; }
		static Result Fail(std::string error, ErrorKind kind) { return { false, {}, std::move(error), kind }; }
	};

	struct Command
	{
		std::string Name;
		std::vector<std::string> Allowed;
		std::vector<std::string> Required;
		std::function<Result(const Parameters&)> Handler;
	};

	class Registry
	{
	public:
		void Register(Command command) { m_Commands[command.Name] = std::move(command); }

		Result Execute(const std::string& name, const Parameters& parameters)
		{
			Result result = Run(name, parameters);
			m_Journal.push_back(name + (result.Success ? " ok" : " failed"));
			return result;
		}

		const std::vector<std::string>& GetJournal() const { return m_Journal; }

	private:
		Result Run(const std::string& name, const Parameters& parameters)
		{
			auto found = m_Commands.find(name);
			if (found == m_Commands.end())
				return Result::Fail("Unknown command '" + name + "'", ErrorKind::UnknownCommand);
			const Command& command = found->second;
			for (const auto& [key, value] : parameters)
			{
				if (std::find(command.Allowed.begin(), command.Allowed.end(), key) == command.Allowed.end())
					return Result::Fail("Unknown parameter '" + key + "' for " + name, ErrorKind::InvalidParameters);
			}
			for (const std::string& key : command.Required)
			{
				if (!parameters.contains(key))
					return Result::Fail("Missing parameter '" + key + "' for " + name, ErrorKind::InvalidParameters);
			}
			return command.Handler(parameters);
		}

		std::map<std::string, Command> m_Commands;
		std::vector<std::string> m_Journal;
	};

}

int main()
{
	using namespace Toy;

	std::vector<std::string> names = { "Ground", "Crate" };
	std::vector<std::pair<size_t, std::string>> undoStack;
	Registry registry;

	registry.Register({ "entity.rename", { "index", "name" }, { "index", "name" }, [&](const Parameters& parameters)
	{
		size_t index = 0;
		const std::string& text = parameters.at("index");
		std::from_chars(text.data(), text.data() + text.size(), index);
		if (index >= names.size())
			return Result::Fail("Parameter 'index': no entity " + text, ErrorKind::InvalidParameters);
		undoStack.push_back({ index, names[index] });
		names[index] = parameters.at("name");
		return Result::Ok(names[index]);
	} });
	registry.Register({ "entity.count", {}, {}, [&](const Parameters&) { return Result::Ok(std::to_string(names.size())); } });
	registry.Register({ "edit.undo", {}, {}, [&](const Parameters&)
	{
		if (undoStack.empty())
			return Result::Fail("Nothing to undo", ErrorKind::Failed);
		names[undoStack.back().first] = undoStack.back().second;
		undoStack.pop_back();
		return Result::Ok("undone");
	} });

	const std::vector<std::pair<std::string, Parameters>> calls = {
		{ "entity.rename", { { "index", "0" }, { "name", "Floor" } } },
		{ "entity.rename", { { "index", "0" }, { "nam", "Floor" } } },
		{ "entity.rename", { { "index", "0" } } },
		{ "entity.rename", { { "index", "7" }, { "name", "Lamp" } } },
		{ "edit.undo", {} },
		{ "edit.undo", {} },
		{ "entity.fly", {} },
	};
	for (const auto& [name, parameters] : calls)
	{
		const Result result = registry.Execute(name, parameters);
		std::printf("%-14s %s  %s\n", name.c_str(), result.Success ? "OK  " : "FAIL", (result.Success ? result.Value : result.Error).c_str());
	}
	std::printf("journal: %zu entries, first '%s'\n", registry.GetJournal().size(), registry.GetJournal().front().c_str());
	std::printf("names: %s, %s\n", names[0].c_str(), names[1].c_str());
	return 0;
}
