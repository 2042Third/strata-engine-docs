// The outline as data: src/generated/outline.json, which the tool chain writes from plan/outline-1.md to outline-4.md
// and plan/tracks.md (`python -I tools/pages.py outline --write`; its format is .tools/handover/outline-format.md).
// The build never parses the plan's Markdown: the rows (id, title, kind, size, tracks, Needs, level), the parts with
// their Needs, and the three tracks come from this file, read and checked here.

import { readFileSync } from 'node:fs';
import { c_KindLabels, c_TrackLetters } from './labels.mjs';

export const c_Kinds = Object.keys(c_KindLabels);
export const c_Sizes = ['S', 'M', 'L', 'XL'];
// A page id: lowercase segments of letters, digits and single hyphens, joined by "/" (site.md, rule O1).
export const c_PageId = /^[a-z0-9]+(-[a-z0-9]+)*(\/[a-z0-9]+(-[a-z0-9]+)*)*$/;
export const c_PartSlug = /^[a-z0-9]+(-[a-z0-9]+)*$/;

/** The alternatives of one Need as the front matter and the outline write it: "a|b" → ["a", "b"]. */
export function needAlternatives(need) {
	return String(need).split('|');
}

function isStringList(value) {
	return Array.isArray(value) && value.every((item) => typeof item === 'string');
}

function lettersProblem(value) {
	if (!isStringList(value)) return 'is not a list of track letters';
	if (value.some((letter) => !c_TrackLetters.includes(letter))) return `holds something other than ${c_TrackLetters.join(', ')}`;
	if (new Set(value).size !== value.length) return 'names a track twice';
	return null;
}

function needsProblem(value) {
	if (!isStringList(value)) return 'is not a list of Needs';
	for (const need of value) {
		const alternatives = needAlternatives(need);
		if (alternatives.some((id) => !c_PageId.test(id))) return `holds "${need}", which is not a page id or "a|b"`;
	}
	return null;
}

/** Problems of the file's shape: what the build reads must be there and of the right type. */
export function checkOutlineShape(data) {
	const problems = [];
	if (!data || typeof data !== 'object' || Array.isArray(data)) return ['the file is not a JSON object'];
	if (!Array.isArray(data.parts) || data.parts.length === 0) problems.push('"parts" must be the list of the book\'s parts');
	if (!Array.isArray(data.pages)) problems.push('"pages" must be the list of the outline\'s rows');
	if (!data.tracks || typeof data.tracks !== 'object' || Array.isArray(data.tracks)) problems.push('"tracks" must map G, B and E to their lists');
	if (problems.length) return problems;
	const slugs = new Set();
	data.parts.forEach((part, index) => {
		const where = `parts[${index}]`;
		if (!part || typeof part !== 'object') {
			problems.push(`${where} is not an object`);
			return;
		}
		if (part.number !== index) problems.push(`${where}: "number" is ${JSON.stringify(part.number)}, not ${index} (the parts are numbered in order from 0)`);
		if (typeof part.slug !== 'string' || !c_PartSlug.test(part.slug)) problems.push(`${where}: "slug" is not a lowercase name`);
		else if (slugs.has(part.slug)) problems.push(`${where}: the slug "${part.slug}" is used twice`);
		slugs.add(part.slug);
		if (typeof part.title !== 'string' || !part.title.trim()) problems.push(`${where}: "title" is missing`);
		const letters = lettersProblem(part.tracks);
		if (letters) problems.push(`${where}: "tracks" ${letters}`);
		const needs = needsProblem(part.needs);
		if (needs) problems.push(`${where}: "needs" ${needs}`);
		if (!isStringList(part.pages)) problems.push(`${where}: "pages" is not a list of page ids`);
		if (typeof part.partPages !== 'boolean') problems.push(`${where}: "partPages" is not true or false`);
	});
	const ids = new Set();
	data.pages.forEach((page, index) => {
		const where = `pages[${index}]`;
		if (!page || typeof page !== 'object') {
			problems.push(`${where} is not an object`);
			return;
		}
		if (typeof page.id !== 'string' || !c_PageId.test(page.id)) {
			problems.push(`${where}: "id" is not a page id`);
			return;
		}
		const named = `${where} (${page.id})`;
		if (ids.has(page.id)) problems.push(`${named}: the id is used twice`);
		ids.add(page.id);
		if (typeof page.title !== 'string' || !page.title.trim()) problems.push(`${named}: "title" is missing`);
		if (!c_Kinds.includes(page.kind)) problems.push(`${named}: "kind" is not one of ${c_Kinds.join(', ')}`);
		if (!c_Sizes.includes(page.size)) problems.push(`${named}: "size" is not one of ${c_Sizes.join(', ')}`);
		const letters = lettersProblem(page.tracks);
		if (letters) problems.push(`${named}: "tracks" ${letters}`);
		const needs = needsProblem(page.needs);
		if (needs) problems.push(`${named}: "needs" ${needs}`);
		if (!slugs.has(page.part) || !page.id.startsWith(`${page.part}/`)) problems.push(`${named}: "part" is not the part its id starts with`);
		if (![1, 2, 3].includes(page.level)) problems.push(`${named}: "level" is not 1, 2 or 3`);
		if (typeof page.row !== 'string' || !page.row) problems.push(`${named}: "row" does not say where the row is`);
	});
	for (const part of data.parts) {
		for (const id of isStringList(part?.pages) ? part.pages : []) {
			if (!ids.has(id)) problems.push(`parts (${part.slug}): "${id}" is not one of "pages"`);
		}
	}
	for (const letter of c_TrackLetters) {
		const entries = data.tracks[letter];
		if (!Array.isArray(entries)) {
			problems.push(`tracks.${letter} is not a list`);
			continue;
		}
		entries.forEach((entry, index) => {
			if (!entry || typeof entry.id !== 'string' || !ids.has(entry.id)) problems.push(`tracks.${letter}[${index}]: "id" is not a row of the outline`);
			else if (entry.sideStep !== undefined && entry.sideStep !== true) problems.push(`tracks.${letter}[${index}]: "sideStep" is true or absent`);
		});
	}
	return problems;
}

