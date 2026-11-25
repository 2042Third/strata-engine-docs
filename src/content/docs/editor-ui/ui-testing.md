---
id: editor-ui/ui-testing
title: "Testing a UI without a screen"
description: "How Strata tests the editor's interface with no window and no GPU: injected input over frames, probe keys, source scans and panel budgets."
kind: internals
size: L
tracks: [E]
needs: [editor-ui/shell, core/first-change]
time: 70
learn:
  - id: click-frames
    text: explain why a click in a UI test takes three frames and what each frame does
  - id: find-by-key
    text: write a test that finds a kit widget by its probe key and clicks it
  - id: source-scan
    text: explain how a source scan turns a rule of the UI code into a test, and why its list of exceptions stays empty
  - id: panel-budget
    text: compute what a panel's 95th percentile frame hides, and name the metric that catches it
  - id: add-rule
    text: write a scan rule with a self-test that checks what it finds and what it allows
since: 0.3.0
status: final
---

A person tests a screen by looking at it, but a test program cannot look, and the build machines that run it have no display and often no :term[graphics processing unit]{id=gpu} (GPU). Strata still tests the editor's interface thoroughly: it draws the real editor in memory, sends it fake mouse and keyboard input, and reads back where each widget is. It also reads the editor's :term[source files]{id=source-file} as text to enforce rules that a :term[compiler]{id=compiler} cannot check, and it times panels that hold huge amounts of data. This page covers the test rig and the rules it enforces. The page omits the test program, the perf lab, GPU tests and the writing of a panel.

## The problem and how engines solve it

Suppose you must test the **Play** button in the row of buttons at the top of the editor. The obvious test clicks the pixel at x = 812, y = 24 and checks that the game started. The test passes today, but next month a designer adds a button on the left, and the **Play** button moves 32 pixels right. The test now clicks empty space, fails, and tells you nothing about what broke. A test that fails for a reason unrelated to the code it guards costs trust, and people start to ignore failures.

Three families of answer exist. Each has a cost.

- **Screenshots and coordinates.** A script drives a real window and compares pictures or clicks fixed positions. It tests what the person sees, but it needs a display and a graphics driver, it is slow, and any layout or :term[font]{id=font} change breaks it.
- **Accessibility trees.** Many libraries for a user interface (UI) publish a tree of widgets with names, so a test can ask for "the button named Play". That survives layout changes, but it needs a library that builds such a tree.
- **A real UI library with injected input.** The test creates the library's context, feeds it events over several frames, and asks the library where each widget is. No window exists, so nothing needs a display.

Strata uses the third family, because the editor's interface is drawn by :term[ImGui]{id=dear-imgui}, an immediate-mode library that draws every widget again on every frame. ImGui can run with no window at all: it needs only a display size and a clock. The test gives it both, and the editor's own code runs as it does in the program.

Strata adds two things on top. The first is a probe, a small table in which every widget of the kit records its rectangle under a name, so a test finds widgets by name instead of position. The second is a set of tests that read source files as text. Some rules, such as "colors come only from the theme", cannot be expressed as types, so a test searches the code for what breaks them.

The cost is fidelity. No pixels are drawn to a screen, so a test cannot see a clipped label or an ugly color. A GPU test or a person must judge those. The harness also depends on ImGui's frame rules, which the next sections explain, so a test must know that a click takes several frames. For the test kinds that do use a screen, see [Kinds of test](../engineering/test-kinds.md).

## The map

Every UI test in the area runs on the same stack. At its base is a **UI harness**, a test rig that draws the real interface through ImGui with no window and no GPU, and feeds it injected input.

The harness owns an :term[ImGui context]{id=imgui-context} with the editor's fonts and theme, accepts injected input through ImGui's queue, and runs the frames. Above it sits either the real editor layer or one panel drawn in a window of the test's own. Beside it stands a fake host, which answers the questions the editor layer asks of the application. The probe sits to the side: widgets write to it while they draw, and the test reads from it.

```mermaid caption="The test drives a harness editor. Input goes through the queue into the editor layer, the widgets record their rectangles in the probe, and the test reads the probe to find where to click next." alt="Boxes joined by arrows. A test case uses a harness editor, which holds a fake host, an ImGui context with the editor fonts and theme, and the editor layer. The test sends mouse and key input into an input queue that feeds the context. The editor layer draws widgets that record their rectangles in the item probe. The test looks keys up in the probe and clicks the rectangle's center."
flowchart LR
	Test["Test case"] -->|"MoveMouse, SetMouseButton, SetKey"| Queue["Input queue"]
	Queue --> Ctx["ImGui context: editor fonts and theme"]
	Host["FakeEditorHost: time, focus, UI scale"] --> Layer["EditorLayer or one panel"]
	Ctx --> Layer
	Layer -->|"widgets of the kit record"| Probe["ItemProbe"]
	Probe -->|"Find(key), ClickItem"| Test
```

Four files carry the stack, all under `StrataTests/src/Editor/` except the probe:

- `ImGuiHarness.h` and `ImGuiHarness.cpp` hold `FakeEditorHost` and `ImGuiHarness`.
- `HarnessEditor.h` holds `HarnessEditor`, a real editor layer on the harness, with helpers for clicks and typing.
- `StrataEditor/src/UI/ItemProbe.h` and `ItemProbe.cpp` hold `UI::ItemProbe`, which is part of the editor, not of the tests.
- `EditorUISourceTests.cpp` holds the source scans, and `EditorPanelPerfTests.cpp` the panel budgets.

