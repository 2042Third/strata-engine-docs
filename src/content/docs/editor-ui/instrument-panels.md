---
id: editor-ui/instrument-panels
title: "Instrument panels"
description: "How the Console, Problems, Activity, Streaming and Performance panels show the editor's machinery while costing almost nothing on an idle frame."
kind: internals
size: L
tracks: [E]
needs: [editor-ui/lists, editor-ui/status, editor/journal, editor/script-builds, worlds/streamer]
time: 85
learn:
  - id: read-instruments
    text: name what each of the five instrument panels shows and where its numbers come from
  - id: idle-contract
    text: explain why a panel compares a version number before it rebuilds its rows
  - id: job-table
    text: trace how the Streaming panel builds its asset table on a job and shows it when done
  - id: write-panel
    text: write a panel whose idle frame rebuilds nothing and draws only the rows on screen
  - id: request-counter
    text: explain how a failed Play brings the Problems panel forward without the core knowing the user interface
since: 0.3.0
status: final
---

The editor runs a :term[build system]{id=build-system}, a crash handler, a command journal, an asset streamer and a frame :term[profiler]{id=profiler-instrumenting-vs-sampling}, and a person
cannot see any of them. Five panels make them visible.

- The **Console** shows the log.
- **Problems** shows script build errors and script crashes.
- **Activity** shows every command the editor ran.
- **Streaming** shows memory and loading.
- **Performance** shows where the :term[frame time]{id=frame-time} goes.

Each panel reads state that other code owns and draws it. None of them
changes the scene, the project or a file. This page explains how they stay cheap. A panel that costs more than the thing it
measures gives wrong numbers and a slow editor at once.

## The problem and how engines solve it

Suppose a panel lists 10,000 journal entries. The editor draws about 60 frames each second, so a frame has 16.7 ms for
everything: the scene view, the inspector, the panels and the work of the game. If the panel walks all 10,000 entries,
filters them and formats their text in every frame, it spends that time whether anything changed or not. A debugging
tool then becomes the main thing a debugger would find in the profile.

Engines meet this in four ways, and each costs something.

- **Draw live data every frame.** The panel reads the source and draws it at once. It is the simplest, it is always
  right, and it scales with the size of the data. It suits a small list.
- **Update widgets on events.** A retained interface keeps one widget per row and the data source tells the panel what
  changed. The panel does no work while idle, but every data source needs a :term[notification]{id=toast} path, and a missed
  notification leaves a stale panel.
- **Keep a version number and rebuild on change.** The source raises a counter whenever it changes. The panel compares
  that number with the one it built from and rebuilds only when they differ. The cost is one comparison per frame, and
  the risk is a source that changes without raising its counter.
- **Move the work to another thread.** A job prepares the rows and the panel shows them when they are done. The frame
  never waits, and the cost is a copy of the data, a second buffer and rows that are a moment old.

Strata combines the last two with a clipped list, which draws only the rows that fit on the screen. The editor is
built on an immediate-mode interface, so there are no widgets to update: the code of a panel runs again each frame and
draws what it finds. Lists that scale are taught in [Lists that scale](../editor-ui/lists.md); this page applies them.

## The map

All five panels share one frame shape, which the panel registry runs. In `OnUpdate` every panel collects its data,
whether it is open or not. In `OnImGuiRender` the registry draws only the panels whose windows show, and calls
`OnHidden` for the others, also for an open panel whose tab hides behind another. Collecting while closed is deliberate: the status bar shows a figure of each panel, such as
the count of errors nobody has seen yet, and the figure must be right when the panel is closed. The rule that follows is that
`OnUpdate` must be cheap, and drawing must not do work that is only needed for the panel's window.

```mermaid caption="One frame of the editor: every panel collects its data, but only shown panels draw, and a job builds the Streaming table." alt="A flow chart. The editor layer asks the registry to update all five panels, and they compare versions and read numbers. The status bar reads figures from that step. The registry then draws only shown panels, and the Streaming panel has a job build its table and swaps it in when done."
flowchart TD
	Layer["EditorLayer: one frame"] --> Update["EditorPanelRegistry::OnUpdate: every panel"]
	Update --> Collect["Collect: compare versions, read numbers"]
	Collect --> Status["Status bar pills read the figures"]
	Layer --> Draw["EditorPanelRegistry::OnImGuiRender"]
	Draw --> Open{"Panel shown?"}
	Open -- yes --> Rows["Draw clipped rows"]
	Open -- no --> Hidden["OnHidden: nothing drawn"]
	Rows --> Job["Streaming: job builds the table"]
	Job --> Swap["Main thread swaps it in"]
```

The five panels differ in what they read and in how they keep their cost low.

| Panel | Reads | Keeps its cost low by |
| --- | --- | --- |
| Console | The log buffer | Appending only new entries; rebuilding its filtered list when entries or filters change |
| Problems | The last script build and the last script crash | Comparing a build number and a crash key; clipping the table |
| Activity | The command journal | Rebuilding rows only when the journal's version or the filters change |
| Streaming | :term[Asset manager]{id=asset-manager} statistics, physics capacity, the world | One statistics read per frame; a table built on a job |
| Performance | The frame profiler's 600 frames | Asking the profiler for a summary at most every quarter second |

Every panel below is a class that derives from `EditorPanel`, declared in `StrataEditor/src/UI/EditorPanelRegistry.h`
and implemented in `StrataEditor/src/Panels/`. The panels belong to the interface layer, so they reach the engine
through `EditorContext`, the one object that holds the editor's state, and never change the scene themselves.

## The contract

A panel keeps six promises. Each has a reason.

1. **An idle frame compares numbers.** If nothing the panel shows has changed, `OnUpdate` returns after comparing a
   version or a build identifier (:term[ID]{id=id}). Reason: the cost of a panel must not depend on how much data it holds.
