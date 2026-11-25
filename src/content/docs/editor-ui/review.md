---
id: editor-ui/review
title: "Review: the editor's interface"
description: "The questions of every page of the part on the editor's interface, and exercises that use several of its pages together."
tracks: [E]
status: final
generated: review
---

## Cumulative exercises

These exercises need more than one page of the part. Try each before you open its worked solution.

1. **Basic.** A panel in a window named "Tools" lists 20,000 entities, each with a `Button("Delete")` and no `PushID`. How many different identifiers (IDs) do the buttons have, and what does one frame cost at 2 microseconds per button, drawn in full and with only the 30 rows on screen? What fixes the IDs, and why does an entity's universally unique identifier (UUID) beat the row number?

   :::answer[Worked solution]
   An ID is a hash of the label under the ID stack, and every button has the label "Delete" under the same window, so the 20,000 buttons have one ID. The library cannot tell the rows apart: a click may seem dead or act on the wrong row.

   Drawing every row costs 20,000 × 2 = 40,000 microseconds, which is 40 ms and more than a whole frame of 16.7 ms. Submitting only the 30 visible rows with `ImGuiListClipper` costs 30 × 2 = 60 microseconds.

   Wrap each row in `PushID` and `PopID`. Use the entity's UUID, which stays with the entity. When a script adds an entity at the top, the row numbers shift, and an ID made from the row number would hand the hover and click state to the wrong entity.
   :::

2. **Basic.** A laptop has a content scale of 2, a window of 1440 by 900 points and a framebuffer of 2880 by 1800 pixels. Interface is Automatic and `DisplayPos` is (0, 0). Give the user interface (UI) scale, the four push constants, the normalized device coordinates (NDC) of the point (360, 90) and the scissor of the clip rectangle (360, 90, 720, 450). What changes at the next start with `--ui-scale 3`?

   :::answer[Worked solution]
   The ratio of framebuffer to window is 2, above 1, so the UI scale is 2 / 2 = 1 and `DisplayFramebufferScale` is 2. The window system has scaled the window already.

   The push constants follow the display's size in points: the scale is (2 / 1440, −2 / 900) = (0.0013889, −0.0022222), and the translate is (−1, 1). The point (360, 90) gives x = 360 × 0.0013889 − 1 = −0.5 and y = 90 × −0.0022222 + 1 = 0.8.

   The scissor multiplies the clip rectangle by the framebuffer scale 2: x from 720 to 1440 and y from 180 to 900. Both lie inside 2880 by 1800, so the clamp changes nothing.

   The override wins over the content scale and the factor, so the UI scale becomes 3, inside [0.5, 4]. Sizes that follow the font triple compared with scale 1. The push constants and the scissor stay as they are, because they follow points and the framebuffer scale.
   :::

3. **Medium.** A Windows display has a content scale of 1.25, its window and framebuffer have the same size, and Interface is at 150 %. The status bar's font, the caption size, is 12 pixels at scale 1. The status bar's full texts take 1,400 pixels, and the bar is compact.

   The available width goes 1,380, 1,440, 1,460 and then 1,440 again. What does the bar show each time?

   :::answer[Worked solution]
   The ratio is 1, so the UI scale is 1.25 × 1.5 = 1.875. The font is 12 × 1.875 = 22.5 pixels and the margin of two font sizes is 45 pixels.

   At 1,380 the full texts overflow (1,400 is above 1,380), so the bar is compact. At 1,440 they fit, but 1,440 − 45 = 1,395 is below 1,400, so the bar keeps its compact state. At 1,460, 1,460 − 45 = 1,415 is at least 1,400, so the bar returns to full.

   At 1,440 again the texts fit, and only an overflow makes a full bar compact, so the bar stays full. The margin is what stops the bar from flickering between 1,440 and 1,460.
   :::

