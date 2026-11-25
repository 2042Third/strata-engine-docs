---
id: editor-ui/status
title: "Status bar, toasts and idle throttling"
description: "How the editor tells you what happens without stopping you, and why it redraws slowly when nothing happens."
kind: internals
size: L
tracks: [E]
needs: [editor-ui/shell, core/profiling]
time: 80
learn:
  - id: pill-compact
    text: explain how the status bar chooses between full and compact pill texts, and why it keeps a margin
  - id: idle-cap
    text: predict which frame rate cap the editor picks from what it is doing
  - id: toast-queue
    text: explain how the notification model merges, replaces, expires and limits toasts
  - id: work-time
    text: explain why the frame pill shows work time and not the frame interval
  - id: add-pill
    text: add a status pill with a compact text, and make a panel that animates keep its frame rate
since: 0.3.0
status: final
---

An editor must tell you what happens: a build failed, a save is running, assets are loading. It must do that without taking the keyboard from the window you work in, and without spending the computer's power when nothing happens. This page teaches the two parts of the editor that do it. The first is the status bar along the bottom of the window with its pills, and the toasts that appear in a corner of the Scene view. The second is idle throttling, the rule that lowers the :term[frame rate]{id=frame-rate} while you do nothing.

The panels that the pills open ([instrument panels](instrument-panels.md)), the measuring of a frame ([profiling](../core/profiling.md)), the `editor.status` command and the recovery offer that a toast leads to ([recovery](../editor/recovery.md)) are other pages.

## The problem and how engines solve it

### Telling without interrupting

Picture a project that opens and imports 200 textures while you orbit the camera. Three imports fail. A program that shows a :term[modal]{id=modal} dialog for each failure stops you three times. Each dialog takes the keyboard focus, so a key you press for the camera lands in a dialog button. After the third click you have lost your place, and you still do not know whether the first failure matters.

Programs choose among three answers. A modal dialog is certain to be seen, but it stops the work, so it suits only a question that needs an answer before anything can continue. A log is silent and complete, but nobody reads it until something breaks. A third answer sits between them: a row of small indicators that always shows the state, and short messages that fade by themselves.

Strata takes the third answer and keeps the log. A pill is a small rounded label with an icon and a short text. The status bar holds one pill for each stream of work, and every pill leads somewhere: a click opens the panel that explains the number.

Failures that someone should hear about appear as toasts. A **toast** is a short message in the corner of the Scene view, also called a notification, that never takes the focus and leaves after a few seconds. Errors in the log count as not yet read until you view the Console, and the count shows in a pill.

The price of this choice is that a toast can be missed. A person who looks away for twelve seconds does not see it. That is why every toast that matters also leaves a trace: the log keeps the error, the activity journal keeps the command, and the buttons on the toast lead to both.

### Drawing only when needed

An immediate-mode user interface, the kind the editor uses, draws every widget again in every frame. At 60 frames per second one frame lasts 16.7 ms, so an editor left open all day with no input would still do 60 frames of work every second. The processor and the :term[graphics card]{id=gpu} stay warm, a laptop's fan turns, and the battery drains for a window that shows the same picture.

Engines meet the problem in three ways. An interface that keeps its widgets between frames can draw only the part that changed. A program can draw at a fixed low rate always, which is simple but makes every drag look slow. Or it can watch for activity, draw at the full rate while something happens and at a low rate when nothing does.

Strata takes the last way and calls it **idle throttling**: the editor lowers its frame rate once nothing has happened for a short time, and raises it again when something does. The default is 30 frames per second after half a second of quiet, and 10 when another window has the focus. At 30 frames per second a frame takes 33.3 ms, and 10 frames per second leaves 100 ms.

