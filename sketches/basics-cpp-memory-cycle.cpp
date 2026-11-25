// Two nodes that own each other never reach a count of 0; a weak link in one direction lets both go.
#include <iostream>
#include <memory>

struct Node
{
	std::shared_ptr<Node> Strong;
	std::weak_ptr<Node> Weak;
	~Node() { std::cout << "node deleted\n"; }
};
void Pair(bool cycle)
{
	std::shared_ptr<Node> a = std::make_shared<Node>();
	std::shared_ptr<Node> b = std::make_shared<Node>();
	a->Strong = b;
	if (cycle) b->Strong = a; else b->Weak = a;
}
int main()
{
	std::cout << "weak back link\n";
	Pair(false);
	std::cout << "cycle\n";
	Pair(true);
	std::cout << "end\n";
}