The probe lives in the editor because it must run in every :term[build configuration]{id=build-configuration}, so tests see what users get. Each widget of the kit writes one entry per frame, a single hash-map write, so the cost is small.

## The contract

A test of the UI relies on rules that keep it stable and honest. Each rule has a reason.

1. **One harness at a time.** An `ImGuiHarness` creates an ImGui context and makes it the current one, and its :term[destructor]{id=destructor} destroys it. Two live harnesses would fight over the current context, and the second would draw into the first one's state. Tests therefore create the harness at the top of a test case and let it end with the case.
2. **Find widgets by key, never by position.** The kit's widgets record themselves under the :term[id]{id=id} they were given, as a name. A test calls `ClickItem("Toolbar.Play", layer)` with that key. The harness moves the mouse to the rectangle's center, so a layout change cannot break the test, and a renamed widget fails loudly with a missing key.
3. **Click over frames.** Input is queued, and a frame applies it. A click is three frames, and a test never presses and releases inside one frame.
4. **A key must name one enabled widget.** `ClickItem` returns false and sends no input when the probe has no entry, the entry is marked a duplicate (two widgets recorded the same key in one frame), or the widget is drawn disabled. The test checks the result, as the editor's own tests do: they `REQUIRE` it when a click must work and `CHECK_FALSE` it when the widget is disabled.
5. **No system state.** The harness has its own clipboard, so copy and paste never touch the person's clipboard, and the fake host reports no window, so no native dialog opens. A harness editor suggests a new temporary folder for project dialogs, never the person's projects folder.
6. **The scans keep empty lists of exceptions.** A scan that finds a fault fails the test. Nobody silences it by adding the file to a list: the code is fixed.

:::rule
Colors, sizes, panels, fonts and file changes follow the rules of the editor's UI code, and the `Editor.UI.Source` tests enforce them with lists of exceptions that stay empty. The reason is that a list of exceptions turns a rule into a suggestion, and the next person copies the exception. See [The editor's shell](../editor-ui/shell.md) for the panel registry these rules protect.
:::

## A toy version

Before the real code, a small model shows the idea. The toy has one button named `Save`. Like ImGui, it decides what is hovered from the frame before, applies queued input at the start of each frame, and lets a test find widgets by key. It counts a click only when a press lands on a widget that was hovered in the previous frame and the release comes while the pointer is still on it.

The fence below holds the whole program. Look at the three places that carry the lesson: `Frame`, which reads the previous frame's hover; `FindItem`, which returns a rectangle by key; and `ClickItem`, which uses three frames.

```cpp sketch="editor-ui-ui-testing-toy.cpp"
// A toy UI harness: one button that decides hovering from the previous frame, and a click over three frames.
#include <cstdio>
#include <map>
#include <string>

struct Rect
{
	float MinX = 0.0f;
	float MinY = 0.0f;
	float MaxX = 0.0f;
	float MaxY = 0.0f;
};

class MiniUI
{
public:
	// Input waits here and applies at the start of the next frame, as in ImGui's queue.
	void SetMouse(float x, float y, bool down)
	{
		m_NextX = x;
		m_NextY = y;
		m_NextDown = down;
	}

	void Frame()
	{
		const bool wasDown = m_Down;
		m_X = m_NextX;
		m_Y = m_NextY;
		m_Down = m_NextDown;
		const Rect button{ 10.0f, 10.0f, 110.0f, 40.0f };
		const bool inside = m_X >= button.MinX && m_X <= button.MaxX && m_Y >= button.MinY && m_Y <= button.MaxY;
		if (m_Down && !wasDown && m_Hovered)
			m_Pressed = true; // A press counts only on a widget hovered in the frame before
		if (!m_Down && wasDown && m_Pressed && inside)
			m_Clicks++; // A button acts on the release
		if (!m_Down)
			m_Pressed = false;
		m_Hovered = inside;
		m_Probe["Save"] = button;
		m_Frames++;
	}

	const Rect* FindItem(const std::string& key) const
	{
		const auto found = m_Probe.find(key);
		return found == m_Probe.end() ? nullptr : &found->second;
	}

	int GetClicks() const { return m_Clicks; }
	int GetFrames() const { return m_Frames; }

private:
	std::map<std::string, Rect> m_Probe;
	float m_NextX = 0.0f, m_NextY = 0.0f, m_X = 0.0f, m_Y = 0.0f;
	bool m_NextDown = false, m_Down = false, m_Hovered = false, m_Pressed = false;
	int m_Clicks = 0;
	int m_Frames = 0;
};

bool ClickItem(MiniUI& ui, const std::string& key)
{
	const Rect* item = ui.FindItem(key);
	if (!item)
		return false;
	const float x = (item->MinX + item->MaxX) * 0.5f;
	const float y = (item->MinY + item->MaxY) * 0.5f;
	ui.SetMouse(x, y, false);
	ui.Frame(); // Hover
	ui.SetMouse(x, y, true);
	ui.Frame(); // Press
	ui.SetMouse(x, y, false);
	ui.Frame(); // Release
	return true;
}

int main()
{
	MiniUI ui;
	ui.Frame();
	std::printf("missing key: %d\n", ClickItem(ui, "Open") ? 1 : 0);
	const bool found = ClickItem(ui, "Save");
	std::printf("Save found: %d, clicks: %d, frames: %d\n", found ? 1 : 0, ui.GetClicks(), ui.GetFrames());

	MiniUI hasty;
	hasty.Frame();
	hasty.SetMouse(60.0f, 25.0f, true); // Move and press together
	hasty.Frame();
	hasty.SetMouse(60.0f, 25.0f, false);
	hasty.Frame();
	std::printf("without a hover frame, clicks: %d\n", hasty.GetClicks());
	return 0;
}
```