The cost is a delay. The first key you press after a quiet period arrives while the editor sleeps, so the editor answers up to one idle interval late. An animation that needs no input (a flash that outlines what an agent's command changed) would freeze unless it says that it needs frames. A run that someone waits for by counting frames would take longer, because each frame lasts longer. The rest of the page shows how Strata handles each of these.

## The map: who draws, who decides

The editor splits the work between a core that knows nothing about drawing and a user interface that draws it. `EditorNotifications` lives in the core, in `StrataEditor/src/Editor/EditorNotifications.h`, and holds the toasts that show now. `UI::DrawNotifications`, in `StrataEditor/src/UI/Notifications.cpp`, draws them. The status bar and the frame rate policy both belong to `EditorLayer`, in `StrataEditor/src/EditorLayer.cpp`, which runs once per frame on the :term[main thread]{id=main-thread}, the only thread that touches any of this.

```mermaid caption="Each frame the layer reads the editor's state to draw the pills and to pick a frame rate cap. Commands from the interface feed the notification model, which the interface draws as toasts." alt="A diagram. The layer's frame step feeds the status bar, the frame rate policy and the toast drawing. The status bar reads the editor state and opens panels on a click. The policy sets the cap on the host. The command runner feeds the notification model, which the toast drawing reads."
flowchart TD
	frame["EditorLayer: one frame"] --> bar["DrawStatusBar: the pills"]
	frame --> policy["UpdateFrameRate"]
	frame --> toasts["UI::DrawNotifications"]
	bar -->|"reads"| state["EditorContext, panels, automation server"]
	bar -->|"a click: Focus"| panels["panels"]
	policy -->|"SetMaxFrameRate"| host["EditorHost, then FramePacer"]
	runner["command runner, build and import events"] -->|"Post"| model["EditorNotifications"]
	model --> toasts
	toasts -->|"an action button"| shell["EditorShell"]
```

Every pill has a source of numbers and a target for its click. The table lists them in the order the bar draws them, from the left.

| Pill | What it shows | A click leads to |
| --- | --- | --- |
| Play state | Editing, Playing, Simulating or Paused, in the state's color | Nothing: the tooltip warns that changes made while the scene runs are discarded |
| Frame | The :term[frame work time]{id=work-time} in ms, frames per second, jobs in flight, and `idle` while throttled | The Performance panel |
| Assets | Assets ready and streaming, imports and scans, and the pool closest to its budget | The Streaming panel |
| Saving | The first running save with its progress, and how many wait | The Activity panel |
| Physics | Bodies of the running game that have no collision | The Streaming panel, physics part |
| Automation | The port and the clients, or why automation is off or failed | The Console, only when automation failed |
| Scripts | Building, crashed, build failed, loaded module, not built | Cancels a build, or opens the Problems panel, or starts a build |
| Input holds | Keys that a tool holds down in the running game | Releases them all |
| Errors | Errors logged since the Console was last viewed | The Console |

Each pill has a full text, and most also have a shorter compact text that they show when the window is too narrow for all the full texts.

Saving, Physics, Input holds and Errors appear only while they have news. The pills for the frame, the assets, the automation and the scripts are always there. The assets pill takes its color from its worst news. A failed asset makes it red (`Cinnabar` in the theme), a pool at 85 % of its budget or more makes it yellow (`Sulfur`), and a pool over its budget makes it red. The kit's `Pill` draws each one ([widget kit](widget-kit.md)).

::figure{id=status-bar variant=full}

::figure{id=status-bar variant=full crop=bar}

The automation pill reads from the server that agents connect to ([the automation server](../automation/rpc-server.md)). With no client it says the port and "no agent".

::figure{id=automation-pill variant=no-agent crop=pill-short}

With one client it says "Agent connected" and the name the client gave, such as `claude-code`.

::figure{id=automation-pill variant=named-agent crop=pill}

With several clients the pill counts them. Its tooltip lists each client with the time since it connected, and the number of pending and answered requests. The tooltip opens only under the pointer, so no picture here shows it.

## The contract

Four rules keep the page's two halves honest. Each has a reason that you can check against the code.

:::why
**Toasts never take focus and cost nothing while empty.** A toast that took the keyboard would steal keys from the Scene view in the middle of a camera move, which is the interruption the toast exists to avoid. The drawing function returns at its first line when the model is empty, so an editor with no news pays no frame cost for the feature.
:::

:::why
**The frame pill shows work time, not the frame interval.** An idle editor capped at 30 frames per second takes 33.3 ms per frame, but it works for 2 ms of them and sleeps the rest. If the pill showed the interval, an idle editor would read as a slow one. The work time is what a frame costs, and the page on frames teaches it as the frame work time ([the page on frames](../core/frame-loop.md)).
:::

:::why
**A panel that animates without input reports `IsAnimating`.** Throttling watches input, so a flash or a drag that moves without input would look like idleness, and the editor would draw it at 30 frames per second. A panel that returns true from `IsAnimating` while it is open keeps the editor at its full rate for as long as the animation lasts.
:::

:::why
**Work that someone waits for by counting frames is never capped.** A paused game that takes 600 steps through `play.step` or a command that waits for frames would take 20 seconds at a cap of 30 frames per second instead of a moment. The function `RunsUncapped` names the three cases: pending steps, pending commands and pending automation requests ([stepping](../editor/stepping.md)).
:::

The contract has a caller's side too. Code that wants to tell the person something posts a notification on the main thread and never opens a modal dialog for a routine failure. Code that draws a pill decides its compact text and builds any costly string once, not every frame.

## A toy version

Before the real code, a program that does the three jobs in about 80 lines. It decides full or compact texts with a margin, keeps a queue of toasts that merges repeats and holds at most four, and picks a :term[frame rate cap]{id=frame-rate-cap}. It is a toy: no window, no clock and no pills, only the decisions.

The program starts with the toast queue, whose `Post` either counts a repeat or adds a new toast and drops the oldest past four. Then `DecideCompact` takes the previous choice, the width of the full texts, the space available and the :term[font]{id=font} size, and returns the new choice. `ChooseCap` returns 0 for no cap. Look in `main` at the widths: the full texts take 700 pixels and the font is 16 pixels, so the margin is 32 pixels.

```cpp sketch="editor-ui-status-toy.cpp"
// A toy of the page's three ideas: compact pills with a margin, a toast queue that merges, and an idle cap.
#include <cstddef>
#include <cstdio>
#include <string>
#include <vector>

struct Toast
{
	std::string Title;
	int Count = 1;
};

class ToastQueue
{
public:
	static constexpr std::size_t c_MaxActive = 4;

	void Post(const std::string& title)
	{
		for (Toast& toast : m_Active)
		{
			if (toast.Title == title)
			{
				toast.Count++; // The same news again: one toast with a count
				return;
			}
		}
		m_Active.push_back({ title, 1 });
		if (m_Active.size() > c_MaxActive)
			m_Active.erase(m_Active.begin()); // Too many: the oldest goes
	}

	void Print() const
	{
		for (const Toast& toast : m_Active)
			std::printf("  %s x%d\n", toast.Title.c_str(), toast.Count);
	}

private:
	std::vector<Toast> m_Active;
};

// Compact once the full texts overflow; full again only with a margin of two font sizes to spare.
bool DecideCompact(bool compact, float fullWidth, float available, float fontSize)
{
	if (fullWidth > available)
		return true;
	if (fullWidth <= available - fontSize * 2.0f)
		return false;
	return compact;
}

// 0 means unlimited. Work someone waits for by frames is never capped.
int ChooseCap(bool uncapped, bool busy, bool focused)
{
	if (uncapped || busy)
		return 0;
	return focused ? 30 : 10;
}

int main()
{
	const float fullWidth = 700.0f;
	bool compact = false;
	for (const float available : { 800.0f, 690.0f, 720.0f, 740.0f })
	{
		compact = DecideCompact(compact, fullWidth, available, 16.0f);
		std::printf("available %.0f: %s\n", available, compact ? "compact" : "full");
	}

	ToastQueue queue;
	for (const char* title : { "a failed", "a failed", "b failed", "c failed", "d failed", "e failed" })
		queue.Post(title);
	std::printf("toasts:\n");
	queue.Print();

	std::printf("cap idle focused: %d\n", ChooseCap(false, false, true));
	std::printf("cap idle unfocused: %d\n", ChooseCap(false, false, false));
	std::printf("cap while stepping: %d\n", ChooseCap(true, false, true));
	return 0;
}
```

```text output-of="editor-ui-status-toy.cpp"
available 800: full
available 690: compact
available 720: compact
available 740: full
toasts:
  b failed x1
  c failed x1
  d failed x1
  e failed x1
cap idle focused: 30
cap idle unfocused: 10
cap while stepping: 0
```

1. **Lines 22–25:** a title that is already shown only raises its count, so a repeat never adds a card.
2. **Lines 28–30:** a new title joins the end, and the fifth one pushes the oldest out.
3. **Lines 46–50:** overflow gives compact, room with a margin gives full, and anything between keeps the old answer.
4. **Line 56:** work that someone waits for, or any busy state, gets no cap.

Walk through the output. At 800 the full texts fit. At 690 they overflow, so the bar goes compact.

At 720 they fit again (700 is at most 720), but the bar stays compact, because 720 minus the margin of 32 is 688 and 700 is above that. Only at 740 (708 or more) does it return to full. The toast queue counted the repeat of the first failure and dropped it when the fifth different one arrived. The idle editor gets 30 frames per second in front, 10 behind another window, and no cap while steps run.

## The real code, in the order data flows

### The status bar decides from the previous frame

Immediate-mode drawing has an ordering problem. The bar must know whether the full texts fit before it draws them, but their widths are known only after they are drawn. Strata solves it as the :term[chip strip]{id=chip-strip} does in the widget kit: it decides from what the previous frame measured. Each pill asks for its text through `StatusPillText`, which adds the width of the full text to a running total as a side effect and returns the full or the compact text.

At the start of the next frame the bar compares that total with the space available. Read the code for the three branches: too wide, wide enough with a margin, and in between.

```cpp src="StrataEditor/src/EditorLayer.cpp#L2172-L2177" from="const float available = ImGui::GetContentRegionAvail().x;" to="m_StatusBarFullWidth = 0.0f;" symbol="EditorLayer::DrawStatusBar"
const float available = ImGui::GetContentRegionAvail().x;
if (m_StatusBarFullWidth > available)
	m_StatusBarCompact = true;
else if (m_StatusBarFullWidth <= available - ImGui::GetFontSize() * c_StatusBarMarginFontSizes)
	m_StatusBarCompact = false;
m_StatusBarFullWidth = 0.0f;
```

The margin is `c_StatusBarMarginFontSizes`, two font sizes. The font is the bar's own, the caption size of the :term[type scale]{id=type-scale}: 12 pixels at a scale of 1 and 18 at 150 %. The margin scales with the font, so at 150 % it grows with the text, and it is the reason the bar does not flicker. Without it, a bar whose full texts take exactly the available width would switch to compact when one more character appeared, and back again when the character left, every other frame.

```mermaid caption="The bar switches to compact the moment the full texts overflow, and returns to full only when they fit with two font sizes to spare. In between it keeps what it had." alt="A line of available width with three zones. Below the full width, the bar is compact. From the full width up to the full width plus two font sizes, the bar keeps its current state. Above that, the bar is full."
flowchart LR
	low["available < full width: compact"] --> mid["between: keep the last state"] --> high["available >= full width + 2 font sizes: full"]
```

The function that collects the widths is short.

```cpp src="StrataEditor/src/EditorLayer.cpp#L2223-L2229" symbol="EditorLayer::StatusPillText"
std::string_view EditorLayer::StatusPillText(const char* icon, std::string_view text, std::string_view compact)
{
	if (m_StatusBarFullWidth > 0.0f)
		m_StatusBarFullWidth += ImGui::GetStyle().ItemSpacing.x;
	m_StatusBarFullWidth += UI::CalcPillWidth(icon, text);
	return m_StatusBarCompact && !compact.empty() ? compact : text;
}
```

An item spacing is added between two pills, but not before the first one. A pill that offers no compact text (the play state) shows its full text in both modes, but its width still counts.

:::example[A narrow window at 150 %]
The editor runs at a scale of 150 % and its status bar's font is 18 pixels high, so its margin is 36 pixels. The pills of a busy session need 1,540 pixels as full texts. The bar's content area is 1,560 pixels wide. The full texts fit (1,540 is below 1,560) but without the margin: 1,560 minus 36 is 1,524, and 1,540 is above it. A bar that was compact stays compact, and a bar that was full stays full, because only an overflow makes it compact.

Now a job starts and the assets pill grows by 80 pixels, so the full width becomes 1,620. That is above 1,560, so the next frame is compact. To return to full, the available space must reach 1,620 plus 36, or 1,656 pixels.
:::

Some pills build their texts with care, because the bar runs every frame. The automation pill rebuilds its texts only when the server's clients version or its port changes, and keeps the strings in members between frames. Tooltips are written only while they show, behind `UI::IsTooltipDue()`.

### The frame pill and the frame statistics

`UpdateFrameStats` runs once per frame. The host measures each frame after it ran, so what the editor reads is the previous frame's work time. The editor keeps the last 60 in a ring and averages them in milliseconds. The frames per second come from :term[ImGui's]{id=dear-imgui} own average.

