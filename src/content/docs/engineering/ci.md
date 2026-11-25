---
id: engineering/ci
title: "Continuous integration"
description: "What runs on every push to Strata's main branch, on pull requests and on ci branches, and how to read a failure without opening a log."
kind: internals
size: L
tracks: [E]
needs: [engineering/flags-portability, engineering/test-program]
time: 90
learn:
  - id: ci-checks
    text: explain what CI builds and tests for a push, and which tests a hosted runner leaves out
  - id: trace-job
    text: trace one job of the CI matrix from its keys to its test command
  - id: cache-budget
    text: compute how many pushes fill GitHub's cache limit with and without the cleanup step
  - id: read-failure
    text: find the cause of a CI failure from its annotations, without a job log
  - id: ci-branch
    text: explain why a large change goes through a ci branch and what it waits for
since: 0.4.0
status: final
---

Strata's tests and builds run on a person's machine before every commit, but one machine proves little. It has one :term[operating system]{id=operating-system}, one :term[compiler]{id=compiler} and often one :term[graphics card]{id=gpu}. Continuous integration is the second line of defence: a set of machines owned by GitHub builds and tests every change in several configurations, and reports what broke.

This page opens that machinery, the file `.github/workflows/ci.yml` and the three scripts beside it. It shows what runs on which push, why the jobs differ, how the :term[compiler cache]{id=compiler-cache} is kept alive, and how a failure is read when the log is closed to you. The compilers' traps are on [the page about flags and portability](flags-portability.md), and the labels and shards the test step selects are on [the page about the test program](test-program.md).

## The problem and how engines solve it

Suppose you change a function and the build passes on your Windows machine. You push. A teammate on an Apple computer pulls your change and the build stops: Apple's compiler rejects a line that yours accepted. Nobody did anything wrong. Each compiler accepts a slightly different language, and you only ever ran one.

**Continuous integration** (CI) is the practice of building and testing every change on shared machines, automatically, soon after it is pushed. The word "continuous" means that the check does not wait for a release: each push is checked, so a break is found while the change is still small and the author still remembers it.

CI needs somewhere to run. A **runner** is the machine that runs one CI job in GitHub Actions, GitHub's CI service. A hosted runner is a fresh virtual machine that GitHub starts for each job and throws away afterwards. A self-hosted runner is a machine you own that connects to GitHub. Hosted runners need no care from you, but they have no graphics processing unit (GPU) and run at whatever speed the shared host offers.

Four problems follow, and every engine that uses CI meets them.

- Coverage. One job proves one configuration. The usual answer is a build matrix: one job description that GitHub expands into several jobs, each with its own operating system, compiler or build type. Strata runs six jobs from two descriptions. A matrix costs machine time in proportion to its size, so each row must earn its place.
- Time. An engine this size takes a long time to compile from nothing, and a hosted runner starts empty. A compiler cache stores the compiled result of each :term[source file]{id=source-file}, keyed by its inputs, so that the next build compiles only what changed. A temporary machine cannot keep it, so the cache must be saved between runs. GitHub offers a cache store for this, with a limit of 10 GB per :term[repository]{id=repository}, and when the store is full it deletes the entries used least recently.
- Diagnosis. A build can fail in many places at once. If it stops at the first error, you fix one, push, wait, and meet the second, so a build that keeps going after an error reports every failure in one run. The log of a hosted job is also hard to reach, because GitHub shows it only to people who can administer the repository. An **annotation** is a message that a job attaches to a file and line, which GitHub shows in the pull request and serves to anyone through its application programming interface (API).
- Gating. Checking after a change lands on the main branch is too late, because everyone who pulls the main branch is now broken. Checking before needs a place to push that is not the main branch. In Strata that place is a **`ci/<name>`** branch: any branch whose name starts with `ci/`, which triggers the same checks as the main branch.

Annotations let someone who cannot open a log see the failure, and Strata relies on them.

The mistake CI exists to prevent is common. A wave of work lands many changes at once, each tested locally, and the person merges it on a green local run. The oldest compiler in the matrix then rejects the merged result, and the main branch is red for everybody. Strata's rule, shown below, is to push such a branch as `ci/<name>` and wait for green.

CI also has limits that no setting removes. A hosted runner has no GPU, so graphics tests cannot run. It is not the reference machine, so the timing budgets of the perf tests would pass or fail at random there. Strata therefore omits those tests from CI and runs them on the machines that suit them, as the contract says.

## The map: which jobs run what

One workflow file defines two jobs. The first, `build-and-test`, is expanded by its matrix into five jobs. The second, `windows-dist`, runs once. Every job checks out the repository with its :term[submodules]{id=submodule}, builds, tests, and on failure turns its logs into annotations.

```mermaid caption="A push to the main branch, a pull request or a push to a ci branch starts six jobs. Five come from one matrix and share the same steps. The sixth builds the shipping configuration on its own." alt="A trigger box leads to a group of five matrix jobs and to a sixth job below it. The group lists its steps in order: install, enter the developer environment, restore the cache, configure, build, check shaders, test, save the cache, remove old caches and write failure annotations. The sixth job lists configure, build, package tests and failure annotations."
flowchart LR
    T["push to main, push to ci/**, pull request"] --> M["build-and-test: 5 jobs from one matrix"]
    T --> D["windows-dist: 1 job"]
    M --> S1["restore cache, configure, build"]
    S1 --> S2["shader check on Linux and macOS"]
    S2 --> S3["test with -LE gpu|perf"]
    S3 --> S4["save cache, remove old entries, annotate"]
    D --> D1["configure, build Dist, test -L package, annotate"]
```

The table reads the same jobs across. The Linux jobs use GCC 14. The last column answers "what does this job not test", which matters as much as what it does.

