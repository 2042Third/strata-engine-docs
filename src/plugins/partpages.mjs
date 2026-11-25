// partpages: a part's index and review pages (`generated: index` or `generated: review`, plan/style.md §7.7) get their
// generated part here, built by src/lib/partpages.mjs from the outline's data and the written pages: on the index page
// after the part editor's paragraph, on the review page before the part editor's exercises. It runs before the other
// plugins, so the generated text is drawn like written text (links checked, the Needs graph drawn as a diagram,
// answers hidden). Questions copied from a page keep that page for their pictures, and a problem in them is reported
// with the page and line they come from.

import { partPageContent } from '../lib/partpages.mjs';
import { markOrigin, pageOf } from './shared.mjs';

export function remarkBookPartPages(context) {
	return function attacher() {
		return async function transformer(tree, file) {
			const index = await context.index();
			const page = pageOf(file, index);
			if (!page || page.error || page.data?.generated === undefined) return;
			const questions = new Map();
			for (const [id, other] of index.pages) if (other.checkYourself?.length) questions.set(id, other.checkYourself);
			const content = partPageContent(page, context.outline, index.pages, questions);
			if (!content) return;
			const at = { line: 1, column: 1 };
			for (const node of content.nodes) {
				const from = node.data?.bookPageId;
				markOrigin([node], from ? `src/content/docs/${from}.md` : 'the part page\'s generated part (src/lib/partpages.mjs)', at);
			}
			if (content.after) tree.children.push(...content.nodes);
			else tree.children.unshift(...content.nodes);
		};
	};
}
