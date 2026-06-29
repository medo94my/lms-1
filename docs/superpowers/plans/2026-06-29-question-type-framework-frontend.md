# Question-Type Framework — Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the hardcoded per-type UI in `Modals/Question.vue` (authoring) and `Quiz.vue` (answering) into thin **hosts** that render per-type components resolved from a frontend question-type registry mirroring the backend.

**Architecture:** A new `frontend/src/questionTypes/` module holds a registry plus, per type, a definition object (`label`, `defaultConfig`, pure `getAnswers`/`loadAnswer` helpers, `AuthorComponent`, `PlayerComponent`). The existing three types (Choices, User Input, Open Ended) are re-homed with **identical behavior and storage** — they keep reading/writing `option_1..10` / `possibility_1..10`. New types (later spec) use the `data` JSON field.

**Tech Stack:** Vue 3 `<script setup>`, frappe-ui, TypeScript for the registry, Vitest for unit tests. The preview container (`lms-preview.craftspace.space`) hot-reloads these files; use it for visual verification.

## Global Constraints

- **Behavior + storage unchanged** for Choices / User Input / Open Ended. The insert/update payload to `LMS Question` must keep the same `option_N` / `is_correct_N` / `explanation_N` / `possibility_N` fields. Do not move existing types to the `data` field in this plan.
- **i18n:** every user-facing string wrapped in `__()` (project rule).
- **RTL:** use logical spacing (`ms-`/`me-`/`ps-`/`pe-`), never hardcoded `left`/`right` (project rule). Preserve existing classes when moving markup.
- **frappe-ui resource gotcha:** never `auto: true` when params come from async props; the existing components already follow this — don't regress it.
- **Tests:** Vitest, run locally with `npx vitest run <path>` (or the package script `yarn test`). Component-level behavior is verified manually in the preview (`/preview-deploy` if a config change is needed; `.vue` edits hot-reload).
- After editing files under `frontend/src`, run the **vue-frontend-reviewer** and **rtl-i18n-reviewer** agents before the final commit (project rule).

---

## File Structure

- Create: `frontend/src/questionTypes/types.ts` — the `QuestionTypeDef` TS interface.
- Create: `frontend/src/questionTypes/index.ts` — registry: `getQuestionType`, `questionTypeOptions`, `questionTypeNames`.
- Create: `frontend/src/questionTypes/choices.ts` / `userInput.ts` / `openEnded.ts` — definitions + pure helpers.
- Create: `frontend/src/questionTypes/components/ChoicesAuthor.vue` / `UserInputAuthor.vue` / `OpenEndedAuthor.vue`.
- Create: `frontend/src/questionTypes/components/ChoicesPlayer.vue` / `UserInputPlayer.vue` / `OpenEndedPlayer.vue`.
- Create: `frontend/src/tests/questionTypes.test.ts` — unit tests for the pure helpers + registry.
- Modify: `frontend/src/components/Modals/Question.vue` — becomes the authoring host.
- Modify: `frontend/src/components/Quiz.vue` — becomes the player host.

---

## Task 1: Registry + definition contract

**Files:**
- Create: `frontend/src/questionTypes/types.ts`
- Create: `frontend/src/questionTypes/index.ts`
- Test: `frontend/src/tests/questionTypes.test.ts`

**Interfaces:**
- Produces:
  - `interface QuestionTypeDef { name: string; label: string; autoGraded: boolean; hasLiveCheck: boolean; defaultConfig(): Record<string, any>; getAnswers(question: any, state: any): string[]; loadAnswer(question: any, savedAnswers: string[]): any; AuthorComponent: Component; PlayerComponent: Component }`
  - `getQuestionType(name: string): QuestionTypeDef`
  - `questionTypeNames(): string[]`
  - `questionTypeOptions(): string[]` (for the `type` FormControl select; same values as backend Select).

- [ ] **Step 1: Write the failing test**

Create `frontend/src/tests/questionTypes.test.ts`:

```ts
import { describe, it, expect } from 'vitest'
import { getQuestionType, questionTypeNames } from '@/questionTypes'

describe('question type registry', () => {
	it('registers the three existing types', () => {
		const names = questionTypeNames()
		expect(names).toContain('Choices')
		expect(names).toContain('User Input')
		expect(names).toContain('Open Ended')
	})

	it('throws on an unknown type', () => {
		expect(() => getQuestionType('Nope')).toThrow()
	})
})
```

