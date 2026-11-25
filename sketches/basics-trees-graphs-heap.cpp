// Taking the smallest number out of a binary heap kept in a vector.
#include <cstdio>
#include <utility>
#include <vector>

int Pop(std::vector<int>& heap)
{
	const int smallest = heap[0];
	heap[0] = heap.back(); // the last item takes the root's place, then sinks
	heap.pop_back();
	for (size_t i = 0, child = 1; child < heap.size(); i = child, child = 2 * i + 1)
	{
		if (child + 1 < heap.size() && heap[child + 1] < heap[child]) child++; // the smaller child
		if (heap[i] <= heap[child])
			break; // the item is no larger than both children: it stays
		std::swap(heap[i], heap[child]);
	}
	return smallest;
}

int main()
{
	for (std::vector<int> heap = { 1, 3, 2, 5, 4, 8 }; !heap.empty();)
		std::printf("%d\n", Pop(heap));
}
