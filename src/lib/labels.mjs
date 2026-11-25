// Words the site shows for the front matter's values (the badges and lines of the top strip, the search metadata) and
// the fixed names of the book's tracks (plan/style.md §6.2, plan/site.md "Navigation").

export const c_KindLabels = {
	primer: 'Primer',
	concept: 'Concept',
	internals: 'Internals',
	tutorial: 'Tutorial',
	'how-to': 'How-to',
	reference: 'Reference',
};

/**
 * The three tracks: the letter pages write in `tracks`, the key of src/sidebar.json and of the reader's stored choice,
 * and the badge's accessible name (visually hidden text beside the letter, never a `title`).
 */
export const c_Tracks = [
	{ letter: 'G', key: 'game', name: 'Game maker' },
	{ letter: 'B', key: 'beginner', name: 'Beginner' },
	{ letter: 'E', key: 'engine', name: 'Engine builder' },
];

export const c_TrackLetters = c_Tracks.map((track) => track.letter);

// The page where readers choose their track with ::track-chooser (site.md, "Navigation").
export const c_ChooserPage = 'start/how-to-read';

export function trackByLetter(letter) {
	return c_Tracks.find((track) => track.letter === letter) ?? null;
}

export function trackByKey(key) {
	return c_Tracks.find((track) => track.key === key) ?? null;
}

/** What the strip says about each level (style.md §6.2); the level itself comes from the outline's data. */
export const c_LevelTexts = {
	1: 'Level 1: needs only Start here, Making games and Foundations.',
	2: "Level 2: also needs the engine's core (parts 3 to 5) or earlier pages of this part.",
	3: 'Level 3: builds on other parts of the engine.',
};
