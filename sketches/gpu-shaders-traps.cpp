#include <cstdio>

struct Vec3
{
	float X;
	float Y;
	float Z;
};

struct Mat2
{
	float M[2][2]; // M[row][column], the order of HLSL's float2x2(...)
};

// What HLSL's mul(v, w) of two vectors does: a dot product, one number.
static float MulVectors(const Vec3& v, const Vec3& w)
{
	return v.X * w.X + v.Y * w.Y + v.Z * w.Z;
}

// What HLSL's M * N does: each element times its partner.
static Mat2 Componentwise(const Mat2& a, const Mat2& b)
{
	Mat2 result;
	for (int row = 0; row < 2; row++)
		for (int column = 0; column < 2; column++)
			result.M[row][column] = a.M[row][column] * b.M[row][column];
	return result;
}

// What HLSL's mul(A, B) does: the matrix product.
static Mat2 MatrixProduct(const Mat2& a, const Mat2& b)
{
	Mat2 result;
	for (int row = 0; row < 2; row++)
		for (int column = 0; column < 2; column++)
			result.M[row][column] = a.M[row][0] * b.M[0][column] + a.M[row][1] * b.M[1][column];
	return result;
}

static void Print(const char* label, const Mat2& m)
{
	std::printf("%s: [%g %g] [%g %g]\n", label, m.M[0][0], m.M[0][1], m.M[1][0], m.M[1][1]);
}

int main()
{
	const Vec3 v = { 1.0f, 2.0f, 3.0f };
	const Vec3 w = { 4.0f, 5.0f, 6.0f };
	std::printf("mul(v, w) = %g, one number where a vector was meant\n", MulVectors(v, w));

	const Mat2 a = { { { 1.0f, 2.0f }, { 3.0f, 4.0f } } };
	const Mat2 b = { { { 5.0f, 6.0f }, { 7.0f, 8.0f } } };
	Print("A * B  ", Componentwise(a, b));
	Print("mul(A,B)", MatrixProduct(a, b));
	return 0;
}
