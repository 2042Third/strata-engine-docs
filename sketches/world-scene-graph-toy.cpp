// A toy scene graph: children in an intrusive list, world transforms cached and computed only below changes.
#include <cstdio>
#include <vector>

constexpr int c_None = -1;

struct Node
{
	int Parent = c_None, FirstChild = c_None, LastChild = c_None, NextSibling = c_None;
	float LocalX = 0.0f, LocalScale = 1.0f; // relative to the parent: an offset in metres and a size
	float WorldX = 0.0f, WorldScale = 1.0f; // the cache: the same two numbers in the world
	bool Dirty = false;
};

std::vector<Node> s_Nodes;
std::vector<int> s_DirtyList;

void MarkDirty(int entity)
{
	if (!s_Nodes[entity].Dirty)
		s_DirtyList.push_back(entity);
	s_Nodes[entity].Dirty = true;
}

int Create(int parent, float localX, float localScale)
{
	const int entity = static_cast<int>(s_Nodes.size());
	s_Nodes.push_back(Node { parent, c_None, c_None, c_None, localX, localScale });
	if (parent != c_None)
	{
		const int last = s_Nodes[parent].LastChild;
		(last == c_None ? s_Nodes[parent].FirstChild : s_Nodes[last].NextSibling) = entity;
		s_Nodes[parent].LastChild = entity;
	}
	MarkDirty(entity); // a new entity is computed at the next update
	return entity;
}

bool HasDirtyAncestor(int entity)
{
	for (int current = s_Nodes[entity].Parent; current != c_None; current = s_Nodes[current].Parent)
		if (s_Nodes[current].Dirty)
			return true;
	return false;
}

void Update(const char* what)
{
	std::vector<int> level; // the frontier: dirty entities with no dirty ancestor
	for (const int entity : s_DirtyList)
		if (!HasDirtyAncestor(entity))
			level.push_back(entity);
	s_DirtyList.clear();
	int computed = 0;
	while (!level.empty())
	{
		std::vector<int> next;
		for (const int entity : level)
		{
			Node& node = s_Nodes[entity];
			const Node parent = node.Parent == c_None ? Node {} : s_Nodes[node.Parent];
			node.WorldX = parent.WorldX + parent.WorldScale * node.LocalX;
			node.WorldScale = parent.WorldScale * node.LocalScale;
			node.Dirty = false;
			computed++;
			for (int child = node.FirstChild; child != c_None; child = s_Nodes[child].NextSibling)
				next.push_back(child);
		}
		level.swap(next);
	}
	std::printf("%-20s computed %d, world x:", what, computed);
	for (const Node& node : s_Nodes)
		std::printf(" %5.1f", node.WorldX);
	std::printf("\n");
}

int main()
{
	const int car = Create(c_None, 10.0f, 1.0f);
	const int wheel = Create(car, 2.0f, 0.5f);
	const int bolt = Create(wheel, 1.0f, 1.0f);
	const int tree = Create(c_None, 50.0f, 3.0f);
	Update("first update:");
	Update("nothing changed:");
	s_Nodes[bolt].LocalX = 3.0f;
	MarkDirty(bolt); // a write, then its signal
	s_Nodes[car].LocalX = 20.0f;
	MarkDirty(car);
	Update("bolt and car moved:");
	s_Nodes[tree].LocalX = 60.0f; // a write without a signal
	Update("silent write:");
}
