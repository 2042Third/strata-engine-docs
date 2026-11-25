// Takes the picture of a web page for a tool figure (plan/pipelines.md §5.5, "Tool pictures"): the site's pinned
// Playwright, headless Chromium, the light color scheme, one device pixel per CSS pixel, the visible part of the page.
// tools/figures.py take --kinds tool runs it twice per figure and compares the two pictures.
//
//     node scripts/screenshot-page.mjs <url> <png> [--size <width>x<height>]
//
// The page is loaded until the network is idle, and the picture is taken once the fonts are ready. --size is the
// viewport, 1920x1080 by default (each side 16 to 4096, as the figures' sizes). Exit codes: 0 the PNG was written; 1 the
// page did not load (an HTTP status of 400 or more, or no answer within 60 s) or the picture could not be written;
// 2 usage.

import { rename, rm } from 'node:fs/promises';
import { chromium } from 'playwright';

const c_Timeout = 60000;

class UsageError extends Error {}

function parse(argv) {
	const files = [];
	let size = '1920x1080';
	for (let index = 0; index < argv.length; index++) {
		if (argv[index] === '--size') {
			if (index + 1 >= argv.length) throw new UsageError('--size needs <width>x<height>');
			size = argv[++index];
		} else if (argv[index].startsWith('--')) {
			throw new UsageError(`unknown option ${argv[index]}`);
		} else {
			files.push(argv[index]);
		}
	}
	if (files.length !== 2) throw new UsageError('give the page\'s URL and the PNG to write');
	const [url, output] = files;
	if (!/^(https?|file):\/\/\S+$/.test(url)) throw new UsageError(`${url} is not an http, https or file URL`);
	if (!output.toLowerCase().endsWith('.png')) throw new UsageError(`${output}: the picture is written as PNG`);
	const match = /^(\d+)x(\d+)$/.exec(size);
	const [width, height] = match ? [Number(match[1]), Number(match[2])] : [0, 0];
	if (!match || width < 16 || height < 16 || width > 4096 || height > 4096) throw new UsageError(`--size ${size}: <width>x<height>, each 16 to 4096`);
	return { url, output, width, height };
}

async function screenshot({ url, output, width, height }) {
	const browser = await chromium.launch();
	try {
		const context = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: 1, colorScheme: 'light', reducedMotion: 'reduce' });
		const page = await context.newPage();
		const response = await page.goto(url, { waitUntil: 'networkidle', timeout: c_Timeout });
		if (response && response.status() >= 400) throw new Error(`${url} answered ${response.status()}`);
		await page.evaluate(() => document.fonts.ready);
		const partial = `${output}.partial.png`;
		try {
			await page.screenshot({ path: partial, type: 'png', fullPage: false, animations: 'disabled', caret: 'hide' });
			await rename(partial, output);
		} catch (error) {
			await rm(partial, { force: true });
			throw error;
		}
	} finally {
		await browser.close();
	}
}

try {
	const options = parse(process.argv.slice(2));
	await screenshot(options);
	console.log(options.output);
} catch (error) {
	console.error(`screenshot-page: ${error.message}`);
	process.exitCode = error instanceof UsageError ? 2 : 1;
}