2. **A big table is drawn clipped.** The panel asks `ImGuiListClipper` which rows are on screen and draws only those.
   Reason: drawing 10,000 rows costs 10,000 times as much as drawing one, and the person sees about 30.
3. **A big table is built off the main thread.** Sorting tens of thousands of rows is a job, not a frame's work.
   Reason: a frame must never wait for a panel.
4. **Text the program does not control is never a label.** :term[Dear ImGui]{id=dear-imgui}, the interface library the editor uses, cuts a
   label at `##` and uses the part after it as an identifier. A :term[compiler]{id=compiler} message may hold `##`. Reason: a label would
   cut the message.
5. **Panels only draw state and call commands.** A button runs a command with the origin of the user interface; it never
   writes a file. Reason: every change must reach the journal and the :term[undo stack]{id=undo-stack}.
6. **The core asks the user interface through counters.** The core raises a number, and the interface compares it each
   frame. Reason: the core must not know the interface exists.

:::rule
The editor's rule says that interface code never walks the scene or the asset folder each frame. It draws cached
views that are rebuilt when versions change, and it draws long lists through `ImGuiListClipper`. The reason is the cost
above: a panel is drawn every frame, so any walk it makes is repeated 60 times a second. The practice is taught in
[Lists that scale](../editor-ui/lists.md).
:::

## A toy version

The toy below is a panel in the engine's shape. A journal raises a version each time an entry is added. The panel
rebuilds its list of matching entries only when the version or the filter differs from what it built from, and its
`Draw` counts only the rows that fit on a 30-row screen. A second panel, with caching disabled, rebuilds every frame.
Both run for 600 frames with 10,000 entries, one entry added at frame 300 and a filter typed at frame 450.

```cpp sketch="editor-ui-instrument-panels-toy.cpp"
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <string>
#include <vector>

// A journal that counts its changes: every Add raises the version.
struct Journal
{
	std::vector<std::string> Entries;
	uint64_t Version = 0;

	void Add(const std::string& text)
	{
		Entries.push_back(text);
		Version++;
	}
};

// A panel in the engine's shape: OnUpdate collects, Draw only reads what OnUpdate prepared.
class ToyPanel
{
public:
	explicit ToyPanel(bool cached)
		: m_Cached(cached)
	{
	}

	void OnUpdate(const Journal& journal, const std::string& filter)
	{
		// Idle frame: one number and one short key are compared, nothing else.
		if (m_Cached && journal.Version == m_Version && filter == m_Filter)
			return;
		m_Version = journal.Version;
		m_Filter = filter;
		m_Rows.clear();
		for (size_t index = 0; index < journal.Entries.size(); index++)
		{
			m_Visited++;
			if (filter.empty() || journal.Entries[index].find(filter) != std::string::npos)
				m_Rows.push_back(index);
		}
		m_Rebuilds++;
	}

	// A clipped list draws only the rows that fit on screen.
	size_t Draw(size_t firstRow, size_t rowsOnScreen) const
	{
		const size_t last = std::min(m_Rows.size(), firstRow + rowsOnScreen);
		return last > firstRow ? last - firstRow : 0;
	}

	size_t GetVisited() const { return m_Visited; }
	size_t GetRebuilds() const { return m_Rebuilds; }
	size_t GetRowCount() const { return m_Rows.size(); }

private:
	bool m_Cached;
	uint64_t m_Version = UINT64_MAX;
	std::string m_Filter;
	std::vector<size_t> m_Rows;
	size_t m_Visited = 0;
	size_t m_Rebuilds = 0;
};

int main()
{
	Journal journal;
	for (int index = 0; index < 10000; index++)
		journal.Add(index % 100 == 0 ? "scene.save" : "entity.move");

	ToyPanel cached(true);
	ToyPanel naive(false);
	size_t drawn = 0;
	for (int frame = 0; frame < 600; frame++)
	{
		if (frame == 300)
			journal.Add("scene.save");
		const std::string filter = frame >= 450 ? "save" : "";
		cached.OnUpdate(journal, filter);
		naive.OnUpdate(journal, filter);
		drawn += cached.Draw(0, 30);
	}
	std::printf("cached: %zu rebuilds, %zu entries visited, %zu rows left, %zu rows drawn\n", cached.GetRebuilds(), cached.GetVisited(),
		cached.GetRowCount(), drawn);
	std::printf("naive:  %zu rebuilds, %zu entries visited\n", naive.GetRebuilds(), naive.GetVisited());
	return 0;
}
```

```text output-of="editor-ui-instrument-panels-toy.cpp"
cached: 3 rebuilds, 30002 entries visited, 101 rows left, 18000 rows drawn
naive:  600 rebuilds, 6000300 entries visited
```

1. **Line 32:** the idle test: a cached panel returns when the version and the filter match what it built from.
2. **Line 39:** each entry looked at counts as one unit of work, so the output measures cost without a clock.
3. **Line 47:** `Draw` touches only the rows that fit the screen, however long the list is.
4. **Line 77:** a new entry at frame 300 raises the version, and the cached panel rebuilds once.
5. **Line 79:** from frame 450 the filter text differs, which also forces one rebuild.

The cached panel rebuilt three times: once at the start, once for the added entry and once for the filter. It visited
30,002 entries in all, while the panel without a cache visited 6,000,300. The ratio is 200 to one, and the ratio
grows with the number of idle frames. The cached panel drew 30 rows per frame whatever the size of the journal.

The toy omits the hard parts of the real code. The real source of a version is another system, the rows
are text that needs measuring and formatting, and some data is too large to rebuild on the :term[main thread]{id=main-thread} at all.

## The real code

### Problems: an idle frame compares two numbers

