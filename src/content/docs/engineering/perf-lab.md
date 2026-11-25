---
id: engineering/perf-lab
title: "Measuring performance honestly: noise, percentiles, budgets and the perf lab"
description: "How Strata's performance tests turn noisy timings into a verdict: warm-up, medians, confirmed checks, budgets, ratchets and the tools around them."
kind: internals
size: L
tracks: [E]
needs: [engineering/test-kinds, core/profiling]
time: 80
learn:
  - id: noise-adds
    text: explain why one attempt within the budget decides a metric, and why a failure on a busy machine says nothing about the code
  - id: summarize
    text: compute the median and the nearest-rank 95th percentile of a list of timings by hand, as the lab does
  - id: budget-rules
    text: choose the entry of a new metric and decide when a budget may be lowered, kept or raised
  - id: read-run
    text: trace one printed perf line back to its measurement, its confirmed check and its budget entry
  - id: add-metric
    text: write a provisional metric and a confirmed check for it
since: 0.3.0
status: final
---

Strata's performance tests answer one question: did a change make the engine slower? The answer is hard to give, because a computer never runs the same code in exactly the same time twice. The **perf lab** is the set of tests, files and tools that turn timings into a verdict you can trust. It has a measuring library in `StrataTests/src/Perf/`, a file of limits and two Python tools.

You learn how a timing becomes a number, how a number becomes a pass or a fail, and why a slow result on a loaded machine proves nothing about the code. The page omits the catalogue of suites and budgets ([performance reference](../reference/performance.md)), measuring one frame ([measuring the frame](../core/profiling.md)), timestamps of the :term[graphics processing unit]{id=gpu} (GPU) ([GPU timing](../gpu/readback-timing.md)) and measuring a shipped game ([performance of a game](../make/performance.md)).

## The problem and how engines solve it

### Benchmarks and gates

You change a function and want to know whether the game got slower. A clock around one call gives one number, and the next call gives another. Two jobs hide in that question. A benchmark measures how fast something is and reports it.

A gate turns the measurement into a verdict, so that the test fails when the number is too big. Strata has both. The gate is what stops slower code at the commit, instead of weeks later when nobody remembers the change.

### Why one run lies

The first calls of a function are slow. Its code is not in the processor's cache yet, memory pages are not mapped and the processor may still run at a low speed. A measurement therefore starts with a warm-up: a few calls whose times are thrown away.

The timed calls differ from each other too, so the lab keeps all of them and reports statistics. The median is the middle value of the sorted list, and one slow call does not move it. The mean is pulled up by every slow call. The 95th percentile by nearest rank, which [measuring the frame](../core/profiling.md) taught, shows how bad the slow end is.

Take the twenty samples 1, 2, up to 20 ms. The median is the mean of the 10th and 11th samples, 10.5 ms. The nearest rank of the 95th percentile is $\lceil 0.95 \cdot 20 \rceil = 19$, so the percentile is the 19th sample, 19 ms. The lab checks medians, because the median of many calls ignores the few calls that the machine slowed.

### Noise only adds

Something else runs on your computer: the :term[operating system]{id=operating-system}, a browser, a virus scan, a :term[compiler]{id=compiler}. That work takes processor time and cache from the code you measure. It never gives the code free speed. A measurement is therefore the true cost of the code plus noise, and the noise is zero or more. The same holds for memory: a graphics driver that keeps memory makes a measurement larger, never smaller.

Two consequences follow. The smallest of several measurements is the closest to the truth. And one measurement within the limit proves that the code can meet the limit, whatever the other measurements say.

:::example[One metric, three machines]
Suppose a function costs 8.0 ms and its limit is 12.0 ms. On a quiet machine, three attempts measure 8.4, 8.1 and 8.9 ms. On a machine that compiles a program meanwhile, five attempts measure 14.2, 8.3, 13.1, 12.6 and 8.2 ms: three of them are over the limit, and the code is the same.

A check that fails when any attempt is over fails on the busy machine for nothing. A check that passes when any attempt is within passes on both machines. Now the code gets slower and costs 13.0 ms. Quiet or busy, every attempt measures 13.0 ms or more, so no attempt is ever within 12.0 ms and the check fails. "One attempt within" separates a busy machine from a regression.
:::

The method has a price. A check that passes on one good attempt cannot see code that gets slower but stays inside the limit: 8.0 ms rising to 11.5 ms is 44 % more and passes. That is why the limit sits close to the measurement, and why the rules below keep it from drifting up.

### Reference machines, budgets and the ratchet

Timings of two machines cannot be compared: a faster processor makes every number smaller. Strata therefore measures every limit on one machine, the **reference machine**: the machine whose measurements the limits come from. It has an Intel Core i7-13700K and an `NVIDIA GeForce RTX 5090`, runs Windows 11, and is quiet while it measures a Release build.

A **metric** is one named number that a perf test measures, with a unit. The metric `MoveRoot1M` of the suite `Perf.Scene` is the time to move the root of a scene of a million entities, in milliseconds.

A **budget** is the most a metric may measure: at most 1.5 times what the reference machine measured. The extra half absorbs small noise and the layout effects below. The canary metric below measured 10.0 ms and has a budget of 15.0 ms.

A **ratchet** is a rule that lets a value move in one direction only, like the tool of that name. A budget is lowered when a change makes the metric cheaper, in the same commit, so that the gain cannot be lost without a failing test. A metric over its budget is a regression to fix, never a reason to raise the budget.

### Differences that are not noise

Two builds of the same source can differ. The processor reads code through caches, and where a function lands in memory decides which :term[cache lines]{id=cache-line} it shares. In a test, two builds of one commit whose engine code lay 48 :term[bytes]{id=byte} apart measured the metrics of one :term[renderer]{id=renderer} suite on the central processing unit (CPU) between 0.93 and 1.07 of each other. That is a layout effect: a change of a few percent that no code change caused.

