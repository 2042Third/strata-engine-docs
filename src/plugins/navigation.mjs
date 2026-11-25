// navigation: "::track-chooser" on a page of Start here (start/how-to-read) lets the reader choose a track: game maker
// (G), beginner (B) or engine builder (E). The choice is kept in the browser and makes "previous" and "next" follow the
// track (src/components/Pagination.astro). Without scripts the chooser still links the first page of each track.

import { c_ChooserPage, c_Tracks } from '../lib/labels.mjs';
import { pageUrl } from '../lib/settings.mjs';
import { trackStart } from '../lib/sidebar.mjs';
import { element, pageOf, report, text } from './shared.mjs';

export const c_ChooserPart = 'start';

/** The chooser's markup: one item per track with its label, description and first written page. */
export function chooser(context, index) {
	const items = [];
	for (const { letter, key } of c_Tracks) {
		const track = context.sidebar.tracks[key];
		const first = trackStart(context.sidebar, key, index.pages);
		const children = [element('strong', {}, [text(track.label)]), text(` (${letter}) ${track.description}`)];
		if (first) {
			const page = index.pages.get(first);
			children.push(text(' '));
			children.push(element('a', { href: pageUrl(context.settings.base, page.route), className: ['book-track__start'] }, [text(`Start with: ${page.title}`)]));
		}
		children.push(element('button', { type: 'button', className: ['book-track__choose'], dataTrack: key, hidden: true }, [text('Follow this track')]));
		items.push(element('li', { className: ['book-track'], dataTrack: key }, children));
	}
	return element('book-track-chooser', {}, [element('ul', {}, items), element('p', { className: ['book-track-chooser__current'], ariaLive: 'polite' }, [])]);
}

export function remarkBookNavigation(context) {
	return function attacher() {
		return async function transformer(tree, file) {
			const index = await context.index();
			const page = pageOf(file, index);
			if (!page) return;
			const visit = (parent) => {
				(parent.children ?? []).forEach((node, position) => {
					if (node.type !== 'leafDirective' || node.name !== 'track-chooser') {
						visit(node);
						return;
					}
					if (page.part !== c_ChooserPart) {
						report(file, node, `::track-chooser belongs on a page of the part "${c_ChooserPart}" (${c_ChooserPage}), where readers choose their track`);
						return;
					}
					parent.children[position] = chooser(context, index);
				});
			};
			visit(tree);
		};
	};
}