The Problems panel shows two kinds of trouble. The first is a script crash, which stopped :term[play mode]{id=play-mode}. The second is the
last script build's diagnostics, the errors and warnings the compiler printed. Its `OnUpdate` decides whether anything
changed. Watch the early return: the whole idle cost is one build identifier (ID) and a comparison of a short key.

```cpp src="StrataEditor/src/Panels/ProblemsPanel.cpp#L100-L108" symbol="ProblemsPanel::OnUpdate"
void ProblemsPanel::OnUpdate(EditorPanelContext& context)
{
	// Idle: one number and an empty string compared (a string of a few fields while a crash is shown).
	const uint64_t buildID = context.Context.GetScriptBuilder().GetLastResult().ID;
	const std::optional<ScriptFault>& fault = context.Context.GetLastScriptFault();
	if (m_Built && buildID == m_BuildID && (fault.has_value() == !m_FaultKey.empty()) && (!fault || MakeFaultKey(fault) == m_FaultKey))
		return;
	Rebuild(context);
}
```

The build identifier is a number that grows with each script build, taught in [Building scripts from the editor](../editor/script-builds.md).

The crash key is a string made of the fault's module, method, entity, description and whether it was symbolized. While
no crash is shown the key is empty, so the comparison is between two empty strings. While one is shown, the panel
formats a few fields each frame to compare them. That is a real cost, accepted because it is small and crashes are rare.
The alternative, a version counter on the fault, would need a change in the code that records faults.

When something changed, `Rebuild` runs. It clears the rows and the cached file texts, builds a crash row first when a
crash exists, then one row per diagnostic, and last the summary line. The crash comes first because it stopped the game.

The crash row starts with "Crash in", names the class and method the engine called, and adds the entity's name when it is known.
Below it stand the stack frames that have a :term[source file]{id=source-file}. The next excerpt is the loop that chooses them.

```cpp src="StrataEditor/src/Panels/ProblemsPanel.cpp#L154-L169" from="const auto isLocation = [&](const ScriptCodeLocation& frame)" to="row.Source = ResolveSource(editor, row.File, {});" symbol="ProblemsPanel::Rebuild"
const auto isLocation = [&](const ScriptCodeLocation& frame)
{
	return fault->Location && frame.Address == fault->Location->Address && frame.File == fault->Location->File && frame.Line == fault->Location->Line;
};
for (const ScriptCodeLocation& frame : fault->Stack)
{
	if (frame.File.empty() || isLocation(frame) || frame.Function.starts_with(c_SDKInternalNamespace))
		continue;
	Row row;
	row.Kind = RowKind::Frame;
	row.Text = frame.Function.empty() ? fmt::format("{}+0x{:X}", frame.Module, frame.ModuleOffset) : frame.Function;
	if (frame.Inlined)
		row.Text += " (inlined)";
	row.File = frame.File;
	row.Line = frame.Line;
	row.Source = ResolveSource(editor, row.File, {});
```

1. **Line 154:** the :term[lambda]{id=lambda} finds the frame that is the crash's own location, matching address, file and line.
2. **Line 160:** a frame without a file, the location frame and a function of the script kit's internals are skipped with one `continue`.
3. **Line 164:** a frame with no function name shows its module and offset, so the row is never empty.
4. **Line 169:** `ResolveSource` turns the file into a path that exists on this machine, or an empty path.

A frame that has no file is skipped: a person cannot open it. The frame at the crash location is skipped as well,
because the crash row stands for it. Frames whose function starts with `Strata::Detail::` are skipped too. Those are the
:term[thunks]{id=thunk}, small functions the script software development kit (:term[SDK]{id=sdk}) uses to call your class, and no person acts on them. The command `script.status`
keeps them for anyone who needs the whole stack, a subject for [symbolization](../scripting/symbolization.md).

`ResolveSource` is the answer to the question where a compiler's file name lives. An :term[absolute path]{id=absolute-path} is used if the file
exists. A relative path is tried against the project folder, then its script folder, then the build folder, because
compilers name files relative to where they ran. A row whose file is found can be opened; a row without one says so in
its tooltip, either "No source file" or "The file is not on this machine". The File column shows the path relative to
the project when the file lies there, which is how a person knows the project's files.

The summary line has a fixed set of forms. With no build and no crash it reads "No script build in this session yet."

A crash puts "The scripts crashed in" and the function first. A build adds "Build 4 failed: 2 errors, 1 warning.",
"Build 4 succeeded.", "Build 4 succeeded with 1 warning." or "Build 4 cancelled." according to its result. The wording follows the count, so a single error reads "1 error".

:::example[Reading the Problems panel]
You add a call to a function that does not exist, and press **Ctrl+B**. Build 4 fails with two errors and one warning.
The panel shows three rows, ordered as the compiler reported them, and the summary reads "Build 4 failed: 2 errors, 1
warning." in the error color.

You fix both errors and build again. Build 5 succeeds with the warning, so its identifier differs from the one the panel
built from, and `Rebuild` runs once. The summary reads "Build 5 succeeded with 1 warning." Nothing else changes, so for
every later frame `OnUpdate` compares 5 with 5 and returns.

Now the game crashes in the update :term[callback]{id=callback} of one of your classes. The key of the fault differs from the empty key, so
the panel rebuilds. The crash row comes first, its stack frames follow, and the summary leads with "The scripts crashed
in" and the function, followed by the build's outcome.
:::

### Problems: the clipped table

The table of rows is drawn with `ImGuiListClipper`. That helper reports the range of rows that are visible, and the loop draws
only those. The first excerpt shows the loop and the double click.

