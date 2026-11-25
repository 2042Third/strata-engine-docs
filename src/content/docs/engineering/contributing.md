---
id: engineering/contributing
title: "The review checklist and the way a change lands"
description: "Take one change through the six-item review, a clean check and a ci branch to main, and learn what four special kinds of change add."
kind: how-to
size: M
tracks: [E]
needs: [engineering/ci, engineering/feature-test]
time: 50
learn:
  - id: review-staged
    text: find what a staged diff breaks of the six items of the pre-commit checklist
  - id: verify-clean
    text: run exactly what is staged in a clean worktree, in Debug and in Release
  - id: land-ci
    text: run a change through a ci branch, read a failed run with CIStatus and move main only on green
  - id: pick-extras
    text: choose the extra steps that a submodule upgrade, a budget change, taken code or a sample change needs
since: 0.3.0
status: final
---

You wrote a change and a test for it. This page takes that change the way every change to Strata lands: one reviewed commit, verified apart from your other work, green on the :term[continuous integration]{id=ci} (CI) servers, and then on `main`. Before you start:

- You have the clone of [your first engine change](../core/first-change.md) with its `ToUpper` function and its test case in the suite `Core.StringUtils`, built in `Debug` and not yet committed.
- You have a fork of the engine's :term[repository]{id=repository} on GitHub with GitHub Actions enabled, and your clone's `origin` points to it.
- You have Python 3 on your path, for the tools in `Tools/`.

## The rules behind the steps

Strata keeps six golden rules in `AGENTS.md`, and each step below serves one of them. Rule 1 says to use no other folder of your machine. It also says you may copy code of another project only when its license is permissive, and you keep its notice. Copyleft code gives ideas and nothing more. Rule 2 says everything ships with tests, and that you never skip or weaken a test to make it pass.

Rule 3 says you review every commit first and fix the findings before you commit. Rule 4 says to follow the code style exactly. Rule 5 forbids placeholder code, errors that nobody handles, and a silenced warning without a reason. Rule 6 says to keep the :term[feature test]{id=feature-test} current.

The rules exist because a commit is hard to take back once other work stands on it. A defect found in review costs a minute. The same defect found a week later costs a search through every commit since.

The steps run from the cheapest check to the dearest. Reading a :term[diff]{id=diff} takes minutes, a local test run takes tens of minutes, and a push to CI takes longer and uses a shared machine. A defect that the cheap check catches never reaches the dear one. That order is why you review before you verify, and verify before you push.

## The review table

Rule 3 points at the **pre-commit review checklist**: six questions you ask of the complete staged :term[diff]{id=diff} before you commit. The table gives what to check in each. You will use it in step 5.

| Item | What to check |
| --- | --- |
| Correctness | Empty input, missing files, zero sizes and invalid handles; :term[undefined behavior]{id=undefined-behavior} and :term[data races]{id=data-race}; a resource that leaks on one path. |
| Tests | New behavior has a test; every test passes locally; the feature test covers a new component or script function. |
| Style | The naming table, tabs, braces, include order; no dead code and no commented-out code. |
| Portability | No platform call outside `Strata/src/Platform/`; no warning on MSVC, GCC or Clang; no include that only MSVC tolerates. |
| Documentation | A short comment wherever the reason is hidden; `Docs/` and `AGENTS.md` follow a changed behavior or its steps. |
| Commit hygiene | One logical change; a subject in the imperative under 72 characters; a body that says what and why. |

A commit that passes the table does not lack tests, style or notes. A commit that skips it passes those checks by luck.

## Land the change

The steps use the `ToUpper` change as the example. Each step says why in a sentence or two, and names the mistake that happens most.

:::::steps

1. Make the change one logical change. Run `git status --short`, then stage your files by path: `git add Strata/src/Strata/Core/StringUtils.h StrataTests/src/Core/StringUtilsTests.cpp`. Never use `git add -A`.

   **You should see:** `git diff --staged --stat` lists two files, and nothing else.

   **If you do not see it:** a third file means unrelated work or a stray build file. Remove it with `git restore --staged <path>`, or split it into its own commit.

   **Why:** a commit that holds one idea can be reviewed in one sitting and reverted without side effects. The usual mistake is to stage every changed file because the work "belongs together".