// The index of each data object read: every page's components index the same imported object, so it is checked once.
const s_Indexed = new WeakMap();

/**
 * The outline ready for lookups: `{ parts, partBySlug, rows: Map<id, row>, tracks: { G, B, E } }`, where a track is
 * its list of `{ id, sideStep }` entries as tracks.md writes it. Throws when the shape is wrong. The data must not be
 * changed after it is indexed.
 */
export function indexOutline(data, where = 'src/generated/outline.json') {
	if (data && typeof data === 'object' && s_Indexed.has(data)) return s_Indexed.get(data);
	const problems = checkOutlineShape(data);
	if (problems.length) throw new Error(`${where}:\n  ${problems.join('\n  ')}\nWrite it again with: python -I tools/pages.py outline --write`);
	const rows = new Map(data.pages.map((page) => [page.id, page]));
	const tracks = {};
	for (const letter of c_TrackLetters) tracks[letter] = data.tracks[letter].map((entry) => ({ id: entry.id, sideStep: entry.sideStep === true }));
	const outline = {
		parts: data.parts,
		partBySlug: new Map(data.parts.map((part) => [part.slug, part])),
		rows,
		tracks,
	};
	s_Indexed.set(data, outline);
	return outline;
}

/** Reads src/generated/outline.json (or another file) and indexes it. */
export function loadOutline(file) {
	let data;
	try {
		data = JSON.parse(readFileSync(file, 'utf8'));
	} catch (error) {
		if (error.code === 'ENOENT') throw new Error(`${file} is missing: write it with python -I tools/pages.py outline --write`);
		throw new Error(`${file}: ${error.message}`);
	}
	return indexOutline(data, file);
}

/** A track's reading order: its entries without the side steps. */
export function trackOrder(outline, letter) {
	return outline.tracks[letter].filter((entry) => !entry.sideStep).map((entry) => entry.id);
}

/** The side steps of a track, each with the page it stands before: `[{ id, before }]`. */
export function trackSideSteps(outline, letter) {
	const entries = outline.tracks[letter];
	const result = [];
	entries.forEach((entry, index) => {
		if (!entry.sideStep) return;
		const following = entries.slice(index + 1).find((candidate) => !candidate.sideStep);
		result.push({ id: entry.id, before: following?.id ?? null });
	});
	return result;
}

/** The part of a page id ("core/time" → the part "core"), or null. */
export function partOf(outline, id) {
	return outline.partBySlug.get(String(id).split('/')[0]) ?? null;
}

/** The first row of a part, or null for a part without rows. */
export function firstRowOf(part) {
	return part?.pages[0] ?? null;
}

/**
 * The Needs a row has for its closure: its own, or, for a row with "-" that is not its part's first row, the part's
 * first row (style.md §1.2: "A page whose outline row has `-` needs the first page of its part"). The same rule as
 * tools/booklib/outline.py's needed().
 */
export function closureNeeds(outline, id) {
	const row = outline.rows.get(id);
	if (!row) return [];
	if (row.needs.length > 0) return row.needs;
	const first = firstRowOf(partOf(outline, id));
	return first && first !== id ? [first] : [];
}

/**
 * The Needs closure of a row (style.md §1.2): every row reached through its Needs, every alternative of "a|b"
 * followed, and the "-" rule of closureNeeds; the row itself is not in it. tools/booklib/outline.py's closure()
 * computes the levels of src/generated/outline.json the same way, which the tests compare row by row.
 */
export function needsClosure(outline, id) {
	const seen = new Set();
	const stack = [id];
	while (stack.length) {
		for (const need of closureNeeds(outline, stack.pop())) {
			for (const alternative of needAlternatives(need)) {
				if (alternative === id || seen.has(alternative)) continue;
				seen.add(alternative);
				stack.push(alternative);
			}
		}
	}
	return seen;
}