```cpp src="StrataEditor/src/Panels/ProblemsPanel.cpp#L272-L301" from="ImGuiListClipper clipper;" to="open = index;" symbol="ProblemsPanel::OnImGuiRender"
ImGuiListClipper clipper;
clipper.Begin(static_cast<int>(m_Rows.size()));
std::optional<size_t> open;
while (clipper.Step())
{
	for (int line = clipper.DisplayStart; line < clipper.DisplayEnd; line++)
	{
		const size_t index = static_cast<size_t>(line);
		const Row& row = m_Rows[index];
		ImGui::TableNextRow();
		ImGui::TableSetColumnIndex(0);
		ImGui::PushID(line);
		// A frame of the crash's stack goes under the crash, its icon included (indenting after the icon would move the
		// text back onto it).
		if (row.Kind == RowKind::Frame)
			ImGui::Indent(ImGui::GetFontSize());
		const ImVec4& color = row.Kind == RowKind::Warning ? colors.Warning : (row.Kind == RowKind::Frame ? colors.TextSecondary : colors.Error);
		ImGui::PushStyleColor(ImGuiCol_Text, color);
		ImGui::TextUnformatted(GetIcon(row.Kind));
		if (index < c_ProbedRows)
			UI::ItemProbe::Record(UI::NumberedProbeKey("Problems.Icon.", index));
		ImGui::PopStyleColor();
		ImGui::SameLine();
		// An unlabeled row with the text drawn after it: messages may hold "##" (token pasting), which a label would cut.
		ImGui::Selectable("##Row", false, ImGuiSelectableFlags_SpanAllColumns | ImGuiSelectableFlags_AllowDoubleClick);
		// The first rows only: the probe keeps a fixed set of keys.
		if (index < c_ProbedRows)
			UI::ItemProbe::Record(UI::NumberedProbeKey("Problems.Row.", index), !row.Source.empty(), 0, row.Text);
		if (ImGui::IsItemHovered() && ImGui::IsMouseDoubleClicked(ImGuiMouseButton_Left))
			open = index;
```

1. **Line 272:** `ImGuiListClipper` learns the total row count and then asks which rows are on screen.
2. **Line 286:** a stack frame sits one step to the right of its crash, icon included, so the text does not move back onto the icon.
3. **Line 296:** the row is a selectable item without a label, `##Row`, with the text drawn after it, because a message may hold `##`.
4. **Line 298:** only the first rows are recorded in the :term[item probe]{id=item-probe}, the tool tests use to find items on screen.
5. **Line 301:** a double click records the row; the panel opens the source after the table, never inside the loop.

The File column has a second cost. Long paths must be cut to fit the column, and the cut keeps the end of the path,
because the file name is what matters. Measuring text is slow, so the panel cuts each text once per column width.

```cpp src="StrataEditor/src/Panels/ProblemsPanel.cpp#L325-L331" from="const float fileWidth = ImGui::GetContentRegionAvail().x;" to="m_FileTextsWidth = fileWidth;" symbol="ProblemsPanel::OnImGuiRender"
const float fileWidth = ImGui::GetContentRegionAvail().x;
if (fileWidth != m_FileTextsWidth || m_FileTexts.size() != m_Rows.size())
{
	m_FileTexts.clear();
	for (const Row& each : m_Rows)
		m_FileTexts.push_back(UI::ElideStart(each.ShownFile, fileWidth));
	m_FileTextsWidth = fileWidth;
```

1. **Line 326:** the texts are cut again only when the width changes or the number of rows differs.
2. **Line 330:** `UI::ElideStart` cuts at the start of the path and keeps the file name visible.

Opening a row is `OpenRow`. It fails with a reason that the panel shows in a warning color next to the summary, as in
"There is no file" with the name or "This entry names no source file". Otherwise `EditorContext::OpenScriptSource` starts the
external editor at the file, line and column. The editor starts only for source code, build files and plain text inside the project or the engine,
so a compiler message cannot make it open any file on disk. The reasons are cleared with the rows,
because an error about an earlier row says nothing about the new ones.

### Console: collect while closed

The Console shows the log. Its `OnUpdate` copies the new log entries into the panel's own list, so the list holds
messages even while the window is closed. The next excerpt is that collecting.

```cpp src="StrataEditor/src/Panels/ConsolePanel.cpp#L21-L35" from="LogBuffer& buffer = Log::GetBuffer();" to="m_Entries.pop_front();" symbol="ConsolePanel::OnUpdate"
LogBuffer& buffer = Log::GetBuffer();
for (LogEntry& entry : buffer.GetEntries(m_LastSequence))
{
	m_LastSequence = entry.Sequence;
	// Errors another pill reports (a failed script build: "Build failed · 2 errors") are not unread news besides.
	if (entry.Level >= LogLevel::Error && !context.Context.IsAnnouncedLogEntry(entry.Sequence))
		m_UnreadErrors++;
	std::optional<ScriptDiagnostic> reference = FindSourceReference(entry.Message);
	m_References.push_back(reference ? std::make_shared<const ScriptDiagnostic>(std::move(*reference)) : nullptr);
	m_Entries.push_back(std::move(entry));
	m_EntriesChanged = true;
}
while (m_Entries.size() > buffer.GetCapacity())
{
	m_Entries.pop_front();
```

1. **Line 22:** only the entries newer than the last sequence number are fetched, so an idle frame fetches none.
2. **Line 26:** an error counts as new unless another pill already announced it, such as a failed script build.
3. **Line 28:** each message is searched once for a source reference such as a file and a line, and the result is stored.
4. **Line 33:** the list never grows beyond the log buffer's own capacity, which keeps old entries from piling up.

The window has check boxes for **Trace**, **Info**, **Warnings** and **Errors**, a search field, **Auto-scroll** and
**Clear**. The filtered list is rebuilt when entries arrive or when the key of the filters changes, and then drawn with `ImGuiListClipper`.

A message with a source reference shows a hand cursor when hovered, with a tooltip "Click to open ... at line ...".
A click opens the external editor. The count of new errors returns to zero when the
Console has the keyboard focus. The exception is the frame its window first appears, because a new window takes the focus
before anyone has looked at it.

