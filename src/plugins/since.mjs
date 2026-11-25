// since: ":since[0.8.0]" at the start of the first paragraph of a section marks a feature that is new in the book's
// release (plan/style.md §12 and §13): it draws the badge "New in 0.8.0" there. A whole page that is new says so
// through its front matter's `since` (the top strip's badge), so its sections carry no mark; a mark names exactly the
// book's release (engine.pin's `release`), so that a mark left behind by an older book fails when the pin moves on.

import { element, pageOf, report, text, withoutTerms } from './shared.mjs';

/** Why a :since mark stands in the wrong place, or null: it starts the first paragraph after a heading. */
export function sincePlaceProblem(node, parent, tree) {
	if (parent?.type !== 'paragraph' || parent.children[0] !== node) return ':since[…] starts its paragraph: write it before the paragraph\'s first word';
	const position = tree.children.indexOf(parent);
	if (position < 0) return ':since[…] starts the first paragraph of a section, not a paragraph inside a list, a table or an aside';
	for (let index = position - 1; index >= 0; index--) {
		const before = tree.children[index];
		if (before.type === 'heading') return null;
		if (before.type === 'paragraph') return ':since[…] starts the first paragraph of a section (style.md §12): this paragraph is not the first one after its heading';
	}
	return ':since[…] starts the first paragraph of a section (style.md §12): this paragraph stands before the page\'s first heading';
}

export function remarkBookSince(context) {
	return function attacher() {
		return async function transformer(tree, file) {
			const index = await context.index();
			const page = pageOf(file, index);
			if (!page) return;
			const release = context.settings.engine.release;
			const visit = (parent) => {
				(parent.children ?? []).forEach((node, position) => {
					if (node.type !== 'textDirective' || node.name !== 'since') {
						visit(node);
						return;
					}
					// Its text in brackets and its attributes are checked by the directives plugin.
					const label = node.children.map((child) => child.value ?? '').join('').trim();
					if (!label) return;
					if (!/^\d+\.\d+\.\d+$/.test(label)) report(file, node, `:since[${label}]: write the release as X.Y.Z, such as :since[${release}]`);
					else if (label !== release) report(file, node, `:since[${label}] marks a feature new in the book's release, which is ${release} (engine.pin): write :since[${release}], or remove the mark from a feature that is older`);
					else if (page.data?.since === release) report(file, node, `the whole page is new in ${release} (since: ${release} in its front matter, shown at the top): its sections carry no :since[${release}]`);
					const place = sincePlaceProblem(node, parent, tree);
					if (place) report(file, node, place);
					parent.children[position] = withoutTerms(element('span', { className: ['book-badge', 'book-badge--new', 'book-since'], dataPagefindIgnore: '' }, [text(`New in ${label}`)]));
				});
			};
			visit(tree);
		};
	};
}