```text output-of="editor-ui-ui-testing-toy.cpp"
missing key: 0
Save found: 1, clicks: 1, frames: 4
without a hover frame, clicks: 0
```

1. **Lines 18–23:** the queue holds the next mouse state, so input applies at the start of a frame.
2. **Line 34:** a press counts only on a button that was hovered in the frame before.
3. **Line 36:** the click happens on the release, while the pointer is still on the button.
4. **Line 39:** hovering is decided now, for the next frame to use.
5. **Lines 69–73:** the click is three frames: hover, press and release.

The program prints three lines. A key that does not exist gives false, and no input is sent. Clicking `Save` finds it, counts one click and runs four frames: one to record the button, then the three of the click. The hasty version, which moves and presses in one step, counts no click, because the button was not yet hovered when the press arrived. Real ImGui does the same, and the harness's `ClickItem` exists to spend the extra frame.

## The real code

### Clicking over three frames

The engine's `ClickItem` is the toy's function with the real probe. Read it for the order: find the widget, move, then three frames of the layer, each with one change of input.

```cpp src="StrataTests/src/Editor/ImGuiHarness.cpp#L143-L157" symbol="ImGuiHarness::ClickItem"
bool ImGuiHarness::ClickItem(std::string_view probeKey, Layer& layer)
{
	const std::optional<UI::ItemProbe::Item> item = UI::ItemProbe::Find(probeKey);
	if (!item || item->Duplicate || !item->Enabled)
		return false;
	// Hover first (ImGui decides what is hovered from the previous frame), then press and release: buttons act on the
	// release.
	MoveMouse(item->GetCenter());
	Frame(layer);
	SetMouseButton(ImGuiMouseButton_Left, true);
	Frame(layer);
	SetMouseButton(ImGuiMouseButton_Left, false);
	Frame(layer);
	return true;
}
```

1. **Line 145:** the lookup asks the probe for the widget drawn under the key in the latest frame.
2. **Lines 146–147:** a missing, duplicate or disabled widget gets no input at all.
3. **Lines 148–151:** the hover frame moves the mouse onto the center and runs one frame of the layer.
4. **Lines 152–153:** the press frame holds the left button down.
5. **Lines 154–155:** the release frame lets go, and the button's handler runs inside it.

The function refuses before it sends anything, so a failed click leaves ImGui untouched. Its three frames are the heart of the harness.

Frame one makes the button hovered, because ImGui learns what the mouse is over at the end of a frame and acts on it in the next. Frame two presses the left button, and ImGui makes the button the active item. Frame three releases it, and an ImGui button reports a click on that release, so the editor's handler runs inside this last frame. That is why a test may check the result right after `ClickItem` returns.

Each frame is `Frame(layer)`, which does what `Application` does for a layer: `OnUpdate`, then `OnImGuiRender` between ImGui's `NewFrame` and `Render`. After `Render`, the harness honors ImGui's texture requests, so the :term[font atlas]{id=glyph-atlas} becomes ready without a :term[renderer]{id=renderer}: it marks each requested texture as created with a dummy id.

Differences from the toy are small. The probe is a global table, not a member. The widget may be disabled, and then the click is refused. And the frame runs a real layer, whose own updates can change what is drawn next.

:::example[A worked test: pressing Play]
The editor's own test of the Play button shows the pattern with real numbers. It builds a `HarnessEditor` with a project, runs two frames so that every widget has drawn once and recorded itself, and checks that the game is not playing. It then runs `Click("Toolbar.Stop")` and checks that the call returns false, because **Stop** is drawn disabled while editing. Then it runs `Click("Toolbar.Play")` and checks that the scene state became `Play` and that the active scene is no longer the edit scene.

The click costs three frames, so `HarnessEditor::Click` adds 3 times 1/60 s, which is 0.05 s, to the fake host's clock, and 3 to its frame count. Everything that reads the host's time then sees the clock move as in the program. After one more frame, the test reads the probe with `Find("Toolbar.Play")` and sees `Enabled` false, because **Play** is disabled while a game runs. It then runs `Click("Toolbar.Pause")` and `Click("Toolbar.Stop")` and checks the state each time. The test never mentions a pixel: it mentions three keys.
:::

### The harness editor and the fake host

The fake host answers what `EditorLayer` asks of the application. Its state is a plain structure that the test shares. It holds the clock, the frame count, window focus, the display's :term[UI scale]{id=ui-scale}, the frame-rate limit, the window title, the :term[exit code]{id=exit-code} and the screenshot count. A test sets the clock or the scale and reads what the layer asked for. `HasWindow` and `HasGraphicsDevice` return false, so the layer opens no native dialogs, and the fake only describes a device for what the interface shows about it.