The two numbers say different things: the rate shows the throttling, and the work time shows what a frame costs. Every panel receives them through the panel context, so a panel may show them without measuring anything.

:::example[Two ways to read an idle editor]
An editor that has been quiet for a second runs at 30 frames per second. Each frame does 2.0 ms of work and then the pacing code sleeps for 31.3 ms. The frame pill reads `2.0 ms · 30 FPS · 1 job · idle`, the last number being the frames per second. If the pill showed the interval, it would read 33.3 ms, twice the 16.7 ms of a 60-frame budget, and an engineer would chase a slow frame that does not exist. Press a key and the work time stays near 2.0 ms while the frame rate rises toward its active cap.
:::

### Idle throttling as a policy

Four preferences of the `Editor.FrameRate` section define the policy. **Idle after (seconds)** is 0.5 seconds. The idle frame rate is 30, the idle frame rate in the background is 10, and the active frame rate is unlimited. A value of 0 for **Idle after (seconds)** means the editor never idles. The rates are choices from a fixed list, and the lowest one offered is 5.

The floor of 5 has a reason in the pacing code. `FramePacer` sleeps until the next frame's time and does not wake when input arrives, so an idle editor answers the first input up to one idle interval late. The delay is 33 ms at 30 frames per second, 100 ms at 10 and 200 ms at 5, a fifth of a second. A lower rate would make the editor feel stuck.