### Streaming: a table built on a job

The Streaming panel shows how the asset system uses memory, and it is the largest of the five. At the top it counts
assets that are registered, ready, streaming, failed and pinned. Its sections are **World**, **Physics**, **Memory**,
**Loads and uploads** and **Assets**.

The **World** section shows the cell map while a world streams, taught in
[Grids, cells and the streamer](../worlds/streamer.md). **Physics** shows the running game's bodies against its capacity.
**Memory** shows each pool against its budget, and **Loads and uploads** shows queues and a small chart of the :term[bytes]{id=byte}
uploaded to the :term[graphics card]{id=gpu} in each of the latest frames. The terms are those of
[Residency, budgets and pools](../assets/residency.md), which this page uses and does not repeat.

The panel's `OnUpdate` is the cheap part: one statistics read of the asset manager per frame, one upload sample for the
chart, and, only while a game runs, two lookups of physics services. It runs while the panel is closed, so the status
bar's assets pill and its pill of bodies without collision stay right.

The **Assets** section is a table of every asset that is resident, loading, failed or pinned, with failed assets first.
It has a Mip column that shows the mip levels resident and wanted.

A world can hold tens of thousands of assets.
Sorting that many names every frame would cost more than the frame, so a job does it. The table is built only while the panel draws its **Assets** section, because nothing else reads it. The next excerpt decides when.

```cpp src="StrataEditor/src/Panels/StreamingPanel.cpp#L609-L626" symbol="StreamingPanel::UpdateTable"
void StreamingPanel::UpdateTable(const Ref<AssetManagerBase>& manager)
{
	if (m_TableJob.IsValid() && m_TableJob.IsComplete())
		FinishTableBuild();
	if (m_TableJob.IsValid())
		return; // One build at a time: a change waits for the running build, then starts the next

	const double now = ImGui::GetTime();
	const bool due = m_LastTableRefresh < 0.0 || now - m_LastTableRefresh >= c_TableRefreshSeconds || now < m_LastTableRefresh;
	const bool changed = !IsTableShown(manager) || m_Table->SortColumn != m_SortColumn || m_Table->SortAscending != m_SortAscending
		|| m_Table->Filter != m_Filter;
	if (!due && !changed)
		return;
	StartTableBuild(manager);
	// Without job threads (JobSystem not running) the job ran in Submit: show its rows at once.
	if (m_TableJob.IsComplete())
		FinishTableBuild();
}
```

1. **Line 611:** a finished job is collected first, so its rows show in the same frame.
2. **Line 613:** one build at a time: while a job runs, a change waits for it, and the next build starts afterwards.
3. **Line 617:** a build is due when none ran yet, when 0.25 seconds passed, or when the clock went backward.
4. **Line 618:** a new sort column, direction, filter or asset manager also starts a build.
5. **Line 624:** with no job threads, the job already ran inside `Submit`, so its rows show at once.

`c_TableRefreshSeconds` is 0.25, so the table is read at most four times a second however fast frames are. The sort or
the filter changing is a request from the person and does not wait for the quarter second, only for a job :term[in flight]{id=in-flight}.

The build copies on the main thread and works on the job. The next excerpt is the copy and the start of the job.

```cpp src="StrataEditor/src/Panels/StreamingPanel.cpp#L637-L656" from="const uint64_t version = manager->GetMetadataVersion();" to="m_TableJob = JobSystem::Submit([target]() { BuildTable(*target); });" symbol="StreamingPanel::StartTableBuild"
const uint64_t version = manager->GetMetadataVersion();
if (m_Labels && IsSameManager(m_LabelsManager, manager) && version == m_LabelsVersion)
{
	build.ReusedLabels = m_Labels;
	build.Metadata.reset();
}
else
{
	build.ReusedLabels.reset();
	build.Metadata = manager->GetAllMetadata();
}
build.MetadataVersion = version;
// Last uses count back from the frame the samples were read in, not the frame they are shown in.
build.Frame = manager->GetFrameIndex();
manager->GetResidencySamples(build.Samples);

m_TableBuilds++;
m_LastTableRefresh = ImGui::GetTime();
TableBuild* target = &build;
m_TableJob = JobSystem::Submit([target]() { BuildTable(*target); });
```

1. **Line 637:** the version of the asset records is read before the names, so an asset registered meanwhile forces a second read.
2. **Line 638:** the names of the last build are kept when the manager and the version are unchanged.
3. **Line 651:** the main thread copies the residency samples, a flat copy, because the job must not read live state.
4. **Line 656:** the job receives a pointer to the build record, which stays alive because the panel owns it.

The panel owns two build records. The job fills the second while the screen shows the first. When the job is complete,
`FinishTableBuild` swaps the two with `std::swap(m_Table, m_NextTable)`, so the table on screen is never half written.

The visible table and the job never touch the same record, which is why no lock is needed. The cost is that the table
may be a quarter second old. Because the job holds a pointer into the panel, `OnDetach`, which the registry calls on every panel when the editor
removes its panels, waits for it before the panel is destroyed. A job that lived longer than its record would write into freed memory.

### Activity: rows rebuilt on a version

The Activity panel shows the command journal, taught in [the activity journal and replays](../editor/journal.md). Every
command that ran is a row: its source as an icon, its command with an arrow, a one-line summary and its duration in
milliseconds. The arrow shows the entry's raw parameters and its result in two extra lines under the row. The source
list offers **Every source**, **UI**, **Automation**, **Command scripts** and **Editor**; the check box **Changes only**
keeps the commands that edit something, the very ones a replay repeats. The search field
matches the command, the client, the parameters and the error text.

