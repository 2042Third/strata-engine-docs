// Token spans that only repeat the code's own colors are left out of the code blocks (src/lib/ec-compact.mjs).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { toHtml } from 'hast-util-to-html';
import { isPlainToken, pluginPlainTokens, unwrapPlainTokens } from '../../lib/ec-compact.mjs';

const span = (style, ...children) => ({ type: 'element', tagName: 'span', properties: style === null ? {} : { style }, children });
const text = (value) => ({ type: 'text', value });
const div = (className, ...children) => ({ type: 'element', tagName: 'div', properties: { className: [className] }, children });
const c_Foregrounds = ['#d6deeb', '#403f53'];

test('a plain token is one whose colors are the code foreground of every theme, and nothing else', () => {
	assert.equal(isPlainToken('--0:#D6DEEB;--1:#403F53', c_Foregrounds), true);
	assert.equal(isPlainToken('--0:#d6deeb;--1:#403f53', c_Foregrounds), true);
	assert.equal(isPlainToken('--0:#D6DEEB', c_Foregrounds), false);
	assert.equal(isPlainToken('--0:#D6DEEB;--1:#403F53;--0fs:italic', c_Foregrounds), false);
	assert.equal(isPlainToken('--0:#C792EA;--1:#8844AE', c_Foregrounds), false);
	assert.equal(isPlainToken('color:red', c_Foregrounds), false);
});

test('plain tokens leave their text in place, unless another colored span holds them', () => {
	const code = div('code',
		span('--0:#C792EA;--1:#8844AE', text('float')),
		span('--0:#D6DEEB;--1:#403F53', text(' ')),
		{ type: 'element', tagName: 'span', properties: { className: ['indent'] }, children: [span('--0:#d6deeb;--1:#403f53', text('  '))] },
		span('--1:#403F53', span('--0:#D6DEEB;--1:#403F53', text('kept')), span('--0:#D7DBE0', text('x'))),
		{ type: 'element', tagName: 'mark', properties: {}, children: [span('--0:#D6DEEB;--1:#403F53', text('marked'))] });
	assert.equal(unwrapPlainTokens(code, c_Foregrounds), 3);
	assert.equal(toHtml(code), '<div class="code"><span style="--0:#C792EA;--1:#8844AE">float</span> <span class="indent">  </span>'
		+ '<span style="--1:#403F53"><span style="--0:#D6DEEB;--1:#403F53">kept</span><span style="--0:#D7DBE0">x</span></span><mark>marked</mark></div>');
});

test('the plugin works on the lines of a rendered block with the themes\' own foregrounds', () => {
	const line = div('code', span('--0:#AAAAAA;--1:#BBBBBB', text('a')), span('--0:#CCCCCC;--1:#DDDDDD', text('b')));
	const gutter = div('gutter', span('--0:#AAAAAA;--1:#BBBBBB', text('1')));
	const blockAst = div('expressive-code', div('ec-line', gutter, line));
	const styleVariants = ['#aaaaaa', '#bbbbbb'].map((color) => ({ resolvedStyleSettings: new Map([['codeForeground', color]]) }));
	pluginPlainTokens().hooks.postprocessRenderedBlock({ renderData: { blockAst }, styleVariants });
	assert.equal(toHtml(line), '<div class="code">a<span style="--0:#CCCCCC;--1:#DDDDDD">b</span></div>');
	assert.equal(toHtml(gutter), '<div class="gutter"><span style="--0:#AAAAAA;--1:#BBBBBB">1</span></div>');
});
