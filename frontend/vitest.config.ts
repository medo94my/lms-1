import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const root = path.dirname(fileURLToPath(import.meta.url))

export default defineConfig({
	plugins: [vue()],
	test: {
		environment: 'jsdom',
		globals: true,
		include: ['src/tests/**/*.test.{ts,js}'],
	},
	resolve: {
		alias: [
			{ find: '@', replacement: path.resolve(root, 'src') },
			// frappe-ui's internal ESM imports break under Node's strict ESM
			// resolution in Vitest. Tests that call vi.mock('frappe-ui', factory)
			// override this; tests that don't get this minimal stub instead.
			// Regex exact-match prevents catching sub-path imports like
			// 'frappe-ui/frappe' (string aliases match by prefix).
			{
				find: /^frappe-ui$/,
				replacement: path.resolve(root, 'src/__mocks__/frappe-ui.ts'),
			},
		],
	},
})
