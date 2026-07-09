import { describe, it, expect } from 'vitest'
import { resolveTabIndex } from '@/utils/courseTabs'

const tabs = [
	{ key: 'overview', label: 'Overview' },
	{ key: 'dashboard', label: 'Dashboard' },
	{ key: 'editor', label: 'Course editor' },
	{ key: 'settings', label: 'Settings' },
]

describe('resolveTabIndex', () => {
	it('matches by stable key', () => {
		expect(resolveTabIndex(tabs, '#editor')).toBe(2)
		expect(resolveTabIndex(tabs, '#settings')).toBe(3)
	})
	it('falls back to the lowercased label for legacy hashes', () => {
		expect(resolveTabIndex(tabs, '#course editor')).toBe(2)
		expect(resolveTabIndex(tabs, '#overview')).toBe(0)
	})
	it('returns 0 for an unknown or empty hash', () => {
		expect(resolveTabIndex(tabs, '')).toBe(0)
		expect(resolveTabIndex(tabs, '#nope')).toBe(0)
	})
})