Selecting a row shows its details: the entry as a :term[JSON]{id=json} text, the same that `editor.activity` returns, in a read-only
field you can select and copy. Three buttons act on it.

**Copy as script** puts a :term[command script]{id=command-script} step on the clipboard,
so the command can run again with `StrataEditor --commands`. **Re-run** runs the command again with the same
parameters, as the person. **Undo to here** undoes every step after this entry's own. Each button is disabled when it
could be wrong, and its tooltip says why: the journal shortens very large parameters, and then neither **Copy as
script** nor **Re-run** can be exact.

The rows are rebuilt only when the journal changed or a filter did. The excerpt is the whole decision.

```cpp src="StrataEditor/src/Panels/ActivityPanel.cpp#L167-L198" from="const std::string filter = StringUtils::ToLower(m_Filter);" to="m_Lines.push_back({ entry.Id, LineKind::Entry });" symbol="ActivityPanel::RebuildRows"
const std::string filter = StringUtils::ToLower(m_Filter);
const std::string key = fmt::format("{}|{}|{}|{}", m_SourceFilter, m_EditsOnly, m_ExpandedVersion, filter);
if (journal.GetVersion() == m_RowsVersion && key == m_RowsKey)
	return;
m_RowsVersion = journal.GetVersion();
m_RowsKey = key;

const std::deque<CommandJournalEntry>& entries = journal.GetEntries();
// Previews and expansions of entries the ring dropped go with them.
const uint64_t oldest = entries.empty() ? UINT64_MAX : entries.front().Id;
std::erase_if(m_ParameterPreviews, [oldest](const auto& preview) { return preview.first < oldest; });
std::erase_if(m_Expanded, [oldest](uint64_t id) { return id < oldest; });

m_Rows.clear();
m_Lines.clear();
for (const CommandJournalEntry& entry : entries)
{
	if (m_SourceFilter > 0 && static_cast<int>(entry.Source) != m_SourceFilter - 1)
		continue;
	if (m_EditsOnly && entry.Kind != EditorCommandKind::Edit)
		continue;
	if (!filter.empty())
	{
		const bool found = StringUtils::ToLower(entry.Command).find(filter) != std::string::npos
			|| StringUtils::ToLower(entry.Client).find(filter) != std::string::npos
			|| StringUtils::ToLower(GetParameterPreview(entry)).find(filter) != std::string::npos
			|| StringUtils::ToLower(entry.Error).find(filter) != std::string::npos;
		if (!found)
			continue;
	}
	m_Rows.push_back(entry.Id);
	m_Lines.push_back({ entry.Id, LineKind::Entry });
```

1. **Line 168:** the key joins the source filter, the changes-only flag, a version of the expanded rows and the text.
2. **Line 169:** an unchanged journal version with an unchanged key returns, so an idle frame compares one number and a string.
3. **Line 177:** previews of entries that the journal's ring has dropped are erased with them.
4. **Line 192:** the parameter preview is computed once per entry, so searching does not dump the JSON again.

An entry expands into three lines, the entry, its parameters and its result, so `ImGuiListClipper` draws lines, not entries.
Expanding a row changes the key and rebuilds the lines. The journal's version is raised when an entry is added or its
status changes, so a command that is running and then finishes also causes a rebuild.

### Performance: reading a ready summary

The Performance panel shows 600 frames of the frame profiler, taught in [Measuring the frame](../core/profiling.md).
A stacked chart shows the :term[central processing unit]{id=processor} (CPU) time of each frame, split into stages, with the newest frame at the right edge, and a
second chart shows the graphics processing unit (GPU) time. A frame is marked as a spike when its time is above a threshold that the code
computes as the larger of one 60th of a second and twice the median :term[work time]{id=work-time}.

:::example[The spike threshold]
At a median work time of 5 ms, twice the median is 10 ms and one 60th of a second is 16.7 ms. The threshold is 16.7
ms, so only frames above a 60-frames-per-second budget count. At a median of 14 ms, twice the median is 28 ms, which is
larger, so the threshold is 28 ms. A game that always runs slowly is not marked all over, only the frames that are
twice its usual.
:::

Under the charts a table lists the stages. One line says what bounds the frame. The text ":term[GPU-bound]{id=gpu-bound}: GPU 11.8 ms busy of
12.3 ms frames (CPU 9.8 ms)" means the graphics processor limits the frame, and ":term[CPU-bound]{id=cpu-bound}" means the main thread does.
Two more forms cover frames held to a limit and frames without GPU times.

The panel's `OnUpdate` only samples the job system, and
the summary is computed again at most every quarter second; both are read from the profiler, so the panel measures nothing
itself. **Pause**, or **Space** while the panel has the focus, holds the frames still. The profiler continues measuring.
The panel waits for the GPU times of the frames at the click, then keeps a snapshot, so a paused table is complete.
**Copy as JSON** puts what the command `editor.perf` returns for the 600 frames on the clipboard.

### Play brings the Problems panel forward

When you press Play and the script build fails, or the build works but its module does not load, you must see the
errors. The command `play.start` is in the core, which does not know panels exist. So it calls `RequestProblemsPanel`,
which raises a counter. The interface compares the counter in each frame. The excerpt is that comparison, next to the
older one it copies.

```cpp src="StrataEditor/src/EditorLayer.cpp#L1028-L1037" from="if (m_Context.GetInspectionVersion() != m_ShownInspectionVersion)" to="m_Panels.Focus(EditorPanels::c_Problems);" symbol="EditorLayer::OnImGuiRender"
if (m_Context.GetInspectionVersion() != m_ShownInspectionVersion)
{
	m_ShownInspectionVersion = m_Context.GetInspectionVersion();
	m_Panels.ShowTab(m_Context.GetInspectionTarget() == InspectionTarget::Asset ? EditorPanels::c_AssetInspector : EditorPanels::c_Inspector);
}
// A play whose script build failed shows its errors.
if (m_Context.GetProblemsPanelRequests() != m_ShownProblemsRequests)
{
	m_ShownProblemsRequests = m_Context.GetProblemsPanelRequests();
	m_Panels.Focus(EditorPanels::c_Problems);
```