- [ ] **Step 2: Run it to confirm it fails**

Run: `cd frontend && npx vitest run src/tests/questionTypes.test.ts`
Expected: FAIL — cannot resolve `@/questionTypes`.

- [ ] **Step 3: Write the contract type**

Create `frontend/src/questionTypes/types.ts`:

```ts
import type { Component } from 'vue'

export interface QuestionTypeDef {
	name: string
	label: string
	autoGraded: boolean
	hasLiveCheck: boolean
	/** Initial per-type fields merged into a new question object. */
	defaultConfig(): Record<string, any>
	/** Normalize the learner's current UI state into the answer array the
	 *  backend expects (the same shape today's getAnswers() returns). */
	getAnswers(question: any, state: any): string[]
	/** Given saved answers from localStorage, return the UI state to restore. */
	loadAnswer(question: any, savedAnswers: string[]): any
	AuthorComponent: Component
	PlayerComponent: Component
}
```

- [ ] **Step 4: Write the registry**

Create `frontend/src/questionTypes/index.ts`:

```ts
import type { QuestionTypeDef } from './types'
import choices from './choices'
import userInput from './userInput'
import openEnded from './openEnded'

const REGISTRY: Record<string, QuestionTypeDef> = {}

function register(def: QuestionTypeDef) {
	REGISTRY[def.name] = def
}

register(choices)
register(userInput)
register(openEnded)

export function getQuestionType(name: string): QuestionTypeDef {
	const def = REGISTRY[name]
	if (!def) throw new Error(`Unknown question type: ${name}`)
	return def
}

export function questionTypeNames(): string[] {
	return Object.keys(REGISTRY)
}

export function questionTypeOptions(): string[] {
	return Object.values(REGISTRY).map((d) => d.label)
}
```

> The three imports require Tasks 2-4's files. Create the definition files (Tasks 2-4) before running the test green. Implement Tasks 1-4 as one unit.

- [ ] **Step 5: Run the test to confirm it passes** (after Tasks 2-4 files exist)

Run: `cd frontend && npx vitest run src/tests/questionTypes.test.ts`
Expected: PASS.

- [ ] **Step 6: Commit** (with Tasks 2-4)

```bash
git add frontend/src/questionTypes/ frontend/src/tests/questionTypes.test.ts
git commit -m "feat(quiz-fe): add question-type registry and contract"
```

---

## Task 2: Choices definition + pure answer helpers

**Files:**
- Create: `frontend/src/questionTypes/choices.ts`
- (AuthorComponent/PlayerComponent created in Tasks 5/6; until then reference them via dynamic import placeholders — see Step 3.)

**Interfaces:**
- Produces: default-exported `QuestionTypeDef` named `Choices`.
- `getAnswers(question, state)`: `state` = `{ selectedOptions: number[] }`; returns the selected option strings (mirrors `Quiz.vue:772-786` Choices branch).
- `loadAnswer(question, savedAnswers)`: returns `{ selectedOptions: number[] }` of length 10 (mirrors `Quiz.vue:731-738`).

- [ ] **Step 1: Write the failing helper tests (append to questionTypes.test.ts)**

```ts
import { getQuestionType as gt } from '@/questionTypes'

describe('Choices helpers', () => {
	const question = { type: 'Choices', option_1: 'a', option_2: 'b', option_3: 'c' }

	it('getAnswers returns the selected option labels', () => {
		const def = gt('Choices')
		const answers = def.getAnswers(question, { selectedOptions: [1, 0, 1, ...Array(7).fill(0)] })
		expect(answers).toEqual(['a', 'c'])
	})

	it('loadAnswer marks the saved options as selected', () => {
		const def = gt('Choices')
		const state = def.loadAnswer(question, ['b'])
		expect(state.selectedOptions[1]).toBe(1)
		expect(state.selectedOptions[0]).toBe(0)
	})
})
```

- [ ] **Step 2: Run to confirm failure**

Run: `cd frontend && npx vitest run src/tests/questionTypes.test.ts`
Expected: FAIL — `choices.ts` not found / helpers undefined.

- [ ] **Step 3: Implement the definition**

Create `frontend/src/questionTypes/choices.ts`:

