// report: the last of the book's Markdown plugins. It fails the build on any directive no plugin handled (a typo
// such as ":::pitfal" must not render as plain text) and then on every problem the other plugins recorded, listing
// them all with their lines, so that one build shows everything to fix.

import { c_Directives, knownSpellings } from '../lib/directives.mjs';
import { displayPath, report } from './shared.mjs';

/** Throws one error listing every recorded problem of the file, sorted by line. */
export function throwProblems(file, root) {
	const problems = file.data.bookProblems ?? [];
	if (problems.length === 0) return;
	problems.sort((a, b) => a.line - b.line || a.column - b.column);
	const where = displayPath(file, root);
	const lines = problems.map((problem) => `  ${where}:${problem.line}:${problem.column}: ${problem.message}${problem.origin ? ` (${problem.origin})` : ''}`);
	file.data.bookProblems = [];
	throw new Error(`The page ${where} has ${problems.length} problem${problems.length === 1 ? '' : 's'}:\n${lines.join('\n')}`);
}

export function remarkBookReport(context) {
	return function attacher() {
		return function transformer(tree, file) {
			const visit = (node) => {
				// A directive another plugin reported (an unknown figure or term id, a wrong form) is known; its problem is
				// listed already.
				if (node.data?.bookReported) {
					for (const child of node.children ?? []) visit(child);
					return;
				}
				const starlight = Object.hasOwn(c_Directives, node.name) && c_Directives[node.name].starlight;
				if ((node.type === 'containerDirective' || node.type === 'leafDirective') && !starlight) {
					const colons = node.type === 'containerDirective' ? ':::' : '::';
					report(file, node, `unknown directive ${colons}${node.name}: the book knows ${knownSpellings().join(', ')}`);
				} else if (node.type === 'textDirective' && (node.children?.length || Object.keys(node.attributes ?? {}).length)) {
					// Prose such as "a:b" parses as a bare text directive, which Starlight writes back as text; one with a label
					// or attributes was meant as a directive, and would otherwise show as literal text.
					report(file, node, `unknown inline directive :${node.name}[…]: the book knows :term[text]{id=…}, :since[release] and :value{key=…} (write code such as a::b in backticks)`);
				}
				for (const child of node.children ?? []) visit(child);
			};
			visit(tree);
			throwProblems(file, context.settings.root);
		};
	};
}