Processors with two kinds of cores add another. A hybrid processor has fast performance cores and slower efficiency cores, and the core that Windows picks for the :term[main thread]{id=main-thread} stays the same for the process. On the reference machine a frame of the editor takes 1.3 to 1.9 times longer on an efficiency core. Strata's programs and the test runner ask Windows not to move them to efficiency cores when their windows are covered (`Platform::DisableExecutionSpeedThrottling`).

Both effects are the reason for interleaved runs, which the real-code section explains: to compare two builds, you run them alternately on the same machine.

### The mistakes the lab is built against

- Raising a budget to make a test pass. The slower code stays, and the next change starts from a worse place.
- Trusting one run. One run holds the code's cost and the machine's noise together.
- Measuring on a busy machine, for example while a build runs.
- Taking numbers from a Debug build. Debug code is not what players run.
- Testing a complexity claim ("this is linear") with a clock. Count operations in an ordinary unit test instead, which gives the same answer on every machine.

## The map of the lab

The lab has three parts: tests that measure, files that decide and record, and tools that run the tests many times. The diagram shows how they connect.

```mermaid caption="The perf lab: perf tests read the budget file and write a results file, and two Python tools run the tests, read the results and keep measurements from overlapping." alt="A diagram of boxes and arrows. Perf tests use the measuring library, which reads the budget file and writes a results file. A stability tool runs the tests and reads both files. A lock tool wraps any command."
flowchart LR
  tests[Perf tests] --> lib[Measure and confirmed checks]
  lib --> budgets[(Budget file)]
  lib --> results[(Results file)]
  stability[Stability tool] -->|runs ctest| tests
  stability --> results
  stability --> budgets
  stability --> proposals[Proposed budgets]
  lock[Lock tool] -->|wraps a command| stability
```

The tests are three CTests (the test runner `ctest` from [the test program](../engineering/test-program.md)). `StrataTests.Perf` runs the suites named `Perf.*` on the CPU. `StrataTests.PerfGPU` runs `PerfGPU.*` on the graphics card, with the :term[validation layers]{id=validation-layer} off, because they would multiply the cost of every graphics call. `StrataTests.PerfGPU.Samples` measures the sample games and runs after the tests that export them (the GPU suites and exports of [test kinds](../engineering/test-kinds.md)).

All three exist in Release and :term[Dist]{id=dist} only, carry the label `perf` and run alone (`RUN_SERIAL`), because a test running beside them would take the processor's time. A setup test, `StrataTests.PerfResults.Clean`, deletes the results file first, so that a file holds one run.

## The contract

A perf test follows these rules. Each has a reason.