```ts
import type { QuestionTypeDef } from './types'
import ChoicesAuthor from './components/ChoicesAuthor.vue'
import ChoicesPlayer from './components/ChoicesPlayer.vue'

const MAX_OPTIONS = 10

const Choices: QuestionTypeDef = {
	name: 'Choices',
	label: 'Choices',
	autoGraded: true,
	hasLiveCheck: true,

	defaultConfig() {
		const cfg: Record<string, any> = {}
		for (let n = 1; n <= MAX_OPTIONS; n++) {
			cfg[`option_${n}`] = null
			cfg[`is_correct_${n}`] = false
			cfg[`explanation_${n}`] = null
		}
		return cfg
	},

	getAnswers(question, state) {
		const answers: string[] = []
		const selected: number[] = state?.selectedOptions || []
		selected.forEach((value, index) => {
			if (value) answers.push(question[`option_${index + 1}`])
		})
		return answers
	},

	loadAnswer(question, savedAnswers) {
		const selectedOptions = Array(MAX_OPTIONS).fill(0)
		;(savedAnswers || []).forEach((answer) => {
			for (let i = 1; i <= MAX_OPTIONS; i++) {
				if (question[`option_${i}`] === answer) selectedOptions[i - 1] = 1
			}
		})
		return { selectedOptions }
	},

	AuthorComponent: ChoicesAuthor,
	PlayerComponent: ChoicesPlayer,
}

export default Choices
```

> The `.vue` imports require Tasks 5/6. If running tests before those exist, the import will fail. Create stub `.vue` files (`<template><div/></template>`) for ChoicesAuthor/ChoicesPlayer first, then flesh them out in Tasks 5/6. The helper unit tests don't render the components, so stubs are fine for green helper tests.

- [ ] **Step 4: Run to confirm pass**

Run: `cd frontend && npx vitest run src/tests/questionTypes.test.ts`
Expected: PASS.

- [ ] **Step 5: Commit** (folded into Task 1 unit).

```bash
git add frontend/src/questionTypes/choices.ts frontend/src/tests/questionTypes.test.ts
git commit -m "feat(quiz-fe): add Choices type definition and helpers"
```

---

## Task 3: User Input definition + helpers

**Files:**
- Create: `frontend/src/questionTypes/userInput.ts`

**Interfaces:**
- `getAnswers(question, state)`: `state` = `{ possibleAnswer: string }`; returns `[possibleAnswer]` (mirrors `Quiz.vue:781-783`).
- `loadAnswer(question, savedAnswers)`: returns `{ possibleAnswer: savedAnswers[0] ?? null }` (mirrors `Quiz.vue:739-741`).

- [ ] **Step 1: Failing test (append)**

```ts
describe('User Input helpers', () => {
	it('getAnswers wraps the text answer in an array', () => {
		const def = gt('User Input')
		expect(def.getAnswers({}, { possibleAnswer: 'hello' })).toEqual(['hello'])
	})
	it('loadAnswer restores the first saved answer', () => {
		const def = gt('User Input')
		expect(def.loadAnswer({}, ['hi']).possibleAnswer).toBe('hi')
	})
})
```

- [ ] **Step 2: Run, confirm failure** — `cd frontend && npx vitest run src/tests/questionTypes.test.ts` → FAIL.

- [ ] **Step 3: Implement**

Create `frontend/src/questionTypes/userInput.ts`:

```ts
import type { QuestionTypeDef } from './types'
import UserInputAuthor from './components/UserInputAuthor.vue'
import UserInputPlayer from './components/UserInputPlayer.vue'

const MAX_OPTIONS = 10

const UserInput: QuestionTypeDef = {
	name: 'User Input',
	label: 'User Input',
	autoGraded: true,
	hasLiveCheck: true,

	defaultConfig() {
		const cfg: Record<string, any> = {}
		for (let n = 1; n <= MAX_OPTIONS; n++) cfg[`possibility_${n}`] = null
		return cfg
	},

	getAnswers(_question, state) {
		return [state?.possibleAnswer]
	},

	loadAnswer(_question, savedAnswers) {
		return { possibleAnswer: savedAnswers?.[0] ?? null }
	},

	AuthorComponent: UserInputAuthor,
	PlayerComponent: UserInputPlayer,
}

export default UserInput
```

- [ ] **Step 4: Run, confirm pass.** Commit (folded into Task 1 unit).

