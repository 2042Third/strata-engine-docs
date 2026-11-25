// The page index: every page of the book with its front matter and anchors, read from the Markdown files before any
// page is rendered. The links plugin checks targets and anchors against it, the strips check the front matter, and the
// sidebar, the tracks and the top strip read which pages are written from it. Files are re-read only when they change,
// so the dev server stays fast.
//
// A page's anchors include those of what the build puts into it: the generated reference a reference page includes
// (::include, src/generated/reference/) and the generated part of a part's index and review page (src/lib/partpages.mjs),
// in the order the page shows them, so that a link to any of its headings is checked like any other.
//
// A page is known by its book id, the file's path under src/content/docs/ without .md (rule O1): "core/time", the part
// page "core/index", the landing page "index". Its route id is the one Starlight serves it under: "core" for
// "core/index".

import { readFile, readdir, stat } from 'node:fs/promises';
import path from 'node:path';
import GithubSlugger from 'github-slugger';
import { readFileSync, statSync } from 'node:fs';
import { captureAnchor, captureOf, figureAnchor } from './figures.mjs';
import { headingText, parseMarkdown, splitFrontmatter, walk } from './markdown.mjs';
import { partPageContent } from './partpages.mjs';
import { routeIdOf } from './sidebar.mjs';

/** Book id of a file below the docs folder: "core/time.md" → "core/time", "make/index.md" → "make/index". */
export function pageIdOf(relativePath) {
	return relativePath.split(path.sep).join('/').replace(/\.md$/, '');
}

/** The mermaid fences of a page: `{ source, meta, line }` each (line counted in the whole file). */
export function collectDiagrams(tree, bodyLine) {
	const diagrams = [];
	walk(tree, (node) => {
		if (node.type === 'code' && node.lang === 'mermaid') diagrams.push({ source: node.value, meta: node.meta ?? '', line: (node.position?.start.line ?? 1) + bodyLine - 1 });
	});
	return diagrams;
}

/** Whether a heading holds math: its anchor would be slugged from KaTeX's output, which the index cannot know. */
export function hasMath(node) {
	return node.type === 'inlineMath' || (node.children ?? []).some(hasMath);
}

/**
 * The anchors a page's body defines: heading slugs as Astro makes them, figure ids (of pictures and of text figures),
 * and the glossary's entries.
 * Headings with math get none: Astro slugs the formula as KaTeX draws it, and tools/lint.py refuses math in headings
 * (deep-heading), so the links plugin refuses links to them instead of accepting an anchor the page lacks.
 */
export function collectAnchors(tree, glossaryIds = [], { include = () => null } = {}) {
	const slugger = new GithubSlugger();
	const anchors = new Set(['_top']);
	const figures = new Set();
	const visit = (root) => walk(root, (node) => {
		if (node.type === 'heading') {
			if (!hasMath(node)) anchors.add(slugger.slug(headingText(node)));
		} else if ((node.type === 'leafDirective' || node.type === 'containerDirective') && (node.name === 'figure' || node.name === 'compare') && node.attributes?.id) {
			anchors.add(figureAnchor(figures, node));
		} else if (node.type === 'code') {
			const capture = captureOf(node.meta);
			if (capture?.id) anchors.add(captureAnchor(figures, capture));
		} else if (node.type === 'leafDirective' && node.name === 'glossary') {
			for (const id of glossaryIds) anchors.add(id);
		} else if (node.type === 'leafDirective' && node.name === 'include') {
			// The included file's headings stand where the directive does.
			const included = include(node.attributes?.file);
			if (included) visit(included);
			return false;
		}
		return undefined;
	});
	visit(tree);
	return anchors;
}

/** The file an ::include names, under the generated reference folder, or null when the name is not one. */
export function includedFile(referenceDir, name) {
	if (typeof name !== 'string' || !/^[a-z0-9]+(-[a-z0-9]+)*(\/[a-z0-9]+(-[a-z0-9]+)*)*\.md$/.test(name)) return null;
	return path.join(referenceDir, ...name.split('/'));
}

/**
 * Reads and parses an included file: `{ file, text, tree, mtimeMs, size }`, or null when the name is not one or the file
 * does not exist (the include plugin reports both). The tree is the file's Markdown parsed as a page body is.
 */
export function readIncluded(referenceDir, name) {
	const file = includedFile(referenceDir, name);
	if (!file) return null;
	try {
		const info = statSync(file);
		const text = readFileSync(file, 'utf8');
		return { file, text, tree: parseMarkdown(text), mtimeMs: info.mtimeMs, size: info.size };
	} catch (error) {
		if (error.code === 'ENOENT') return null;
		throw error;
	}
}

/** The nodes of a page's "## Check yourself" section, without its heading, or null when it has none. */
export function checkYourselfNodes(tree) {
	const start = tree.children.findIndex((node) => node.type === 'heading' && node.depth === 2 && headingText(node).trim() === 'Check yourself');
	if (start < 0) return null;
	const end = tree.children.findIndex((node, index) => index > start && node.type === 'heading' && node.depth <= 2);
	return tree.children.slice(start + 1, end < 0 ? undefined : end);
}

/** How many headings of a page hold math (they have no anchor in the index). */
export function countMathHeadings(tree) {
	let count = 0;
	walk(tree, (node) => {
		if (node.type === 'heading' && hasMath(node)) count++;
	});
	return count;
}

async function listMarkdown(folder, relative = '') {
	let entries;
	try {
		entries = await readdir(path.join(folder, relative), { withFileTypes: true });
	} catch (error) {
		if (error.code === 'ENOENT') return [];
		throw error;
	}
	const files = [];
	for (const entry of entries) {
		// Starlight's docs loader ignores names that start with "_" (generated fragments live there).
		if (entry.name.startsWith('_') || entry.name.startsWith('.')) continue;
		const child = path.join(relative, entry.name);
		if (entry.isDirectory()) files.push(...(await listMarkdown(folder, child)));
		else if (entry.isFile() && entry.name.endsWith('.md')) files.push(child);
	}
	return files;
}

