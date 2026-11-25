#include <cstdio>
#include <deque>
#include <cstddef>
#include <memory>
#include <utility>

// One undoable change of an integer: it adds a delta, and a mergeable one absorbs the next mergeable one.
class Action
{
public:
	Action(int delta, bool mergeable)
		: m_Delta(delta), m_Mergeable(mergeable)
	{
	}

	void Apply(int& value) const { value += m_Delta; }
	void Revert(int& value) const { value -= m_Delta; }
	bool MergeWith(const Action& next)
	{
		if (!m_Mergeable || !next.m_Mergeable)
			return false;
		m_Delta += next.m_Delta;
		return true;
	}
	bool IsNoOp() const { return m_Delta == 0; }
private:
	int m_Delta;
	bool m_Mergeable;
};

class History
{
public:
	explicit History(size_t capacity)
		: m_Capacity(capacity)
	{
	}

	void Execute(std::unique_ptr<Action> action, int& value)
	{
		action->Apply(value);
		if (m_Position < m_Entries.size())
		{
			// A new edit after undo: the redo branch goes, and a save point inside it is lost.
			m_Entries.erase(m_Entries.begin() + static_cast<std::ptrdiff_t>(m_Position), m_Entries.end());
			if (m_Saved != c_Lost && m_Saved > m_Position)
				m_Saved = c_Lost;
			m_MergeBroken = true;
		}
		// Never merge across the save point: saving ends a drag's step.
		if (!m_MergeBroken && m_Position > 0 && m_Saved != m_Position && m_Entries.back()->MergeWith(*action))
		{
			if (m_Entries.back()->IsNoOp())
			{
				m_Entries.pop_back();
				m_Position--;
				m_MergeBroken = true;
			}
			return;
		}
		m_Entries.push_back(std::move(action));
		m_Position = m_Entries.size();
		m_MergeBroken = false;
		if (m_Entries.size() > m_Capacity)
		{
			m_Entries.pop_front();
			m_Position--;
			m_Saved = (m_Saved == 0 || m_Saved == c_Lost) ? c_Lost : m_Saved - 1;
		}
	}

	bool Undo(int& value)
	{
		if (m_Position == 0)
			return false;
		m_Entries[--m_Position]->Revert(value);
		m_MergeBroken = true;
		return true;
	}

	bool Redo(int& value)
	{
		if (m_Position == m_Entries.size())
			return false;
		m_Entries[m_Position++]->Apply(value);
		m_MergeBroken = true;
		return true;
	}

	void MarkSaved() { m_Saved = m_Position; m_MergeBroken = true; }
	bool IsModified() const { return m_Saved != m_Position; }
	size_t GetCount() const { return m_Entries.size(); }
	size_t GetPosition() const { return m_Position; }
private:
	static constexpr size_t c_Lost = static_cast<size_t>(-1);
	std::deque<std::unique_ptr<Action>> m_Entries;
	size_t m_Capacity;
	size_t m_Position = 0;
	size_t m_Saved = 0;
	bool m_MergeBroken = true;
};

static void Show(const char* label, const int value, const History& history)
{
	std::printf("%-22s value=%2d steps=%zu position=%zu modified=%s\n", label, value, history.GetCount(), history.GetPosition(),
		history.IsModified() ? "yes" : "no");
}

int main()
{
	int value = 0;
	History history(512);
	history.Execute(std::make_unique<Action>(5, false), value);
	history.MarkSaved();
	Show("add 5, save", value, history);
	history.Execute(std::make_unique<Action>(2, true), value);
	history.Execute(std::make_unique<Action>(3, true), value);
	Show("drag +2, +3", value, history);
	history.Execute(std::make_unique<Action>(-5, true), value);
	Show("drag -5 (back)", value, history);
	history.Undo(value);
	Show("undo", value, history);
	history.Execute(std::make_unique<Action>(7, false), value);
	Show("add 7 (redo branch)", value, history);
	history.Undo(value);
	Show("undo again", value, history);

	int small = 0;
	History tiny(2);
	for (int delta = 1; delta <= 3; delta++)
		tiny.Execute(std::make_unique<Action>(delta, false), small);
	Show("capacity 2, three adds", small, tiny);
	while (tiny.Undo(small))
	{
	}
	Show("undo all", small, tiny);
	return 0;
}