| Job | Machine | :term[Preset]{id=preset} and configuration | Compiler cache and key | Extra steps | Labels omitted |
| --- | --- | --- | --- | --- | --- |
| Windows | `windows-2022` | `windows-ninja`, Release | `sccache`, `windows-release` | developer environment | `gpu`, `perf` |
| Windows (Debug) | `windows-2022` | `windows-ninja`, Debug | `sccache`, `windows-debug` | developer environment | `gpu`, `perf` |
| Linux | `ubuntu-24.04` | `linux`, Release, GCC 14 | `ccache`, `linux-release` | `spirv-val` | `gpu`, `perf` |
| macOS | `macos-15` | `macos`, Release, Apple Clang 17 | `ccache`, `macos-release` | Metal conversion | `gpu`, `perf` |
| Linux without modules | `ubuntu-24.04` | `linux`, Release | `ccache`, `linux-without-modules-release` | four `-D` options | `gpu`, `perf`, `package` |
| Windows (:term[Dist]{id=dist} build) | `windows-2022` | `windows-vs2022`, Dist | none | none | runs only `package` |

Three facts in the table need a reason. Debug is built only on Windows: the file says Debug keeps the asserts and checks that Release drops, and no other job builds it. The sixth job has no cache because the Visual Studio generator ignores :term[compiler launchers]{id=compiler-launcher}, which is how a compiler cache attaches. And the job without modules builds a game that has no audio, no physics and no window backend, so it checks that the engine compiles, and its tests pass, with those optional modules off.

## The contract: what CI promises and what you must do

CI gives a small set of promises. Each has a reason, and three come from `AGENTS.md`, the engine's guide for its developers.

- **Every CI build treats warnings as errors.** Strata's compiler policy fails the build on any warning in first-party code, and CI never relaxes it. A warning that GCC 14 raises, and newer GCC versions do not, is still a failure on the Linux job.
- **The test step omits the `gpu` and `perf` labels.** A hosted runner has no GPU, and perf budgets hold only on the reference machine. A suite carrying either label never runs in CI, so you run `gpu` suites on a machine with a graphics card and `perf` suites on the reference machine.
- **A change that lands many commits goes through a `ci/<name>` branch.** You push the branch, wait for every job to end green, and only then move `main`.
- **A failure is read from its annotations.** The job log needs administrator rights; annotations are public.
- **Tests run whenever the build succeeded.** A failed :term[shader]{id=shader} check never hides the test results.

:::rule[CI before main]
`AGENTS.md` warns that an older compiler or another :term[standard library]{id=standard-library} can reject code that your own machine accepts. A branch that lands many changes therefore goes to `ci/<name>` first, and `main` moves only after green CI. The reason is that your compiler is one of several: a large integration holds many lines, and one line that one compiler rejects turns the whole main branch red. The branch costs one push and a wait. See [the page about flags and portability](flags-portability.md) for what the other compilers reject.
:::

## A toy version: a small workflow

The :term[file format]{id=file-format} is small enough to learn from a toy. A **workflow** is a file in the repository's `.github/workflows/` folder. It names the events that start it, and it holds one or more jobs. A job runs on one runner and holds steps: a step either runs a :term[shell command]{id=terminal-command} (`run`) or uses a ready-made action (`uses`).

The first toy has one job with four steps. Read the `on` block for what starts it, `runs-on` for the machine, and the order of the steps, which run one after another and stop at the first failure.

```yaml
name: Toy CI
on:
  push:
    branches: [main, 'ci/**']
  pull_request:
jobs:
  build:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v6
      - run: cmake --preset linux
      - run: cmake --build --preset linux-release
      - run: ctest --preset linux-release -LE "gpu|perf"
```

1. **Lines 2-5:** the events that start the workflow: a push to `main` or to a `ci/` branch, and every pull request.
2. **Line 8:** the runner image that GitHub starts for the job.
3. **Line 10:** `uses` runs a ready-made action, here the one that fetches the repository's files.
4. **Lines 11-13:** each `run` is a shell command, and the first one that fails ends the job.

The toy builds one configuration on one machine. A push to a branch named `feature/x` starts nothing, because only `main` and names that begin with `ci/` are listed under `push`. A pull request starts it whatever the branch is called.

To cover two configurations without copying the job, add a `strategy` with a `matrix`. Each entry of `include` is one job, and `${{ matrix.name }}` reads a field of the entry. The `if` line on a step is a condition: a step whose condition is false is skipped.

```yaml
jobs:
  build:
    strategy:
      fail-fast: false
      matrix:
        include:
          - { preset: linux, config: release, exclude: "" }
          - { preset: linux, config: debug, exclude: "|package" }
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v6
      - run: cmake --preset ${{ matrix.preset }}
      - id: build
        run: cmake --build --preset ${{ matrix.preset }}-${{ matrix.config }}
      - if: ${{ !cancelled() && steps.build.outcome == 'success' }}
        run: ctest --preset ${{ matrix.preset }}-${{ matrix.config }} -LE "gpu|perf${{ matrix.exclude }}"
```

1. **Line 4:** `fail-fast: false` lets every job finish when one fails.
2. **Lines 7-8:** each entry is one job, and its fields are read as `matrix.preset` and so on.
3. **Lines 13-14:** `id` names a step so that a later step can read its outcome, and `${{ ... }}` writes a field into the command.
4. **Line 15:** the tests run after an earlier failure only if the build itself succeeded, as in the real file.

The matrix makes two jobs from one description. `fail-fast: false` lets the second job finish when the first fails, so one run shows every broken configuration. The `exclude` field is added to the label pattern, the same trick the real file uses to leave `package` out of one job.

The toy omits everything that makes the real file long: dependencies to install, a compiler cache, shader checks, limits against runaway tests and annotations. The real file is the toy plus a reason for each addition, and the next section follows its data in order.