```bash
git add frontend/src/questionTypes/userInput.ts frontend/src/tests/questionTypes.test.ts
git commit -m "feat(quiz-fe): add User Input type definition and helpers"
```

---

## Task 4: Open Ended definition + helpers

**Files:**
- Create: `frontend/src/questionTypes/openEnded.ts`

**Interfaces:**
- `getAnswers(question, state)`: returns `[state.possibleAnswer]` (open-ended uses the rich-text answer; mirrors `Quiz.vue:781-783` else-branch).
- `loadAnswer`: `{ possibleAnswer: savedAnswers?.[0] ?? null }`.

- [ ] **Step 1: Failing test (append)**

```ts
describe('Open Ended helpers', () => {
	it('is not auto-graded and has no live check', () => {
		const def = gt('Open Ended')
		expect(def.autoGraded).toBe(false)
		expect(def.hasLiveCheck).toBe(false)
	})
})
```

- [ ] **Step 2: Run, confirm failure.**

- [ ] **Step 3: Implement**

Create `frontend/src/questionTypes/openEnded.ts`:

```ts
import type { QuestionTypeDef } from './types'
import OpenEndedAuthor from './components/OpenEndedAuthor.vue'
import OpenEndedPlayer from './components/OpenEndedPlayer.vue'

const OpenEnded: QuestionTypeDef = {
	name: 'Open Ended',
	label: 'Open Ended',
	autoGraded: false,
	hasLiveCheck: false,

	defaultConfig() {
		return {}
	},

	getAnswers(_question, state) {
		return [state?.possibleAnswer]
	},

	loadAnswer(_question, savedAnswers) {
		return { possibleAnswer: savedAnswers?.[0] ?? null }
	},

	AuthorComponent: OpenEndedAuthor,
	PlayerComponent: OpenEndedPlayer,
}

export default OpenEnded
```

- [ ] **Step 4: Run, confirm pass; push Tasks 1-4 together.**

```bash
git add frontend/src/questionTypes/ frontend/src/tests/questionTypes.test.ts
git commit -m "feat(quiz-fe): add Open Ended type definition and helpers"
git push
```

Verification: `cd frontend && npx vitest run src/tests/questionTypes.test.ts` all green.

---

## Task 5: Author components + `Question.vue` host

**Files:**
- Create: `frontend/src/questionTypes/components/ChoicesAuthor.vue`, `UserInputAuthor.vue`, `OpenEndedAuthor.vue`
- Modify: `frontend/src/components/Modals/Question.vue`

**Interfaces:**
- AuthorComponent contract: prop `question` (the reactive question object, two-way) and `visibleCount` handling internal to each component. Author components mutate the shared `question` object's `option_N` / `possibility_N` fields directly (same object `Question.vue` inserts), so the insert payload is unchanged.

- [ ] **Step 1: Extract ChoicesAuthor.vue**

Create `frontend/src/questionTypes/components/ChoicesAuthor.vue`, moving the Choices markup from `Question.vue:44-104` verbatim (the Options heading, the `v-for="n in visibleOptionCount"` grid with option/explanation/is_correct controls, and the Add Option button) plus the `addOption` / `removeOption` / `visibleOptionCount` logic from `Question.vue:194,315-331`:

