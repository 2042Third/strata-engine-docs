#include <cstdio>
#include <initializer_list>

// box3d's hulls hold at most this many vertices, faces and edges each.
constexpr int c_Limit = 128;

int main()
{
	int largest = 0;
	for (int vertices = 4; vertices <= 200; vertices++)
	{
		// A hull whose faces are all triangles: Euler's formula gives its faces and edges.
		const int faces = 2 * vertices - 4;
		const int edges = 3 * vertices - 6;
		if (faces <= c_Limit && edges <= c_Limit)
			largest = vertices;
	}
	std::printf("largest all-triangle hull that fits: %d vertices\n", largest);

	for (const int vertices : { 44, 45, 64, 128 })
	{
		const int faces = 2 * vertices - 4;
		const int edges = 3 * vertices - 6;
		std::printf("%3d vertices: %3d faces, %3d edges, %s\n", vertices, faces, edges, faces <= c_Limit && edges <= c_Limit ? "fits" : "too many");
	}
	return 0;
}
