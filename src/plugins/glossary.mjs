// glossary: a writer marks the first use of a term on a page, ":term[draw calls]{id=draw-call}" (plan/style.md §3; an
// unknown id fails the build). The mark becomes a link to the term's entry on the glossary page and a button that opens
// a popover with the definition and a link to the term's home page (plan/site.md, "Glossary"); later marks of the same
// term are plain words. The build links nothing on its own: a use the writer did not mark stays text, and the style
// linter (tools/lint.py, term-mark) reports it. "::glossary" on the reference page draws every entry as one list.

import { pageUrl } from '../lib/settings.mjs';
import { element, pageOf, report, text, withoutTerms } from './shared.mjs';

export const c_GlossaryPage = 'reference/glossary';

/** The id of the popover that holds a term's definition on a page (no heading or glossary entry starts so). */
export function termPopoverId(term) {
	return `book-term-${term.id}`;
}

/**
 * The first marked use of a term (site.md, "Glossary"): a link to its glossary entry, then a small button that opens a
 * native popover with the definition and a link to the term's home page. The popover needs no script: the button
 * opens it, Escape closes it and focus stays on the button. A browser without popovers shows the link only (the style
 * sheet hides the button and the popover there).
 */
export function termUse(term, children, { href, home, base }) {
	const id = termPopoverId(term);
	const definition = [element('strong', {}, [text(term.term)]), text(`: ${term.definition}`)];
	if (home) definition.push(text(' '), element('a', { href: pageUrl(base, home.route) }, [text(`Read: ${home.title}`)]));
	return withoutTerms(element('span', { className: ['book-term-use'] }, [
		element('a', { className: ['book-term'], href }, children),
		// Search leaves out the button's words ("? Definition of <term>"): on every page that uses a term they would
		// count for that page instead of the term's home (site.md, "Search").
		element('button', { type: 'button', className: ['book-term__button'], popoverTarget: id, dataPagefindIgnore: '' }, [
			element('span', { ariaHidden: 'true' }, [text('?')]),
			element('span', { className: ['sr-only'] }, [text(`Definition of ${term.term}`)]),
		]),
		element('span', { id, popover: 'auto', className: ['book-term__popover'], dataPagefindIgnore: '' }, definition),
	]));
}

// The places a term mark cannot stand: its link and button would sit in a heading (and in the table of contents), in
// another link, or in an element hidden from screen readers or opened by a click (an aside's title, an answer's
// summary).
function markPlaceProblem(ancestors) {
	for (const node of ancestors) {
		if (node.type === 'heading') return 'a :term mark stands in a sentence, not in a heading: mark the term\'s first use in the text below it';
		if (node.type === 'link' || node.type === 'linkReference' || node.data?.hName === 'a') return 'a :term mark does not stand inside a link';
		if (node.data?.bookNoTerms) return 'a :term mark does not stand in a title or a summary the book draws (an aside\'s title, an answer\'s summary): mark the term in the text';
	}
	return null;
}

/**
 * Turns ":term[text]{id=…}" marks into the first use of each term (a link with its popover); a later mark of the same
 * term on the page is plain words (style.md §3).
 */
function linkMarkedTerms(tree, file, context, page, index) {
	const linked = new Set();
	const base = context.settings.base;
	const visit = (parent, ancestors) => {
		(parent.children ?? []).forEach((node, position) => {
			if (node.type !== 'textDirective' || node.name !== 'term') {
				visit(node, [...ancestors, node]);
				return;
			}
			const id = node.attributes?.id;
			const term = id ? context.glossary.byId.get(id) : null;
			if (!term) {
				report(file, node, id ? `:term{id=${id}}: the glossary has no entry "${id}"` : ':term[…] needs the id of its glossary entry: :term[text]{id=…}');
				return;
			}
			const place = markPlaceProblem(ancestors);
			if (place) {
				report(file, node, place);
				return;
			}
			const children = node.children.length ? node.children : [text(term.term)];
			if (linked.has(term.id)) {
				parent.children[position] = element('span', {}, children);
				return;
			}
			const home = term.home && term.home !== page.id ? index.pages.get(term.home) : null;
			parent.children[position] = termUse(term, children, { href: `${pageUrl(base, c_GlossaryPage)}#${term.id}`, home, base });
			linked.add(term.id);
		});
	};
	visit(tree, []);
}

/** A link to a written page of the book, "<label>: <its title>", or null while the page is not written. */
function pageLink(label, id, index, base) {
	const page = id ? index.pages.get(id) : null;
	return page ? element('a', { href: pageUrl(base, page.route) }, [text(`${label}: ${page.title}`)]) : null;
}

/**
 * The list of every entry, in alphabetical order: one <dl>, each <dt> carrying the entry's id (the anchor marks link)
 * and data-pagefind-title, which makes it a result of its own in search (site.md, "Glossary"); each <dd> the
 * definition, the home page and, for a term a game maker acts on, the page of part make where it is used.
 */
export function glossaryList(terms, index, base) {
	const items = [];
	for (const term of [...terms].sort((a, b) => a.term.localeCompare(b.term, 'en'))) {
		// Search finds an entry by its term and its other names. The definition and the links stay out of the search
		// index: the home page defines the term in its own words and is indexed, and with every definition the
		// glossary's fragment, which a search for any term loads, was 100 KB of the 300 KB one search may download
		// (plan/site.md, budget row 12).
		const definition = [text(term.definition)];
		for (const link of [pageLink('Read', term.home, index, base), pageLink('Used in', term.use, index, base)]) {
			if (link) definition.push(text(' '), link);
		}
		const details = [element('span', { className: ['book-glossary__definition'], dataPagefindIgnore: '' }, definition)];
		if (term.aliases.length) details.push(element('span', { className: ['book-glossary__aliases'] }, [text(` Also called: ${term.aliases.join(', ')}.`)]));
		items.push(element('dt', { id: term.id, dataPagefindTitle: term.term }, [text(term.term)]));
		items.push(element('dd', {}, details));
	}
	return element('dl', { className: ['book-glossary'] }, items);
}

export function remarkBookGlossary(context) {
	return function attacher() {
		return async function transformer(tree, file) {
			const index = await context.index();
			const page = pageOf(file, index);
			if (!page) return;
			const replaceLists = (parent) => {
				(parent.children ?? []).forEach((node, position) => {
					if (node.type === 'leafDirective' && node.name === 'glossary') {
						if (page.id !== c_GlossaryPage) report(file, node, `::glossary belongs on ${c_GlossaryPage}.md`);
						// One entry per term in the table of contents would be thousands of links on every side of the page.
						else if (page.data?.tableOfContents !== false) report(file, node, `${c_GlossaryPage}.md sets "tableOfContents: false" in its front matter: the list of every term needs no table of contents`);
						parent.children[position] = glossaryList(context.glossary.terms, index, context.settings.base);
					} else replaceLists(node);
				});
			};
			replaceLists(tree);
			linkMarkedTerms(tree, file, context, page, index);
			if (page.id !== c_GlossaryPage && context.glossary.terms.length > 0 && !index.pages.has(c_GlossaryPage)) {
				report(file, tree, `src/content/glossary.json has terms, but the glossary page ${c_GlossaryPage}.md does not exist`);
			}
		};
	};
}
