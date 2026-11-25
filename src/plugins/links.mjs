// links: a link between pages is a relative path to the other page's .md file ("../core/time.md#the-accumulator").
// The plugin turns it into the page's URL under the site's base and fails the build when the file or the anchor does
// not exist. Links that start with "/" fail too: content never writes the base path, so that the site works under any
// base. Plain Markdown images fail as well: pictures come from figure manifests (::figure).

import path from 'node:path';
import { pageIdOf, normalizeFile } from '../lib/pages.mjs';
import { pageUrl } from '../lib/settings.mjs';
import { pageOf, report } from './shared.mjs';

const c_Scheme = /^[a-z][a-z0-9+.-]*:/i;

/** Why an anchor may be missing: headings with math have none that a link can name. */
function mathHint(page) {
	return page.mathHeadings ? ' (a heading with math has no anchor a link can name: Astro slugs the formula as KaTeX draws it; take the math out of the heading, as tools/lint.py asks)' : '';
}

/** decodeURIComponent, or null when the text is not valid percent-encoding ("#100%"). */
function decode(value) {
	try {
		return decodeURIComponent(value);
	} catch {
		return null;
	}
}

/**
 * What a link's URL means: `{ kind: 'external' }`, `{ kind: 'anchor', anchor }`, `{ kind: 'page', target, anchor }`
 * or `{ kind: 'error', message }`. `from` is the page holding the link; `pages` the index.
 */
export function resolveLink(url, from, docsDir, pages) {
	if (c_Scheme.test(url)) return { kind: 'external' };
	if (url.startsWith('//')) return { kind: 'error', message: `"${url}" names another host without a scheme: write https://…` };
	if (url.startsWith('/')) return { kind: 'error', message: `"${url}" is an absolute path: link to the page's .md file with a relative path (the base path is added by the build)` };
	if (url.includes('?')) return { kind: 'error', message: `"${url}" has a query string, which pages of a static book do not read` };
	const hash = url.indexOf('#');
	const target = hash >= 0 ? url.slice(0, hash) : url;
	const anchor = hash >= 0 ? decode(url.slice(hash + 1)) : null;
	const decodedTarget = decode(target);
	if ((hash >= 0 && anchor === null) || decodedTarget === null) return { kind: 'error', message: `"${url}" holds a "%" that is not percent-encoding: write %25 for a percent sign` };
	if (target === '') {
		if (!anchor) return { kind: 'error', message: 'an empty link' };
		return from.anchors.has(anchor) ? { kind: 'anchor', anchor } : { kind: 'error', message: `"#${anchor}": this page has no heading or figure with that anchor${mathHint(from)}` };
	}
	if (!target.endsWith('.md')) return { kind: 'error', message: `"${url}" does not name a .md file: links between pages point at the other page's Markdown file` };
	const absolute = path.resolve(path.dirname(from.file), decodedTarget);
	const relative = path.relative(docsDir, absolute);
	if (relative.startsWith('..') || path.isAbsolute(relative)) return { kind: 'error', message: `"${url}" leaves the book's pages (src/content/docs)` };
	const id = pageIdOf(relative);
	const page = pages.get(id);
	if (!page || normalizeFile(page.file) !== normalizeFile(absolute)) return { kind: 'error', message: `"${url}": there is no page ${relative.split(path.sep).join('/')}`, missing: id };
	if (anchor !== null && !page.anchors.has(anchor)) return { kind: 'error', message: `"${url}": the page ${id} has no heading or figure with the anchor "${anchor}"${mathHint(page)}` };
	return { kind: 'page', target: page, anchor };
}

export function remarkBookLinks(context) {
	return function attacher() {
		return async function transformer(tree, file) {
			const index = await context.index();
			const page = pageOf(file, index);
			if (!page) return;
			const { base, docsDir, preview } = context.settings;
			const visit = (node) => {
				if (node.type === 'link' || node.type === 'definition') {
					const resolved = resolveLink(node.url, page, docsDir, index.pages);
					if (resolved.kind === 'error' && preview && node.type === 'link' && resolved.missing && context.outline.rows.has(resolved.missing)) {
						// A preview draws a link to a page not written yet as its text, marked for the reader.
						node.type = 'emphasis';
						delete node.url;
						delete node.title;
						node.data = { hName: 'span', hProperties: { className: ['book-unwritten'], title: 'This page is not written yet' } };
					} else if (resolved.kind === 'error') report(file, node, resolved.message);
					else if (resolved.kind === 'page') node.url = pageUrl(base, resolved.target.route) + (resolved.anchor ? `#${encodeURIComponent(resolved.anchor)}` : '');
				} else if (node.type === 'image' || node.type === 'imageReference') {
					report(file, node, 'Markdown images are not used in the book: add the picture to the chapter\'s figure manifest and write ::figure{id=…}');
				} else if (node.type === 'linkReference' && !node.children?.length) {
					report(file, node, `the reference link [${node.identifier}] has no text`);
				}
				for (const child of node.children ?? []) visit(child);
			};
			visit(tree);
		};
	};
}
