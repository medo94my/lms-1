export interface TabLike {
	key?: string
	label?: string
}

/** Resolve a route hash (e.g. '#editor', or a legacy '#course editor') to a tab
 *  index. Match by stable key first, then fall back to the lowercased label so
 *  bookmarked label-based hashes keep working. Returns 0 when unmatched. */
export function resolveTabIndex(tabs: TabLike[], hash: string): number {
	const target = (hash || '').replace(/^#/, '').toLowerCase()
	if (!target) return 0
	const byKey = tabs.findIndex((t) => t.key === target)
	if (byKey !== -1) return byKey
	const byLabel = tabs.findIndex(
		(t) => (t.label || '').toLowerCase() === target
	)
	return byLabel === -1 ? 0 : byLabel
}
