# New Question Types — Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the True/False and multi-blank Fill-in-the-blank types to the frontend registry (Author + Player components + helpers), plus the framework touch-ups they need (registry-driven type options + live-check gate, `data` as a first-class question field).

**Architecture:** Two new `QuestionTypeDef`s registered in `frontend/src/questionTypes/`, each with an Author component (writes config into `question.data`) and a Player component (reads `question.data`, renders inputs, shows live-check reveal). A shared `parseConfig` helper tolerates `data` arriving as a JSON string or object. `Question.vue` gains `data` as a first-class reactive field; `Quiz.vue` gates the Check button on the registry `hasLiveCheck`.

**Tech Stack:** Vue 3 `<script setup>`, frappe-ui, TypeScript, Vitest.

## Global Constraints

- **Existing types unchanged.** Choices/User Input/Open Ended authoring + answering behave identically. The existing 134 Vitest tests stay green.
- **Names match backend exactly:** registry `name` = `"True/False"` and `"Fill in the Blank"` (these equal the backend plugin names and DocType Select options). `label` = same.
- **`data` is a first-class question field.** Author components write `question.data` (object); `Question.vue` initializes `data: {}` on the reactive so edit-mode reloads it. Players read config via `parseConfig` (handles string-or-object).
- **Answer-array alignment:** Fill-blank `getAnswers` returns one entry per blank (empty string for unanswered) so backend per-blank indexing stays aligned through `Quiz.vue`'s `.filter(a => a !== null && a !== undefined)`.
- i18n (`__()`), RTL (logical spacing `ms-`/`me-`/`ps-`/`pe-`), preserve existing class names.
- **Tests:** Vitest locally — `cd frontend && npx vitest run`. Component behavior verified manually in the preview (deferred). After editing `frontend/src`, run the **vue-frontend-reviewer** and **rtl-i18n-reviewer** agents before the final commit.

---

## File Structure

- Create: `frontend/src/questionTypes/util.ts` — `parseConfig(question)`.
- Create: `frontend/src/questionTypes/trueFalse.ts`, `fillBlank.ts` — defs + helpers.
- Create: `frontend/src/questionTypes/components/TrueFalseAuthor.vue`, `TrueFalsePlayer.vue`, `FillBlankAuthor.vue`, `FillBlankPlayer.vue`.
- Modify: `frontend/src/questionTypes/index.ts` — register the two; `questionTypeOptions()` → `name`.
- Modify: `frontend/src/components/Modals/Question.vue` — `data` first-class field.
- Modify: `frontend/src/components/Quiz.vue` — Check gate on `hasLiveCheck`.
- Modify: `frontend/src/tests/questionTypes.test.ts` — tests + extend the `vi.mock('frappe-ui')` factory.

---

## Task 1: Framework touch-ups (options→name, live-check gate, data field, parseConfig)

**Files:**
- Modify: `frontend/src/questionTypes/index.ts`
- Create: `frontend/src/questionTypes/util.ts`
- Modify: `frontend/src/components/Modals/Question.vue`
- Modify: `frontend/src/components/Quiz.vue`
- Test: `frontend/src/tests/questionTypes.test.ts`

**Interfaces:**
- Produces: `questionTypeOptions()` returns type `name`s; `parseConfig(question) -> object`; `Question.vue` reactive has `data: {}`; `Quiz.vue` Check button gated on `getQuestionType(type).hasLiveCheck`.

- [ ] **Step 1: Write the failing tests (append to questionTypes.test.ts)**

```ts
import { questionTypeOptions } from '@/questionTypes'
import { parseConfig } from '@/questionTypes/util'

describe('framework touch-ups', () => {
	it('questionTypeOptions returns names (not labels)', () => {
		const opts = questionTypeOptions()
		expect(opts).toContain('Choices')
		expect(opts).toContain('User Input')
		expect(opts).toContain('Open Ended')
	})
	it('parseConfig handles object and JSON string', () => {
		expect(parseConfig({ data: { a: 1 } })).toEqual({ a: 1 })
		expect(parseConfig({ data: '{"a":2}' })).toEqual({ a: 2 })
		expect(parseConfig({})).toEqual({})
		expect(parseConfig({ data: null })).toEqual({})
	})
})
```