## The real code, in the order of a run

A run starts with the trigger. Read the quote for three facts: which pushes start CI, that pull requests start it too, and what the `concurrency` block does.

```yaml src=".github/workflows/ci.yml#L3-L11"
on:
  push:
    # ci/<name> branches run CI before a change lands on main (AGENTS.md, "CI before main").
    branches: [main, 'ci/**']
  pull_request:

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true
```

The `concurrency` group is named after the reference, such as `refs/heads/main` or the pull request's merge reference. With `cancel-in-progress`, a new push to a branch cancels the run still going for the same branch. An older run would only spend machine time on a commit that a newer push has replaced.

The matrix is next. Each `include` entry becomes a job whose fields are read as `matrix.name`, `matrix.preset` and so on. The quote shows the first Windows entry and the last job, the one with options.

```yaml src=".github/workflows/ci.yml#L23-L60"
      matrix:
        include:
          - name: Windows
            os: windows-2022
            preset: windows-ninja
            config: release
            cache: sccache
            key: windows-release
          # Debug builds keep the asserts and checks Release drops; no other job builds them.
          - name: Windows (Debug)
            os: windows-2022
            preset: windows-ninja
            config: debug
            cache: sccache
            key: windows-debug
          - name: Linux
            os: ubuntu-24.04
            preset: linux
            config: release
            cache: ccache
            key: linux-release
          - name: macOS
            os: macos-15
            preset: macos
            config: release
            cache: ccache
            key: macos-release
          # A game without the audio and physics modules and without a window backend (Docs/DeveloperGuide.md, "Optional
          # modules", "Platform seams"): no editor, and no package tests (they build games of every module).
          - name: Linux (no Audio, no Physics, no GLFW)
            os: ubuntu-24.04
            preset: linux
            config: release
            cache: ccache
            # Not prefixed by the Linux job's key: restoring by prefix must not cross between the two configurations.
            key: linux-without-modules-release
            options: -DSTRATA_WITH_AUDIO=OFF -DSTRATA_WITH_PHYSICS=OFF -DSTRATA_WITH_GLFW=OFF -DSTRATA_BUILD_EDITOR=OFF
            exclude: package
```

1. **Line 24:** `include` lists the jobs one by one. Setting each field by hand keeps the matrix a list of chosen configurations, not every combination of two axes.
2. **Line 27:** the `windows-ninja` preset builds with Ninja inside a developer environment, because the Visual Studio generators ignore compiler launchers and so cannot use `sccache`.
3. **Lines 29-30:** `cache` names the cache program and `key` the job's cache. The key of each job is distinct.
4. **Lines 50-52:** the comment says why a job without modules exists, and the job gets its own name.
5. **Lines 57-60:** the key is not prefixed by the Linux job's key, because restoring by prefix must not cross from one configuration to the other. `options` passes four `-D` switches to the :term[configure step]{id=configure-step}, and `exclude` adds `package` to the omitted labels.

The Linux job installs GCC 14 and `spirv-tools`, and the macOS job installs Ninja, `ccache` and MoltenVK with Homebrew. The Windows jobs need more: `windows-ninja` compiles with `cl` from the program path, and a bare runner does not have the Visual Studio environment ready. The step below finds Visual Studio with `vswhere`, runs `vcvars64.bat` and copies what it changed into the file named by `GITHUB_ENV`, which GitHub reads to set the variables of the later steps.

```yaml src=".github/workflows/ci.yml#L97-L113"
      - name: Enter the Visual Studio developer environment
        if: runner.os == 'Windows'
        shell: pwsh
        run: |
          $vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
          $installation = & $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
          if (-not $installation) { throw 'No Visual Studio with the C++ tools was found' }
          $variables = cmd /c "`"$installation\VC\Auxiliary\Build\vcvars64.bat`" > nul && set"
          if ($LASTEXITCODE -ne 0) { throw 'vcvars64.bat failed' }
          foreach ($line in $variables) {
            if ($line -notmatch '^([^=]+)=(.*)$') { continue }
            $name = $Matches[1]; $value = $Matches[2]
            if ($name -match '^(GITHUB_|RUNNER_|ACTIONS_)' -or $name -eq 'NODE_OPTIONS') { continue }
            if ([Environment]::GetEnvironmentVariable($name) -ne $value) {
              "$name=$value" | Out-File -FilePath $env:GITHUB_ENV -Append -Encoding utf8
            }
          }
```

1. **Line 99:** the step runs in PowerShell, `pwsh`, because the commands that find Visual Studio and read its variables are PowerShell commands.
2. **Lines 101-105:** it finds the newest Visual Studio with the C++ tools and fails with a message when none exists or `vcvars64.bat` fails.
3. **Line 109:** variables that GitHub itself uses (`GITHUB_`, `RUNNER_`, `ACTIONS_`) are skipped, so the batch file cannot replace them.
4. **Lines 110-112:** only variables that differ from the current value are appended, which keeps the later steps' environment small.

### The compiler cache

Both a restore and a save step surround the build. The restore uses two keys. Read both lines: the key is exact (the cache program, the job's key and the commit), and `restore-keys` is a prefix.

```yaml src=".github/workflows/ci.yml#L122-L127"
      - name: Restore the compiler cache
        uses: actions/cache/restore@v6
        with:
          path: ${{ runner.temp }}/compiler-cache
          key: ${{ matrix.cache }}-${{ matrix.key }}-${{ github.sha }}
          restore-keys: ${{ matrix.cache }}-${{ matrix.key }}-
