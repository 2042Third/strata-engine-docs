// The print view of a part (src/pages/print/[part].astro) holds every chapter of the part on one page. Ids of
// different chapters would collide there (two "summary" headings, two "user-content-fn-1" footnotes), so every id of a
// chapter gets the chapter's name in front ("core--time--summary"), and every reference to it follows: links within
// the chapter, aria-describedby and the other attributes that name ids, and links from the part's other chapters,
// which become links within the print view. What a page hides until it is asked for is shown (plan/site.md,
// "Navigation"): every <details> is open and every picture loads at once, so that a browser prints the whole part.
// The view is for printing, not for finding: it asks search engines not to index it, and it stays out of the sitemap
// (src/lib/sitemap.mjs) and out of the book's search.

import { fromHtml } from 'hast-util-from-html';
import { toHtml } from 'hast-util-to-html';
import { pageUrl } from './settings.mjs';

/** The anchor of a chapter in the print view: "core/time" → "core--time". */
export function anchorOf(id) {
	return id.replace(/\//g, '--');
}

// hast's names of the attributes whose value is one id or a list of ids.
const c_IdReferences = ['htmlFor', 'headers', 'ariaActiveDescendant', 'ariaControls', 'ariaDescribedBy', 'ariaDetails', 'ariaErrorMessage', 'ariaFlowTo', 'ariaLabelledBy', 'ariaOwns', 'popoverTarget'];

function decode(value) {
	try {
		return decodeURIComponent(value);
	} catch {
		return value;
	}
}

function elements(node, visit) {
	if (node.type === 'element') visit(node);
	for (const child of node.children ?? []) elements(child, visit);
	if (node.content) elements(node.content, visit);
}

/**
 * Every chapter loads Expressive Code's script (<script type="module" src="…/ec.….js">) after its first code block,
 * so a part's print view named it once per chapter: 45 times in print/make. A module script runs once however often
 * it is named, but Chromium's parser yields at each such element and the page so far is laid out again, so the repeats
 * made print/make (7 MB) parse in 24 s instead of 7 s. Only the first element of each external script is kept; inline
 * scripts stay where they are.
 */
function dropRepeatedScripts(node, scripts) {
	if (!node.children) return;
	node.children = node.children.filter((child) => {
		if (child.type !== 'element' || child.tagName !== 'script' || typeof child.properties?.src !== 'string') return true;
		if (scripts.has(child.properties.src)) return false;
		scripts.add(child.properties.src);
		return true;
	});
	for (const child of node.children) dropRepeatedScripts(child, scripts);
}

/**
 * The front matter of the print view of the part with the label `label` (src/pages/print/[part].astro): left out of the
 * book's search, and "noindex" for search engines.
 */
export function printFrontmatter(label) {
	return {
		title: `${label}: the whole part`,
		description: `Every page of the part “${label}” on one page, for printing.`,
		pagefind: false,
		head: [{ tag: 'meta', attrs: { name: 'robots', content: 'noindex' } }],
	};
}

/**
 * The chapter's HTML for the print view: its ids prefixed, references to them following, and links to the part's own
 * pages turned into links within the page; every <details> open and every picture loaded eagerly. A diagram's ids
 * ("dg-<hash>-<theme>…", src/lib/diagrams.mjs) are named from inside its SVG too, in url(#…) and in its style sheet, so
 * they get the chapter's name in front as text, everywhere at once: two chapters that show one diagram share no id.
 * `scripts` holds the addresses of the external scripts the view's earlier chapters load: the chapter's elements that
 * load one of them again are left out, and its own addresses are added (dropRepeatedScripts).
 */
export function prefixChapter(html, id, partPages, base, scripts = new Set()) {
	const prefix = anchorOf(id);
	const diagramIds = `${prefix}--dg-`;
	const tree = fromHtml(html.replace(/\bdg-([0-9a-f]{16}-(?:light|dark))/g, `${diagramIds}$1`), { fragment: true });
	dropRepeatedScripts(tree, scripts);
	const ids = new Set();
	elements(tree, (node) => {
		if (node.tagName === 'details') node.properties.open = true;
		if (node.tagName === 'img') node.properties.loading = 'eager';
		const own = node.properties?.id;
		if (typeof own === 'string' && own && !own.startsWith(diagramIds)) {
			ids.add(own);
			node.properties.id = `${prefix}--${own}`;
		}
	});
	const pageLinks = [...partPages].map((page) => ({ url: pageUrl(base, page), anchor: anchorOf(page) }));
	elements(tree, (node) => {
		const properties = node.properties ?? {};
		for (const name of c_IdReferences) {
			const value = properties[name];
			if (Array.isArray(value)) properties[name] = value.map((item) => (ids.has(String(item)) ? `${prefix}--${item}` : item));
			else if (typeof value === 'string' && ids.has(value)) properties[name] = `${prefix}--${value}`;
		}
		if (typeof properties.href !== 'string') return;
		const href = properties.href;
		if (href.startsWith('#')) {
			// The fragment is compared decoded (the links plugin writes "#%C3%BCber-die-zeit" for the id "über-die-zeit")
			// and written back as it was.
			if (ids.has(decode(href.slice(1)))) properties.href = `#${prefix}--${href.slice(1)}`;
			return;
		}
		for (const page of pageLinks) {
			if (href === page.url) properties.href = `#${page.anchor}`;
			else if (href.startsWith(`${page.url}#`)) properties.href = `#${page.anchor}--${href.slice(page.url.length + 1)}`;
			else continue;
			return;
		}
	});
	return toHtml(tree, { allowDangerousHtml: true });
}
