---
id: engineering/testing
title: "Testing an engine"
description: "What a test is, which kinds an engine needs, why repeatable tests wait on conditions and not frames, and how to prove a regression test works."
kind: concept
size: M
tracks: [E]
needs: []
time: 45
learn:
  - id: pick-kind
    text: choose the kind of test a change needs and say why
  - id: stable-test
    text: write a test that waits on a condition or the clock and never fails by chance
  - id: regression-proof
    text: run a regression test without its fix and read why it fails
  - id: snapshot
    text: explain how a snapshot test finds a change that nobody meant to make
since: 0.3.0
status: final
---

A test passed on your machine. It fails on the macOS machine that checks every change, and it passes when you run it again. A month later a bug that you fixed comes back, and nobody notices for a week.

Both stories have one cause: the engine has checks that depend on luck or on a person's memory. This page shows how an engine turns checks into programs that run on every change and give the same answer each time.

## A check you run once protects nothing

The first answer is to run the program and look. You start the editor, move a cube and see that it moves. That works for the change you made a minute ago, and it fails for the next hundred changes. Nobody looks at every feature after every change, so a break stays hidden until a person happens to hit it.

The second answer is to write a check once: a small program that proves the bug is gone, run on the day you fixed it. That is better, but a check that nobody runs again protects nothing a week later.

A third answer fails in a quieter way. You write a test that starts some work and then waits 100 ms or five frames before it checks the result. On your fast desktop the work takes 30 ms, so the test passes. On a busy machine the work takes 150 ms, so the same test fails. A test like that is a coin toss, and a team that sees coin tosses stops believing its failures.

## A test is a small program that checks one claim

A **test** is a program that runs a piece of the engine, compares what happens with one claim, and fails loudly when they differ. A group of tests is a suite. The suite is worth as much as its answers can be trusted: given the same code, it gives the same answer on every machine, every time.

The suite runs on every change, so a break shows within minutes. The author of the break still remembers the change, and the fix costs little. The diagram shows the loop.

```mermaid caption="A change goes through the suite, and a failure returns to the author at once." alt="A flow from a change to the test suite, then to a result of pass or fail, with a failure returning to the author who made the change."
flowchart LR
    A["Change"] --> B["Test suite"]
    B -->|pass| C["Merged"]
    B -->|fail| D["Author fixes"]
    D --> A
```

The loop only works when a failure means a real break. If a test fails by luck, people run it again until it passes, and a real failure hides among the false ones. A **flaky test** is a test that sometimes passes and sometimes fails on the same code. It does more harm than no test at all, because it teaches the team to ignore red results.

## Kinds of test, each added for what the one before misses

The smallest kind is the unit test. It calls one function or class with chosen inputs and checks the output. It runs in microseconds and needs nothing else: no window, no files, no network. Its flaw is that every part can work alone while the parts together fail, for example when one part writes a file in a format another part cannot read.

The integration test joins several parts and checks that they agree: a loader with the asset registry, or the scene with the physics system. It is slower and finds the faults between parts. Its flaw is that it still runs inside the test program, so it cannot see what the real program does at start-up, with its :term[command line]{id=terminal-command}, its files and its windows.

An **end-to-end test** runs the real :term[executables]{id=executable}, as a user or a script would, and checks what they print or write. It finds faults that no smaller test can find. It is slow and has many ways to fail, so a team keeps few of them.

A **smoke test** is the cheapest of this kind: it checks that a program starts, does its basics and quits. The name comes from hardware, where the first test was to switch a new board on and see whether smoke came out.

Some claims are about a large body of output, such as every property of every component. A snapshot test, also called a golden-file test, keeps the expected output in a committed file and compares it with what the code makes now. When the output changes on purpose, a person writes the file again and reviews the difference. When it changes by accident, the test fails and shows where.

Strata has one such file: `StrataTests/Architecture/ComponentSchema.json` lists the components with their names, descriptions and properties, in order. The test `Reflection.ComponentSchema` compares each component of the file with the live registry; components added later are allowed. The helper mode `write-component-schema` of the test program writes the file again on purpose. The test also fails when a property or a component changes its place in the order.

