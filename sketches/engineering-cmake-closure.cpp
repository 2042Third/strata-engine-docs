// A toy of the link-closure walk: collect everything a target links, directly or through other libraries, and report
// the path to each forbidden name.
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <vector>

using Graph = std::map<std::string, std::vector<std::string>>;

static void Collect(const Graph& graph, const std::string& name, const std::string& path, std::map<std::string, std::string>& paths,
	std::vector<std::string>& order)
{
	if (paths.count(name) > 0)
		return;
	paths[name] = path + " -> " + name;
	order.push_back(name);
	const auto links = graph.find(name);
	if (links == graph.end())
		return;
	for (const std::string& next : links->second)
		Collect(graph, next, path + " -> " + name, paths, order);
}

int main()
{
	const Graph graph = {
		{ "StrataRuntime", { "Strata" } },
		{ "Strata", { "Strata_Core", "Strata_Scene" } },
		{ "Strata_Scene", { "Strata_Core", "Strata_AssetPipeline" } },
		{ "Strata_AssetPipeline", { "Strata_Core", "cgltf" } },
	};
	const std::set<std::string> forbidden = { "Strata_AssetPipeline", "cgltf" };

	std::map<std::string, std::string> paths;
	std::vector<std::string> order;
	for (const std::string& item : graph.at("StrataRuntime"))
		Collect(graph, item, "StrataRuntime", paths, order);

	for (const std::string& name : order)
	{
		if (forbidden.count(name) > 0)
			std::cout << "  " << paths[name] << "\n";
	}
	return 0;
}
