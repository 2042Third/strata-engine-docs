// Helpers shared by the book's remark and rehype plugins: building HTML elements inside the Markdown tree, reporting
// problems with their place in the page, finding the page a file is, and reading the attributes of code fences.

import path from 'node:path';
import { normalizeFile } from '../lib/pages.mjs';

/**
 * A node of the Markdown tree that becomes the element `tagName` in HTML. Its children are Markdown and are converted
 * as usual, so code blocks inside it still reach Expressive Code.
 */
export function element(tagName, properties = {}, children = []) {
	return { type: 'bookElement', data: { hName: tagName, hProperties: properties }, children };
}

/** A node that becomes the given HTML (hast) children as they are. */
export function hastElement(tagName, properties, hastChildren) {
	return { type: 'bookElement', data: { hName: tagName, hProperties: properties, hChildren: hastChildren }, children: [] };
}

/**
 * Marks a node whose text is the build's own words (labels, titles, summaries, placeholders): a :term mark may not stand
 * in it (src/plugins/glossary.mjs), and the glossary's links are never drawn there.
 */
export function withoutTerms(node) {
	node.data.bookNoTerms = true;
	return node;
}

export function text(value) {
	return { type: 'text', value };
}

/** Raw HTML (rendered SVG); parsed into the page by rehype-raw at the end of Astro's pipeline. */
export function rawHtml(value) {
	return { type: 'html', value };
}

/**
 * Records a problem of the page at a node; the report plugin fails the build with all of them at the end. A directive
 * a plugin reported is marked, so that the report does not add "unknown directive" for it. A node that came from
 * another file (an included table, a question copied onto a part's review page) carries `data.bookOrigin`: the problem
 * is reported at the place of the page that holds it, with the file and line it came from.
 */
export function report(file, node, message) {
	const start = node?.position?.start;
	const origin = node?.data?.bookOrigin;
	file.data.bookProblems ??= [];
	if (origin) {
		const from = start ? `${origin.file}:${start.line}:${start.column}` : origin.file;
		file.data.bookProblems.push({ line: origin.at?.line ?? 0, column: origin.at?.column ?? 0, message, origin: `from ${from}` });
	} else {
		file.data.bookProblems.push({ line: start?.line ?? 0, column: start?.column ?? 0, message });
	}
	if (node && typeof node.type === 'string' && node.type.endsWith('Directive')) {
		node.data ??= {};
		node.data.bookReported = true;
	}
}

/**
 * Marks every node of `nodes` (and their children) as coming from `file` (relative to the project), inserted on the page
 * at the position `at`; see report.
 */
export function markOrigin(nodes, file, at) {
	const visit = (node) => {
		node.data ??= {};
		node.data.bookOrigin = { file, at };
		for (const child of node.children ?? []) visit(child);
	};
	nodes.forEach(visit);
	return nodes;
}

/** The page a Markdown file is, or null for files outside the book (the plugins leave those alone). */
export function pageOf(file, index) {
	if (!file.path) return null;
	const id = index.byFile.get(normalizeFile(file.path));
	return id === undefined ? null : index.pages.get(id);
}

/** The file's path relative to the project, for messages. */
export function displayPath(file, root) {
	return file.path ? path.relative(root, file.path).split(path.sep).join('/') : '<unknown file>';
}

/** Reads a directive's label (`:::tab[Label]`): its text, and removes the label paragraph from the children. */
export function takeDirectiveLabel(node) {
	const first = node.children?.[0];
	if (first?.type === 'paragraph' && first.data?.directiveLabel) {
		node.children.shift();
		return { text: plainText(first), nodes: first.children };
	}
	return null;
}

export function plainText(node) {
	if (node.type === 'text' || node.type === 'inlineCode') return node.value;
	return (node.children ?? []).map(plainText).join('');
}

// A fence's meta string is read as the page index reads it (src/lib/markdown.mjs).
export { parseMeta } from '../lib/markdown.mjs';