A golden image is a snapshot of a picture. The :term[renderer]{id=renderer} draws a scene, and the test compares the pixels with a stored image. Its flaw is that different graphics drivers round differently, so the comparison needs a rule for how much difference counts. [Image comparison with the look-dev harness](look-dev.md) shows that rule.

A corruption sweep feeds a loader damaged copies of a valid file. For example, it changes one :term[byte]{id=byte} at each offset in turn. The loader must report an error each time and never crash. Fuzzing does the same with random damage, and both find inputs that nobody thought of. [The test program](test-program.md) shows Strata's sweeps.

A performance gate measures a time or a size and fails when it passes a budget. Speed is a claim like any other, and without a gate it falls slowly and unseen. [The performance lab](perf-lab.md) shows how Strata sets its budgets.

| Kind | Cost to run | What it catches | Complexity | Used by |
| --- | --- | --- | --- | --- |
| Unit | microseconds | wrong results of one function | low | every engine; Strata, Godot |
| Integration | milliseconds | parts that disagree | medium | every engine; Strata |
| End-to-end | seconds | faults of the real program | high | Strata; engines that run their editor in automation |
| Smoke | seconds | a program that does not start | low | every release process |
| Snapshot | milliseconds | output that changed without notice | low | Strata's component schema |
| Golden image | seconds, needs a :term[graphics processing unit]{id=gpu} (GPU) | drawing changes | high | rendering teams |
| Sweep and fuzzing | seconds to minutes | crashes on bad input | medium | Strata's loaders; browsers |
| Performance gate | seconds, needs a quiet machine | programs that became slower | high | Strata's perf tests |

## One timer test, three ways

The idea of a stable test shows best with numbers. Take a function that starts some work. The work finishes 30 ms after it starts on a desktop, and 150 ms after it starts on a busy continuous integration (CI) machine. Frames take 16 ms on the desktop, and 1 ms on a machine without a screen, which never waits for a display.

You write the check three ways. Way 1 sleeps 100 ms and then checks that the work is done. Way 2 lets five frames pass and then checks. Way 3 polls the condition every 5 ms and fails only when 5,000 ms have passed. The sketch simulates the clock, so the output never varies.

:::question
Does this code use C++ you have not met? Read [programming 1](../basics/programming-1.md), [programming 2](../basics/programming-2.md) and [programming 3](../basics/programming-3.md) first.
:::

The sketch below holds a machine with two numbers and the three ways. Look at how each way decides when to check.

```cpp sketch="engineering-testing-timer.cpp"
// A timer test written three ways, run on three machines. The clock is simulated so the output never varies.
#include <cstdio>

struct Machine
{
	const char* Name;
	int WorkMs;  // when the work under test finishes
	int FrameMs; // how long one frame takes
};

// Way 1: sleep 100 ms, then check.
static bool SleepThenCheck(const Machine& machine)
{
	const int now = 100;
	return now >= machine.WorkMs;
}

// Way 2: let five frames pass, then check.
static bool CountFrames(const Machine& machine)
{
	const int now = 5 * machine.FrameMs;
	return now >= machine.WorkMs;
}

// Way 3: poll every 5 ms until the work is done; the limit only ends a test that would hang.
static int WaitForCondition(const Machine& machine, int limitMs)
{
	for (int now = 0; now <= limitMs; now += 5)
	{
		if (now >= machine.WorkMs)
			return now;
	}
	return -1;
}

int main()
{
	const Machine machines[] = {
		{ "Desktop", 30, 16 },
		{ "Busy", 150, 16 },
		{ "Headless", 30, 1 },
	};

	std::printf("%-9s %-6s %-7s %s\n", "Machine", "Sleep", "Frames", "Condition");
	for (const Machine& machine : machines)
	{
		const int waited = WaitForCondition(machine, 5000);
		std::printf("%-9s %-6s %-7s %s after %d ms\n", machine.Name, SleepThenCheck(machine) ? "pass" : "FAIL",
			CountFrames(machine) ? "pass" : "FAIL", waited >= 0 ? "pass" : "FAIL", waited);
	}
	return 0;
}
```