Each frame the layer first reads input, then asks whether anything is busy. `TrackInput` notes the time of the last input: any event that ImGui processed, a held mouse button, or a held key. Held keys count so that a camera fly with the mouse at rest stays busy.

```cpp src="StrataEditor/src/EditorLayer.cpp#L1144-L1162" symbol="EditorLayer::IsBusy"
bool EditorLayer::IsBusy(double now) const
{
	if (now - m_LastInputTime < m_FrameRatePolicy.IdleAfterSeconds
		|| now - m_LastAutomationTime < std::max(c_AutomationActivitySeconds, m_FrameRatePolicy.IdleAfterSeconds))
	{
		return true;
	}
	if (m_Panels.IsAnyAnimating())
		return true;
	if (m_Context.IsPlaying())
	{
		if (!m_Context.IsPaused() || m_Context.GetActiveScene()->GetStepFrames() > 0)
			return true;
	}
	if (const EditorAssetManager* assets = m_Context.GetAssetManager(); assets && assets->GetStats().LoadingAssets > 0)
		return true;
	return m_CommandRunner.GetPendingCount() > 0 || m_Automation.GetPendingRequestCount() > 0 || m_Context.GetScriptBuilder().IsRunning()
		|| m_Context.GetViewport().IsPickPending();
}
```

1. **Lines 1146–1147:** two clocks, the last input and the last automation request, each compared with a delay.
2. **Line 1151:** the open panels are asked whether they animate.
3. **Lines 1153–1157:** a game that plays and is not paused, or that has steps left, is busy.
4. **Lines 1160–1161:** pending commands, requests, builds and picks keep the editor busy.

The function `IsBusy` lists what keeps the editor from idling. The first test is time: the last input came within the idle delay, or an automation request came within one second (or the idle delay, if that is longer). Then come the open panels that report animating, a game that plays and is not paused, or still has steps to run, and assets that load. The last line holds the pending work: commands, automation requests, a script build and a pick in the Scene view.

The three cases that lift the cap are in `RunsUncapped`, and `UpdateFrameRate` combines the two functions.

```cpp src="StrataEditor/src/EditorLayer.cpp#L1195-L1202" from="const bool uncapped = RunsUncapped();" to="m_Host->SetMaxFrameRate(cap);" symbol="EditorLayer::UpdateFrameRate"
const bool uncapped = RunsUncapped();
m_Idle = m_FrameRatePolicy.IdleAfterSeconds > 0.0 && !uncapped && !IsBusy(m_Host->GetTime());
uint32_t cap = 0;
if (m_Idle)
	cap = m_Host->IsWindowFocused() ? m_FrameRatePolicy.IdleFrameRate : m_FrameRatePolicy.UnfocusedIdleFrameRate;
else if (!uncapped)
	cap = m_FrameRatePolicy.ActiveFrameRate;
m_Host->SetMaxFrameRate(cap);
```

The code sets `m_Idle` first, then picks the cap from it. The diagram shows the same decision from the first question to the last.

```mermaid caption="The decision runs once per frame. Work that someone waits for removes the cap, busy work keeps the active rate, and only a quiet editor with the policy on drops to an idle rate." alt="A diagram. If throttling is off for this run, nothing changes. Otherwise, if pending steps, commands or requests exist, the cap is none. Otherwise, if the delay is zero or the editor is busy, the cap is the active rate. Otherwise the cap is the idle rate when the window is focused and the background rate when it is not."
flowchart TD
	start["each frame"] --> enabled{"throttling enabled for this run?"}
	enabled -->|"no: headless, frame limit, command script"| keep["leave the cap alone"]
	enabled -->|"yes"| uncapped{"pending steps, commands or requests?"}
	uncapped -->|"yes"| none["cap 0: unlimited"]
	uncapped -->|"no"| busy{"idle delay above 0 and nothing busy?"}
	busy -->|"no"| active["cap: the active rate"]
	busy -->|"yes"| focus{"window focused?"}
	focus -->|"yes"| idle["cap: the idle rate"]
	focus -->|"no"| background["cap: the background rate"]
```

