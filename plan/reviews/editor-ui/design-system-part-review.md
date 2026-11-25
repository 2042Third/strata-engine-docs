# Part review: `editor-ui/design-system`

- contradiction: "thin lines ... stay one pixel wide up to a scale of 2" against `editor-ui/ui-scale` (2 pixels at 2, `ScaleAllSizes` truncates 1 x 2); now "below a scale of 2 and become two pixels at 2".
- wrong: Exercise 3's answer said "At 1.25 only 4 and 8 stay exact"; the sketch's own output shows 20 -> 25 exact too; now "4, 8 and 20".
- unclear: "serves the console, :term[ids]{id=id} and numbers" marked generic identifiers as the ImGui item ID; now "identifiers".