```

GitHub searches for the exact key first. A new commit has no entry, so GitHub tries the prefix and returns the newest entry whose key starts with it, from the branch being built or, failing that, from `main`. The commit therefore starts from the cache of the previous commit of its branch, which is nearly right. A branch that has never been built starts from the main branch's cache.

The build comes after the configure step. Its command carries the one option that makes a CI run informative.

```yaml src=".github/workflows/ci.yml#L135-L141"
      - name: Build
        id: build
        shell: bash
        run: |
          set -o pipefail
          # Ninja keeps building after a failure, so one run reports every compile error.
          cmake --build --preset ${{ matrix.preset }}-${{ matrix.config }} --parallel -- -k 0 2>&1 | tee build.log
```

The option `-- -k 0` passes `-k 0` to Ninja, which means "keep going until zero jobs fail": after a :term[compile error]{id=compile-error} Ninja continues with every file that does not depend on the failed one. One run then reports all the compile errors of a change, not the first. Without it, a change with ten errors would cost ten pushes and ten waits.

Shader checks follow on two jobs. The Linux job runs only on the key `linux-release`, so the job without modules skips it. Read how each step asks for a different tool and reads the same list of embedded shaders.

```yaml src=".github/workflows/ci.yml#L146-L160"
      - name: Validate the embedded shaders
        if: matrix.key == 'linux-release'
        shell: bash
        run: |
          set -o pipefail
          bash .github/scripts/validate_shaders.sh build/${{ matrix.preset }}/Strata/EmbeddedShaders 2>&1 | tee shaders.log

      # No Mac with a GPU runs CI: every embedded module goes through MoltenVK's SPIR-V to Metal conversion and Apple's Metal
      # compiler, a lower bound of what MoltenVK does at run time (Docs/DeveloperGuide.md, "Shaders").
      - name: Convert the embedded shaders to Metal
        if: runner.os == 'macOS'
        shell: bash
        run: |
          set -o pipefail
          bash .github/scripts/convert_shaders_to_metal.sh build/${{ matrix.preset }}/Strata/EmbeddedShaders "${{ runner.temp }}/metal" 2>&1 | tee metal.log
```

1. **Line 147:** only the job with the key `linux-release` validates shaders. The condition reads a matrix field, not the operating system, so the second Linux job does not repeat it.
2. **Line 151:** the script gets the folder of embedded shaders that the build wrote, the final modules after the shader tool patched some.
3. **Line 156:** the macOS job runs the conversion step. No Apple computer with a GPU runs CI, so the step compiles the converted source with Apple's Metal compiler as the next best check.
4. **Line 160:** the same folder goes to the second script together with a scratch folder for the converted sources.

The Linux step uses **spirv-val**, the checker of the SPIR-V tools: it checks that a shader module obeys the rules of the binary format and of one target environment. The call in `validate_shaders.sh` is `spirv-val --target-env vulkan1.2`, run for every entry of `ShaderEntries.txt`. The compiler already validates its output, but the tool that embeds shaders patches some of them afterwards, and the compiler's archive has no `spirv-val`, so the patched modules are checked here. The shader dialect and the engine's own shader checks are on [the shader page](../gpu/shaders.md).

On macOS, `convert_shaders_to_metal.sh` holds a list named `c_KnownFailures`: modules that the converter refuses when it runs alone, because MoltenVK configures its argument buffers at run time, which a conversion made ahead of time cannot know. A listed failure prints a line that starts `known failure:`, not an error line, so the annotations do not fill with expected lines. The list only shrinks: the script fails when a listed module now converts and compiles, so nobody forgets to delete its entry. How MoltenVK works at run time is on [the Vulkan page](../gpu/vulkan-nvrhi.md).

### Saving the cache and keeping main's set

After the build, the job saves the cache and then deletes the older entries of its branch. The comment before the delete step says why: GitHub removes entries by last access, and an old entry of the branch was restored more recently than the entries of `main`. Left alone, the branch's old entries would last longer than `main`'s.

```yaml src=".github/workflows/ci.yml#L169-L193"
      - name: Save the compiler cache
        if: ${{ !cancelled() }}
        uses: actions/cache/save@v6
        with:
          path: ${{ runner.temp }}/compiler-cache
          key: ${{ matrix.cache }}-${{ matrix.key }}-${{ github.sha }}

      # Each run saves a new entry. GitHub evicts by last access, and a superseded entry of this ref was restored more
      # recently than main's, so it would outlive main's set: this ref's older entries of this job go. The key must match
      # exactly (a commit hash after the prefix), so that no other job's entries are taken for this one's.
      - name: Remove superseded compiler caches
        if: ${{ !cancelled() }}
        continue-on-error: true # A pull request from a fork has a read-only token: a failed cleanup must not fail the build.
        shell: bash
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          prefix="${{ matrix.cache }}-${{ matrix.key }}-"
          current="${prefix}${{ github.sha }}"
          gh cache list --repo "${{ github.repository }}" --ref "${{ github.ref }}" --key "$prefix" --limit 100 --json id,key \
            --jq ".[] | select((.key | test(\"^${prefix}[0-9a-f]{40}\$\")) and .key != \"${current}\") | .id" |
            while read -r id; do
              echo "Deleting the superseded cache entry $id"
              gh cache delete "$id" --repo "${{ github.repository }}"
            done