```vue
<template>
	<div>
		<div class="text-base-semibold text-ink-gray-9 mb-5 mt-10">
			{{ __('Options') }}
		</div>
		<div class="grid grid-cols-2 gap-x-8 gap-y-4">
			<div v-for="n in visibleOptionCount" :key="n" class="space-y-4 py-2">
				<div class="flex items-center justify-between">
					<label class="block text-p-sm-medium text-ink-gray-7">
						{{ __('Option') + ' ' + n }}
					</label>
					<Button
						v-if="visibleOptionCount > 2"
						variant="ghost"
						size="sm"
						@click="removeOption(n)"
					>
						<span class="lucide-trash-2 size-4" />
					</Button>
				</div>
				<FormControl
					v-model="question[`option_${n}`]"
					:required="n <= 2 ? true : false"
				/>
				<FormControl
					:label="__('Explanation')"
					v-model="question[`explanation_${n}`]"
				/>
				<BooleanSwitch
					size="sm"
					:label="__('Correct Answer')"
					:description="__('Mark this option as a correct answer.')"
					v-model="question[`is_correct_${n}`]"
				/>
			</div>
		</div>
		<div class="mt-4">
			<Button v-if="visibleOptionCount < MAX_OPTIONS" @click="addOption()">
				<template #prefix>
					<span class="lucide-plus size-4" />
				</template>
				{{ __('Add Option') }}
			</Button>
		</div>
	</div>
</template>
<script setup>
import { ref, watch } from 'vue'
import { FormControl, Button } from 'frappe-ui'
import BooleanSwitch from '@/components/Controls/BooleanSwitch.vue'

const MAX_OPTIONS = 10
const question = defineModel('question')
const visibleOptionCount = ref(2)

// Restore the visible count when editing an existing question.
watch(
	question,
	(q) => {
		if (!q) return
		visibleOptionCount.value = Math.max(
			2,
			...Array.from({ length: MAX_OPTIONS }, (_, i) =>
				q[`option_${i + 1}`] ? i + 1 : 0,
			),
		)
	},
	{ immediate: true },
)

const addOption = () => {
	if (visibleOptionCount.value < MAX_OPTIONS) visibleOptionCount.value++
}

const removeOption = (pos) => {
	if (visibleOptionCount.value <= 2) return
	for (let n = pos; n < visibleOptionCount.value; n++) {
		question.value[`option_${n}`] = question.value[`option_${n + 1}`]
		question.value[`is_correct_${n}`] = question.value[`is_correct_${n + 1}`]
		question.value[`explanation_${n}`] = question.value[`explanation_${n + 1}`]
	}
	const last = visibleOptionCount.value
	question.value[`option_${last}`] = null
	question.value[`is_correct_${last}`] = false
	question.value[`explanation_${last}`] = null
	visibleOptionCount.value--
}
</script>
```

- [ ] **Step 2: Extract UserInputAuthor.vue**

Create `frontend/src/questionTypes/components/UserInputAuthor.vue` from `Question.vue:105-138` (Possibilities heading + grid + Add Possibility) plus `addPossibility`/`removePossibility`/`visiblePossibilityCount` (`Question.vue:195,301-313`):

```vue
<template>
	<div>
		<div class="text-base-semibold text-ink-gray-9 mb-5 mt-5">
			{{ __('Possibilities') }}
		</div>
		<div class="grid grid-cols-2 gap-x-8 gap-y-4 py-2">
			<div
				v-for="n in visiblePossibilityCount"
				:key="n"
				class="flex items-end gap-2"
			>
				<FormControl
					class="flex-1"
					:label="__('Possibility') + ' ' + n"
					v-model="question[`possibility_${n}`]"
					:required="n == 1 ? true : false"
				/>
				<Button
					v-if="visiblePossibilityCount > 1"
					variant="ghost"
					@click="removePossibility(n)"
				>
					<span class="lucide-trash-2 size-4" />
				</Button>
			</div>
		</div>
		<div class="mt-4">
			<Button
				v-if="visiblePossibilityCount < MAX_OPTIONS"
				@click="addPossibility()"
			>
				<template #prefix>
					<span class="lucide-plus size-4" />
				</template>
				{{ __('Add Possibility') }}
			</Button>
		</div>
	</div>
</template>
<script setup>
import { ref, watch } from 'vue'
import { FormControl, Button } from 'frappe-ui'

const MAX_OPTIONS = 10
const question = defineModel('question')
const visiblePossibilityCount = ref(1)

watch(
	question,
	(q) => {
		if (!q) return
		visiblePossibilityCount.value = Math.max(
			1,
			...Array.from({ length: MAX_OPTIONS }, (_, i) =>
				q[`possibility_${i + 1}`] ? i + 1 : 0,
			),
		)
	},
	{ immediate: true },
)

const addPossibility = () => {
	if (visiblePossibilityCount.value < MAX_OPTIONS) visiblePossibilityCount.value++
}

const removePossibility = (pos) => {
	if (visiblePossibilityCount.value <= 1) return
	for (let n = pos; n < visiblePossibilityCount.value; n++) {
		question.value[`possibility_${n}`] = question.value[`possibility_${n + 1}`]
	}
	question.value[`possibility_${visiblePossibilityCount.value}`] = null
	visiblePossibilityCount.value--
}
</script>
```

- [ ] **Step 3: Create OpenEndedAuthor.vue (no extra fields)**

Create `frontend/src/questionTypes/components/OpenEndedAuthor.vue`:

