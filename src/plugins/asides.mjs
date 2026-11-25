// asides: the book's own kinds of aside beside Starlight's note, tip, caution and danger (plan/style.md §12). Each is a
// container directive with an optional title in brackets (":::why[Why a fixed step?]") and renders with Starlight's
// aside markup, so it looks and reads like the built-in ones. An analogy ends with the paragraph that says where it
// breaks ("**Where it breaks:** …"), which the plugin requires and marks.

import { element, report, takeDirectiveLabel, text, withoutTerms } from './shared.mjs';

export const c_BookAsides = {
	why: 'Why it is so',
	question: 'A question you may have',
	history: 'How it came to be',
	elsewhere: 'In other engines',
	rule: 'A rule of the engine',
	simplified: 'Simplified for now',
	analogy: 'An analogy',
	example: 'Worked example',
};

// style.md §12: an analogy's last paragraph starts with these words, in bold (`analogy-limit`).
export const c_AnalogyLimit = 'Where it breaks:';

/** The paragraph an analogy ends with when it starts with "**Where it breaks:**", or null. */
export function analogyLimit(children) {
	const last = children.at(-1);
	if (last?.type !== 'paragraph') return null;
	const first = last.children?.[0];
	if (first?.type !== 'strong') return null;
	const words = (first.children ?? []).map((child) => child.value ?? '').join('').trim();
	return words === c_AnalogyLimit ? last : null;
}

/** The aside a directive node becomes, or null when it is not one of the book's asides. */
export function bookAside(node, file) {
	if (node.type !== 'containerDirective' || !Object.hasOwn(c_BookAsides, node.name)) return null;
	const label = takeDirectiveLabel(node);
	const title = label?.text ?? c_BookAsides[node.name];
	if (node.children.length === 0) report(file, node, `the :::${node.name} aside is empty`);
	if (node.name === 'analogy') {
		const limit = analogyLimit(node.children);
		if (limit) {
			limit.data ??= {};
			limit.data.hProperties = { ...(limit.data.hProperties ?? {}), className: ['book-aside__limit'] };
		} else {
			report(file, node, `an analogy ends with the paragraph that says where it breaks: its last paragraph starts with "**${c_AnalogyLimit}**" (style.md §12)`);
		}
	}
	// The title is hidden from screen readers (the aside's label says it), so it holds no link: a focusable element
	// inside aria-hidden is an accessibility error. No :term mark stands in it.
	return element('aside', { className: ['starlight-aside', 'book-aside', `book-aside--${node.name}`], ariaLabel: title }, [
		withoutTerms(element('p', { className: ['starlight-aside__title'], ariaHidden: 'true' }, label?.nodes ?? [text(title)])),
		element('div', { className: ['starlight-aside__content'] }, node.children),
	]);
}

export function remarkBookAsides() {
	return function attacher() {
		return function transformer(tree, file) {
			const visit = (parent) => {
				(parent.children ?? []).forEach((node, index) => {
					visit(node);
					const aside = bookAside(node, file);
					if (aside) parent.children[index] = aside;
				});
			};
			visit(tree);
		};
	};
}
