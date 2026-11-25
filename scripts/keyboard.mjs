// Check 9, the keyboard (plan/site.md, "Checks"), in Chromium on the built site:
// - tabs follow the ARIA tabs pattern: the arrow keys move between tabs, Home and End go to the first and the last,
//   and Tab leaves the list;
// - the slider is an <input type="range"> with a label, moved by the arrow keys;
// - an answer opens with Enter and with Space;
// - a glossary term's popover opens from its button, closes with Escape, and focus returns to the button;
// - the track chooser's buttons are reached with Tab, and after a choice made with the keyboard "next" follows the track
//   (a chooser page whose pagination holds no "next" of the chosen track fails).
//
//     node scripts/keyboard.mjs [--url http://host/strata-engine-docs/] [--dist <built site>] [--root <book folder>]
//
// Each check runs on the first page of the build (--dist, default <root>/dist) that holds its component; a component
// no page holds is a failure, so that a check never passes by finding nothing. It serves the build with tools/crawl.py
// (name Python in PYTHON where `python` is not on the PATH) unless --url names a server that runs.

import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { sitePages } from './runtime.mjs';

const c_Root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
// How many presses of Tab may pass before the chooser's buttons are reached from the top of the page.
const c_MaxTabs = 400;
export const c_Checks = {
	tabs: '<book-tabs',
	slider: '<book-compare',
	answer: 'book-answer',
	popover: 'class="book-term__button"',
	chooser: '<book-track-chooser',
};

/** The first page (not a print view) that holds each component: `{ tabs: "make/first-script/", … }` (null if none). */
export function keyboardPages(distDir) {
	const pages = sitePages(distDir).filter((page) => !page.route.startsWith('print/'));
	return Object.fromEntries(Object.entries(c_Checks).map(([name, marker]) => [name, pages.find((page) => page.html.includes(marker))?.route ?? null]));
}

async function focused(page) {
	return page.evaluate(() => {
		const element = document.activeElement;
		return { id: element?.id ?? '', role: element?.getAttribute('role') ?? '', inTablist: Boolean(element?.closest('[role="tablist"]')), text: element?.textContent?.trim().slice(0, 40) ?? '' };
	});
}

/** The tabs of the first tab set: Arrow keys, Home and End move the selection and the focus; Tab leaves the list. */
export async function checkTabs(page) {
	const problems = [];
	const set = await page.$('book-tabs');
	const tabs = set ? await set.$$(':scope > [role="tablist"] > [role="tab"]') : [];
	if (tabs.length < 2) return ['no tab list of two or more tabs: the tabs\' script did not run'];
	const selected = async () => set.evaluate((element) => [...element.querySelector(':scope > [role="tablist"]').children].findIndex((tab) => tab.getAttribute('aria-selected') === 'true'));
	const ids = await Promise.all(tabs.map((tab) => tab.evaluate((element) => element.id)));
	await tabs[0].click();
	const steps = [['ArrowRight', 1], ['ArrowLeft', 0], ['End', tabs.length - 1], ['Home', 0], ['ArrowLeft', tabs.length - 1], ['ArrowRight', 0]];
	for (const [key, expected] of steps) {
		await page.keyboard.press(key);
		const index = await selected();
		const focus = await focused(page);
		if (index !== expected || focus.id !== ids[expected]) {
			problems.push(`tabs: ${key} selects tab ${index + 1} with the focus on "${focus.id || focus.text}", not tab ${expected + 1}`);
			return problems;
		}
	}
	await page.keyboard.press('Tab');
	if ((await focused(page)).inTablist) problems.push('tabs: Tab does not leave the tab list (only the selected tab is in the tab order)');
	return problems;
}

/** The slider: a range input with an accessible name, moved by the arrow keys. */
export async function checkSlider(page) {
	const range = await page.$('book-compare input[type="range"]');
	if (!range) return ['the slider: no <input type="range"> (the slider\'s script did not run)'];
	const problems = [];
	const name = await range.evaluate((input) => input.getAttribute('aria-label') || (input.labels && [...input.labels].map((label) => label.textContent).join(' ')) || input.getAttribute('aria-labelledby') || '');
	if (!name.trim()) problems.push('the slider has no label (aria-label or a <label>)');
	await range.focus();
	const value = async () => Number(await range.evaluate((input) => input.value));
	const before = await value();
	await page.keyboard.press('ArrowRight');
	const right = await value();
	await page.keyboard.press('ArrowLeft');
	await page.keyboard.press('ArrowLeft');
	const left = await value();
	if (!(right > before)) problems.push(`the slider: ArrowRight leaves it at ${right} (it was ${before})`);
	if (!(left < right)) problems.push(`the slider: ArrowLeft leaves it at ${left} (it was ${right})`);
	return problems;
}

/** An answer: a closed <details> whose summary opens it with Enter and with Space. */
export async function checkAnswer(page) {
	const summary = await page.$('details.book-answer:not([open]) > summary');
	if (!summary) return ['an answer: no closed <details class="book-answer"> with a <summary>'];
	const problems = [];
	const open = () => summary.evaluate((element) => element.parentElement.open);
	for (const key of ['Enter', 'Space']) {
		await summary.focus();
		await page.keyboard.press(key);
		if (!(await open())) problems.push(`an answer does not open with ${key}`);
		else {
			await page.keyboard.press(key);
			if (await open()) problems.push(`an answer does not close again with ${key}`);
		}
	}
	return problems;
}