Scripted runs, runs with a frame limit and headless runs skip all of this, because they measure in frames and slowing them would only make them last longer. A separate branch handles an idle delay of 0, so that a policy of "never idle" cannot leave the last idle cap in place. Setting a cap that is already set changes nothing, so the layer sets it every frame. `UpdateSteppingFrameRate` remembers the cap before steps begin, lifts it, and restores it when they end.

## Notifications

### The model in the core

A notification is a plain :term[struct]{id=struct}, `EditorNotification`: a level (Info, Success, Warning or Error), a title, a message, and optional leads. The leads are a journal entry, an asset, flags for the Console, the Problems panel and the recovery dialog. Each lead becomes a button. The model keeps at most four notifications, newest last.

Two notifications merge when they say the same thing. Posting an identical one (same level, title and message) while the first shows counts it: the count grows, the lifetime starts again, and the toast points at the latest journal entry. A **notification group** is a name that notifications share so that they merge although their texts differ: the shown toast holds the latest of them and the count adds up. Three imports that fail while a project opens become one toast that says three.

```cpp src="StrataEditor/src/Editor/EditorNotifications.cpp#L13-L48" symbol="EditorNotifications::Post"
uint64_t EditorNotifications::Post(EditorNotification notification)
{
	const auto now = std::chrono::steady_clock::now();
	m_Version++;
	notification.Count = std::max<uint32_t>(notification.Count, 1);
	const auto same = std::find_if(m_Active.begin(), m_Active.end(), [&notification](const EditorNotification& active)
	{
		if (!notification.Group.empty())
			return active.Group == notification.Group;
		return active.Group.empty() && active.Level == notification.Level && active.Title == notification.Title && active.Message == notification.Message;
	});
	if (same != m_Active.end())
	{
		// Again while it shows: counted, kept longer, and pointing at the latest journal entry. One of a group shows the
		// latest of it.
		EditorNotification merged = std::move(*same);
		m_Active.erase(same);
		const uint64_t id = merged.Id;
		const uint32_t count = merged.Count + notification.Count;
		if (!notification.Group.empty())
			merged = std::move(notification);
		else if (notification.JournalEntry != 0)
			merged.JournalEntry = notification.JournalEntry;
		merged.Id = id;
		merged.Count = count;
		merged.Expires = now + GetLifetime(merged.Level);
		m_Active.push_back(std::move(merged));
		return id;
	}
	notification.Id = m_NextId++;
	notification.Expires = now + GetLifetime(notification.Level);
	m_Active.push_back(std::move(notification));
	while (m_Active.size() > c_MaxActive)
		m_Active.pop_front();
	return m_Active.back().Id;
}
```

1. **Lines 20–22:** a notification of a group matches by group alone, and any other matches by level, title and message.
2. **Lines 28–35:** a group member replaces what shows, and a plain repeat only takes the latest journal entry.
3. **Lines 36–39:** the merged toast keeps its :term[id]{id=id}, adds the counts, restarts its lifetime and moves to the end.
4. **Lines 45–46:** past four, the oldest is dropped.

Lifetimes depend on the level: 5 seconds for Info and Success, 8 for Warning and 12 for Error. A fifth notification drops the oldest. `Replace` puts a new notification in the place of one with a given :term[id]{id=id}, such as "Building scripts" turning into "Scripts built". It keeps the id and the place and restarts the lifetime, and it posts the notification when the old one is gone.

`KeepAlive` extends a toast to at least 2 seconds from now, and the drawing calls it every frame the pointer rests on a toast. Every post, replacement and dismissal raises a version number, so a reader can learn that something changed without comparing lists.

```mermaid caption="A notification is posted or merged, shown, kept while the pointer rests on it, and then leaves when it is replaced, dismissed or expired. A fifth toast pushes out the oldest." alt="A state diagram. Post leads to Shown. Merging, hovering and replacing keep a toast shown. Dismissing, running out of time and a fifth toast each lead to Gone."
stateDiagram-v2
	[*] --> Shown: Post
	Shown --> Shown: merge (count + 1, lifetime restarts)
	Shown --> Shown: hover (at least 2 s more)
	Shown --> Shown: Replace (same id, same place)
	Shown --> Gone: Dismiss
	Shown --> Gone: lifetime ends
	Shown --> Gone: a fifth toast pushes it out
	Gone --> [*]
```

### What the person's commands post

The function `NotifyCommandOutcome` posts the end of a command that the person ran. It ignores a result that is still pending. A failure becomes an Error toast titled `<command> failed`, with the command's error as its message, unless the command was cancelled or announced. A success whose value holds a warning becomes a Warning toast. A plain success posts nothing, because success is the expected case.

```cpp src="StrataEditor/src/Editor/EditorNotifications.cpp#L109-L135" symbol="NotifyCommandOutcome"
void NotifyCommandOutcome(EditorNotifications& notifications, std::string_view command, const EditorCommandResult& result)
{
	if (result.IsPending())
		return;
	EditorNotification notification;
	notification.JournalEntry = result.JournalId;
	if (!result.Success)
	{
		if (result.ErrorKind == EditorCommandError::Cancelled || result.Announced)
			return;
		notification.Level = NotificationLevel::Error;
		notification.Title = fmt::format("{} failed", command);
		notification.Message = result.Error;
	}
	else if (result.Value.is_object() && result.Value.contains("warning") && result.Value["warning"].is_string())
	{
		notification.Level = NotificationLevel::Warning;
		notification.Title = std::string(command);
		notification.Message = result.Value["warning"].get<std::string>();
	}
	else
	{
		return;
	}
	notification.ShowConsole = true;
	notifications.Post(std::move(notification));
}
```

