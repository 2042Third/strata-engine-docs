# Notes: basics/programming-2

## New terms

| Term | Definition | Home | Aliases |
| --- | --- | --- | --- |
| off-by-one mistake | A loop that runs one turn too many or too few, usually because `<` and `<=` were mixed up. | `basics/programming-2` | off by one |

## Requests

- External host: none asked. The Further reading entry "Learn C++ (learncpp.com)" is cited without a link, so
  `learncpp.com` is requested as a host if later pages want to link it (a well-known reference; not fetched).
- Words: none proposed; every prose word is on the lists.

## Not verified

- `glm::vec3` has the members `x`, `y` and `z`: the glm sources were not read at the pin (the page uses only the
  well-known fact).
- The per-OS steps to end a frozen editor (Task Manager, Force Quit, System Monitor, `kill`) are operating system
  facts, not Strata facts; they were not run.
- That the frozen window's own close button does not answer follows from the single main thread
  (`Docs/Architecture.md`, "The main thread owns the scene, input, scripts, editor state and rendering submission");
  it was not tried.
- That coins made by the Coin Run loop carry the `Coin` script (so a loop inside `Coin` would multiply them) comes from
  the brief's critic finding, not from a run; the positions in the `PlaceCoin` solution (y at 1, 2 metres apart) are
  illustrative, not read from the Coin Run scene.
- The Console's display of the script exception line: the text `threw an exception` and `The script is disabled.` is
  from `ScriptSystem::HandleCallResult`; that the Console shows it as an error was not checked.
- The message text of `std::stoi`'s exception differs by standard library; the page does not quote it.

## Findings not applied

- critic-basics-a-12 (`uint32_t`, `std::string_view` and the other SDK words on `basics/programming-3`): it names
  `basics/programming-3` as its place; this page applies only the two sentences that its own quotes need (`uint32_t` in
  `GetGamepadAxis`, `std::string_view` in `IsActionDown`).
- Applied: critic-basics-a-1 (script `CoinLine` on its own entity, `Playground` for the other exercises), critic-basics-a-26
  (handle, value and write-back example), critic-basics-a-27 (one way to end the editor per operating system).
- `new:213` asks for a faded trio on `std::to_string` and `std::stoi`; the third step (text that is no number) has a
  solution in words and a sketch of the leading-digit cases only, because a standalone sketch cannot show the script
  being switched off.
- The brief's evidence line `Docs/Architecture.md:1415` and `ScriptEngine.cpp:257-266` were checked; the page does not
  cite them by path.

## Clerk

- Admitted: off-by-one mistake (alias off by one). `learncpp.com` is on `external-hosts.txt` already.
