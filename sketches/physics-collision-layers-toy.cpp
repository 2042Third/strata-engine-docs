#include <array>
#include <cstdint>
#include <cstdio>

namespace
{

	constexpr uint32_t c_LayerCount = 32;
	constexpr uint32_t c_AllLayers = 0xFFFFFFFFu;
	constexpr uint64_t c_QueryCategory = uint64_t(1) << 63;

	struct Matrix
	{
		std::array<uint32_t, c_LayerCount> Masks;

		Matrix()
		{
			Masks.fill(c_AllLayers);
		}

		void SetCollide(uint32_t a, uint32_t b, bool collide)
		{
			if (collide)
			{
				Masks[a] |= 1u << b;
				Masks[b] |= 1u << a;
			}
			else
			{
				Masks[a] &= ~(1u << b);
				Masks[b] &= ~(1u << a);
			}
		}
	};

	struct Filter
	{
		uint64_t Category;
		uint64_t Mask;
	};

	Filter MakeShapeFilter(uint32_t layer, const Matrix& matrix)
	{
		return { uint64_t(1) << layer, uint64_t(matrix.Masks[layer]) | c_QueryCategory };
	}

	Filter MakeQueryFilter(uint32_t layerMask)
	{
		return { c_QueryCategory, layerMask };
	}

	// Each side's mask must hold the other side's category.
	bool Accepts(const Filter& a, const Filter& b)
	{
		return (a.Mask & b.Category) != 0 && (b.Mask & a.Category) != 0;
	}

	void Print(const char* name, const Filter& filter)
	{
		std::printf("%-5s category %016llx mask %016llx\n", name, static_cast<unsigned long long>(filter.Category),
			static_cast<unsigned long long>(filter.Mask));
	}

	const char* YesNo(bool value)
	{
		return value ? "yes" : "no";
	}

}

int main()
{
	Matrix matrix;
	matrix.SetCollide(1, 2, false);
	const Filter floor = MakeShapeFilter(0, matrix);
	const Filter ball = MakeShapeFilter(1, matrix);
	const Filter ghost = MakeShapeFilter(2, matrix);
	Print("floor", floor);
	Print("ball", ball);
	Print("ghost", ghost);

	std::printf("ball and ghost collide: %s\n", YesNo(Accepts(ball, ghost)));
	std::printf("ghost and floor collide: %s\n", YesNo(Accepts(ghost, floor)));
	std::printf("query on all layers sees the ghost: %s\n", YesNo(Accepts(MakeQueryFilter(c_AllLayers), ghost)));
	std::printf("query without layer 2 sees the ghost: %s\n", YesNo(Accepts(MakeQueryFilter(c_AllLayers & ~(1u << 2)), ghost)));

	Matrix oneSided;
	oneSided.Masks[1] &= ~(1u << 2);
	std::printf("one-sided edit, ball and ghost collide: %s\n",
		YesNo(Accepts(MakeShapeFilter(1, oneSided), MakeShapeFilter(2, oneSided))));
	return 0;
}
