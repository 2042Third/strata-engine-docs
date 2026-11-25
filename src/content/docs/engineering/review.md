---
id: engineering/review
title: "Review: building, testing and releasing the engine"
description: "The questions of every page of the part on building, testing and releasing the engine, and exercises that use several of its pages together."
tracks: [E]
status: final
generated: review
---

## Cumulative exercises

These exercises need more than one page of the part. Try each before you open its worked solution.

1. **Basic.** You build the engine on Linux for a server without sound. You run `cmake --preset linux -DSTRATA_WITH_AUDIO=OFF`. In the same change you add the file `Clip.cpp` to a new folder `Video` of the engine's source, and no layer in `StrataTests/Architecture/Layers.json` lists that folder.

   Name each cause that stops this configure, and the fix of each. Then say what a plain `cmake --preset linux` does in the same build folder a week later.

   :::answer[Worked solution]
   There are two causes. First, the editor is on by default and needs every engine module, so a configure with audio off and the editor on stops with a message that the editor needs every module and a window. The fix is `-DSTRATA_BUILD_EDITOR=OFF` on the same command, since a server needs no editor. This check stands in the root file, before the layer libraries are made, so you meet the second cause only after this fix.

   Second, the new file belongs to no layer. The layer table gives every engine source to exactly one layer, so the configure stops and names the file. The fix is a `Paths` pattern for the folder `Video` in the layer that should own it. Widening a `MayInclude` row is never the fix. After the next configure the file compiles into the library of that layer.

   The `-D` options stay in the cache of the build folder. A plain configure a week later therefore still builds without audio and without the editor. You bring a switch back with `-U` on its name, which returns its default, or with a fresh build folder.
   :::

2. **Basic.** A full set of caches of continuous integration (CI) holds three `ccache` entries of 40 MB and two `sccache` entries of 500 MB. GitHub's store holds 10,240 MB, and `main` holds one set.

   (a) A branch pushes without deleting its older entries, and each push saves one new set. After which push does GitHub delete the set of `main`? (b) With the cleanup step, how many active branches fit beside `main`?

   (c) You push a branch named `wave9` and open no pull request. Does CI run? You rename it `ci/wave9`, its first run fails and you cannot open the job log. What do you do, and when does `main` move?

   :::answer[Worked solution]
   (a) One set measures $3 \times 40 + 2 \times 500 = 1{,}120$ MB. After push $n$ the store holds the set of `main` and $n$ sets of the branch, $(n + 1) \times 1{,}120$ MB. For $n = 8$ that is 10,080 MB, which fits. For $n = 9$ it is 11,200 MB, which is over 10,240 MB, so GitHub deletes the least recently used entry. That entry is the set of `main`, and it goes after push 9.

   (b) With the cleanup, each branch keeps one set. The store holds $10{,}240 / 1{,}120 \approx 9.1$ sets, so nine fit: `main` and eight branches.

   (c) CI runs for pushes to `main`, for pull requests and for pushes to branches named `ci/<name>`. A branch `wave9` without a pull request starts nothing. After the rename, the run starts. Job logs need administrator rights, so you read the annotations of the failed job with `Tools/CIStatus.py`. You fix the cause, push again, and move `main` only when every job is green.
   :::

3. **Medium.** The reference machine measured a metric at 8.0 ms, and its budget is 12.0 ms. After your change, the lab's samples for it on the reference machine are, in milliseconds, 4.8, 5.4, 4.9, 5.0, 5.2 and 9.0, the last while a build ran on the machine.

   What do `Summarize` and the check use, what is the highest budget the rules allow now, and what do you do before you merge? Then predict three later attempts against a budget of 7.5 ms: 9.2, 7.1 and 9.0.

   :::answer[Worked solution]
   Sorted, the samples are 4.8, 4.9, 5.0, 5.2, 5.4 and 9.0. With six samples the median is the mean of the third and fourth, $(5.0 + 5.2) / 2 = 5.1$ ms. The nearest rank of the 95th percentile is $\lceil 0.95 \times 6 \rceil = 6$, so it is the sixth sample, 9.0 ms. The lab checks medians, so the slow sample of the busy moment does not matter.

   A budget is at most 1.5 times the measurement: $1.5 \times 5.1 = 7.65$ ms. The metric became cheaper, so the budget is lowered, never kept at 12.0, and a budget of 7.5 ms is within the rule.

   Before the merge, the commit message states the measured values, 8.0 ms before and 5.1 ms after. On the reference machine you run `ctest --preset windows-release -L perf`, and `Tools/PerfStability.py --runs 5` because a budget changed. CI skips the label `perf`, so a green CI run proves nothing about this.

   The check measures again while an attempt is over the budget, and one attempt within it decides. Attempt 1 (9.2 ms) is over, and attempt 2 (7.1 ms) is within 7.5 ms, so the check passes. If the attempts were 9.2, 9.0 and 9.3 ms, every attempt would be over, which is a regression and not a busy machine.
   :::