4. **Medium.** The Hierarchy shows A, B, X, C, D, E, where X is the child of B and B is expanded. The person selects B, X and D, and drags the row D onto the bottom quarter of E's row.

   Which entities travel, what are the parent and the index, and which command runs, as whom? Then the drop goes onto the middle of X's row instead. What happens?

   :::answer[Worked solution]
   The dragged row D is selected, so the whole selection is dragged, reduced to its topmost entities in hierarchy order. X leaves the list because its ancestor B is listed. The payload holds the UUIDs of B and D.

   The bottom quarter of E means After. E has no shown children, so the parent is E's parent, the top level, and the landing position is E's sibling index 4 plus 1, which is 5. B (index 1) and D (index 3) stand in front of 5 and leave, so the index is 5 − 2 = 3. The result is A, C, E, B, D, with X still under B.

   After the drawing loop, the panel runs `entity.setParent` with these parameters through `RunEditorCommand`, so the origin is the UI and the journal records the person's action.

   The middle half of X's row means Inside, so the parent would be X. X lies below B, which moves, so B would become its own ancestor. `GetDropTarget` returns nothing, the pointer shows the no-entry cursor and no command runs.
   :::

5. **Medium.** A person drags a float field for two seconds, first the Softness of three lights (0.2, 0.2 and 0.8) in the Inspector, then a float field of a generated settings page. Both end at 0.5.

   What does each row show before the drag? When does each store change? How many undo steps and which command does each produce?

   :::answer[Worked solution]
   The Inspector's row shows "--" before the drag, because the three values differ. During the drag every frame writes to the lights through `SetPropertyWithUndo`, so the Scene view follows. The edits of one property merge into one undo step with the before values 0.2, 0.2 and 0.8, and one undo restores all three. The widget's finished flag on release ends the merge. The Inspector runs no command here: the undo helper is the path for edits that continue over many frames.

   The settings page changes only its copy while the drag runs, so the project's value stays as it was. On release the finished edit runs one `project.setSettings` command with the origin of the UI. It validates, stores the value as one undo step and moves the version, and the page reads again because the version changed.

   Both produce one undo step, but only the settings page runs a command. They also differ in when the data changes: the Inspector's data moves every frame of the drag, and the settings value moves once, at the end.
   :::

6. **Medium.** A chip strip is 300 pixels wide. At UI scale 1 its three chips measure 100, 120 and 90 pixels with their labels, an icon is 36 and the gap is 8. The person changes the scale to 1.5, and the strip stays 300 wide. Which chips are icons before and after the change, and in which frame does the strip fit again?

   :::answer[Worked solution]
   At scale 1 the sum is 100 + 120 + 90 + 2 × 8 = 326, above 300. Turning the last chip into an icon saves 90 − 36 = 54, giving 272, which fits. `FirstIcon` is 2.

   At 1.5 the widths are 150, 180, 135, an icon of 54 and a gap of 12. The frame of the change still draws with the old decision: chips 0 and 1 with labels and chip 2 as an icon take 150 + 180 + 54 + 24 = 408, which overflows. During that frame the strip measures the new widths.

   In its destructor the strip walks back from the last chip. With chip 2 as an icon the sum is 408, still above 300. With chips 1 and 2 as icons it is 150 + 54 + 54 + 24 = 282, which fits, so `FirstIcon` becomes 1. The next frame draws that decision, so the strip fits again one frame after the scale changed.
   :::

7. **Hard.** The display has 2 pixels per point. The Scene view's image area is 640 by 360 points. The Game view's panel, on the same display, is 1000 by 700 units and set to the fixed resolution 1920 x 1080.

   How large is the Scene view's target, and what are the Game view's image size and offset? A mouse is 250 units right and 200 units down from the Game view's corner: which game pixel is it?

   Both panels then lose 200 units of width: the Scene view's image area becomes 440 by 360 points and the Game view's panel 800 by 700 units. Which of the two views renders a different number of pixels?

   :::answer[Worked solution]
   The Scene view renders at the panel's size in pixels: 640 × 2 by 360 × 2 = 1,280 by 720 pixels, which is 921,600 pixels.

   The Game view tries the full width: 1000 by 1000 / (16/9) = 562.5, floored to 562. That fits in 700, so the image is 1000 by 562. The offset is floor((1000 − 1000) / 2) = 0 across and floor((700 − 562) / 2) = 69 down.

   The mouse is at (250, 200) from the corner, so it is at (250, 200 − 69) = (250, 131) in the image. Scaling by 1920 / 1000 and 1080 / 562 gives the game pixel (480, 251.7).

   At 800 by 700 the Game view's image becomes 800 by 450 with the offset (0, 125). The fixed mode still renders exactly 1920 by 1080, so only the scaling to the screen changes. The Scene view's target follows its panel and becomes 880 by 720 pixels, so the Scene view is the one that changes. In aspect modes such as **16:9**, the Game view would change too, because they render at the picture's own size: 1,600 by 900 pixels here.
   :::

