// math: every formula is checked with KaTeX while the page is still Markdown, so that a formula KaTeX cannot render
// is reported once, at its own line and column, together with the page's other problems (the report plugin runs
// after this one). rehype-katex renders the formulas later with the same options; it only warns about a bad formula
// and draws it in red, and the math step of src/plugins/rehype.mjs remains as the net behind this check.

import katex from 'katex';
import { report } from './shared.mjs';

/** KaTeX's options, shared with rehype-katex in src/plugins/index.mjs so that the check and the rendering agree. */
export const c_KatexOptions = { throwOnError: true, strict: 'error', output: 'htmlAndMathml', trust: false };

/** The message KaTeX gives for a formula, or null when it renders. */
export function formulaProblem(value, displayMode) {
	try {
		katex.renderToString(value, { ...c_KatexOptions, displayMode });
		return null;
	} catch (error) {
		return error instanceof katex.ParseError ? error.message : `KaTeX failed: ${error.message}`;
	}
}

export function remarkBookMathCheck() {
	return function attacher() {
		return function transformer(tree, file) {
			const visit = (node) => {
				if (node.type === 'math' || node.type === 'inlineMath') {
					const problem = formulaProblem(node.value, node.type === 'math');
					if (problem) report(file, node, `math: ${problem}`);
					return;
				}
				for (const child of node.children ?? []) visit(child);
			};
			visit(tree);
		};
	};
}
