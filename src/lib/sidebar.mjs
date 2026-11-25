// The sidebar and the reading tracks, from src/sidebar.json. The file lists the book's 25 parts in order with the pages
// of each part that are written, in the order of the outline's rows, and the three tracks (game, beginner, engine):
// each track's reading order as every row it holds, written or not, and its side steps. The outline's data
// (src/generated/outline.json) says what the file must hold; the checks below compare the two (site.md, rules O5 and
// O9) and the file with the pages that exist.

import { readFileSync } from 'node:fs';
import { c_Tracks } from './labels.mjs';
import { trackOrder, trackSideSteps } from './outline.mjs';

// First segments no page id or part may start with (site.md, "The base path", rule 8): archived versions ("v" and a
// digit) and the site's own folders, among them the files readers download (downloads/; rulings-6, R26).
export const c_ReservedFirstSegments = ['print', 'pagefind', 'downloads', '_astro', '_figures', '404'];

export function reservedSegmentProblem(id) {
	const first = String(id).split('/')[0];
	if (/^v[0-9]/.test(first)) return `"${first}" is reserved for archived versions of the book (v and a digit)`;
	if (c_ReservedFirstSegments.includes(first)) return `"${first}" is reserved for the site's own files (${c_ReservedFirstSegments.join(', ')})`;
	return null;
}

/** The URL id Starlight gives a page: the part page "core/index" is served as "core". */
export function routeIdOf(bookId) {
	return bookId.replace(/\/index$/, '');
}

const c_PartKeys = ['slug', 'label', 'pages'];
const c_TrackKeys = ['label', 'description', 'sequence', 'sideSteps'];

function unknownKeys(value, allowed) {
	return Object.keys(value).filter((key) => !allowed.includes(key));
}

/** Problems of the file's shape alone. */
export function checkSidebarShape(data) {
	const problems = [];
	if (!data || typeof data !== 'object' || Array.isArray(data)) return ['the file is not a JSON object'];
	for (const key of unknownKeys(data, ['parts', 'tracks'])) problems.push(`"${key}" is not a key of the sidebar (parts, tracks)`);
	if (!Array.isArray(data.parts)) problems.push('"parts" must be a list');
	else {
		data.parts.forEach((part, index) => {
			const where = `parts[${index}]`;
			if (!part || typeof part !== 'object' || Array.isArray(part)) {
				problems.push(`${where} is not an object`);
				return;
			}
			for (const key of unknownKeys(part, c_PartKeys)) problems.push(`${where}: "${key}" is not a key of a part (${c_PartKeys.join(', ')})`);
			if (typeof part.slug !== 'string' || !part.slug) problems.push(`${where}: "slug" is missing`);
			if (typeof part.label !== 'string' || !part.label.trim()) problems.push(`${where}: "label" is missing`);
			if (!Array.isArray(part.pages) || part.pages.some((id) => typeof id !== 'string')) problems.push(`${where}: "pages" must be a list of page ids (empty while the part has no page)`);
		});
	}
	if (!data.tracks || typeof data.tracks !== 'object' || Array.isArray(data.tracks)) problems.push('"tracks" must map game, beginner and engine to their tracks');
	else {
		const keys = c_Tracks.map((track) => track.key);
		for (const key of unknownKeys(data.tracks, keys)) problems.push(`tracks: "${key}" is not a track (${keys.join(', ')})`);
		for (const key of keys) {
			const track = data.tracks[key];
			const where = `tracks.${key}`;
			if (!track || typeof track !== 'object' || Array.isArray(track)) {
				problems.push(`${where} is missing`);
				continue;
			}
			for (const name of unknownKeys(track, c_TrackKeys)) problems.push(`${where}: "${name}" is not a key of a track (${c_TrackKeys.join(', ')})`);
			if (typeof track.label !== 'string' || !track.label.trim()) problems.push(`${where}: "label" is missing`);
			if (typeof track.description !== 'string' || !track.description.trim()) problems.push(`${where}: "description" is missing`);
			if (!Array.isArray(track.sequence) || track.sequence.some((id) => typeof id !== 'string')) problems.push(`${where}: "sequence" must be the track's reading order as page ids`);
			if (!Array.isArray(track.sideSteps) || track.sideSteps.some((step) => !step || typeof step.id !== 'string' || typeof step.before !== 'string' || unknownKeys(step, ['id', 'before']).length)) {
				problems.push(`${where}: "sideSteps" must be a list of { "id", "before" } (empty when the track has none)`);
			}
		}
	}
	return problems;
}

/** Reads and checks the shape of sidebar.json; throws with every problem found. */
export function loadSidebar(file) {
	let data;
	try {
		data = JSON.parse(readFileSync(file, 'utf8'));
	} catch (error) {
		throw new Error(`${file}: ${error.message}`);
	}
	const problems = checkSidebarShape(data);
	if (problems.length) throw new Error(`${file}:\n  ${problems.join('\n  ')}`);
	return data;
}

/** Where two lists of ids first differ, in words, or null when they are equal. */
function firstDifference(got, want) {
	const length = Math.max(got.length, want.length);
	for (let index = 0; index < length; index++) {
		if (got[index] !== want[index]) {
			const name = (value) => (value === undefined ? 'the end of the list' : `"${value}"`);
			return `entry ${index + 1} is ${name(got[index])}, the outline's is ${name(want[index])}`;
		}
	}
	return null;
}

/**
 * Rules O9 (the parts) and O5 (the tracks) between sidebar.json and the outline: the 25 parts in the book's order with
 * their titles, each track's reading order and side steps exactly those of plan/tracks.md.
 */
