#include <iostream>

// The class as Counter.h declares it.
class Counter
{
public:
	Counter(int start);
	void Increase();
	int GetCount() const;
private:
	int m_Count = 0;
};

// The functions as Counter.cpp defines them.
Counter::Counter(int start) : m_Count(start) {}
void Counter::Increase() { m_Count++; }
int Counter::GetCount() const { return m_Count; }

int main()
{
	Counter counter(3);
	counter.Increase();
	counter.Increase();
	std::cout << "count is " << counter.GetCount() << '\n';
}