```text output-of="engineering-testing-timer.cpp"
Machine   Sleep  Frames  Condition
Desktop   pass   pass    pass after 30 ms
Busy      FAIL   FAIL    pass after 150 ms
Headless  pass   FAIL    pass after 30 ms
```

1. **Line 14:** way 1 fixes the moment of the check at 100 ms, whatever the machine does.
2. **Line 21:** way 2 ties the moment to the :term[frame time]{id=frame-time}, which differs between machines.
3. **Lines 28–33:** way 3 asks the work itself every 5 ms, so its moment follows the machine.

Read the table by columns. Only the last column passes on every row, and the rows are the machines that differ.

:::example[Which way survives which machine]
Take the work time of each machine and compare it with the moment each way checks. On the desktop, way 1 checks at 100 ms and way 2 at 5 frames of 16 ms, which is 80 ms. Both come after 30 ms, so both pass.

On the busy machine, 100 ms and 80 ms both come before 150 ms, so ways 1 and 2 fail. On the headless machine, five frames take 5 ms, which comes before 30 ms, so way 2 fails there and only there. Way 3 checks when the work is done, so it passes on all three and waits 30, 150 and 30 ms.

The three ways pass or fail by the machine's speed and not by the code's correctness. Way 3 passes because it asks about the work and not about time. Its limit of 5,000 ms matters only when the work hangs, and then the failure arrives in five seconds and not never.
:::

## doctest and CTest run the tests

You wrote one test case in [your first engine change](../core/first-change.md). This section names the parts. **doctest** is the header-only C++ test framework that Strata uses; one header gives you the macros and a test program with a command line.

`TEST_SUITE("Core.StringUtils")` groups cases under a name, and Strata names a suite after its module. `TEST_CASE("...")` is one test; its text states the claim, as in "Letters become capitals". `CHECK(a == b)` records a failure and lets the case continue, so one run shows every wrong value. `REQUIRE(x)` stops the case at once, which suits a step that later lines depend on: a file that failed to open leaves nothing to check.

When a check fails, doctest prints both sides of the comparison. `INFO("text", value)` adds a message to the failures of its scope, and `CAPTURE(name)` adds the name and the value of a variable. A filter selects a part of the suite: `StrataTests.exe --test-suite=Core*` runs the suites whose names start with `Core`. Above the test program stands CTest, the runner of :term[CMake]{id=cmake}, which starts the program in several groups at once and reports one result per group.

A framework has one more feature that surprises people. Some code exists to make a test fail, such as the perf harness, whose job is to report a measurement over its budget. To test such code, mark the case with `doctest::expected_failures(1)`: the case passes only when exactly one check fails.

The quote shows one such case. The measurements 12, 13 and 11 are all over the budget of 10, so the checker must fail once.

```cpp src="StrataTests/src/Perf/PerfHarnessTests.cpp#L405-L410"
TEST_CASE("A confirmed check fails when every attempt is over the budget" * doctest::expected_failures(1))
{
	TestChecker test;
	ScriptedMeasurement measurement { "A", { 12.0, 13.0, 11.0 } };
	const std::vector<Tests::Perf::ConfirmedMetric> metrics = test.Checker.CheckConfirmed({ "A" }, std::ref(measurement));
	CHECK(measurement.Calls == Tests::Perf::c_ConfirmationAttempts);
```

Read two lines first: the marker on the first line, and the last line, which checks that the harness measured the full number of attempts. The case fails if the harness stops failing, so it protects the harness from a quiet change.

## Stable tests wait on conditions and never on frames

A test is stable when nothing it depends on changes between runs. Strata's rules for this come from one fact: the machine that runs the tests is not yours. A test must hold on every machine that CI runs it on, the slowest included, and the macOS runners have three :term[hardware threads]{id=hardware-thread}, so a test that works on twenty threads can fail there.