`HarnessEditor` wraps all of it. It creates the harness, a fake host, and an `EditorLayer` with automation and :term[file watchers]{id=file-watcher} off. It starts the project dialogs in a temporary folder and clears the log, as in a new editor process. Its helpers are the vocabulary of a test:

- `Frames(count)` advances the clock, the layer and the frame count together.
- `Click(key)` is the three-frame click, and `ClickAt(position)` is the same at a point.
- `ReplaceText(key, text)` clicks a text field of the kit, selects its text with **Ctrl+A** and types the new text.
- `FramesUntil(condition)` runs frames, with a short sleep for work on other threads, until a condition holds or ten seconds pass.
- `RunToCompletion(name)` runs a command and waits for deferred ones.

The state of the fake host moves with the frames, never with the real clock. A test that waits for work on another thread does it by a condition and a timeout, as the engine's test rules say, and never by counting frames.

### Rules a compiler cannot check

The editor's UI code follows rules that no type system sees. A color must come from a theme token, so the editor can change its theme. A pixel size must follow the font, so the interface scales on a high-resolution display. Each rule is a `TEST_CASE` in the suite `Editor.UI.Source`, in `EditorUISourceTests.cpp`. The suite introduces a new term.

A **source scan** is a test that reads source files as text and fails on a pattern that a rule forbids.

A scan first prepares the text. `StripComments` blanks out comments, and `BlankLiterals` blanks out the contents of strings and character literals, in both cases keeping line breaks, so reported line numbers stay true and prose that mentions `ImVec4(1, 0, 0, 1)` does not count. Each file keeps two forms: `Code` with the blanks, and `Text` as written. Rules search `Code`. Each scan names its own folders of `StrataEditor/src`: the colors and sizes read `Panels`, `UI` and `EditorLayer.cpp`, the panel rules read `Panels`, and the font and encoding rules read everything.

The suite holds these rules:

| Test case | What fails it |
| --- | --- |
| Colors come only from the theme | A literal color outside `UI/Theme.cpp`: `ImVec4` or `ImColor` built from numbers, packed colors such as `IM_COL32` or :term[hexadecimal]{id=hexadecimal}, and number lists passed to calls that take colors |
| Sizes scale with the font | A pixel size above 16 that does not follow the font, the style or the layout, found by judging the whole product the number is part of |
| Panels draw through the panel registry | A call of `ImGui::Begin` inside a panel: the registry begins and ends every panel's window |
| The editor never uses ImGui's built-in font | Any use of `AddFontDefault` in the editor's source |
| Text is encoded as :term[UTF-8]{id=utf-8} once | A pair of :term[bytes]{id=byte} that is a character encoded twice, which shows as a stray accented letter before a middle dot |
| Panels change files only through commands | A call that writes, moves, copies or removes a file from the panel code |

Look at the last rule's code. A panel never writes a file itself, because a command validates the request, records an :term[undo step]{id=undo-step} and is what automation agents use. The function below finds the calls that would break the rule.

```cpp src="StrataTests/src/Editor/EditorUISourceTests.cpp#L478-L485"
std::vector<std::string> FindFileSystemWrites(const SourceFile& file)
{
	static const std::regex write(R"(\b(FileSystem::(Write\w*|Remove|CreateDirector\w*|Rename|Copy\w*)|std::filesystem::(remove\w*|create_director\w*|rename|copy\w*))\s*\()");
	std::vector<std::string> findings;
	for (std::sregex_iterator it(file.Code.begin(), file.Code.end(), write), end; it != end; ++it)
		findings.push_back(Describe(file, static_cast<size_t>(it->position()), it->str()));
	return findings;
}
```

