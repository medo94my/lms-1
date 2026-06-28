import frappeUIPreset from 'frappe-ui/tailwind'

export default {
	presets: [frappeUIPreset],
	content: [
		'./index.html',
		'./src/**/*.{vue,js,ts,jsx,tsx}',
		'./node_modules/frappe-ui/src/**/*.{vue,js,ts,jsx,tsx}',
		'../node_modules/frappe-ui/src/**/*.{vue,js,ts,jsx,tsx}',
		'./node_modules/frappe-ui/frappe/**/*.{vue,js,ts,jsx,tsx}',
		'../node_modules/frappe-ui/frappe/**/*.{vue,js,ts,jsx,tsx}',
	],
	theme: {
		extend: {
			// Basiret brand palette (COLORS_TOKENS.md) — exposes bg-primary-700,
			// text-gold-500, bg-cream-100 etc. for OUR custom markup. These are new
			// keys (the frappe-ui preset defines none of primary/gold/cream), so they
			// merge cleanly over the preset and do not affect frappe-ui's own
			// components (which use surface-*/ink-* tokens).
			colors: {
				primary: {
					50: '#EAF5EF',
					100: '#D5EADF',
					200: '#ABD5BF',
					300: '#80BF9E',
					400: '#56AA7E',
					500: '#0E8F58',
					600: '#0A7448',
					700: '#075536',
					800: '#063F2B',
					900: '#03291C',
				},
				gold: {
					50: '#FBF7E8',
					100: '#F5EECF',
					200: '#EADDA0',
					300: '#DECB70',
					400: '#D4B64A',
					500: '#C6A63A',
					600: '#B89A2E',
					700: '#9A7D1D',
					800: '#7A6417',
					900: '#4F3F0D',
				},
				cream: {
					50: '#FFFDF8',
					100: '#FBF8F0',
					200: '#F5EFE2',
					300: '#EDE3D1',
					400: '#E2D3BB',
				},
			},
			strokeWidth: {
				1.5: '1.5',
			},
			screens: {
				'2xl': '1600px',
				'3xl': '1920px',
			},
		},
	},
	plugins: [],
}