- Wait on a condition or the clock. `Tests::WaitUntil` polls a condition until it is true or a timeout passes, and the tests never wait for a count of frames or updates.
- Give each test its own folder. `Tests::CreateTemporaryDirectory()` makes one, so tests never write into the source tree or the user's files, and never open a sample in place.
- Do not depend on a program outside the build. Strata turns its own test binary into a helper child process when a test needs one, so no test needs a tool that the machine may lack.
- Do not change the environment of the test process for one child. A test starts the child with its own environment through a helper instead.
- Size the job pools of a test yourself. The application's defaults follow the hardware, and the hardware differs from machine to machine.

The first rule is Strata's own helper. Read how it decides when to stop.

```cpp src="StrataTests/src/TestHelpers.h#L62-L73" symbol="Tests::WaitUntil"
// Polls condition until it returns true or the timeout elapses; returns the final condition value.
inline bool WaitUntil(const std::function<bool()>& condition, std::chrono::milliseconds timeout = std::chrono::milliseconds(5000))
{
	const auto deadline = std::chrono::steady_clock::now() + timeout;
	while (std::chrono::steady_clock::now() < deadline)
	{
		if (condition())
			return true;
		std::this_thread::sleep_for(std::chrono::milliseconds(5));
	}
	return condition();
}
```

1. **Line 65:** the deadline comes from `steady_clock`, which never jumps backwards when a person changes the time of day.
2. **Line 66:** the loop asks the clock, not a count of frames, whether the time is over.
3. **Line 70:** the sleep of 5 ms keeps the test from using up a :term[processor core]{id=processor-core} while it waits.
4. **Line 72:** after the deadline the condition is asked one last time, so a condition that became true during the last sleep still counts.

Randomness needs the same care. A test that uses random numbers must use a fixed seed, so that a failure repeats. A test that races two threads must wait for the outcome and not hope that one thread is faster. See [threads](../basics/threads.md) for races and [time](../core/time.md) for the clock and the fixed step. The [job system](../core/jobs.md) explains why the pool size changes timing.

## A regression test must fail without its fix

A regression is a bug that returns after a fix. The cure is a regression test: when you fix a bug, you add a test that fails with the bug. A test that has never failed proves nothing, because you do not know that it can fail. It may check the wrong thing, or run no code at all.

Strata's rule is to prove that a new regression test fails when the fix is missing. The steps are short. Write the test, run it against the code that has the bug, and read the failure message. Then apply the fix and run again. The first run must be red for the reason you expect, and the second must be green.

If the test passes with the bug in place, the test is wrong. The usual causes are a check on the wrong variable, a case in a suite that does not run, and an input that never reaches the faulty line. You met the habit in the first-change tutorial, where you broke `ToUpper` on purpose and watched the test fail.

## Strata ships every change with tests

Golden rule 2 of Strata has four parts. New behavior gets unit tests, and a bug fix gets a regression test. All tests pass before a commit. No test is disabled, skipped or weakened to make it pass. [The contributing page](contributing.md) shows the rules of a change.

:::why[Why does Strata never weaken a test to get green?]
A failing test is information: either the code is wrong or the claim is. If a person loosens the check, deletes the case or skips it on one platform, the failure goes away and the cause stays. Each such step makes the suite a little less true, and a suite that is not true is a suite that nobody reads. The cost is that a change sometimes takes longer, because the test that fails must be understood before the change lands.
:::

Strata also does not measure line coverage, which is the share of code lines that a test run executes. A high share says the lines ran, not that anyone checked their results. Strata asks a different question: does something exercise every feature that is registered? The feature test answers it, by failing when a component, a setting or a script function goes unused. [The feature test page](feature-test.md) teaches that idea, which is coverage by construction.

Corruption sweeps are the other unusual part of Strata's suite. A normal run tries a fixed sample of byte offsets. A Release run of the fuzz label tries every offset, so that the claim "this loader never crashes on bad bytes" is checked and not hoped. [The test program page](test-program.md) shows how they run.

## What the suite cannot do

A suite shows that the claims it contains hold. It cannot show that no other fault exists. Strata labels GPU tests and package tests apart from the fast ones, because they need a graphics device or a :term[compiler]{id=compiler}; [the test kinds page](test-kinds.md) lists them. Perf tests run only in Release and :term[Dist]{id=dist} builds, CI skips them, and their budgets come from measurements on one reference machine.

