// The book's directives (plan/site.md, "Directives", and the generated value of plan/pipelines.md §7.3): the complete
// list, with the form each is written in, whether it takes a label in brackets, and the attributes it takes.
// src/plugins/directives.mjs checks every directive of a page against this table before the other plugins draw them,
// and src/plugins/report.mjs fails the build on a directive the table does not know. Where a directive may stand (only
// on tutorials, only on pages of `reference`) is checked by the plugin that draws it, which knows the page.

/**
 * name → { forms, label, attributes, plugin }:
 * - `forms`: 'container' (":::name" … ":::"), 'leaf' ("::name{…}" on a line of its own) or 'text' (":name[…]{…}" in a
 *   sentence); the first is the one the book writes;
 * - `label`: 'none', 'optional' or 'required' (the text in brackets);
 * - `attributes`: the names it takes in braces, or null when its own plugin checks them (figures, compare);
 * - `starlight`: Starlight's own asides, which Starlight draws after the book's plugins.
 */
export const c_Directives = {
	note: { forms: ['container'], label: 'optional', attributes: ['icon'], starlight: true },
	tip: { forms: ['container'], label: 'optional', attributes: ['icon'], starlight: true },
	caution: { forms: ['container'], label: 'optional', attributes: ['icon'], starlight: true },
	danger: { forms: ['container'], label: 'optional', attributes: ['icon'], starlight: true },
	why: { forms: ['container'], label: 'optional', attributes: [] },
	question: { forms: ['container'], label: 'optional', attributes: [] },
	history: { forms: ['container'], label: 'optional', attributes: [] },
	elsewhere: { forms: ['container'], label: 'optional', attributes: [] },
	rule: { forms: ['container'], label: 'optional', attributes: [] },
	simplified: { forms: ['container'], label: 'optional', attributes: [] },
	analogy: { forms: ['container'], label: 'optional', attributes: [] },
	example: { forms: ['container'], label: 'optional', attributes: [] },
	derivation: { forms: ['container'], label: 'none', attributes: [] },
	'test-out': { forms: ['container'], label: 'none', attributes: [] },
	answer: { forms: ['container'], label: 'optional', attributes: ['tests', 'solution'] },
	tabs: { forms: ['container'], label: 'none', attributes: ['sync'] },
	tab: { forms: ['container'], label: 'required', attributes: [] },
	steps: { forms: ['container'], label: 'none', attributes: [] },
	files: { forms: ['container'], label: 'optional', attributes: [] },
	// A container figure is the spike's form whose body adds to the caption (plan/spike-report-1.md §4).
	figure: { forms: ['leaf', 'container'], label: 'none', attributes: null },
	compare: { forms: ['leaf', 'container'], label: 'none', attributes: null },
	checkpoint: { forms: ['leaf'], label: 'none', attributes: ['stage'] },
	glossary: { forms: ['leaf'], label: 'none', attributes: [] },
	'track-chooser': { forms: ['leaf'], label: 'none', attributes: [] },
	include: { forms: ['leaf'], label: 'none', attributes: ['file'] },
	term: { forms: ['text'], label: 'optional', attributes: ['id'] },
	since: { forms: ['text'], label: 'required', attributes: [] },
	value: { forms: ['text'], label: 'none', attributes: ['key'] },
};

const c_NodeForms = { containerDirective: 'container', leafDirective: 'leaf', textDirective: 'text' };

/** The form of a directive node, or null for another node. */
export function formOf(node) {
	return c_NodeForms[node?.type] ?? null;
}

/** How a directive of this form is written: ":::why", "::figure", ":term". */
export function spelling(name, form) {
	return `${{ container: ':::', leaf: '::', text: ':' }[form]}${name}`;
}

/** The names the book knows, as the report lists them: ":::why", "::figure", ":term", … */
export function knownSpellings() {
	return Object.entries(c_Directives).map(([name, directive]) => spelling(name, directive.forms[0]));
}

/** How to write a directive in its form, for messages. */
export function howToWrite(name) {
	const form = c_Directives[name].forms[0];
	if (form === 'container') return `${spelling(name, form)} is a block: write ${spelling(name, form)} on a line of its own, then its content, then a line of ::: (four colons around a block that holds other blocks)`;
	if (form === 'leaf') return `${spelling(name, form)} stands on a line of its own: ${spelling(name, form)}{…}`;
	return `${spelling(name, form)} stands inside a sentence: ${spelling(name, form)}[text]${c_Directives[name].attributes.length ? '{…}' : ''}`;
}

/**
 * The label of a directive node: `{ text, nodes }`, or null without one. A container's label is its first paragraph
 * marked as the label; a leaf's and a text directive's are its children.
 */
export function labelOf(node) {
	if (node.type === 'containerDirective') {
		const first = node.children?.[0];
		return first?.type === 'paragraph' && first.data?.directiveLabel ? { text: plainText(first), nodes: first.children } : null;
	}
	return node.children?.length ? { text: node.children.map(plainText).join(''), nodes: node.children } : null;
}

function plainText(node) {
	if (node.type === 'text' || node.type === 'inlineCode') return node.value;
	return (node.children ?? []).map(plainText).join('');
}

/**
 * The problems of one directive node against the table: `[message]`. A text directive without a label and without
 * attributes is prose (`a:b`, `std::vector`) and has none; an unknown name is the report's to name.
 */
export function directiveProblems(node) {
	const form = formOf(node);
	if (!form) return [];
	const attributes = Object.keys(node.attributes ?? {});
	if (form === 'text' && !node.children?.length && attributes.length === 0) return [];
	const directive = Object.hasOwn(c_Directives, node.name) ? c_Directives[node.name] : null;
	if (!directive) return [];
	if (!directive.forms.includes(form)) return [`${spelling(node.name, form)}: ${howToWrite(node.name)}`];
	const problems = [];
	const written = spelling(node.name, form);
	const label = labelOf(node);
	if (directive.label === 'none' && label) problems.push(`${written}[${label.text}] takes no text in brackets`);
	if (directive.label === 'required' && !label?.text.trim()) problems.push(`${written} needs its text in brackets: ${written}[…]`);
	if (directive.attributes) {
		for (const name of attributes) {
			if (directive.attributes.includes(name)) continue;
			const takes = directive.attributes.length ? `it takes ${directive.attributes.join(', ')}` : 'it takes none';
			problems.push(`${written} has no attribute "${name}" (${takes})`);
		}
	}
	return problems;
}