```

1. **Line 170:** `!cancelled()` saves the cache even after a failed test, so a failing test does not cost the next run its cache.
2. **Line 174:** the key is exact, ending with the commit, so each run writes a new entry.
3. **Line 181:** `continue-on-error` is there because a pull request from a fork has a read-only token and cannot delete. A failed cleanup must not fail the build.
4. **Lines 186-189:** the filter keeps keys that equal the prefix followed by forty :term[hexadecimal]{id=hexadecimal} digits and are not the current key. No other job's entries match.
5. **Lines 190-193:** each remaining entry of this reference is deleted with `gh cache delete`.

:::example[How long main's set survives]
Take the figures in the file's comments, read here as MB. A full set of one run is five entries: three `ccache` jobs at 33 to 71 MB each and two `sccache` jobs at 470 to 582 MB each. The largest set is 3 × 71 + 2 × 582 = 1,377 MB, and the smallest is 3 × 33 + 2 × 470 = 1,039 MB.

GitHub's limit is 10 GB, which this example takes as 10,240 MB. Without cleanup, a branch adds the largest set, 1,377 MB, with every push, and main's set sits at the bottom of the used list. After seven pushes the store holds main's set and seven of the branch's, 8 × 1,377 = 11,016 MB, which is over the limit. GitHub deletes the least recently used entry, and that is main's. The next push to main then builds cold.

With cleanup, each branch keeps one set. The limit holds 10,240 / 1,377, about 7.4 sets, so the store fits main and six active branches before GitHub removes anything. The sizes in `CCACHE_MAXSIZE` and `SCCACHE_CACHE_SIZE` cap one set at 3 × 250 + 2 × 1,000 = 2,750 MB, a bound that holds even when the measured sizes grow.
:::

```mermaid caption="Each job restores the newest entry with its key prefix from its own branch or from the main branch. It saves a new entry named after the commit and deletes the older entries of its branch, so the main branch's entry is not the least recently used." alt="Two columns, one for the main branch and one for a feature branch, each holding cache entries. An arrow from the older main entry goes into the first run of the feature branch, which then saves a new entry. Each later run restores the feature branch's newest entry, saves a new one and deletes the older one."
flowchart LR
    M["main: entry of commit M"] -- "first run restores by prefix" --> R1["run 1 of a branch"]
    R1 -- "saves" --> E1["branch entry of commit 1"]
    E1 -- "run 2 restores it" --> R2["run 2"]
    R2 -- "saves" --> E2["branch entry of commit 2"]
    R2 -- "deletes" --> E1
```

### The test step

The tests run after the build and the shader steps. The long comment at the top of the step is part of the contract: read what it says about hosted runners, perf budgets and failed shader steps before the code below.

```yaml src=".github/workflows/ci.yml#L200-L215"
      - name: Test
        if: ${{ !cancelled() && steps.build.outcome == 'success' }}
        shell: bash
        env:
          STRATA_TEST_TRACE: "1" # Tests print each test case as it starts, so a crash names its test
        run: |
          set -o pipefail
          # Linux overcommits memory: a test that runs away with memory or disk would take the whole runner down (the
          # job ends with exit code 143 and no annotations). Limits make such a test fail on its own instead.
          if [ "$RUNNER_OS" = "Linux" ]; then
            ulimit -v 10000000 # KiB of address space per process
            ulimit -f 2097152  # KiB per file
          fi
          exclude="gpu|perf"
          if [ -n "${{ matrix.exclude }}" ]; then exclude="$exclude|${{ matrix.exclude }}"; fi
          ctest --preset ${{ matrix.preset }}-${{ matrix.config }} -LE "$exclude" -j 4 --output-on-failure --timeout 900 2>&1 | tee test.log
```

1. **Line 201:** the step runs when the run was not cancelled and the build succeeded. A failed shader step does not skip it, so a shader finding never hides the test results.
2. **Line 204:** `STRATA_TEST_TRACE` makes the test program print each test case as it starts, so a crash names its test. The page about the test program explains the trace.
3. **Lines 209-212:** on Linux, `ulimit -v` limits the address space of each process to about 10 GB and `ulimit -f` limits each file to 2 GB. Linux lets a program claim more memory than the machine has, so a runaway test would otherwise take the whole runner down. The comment says such a job ends with :term[exit code]{id=exit-code} 143 and no annotations.
4. **Lines 213-214:** the omitted labels start as `gpu|perf`, and the matrix field `exclude` adds more, which is how the job without modules also omits `package`.
5. **Line 215:** `ctest -LE "$exclude" -j 4 --output-on-failure --timeout 900` runs four tests at a time, prints a failing test's output and stops any test after 900 s.

The four at a time come from the shards of the test program, which split the Core suites so that four processes keep the runner busy. The `-LE` option takes a :term[regular expression]{id=regular-expression} and skips every test with a label that matches. The page about the test program has the labels, the shards and the trace in detail.

### Failure annotations

The last step of each job runs when a step failed or the run was cancelled. It passes the logs of the job's earlier steps to a Python script.

```yaml src=".github/workflows/ci.yml#L219-L224"
      - name: Annotate failures
        if: failure() || cancelled()
        shell: bash
        run: |
          python=$(command -v python3 || command -v python)
          "$python" .github/scripts/annotate_failures.py configure.log build.log shaders.log metal.log test.log