1. **Line 111:** a command that still runs has no outcome yet, so nothing is posted.
2. **Line 117:** a cancelled command and an announced failure stay silent.
3. **Lines 123–127:** a success with a warning text becomes a Warning toast.
4. **Line 133:** every toast of this kind offers the Console.

Only commands with the origin `CommandSource::UI` come through here, from the :term[command runner]{id=command-runner} and from the interface's actions ([commands](../editor/commands.md)). An agent has the answer in its reply and needs no toast. Take a command that waited for a script build, and the build failed. The build already posted "Script build failed" with Show Problems, so the command's result sets `Announced` and `NotifyCommandOutcome` stays silent.

### The drawing

`UI::DrawNotifications` runs last in the layer's frame, over everything, with the shown Scene view's rectangle (or the Game view's, or the work area above the status bar when neither shows). The rectangle comes from `GetShownWindowRect` of the panel registry, so a toast sits in the corner of the view that has the room: it covers neither the Inspector nor the Hierarchy.

```cpp src="StrataEditor/src/UI/Notifications.cpp#L81-L94" from="ImGui::SetNextWindowPos(ImVec2(areaMax.x" to="ImGui::BringWindowToDisplayFront(ImGui::GetCurrentWindow());" symbol="UI::DrawNotifications"
ImGui::SetNextWindowPos(ImVec2(areaMax.x - style.WindowPadding.x, areaMax.y - style.WindowPadding.y), ImGuiCond_Always, ImVec2(1.0f, 1.0f));
ImGui::SetNextWindowSizeConstraints(ImVec2(0.0f, 0.0f), ImVec2(areaMax.x - areaMin.x, areaMax.y - areaMin.y));
constexpr ImGuiWindowFlags flags = ImGuiWindowFlags_NoDecoration | ImGuiWindowFlags_AlwaysAutoResize | ImGuiWindowFlags_NoSavedSettings
	| ImGuiWindowFlags_NoFocusOnAppearing | ImGuiWindowFlags_NoNav | ImGuiWindowFlags_NoDocking | ImGuiWindowFlags_NoBackground
	| ImGuiWindowFlags_NoMove | ImGuiWindowFlags_NoBringToFrontOnFocus;
if (!ImGui::Begin("##Notifications", nullptr, flags))
{
	ImGui::End();
	return;
}
// In front of the panels without taking the focus (a focused window would take the keyboard from the game view), but not
// of a modal dialog: in the Scene view's corner they could cover its buttons, which it alone takes clicks on.
if (!ImGui::GetTopMostPopupModal())
	ImGui::BringWindowToDisplayFront(ImGui::GetCurrentWindow());
```

1. **Line 81:** the pivot (1, 1) anchors the window by its bottom right corner, a padding inside the area's corner.
2. **Lines 83–85:** the flags: no focus when it appears, no navigation, no docking, no saved settings, no moving.
3. **Lines 91–94:** the window comes to the front, unless a modal dialog is open.

All toasts share one window, and its flags are the contract in code. A window with no decoration, no navigation, no docking and no saved settings that does not take the focus when it appears leaves the keyboard where it was. It is brought to the front unless a modal dialog is open. Each toast is drawn as a card with a bar in its level's color, a title, a message cut at 280 :term[bytes]{id=byte}, and a row of links. A toast that stands for repeats adds its count beside the title, such as `x3`.

```cpp src="StrataEditor/src/UI/Notifications.cpp#L187-L200" from="if (hovered)" to="notifications.Dismiss(notification.Id);" symbol="UI::DrawNotifications"
if (hovered)
	notifications.KeepAlive(notification.Id);
if (showActivity)
	shell.ShowActivity(notification.JournalEntry);
if (showAsset)
	shell.ShowAsset(notification.Asset);
if (showProblems)
	shell.ShowPanel(problemsPanel);
if (showConsole)
	shell.ShowPanel(consolePanel);
if (recover)
	shell.ShowRecoveryDialog();
if (close || showActivity || showAsset || showProblems || showConsole || recover)
	notifications.Dismiss(notification.Id);
```

1. **Lines 187–188:** a pointer on the card keeps it alive.
2. **Lines 189–198:** each action runs after the card is drawn, through the shell.
3. **Lines 199–200:** the close button and every action dismiss the toast.

Five buttons exist. **Show in Activity** opens the command's journal entry and **Show Asset** reveals the asset. **Show Problems** and **Show in Console** open those panels, and **Recover...** opens the recovery dialog. A button acts on a copy of the notifications taken before the loop, because an action may dismiss toasts or open a panel, and both change the list the loop walks.

::figure{id=toasts}

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| A modal dialog for every failure | Small tools and installers | The person always sees it | The work stops, focus moves, and three failures cost three clicks |
| A log only | Servers and command-line tools | No interruption at all | Failures go unseen until the person looks |
| Waking the pacing code on input | Programs that wait for events | A lower idle floor with no late first input | Platform code in each window system that interrupts a sleep |
| A fixed low rate at all times | Simple tools | One rule and no idle detection | Every drag and every animation looks slow |
| Drawing only after an event | Interfaces that keep their widgets | Nearly no idle cost | The immediate-mode drawing that the editor's panels rely on |
| Showing the interval in the frame pill | Naive frame counters | One number for both ideas | An idle editor reads as slow |

## How it is tested

Two suites check the notifications. `Editor.Notifications` tests the model. Repeats merge, only four stay, and they end by level. `Replace` keeps the place, groups count, and commands of the person post their failures and warnings while others post none.

`Editor.UI.Notifications` runs the interface. A failing command shows a toast that leads to the Activity panel. Toasts sit at the bottom right of the Scene view, clear of the Inspector's buttons, and a long title stays clear of the close button.

The throttling and the pills live in the suite `Editor.UI`. One test checks that idle throttling lowers the frame rate only while nothing happens.

Others check three facts about the policy. Scripted and frame-limited editors ignore the preferences, and an idle delay of 0 never idles and lifts an idle cap at once. One test checks that the pills go compact at 150 % in a narrow window and return to full with room. Another checks that the :term[frame time]{id=frame-time} is what frames take, not the interval of the idle cap. Further tests cover the errors, automation, assets and scripts pills.

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Editor.Notifications
build/windows/bin/Debug/StrataTests.exe --test-suite=Editor.UI*
```

The first command runs the model. The second runs the pills, the throttling and the toast drawing of `Editor.UI.Notifications`, with the other interface suites.

## Changing it safely

To add a pill, add a function beside `DrawSavingPill` in `EditorLayer.cpp` and call it from `DrawStatusBar`. Give the pill a stable id, a full text, a compact text and a tooltip that is written only behind `UI::IsTooltipDue()`. Pass both texts through `StatusPillText`, because that call is what adds the pill's width to the total. Make its click focus a panel through `Focus`, and keep any text that costs work in a member that you rebuild when its inputs change.

To make a panel that animates keep its frame rate, override `IsAnimating` and return true from the clock or the state of the interaction, never from the last draw. The viewport shows the idea for its agent flash. It compares the time now with the flash's start, so a viewport that stops being drawn in mid-flash does not hold the editor at its full rate.

Four rules of the engine's developer guide govern this area. A panel draws state and calls commands, so a pill's click either focuses a panel or runs a command, and never edits a file. Commands never block a frame, so a pill that waits for something shows progress and does not stop the frame.

Interface code takes its colors from theme tokens, so a pill's color is `Info`, `Warning`, `Error` or `TextSecondary`, never a number. Tools count game time in :term[fixed steps]{id=fixed-step}, never in frames, so code that waits for a game uses the step count.

Before you commit, run `Editor.Notifications` and `Editor.UI*`, and open the editor in a window of 1,000 points at 150 % to see the compact bar.

## Summary

- The status bar decides between full and compact texts from the previous frame's widths, goes compact on overflow, and returns to full only with a margin of two font sizes.
- The editor picks its frame rate cap from what it does: none for pending steps, commands and requests, the active rate while busy, and the idle rates otherwise, with a floor of 5.
- The notification model holds at most four toasts, merges identical ones and groups, lasts 5, 8 or 12 seconds by level, and replaces a toast in place or keeps it while hovered.
- The frame pill shows the average work time of 60 frames, because the frame interval shows the cap and not the cost.
- A new pill goes through `StatusPillText` with a compact text, and a panel that moves without input reports `IsAnimating`.

## Check yourself

1. The full texts of the bar take 800 pixels, the font is 16 pixels, and the bar was compact. The available width goes 790, 820, 835. What does the bar show at each?

   :::answer{tests="pill-compact"}
   Compact, compact, full. At 790 the texts overflow, so the bar is compact. At 820 they fit, but 820 minus the margin of 32 is 788, and 800 is above 788, so the bar keeps its state. At 835, 835 minus 32 is 803, and 800 is at most 803, so it returns to full.
   :::

2. A person has stopped typing for 2 seconds with the editor focused, and a script build is running. Which cap does the editor pick: the idle rate of 30, or the active rate?

   :::answer{tests="idle-cap"}
   The active rate, which is unlimited by default, written as a cap of 0. A running script build makes `IsBusy` true, so the editor does not idle, and nothing pending makes `RunsUncapped` true, so the active cap applies. It does not pick 30.
   :::

3. Three imports of one project fail, with the same group name and different messages, and a fourth failure of another kind follows. How many toasts show, and what is the count of the first?

   :::answer{tests="toast-queue"}
   Two toasts show. The three imports merge into one of the group, with a count of 3 and the latest message. The fourth failure is a separate toast. A merge also restarts the lifetime of the grouped toast.
   :::

4. An editor idles at 30 frames per second. Each frame works 3 ms. Which does the frame pill show, and which is wrong: 3.0 ms, 33.3 ms, or 30 ms?

   :::answer{tests="work-time"}
   The pill shows 3.0 ms and 30 frames per second. The value 33.3 ms is the interval that the cap makes, which says nothing about cost; 30 ms is neither. The work time excludes the wait of the pacing code.
   :::

5. A panel shows a progress bar that fills over 4 seconds without any input. The editor drops it to 30 frames per second after half a second. What is missing?

   :::answer{tests="add-pill"}
   The panel does not override `IsAnimating`. Without it, `IsBusy` sees no input and no work, the editor idles, and the bar steps at 30 frames per second. Returning true while the bar fills keeps the full rate for those 4 seconds.
   :::

## Exercises

1. **Basic.** The font is 20 pixels and the full texts take 900 pixels. The bar starts full, and the available widths are 950, 880, 930 and 960. Give the state after each.

   :::answer[Worked solution]{tests="pill-compact"}
   The margin is 40 pixels. At 950: 900 fits and 900 is at most 910, so full. At 880: 900 is above 880, so compact. At 930: 900 fits, but 930 minus 40 is 890 and 900 is above it, so compact stays. At 960: 960 minus 40 is 920 and 900 is at most that, so full.
   :::

2. **Medium.** Write a program that gives an error toast a lifetime of 12 seconds. A hover keeps it for 2 seconds from now without shortening it. Print when an error posted at 0 s is gone if the person hovers at 5 s and at 11 s.

   :::answer[Worked solution]{tests="toast-queue" solution="sketches/editor-ui-status-expire.cpp"}
   The lifetime comes from a switch on the level. `KeepAlive` takes the larger of the old end time and now plus 2, as the model does.

   ```cpp sketch="editor-ui-status-expire.cpp"
   // A toast's lifetime by level, and what hovering does to it.
   #include <algorithm>
   #include <cstdio>

   enum class Level
   {
   	Info,
   	Warning,
   	Error
   };

   double GetLifetime(Level level)
   {
   	switch (level)
   	{
   		case Level::Info: return 5.0;
   		case Level::Warning: return 8.0;
   		case Level::Error: return 12.0;
   	}
   	return 5.0;
   }

   struct Toast
   {
   	Level Kind = Level::Info;
   	double Expires = 0.0;
   };

   // The person hovers the toast: it stays at least `extra` seconds from now, and never loses time it already had.
   void KeepAlive(Toast& toast, double now, double extra)
   {
   	toast.Expires = std::max(toast.Expires, now + extra);
   }

   int main()
   {
   	Toast toast { Level::Error, 0.0 };
   	toast.Expires = 0.0 + GetLifetime(toast.Kind);
   	std::printf("posted at 0 s, expires at %.1f s\n", toast.Expires);
   	KeepAlive(toast, 5.0, 2.0);
   	std::printf("hover at 5 s: expires at %.1f s\n", toast.Expires);
   	KeepAlive(toast, 11.0, 2.0);
   	std::printf("hover at 11 s: expires at %.1f s\n", toast.Expires);
   	for (const double now : { 12.5, 13.0 })
   		std::printf("at %.1f s the toast is %s\n", now, toast.Expires <= now ? "gone" : "shown");
   	return 0;
   }
   ```

   ```text output-of="editor-ui-status-expire.cpp"
   posted at 0 s, expires at 12.0 s
   hover at 5 s: expires at 12.0 s
   hover at 11 s: expires at 13.0 s
   at 12.5 s the toast is shown
   at 13.0 s the toast is gone
   ```

   1. **Lines 14–19:** the lifetime comes from the level.
   2. **Line 32:** the larger value means a hover never shortens a toast.
   3. **Lines 40–42:** the two hovers of the exercise.

   The first hover at 5 s changes nothing, because 7 is below 12. The second, at 11 s, moves the end to 13. At 12.5 s the toast still shows.
   :::

3. **Medium.** Trace it yourself: find what stops an idle editor from lowering its frame rate while a panel animates, and what lifts the cap while a game takes steps. Use a breakpoint or a search, and name the files and functions.

   :::answer[Worked solution]{tests="idle-cap"}
   Search for `IsAnimating` in `StrataEditor/src`. The registry's `EditorPanelRegistry::IsAnyAnimating`, in `StrataEditor/src/UI/EditorPanelRegistry.cpp`, asks every open panel, and `EditorLayer::IsBusy` in `StrataEditor/src/EditorLayer.cpp` calls it. In the same file `EditorLayer::RunsUncapped` returns true while `HasPendingSteps` holds, and `EditorLayer::UpdateFrameRate` then sets the cap to 0. A breakpoint in `IsBusy` shows which clause returns true, and `IsThrottlingEnabled` turns the policy off for a command-script run.
   :::

4. **Hard.** Plan a pill that counts the documents with changes not yet saved, with a compact text. Plan also the fix for a panel whose highlight fades over 600 ms. Name the functions you touch and the test you add.

   :::answer[Worked solution]{tests="add-pill"}
   Add `DrawUnsavedPill`, called from `DrawStatusBar` only when the count is above 0. Its full text is `3 documents not saved`, its compact text `3 not saved`, both through `StatusPillText`, with the tooltip behind `UI::IsTooltipDue()` and a click that focuses the Activity panel. For the fade, store the start time of the highlight and return true from `IsAnimating` while the clock is within 600 ms of it, as the viewport does for its flash. Add a test to `Editor.UI` that fills the bar in a narrow window and checks the compact text, and one that checks the cap is not lowered while the highlight lasts.
   :::

## Where it lives in Strata

- `StrataEditor/src/EditorLayer.cpp`: `DrawStatusBar`, `StatusPillText`, the pill functions, `TrackInput`, `IsBusy`, `RunsUncapped`, `UpdateFrameRate`, `UpdateSteppingFrameRate` and `UpdateFrameStats`.
- `StrataEditor/src/Editor/EditorFrameRate.h`: the `Editor.FrameRate` section, its defaults and the floor of 5.
- `StrataEditor/src/Editor/EditorNotifications.h` and `.cpp`: the model and `NotifyCommandOutcome`.
- `StrataEditor/src/UI/Notifications.cpp`: `UI::DrawNotifications`.
- `StrataEditor/src/UI/EditorPanelRegistry.h`: `IsAnimating` and `EditorFrameStats`.
- Tests: the suites `Editor.Notifications`, `Editor.UI.Notifications` and `Editor.UI`.
- Settings: **Preferences** in the editor, section `Editor.FrameRate`.

## Further reading

- The documentation of Dear ImGui, the immediate-mode library the editor uses: what a frame of immediate-mode drawing does (intermediate).
- Articles on notification design in desktop programs: when a message may interrupt and when it must not (beginner).
- Game programming texts on the frame loop and frame pacing: sleeping, vertical sync and timer resolution (intermediate).