2. Cover the behavior with a test. New behavior gets test cases. For a bug fix, prove the regression test fails without the fix: remove the fix, run the test, read the failure, and restore the fix. The program `build/windows/bin/Debug/StrataTests.exe --test-suite=Core.StringUtils` runs the suite of `ToUpper`.

   **You should see:** with the fix, the run ends with `Status: SUCCESS!`; without it, :term[doctest]{id=doctest} prints the two sides of the failing check.

   **If you do not see it:** a test that passes without the fix proves nothing. Make its input one that the old code gets wrong, as [the page on testing](testing.md) shows.

   **Why:** a test that cannot fail guards nothing. The usual mistake is to write the test after the fix and never run it against the old code.

3. Extend the feature test when something registered changed. These must appear in `StrataTests/FeatureTest/`: a new component, a new property set to a value other than its default, a :term[settings section]{id=settings-section-world}, a script field type, a host function or an :term[asset type]{id=asset-type}. Run `build/windows/bin/Debug/StrataTests.exe --test-suite=FeatureTest`.

   **You should see:** for `ToUpper`, nothing to add: a text function registers nothing, and the suite passes as it did.

   **If you do not see it:** the suite fails with a message that names the component or property that no test touches. Add it to the project as [the page on the feature test](feature-test.md) shows.

   **Why:** the feature test is the one test that notices a feature nobody exercises. The usual mistake is to widen what it tolerates, instead of covering the feature.

4. Update the documents that your change makes false. Search `Docs/` and `AGENTS.md` for the names you changed. When you edit `AGENTS.md`, run `build/windows/bin/Debug/StrataTests.exe --test-suite=Docs.AgentGuide`.

   **You should see:** the suite passes. At the pin `AGENTS.md` holds 39,343 characters against a limit of 40,000, so 657 are left, and every link resolves to a file and a heading.

   **If you do not see it:** the message gives the character count or the broken link. Move the details into `Docs/DeveloperGuide.md` and keep the rule and its link in `AGENTS.md`.

   **Why:** every agent session loads `AGENTS.md` whole, so it must stay short. The usual mistake is to count :term[bytes]{id=byte}: the suite counts :term[code points]{id=code-point}, and a dash that takes three bytes counts once.

5. Stage everything, then review the complete diff with `git diff --staged` against the six items of the table above. Read it as a stranger would, line by line, and write each finding down before you fix any.

   **You should see:** a short diff. For `ToUpper`, it adds the function after `ToLower` and one test case.

   **If you do not see it:** when the diff holds more than you meant, return to step 1. When the table finds a defect, fix it, stage again and read the new diff from the top.

   **Why:** you read your own work as you meant it; the diff shows what it says. The usual mistake is to review the working tree, which holds changes that are not staged.

6. Run every test locally: `ctest --preset <platform>-debug -j 8`, with `<platform>` one of `windows`, `linux` or `macos`. Add `-LE gpu` on a machine without a :term[graphics processing unit]{id=gpu} (GPU). For a change that can move performance, also run `ctest --preset <platform>-release -L perf`.

   **You should see:** the run ends with every test passed.

   **If you do not see it:** read the first failure, not the last. Do not delete or skip a failing test: rule 2 forbids it.

   **Why:** CI runs `ctest -LE "gpu|perf"` only, so the GPU and perf tests run on your machine or nowhere. The usual mistake is to run the one suite you changed.