- [ ] **Step 2: Run to confirm failure**

Run: `cd frontend && npx vitest run src/tests/questionTypes.test.ts`
Expected: FAIL — `parseConfig` not found.

- [ ] **Step 3: Create parseConfig util**

Create `frontend/src/questionTypes/util.ts`:

```ts
/** LMS Question.data may arrive as a parsed object (authoring) or a JSON
 *  string (from frappe.get_all in the player fetch). Normalize to an object. */
export function parseConfig(question: any): Record<string, any> {
	const raw = question?.data
	if (!raw) return {}
	if (typeof raw === 'string') {
		try {
			return JSON.parse(raw) || {}
		} catch {
			return {}
		}
	}
	return raw
}
```

- [ ] **Step 4: questionTypeOptions → name**

In `frontend/src/questionTypes/index.ts`, change:

```ts
export function questionTypeOptions(): string[] {
	return Object.values(REGISTRY).map((d) => d.label)
}
```

to:

```ts
export function questionTypeOptions(): string[] {
	return Object.values(REGISTRY).map((d) => d.name)
}
```

- [ ] **Step 5: `data` as a first-class field in Question.vue**

In `frontend/src/components/Modals/Question.vue`, the `question` reactive is initialized like:

```js
const question = reactive({
	question: '',
	type: 'Choices',
	marks: 1,
})
```

Add `data: {}` to it:

```js
const question = reactive({
	question: '',
	type: 'Choices',
	marks: 1,
	data: {},
})
```

In the `watch(show, ...)` reset branch (where it resets `question.question = ''`, `question.type = 'Choices'`, etc.), add `question.data = {}` alongside those resets so a fresh dialog starts with empty config.

