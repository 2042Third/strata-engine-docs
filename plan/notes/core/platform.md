# Notes: `core/platform`

## New terms

- **seam**: a place where two parts of a program meet and one side can change without the other noticing; Strata's seam
  to the operating system is the class `Platform`. Home: `core/platform`. Aliases: platform layer, seams.
- **console subsystem**: the kind of Windows program that gets a console, which a shell waits for. Home:
  `core/platform`. Aliases: console program.
- **GUI subsystem**: the kind of Windows program that gets no console, which a shell does not wait for. Home:
  `core/platform`. Aliases: GUI program, GUI programs, windowed program.
- **signal**: the message a POSIX system sends a process for an event such as Ctrl+C (`SIGINT`) or a request to end
  (`SIGTERM`). Home: `core/platform`. Aliases: signals. (The brief's items `foundation:624` and `scripting:609` home
  it here; the terms table of the brief does not list it, so the page defines it in bold and proposes it.)
- **console control handler**: the function a Windows program registers to learn of Ctrl+C, Ctrl+Break and the closing
  of its console. Home: `core/platform`.

The page also defines the four terms the brief lists: async-signal-safe, power throttling (EcoQoS), scheduling
quantum and thread priority.

## Requests

- Word-list: "subsystem" (in "console subsystem" and "GUI subsystem", proposed above). The finding is left until the
  two terms exist.
- Hosts for Further reading, cited without a link: `man7.org` (the manual page signal-safety(7)) and `glfw.org` (the
  GLFW documentation).
- `tools/data/names.txt`: Jason Gregory (author named in Further reading); the Further reading entries are not read.

## Since

`since: 0.3.0`. `Platform.h` came with the first commit (`a0f2865f`, in `v0.3.0`); `InstallInterruptHandler` with
`6013314c` and `ConnectStandardStreams` with `5e898c89`, both in `v0.3.0`. Later changes: `SleepUntil` (after `v0.7.0`,
so in 0.8.0), thread priorities and the power-throttling opt-out, whose first tags were not checked.

## Not verified

- The figure `headless-run` is taken now (see "Figures"); the Ctrl+C run of the example was not run.
- The statements that PowerShell returns at once for a GUI program, and why a pipe changes that, come from the
  engine's guide (`Docs/DeveloperGuide.md`, "Windows subsystem"), not from a test.
- The values of a scheduling quantum ("a few milliseconds to tens of milliseconds"), "Windows has no signals of that
  kind", and the exit code convention 128 plus the signal number are general operating-system knowledge, not engine
  facts.
- The Alternatives table names Godot's `OS` class, `SDL`'s thread priorities and message boxes, and the pattern of a
  thread that waits for signals from memory; the table row for the signal-waiting thread was cut for size, the other
  two stand. The Further reading links to Microsoft's pages were not fetched.
- The Windows closing wait of "at most 5 seconds" comes from the comment at `WindowsPlatform.cpp` lines 722-724.
- Exercise 3 (`GetHostName`) is a description; its code was not compiled, and `GetComputerNameExW` with
  `ComputerNameDnsHostname` and `gethostname` with `HOST_NAME_MAX` are from memory of the system interfaces.
- The simulated pacer of the sketches `core-platform-tick.cpp` and `core-platform-caps.cpp` follows the schedule of
  `FramePacer::WaitForNextFrame` (`Strata/src/Strata/Core/Timer.h`) and a sleep that wakes at the next tick; it is a
  model, and the 95 frames at a cap of 120 are the model's count, not a measurement of the engine.

## Figures

- `headless-run` (text), published in round 2. Round 1: two runs differed in the automation port
  (`127.0.0.1:51698` against `51701`) and the start-up time (`Started in 0.27 s` against `0.24 s`); the recipe now
  redacts those and the time stamps (each replaced by `…`, the brackets kept), and the caption and alt say so. The
  output is of the pin's Release build on this machine (RTX 5090, 23 workers); exit code 0, eleven lines, the last three
  the shutdown (`RpcServer: stopped`, `Automation: stopped`, `AudioEngine: shut down`).
- For the page's writer: the example says each line reads `[time] [level] Strata: message`; the logger's name is
  `Strata` for engine lines and `App` for the editor's own (4 of the 11 lines). The output names no frame count, so
  "ends by itself after its last frame" rests on the exit and the shutdown lines.
- `headless-run`, mended after a viewer's look (no retake: the output is unchanged): the caption now says the run was
  left alone (no Ctrl+C, no warning), that the logger is `Strata` on engine lines and `App` on the editor's, and that
  the threads and the graphics device are the book's machine's. Still for the page's writer: put "Left alone, the run
  logs:" before the fence in place of "The log reads:", and word the example's line as `[time] [level] <logger>:
  message`.
- `headless-run`, retaken at the pin v0.8.0 (`319075e3`) in one round: the same eleven lines, exit code 0; the only
  change from the 822a7a46 take is line 1, `Strata Editor 0.8.0 (Windows)` in place of `0.7.0`. Published; `fill`
  updated the page's fence. Caption, alt and recipe unchanged.
- `headless-run`, mended after a viewer's look (no retake: the output is unchanged): note 2 says lines 9–11 show exit
  code 0, but the log prints no exit code. A text recipe of a program (`program`, `arguments`, `redact`, `measured`)
  has no field that appends one, and `take_text_program` drops the code, so the recipe cannot show it; the take's logs
  (`log/0005-StrataEditor.log`, `0006`) record exit code 0 for both runs. The caption now says "the shell, not the log,
  reports its exit code" (no number: the lint asks a caption's numbers to come from stats), and is shortened to keep
  the page within size L (6,496 words). For the page's writer: word note 2 as "Lines 9–11: The run ends at
  frame 120 with the services stopping and no warning; the shell then reports exit code 0, which the log does not
  print."

## Findings not applied

The brief lists no open findings.

Items left out for size: `Platform::IsExecutionSpeedThrottlingDisabled` is not described on the page.

## Clerk

- Admitted: seam (alias "platform layer" left out: no bold use on the page). `extra-words.txt`: subsystem, subsystems (the four terms of "The contract" are not admitted, see below).
- `external-hosts.txt`: `man7.org` (front page fetched: Michael Kerrisk's man7.org), `www.glfw.org` (front page fetched; the asked `glfw.org` is the same site, write `www.glfw.org`).
- `names.txt`: "Jason Gregory" passes already.
- Not admitted, because the page check would then fail and the page is the writer's: console-subsystem (the section "The contract" would define 8 terms (term-section), and its paragraph 2 with GUI subsystem); gui-subsystem (the section "The contract" would define 8 terms (term-section)); signal-core (the section "The contract" would define 8 terms (term-section), and its paragraph 2 with console control handler); console-control-handler (the section "The contract" would define 8 terms (term-section)). The part's reviewer splits the paragraph or section; the next clerk admits it then (the entries are in the wave-1b clerk's apply.py).