The pattern has two halves, one for `FileSystem` functions that write and one for the :term[standard library's]{id=standard-library}. It ends at an opening bracket, so only a call matches: the word `Remove` in a comment or a name has no effect. The loop returns one finding string per match, with the file and line, and the test case reports each with `FAIL_CHECK` and then checks that the list is empty. A finding tells the author what to do: run an `asset.*` command instead.

The size rule is the cleverest. A number such as `320.0f` is a fault in `ImVec2(320.0f, 280.0f)` but fine in `ImGui::GetFontSize() * 20.0f`. The scan therefore finds the term a number belongs to, the product around it, and accepts it when the term mentions the font, a style value or a layout size. It also follows names: a `const float buttonWidth = 200.0f;` that is used later as a size is a fault at its use. A value of 16 or less is allowed, since small gaps and borders need no scaling.

Most rules have a second test case, a self-test, whose name starts "The ... rule finds". The self-test feeds the rule short strings and counts the findings. The ways a fault can be spelled must be found, and the look-alikes that are fine must not be. Without a self-test, a rule whose pattern breaks would find nothing, and nobody would notice that the guard was gone.

The self-test of the file rule sits inside its own test case. It builds a source with six different write calls and checks that exactly six are found. It then builds another with reads and a commented-out call, and checks that none are found.

### Panels with huge data

A panel must stay cheap when its data is large. The Streaming panel lists every registered asset, and a project can hold tens of thousands. The suite `Perf.EditorPanels` measures that with the same harness, in `EditorPanelPerfTests.cpp`. It covers the Streaming panel with 10,000 assets, the Content Browser with 10,001 assets in one folder, and the Performance panel with a full ring of recorded frames, drawn live and paused. The test names say "a fraction of a millisecond per frame", and the budgets keep it so.

`MeasurePanel` is the measuring tool. It draws a panel for a number of frames and records the cost of each, timed inside the frame around `OnUpdate` and `OnImGuiRender`.

```cpp src="StrataTests/src/Editor/EditorPanelPerfTests.cpp#L56-L82" symbol="MeasurePanel"
// Draws a panel in a window of its own for a number of harness frames.
PanelFrames MeasurePanel(ImGuiHarness& harness, EditorPanel& panel, EditorPanelContext& context, uint32_t frames,
	const std::function<uint64_t()>& refreshes = {})
{
	PanelFrames result;
	result.All.reserve(frames);
	for (uint32_t frame = 0; frame < frames; frame++)
	{
		const uint64_t refreshesBefore = refreshes ? refreshes() : 0;
		double cost = 0.0;
		harness.Frame([&]()
		{
			ImGui::SetNextWindowPos(ImVec2(0.0f, 0.0f));
			ImGui::SetNextWindowSize(ImVec2(1200.0f, 800.0f));
			ImGui::Begin("Panel", nullptr, ImGuiWindowFlags_NoSavedSettings);
			const auto start = std::chrono::steady_clock::now();
			panel.OnUpdate(context);
			panel.OnImGuiRender(context);
			cost = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - start).count();
			ImGui::End();
		});
		result.All.push_back(cost);
		if (refreshes && refreshes() != refreshesBefore)
			result.Refreshes.push_back(cost);
	}
	return result;
}
```

1. **Line 64:** the refresh counter is read before the frame, to see whether the frame changed it.
2. **Lines 68–70:** every frame draws the panel in the same fixed window.
3. **Lines 71–74:** the clock runs only around the panel's update and drawing.
4. **Line 77:** every frame's cost joins the list of all frames.
5. **Lines 78–79:** a frame that refreshed the table also joins the list of refresh frames.

The timer wraps only the panel, not `NewFrame` or `Render`, so the number is the panel's cost and not ImGui's. The refresh counter, when the test passes one, labels the frames in which the panel rebuilt its table, so they are kept apart. Warm-up frames run first, 30 of them, so that the first-use work of fonts and caches does not count. The measured run is 240 frames, four seconds at the harness's 60 :term[frames per second]{id=frame-rate}.

Why the 95th percentile, and not the mean? A mean hides a rare slow frame, but a person sees the slow frame as a pause. Take the 240 sorted costs. The test uses the nearest-rank rule: 0.95 times 240 is 228, so the 95th percentile is the value at rank 228, and 12 frames rank above it.

A hitch in 12 frames or fewer cannot move this metric. The Streaming panel refreshes its table about four times per second of harness time: the :term[main thread]{id=main-thread} copies the residency data, and a job names, sorts and filters it. In four seconds that is up to 16 refresh frames, and the test requires at least 4. With only 4, all of them could hide above the percentile. So the test adds a second metric, the median of only the refresh frames, and checks both together.

```cpp src="StrataTests/src/Editor/EditorPanelPerfTests.cpp#L126-L138"
Perf::CheckBudgetsConfirmed({ "Perf.EditorPanels.Streaming10kAssetsP95", "Perf.EditorPanels.Streaming10kAssetsRefreshFrame" }, [&]
{
	const PanelFrames streamingFrames = MeasurePanel(harness, streaming, panelContext, c_MeasuredFrames, [&]() { return streaming.GetTableBuildCount(); });
	const Perf::Measurement streamingStats = Perf::Summarize(streamingFrames.All);
	// The table is read again four times per second of harness time, unless the previous build is still running.
	REQUIRE(streamingFrames.Refreshes.size() >= c_MeasuredFrames / 60);
	const Perf::Measurement refreshStats = Perf::Summarize(streamingFrames.Refreshes);
	MESSAGE("Streaming panel with ", c_RegisteredAssets, " assets: mean ", Mean(streamingFrames.All), " ms, median ", streamingStats.MedianMs, " ms, p95 ",
		streamingStats.P95Ms, " ms, max ", streamingStats.MaxMs, " ms per frame; ", streamingFrames.Refreshes.size(), " frames that refreshed the table: median ",
		refreshStats.MedianMs, " ms, max ", refreshStats.MaxMs, " ms");
	return Perf::MetricValues { { "Perf.EditorPanels.Streaming10kAssetsP95", streamingStats.P95Ms },
		{ "Perf.EditorPanels.Streaming10kAssetsRefreshFrame", refreshStats.MedianMs } };
});
```

1. **Line 126:** one check holds two metrics, so one measured run feeds both budgets.
2. **Line 128:** the run is 240 frames, and the counter marks the frames that refresh the table.
3. **Line 131:** the run must contain at least 4 refresh frames, or the second metric means nothing.
4. **Lines 136–137:** the 95th percentile of all frames and the median of the refresh frames are returned by name.

The check is `CheckBudgetsConfirmed`: when a metric is over its budget, the measurement runs again, and the test fails only if every attempt is over. A busy machine can slow one attempt, but a real regression slows them all. The `Perf.*` suites run in :term[optimized]{id=optimization} builds only, and a build that is not optimized fails these checks without measuring. The budgets themselves are not in the test but in `StrataTests/Perf/Budgets.json`, which the perf lab explains in [The perf lab](../engineering/perf-lab.md).

The panels have five metrics in the `Perf.EditorPanels` group of `StrataTests/Perf/Budgets.json`: `Performance600FramesP95`, `Performance600FramesPausedP95`, `ContentBrowser10kAssetsP95`, `Streaming10kAssetsP95` and `Streaming10kAssetsRefreshFrame`. One of them, the paused Performance panel, is provisional at the pin: its entry has a target and no measurement yet, so it has no budget to fail. The other four carry a measured value and a budget. The values stand in [Performance numbers](../reference/performance.md), not here.

A different kind of check guards the Hierarchy view. The test case "With 100,000 top-level entities, unchanged frames rebuild no rows", in `HierarchyViewTests.cpp`, creates 100,000 :term[root entities]{id=root-entity} and runs 1,000 more updates. It checks that the view's rebuild count is still 1. The check counts work, not milliseconds, so a slow machine never fails it. Where a rule can be stated as a count, a count is the better test.

### The suites of the area

The suites below pin the interface from different sides. All use the harness except the last two lines.

- `Editor.UI` holds the broadest cases: the buttons at the top, the status bar, the notifications, scaling and dialogs. They live in `EditorUITests.cpp` and `EditorObservatoryUITests.cpp`.
- `Editor.UI.Hierarchy`, `Editor.UI.Inspector` and `Editor.UI.AssetInspector` hold the cases of the panels that edit the scene and assets, mostly in `EditorAuthoringUITests.cpp`, with more in the animation, game UI and Graphics Quality test files.
- `Editor.HierarchyView`, `Editor.Notifications`, `Editor.UI.Notifications` and `Editor.UI.Text` pin the views and texts under the panels.
- Files for the launcher, the settings pages, the Graphics Quality page, the Content Browser and the activity panel each hold their own cases.
- `ImGui.Layer` and `ImGui.Platform` test the engine's ImGui layer and platform code, and `Editor.Theme` tests the theme tokens.
- `Editor.UI.Source` holds the scans, and `Perf.EditorPanels` the budgets above.

The case counts change from release to release, so look at a suite with `StrataTests.exe --test-suite=Editor.UI` or by listing test cases, never from a number in a document.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Screenshot comparison of the whole editor | Visual regression tools of many web and desktop products | It would catch clipped labels and color errors | A display and a GPU on every build machine, slow tests, and a failure for every font or driver change |
| Clicks by pixel coordinates in a real window | Simple :term[macro]{id=macro} recorders | Nothing to build | Tests that break when a layout moves |
| An accessibility tree of widgets | Libraries with accessibility support | Names for free, and checks that the interface is usable by screen readers | ImGui builds no such tree, so Strata would have to build and maintain one |
| A scripting hook inside the editor | Games with a debug console | One path for tests and agents | Tests would share state with the program, and a failure inside the hook would take the editor down |
| Checks by a tool that parses C++ | Large C++ code bases | Exact understanding of types and scopes | A build dependency on a :term[parser]{id=parser}, and rules that need a compile to run |
| Source scans as test cases | Strata | Rules run with the unit tests, need no extra tool and read like code | Patterns can be fooled, so each rule needs a self-test |

Strata's own choice is the cheapest that keeps the failure message useful. The scans are approximate by design: they search text, so a macro that builds a color from pieces escapes them. The self-tests cover the spellings that were seen, and a new way to break a rule gets a new example in the self-test.

## How it is tested

The harness is itself under test, and so are the rules that use it.

Run the area's suites with the doctest filter of the test program:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Editor.UI*
```

The command runs every suite whose name starts with `Editor.UI`, the scans included. Run the budgets in a Release build with `ctest --preset windows-release -L perf`, because a debug build fails them without measuring. The test program's shards and labels belong to [The test program](../engineering/test-program.md).

The cases that use the harness also pin its behavior. They cover a click that works, a click refused on a disabled widget, a hover count that shows an id conflict, and the :term[glyph]{id=glyph} counters. `CountFallbackGlyphs` counts :term[glyphs]{id=glyph} that a frame drew with a font's fallback character. A test calls it on a panel's window to prove that no icon is drawn in a font that lacks it. `GetHoveredItemIdCount` serves the id check: with conflict highlighting on, it counts the items submitted with the id of the item hovered a frame ago, and the answer is 1 unless two widgets share an id.

## Changing it safely

**Add a widget to the kit.** Record it in the probe under its id, with the kit's helpers, and use a fixed set of keys. Entries stay until `Clear`, so a key made from a growing counter would grow the table forever. Rows that are drawn every frame use `NumberedProbeKey`, which builds a key such as `Problems.Row.3` in place and allocates nothing.

**Add a test of a panel.** Build a `HarnessEditor`, run `Frames(2)` so the widgets record themselves, click by key, and check the state through the editor context, never through pixel positions. Wait by `FramesUntil` and a timeout. Put project files in `Tests::CreateTemporaryDirectory()` and copy samples with `Tests::CopySampleProject`. A step-by-step panel and test come in [Writing a panel and its test](../editor-ui/tutorial-panel.md).

**Add a scan rule.** Write a function that takes a `SourceFile` and returns finding strings with file and line. Add a test case that loads the sources, reports each finding with `FAIL_CHECK` and checks the list is empty. Add a self-test that counts what the rule finds and what it allows. Never add the offending file to a list of exceptions to make a rule pass.

**Change a budget.** A budget only goes down, and a commit that lowers one states the measured values. The perf lab page explains how.

Three rules of the engine's guide apply here.

:::rule
Everything ships with tests, and a regression test must fail without its fix. For a scan, that means the self-test has a case that the rule finds, and for a fix of a UI bug, a harness test that failed before. The reason is that a test that never failed proves nothing. See [Kinds of test](../engineering/test-kinds.md).
:::

:::rule
Panels take colors from theme tokens, sizes from the font and windows from the registry, and never write files themselves. The reason is that these rules keep the editor able to change its theme, to scale, to be driven by agents and to undo what a person did. See [The widget kit](../editor-ui/widget-kit.md).
:::

:::rule
Tests wait by the clock or a condition, never by a count of frames, and keep their files in a temporary folder. The reason is that frame counts change with the machine and a shared folder makes tests depend on each other. See [The test program](../engineering/test-program.md).
:::

Before a change to the harness or a scan merges, run `Editor.UI*` and then the whole test program, because a harness change can alter every test of the area.

## Summary

- A click in a UI test takes three frames: hover first, because ImGui decides hovering from the previous frame, then press, then release, because buttons act on the release.
- A test finds a widget by its probe key and clicks the center of its rectangle; `ClickItem` refuses a missing, duplicate or disabled widget.
- A source scan reads the code with comments and literals blanked out and fails on the pattern a rule forbids; the lists of exceptions stay empty and each rule has a self-test.
- A panel's perf test measures the cost per frame and reports the 95th percentile, and a second metric of the refresh frames catches the hitch that the percentile ignores.
- A new rule is a function that finds, a test case that reports, and a self-test that counts what is found and what is allowed.

## Check yourself

1. A test moves the mouse onto a button, presses the left button and releases it, all before running a frame, and then runs frames. How many clicks does ImGui see, and why?

   :::answer{tests="click-frames"}
   None. ImGui's queue spreads a press and a release of one button over two frames. The move and the press still apply in the same frame, so the press arrives on a button that was not hovered in the frame before. A press counts only on a widget that was hovered in the previous frame, and a button acts on the release after such a press. `ClickItem` spends one frame on the hover, one on the press and one on the release.
   :::

2. `ClickItem("Toolbar.Stop", layer)` returns false while the editor is not playing. What is wrong with the harness or the test?

   - A. The harness is broken, and the probe lost the entry.
   - B. The test must call `Frames` before every click.
   - C. Nothing is wrong: the button is drawn disabled, so the harness refuses the click.
   - D. The key is a duplicate, so the harness clicks the first widget.

   :::answer{tests="find-by-key"}
   C is right. The probe records the enabled state, and `ClickItem` returns false and sends no input for a disabled widget. A is wrong because the entry exists, with `Enabled` false. B is wrong because one drawn frame is enough to record the widget. D is wrong because a duplicate also returns false: the harness never guesses between two widgets.
   :::

3. A panel draws `ImGui::TextColored(ImVec4(0.9f, 0.2f, 0.2f, 1.0f), "Failed")`. Which scan fails, what must the author do, and may they add the panel's file to the scan's list?

   :::answer{tests="source-scan"}
   The scan "Colors come only from the theme" fails, because the color is built from numbers outside `UI/Theme.cpp`. The author takes the color from the theme, for example `UI::GetThemeColors().Error`. They may not add the file to a list of exceptions: the lists stay empty by rule, because an exception is copied by the next author and the rule fades.
   :::

4. A perf test draws a panel for 240 frames. Eleven of them take 3 ms and the others 0.05 ms. What is the 95th percentile, and can it see the 3 ms frames?

   :::answer{tests="panel-budget"}
   The rank is 0.95 times 240, rounded up, which is 228, so the value is the 228th smallest cost: 0.05 ms. The 11 slow frames hold ranks 230 to 240, above it. The percentile cannot see them, and a hitch of up to 12 frames hides. A metric of the refresh frames alone, such as the Streaming panel's median of refresh frames, would see them.
   :::

5. Why does `FindFileSystemWrites` search a copy of the source with comments and literals blanked out, and not the file as written?

   :::answer{tests="source-scan"}
   The rule must find calls, not words. A comment such as `// FileSystem::Remove(path)` or a string that quotes the call would otherwise produce a false finding, and line numbers must stay true, so the blanks keep the line breaks. The self-test checks that a commented-out call is not found.
   :::

6. A new scan rule finds nothing in the engine's code. What shows that the rule works, and not that it is broken?

   :::answer{tests="add-rule"}
   Its self-test shows it. The self-test feeds the rule strings that break the rule in every spelling known so far and checks that each is found, and feeds look-alikes that are fine and checks that none are found. A rule that finds nothing in the real code and nothing in the examples that should fail is broken, and only the self-test can tell the two cases apart.
   :::

## Exercises

1. **Basic.** Trace it yourself: find where a click on the Play button becomes three frames, and show where the probe lookup happens.

   :::answer[Worked solution]{tests="click-frames,find-by-key"}
   Open `StrataTests/src/Editor/ImGuiHarness.cpp` and set a breakpoint in `ImGuiHarness::ClickItem`, which the test reaches through `HarnessEditor::Click` in `StrataTests/src/Editor/HarnessEditor.h`. Run `StrataTests.exe --test-case="Clicking Play on the toolbar runs play.start, and Stop play.stop"` under a debugger. The first stop is the call `Click("Toolbar.Stop")`: the lookup returns an item whose `Enabled` is false and the function returns false. The second stop is the call `Click("Toolbar.Play")`. Step over the lookup, then over `MoveMouse`, and each `Frame(layer)` that follows is one of the three frames: hover, press, release.
   :::

2. **Medium.** Write a separate rule, with its self-test, that finds a fixed pixel width passed to `SetNextItemWidth`, and make it allow a width that follows the font and the fill width `-FLT_MIN`.

   :::answer[Worked solution]{tests="add-rule"}
   The rule is one :term[regular expression]{id=regular-expression}: the call, an opening bracket, optional space and a digit. A negative number or a call such as `ImGui::GetFontSize()` does not start with a digit, so both pass. The function counts matches, and the program checks four examples: a fixed width, a scaled one, the fill width and two calls in one text.

   ```cpp sketch="editor-ui-ui-testing-scan.cpp"
   // A source-scan rule with its self-test: no fixed pixel width given to SetNextItemWidth.
   #include <cstdio>
   #include <regex>
   #include <string>

   int CountFixedWidths(const std::string& code)
   {
   	static const std::regex fixedWidth(R"(\bSetNextItemWidth\s*\(\s*\d)");
   	int count = 0;
   	for (std::sregex_iterator it(code.begin(), code.end(), fixedWidth), end; it != end; ++it)
   		count++;
   	return count;
   }

   int main()
   {
   	std::printf("fixed: %d\n", CountFixedWidths("ImGui::SetNextItemWidth(120.0f);"));
   	std::printf("scaled: %d\n", CountFixedWidths("ImGui::SetNextItemWidth(ImGui::GetFontSize() * 8.0f);"));
   	std::printf("fill: %d\n", CountFixedWidths("ImGui::SetNextItemWidth(-FLT_MIN);"));
   	std::printf("two: %d\n", CountFixedWidths("SetNextItemWidth(4);\nSetNextItemWidth(9);"));
   	return 0;
   }
   ```

   ```text output-of="editor-ui-ui-testing-scan.cpp"
   fixed: 1
   scaled: 0
   fill: 0
   two: 2
   ```

   1. **Line 8:** the pattern is the call name, a bracket, optional space and a digit.
   2. **Lines 10–11:** every match adds one to the count.
   3. **Lines 17–20:** one fixed width, one scaled width, the fill width and two calls in one text.

   The output is 1, 0, 0 and 2. The engine's size rule is stricter: it judges the whole product a number belongs to, so `GetFontSize() * 8.0f` is fine and `GetFontSize() * 10.0f, 300.0f` is not, because the 300 stands alone. A rule meant for the engine needs that, and its own examples.
   :::

3. **Hard.** Plan a scan rule for the editor's source that fails on a panel that prints with `std::printf` or `std::cout`, because messages must go through the log. Say which functions, which test cases and which examples you write.

   :::answer[Worked solution]{tests="add-rule,source-scan"}
   Add `FindConsoleOutput(const SourceFile& file)` to `EditorUISourceTests.cpp`, next to `FindFileSystemWrites`. It searches `file.Code` with a pattern for `printf`, `puts`, `std::cout` and `std::cerr`, and returns one finding per match, built with `Describe`.

   Add a test case, "The editor writes no console output", that loads `LoadUISources()`, reports each finding with `FAIL_CHECK` and checks the list is empty. Add a self-test, "The console rule finds output however it is spelled". It counts two or three spellings as found. It counts a comment, a string that mentions `printf` and a log call such as `ST_INFO` as allowed.

   Run the new cases and fix every finding in the code, because the list of exceptions stays empty. If the rule found nothing, put one bad line in a panel and check that the test fails, then remove the line.
   :::

## Where it lives in Strata

- Harness and fake host: `StrataTests/src/Editor/ImGuiHarness.h`, `StrataTests/src/Editor/ImGuiHarness.cpp`.
- A real editor on the harness: `StrataTests/src/Editor/HarnessEditor.h`.
- The probe: `StrataEditor/src/UI/ItemProbe.h`, `StrataEditor/src/UI/ItemProbe.cpp`.
- Source scans: `StrataTests/src/Editor/EditorUISourceTests.cpp`, suite `Editor.UI.Source`.
- Panel budgets: `StrataTests/src/Editor/EditorPanelPerfTests.cpp`, suite `Perf.EditorPanels`, rows in `StrataTests/Perf/Budgets.json`.
- The idle Hierarchy view: `StrataTests/src/Editor/HierarchyViewTests.cpp`, suite `Editor.HierarchyView`.
- The test of the Play button: `StrataTests/src/Editor/EditorUITests.cpp`, suite `Editor.UI`.

## Further reading

- The ImGui project's documentation on its input queue and frame rules, in the `imgui.h` header of the pinned library: intermediate.
- Martin Fowler, "Test Pyramid": a short essay on why most tests should be fast and low-level: beginner.
- Kent Beck, "Test-Driven Development: By Example": the habit of seeing a test fail before it passes: beginner.
