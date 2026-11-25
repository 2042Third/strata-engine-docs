// test-out: "::::test-out" opens a primer (plan/style.md §7.1): five questions, each followed by its hidden answer,
// for a reader who may know the subject already. The plugin writes the box's title and its instruction: answer all
// five without opening the answers, and if all five are right, go on to the next page of your track, linked for every
// track that holds the page (written into the page, so that it works without scripts). What the box must hold (rule
// P3) is checked by the strips plugin.

import { c_Tracks } from '../lib/labels.mjs';
import { pageUrl } from '../lib/settings.mjs';
import { trackNeighbours } from '../lib/sidebar.mjs';
import { element, pageOf, report, text, withoutTerms } from './shared.mjs';

export const c_TestOutTitle = 'Test out';
export const c_TestOutInstruction = 'Answer all five questions without opening the answers. If all five answers are right, you know what this page teaches: skip it and go on to the next page of your track.';

/** The links to the next page of each track that holds the page or offers it as a side step. */
export function nextPages(context, index, pageId) {
	return trackNeighbours(context.sidebar, index.pages, pageId).map((track) => {
		const name = c_Tracks.find((candidate) => candidate.key === track.key).name;
		const children = [text(`${name} (${track.letter}): `)];
		if (track.next) {
			const next = index.pages.get(track.next);
			children.push(element('a', { href: pageUrl(context.settings.base, next.route) }, [text(next.title)]));
		} else {
			children.push(element('span', { className: ['book-top-strip__unwritten'] }, [text('no later page of this track is written yet')]));
		}
		return element('li', { dataBookTrack: track.key }, children);
	});
}

export function remarkBookTestOut(context) {
	return function attacher() {
		return async function transformer(tree, file) {
			const index = await context.index();
			const page = pageOf(file, index);
			if (!page) return;
			const visit = (parent) => {
				(parent.children ?? []).forEach((node, position) => {
					if (node.type !== 'containerDirective' || node.name !== 'test-out') {
						visit(node);
						return;
					}
					if (page.data.kind !== 'primer') {
						report(file, node, 'the Test out box stands only on primers (style.md §12): remove it');
						return;
					}
					visit(node);
					const next = nextPages(context, index, page.id);
					const intro = [
						withoutTerms(element('p', { className: ['book-test-out__title'] }, [text(c_TestOutTitle)])),
						withoutTerms(element('p', { className: ['book-test-out__instruction'] }, [text(c_TestOutInstruction)])),
					];
					if (next.length) intro.push(withoutTerms(element('ul', { className: ['book-test-out__next'] }, next)));
					parent.children[position] = element('section', { className: ['book-test-out'], ariaLabel: c_TestOutTitle }, [
						element('div', { className: ['book-test-out__intro'], dataPagefindIgnore: '' }, intro),
						...node.children,
					]);
				});
			};
			visit(tree);
		};
	};
}
