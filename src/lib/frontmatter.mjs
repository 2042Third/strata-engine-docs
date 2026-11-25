// The rules of a page's front matter that the build enforces (plan/style.md §6.1, plan/site.md "Front matter and the
// teaching checks"): the keys of each kind of page, and the outline rules one page can be checked against: O1 (the id),
// O2 and O3 (the Needs), O4 (each Need earlier on the page's tracks), O5 (the tracks that hold it), O7 (the page equals
// its row of the outline) and the part pages' side of O8. src/content.config.ts checks the same keys' shapes; the
// messages here name the rule and say what to write.

import { c_TrackLetters } from './labels.mjs';
import { c_Kinds, c_PageId, c_Sizes, needAlternatives, partOf, trackOrder } from './outline.mjs';
import { reservedSegmentProblem, tracksHolding } from './sidebar.mjs';

export const c_Statuses = ['draft', 'reviewed', 'final'];
export const c_MaxNeedIds = 5;
export const c_DescriptionLength = 160;
export const c_LearnId = /^[a-z0-9]+(-[a-z0-9]+)*$/;
export const c_Release = /^\d+\.\d+\.\d+$/;
// style.md §6.1: a learn line starts with an observable verb of this list, never with "understand", "know", "learn"
// or "be familiar with".
export const c_LearnVerbs = ['explain', 'compute', 'name', 'choose', 'write', 'build', 'find', 'predict', 'change', 'add', 'fix', 'trace', 'measure', 'compare', 'draw', 'export', 'create', 'run', 'set'];
export const c_LearnNever = ['understand', 'know', 'learn', 'be familiar with'];
// The kinds whose pages name the release that first had their subject, in the parts 1 and 3 to 21 (`make` to
// `engineering`).
export const c_SinceKinds = ['concept', 'internals', 'tutorial', 'how-to'];
export const c_GeneratedPages = ['index', 'review'];

const c_ChapterKeys = ['id', 'title', 'description', 'kind', 'size', 'tracks', 'needs', 'time', 'learn', 'since', 'status'];
const c_PartPageKeys = ['id', 'title', 'description', 'tracks', 'status', 'generated'];
const c_BookKeys = new Set([...c_ChapterKeys, ...c_PartPageKeys]);
// Starlight's keys that only change how a page is displayed: a page may carry them.
export const c_DisplayKeys = ['template', 'hero', 'tableOfContents', 'pagefind', 'sidebar', 'banner', 'lastUpdated'];
// Keys a page never carries, with the reason (tools/pages.py refuses the same).
export const c_RefusedKeys = {
	slug: 'a page\'s URL is its id, the file\'s path (site.md, "The base path")',
	draft: 'a page\'s state is "status" (Starlight\'s draft pages are left out of the build)',
	prev: '"previous" follows the sidebar or the reader\'s track (site.md, "Navigation")',
	next: '"next" follows the sidebar or the reader\'s track (site.md, "Navigation")',
	head: 'pages set no head entries (site.md, "The base path", rule 4)',
	level: 'the level is computed from the Needs closure (style.md §6.2)',
	engine: 'the engine release comes from engine.pin (style.md §6.2)',
	prerequisites: 'the key is "needs" (style.md §6.1)',
	editUrl: 'the book\'s repository is not public, so no page links to it to be edited',
};
export const c_FirstRelease = '0.3.0';

/** Compares two releases written X.Y.Z: negative when `a` is older. */
export function compareReleases(a, b) {
	const left = a.split('.').map(Number);
	const right = b.split('.').map(Number);
	for (let index = 0; index < 3; index++) if (left[index] !== right[index]) return left[index] - right[index];
	return 0;
}

/** What kind of file a page is: the landing page, the 404 page, a part's index or review page, or a chapter. */
export function pageRole(bookId, data) {
	if (bookId === 'index') return 'landing';
	if (bookId === '404') return 'not-found';
	if (data?.generated !== undefined) return 'part-page';
	return 'chapter';
}

function sameSet(a, b) {
	return a.length === b.length && new Set(a).size === a.length && a.every((item) => b.includes(item));
}

