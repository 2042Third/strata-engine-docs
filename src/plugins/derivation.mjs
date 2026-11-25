// derivation: ":::derivation" holds a derivation the reader may skip (plan/style.md §4 and §12): a closed <details>
// titled "Where this comes from", whose first line the plugin writes, so that every such box tells the reader the same
// thing in the same words. It works without scripts; the book's script opens it before the page prints.

import { element, report, text, withoutTerms } from './shared.mjs';

export const c_DerivationTitle = 'Where this comes from';
export const c_DerivationSkip = 'You can skip this: the rest of the page does not need it.';

export function remarkBookDerivations() {
	return function attacher() {
		return function transformer(tree, file) {
			const visit = (parent) => {
				(parent.children ?? []).forEach((node, index) => {
					visit(node);
					if (node.type !== 'containerDirective' || node.name !== 'derivation') return;
					// A title in brackets is refused by the directives plugin: the box's title is always the same.
					if (node.children[0]?.data?.directiveLabel) node.children.shift();
					if (node.children.length === 0) report(file, node, 'the :::derivation box is empty: it holds the steps of a derivation');
					parent.children[index] = element('details', { className: ['book-derivation'] }, [
						withoutTerms(element('summary', {}, [text(c_DerivationTitle)])),
						element('div', { className: ['book-derivation__body'] }, [
							withoutTerms(element('p', { className: ['book-derivation__skip'] }, [text(c_DerivationSkip)])),
							...node.children,
						]),
					]);
				});
			};
			visit(tree);
		};
	};
}