```vue
<template>
	<!-- Open-ended questions need no answer configuration. -->
	<div />
</template>
<script setup>
defineModel('question')
</script>
```

- [ ] **Step 4: Refactor `Question.vue` to host the author components**

In `frontend/src/components/Modals/Question.vue`:

1. Replace the entire per-type block (`Question.vue:44-138` — the Options/Possibilities sections) with a single dynamic host, placed right after the Type FormControl (`:44`):

```vue
<component
	:is="getQuestionType(question.type).AuthorComponent"
	v-model:question="question"
/>
```

2. Make the Type select options come from the registry. Replace `Question.vue:39`:

```vue
:options="['Choices', 'User Input', 'Open Ended']"
```

with:

```vue
:options="questionTypeOptions()"
```

3. Add imports to the `<script setup>`:

```js
import { getQuestionType, questionTypeOptions } from '@/questionTypes'
```

4. Remove the now-unused `addOption`, `removeOption`, `addPossibility`, `removePossibility`, `visibleOptionCount`, `visiblePossibilityCount` from `Question.vue` (they moved into the author components). Keep `populateFields()`, `MAX_OPTIONS`, and the `questionData.onSuccess` field-copy logic — the host still owns the shared `question` object and its create/update resources. The `onSuccess` visible-count recomputation (`Question.vue:238-249`) is now handled inside the author components' `watch`, so delete those two `Math.max` assignments from `onSuccess`.

- [ ] **Step 5: Verify in the preview (manual)**

Open the preview, edit a quiz, and confirm: creating a Choices question (add/remove options, mark correct), a User Input question (add/remove possibilities), and an Open Ended question all save and re-open for edit identically to before. Confirm the saved `LMS Question` still has `option_N`/`possibility_N` populated (check via the quiz list).

- [ ] **Step 6: Run reviewers, then commit**

Run the **vue-frontend-reviewer** and **rtl-i18n-reviewer** agents on the changed files; address findings.

```bash
git add frontend/src/components/Modals/Question.vue frontend/src/questionTypes/components/
git commit -m "refactor(quiz-fe): host per-type author components in Question modal"
git push
```

---

## Task 6: Player components + `Quiz.vue` host

> **Highest-risk task.** `Quiz.vue` weaves per-type state (`selectedOptions`, `possibleAnswer`, `showAnswers`) through shared orchestration (timer, pagination, localStorage, submit). The contract below pulls per-type rendering + answer-shaping into components while the host keeps orchestration and a single normalized `currentAnswerState`.

**Files:**
- Create: `frontend/src/questionTypes/components/ChoicesPlayer.vue`, `UserInputPlayer.vue`, `OpenEndedPlayer.vue`
- Modify: `frontend/src/components/Quiz.vue`

**Player contract (all three components):**
- Props:
  - `question` (Object) — the question detail (`questionDetails.data`).
  - `state` (Object, `v-model:state`) — the per-type UI state object (`{ selectedOptions }` for Choices, `{ possibleAnswer }` for the other two). The host owns it so `getAnswers`/`loadAnswer` from the registry stay the single source of truth.
  - `showAnswers` (Array) — the live-check / reveal payload; truthy length = reveal mode (disable inputs, show correctness).
  - `quizShowAnswers` (Boolean) — `quiz.data.show_answers`.
- The component renders inputs bound to `state` and the reveal UI from `showAnswers`. It does **not** call the backend; the host owns `checkAnswer`/`submit`.

- [ ] **Step 1: Create ChoicesPlayer.vue**

Move `Quiz.vue:155-215` (the Choices option rendering with radio/checkbox, the `showAnswers` icon logic, explanations) into `frontend/src/questionTypes/components/ChoicesPlayer.vue`. Bind selection to `state.selectedOptions` and emit changes via `v-model:state`. Move `markAnswer` (`Quiz.vue:762-770`) into this component:

