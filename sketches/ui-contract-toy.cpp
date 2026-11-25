// A toy UI contract: a cached area behind a dirty flag, a writer that signals and a writer that does not.
#include <cstdio>

struct Rect
{
	float Width = 10.0f;
	float Height = 5.0f;
};

class AreaCache
{
public:
	explicit AreaCache(const Rect& rect)
		: m_Rect(rect)
	{
	}

	// The signal: the rect changed, so the cached area is stale.
	void MarkModified() { m_Dirty = true; }

	float GetArea()
	{
		if (m_Dirty)
		{
			m_Area = m_Rect.Width * m_Rect.Height;
			m_Dirty = false;
			m_Computations++;
		}
		return m_Area;
	}

	// The full recomputation: the cache is true when it agrees with the rect.
	bool Validate() const { return m_Area == m_Rect.Width * m_Rect.Height; }

	int GetComputations() const { return m_Computations; }

private:
	const Rect& m_Rect;
	float m_Area = 0.0f;
	bool m_Dirty = true;
	int m_Computations = 0;
};

int main()
{
	Rect rect;
	AreaCache cache(rect);
	std::printf("first area %.0f, idle frames add 2 reads: %.0f %.0f\n", cache.GetArea(), cache.GetArea(), cache.GetArea());
	std::printf("computations %d\n", cache.GetComputations());

	rect.Width = 20.0f;
	cache.MarkModified();
	const float signaledArea = cache.GetArea(); // Read before Validate: printf's arguments have no fixed order
	std::printf("signaled write: area %.0f, valid %d\n", signaledArea, cache.Validate());
	rect.Height = 8.0f; // No MarkModified
	std::printf("unsignaled write: area %.0f, valid %d\n", cache.GetArea(), cache.Validate());
	std::printf("computations %d\n", cache.GetComputations());
	return 0;
}
