// directives: the first of the book's Markdown plugins after math. It checks every directive of the page against the
// book's table (src/lib/directives.mjs): its form (block, line or inline), its text in brackets and its attributes, so
// that a mistyped attribute or a directive written in the wrong form fails the build at its own line instead of being
// ignored. The plugins that draw the directives then check what only they know (an id of the figure manifest, a learn
// id, the page a directive may stand on); the report plugin fails on names the table does not know.

import { directiveProblems, formOf } from '../lib/directives.mjs';
import { pageOf, report } from './shared.mjs';

export function remarkBookDirectives(context) {
	return function attacher() {
		return async function transformer(tree, file) {
			const index = await context.index();
			if (!pageOf(file, index)) return;
			const visit = (node) => {
				// A directive a plugin before this one checked already (::include) is not checked twice.
				if (formOf(node) && !node.data?.bookChecked) for (const problem of directiveProblems(node)) report(file, node, problem);
				for (const child of node.children ?? []) visit(child);
			};
			visit(tree);
		};
	};
}
