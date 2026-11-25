// Crops at whole factors (plan/site.md "Pictures", gate (b) and confirm item 12): every crop of the built site, in
// Chromium at viewports 375, 768 and 1280 pixels wide, is shown at a whole multiple of its own width, never smoothed,
// and at the largest whole factor up to its recipe's scale that its column holds (its own width when the column is
// narrower, where it scrolls). The rendered width is the image's box in CSS pixels; its own width is the picture's.
//
//     node scripts/crops.mjs [--url http://host/strata-engine-docs/] [--root <book folder>] [--pages a/,b/]
//
// It serves the build with tools/crawl.py (name Python in PYTHON where `python` is not on the PATH) unless --url names
// a server that runs.

import { readdirSync, readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const c_Root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const c_Viewports = [375, 768, 1280];
// A rendered width within this many CSS pixels of a whole multiple is that multiple (layout rounds to 1/64 pixel).
const c_Epsilon = 0.02;

/** The factor a crop should show at: the largest whole one up to `scale` that `column` holds, and at least 1. */
export function expectedFactor({ natural, scale, column }) {
	return Math.min(scale, Math.max(1, Math.floor((column + c_Epsilon) / natural)));
}

/** What is wrong with one measured crop, or null: `{ rendered, natural, scale, column, rendering }`. */
export function cropProblem({ rendered, natural, scale, column, rendering }) {
	if (!(natural > 0)) return 'the picture has no width of its own (it did not load)';
	const factor = rendered / natural;
	if (Math.abs(factor - Math.round(factor)) > c_Epsilon / natural) return `it is shown ${rendered} px wide, ${factor.toFixed(3)} times its own ${natural} px: not a whole factor`;
	const expected = expectedFactor({ natural, scale, column });
	if (Math.round(factor) !== expected) return `it is shown at ${Math.round(factor)} times its own width; its column of ${column} px holds ${expected} (its scale is ${scale})`;
	if (rendering !== 'pixelated') return `its pixels are smoothed (image-rendering: ${rendering}), not shown as they are`;
	return null;
}

/** The pages of a built site that show a crop: their paths below the base ("make/first-script/"). */
export function cropPages(distDir, relative = '') {
	const pages = [];
	let entries;
	try {
		entries = readdirSync(path.join(distDir, relative), { withFileTypes: true });
	} catch (error) {
		if (error.code === 'ENOENT') return [];
		throw error;
	}
	for (const entry of entries.sort((a, b) => a.name.localeCompare(b.name))) {
		const child = relative ? `${relative}/${entry.name}` : entry.name;
		if (entry.isDirectory()) {
			if (!['_astro', '_figures', 'pagefind'].includes(child)) pages.push(...cropPages(distDir, child));
		} else if (entry.name === 'index.html' && readFileSync(path.join(distDir, child), 'utf8').includes('book-crop__img')) {
			pages.push(relative ? `${relative}/` : '');
		}
	}
	return pages;
}

/** In the page: every crop, measured once its picture has loaded. */
export async function measureCrops() {
	const images = [...document.querySelectorAll('img.book-crop__img')];
	// A crop further down the page loads only when it is near: it is asked for at once, and waited for.
	const loaded = (image) => new Promise((resolve) => {
		image.addEventListener('load', resolve, { once: true });
		image.addEventListener('error', resolve, { once: true });
		image.loading = 'eager';
	});
	await Promise.all(images.map((image) => (image.complete ? null : loaded(image))));
	return images.map((image) => {
		const figure = image.closest('.book-figure--crop');
		const style = getComputedStyle(figure);
		const column = figure.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight);
		const scale = Number(getComputedStyle(image.closest('.book-crop')).getPropertyValue('--book-crop-scale'));
		return { src: image.getAttribute('src'), rendered: image.getBoundingClientRect().width, natural: image.naturalWidth, scale, column, rendering: getComputedStyle(image).imageRendering };
	});
}

async function main(argv) {
	const { chromium } = await import('playwright');
	const { serveSite } = await import('./serve.mjs');
	const rootIndex = argv.indexOf('--root');
	const root = rootIndex >= 0 ? path.resolve(argv[rootIndex + 1]) : c_Root;
	const pagesIndex = argv.indexOf('--pages');
	const pages = pagesIndex >= 0 ? argv[pagesIndex + 1].split(',') : cropPages(path.join(root, 'dist'));
	if (pages.length === 0) {
		console.log('crops: no page of the build shows a crop');
		return 1;
	}
	const site = await serveSite({ argv });
	const browser = await chromium.launch();
	const problems = [];
	let measured = 0;
	try {
		for (const width of c_Viewports) {
			const page = await browser.newPage({ viewport: { width, height: 900 }, deviceScaleFactor: 1 });
			for (const relative of pages) {
				const response = await page.goto(site.url + relative, { waitUntil: 'networkidle' });
				if (response?.status() !== 200) {
					problems.push(`${relative} [${width} px]: answered ${response?.status()}`);
					continue;
				}
				for (const crop of await page.evaluate(measureCrops)) {
					measured++;
					const problem = cropProblem(crop);
					const factor = (crop.rendered / crop.natural).toFixed(2);
					if (problem) problems.push(`${relative} [${width} px] ${crop.src}: ${problem}`);
					else console.log(`${relative} [${width} px] ${path.posix.basename(crop.src)}: ${factor} times its ${crop.natural} px in a column of ${Math.round(crop.column)} px`);
				}
			}
			await page.close();
		}
	} finally {
		await browser.close();
		await site.stop();
	}
	for (const problem of problems) console.log(problem);
	console.log(`crops: ${measured} crops measured at ${c_Viewports.join(', ')} px; ${problems.length} problem${problems.length === 1 ? '' : 's'}`);
	return problems.length ? 1 : 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) process.exitCode = await main(process.argv.slice(2));
