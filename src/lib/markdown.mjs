// Parsing of the book's Markdown outside the build's own pipeline: the page index reads every page's front matter and
// anchors before any page is rendered. The syntax extensions are the build's (GFM, smart punctuation, math,
// directives), so that a heading gets the same anchor here as Astro gives it.

import { isMap, isScalar, isSeq, parseDocument, visit } from 'yaml';
import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkGfm from 'remark-gfm';
import remarkSmartypants from 'remark-smartypants';
import remarkMath from 'remark-math';
import remarkDirective from 'remark-directive';

// As Astro finds front matter (@astrojs/internal-helpers/frontmatter): at the very start, after a byte-order mark
// (Notepad writes one) or after blank lines. tools/booklib/frontmatter.py reads the same.
const c_FrontmatterPattern = /^\uFEFF?(?:[ \t]*\r?\n)*---\r?\n([\s\S]*?)\r?\n---[ \t]*(?:\r?\n|$)/;
const c_Key = /^[A-Za-z_][A-Za-z0-9_-]*$/;

/**
 * Why a front matter document is outside the subset of YAML that tools/booklib/frontmatter.py reads (the Python twin
 * of this module, which has no YAML library), or null. The subset: "key: value" pairs, values that are scalars, lists
 * of scalars, one level of "key: value" lines (Starlight's hero), or a block list of block mappings of scalars (the
 * objectives, style.md §6.1: "- id: …" and "text: …"); no block scalars, anchors, aliases or tags.
 */
export function subsetProblem(document) {
	let problem = null;
	const collections = (path) => path.filter((node) => isMap(node) || isSeq(node));
	visit(document, {
		Alias() {
			problem ??= 'aliases (*name) are not part of the book\'s front matter';
			return visit.BREAK;
		},
		Scalar(key, node) {
			if (node.type === 'BLOCK_LITERAL' || node.type === 'BLOCK_FOLDED') problem ??= 'block scalars (| and >) are not part of the book\'s front matter: write the value on one line';
			else if (node.anchor || node.tag) problem ??= 'anchors (&name) and tags (!tag) are not part of the book\'s front matter';
			if (problem) return visit.BREAK;
		},
		Pair(key, node) {
			if (!isScalar(node.key) || typeof node.key.value !== 'string' || !c_Key.test(node.key.value)) problem ??= `the key ${JSON.stringify(String(node.key?.value ?? node.key))} is not a name of letters, digits, "_" and "-"`;
			if (problem) return visit.BREAK;
		},
		Map(key, node, path) {
			const above = collections(path);
			if (above.length === 0) return undefined;
			// A mapping under a top-level key, or one item of a block list under a top-level key.
			const underKey = above.length === 1 && isMap(above[0]);
			const listItem = above.length === 2 && isMap(above[0]) && isSeq(above[1]) && !above[1].flow;
			if (!underKey && !listItem) problem ??= 'nested lists and mappings are not part of the book\'s front matter';
			else if (node.flow) problem ??= 'mappings in braces ({…}) are not part of the book\'s front matter: write one "key: value" line each';
			else if (node.items.some((pair) => !isScalar(pair.value) && pair.value !== null)) problem ??= 'only "key: value" lines are read inside a mapping of the front matter';
			if (problem) return visit.BREAK;
			return undefined;
		},
		Seq(key, node, path) {
			const above = collections(path);
			if (above.length !== 1 || !isMap(above[0])) problem ??= 'nested lists and mappings are not part of the book\'s front matter';
			else if (node.items.some(isMap) && !node.items.every(isMap)) problem ??= 'a list of the front matter holds either "key: value" items or plain values, not both';
			if (problem) return visit.BREAK;
			return undefined;
		},
	});
	return problem;
}

/**
 * Splits "---\n<yaml>\n---\n<body>"; `data` is null when the file has no front matter. Throws on YAML errors and on
 * YAML outside the subset the Python tools read. YAML is read as Astro reads it (the core schema, merge keys,
 * timestamps).
 */
export function splitFrontmatter(text) {
	const match = c_FrontmatterPattern.exec(text);
	if (!match) return { data: null, body: text.replace(/^\uFEFF/, ''), bodyLine: 1 };
	const document = parseDocument(match[1], { customTags: ['timestamp'], merge: true, schema: 'core' });
	if (document.errors.length) throw document.errors[0];
	const problem = subsetProblem(document);
	if (problem) throw new Error(problem);
	const data = document.toJS() ?? {};
	if (typeof data !== 'object' || Array.isArray(data)) throw new Error('the front matter is not a mapping of keys to values');
	const bodyLine = match[0].split('\n').length;
	return { data, body: text.slice(match[0].length), bodyLine };
}

let s_Parser = null;

/** The mdast of a page body, parsed with the build's syntax extensions. */
export function parseMarkdown(body) {
	s_Parser ??= unified().use(remarkParse).use(remarkGfm).use(remarkSmartypants).use(remarkMath).use(remarkDirective);
	return s_Parser.runSync(s_Parser.parse(body));
}

/**
 * The text Astro's rehype-heading-ids slugs for a heading: its text nodes (with "{" written as "${", as Astro does for
 * Markdown) and the raw text of inline code.
 */
export function headingText(node) {
	let text = '';
	const walk = (current) => {
		if (current.type === 'text') text += current.value.replace(/\{/g, '${');
		else if (current.type === 'inlineCode') text += current.value;
		else if (current.type === 'inlineMath') text += current.value;
		else if (Array.isArray(current.children)) current.children.forEach(walk);
	};
	(node.children ?? []).forEach(walk);
	return text;
}

// name=value (quoted, in braces, a regular expression or one word), a range in braces, a quoted text or regular
// expression marker of Expressive Code (which may hold spaces), or one word.
const c_MetaToken = /([A-Za-z_][\w-]*)=("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|\{[^}]*\}|\/(?:[^/\\]|\\.)+\/|\S+)|\{[^}]*\}|"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|\/(?:[^/\\\s]|\\.)(?:[^/\\]|\\.)*\/|\S+/g;

/**
 * Splits a fence's meta string into attributes: `{ attributes: Map<name, value>, flags: Set, rest: [tokens] }`. The
 * names in `own` are the book's (src, mark, sketch, pseudocode); every other token is kept, in order, for Expressive
 * Code (`title="…"`, `{3-5}`, `ins={2}`).
 */
export function parseMeta(meta, own) {
	const attributes = new Map();
	const flags = new Set();
	const rest = [];
	for (const match of (meta ?? '').matchAll(c_MetaToken)) {
		const [token, name, rawValue] = match;
		if (name && own.includes(name)) {
			let value = rawValue;
			if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) value = value.slice(1, -1).replace(/\\(.)/g, '$1');
			attributes.set(name, value);
		} else if (!name && own.includes(token)) {
			flags.add(token);
		} else {
			rest.push(token);
		}
	}
	return { attributes, flags, rest };
}

/** Calls `visitor(node, parent, index)` for every node in document order. Return false to skip a node's children. */
export function walk(tree, visitor) {
	const visit = (node, parent, index) => {
		if (visitor(node, parent, index) === false) return;
		if (Array.isArray(node.children)) {
			for (let i = 0; i < node.children.length; i++) visit(node.children[i], node, i);
		}
	};
	visit(tree, null, null);
}