function tracksProblem(tracks) {
	if (!Array.isArray(tracks)) return '"tracks" must be a list of the letters G, B and E ([] for a page on no track)';
	if (tracks.some((letter) => !c_TrackLetters.includes(letter))) return `"tracks" holds ${JSON.stringify(tracks.find((letter) => !c_TrackLetters.includes(letter)))}; a track is one of the letters ${c_TrackLetters.join(', ')}`;
	if (new Set(tracks).size !== tracks.length) return '"tracks" names a track twice';
	return null;
}

function learnProblems(learn) {
	if (!Array.isArray(learn) || learn.length < 2 || learn.length > 5) return ['"learn" must hold two to five objectives, each "- id: …" with "text: …" (style.md §6.1)'];
	const problems = [];
	const ids = new Set();
	learn.forEach((item, index) => {
		const where = `"learn" item ${index + 1}`;
		if (!item || typeof item !== 'object' || Array.isArray(item)) {
			problems.push(`${where} is not "id: …" and "text: …"`);
			return;
		}
		const extra = Object.keys(item).filter((key) => key !== 'id' && key !== 'text');
		if (extra.length) problems.push(`${where} holds ${extra.map((key) => `"${key}"`).join(', ')}; an objective has only "id" and "text"`);
		if (typeof item.id !== 'string' || !c_LearnId.test(item.id)) problems.push(`${where}: "id" must be lowercase words joined by hyphens, such as fixed-step`);
		else if (ids.has(item.id)) problems.push(`${where}: the id "${item.id}" is used twice on the page`);
		else ids.add(item.id);
		if (typeof item.text !== 'string' || !item.text.trim()) {
			problems.push(`${where}: "text" says what the reader can do afterwards`);
			return;
		}
		const text = item.text.trim().toLowerCase();
		const never = c_LearnNever.find((words) => text === words || text.startsWith(`${words} `));
		// The first word without the punctuation after it ("create, save and open"), as tools/pages.py reads it.
		const first = /^[a-z]*/.exec(text)[0] || text.split(/\s+/)[0];
		if (never) problems.push(`${where}: "${item.text}" starts with "${never}", which no reader can be seen doing; start with one of: ${c_LearnVerbs.join(', ')}`);
		else if (!c_LearnVerbs.includes(first)) problems.push(`${where}: "${item.text}" starts with "${first}"; an objective starts with an observable verb: ${c_LearnVerbs.join(', ')}`);
	});
	return problems;
}

function needsProblems(needs, bookId, book) {
	if (!Array.isArray(needs) || needs.some((need) => typeof need !== 'string')) return ['"needs" must be a list of page ids, "a|b" for alternatives ([] for the outline\'s "-")'];
	const problems = [];
	let count = 0;
	const seen = new Set();
	for (const need of needs) {
		const alternatives = needAlternatives(need);
		count += alternatives.length;
		if (seen.has(need)) problems.push(`"needs" lists "${need}" twice`);
		seen.add(need);
		for (const id of alternatives) {
			if (!c_PageId.test(id)) problems.push(`"needs" holds "${need}": "${id}" is not a page id`);
			else if (id === bookId) problems.push('"needs" names the page itself');
			else if (!book.outline.rows.has(id)) problems.push(`O2: the Need "${id}" is no row of the outline (plan/outline-*.md)`);
			else if (book.release && !book.pages.has(id)) problems.push(`O2: the Need "${id}" is not written yet, and a release build links every Need (src/content/docs/${id}.md)`);
		}
	}
	if (count > c_MaxNeedIds) problems.push(`O3: "needs" names ${count} page ids, alternatives included; at most ${c_MaxNeedIds}`);
	return problems;
}

/** O4: on each track of the page, every Need (or one of its alternatives) comes earlier. */
function orderProblems(bookId, tracks, needs, outline) {
	const problems = [];
	for (const letter of tracks) {
		const order = trackOrder(outline, letter);
		const position = order.indexOf(bookId);
		if (position < 0) continue;
		for (const need of needs) {
			const alternatives = needAlternatives(need);
			if (!alternatives.some((id) => { const at = order.indexOf(id); return at >= 0 && at < position; })) {
				problems.push(`O4: on track ${letter}, no alternative of the Need "${need}" comes before this page`);
			}
		}
	}
	return problems;
}