4. **Medium.** You fix a bug in a loader and add a test case in a new suite named Water.Waves. The case passes at once.

   (a) What do you do before the commit? (b) What do you expect from `ctest`, and which file do you change?

   (c) Another test uses the suite `Asset.Pack.Sweep` on a pack of 4,096 bytes. How many cut lengths and flipped bytes does the fuzz run test, and which offsets does a shard test?

   :::answer[Worked solution]
   (a) A regression test must fail without its fix. You run the case against the code without the fix and confirm that it fails for the reason you expect. A case that passes there checks the wrong thing.

   (b) No shard filter matches the new prefix, so the suite runs nowhere, and the shards pass. The check `Testing.Shards` fails and names Water.Waves. You add a filter for the prefix to the `Suites` of a fitting shard in `StrataTests/CoreShards.json`. CMake reads the file at configure time, so you configure again.

   (c) The fuzz run tests every offset: 4,096 cut lengths and 4,096 flipped bytes, 8,192 cases. A shard tests a sample: the header's range, the tables at the file's end, the bytes near the edges of the entry alignment and a fixed number of seeded draws. `SelectSweepOffsets` seeds its generator with a constant mixed with the size, not with the time, so the same pack gets the same offsets in every run, and a failing offset comes back. The fuzz run exists in Release and Dist only.
   :::

5. **Medium.** Two Linux builds replay the same fall of a box: one with the defaults and one with `-DSTRATA_CROSS_PLATFORM_DETERMINISTIC=ON`. The golden hash of box3d is equal in both, but a position that engine code computes as `a * b + c` may differ in its last bit. Explain both facts and say what the option costs.

   Then take the toy numbers: in `float`, $1.1 \times 1.5 + 0.1$ gives 1.75000012 with two roundings and 1.75 with one. How far apart are they, and is either wrong?

   :::answer[Worked solution]
   The default build compiles the engine's own code with `-mfma`, which lets the compiler fuse a multiply and an add into one instruction that rounds once. The option removes `-mfma` from that code, so the two builds may round differently in the last bit.

   Box3d does not follow the option. Its vendor build file builds it from sources with `-ffp-contract=off`, so that no compiler fuses its arithmetic, and its results match in both builds. This is also why the golden hash of the suite `Physics.Box3D` holds.

   The option costs the speed of the fused instructions in the engine's own loops. It also does not make the whole engine match across platforms: of the engine's code, only box3d gives matching results.

   The two toy results differ by $1.75000012 - 1.75 \approx 1.2 \times 10^{-7}$, and their bit patterns, `3fe00001` and `3fe00000`, differ by 1 in the last place. Neither is wrong. Each is the correctly rounded result of its own rule: round after the product and again after the sum, or round once.
   :::