1. **Line 1028:** the first counter is the inspection version, which switches to the Asset tab or the Inspector.
2. **Line 1034:** the second compares the number of Problems requests with the last number the layer acted on.
3. **Line 1037:** a difference focuses the panel once, and the layer then stores the number.

Two code paths in `StrataEditor/src/Editor/Commands/PlayCommands.cpp` raise the counter: a failed build and a module that
did not load. A cancelled build raises nothing, since cancelling is the person's decision. The build already told the
person through a notification with a **Show Problems** button, so the command marks its failure as announced and no
second toast appears. The counter pattern is the one of [inspectors](../editor-ui/inspectors.md), and it needs no
:term[callback]{id=callback}: the core stays ignorant of the interface, and two requests in one frame produce one focus.

The pictures below show the panels as commands leave them, with no pointer over a panel. The Console therefore shows its message without the hand cursor or the tooltip. No row of the Activity panel is selected, so its details and its three buttons stay hidden.

::figure{id=problems-failed-build}

::figure{id=console-source-reference}

::figure{id=activity-details}

::figure{id=performance-timeline}

::figure{id=streaming-cell-map}

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Rebuild every frame | Small tools, prototypes | No version counters, no stale rows | A cost that grows with the data, paid on idle frames |
| Retained widgets updated by events | Many desktop interface libraries | No work while idle | A notification path from every data source |
| A background thread that draws | Rare | Smooth panels whatever the frame | Interface calls from workers, which the interface library forbids |
| Sampling at a fixed rate for every panel | Profilers | One simple rule | Stale data for panels that change rarely, wasted reads for others |
| Every panel on a job | Large data tools | Equal treatment | Copies and swaps for panels that hold 20 rows |

Strata chooses by the size of the data. Problems holds a few rows, so a version compare is enough. Streaming holds tens
of thousands, so it also needs a job. The cost of the choice is that every panel must know its own version.

## How it is tested

The panel suites run inside the editor tests, with the panel drawn against a test context, and read results through the
item probe.

`Editor.UI.Scripts`, in `StrataTests/src/Editor/EditorScriptUITests.cpp`, checks that a failed build's
diagnostics are listed, that a double click opens the source and that a crash shows where it happened. The File column is cut at the
start where it is narrow. A failed build and a crash show one toast each.

`Editor.UI.Activity`, in
`StrataTests/src/Editor/ActivityUITests.cpp`, checks that commands are listed, filtered and acted on, that raw parameters
show on demand and that **Re-run** and **Undo to here** work on the oldest entry of a full journal.