/** O7: the front matter's title, kind, size, tracks and Needs equal the page's row of the outline. */
function rowProblems(data, row) {
	const problems = [];
	const where = `its row (${row.row})`;
	if (data.title !== row.title) problems.push(`O7: "title" is ${JSON.stringify(data.title)}; ${where} says ${JSON.stringify(row.title)}`);
	if (data.kind !== row.kind) problems.push(`O7: "kind" is ${JSON.stringify(data.kind)}; ${where} says "${row.kind}"`);
	if (data.size !== row.size) problems.push(`O7: "size" is ${JSON.stringify(data.size)}; ${where} says "${row.size}"`);
	if (Array.isArray(data.tracks) && !sameSet(data.tracks, row.tracks)) problems.push(`O7: "tracks" is [${data.tracks.join(', ')}]; ${where} says [${row.tracks.join(', ')}]`);
	if (Array.isArray(data.needs) && JSON.stringify(data.needs) !== JSON.stringify(row.needs)) problems.push(`O7: "needs" is [${data.needs.join(', ')}]; ${where} says [${row.needs.join(', ')}]`);
	return problems;
}

function commonProblems(data) {
	const problems = [];
	for (const key of Object.keys(data)) {
		if (c_RefusedKeys[key]) problems.push(`"${key}" is not a key of the book's pages: ${c_RefusedKeys[key]}`);
		else if (!c_BookKeys.has(key) && !c_DisplayKeys.includes(key)) problems.push(`"${key}" is not a key of the book's pages (style.md §6.1; Starlight's display keys: ${c_DisplayKeys.join(', ')})`);
	}
	if (typeof data.title !== 'string' || !data.title.trim()) problems.push('"title" is missing');
	if (typeof data.description !== 'string' || !data.description.trim()) problems.push('"description" is missing (one sentence for search results and link previews)');
	else if (data.description.length > c_DescriptionLength) problems.push(`"description" is ${data.description.length} characters; at most ${c_DescriptionLength}`);
	else if (!/[.?!]$/.test(data.description.trim())) problems.push('"description" is one sentence: it ends with ".", "?" or "!"');
	return problems;
}

/**
 * Every problem of one page's front matter. `page` is the page index's entry (`id` is the book id, the file's path
 * under src/content/docs/ without .md); `book` holds `outline`, `sidebar`, `pages` (the page index), `pin` and
 * `release`.
 */