8. **Hard.** You add a panel named "Selection Summary" that is open by default. You dock it in `BuildDefaultLayout` and leave `c_LayoutVersion` at 5. A teammate who has a saved layout of version 5 and a new user both start the editor. Where is the panel for each, how do you fix it, and what does it cost?

   Your drawing code also calls `ImGui::SetNextItemWidth(240.0f)`, builds a red color from numbers, and its button calls `Execute` on the registry without an origin. What fails, and what do you write instead?

   :::answer[Worked solution]
   The editor builds the default layout only when the layout file holds none or another version. The new user has no file, so the panel is docked. The teammate's file holds version 5, the same as the editor's, so the editor keeps the layout. That layout says nothing about the new panel, and its window floats over the editor.

   Raise `c_LayoutVersion` to 6. Then `m_ResetLayout` is true on the first frame of every older layout. The editor resets the open states, builds the default layout again and records version 6. The cost is that each person who arranged panels loses the arrangement once.

   **View ▸ Reset Layout** rebuilds it at any time. A panel that starts closed needs no bump.

   The scan "Sizes scale with the font" fails on 240, a pixel size above 16: write `ImGui::GetFontSize() * 17.0f`, which is 238 pixels at the body size of 14 and grows with the scale. The scan "Colors come only from the theme" fails on the numbers: take the color from `UI::GetThemeColors()`. Both are in `Editor.UI.Source`, and the lists of exceptions stay empty. Calling `Execute` without an origin makes the journal record an internal call, and a failure shows no toast: use `RunEditorCommand`.
   :::

9. **Hard.** The scene is at undo version 20 with unsaved changes. You press **File ▸ New Project**, and the question about unsaved changes appears. While it shows, an agent runs `entity.create`. You press `Don't Save`, and then a second time.

   The dialog opens, and the agent runs `entity.create` again before you press Create. How many times do you press `Don't Save` in all? Where is the last question drawn, and what runs afterwards?

   :::answer[Worked solution]
   The first press of `Don't Save` finds the undo version moved from 20 to 21. The modal stays, warns that the scene changed and says that discarding includes those changes. Only a second press is an answer, so that is two presses for the first question. The dialog opens with 21 stored.

   The second agent call moves the version to 22. When you press Create, `MayReplaceScene` sees a modified scene and 22 against the stored 21, so it asks again with `RequestReleaseProject`. The question is drawn over the dialog, inside it, because ImGui keeps one popup per level and a question at the top level would close the dialog.

   One more press of `Don't Save` answers it, so there are three presses in all. The callback stores 22, and the dialog runs `project.create` in the next frame with the origin of the UI. Cancelling the last question would run nothing and keep the agent's entities.
   :::

10. **Hard.** A panel like Streaming refreshes its table at most every quarter second. A perf test runs it for 240 frames at 60 frames per second. A refresh frame costs 3 ms and any other frame 0.05 ms.

   What is the most refresh frames the run can hold? What 95th percentile does the test report with that many, with 12 and with 4? Which second metric still sees the hitch, and what makes an idle frame cheap?

   :::answer[Worked solution]
   The run lasts 240 / 60 = 4 seconds, with at most one refresh per quarter second, so up to 16 refresh frames.

   The test uses the nearest-rank rule: 0.95 × 240 = 228, so the 95th percentile is the value at rank 228 of the sorted costs, and 12 frames rank above it. With 16 refresh frames the 3 ms frames take ranks 225 to 240, so rank 228 is 3 ms and the percentile sees them. With 12 they take ranks 229 to 240, so the percentile is 0.05 ms, and with 4 it is 0.05 ms too.

   A hitch in 12 frames or fewer cannot move the percentile. The test therefore also reports the median of the refresh frames alone, 3 ms in all three cases, and requires at least 4 of them.

   The idle frame is cheap because the panel compares a version, an ID or a key before it rebuilds, and the table is built on a job and swapped in when finished.
   :::
