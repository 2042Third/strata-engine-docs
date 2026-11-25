// A pool of four equal slots: a free list links the unused slots, so taking and giving back cost one step.
#include <iostream>

struct Pool
{
	int Next[4] = { 1, 2, 3, -1 }; // for a free slot: the free slot after it, or -1
	int Head = 0;                  // the first free slot, or -1 when none is free
	int Take() { int slot = Head; if (slot >= 0) Head = Next[slot]; return slot; }
	void Give(int slot) { Next[slot] = Head; Head = slot; }
};

int main()
{
	Pool pool;
	int a = pool.Take(), b = pool.Take(), c = pool.Take();
	std::cout << "took " << a << ' ' << b << ' ' << c << '\n';
	pool.Give(b);
	std::cout << "after giving back " << b << ", next take: " << pool.Take() << '\n';
	std::cout << "then: " << pool.Take() << ' ' << pool.Take() << '\n';
}
