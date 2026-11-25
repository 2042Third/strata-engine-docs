// mermaid: a "mermaid" fence becomes a figure holding the diagram's two committed drawings, for the light and the
// dark theme (the page's theme shows one; src/styles/book.css), from src/generated/diagrams/ (src/lib/diagrams.mjs).
// caption="…" says what to notice and becomes the <figcaption>; alt="…" says what it shows and becomes each drawing's
// accessible name (role="img", aria-label and <title>); both are required. A fence whose drawings are not committed
// fails the build ("npm run diagrams" draws them); the dev server draws them itself, into the same folder, so that
// the writer sees the diagram. The fence never reaches Expressive Code: this runs before it, in the Markdown stage.

import { c_ThemeNames, drawDiagrams, inlineDrawing, readDrawings, sourceProblems, writeDrawings } from '../lib/diagrams.mjs';
import { displayPath, element, pageOf, parseMeta, rawHtml, report, text } from './shared.mjs';

/** The drawings of one fence: from the committed files, or (the dev server) drawn now; `{ drawings }` or `{ error }`. */
async function drawingsOf(context, node, where) {
	let drawings = await readDrawings(context.settings.diagramsDir, node.value);
	if (drawings.missing && context.settings.command === 'dev') {
		const { drawn, failures } = await drawDiagrams([{ source: node.value, where: [where] }]);
		if (failures.length) return { error: failures.join('\n') };
		await writeDrawings(context.settings.diagramsDir, drawn);
		drawings = await readDrawings(context.settings.diagramsDir, node.value);
	}
	if (drawings.missing) return { error: `the diagram has no committed drawing (${drawings.missing.map((theme) => `src/generated/diagrams/${drawings.hash}-${theme}.svg`).join(' and ')} ${drawings.missing.length === 1 ? 'is' : 'are'} missing): run npm run diagrams and commit what it writes` };
	if (drawings.error) return { error: drawings.error };
	return { drawings };
}

export function remarkBookMermaid(context) {
	return function attacher() {
		return async function transformer(tree, file) {
			const index = await context.index();
			const page = pageOf(file, index);
			if (!page) return;
			const jobs = [];
			const find = (parent) => {
				(parent.children ?? []).forEach((node, position) => {
					if (node.type === 'code' && node.lang === 'mermaid') jobs.push({ parent, position, node });
					else find(node);
				});
			};
			find(tree);
			// The same diagram twice on a page gets its ids renamed the second time, so that the page holds no id twice.
			const occurrences = new Map();
			for (const { parent, position, node } of jobs) {
				const { attributes, rest } = parseMeta(node.meta, ['caption', 'alt']);
				if (rest.length) report(file, node, `a diagram takes only caption="…" and alt="…" (found ${rest.join(' ')})`);
				const caption = attributes.get('caption');
				const alt = attributes.get('alt');
				if (!caption) report(file, node, 'a diagram needs caption="…" (what to notice)');
				if (!alt) report(file, node, 'a diagram needs alt="…" (what it shows, for readers who cannot see it)');
				const problems = sourceProblems(node.value);
				for (const problem of problems) report(file, node, problem);
				if (!caption || !alt || problems.length) continue;
				const { drawings, error } = await drawingsOf(context, node, `${displayPath(file, context.settings.root)}:${node.position?.start.line ?? 0}`);
				if (error) {
					report(file, node, error);
					continue;
				}
				const occurrence = (occurrences.get(drawings.hash) ?? 0) + 1;
				occurrences.set(drawings.hash, occurrence);
				// Search reads the diagram's words once: the drawings of the other themes repeat them (site.md, "Search").
				parent.children[position] = element('figure', { className: ['book-diagram'] }, [
					...c_ThemeNames.map((theme, index) => element('div', { className: ['book-diagram__svg', `book-diagram__svg--${theme}`], ...(index > 0 ? { dataPagefindIgnore: '' } : {}) }, [rawHtml(inlineDrawing(drawings[theme], { hash: drawings.hash, theme, alt, occurrence }))])),
					element('figcaption', {}, [text(caption)]),
				]);
			}
		};
	};
}
