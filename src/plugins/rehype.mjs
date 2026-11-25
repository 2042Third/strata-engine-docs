// The book's HTML-stage plugins.
// - math: KaTeX renders formulas at build time (rehype-katex), but reports a formula it cannot render only as a
//   warning and draws it in red; the book fails the build instead. The Markdown stage checks every formula first
//   (src/plugins/math.mjs), so this is the net behind it: each failure once, at the best place known.
// - strip: wraps the bottom strip (from "Summary" to the end) in a section of its own, styled and printed as a block.
// - search: line numbers of code blocks and KaTeX's drawn formulas stay out of the search index, and code blocks weigh
//   less than prose (runs after Expressive Code, which draws the code blocks).
// - anchor icons: the heading links' icon is defined once per page and used by each link.

import { report } from './shared.mjs';
import { throwProblems } from './report.mjs';

export function rehypeBookMath(context) {
	return function attacher() {
		return function transformer(tree, file) {
			let messages = 0;
			for (const message of file.messages) {
				if (message.source !== 'rehype-katex') continue;
				messages++;
				// Display math has no place of its own: the nearest ancestor with a position gives the line.
				const start = message.place?.start ?? message.place ?? [...(message.ancestors ?? [])].reverse().find((node) => node.position)?.position?.start;
				report(file, { position: start ? { start } : undefined }, `math: ${message.cause?.message ?? message.reason}`);
			}
			// Each failed formula is both a message and a red element: the elements count only without messages.
			const visit = (node) => {
				const classes = node.properties?.className;
				if (messages === 0 && node.type === 'element' && Array.isArray(classes) && classes.includes('katex-error')) {
					report(file, node, `math: KaTeX cannot render ${JSON.stringify(node.properties.title ?? '')}`);
				}
				for (const child of node.children ?? []) visit(child);
			};
			visit(tree);
			throwProblems(file, context.settings.root);
		};
	};
}

function textOf(node) {
	if (node.type === 'text') return node.value;
	return (node.children ?? []).map(textOf).join('');
}

export function rehypeBookStrip() {
	return function attacher() {
		return function transformer(tree) {
			const start = tree.children.findIndex((node) => node.type === 'element' && node.tagName === 'h2' && textOf(node).trim() === 'Summary');
			if (start < 0) return;
			const strip = tree.children.splice(start);
			tree.children.push({ type: 'element', tagName: 'section', properties: { className: ['book-bottom-strip'], ariaLabel: 'Summary, questions and exercises' }, children: strip });
		};
	};
}

// What search leaves out of its index and of the fragments a result loads: the line numbers of code blocks (not words),
// and KaTeX's drawn formulas (.katex-html; the MathML beside them keeps the formula's text once, instead of three times)
// with the formula's TeX source in the MathML's <annotation> (markup, not words).
const c_SearchIgnored = ['gutter', 'katex-html'];
const c_SearchIgnoredTags = ['annotation'];

// How much a word counts in search where it stands (site.md, "Search"): a word in a code block half as much as one of
// the prose, which explains it; the generated reference (src/plugins/include.mjs) 0.3, its code blocks included.
export const c_CodeWeight = '0.5';
const c_CodeBlock = 'expressive-code';
const c_GeneratedReference = 'book-reference';

function classesOf(node) {
	const classes = node.properties?.className;
	return node.type === 'element' && Array.isArray(classes) ? classes : [];
}

export function rehypeBookSearch() {
	return function attacher() {
		return function transformer(tree) {
			const visit = (node, inReference) => {
				const classes = classesOf(node);
				if (classes.some((name) => c_SearchIgnored.includes(name)) || (node.type === 'element' && c_SearchIgnoredTags.includes(node.tagName))) {
					node.properties.dataPagefindIgnore = '';
					return;
				}
				if (classes.includes(c_CodeBlock) && !inReference) node.properties.dataPagefindWeight = c_CodeWeight;
				const nested = inReference || classes.includes(c_GeneratedReference);
				for (const child of node.children ?? []) visit(child, nested);
			};
			visit(tree, false);
		};
	};
}

// The icon of the heading links, drawn once per page (rulings-13, R59).
export const c_AnchorIconId = 'book-anchor-icon';

/**
 * anchor icons: Starlight draws the same link icon, an inline SVG of about 500 bytes, in the link of every heading
 * (src/integrations/rehype-heading-links of Starlight); a chapter has dozens and its part's print view holds them again.
 * The page keeps each icon's <svg> as it is, its size, view box and color included: the first draws the shape in a
 * group with the id "book-anchor-icon", and the others draw it through <use href="#book-anchor-icon">, so that the
 * definition stands wherever the first heading does. The print view renames the id and the references with the
 * chapter's name (src/lib/print.mjs), as it does every id. Runs after Starlight's heading links.
 */
export function rehypeBookAnchorIcons() {
	return function attacher() {
		return function transformer(tree) {
			const icons = [];
			// Starlight puts one and the same icon node into every heading link: each link gets a node of its own here
			// (shallow copies: the shape's own nodes are only moved, never changed), so that the first can hold the
			// definition and the others the reference.
			const visit = (node) => {
				const children = node.children ?? [];
				for (let index = 0; index < children.length; index++) {
					if (classesOf(children[index]).includes('sl-anchor-icon')) {
						const original = children[index];
						const icon = { ...original, children: (original.children ?? []).map((child) => (child.type === 'element' ? { ...child } : child)) };
						children[index] = icon;
						for (const child of icon.children) if (child.type === 'element' && child.tagName === 'svg') icons.push(child);
					} else {
						visit(children[index]);
					}
				}
			};
			visit(tree);
			if (icons.length === 0) return;
			const shape = JSON.stringify(icons[0].children);
			const shared = icons.filter((icon) => JSON.stringify(icon.children) === shape);
			if (shared.length < 2) return;
			const [first, ...others] = shared;
			first.children = [{ type: 'element', tagName: 'g', properties: { id: c_AnchorIconId }, children: first.children }];
			for (const icon of others) icon.children = [{ type: 'element', tagName: 'use', properties: { href: `#${c_AnchorIconId}` }, children: [] }];
		};
	};
}
