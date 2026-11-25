// The book's scripts: optional extras on pages that already show everything without them.
// - <book-tabs>: one panel at a time, with a keyboard-friendly tab list; sets with the same sync key follow each other.
// - <book-compare>: the two pictures stacked with a range input that reveals the second one.
// - <book-track-chooser> and the pagination: the reader's track, kept in the browser, decides "previous" and "next".
// - Printing opens every hidden answer and derivation, and closes them again afterwards (./print.js).

import { openForPrint } from './print.js';

const c_TrackKey = 'strata-book:track';
const c_TabsKeyPrefix = 'strata-book:tabs:';

function readStored(key) {
	try {
		return window.localStorage.getItem(key);
	} catch {
		return null; // Storage can be off (private windows, strict settings): the choice is then not kept.
	}
}

function writeStored(key, value) {
	try {
		if (value === null) window.localStorage.removeItem(key);
		else window.localStorage.setItem(key, value);
	} catch {
		// See readStored.
	}
}

let s_TabsCount = 0;

class BookTabs extends HTMLElement {
	connectedCallback() {
		if (this.dataset.enhanced) return;
		const panels = [...this.querySelectorAll(':scope > .book-tabs__panel')];
		if (panels.length < 2) return;
		this.dataset.enhanced = 'true';
		const set = ++s_TabsCount;
		const list = document.createElement('div');
		list.setAttribute('role', 'tablist');
		list.className = 'book-tabs__list';
		this.tabs = panels.map((panel, index) => {
			const tab = document.createElement('button');
			tab.type = 'button';
			tab.id = `book-tabs-${set}-tab-${index}`;
			tab.setAttribute('role', 'tab');
			tab.textContent = panel.dataset.label;
			panel.id = `book-tabs-${set}-panel-${index}`;
			panel.setAttribute('role', 'tabpanel');
			panel.setAttribute('aria-labelledby', tab.id);
			panel.tabIndex = 0;
			tab.setAttribute('aria-controls', panel.id);
			tab.addEventListener('click', () => this.select(index, true));
			tab.addEventListener('keydown', (event) => this.onKey(event, index));
			list.append(tab);
			return { tab, panel };
		});
		this.prepend(list);
		const stored = this.dataset.sync ? readStored(c_TabsKeyPrefix + this.dataset.sync) : null;
		const initial = Math.max(0, panels.findIndex((panel) => panel.dataset.label === stored));
		this.select(initial, false);
		if (this.dataset.sync) {
			document.addEventListener('book-tabs-sync', (event) => {
				if (event.detail.sync !== this.dataset.sync || event.detail.source === this) return;
				const match = this.tabs.findIndex(({ panel }) => panel.dataset.label === event.detail.label);
				if (match >= 0) this.select(match, false);
			});
		}
	}

	select(index, fromReader) {
		this.tabs.forEach(({ tab, panel }, position) => {
			const selected = position === index;
			tab.setAttribute('aria-selected', String(selected));
			tab.tabIndex = selected ? 0 : -1;
			panel.hidden = !selected;
		});
		if (fromReader && this.dataset.sync) {
			const label = this.tabs[index].panel.dataset.label;
			writeStored(c_TabsKeyPrefix + this.dataset.sync, label);
			document.dispatchEvent(new CustomEvent('book-tabs-sync', { detail: { sync: this.dataset.sync, label, source: this } }));
		}
	}

	onKey(event, index) {
		const last = this.tabs.length - 1;
		const target = { ArrowRight: index === last ? 0 : index + 1, ArrowLeft: index === 0 ? last : index - 1, Home: 0, End: last }[event.key];
		if (target === undefined) return;
		event.preventDefault();
		this.select(target, true);
		this.tabs[target].tab.focus();
	}
}

class BookCompare extends HTMLElement {
	connectedCallback() {
		if (this.dataset.enhanced) return;
		const items = this.querySelectorAll('.book-compare__item');
		if (items.length !== 2) return;
		this.dataset.enhanced = 'true';
		const [before, after] = [...items].map((item) => item.dataset.label);
		const range = document.createElement('input');
		range.type = 'range';
		range.min = '0';
		range.max = '100';
		range.value = '50';
		range.className = 'book-compare__range';
		range.setAttribute('aria-label', `Slide between ${before} (left) and ${after} (right)`);
		const update = () => this.style.setProperty('--book-compare-position', `${range.value}%`);
		range.addEventListener('input', update);
		update();
		this.append(range);
	}
}

function trackLabel(name) {
	const template = document.querySelector(`template[data-book-track="${CSS.escape(name)}"]`);
	return template?.dataset.bookTrackLabel ?? document.querySelector(`.book-track[data-track="${CSS.escape(name)}"] strong`)?.textContent ?? name;
}

function applyTrack() {
	const track = readStored(c_TrackKey);
	const container = document.querySelector('.book-pagination');
	if (!container) return;
	const links = container.querySelector('.pagination-links');
	const note = container.querySelector('.book-pagination__track');
	if (!container.dataset.defaultLinks && links) container.dataset.defaultLinks = links.innerHTML;
	const template = track ? container.querySelector(`template[data-book-track="${CSS.escape(track)}"]`) : null;
	if (links) links.innerHTML = template ? template.innerHTML : container.dataset.defaultLinks;
	if (note) {
		note.hidden = !template;
		const name = note.querySelector('.book-pagination__track-name');
		if (name) name.textContent = template ? template.dataset.bookTrackLabel : '';
	}
}

class BookTrackChooser extends HTMLElement {
	connectedCallback() {
		if (this.dataset.enhanced) return;
		this.dataset.enhanced = 'true';
		for (const button of this.querySelectorAll('.book-track__choose')) {
			button.hidden = false;
			button.addEventListener('click', () => {
				const chosen = readStored(c_TrackKey) === button.dataset.track ? null : button.dataset.track;
				writeStored(c_TrackKey, chosen);
				this.update();
				applyTrack();
			});
		}
		this.update();
	}

	update() {
		const track = readStored(c_TrackKey);
		for (const button of this.querySelectorAll('.book-track__choose')) {
			const chosen = button.dataset.track === track;
			button.setAttribute('aria-pressed', String(chosen));
			button.textContent = chosen ? 'Following this track (stop)' : 'Follow this track';
		}
		const current = this.querySelector('.book-track-chooser__current');
		if (current) current.textContent = track ? `You follow: ${trackLabel(track)}. "Previous" and "next" on every page follow it.` : 'You follow no track: "previous" and "next" follow the parts in order.';
	}
}

customElements.define('book-tabs', BookTabs);
customElements.define('book-compare', BookCompare);
customElements.define('book-track-chooser', BookTrackChooser);
applyTrack();
let s_ClosePrinted = null;
window.addEventListener('beforeprint', () => {
	s_ClosePrinted?.();
	s_ClosePrinted = openForPrint(document);
});
window.addEventListener('afterprint', () => {
	s_ClosePrinted?.();
	s_ClosePrinted = null;
});