```

The script, `annotate_failures.py`, reads each log that exists and skips those that do not.

The script recognizes error lines of GCC and Clang (`path:line:column: error:`), of the Visual Studio compiler (`path(line): error C1234:`), of :term[doctest's]{id=doctest} failed assertions, and of the shader compiler, whose error and location sit on two lines. For each of the first five errors it finds, it prints a workflow command, `::error file=…,line=…::message`, which GitHub turns into an annotation on that line of that file.

The script adds one annotation that lists the test cases with errors and up to three summary annotations that hold the lines around each error and the end of a crashed test's output.

The limits come from GitHub: an annotation's message is cut at 4,096 :term[bytes]{id=byte} and a step may show 10 error annotations. The script keeps its pieces under 3,900 bytes. The lines that begin `known failure:` match no error pattern, so they do not take any of the five places.

:::example[A failure read without a log]
Imagine a push whose Linux job fails with one sign-compare error in `Scene.cpp` at line 412. The script, run on a log with that one error, prints this line, which GitHub shows on the file.

```text
::error file=Strata/src/Strata/Scene/Scene.cpp,line=412,col=21::comparison of integer expressions of different signedness: 'int' and 'size_t' [-Werror=sign-compare]
```

The file, line, column and message are all there, so you can fix the line without ever opening the job's log. The same run also prints a `Failure summary` annotation with the lines around the error. A line such as `known failure: Scene/Forward.frag: metal: …` in a macOS job's log produces nothing, because it names no error.
:::

### The Windows Dist job

The sixth job stands apart. A release ships the Dist configuration, where asserts are compiled out and code guarded by `ST_DIST` is in. For a while only the release workflow built it, and a change that compiled with asserts on alone broke Dist in wave 3 without anyone noticing. This job builds every target in Dist on every push.

```yaml src=".github/workflows/ci.yml#L241-L259"
      - name: Configure
        shell: bash
        run: |
          set -o pipefail
          cmake --preset windows-vs2022 2>&1 | tee configure.log

      - name: Build (Dist)
        shell: bash
        run: |
          set -o pipefail
          cmake --build --preset windows-vs2022-dist --parallel 2>&1 | tee build.log

      - name: Test packages (Dist)
        shell: bash
        env:
          STRATA_TEST_TRACE: "1"
        run: |
          set -o pipefail
          ctest --preset windows-vs2022-dist -L package --output-on-failure --timeout 1800 2>&1 | tee test.log