(Why: the insert payload is `...question`, so `data` is saved to the JSON field; and `questionData.onSuccess` only copies keys the reactive already has — adding `data` lets edit-mode reload a new-type question's config. Legacy types leave `data` as `{}`, which the backend ignores.)

- [ ] **Step 6: Gate the Check button on hasLiveCheck**

In `frontend/src/components/Quiz.vue`, find the Check button's `v-if` containing `questionDetails.data.type != 'Open Ended'` (~line 217) and replace that clause with `getQuestionType(questionDetails.data.type).hasLiveCheck`. The surrounding conditions (`quiz.data.show_answers && !showAnswers.length && ...`) stay. `getQuestionType` is already imported in Quiz.vue.

- [ ] **Step 7: Run tests**

Run: `cd frontend && npx vitest run src/tests/questionTypes.test.ts`
Expected: PASS (new framework-touch-up tests green; existing tests still green).

- [ ] **Step 8: Commit**

```bash
git add frontend/src/questionTypes/index.ts frontend/src/questionTypes/util.ts frontend/src/components/Modals/Question.vue frontend/src/components/Quiz.vue frontend/src/tests/questionTypes.test.ts
git commit -m "refactor(quiz-fe): registry-driven type options + live-check gate + data field"
```

---

## Task 2: True/False type

**Files:**
- Create: `frontend/src/questionTypes/trueFalse.ts`
- Create: `frontend/src/questionTypes/components/TrueFalseAuthor.vue`, `TrueFalsePlayer.vue`
- Modify: `frontend/src/questionTypes/index.ts`
- Test: `frontend/src/tests/questionTypes.test.ts`

**Interfaces:**
- Produces: default-exported `QuestionTypeDef` named `True/False`. `getAnswers(question, state)` → `[state.choice]` (`"true"`/`"false"`); `loadAnswer(question, saved)` → `{ choice: saved?.[0] ?? null }`. Config in `question.data` = `{ correct: boolean, explanation: string }`. `autoGraded: true`, `hasLiveCheck: true`.

- [ ] **Step 1: Write the failing helper tests (append)**

```ts
import { getQuestionType as gtype } from '@/questionTypes'

describe('True/False helpers', () => {
	it('getAnswers wraps the choice', () => {
		expect(gtype('True/False').getAnswers({}, { choice: 'true' })).toEqual(['true'])
	})
	it('loadAnswer restores the choice', () => {
		expect(gtype('True/False').loadAnswer({}, ['false']).choice).toBe('false')
	})
})
```

- [ ] **Step 2: Run to confirm failure** — `cd frontend && npx vitest run src/tests/questionTypes.test.ts` → FAIL (`True/False` not registered).

- [ ] **Step 3: Create the Author component**

Create `frontend/src/questionTypes/components/TrueFalseAuthor.vue`:

```vue
<template>
	<div class="space-y-4">
		<div>
			<label class="block text-p-sm-medium text-ink-gray-7 mb-1.5">
				{{ __('Correct answer') }}
			</label>
			<div class="flex gap-2">
				<Button
					:variant="config.correct === true ? 'solid' : 'subtle'"
					@click="setCorrect(true)"
				>
					{{ __('True') }}
				</Button>
				<Button
					:variant="config.correct === false ? 'solid' : 'subtle'"
					@click="setCorrect(false)"
				>
					{{ __('False') }}
				</Button>
			</div>
		</div>
		<FormControl
			type="textarea"
			:label="__('Explanation (optional)')"
			:model-value="config.explanation"
			@update:model-value="(v) => set('explanation', v)"
		/>
	</div>
</template>
<script setup>
import { computed, watch } from 'vue'
import { FormControl, Button } from 'frappe-ui'
import { parseConfig } from '@/questionTypes/util'

const question = defineModel('question')
const config = computed(() => parseConfig(question.value))

// Ensure data exists with defaults on first mount / type switch.
watch(
	question,
	(q) => {
		if (!q) return
		const c = parseConfig(q)
		if (c.correct === undefined) {
			question.value.data = { correct: true, explanation: c.explanation || '' }
		} else if (typeof q.data === 'string') {
			question.value.data = c
		}
	},
	{ immediate: true },
)

const set = (key, value) => {
	question.value.data = { ...parseConfig(question.value), [key]: value }
}
const setCorrect = (v) => set('correct', v)
</script>
```

- [ ] **Step 4: Create the Player component**

Create `frontend/src/questionTypes/components/TrueFalsePlayer.vue`:

```vue
<template>
	<div class="space-y-3 mt-2">
		<label
			v-for="opt in options"
			:key="opt.value"
			class="flex items-center bg-surface-gray-3 rounded-md p-3 w-full cursor-pointer"
		>
			<input
				v-if="!showAnswers.length"
				type="radio"
				class="w-3.5 h-3.5 text-ink-gray-9"
				:name="encodeURIComponent(question.question)"
				:checked="state?.choice === opt.value"
				@change="select(opt.value)"
			/>
			<span class="ms-2 text-ink-gray-9">{{ opt.label }}</span>
		</label>
		<div v-if="showAnswers.length">
			<Badge v-if="showAnswers[0]" :label="__('Correct')" theme="green">
				<template #prefix>
					<span class="lucide-check-circle w-4 h-4 text-ink-green-5 me-1" />
				</template>
			</Badge>
			<Badge v-else theme="red" :label="__('Incorrect')">
				<template #prefix>
					<span class="lucide-x-circle w-4 h-4 text-ink-red-6 me-1" />
				</template>
			</Badge>
		</div>
	</div>
</template>
<script setup>
import { Badge } from 'frappe-ui'

defineProps({
	question: { type: Object, required: true },
	showAnswers: { type: Array, default: () => [] },
	quizShowAnswers: { type: Boolean, default: false },
})
const state = defineModel('state')
const options = [
	{ value: 'true', label: __('True') },
	{ value: 'false', label: __('False') },
]
const select = (value) => {
	state.value = { choice: value }
}
</script>
```

- [ ] **Step 5: Create the type definition**

Create `frontend/src/questionTypes/trueFalse.ts`:

```ts
import type { QuestionTypeDef } from './types'
import TrueFalseAuthor from './components/TrueFalseAuthor.vue'
import TrueFalsePlayer from './components/TrueFalsePlayer.vue'

const TrueFalse: QuestionTypeDef = {
	name: 'True/False',
	label: 'True/False',
	autoGraded: true,
	hasLiveCheck: true,
	defaultConfig() {
		return { data: { correct: true, explanation: '' } }
	},
	getAnswers(_question, state) {
		return [state?.choice]
	},
	loadAnswer(_question, savedAnswers) {
		return { choice: savedAnswers?.[0] ?? null }
	},
	AuthorComponent: TrueFalseAuthor,
	PlayerComponent: TrueFalsePlayer,
}

export default TrueFalse
```

- [ ] **Step 6: Register + extend the test mock**

In `frontend/src/questionTypes/index.ts`, add `import trueFalse from './trueFalse'` and `register(trueFalse)`.

In `frontend/src/tests/questionTypes.test.ts`, the `vi.mock('frappe-ui', ...)` factory must include every frappe-ui export the new components import. Add `Badge` (TrueFalsePlayer) to the factory's returned object if not already present, stubbing it the same way as the other component stubs.

- [ ] **Step 7: Run tests** — `cd frontend && npx vitest run src/tests/questionTypes.test.ts` → PASS.

- [ ] **Step 8: Commit**

```bash
git add frontend/src/questionTypes/trueFalse.ts frontend/src/questionTypes/components/TrueFalseAuthor.vue frontend/src/questionTypes/components/TrueFalsePlayer.vue frontend/src/questionTypes/index.ts frontend/src/tests/questionTypes.test.ts
git commit -m "feat(quiz-fe): add True/False question type"
```

---

## Task 3: Fill-in-the-blank type

**Files:**
- Create: `frontend/src/questionTypes/fillBlank.ts`
- Create: `frontend/src/questionTypes/components/FillBlankAuthor.vue`, `FillBlankPlayer.vue`
- Modify: `frontend/src/questionTypes/index.ts`
- Test: `frontend/src/tests/questionTypes.test.ts`

**Interfaces:**
- Produces: default-exported `QuestionTypeDef` named `Fill in the Blank`. Config = `{ blanks: [{ label: string, accepted: string[] }] }`. `getAnswers(question, state)` → one entry per blank (empty string if unanswered); `loadAnswer(question, saved)` → `{ values: saved ?? [] }`. `autoGraded: true`, `hasLiveCheck: true`.

- [ ] **Step 1: Write the failing helper tests (append)**

```ts
describe('Fill in the Blank helpers', () => {
	const q = { data: { blanks: [{ label: '1', accepted: ['a'] }, { label: '2', accepted: ['b'] }] } }
	it('getAnswers returns one entry per blank, empty for missing', () => {
		expect(gtype('Fill in the Blank').getAnswers(q, { values: ['x'] })).toEqual(['x', ''])
	})
	it('loadAnswer restores values', () => {
		expect(gtype('Fill in the Blank').loadAnswer(q, ['p', 'q']).values).toEqual(['p', 'q'])
	})
})
```

- [ ] **Step 2: Run to confirm failure** — FAIL (`Fill in the Blank` not registered).

- [ ] **Step 3: Create the Author component**

Create `frontend/src/questionTypes/components/FillBlankAuthor.vue`:

```vue
<template>
	<div class="space-y-4">
		<div class="text-base-semibold text-ink-gray-9">{{ __('Blanks') }}</div>
		<p class="text-xs text-ink-gray-6">
			{{ __('Reference blanks in your question text as (1), (2), … Learners fill them in order.') }}
		</p>
		<div
			v-for="(blank, i) in blanks"
			:key="i"
			class="border border-outline-elevation-2 rounded-md p-3 space-y-2"
		>
			<div class="flex items-center justify-between">
				<label class="text-p-sm-medium text-ink-gray-7">
					{{ __('Blank {0}', [i + 1]) }}
				</label>
				<Button v-if="blanks.length > 1" variant="ghost" size="sm" @click="removeBlank(i)">
					<span class="lucide-trash-2 size-4" />
				</Button>
			</div>
			<FormControl
				type="textarea"
				:label="__('Accepted answers (one per line)')"
				:model-value="(blank.accepted || []).join('\n')"
				@update:model-value="(v) => setAccepted(i, v)"
			/>
		</div>
		<Button @click="addBlank">
			<template #prefix><span class="lucide-plus size-4" /></template>
			{{ __('Add Blank') }}
		</Button>
	</div>
</template>
<script setup>
import { computed, watch } from 'vue'
import { FormControl, Button } from 'frappe-ui'
import { parseConfig } from '@/questionTypes/util'

const question = defineModel('question')
const blanks = computed(() => parseConfig(question.value).blanks || [])

watch(
	question,
	(q) => {
		if (!q) return
		const c = parseConfig(q)
		if (!c.blanks) {
			question.value.data = { blanks: [{ label: '1', accepted: [] }] }
		} else if (typeof q.data === 'string') {
			question.value.data = c
		}
	},
	{ immediate: true },
)

const write = (next) => {
	question.value.data = { blanks: next }
}
const setAccepted = (i, text) => {
	const next = blanks.value.map((b) => ({ ...b }))
	next[i].accepted = text.split('\n').map((s) => s.trim()).filter(Boolean)
	write(next)
}
const addBlank = () => {
	const next = blanks.value.map((b) => ({ ...b }))
	next.push({ label: String(next.length + 1), accepted: [] })
	write(next)
}
const removeBlank = (i) => {
	const next = blanks.value.filter((_, idx) => idx !== i)
	next.forEach((b, idx) => (b.label = String(idx + 1)))
	write(next)
}
</script>
```

- [ ] **Step 4: Create the Player component**

Create `frontend/src/questionTypes/components/FillBlankPlayer.vue`:

```vue
<template>
	<div class="space-y-3 mt-2">
		<div v-for="(blank, i) in blanks" :key="i" class="space-y-1">
			<label class="text-p-sm-medium text-ink-gray-7">
				{{ __('Blank {0}', [i + 1]) }}
			</label>
			<div class="flex items-center gap-2">
				<FormControl
					class="flex-1"
					:model-value="values[i] || ''"
					:disabled="showAnswers.length ? true : false"
					@update:model-value="(v) => setValue(i, v)"
				/>
				<span
					v-if="showAnswers.length && perBlank[i] === 1"
					class="lucide-check-circle w-4 h-4 text-ink-green-5"
				/>
				<span
					v-else-if="showAnswers.length && perBlank[i] === 0"
					class="lucide-x-circle w-4 h-4 text-ink-red-6"
				/>
			</div>
			<div v-if="showAnswers.length && perBlank[i] === 0" class="text-xs text-ink-gray-6">
				{{ __('Accepted: {0}', [(blank.accepted || []).join(', ')]) }}
			</div>
		</div>
	</div>
</template>
<script setup>
import { computed } from 'vue'
import { FormControl } from 'frappe-ui'
import { parseConfig } from '@/questionTypes/util'

const props = defineProps({
	question: { type: Object, required: true },
	showAnswers: { type: Array, default: () => [] },
	quizShowAnswers: { type: Boolean, default: false },
})
const state = defineModel('state')
const blanks = computed(() => parseConfig(props.question).blanks || [])
const values = computed(() => state.value?.values || [])
// checkAnswer pushes the per-blank array as showAnswers[0].
const perBlank = computed(() => (props.showAnswers.length ? props.showAnswers[0] || [] : []))

const setValue = (i, v) => {
	const next = blanks.value.map((_, idx) => values.value[idx] ?? '')
	next[i] = v
	state.value = { values: next }
}
</script>
```

- [ ] **Step 5: Create the type definition**

Create `frontend/src/questionTypes/fillBlank.ts`:

```ts
import type { QuestionTypeDef } from './types'
import { parseConfig } from './util'
import FillBlankAuthor from './components/FillBlankAuthor.vue'
import FillBlankPlayer from './components/FillBlankPlayer.vue'

const FillBlank: QuestionTypeDef = {
	name: 'Fill in the Blank',
	label: 'Fill in the Blank',
	autoGraded: true,
	hasLiveCheck: true,
	defaultConfig() {
		return { data: { blanks: [{ label: '1', accepted: [] }] } }
	},
	getAnswers(question, state) {
		const blanks = parseConfig(question).blanks || []
		const values = state?.values || []
		return blanks.map((_: any, i: number) => values[i] ?? '')
	},
	loadAnswer(_question, savedAnswers) {
		return { values: savedAnswers ?? [] }
	},
	AuthorComponent: FillBlankAuthor,
	PlayerComponent: FillBlankPlayer,
}

export default FillBlank
```

- [ ] **Step 6: Register**

In `frontend/src/questionTypes/index.ts`, add `import fillBlank from './fillBlank'` and `register(fillBlank)`. (The new components import only `FormControl` — already in the test mock factory from earlier — so no further `vi.mock` additions are needed; verify by running the suite.)

- [ ] **Step 7: Run tests** — `cd frontend && npx vitest run src/tests/questionTypes.test.ts` → PASS.

- [ ] **Step 8: Manual preview verification (deferred to user)**

In the preview: author a True/False question (pick correct + explanation) and a Fill-in-the-blank (2 blanks, accepted answers); save and re-open for edit (config reloads). As a learner on a `show_answers` quiz: answer both, click Check — True/False shows Correct/Incorrect badge; Fill-blank shows per-blank ✓/✗ and accepted answers; partial fill-blank yields a partial score in the summary.

- [ ] **Step 9: Run reviewers, then commit & push**

Run **vue-frontend-reviewer** and **rtl-i18n-reviewer** on the changed files; address findings.

```bash
git add frontend/src/questionTypes/fillBlank.ts frontend/src/questionTypes/components/FillBlankAuthor.vue frontend/src/questionTypes/components/FillBlankPlayer.vue frontend/src/questionTypes/index.ts frontend/src/tests/questionTypes.test.ts
git commit -m "feat(quiz-fe): add Fill in the Blank question type"
git push
```

---

## Self-Review

- **Spec coverage:** questionTypeOptions→name (Task 1) ✓; live-check gate frontend (Task 1) ✓; `data` first-class field (Task 1) ✓; True/False author/player/helpers (Task 2) ✓; Fill-blank multi-blank, separate-list, per-blank reveal (Task 3) ✓; case-insensitive matching is BACKEND (backend plan) — frontend just sends raw strings ✓; partial credit shown via summary score (Task 3 manual) ✓.
- **Placeholder scan:** none — every component and helper is complete.
- **Type consistency:** `name` strings (`'True/False'`, `'Fill in the Blank'`) match the backend plan's plugin names and Select options exactly. `parseConfig` used in both authors, both players, and fillBlank.getAnswers. Player props (`question`/`showAnswers`/`quizShowAnswers`/`v-model:state`) match the existing player contract from the framework. `getAnswers`/`loadAnswer` signatures match `QuestionTypeDef`.
- **Alignment note:** Fill-blank `getAnswers` returns a fixed-length array (one per blank, `''` for missing) so Quiz.vue's null-filter never shortens it and backend per-blank indices stay aligned.
- **Cross-plan dependency:** requires the backend plan's `data`-in-fetch (Task 4) for the player to receive config, and the new Select options (backend Tasks 5-6) for the Type dropdown values to be accepted on save.
