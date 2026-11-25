// Finds the re-layout roots of a set of marked elements: each mark climbs to the highest ancestor that depends on its children.
#include <algorithm>
#include <cstdio>
#include <vector>

struct Element
{
	int Parent;
	bool DependsOnChildren;
};

int FindRoot(const std::vector<Element>& elements, int marked)
{
	int root = marked;
	while (elements[root].Parent >= 0 && elements[elements[root].Parent].DependsOnChildren)
		root = elements[root].Parent;
	return root;
}

int main()
{
	// 0 canvas, 1 panel (a layout group), 2 and 3 buttons (fit their text), 4 a label under 2, 5 a plain sibling of the panel.
	const std::vector<Element> elements = { { -1, false }, { 0, true }, { 1, true }, { 1, true }, { 2, false }, { 0, false } };
	const std::vector<int> marks = { 4, 3, 5 };

	std::vector<int> roots;
	for (const int marked : marks)
		roots.push_back(FindRoot(elements, marked));
	std::sort(roots.begin(), roots.end());
	roots.erase(std::unique(roots.begin(), roots.end()), roots.end());

	for (const int root : roots)
		std::printf("root %d\n", root);
	return 0;
}