- Limits live only in `StrataTests/Perf/Budgets.json`, never in a test's code. A test whose metric has no entry fails before it measures anything, so no limit can hide in a :term[source file]{id=source-file}.
- A budget is at most 1.5 times the measurement. The file's :term[parser]{id=parser} rejects a larger one.
- A budget is lowered, never raised, for a cheaper metric. A commit that adds or lowers one states the measured values in its message, so that a reader can check the claim.
- A budget goes up in only two cases. The machine changed, and an interleaved A/B (two builds measured in turns, explained below) shows it against the build of the commit that set the budget. Or the project's owner accepted the cost by name, and the budget is re-baselined once.
- Lower is better in every metric. Write a rate as a cost per item, so that every comparison reads the same way.
- Perf tests measure the Medium quality preset unless the metric's name says another.
- Numbers come from :term[optimized]{id=optimization} builds only, on a graphics device without validation layers, and GPU work is submitted through `GPUContext::ExecuteAndWait`, which recycles the :term[command buffer]{id=command-list} as the engine does every frame.
- Memory peaks are measured in a fresh helper process, because the process's peak never shrinks.
- Measure with the Visual Studio :term[preset]{id=preset} the budgets were set with, `ctest --preset windows-release -L perf`, and never `windows-ninja`. MSVC (Microsoft's compiler) gets `/arch:AVX2` only under the Visual Studio generators, so a Ninja build compiles other engine code than the one the budgets measured.
- A failing run on a loaded machine proves nothing about the code: repeat it on a quiet machine and read the canary, a fixed workload whose time shows how fast the machine is now.

:::rule
The engine's guide fixes the limits of perf tests in one file, lets them fall but not rise, caps them at 1.5 times the measurement and asks every commit to state its numbers. The reason is that a gate whose limit moves with the test protects nothing. The kinds of test around these rules are in [test kinds](../engineering/test-kinds.md).
:::

:::why
**Trade-offs are measured on the reference machine, and the numbers are shown.** Strata could settle performance arguments by reasoning ("this should be faster"), and many teams do. Reasoning about caches, cores and drivers is wrong often enough that Strata decides by measurement: one machine, one build recipe, and every number in the commit message. The cost is that only that machine decides.

Hosted runners of continuous integration (CI) skip the label `perf`, so a slower change can pass CI. You must run `-L perf` on the reference machine before you merge a change that can affect speed. While the machine is away, new metrics wait as provisional entries, which hold a unit and no numbers yet.
:::

## A toy version of the lab

The toy below does the job of the lab in 60 lines. It pretends a workload of 8 ms with noise that only adds, a cold first call and a busy machine for the first two attempts. It warms up and summarizes with the median and the nearest-rank 95th percentile.

Then it runs a **confirmed check**: a check that measures a metric again while it is over its budget, and fails only when every attempt is over.

Before the code: `size_t` is an :term[unsigned integer]{id=unsigned-integer} type for counts, `std::vector` is a list that grows, and `uint32_t&` is a reference to a number, which lets the function change the caller's number. Search for the line that computes the rank, and for the loop in `main`, which stops at the first attempt within the budget.

```cpp sketch="engineering-perf-lab-toy.cpp"
#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <vector>

struct Summary
{
	double MedianMs = 0.0;
	double P95Ms = 0.0;
};

// The median, and the nearest-rank 95th percentile computed in integers so that no rounding moves it.
Summary Summarize(std::vector<double> samples)
{
	std::sort(samples.begin(), samples.end());
	const size_t count = samples.size();
	Summary summary;
	summary.MedianMs = count % 2 == 1 ? samples[count / 2] : (samples[count / 2 - 1] + samples[count / 2]) * 0.5;
	summary.P95Ms = samples[(count * 95 + 99) / 100 - 1];
	return summary;
}

// A pretend workload: 8 ms of work, noise from 0 to 1.5 ms that only ever adds, a cold first call and the time that
// other work on a busy machine takes.
double PretendCall(uint32_t& state, int call, double busyMs)
{
	state ^= state << 13;
	state ^= state >> 17;
	state ^= state << 5;
	const double noise = static_cast<double>(state % 1500) / 1000.0;
	return 8.0 + noise + (call == 0 ? 30.0 : 0.0) + busyMs;
}

// Calls the workload `warmup` times untimed, then `iterations` times, and summarizes the timed calls.
Summary Measure(uint32_t& state, double busyMs, int warmup, int iterations)
{
	std::vector<double> samples;
	for (int call = 0; call < warmup + iterations; call++)
	{
		const double milliseconds = PretendCall(state, call, busyMs);
		if (call >= warmup)
			samples.push_back(milliseconds);
	}
	return Summarize(samples);
}

int main()
{
	constexpr double c_BudgetMs = 12.0; // 1.5 times the 8 ms measured on the reference machine
	constexpr int c_Attempts = 3;
	const double busyMs[c_Attempts] = { 5.0, 5.0, 0.0 }; // The machine is busy for the first two attempts

	uint32_t state = 2463534242u;
	bool passed = false;
	for (int attempt = 1; attempt <= c_Attempts && !passed; attempt++)
	{
		const Summary summary = Measure(state, busyMs[attempt - 1], 1, 21);
		passed = summary.MedianMs <= c_BudgetMs;
		std::printf("attempt %d: median %.3f ms, p95 %.3f ms: %s\n", attempt, summary.MedianMs, summary.P95Ms,
			passed ? "within the budget" : "over the budget, measuring again");
	}
	std::puts(passed ? "the metric passed" : "the metric failed");
	return passed ? 0 : 1;
}
```

```text output-of="engineering-perf-lab-toy.cpp"
attempt 1: median 13.526 ms, p95 14.361 ms: over the budget, measuring again
attempt 2: median 13.720 ms, p95 14.468 ms: over the budget, measuring again
attempt 3: median 8.707 ms, p95 9.293 ms: within the budget
the metric passed
```

1. **Line 20:** the rank is computed in :term[integers]{id=integer}, so that no rounding moves it.
2. **Lines 31–32:** the noise only adds, the first call is cold and a busy machine adds more.
3. **Line 42:** calls before `warmup` run but are not kept.
4. **Line 56:** the loop stops at the first attempt within the budget.
5. **Line 59:** a value exactly at the budget is within it.

The first two attempts print medians of 13.5 and 13.7 ms: the busy machine adds 5 ms to code that costs about 8.7 ms. The check measures again instead of failing, and the third attempt, on the quiet machine, passes. The first call of every attempt is cold (30 ms more), and the warm-up keeps it out of the numbers. Set the warm-up to zero and that call joins the 21 samples with 38 ms or more: the median hardly moves, but the maximum and the mean do.

## The real code

The real library is `StrataTests/src/Perf/PerfUtils.cpp`. The toy differs from it in what it checks, how much and where it writes. The sections follow the flow of one measurement.

### Measuring and summarizing

`Summarize` turns the timings, in milliseconds, into a `Measurement`. Search for the line that computes the rank.

```cpp src="StrataTests/src/Perf/PerfUtils.cpp#L110-L119" from="std::vector<double> sorted(samplesMs.begin(), samplesMs.end());" to="measurement.P95Ms = sorted[rank - 1];" symbol="Summarize"
std::vector<double> sorted(samplesMs.begin(), samplesMs.end());
std::sort(sorted.begin(), sorted.end());
const size_t count = sorted.size();
measurement.Iterations = static_cast<uint32_t>(count);
measurement.MinMs = sorted.front();
measurement.MaxMs = sorted.back();
measurement.MedianMs = count % 2 == 1 ? sorted[count / 2] : (sorted[count / 2 - 1] + sorted[count / 2]) * 0.5;
// Nearest rank ceil(0.95 * count), in integers so that no rounding moves it.
const size_t rank = (count * 95 + 99) / 100;
measurement.P95Ms = sorted[rank - 1];
```

1. **Line 110:** the function sorts a copy, so the caller's list keeps its order.
2. **Line 116:** an even count takes the mean of the two middle samples.
3. **Lines 118–119:** the rank is computed in integers, and the percentile is the sample at that rank.

`Measure` runs the warm-up, times each call with `std::chrono::steady_clock` (a clock that never runs backward) and prints one line.

```cpp src="StrataTests/src/Perf/PerfUtils.cpp#L127-L145" from="for (uint32_t call = 0; call < warmup; call++)" to="return measurement;" symbol="Measure"
for (uint32_t call = 0; call < warmup; call++)
	function();

std::vector<double> samples;
samples.reserve(iterations);
for (uint32_t call = 0; call < iterations; call++)
{
	const auto start = std::chrono::steady_clock::now();
	function();
	const auto end = std::chrono::steady_clock::now();
	samples.push_back(std::chrono::duration<double, std::milli>(end - start).count());
}

const Measurement measurement = Summarize(samples);
std::printf("[perf] %.*s: median %.4f ms, p95 %.4f ms, min %.4f ms, max %.4f ms (%u iterations, %u warmup)\n",
	static_cast<int>(name.size()), name.data(), measurement.MedianMs, measurement.P95Ms, measurement.MinMs, measurement.MaxMs,
	measurement.Iterations, warmup);
std::fflush(stdout);
return measurement;
```

1. **Lines 127–128:** the warm-up calls run first, and nothing times them.
2. **Lines 134–136:** each timed call is bracketed by two readings of the clock.
3. **Lines 141–143:** the line that starts with `[perf]` is printed here, so you can find it by searching for that text.

The printed line starts with `[perf]`, the mark that every line of the lab carries, and holds the median, the 95th percentile, the minimum and the maximum. The rank is computed in :term[integers]{id=integer}: for 21 samples, $(21 \cdot 95 + 99) / 100 = 20$, so the 20th smallest sample is the percentile, and no floating-point rounding can move it to the 21st.

### The budget file

`Budgets.json` begins with a `_comment` that is the file's specification: the units (`ms`, `us`, `MB`, `count`, `ratio`), the reference machine, the 1.5 rule and the ratchet. After it, each key is `<Suite>.<Metric>`. The parser checks every entry when the first test reads the file. It rejects an unknown unit, a negative or infinite number and a budget above 1.5 times its measurement. The entry of the canary looks like this:

```json
"Perf.Harness.Sort200k": { "Measured": 10.0, "Budget": 15.0, "Unit": "ms" }
```

`Measured` is the value on the reference machine and `Budget` is its limit. An entry can also carry a `Target`. The budget is the gate, and the target is printed with every check. The parser refuses a target that is not below the budget, because the budget already enforces it.

A **target** is a goal below the budget that a metric has not reached on every run yet.

A **provisional** metric is one the reference machine has not measured. Its entry has a unit and no `Measured` or `Budget`, so its check measures and records it and never fails.

```json
"Perf.Jobs.WakeLatency": { "Unit": "us", "Provisional": true }
```

When the reference machine measures it, the entry gets its `Measured` and `Budget` and is no longer provisional. Numbers of other machines never go into an entry, because they would make the gate depend on whoever measured last.

### The confirmed check

`CheckConfirmed` takes the metrics' keys and a function that measures all of them. First it checks every key against the file, because a measurement can take minutes and an unknown key should fail before it, not after. Then it runs the attempts. The diagram shows one metric's life.

```mermaid caption="A confirmed check measures a metric, decides it at the first attempt within the budget, and measures again only while the metric is over and attempts remain." alt="A diagram of boxes and arrows. A measurement leads to the question whether the value is within the budget. If yes, the metric passes. If no, the question is whether attempts remain: if yes, the measurement repeats, and if no, the metric fails."
flowchart TD
  start[Attempt n] --> measure[Measure the metric]
  measure --> within{Within the budget?}
  within -->|yes| pass[Decided: pass, record the attempts]
  within -->|no| more{Attempts left?}
  more -->|yes| start
  more -->|no| fail[Fail, record the attempts]
```

In the code, look at how `undecided` counts the metrics that are still open.

```cpp src="StrataTests/src/Perf/PerfUtils.cpp#L315-L351" from="size_t undecided = metrics.size();" to="undecided--;" symbol="BudgetChecker::CheckConfirmed"
size_t undecided = metrics.size();
for (uint32_t attempt = 1; attempt <= attempts && undecided > 0; attempt++)
{
	const MetricValues values = measure();
	bool reportedKeys = values.size() == keys.size();
	for (const std::string& key : keys)
		reportedKeys = reportedKeys && values.contains(key);
	if (!reportedKeys)
	{
		std::string reported;
		for (const auto& [key, value] : values)
			reported += fmt::format("{}'{}'", reported.empty() ? "" : ", ", key);
		std::string listed;
		for (const std::string& key : keys)
			listed += fmt::format("{}'{}'", listed.empty() ? "" : ", ", key);
		FAIL(fmt::format("the measurement reported the metrics {} instead of {}", reported.empty() ? "none" : reported, listed));
	}

	for (ConfirmedMetric& metric : metrics)
	{
		if (metric.Passed)
			continue;
		const double value = values.find(metric.Key)->second;
		REQUIRE_MESSAGE(std::isfinite(value), fmt::format("'{}' measured a value that is not finite", metric.Key));
		metric.Attempts.push_back(value);
		metric.Passed = metric.Entry.Provisional || value <= metric.Entry.Budget;

		std::string line = fmt::format("{}: {}", metric.Key, DescribeValue(value, metric.Entry));
		if (metric.Passed && attempt > 1)
			line += fmt::format(": within the budget in attempt {} of {}", attempt, attempts);
		else if (!metric.Passed && attempt < attempts)
			line += fmt::format(": over the budget in attempt {} of {}, measuring again", attempt, attempts);
		else if (!metric.Passed)
			line += fmt::format(": over the budget in all {} attempts", attempts);
		Print(line);
		if (metric.Passed)
			undecided--;
```

1. **Line 316:** the loop ends when no metric is open or the attempts run out.
2. **Line 318:** the measuring function runs again for every attempt, for all keys together.
3. **Line 340:** a provisional metric passes at once, and any other needs a value within its budget.
4. **Lines 343–348:** the text that tells you which of the three cases happened.
5. **Line 351:** a passed metric leaves the open count, and its later values do not count.

Metrics measured together are measured together again, because one function produces them all. The function runs from the start. The new values of the metrics that already passed do not count, so a decided metric is never replaced by a worse one. A provisional metric counts as passed at once.

After the loop, each metric stores its deciding value: the passing attempt, or the smallest attempt if none passed. The last check reports the failure.

```cpp src="StrataTests/src/Perf/PerfUtils.cpp#L357-L367" from="metric.Value = metric.Passed" to="metric.Entry.Budget, metric.Entry.Unit));" symbol="BudgetChecker::CheckConfirmed"
metric.Value = metric.Passed ? metric.Attempts.back() : *std::min_element(metric.Attempts.begin(), metric.Attempts.end());
Result result;
result.Value = metric.Value;
result.Unit = metric.Entry.Unit;
result.Budget = metric.Entry.Budget;
result.Target = metric.Entry.Target;
result.Attempts = metric.Attempts;
result.Provisional = metric.Entry.Provisional;
Store(metric.Key, std::move(result));
CHECK_MESSAGE(metric.Passed, fmt::format("'{}' measured {} in {} attempts, each over its budget of {} {}", metric.Key,
	JoinValues(metric.Attempts, metric.Entry.Unit), metric.Attempts.size(), metric.Entry.Budget, metric.Entry.Unit));
```

1. **Line 357:** the deciding value is the passing attempt, else the smallest.
2. **Line 365:** the result goes into the results file with its attempts.
3. **Lines 366–367:** the test fails here, with every attempt in its message.

The default is `c_ConfirmationAttempts`, 3 attempts in all, the first included. Each attempt prints a line that starts with `[perf]`, the metric's key, the value with its unit and the share of the budget it uses. A metric that is over the budget but has attempts left adds "measuring again". A metric that passes after the first attempt adds the number of the attempt, and one that fails in the last attempt says that all attempts were over.

### The results file

Every check calls `Store`, which merges the metric into `build/<preset>/PerfResults/<config>.json`. An entry holds `Value`, `Unit`, `Budget` (or `Provisional`), the `Target` and every attempt. The deciding `Value` is the passing attempt, or the smallest attempt when none passed.

The file replaces the old one in one step, so a reader never sees half a file. It holds nothing that belongs to one run alone, such as a time or a machine's name, and its keys are sorted. Two runs therefore compare with a :term[diff]{id=diff}.

### The canary

A **canary** is a fixed workload whose time tells you about the machine, not about the code, like the bird that miners once carried. The canary of the lab is the metric `Sort200k` of the suite `Perf.Harness`: the median of 31 sorts of 200,000 fixed numbers. Its reference measurement is 10.0 ms. Search for the lines that make the numbers the same on every machine.

```cpp src="StrataTests/src/Perf/PerfHarnessTests.cpp#L512-L543"
TEST_CASE("The sort canary stays within its budget and is recorded with its attempts")
{
	constexpr size_t c_Count = 200'000;
	std::vector<uint32_t> input(c_Count);
	uint32_t state = 0x9E3779B9u; // xorshift32: the same values on every machine
	for (uint32_t& value : input)
	{
		state ^= state << 13;
		state ^= state >> 17;
		state ^= state << 5;
		value = state;
	}

	// The median of 31 sorts: a few sorts slowed down by the machine's other work do not move it.
	std::vector<uint32_t> values;
	const Tests::Perf::ConfirmedMetric canary = Tests::Perf::CheckBudgetConfirmed(c_CanaryMetric, [&]
	{
		return Tests::Perf::Measure(c_CanaryMetric, 3, 31, [&]
		{
			values = input;
			std::sort(values.begin(), values.end());
		}).MedianMs;
	});
	CHECK(std::is_sorted(values.begin(), values.end()));

	// The check recorded the metric with the unit and budget of its entry and every attempt.
	const std::optional<Tests::Perf::BudgetEntry> budget = Tests::Perf::FindBudget(c_CanaryMetric);
	REQUIRE(budget.has_value());
	const std::optional<nlohmann::json> recorded = ReadResultEntry(Tests::Perf::GetResultsFile(), c_CanaryMetric);
	REQUIRE(recorded.has_value());
	CHECK(IsResultEntry(*recorded, canary.Value, "ms", budget->Budget, canary.Attempts));
}
```

1. **Line 516:** a fixed starting number and a fixed generator give the same input on every machine.
2. **Line 525:** the median of many sorts ignores a few slowed ones.
3. **Lines 527–534:** the canary is itself a confirmed check, with three sorts of warm-up and 31 timed ones.
4. **Lines 538–542:** the test reads the results file back and compares the record with the check.

If the canary measures 14 ms on a machine where it measured 10 ms, the machine is slow now: throttled, hot or crowded, and you cannot trust the other metrics. The canary uses one thread, so load on many cores usually leaves it unchanged, and a run that failed from such load shows a normal canary.

### The stability tool

`Tools/PerfStability.py` runs `ctest --preset <preset> -L perf` several times. Per metric, it reports the smallest, middle and largest value, the pass rate and how often the metric needed more than one attempt. Per run, it reports how busy the machine was and the canary against its reference. The option `--wait-quiet` delays each run until the machine is quiet.

With `--propose-budgets`, the tool writes a proposed `Budgets.json` from kept runs, under the ratchet. Its function `classify` decides per metric. In this Python, spaces at the start of a line mark a block where C++ has braces, and `return a, b` gives back two values at once. Also `entry.get("Target")` reads a key of a dictionary (a map) and gives `None` when the key is missing.

```python src="Tools/PerfStability.py#L348-L390"
def classify(key, entry, values, rebaselines):
    """The class of a metric and its proposed entry (None: unchanged), by the rules in the module's description."""
    unit = entry.get("Unit")
    if len(values) < 3:
        return "not recorded", None
    median = statistics.median(values)
    if unit == "count" and len(set(values)) == 1:
        if not entry.get("Provisional") and entry.get("Measured") == values[0] and entry.get("Budget") == values[0]:
            return "same", None
        return "count", {"Measured": values[0], "Budget": values[0], "Unit": unit}
    # A failure confirmed in every attempt is decided by the guide's procedure, however much the metric spreads.
    if not entry.get("Provisional") and any(value > entry["Budget"] for value in values) and key not in rebaselines:
        return "over budget", None
    spread = (max(values) - min(values)) / median if median > 0 else 0.0
    if unit != "count" and spread > 0.25 and key not in rebaselines:
        return "unstable", None
    measured = significant(median, decimal.ROUND_HALF_EVEN)
    # 1.5 times the rounded measurement, rounded down, so the parser's limit holds for the numbers written.
    ceiling = significant(1.5 * measured, decimal.ROUND_FLOOR)
    target = entry.get("Target")
    if entry.get("Provisional"):
        proposed = {"Measured": measured, "Budget": ceiling, "Unit": unit}
        if target is not None:
            if all(value <= target for value in values):
                proposed["Budget"] = min(ceiling, target)
            elif target < ceiling:
                proposed["Target"] = target
        return "provisional", proposed
    budget = entry["Budget"]
    if key in rebaselines:
        proposed = {"Measured": measured, "Budget": ceiling, "Unit": unit}
        if target is not None and target < ceiling:
            proposed["Target"] = target
        return "over budget, re-baselined", proposed
    if median < 0.9 * entry["Measured"]:
        proposed = {"Measured": measured, "Budget": min(budget, ceiling), "Unit": unit}
    elif median > 1.1 * entry["Measured"]:
        proposed = {"Measured": measured, "Budget": min(budget, ceiling), "Unit": unit}
    else:
        return "same", None
    if target is not None and target < proposed["Budget"]:
        proposed["Target"] = target
    return "cheaper" if median < entry["Measured"] else "dearer within", proposed
```

1. **Line 351:** fewer than three values say nothing.
2. **Line 359:** a value over the budget stops everything: the tool never raises a budget.
3. **Line 362:** a spread above a quarter of the median is unstable and stays as it is.
4. **Line 366:** the new budget is 1.5 times the rounded measurement, rounded down.
5. **Lines 382–390:** a cheaper or dearer median gives a new `Measured`, and the budget never grows.

Read the order of the tests, because it is the rule: too few values, counts, over budget, unstable, then the median against `Measured`. A metric whose values are over its budget stays unchanged, because the tool never raises a budget. It raises one only for a metric that you name with `--rebaseline <metric>=<reason>`, after the method below showed a change of the machine.

That method uses an **interleaved A/B**: two builds measured alternately on one machine, so that the machine's drift touches both equally. You measure the current build alone, then interleaved with the build of the commit that set the budget, in three pairs. If the old build is as far over its own budget as the new one (the median ratio within 1.10), the machine changed, and the budget is re-baselined. If the old build is within its budget, the code got slower between the two commits. The option `--baseline <files>` compares two sets of results by the ratio of their medians.

### The lock and the helpers

`Tools/PerfLock.py` runs a command while it holds a lock file in the temporary folder of the user, so that the measurements of two agents on one machine never overlap. It waits for the lock up to 30 minutes and then exits with 75. It ends the command after 25 minutes and exits with 124. Otherwise it exits with the command's own code, and 2 means wrong usage. The operating system releases the lock when the holder ends, also by a crash.

The rest of the lab is helper code. `Perf/SceneGenerators.h` builds scenes of flat roots, trees, grids of cubes and entities that run a script that does nothing. A world fixture builds worlds for streaming tests. `MeasureFrames` and `MeasureGPU` in `Perf/RendererPerfUtils.h` run frames as an application does and give the median GPU time. Peak memory is measured by a helper process that the test starts, such as `MeasureFolderImportInHelper`.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Statistical tests on many runs of old and new code | General benchmark libraries, with a tool that compares two result sets | A verdict with a stated chance of a wrong answer, and no need for a fixed limit | A budget that anyone can read and check at a glance, and the ratchet's plain rule |
| Counting instructions, not time | Compiler teams that track performance, with tools that simulate a processor | Numbers with almost no noise, so one run decides | Cache, memory and cores, which decide most game costs, and the GPU |
| Compare with the main branch on the same hosted runner | Many project CI systems | No reference machine, and a check on every pull request | Reliable numbers: hosted runners share their machines, so noise is large |
| The minimum of many runs as the statistic | Small benchmark tools | The least noise from a single number | The shape of the slow tail, which players feel as hitches |

## How it is tested

The lab tests itself in two ways. The suite `PerfLab` holds the lab's own logic and runs in every configuration, in the Core :term[shard]{id=shard} of the unit tests. It checks that `Summarize` returns the median, the 95th percentile and the extremes for odd, even, single and empty lists. It checks that a budget file which breaks a rule is rejected with the reason, and that a results file holds one entry per metric.

The suite also checks the confirmed check. It measures once within the budget and measures again while over it. It fails when every attempt is over, and it fails before any measurement when a metric has no budget.

The suite `Perf.Harness` runs only with the perf label. It checks that `Measure` times only the calls after the warm-up: its warm-up calls take 500 ms and its timed calls half a millisecond, so a timed call that was a warm-up call would show. It also runs the canary.

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=PerfLab*
ctest --preset windows-release -L perf
```

The first command runs the lab's logic in a Debug build. The second runs the perf tests of a Release build, alone, on a quiet machine.

## Changing it safely

To add a metric, add a provisional entry to `Budgets.json` and measure it inside `CheckBudgetConfirmed`. The measuring function must start from the start on every call, with its own warm-up and with counters that begin at zero, because the check may call it again. Say in a comment which statistic you check and why. On the reference machine, run the suite, read the results file and give the entry its `Measured` and a `Budget` of at most 1.5 times it. Use the median of enough samples, and a maximum only for a metric that is a maximum by nature, such as peak memory.

Before you merge a change that touches budgets or perf tests, run `Tools/PerfStability.py --runs 5` on the reference machine. Run the `PerfLab` suite after any change to `PerfUtils.cpp`: the lab's own rules are tested there, and a weakened rule would weaken every later test.

## Summary

- One attempt within the budget decides a metric, because noise only adds; a failure on a busy machine says nothing, while a failure in every attempt is a regression.
- `Measure` discards a warm-up, and `Summarize` returns the median and the nearest-rank 95th percentile, computed in integers.
- A budget is at most 1.5 times the reference machine's measurement and falls with a cheaper metric. It rises only for a machine change that an interleaved A/B shows, or for a cost the owner accepted.
- A perf line starts with `[perf]` and comes from `Measure` or from a confirmed check. An entry of `Budgets.json` decides it, and the results file records it with its attempts.
- A new metric starts provisional and is measured inside `CheckBudgetConfirmed` until the reference machine gives it a measurement.

## Check yourself

1. A metric has the budget 12.0 ms. Its three attempts measure 13.1, 11.8 and 12.9 ms. What does the check report, and why?

   :::answer{tests="noise-adds"}
   The check passes. The second attempt is within the budget, and noise only adds, so the code can meet the budget. The check stops there, and the record holds the attempts 13.1 and 11.8 with the value 11.8.
   :::

2. Which values does `Summarize` return for the samples 7, 3, 9, 1, 5, 8 (in milliseconds)?
   - A. median 6.0, 95th percentile 9
   - B. median 5.0, 95th percentile 8
   - C. median 5.5, 95th percentile 8

   :::answer{tests="summarize"}
   A. Sorted: 1, 3, 5, 7, 8, 9. The count is 6, an even number, so the median is the mean of 5 and 7, which is 6.0. The rank is $(6 \cdot 95 + 99) / 100 = 6$, so the 95th percentile is the 6th sample, 9.

   Options B and C take the 5th sample as the percentile, but the rank is 6. Option B also takes the 3rd sample (5) as the median. Option C's median, 5.5, is the mean of no two middle samples: those are 5 and 7.
   :::

3. A metric measured 10.0 ms on the reference machine, and its budget is 15.0 ms. A change makes it 7.0 ms. What do you do?

   :::answer{tests="budget-rules"}
   Lower the entry in the same commit: `Measured` 7.0 and `Budget` 10.5, at most 1.5 times 7.0. The ratchet lets budgets only go down, so the gain stays, and the commit message states the measured values. Leaving the budget at 15.0 ms would let a later change slow the code by 50 % and still pass.
   :::

4. Your change fails a perf test while a build runs on the same machine. The canary measures 10.1 ms. What is your next step?

   :::answer{tests="noise-adds"}
   Run the failing suite again on a quiet machine. The canary uses one thread and load on many cores can leave it unchanged, so a normal canary does not clear the code. On the quiet machine a regression is over its budget in every attempt, and noise is not.
   :::

5. A test prints a line that ends "over the budget in attempt 1 of 3" and then "measuring again". Where did the line come from, and what happens next?

   :::answer{tests="read-run"}
   `BudgetChecker::CheckConfirmed` in `StrataTests/src/Perf/PerfUtils.cpp` printed it through `Print` after the first attempt measured more than the budget. The check calls the measuring function again, up to attempt 3, and stops at the first attempt within the budget.
   :::

6. A new metric has no measurement from the reference machine yet. Which entry do you add to `Budgets.json`?
   - A. `{ "Measured": 5.0, "Budget": 7.5, "Unit": "ms" }`, with the numbers of your laptop
   - B. `{ "Unit": "ms", "Provisional": true }`
   - C. No entry: the test measures it and nothing is checked

   :::answer{tests="add-metric"}
   B. A provisional entry names the unit, and the check measures and records the metric without failing. Option A puts the numbers of another machine into the file, which the rules forbid. Option C fails the test before it measures anything, because a metric without an entry is an error.
   :::

## Exercises

1. **Basic.** The samples of a measurement are 4.0, 4.2, 4.1, 9.0 and 4.3 ms. Find the median, the mean and the nearest-rank 95th percentile, and say which one the lab checks.

   :::answer[Worked solution]{tests="summarize"}
   Sorted: 4.0, 4.1, 4.2, 4.3, 9.0. The median is the middle value of five, 4.2 ms. The mean is 25.6 / 5 = 5.12 ms, pulled up by the 9.0 ms call. The rank is $(5 \cdot 95 + 99) / 100 = 5$, so the 95th percentile is the 5th sample, 9.0 ms. The lab checks medians, because the slow call is noise that the median ignores.
   :::

2. **Medium.** Add a provisional metric of unit `us` for a function `spin`, in a suite of your own, and measure it in a confirmed check. Say what the first run does, and what the entry gets later.

   :::answer[Worked solution]{tests="add-metric"}
   First the entry, which has a unit and no measurement:

   ```json
   "Perf.Example.Spin": { "Unit": "us", "Provisional": true }
   ```

   Then the test, written as :term[pseudocode]{id=pseudocode} after the engine's function `CheckBudgetConfirmed`:

   ```pseudocode
   CheckBudgetConfirmed("Perf.Example.Spin", function ()
       measurement = Measure("Perf.Example.Spin", 3, 30, spin)
       return measurement.MedianMs * 1000   // microseconds, lower is better
   )
   ```

   The first run measures once, prints the value with "provisional, no budget until the reference machine measures it", records it in the results file with `"Provisional": true` and never fails. On the reference machine, you run `ctest --preset windows-release -L perf`, read the metric's `Value` in `PerfResults`, and then edit the entry to `Measured` and `Budget` (at most 1.5 times it) and no `Provisional`. `Tools/PerfStability.py --results <runs> --propose-budgets <file>` proposes the same numbers from at least three runs.
   :::

3. **Hard.** Write a function `Classify` that returns "not recorded", "over budget", "unstable", "cheaper", "dearer within" or "same" for an entry and a list of values, and test it on six lists.

   :::answer[Worked solution]{tests="budget-rules" solution="sketches/engineering-perf-lab-ratchet.cpp"}
   The order of the tests is the rule. A list needs three values. Then a value over the budget wins over everything, and a spread above 25 % of the median means the metric is unstable.

   Only then does the median decide between cheaper (below 0.9 of `Measured`), dearer within (above 1.1) and same.

   ```cpp sketch="engineering-perf-lab-ratchet.cpp"
   #include <algorithm>
   #include <cstddef>
   #include <cstdio>
   #include <string>
   #include <vector>

   struct Entry
   {
   	double Measured = 0.0;
   	double Budget = 0.0;
   };

   // The class of a metric after several runs, in the order of the lab's tool: too few runs, over budget, unstable,
   // then the median against the measurement on the reference machine.
   std::string Classify(const Entry& entry, std::vector<double> values)
   {
   	const size_t count = values.size();
   	if (count < 3)
   		return "not recorded";
   	std::sort(values.begin(), values.end());
   	const double median = count % 2 == 1 ? values[count / 2] : (values[count / 2 - 1] + values[count / 2]) * 0.5;
   	if (values.back() > entry.Budget)
   		return "over budget";
   	if ((values.back() - values.front()) / median > 0.25)
   		return "unstable";
   	if (median < 0.9 * entry.Measured)
   		return "cheaper";
   	if (median > 1.1 * entry.Measured)
   		return "dearer within";
   	return "same";
   }

   int main()
   {
   	const Entry entry = { 10.0, 15.0 };
   	const std::vector<std::vector<double>> runs = {
   		{ 10.1, 9.8 },
   		{ 10.2, 9.9, 10.4, 10.0 },
   		{ 8.1, 8.3, 8.2 },
   		{ 11.6, 11.4, 11.9, 11.5 },
   		{ 10.0, 13.9, 9.9, 10.1 },
   		{ 10.0, 10.1, 15.5 },
   	};
   	for (const std::vector<double>& values : runs)
   		std::printf("%zu values: %s\n", values.size(), Classify(entry, values).c_str());
   	return 0;
   }
   ```

   ```text output-of="engineering-perf-lab-ratchet.cpp"
   2 values: not recorded
   4 values: same
   3 values: cheaper
   4 values: dearer within
   4 values: unstable
   3 values: over budget
   ```

   1. **Line 18:** fewer than three values are not enough to decide.
   2. **Line 22:** a value over the budget comes before every other test.
   3. **Line 24:** a spread of more than a quarter of the median marks the metric unstable.
   4. **Line 26:** only a stable metric reaches the comparison with `Measured`.

   The real tool also handles counts, provisional entries and named re-baselines, and rounds the numbers it proposes to four significant digits.
   :::

4. **Hard.** Trace it yourself: take one `[perf]` line of a run and find the line of code that printed it, the check that measured its metric and the entry that decided it.

   :::answer[Worked solution]{tests="read-run"}
   Search the line's fixed words in `StrataTests/src/Perf/`. A line with "median", "p95", "min" and "max" comes from the `std::printf` in `Measure` in `PerfUtils.cpp`. A line with "budget" and a percentage comes from `Print`, called in `BudgetChecker::CheckConfirmed`, which formats it with `DescribeValue`. Search the metric's name in the other test files to find the `CheckBudgetConfirmed` call. The measuring function inside it runs `Measure`.

   The name is also a key of `StrataTests/Perf/Budgets.json`, where its `Budget` decides the verdict. The canary's entry is on line 26.
   :::

## Where it lives in Strata

- `StrataTests/src/Perf/PerfUtils.h` and `PerfUtils.cpp`: `Measure`, `Summarize`, `BudgetChecker`, `CheckBudgetConfirmed`, `MergeResults`.
- `StrataTests/Perf/Budgets.json`: the budgets, and the specification in its `_comment`.
- `StrataTests/src/Perf/PerfHarnessTests.cpp`: the `PerfLab` and `Perf.Harness` suites, with the canary.
- `StrataTests/CMakeLists.txt`: the CTests `StrataTests.Perf`, `StrataTests.PerfGPU`, `StrataTests.PerfGPU.Samples` and `StrataTests.PerfResults.Clean`.
- `Tools/PerfStability.py` and `Tools/PerfLock.py`: the stability tool and the lock.
- `StrataTests/src/Perf/SceneGenerators.h`, `RendererPerfUtils.h`: scene generators and the frame measurements of the GPU suites.

## Further reading

- Google Benchmark, user guide: a benchmark library with warm-up, repetitions and a tool that compares runs (intermediate).
- Mytkowicz, Diwan, Hauswirth and Sweeney, 2009, a paper on measurement bias: how the place of code and the size of the environment change timings (advanced).
- The Valgrind manual, chapter on Cachegrind: counting instructions and cache misses instead of time (intermediate).
