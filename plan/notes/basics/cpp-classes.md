# Notes: `basics/cpp-classes`

## New terms

- **slicing**: what happens when a derived object is copied into a base value: the copy keeps only the base part and loses the derived part and its virtual behavior. Home: `basics/cpp-classes`. Aliases: slice, sliced.
- **virtual table**: a table, made once per class, that lists the address of each virtual function of that class; a hidden pointer in each object leads to it. Home: `basics/cpp-classes`. Aliases: vtable, virtual tables.

The page also defines the glossary's entries homed here: virtual function, pure virtual function, abstract class, interface, polymorphism, operator overloading, and in bold `inheritance` (homed on `basics/programming-3`, used in its words).

## Requests

- None. The word-list findings of the first run (typo, vertices, instantiated, standalone) were reworded away.

## Not verified

- The Coin Run starting state (the names of its scripts, how its coins and player collide): the Practice item 5 is written without them and says "your Coin Run project".
- The playground's layout for exercises 1 to 4 (classes above the script class, objects made in `OnCreate`): follows `basics/programming-1`'s description and was not run.
- That the sketches' sizes (4 and 16 bytes) hold on every platform: they are the output on a 64-bit machine; the page says so.
- That a script class may derive from another script class that is not registered (`Pickup`): read from `Script.h` (`GetScript` asks the host for the class registered under `T`'s name; `static_assert` needs only `std::is_base_of_v<Script, T>`); never built or run.

## Findings not applied

- None. `critic-basics-a-14` holds at the pin (`Script.h` lines 816-828, `ScriptHostAPI.cpp` lines 962-969) and is applied in exercise 5: `GetScript<Coin>()` and `GetScript<SpeedBoost>()` convert to `Pickup*`, and `Pickup` is not registered with `ST_SCRIPT_CLASS`.

## Requests for figures

- None: the one drawing is a Mermaid diagram on the page.

## Clerk

- Admitted: slicing (aliases "slice" and "sliced" left out: everyday words), virtual table (aliases vtable, virtual tables).

## Track walk E-final-2

Each sketch of the page compiled warning-free with `cl /std:c++20 /EHsc /W3` (Visual Studio 2026, 19.50, x64) and with g++ 15 `-std=c++20`; both printed the same output (`docs-work/walkfix-E2/cl/`, 2026-11-24, 60 sketches of the four C++ pages).

Up-to-date builds (WK10): reproduced with the official 0.8.0 package, headless, under the perf lock (`docs-work/walkfix-E2/session.ps1`, `session.out`): of the walker's 18 exercise files, written with verified bytes, one (`g1bad`, which cannot compile) built `success`, `moduleChanged: false`, and the Console line ends `Script build 12 finished in 0.6 s (the module was up to date)`. The work folders lie on G:, an exFAT drive, which stores file times rounded to 2 seconds (18:39:37.456 reads back 18:39:38.000; NTFS keeps 18:39:37.456), so a file saved within about 2 seconds of the last build's object file is no newer than it, and MSBuild skips it. Not an engine fault: the build's file-time rule (basics/build) on a coarse file system. The Practice intro says what the reader sees and does.

Exercise 5 now runs in `Playground` with `Star` and `SpeedBoost` (the name `Coin` would clash with Coin Run's `Coin`, `Gem` with exercise 1). Run as a script with the package (`variants/hc.cpp`): `Star: GetScript<Pickup> is null: true`, `star collected`, `Boost: GetScript<Pickup> is null: true`, `speed boost collected`.