7. Verify exactly what is staged in a clean :term[worktree]{id=worktree}, in `Debug` and in `Release`. Your working tree often holds other work, and a bug can show in one configuration only. The skill `strata-build-test` gives the commands.

   ```sh src=".claude/skills/strata-build-test/SKILL.md#L215-L219"
   git diff --cached --binary > staged.patch
   cd .worktrees/verify && git reset --hard <base> && git clean -fd
   git apply --index ../../staged.patch
   cmake --preset windows && cmake --build --preset windows-debug && ctest --preset windows-debug
   cmake --build --preset windows-release && ctest --preset windows-release
   ```

   The first line writes your staged changes into a patch file. The second resets a second worktree, `.worktrees/verify`, to the commit `<base>` your branch started from, and removes the files :term[git]{id=git} does not track. The third applies the patch there. The last two lines build and test `Debug`, then `Release`, with the :term[preset]{id=preset} names of Windows.

   Create the worktree once with `git worktree add .worktrees/verify <base>`, and replace `windows` by your platform. While nothing is committed yet, `<base>` is `HEAD`.

   **You should see:** both runs end with every test passed, and the patch applies without a message.

   **If you do not see it:** a failure here that your main folder did not show means your working tree held something the commit lacks, often a new file you forgot to stage. Stage it and repeat from step 5.

   **Why:** this is the only check of what you will commit, and not of what you happen to have. The usual mistake is to commit what the working tree compiles.

8. Write the commit message. The subject is one line in the imperative, under 72 characters; the body says what changed and why. For example, the subject `Add StringUtils::ToUpper beside ToLower` has 39 characters. Commit in the folder of your clone with `git commit`.

   **You should see:** `git log -1` shows your subject and body, and the working tree is clean.

   **If you do not see it:** a subject that says "fixed stuff" is not hygiene. Rewrite it with `git commit --amend` before you push.

   **Why:** the log is the history people search years later; a body that says why saves them a guess. The usual mistake is a subject in the past tense that names a file and not the change.

9. Push the commit to a branch named `ci/<name>`, wait for green CI, and only then move `main`. Run `git switch -c ci/to-upper`, then `git push -u origin ci/to-upper`, and watch the result with `python3 Tools/CIStatus.py status ci/to-upper`. For a change that touches many files, run `python3 Tools/CompatLint.py --changed-since main` before the push.

   **You should see:** the tool prints one line per run and job. Its :term[exit code]{id=exit-code} is 3 while a job still runs and 0 when every run completed, and every job line must end in `completed success`. Then run `git switch main`, `git merge --ff-only ci/to-upper` and `git push origin main`.

   **If you do not see it:** when a job fails, run `python3 Tools/CIStatus.py annotations ci/to-upper`. It prints the failure notes of the failed jobs with file and line, that you can read without a log. Fix, repeat from step 5 and push again. The tool reads a token from `GH_TOKEN`, from `GITHUB_TOKEN` or from `gh auth token`, and never prints it.

   **Why:** older :term[compilers]{id=compiler} and other :term[standard libraries]{id=standard-library} reject code that yours accepts, and CI builds on all three systems. The usual mistake is to push straight to `main` and find the failure there, where everybody else's work stands on it.

:::::

## Result

You have one commit on `main`. Its tests ran green on your machine in two configurations and in CI on three systems. The log tells why it exists, and nobody needs to ask what it touches.

## Variations

The nine steps stay. These changes add to them.

**A submodule upgrade:** Strata pins every dependency in `Strata/vendor/`. Check out the new tag inside the submodule, rebuild, run all tests, and update `ThirdPartyNotices.md`. Commit the bump alone, apart from any change that needs it. An upgrade of box3d must also keep the :term[golden hash]{id=golden-hash} of the suite `Physics.Box3D`. The [page on third-party code](third-party.md) gives the reasons.

**A change to a perf budget:** A limit lives only in `StrataTests/Perf/Budgets.json`. A budget never rises, and it stays within 1.5 times its measurement. A commit that adds or lowers one states the measured values in its message. Before it merges, run `python3 Tools/PerfStability.py --runs 5` on the reference machine. The [page on the performance lab](perf-lab.md) explains the rule.

