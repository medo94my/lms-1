# Matching + Ordering — Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the Matching (dropdown-per-left) and Ordering (drag-to-reorder + up/down a11y buttons) question types to the frontend registry, mirroring the merged Fill-blank patterns.

**Architecture:** Two new `QuestionTypeDef`s registered in `frontend/src/questionTypes/`, each with an Author component (writes `question.data`) and a Player component (reads `data` via `parseConfig`, presents options shuffled, writes a fixed-length answer via `v-model:state`). A shared `shuffle` helper is added to `util.ts`. The Ordering player uses `vuedraggable` plus up/down buttons.

**Tech Stack:** Vue 3 `<script setup>`, frappe-ui, `vuedraggable@4.1.0`, TypeScript, Vitest.

## Global Constraints

- **Existing types unchanged.** All current Vitest tests stay green.
- **Names match backend exactly:** registry `name` = `"Matching"` and `"Ordering"` (= backend plugin names = DocType Select options). `label` = same.
- **Answer-array alignment:** `getAnswers` returns one entry per element (`''`/empty for unanswered), length == elements, so `Quiz.vue`'s `.filter(a => a !== null && a !== undefined)` never shortens it and backend per-element indices align. Matching answer = chosen right per left, in left order. Ordering answer = learner's current ordered item list.
- **Config read via `parseConfig`** (handles `data` as object or JSON string). Author components initialize `question.data` defaults on mount via the `{ immediate: true, deep: true }` watch pattern (mirror `FillBlankAuthor.vue`).
- **Live-check reveal:** the per-element correctness array arrives as `showAnswers[0]` (the framework's non-Choices `checkAnswer` path).
- **Shuffle:** present Matching rights and Ordering items shuffled (Fisher–Yates); for Ordering, re-shuffle if the shuffle equals the correct order.
- i18n (`__()`), RTL logical spacing (`ms-`/`me-`/`ps-`/`pe-`).
- **Tests:** Vitest locally — `cd frontend && npx vitest run`. The registry transitively imports the new components, so the test file must mock `vuedraggable` (and already mocks `frappe-ui`). Drag/reorder behavior is verified manually in the preview. After editing `frontend/src`, run the **vue-frontend-reviewer** and **rtl-i18n-reviewer** agents before the final commit.

## Known limitation (carried over from Fill-blank; out of scope here)

The player fetch (`get_quiz_with_questions`) sends the full `data` field — including the answer key — to the client for all `data`-based types (Fill-blank, and now Matching/Ordering). Scoring is still server-side and trustworthy, but a determined learner could read the answers from the page. This is a pre-existing property of the shipped Fill-blank type; hardening it (a sanitized player-view of `data`) should be its own sub-project covering all data-based types. Flagged to the user at handoff.

---

## File Structure

- Modify: `frontend/src/questionTypes/util.ts` — add `shuffle`.
- Create: `frontend/src/questionTypes/matching.ts`, `ordering.ts` — defs + helpers.
- Create: `frontend/src/questionTypes/components/MatchingAuthor.vue`, `MatchingPlayer.vue`, `OrderingAuthor.vue`, `OrderingPlayer.vue`.
- Modify: `frontend/src/questionTypes/index.ts` — register both.
- Modify: `frontend/src/tests/questionTypes.test.ts` — tests + `vi.mock('vuedraggable', ...)`.

---

## Task 1: shuffle helper + Matching type

**Files:**
- Modify: `frontend/src/questionTypes/util.ts`
- Create: `frontend/src/questionTypes/matching.ts`, `components/MatchingAuthor.vue`, `components/MatchingPlayer.vue`
- Modify: `frontend/src/questionTypes/index.ts`
- Test: `frontend/src/tests/questionTypes.test.ts`

**Interfaces:**
- Produces: `shuffle<T>(arr: T[]): T[]` in util.ts; default-exported `QuestionTypeDef` `Matching`. `getAnswers(question, state)` → `pairs.map((_, i) => state?.selections?.[i] ?? '')`; `loadAnswer(_q, saved)` → `{ selections: saved ?? [] }`. Config `{ pairs: [{ left, right }] }`.

- [ ] **Step 1: Write the failing tests (append to questionTypes.test.ts)**

```ts
describe('Matching helpers', () => {
	const q = { data: { pairs: [{ left: 'A', right: '1' }, { left: 'B', right: '2' }] } }
	it('getAnswers returns one entry per left, empty for missing', () => {
		expect(getQuestionType('Matching').getAnswers(q, { selections: ['1'] })).toEqual(['1', ''])
	})
	it('loadAnswer restores selections', () => {
		expect(getQuestionType('Matching').loadAnswer(q, ['1', '2']).selections).toEqual(['1', '2'])
	})
})
```

- [ ] **Step 2: Run to confirm failure** — `cd frontend && npx vitest run src/tests/questionTypes.test.ts` → FAIL (`Matching` not registered).

- [ ] **Step 3: Add `shuffle` to util.ts**

Append to `frontend/src/questionTypes/util.ts`:

```ts
/** Fisher–Yates shuffle; returns a new array (does not mutate the input). */
export function shuffle<T>(arr: T[]): T[] {
	const out = [...arr]
	for (let i = out.length - 1; i > 0; i--) {
		const j = Math.floor(Math.random() * (i + 1))
		;[out[i], out[j]] = [out[j], out[i]]
	}
	return out
}
```

- [ ] **Step 4: Create MatchingAuthor.vue**

```vue
<template>
	<div class="space-y-4">
		<div class="text-base-semibold text-ink-gray-9">{{ __('Pairs') }}</div>
		<p class="text-xs text-ink-gray-6">
			{{ __('Each left item matches exactly one right item. Use distinct right values.') }}
		</p>
		<div
			v-for="(pair, i) in pairs"
			:key="i"
			class="border border-outline-elevation-2 rounded-md p-3 grid grid-cols-2 gap-3"
		>
			<FormControl
				:label="__('Left {0}', [i + 1])"
				:model-value="pair.left"
				@update:model-value="(v) => setField(i, 'left', v)"
			/>
			<div class="flex items-end gap-2">
				<FormControl
					class="flex-1"
					:label="__('Right {0}', [i + 1])"
					:model-value="pair.right"
					@update:model-value="(v) => setField(i, 'right', v)"
				/>
				<Button
					v-if="pairs.length > 2"
					variant="ghost"
					size="sm"
					:aria-label="__('Remove pair {0}', [i + 1])"
					@click="removePair(i)"
				>
					<span class="lucide-trash-2 size-4" />
				</Button>
			</div>
		</div>
		<Button @click="addPair">
			<template #prefix><span class="lucide-plus size-4" /></template>
			{{ __('Add Pair') }}
		</Button>
	</div>
</template>
<script setup>
import { computed, watch } from 'vue'
import { FormControl, Button } from 'frappe-ui'
import { parseConfig } from '@/questionTypes/util'

const question = defineModel('question')
const pairs = computed(() => parseConfig(question.value).pairs || [])

watch(
	question,
	(q) => {
		if (!q) return
		const c = parseConfig(q)
		if (!c.pairs) {
			question.value.data = { pairs: [{ left: '', right: '' }, { left: '', right: '' }] }
		} else if (typeof q.data === 'string') {
			question.value.data = c
		}
	},
	{ immediate: true, deep: true }
)

const write = (next) => {
	question.value.data = { pairs: next }
}
const setField = (i, key, value) => {
	const next = pairs.value.map((p) => ({ ...p }))
	next[i][key] = value
	write(next)
}
const addPair = () => {
	write([...pairs.value.map((p) => ({ ...p })), { left: '', right: '' }])
}
const removePair = (i) => {
	write(pairs.value.filter((_, idx) => idx !== i).map((p) => ({ ...p })))
}
</script>
```

- [ ] **Step 5: Create MatchingPlayer.vue**

```vue
<template>
	<div class="space-y-3 mt-2">
		<div v-for="(pair, i) in pairs" :key="i" class="flex items-center gap-3">
			<div class="flex-1 text-ink-gray-9" v-html="sanitizeRichHTML(pair.left)" />
			<FormControl
				class="flex-1"
				type="select"
				:options="selectOptions"
				:model-value="selections[i] || ''"
				:disabled="showAnswers.length > 0"
				@update:model-value="(v) => setSelection(i, v)"
			/>
			<span
				v-if="showAnswers.length && perPair[i] === 1"
				class="lucide-check-circle w-4 h-4 text-ink-green-5"
			/>
			<span
				v-else-if="showAnswers.length && perPair[i] === 0"
				class="lucide-x-circle w-4 h-4 text-ink-red-6"
			/>
		</div>
		<div v-if="showAnswers.length" class="text-xs text-ink-gray-6 space-y-1">
			<div v-for="(pair, i) in pairs" :key="i" v-show="perPair[i] === 0">
				{{ __('{0} → {1}', [stripTags(pair.left), pair.right]) }}
			</div>
		</div>
	</div>
</template>
<script setup>
import { computed, ref, onMounted } from 'vue'
import { FormControl } from 'frappe-ui'
import { parseConfig, shuffle } from '@/questionTypes/util'
import { sanitizeRichHTML } from '@/utils/sanitizeRichHTML'

const props = defineProps({
	question: { type: Object, required: true },
	showAnswers: { type: Array, default: () => [] },
	quizShowAnswers: { type: Boolean, default: false },
})
const state = defineModel('state')
const pairs = computed(() => parseConfig(props.question).pairs || [])
const selections = computed(() => state.value?.selections || [])
const perPair = computed(() => (props.showAnswers.length ? props.showAnswers[0] || [] : []))

// Shuffle the right-hand options ONCE on mount (presentation only).
const shuffledRights = ref([])
onMounted(() => {
	shuffledRights.value = shuffle(pairs.value.map((p) => p.right))
})
const selectOptions = computed(() => [
	{ label: __('Select…'), value: '' },
	...shuffledRights.value.map((r) => ({ label: r, value: r })),
])

const stripTags = (html) => String(html || '').replace(/<[^>]*>/g, '')

const setSelection = (i, v) => {
	const next = pairs.value.map((_, idx) => selections.value[idx] ?? '')
	next[i] = v
	state.value = { selections: next }
}
</script>
```

- [ ] **Step 6: Create matching.ts + register**

Create `frontend/src/questionTypes/matching.ts`:

```ts
import type { QuestionTypeDef } from './types'
import { parseConfig } from './util'
import MatchingAuthor from './components/MatchingAuthor.vue'
import MatchingPlayer from './components/MatchingPlayer.vue'

const Matching: QuestionTypeDef = {
	name: 'Matching',
	label: 'Matching',
	autoGraded: true,
	hasLiveCheck: true,
	defaultConfig() {
		return { data: { pairs: [{ left: '', right: '' }, { left: '', right: '' }] } }
	},
	getAnswers(question, state) {
		const pairs = parseConfig(question).pairs || []
		const selections = state?.selections || []
		return pairs.map((_: any, i: number) => selections[i] ?? '')
	},
	loadAnswer(_question, savedAnswers) {
		return { selections: savedAnswers ?? [] }
	},
	AuthorComponent: MatchingAuthor,
	PlayerComponent: MatchingPlayer,
}

export default Matching
```

In `frontend/src/questionTypes/index.ts`, add `import matching from './matching'` and `register(matching)`.

- [ ] **Step 7: Run tests** — `cd frontend && npx vitest run src/tests/questionTypes.test.ts` → PASS. Then full `npx vitest run` to confirm no regressions.

(The new components import `FormControl`/`Button` — already in the `vi.mock('frappe-ui')` factory — and `sanitizeRichHTML` from `@/utils/sanitizeRichHTML`, a real local util that imports cleanly. No new mock needed for Matching.)

- [ ] **Step 8: Commit**

```bash
git add frontend/src/questionTypes/util.ts frontend/src/questionTypes/matching.ts frontend/src/questionTypes/components/MatchingAuthor.vue frontend/src/questionTypes/components/MatchingPlayer.vue frontend/src/questionTypes/index.ts frontend/src/tests/questionTypes.test.ts
git commit -m "feat(quiz-fe): add Matching question type"
```

---

## Task 2: Ordering type (vuedraggable + up/down)

**Files:**
- Create: `frontend/src/questionTypes/ordering.ts`, `components/OrderingAuthor.vue`, `components/OrderingPlayer.vue`
- Modify: `frontend/src/questionTypes/index.ts`
- Test: `frontend/src/tests/questionTypes.test.ts`

**Interfaces:**
- Produces: default-exported `QuestionTypeDef` `Ordering`. Config `{ items: [...] }` (correct order). `getAnswers(question, state)` → `items.map((_, i) => state?.order?.[i] ?? '')`; `loadAnswer(_q, saved)` → `{ order: saved ?? [] }`.

- [ ] **Step 1: Write the failing tests (append) + mock vuedraggable**

At the TOP of `frontend/src/tests/questionTypes.test.ts`, next to the existing `vi.mock('frappe-ui', …)`, add:

```ts
vi.mock('vuedraggable', () => ({ default: { template: '<div><slot /></div>' } }))
```

Append the helper tests:

```ts
describe('Ordering helpers', () => {
	const q = { data: { items: ['a', 'b', 'c'] } }
	it('getAnswers returns the current order, fixed length', () => {
		expect(getQuestionType('Ordering').getAnswers(q, { order: ['b', 'a'] })).toEqual(['b', 'a', ''])
	})
	it('loadAnswer restores order', () => {
		expect(getQuestionType('Ordering').loadAnswer(q, ['c', 'b', 'a']).order).toEqual(['c', 'b', 'a'])
	})
})
```

- [ ] **Step 2: Run to confirm failure** — FAIL (`Ordering` not registered).

- [ ] **Step 3: Create OrderingAuthor.vue**

```vue
<template>
	<div class="space-y-4">
		<div class="text-base-semibold text-ink-gray-9">{{ __('Items in correct order') }}</div>
		<p class="text-xs text-ink-gray-6">
			{{ __('Enter items in the correct order. Learners will see them shuffled. Use distinct values.') }}
		</p>
		<div v-for="(item, i) in items" :key="i" class="flex items-end gap-2">
			<FormControl
				class="flex-1"
				:label="__('Item {0}', [i + 1])"
				:model-value="item"
				@update:model-value="(v) => setItem(i, v)"
			/>
			<Button
				v-if="items.length > 2"
				variant="ghost"
				size="sm"
				:aria-label="__('Remove item {0}', [i + 1])"
				@click="removeItem(i)"
			>
				<span class="lucide-trash-2 size-4" />
			</Button>
		</div>
		<Button @click="addItem">
			<template #prefix><span class="lucide-plus size-4" /></template>
			{{ __('Add Item') }}
		</Button>
	</div>
</template>
<script setup>
import { computed, watch } from 'vue'
import { FormControl, Button } from 'frappe-ui'
import { parseConfig } from '@/questionTypes/util'

const question = defineModel('question')
const items = computed(() => parseConfig(question.value).items || [])

watch(
	question,
	(q) => {
		if (!q) return
		const c = parseConfig(q)
		if (!c.items) {
			question.value.data = { items: ['', ''] }
		} else if (typeof q.data === 'string') {
			question.value.data = c
		}
	},
	{ immediate: true, deep: true }
)

const write = (next) => {
	question.value.data = { items: next }
}
const setItem = (i, v) => {
	const next = [...items.value]
	next[i] = v
	write(next)
}
const addItem = () => {
	write([...items.value, ''])
}
const removeItem = (i) => {
	write(items.value.filter((_, idx) => idx !== i))
}
</script>
```

- [ ] **Step 4: Create OrderingPlayer.vue**

```vue
<template>
	<div class="mt-2">
		<draggable
			v-model="order"
			item-key="value"
			handle=".drag-handle"
			:disabled="showAnswers.length > 0"
		>
			<template #item="{ element, index }">
				<div class="flex items-center gap-2 bg-surface-gray-3 rounded-md p-3 mb-2">
					<span
						class="drag-handle lucide-grip-vertical size-4 text-ink-gray-5 cursor-grab"
						:class="{ 'opacity-40': showAnswers.length }"
					/>
					<span class="flex-1 text-ink-gray-9" v-html="sanitizeRichHTML(element)" />
					<span
						v-if="showAnswers.length && perPosition[index] === 1"
						class="lucide-check-circle w-4 h-4 text-ink-green-5"
					/>
					<span
						v-else-if="showAnswers.length && perPosition[index] === 0"
						class="lucide-x-circle w-4 h-4 text-ink-red-6"
					/>
					<template v-else>
						<Button
							variant="ghost"
							size="sm"
							:disabled="index === 0"
							:aria-label="__('Move up')"
							@click="move(index, -1)"
						>
							<span class="lucide-chevron-up size-4" />
						</Button>
						<Button
							variant="ghost"
							size="sm"
							:disabled="index === order.length - 1"
							:aria-label="__('Move down')"
							@click="move(index, 1)"
						>
							<span class="lucide-chevron-down size-4" />
						</Button>
					</template>
				</div>
			</template>
		</draggable>
	</div>
</template>
<script setup>
import { computed, onMounted } from 'vue'
import { Button } from 'frappe-ui'
import draggable from 'vuedraggable'
import { parseConfig, shuffle } from '@/questionTypes/util'
import { sanitizeRichHTML } from '@/utils/sanitizeRichHTML'

const props = defineProps({
	question: { type: Object, required: true },
	showAnswers: { type: Array, default: () => [] },
	quizShowAnswers: { type: Boolean, default: false },
})
const state = defineModel('state')
const items = computed(() => parseConfig(props.question).items || [])
const perPosition = computed(() => (props.showAnswers.length ? props.showAnswers[0] || [] : []))

const order = computed({
	get: () => state.value?.order || [],
	set: (val) => {
		state.value = { order: val }
	},
})

// On mount, if there's no restored order, present a shuffle (re-shuffle if it
// happens to equal the correct order so the start isn't trivially correct).
onMounted(() => {
	if (order.value.length) return
	const correct = items.value
	let next = shuffle(correct)
	if (correct.length > 1 && next.every((v, i) => v === correct[i])) {
		next = shuffle(correct)
	}
	order.value = next
})

const move = (index, delta) => {
	const target = index + delta
	if (target < 0 || target >= order.value.length) return
	const next = [...order.value]
	;[next[index], next[target]] = [next[target], next[index]]
	order.value = next
}
</script>
```

- [ ] **Step 5: Create ordering.ts + register**

Create `frontend/src/questionTypes/ordering.ts`:

```ts
import type { QuestionTypeDef } from './types'
import { parseConfig } from './util'
import OrderingAuthor from './components/OrderingAuthor.vue'
import OrderingPlayer from './components/OrderingPlayer.vue'

const Ordering: QuestionTypeDef = {
	name: 'Ordering',
	label: 'Ordering',
	autoGraded: true,
	hasLiveCheck: true,
	defaultConfig() {
		return { data: { items: ['', ''] } }
	},
	getAnswers(question, state) {
		const items = parseConfig(question).items || []
		const order = state?.order || []
		return items.map((_: any, i: number) => order[i] ?? '')
	},
	loadAnswer(_question, savedAnswers) {
		return { order: savedAnswers ?? [] }
	},
	AuthorComponent: OrderingAuthor,
	PlayerComponent: OrderingPlayer,
}

export default Ordering
```

In `frontend/src/questionTypes/index.ts`, add `import ordering from './ordering'` and `register(ordering)`.

- [ ] **Step 6: Run tests** — `cd frontend && npx vitest run src/tests/questionTypes.test.ts` → PASS. Then full `npx vitest run`.

- [ ] **Step 7: Manual preview verification (deferred to user)**

In the preview: author a Matching question (≥2 pairs) and an Ordering question (≥2 items); save and re-open for edit (config reloads). As a learner on a `show_answers` quiz: Matching dropdowns show shuffled rights, pick matches, Check → per-left ✓/✗ + correct pairs shown; Ordering shows shuffled items, reorder by drag AND by up/down buttons, Check → per-position ✓/✗; partial answers yield a partial score in the summary.

- [ ] **Step 8: Run reviewers, then commit & push**

Run **vue-frontend-reviewer** and **rtl-i18n-reviewer** on the changed files; address findings.

```bash
git add frontend/src/questionTypes/ordering.ts frontend/src/questionTypes/components/OrderingAuthor.vue frontend/src/questionTypes/components/OrderingPlayer.vue frontend/src/questionTypes/index.ts frontend/src/tests/questionTypes.test.ts
git commit -m "feat(quiz-fe): add Ordering question type"
git push
```

---

## Self-Review

- **Spec coverage:** Matching dropdown player + author (Task 1) ✓; Ordering vuedraggable + up/down a11y buttons + author (Task 2) ✓; shuffle of rights/items (Task 1 util + both players) ✓; re-shuffle if equals correct order (Task 2 OrderingPlayer onMounted) ✓; fixed-length getAnswers (both defs) ✓; per-element reveal via showAnswers[0] ✓; distinct-values hint in author UIs ✓.
- **Placeholder scan:** none — every component/helper is complete.
- **Type consistency:** `name`s `'Matching'`/`'Ordering'` match the backend plan's plugin names + Select options. State keys `selections` (matching) and `order` (ordering) used identically in def `getAnswers`/`loadAnswer` and the players. Player props match the framework contract (`question`/`showAnswers`/`quizShowAnswers`/`v-model:state`). `parseConfig`/`shuffle` from util used consistently.
- **Cross-plan dependency:** backend plugins consume matching answer = chosen-right-per-left (left order) and ordering answer = learner's ordered list — exactly what these `getAnswers` produce. Requires the backend Select options + registry (backend plan).
- **Known limitation** documented (answer-key in player fetch) — flagged for a follow-up sub-project, not addressed here.