```

1. **Line 245:** it configures the `windows-vs2022` preset, the Visual Studio generator that people use to build, with no compiler cache.
2. **Line 251:** the preset `windows-vs2022-dist` builds every target in Dist.
3. **Line 256:** the trace is on here too.
4. **Line 259:** only the tests labelled `package` run, with a timeout of 1,800 s, twice the main job's, because a package test builds whole games.

The job has a second reason. Script builds take the generator that the editor was built with, and the other five jobs build with Ninja. The package tests of this job are therefore the only ones that build scripts through the Visual Studio generator. How a script build picks its generator is on [the page about script builds](../editor/script-builds.md).

### Reading a commit's CI from a terminal

`Tools/CIStatus.py` reads the results through GitHub's API. It takes a command and a commit: a short or full :term[hash]{id=hash}, or a branch name. `status` prints one line per run and job with the failed steps. It exits with 0 when every run completed, 3 while something still runs or no run has started yet, and 2 on an error. A completed run can still have failed, so read the jobs' lines too.

The command `annotations` prints the failure annotations of the jobs that did not succeed, and `--all` adds every annotation of every check run. The tool takes a token from `GH_TOKEN` or `GITHUB_TOKEN`, or from `gh auth token`, and never prints it. Without a token, GitHub allows 60 requests an hour.

### What CI does not check

Two things that a reader may expect are missing. No job builds with a checker for memory errors and undefined behaviour, such as `AddressSanitizer` or `UndefinedBehaviorSanitizer`, so nothing finds the faults that warnings do not show. The annotation script knows the word `Sanitizer` in a log, but no build produces one.

No job checks formatting: neither CI nor a test runs `clang-format`, so `.clang-format` and `.editorconfig` act only in editors that read them, although `AGENTS.md` calls the formatting enforced.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Self-hosted runner with a GPU | Teams that own build machines; GitHub documents the setup | The `gpu` suites in CI | A machine to maintain, and code from pull requests running on it |
| Checked builds | Projects that run `AddressSanitizer` or `UndefinedBehaviorSanitizer` in CI; the manuals of Clang and GCC describe them | Memory and undefined-behaviour errors found on every push | A slower build and slower tests |
| A format check job | Projects that run `clang-format` and fail a :term[diff]{id=diff} | The formatting rule the guide calls enforced would be enforced | A job that fails changes for spacing, and a pinned `clang-format` version |
| Required checks and a merge queue | Repositories that use GitHub's branch rules | No change reaches `main` unless the jobs pass, without a person remembering | Setup in GitHub, and a queue that slows landing a wave |
| A remote build cache | Large :term[build systems]{id=build-system} with a shared cache server | Warm builds that do not depend on GitHub's 10 GB store | A server to run and secure |
| Cancelling siblings on failure (`fail-fast: true`) | The default of GitHub's matrix | Machine time saved | One run would show one broken configuration, not all |

## How it is tested

CI is checked by running it; no unit test reads `ci.yml`. A change to the workflow, to its three scripts or to `Tools/CIStatus.py` is tested by pushing a `ci/<name>` branch and reading the result, which is what the contract asks for anyway. The scripts take plain inputs, so you can run them on your machine. `annotate_failures.py` takes log files, and `validate_shaders.sh` takes the folder `build/<preset>/Strata/EmbeddedShaders` of a built tree.

The tests that CI runs are the ones the other pages describe. The Core shards, the end-to-end and the package suites run in the jobs above, and the engine's developer guide adds that every job except the Dist build also runs `StrataShaders.TargetHLSL` and `StrataTools.LookDevOffline`. To run what a job runs, use the same preset and labels:

```sh
ctest --preset linux-release -LE "gpu|perf" -j 4 --output-on-failure --timeout 900
```

On Windows the preset is `windows-ninja-release`, and you run it from a developer environment. The command prints the output of a failing test, which is the part the annotation script copies.

## Changing it safely

The workflow is code with a delayed feedback loop: a mistake shows only after a push. Change it in a branch named `ci/<name>`, wait for the whole run, and read the result of every job, not only the one you edited. Before you change it, check the rules below.

- **Keep the matrix a list.** A new job is a new `include` entry with its `preset`, `config`, `cache` and `key`. Give it a key that is not a prefix of another job's key, as the comment at line 57 explains, or its restore would take another configuration's cache.
- **Keep the cleanup exact.** The delete filter matches a forty-digit commit hash after the prefix. A looser filter could delete another job's entries, and a missing one would let `main`'s set be removed.
- **Do not give a suite a label that CI omits without a reason.** A suite labelled `gpu` or `perf` never runs on a hosted runner, so it must join the routine of a machine that runs it.
- **Do not hide a failure.** A new step that can fail needs its log in the final `annotate_failures.py` call, or the annotation step cannot read it.
- **Keep the list of known Metal failures shrinking.** Add a module to `c_KnownFailures` only with the converter's reason beside it. Remove it when the script says it now converts.
- **Append, do not rename, the job names.** The job names are what `CIStatus.py` prints and what branch rules would name.

When you add a job that needs a package, install it in a step guarded by `runner.os` and add it to the matrix as a field, so that the other jobs stay unchanged.

## What went wrong before

Three incidents shaped the file. In wave 3, a change compiled with asserts on and broke the Dist configuration, which only the release workflow built, so nobody saw it for a while. The `windows-dist` job exists because of that, and it was kept for the second reason, the Visual Studio generator's script builds.

Apple Clang 17 assumed that a value picked by `std::abs(x) > 0 ? x : 0` is never negative, and so dropped a later `std::abs` of it. Every gamepad axis held to its negative side then read 0 in the input actions. The macOS job found it in CI run 42634304897. The developer guide's remedy is to compare the values with each other and never with a running value that starts at 0.

The third is the runaway test. A test that used all the memory or disk of a Linux runner ended the job with exit code 143 and no annotations, and so with no failure to read. The `ulimit` lines in the test step make such a test fail alone, with its name in the trace. The regression guard is the step itself: it runs on every push.

## Summary

- CI builds every push to `main`, every pull request and every push to a `ci/` branch, in five matrix jobs and one Dist job. The test step omits the `gpu` and `perf` labels, because a hosted runner has no GPU and is not the reference machine.
- A job's keys (`preset`, `config`, `cache`, `key`, `options`, `exclude`) lead to its configure command, its cache and the exact `ctest` command line of its test step.
- Each job restores a cache by prefix, saves it even when tests fail and deletes its branch's older entries, so `main`'s set stays inside GitHub's 10 GB.
- Failures are read from annotations, because job logs need administrator rights, and `Tools/CIStatus.py` prints them.
- A branch that lands many changes goes through a `ci/<name>` branch and moves `main` only after every job is green.

## Check yourself

1. The job named "Linux (no Audio, no Physics, no GLFW)" runs a `ctest` command. Which labels does it omit, and from which keys of the matrix does the command take them?

   - (a) `gpu` only, from the preset.
   - (b) `gpu`, `perf` and `package`, from the fixed pattern and the `exclude` field.
   - (c) `perf` and `package`, from `exclude`.
   - (d) None, because it builds without an editor.

   :::answer{tests="ci-checks,trace-job"}
   The answer is b. The step starts with `gpu|perf`, which every job omits, and then appends `|package` when `matrix.exclude` is not empty, which only this job sets. Option a forgets that `perf` is fixed too. Option c forgets that `gpu` is fixed. Option d confuses the build option `STRATA_BUILD_EDITOR=OFF` with a label.
   :::

2. You push a branch named `feature/fog` to the repository and open no pull request. Does CI run? What changes when you rename the branch `ci/fog`?

   :::answer{tests="ci-checks"}
   Nothing runs for `feature/fog`: the `push` trigger lists `main` and `ci/**` only, and no pull request exists. After the rename, the push matches `ci/**`, so all six jobs start. Opening a pull request would start them for `feature/fog` too, through the `pull_request` trigger.
   :::

3. Each full set of caches measures at most 1,377 MB, and the store holds 10,240 MB. Main holds one set. A branch pushes without any cleanup step. After which push is `main`'s set the one GitHub deletes, if each push saves one new set and nothing else is stored?

   :::answer{tests="cache-budget"}
   After the seventh push. After push $n$ the store holds the main set and $n$ branch sets, $(n + 1) \times 1{,}377$ MB. For $n = 6$ that is 9,639 MB, which fits. For $n = 7$ it is 11,016 MB, which is over 10,240 MB, and GitHub deletes the least recently used entry, which is the one of `main`.
   :::

4. A job fails and you cannot open its log. Which is the best next step?

   - (a) Ask an administrator to download the log.
   - (b) Push again with more output.
   - (c) Run `python3 Tools/CIStatus.py annotations <commit>` and read the failure annotations.
   - (d) Wait for the cache to refresh.

   :::answer{tests="read-failure"}
   The answer is c. The annotation step turned the job's logs into public annotations, with the file, line and message of the first errors, and the tool prints them. Option a works but needs another person. Option b spends a wait and shows the same annotations. Option d has no relation to a failure.
   :::

5. A teammate has a wave of 40 commits that pass every test on their machine. They plan to merge to `main` at once. What do you advise, and why?

   :::answer{tests="ci-branch"}
   Push the work as `ci/<name>` first and merge only when every job is green. The local run used one compiler, but CI builds with GCC 14, Apple Clang 17 and the Visual Studio compiler, which reject different lines, and with warnings as errors. A red `main` stops everybody who pulls it, and the branch costs one push and a wait.
   :::

## Exercises

1. **Basic.** Find the failure of one real push from its annotations alone. Pick a commit of your fork that has CI runs, run `status` on it, then `annotations`, and write what failed, in which file and line, and which job reported it.

   :::answer[Worked solution]{tests="read-failure"}
   Run `python3 Tools/CIStatus.py status <commit>`. It prints one line per run and job, and a line `step <name> failure` under each job that failed.

   Then run `python3 Tools/CIStatus.py annotations <commit>`. For each job that did not succeed, it prints `--- <file>:<line> <title>` and the message. A located error gives the file and line directly. A `Failure summary` annotation holds the lines around the error and the end of the log. If `status` exits with 3, the runs are not finished: wait and run it again.
   :::

2. **Medium.** Trace it yourself. Search `.github/workflows/ci.yml` for the job "Linux (no Audio, no Physics, no GLFW)" and follow it from its `preset`, `config`, `options` and `exclude` to the test step's `ctest` command line. Write the line with every value written out, and say which labels the job omits and why.

   :::answer[Worked solution]{tests="trace-job"}
   The job is the last entry of `matrix.include`. Its fields give `preset: linux`, `config: release` and `exclude: package`; its `options` go to `cmake --preset linux -DSTRATA_COMPILER_CACHE=ON …` in the Configure step. The Test step builds `exclude="gpu|perf"`, appends `|package` because `matrix.exclude` is not empty, and runs `ctest --preset linux-release -LE "gpu|perf|package" -j 4 --output-on-failure --timeout 900`, after two `ulimit` lines because the runner is Linux. It omits `gpu` (no GPU on a hosted runner), `perf` (budgets hold on the reference machine) and `package` (package tests build games of every module, and this job has no editor and no modules). The file is `.github/workflows/ci.yml`, the step is "Test".
   :::

3. **Hard.** Write a program that models GitHub's cache with a limit of 10,240 MB and sets of 1,377 MB. It restores the newest set of the branch, saves a new one and removes the least recently used set when the store is over the limit. Run it with and without deleting the branch's old sets, and print the push on which `main`'s set is removed.

   :::question
   The program uses a :term[struct]{id=struct}, a vector, loops and :term[function calls]{id=function-call}: see [the first programming page](../basics/programming-1.md) and [the third](../basics/programming-3.md) for the parts you need.
   :::

   :::answer[Worked solution]{tests="cache-budget"}
   The model keeps each entry's size and the time of its last use. A push restores the branch's newest entry, or main's when the branch has none, which updates that time. It saves a new entry, deletes the branch's older entries when cleanup is on, and removes the oldest by time while the total is above the limit.

   ```cpp sketch="engineering-ci-eviction.cpp"
   #include <cstdio>
   #include <vector>

   struct Entry
   {
   	bool IsMain = false;
   	int Megabytes = 0;
   	int LastUsed = 0;
   };

   static int PushWhereMainIsEvicted(bool deleteOldEntries)
   {
   	const int limit = 10240;
   	const int setSize = 1377;
   	std::vector<Entry> cache = { { true, setSize, 0 } };
   	for (int push = 1; push <= 50; push++)
   	{
   		// Restore: the newest entry of the branch, else main's. Either counts as used now.
   		Entry* newest = &cache.back();
   		newest->LastUsed = push;
   		cache.push_back({ false, setSize, push });
   		if (deleteOldEntries)
   		{
   			// Keep only main's entry and the one just saved.
   			std::vector<Entry> kept;
   			for (const Entry& entry : cache)
   				if (entry.IsMain || entry.LastUsed == push)
   					kept.push_back(entry);
   			cache = kept;
   		}
   		int total = 0;
   		for (const Entry& entry : cache)
   			total += entry.Megabytes;
   		while (total > limit)
   		{
   			size_t oldest = 0;
   			for (size_t i = 1; i < cache.size(); i++)
   				if (cache[i].LastUsed < cache[oldest].LastUsed)
   					oldest = i;
   			if (cache[oldest].IsMain)
   				return push;
   			total -= cache[oldest].Megabytes;
   			cache.erase(cache.begin() + static_cast<long>(oldest));
   		}
   	}
   	return 0;
   }

   int main()
   {
   	std::printf("without cleanup: main is evicted at push %d\n", PushWhereMainIsEvicted(false));
   	std::printf("with cleanup: main is evicted at push %d (0 means never)\n", PushWhereMainIsEvicted(true));
   	return 0;
   }
   ```

   ```text output-of="engineering-ci-eviction.cpp"
   without cleanup: main is evicted at push 7
   with cleanup: main is evicted at push 0 (0 means never)
   ```

   1. **Lines 19-21:** the restore marks the newest entry as used now, and the save adds a new entry.
   2. **Lines 22-29:** with cleanup on, only main's entry and the new one stay, as the delete step leaves them.
   3. **Lines 34-39:** while the store is over the limit, the loop finds the entry used longest ago.
   4. **Lines 40-41:** when that entry is main's, the function returns the push number.
   :::

## Where it lives in Strata

- `.github/workflows/ci.yml`: the triggers, the matrix, every step and the Dist job.
- `.github/scripts/annotate_failures.py`, `validate_shaders.sh`, `convert_shaders_to_metal.sh`: failure annotations, the `spirv-val` step and the Metal conversion with `c_KnownFailures`.
- `Tools/CIStatus.py`: the status and annotations of a commit's runs. `Tools/CompatLint.py`: the check to run before a push.
- `CMakePresets.json`: the presets and test presets named by the matrix, such as `windows-ninja`, `linux-release` and `windows-vs2022-dist`.
- `CMake/StrataCompilerOptions.cmake`: `STRATA_COMPILER_CACHE`, the switch the Configure step enables.
- `StrataTests/CoreShards.json`: the shards that CI runs four at a time.

## Further reading

- GitHub Docs, "Workflow syntax for GitHub Actions": every key of a workflow file, including `strategy`, `concurrency` and `if` (beginner to intermediate).
- GitHub Docs, the page on caching dependencies: keys, restore keys and the repository's cache limit and eviction (intermediate).
- GitHub Docs, "Workflow commands for GitHub Actions": the `::error` command that makes an annotation (intermediate).
- The manuals of `ccache` and `sccache`: how a compiler cache decides that two compiles are the same (intermediate).
- Ninja's manual, the `-k` option: how a build keeps going after a failure (beginner).