/** A term's popover: Enter on its button opens it, Escape closes it, and the focus is back on the button. */
export async function checkPopover(page) {
	const button = await page.$('button.book-term__button');
	if (!button) return ['a term: no popover button'];
	const problems = [];
	const target = await button.evaluate((element) => element.getAttribute('popovertarget'));
	const shown = () => page.evaluate((id) => document.getElementById(id)?.matches(':popover-open') ?? false, target);
	await button.focus();
	await page.keyboard.press('Enter');
	if (!(await shown())) return [`a term: Enter on its button does not open the popover #${target}`];
	await page.keyboard.press('Escape');
	if (await shown()) problems.push(`a term: Escape does not close the popover #${target}`);
	const back = await button.evaluate((element) => document.activeElement === element);
	if (!back) problems.push(`a term: after Escape the focus is on "${(await focused(page)).text}", not on the term's button`);
	return problems;
}

/** The track chooser: Tab reaches every button; Enter chooses a track; "next" is then the track's. */
export async function checkChooser(page) {
	const problems = [];
	const tracks = await page.$$eval('.book-track__choose', (buttons) => buttons.map((button) => button.dataset.track));
	if (tracks.length === 0) return ['the track chooser: no buttons'];
	const reached = new Set();
	await page.evaluate(() => document.activeElement?.blur());
	await page.mouse.click(1, 1);
	for (let press = 0; press < c_MaxTabs && reached.size < tracks.length; press++) {
		await page.keyboard.press('Tab');
		const track = await page.evaluate(() => (document.activeElement?.classList.contains('book-track__choose') ? document.activeElement.dataset.track : null));
		if (track) reached.add(track);
	}
	for (const track of tracks) if (!reached.has(track)) problems.push(`the track chooser: Tab never reaches the button of the track ${track}`);
	if (problems.length) return problems;
	// The focus is on the last track's button: Enter chooses it.
	const chosen = tracks.at(-1);
	await page.keyboard.press('Enter');
	const pressed = await page.$eval(`.book-track__choose[data-track="${chosen}"]`, (button) => button.getAttribute('aria-pressed'));
	if (pressed !== 'true') problems.push(`the track chooser: Enter on the track ${chosen} leaves it unchosen (aria-pressed ${pressed})`);
	const links = await page.evaluate((name) => {
		const container = document.querySelector('.book-pagination');
		const template = container?.querySelector(`template[data-book-track="${name}"]`);
		const href = template?.content.querySelector('a[rel="next"]')?.getAttribute('href');
		return { shown: container?.querySelector('.pagination-links a[rel="next"]')?.href ?? null, expected: href ? new URL(href, document.baseURI).href : null, template: Boolean(template) };
	}, chosen);
	// The chooser stands on pages of start, which every track holds: a page without the track's "next" cannot show the
	// choice at work, so the check fails rather than pass by finding nothing.
	if (!links.template) problems.push(`the track chooser: its page holds no "next" of the track ${chosen} (no <template data-book-track="${chosen}"> in its pagination)`);
	else if (links.shown !== links.expected) problems.push(`the track chooser: after choosing ${chosen}, "next" leads to ${links.shown ?? 'nothing'}, not to the track's ${links.expected ?? 'end'}`);
	return problems;
}

const c_Runners = { tabs: checkTabs, slider: checkSlider, answer: checkAnswer, popover: checkPopover, chooser: checkChooser };

/** Every check on its page below `site`: `{ problems, pages }`. */
export async function runKeyboard({ site, pages }) {
	const { chromium } = await import('playwright');
	const browser = await chromium.launch();
	const problems = [];
	try {
		for (const [name, route] of Object.entries(pages)) {
			if (route === null) {
				problems.push(`${name}: no page of the build holds it, so it was not checked`);
				continue;
			}
			// A fresh context each time: the chooser's choice and the tabs' stored choice start empty.
			const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
			const page = await context.newPage();
			const response = await page.goto(site + route, { waitUntil: 'networkidle' });
			if (response?.status() !== 200) problems.push(`${name}: ${route} answered ${response?.status()}`);
			else problems.push(...(await c_Runners[name](page)).map((problem) => `${route || '(home)'}: ${problem}`));
			await context.close();
		}
	} finally {
		await browser.close();
	}
	return { problems, pages };
}

async function main(argv) {
	const option = (name, fallback = null) => {
		const index = argv.indexOf(name);
		return index >= 0 ? argv[index + 1] : fallback;
	};
	const root = path.resolve(option('--root', c_Root));
	const distDir = path.resolve(option('--dist', path.join(root, 'dist')));
	const pages = keyboardPages(distDir);
	const { serveSite } = await import('./serve.mjs');
	const site = await serveSite({ argv });
	let result;
	try {
		result = await runKeyboard({ site: site.url, pages });
	} finally {
		await site.stop();
	}
	for (const problem of result.problems) console.log(problem);
	console.log(`keyboard: ${Object.entries(pages).map(([name, route]) => `${name} on ${route ?? 'no page'}`).join(', ')}; ${result.problems.length} problem${result.problems.length === 1 ? '' : 's'}`);
	return result.problems.length ? 1 : 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) process.exitCode = await main(process.argv.slice(2));
