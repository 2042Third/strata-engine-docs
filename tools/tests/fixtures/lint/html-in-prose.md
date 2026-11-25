No raw HTML or C++ templates outside backticks (the spike's rule, style.md §2.2). HTML comments are not prose.

%%% pass core/time
A `Ref<Scene>` holds the scene. <!-- a note for the writer -->
The value is 2 < 3.

%%% fail core/time 1 2 4
A Ref<Scene> holds the scene.
A line<br>break.

<details>