```vue
<template>
	<div v-for="index in MAX_OPTIONS" :key="index">
		<label
			v-if="question[`option_${index}`]"
			class="flex items-center bg-surface-gray-3 rounded-md p-3 mt-4 w-full cursor-pointer focus:border-primary-600"
		>
			<input
				v-if="!showAnswers.length && !question.multiple"
				type="radio"
				:name="encodeURIComponent(question.question)"
				class="w-3.5 h-3.5 text-ink-gray-9 focus:ring-outline-elevation-2"
				@change="markAnswer(index)"
				:checked="selected[index - 1]"
			/>
			<input
				v-else-if="!showAnswers.length && question.multiple"
				type="checkbox"
				:name="encodeURIComponent(question.question)"
				class="w-3.5 h-3.5 text-ink-gray-9 rounded-sm focus:ring-outline-elevation-2"
				@change="markAnswer(index)"
				:checked="selected[index - 1]"
			/>
			<div v-else-if="quizShowAnswers" v-for="(answer, idx) in showAnswers" :key="idx">
				<div v-if="index - 1 == idx">
					<span v-if="answer == 1" class="lucide-check-circle w-4 h-4 text-ink-green-5" />
					<span v-else-if="answer == 2" class="lucide-minus-circle w-4 h-4 text-ink-green-5" />
					<span v-else-if="answer == 0" class="lucide-x-circle w-4 h-4 text-ink-red-6" />
					<span v-else class="lucide-minus-circle w-4 h-4" />
				</div>
			</div>
			<span class="ms-2 text-ink-gray-9" v-html="sanitizeRichHTML(question[`option_${index}`])" />
		</label>
		<div
			v-if="question[`explanation_${index}`]"
			class="mt-2 text-xs text-ink-gray-7"
			v-show="showAnswers.length"
		>
			{{ question[`explanation_${index}`] }}
		</div>
	</div>
</template>
<script setup>
import { computed } from 'vue'
import { sanitizeRichHTML } from '@/utils/sanitizeRichHTML'

const MAX_OPTIONS = 10
const props = defineProps({
	question: { type: Object, required: true },
	showAnswers: { type: Array, default: () => [] },
	quizShowAnswers: { type: Boolean, default: false },
})
const state = defineModel('state')
const selected = computed(() => state.value?.selectedOptions || Array(MAX_OPTIONS).fill(0))

const markAnswer = (index) => {
	const next = props.question.multiple
		? [...selected.value]
		: Array(MAX_OPTIONS).fill(0)
	next[index - 1] = selected.value[index - 1] ? 0 : 1
	state.value = { selectedOptions: next }
}
</script>
```

- [ ] **Step 2: Create UserInputPlayer.vue**

From `Quiz.vue:216-237` (textarea + correct/incorrect badge):

```vue
<template>
	<div>
		<FormControl
			:model-value="state?.possibleAnswer"
			@update:model-value="(v) => (state = { possibleAnswer: v })"
			type="textarea"
			:disabled="showAnswers.length ? true : false"
			class="my-2"
		/>
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
import { FormControl, Badge } from 'frappe-ui'

defineProps({
	question: { type: Object, required: true },
	showAnswers: { type: Array, default: () => [] },
	quizShowAnswers: { type: Boolean, default: false },
})
const state = defineModel('state')
</script>
```

- [ ] **Step 3: Create OpenEndedPlayer.vue**

From `Quiz.vue:238-247` (rich TextEditor):

```vue
<template>
	<TextEditor
		class="mt-4"
		:content="state?.possibleAnswer"
		@change="(val) => (state = { possibleAnswer: val })"
		:editable="true"
		:fixedMenu="true"
		editorClass="prose-sm max-w-none border-b border-x border-outline-elevation-2 bg-surface-gray-2 rounded-b-md py-1 px-2 min-h-[7rem]"
	/>
</template>
<script setup>
import { TextEditor } from 'frappe-ui'

defineProps({
	question: { type: Object, required: true },
	showAnswers: { type: Array, default: () => [] },
	quizShowAnswers: { type: Boolean, default: false },
})
const state = defineModel('state')
</script>
```

- [ ] **Step 4: Refactor `Quiz.vue` to host the player components**

1. Replace the three type branches in the template (`Quiz.vue:155-247`) with a single host:

```vue
<component
	:is="getQuestionType(questionDetails.data.type).PlayerComponent"
	:question="questionDetails.data"
	v-model:state="currentAnswerState"
	:show-answers="showAnswers"
	:quiz-show-answers="quiz.data.show_answers"
/>
```

2. Replace the two separate state refs (`selectedOptions`, `possibleAnswer`) with one normalized object:

```js
const currentAnswerState = ref({})
```

3. Rewrite `getAnswers()` (`Quiz.vue:772-786`) to delegate to the registry:

