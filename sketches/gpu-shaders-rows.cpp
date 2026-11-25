#include <cstdio>

struct Vec2
{
	float X;
	float Y;
};

// A 2x2 matrix stored by rows, as HLSL's float2x2(a, b, c, d) fills it: first row a, b; second row c, d.
struct RowMatrix
{
	float A;
	float B;
	float C;
	float D;
};

static Vec2 Multiply(const RowMatrix& m, const Vec2& v)
{
	return { m.A * v.X + m.B * v.Y, m.C * v.X + m.D * v.Y };
}

static void Print(const char* label, const Vec2& v)
{
	std::printf("%s -> (%g, %g)\n", label, v.X, v.Y);
}

int main()
{
	const Vec2 v = { 1.0f, 1.0f };

	// GLSL's mat2(1, 2, 3, 4) fills columns: column 0 is (1, 2), column 1 is (3, 4). As rows that is (1, 3) and (2, 4).
	const RowMatrix glslMeaning = { 1.0f, 3.0f, 2.0f, 4.0f };
	Print("GLSL mat2(1, 2, 3, 4) times (1, 1)", Multiply(glslMeaning, v));

	// The same four numbers typed into HLSL's float2x2 fill rows: a different matrix.
	const RowMatrix hlslTyped = { 1.0f, 2.0f, 3.0f, 4.0f };
	Print("HLSL float2x2(1, 2, 3, 4) times (1, 1)", Multiply(hlslTyped, v));

	// The translation writes the rows out: float2x2(1, 3, 2, 4).
	const RowMatrix translated = { 1.0f, 3.0f, 2.0f, 4.0f };
	Print("HLSL float2x2(1, 3, 2, 4) times (1, 1)", Multiply(translated, v));
	return 0;
}
