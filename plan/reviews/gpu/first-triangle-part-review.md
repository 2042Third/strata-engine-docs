# Part review: gpu/first-triangle (group 1 of 2)

- step: the broken run's "You should see" gave the checks as `5 | 5 passed | 2 failed`; doctest's first number is the total, `7 | 5 passed | 2 failed` (step 1 of the page already reads `7 | 7 passed | 0 failed`).
- wrong: the Checker shader's callout "Line 34: the entry takes the v_UV" pointed at `return output`; `v_UV = input.v_UV;` is line 30 of hunk 1.