```js
const getAnswers = () => {
	if (!questionDetails.data) return []
	return getQuestionType(questionDetails.data.type)
		.getAnswers(questionDetails.data, currentAnswerState.value)
		.filter((a) => a !== null && a !== undefined)
}
```

4. Rewrite `loadSavedAnswers()` (`Quiz.vue:722-745`) to delegate:

```js
const loadSavedAnswers = () => {
	const quizData = JSON.parse(localStorage.getItem(quiz.data.title) || 'null')
	if (!quizData) return
	const localQuestion = quizData.find((q) => q.question_name == currentQuestion.value)
	if (!localQuestion?.answer?.length) return
	currentAnswerState.value = getQuestionType(questionDetails.data.type).loadAnswer(
		questionDetails.data,
		localQuestion.answer,
	)
}
```

5. Update the reset/markAnswer touch points:
   - Delete `markAnswer` (moved into ChoicesPlayer) and the `selectedOptions` resets in `resetQuestion` (`:860-864`), `resetQuiz` (`:907-911`), `startQuiz` — replace each `selectedOptions.value.splice(...)` + `possibleAnswer.value = null` pair with `currentAnswerState.value = {}`.
   - In `checkAnswer()` onSuccess (`Quiz.vue:804-818`), the Choices branch updated `showAnswers` from `selectedOptions`. Keep the existing logic but read selection from `currentAnswerState.value.selectedOptions` instead of `selectedOptions.value`. The User Input/Open Ended branch (`showAnswers.push(data)`) is unchanged.
   - Remove the now-unused `MAX_OPTIONS`, `selectedOptions`, `possibleAnswer` declarations (`Quiz.vue:491-492,498`).

6. Add the import:

```js
import { getQuestionType } from '@/questionTypes'
```

- [ ] **Step 5: Verify in the preview (manual — exhaustive)**

This is the risky task; test all paths in the preview:
- Choices single-correct (radio) and multi-correct (checkbox): select, navigate, submit, score correct.
- "Check" live feedback (quiz with `show_answers`): per-option icons appear correctly.
- User Input: type answer, submit, correct/incorrect badge on reveal.
- Open Ended: rich answer submits; summary shows the "instructor will review" message.
- localStorage restore: answer a question, navigate away and back — answer is restored.
- Refresh/unload auto-submit still fires (the `pagehide`/`beforeunload` handlers read `getAnswers()`).

- [ ] **Step 6: Run reviewers, then commit & push**

Run **vue-frontend-reviewer** and **rtl-i18n-reviewer**; address findings.

```bash
git add frontend/src/components/Quiz.vue frontend/src/questionTypes/components/
git commit -m "refactor(quiz-fe): host per-type player components in Quiz"
git push
```

---

## Self-Review

- **Spec coverage:**
  - "Frontend type registry mirroring backend" → Task 1. ✓
  - "Question.vue becomes a host rendering AuthorComponent" → Task 5. ✓
  - "Learner player becomes a host rendering PlayerComponent" → Task 6. ✓
  - "Behavior + storage unchanged for the 3 types" → author components keep writing `option_N`/`possibility_N`; player helpers reproduce the exact `getAnswers`/`loadSavedAnswers` logic; verified manually in preview + Vitest helper tests. ✓
  - "type options from registry" → Task 5 Step 4.2 (`questionTypeOptions()`), guarded against backend drift by the backend plan's Task 1 test. ✓
- **Placeholder scan:** none — every component has full markup/script; helper logic is concrete.
- **Type consistency:** `getQuestionType` / `questionTypeOptions` / `questionTypeNames`, the `QuestionTypeDef` fields (`getAnswers`, `loadAnswer`, `AuthorComponent`, `PlayerComponent`, `autoGraded`, `hasLiveCheck`), and the player `v-model:state` / `showAnswers` / `quizShowAnswers` props are used identically across Tasks 1-6. ✓
- **Ordering note:** Tasks 1-4 (registry + defs + helpers) ship as one push and are unit-tested. Task 5 (authoring) and Task 6 (player) are independent of each other and each independently shippable — the player keeps working with legacy code until Task 6, and authoring keeps working until Task 5.
- **Dependency on backend plan:** none at runtime for the 3 existing types (they use legacy columns). The frontend registry's `data`-field usage only matters once new types are added (later spec).