export function checkSidebarOutline(sidebar, outline) {
	const problems = [];
	const parts = sidebar.parts;
	if (parts.length !== outline.parts.length) problems.push(`sidebar.json lists ${parts.length} parts; the book has ${outline.parts.length} (book.md, "Parts")`);
	outline.parts.forEach((want, index) => {
		const got = parts[index];
		if (!got) return;
		if (got.slug !== want.slug) problems.push(`sidebar.json part ${index} is "${got.slug}"; the book's part ${index} is "${want.slug}"`);
		else if (got.label !== want.title) problems.push(`sidebar.json part "${got.slug}" is labelled "${got.label}"; the outline calls it "${want.title}"`);
	});
	for (const part of parts) {
		const reserved = reservedSegmentProblem(part.slug);
		if (reserved) problems.push(`sidebar.json part "${part.slug}": ${reserved}`);
	}
	for (const { letter, key } of c_Tracks) {
		const track = sidebar.tracks[key];
		const sequence = firstDifference(track.sequence, trackOrder(outline, letter));
		if (sequence) problems.push(`sidebar.json track "${key}" (${letter}): its sequence differs from plan/tracks.md: ${sequence}`);
		const seen = new Set();
		for (const id of track.sequence) {
			if (seen.has(id)) problems.push(`sidebar.json track "${key}" lists "${id}" twice`);
			seen.add(id);
		}
		const want = trackSideSteps(outline, letter);
		const got = track.sideSteps;
		if (JSON.stringify(got.map((step) => [step.id, step.before])) !== JSON.stringify(want.map((step) => [step.id, step.before]))) {
			problems.push(`sidebar.json track "${key}" (${letter}): its side steps are ${JSON.stringify(got)}; plan/tracks.md gives ${JSON.stringify(want)}`);
		}
	}
	return problems;
}

/**
 * The parts' pages against the pages that exist (`pages`: Map of book id → `{ relative, generated }`): every page
 * listed once, in its own part, in the order of the outline's rows with the part's index first and its review last.
 */
export function checkSidebarPages(sidebar, outline, pages) {
	const problems = [];
	const listed = new Set();
	for (const part of sidebar.parts) {
		const rows = outline.partBySlug.get(part.slug)?.pages ?? [];
		// The place of a page in its part: the index first, the rows in order, the review last; null for a page that is
		// no row (its own front matter check says so).
		const rank = (id) => {
			if (id === `${part.slug}/index`) return -1;
			if (id === `${part.slug}/review`) return rows.length;
			const index = rows.indexOf(id);
			return index < 0 ? null : index;
		};
		let previous = null;
		for (const id of part.pages) {
			if (listed.has(id)) problems.push(`sidebar.json lists "${id}" twice`);
			listed.add(id);
			if (!id.startsWith(`${part.slug}/`)) problems.push(`sidebar.json part "${part.slug}" lists "${id}", a page of another part`);
			if (!pages.has(id)) {
				problems.push(`sidebar.json lists "${id}", which is not a page (src/content/docs/${id}.md)`);
				continue;
			}
			const position = rank(id);
			if (position === null) continue;
			if (previous !== null && position <= previous.position) problems.push(`sidebar.json part "${part.slug}" lists "${id}" after "${previous.id}", against the order of the outline's rows (a part's index first, its review last)`);
			previous = { id, position };
		}
	}
	for (const [id, page] of pages) {
		if (id === 'index' || id === '404') continue;
		if (!listed.has(id)) problems.push(`${page.relative} is not listed in src/sidebar.json (part "${id.split('/')[0]}")`);
	}
	return problems;
}

/** Starlight's sidebar: one group per part that has pages, collapsed unless it holds the page being read. */
export function starlightSidebar(sidebar) {
	return sidebar.parts
		.filter((part) => part.pages.length > 0)
		.map((part) => ({ label: part.label, collapsed: true, items: part.pages.map(routeIdOf) }));
}

/** The first page of a track that is written (`written`: a Set or Map of book ids), or null. */
export function trackStart(sidebar, key, written) {
	return sidebar.tracks[key].sequence.find((id) => written.has(id)) ?? null;
}

/**
 * "Previous" and "next" of a page on every track that holds it or offers it as a side step, over the pages that are
 * written: `[{ key, letter, label, prev, next, sideStep }]`. Rows not written yet are passed over, and so are side
 * steps (a track's "next" never leads into one). On a side step itself, "previous" is the page the track reads before
 * it and "next" the page it stands before.
 */
export function trackNeighbours(sidebar, written, id) {
	const result = [];
	for (const { letter, key } of c_Tracks) {
		const track = sidebar.tracks[key];
		let position = track.sequence.indexOf(id);
		let sideStep = false;
		if (position < 0) {
			const step = track.sideSteps.find((candidate) => candidate.id === id);
			if (!step) continue;
			position = track.sequence.indexOf(step.before);
			if (position < 0) continue;
			sideStep = true;
		}
		const before = track.sequence.slice(0, position).filter((other) => written.has(other));
		const after = track.sequence.slice(sideStep ? position : position + 1).filter((other) => written.has(other));
		result.push({ key, letter, label: track.label, prev: before.at(-1) ?? null, next: after[0] ?? null, sideStep });
	}
	return result;
}

/** The letters of the tracks whose reading order holds a page (side steps do not count: rule O5). */
export function tracksHolding(sidebar, id) {
	return c_Tracks.filter(({ key }) => sidebar.tracks[key].sequence.includes(id)).map((track) => track.letter);
}