Strata does not do some things at all: it has no line coverage report, and no tool that judges how good a test is. [What Strata does not do](../appendix/not-in-strata.md) lists such gaps. A person still has to ask whether the tests check the right claims.

## Common mistakes

- **A sleep followed by an assert.** Symptom: the test passes on your machine and fails on a busy one, or the reverse. Fix: wait on the condition with a clock limit, as in way 3 above.
- **A test that cannot fail.** Symptom: the test passed on the first run and no run ever failed. Fix: break the code on purpose and see the failure, then restore it.
- **A test that depends on a program outside the build.** Symptom: it passes on your machine and fails on a clean one that lacks the tool. Fix: use a helper mode of the test binary, or a file the test writes itself.
- **A test that reads or writes the user's files.** Symptom: it fails on a second run, or damages real data. Fix: use a temporary folder that the test makes and removes.
- **Weakening a test to get green.** Symptom: a check loses a case, a tolerance grows or a case is skipped. Fix: examine why it fails; the code or the claim is wrong.
- **Counting frames.** Symptom: the test fails on machines that draw faster or slower than yours. Fix: count time or wait on a condition.

## Summary

- Choose the kind of test by the claim. A unit test checks one function, an integration test parts that must agree, and an end-to-end or smoke test the real program. A snapshot covers large output, a sweep bad input and a gate speed.
- A stable test waits on a condition or a clock limit, uses its own folder and process state, and gives the same answer on the slowest machine.
- A regression test is proved by a run that fails without the fix and passes with it.
- A snapshot test compares output with a committed file, so a change that nobody meant to make appears as a failure, and a deliberate change rewrites the file.

## Check yourself

1. A test starts a job and calls `sleep` for 50 ms, then checks the result. It passes on a laptop and fails on CI. Which fix is right? The options are: (a) sleep 500 ms; (b) wait with `Tests::WaitUntil` until the result exists; (c) run the test twice; (d) skip the test on CI.

   :::answer{tests="stable-test"}
   Option (b). Option (a) only moves the coin toss to a slower machine and wastes time on a fast one. Option (c) hides the flaky test. Option (d) weakens the suite, which Strata's golden rule 2 forbids. Waiting on the condition passes as soon as the job ends, and its limit ends a hung job.
   :::

2. You fix a bug in a text parser and add a test. It passes at once. What do you do before the commit?

   :::answer{tests="regression-proof"}
   Run the test against the code without the fix. The test must fail there, for the reason you expect. If it passes, it checks the wrong thing or never reaches the faulty line, and it would not have caught the bug.
   :::

3. Which kind of test fits a change that renames a property of a component? Explain.

   :::answer{tests="pick-kind snapshot"}
   The snapshot test, `Reflection.ComponentSchema`. It compares every component's names and properties, in order, with the committed file, so the rename fails the test and shows where. If the rename is meant, someone writes the file again with the helper mode and reviews the difference.
   :::

4. A test using `expected_failures(1)` passes. What does that tell you?

   :::answer{tests="pick-kind"}
   Exactly one check failed in the case, as the author declared. It proves that code whose job is to fail, such as a budget check, still fails when it should. It does not mean that the code under test works for a normal input.
   :::

## Exercises

1. **Basic.** Open the `ToUpper` of [your first engine change](../core/first-change.md). Change `std::toupper` to `std::tolower`, build, and run the suite `Core.StringUtils`. Read the failure, then restore the line and run again.

   :::answer[Worked solution]{tests="regression-proof"}
   In `Strata/src/Strata/Core/StringUtils.h`, edit only `ToUpper`. The case in `StrataTests/src/Core/StringUtilsTests.cpp` then fails, and doctest prints each check with its two sides. Restore the call to `std::toupper` and run again; the summary reads `Status: SUCCESS!`. You have shown that the test can fail.
   :::

