No sentence has more than 35 words (style.md §2.2). A list item is a sentence too; captions are prose.

%%% pass core/time
%%repeat 7 The ball rolls on%% to the wall.

%%% fail core/time 1 3
%%repeat 8 The ball rolls on%% to the wall and back.

- %%repeat 9 one two three four%%

%%% fail core/time src/content/figures/core/time.json:6
A line.
%%% file src/content/figures/core/time.json
{
	"figures": [
		{
			"id": "shot",
			"shows": "a ball",
			"caption": "%%repeat 9 one two three four%%",
			"alt": "A ball."
		}
	]
}