/**
 * Reads one page. Front matter errors are kept on the page (the strips plugin reports them with the file's name).
 * `referenceDir` is the folder ::include reads.
 */
export function indexPage(relative, file, text, { glossaryIds = [], referenceDir = null } = {}) {
	const id = pageIdOf(relative);
	let data = null;
	let error = null;
	let body = text;
	let bodyLine = 1;
	try {
		({ data, body, bodyLine } = splitFrontmatter(text));
		if (data === null) error = 'the page has no front matter';
	} catch (cause) {
		error = `the front matter is not valid YAML: ${cause.message}`;
	}
	data ??= {};
	const tree = parseMarkdown(body);
	const includes = [];
	const include = (name) => {
		if (!referenceDir) return null;
		const included = readIncluded(referenceDir, name);
		includes.push({ file: includedFile(referenceDir, name), mtimeMs: included?.mtimeMs ?? null, size: included?.size ?? null });
		return included?.tree ?? null;
	};
	const anchors = collectAnchors(tree, glossaryIds, { include });
	const generated = data.generated !== undefined;
	return {
		id,
		route: routeIdOf(id),
		file,
		relative: relative.split(path.sep).join('/'),
		part: id === 'index' || id === '404' ? null : id.split('/')[0],
		data,
		error,
		title: typeof data.title === 'string' ? data.title : id,
		kind: data.kind,
		needs: Array.isArray(data.needs) ? data.needs.filter((need) => typeof need === 'string') : [],
		anchors,
		mathHeadings: countMathHeadings(tree),
		diagrams: collectDiagrams(tree, bodyLine),
		includes,
		checkYourself: generated ? null : checkYourselfNodes(tree),
		// A part page's own text, parsed again with its generated part once every page is known (completePartPages).
		body: generated ? body : null,
		bodyLine,
	};
}

/** Whether the files a page includes are still the ones its cached index entry read. */
function includesCurrent(includes) {
	return includes.every(({ file, mtimeMs, size }) => {
		if (!file) return true;
		try {
			const info = statSync(file);
			return info.mtimeMs === mtimeMs && info.size === size;
		} catch (error) {
			if (error.code === 'ENOENT') return mtimeMs === null;
			throw error;
		}
	});
}

/**
 * The anchors and diagrams of every part page, with its generated part where the page shows it: after the part
 * editor's text on an index page, before it on a review page (src/lib/partpages.mjs).
 */
export function completePartPages(pages, outline, glossaryIds = []) {
	if (!outline) return;
	const questions = new Map();
	for (const [id, page] of pages) if (page.checkYourself?.length) questions.set(id, page.checkYourself);
	for (const page of pages.values()) {
		if (page.body === null || page.error) continue;
		const content = partPageContent(page, outline, pages, questions);
		if (!content) continue;
		const own = parseMarkdown(page.body).children;
		const root = { type: 'root', children: content.after ? [...own, ...content.nodes] : [...content.nodes, ...own] };
		page.anchors = collectAnchors(root, glossaryIds);
		page.mathHeadings = countMathHeadings(root);
		page.diagrams = [...collectDiagrams({ type: 'root', children: own }, page.bodyLine), ...content.diagrams.map((diagram) => ({ ...diagram, line: page.bodyLine }))];
	}
}

const s_FileCache = new Map();
const s_Indexes = new Map();

/**
 * The index of every page below `docsDir`: `{ pages: Map<id, page>, byFile: Map<absolute path, id> }`. In builds it is
 * read once per process; with `revalidate` (the dev server) every call re-checks the files' sizes and times.
 */
export async function loadPageIndex(docsDir, { glossaryIds = [], revalidate = false, referenceDir = null, outline = null, omit = new Set() } = {}) {
	const key = `${docsDir}\n${glossaryIds.length}`;
	if (!revalidate && s_Indexes.has(key)) return s_Indexes.get(key);
	const promise = (async () => {
		const pages = new Map();
		const byFile = new Map();
		for (const relative of (await listMarkdown(docsDir)).sort()) {
			if (omit.has(relative.split(path.sep).join('/').slice(0, -'.md'.length))) continue;
			const file = path.join(docsDir, relative);
			const info = await stat(file);
			const cacheKey = `${file}\n${glossaryIds.length}`;
			let cached = s_FileCache.get(cacheKey);
			if (!cached || cached.mtimeMs !== info.mtimeMs || cached.size !== info.size || !includesCurrent(cached.page.includes)) {
				cached = { mtimeMs: info.mtimeMs, size: info.size, page: indexPage(relative, file, await readFile(file, 'utf8'), { glossaryIds, referenceDir }) };
				s_FileCache.set(cacheKey, cached);
			}
			const page = cached.page;
			if (pages.has(page.id)) throw new Error(`two files make the page "${page.id}": ${pages.get(page.id).relative} and ${page.relative}`);
			pages.set(page.id, page);
			byFile.set(normalizeFile(file), page.id);
		}
		completePartPages(pages, outline, glossaryIds);
		return { pages, byFile };
	})();
	s_Indexes.set(key, promise);
	return promise;
}

/** Comparable form of a file path (Windows paths differ in separators and drive letter case between tools). */
export function normalizeFile(file) {
	const resolved = path.resolve(file).split(path.sep).join('/');
	return /^[a-zA-Z]:/.test(resolved) ? resolved[0].toLowerCase() + resolved.slice(1) : resolved;
}