2. **Medium.** A test lets five frames pass and then checks that a job is done. Rewrite the wait to poll the condition every 5 ms with a limit of 1,000 ms, and report a failure message when the limit passes. Run it on a desktop, a busy machine, a headless machine and one whose work never ends.

   :::answer[Worked solution]{tests="stable-test" solution="sketches/engineering-testing-waituntil.cpp"}
   The function `WaitUntilDone` replaces the frame count. The first three machines pass after 30, 150 and 30 ms. The fourth, whose work never ends, fails after the limit with a message, and does not hang the suite. In Strata the same shape is `Tests::WaitUntil` inside a `CHECK`.

   ```cpp sketch="engineering-testing-waituntil.cpp"
   // Exercise solution: a frame-counting test rewritten to wait for its condition, with a limit.
   #include <cstdio>

   struct Machine
   {
   	const char* Name;
   	int WorkMs;  // when the work under test finishes; a huge value is work that never finishes
   	int FrameMs; // how long one frame takes
   };

   // Returns the milliseconds waited, or -1 when the limit passes first: the test then fails with a message.
   static int WaitUntilDone(const Machine& machine, int limitMs)
   {
   	for (int now = 0; now <= limitMs; now += 5)
   	{
   		if (now >= machine.WorkMs)
   			return now;
   	}
   	return -1;
   }

   int main()
   {
   	const Machine machines[] = {
   		{ "Desktop", 30, 16 },
   		{ "Busy", 150, 16 },
   		{ "Headless", 30, 1 },
   		{ "Hung", 1000000, 16 },
   	};

   	for (const Machine& machine : machines)
   	{
   		const int waited = WaitUntilDone(machine, 1000);
   		if (waited >= 0)
   			std::printf("%-9s pass after %d ms\n", machine.Name, waited);
   		else
   			std::printf("%-9s FAIL: not done within 1000 ms\n", machine.Name);
   	}
   	return 0;
   }
   ```

   ```text output-of="engineering-testing-waituntil.cpp"
   Desktop   pass after 30 ms
   Busy      pass after 150 ms
   Headless  pass after 30 ms
   Hung      FAIL: not done within 1000 ms
   ```

   1. **Lines 14–19:** the loop stops at the first moment the work is done, or returns -1 at the limit.
   2. **Line 28:** the work of the machine `Hung` never ends, as a test of a stuck job would.

   The last row never finishes, so only the limit ends its wait.
   :::

3. **Hard.** Name the kind of test that each of three changes needs, and say why. The changes are a parser of a text format, a fix of a :term[shader]{id=shader} that lit a mirrored mesh wrongly, and an editor command that creates an entity.

   :::answer[Worked solution]{tests="pick-kind"}
   The parser needs unit tests with chosen inputs, plus a corruption sweep, because bad text is the usual input of a parser. The shader needs a test that draws the scene on a GPU and compares pixels, the golden-image kind, with the broken case as its regression. The command needs an integration test that runs it against a scene and checks the entity and its undo step; a smoke or end-to-end test adds little here.
   :::

## Where it lives in Strata

- Tests: `StrataTests/src/Core/*Tests.cpp` and the folders beside it, grouped into suites named after the module, for example `Core.StringUtils`.
- The snapshot: `StrataTests/Architecture/ComponentSchema.json`, checked by the suite `Reflection.ComponentSchema`.
- Helpers: `StrataTests/src/TestHelpers.h` holds `Tests::WaitUntil` and `Tests::CreateTemporaryDirectory`.
- The test binary: `StrataTests/src/TestMain.cpp`, with the helper mode `write-component-schema`.
- Runner: `ctest --preset windows-debug -j 8`, and `StrataTests.exe --test-suite=Core*` for one group.

## Further reading

- doctest, the project's tutorial and reference on GitHub (github.com/doctest/doctest): the macros of this page; beginner to intermediate.
- CTest, the CMake documentation on testing (cmake.org): how a runner finds and labels tests; intermediate.
- Godot's contributor documentation on unit testing (docs.godotengine.org): another engine's use of doctest; intermediate.
- Software Engineering at Google, the chapters on testing (no link): flaky tests, test size and why teams delete them; intermediate.