**Code from another project:** Take it only under a permissive license, keep its notice, name its source, and add it to `ThirdPartyNotices.md`. Read copyleft code for ideas and never copy it, since copying would bind the engine to that license.

**A change to a sample:** The :term[command script]{id=command-script} `Editor/<Sample>Commands.json.in` of the sample must keep passing. The suite `Samples.Content` checks every sample. A sample must stand in `Samples/Samples.json`, and no folder of `Samples/` may be missing from it. Every :term[source asset]{id=source-file} needs exactly one row of its `CREDITS.md`, and the packs also stand in `ThirdPartyNotices.md`.

The budgets are 25 MB of source assets, or 80 MB for a showcase, and three screenshots in 3 MB, or six in 8 MB for a showcase. Totals over all samples bound how much a release archive grows. The suite belongs to the :term[shard]{id=shard} `Samples`, so `StrataTests.exe --test-suite=Samples.Content` runs it.

## Summary

- A staged diff is reviewed against six items: correctness, tests, style, portability, documentation and commit hygiene.
- What is staged is built and tested in a clean worktree in `Debug` and in `Release`, not what your working tree holds.
- A change lands through a `ci/<name>` push, `Tools/CIStatus.py` for a failed run, and a merge only on green.
- A submodule upgrade, a budget change, taken code and a sample change each add steps to the nine.

## Check yourself

1. Your working tree holds a :term[header]{id=header} that git does not track yet, and the file you staged includes it. Debug passes at your desk. What does step 7 show, and why?

   :::answer{tests="verify-clean"}
   The clean worktree lacks the header, so the build fails there. The commit would have broken the build for everyone else. Stage the header and repeat the review.
   :::

2. A fix for a crash comes with a new test case that passes at once. What do you check before you commit?

   :::answer{tests="review-staged"}
   Remove the fix, run the test, and see it fail. A test that passes without the fix does not guard it, and rule 2 asks for a regression test that can fail.
   :::

3. Suppose `AGENTS.md` has 38,677 characters and your edit adds 1,400. What happens, and what do you do?

   :::answer{tests="review-staged"}
   The total is 40,077, so `Docs.AgentGuide` fails. Move the details into `Docs/DeveloperGuide.md` and keep the rule and a link in `AGENTS.md`.
   :::

4. `CIStatus.py` exits with 3. Is the run green?

   :::answer{tests="land-ci"}
   No. Exit 3 means a job still runs, or no run has started yet. Wait and ask again; only exit 0 with every run succeeded permits the merge.
   :::

5. You lower a perf budget in your change. What goes into the commit message, and what do you run?

   :::answer{tests="pick-extras"}
   The measured values go into the message. Run `Tools/PerfStability.py --runs 5` before the merge.
   :::

## Exercises

1. **Basic.** Take a second small change of your own through the nine steps, from the staged diff reviewed against the table to a `ci/<name>` push read with `CIStatus.py`.

   :::answer[Worked solution]{tests="land-ci verify-clean"}
   Any small change with a test serves, for example a test case for a function that has none. Write each finding of step 5 down, run the clean check, and push. Read `status` until its exit code is 0.
   :::

2. **Medium.** A staged diff adds a function in `Strata/src/Platform/Windows/` and calls it from a file of `Strata/src/Strata/Scene/`. It also marks an old test case that now fails to be skipped, and keeps a 120-line `// old version` block. Which item of the checklist does each defect break?

   :::answer[Worked solution]{tests="review-staged"}
   The call from the scene file breaks portability: a platform call outside the platform folder. The skipped test breaks tests: every test must pass, and rule 2 forbids skipping one to make the run pass. The comment block breaks style, which forbids commented-out code.
   :::