6. **Hard.** A tool patches a SPIR-V module of 30 words with two edits, numbered in the original module: add 4 words at word 11, and add 3 words at word 20.

   (a) In which order does the tool apply them, and how long is the result? (b) What goes wrong if it applies the edit at word 11 first?

   (c) The tool writes the result as a header with eight words per line. How many array lines does it hold? (d) A sweep cuts the patched module of 148 bytes at every length and flips each byte once, as the fuzz run does. How many cases is that?

   :::answer[Worked solution]
   (a) The tool collects its edits first and applies them from the back: the edit at word 20 first, then the one at word 11. The first edit changes nothing before word 20, so the position 11 is still right for the second. The result holds $30 + 3 + 4 = 37$ words.

   (b) The edit at word 11 moves every later word by 4. The instruction that stood at word 20 now stands at word 24, and the second edit at word 20 lands 4 words before the instruction it meant, inside or between other instructions. The result is a module that no reader can read.

   (c) Eight words per line: $37 = 4 \times 8 + 5$, so four full lines and one line of 5 words, 5 lines.

   (d) The module has $37 \times 4 = 148$ bytes. A full sweep tests every offset: 148 cut lengths and 148 flipped bytes, 296 cases. A shard tests a sample, with the same offsets in every run because the seed is fixed.
   :::

7. **Hard.** A teammate adds the host function `SetFogDensity` to the script interface. Their unit test calls it from the test module of the script interface and checks that `GetScriptHostCallCounts()` lists it once. The unit test passes in Release at their desk, but the first CI run of their branch fails.

   (a) Which check of the feature test fails, and what must the teammate add? (b) With that added, CI is green, but the release run later fails the same unit test. Why?

   (c) Why did CI not see this fault, and which run finds it before a release is published?

   :::answer[Worked solution]
   (a) The feature test demands at least one call of every entry of the host table during its play. No feature script calls `SetFogDensity`, so the check for host functions fails. `StrataTests.FeatureTest` needs no graphics processing unit (GPU), and the test step of CI omits only the labels `gpu` and `perf`, so CI runs it. The teammate adds a call from a feature script, with an `Expect` on its result, and an entry in `ST_SCRIPT_HOST_FUNCTIONS`. The call must come after `ResetScriptHostCallCounts()`, because the check reads the counts after the play.

   (b) Release builds count host calls, and Dist builds do not. The unit test expects a count of 1, and in the Dist run the list is empty. The test must say so with `#if defined(ST_DIST)` and expect an empty list there.

   (c) CI tests Release, and its Dist job runs only the package tests, so no CI run executes this test in Dist. A dry run does: push the tag `v0.7.0-rc1` when the project's version is 0.7.0. It builds and tests Dist on every system and publishes nothing, so the fault appears before the plain tag `v0.7.0`.
   :::

8. **Hard.** You change a temporal filter of the renderer and compare two captures on one machine. The images have six pixels. Three of them hold 100, 100 and 100 in the old build and 103, 94 and 101 in the new one; the other three are equal. The repeats of the new build differ from each other by 0 pixels.

   (a) Give the differing pixels, the largest difference, the mean difference over all six pixels and the signed values. (b) At one world point, three frames of the new build read 0.50, 0.58 and 0.50, and three frames of the old build read 0.50, 0.54 and 0.58. What is $|d|$ of each, rounded to two decimals?

   (c) A block of 32 by 32 pixels holds 1,024 pixels, of which 600 were measured. Half of the measured pixels have $d = +0.30$ and half have $d = -0.30$. Does the block count, and what is its value? What if all 600 have $d = +0.30$?

   :::answer[Worked solution]
   (a) Three pixels differ, by +3, −6 and +1. The largest difference is 6. The sum of the differences is $3 + 6 + 1 = 10$, and over the six pixels the mean is $10 / 6 \approx 1.67$. The repeats differ by 0, so the render is steady, and these differences are a change of the build. The signed image shows that two pixels became brighter and one darker.

   (b) New build: the second difference is $0.50 - 1.16 + 0.50 = -0.16$, and the mean is $1.58 / 3 \approx 0.527$, so $|d| = 0.16 / 0.527 \approx 0.30$. Old build: $0.58 - 1.08 + 0.50 = 0$, a steady drift, so $|d| = 0.00$. The new build flickers where the old one drifted.

   (c) A block counts when more than half of its pixels were measured. Half of 1,024 is 512, and 600 is more, so it counts. The meter takes the absolute value of the block's mean $d$. With half $+0.30$ and half $-0.30$ the mean is 0, and the block's value is 0: noise of single pixels cancels. With all 600 at $+0.30$ the mean is 0.30: the change of a whole region remains, and that is what a real change looks like.
   :::
