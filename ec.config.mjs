// Expressive Code, which draws every code block. Quotes of the engine show the engine's own line numbers (the
// excerpts plugin sets startLineNumber); long ones can fold sections. Shiki has no grammar for Slang; Strata's
// shaders are written in Slang with HLSL syntax, so "slang" fences are highlighted as HLSL.

import { defineEcConfig } from '@astrojs/starlight/expressive-code';
import { pluginCollapsibleSections } from '@expressive-code/plugin-collapsible-sections';
import { pluginLineNumbers } from '@expressive-code/plugin-line-numbers';
import { pluginPlainTokens } from './src/lib/ec-compact.mjs';

export default defineEcConfig({
	// Token spans that only repeat the code's own colors are left out (src/lib/ec-compact.mjs).
	plugins: [pluginLineNumbers(), pluginCollapsibleSections(), pluginPlainTokens()],
	// Engine lines run to 120 characters; wrapping (with the line's indentation kept) beats scrolling sideways and
	// prints whole.
	defaultProps: { showLineNumbers: false, wrap: true, preserveIndent: true },
	shiki: { langAlias: { slang: 'hlsl' } },
	styleOverrides: {
		// The themes' line numbers are too faint for WCAG AA (3.3:1, axe in scripts/a11y.mjs). These reach 4.5:1 on the
		// lines a diff marks as well: the light one 5.4:1 on an inserted line's green (#b8daaf), where #56606b gave 4.17:1.
		lineNumbers: { foreground: ({ theme }) => (theme.type === 'dark' ? '#a3b1bf' : '#464f59') },
		codeFontFamily: "'JetBrains Mono Variable', ui-monospace, 'Cascadia Mono', Menlo, Consolas, monospace",
		uiFontFamily: "'Inter Variable', system-ui, sans-serif",
	},
});