`Editor.Streaming`, in
`StrataTests/src/Editor/EditorStreamingTests.cpp`, checks the statistics that the Streaming panel shows. The cost budgets of the panels are taught in
[testing the interface](../editor-ui/ui-testing.md). Run one suite directly:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Editor.UI.Scripts
```

The runner lists any failed check with its file and line, and ends with a count of the test cases that passed.

## Changing it safely

To add a panel, derive from `EditorPanel`, register it with `EditorPanelRegistry`, and keep the contract: collect in
`OnUpdate`, compare a version first, draw clipped. To change what a panel reads, add the number it compares. The rules
that apply, with their reasons:

- A button runs a command with `CommandOrigin { CommandSource::UI }`, so the journal records who acted.
- A panel never writes or removes a file, because a file change must go through a command that can be undone or refused.
- Text from outside, such as a compiler message or a log line, is drawn after an item without a label.
- A job never reads live engine state: copy on the main thread, work on the copy, show it on the main thread.
- A panel that waits for a job must wait for it in `OnDetach`.
- A new colour comes from a theme token, never a number written in the panel.

Before you commit, run the suites above, the ones for the panel you changed, and the :term[layering test]{id=layer-table}, which checks that a
panel includes only what its layer allows.

## Summary

- The five panels show the log, script problems, the command journal, streaming and the frame, each from state another system owns.
- A panel compares a version, an ID or a key before rebuilding rows, so an idle frame costs a comparison.
- The Streaming table is copied on the main thread, built on a job, and swapped in when finished, at most every quarter second.
- A panel for a big list rebuilds only on a version change and draws only the rows on screen.
- A failed Play raises a counter in the core, and the interface compares it each frame and focuses the Problems panel.

## Check yourself

1. An idle frame of the Problems panel does which of these?

   - Option a: it reads every diagnostic again and compares each with its row.
   - Option b: it compares the last build's ID and a key of the last crash, and returns.
   - Option c: it waits for the script build to finish.
   - Option d: it rebuilds the rows only when the window is visible.

   :::answer{tests="idle-contract"}
   Answer b. Option a would make the cost grow with the number of diagnostics, which the early return avoids. Option c
   is wrong because a panel never waits for a build. Option d is wrong because `OnUpdate` runs while the window is
   closed, so that the status bar's figure stays right.
   :::

2. Run the toy with 20,000 entries and no other change. How many entries does the cached panel visit in 600 frames?

   :::answer{tests="write-panel"}
   The panel rebuilds three times, as before, and each rebuild visits every entry: 20,000 at the start, 20,001 after the added
   entry and 20,001 for the filter. The total is 60,002. The count depends on the number of rebuilds and the size of the
   data, never on the 600 frames.
   :::

3. The person changes the sort column of the asset table while a job is running. When does the new order appear?

   :::answer{tests="job-table"}
   The running job finishes first, since there is one build at a time. After the swap the change is seen, so a new
   build starts at once, with no wait for the quarter second, and its result appears when that job is done.
   :::

4. A median work time of 14 ms and a frame of 20 ms: is the frame a spike in the Performance panel?

   :::answer{tests="read-instruments"}
   No. The threshold is the larger of 16.7 ms and twice 14 ms, which is 28 ms, and 20 ms is below it.
   :::

5. Why does `play.start` call `RequestProblemsPanel` and not the panel's own function?

   :::answer{tests="request-counter"}
   The command lives in the editor's core, which does not depend on the interface. It raises a number, and the interface
   layer compares it each frame and focuses the panel. A direct call would make the core depend on the interface.
   :::

## Exercises

1. **Basic.** Find where an idle frame of the Problems panel returns. Use a debugger or a search, and name the file and
   the function.

   :::answer[Worked solution]{tests="idle-contract"}
   Search for `ProblemsPanel::OnUpdate`. It is in `StrataEditor/src/Panels/ProblemsPanel.cpp`. Put a breakpoint on its
   first line, run the editor, and step: with no build running, the `if` that compares `buildID` with `m_BuildID` and the
   key of the fault returns before `Rebuild`.
   :::

2. **Medium.** In a project with a script, introduce a :term[compile error]{id=compile-error} in the script's source, build from the editor with
   **Ctrl+B**, double click the row, and then press Play. Describe what you see.

   :::answer[Worked solution]{tests="read-instruments,request-counter"}
   Open the script in the external editor and change the name of a function you call to one that does not exist.
   Press **Ctrl+B**. The summary of the Problems panel reads "Build N failed: 1 error, 0 warnings." and one row shows its
   file and line. A double click opens the file at that line.

    Press Play with the error still there: the play command waits for a build, and the build fails.
   The command
   raises the Problems request, and the panel comes forward. Fix the error and build again to see "Build N succeeded."
   :::

3. **Hard.** Extend the toy: a panel of assets sorted by name or by size that sorts only when the data version or the sort
   column changes, and counts its comparisons.

   :::answer[Worked solution]{tests="write-panel" solution="sketches/editor-ui-instrument-panels-sorted.cpp"}
   The sketch sorts four assets and counts comparisons. Look at how the 100 frames cost one sort, and the changed column one more.

   ```cpp sketch="editor-ui-instrument-panels-sorted.cpp"
   #include <algorithm>
   #include <cstdint>
   #include <cstdio>
   #include <string>
   #include <vector>

   struct Asset
   {
   	std::string Name;
   	int Bytes = 0;
   };

   // Rows are sorted only when the data version or the sort column changes.
   class SortedPanel
   {
   public:
   	void OnUpdate(const std::vector<Asset>& assets, uint64_t version, bool byBytes)
   	{
   		if (version == m_Version && byBytes == m_ByBytes)
   			return;
   		m_Version = version;
   		m_ByBytes = byBytes;
   		m_Rows = assets;
   		std::sort(m_Rows.begin(), m_Rows.end(), [&](const Asset& left, const Asset& right)
   		{
   			m_Comparisons++;
   			return byBytes ? left.Bytes > right.Bytes : left.Name < right.Name;
   		});
   	}

   	size_t GetComparisons() const { return m_Comparisons; }
   	const std::vector<Asset>& GetRows() const { return m_Rows; }

   private:
   	uint64_t m_Version = UINT64_MAX;
   	bool m_ByBytes = false;
   	std::vector<Asset> m_Rows;
   	size_t m_Comparisons = 0;
   };

   int main()
   {
   	std::vector<Asset> assets = { { "rock", 300 }, { "tree", 900 }, { "bush", 120 }, { "sky", 500 } };
   	SortedPanel panel;
   	for (int frame = 0; frame < 100; frame++)
   		panel.OnUpdate(assets, 1, false);
   	const size_t afterIdle = panel.GetComparisons();
   	panel.OnUpdate(assets, 1, true);
   	std::printf("100 frames, one sort: %zu comparisons in total\n", afterIdle);
   	std::printf("after the sort changed: %zu more, first row %s\n", panel.GetComparisons() - afterIdle, panel.GetRows()[0].Name.c_str());
   	return 0;
   }
   ```

   ```text output-of="editor-ui-instrument-panels-sorted.cpp"
   100 frames, one sort: 6 comparisons in total
   after the sort changed: 7 more, first row tree
   ```

   1. **Line 19:** the panel returns when the version and the sort column are the same as before.
   2. **Line 26:** the comparison counts each call, so the output shows when the sort ran.
   3. **Line 31:** `GetComparisons` lets a test check that idle frames sorted nothing.
   :::

## Where it lives in Strata

- Panels: `StrataEditor/src/Panels/ConsolePanel.cpp`, `StrataEditor/src/Panels/ProblemsPanel.cpp`, `StrataEditor/src/Panels/ActivityPanel.cpp`, `StrataEditor/src/Panels/StreamingPanel.cpp` and `StrataEditor/src/Panels/PerformancePanel.cpp`.
- The registry that runs them: `StrataEditor/src/UI/EditorPanelRegistry.cpp`.
- The counter: `EditorContext::RequestProblemsPanel` in `StrataEditor/src/Editor/EditorContext.h`, raised in `StrataEditor/src/Editor/Commands/PlayCommands.cpp`, compared in `StrataEditor/src/EditorLayer.cpp`.
- Tests: the suites `Editor.UI.Scripts`, `Editor.UI.Activity` and `Editor.Streaming`.
- Commands: `editor.activity`, `editor.perf`, `asset.stats`, `script.build`, `script.status`.

## Further reading

- Dear ImGui documentation, the manual of the interface library: how `ImGuiListClipper` and identifiers work (intermediate).
- "Game Programming Patterns", chapter "Dirty Flag", by Robert Nystrom: the version-number idea in general (beginner).