export function checkFrontmatter(page, book) {
	if (page.error) return [page.error];
	const data = page.data;
	const role = pageRole(page.id, data);
	const problems = commonProblems(data);
	if (role === 'landing' || role === 'not-found') {
		const extra = Object.keys(data).filter((key) => c_BookKeys.has(key) && key !== 'title' && key !== 'description');
		if (extra.length) problems.push(`the ${role === 'landing' ? 'landing page' : '404 page'} carries only "title" and "description" of the book's keys, not ${extra.map((key) => `"${key}"`).join(', ')}`);
		return problems;
	}
	if (data.id !== page.id) problems.push(`O1: "id" must be the file's path under src/content/docs/ without .md: id: ${page.id}`);
	else if (!c_PageId.test(page.id)) problems.push(`O1: the id "${page.id}" is not lowercase segments of a-z, 0-9 and single hyphens`);
	const reserved = reservedSegmentProblem(page.id);
	if (reserved) problems.push(`O1: ${reserved}`);
	if (!c_Statuses.includes(data.status)) problems.push(`"status" must be one of ${c_Statuses.join(', ')}`);
	const part = partOf(book.outline, page.id);
	if (!part) {
		problems.push(`the page is in no part of the book: its folder "${page.id.split('/')[0]}" is no part's slug`);
		return problems;
	}
	if (role === 'part-page') {
		const extra = Object.keys(data).filter((key) => c_BookKeys.has(key) && !c_PartPageKeys.includes(key));
		if (extra.length) problems.push(`a part page carries ${c_PartPageKeys.map((key) => `"${key}"`).join(', ')}, not ${extra.map((key) => `"${key}"`).join(', ')} (style.md §7.7)`);
		if (!c_GeneratedPages.includes(data.generated)) problems.push(`"generated" is ${c_GeneratedPages.join(' or ')}`);
		else if (page.id !== `${part.slug}/${data.generated}`) problems.push(`O8: a page with "generated: ${data.generated}" is the file src/content/docs/${part.slug}/${data.generated}.md`);
		if (!part.partPages) problems.push(`O8: the part "${part.slug}" has ${part.pages.length} rows; only parts of eight or more rows have an index and a review page`);
		const tracks = tracksProblem(data.tracks);
		if (tracks) problems.push(tracks);
		else if (!sameSet(data.tracks, part.tracks)) problems.push(`"tracks" of a part page are the part's: [${part.tracks.join(', ')}]`);
		return problems;
	}
	if (c_GeneratedPages.some((name) => page.id === `${part.slug}/${name}`)) {
		problems.push(`O8: ${page.id}.md is the part's ${page.id.endsWith('index') ? 'index' : 'review'} page: it carries "generated: ${page.id.split('/').pop()}"`);
		return problems;
	}
	if (!c_Kinds.includes(data.kind)) problems.push(`"kind" must be one of ${c_Kinds.join(', ')}`);
	if (!c_Sizes.includes(data.size)) problems.push(`"size" must be one of ${c_Sizes.join(', ')}`);
	const tracks = tracksProblem(data.tracks);
	if (tracks) problems.push(tracks);
	problems.push(...needsProblems(data.needs, page.id, book));
	const reference = data.kind === 'reference';
	if (reference) {
		for (const key of ['time', 'learn']) if (data[key] !== undefined) problems.push(`"${key}" is absent on reference pages (style.md §6.1)`);
	} else {
		if (!Number.isInteger(data.time) || data.time <= 0) problems.push('"time" must be the minutes the page takes, a whole number');
		problems.push(...learnProblems(data.learn));
	}
	const takesSince = c_SinceKinds.includes(data.kind) && (part.number === 1 || (part.number >= 3 && part.number <= 21));
	if (takesSince) {
		if (typeof data.since !== 'string' || !c_Release.test(data.since)) problems.push('"since" must be the first release whose engine had the subject, as a string like 0.3.0 (style.md §6.1)');
		else if (compareReleases(data.since, book.pin.release) > 0) problems.push(`"since" is ${data.since}, later than the book's release ${book.pin.release} (engine.pin)`);
		else if (compareReleases(data.since, c_FirstRelease) < 0) problems.push(`"since" is ${data.since}; anything older than the engine's first tag is ${c_FirstRelease} (style.md §6.1)`);
	} else if (data.since !== undefined) {
		problems.push(`"since" is absent on ${data.kind ?? 'these'} pages of the part "${part.slug}" (style.md §6.1: concept, internals, tutorial and how-to pages of the parts 1 and 3 to 21)`);
	}
	const row = book.outline.rows.get(page.id);
	if (!row) {
		problems.push(`O7: the page has no row in the outline (plan/outline-*.md); a page of the book is one of its rows`);
		return problems;
	}
	problems.push(...rowProblems(data, row));
	if (!tracks && Array.isArray(data.needs)) problems.push(...orderProblems(page.id, data.tracks, data.needs, book.outline));
	if (!tracks) {
		const holding = tracksHolding(book.sidebar, page.id);
		if (!sameSet(data.tracks, holding)) problems.push(`O5: "tracks" is [${data.tracks.join(', ')}], but the tracks of src/sidebar.json that hold the page are [${holding.join(', ')}]`);
	}
	return problems;
}

/** Needs cycles among the written pages, each as the list of page ids around it (the first id repeated at the end). */
export function findNeedCycles(pages) {
	const state = new Map();
	const stack = [];
	const cycles = [];
	const visit = (id) => {
		state.set(id, 'open');
		stack.push(id);
		for (const need of pages.get(id)?.needs ?? []) {
			for (const next of needAlternatives(need)) {
				if (!pages.has(next)) continue;
				if (state.get(next) === 'open') cycles.push([...stack.slice(stack.indexOf(next)), next]);
				else if (!state.has(next)) visit(next);
			}
		}
		stack.pop();
		state.set(id, 'done');
	};
	for (const id of [...pages.keys()].sort()) if (!state.has(id)) visit(id);
	return cycles;
}
