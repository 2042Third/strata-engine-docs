// The glossary (src/content/glossary.json, plan/pipelines.md §9): one entry per thing, with its id, its one-sentence
// definition, the page that is its home, the page of part make where a game maker uses it, and its other names. Pages
// mark a term's use explicitly with ":term[text]{id=…}" (src/plugins/glossary.mjs); the build never links a term on its
// own. tools/pages.py check is the glossary's full check (its homes against the outline, every name in one entry); the
// build reads what it draws and refuses an entry it could not draw or link.

import { readFileSync } from 'node:fs';

// The keys of an entry (pipelines.md §9 and style.md §3; tools/pages.py's c_GlossaryKeys).
export const c_GlossaryKeys = ['id', 'term', 'definition', 'home', 'use', 'aliases', 'avoid', 'known'];

const c_PageId = /^[a-z0-9]+(-[a-z0-9]+)*(\/[a-z0-9]+(-[a-z0-9]+)*)*$/;

/** An entry's id: its term in lowercase words joined by "-", apostrophes dropped ("two's complement" → twos-complement). */
export function glossaryId(term) {
	return term.toLowerCase().replace(/['’]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
}

/** Reads glossary.json: `{ terms, byId }`; a missing file is an empty glossary. Throws with every problem of its shape. */
export function loadGlossary(file) {
	let data;
	try {
		data = JSON.parse(readFileSync(file, 'utf8'));
	} catch (error) {
		if (error.code === 'ENOENT') return { terms: [], byId: new Map() };
		throw new Error(`${file}: ${error.message}`);
	}
	const { terms, problems } = normalizeGlossary(data);
	if (problems.length) throw new Error(`${file}:\n  ${problems.join('\n  ')}`);
	return { terms, byId: new Map(terms.map((term) => [term.id, term])) };
}

function namesProblem(value) {
	return !Array.isArray(value) || value.some((name) => typeof name !== 'string' || !name.trim());
}

/** The entries of the file's data with every problem the build cannot draw past: `{ terms, problems }`. */
export function normalizeGlossary(data) {
	const problems = [];
	if (!data || typeof data !== 'object' || Array.isArray(data) || !Array.isArray(data.terms)) return { terms: [], problems: ['the glossary is {"terms": [{"id", "term", "definition", "home", …}]} (pipelines.md §9)'] };
	const names = new Map();
	const ids = new Map();
	const terms = [];
	data.terms.forEach((entry, index) => {
		const where = `term ${index + 1} (${entry?.term ?? '?'})`;
		if (!entry || typeof entry !== 'object' || Array.isArray(entry)) {
			problems.push(`term ${index + 1} is not an object {"id", "term", "definition", "home"}`);
			return;
		}
		for (const key of Object.keys(entry)) {
			if (!c_GlossaryKeys.includes(key)) problems.push(`${where}: "${key}" is not a key of an entry (${c_GlossaryKeys.join(', ')})`);
		}
		if (typeof entry.term !== 'string' || !entry.term.trim()) {
			problems.push(`${where}: "term" is missing`);
			return;
		}
		const expected = glossaryId(entry.term);
		if (entry.id === undefined) problems.push(`${where}: "id" is missing: write "id": "${expected}"`);
		else if (entry.id !== expected) problems.push(`${where}: "id" is the term in lowercase words joined by "-": write "id": "${expected}"`);
		if (ids.has(expected)) problems.push(`${where}: the id "${expected}" also names "${ids.get(expected)}": two meanings get two qualified terms ("pack block", "BC block")`);
		ids.set(expected, entry.term);
		if (typeof entry.definition !== 'string' || !/^[^.!?]+(\.[^\s.!?][^.!?]*)*[.]$/.test(entry.definition.trim())) {
			problems.push(`${where}: "definition" must be one sentence ending with a full stop`);
		}
		if (typeof entry.home !== 'string' || !c_PageId.test(entry.home)) problems.push(`${where}: "home" must be the id of the page that defines the term, such as core/time`);
		if (entry.use !== undefined && (typeof entry.use !== 'string' || !c_PageId.test(entry.use) || !entry.use.startsWith('make/'))) {
			problems.push(`${where}: "use" names the page of part make where a game maker uses the term, such as make/first-script`);
		}
		if (entry.known !== undefined && typeof entry.known !== 'boolean') problems.push(`${where}: "known" is true or false`);
		const aliases = entry.aliases ?? [];
		const avoid = entry.avoid ?? [];
		if (namesProblem(aliases)) problems.push(`${where}: "aliases" must be a list of names`);
		if (namesProblem(avoid)) problems.push(`${where}: "avoid" must be a list of names`);
		for (const name of [entry.term, ...(namesProblem(aliases) ? [] : aliases)]) {
			const key = name.toLowerCase();
			if (names.has(key)) problems.push(`${where}: the name "${name}" also names "${names.get(key)}" (one name per thing)`);
			names.set(key, entry.term);
		}
		terms.push({
			id: expected,
			term: entry.term,
			definition: entry.definition,
			home: typeof entry.home === 'string' ? entry.home : null,
			use: typeof entry.use === 'string' ? entry.use : null,
			aliases: namesProblem(aliases) ? [] : aliases,
			avoid: namesProblem(avoid) ? [] : avoid,
			known: entry.known === true,
		});
	});
	for (const term of terms) {
		for (const name of term.avoid) {
			const owner = names.get(name.toLowerCase());
			if (owner) problems.push(`"${term.term}": the avoided name "${name}" is a name of "${owner}": the book uses a name or avoids it, not both`);
		}
	}
	return { terms, problems };
}