3. **Hard.** The suite `Core.StringUtils` has no test of `StartsWith` and `EndsWith`. Add one through all nine steps, and write its commit message.

   :::answer[Worked solution]{tests="review-staged verify-clean" solution="tutorials/engineering/contributing/exercise-3.patch"}
   The patch adds one test case at the end of the suite:

   ```diff src="book:tutorials/engineering/contributing/exercise-3.patch#hunk-1"
    		const std::string repaired = StringUtils::MakeValidUTF8("\xE6\x97 \x8F\xFF ok");
    		CHECK(StringUtils::MakeValidUTF8(repaired) == repaired);
    	}
   +
   +	TEST_CASE("Prefixes and suffixes are found, and one longer than the text never matches")
   +	{
   +		CHECK(StringUtils::StartsWith("file.png", "file"));
   +		CHECK_FALSE(StringUtils::StartsWith("file.png", "png"));
   +		CHECK(StringUtils::EndsWith("file.png", ".png"));
   +		CHECK_FALSE(StringUtils::EndsWith("png", "file.png"));
   +		CHECK(StringUtils::StartsWith("", ""));
   +	}
    }
   ```

   1. **Lines 7–8:** a prefix is found, and a word that only ends the text is not.
   2. **Line 10:** a suffix longer than the text must never match.
   3. **Line 11:** the empty text starts with the empty prefix.

   Stage the test file only, review it, run the suite, check in the clean worktree and use the subject `Test StringUtils::StartsWith and EndsWith`.
   :::

4. **Hard.** Write a program that counts the code points of a text and tells whether adding a number of them still fits under the limit of 40,000.

   :::answer[Worked solution]{tests="review-staged" solution="sketches/engineering-contributing-codepoints.cpp"}
   A byte that starts with the bits `10` continues a sequence, so it adds no code point.

   ```cpp sketch="engineering-contributing-codepoints.cpp"
   // Exercise solution: a size limit counted in code points, not in bytes, as Docs.AgentGuide counts.
   #include <cstddef>
   #include <cstdio>
   #include <string>

   // A UTF-8 text has one code point for every byte that is not a continuation byte (10xxxxxx).
   static size_t CountCodePoints(const std::string& text)
   {
   	size_t count = 0;
   	for (const char byte : text)
   	{
   		if ((static_cast<unsigned char>(byte) & 0xC0) != 0x80)
   			count++;
   	}
   	return count;
   }

   int main()
   {
   	const size_t limit = 40000;
   	const size_t current = 38677; // the code points of AGENTS.md before the change
   	// A heading with an em dash: the dash is one code point and three bytes.
   	const std::string heading = "Strata Engine \xE2\x80\x94 Agent Guide";
   	std::printf("heading: %zu bytes, %zu code points\n", heading.size(), CountCodePoints(heading));

   	const size_t added[] = { 1300, 1400 };
   	for (const size_t count : added)
   		std::printf("adding %zu: %zu of %zu, %s\n", count, current + count, limit, current + count <= limit ? "fits" : "over the limit");
   	return 0;
   }
   ```

   ```text output-of="engineering-contributing-codepoints.cpp"
   heading: 29 bytes, 27 code points
   adding 1300: 39977 of 40000, fits
   adding 1400: 40077 of 40000, over the limit
   ```

   1. **Lines 7–16:** the function counts every byte that is not a continuation byte, so a three-byte dash counts once.
   2. **Line 23:** the heading holds 27 code points in 29 bytes, which shows why a count of bytes is wrong.
   3. **Lines 26–28:** 1,300 more characters fit, and 1,400 more do not.
   :::

## Where it lives in Strata

- The rules and the checklist: `AGENTS.md`, sections "Golden rules" and "Pre-commit review checklist".
- The size and link check: `StrataTests/src/Docs/AgentGuideTests.cpp`.
- The clean check: `.claude/skills/strata-build-test/SKILL.md`.
- The CI reader and the compatibility check: `Tools/CIStatus.py` and `Tools/CompatLint.py`.
- The sample check: `StrataTests/src/Samples/SampleContentTests.cpp`.

## Further reading

- The Pro Git book, chapter 2 on recording changes (beginner): staging, diff and commit.
- Google's engineering practices, "How to do a code review" (intermediate): what a reviewer checks.
